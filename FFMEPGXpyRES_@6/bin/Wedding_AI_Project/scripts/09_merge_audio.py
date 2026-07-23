#!/usr/bin/env python3
"""
Stage 8 — Lossless Audio Muxing Wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import argparse
from pathlib import Path
import yaml

from scripts.run_pipeline import mux_audio

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Lossless audio muxing (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--original-video", type=Path, default=None)
    p.add_argument("--silent-video", type=Path, default=None)
    p.add_argument("--final-video", type=Path, default=None)
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    original = args.original_video or Path(config["global"]["video_path"])
    silent = args.silent_video or Path(config["video_propagation"]["output_silent"])
    final = args.final_video or Path(config["video_propagation"]["output_final"])

    success = mux_audio(original, silent, final)
    if not success:
        print("ERROR: Lossless audio muxing failed.")
        exit(1)
    print(f"SUCCESS: Muxed final video saved to {final}")

if __name__ == "__main__":
    main()
