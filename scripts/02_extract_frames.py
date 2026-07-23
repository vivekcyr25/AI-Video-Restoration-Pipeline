#!/usr/bin/env python3
"""
Stage 2 — Representative Frame Extraction Wrapper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from pipeline.frame_extractor import FrameExtractorStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Representative frame extraction (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--scenes", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.video:
        config["video_repair"]["cfr_video_path"] = str(args.video)
    if args.scenes:
        config["video_repair"]["scene_csv_path"] = str(args.scenes)
    if args.output_dir:
        config["frame_extractor"]["output_dir"] = str(args.output_dir)

    stage = FrameExtractorStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
