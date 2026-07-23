#!/usr/bin/env python3
"""
Stage 3A — CLIP Visual Embedding Generation Wrapper.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from pipeline.clip_embedder import CLIPEmbedderStage

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Generate CLIP embeddings (Wrapper).")
    p.add_argument("--config", type=Path, default=root / "configs" / "pipeline_config.yaml")
    p.add_argument("--albums", type=Path, default=None)
    p.add_argument("--frames", type=Path, default=None)
    p.add_argument("--models", type=Path, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--force", action="store_true", help="Force rebuild")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # CLI overrides for backwards compatibility
    if args.albums:
        config["global"]["albums_dir"] = str(args.albums)
    if args.frames:
        config["frame_extractor"]["output_dir"] = str(args.frames)
    if args.models:
        config["global"]["models_dir"] = str(args.models)
    if args.batch_size:
        config["clip_embeddings"]["batch_size"] = args.batch_size

    stage = CLIPEmbedderStage(config)
    stage.run(force=args.force)

if __name__ == "__main__":
    main()
