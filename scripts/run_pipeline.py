"""
scripts/run_pipeline.py
=======================
Unified pipeline manager. Coordinates the execution of all 8 restoration stages
using parameters defined in a central configuration file.
Supports checkpointing, resume, and selective stage execution.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import time
from pathlib import Path
import yaml

from pipeline import (
    VideoRepairStage,
    FrameExtractorStage,
    CLIPEmbedderStage,
    FaceEmbedderStage,
    HybridMatcherStage,
    ReferenceRestorer,
    VideoPropagationStage,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("pipeline_manager")


def mux_audio(original_video: Path, silent_video: Path, final_video: Path) -> bool:
    """Losslessly stream-copies original audio track into the restored video."""
    logger.info(f"Muxing audio from {original_video} into {silent_video} -> {final_video}")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(original_video),
        "-map", "0:v",
        "-map", "1:a?",  # Map audio if present
        "-c:v", "copy",
        "-c:a", "copy",
        "-shortest",
        str(final_video)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg audio muxing failed:\n{result.stderr}")
        return False
    return True


def run_all(config: dict, force: bool = False) -> None:
    start_time = time.time()
    
    # Stage 1: Video Repair
    stage1 = VideoRepairStage(config)
    stage1.run(force=force)
    
    # Stage 2: Frame Extraction
    stage2 = FrameExtractorStage(config)
    stage2.run(force=force)
    
    # Stage 3: CLIP Embeddings
    stage3 = CLIPEmbedderStage(config)
    stage3.run(force=force)
    
    # Stage 4: InsightFace Face Embeddings
    stage4 = FaceEmbedderStage(config)
    stage4.run(force=force)
    
    # Stage 5: Hybrid Matching
    stage5 = HybridMatcherStage(config)
    stage5.run(force=force)
    
    # Stage 6: Reference-guided Restoration
    stage6 = ReferenceRestorer(config)
    stage6.run(force=force)
    
    # Stage 7: Video Detail Propagation (RAFT)
    stage7 = VideoPropagationStage(config)
    stage7.run(force=force)
    
    # Stage 8: Lossless Audio Muxing
    original = Path(config["global"]["video_path"])
    silent = Path(config["video_propagation"]["output_silent"])
    final = Path(config["video_propagation"]["output_final"])
    success = mux_audio(original, silent, final)
    if not success:
        raise RuntimeError("Audio muxing failed.")
        
    duration = time.time() - start_time
    logger.info(f"Complete Restoration Pipeline executed successfully in {duration:.1f}s.")


def main() -> None:
    p = argparse.ArgumentParser(description="AI Video Restoration Unified Pipeline Runner")
    p.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "configs" / "pipeline_config.yaml",
        help="Path to pipeline configuration YAML file."
    )
    p.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["1", "2", "3", "4", "5", "6", "7", "8", "all"],
        help="Specific stage to execute or 'all' to run sequentially."
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Force execution and overwrite existing checkpoints."
    )
    p.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["cpu", "cuda"],
        help="Override execution device (cpu or cuda)."
    )
    args = p.parse_args()

    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        return

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.device is not None:
        config["global"]["device"] = args.device

    stage = args.stage
    logger.info(f"Running pipeline with stage: {stage} (force={args.force})")
    
    try:
        if stage == "all":
            run_all(config, force=args.force)
        elif stage == "1":
            VideoRepairStage(config).run(force=args.force)
        elif stage == "2":
            FrameExtractorStage(config).run(force=args.force)
        elif stage == "3":
            CLIPEmbedderStage(config).run(force=args.force)
        elif stage == "4":
            FaceEmbedderStage(config).run(force=args.force)
        elif stage == "5":
            HybridMatcherStage(config).run(force=args.force)
        elif stage == "6":
            ReferenceRestorer(config).run(force=args.force)
        elif stage == "7":
            VideoPropagationStage(config).run(force=args.force)
        elif stage == "8":
            original = Path(config["global"]["video_path"])
            silent = Path(config["video_propagation"]["output_silent"])
            final = Path(config["video_propagation"]["output_final"])
            mux_audio(original, silent, final)
    except Exception as e:
        logger.exception(f"Pipeline execution failed on Stage {stage}: {e}")


if __name__ == "__main__":
    main()
