#!/usr/bin/env python3
"""
Stage 5A — Frame Restoration v1 (SIFT Homography)
==================================================
Restores representative video frames by geometrically aligning the best-
matched album photo using SIFT keypoints and RANSAC homography, then
blending high-frequency detail and luminance enhancements into the frame
using a multi-criterion confidence mask.

This is the baseline restoration method. For face-guided restoration see
``07_restore_frame_v2.py`` (Stage 5B).

Pipeline per frame
------------------
1. Load representative frame + best-matched album photo.
2. Resize album preserving aspect ratio, centred on a black canvas.
3. Detect SIFT (or ORB) keypoints on both images.
4. Lowe-ratio test (0.75) → good matches.
5. RANSAC homography → warp album to frame geometry.
6. Build a confidence mask (edge agreement + gradient agreement + pixel diff).
7. Apply CLAHE luminance enhancement (LAB colour space).
8. Bilateral filter + unsharp mask.
9. Confidence-weighted blend: frame × (1 − w) + restored × w.

Usage
-----
    python scripts/06_restore_frame.py [--csv CSV_PATH]
                                        [--frames FRAMES_DIR]
                                        [--albums ALBUMS_DIR]
                                        [--output OUTPUT_DIR]

Outputs
-------
    output/Restored_Frames/frame_XXXX.jpg  — Restored representative frames
    output/restore_log.csv                 — Processing log with status codes

Requirements
------------
    pip install opencv-python numpy pandas tqdm
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

MIN_GOOD_MATCHES = 12
RANSAC_THRESHOLD = 5.0
FRAME_ALPHA = 0.82       # Weight of original frame in final blend
DETAIL_ALPHA = 0.18      # Weight of album high-frequency detail


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Restore frames via SIFT homography alignment.")
    p.add_argument("--csv",     type=Path, default=root / "output" / "advanced_matches.csv")
    p.add_argument("--frames",  type=Path, default=root / "Representative_Frames")
    p.add_argument("--albums",  type=Path, default=root / "Albums")
    p.add_argument("--output",  type=Path, default=root / "output")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
#  Image utilities
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
    for candidate in (base / p, root / p):
        if candidate.exists():
            return candidate
    return base / p


def resize_preserve_aspect(image: np.ndarray, target: tuple[int, int, int]) -> np.ndarray:
    """Resize *image* to fit within *target* shape, centred on a black canvas."""
    th, tw = target[:2]
    sh, sw = image.shape[:2]
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (nw, nh), interpolation=interp)
    canvas = np.zeros((th, tw, 3), dtype=image.dtype)
    y0, x0 = (th - nh) // 2, (tw - nw) // 2
    canvas[y0:y0 + nh, x0:x0 + nw] = resized
    return canvas


# ─────────────────────────────────────────────────────────────────────────────
#  Feature matching & alignment
# ─────────────────────────────────────────────────────────────────────────────

def create_detector() -> tuple[cv2.Feature2D, str]:
    if hasattr(cv2, "SIFT_create"):
        return cv2.SIFT_create(nfeatures=5000), "SIFT"
    return cv2.ORB_create(nfeatures=5000), "ORB"


def match_descriptors(
    desc_frame: np.ndarray,
    desc_album: np.ndarray,
    detector_name: str,
) -> list:
    norm = cv2.NORM_L2 if detector_name == "SIFT" else cv2.NORM_HAMMING
    matcher = cv2.BFMatcher(norm)
    raw = matcher.knnMatch(desc_album, desc_frame, k=2)
    return [m for pair in raw if len(pair) == 2 for m, n in [pair] if m.distance < 0.75 * n.distance]


def align_album_to_frame(
    frame: np.ndarray,
    album: np.ndarray,
) -> tuple[np.ndarray | None, np.ndarray | None, str]:
    """Homography-align *album* to *frame*. Returns (warped, valid_mask, status)."""
    album_r = resize_preserve_aspect(album, frame.shape)
    fg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ag = cv2.cvtColor(album_r, cv2.COLOR_BGR2GRAY)

    detector, name = create_detector()
    kp_f, desc_f = detector.detectAndCompute(fg, None)
    kp_a, desc_a = detector.detectAndCompute(ag, None)

    if desc_f is None or desc_a is None:
        return None, None, "no_descriptors"

    good = match_descriptors(desc_f, desc_a, name)
    if len(good) < MIN_GOOD_MATCHES:
        return None, None, "not_enough_matches"

    src = np.float32([kp_a[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp_f[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, RANSAC_THRESHOLD)

    if H is None or mask is None or int(mask.sum()) < MIN_GOOD_MATCHES:
        return None, None, "homography_failure"

    h, w = frame.shape[:2]
    warped = cv2.warpPerspective(album_r, H, (w, h))
    valid_src = np.ones(album_r.shape[:2], dtype=np.uint8) * 255
    valid = cv2.warpPerspective(valid_src, H, (w, h), flags=cv2.INTER_NEAREST,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return warped, valid, "aligned"


# ─────────────────────────────────────────────────────────────────────────────
#  Confidence mask
# ─────────────────────────────────────────────────────────────────────────────

def _gradient(gray: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def _normalize(img: np.ndarray) -> np.ndarray:
    img = img.astype(np.float32)
    lo, hi = float(img.min()), float(img.max())
    if hi - lo < 1e-6:
        return np.zeros_like(img)
    return (img - lo) / (hi - lo)


def create_confidence_mask(
    frame: np.ndarray,
    aligned: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray | None:
    fg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ag = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)

    fe = cv2.Canny(fg, 60, 160)
    ae = cv2.Canny(ag, 60, 160)
    edge_score = cv2.GaussianBlur((cv2.bitwise_and(fe, ae).astype(np.float32) / 255.0), (0, 0), 2.0)

    grad_agree = 1.0 - np.abs(_normalize(_gradient(fg)) - _normalize(_gradient(ag)))
    diff_score = np.exp(-cv2.absdiff(fg, ag).astype(np.float32) / 255.0 * 5.0)

    conf = (0.35 * edge_score + 0.35 * grad_agree * _normalize(_gradient(fg)) + 0.30 * diff_score)
    conf *= valid.astype(np.float32) / 255.0
    conf = cv2.GaussianBlur(conf, (0, 0), 3.0)
    conf = np.clip(conf, 0.0, 1.0)
    conf[conf < 0.18] = 0.0

    return None if np.count_nonzero(conf > 0.0) == 0 else conf


# ─────────────────────────────────────────────────────────────────────────────
#  Enhancement
# ─────────────────────────────────────────────────────────────────────────────

def apply_clahe(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)


def unsharp_mask(image: np.ndarray, amount: float = 0.65, sigma: float = 1.2) -> np.ndarray:
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    return np.clip(cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0), 0, 255).astype(np.uint8)


def high_freq(image: np.ndarray) -> np.ndarray:
    return image.astype(np.float32) - cv2.GaussianBlur(image, (0, 0), 1.4).astype(np.float32)


def restore_frame(frame: np.ndarray, aligned: np.ndarray, conf: np.ndarray) -> np.ndarray:
    """Apply album detail + CLAHE + bilateral + unsharp to the frame."""
    detail_w = conf[..., None] * DETAIL_ALPHA
    guided = np.clip(frame.astype(np.float32) + high_freq(aligned) * detail_w, 0, 255).astype(np.uint8)

    enhanced = unsharp_mask(cv2.bilateralFilter(apply_clahe(guided), d=5, sigmaColor=35, sigmaSpace=35))

    adaptive_w = np.clip(conf[..., None] * 0.65, 0.0, 0.65)
    restored = frame.astype(np.float32) * (1.0 - adaptive_w) + enhanced.astype(np.float32) * adaptive_w
    guard = frame.astype(np.float32) * FRAME_ALPHA + restored * (1.0 - FRAME_ALPHA)
    final_w = np.clip(conf[..., None], 0.0, 0.85)
    return np.clip(frame.astype(np.float32) * (1.0 - final_w) + guard * final_w, 0, 255).astype(np.uint8)


# ─────────────────────────────────────────────────────────────────────────────
#  Per-row processing
# ─────────────────────────────────────────────────────────────────────────────

def get_score(row: pd.Series) -> str:
    for col in ("FinalScore", "SimilarityScore", "CLIPScore", "FaceScore"):
        if col in row and not pd.isna(row[col]):
            return str(row[col])
    return ""


def process_row(
    row: pd.Series,
    idx: int,
    frames_dir: Path,
    albums_dir: Path,
    restored_dir: Path,
    root: Path,
) -> dict[str, str]:
    frame_name = row["Frame"]
    album_name = row["AlbumImage"]
    score = get_score(row)
    out_path = restored_dir / f"frame_{idx:04d}.jpg"

    frame = read_image(resolve_path(frames_dir, root, frame_name))
    if frame is None:
        return _log(frame_name, album_name, score, "missing_frame", None, root)

    album = read_image(resolve_path(albums_dir, root, album_name))
    if album is None:
        return _log(frame_name, album_name, score, "missing_album", None, root)

    warped, valid, status = align_album_to_frame(frame, album)
    if warped is None:
        return _log(frame_name, album_name, score, status, None, root)

    conf = create_confidence_mask(frame, warped, valid)
    if conf is None:
        return _log(frame_name, album_name, score, "empty_mask", None, root)

    restored = restore_frame(frame, warped, conf)
    if not cv2.imwrite(str(out_path), restored):
        return _log(frame_name, album_name, score, "save_failed", None, root)

    return _log(frame_name, album_name, score, "restored", out_path, root)


def _log(frame, album, score, status, out, root) -> dict[str, str]:
    return {
        "Frame": str(frame),
        "MatchedAlbum": str(album),
        "SimilarityScore": score,
        "Status": status,
        "OutputImage": "" if out is None else str(out.relative_to(root)),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    root = args.output.parent
    restored_dir = args.output / "Restored_Frames"
    restored_dir.mkdir(parents=True, exist_ok=True)

    if not args.csv.exists():
        raise FileNotFoundError(f"Matches CSV not found: {args.csv}")

    data = pd.read_csv(args.csv)
    required = {"Frame", "Rank", "AlbumImage"}
    if missing := required - set(data.columns):
        raise ValueError(f"CSV missing columns: {missing}")

    matches = data.loc[pd.to_numeric(data["Rank"], errors="coerce") == 1].copy()
    matches.reset_index(drop=True, inplace=True)

    log_rows = []
    for i, (_, row) in enumerate(
        tqdm(matches.iterrows(), total=len(matches), desc="Restoring frames"), start=1
    ):
        log_rows.append(process_row(row, i, args.frames, args.albums, restored_dir, root))

    pd.DataFrame(log_rows, columns=["Frame", "MatchedAlbum", "SimilarityScore", "Status", "OutputImage"]).to_csv(
        args.output / "restore_log.csv", index=False
    )
    print("Completed.")


if __name__ == "__main__":
    main()
