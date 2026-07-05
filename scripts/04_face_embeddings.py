#!/usr/bin/env python3
"""
Stage 3B — Face Identity Embedding Generation
==============================================
Detects the largest face in each album photo and representative frame
using InsightFace (RetinaFace detector + ArcFace ResNet-50 backbone),
then saves 512-dimensional identity embeddings.

These face embeddings are later combined with CLIP embeddings in the
hybrid matcher (Stage 4) to improve matching accuracy for person-centric
wedding footage.

Usage
-----
    python scripts/04_face_embeddings.py [--albums ALBUMS_DIR]
                                          [--frames FRAMES_DIR]
                                          [--models MODELS_DIR]
                                          [--gpu]

Outputs (written to MODELS_DIR)
-------------------------------
    album_face_embeddings.npy  — shape (N_album_faces, 512), float32
    album_face_names.npy       — shape (N_album_faces,), str
    album_face_names.csv       — metadata: image, embedding_index, bbox, score
    frame_face_embeddings.npy  — shape (N_frame_faces, 512), float32
    frame_face_names.npy       — shape (N_frame_faces,), str
    frame_face_names.csv       — metadata: image, embedding_index, bbox, score

Notes
-----
- Only the **largest** face per image is extracted (wedding primary subject).
- Images with no detected face are skipped (not included in output arrays).
- The buffalo_l model (~350 MB) is downloaded automatically on first run.

Requirements
------------
    pip install insightface onnxruntime opencv-python numpy pandas tqdm
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from insightface.app import FaceAnalysis
from tqdm import tqdm

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DETECTION_SIZE = (640, 640)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate InsightFace face embeddings for albums and frames."
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
        "--gpu",
        action="store_true",
        help="Use CUDA GPU for inference (requires onnxruntime-gpu).",
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


def extract_embeddings(
    images: list[Path],
    analyzer: FaceAnalysis,
) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """
    Detect the largest face in each image and extract its ArcFace embedding.

    Returns
    -------
    embeddings : np.ndarray, shape (N_faces, 512), float32
    names      : np.ndarray, shape (N_faces,), str
    mapping    : list[dict], bounding box + score metadata per face
    """
    embeddings: list[np.ndarray] = []
    names: list[str] = []
    mapping: list[dict] = []

    for img_path in tqdm(images, unit="img"):
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                continue

            faces = analyzer.get(img)
            if not faces:
                continue

            # Select largest face by bounding-box area (primary subject)
            face = max(
                faces,
                key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
            )

            idx = len(embeddings)
            embeddings.append(face.embedding.astype(np.float32))
            names.append(img_path.name)
            mapping.append(
                {
                    "image": img_path.name,
                    "embedding_index": idx,
                    "x1": float(face.bbox[0]),
                    "y1": float(face.bbox[1]),
                    "x2": float(face.bbox[2]),
                    "y2": float(face.bbox[3]),
                    "score": float(face.det_score),
                }
            )
        except Exception as exc:
            print(f"  Skipped {img_path.name} → {exc}")

    arr = np.array(embeddings, dtype=np.float32) if embeddings else np.empty((0, 512), dtype=np.float32)
    return arr, np.array(names), mapping


def save_embeddings(
    models_dir: Path,
    prefix: str,
    embeddings: np.ndarray,
    names: np.ndarray,
    mapping: list[dict],
) -> None:
    """Persist embeddings, name array, and CSV metadata to *models_dir*."""
    emb_path  = models_dir / f"{prefix}_face_embeddings.npy"
    name_path = models_dir / f"{prefix}_face_names.npy"
    csv_path  = models_dir / f"{prefix}_face_names.csv"

    np.save(emb_path, embeddings)
    np.save(name_path, names)
    pd.DataFrame(mapping).to_csv(csv_path, index=False)

    print(f"  Saved {len(embeddings)} embeddings → {emb_path.name}")
    print(f"  Saved name list          → {name_path.name}")
    print(f"  Saved CSV manifest       → {csv_path.name}")


def main() -> None:
    args = parse_args()
    args.models.mkdir(parents=True, exist_ok=True)

    ctx_id = 0 if args.gpu else -1
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if args.gpu
        else ["CPUExecutionProvider"]
    )

    print("Loading InsightFace buffalo_l model…")
    analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
    analyzer.prepare(ctx_id=ctx_id, det_size=DETECTION_SIZE)

    # ── Album photos ────────────────────────────────────────────────────────
    album_images = get_images(args.albums)
    print(f"\nAlbum images  : {len(album_images)}")
    print("Extracting album face embeddings…")
    emb, names, mapping = extract_embeddings(album_images, analyzer)
    save_embeddings(args.models, "album", emb, names, mapping)

    # ── Representative frames ────────────────────────────────────────────────
    frame_images = get_images(args.frames)
    print(f"\nFrame images  : {len(frame_images)}")
    print("Extracting frame face embeddings…")
    emb, names, mapping = extract_embeddings(frame_images, analyzer)
    save_embeddings(args.models, "frame", emb, names, mapping)

    print("\n" + "=" * 60)
    print("FACE EMBEDDINGS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
