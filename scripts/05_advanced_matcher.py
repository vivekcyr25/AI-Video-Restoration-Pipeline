#!/usr/bin/env python3
"""
Stage 4 — Hybrid Frame–Album Matching
======================================
Matches each representative video frame to the top-K most similar album
photos using a weighted combination of:

    - CLIP semantic similarity  (weight = 0.30)
    - InsightFace identity similarity  (weight = 0.70)

Face scoring is applied only when a face was detected in both the frame
and the album candidate. Otherwise, pure CLIP cosine similarity is used.

The resulting ranked CSV is consumed by restoration stages 5A and 5B.

Usage
-----
    python scripts/05_advanced_matcher.py [--models MODELS_DIR]
                                           [--output OUTPUT_DIR]
                                           [--top-k K]
                                           [--face-weight W]

Outputs
-------
    output/advanced_matches.csv
        Columns: Frame, Rank, AlbumImage, CLIPScore, FaceScore, FinalScore

Requirements
------------
    pip install numpy pandas tqdm
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import numpy as np
from tqdm import tqdm

EPSILON = 1e-12


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hybrid CLIP + face frame-to-album matcher.")
    p.add_argument(
        "--models",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models",
        help="Directory containing .npy embedding files.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "output",
        help="Directory where advanced_matches.csv is written.",
    )
    p.add_argument("--top-k", type=int, default=5, help="Number of top matches to retain per frame.")
    p.add_argument(
        "--face-weight",
        type=float,
        default=0.70,
        help="Weight for face similarity score (CLIP weight = 1 - face_weight).",
    )
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
#  Embedding I/O utilities
# ─────────────────────────────────────────────────────────────────────────────

def safe_load_npy(path: Path, allow_pickle: bool = False) -> np.ndarray | None:
    """Load a .npy file, returning None on any error."""
    if not path.exists():
        return None
    try:
        return np.load(path, allow_pickle=allow_pickle)
    except Exception:
        return None


def load_names(path: Path) -> list[str]:
    """Load a string-array .npy file as a plain Python list."""
    data = safe_load_npy(path, allow_pickle=True)
    if data is None:
        return []
    try:
        return [str(item) for item in data.tolist()]
    except Exception:
        return []


def load_embeddings(path: Path) -> np.ndarray:
    """Load a 2-D float32 embedding matrix. Returns an empty array on failure."""
    data = safe_load_npy(path)
    if data is None:
        return np.empty((0, 0), dtype=np.float32)
    try:
        data = np.asarray(data, dtype=np.float32)
    except Exception:
        return np.empty((0, 0), dtype=np.float32)

    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.ndim != 2 or data.shape[0] == 0 or data.shape[1] == 0:
        return np.empty((0, 0), dtype=np.float32)
    return data


def align(embeddings: np.ndarray, names: list[str]) -> tuple[np.ndarray, list[str]]:
    """Trim to the smaller of the two lengths."""
    n = min(len(embeddings), len(names))
    if n <= 0:
        w = embeddings.shape[1] if embeddings.ndim == 2 and embeddings.shape[1] > 0 else 0
        return np.empty((0, w), dtype=np.float32), []
    return embeddings[:n], names[:n]


def normalize(embeddings: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalization (no-op for zero vectors)."""
    if embeddings.size == 0:
        return embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    valid = norms[:, 0] > EPSILON
    out = np.zeros_like(embeddings, dtype=np.float32)
    out[valid] = embeddings[valid] / norms[valid]
    return out


# ─────────────────────────────────────────────────────────────────────────────
#  Face map (CSV-based embedding-index look-up)
# ─────────────────────────────────────────────────────────────────────────────

def load_face_map(csv_path: Path) -> dict[str, int]:
    """Parse the face-names CSV into {image_filename: embedding_row_index}."""
    face_map: dict[str, int] = {}
    if not csv_path.exists():
        return face_map
    try:
        with csv_path.open("r", newline="", encoding="utf-8-sig") as fh:
            sample = fh.read(4096)
            fh.seek(0)
            has_header = csv.Sniffer().has_header(sample) if sample.strip() else False
            if has_header:
                reader = csv.DictReader(fh)
                fields = reader.fieldnames or []
                name_key = _find_column(fields, ("name", "image", "frame", "file", "path"))
                idx_key = _find_column(fields, ("index", "embedding", "face", "id"))
                for rn, row in enumerate(reader):
                    name = _clean(row.get(name_key)) if name_key else None
                    idx = _parse_int(row.get(idx_key)) if idx_key else rn
                    if name and idx is not None:
                        face_map[name] = idx
            else:
                reader = csv.reader(fh)
                for rn, row in enumerate(reader):
                    if not row:
                        continue
                    name = _clean(row[0])
                    idx = _parse_int(row[1]) if len(row) > 1 else rn
                    if name and idx is not None:
                        face_map[name] = idx
    except Exception:
        return {}
    return face_map


def _find_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    lowered = {c.lower().strip(): c for c in columns}
    for cand in candidates:
        for key, orig in lowered.items():
            if cand in key:
                return orig
    return columns[0] if columns else None


def _clean(value: object) -> str | None:
    if value is None:
        return None
    v = str(value).strip()
    return v if v else None


def _parse_int(value: object) -> int | None:
    try:
        return int(str(value).strip())
    except Exception:
        return None


def build_face_lookup(
    face_names: list[str],
    face_map: dict[str, int],
    total: int,
) -> dict[str, int]:
    """Build {filename: embedding_row_index} lookup from names array + CSV override."""
    lookup: dict[str, int] = {}
    for i, name in enumerate(face_names[:total]):
        if name:
            lookup.setdefault(name, i)
            lookup.setdefault(os.path.basename(name), i)
    for name, idx in face_map.items():
        if 0 <= idx < total:
            lookup[name] = idx
            lookup[os.path.basename(name)] = idx
    return lookup


def get_face_index(name: str, lookup: dict[str, int]) -> int | None:
    return lookup.get(name, lookup.get(os.path.basename(name)))


# ─────────────────────────────────────────────────────────────────────────────
#  Scoring
# ─────────────────────────────────────────────────────────────────────────────

def compatible(a: np.ndarray, b: np.ndarray) -> bool:
    return (
        a.ndim == 2 and b.ndim == 2
        and a.shape[0] > 0 and b.shape[0] > 0
        and a.shape[1] > 0 and a.shape[1] == b.shape[1]
    )


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    if scores.size == 0:
        return np.array([], dtype=np.int64)
    k = min(k, scores.size)
    idx = np.argpartition(-scores, k - 1)[:k]
    return idx[np.argsort(-scores[idx])]


def score_frame(
    frame_name: str,
    clip_scores: np.ndarray,
    frame_face_emb: np.ndarray,
    album_face_emb: np.ndarray,
    frame_face_lookup: dict[str, int],
    album_face_indices: list[list[int]],
    face_weight: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute per-album face scores and weighted final scores for one frame.

    Returns
    -------
    face_scores  : (N_album,) float32, NaN where no face match
    final_scores : (N_album,) float32
    """
    clip_weight = 1.0 - face_weight
    fi = get_face_index(frame_name, frame_face_lookup)
    has_face = (
        fi is not None
        and 0 <= fi < len(frame_face_emb)
        and len(album_face_emb) > 0
        and frame_face_emb.shape[1] == album_face_emb.shape[1]
    )

    face_scores = np.full_like(clip_scores, np.nan, dtype=np.float32)

    if not has_face:
        return face_scores, clip_scores.astype(np.float32)

    all_face = album_face_emb @ frame_face_emb[fi]
    for ai, indices in enumerate(album_face_indices):
        if indices:
            face_scores[ai] = float(np.max(all_face[indices]))

    valid = ~np.isnan(face_scores)
    final = clip_scores.astype(np.float32, copy=True)
    final[valid] = face_weight * face_scores[valid] + clip_weight * clip_scores[valid]
    return face_scores, final


def fmt(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return f"{float(value):.6f}"


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    print("Loading embeddings…")
    album_emb   = normalize(align(*[load_embeddings(args.models / "album_embeddings.npy"),  load_names(args.models / "album_names.npy")])[0:1])[0] if False else normalize(load_embeddings(args.models / "album_embeddings.npy"))
    # Reload cleanly
    raw_album_emb,  album_names   = align(load_embeddings(args.models / "album_embeddings.npy"),  load_names(args.models / "album_names.npy"))
    raw_frame_emb,  frame_names   = align(load_embeddings(args.models / "frames_embeddings.npy"), load_names(args.models / "frames_names.npy"))
    raw_af_emb,     album_fn      = align(load_embeddings(args.models / "album_face_embeddings.npy"), load_names(args.models / "album_face_names.npy"))
    raw_ff_emb,     frame_fn      = align(load_embeddings(args.models / "frame_face_embeddings.npy"), load_names(args.models / "frame_face_names.npy"))

    album_emb = normalize(raw_album_emb)
    frame_emb = normalize(raw_frame_emb)
    af_emb    = normalize(raw_af_emb)
    ff_emb    = normalize(raw_ff_emb)

    print("Loading face maps…")
    af_map = load_face_map(args.models / "album_face_names.csv")
    ff_map = load_face_map(args.models / "frame_face_names.csv")
    af_lookup = build_face_lookup(album_fn, af_map, len(af_emb))
    ff_lookup = build_face_lookup(frame_fn, ff_map, len(ff_emb))

    album_face_indices: list[list[int]] = []
    for an in album_names:
        fi = get_face_index(an, af_lookup)
        album_face_indices.append([fi] if fi is not None and 0 <= fi < len(af_emb) else [])

    print("Matching…")
    rows: list[dict] = []

    if compatible(frame_emb, album_emb):
        clip_sim = frame_emb @ album_emb.T  # (N_frames, N_album)
        for i in tqdm(range(len(frame_names)), desc="Frames", unit="frame"):
            face_s, final_s = score_frame(
                frame_names[i], clip_sim[i], ff_emb, af_emb,
                ff_lookup, album_face_indices, args.face_weight,
            )
            for rank, ai in enumerate(top_k_indices(final_s, args.top_k), start=1):
                rows.append({
                    "Frame":      frame_names[i],
                    "Rank":       rank,
                    "AlbumImage": album_names[ai],
                    "CLIPScore":  fmt(clip_sim[i][ai]),
                    "FaceScore":  fmt(face_s[ai]),
                    "FinalScore": fmt(final_s[ai]),
                })
    else:
        print("WARNING: Embedding arrays are incompatible — no matches written.")

    out_csv = args.output / "advanced_matches.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["Frame", "Rank", "AlbumImage", "CLIPScore", "FaceScore", "FinalScore"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} match rows → {out_csv}")
    print("Completed.")


if __name__ == "__main__":
    main()
