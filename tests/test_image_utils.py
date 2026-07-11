"""
tests/test_image_utils.py
=========================
Unit tests for utils/image_utils.py.

Tests operate on synthetic NumPy arrays — no real image files are required.
File I/O tests use pytest's tmp_path fixture.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from utils.image_utils import (
    load_image_rgb,
    save_image_rgb,
    to_grayscale,
    to_lab,
    compute_histogram,
    histogram_similarity,
    estimate_blur,
    compute_psnr,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid_rgb(h: int, w: int, r: int, g: int, b: int) -> np.ndarray:
    """Return a solid-colour RGB image."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = [r, g, b]
    return img


# ---------------------------------------------------------------------------
# load_image_rgb / save_image_rgb (round-trip)
# ---------------------------------------------------------------------------

class TestImageIO:
    def test_save_and_reload_roundtrip(self, tmp_path):
        """Saved image should survive a JPEG round-trip with low error."""
        img = _solid_rgb(64, 64, 200, 100, 50)
        out = tmp_path / "test.jpg"
        save_image_rgb(img, out, quality=99)
        reloaded = load_image_rgb(out)
        # JPEG is lossy but with quality=99 the error should be small
        assert np.mean(np.abs(img.astype(int) - reloaded.astype(int))) < 5.0

    def test_load_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_image_rgb(tmp_path / "missing.jpg")

    def test_save_creates_parent_dirs(self, tmp_path):
        img = _solid_rgb(32, 32, 128, 128, 128)
        out = tmp_path / "nested" / "deep" / "img.jpg"
        save_image_rgb(img, out)
        assert out.exists()


# ---------------------------------------------------------------------------
# to_grayscale
# ---------------------------------------------------------------------------

class TestToGrayscale:
    def test_output_shape(self):
        img = _solid_rgb(48, 64, 128, 64, 32)
        gray = to_grayscale(img)
        assert gray.shape == (48, 64)

    def test_all_channels_same_gives_gray_equal_to_luminance(self):
        """Pure gray input should produce a uniform grayscale image."""
        img = _solid_rgb(16, 16, 127, 127, 127)
        gray = to_grayscale(img)
        assert gray.min() == gray.max()


# ---------------------------------------------------------------------------
# to_lab
# ---------------------------------------------------------------------------

class TestToLab:
    def test_output_shape(self):
        img = _solid_rgb(16, 16, 255, 0, 0)
        lab = to_lab(img)
        assert lab.shape == (16, 16, 3)
        assert lab.dtype == np.float32

    def test_pure_black_has_L_zero(self):
        img = _solid_rgb(8, 8, 0, 0, 0)
        lab = to_lab(img)
        np.testing.assert_allclose(lab[:, :, 0], 0.0, atol=1.0)

    def test_pure_white_has_L_near_100(self):
        img = _solid_rgb(8, 8, 255, 255, 255)
        lab = to_lab(img)
        assert lab[:, :, 0].mean() > 90.0


# ---------------------------------------------------------------------------
# compute_histogram
# ---------------------------------------------------------------------------

class TestComputeHistogram:
    def test_output_length(self):
        img = _solid_rgb(32, 32, 100, 100, 100)
        hist = compute_histogram(img, bins=256)
        assert len(hist) == 256

    def test_normalized_sums_to_one(self):
        img = _solid_rgb(32, 32, 100, 100, 100)
        hist = compute_histogram(img, normalize=True)
        np.testing.assert_allclose(hist.sum(), 1.0, atol=1e-5)

    def test_unnormalized_sums_to_pixel_count(self):
        img = _solid_rgb(10, 10, 200, 200, 200)
        hist = compute_histogram(img, normalize=False)
        assert hist.sum() == 100  # 10×10 = 100 pixels

    def test_single_color_histogram_spike(self):
        """A uniform image should have one non-zero bin."""
        img = _solid_rgb(8, 8, 200, 200, 200)
        hist = compute_histogram(img, normalize=False)
        non_zero = np.count_nonzero(hist)
        assert non_zero == 1


# ---------------------------------------------------------------------------
# histogram_similarity
# ---------------------------------------------------------------------------

class TestHistogramSimilarity:
    def test_identical_histograms_similarity_one(self):
        h = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float32)
        assert abs(histogram_similarity(h, h) - 1.0) < 1e-5

    def test_disjoint_histograms_similarity_zero(self):
        a = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        assert histogram_similarity(a, b) == 0.0

    def test_shape_mismatch_returns_zero(self):
        a = np.ones(4, dtype=np.float32) / 4
        b = np.ones(8, dtype=np.float32) / 8
        assert histogram_similarity(a, b) == 0.0


# ---------------------------------------------------------------------------
# estimate_blur
# ---------------------------------------------------------------------------

class TestEstimateBlur:
    def test_uniform_image_has_zero_variance(self):
        """A completely flat image has no edges → Laplacian variance ≈ 0."""
        img = _solid_rgb(64, 64, 128, 128, 128)
        score = estimate_blur(img)
        assert score < 1.0

    def test_sharp_gradient_has_high_variance(self):
        """Half-black, half-white image has a hard edge → high Laplacian."""
        img = np.zeros((64, 64, 3), dtype=np.uint8)
        img[:, 32:] = 255
        score = estimate_blur(img)
        assert score > 100.0

    def test_grayscale_input_accepted(self):
        gray = np.zeros((32, 32), dtype=np.uint8)
        score = estimate_blur(gray)
        assert isinstance(score, float)


# ---------------------------------------------------------------------------
# compute_psnr
# ---------------------------------------------------------------------------

class TestComputePSNR:
    def test_identical_images_returns_none(self):
        img = _solid_rgb(16, 16, 100, 100, 100)
        assert compute_psnr(img, img) is None

    def test_psnr_decreases_with_more_noise(self):
        rng = np.random.default_rng(0)
        ref = rng.integers(0, 255, (64, 64, 3), dtype=np.uint8)
        low_noise = np.clip(ref.astype(int) + rng.integers(-5, 5, ref.shape), 0, 255).astype(np.uint8)
        high_noise = np.clip(ref.astype(int) + rng.integers(-50, 50, ref.shape), 0, 255).astype(np.uint8)
        psnr_low = compute_psnr(ref, low_noise)
        psnr_high = compute_psnr(ref, high_noise)
        assert psnr_low > psnr_high

    def test_shape_mismatch_raises(self):
        ref = _solid_rgb(16, 16, 128, 128, 128)
        other = _solid_rgb(32, 32, 128, 128, 128)
        with pytest.raises(ValueError):
            compute_psnr(ref, other)
