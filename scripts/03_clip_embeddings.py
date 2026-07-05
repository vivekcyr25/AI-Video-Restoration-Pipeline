#!/usr/bin/env python3
"""
Stage 3A — CLIP Visual Embedding Generation
============================================
Encodes album photos and representative frames into 512-dimensional
semantic vectors using OpenCLIP ViT-B-32 (pretrained on LAION-2B).

Embeddings are L2-normalised before saving, so downstream cosine
similarity can be computed with a simple dot product.

Usage
-----
    python scripts/03_clip_embeddings.py [--albums ALBUMS_DIR]
                                          [--frames FRAMES_DIR]
                                          [--models MODELS_DIR]

Outputs (written to MODELS_DIR)
-------------------------------
    album_embeddings.npy   — shape (N_album, 512), float32
    album_names.npy        — shape (N_album,), str
    frames_embeddings.npy  — shape (N_frames, 512), float32
    frames_names.npy       — shape (N_frames,), str

Requirements
------------
    pip install open-clip-torch torch Pillow numpy tqdm
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from tqdm import tqdm

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MODEL_NAME = "ViT-B-32"
PRETRAINED = "laion2b_s34b_b79k"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CLIP embeddings for album photos and video frames."
    )
    parser.add_argument(
        "--albums",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Albums",
        help="Directory containing album photos.",
    )
    parser.add_argument(
        "--frames",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Representative_Frames",
        help="Directory containing representative frames.",
    )
    parser.add_argument(
        "--models",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models",
        help="Output directory for .npy embedding files.",
    )
    return parser.parse_args()


def get_images(folder: Path) -> list[Path]:
    """Return a sorted list of image files in *folder*."""
    if not folder.exists():
        raise FileNotFoundError(f"Image directory not found: {folder}")
    return sorted(
        [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS],
        key=lambda x: x.name.lower(),
    )


def create_embeddings(
    images: list[Path],
    model: open_clip.CLIP,
    preprocess,
    device: str,
) -> tuple[np.ndarray, list[str]]:
    """
    Encode a list of image paths into L2-normalised CLIP embeddings.

    Returns
    -------
    embeddings : np.ndarray, shape (N, 512), float32
    names      : list[str], corresponding image filenames
    """
    embeddings: list[np.ndarray] = []
    names: list[str] = []

    for img_path in tqdm(images, unit="img"):
        try:
            image = Image.open(img_path).convert("RGB")
            tensor = preprocess(image).unsqueeze(0).to(device)

            with torch.no_grad():
                emb = model.encode_image(tensor)
                emb /= emb.norm(dim=-1, keepdim=True)  # L2 normalise

            embeddings.append(emb.cpu().numpy()[0])
            names.append(img_path.name)
        except Exception as exc:
            print(f"  Skipped: {img_path.name} → {exc}")

    if not embeddings:
        return np.empty((0, 512), dtype=np.float32), []

    return np.array(embeddings, dtype=np.float32), names


def main() -> None:
    args = parse_args()
    args.models.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print(f"Loading {MODEL_NAME} ({PRETRAINED})…")

    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=PRETRAINED
    )
    model = model.to(device)
    model.eval()

    # ── Album photos ────────────────────────────────────────────────────────
    album_images = get_images(args.albums)
    print(f"\nAlbum images  : {len(album_images)}")
    print("Encoding album photos…")
    album_emb, album_names = create_embeddings(album_images, model, preprocess, device)
    np.save(args.models / "album_embeddings.npy", album_emb)
    np.save(args.models / "album_names.npy", np.array(album_names))
    print(f"  Saved {len(album_names)} album embeddings → {args.models}/album_embeddings.npy")

    # ── Representative frames ────────────────────────────────────────────────
    frame_images = get_images(args.frames)
    print(f"\nFrame images  : {len(frame_images)}")
    print("Encoding representative frames…")
    frame_emb, frame_names = create_embeddings(frame_images, model, preprocess, device)
    np.save(args.models / "frames_embeddings.npy", frame_emb)
    np.save(args.models / "frames_names.npy", np.array(frame_names))
    print(f"  Saved {len(frame_names)} frame embeddings → {args.models}/frames_embeddings.npy")

    print("\nDONE")


if __name__ == "__main__":
    main()
