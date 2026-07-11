#!/usr/bin/env python3
"""
Stage 8 — Restoration Quality Report
======================================
Generates a CSV and console summary of per-frame restoration quality metrics
by comparing original representative frames against their restored counterparts.

Metrics computed for each frame pair:
- PSNR (Peak Signal-to-Noise Ratio) in dB
- Sharpness delta (Laplacian variance: restored − original)
- Histogram similarity (Bhattacharyya coefficient)
- File size change (bytes)

Usage
-----
    python scripts/10_quality_report.py [--original ORIGINAL_DIR]
                                         [--restored RESTORED_DIR]
                                         [--output OUTPUT_CSV]

Outputs
-------
    output/quality_report.csv  — Per-frame metrics
    Console summary            — Mean/min/max for each metric

Requirements
------------
    pip install numpy opencv-python tqdm
"""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

from tqdm import tqdm

# Import project utilities
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.image_utils import (
    load_image_rgb,
    estimate_blur,
    compute_histogram,
    histogram_similarity,
    compute_psnr,
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a quality report comparing original vs restored frames."
    )
    parser.add_argument(
        "--original",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Representative_Frames",
        help="Directory containing the original representative frames.",
    )
    parser.add_argument(
        "--restored",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "output" / "Restored_Frames",
        help="Directory containing the restored frames.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "output" / "quality_report.csv",
        help="Output CSV file path.",
    )
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
#  Core comparison logic
# ─────────────────────────────────────────────────────────────────────────────

def compare_frame_pair(
    original_path: Path,
    restored_path: Path,
) -> dict:
    """
    Compute quality metrics for a single (original, restored) frame pair.

    Returns a dict with keys: frame, psnr_db, sharpness_delta,
    hist_similarity, size_change_bytes, status.
    """
    result: dict = {
        "frame": original_path.name,
        "psnr_db": None,
        "sharpness_delta": None,
        "hist_similarity": None,
        "size_change_bytes": None,
        "status": "ok",
    }

    try:
        orig = load_image_rgb(original_path)
        rest = load_image_rgb(restored_path)
    except Exception as exc:
        result["status"] = f"load_error: {exc}"
        return result

    # Resize restored to match original if dimensions differ
    if orig.shape != rest.shape:
        import cv2
        rest = cv2.resize(rest, (orig.shape[1], orig.shape[0]))

    # PSNR
    try:
        result["psnr_db"] = compute_psnr(orig, rest)
    except Exception:
        pass

    # Sharpness delta
    result["sharpness_delta"] = estimate_blur(rest) - estimate_blur(orig)

    # Histogram similarity
    hist_orig = compute_histogram(orig)
    hist_rest = compute_histogram(rest)
    result["hist_similarity"] = round(histogram_similarity(hist_orig, hist_rest), 4)

    # File size change
    if restored_path.exists() and original_path.exists():
        result["size_change_bytes"] = restored_path.stat().st_size - original_path.stat().st_size

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Summary printing
# ─────────────────────────────────────────────────────────────────────────────

def _print_summary(rows: list[dict]) -> None:
    psnrs = [r["psnr_db"] for r in rows if r["psnr_db"] is not None]
    sharpness = [r["sharpness_delta"] for r in rows if r["sharpness_delta"] is not None]
    hist_sims = [r["hist_similarity"] for r in rows if r["hist_similarity"] is not None]

    print("\n" + "=" * 60)
    print("QUALITY REPORT SUMMARY")
    print("=" * 60)
    print(f"  Frames compared : {len(rows)}")
    print(f"  Errors          : {sum(1 for r in rows if r['status'] != 'ok')}")

    if psnrs:
        print(f"\n  PSNR (dB)")
        print(f"    Mean : {statistics.mean(psnrs):.2f}")
        print(f"    Min  : {min(psnrs):.2f}")
        print(f"    Max  : {max(psnrs):.2f}")

    if sharpness:
        print(f"\n  Sharpness delta (Laplacian var, positive = sharper)")
        print(f"    Mean : {statistics.mean(sharpness):.2f}")
        print(f"    Min  : {min(sharpness):.2f}")
        print(f"    Max  : {max(sharpness):.2f}")

    if hist_sims:
        print(f"\n  Histogram similarity (Bhattacharyya, 1=identical)")
        print(f"    Mean : {statistics.mean(hist_sims):.4f}")
        print(f"    Min  : {min(hist_sims):.4f}")
        print(f"    Max  : {max(hist_sims):.4f}")

    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    if not args.original.exists():
        print(f"[ERROR] Original frames directory not found: {args.original}")
        return
    if not args.restored.exists():
        print(f"[ERROR] Restored frames directory not found: {args.restored}")
        return

    original_frames = sorted(
        f for f in args.original.iterdir()
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS
    )

    if not original_frames:
        print(f"[WARNING] No images found in: {args.original}")
        return

    rows: list[dict] = []
    for orig_path in tqdm(original_frames, desc="Comparing frames", unit="frame"):
        rest_path = args.restored / orig_path.name
        if not rest_path.exists():
            rows.append({
                "frame": orig_path.name,
                "psnr_db": None,
                "sharpness_delta": None,
                "hist_similarity": None,
                "size_change_bytes": None,
                "status": "restored_missing",
            })
            continue
        rows.append(compare_frame_pair(orig_path, rest_path))

    # Write CSV
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["frame", "psnr_db", "sharpness_delta", "hist_similarity",
                  "size_change_bytes", "status"]
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nReport written to: {args.output}")
    _print_summary(rows)


if __name__ == "__main__":
    main()
