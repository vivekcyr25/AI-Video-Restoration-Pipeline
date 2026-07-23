"""
tests/test_pipeline_redesign.py
===============================
Unit tests for utils/image_enhancement.py and utils/temporal_utils.py.
"""

from __future__ import annotations

import numpy as np
import pytest

from utils.image_enhancement import (
    apply_clahe,
    color_transfer,
    white_balance_gray_world,
    histogram_matching,
    edge_enhancement,
    guided_filter,
)
from utils.temporal_utils import (
    remove_flicker_global,
    smooth_temporal_guided,
)


def _generate_synthetic_image(h: int, w: int, noise_level: float = 0.0) -> np.ndarray:
    """Helper to generate a synthetic RGB image with color gradients."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            img[y, x] = [
                int((x / w) * 255),
                int((y / h) * 255),
                int(((x + y) / (w + h)) * 255),
            ]
    if noise_level > 0:
        noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return img


class TestImageEnhancement:
    def test_apply_clahe(self):
        img = _generate_synthetic_image(64, 64)
        enhanced = apply_clahe(img, clip_limit=3.0, grid_size=(4, 4))
        assert enhanced.shape == img.shape
        assert enhanced.dtype == np.uint8

    def test_color_transfer(self):
        src = np.ones((64, 64, 3), dtype=np.uint8) * 180  # bright grey
        tgt = np.ones((64, 64, 3), dtype=np.uint8) * 50   # dark grey
        transferred = color_transfer(src, tgt)
        assert transferred.shape == tgt.shape
        assert transferred.dtype == np.uint8
        # The transferred image mean should be shifted towards the source mean
        assert transferred.mean() > 50

    def test_white_balance_gray_world(self):
        # Image biased heavily towards red
        img = _generate_synthetic_image(32, 32)
        img[:, :, 0] = np.clip(img[:, :, 0].astype(int) + 100, 0, 255).astype(np.uint8)
        balanced = white_balance_gray_world(img)
        assert balanced.shape == img.shape
        assert balanced.dtype == np.uint8

    def test_histogram_matching(self):
        src = _generate_synthetic_image(32, 32)
        tmpl = _generate_synthetic_image(32, 32) * 2
        matched = histogram_matching(src, tmpl)
        assert matched.shape == src.shape
        assert matched.dtype == np.uint8

    def test_edge_enhancement(self):
        img = _generate_synthetic_image(64, 64, noise_level=5.0)
        sharpened = edge_enhancement(img, strength=1.0)
        assert sharpened.shape == img.shape
        assert sharpened.dtype == np.uint8

    def test_guided_filter(self):
        I = np.ones((32, 32), dtype=np.uint8) * 128
        p = np.ones((32, 32, 3), dtype=np.uint8) * 128
        res = guided_filter(I, p, r=4, eps=0.01)
        assert res.shape == p.shape
        assert res.dtype == np.uint8


class TestTemporalUtils:
    def test_remove_flicker_global(self):
        # Generate sequence of frames with global exposure variation
        frames = []
        for bias in [100, 150, 110, 140, 120]:
            img = np.ones((32, 32, 3), dtype=np.uint8) * bias
            frames.append(img)
            
        flicker_free = remove_flicker_global(frames, window_size=3)
        assert len(flicker_free) == len(frames)
        # Check that the standard deviation of means is reduced after smoothing
        original_means = [f.mean() for f in frames]
        restored_means = [f.mean() for f in flicker_free]
        assert np.std(restored_means) < np.std(original_means)

    def test_smooth_temporal_guided(self):
        frames = [_generate_synthetic_image(32, 32, noise_level=10.0) for _ in range(5)]
        smoothed = smooth_temporal_guided(frames, alpha=0.5)
        assert len(smoothed) == len(frames)
        assert smoothed[0].shape == frames[0].shape
