"""
pipeline/main_restoration.py
============================
Stage 6: Reference-Guided Frame Restoration.
Enhances the background using Real-ESRGAN (via the custom RealESRGANEngine).
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
from pipeline.realesrgan_engine import RealESRGANEngine

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
        self.esrgan_engine = self._init_realesrgan()

    def _load_face_cache(self) -> dict:
        cache_path = self.models_dir / "face_cache.json"
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load face cache: {e}")
        return {}

    def _init_realesrgan(self) -> RealESRGANEngine | None:
        if not self.use_realesrgan:
            return None
        try:
            engine = RealESRGANEngine(
                model_name=self.realesrgan_model,
                models_dir=str(self.models_dir),
                device=self.device
            )
            return engine
        except Exception as e:
            logger.warning(f"Could not initialize RealESRGANEngine: {e}. Falling back to standard filters.")
            return None

    def _enhance_background(self, img: np.ndarray) -> np.ndarray:
        """Sharpen, denoise, and upscale background."""
        # 1. Denoise using bilateral filter
        denoised = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        
        # 2. Super-resolution (ESRGAN or Lanczos)
        if self.esrgan_engine is not None:
            try:
                # Upscale background using Real-ESRGAN BGR
                sr_bgr = self.esrgan_engine.enhance(
                    denoised,
                    tile_size=256,
                    tile_pad=10,
                    outscale=2.0
                )
                # Apply edge enhancement to super-resolved background
                sharpened = edge_enhancement(sr_bgr, strength=self.config["restoration"]["unsharp_strength"])
                return sharpened
            except Exception as e:
                logger.warning(f"RealESRGANEngine inference failed: {e}. Falling back to Lanczos.")
                
        # Fallback super-resolution (Lanczos)
        h, w = img.shape[:2]
        sr_bgr = cv2.resize(denoised, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
        sharpened = edge_enhancement(sr_bgr, strength=self.config["restoration"]["unsharp_strength"])
        return sharpened

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
            
        album = cv2.imread(str(self.albums_dir / a_name))
        if album is None:
            return frame_bg
            
        # Landmarks scaled to high-res
        f_kps = np.array(f_cache["kps"]) * scale
        a_kps = np.array(a_cache["kps"])
        
        # Affine transform matrix
        M, inliers = cv2.estimateAffinePartial2D(a_kps, f_kps)
        if M is None:
            logger.warning(f"Could not compute affine transform for {f_name}")
            return frame_bg
            
        h_bg, w_bg = frame_bg.shape[:2]
        warped_album = cv2.warpAffine(album, M, (w_bg, h_bg), flags=cv2.INTER_CUBIC)
        
        # Masks
        face_size = np.linalg.norm(f_kps[1] - f_kps[0])
        mask_eyes, mask_lips, mask_skin, mask_hair, mask_jewel = self._get_component_masks(
            frame_bg.shape, f_kps, face_size
        )
        
        mask_eyes_3c = np.expand_dims(mask_eyes, axis=2)
        mask_lips_3c = np.expand_dims(mask_lips, axis=2)
        mask_skin_3c = np.expand_dims(mask_skin, axis=2)
        mask_hair_3c = np.expand_dims(mask_hair, axis=2)
        mask_jewel_3c = np.expand_dims(mask_jewel, axis=2)
        
        output = frame_bg.copy()
        
        # 1. Restore Eyes and Lips (blend directly)
        output = (output * (1.0 - mask_eyes_3c) + warped_album * mask_eyes_3c).astype(np.uint8)
        output = (output * (1.0 - mask_lips_3c) + warped_album * mask_lips_3c).astype(np.uint8)
        
        # 2. Restore Skin (color transfer + guided filter smoothing)
        skin_color = color_transfer(warped_album, output)
        guidance = cv2.cvtColor(skin_color, cv2.COLOR_BGR2GRAY)
        smoothed_skin = guided_filter(guidance, skin_color, r=8, eps=0.01)
        output = (output * (1.0 - mask_skin_3c) + smoothed_skin * mask_skin_3c).astype(np.uint8)
        
        # 3. Restore Hair (high-frequency detail transfer)
        album_gray = cv2.cvtColor(warped_album, cv2.COLOR_BGR2GRAY)
        album_smooth = cv2.GaussianBlur(album_gray, (0, 0), 2.0)
        album_detail = cv2.subtract(album_gray, album_smooth)
        album_detail_3c = np.expand_dims(album_detail, axis=2)
        
        hair_enhanced = cv2.add(output, album_detail_3c)
        output = (output * (1.0 - mask_hair_3c) + hair_enhanced * mask_hair_3c).astype(np.uint8)
        
        # 4. Restore Jewellery (unsharp detail transfer)
        jewel_enhanced = cv2.addWeighted(output, 1.0, warped_album, 0.4, 0)
        output = (output * (1.0 - mask_jewel_3c) + jewel_enhanced * mask_jewel_3c).astype(np.uint8)
        
        return output

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 6: Reference-Guided Restoration")
        
        matches_csv = self.output_dir / "advanced_matches.csv"
        if not matches_csv.exists():
            raise FileNotFoundError(f"Matches CSV not found at {matches_csv}. Run Stage 5 first.")
            
        df = pd.read_csv(matches_csv)
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
        
        for _, row in tqdm(top_matches.iterrows(), total=len(top_matches), desc="Restoring Keyframes"):
            f_name = str(row["Frame"])
            a_name = str(row["AlbumImage"])
            
            out_path = self.restored_dir / f_name
            if f_name in processed_frames and out_path.exists() and not force:
                continue
                
            frame_img = cv2.imread(str(self.frames_dir / f_name))
            if frame_img is None:
                logger.warning(f"Frame image not found: {f_name}")
                continue
                
            # Enhance background (Real-ESRGAN upscales 2x)
            enhanced_bg = self._enhance_background(frame_img)
            
            # Align and restore face
            restored = self._restore_face_regions(enhanced_bg, f_name, a_name, scale=2.0)
            
            cv2.imwrite(str(out_path), restored)
            log_rows.append([f_name, a_name, "success"])
            
        log_exists = processed_log.exists()
        with open(processed_log, "a" if log_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not log_exists:
                writer.writerow(["Frame", "ReferencePhoto", "Status"])
            writer.writerows(log_rows)
            
        logger.info(f"Stage 6 completed. Restored frames saved to {self.restored_dir}")
        
        # Release CUDA VRAM
        if self.esrgan_engine is not None:
            del self.esrgan_engine
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
