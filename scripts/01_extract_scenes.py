#!/usr/bin/env python3
"""
Stage 1 — Scene Boundary Detection Wrapper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from pipeline.video_repair import VideoRepairStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Scene boundary detection and video repair (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--output-csv", type=Path, default=None)
    p.add_argument("--threshold", type=float, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.video:
        config["global"]["video_path"] = str(args.video)
    if args.output_csv:
        config["video_repair"]["scene_csv_path"] = str(args.output_csv)
    if args.threshold:
        config["video_repair"]["scene_threshold"] = args.threshold

    stage = VideoRepairStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
