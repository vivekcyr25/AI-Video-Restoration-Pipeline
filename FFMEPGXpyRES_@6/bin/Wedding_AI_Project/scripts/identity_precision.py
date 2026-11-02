"""
scripts/identity_precision.py
=============================
Evaluates identity precision and coverage of the AI Video Restoration Pipeline
against human-labeled ground truth in reports/identity_labels.csv.

Computes:
  - Labeled faces count
  - Faces with reference assigned count
  - Correct references count
  - Precision = correct / assigned
  - Coverage = assigned / labeled
  - 95% Wilson score confidence interval for precision
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_project_root = Path(__file__).resolve().parent.parent


def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Compute Wilson score continuity-corrected / standard confidence interval for binomial proportion.
    
    Args:
        k: Number of successes (correct assignments)
        n: Total number of trials (assigned faces)
        confidence: Confidence level (default 0.95)
        
    Returns:
        (lower_bound, upper_bound) clamped to [0.0, 1.0]
    """
    if n == 0:
        return (0.0, 0.0)
    
    # 95% two-tailed standard normal z-score ≈ 1.95996
    z = 1.959963984540054
    p = k / n
    z2 = z * z
    denominator = 1.0 + z2 / n
    center = p + z2 / (2.0 * n)
    spread = z * math.sqrt((p * (1.0 - p)) / n + z2 / (4.0 * n * n))
    
    lower = max(0.0, (center - spread) / denominator)
    upper = min(1.0, (center + spread) / denominator)
    return (round(lower, 4), round(upper, 4))


def evaluate_identity_precision(
    labels_csv_path: Path,
    candidates_csv_path: Path,
    output_json_path: Path,
    min_required_labels: int = 20,
) -> Dict[str, any]:
    """
    Reads labels and candidates, computes identity precision and 95% Wilson interval.
    """
    if not labels_csv_path.exists():
        raise FileNotFoundError(f"Labels file not found: {labels_csv_path}")
    
    # 1. Read ground truth labels, skipping empty true_person_id
    labeled_rows: List[Dict[str, str]] = []
    with open(labels_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row.get("true_person_id", "").strip()
            if tid:
                labeled_rows.append(row)
                
    if len(labeled_rows) < min_required_labels:
        raise ValueError(
            f"Fewer than {min_required_labels} labeled faces found (found {len(labeled_rows)}). "
            f"Please populate true_person_id in {labels_csv_path} before computing precision."
        )
        
    # 2. Read candidates / pipeline chosen references
    candidate_map: Dict[Tuple[str, str], Dict[str, str]] = {}
    if candidates_csv_path.exists():
        with open(candidates_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["frame_path"].strip(), str(row["face_index"]).strip())
                candidate_map[key] = row

    total_labeled = len(labeled_rows)
    assigned_count = 0
    correct_count = 0
    detailed_eval: List[Dict[str, any]] = []

    for r in labeled_rows:
        frame_path = r["frame_path"].strip()
        face_idx = str(r["face_index"]).strip()
        true_id = r["true_person_id"].strip().lower()

        cand = candidate_map.get((frame_path, face_idx))
        chosen_ref = cand.get("top1_album_match", "none").strip() if cand else "none"

        is_assigned = chosen_ref not in ("", "none", "None")
        if is_assigned:
            assigned_count += 1
            # Check if chosen reference matches true person ID
            # Accepts direct string equality or if true_id is contained within chosen_ref filename
            is_correct = (
                true_id in chosen_ref.lower() or
                chosen_ref.lower().startswith(true_id)
            )
            if is_correct:
                correct_count += 1
        else:
            is_correct = False

        detailed_eval.append({
            "frame_path": frame_path,
            "face_index": face_idx,
            "true_person_id": true_id,
            "assigned_reference": chosen_ref,
            "is_correct": is_correct,
        })

    precision = round(correct_count / assigned_count, 4) if assigned_count > 0 else 0.0
    coverage = round(assigned_count / total_labeled, 4) if total_labeled > 0 else 0.0
    ci_lower, ci_upper = wilson_score_interval(correct_count, assigned_count, confidence=0.95)

    results = {
        "labeled_faces_count": total_labeled,
        "assigned_faces_count": assigned_count,
        "correct_references_count": correct_count,
        "precision": precision,
        "coverage": coverage,
        "wilson_95_ci": [ci_lower, ci_upper],
        "evaluations": detailed_eval,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


def main() -> None:
    p = argparse.ArgumentParser(description="Identity Precision Evaluator")
    p.add_argument(
        "--labels",
        type=Path,
        default=_project_root / "reports" / "identity_labels.csv",
        help="Path to identity_labels.csv",
    )
    p.add_argument(
        "--candidates",
        type=Path,
        default=_project_root / "reports" / "identity_candidates.csv",
        help="Path to identity_candidates.csv",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=_project_root / "reports" / "identity_precision.json",
        help="Path to output JSON report",
    )
    p.add_argument(
        "--min-labels",
        type=int,
        default=20,
        help="Minimum required labeled faces",
    )
    args = p.parse_args()

    try:
        res = evaluate_identity_precision(
            labels_csv_path=args.labels,
            candidates_csv_path=args.candidates,
            output_json_path=args.output,
            min_required_labels=args.min_labels,
        )
        print("Identity Precision Evaluation Summary:")
        print(f"  Labeled Faces:    {res['labeled_faces_count']}")
        print(f"  Assigned Faces:   {res['assigned_faces_count']}")
        print(f"  Correct Matches:  {res['correct_references_count']}")
        print(f"  Precision:        {res['precision']:.2%}")
        print(f"  Coverage:         {res['coverage']:.2%}")
        print(f"  95% Wilson CI:    [{res['wilson_95_ci'][0]:.2%}, {res['wilson_95_ci'][1]:.2%}]")
        print(f"Saved report to: {args.output}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
