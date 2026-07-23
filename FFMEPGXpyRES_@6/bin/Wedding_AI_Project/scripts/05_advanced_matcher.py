#!/usr/bin/env python3
"""
Stage 4 — Hybrid Matching Wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import argparse
from pathlib import Path
import yaml

from pipeline.hybrid_matcher import HybridMatcherStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Hybrid CLIP + face matching (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--models", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--face-weight", type=float, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Overrides
    if args.models:
        config["global"]["models_dir"] = str(args.models)
    if args.output:
        config["global"]["output_dir"] = str(args.output)
    if args.top_k:
        config["hybrid_matching"]["top_k"] = args.top_k
    if args.face_weight:
        config["hybrid_matching"]["weights"]["face"] = args.face_weight

    stage = HybridMatcherStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
