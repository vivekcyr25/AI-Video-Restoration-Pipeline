"""
pipeline/video_repair.py
========================
Stage 1: Video Repair, CFR conversion, and Scene Boundary Detection.
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import subprocess
from pathlib import Path

from scenedetect import ContentDetector, SceneManager, open_video

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("video_repair")


class VideoRepairStage:
    def __init__(self, config: dict):
        self.config = config
        self.video_path = Path(config["global"]["video_path"])
        self.output_dir = Path(config["global"]["output_dir"])
        
        cfg = config["video_repair"]
        self.repaired_path = Path(cfg["repaired_video_path"])
        self.cfr_path = Path(cfg["cfr_video_path"])
        self.scene_csv_path = Path(cfg["scene_csv_path"])
        self.threshold = float(cfg["scene_threshold"])
        self.min_scene_len = int(cfg["min_scene_len"])
        self.fps = float(cfg["fps"])
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repaired_path.parent.mkdir(parents=True, exist_ok=True)
        self.cfr_path.parent.mkdir(parents=True, exist_ok=True)
        self.scene_csv_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self, force: bool = False) -> None:
        """Run the complete video repair and scene detection stage."""
        logger.info("Starting Stage 1: Video Repair & CFR Conversion")
        
        # 1. FFmpeg Container Repair
        if not self.repaired_path.exists() or force:
            logger.info(f"Repairing video container: {self.video_path} -> {self.repaired_path}")
            cmd = [
                "ffmpeg", "-y",
                "-err_detect", "ignore_err",
                "-i", str(self.video_path),
                "-c", "copy",
                "-map", "0",
                str(self.repaired_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg repair failed:\n{result.stderr}")
                raise RuntimeError("Failed to repair video container.")
            logger.info("Video container repaired successfully.")
        else:
            logger.info(f"Checkpoint found: Repaired video exists at {self.repaired_path}. Skipping repair.")

        # 2. CFR Conversion
        if not self.cfr_path.exists() or force:
            logger.info(f"Converting video to Constant Frame Rate ({self.fps} FPS): {self.repaired_path} -> {self.cfr_path}")
            cmd = [
                "ffmpeg", "-y",
                "-i", str(self.repaired_path),
                "-filter:v", f"fps=fps={self.fps}",
                "-c:v", "libx264",
                "-crf", "18",
                "-c:a", "aac",
                "-vsync", "cfr",
                str(self.cfr_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"CFR conversion failed:\n{result.stderr}")
                raise RuntimeError("Failed to convert video to constant frame rate.")
            logger.info("Constant frame rate conversion complete.")
        else:
            logger.info(f"Checkpoint found: CFR video exists at {self.cfr_path}. Skipping conversion.")

        # 3. PySceneDetect Boundary Detection
        if not self.scene_csv_path.exists() or force:
            logger.info(f"Detecting scenes in CFR video using threshold={self.threshold}")
            video = open_video(str(self.cfr_path))
            scene_manager = SceneManager()
            scene_manager.add_detector(
                ContentDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)
            )
            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()
            
            logger.info(f"Detected {len(scene_list)} scenes. Saving to {self.scene_csv_path}")
            with open(self.scene_csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Scene Number", "Start Frame", "End Frame", "Start Time", "End Time", "Length (frames)"])
                for i, scene in enumerate(scene_list):
                    start_frame = scene[0].get_frames()
                    end_frame = scene[1].get_frames()
                    start_time = scene[0].get_timecode()
                    end_time = scene[1].get_timecode()
                    length = end_frame - start_frame
                    writer.writerow([i + 1, start_frame, end_frame, start_time, end_time, length])
            logger.info("Scene detection boundary file saved.")
        else:
            logger.info(f"Checkpoint found: Scene list exists at {self.scene_csv_path}. Skipping detection.")


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 1: Video Repair and Scene Detection")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force execution and overwrite checkpoints")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = VideoRepairStage(cfg)
    stage.run(force=args.force)
