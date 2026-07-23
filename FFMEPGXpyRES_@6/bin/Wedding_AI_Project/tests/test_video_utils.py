"""
tests/test_video_utils.py
=========================
Unit tests for utils/video_utils.py.

These tests use only stdlib modules and do not require a GPU or real video
files for the pure-logic functions. Functions that call FFmpeg or OpenCV
on real files are tested with integration guards that skip if the required
binary is not available.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _has_ffprobe() -> bool:
    return shutil.which("ffprobe") is not None


# ---------------------------------------------------------------------------
# Tests for resize_fit
# ---------------------------------------------------------------------------

class TestResizeFit:
    """Tests for video_utils.resize_fit (pure NumPy / OpenCV logic)."""

    def test_output_shape_matches_target(self):
        from utils.video_utils import resize_fit
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        result = resize_fit(img, (224, 224))
        assert result.shape == (224, 224, 3)

    def test_aspect_ratio_preserved_with_letterbox(self):
        """Wide image fitted into square canvas: horizontal bars should be black."""
        from utils.video_utils import resize_fit
        # Create a bright-red wide image
        img = np.full((100, 300, 3), fill_value=[0, 0, 255], dtype=np.uint8)
        result = resize_fit(img, (100, 100))
        # Top row must be black (letterbox padding)
        assert result[0, 50, 0] == 0 and result[0, 50, 1] == 0 and result[0, 50, 2] == 0

    def test_minimum_dimension_one(self):
        """Degenerate 1-pixel image should not raise."""
        from utils.video_utils import resize_fit
        img = np.ones((1, 1, 3), dtype=np.uint8)
        result = resize_fit(img, (64, 64))
        assert result.shape == (64, 64, 3)


# ---------------------------------------------------------------------------
# Tests for resize_cover
# ---------------------------------------------------------------------------

class TestResizeCover:
    def test_output_shape_matches_target(self):
        from utils.video_utils import resize_cover
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        result = resize_cover(img, (224, 224))
        assert result.shape == (224, 224, 3)

    def test_no_black_bars(self):
        """Every pixel of a solid-colour source image should remain non-black."""
        from utils.video_utils import resize_cover
        img = np.full((100, 300, 3), fill_value=128, dtype=np.uint8)
        result = resize_cover(img, (50, 50))
        assert np.all(result > 0), "resize_cover must not introduce black padding"


# ---------------------------------------------------------------------------
# Tests for get_video_aspect_ratio (pure-math path via get_video_info mock)
# ---------------------------------------------------------------------------

class TestGetVideoAspectRatio:
    def test_16x9(self, monkeypatch):
        """1920×1080 should reduce to (16, 9)."""
        from utils import video_utils
        monkeypatch.setattr(
            video_utils,
            "get_video_info",
            lambda p: {"fps": 30.0, "width": 1920, "height": 1080,
                       "frame_count": 100, "duration_seconds": 100 / 30.0},
        )
        ratio = video_utils.get_video_aspect_ratio(Path("dummy.mp4"))
        assert ratio == (16, 9)

    def test_4x3(self, monkeypatch):
        from utils import video_utils
        monkeypatch.setattr(
            video_utils,
            "get_video_info",
            lambda p: {"fps": 25.0, "width": 640, "height": 480,
                       "frame_count": 250, "duration_seconds": 10.0},
        )
        ratio = video_utils.get_video_aspect_ratio(Path("dummy.mp4"))
        assert ratio == (4, 3)

    def test_square(self, monkeypatch):
        from utils import video_utils
        monkeypatch.setattr(
            video_utils,
            "get_video_info",
            lambda p: {"fps": 30.0, "width": 512, "height": 512,
                       "frame_count": 30, "duration_seconds": 1.0},
        )
        ratio = video_utils.get_video_aspect_ratio(Path("dummy.mp4"))
        assert ratio == (1, 1)


# ---------------------------------------------------------------------------
# Tests for validate_video_file
# ---------------------------------------------------------------------------

class TestValidateVideoFile:
    def test_raises_file_not_found(self, tmp_path):
        from utils.video_utils import validate_video_file
        with pytest.raises(FileNotFoundError):
            validate_video_file(tmp_path / "nonexistent.mp4")

    def test_raises_value_error_for_empty_file(self, tmp_path):
        from utils.video_utils import validate_video_file
        empty = tmp_path / "empty.mp4"
        empty.write_bytes(b"")
        with pytest.raises(ValueError, match="empty"):
            validate_video_file(empty)

    def test_raises_runtime_error_for_corrupt_file(self, tmp_path):
        from utils.video_utils import validate_video_file
        corrupt = tmp_path / "bad.mp4"
        corrupt.write_bytes(b"\x00\x01\x02\x03" * 64)  # garbage bytes
        with pytest.raises(RuntimeError):
            validate_video_file(corrupt)
