"""
pipeline/video_propagation.py
=============================
Stage 7: Modern Optical Flow Video Reconstruction and Temporal Propagation.
Uses torchvision RAFT-small in FP16 on CUDA.
Warping is computed entirely on GPU via grid_sample.
Confidence masks are calculated based on warping residuals.
Features temporal EMA smoothing and Lab flicker removal.
Streams output frames directly to FFmpeg via a pipe.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from pathlib import Path
import re

import cv2
import numpy as np
import pandas as pd
import torch
import torchvision.models.optical_flow as opt_flow
from tqdm import tqdm

from utils.temporal_utils import remove_flicker_global

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("video_propagation")


def warp_flow(img: torch.Tensor, flow: torch.Tensor) -> torch.Tensor:
    """
    Warp image tensor of shape (B, C, H, W) using flow tensor of shape (B, 2, H, W).
    Performs bilinear grid sampling on GPU.
    """
    B, C, H, W = img.size()
    
    # Create meshgrid
    yy, xx = torch.meshgrid(
        torch.arange(0, H, device=img.device, dtype=torch.float32),
        torch.arange(0, W, device=img.device, dtype=torch.float32),
        indexing="ij"
    )
    
    grid = torch.stack((xx, yy), dim=0).unsqueeze(0).repeat(B, 1, 1, 1)  # B, 2, H, W
    vgrid = grid + flow
    
    # Scale grid to [-1, 1] for grid_sample
    vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :].clone() / max(1, W - 1) - 1.0
    vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :].clone() / max(1, H - 1) - 1.0
    
    vgrid = vgrid.permute(0, 2, 3, 1)  # B, H, W, 2
    output = torch.nn.functional.grid_sample(
        img, vgrid, mode="bilinear", padding_mode="replicate", align_corners=True
    )
    return output


def pad_to_multiple(img: torch.Tensor, divisor: int = 8) -> tuple[torch.Tensor, int, int]:
    """Pad tensor dimensions to be divisible by divisor (required by RAFT)."""
    h, w = img.shape[-2:]
    pad_h = (divisor - h % divisor) % divisor
    pad_w = (divisor - w % divisor) % divisor
    if pad_h > 0 or pad_w > 0:
        img = torch.nn.functional.pad(img, (0, pad_w, 0, pad_h), mode="replicate")
    return img, pad_h, pad_w


class VideoPropagationStage:
    def __init__(self, config: dict):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() and config["global"]["device"] == "cuda" else "cpu"
        self.cfr_path = Path(config["video_repair"]["cfr_video_path"])
        self.scene_csv_path = Path(config["video_repair"]["scene_csv_path"])
        self.restored_dir = Path(config["restoration"]["output_dir"])
        
        cfg = config["video_propagation"]
        self.output_silent = Path(cfg["output_silent"])
        self.model_type = cfg["model_type"]
        self.strength = float(cfg["strength"])
        self.temporal_strength = float(cfg["temporal_strength"])
        self.detail_strength = float(cfg["detail_strength"])
        self.flicker_removal = bool(cfg["flicker_removal"])
        
        self.output_silent.parent.mkdir(parents=True, exist_ok=True)
        self.raft_model = self._init_raft()

    def _init_raft(self):
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

    def _compute_flow(self, img1: torch.Tensor, img2: torch.Tensor) -> torch.Tensor:
        """Compute optical flow from img1 to img2 using RAFT (FP16)."""
        # RAFT expects [0, 255] tensors of shape (B, 3, H, W)
        img1_pad, pad_h, pad_w = pad_to_multiple(img1)
        img2_pad, _, _ = pad_to_multiple(img2)
        
        with torch.inference_mode():
            list_of_flows = self.raft_model(img1_pad, img2_pad, num_flow_updates=12)
            flow = list_of_flows[-1]
            
        # Crop back to original size
        h, w = img1.shape[-2:]
        flow = flow[..., :h, :w]
        return flow

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 7: Video Detail Propagation (RAFT)")
        
        if self.output_silent.exists() and not force:
            logger.info("Silent video already reconstructed. Skipping.")
            return
            
        scenes = self._get_scenes()
        cap = cv2.VideoCapture(str(self.cfr_path))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open CFR video: {self.cfr_path}")
            
        # Determine output properties from restored directory frames (at 2x resolution)
        sample_frame_path = next(self.restored_dir.glob("*.jpg"), None)
        if sample_frame_path is None:
            raise FileNotFoundError("No restored keyframes found. Run Stage 6 first.")
            
        sample_img = cv2.imread(str(sample_frame_path))
        h_out, w_out = sample_img.shape[:2]
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Reconstructed resolution: {w_out}x{h_out} @ {fps:.2f} FPS")
        
        # Open FFmpeg pipe for writing video
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
        
        # Start FFmpeg process
        ffmpeg_proc = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        try:
            # We iterate scene-by-scene
            for scene in tqdm(scenes, desc="Propagating scenes"):
                scene_frames = []
                start, end = scene["start"], scene["end"]
                midpoint = scene["midpoint"]
                restored_path = scene["restored_path"]
                
                # Check if keyframe was successfully restored. If not, use original midpoint frame.
                cap.set(cv2.CAP_PROP_POS_FRAMES, midpoint)
                ret, ref_img = cap.read()
                if not ret:
                    logger.warning(f"Could not read midpoint frame {midpoint}")
                    continue
                    
                if restored_path.exists():
                    ref_restored = cv2.imread(str(restored_path))
                else:
                    logger.warning(f"Restored keyframe missing for scene {scene['scene_idx']}. Using original.")
                    ref_restored = cv2.resize(ref_img, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                
                # 1. Compute delta field at upscaled resolution
                # Upscale original reference image to match restored size
                ref_orig_upscaled = cv2.resize(ref_img, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                
                delta_bgr = ref_restored.astype(np.float32) - ref_orig_upscaled.astype(np.float32)
                
                # 2. Extract high frequency details for extra detail strength
                ref_gray = cv2.cvtColor(ref_restored, cv2.COLOR_BGR2GRAY)
                ref_smooth = cv2.GaussianBlur(ref_gray, (0, 0), 2.0)
                ref_detail = cv2.subtract(ref_gray, ref_smooth).astype(np.float32)
                
                # Convert reference images to PyTorch tensors for RAFT (at original resolution to save VRAM)
                ref_img_tensor = torch.from_numpy(ref_img).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                if self.device == "cuda":
                    ref_img_tensor = ref_img_tensor.half()
                    
                # Convert upscaled delta and details to GPU Tensors
                delta_tensor = torch.from_numpy(delta_bgr).permute(2, 0, 1).unsqueeze(0).to(self.device)
                detail_tensor = torch.from_numpy(ref_detail).unsqueeze(0).unsqueeze(0).to(self.device)
                
                # Read all frames in this scene
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                original_frames_in_scene = []
                for f_idx in range(start, end):
                    ret_f, frame_bgr = cap.read()
                    if not ret_f:
                        break
                    original_frames_in_scene.append((f_idx, frame_bgr))
                
                # We will hold reconstructed frames for this scene to apply flicker removal globally per scene
                scene_reconstructed = []
                
                # Temporal consistency state
                prev_delta_warped = None
                
                for f_idx, frame_bgr in original_frames_in_scene:
                    if f_idx == midpoint:
                        # Exact restored reference frame
                        scene_reconstructed.append(ref_restored)
                        continue
                        
                    # Target frame upscaled
                    frame_upscaled = cv2.resize(frame_bgr, (w_out, h_out), interpolation=cv2.INTER_CUBIC)
                    
                    # Convert to PyTorch tensor for optical flow
                    tgt_img_tensor = torch.from_numpy(frame_bgr).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                    if self.device == "cuda":
                        tgt_img_tensor = tgt_img_tensor.half()
                        
                    # Compute flow from target to reference: RAFT maps where pixels went
                    # We compute flow at original resolution to stay within 4GB VRAM
                    flow = self._compute_flow(tgt_img_tensor, ref_img_tensor)
                    
                    # Upscale flow to high-res target resolution
                    flow_upscaled = torch.nn.functional.interpolate(
                        flow, size=(h_out, w_out), mode="bilinear", align_corners=True
                    )
                    # Scale flow coordinates by upscale factor (2.0)
                    flow_upscaled = flow_upscaled * (w_out / frame_bgr.shape[1])
                    
                    # Warp delta field to target coordinates
                    delta_warped = warp_flow(delta_tensor, flow_upscaled)
                    detail_warped = warp_flow(detail_tensor, flow_upscaled)
                    
                    # Warp reference original image to target coordinates to compute residual error
                    ref_orig_tensor_up = torch.from_numpy(ref_orig_upscaled).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                    ref_warped = warp_flow(ref_orig_tensor_up, flow_upscaled)
                    
                    tgt_upscaled_tensor = torch.from_numpy(frame_upscaled).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
                    
                    # Compute warping error (residual)
                    residual = torch.abs(tgt_upscaled_tensor - ref_warped).mean(dim=1, keepdim=True)
                    # Flow confidence mask: lower confidence in occlusions / large residual errors
                    sigma = 35.0
                    conf_mask = torch.exp(-residual / (2.0 * sigma**2))
                    
                    # Temporal EMA blending of warped delta field
                    if prev_delta_warped is not None:
                        delta_warped = delta_warped * self.temporal_strength + prev_delta_warped * (1.0 - self.temporal_strength)
                    prev_delta_warped = delta_warped.clone()
                    
                    # Apply warped delta and details weighted by confidence
                    restored_tensor = tgt_upscaled_tensor + delta_warped * conf_mask * self.strength
                    # Add high-frequency details
                    detail_enhanced = detail_warped * conf_mask * self.detail_strength
                    restored_tensor = restored_tensor + detail_enhanced
                    
                    restored_np = restored_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
                    restored_np = np.clip(restored_np, 0, 255).astype(np.uint8)
                    
                    scene_reconstructed.append(restored_np)
                
                # Apply Global Lab Flicker Removal across this scene's frames
                if self.flicker_removal and len(scene_reconstructed) > 2:
                    # Convert list to RGB for flicker removal, then back to BGR
                    scene_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in scene_reconstructed]
                    scene_rgb_fixed = remove_flicker_global(scene_rgb, window_size=5)
                    scene_reconstructed = [cv2.cvtColor(f, cv2.COLOR_RGB2BGR) for f in scene_rgb_fixed]
                    
                # Write frames to FFmpeg pipe
                for frame in scene_reconstructed:
                    ffmpeg_proc.stdin.write(frame.tobytes())
                    
        finally:
            cap.release()
            if ffmpeg_proc.stdin:
                ffmpeg_proc.stdin.close()
            ffmpeg_proc.wait()
            
        logger.info(f"Video propagation complete. Silent video saved to {self.output_silent}")
        
        # Free RAFT model memory
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
