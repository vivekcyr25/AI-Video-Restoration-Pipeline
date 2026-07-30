"""
pipeline/video_propagation.py
=============================
Stage 7: Modern Optical Flow Video Reconstruction and Temporal Propagation.
Uses torchvision RAFT-small in FP16 on CUDA.
Features adaptive keyframe insertion: when the average propagation confidence
drops below a threshold (due to occlusion, scene shifts, or extreme motion),
it automatically triggers reference-guided restoration on the current frame
to establish a new local anchor, preventing error accumulation.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils.temporal_utils import remove_flicker_global
from pipeline.main_restoration import ReferenceRestorer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("video_propagation")


_grid_cache = {}

def warp_flow(img, flow):
    """Warp image tensor of shape (B, C, H, W) using flow tensor of shape (B, 2, H, W) via grid_sample."""
    import torch
    B, C, H, W = img.size()
    grid_key = (B, H, W, img.device, img.dtype)
    global _grid_cache
    if grid_key in _grid_cache:
        grid = _grid_cache[grid_key]
    else:
        yy, xx = torch.meshgrid(
            torch.arange(0, H, device=img.device, dtype=torch.float32),
            torch.arange(0, W, device=img.device, dtype=torch.float32),
            indexing="ij"
        )
        grid = torch.stack((xx, yy), dim=0).unsqueeze(0).repeat(B, 1, 1, 1)
        if img.dtype == torch.float16:
            grid = grid.half()
        _grid_cache[grid_key] = grid
        
    vgrid = grid + flow
    vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :].clone() / max(1, W - 1) - 1.0
    vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :].clone() / max(1, H - 1) - 1.0
    vgrid = vgrid.permute(0, 2, 3, 1)
    output = torch.nn.functional.grid_sample(
        img, vgrid, mode="bilinear", padding_mode="replicate", align_corners=True
    )
    return output


def pad_to_multiple(img, divisor: int = 8):
    """Pad tensor dimensions to be divisible by divisor for RAFT processing."""
    import torch
    h, w = img.shape[-2:]
    pad_h = (divisor - h % divisor) % divisor
    pad_w = (divisor - w % divisor) % divisor
    if pad_h > 0 or pad_w > 0:
        img = torch.nn.functional.pad(img, (0, pad_w, 0, pad_h), mode="replicate")
    return img, pad_h, pad_w


class VideoPropagationStage:
    def __init__(self, config: dict):
        import torch
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() and config["global"]["device"] == "cuda" else "cpu"
        self.repaired_path = Path(config["video_repair"]["repaired_video_path"])
        self.scene_csv_path = Path(config["video_repair"]["scene_csv_path"])
        self.restored_dir = Path(config["restoration"]["output_dir"])
        
        cfg = config["video_propagation"]
        self.output_silent = Path(cfg["output_silent"])
        self.model_type = cfg["model_type"]
        self.strength = float(cfg["strength"])
        self.temporal_strength = float(cfg["temporal_strength"])
        self.detail_strength = float(cfg["detail_strength"])
        self.flicker_removal = bool(cfg["flicker_removal"])
        self.conf_threshold = 0.55  # Confidence drop threshold
        
        self.output_silent.parent.mkdir(parents=True, exist_ok=True)
        
        # Read optimization settings with defaults
        self.batch_size = int(cfg.get("batch_size", 16))
        self.num_flow_updates = int(cfg.get("num_flow_updates", 8))
        logger.info(f"Using batch_size={self.batch_size}, num_flow_updates={self.num_flow_updates} for Video Propagation")
        
        # Initialize restorer dependency for adaptive keyframe generation
        self.restorer = ReferenceRestorer(config)
        self.raft_model = self._init_raft()

    def _init_raft(self):
        import torchvision.models.optical_flow as opt_flow
        logger.info(f"Initializing optical flow model: {self.model_type}")
        if self.model_type == "raft_small":
            model = opt_flow.raft_small(weights=opt_flow.Raft_Small_Weights.DEFAULT)
        else:
            model = opt_flow.raft_large(weights=opt_flow.Raft_Large_Weights.DEFAULT)
        model = model.to(self.device).eval()
        if self.device == "cuda":
            model = model.half()
        return model

    def _get_scenes(self) -> list[dict]:
        df = pd.read_csv(self.scene_csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        start_col = next((c for c in df.columns if "start" in c.lower() and "frame" in c.lower()), None)
        length_col = next((c for c in df.columns if "length" in c.lower() and "frame" in c.lower()), None)
        end_col = next((c for c in df.columns if "end" in c.lower() and "frame" in c.lower()), None)
        
        scenes = []
        for i, row in df.iterrows():
            start = int(row[start_col])
            length = int(row[length_col]) if length_col else (int(row[end_col]) - start)
            midpoint = start + max(0, length - 1) // 2
            scenes.append({
                "scene_idx": i + 1,
                "start": start,
                "end": start + length,
                "midpoint": midpoint,
                "restored_path": self.restored_dir / f"scene_{i+1:04d}.jpg"
            })
        return scenes

    def _compute_flow(self, img1, img2):
        import torch
        img1_pad, pad_h, pad_w = pad_to_multiple(img1)
        img2_pad, _, _ = pad_to_multiple(img2)
        with torch.inference_mode():
            list_of_flows = self.raft_model(img1_pad, img2_pad, num_flow_updates=self.num_flow_updates)
            flow = list_of_flows[-1]
        h, w = img1.shape[-2:]
        flow = flow[..., :h, :w]
        return flow

    def _compute_flow_batch(self, img1_batch, img2_batch):
        import torch
        img1_pad, pad_h, pad_w = pad_to_multiple(img1_batch)
        img2_pad, _, _ = pad_to_multiple(img2_batch)
        with torch.inference_mode():
            list_of_flows = self.raft_model(img1_pad, img2_pad, num_flow_updates=self.num_flow_updates)
            flow = list_of_flows[-1]
        h, w = img1_batch.shape[-2:]
        flow = flow[..., :h, :w]
        return flow

    def run(self, force: bool = False) -> None:
        import torch
        logger.info("Starting Stage 7: Video Detail Propagation (RAFT)")
        
        if self.output_silent.exists() and not force:
            logger.info("Silent video already reconstructed. Skipping.")
            return
            
        scenes = self._get_scenes()
        cap = cv2.VideoCapture(str(self.repaired_path))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open repaired video: {self.repaired_path}")
            
        sample_frame_path = next(self.restored_dir.glob("*.jpg"), None)
        if sample_frame_path is None:
            raise FileNotFoundError("No restored keyframes found. Run Stage 6 first.")
            
        sample_img = cv2.imread(str(sample_frame_path))
        h_out, w_out = sample_img.shape[:2]
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Reconstructed resolution: {w_out}x{h_out} @ {fps:.2f} FPS")
        
        cmd_out = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{w_out}x{h_out}",
            "-r", f"{fps}",
            "-i", "-",
            "-c:v", "libx264",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(self.output_silent)
        ]
        
        ffmpeg_proc = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        try:
            for scene in tqdm(scenes, desc="Propagating scenes"):
                start, end = scene["start"], scene["end"]
                midpoint = scene["midpoint"]
                restored_path = scene["restored_path"]
                
                # Fetch reference photo filename for adaptive keyframe triggers
                matches_csv = self.restorer.output_dir / "advanced_matches.csv"
                df_matches = pd.read_csv(matches_csv)
                a_name = df_matches[(df_matches["Frame"] == f"scene_{scene['scene_idx']:04d}.jpg") & (df_matches["Rank"] == 1)]["AlbumImage"].values[0]
                
                # Load midpoint
                cap.set(cv2.CAP_PROP_POS_FRAMES, midpoint)
                ret, ref_img = cap.read()
                if not ret:
                    continue
                    
                if restored_path.exists():
                    ref_restored = cv2.imread(str(restored_path))
                else:
                    ref_restored = cv2.resize(ref_img, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                
                ref_orig_upscaled = cv2.resize(ref_img, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                delta_bgr = ref_restored.astype(np.float32) - ref_orig_upscaled.astype(np.float32)
                
                ref_gray = cv2.cvtColor(ref_restored, cv2.COLOR_BGR2GRAY)
                ref_smooth = cv2.GaussianBlur(ref_gray, (0, 0), 2.0)
                ref_detail = cv2.subtract(ref_gray, ref_smooth).astype(np.float32)
                
                ref_img_tensor = torch.from_numpy(ref_img).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                if self.device == "cuda":
                    ref_img_tensor = ref_img_tensor.half()
                    
                delta_tensor = torch.from_numpy(delta_bgr).permute(2, 0, 1).unsqueeze(0).to(self.device)
                detail_tensor = torch.from_numpy(ref_detail).unsqueeze(0).unsqueeze(0).to(self.device)
                
                # Read scene frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                original_frames_in_scene = []
                for f_idx in range(start, end):
                    ret_f, frame_bgr = cap.read()
                    if not ret_f:
                        break
                    original_frames_in_scene.append((f_idx, frame_bgr))
                
                scene_reconstructed = [None] * len(original_frames_in_scene)
                prev_delta_warped = None
                
                i = 0
                while i < len(original_frames_in_scene):
                    f_idx, frame_bgr = original_frames_in_scene[i]
                    
                    if f_idx == midpoint:
                        scene_reconstructed[i] = ref_restored
                        i += 1
                        continue
                        
                    # Build batch up to batch_size, stopping if we hit the midpoint (which is already set)
                    batch_frames = []
                    batch_indices = []
                    for k in range(i, min(i + self.batch_size, len(original_frames_in_scene))):
                        fk, fb = original_frames_in_scene[k]
                        if fk == midpoint:
                            break
                        batch_frames.append(fb)
                        batch_indices.append(k)
                        
                    if not batch_frames:
                        i += 1
                        continue
                        
                    # Precompute batch flow
                    tgt_tensors = []
                    ref_tensors = []
                    for fb in batch_frames:
                        tgt_t = torch.from_numpy(fb).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                        if self.device == "cuda":
                            tgt_t = tgt_t.half()
                        tgt_tensors.append(tgt_t)
                        ref_tensors.append(ref_img_tensor)
                        
                    tgt_batch = torch.cat(tgt_tensors, dim=0)
                    ref_batch = torch.cat(ref_tensors, dim=0)
                    
                    flows = self._compute_flow_batch(tgt_batch, ref_batch)
                    
                    # Sequentially process flows to handle temporal dependency and adaptive keyframe insertions
                    conf_dropped = False
                    for idx_in_batch, k in enumerate(batch_indices):
                        fk, fb = original_frames_in_scene[k]
                        flow_k = flows[idx_in_batch:idx_in_batch+1]
                        
                        flow_upscaled = torch.nn.functional.interpolate(
                            flow_k, size=(h_out, w_out), mode="bilinear", align_corners=True
                        )
                        flow_upscaled = flow_upscaled * (w_out / fb.shape[1])
                        
                        # 2. Warp delta
                        delta_warped = warp_flow(delta_tensor, flow_upscaled)
                        detail_warped = warp_flow(detail_tensor, flow_upscaled)
                        
                        # 3. Compute residual and confidence
                        ref_orig_tensor_up = torch.from_numpy(ref_orig_upscaled).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                        if self.device == "cuda":
                            ref_orig_tensor_up = ref_orig_tensor_up.half()
                        ref_warped = warp_flow(ref_orig_tensor_up, flow_upscaled)
                        
                        frame_upscaled = cv2.resize(fb, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                        tgt_upscaled_tensor = torch.from_numpy(frame_upscaled).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                        if self.device == "cuda":
                            tgt_upscaled_tensor = tgt_upscaled_tensor.half()
                            
                        residual = torch.abs(tgt_upscaled_tensor - ref_warped).mean(dim=1, keepdim=True)
                        sigma = 35.0
                        conf_mask = torch.exp(-residual / (2.0 * sigma**2))
                        mean_conf = float(conf_mask.mean().cpu().item())
                        
                        # 4. Adaptive Keyframe Restoration Trigger
                        if mean_conf < self.conf_threshold:
                            logger.info(f"Scene {scene['scene_idx']} confidence dropped to {mean_conf:.3f} at frame {fk}. Restoring new local anchor.")
                            
                            # Generate restored frame on-the-fly for new anchor
                            restored_anchor = self.restorer._enhance_background(fb)
                            
                            # Run face restoration dynamically if face detected
                            restored_anchor = self.restorer._restore_face_regions(
                                restored_anchor,
                                f"scene_{scene['scene_idx']:04d}.jpg",
                                a_name,
                                scale=2.0
                            )
                            
                            # Set new anchor variables
                            ref_img = fb.copy()
                            ref_restored = restored_anchor.copy()
                            ref_orig_upscaled = cv2.resize(ref_img, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                            delta_bgr = ref_restored.astype(np.float32) - ref_orig_upscaled.astype(np.float32)
                            
                            ref_gray = cv2.cvtColor(ref_restored, cv2.COLOR_BGR2GRAY)
                            ref_smooth = cv2.GaussianBlur(ref_gray, (0, 0), 2.0)
                            ref_detail = cv2.subtract(ref_gray, ref_smooth).astype(np.float32)
                            
                            ref_img_tensor = torch.from_numpy(ref_img).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                            if self.device == "cuda":
                                ref_img_tensor = ref_img_tensor.half()
                                
                            delta_tensor = torch.from_numpy(delta_bgr).permute(2, 0, 1).unsqueeze(0).to(self.device)
                            detail_tensor = torch.from_numpy(ref_detail).unsqueeze(0).unsqueeze(0).to(self.device)
                            
                            # Reset temporal flow state
                            prev_delta_warped = None
                            scene_reconstructed[k] = ref_restored
                            
                            # Discard subsequent precomputed flows in the batch & slide loop to k + 1
                            i = k + 1
                            conf_dropped = True
                            break
                            
                        # Apply standard flow details
                        if prev_delta_warped is not None:
                            delta_warped = delta_warped * self.temporal_strength + prev_delta_warped * (1.0 - self.temporal_strength)
                        prev_delta_warped = delta_warped.clone()
                        
                        restored_tensor = tgt_upscaled_tensor + delta_warped * conf_mask * self.strength
                        detail_enhanced = detail_warped * conf_mask * self.detail_strength
                        restored_tensor = restored_tensor + detail_enhanced
                        
                        restored_np = restored_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
                        restored_np = np.clip(restored_np, 0, 255).astype(np.uint8)
                        scene_reconstructed[k] = restored_np
                        
                    if not conf_dropped:
                        # Advance sequentially by the size of processed batch
                        i += len(batch_frames)
                
                # Filter out any None frames just in case of decode/trigger anomalies
                scene_reconstructed_clean = [f for f in scene_reconstructed if f is not None]
                
                # Apply Global Lab Flicker Removal
                if self.flicker_removal and len(scene_reconstructed_clean) > 2:
                    scene_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in scene_reconstructed_clean]
                    scene_rgb_fixed = remove_flicker_global(scene_rgb, window_size=5)
                    scene_reconstructed_clean = [cv2.cvtColor(f, cv2.COLOR_RGB2BGR) for f in scene_rgb_fixed]
                    
                for frame in scene_reconstructed_clean:
                    ffmpeg_proc.stdin.write(frame.tobytes())
                    
        finally:
            cap.release()
            if ffmpeg_proc.stdin:
                ffmpeg_proc.stdin.close()
            ffmpeg_proc.wait()
            
        logger.info(f"Video propagation complete. Silent video saved to {self.output_silent}")
        del self.raft_model
        if self.device == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 7: Video Detail Propagation")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of silent video")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = VideoPropagationStage(cfg)
    stage.run(force=args.force)
