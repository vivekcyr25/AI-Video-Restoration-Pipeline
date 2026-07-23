"""
pipeline/frame_extractor.py
==========================
Stage 2: Representative Frame Extraction.
Extracts the midpoint frame of each detected scene to serve as the keyframe.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("frame_extractor")


class FrameExtractorStage:
    def __init__(self, config: dict):
        self.config = config
        self.cfr_path = Path(config["video_repair"]["cfr_video_path"])
        self.scene_csv_path = Path(config["video_repair"]["scene_csv_path"])
        
        cfg = config["frame_extractor"]
        self.output_dir = Path(cfg["output_dir"])
        self.quality = int(cfg["quality"])
        
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 2: Representative Frame Extraction")
        
        if not self.scene_csv_path.exists():
            raise FileNotFoundError(f"Scenes CSV not found at {self.scene_csv_path}. Please run Stage 1 first.")
        if not self.cfr_path.exists():
            raise FileNotFoundError(f"CFR video not found at {self.cfr_path}. Please run Stage 1 first.")
            
        df = pd.read_csv(self.scene_csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        # Identify columns
        start_col = next((c for c in df.columns if "start" in c.lower() and "frame" in c.lower()), None)
        length_col = next((c for c in df.columns if "length" in c.lower() and "frame" in c.lower()), None)
        end_col = next((c for c in df.columns if "end" in c.lower() and "frame" in c.lower()), None)
        
        if start_col is None:
            raise KeyError("Scenes CSV is missing a Start Frame column.")
            
        extracted_count = 0
        skipped_count = 0
        
        for i, row in df.iterrows():
            start = int(row[start_col])
            if length_col:
                length = int(row[length_col])
                midpoint = start + max(0, length - 1) // 2
            elif end_col:
                end = int(row[end_col])
                midpoint = (start + end) // 2
            else:
                midpoint = start
                
            scene_idx = i + 1
            out_path = self.output_dir / f"scene_{scene_idx:04d}.jpg"
            
            if out_path.exists() and not force:
                skipped_count += 1
                continue
                
            # Extract via FFmpeg for high quality and speed
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(midpoint / 30.0),  # Seek roughly using seconds for fast seeking
                "-i", str(self.cfr_path),
                "-vf", f"select=eq(n\\,{midpoint})",
                "-vframes", "1",
                "-q:v", str(self.quality),
                str(out_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                extracted_count += 1
            else:
                # Fallback without pre-seeking if ss seeking fails or offsets frames
                cmd_fallback = [
                    "ffmpeg", "-y",
                    "-i", str(self.cfr_path),
                    "-vf", f"select=eq(n\\,{midpoint})",
                    "-vframes", "1",
                    "-q:v", str(self.quality),
                    str(out_path)
                ]
                res_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True)
                if res_fallback.returncode == 0:
                    extracted_count += 1
                else:
                    logger.error(f"Failed to extract frame {midpoint} for Scene {scene_idx}: {res_fallback.stderr}")
                    
        logger.info(f"Frame extraction summary: {extracted_count} extracted, {skipped_count} skipped. Total: {len(df)} frames.")


if __name__ == "__main__":
    import yaml
    p = argparse.ArgumentParser(description="Stage 2: Representative Frame Extraction")
    p.add_argument("--config", type=Path, default=Path("configs/pipeline_config.yaml"))
    p.add_argument("--force", action="store_true", help="Force execution and overwrite checkpoints")
    args = p.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
        
    stage = FrameExtractorStage(cfg)
    stage.run(force=args.force)
