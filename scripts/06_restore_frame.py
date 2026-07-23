#!/usr/bin/env python3
"""
Stage 5A — Frame Restoration Wrapper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from pipeline.main_restoration import ReferenceRestorer

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Reference-guided frame restoration (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--csv", type=Path, default=None)
    p.add_argument("--frames", type=Path, default=None)
    p.add_argument("--albums", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Overrides
    if args.csv:
        config["global"]["output_dir"] = str(args.csv.parent)
    if args.frames:
        config["frame_extractor"]["output_dir"] = str(args.frames)
    if args.albums:
        config["global"]["albums_dir"] = str(args.albums)
    if args.output:
        config["restoration"]["output_dir"] = str(args.output / "Restored_Frames")

    stage = ReferenceRestorer(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
