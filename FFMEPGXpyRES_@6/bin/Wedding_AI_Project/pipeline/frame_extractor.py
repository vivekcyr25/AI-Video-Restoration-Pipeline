"""
pipeline/frame_extractor.py
==========================
Stage 2: Representative Frame Extraction.
Extracts the midpoint frame of each detected scene to serve as the keyframe.
"""

from __future__ import annotations

import argparse
import logging
import os
import time
import math
import cv2
import numpy as np
import pandas as pd
import threading
import concurrent.futures
from pathlib import Path

from utils.video_utils import get_video_info

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("frame_extractor")


def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS string."""
    if not math.isfinite(seconds) or seconds < 0:
        return "00:00:00"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def map_ffmpeg_quality_to_opencv(q_ffmpeg: int) -> int:
    """
    Map FFmpeg JPEG quality (-q:v, 1=best, 31=worst)
    to OpenCV JPEG quality (0-100, 100=best).
    """
    if q_ffmpeg <= 1:
        return 98
    elif q_ffmpeg == 2:
        return 95
    elif q_ffmpeg == 3:
        return 92
    elif q_ffmpeg <= 5:
        return 85
    elif q_ffmpeg <= 10:
        return 75
    elif q_ffmpeg <= 20:
        return 60
    else:
        return max(10, 100 - int(q_ffmpeg * 2.5))


class FrameExtractorStage:
    def __init__(self, config: dict):
        self.config = config
        self.repaired_path = Path(config["video_repair"]["repaired_video_path"])
        self.scene_csv_path = Path(config["video_repair"]["scene_csv_path"])
        
        cfg = config["frame_extractor"]
        self.output_dir = Path(cfg["output_dir"])
        self.quality = int(cfg["quality"])
        
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_frame_with_retry(self, cap: cv2.VideoCapture, frame_idx: int) -> tuple[cv2.VideoCapture, np.ndarray | None]:
        """
        Attempt to seek and read a frame. If seek/read fails, reopen VideoCapture and try once more.
        Returns (cap, frame).
        """
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ok, frame = cap.read()
            if ok and frame is not None:
                return cap, frame
        except Exception as e:
            logger.warning(f"Error seeking/reading frame {frame_idx}: {e}. Retrying with new VideoCapture handle...")
        
        # Retry logic: release current handle and reopen
        try:
            cap.release()
            cap = cv2.VideoCapture(str(self.repaired_path))
            if not cap.isOpened():
                logger.error("Failed to reopen VideoCapture during seek fallback.")
                return cap, None
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ok, frame = cap.read()
            if ok and frame is not None:
                return cap, frame
        except Exception as e:
            logger.error(f"Fallback seek failed for frame {frame_idx}: {e}")
        
        return cap, None

    def run(self, force: bool = False) -> None:
        logger.info("Starting Stage 2: Representative Frame Extraction")
        
        if not self.scene_csv_path.exists():
            raise FileNotFoundError(f"Scenes CSV not found at {self.scene_csv_path}. Please run Stage 1 first.")
        if not self.repaired_path.exists():
            raise FileNotFoundError(f"Repaired video not found at {self.repaired_path}. Please run Stage 1 first.")
            
        df = pd.read_csv(self.scene_csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        # Identify columns
        start_col = next((c for c in df.columns if "start" in c.lower() and "frame" in c.lower()), None)
        length_col = next((c for c in df.columns if "length" in c.lower() and "frame" in c.lower()), None)
        end_col = next((c for c in df.columns if "end" in c.lower() and "frame" in c.lower()), None)
        
        if start_col is None:
            raise KeyError("Scenes CSV is missing a Start Frame column.")

        # Set up CPU cores autodetect and thread pool
        num_cores = os.cpu_count() or 4
        # Thread pool size matches CPU core count for parallel JPEG compression and disk writes
        max_workers = num_cores
        logger.info(f"Detected {num_cores} CPU cores. Initializing thread pool with {max_workers} workers.")
        
        # Open video only ONCE
        cap = cv2.VideoCapture(str(self.repaired_path))
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {self.repaired_path}")
            
        # Determine the JPEG quality setting
        opencv_jpeg_quality = map_ffmpeg_quality_to_opencv(self.quality)
        
        # Stats tracking
        total_scenes = len(df)
        skipped_count = 0
        extracted_count = 0
        failed_count = 0
        
        # Identify which scenes need extraction
        scenes_to_extract = []
        for i, row in df.iterrows():
            scene_idx = i + 1
            out_path = self.output_dir / f"scene_{scene_idx:04d}.jpg"
            
            # Determine midpoint frame index
            start = int(row[start_col])
            if length_col:
                length = int(row[length_col])
                midpoint = start + max(0, length - 1) // 2
            elif end_col:
                end = int(row[end_col])
                midpoint = (start + end) // 2
            else:
                midpoint = start
                
            if out_path.exists() and not force:
                skipped_count += 1
            else:
                scenes_to_extract.append((scene_idx, midpoint, out_path))

        num_to_extract = len(scenes_to_extract)
        logger.info(f"Total scenes: {total_scenes}. Skipped (already extracted): {skipped_count}. To extract: {num_to_extract}.")

        # If everything is skipped, exit early
        if num_to_extract == 0:
            cap.release()
            logger.info("All representative frames already exist. Nothing to extract.")
            logger.info("=========================================")
            logger.info("FINAL EXTRACTION STATISTICS")
            logger.info("=========================================")
            logger.info(f"Extraction Time: 0.00s")
            logger.info(f"Average FPS: 0.00")
            logger.info(f"Skipped: {skipped_count}")
            logger.info(f"Extracted: {extracted_count}")
            logger.info(f"Failures: {failed_count}")
            return

        # Bounded semaphore to prevent high RAM usage by limiting queued frames in memory
        semaphore = threading.BoundedSemaphore(max_workers + 4)
        
        # Futures dictionary to track progress
        futures = {}
        
        def save_frame_task(frame_data: np.ndarray, path: Path, quality_val: int) -> bool:
            try:
                # cv2.imwrite returns True on success, False on failure
                success = cv2.imwrite(str(path), frame_data, [cv2.IMWRITE_JPEG_QUALITY, quality_val])
                return success
            except Exception as e:
                logger.error(f"Failed writing frame to {path}: {e}")
                return False
            finally:
                semaphore.release()

        start_time = time.time()
        active_processed = 0

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                for idx, (scene_idx, midpoint, out_path) in enumerate(scenes_to_extract):
                    # Check/acquire semaphore to limit RAM usage
                    semaphore.acquire()
                    
                    # Seek internally and read frame
                    cap, frame = self._read_frame_with_retry(cap, midpoint)
                    
                    if frame is None:
                        logger.error(f"Failed to decode frame {midpoint} for Scene {scene_idx}")
                        failed_count += 1
                        semaphore.release()  # release since we didn't submit task
                        continue
                        
                    # Submit task to save the frame (will release semaphore upon completion)
                    future = executor.submit(save_frame_task, frame, out_path, opencv_jpeg_quality)
                    futures[future] = scene_idx
                    active_processed += 1
                    
                    # Logging progress
                    elapsed = time.time() - start_time
                    fps = active_processed / elapsed if elapsed > 0 else 0.0
                    remaining = num_to_extract - active_processed
                    eta = remaining / fps if fps > 0 else 0.0
                    
                    # Log message layout matches requirement
                    progress_msg = (
                        f"Scene {scene_idx}/{total_scenes}\n"
                        f"ETA: {format_time(eta)}\n"
                        f"Frames/sec: {fps:.2f}\n"
                        f"Elapsed: {format_time(elapsed)}"
                    )
                    logger.info(progress_msg)
                    
                # Wait for all submitted writes to complete and gather results
                for future in concurrent.futures.as_completed(futures.keys()):
                    scene_idx = futures[future]
                    try:
                        success = future.result()
                        if success:
                            extracted_count += 1
                        else:
                            failed_count += 1
                            logger.error(f"Thread failed to write JPEG for Scene {scene_idx}")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Exception during saving of Scene {scene_idx}: {e}")
                        
        finally:
            cap.release()

        # Compute and display final stats
        end_time = time.time()
        extraction_time = end_time - start_time
        avg_fps = active_processed / extraction_time if extraction_time > 0 else 0.0
        
        logger.info("=========================================")
        logger.info("FINAL EXTRACTION STATISTICS")
        logger.info("=========================================")
        logger.info(f"Extraction Time: {extraction_time:.2f}s")
        logger.info(f"Average FPS: {avg_fps:.2f}")
        logger.info(f"Skipped: {skipped_count}")
        logger.info(f"Extracted: {extracted_count}")
        logger.info(f"Failures: {failed_count}")


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
