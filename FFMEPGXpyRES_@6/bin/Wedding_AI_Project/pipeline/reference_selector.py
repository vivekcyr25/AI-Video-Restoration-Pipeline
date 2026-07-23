"""
pipeline/reference_selector.py
==============================
Stage 5: Reference Selection Module.
Computes and fuses five similarity metrics:
  1. CLIP Cosine Similarity (Semantic Content)
  2. ArcFace Cosine Similarity (Face Identity)
  3. Scene Context Similarity (Temporal Shot Proximity)
  4. Color Histogram Similarity (Bhattacharyya Distance in Lab Space)
  5. Perceptual Similarity (VGG16 LPIPS-equivalent)
Fuses scores using confidence weights and outputs the ranked reference mappings.
"""

from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
import torchvision.models as models
from tqdm import tqdm

from utils.image_enhancement import compute_histogram, histogram_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reference_selector")


class VGGPerceptualLoss(torch.nn.Module):
    """VGG16-based Perceptual Similarity metric (LPIPS equivalent)."""
    def __init__(self):
        super().__init__()
        vgg = models.vgg16(weights=models.VGG16_Weights.DEFAULT).features
        self.slice1 = torch.nn.Sequential(*list(vgg.children())[:4])   # conv1_2
        self.slice2 = torch.nn.Sequential(*list(vgg.children())[4:9])   # conv2_2
        self.slice3 = torch.nn.Sequential(*list(vgg.children())[9:16])  # conv3_3
        for param in self.parameters():
            param.requires_grad = False

    def forward(self, x: torch.Tensor) -> list[torch.Tensor]:
        h1 = self.slice1(x)
        h2 = self.slice2(h1)
        h3 = self.slice3(h2)
        # L2 normalize feature maps channel-wise
        return [h / (h.norm(dim=1, keepdim=True) + 1e-10) for h in [h1, h2, h3]]


class ReferenceSelectorStage:
    def __init__(self, config: dict):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() and config["global"]["device"] == "cuda" else "cpu"
        self.albums_dir = Path(config["global"]["albums_dir"])
        self.frames_dir = Path(config["frame_extractor"]["output_dir"])
        self.models_dir = Path(config["global"]["models_dir"])
        self.output_dir = Path(config["global"]["output_dir"])
        
        cfg = config["hybrid_matching"]
        self.top_k = int(cfg["top_k"])
        self.weights = cfg["weights"]
        self.lpips_backbone = cfg["lpips_backbone"]

    def _load_face_metadata(self, prefix: str) -> dict[str, dict]:
        csv_path = self.models_dir / f"{prefix}_face_names.csv"
        emb_path = self.models_dir / f"{prefix}_face_embeddings.npy"
        
        if not csv_path.exists() or not emb_path.exists():
            return {}
            
        try:
            df = pd.read_csv(csv_path)
            embeddings = np.load(emb_path)
            face_map = {}
            for _, row in df.iterrows():
                img_name = row["image"]
                idx = int(row["embedding_index"])
                face_map[img_name] = {
                    "embedding": embeddings[idx],
                    "bbox": [row["x1"], row["y1"], row["x2"], row["y2"]],
                    "score": row["score"]
                }
            return face_map
        except Exception as e:
            logger.warning(f"Error loading face metadata for {prefix}: {e}")
            return {}

    def _preprocess_lpips(self, img_path: Path) -> torch.Tensor:
        img = cv2.imread(str(img_path))
        if img is None:
            return torch.zeros((1, 3, 224, 224), dtype=torch.float32)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        # Scale to [-1, 1]
        tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 127.5 - 1.0
        return tensor.unsqueeze(0)

    def run(self, force: bool = False) -> None:
        logger.info("Running Reference Selector Stage")
        out_csv = self.output_dir / "advanced_matches.csv"
        
        if out_csv.exists() and not force:
            logger.info("Matches file already exists. Skipping.")
            return

        # Load pre-computed CLIP embeddings
        album_clip = np.load(self.models_dir / "album_embeddings.npy")
        album_names = np.load(self.models_dir / "album_names.npy", allow_pickle=True).tolist()
        frame_clip = np.load(self.models_dir / "frames_embeddings.npy")
        frame_names = np.load(self.models_dir / "frames_names.npy", allow_pickle=True).tolist()
        
        # Load face metadata
        album_faces = self._load_face_metadata("album")
        frame_faces = self._load_face_metadata("frame")
        
        # Compute Scene similarity context
        window = 3
        pad_width = window // 2
        padded_frames = np.pad(frame_clip, ((pad_width, pad_width), (0, 0)), mode="edge")
        scene_clip = np.zeros_like(frame_clip)
        for i in range(len(frame_clip)):
            scene_clip[i] = np.mean(padded_frames[i : i + window], axis=0)
            scene_clip[i] /= np.linalg.norm(scene_clip[i]) + 1e-10

        # Load LPIPS equivalent (VGG16)
        lpips_net = VGGPerceptualLoss().to(self.device)
        lpips_net.eval()
        use_fp16 = (self.device == "cuda")
        if use_fp16:
            lpips_net = lpips_net.half()

        match_rows = []

        for f_idx, f_name in enumerate(tqdm(frame_names, desc="Selecting Reference Photos")):
            f_clip_emb = frame_clip[f_idx]
            f_scene_emb = scene_clip[f_idx]
            f_face = frame_faces.get(f_name)
            
            f_img = cv2.imread(str(self.frames_dir / f_name))
            f_hist = compute_histogram(f_img) if f_img is not None else None
            
            # Step A: Coarse search
            clip_sims = np.dot(album_clip, f_clip_emb)
            scene_sims = np.dot(album_clip, f_scene_emb)
            
            face_sims = np.zeros(len(album_names))
            has_face_pair = np.zeros(len(album_names), dtype=bool)
            
            if f_face is not None:
                f_face_emb = f_face["embedding"]
                for a_idx, a_name in enumerate(album_names):
                    a_face = album_faces.get(a_name)
                    if a_face is not None:
                        sim = np.dot(f_face_emb, a_face["embedding"])
                        face_sims[a_idx] = max(0.0, float(sim))
                        has_face_pair[a_idx] = True

            w_face = self.weights["face"]
            w_clip = self.weights["clip"]
            w_scene = self.weights["scene"]
            
            coarse_scores = np.zeros(len(album_names))
            for a_idx in range(len(album_names)):
                eff_w_face = w_face if has_face_pair[a_idx] else 0.0
                eff_w_clip = w_clip + (w_face - eff_w_face)
                coarse_scores[a_idx] = (
                    eff_w_face * face_sims[a_idx] +
                    eff_w_clip * clip_sims[a_idx] +
                    w_scene * scene_sims[a_idx]
                )

            # Step B: Fine selection on top 10
            top_10_indices = np.argsort(coarse_scores)[::-1][:10]
            
            best_candidates = []
            f_tensor = self._preprocess_lpips(self.frames_dir / f_name).to(self.device)
            if use_fp16:
                f_tensor = f_tensor.half()
                
            with torch.inference_mode():
                f_feats = lpips_net(f_tensor)

            for a_idx in top_10_indices:
                a_name = album_names[a_idx]
                
                a_img = cv2.imread(str(self.albums_dir / a_name))
                a_hist = compute_histogram(a_img) if a_img is not None else None
                color_sim = histogram_similarity(f_hist, a_hist) if (f_hist is not None and a_hist is not None) else 0.0
                
                a_tensor = self._preprocess_lpips(self.albums_dir / a_name).to(self.device)
                if use_fp16:
                    a_tensor = a_tensor.half()
                    
                with torch.inference_mode():
                    a_feats = lpips_net(a_tensor)
                    
                lpips_dist = 0.0
                for feat_f, feat_a in zip(f_feats, a_feats):
                    diff = (feat_f - feat_a) ** 2
                    lpips_dist += float(diff.mean().cpu().item())
                lpips_sim = max(0.0, 1.0 - (lpips_dist * 2.0))
                
                eff_w_face = w_face if has_face_pair[a_idx] else 0.0
                w_other = w_clip + w_scene + self.weights["color"] + self.weights["lpips"]
                eff_w_clip = w_clip + (w_face - eff_w_face) * (w_clip / w_other)
                eff_w_scene = w_scene + (w_face - eff_w_face) * (w_scene / w_other)
                eff_w_color = self.weights["color"] + (w_face - eff_w_face) * (self.weights["color"] / w_other)
                eff_w_lpips = self.weights["lpips"] + (w_face - eff_w_face) * (self.weights["lpips"] / w_other)
                
                final_score = (
                    eff_w_face * face_sims[a_idx] +
                    eff_w_clip * clip_sims[a_idx] +
                    eff_w_scene * scene_sims[a_idx] +
                    eff_w_color * color_sim +
                    eff_w_lpips * lpips_sim
                )
                
                best_candidates.append({
                    "album": a_name,
                    "clip_score": float(clip_sims[a_idx]),
                    "face_score": float(face_sims[a_idx]) if has_face_pair[a_idx] else 0.0,
                    "scene_score": float(scene_sims[a_idx]),
                    "color_score": float(color_sim),
                    "lpips_score": float(lpips_sim),
                    "final_score": float(final_score)
                })

            best_candidates = sorted(best_candidates, key=lambda x: x["final_score"], reverse=True)[:self.top_k]
            
            for rank, cand in enumerate(best_candidates):
                match_rows.append([
                    f_name,
                    rank + 1,
                    cand["album"],
                    f"{cand['clip_score']:.4f}",
                    f"{cand['face_score']:.4f}",
                    f"{cand['scene_score']:.4f}",
                    f"{cand['color_score']:.4f}",
                    f"{cand['lpips_score']:.4f}",
                    f"{cand['final_score']:.4f}"
                ])
                
        # Save output to CSV
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Frame", "Rank", "AlbumImage", "CLIPScore", "FaceScore",
                "SceneScore", "ColorScore", "LPIPSScore", "FinalScore"
            ])
            writer.writerows(match_rows)
            
        logger.info(f"Reference selection complete. Saved results to {out_csv}")
        del lpips_net
        if self.device == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 5: Reference Selection Module")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of matching CSV")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = ReferenceSelectorStage(cfg)
    stage.run(force=args.force)
