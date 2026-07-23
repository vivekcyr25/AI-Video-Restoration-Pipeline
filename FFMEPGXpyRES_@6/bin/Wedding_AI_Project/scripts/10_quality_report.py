#!/usr/bin/env python3
"""
Stage 9 — Quality Report Wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import argparse
from pathlib import Path
import yaml

from pipeline.quality_validator import QualityValidator

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Generate Quality Reports (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Overrides
    if args.video:
        config["video_propagation"]["output_final"] = str(args.video)
    if args.output:
        config["global"]["output_dir"] = str(args.output)

    validator = QualityValidator(config)
    validator.run()

if __name__ == "__main__":
    main()
