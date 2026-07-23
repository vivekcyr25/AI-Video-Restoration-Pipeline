"""
pipeline/hybrid_matcher.py
==========================
Stage 5: Hybrid Frame-to-Album Matching.
Reuses the implementation from pipeline/reference_selector.py to prevent code duplication.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .reference_selector import ReferenceSelectorStage

# Backwards compatibility alias
HybridMatcherStage = ReferenceSelectorStage

if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 5: Hybrid Frame Matcher")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force rebuild of matching CSV")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = HybridMatcherStage(cfg)
    stage.run(force=args.force)
