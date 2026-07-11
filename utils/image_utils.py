"""
utils/image_utils.py
====================
Image preprocessing helpers for the AI Video Restoration pipeline.

Provides reusable functions for loading, saving, colour-space conversion,
histogram analysis, and quality assessment that are shared across multiple
pipeline stages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_image_rgb(path: Path) -> np.ndarray:
    """
    Load an image from *path* and return it as an RGB uint8 array.

    OpenCV loads images in BGR order by default; this wrapper converts to RGB
    so that downstream code (CLIP, PIL integrations) does not need to remember
    the byte order.

    Args:
        path: Path to the image file (.jpg, .png, etc.).

    Returns:
        ``(H, W, 3)`` uint8 NumPy array in RGB channel order.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError:      If OpenCV cannot decode the image.
    """
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise RuntimeError(f"OpenCV could not decode image: {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def save_image_rgb(image: np.ndarray, path: Path, quality: int = 95) -> None:
    """
    Save an RGB uint8 image to *path* as a JPEG.

    Args:
        image:   ``(H, W, 3)`` uint8 array in RGB channel order.
        path:    Output file path.  Parent directory is created if missing.
        quality: JPEG quality (0–100, higher is better).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])


# ─────────────────────────────────────────────────────────────────────────────
#  Colour-space helpers
# ─────────────────────────────────────────────────────────────────────────────

def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert an RGB or BGR uint8 image to a single-channel grayscale image.

    Assumes the input is already in RGB order (as returned by
    :func:`load_image_rgb`).

    Args:
        image: ``(H, W, 3)`` uint8 array.

    Returns:
        ``(H, W)`` uint8 grayscale array.
    """
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def to_lab(image: np.ndarray) -> np.ndarray:
    """
    Convert an RGB uint8 image to CIE L*a*b* float32 representation.

    The L channel spans [0, 100] and a*, b* span [-127, 127].

    Args:
        image: ``(H, W, 3)`` uint8 array in RGB order.

    Returns:
        ``(H, W, 3)`` float32 array in L*a*b* order.
    """
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2Lab)


# ─────────────────────────────────────────────────────────────────────────────
#  Histogram helpers
# ─────────────────────────────────────────────────────────────────────────────

def compute_histogram(
    image: np.ndarray,
    bins: int = 256,
    normalize: bool = True,
) -> np.ndarray:
    """
    Compute a grayscale intensity histogram for *image*.

    Args:
        image:     ``(H, W)`` or ``(H, W, C)`` uint8 array.  Colour images are
                   converted to grayscale before histogram computation.
        bins:      Number of histogram bins (default: 256).
        normalize: If True, the histogram is L1-normalized to sum to 1.0.

    Returns:
        1-D float32 array of length *bins*.
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    hist = cv2.calcHist([gray], [0], None, [bins], [0, 256]).flatten()
    if normalize and hist.sum() > 0:
        hist = hist / hist.sum()
    return hist.astype(np.float32)


def histogram_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute the Bhattacharyya coefficient between two normalized histograms.

    A value of 1.0 means identical distributions; 0.0 means no overlap.

    Args:
        a: Normalized float32 histogram (same length as *b*).
        b: Normalized float32 histogram.

    Returns:
        Bhattacharyya coefficient in [0, 1].
    """
    if a.shape != b.shape or a.size == 0:
        return 0.0
    return float(np.sum(np.sqrt(a * b)))


# ─────────────────────────────────────────────────────────────────────────────
#  Quality metrics
# ─────────────────────────────────────────────────────────────────────────────

def estimate_blur(image: np.ndarray) -> float:
    """
    Estimate the blurriness of *image* using the variance of the Laplacian.

    Higher values indicate a sharper image.  Typical thresholds:
    - < 50:  likely blurry
    - 50–200: moderate sharpness
    - > 200:  sharp

    Args:
        image: ``(H, W)`` or ``(H, W, C)`` uint8 array.

    Returns:
        Variance of the Laplacian (float).
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def compute_psnr(
    reference: np.ndarray,
    restored: np.ndarray,
    max_pixel: float = 255.0,
) -> Optional[float]:
    """
    Compute the Peak Signal-to-Noise Ratio between *reference* and *restored*.

    Args:
        reference:  Ground-truth image ``(H, W[, C])`` uint8 or float.
        restored:   Restored/predicted image of the same shape.
        max_pixel:  Maximum possible pixel value (255 for uint8).

    Returns:
        PSNR in dB, or ``None`` if the images are identical (MSE == 0).
    """
    if reference.shape != restored.shape:
        raise ValueError(
            f"Shape mismatch: reference {reference.shape} vs restored {restored.shape}"
        )
    mse = float(np.mean((reference.astype(np.float64) - restored.astype(np.float64)) ** 2))
    if mse == 0.0:
        return None
    return 10.0 * np.log10((max_pixel ** 2) / mse)


# ─────────────────────────────────────────────────────────────────────────────
#  Crop and resize helpers
# ─────────────────────────────────────────────────────────────────────────────

def resize_with_padding(
    image: np.ndarray,
    target_hw: tuple[int, int],
    pad_value: int = 0,
) -> np.ndarray:
    """
    Resize *image* to fit exactly within *target_hw* (height, width) while
    preserving the aspect ratio, filling the remaining area with *pad_value*.

    This is equivalent to ``video_utils.resize_fit`` but operates on in-memory
    arrays and supports a configurable padding colour rather than only black.

    Args:
        image:      ``(H, W, C)`` or ``(H, W)`` uint8 array.
        target_hw:  (target_height, target_width) tuple.
        pad_value:  Scalar fill value for padded pixels (0 = black, 255 = white).

    Returns:
        ``(target_height, target_width[, C])`` uint8 array.
    """
    th, tw = target_hw
    sh, sw = image.shape[:2]
    scale = min(tw / sw, th / sh)
    nw = max(1, int(round(sw * scale)))
    nh = max(1, int(round(sh * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (nw, nh), interpolation=interp)

    if image.ndim == 3:
        canvas = np.full((th, tw, image.shape[2]), fill_value=pad_value, dtype=image.dtype)
    else:
        canvas = np.full((th, tw), fill_value=pad_value, dtype=image.dtype)

    y0, x0 = (th - nh) // 2, (tw - nw) // 2
    if image.ndim == 3:
        canvas[y0:y0 + nh, x0:x0 + nw] = resized
    else:
        canvas[y0:y0 + nh, x0:x0 + nw] = resized
    return canvas


def crop_center(
    image: np.ndarray,
    crop_hw: tuple[int, int],
) -> np.ndarray:
    """
    Extract a centre-aligned rectangular crop from *image*.

    If *crop_hw* is larger than the image in either dimension, the image is
    returned unchanged (no padding is added).

    Args:
        image:   ``(H, W[, C])`` array.
        crop_hw: (crop_height, crop_width) tuple.

    Returns:
        ``(crop_height, crop_width[, C])`` array, or the original image if
        the requested crop exceeds the image dimensions.
    """
    sh, sw = image.shape[:2]
    ch, cw = crop_hw
    if ch >= sh and cw >= sw:
        return image
    ch = min(ch, sh)
    cw = min(cw, sw)
    y0 = (sh - ch) // 2
    x0 = (sw - cw) // 2
    return image[y0:y0 + ch, x0:x0 + cw].copy()


# ─────────────────────────────────────────────────────────────────────────────
#  Edge detection helpers
# ─────────────────────────────────────────────────────────────────────────────

def canny_edges(
    image: np.ndarray,
    low_threshold: int = 50,
    high_threshold: int = 150,
) -> np.ndarray:
    """
    Compute Canny edge map for *image*.

    Args:
        image:          ``(H, W)`` or ``(H, W, C)`` uint8 array.
        low_threshold:  Lower hysteresis threshold.
        high_threshold: Upper hysteresis threshold.

    Returns:
        ``(H, W)`` uint8 binary edge map (255 = edge, 0 = non-edge).
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    return cv2.Canny(gray, low_threshold, high_threshold)


def gradient_magnitude(image: np.ndarray) -> np.ndarray:
    """
    Compute the gradient magnitude of *image* using Sobel operators.

    Useful for building confidence masks in the restoration pipeline
    (high gradient → reliable structure; low gradient → flat/smooth area).

    Args:
        image: ``(H, W)`` or ``(H, W, C)`` uint8 array.

    Returns:
        ``(H, W)`` float32 array with gradient magnitudes, normalised to [0, 1].
    """
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        gray = image.astype(np.float32)

    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)

    max_val = mag.max()
    if max_val > 0:
        mag /= max_val
    return mag


def edge_agreement(
    image_a: np.ndarray,
    image_b: np.ndarray,
    low_threshold: int = 50,
    high_threshold: int = 150,
) -> float:
    """
    Measure the spatial agreement between the Canny edges of two images.

    Agreement is computed as the Intersection-over-Union (IoU) of the two
    binary edge maps.  A value close to 1.0 means the images share the same
    structural layout; a value near 0.0 indicates misalignment.

    Args:
        image_a:        First image ``(H, W[, C])`` uint8.
        image_b:        Second image ``(H, W[, C])`` uint8 (must match shape).
        low_threshold:  Canny lower threshold.
        high_threshold: Canny upper threshold.

    Returns:
        IoU score in [0, 1].
    """
    edges_a = canny_edges(image_a, low_threshold, high_threshold) > 0
    edges_b = canny_edges(image_b, low_threshold, high_threshold) > 0

    intersection = np.logical_and(edges_a, edges_b).sum()
    union = np.logical_or(edges_a, edges_b).sum()

    if union == 0:
        return 1.0  # Both images have no edges → trivially identical
    return float(intersection) / float(union)
