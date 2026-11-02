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

Optimizations applied (Step 2 — Python-level):
  2.1 — Eliminated .cpu().item() inside LPIPS loop: accumulate on-GPU tensor and
         transfer a single scalar per candidate.
  2.2 — Batched CLIP/ArcFace matrix similarity: numpy matrix–vector ops replace
         per-element Python loops.
  2.3 — Persistent .npz album feature cache keyed by album composite SHA-256 hash;
         album VGG features and histograms are computed once and reloaded on
         subsequent runs without disk I/O for cv2.imread or model inference.
  2.4 — Vectorized score fusion: numpy broadcasting replaces per-element Python
         arithmetic inside the coarse scoring loop.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import os
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils.image_utils import compute_histogram, histogram_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reference_selector")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dir_sha256(dir_path: Path) -> str:
    """Deterministic composite SHA-256 of all file names + sizes in a directory."""
    h = hashlib.sha256()
    for p in sorted(dir_path.glob("*")):
        if p.is_file():
            h.update(p.name.encode("utf-8"))
            h.update(str(p.stat().st_size).encode("utf-8"))
    return h.hexdigest()


class ReferenceSelectorStage:
    def __init__(self, config: dict):
        import torch
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

    def _preprocess_lpips_from_img(self, img: np.ndarray):
        import torch
        if img is None:
            return torch.zeros((1, 3, 224, 224), dtype=torch.float32)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        # Scale to [-1, 1]
        tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 127.5 - 1.0
        return tensor.unsqueeze(0)

    def _preprocess_lpips(self, img_path: Path):
        img = cv2.imread(str(img_path))
        return self._preprocess_lpips_from_img(img)

    def run(self, force: bool = False) -> None:
        import torch
        import torchvision.models as models

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

        # ── OPT 2.2: Pre-build ArcFace embedding matrix for album (N, D) ──
        # Stack all album ArcFace embeddings into a matrix to allow batched
        # matrix–vector cosine similarity instead of per-element Python loops.
        album_face_emb_matrix = None
        album_has_face = np.zeros(len(album_names), dtype=bool)
        if album_faces:
            emb_dim = next(iter(album_faces.values()))["embedding"].shape[0]
            album_face_emb_matrix = np.zeros((len(album_names), emb_dim), dtype=np.float32)
            for a_idx, a_name in enumerate(album_names):
                a_face = album_faces.get(a_name)
                if a_face is not None:
                    album_face_emb_matrix[a_idx] = a_face["embedding"]
                    album_has_face[a_idx] = True
        
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

        # ── OPT 2.3: Persistent album feature cache (.npz) ──────────────────
        # Cache is keyed by a composite hash of album directory contents so
        # it is automatically invalidated when album photos change.
        cache_dir = self.models_dir
        album_hash = _dir_sha256(self.albums_dir)
        cache_path = cache_dir / f"album_vgg_cache_{album_hash[:16]}.npz"

        if cache_path.exists() and not force:
            logger.info(f"Loading album VGG feature cache: {cache_path.name}")
            _cache = np.load(cache_path, allow_pickle=True)
            album_hists = _cache["album_hists"].item()
            # Reload tensors from numpy arrays stored in the cache
            _feat1 = _cache["feats_slice1"]   # (N, C, H, W) float16 or float32
            _feat2 = _cache["feats_slice2"]
            _feat3 = _cache["feats_slice3"]
            # Rebuild per-album dict for convenient access in the per-frame loop
            album_vgg_feats = {}
            for a_idx, a_name in enumerate(album_names):
                album_vgg_feats[a_name] = [
                    torch.from_numpy(_feat1[a_idx]).to(self.device),
                    torch.from_numpy(_feat2[a_idx]).to(self.device),
                    torch.from_numpy(_feat3[a_idx]).to(self.device),
                ]
        else:
            # Precompute album histograms and VGG features to prevent redundant disk I/O and model inferences
            logger.info("Precomputing histograms and VGG perceptual features for all album images...")
            album_hists = {}
            album_vgg_feats = {}
            raw_feats1, raw_feats2, raw_feats3 = [], [], []
            for a_name in album_names:
                a_path = self.albums_dir / a_name
                a_img = cv2.imread(str(a_path))
                if a_img is not None:
                    album_hists[a_name] = compute_histogram(a_img)
                    a_tensor = self._preprocess_lpips_from_img(a_img).to(self.device)
                    if use_fp16:
                        a_tensor = a_tensor.half()
                    with torch.inference_mode():
                        feats = lpips_net(a_tensor)
                    album_vgg_feats[a_name] = feats
                    raw_feats1.append(feats[0].cpu().numpy())
                    raw_feats2.append(feats[1].cpu().numpy())
                    raw_feats3.append(feats[2].cpu().numpy())
                else:
                    album_hists[a_name] = None
                    album_vgg_feats[a_name] = None
                    raw_feats1.append(None)
                    raw_feats2.append(None)
                    raw_feats3.append(None)

            # Save cache — only when at least one valid feature was computed
            valid = [i for i, f in enumerate(raw_feats1) if f is not None]
            if valid:
                # Pad None entries with zeros to keep array structure consistent
                ref_shape1 = raw_feats1[valid[0]].shape
                ref_shape2 = raw_feats2[valid[0]].shape
                ref_shape3 = raw_feats3[valid[0]].shape
                arr1 = np.stack([raw_feats1[i] if raw_feats1[i] is not None else np.zeros(ref_shape1, dtype=np.float16) for i in range(len(album_names))])
                arr2 = np.stack([raw_feats2[i] if raw_feats2[i] is not None else np.zeros(ref_shape2, dtype=np.float16) for i in range(len(album_names))])
                arr3 = np.stack([raw_feats3[i] if raw_feats3[i] is not None else np.zeros(ref_shape3, dtype=np.float16) for i in range(len(album_names))])
                np.savez(
                    cache_path,
                    album_hists=np.array(album_hists, dtype=object),
                    feats_slice1=arr1,
                    feats_slice2=arr2,
                    feats_slice3=arr3,
                )
                logger.info(f"Saved album VGG feature cache: {cache_path.name}")

        match_rows = []

        for f_idx, f_name in enumerate(tqdm(frame_names, desc="Selecting Reference Photos")):
            f_clip_emb = frame_clip[f_idx]
            f_scene_emb = scene_clip[f_idx]
            f_face = frame_faces.get(f_name)
            
            f_img = cv2.imread(str(self.frames_dir / f_name))
            if f_img is None:
                continue
            f_hist = compute_histogram(f_img)

            # ── OPT 2.2: Batched CLIP and scene similarity (matrix–vector) ───
            # Single np.dot call replaces 65-iteration Python loop.
            clip_sims = np.dot(album_clip, f_clip_emb)        # (N,)
            scene_sims = np.dot(album_clip, f_scene_emb)      # (N,)

            # ── OPT 2.2: Batched ArcFace similarity ───────────────────────
            face_sims = np.zeros(len(album_names), dtype=np.float32)
            has_face_pair = np.zeros(len(album_names), dtype=bool)
            if f_face is not None and album_face_emb_matrix is not None:
                f_face_emb = f_face["embedding"].astype(np.float32)
                raw_face_sims = album_face_emb_matrix @ f_face_emb   # (N,) matrix–vector
                face_sims = np.maximum(0.0, raw_face_sims)
                has_face_pair = album_has_face.copy()

            # ── OPT 2.4: Vectorized coarse score fusion ────────────────────
            w_face = self.weights["face"]
            w_clip = self.weights["clip"]
            w_scene = self.weights["scene"]
            # Effective per-album clip weight: absorbs face weight for albums without a face
            eff_w_face_arr = np.where(has_face_pair, w_face, 0.0)
            eff_w_clip_arr = w_clip + (w_face - eff_w_face_arr)
            coarse_scores = (
                eff_w_face_arr * face_sims +
                eff_w_clip_arr * clip_sims +
                w_scene * scene_sims
            )

            # Step B: Fine selection on top 10
            top_10_indices = np.argsort(coarse_scores)[::-1][:10]
            
            best_candidates = []
            f_tensor = self._preprocess_lpips_from_img(f_img).to(self.device)
            if use_fp16:
                f_tensor = f_tensor.half()
                
            with torch.inference_mode():
                f_feats = lpips_net(f_tensor)

            for a_idx in top_10_indices:
                a_name = album_names[a_idx]
                
                a_hist = album_hists.get(a_name)
                color_sim = histogram_similarity(f_hist, a_hist) if (f_hist is not None and a_hist is not None) else 0.0
                
                a_feats = album_vgg_feats.get(a_name)
                
                # ── OPT 2.1: GPU-resident LPIPS accumulation ─────────────
                # Accumulate squared differences as a CUDA tensor; transfer a
                # single scalar after all layers, eliminating 30 round-trips
                # per frame (3 layers × 10 candidates).
                if f_feats is not None and a_feats is not None:
                    with torch.inference_mode():
                        lpips_dist_tensor = torch.tensor(0.0, device=self.device, dtype=f_feats[0].dtype)
                        for feat_f, feat_a in zip(f_feats, a_feats):
                            diff = (feat_f - feat_a) ** 2
                            lpips_dist_tensor = lpips_dist_tensor + diff.mean()
                        # Single transfer for the whole candidate
                        lpips_dist = float(lpips_dist_tensor.item())
                    lpips_sim = max(0.0, 1.0 - (lpips_dist * 2.0))
                else:
                    lpips_sim = 0.0
                
                # ── OPT 2.4: Vectorized fine score fusion ─────────────────
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
