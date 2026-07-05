#!/usr/bin/env python3
"""
Stage 5B — Frame Restoration v2 (Face-Affine + Detail Transfer)
================================================================
An upgraded restoration pipeline that uses face-guided affine alignment
for identity-centric detail transfer, falling back gracefully when no
matching faces are detected.

Restoration cascade
-------------------
1. **Face-guided** (best quality): Detects largest face in both frame and album
   photo; computes an affine transform that aligns face scale + position; uses
   a Gaussian-softened face-region mask as the confidence map; transfers high-
   frequency texture detail from the album into the masked region.

2. **Confidence-guided** (fallback): When no face match, computes a global
   texture-based confidence map (edge + gradient + Laplacian) and transfers
   detail proportional to the local confidence.

3. **Adaptive CLAHE-only** (final fallback): When the confidence map is
   too sparse, applies standalone luminance enhancement and bilateral denoising.

Usage
-----
    python scripts/07_restore_frame_v2.py [--csv CSV_PATH]
                                           [--frames FRAMES_DIR]
                                           [--albums ALBUMS_DIR]
                                           [--output OUTPUT_DIR]
                                           [--gpu]

Outputs
-------
    output/Restored_Frames/<frame_name>.jpg
    output/restore_log.csv

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

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
DETECTION_SIZE = (640, 640)


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Face-guided frame restoration v2.")
    p.add_argument("--csv",    type=Path, default=root / "output" / "advanced_matches.csv")
    p.add_argument("--frames", type=Path, default=root / "Representative_Frames")
    p.add_argument("--albums", type=Path, default=root / "Albums")
    p.add_argument("--output", type=Path, default=root / "output")
    p.add_argument("--gpu", action="store_true", help="Use GPU for InsightFace.")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
#  Image I/O
# ─────────────────────────────────────────────────────────────────────────────

def read_image(path: Path) -> np.ndarray | None:
    if not path.exists() or not path.is_file():
        return None
    return cv2.imread(str(path), cv2.IMREAD_COLOR)


def resolve_path(base: Path, root: Path, value: object) -> Path:
    text = "" if pd.isna(value) else str(value).strip()
    p = Path(text)
    if p.is_absolute():
        return p
    for c in (base / p, root / p):
        if c.exists():
            return c
    return base / p


def safe_output_path(frame_name: object, restored_dir: Path) -> Path:
    name = Path(str(frame_name)).name
    if Path(name).suffix.lower() not in SUPPORTED_SUFFIXES:
        name = f"{Path(name).stem}.jpg"
    return restored_dir / name


def save_image(path: Path, image: np.ndarray) -> bool:
    return bool(cv2.imwrite(str(path), image))


# ─────────────────────────────────────────────────────────────────────────────
#  Geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def resize_cover(image: np.ndarray, target: tuple[int, int, int]) -> np.ndarray:
    """Scale+crop *image* to exactly match *target* shape (cover strategy)."""
    th, tw = target[:2]
    sh, sw = image.shape[:2]
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (nw, nh), interpolation=interp)
    x0 = max(0, (nw - tw) // 2)
    y0 = max(0, (nh - th) // 2)
    return resized[y0:y0 + th, x0:x0 + tw].copy()


def to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# ─────────────────────────────────────────────────────────────────────────────
#  Face detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_faces(
    image: np.ndarray,
    analyzer: FaceAnalysis,
) -> list[tuple[int, int, int, int]]:
    """Return a list of (x, y, w, h) face bounding boxes, largest first."""
    h, w = image.shape[:2]
    faces = []
    for det in analyzer.get(image):
        x0, y0, x1, y1 = det.bbox.astype(np.float32)
        x0 = max(0, min(w - 1, int(round(x0))))
        y0 = max(0, min(h - 1, int(round(y0))))
        x1 = max(x0 + 1, min(w, int(round(x1))))
        y1 = max(y0 + 1, min(h, int(round(y1))))
        faces.append((x0, y0, x1 - x0, y1 - y0))
    return sorted(faces, key=lambda b: b[2] * b[3], reverse=True)


def expand_box(box: tuple[int, int, int, int], shape: tuple, scale: float = 1.55):
    x, y, w, h = box
    ih, iw = shape[:2]
    cx, cy = x + w / 2.0, y + h / 2.0
    sz = max(w, h) * scale
    x0 = max(0, min(iw - 1, int(round(cx - sz / 2))))
    y0 = max(0, min(ih - 1, int(round(cy - sz / 2))))
    x1 = max(x0 + 1, min(iw, int(round(cx + sz / 2))))
    y1 = max(y0 + 1, min(ih, int(round(cy + sz / 2))))
    return x0, y0, x1, y1


# ─────────────────────────────────────────────────────────────────────────────
#  Alignment
# ─────────────────────────────────────────────────────────────────────────────

def align_face(
    frame: np.ndarray,
    album: np.ndarray,
    frame_faces: list,
    album_faces: list,
) -> tuple[np.ndarray, np.ndarray, bool]:
    if not frame_faces or not album_faces:
        return album, np.ones(frame.shape[:2], dtype=np.float32), False

    ff, af = frame_faces[0], album_faces[0]
    fcx, fcy = ff[0] + ff[2] / 2.0, ff[1] + ff[3] / 2.0
    acx, acy = af[0] + af[2] / 2.0, af[1] + af[3] / 2.0
    fsc, asc = max(ff[2], ff[3]), max(af[2], af[3])

    if asc <= 1:
        return album, np.ones(frame.shape[:2], dtype=np.float32), False

    s = fsc / asc
    M = np.array([[s, 0.0, fcx - s * acx], [0.0, s, fcy - s * acy]], dtype=np.float32)
    h, w = frame.shape[:2]

    aligned = cv2.warpAffine(album, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    valid_src = np.ones(album.shape[:2], dtype=np.uint8) * 255
    valid = cv2.warpAffine(valid_src, M, (w, h), flags=cv2.INTER_NEAREST,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=0).astype(np.float32) / 255.0

    mask = np.zeros(frame.shape[:2], dtype=np.float32)
    x0, y0, x1, y1 = expand_box(ff, frame.shape, scale=1.85)
    mask[y0:y1, x0:x1] = 1.0
    sigma = max(3.0, (x1 - x0) * 0.035)
    mask = np.clip(cv2.GaussianBlur(mask, (0, 0), sigma) * valid, 0.0, 1.0)

    if np.count_nonzero(mask > 0.05) == 0:
        return album, np.ones(frame.shape[:2], dtype=np.float32), False

    return aligned, mask, True


# ─────────────────────────────────────────────────────────────────────────────
#  Texture / confidence maps
# ─────────────────────────────────────────────────────────────────────────────

def _robust_norm(x: np.ndarray, lo: float = 2.0, hi: float = 98.0) -> np.ndarray:
    x = x.astype(np.float32)
    p_lo, p_hi = float(np.percentile(x, lo)), float(np.percentile(x, hi))
    if p_hi - p_lo < 1e-6:
        mn, mx = float(x.min()), float(x.max())
        return np.zeros_like(x) if mx - mn < 1e-6 else (x - mn) / (mx - mn)
    return np.clip((x - p_lo) / (p_hi - p_lo), 0.0, 1.0)


def texture_map(gray: np.ndarray) -> np.ndarray:
    lap = np.abs(cv2.Laplacian(gray, cv2.CV_32F, ksize=3))
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad = cv2.magnitude(gx, gy)
    gf = gray.astype(np.float32)
    mean = cv2.GaussianBlur(gf, (0, 0), 3.0)
    var = np.maximum(cv2.GaussianBlur(gf * gf, (0, 0), 3.0) - mean * mean, 0.0)
    contrast = np.sqrt(var)
    return 0.45 * _robust_norm(lap) + 0.30 * _robust_norm(contrast) + 0.25 * _robust_norm(grad)


def similarity_map(a: np.ndarray, b: np.ndarray, softness: float = 4.0) -> np.ndarray:
    return np.exp(-softness * _robust_norm(np.abs(a.astype(np.float32) - b.astype(np.float32)))).astype(np.float32)


def confidence_map(
    frame: np.ndarray,
    album: np.ndarray,
    region_mask: np.ndarray | None = None,
) -> np.ndarray:
    fg, ag = to_gray(frame), to_gray(album)
    fe = cv2.Canny(fg, 50, 150).astype(np.float32) / 255.0
    ae = cv2.Canny(ag, 50, 150).astype(np.float32) / 255.0
    edge_sim = 1.0 - cv2.GaussianBlur(np.abs(fe - ae), (0, 0), 1.2)

    def sobel(g):
        return cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3),
                              cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))

    grad_sim = similarity_map(_robust_norm(sobel(fg)), _robust_norm(sobel(ag)), softness=3.0)
    tex_f, tex_a = texture_map(fg), texture_map(ag)
    tex_sim = similarity_map(tex_f, tex_a, softness=3.0)

    conf = (0.30 * edge_sim + 0.35 * grad_sim + 0.35 * tex_sim) * np.clip(0.35 + np.maximum(tex_f, tex_a), 0.0, 1.0)
    if region_mask is not None:
        conf *= np.clip(region_mask.astype(np.float32), 0.0, 1.0)
    conf = np.clip(cv2.GaussianBlur(conf.astype(np.float32), (0, 0), 2.0), 0.0, 1.0)
    conf[conf < 0.08] = 0.0
    return conf


# ─────────────────────────────────────────────────────────────────────────────
#  Enhancement
# ─────────────────────────────────────────────────────────────────────────────

def high_freq(image: np.ndarray, sigma: float = 1.25) -> np.ndarray:
    return image.astype(np.float32) - cv2.GaussianBlur(image, (0, 0), sigma).astype(np.float32)


def transfer_details(frame: np.ndarray, album: np.ndarray, conf: np.ndarray) -> np.ndarray:
    ad, fd = high_freq(album), high_freq(frame)
    gain = np.clip(
        cv2.GaussianBlur(
            np.mean(np.abs(ad), axis=2) / (np.mean(np.abs(fd), axis=2) + 8.0), (0, 0), 1.0
        ), 0.0, 1.25
    )
    w = np.clip(conf * gain * 0.32, 0.0, 0.32)[..., None]
    return np.clip(frame.astype(np.float32) + ad * w, 0, 255).astype(np.uint8)


def apply_clahe(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    return cv2.cvtColor(cv2.merge((cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l), a, b)), cv2.COLOR_LAB2BGR)


def adaptive_enhancement(frame: np.ndarray, conf: np.ndarray | None = None) -> np.ndarray:
    if conf is None:
        g = to_gray(frame)
        conf = cv2.GaussianBlur(np.clip(0.25 + texture_map(g) * 0.65, 0.0, 0.75), (0, 0), 2.0)
    clahe = apply_clahe(frame)
    denoised = cv2.bilateralFilter(clahe, d=5, sigmaColor=32, sigmaSpace=32)
    ff = denoised.astype(np.float32)
    blurred = cv2.GaussianBlur(ff, (0, 0), 1.1)
    strength = np.clip(conf.astype(np.float32) * 0.85, 0.0, 0.85)[..., None]
    sharpened = np.clip(ff + (ff - blurred) * strength, 0, 255).astype(np.uint8)
    blend = np.clip(conf * 0.55, 0.0, 0.55)[..., None]
    return np.clip(frame.astype(np.float32) * (1.0 - blend) + sharpened.astype(np.float32) * blend, 0, 255).astype(np.uint8)


def restore_with_album(
    frame: np.ndarray,
    album: np.ndarray,
    analyzer: FaceAnalysis,
) -> tuple[np.ndarray, str, str]:
    album_r = resize_cover(album, frame.shape)
    ff_faces = detect_faces(frame, analyzer)
    af_faces = detect_faces(album_r, analyzer)
    aligned, mask, face_ok = align_face(frame, album_r, ff_faces, af_faces)

    if face_ok:
        conf = confidence_map(frame, aligned, mask)
        detailed = transfer_details(frame, aligned, conf)
        restored = adaptive_enhancement(detailed, conf)
        w = np.clip(conf * 0.75, 0.0, 0.75)[..., None]
        final = np.clip(frame.astype(np.float32) * (1.0 - w) + restored.astype(np.float32) * w, 0, 255).astype(np.uint8)
        return final, "face_affine_detail_transfer", "face_guided"

    conf = confidence_map(frame, album_r)
    thr = max(float(np.mean(conf)) * 0.65, 0.05)
    if np.count_nonzero(conf > thr) > frame.shape[0] * frame.shape[1] * 0.01:
        detailed = transfer_details(frame, album_r, conf)
        restored = adaptive_enhancement(detailed, conf)
        w = np.clip(conf * 0.45, 0.0, 0.45)[..., None]
        final = np.clip(frame.astype(np.float32) * (1.0 - w) + restored.astype(np.float32) * w, 0, 255).astype(np.uint8)
        return final, "confidence_detail_transfer", "detail_transfer"

    return adaptive_enhancement(frame), "frame_only_adaptive_enhancement", "adaptive_restore"


def fallback_restore(frame: np.ndarray) -> np.ndarray:
    g = to_gray(frame)
    conf = cv2.GaussianBlur(np.clip(0.20 + texture_map(g) * 0.50, 0.0, 0.65), (0, 0), 2.0)
    return adaptive_enhancement(frame, conf)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def process_row(
    row: pd.Series,
    frames_dir: Path,
    albums_dir: Path,
    restored_dir: Path,
    root: Path,
    analyzer: FaceAnalysis,
) -> dict[str, str]:
    fname, aname = row["Frame"], row["AlbumImage"]
    out_path = safe_output_path(fname, restored_dir)

    frame = read_image(resolve_path(frames_dir, root, fname))
    if frame is None:
        return {"Frame": str(fname), "MatchedAlbum": str(aname), "MethodUsed": "load_frame", "Status": "load_failed", "OutputImage": ""}

    album = read_image(resolve_path(albums_dir, root, aname))
    if album is None:
        restored = fallback_restore(frame)
        ok = save_image(out_path, restored)
        return {"Frame": str(fname), "MatchedAlbum": str(aname), "MethodUsed": "frame_only_fallback",
                "Status": "fallback_restore" if ok else "save_failed",
                "OutputImage": str(out_path.relative_to(root)) if ok else ""}

    try:
        restored, method, status = restore_with_album(frame, album, analyzer)
    except Exception:
        restored = fallback_restore(frame)
        method, status = "exception_fallback", "fallback_restore"

    if not save_image(out_path, restored):
        return {"Frame": str(fname), "MatchedAlbum": str(aname), "MethodUsed": "save_output", "Status": "save_failed", "OutputImage": ""}

    return {"Frame": str(fname), "MatchedAlbum": str(aname), "MethodUsed": method,
            "Status": status, "OutputImage": str(out_path.relative_to(root))}


def main() -> None:
    args = parse_args()
    root = args.output.parent
    restored_dir = args.output / "Restored_Frames"
    restored_dir.mkdir(parents=True, exist_ok=True)

    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"] if args.gpu else ["CPUExecutionProvider"]
    )
    print("Loading InsightFace buffalo_l…")
    analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
    analyzer.prepare(ctx_id=0 if args.gpu else -1, det_size=DETECTION_SIZE)

    if not args.csv.exists():
        raise FileNotFoundError(f"Matches CSV not found: {args.csv}")

    data = pd.read_csv(args.csv)
    matches = data.loc[pd.to_numeric(data["Rank"], errors="coerce") == 1].copy()
    matches.reset_index(drop=True, inplace=True)

    log_rows = []
    for _, row in tqdm(matches.iterrows(), total=len(matches), desc="Restoring frames"):
        log_rows.append(process_row(row, args.frames, args.albums, restored_dir, root, analyzer))

    pd.DataFrame(log_rows, columns=["Frame", "MatchedAlbum", "MethodUsed", "Status", "OutputImage"]).to_csv(
        args.output / "restore_log.csv", index=False
    )
    print("Completed.")


if __name__ == "__main__":
    main()
