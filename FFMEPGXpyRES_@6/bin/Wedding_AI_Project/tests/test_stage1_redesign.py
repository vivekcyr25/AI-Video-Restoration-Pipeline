"""
tests/test_stage1_redesign.py
=============================
Integration tests for the Stage 1 (Video Repair & Scene Detect) and
Stage 2 (Representative Frame Extraction) redesign.
"""

from __future__ import annotations

import csv
from pathlib import Path
import cv2
import numpy as np
import pytest
import yaml

from pipeline.video_repair import VideoRepairStage
from pipeline.frame_extractor import FrameExtractorStage


def create_synthetic_video(path: Path, width: int = 128, height: int = 128, fps: float = 10.0, num_frames: int = 40) -> None:
    """Helper to generate a synthetic video with a scene cut at midpoint."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    try:
        for i in range(num_frames):
            # Sharp scene transition at frame 20
            color = (255, 0, 0) if i < 20 else (0, 0, 255)
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:] = color
            # Add a moving shape to avoid static frame warnings or compression optimization issues
            cv2.rectangle(img, (i, 10), (i + 20, 30), (0, 255, 0), -1)
            writer.write(img)
    finally:
        writer.release()


def test_stage1_and_stage2_redesign(tmp_path: Path) -> None:
    # Setup test paths
    input_video = tmp_path / "test_input.mp4"
    create_synthetic_video(input_video, fps=10.0, num_frames=40)
    
    output_dir = tmp_path / "Output"
    output_dir.mkdir()
    
    repaired_video = output_dir / "repaired_video.mp4"
    cfr_video = output_dir / "cfr_video.mp4"
    scene_csv = output_dir / "scenes.csv"
    repr_frames_dir = tmp_path / "Representative_Frames"
    
    # Create config dict
    config = {
        "global": {
            "device": "cpu",
            "video_path": str(input_video),
            "output_dir": str(output_dir),
            "albums_dir": str(tmp_path),
            "models_dir": str(tmp_path),
        },
        "video_repair": {
            "repaired_video_path": str(repaired_video),
            "cfr_video_path": str(cfr_video),
            "scene_csv_path": str(scene_csv),
            "scene_threshold": 15.0,  # Lower threshold for synthetic scene cut detection
            "min_scene_len": 5,
            "fps": 10.0,
        },
        "frame_extractor": {
            "output_dir": str(repr_frames_dir),
            "quality": 2,
        }
    }
    
    # --- Execute Stage 1 ---
    stage1 = VideoRepairStage(config)
    stage1.run()
    
    # Assertions for Stage 1 Redesign
    assert repaired_video.exists(), "repaired_video.mp4 should be generated."
    assert not cfr_video.exists(), "cfr_video.mp4 should NOT be generated."
    assert scene_csv.exists(), "scenes.csv should be generated."
    
    # Verify scenes CSV content
    with open(scene_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) > 0, "At least one scene boundary should be detected."
    
    # --- Execute Stage 2 ---
    stage2 = FrameExtractorStage(config)
    stage2.run()
    
    # Assertions for Stage 2
    # Ensure representative frames are extracted
    extracted_frames = list(repr_frames_dir.glob("scene_*.jpg"))
    assert len(extracted_frames) == len(rows), "Should extract exactly one frame per scene."
    for frame_path in extracted_frames:
        assert frame_path.stat().st_size > 0, "Extracted frame should not be empty."
        # Read image to verify it's a valid JPEG
        img = cv2.imread(str(frame_path))
        assert img is not None, "Extracted frame must be a valid image."
        assert img.shape == (128, 128, 3)
