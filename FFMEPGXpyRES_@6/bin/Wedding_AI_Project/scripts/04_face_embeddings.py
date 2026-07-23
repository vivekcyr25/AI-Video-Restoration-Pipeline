#!/usr/bin/env python3
"""
Stage 3B — Face Identity Embedding Wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import argparse
from pathlib import Path
import yaml

from pipeline.face_embedder import FaceEmbedderStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Generate InsightFace embeddings (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--albums", type=Path, default=None)
    p.add_argument("--frames", type=Path, default=None)
    p.add_argument("--models", type=Path, default=None)
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--force", action="store_true", help="Force rebuild")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Overrides
    if args.albums:
        config["global"]["albums_dir"] = str(args.albums)
    if args.frames:
        config["frame_extractor"]["output_dir"] = str(args.frames)
    if args.models:
        config["global"]["models_dir"] = str(args.models)
    if args.gpu:
        config["global"]["device"] = "cuda"

    stage = FaceEmbedderStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
