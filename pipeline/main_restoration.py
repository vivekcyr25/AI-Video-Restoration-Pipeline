"""
pipeline/main_restoration.py
============================
Stage 6: Reference-Guided Frame Restoration.
Enhances the background using Real-ESRGAN (or high-quality bilateral + unsharp filter fallback).
Restores the face by transferring high-frequency details from the aligned album photo,
including eyes, lips, skin, hair, and jewellery without hallucinating details.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch

from utils.image_enhancement import (
    apply_clahe,
    color_transfer,
    edge_enhancement,
    guided_filter,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("main_restoration")


class ReferenceRestorer:
    def __init__(self, config: dict):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() and config["global"]["device"] == "cuda" else "cpu"
        self.albums_dir = Path(config["global"]["albums_dir"])
        self.frames_dir = Path(config["frame_extractor"]["output_dir"])
        self.models_dir = Path(config["global"]["models_dir"])
        self.output_dir = Path(config["global"]["output_dir"])
        
        cfg = config["restoration"]
        self.restored_dir = Path(cfg["output_dir"])
        self.strength = float(cfg["strength"])
        self.face_alignment_scale = float(cfg["face_alignment_scale"])
        self.use_realesrgan = bool(cfg["use_realesrgan"])
        self.realesrgan_model = cfg["realesrgan_model"]
        self.realesrgan_half = bool(cfg["realesrgan_half"])
        
        self.restored_dir.mkdir(parents=True, exist_ok=True)
        self.face_cache = self._load_face_cache()
        self.esrgan_model = self._init_realesrgan()

    def _load_face_cache(self) -> dict:
        cache_path = self.models_dir / "face_cache.json"
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load face cache: {e}")
        return {}

    def _init_realesrgan(self):
        if not self.use_realesrgan:
            return None
            
        try:
            # Attempt to import RealESRGANer
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            
            # Select model config based on config name
            if "anime" in self.realesrgan_model:
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
            else:
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                
            # Download weights if not locally cached by basicsr
            # For simplicity, we initialize the model with basicsr default paths
            upscaler = RealESRGANer(
                scale=4,
                model_path=None,  # Automatically downloads weight
                model=model,
                tile=400,
                tile_pad=10,
                pre_pad=0,
                half=self.realesrgan_half and (self.device == "cuda"),
                device=self.device
            )
            logger.info("Real-ESRGAN initialized successfully.")
            return upscaler
        except Exception as e:
            logger.warning(f"Could not load Real-ESRGAN: {e}. Falling back to classical super-resolution.")
            return None

    def _enhance_background(self, img: np.ndarray) -> np.ndarray:
        """Sharpen, denoise, and upscale background."""
        # 1. Denoise using bilateral filter
        denoised = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        
        # 2. Super-resolution (ESRGAN or Lanczos)
        if self.esrgan_model is not None:
            try:
                # Real-ESRGAN expects BGR input
                sr_bgr, _ = self.esrgan_model.enhance(denoised, outscale=2)
                # Apply edge enhancement to super-resolved background
                sharpened = edge_enhancement(sr_bgr, strength=self.config["restoration"]["unsharp_strength"])
                return sharpened
            except Exception as e:
                logger.warning(f"ESRGAN inference failed: {e}. Falling back to Lanczos.")
                
        # Fallback super-resolution (Lanczos)
        h, w = img.shape[:2]
        sr_bgr = cv2.resize(denoised, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
        sharpened = edge_enhancement(sr_bgr, strength=self.config["restoration"]["unsharp_strength"])
        return sharpened

    def _align_face(
        self,
        src_img: np.ndarray,
        src_kps: np.ndarray,
        tgt_shape: tuple[int, int, int]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Align source face (album) to target face (frame) shape using 5-point affine warp."""
        tgt_h, tgt_w = tgt_shape[:2]
        
        # We need target landmarks to align
        # Standard landmarks crop matrix
        # Let's map album landmarks to targets using partial affine
        # targets = targets_scale * [x, y] + translation
        src_pts = src_kps.astype(np.float32)
        
        # Standard target landmarks normalized coordinates
        # Map source to a canonical 112x112 or target coordinates directly
        return src_pts

    def _get_component_masks(
        self,
        shape: tuple[int, int, int],
        kps: np.ndarray,
        face_size: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate soft masks for eyes, lips, skin, hair, and jewellery based on 5 landmarks."""
        H, W = shape[:2]
        eye_l = kps[0]
        eye_r = kps[1]
        nose = kps[2]
        mouth_l = kps[3]
        mouth_r = kps[4]
        
        # Radii based on face width
        face_w = np.linalg.norm(eye_r - eye_l)
        r_eye = max(4, int(face_w * 0.28))
        
        mask_eyes = np.zeros((H, W), dtype=np.float32)
        cv2.circle(mask_eyes, (int(eye_l[0]), int(eye_l[1])), r_eye, 1.0, -1)
        cv2.circle(mask_eyes, (int(eye_r[0]), int(eye_r[1])), r_eye, 1.0, -1)
        mask_eyes = cv2.GaussianBlur(mask_eyes, (0, 0), r_eye // 3 * 2 + 1)
        
        # Lips mask
        mask_lips = np.zeros((H, W), dtype=np.float32)
        mouth_center = ((mouth_l + mouth_r) / 2.0).astype(int)
        mouth_w = max(4, int(np.linalg.norm(mouth_r - mouth_l) * 0.7))
        mouth_h = max(2, int(face_w * 0.18))
        cv2.ellipse(mask_lips, (mouth_center[0], mouth_center[1]), (mouth_w, mouth_h), 0, 0, 360, 1.0, -1)
        mask_lips = cv2.GaussianBlur(mask_lips, (0, 0), mouth_h // 2 * 2 + 1)
        
        # Face skin mask
        mask_skin = np.zeros((H, W), dtype=np.float32)
        face_center = ((eye_l + eye_r + mouth_l + mouth_r) / 4.0).astype(int)
        face_radius_x = max(10, int(face_w * 0.85))
        face_radius_y = max(10, int(np.linalg.norm(nose - face_center) * 2.2))
        cv2.ellipse(mask_skin, (face_center[0], face_center[1]), (face_radius_x, face_radius_y), 0, 0, 360, 1.0, -1)
        mask_skin = cv2.GaussianBlur(mask_skin, (0, 0), face_radius_x // 3 * 2 + 1)
        
        # Clean skin (subtract eyes and lips)
        mask_skin = np.clip(mask_skin - mask_eyes - mask_lips, 0, 1)
        
        # Hair mask (expanded upwards)
        mask_hair = np.zeros((H, W), dtype=np.float32)
        hair_center = (face_center - np.array([0, face_radius_y * 0.6])).astype(int)
        hair_radius_x = max(10, int(face_radius_x * 1.3))
        hair_radius_y = max(10, int(face_radius_y * 1.1))
        cv2.ellipse(mask_hair, (hair_center[0], hair_center[1]), (hair_radius_x, hair_radius_y), 0, 0, 360, 1.0, -1)
        mask_hair = cv2.GaussianBlur(mask_hair, (0, 0), hair_radius_x // 4 * 2 + 1)
        mask_hair = np.clip(mask_hair - mask_skin - mask_eyes - mask_lips, 0, 1)
        
        # Jewellery / Clothing mask (neck region + ears)
        mask_jewel = np.zeros((H, W), dtype=np.float32)
        chin_y = int(face_center[1] + face_radius_y)
        neck_h = max(10, int(face_radius_y * 0.8))
        neck_w = max(10, int(face_radius_x * 1.2))
        cv2.rectangle(mask_jewel, (face_center[0] - neck_w, chin_y), (face_center[0] + neck_w, chin_y + neck_h), 1.0, -1)
        # Ear regions
        cv2.circle(mask_jewel, (int(face_center[0] - face_radius_x * 1.1), int(face_center[1])), int(face_radius_y * 0.4), 1.0, -1)
        cv2.circle(mask_jewel, (int(face_center[0] + face_radius_x * 1.1), int(face_center[1])), int(face_radius_y * 0.4), 1.0, -1)
        mask_jewel = cv2.GaussianBlur(mask_jewel, (0, 0), face_radius_x // 3 * 2 + 1)
        mask_jewel = np.clip(mask_jewel - mask_skin - mask_hair - mask_eyes - mask_lips, 0, 1)
        
        return mask_eyes, mask_lips, mask_skin, mask_hair, mask_jewel

    def _restore_face_regions(
        self,
        frame_bg: np.ndarray,
        f_name: str,
        a_name: str,
        scale: float = 2.0
    ) -> np.ndarray:
        """Align and transfer facial details from album photo onto target upscaled frame."""
        f_cache = self.face_cache.get(f_name)
        a_cache = self.face_cache.get(a_name)
        
        if f_cache is None or a_cache is None:
            logger.info(f"Skipping face-guided warp for {f_name}: face missing in frame or album.")
            return frame_bg
            
        # Load original images to perform warp at high resolution
        album = cv2.imread(str(self.albums_dir / a_name))
        if album is None:
            return frame_bg
            
        # Extract landmarks and scale to upscaled resolution
        f_kps = np.array(f_cache["kps"]) * scale
        a_kps = np.array(a_cache["kps"])
        
        # Compute affine transform to warp album onto frame
        M, inliers = cv2.estimateAffinePartial2D(a_kps, f_kps)
        if M is None:
            logger.warning(f"Could not compute affine transform for {f_name}")
            return frame_bg
            
        # Warp album photo
        h_bg, w_bg = frame_bg.shape[:2]
        warped_album = cv2.warpAffine(album, M, (w_bg, h_bg), flags=cv2.INTER_CUBIC)
        
        # Compute component masks at upscaled resolution
        face_size = np.linalg.norm(f_kps[1] - f_kps[0])
        mask_eyes, mask_lips, mask_skin, mask_hair, mask_jewel = self._get_component_masks(
            frame_bg.shape, f_kps, face_size
        )
        
        # Expand masks to 3-channels
        mask_eyes_3c = np.expand_dims(mask_eyes, axis=2)
        mask_lips_3c = np.expand_dims(mask_lips, axis=2)
        mask_skin_3c = np.expand_dims(mask_skin, axis=2)
        mask_hair_3c = np.expand_dims(mask_hair, axis=2)
        mask_jewel_3c = np.expand_dims(mask_jewel, axis=2)
        
        output = frame_bg.copy()
        
        # 1. Restore Eyes and Lips (directly blend album components)
        # Warp contains the high-fidelity features
        output = (output * (1.0 - mask_eyes_3c) + warped_album * mask_eyes_3c).astype(np.uint8)
        output = (output * (1.0 - mask_lips_3c) + warped_album * mask_lips_3c).astype(np.uint8)
        
        # 2. Restore Skin (color transfer + guided filter smoothing)
        # Transfer color from warped album to the skin region
        skin_color = color_transfer(warped_album, output)
        
        # Smooth out compression blocks using Guided Filter on the skin region
        guidance = cv2.cvtColor(skin_color, cv2.COLOR_BGR2GRAY)
        smoothed_skin = guided_filter(guidance, skin_color, r=8, eps=0.01)
        
        output = (output * (1.0 - mask_skin_3c) + smoothed_skin * mask_skin_3c).astype(np.uint8)
        
        # 3. Restore Hair (transfer high-frequency details from album hair)
        # High frequency detail extraction
        album_gray = cv2.cvtColor(warped_album, cv2.COLOR_BGR2GRAY)
        album_smooth = cv2.GaussianBlur(album_gray, (0, 0), 2.0)
        album_detail = cv2.subtract(album_gray, album_smooth)
        album_detail_3c = np.expand_dims(album_detail, axis=2)
        
        hair_enhanced = cv2.add(output, album_detail_3c)
        output = (output * (1.0 - mask_hair_3c) + hair_enhanced * mask_hair_3c).astype(np.uint8)
        
        # 4. Restore Jewellery (unsharp detail transfer in jewellery region)
        jewel_enhanced = cv2.addWeighted(output, 1.0, warped_album, 0.4, 0)
        output = (output * (1.0 - mask_jewel_3c) + jewel_enhanced * mask_jewel_3c).astype(np.uint8)
        
        # Optional: Save debug checkpoints for masks/faces
        debug_dir = self.output_dir / "debug_masks"
        if debug_dir.exists():
            cv2.imwrite(str(debug_dir / f"{Path(f_name).stem}_eyes.jpg"), (mask_eyes * 255).astype(np.uint8))
            cv2.imwrite(str(debug_dir / f"{Path(f_name).stem}_skin.jpg"), (mask_skin * 255).astype(np.uint8))
            
        return output

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 6: Reference-Guided Restoration")
        
        matches_csv = self.output_dir / "advanced_matches.csv"
        if not matches_csv.exists():
            raise FileNotFoundError(f"Matches CSV not found at {matches_csv}. Run Stage 5 first.")
            
        df = pd.read_csv(matches_csv)
        # Parse top match (Rank 1) for each frame
        top_matches = df[df["Rank"] == 1]
        
        processed_log = self.output_dir / "restore_log.csv"
        processed_frames = set()
        
        if processed_log.exists() and not force:
            try:
                log_df = pd.read_csv(processed_log)
                processed_frames = set(log_df["Frame"].tolist())
            except Exception as e:
                logger.warning(f"Could not read restore log: {e}")
                
        log_rows = []
        
        for _, row in tqdm(top_matches.iterrows(), total=len(top_matches), unit="frame"):
            f_name = str(row["Frame"])
            a_name = str(row["AlbumImage"])
            
            out_path = self.restored_dir / f_name
            if f_name in processed_frames and out_path.exists() and not force:
                continue
                
            frame_img = cv2.imread(str(self.frames_dir / f_name))
            if frame_img is None:
                logger.warning(f"Frame image not found: {f_name}")
                continue
                
            # 1. Enhance and upscale background
            enhanced_bg = self._enhance_background(frame_img)
            
            # 2. Align and restore face regions (identity preservation)
            restored = self._restore_face_regions(enhanced_bg, f_name, a_name, scale=2.0)
            
            # Save output frame (at 2x resolution)
            cv2.imwrite(str(out_path), restored)
            log_rows.append([f_name, a_name, "success"])
            
        # Append to log
        log_exists = processed_log.exists()
        with open(processed_log, "a" if log_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not log_exists:
                writer.writerow(["Frame", "ReferencePhoto", "Status"])
            writer.writerows(log_rows)
            
        logger.info(f"Stage 6 completed. Restored frames saved to {self.restored_dir}")
        
        # Clear VRAM cache
        if self.esrgan_model is not None:
            del self.esrgan_model
        if self.device == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 6: Reference-Guided Restoration")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of restored frames")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = ReferenceRestorer(cfg)
    stage.run(force=args.force)
