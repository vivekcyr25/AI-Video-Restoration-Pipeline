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

Performance notes
-----------------
- Use ``--batch-size 64`` on a GPU with >=8 GB VRAM for best throughput.
- On CUDA devices the model is automatically run in FP16 (half precision)
  which halves VRAM usage with negligible quality loss.
- CPU inference defaults to batch size 8 to avoid excessive memory pressure.
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
DEFAULT_BATCH_GPU = 64
DEFAULT_BATCH_CPU = 8


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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help=(
            "Images per inference batch.  0 = auto (64 on GPU, 8 on CPU)."
        ),
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
    batch_size: int = DEFAULT_BATCH_CPU,
) -> tuple[np.ndarray, list[str]]:
    """
    Encode a list of image paths into L2-normalised CLIP embeddings.

    Images are processed in mini-batches to maximise GPU utilisation.
    On CUDA devices the model is cast to FP16 before the first forward
    pass to halve VRAM requirements.

    Returns
    -------
    embeddings : np.ndarray, shape (N, 512), float32
    names      : list[str], corresponding image filenames
    """
    use_fp16 = device.startswith("cuda")
    if use_fp16:
        model = model.half()

    embeddings: list[np.ndarray] = []
    names: list[str] = []

    for i in tqdm(range(0, len(images), batch_size), unit="batch"):
        batch_paths = images[i : i + batch_size]
        tensors = []
        valid_names = []
        for img_path in batch_paths:
            try:
                image = Image.open(img_path).convert("RGB")
                t = preprocess(image)
                tensors.append(t)
                valid_names.append(img_path.name)
            except Exception as exc:
                print(f"  Skipped: {img_path.name} → {exc}")

        if not tensors:
            continue

        batch_tensor = torch.stack(tensors).to(device)
        if use_fp16:
            batch_tensor = batch_tensor.half()

        with torch.no_grad():
            emb = model.encode_image(batch_tensor)
            emb = emb / emb.norm(dim=-1, keepdim=True)  # L2 normalise

        embeddings.append(emb.float().cpu().numpy())
        names.extend(valid_names)

    if not embeddings:
        return np.empty((0, 512), dtype=np.float32), []

    return np.concatenate(embeddings, axis=0).astype(np.float32), names


def main() -> None:
    args = parse_args()
    args.models.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if args.batch_size == 0:
        batch_size = DEFAULT_BATCH_GPU if device.startswith("cuda") else DEFAULT_BATCH_CPU
    else:
        batch_size = args.batch_size

    print(f"Using device: {device}")
    print(f"Batch size  : {batch_size}")
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
    album_emb, album_names = create_embeddings(
        album_images, model, preprocess, device, batch_size=batch_size
    )
    np.save(args.models / "album_embeddings.npy", album_emb)
    np.save(args.models / "album_names.npy", np.array(album_names))
    print(f"  Saved {len(album_names)} album embeddings → {args.models}/album_embeddings.npy")

    # ── Representative frames ────────────────────────────────────────────────
    frame_images = get_images(args.frames)
    print(f"\nFrame images  : {len(frame_images)}")
    print("Encoding representative frames…")
    frame_emb, frame_names = create_embeddings(
        frame_images, model, preprocess, device, batch_size=batch_size
    )
    np.save(args.models / "frames_embeddings.npy", frame_emb)
    np.save(args.models / "frames_names.npy", np.array(frame_names))
    print(f"  Saved {len(frame_names)} frame embeddings → {args.models}/frames_embeddings.npy")

    print("\nDONE")


if __name__ == "__main__":
    main()
