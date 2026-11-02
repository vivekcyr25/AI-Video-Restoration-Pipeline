"""
scripts/validate_stage5.py
==========================
Regression validator for Stage 5 reference selection.
Compares the current output CSV against the baseline top-5 reference to verify
that Recall@1 and Recall@5 == 1.0 (i.e. every frame's rank-1 match and every
frame's top-5 list are identical to the baseline).

Usage:
    python scripts/validate_stage5.py [--baseline reports/baseline_stage5_top5.json]
                                      [--csv     Output/advanced_matches.csv]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

_project_root = Path(__file__).resolve().parent.parent


def validate(baseline_json: Path, csv_path: Path) -> bool:
    with open(baseline_json, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    if not csv_path.exists():
        print(f"[FAIL] CSV not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    all_pass = True
    recall1_hits = 0
    recall5_hits = 0
    total_frames = len(baseline["frames"])

    for frame_name, baseline_top5 in baseline["frames"].items():
        baseline_rank1 = baseline_top5[0]["album_image"]
        baseline_top5_albums = {e["album_image"] for e in baseline_top5}

        frame_df = df[df["Frame"] == frame_name].sort_values("Rank")
        if frame_df.empty:
            print(f"[FAIL] Frame '{frame_name}' missing from CSV entirely.")
            all_pass = False
            continue

        current_rank1 = frame_df.iloc[0]["AlbumImage"]
        current_top5 = set(frame_df.head(5)["AlbumImage"].tolist())

        r1_ok = (current_rank1 == baseline_rank1)
        r5_ok = (current_top5 == baseline_top5_albums)

        if r1_ok:
            recall1_hits += 1
        else:
            print(f"[FAIL R@1] Frame '{frame_name}': expected '{baseline_rank1}', got '{current_rank1}'")
            all_pass = False

        if r5_ok:
            recall5_hits += 1
        else:
            missing = baseline_top5_albums - current_top5
            extra = current_top5 - baseline_top5_albums
            print(f"[FAIL R@5] Frame '{frame_name}': missing={missing}  extra={extra}")
            all_pass = False

    recall1 = recall1_hits / total_frames
    recall5 = recall5_hits / total_frames

    print(f"\nRecall@1 = {recall1:.3f}  ({recall1_hits}/{total_frames})")
    print(f"Recall@5 = {recall5:.3f}  ({recall5_hits}/{total_frames})")

    if all_pass:
        print("\n[PASS] All frames match baseline exactly. Optimization accepted.")
    else:
        print("\n[FAIL] One or more frames differ from baseline. Optimization rejected — REVERT required.")

    return all_pass


def main() -> None:
    p = argparse.ArgumentParser(description="Stage 5 Regression Validator")
    p.add_argument(
        "--baseline",
        type=Path,
        default=_project_root / "reports" / "baseline_stage5_top5.json",
    )
    p.add_argument(
        "--csv",
        type=Path,
        default=_project_root / "Output" / "advanced_matches.csv",
    )
    args = p.parse_args()
    ok = validate(args.baseline, args.csv)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
