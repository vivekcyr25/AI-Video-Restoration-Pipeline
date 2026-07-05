"""
utils/matcher_utils.py
======================
Shared helper functions for embedding loading, normalization, and
cosine similarity computation used across matching scripts.

These utilities are extracted so they can be reused or tested independently
without importing the full pipeline scripts.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import numpy as np

EPSILON = 1e-12


# ─────────────────────────────────────────────────────────────────────────────
#  Embedding I/O
# ─────────────────────────────────────────────────────────────────────────────

def safe_load_npy(path: Path, allow_pickle: bool = False) -> np.ndarray | None:
    """Load a .npy file, returning None on any error (file not found, corrupt, etc.)."""
    if not path.exists():
        return None
    try:
        return np.load(path, allow_pickle=allow_pickle)
    except Exception:
        return None


def load_names(path: Path) -> list[str]:
    """
    Load a string-array .npy file as a Python list.

    Returns an empty list if the file is missing or malformed.
    """
    data = safe_load_npy(path, allow_pickle=True)
    if data is None:
        return []
    try:
        return [str(item) for item in data.tolist()]
    except Exception:
        return []


def load_embeddings(path: Path) -> np.ndarray:
    """
    Load a 2-D float32 embedding matrix from a .npy file.

    Returns an empty (0, 0) float32 array on any failure.
    """
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


def align_embeddings(
    embeddings: np.ndarray,
    names: list[str],
) -> tuple[np.ndarray, list[str]]:
    """
    Trim embeddings and names to the shorter of the two lengths.

    Required because .npy file pairs may have slight length mismatches
    due to errors during generation (skipped images).
    """
    n = min(len(embeddings), len(names))
    if n <= 0:
        w = embeddings.shape[1] if embeddings.ndim == 2 and embeddings.shape[1] > 0 else 0
        return np.empty((0, w), dtype=np.float32), []
    return embeddings[:n], names[:n]


# ─────────────────────────────────────────────────────────────────────────────
#  Normalization
# ─────────────────────────────────────────────────────────────────────────────

def normalize_embeddings(embeddings: np.ndarray, epsilon: float = EPSILON) -> np.ndarray:
    """
    Row-wise L2 normalization of a 2-D embedding matrix.

    Zero-norm rows are left as zero vectors (not normalized).

    Args:
        embeddings: Shape (N, D) float32 array.
        epsilon:    Minimum norm threshold for a valid row.

    Returns:
        Shape (N, D) float32 array with unit-norm rows.
    """
    if embeddings.size == 0:
        return embeddings.astype(np.float32, copy=False)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    valid = norms[:, 0] > epsilon
    normalized = np.zeros_like(embeddings, dtype=np.float32)
    normalized[valid] = embeddings[valid] / norms[valid]
    return normalized


# ─────────────────────────────────────────────────────────────────────────────
#  Similarity
# ─────────────────────────────────────────────────────────────────────────────

def cosine_similarity_matrix(
    query: np.ndarray,
    gallery: np.ndarray,
) -> np.ndarray:
    """
    Compute a (N_query, N_gallery) cosine similarity matrix.

    Both arrays must already be L2-normalized (use ``normalize_embeddings``
    first). The result is simply the matrix product query @ gallery.T.

    Returns an empty array if the arrays are incompatible.
    """
    if (
        query.ndim != 2 or gallery.ndim != 2
        or query.shape[0] == 0 or gallery.shape[0] == 0
        or query.shape[1] == 0 or query.shape[1] != gallery.shape[1]
    ):
        return np.empty((0, 0), dtype=np.float32)
    return (query @ gallery.T).astype(np.float32)


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """
    Return the indices of the top-k highest scores in *scores*.

    Uses ``np.argpartition`` for O(N) rather than O(N log N) performance.

    Args:
        scores: 1-D float array.
        k:      Number of top results to return.

    Returns:
        1-D int64 array of length min(k, len(scores)), sorted descending.
    """
    if scores.size == 0:
        return np.array([], dtype=np.int64)
    k = min(k, scores.size)
    idx = np.argpartition(-scores, k - 1)[:k]
    return idx[np.argsort(-scores[idx])]


# ─────────────────────────────────────────────────────────────────────────────
#  Face map helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_face_map(csv_path: Path) -> dict[str, int]:
    """
    Parse an InsightFace embedding-index CSV into {image_name: row_index}.

    Handles both header and header-less CSVs. Returns an empty dict on error.
    """
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
                name_key = _find_col(fields, ("name", "image", "frame", "file", "path"))
                idx_key  = _find_col(fields, ("index", "embedding", "face", "id"))
                for rn, row in enumerate(reader):
                    name = _clean(row.get(name_key)) if name_key else None
                    idx  = _parse_int(row.get(idx_key)) if idx_key else rn
                    if name and idx is not None:
                        face_map[name] = idx
            else:
                for rn, row in enumerate(csv.reader(fh)):
                    if not row:
                        continue
                    name = _clean(row[0])
                    idx  = _parse_int(row[1]) if len(row) > 1 else rn
                    if name and idx is not None:
                        face_map[name] = idx
    except Exception:
        return {}
    return face_map


def build_face_lookup(
    face_names: list[str],
    face_map: dict[str, int],
    total_embeddings: int,
) -> dict[str, int]:
    """
    Build a {filename → embedding_row_index} lookup table.

    Merges the name-array ordering with CSV-overridden indices, indexed
    by both full path and basename for flexible key resolution.
    """
    lookup: dict[str, int] = {}
    for i, name in enumerate(face_names[:total_embeddings]):
        if name:
            lookup.setdefault(name, i)
            lookup.setdefault(os.path.basename(name), i)
    for name, idx in face_map.items():
        if 0 <= idx < total_embeddings:
            lookup[name] = idx
            lookup[os.path.basename(name)] = idx
    return lookup


def get_face_index(name: str, lookup: dict[str, int]) -> int | None:
    """Resolve *name* (or its basename) to an embedding row index, or None."""
    return lookup.get(name, lookup.get(os.path.basename(name)))


# ─────────────────────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _find_col(columns: list[str], candidates: tuple[str, ...]) -> str | None:
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
