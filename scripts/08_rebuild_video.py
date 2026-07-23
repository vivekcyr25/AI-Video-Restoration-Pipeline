#!/usr/bin/env python3
"""
Stage 6 — Video Reconstruction Wrapper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from pipeline.video_propagation import VideoPropagationStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="RAFT video propagation reconstruction (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--scenes", type=Path, default=None)
    p.add_argument("--restored-dir", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--strength", type=float, default=None)
    p.add_argument("--temporal-strength", type=float, default=None)
    p.add_argument("--detail-strength", type=float, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Overrides
    if args.video:
        config["global"]["video_path"] = str(args.video)
    if args.scenes:
        config["video_repair"]["scene_csv_path"] = str(args.scenes)
    if args.restored_dir:
        config["restoration"]["output_dir"] = str(args.restored_dir)
    if args.output:
        config["video_propagation"]["output_silent"] = str(args.output)
    if args.strength:
        config["video_propagation"]["strength"] = args.strength
    if args.temporal_strength:
        config["video_propagation"]["temporal_strength"] = args.temporal_strength
    if args.detail_strength:
        config["video_propagation"]["detail_strength"] = args.detail_strength

    stage = VideoPropagationStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
