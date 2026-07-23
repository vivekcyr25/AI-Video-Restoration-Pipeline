"""
pipeline/clip_embedder.py
========================
Stage 3: Batch CLIP Embedding Generation.
Generates 512-dimensional semantic embeddings for album photos and representative frames
using OpenCLIP (ViT-B-32) in FP16 on CUDA. Uses PyTorch DataLoader for async CPU-to-GPU streaming.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("clip_embedder")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class ImageDataset(Dataset):
    """PyTorch Dataset for async image loading and preprocessing."""
    def __init__(self, paths: list[Path], preprocess_fn):
        self.paths = paths
        self.preprocess_fn = preprocess_fn

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, str, int]:
        path = self.paths[idx]
        try:
            img = Image.open(path).convert("RGB")
            tensor = self.preprocess_fn(img)
            return tensor, path.name, 1
        except Exception as e:
            logger.warning(f"Error loading image {path}: {e}")
            # Return dummy tensor on failure
            return torch.zeros(3, 224, 224), path.name, 0


class CLIPEmbedderStage:
    def __init__(self, config: dict):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() and config["global"]["device"] == "cuda" else "cpu"
        self.albums_dir = Path(config["global"]["albums_dir"])
        self.frames_dir = Path(config["frame_extractor"]["output_dir"])
        self.models_dir = Path(config["global"]["models_dir"])
        
        cfg = config["clip_embeddings"]
        self.batch_size = int(cfg["batch_size"])
        self.model_name = cfg["model_name"]
        self.pretrained = cfg["pretrained"]
        
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _get_image_paths(self, folder: Path) -> list[Path]:
        if not folder.exists():
            return []
        return sorted(
            [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS],
            key=lambda x: x.name.lower()
        )

    def _load_existing(self, emb_path: Path, names_path: Path) -> tuple[np.ndarray | None, list[str]]:
        if emb_path.exists() and names_path.exists():
            try:
                emb = np.load(emb_path)
                names = np.load(names_path, allow_pickle=True).tolist()
                # Ensure they are matching in size
                if len(emb) == len(names):
                    return emb, [str(n) for n in names]
            except Exception as e:
                logger.warning(f"Could not load existing embeddings from {emb_path}: {e}")
        return None, []

    def _process_directory(self, folder: Path, out_prefix: str, force: bool = False) -> None:
        emb_path = self.models_dir / f"{out_prefix}_embeddings.npy"
        names_path = self.models_dir / f"{out_prefix}_names.npy"
        
        all_paths = self._get_image_paths(folder)
        if not all_paths:
            logger.warning(f"No images found in {folder}. Skipping.")
            return

        existing_emb, existing_names = (None, []) if force else self._load_existing(emb_path, names_path)
        existing_set = set(existing_names)
        
        # Filter to unprocessed paths
        paths_to_process = [p for p in all_paths if p.name not in existing_set]
        
        if not paths_to_process:
            logger.info(f"All {len(all_paths)} images in {folder} are already embedded. Skipping.")
            return
            
        logger.info(f"Embedding {len(paths_to_process)} / {len(all_paths)} images from {folder}...")
        
        # Load OpenCLIP model
        model, _, preprocess = open_clip.create_model_and_transforms(
            self.model_name, pretrained=self.pretrained
        )
        model = model.to(self.device)
        model.eval()
        
        use_fp16 = (self.device == "cuda")
        if use_fp16:
            model = model.half()
            
        dataset = ImageDataset(paths_to_process, preprocess)
        # Use num_workers=2 or 0 depending on OS. On Windows, 0 is safer and faster in some environments.
        num_workers = 0 if os.name == "nt" else 2
        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=(self.device == "cuda")
        )
        
        new_embeddings = []
        new_names = []
        
        with torch.inference_mode():
            for tensors, names, success_flags in dataloader:
                # Filter valid items
                valid_mask = success_flags == 1
                if not valid_mask.any():
                    continue
                    
                batch_tensors = tensors[valid_mask].to(self.device, non_blocking=True)
                if use_fp16:
                    batch_tensors = batch_tensors.half()
                    
                batch_names = [names[idx] for idx, val in enumerate(valid_mask) if val]
                
                # Inference
                features = model.encode_image(batch_tensors)
                features = features / features.norm(dim=-1, keepdim=True)  # L2 normalise
                
                new_embeddings.append(features.float().cpu().numpy())
                new_names.extend(batch_names)
                
        # Free memory immediately
        del model
        if self.device == "cuda":
            torch.cuda.empty_cache()

        if not new_embeddings:
            logger.warning("No new embeddings were successfully generated.")
            return

        new_emb_arr = np.concatenate(new_embeddings, axis=0)
        
        # Merge if there are existing embeddings
        if existing_emb is not None:
            # Map index by filename to keep sorting aligned
            merged_map = {}
            for name, emb in zip(existing_names, existing_emb):
                merged_map[name] = emb
            for name, emb in zip(new_names, new_emb_arr):
                merged_map[name] = emb
                
            # Reconstruct list sorted by original path name order
            final_names = [p.name for p in all_paths if p.name in merged_map]
            final_emb = np.stack([merged_map[name] for name in final_names], axis=0)
        else:
            final_names = new_names
            final_emb = new_emb_arr

        # Save outputs
        np.save(emb_path, final_emb)
        np.save(names_path, np.array(final_names))
        logger.info(f"Saved {len(final_names)} embeddings to {emb_path}")

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 3: Batch CLIP Embeddings")
        
        # Process albums
        self._process_directory(self.albums_dir, "album", force=force)
        # Process frames
        self._process_directory(self.frames_dir, "frames", force=force)
        
        logger.info("Stage 3 completed.")


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 3: CLIP Embedding Generator")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of all embeddings")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = CLIPEmbedderStage(cfg)
    stage.run(force=args.force)
