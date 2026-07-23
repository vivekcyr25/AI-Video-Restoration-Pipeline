"""
utils/image_enhancement.py
===========================
Image enhancement utilities for reference-guided color, skin, and detail restoration.
Provides CLAHE, color transfer, white-balance, histogram matching, guided filtering,
and edge enhancement.
"""

from __future__ import annotations

import cv2
import numpy as np


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L channel of Lab space.
    
    Args:
        image: RGB uint8 image of shape (H, W, 3)
        clip_limit: CLAHE threshold for contrast limiting
        grid_size: Size of grid for histogram equalization
        
    Returns:
        Enhanced RGB image
    """
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2Lab)
    l_channel, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    cl = clahe.apply(l_channel)
    
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_Lab2RGB)


def color_transfer(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """
    Transfer color statistics (mean and std dev) from source to target image in Lab space (Reinhard's method).
    
    Args:
        source: RGB uint8 image of high-quality reference (album photo)
        target: RGB uint8 image of target image to modify (video frame)
        
    Returns:
        Color-matched RGB uint8 image
    """
    # Convert images to Lab color space
    src_lab = cv2.cvtColor(source, cv2.COLOR_RGB2Lab).astype(np.float32)
    tgt_lab = cv2.cvtColor(target, cv2.COLOR_RGB2Lab).astype(np.float32)
    
    # Compute mean and standard deviation for both
    src_mean, src_std = cv2.meanStdDev(src_lab)
    tgt_mean, tgt_std = cv2.meanStdDev(tgt_lab)
    
    src_mean = src_mean.flatten()
    src_std = src_std.flatten()
    tgt_mean = tgt_mean.flatten()
    tgt_std = tgt_std.flatten()
    
    # Reshape for broadcasting
    src_mean = src_mean.reshape(1, 1, 3)
    src_std = src_std.reshape(1, 1, 3)
    tgt_mean = tgt_mean.reshape(1, 1, 3)
    tgt_std = tgt_std.reshape(1, 1, 3)
    
    # Subtract mean from target
    res = tgt_lab - tgt_mean
    
    # Scale by std deviation ratio
    eps = 1e-6
    res = res * (src_std / (tgt_std + eps))
    
    # Add source mean
    res = res + src_mean
    
    # Clip to valid Lab range and convert back
    res = np.clip(res, 0, 255).astype(np.uint8)
    return cv2.cvtColor(res, cv2.COLOR_Lab2RGB)


def white_balance_gray_world(image: np.ndarray) -> np.ndarray:
    """
    Apply Gray World hypothesis white balancing.
    
    Args:
        image: RGB uint8 image
        
    Returns:
        White-balanced RGB uint8 image
    """
    # Compute channel averages
    avg_r = np.mean(image[:, :, 0])
    avg_g = np.mean(image[:, :, 1])
    avg_b = np.mean(image[:, :, 2])
    
    avg_gray = (avg_r + avg_g + avg_b) / 3.0
    if avg_r == 0 or avg_g == 0 or avg_b == 0:
        return image.copy()
        
    scale_r = avg_gray / avg_r
    scale_g = avg_gray / avg_g
    scale_b = avg_gray / avg_b
    
    # Scale channels
    res = np.zeros_like(image, dtype=np.float32)
    res[:, :, 0] = image[:, :, 0] * scale_r
    res[:, :, 1] = image[:, :, 1] * scale_g
    res[:, :, 2] = image[:, :, 2] * scale_b
    
    return np.clip(res, 0, 255).astype(np.uint8)


def histogram_matching(source: np.ndarray, template: np.ndarray) -> np.ndarray:
    """
    Match the histogram of source to template channel-by-channel.
    
    Args:
        source: RGB uint8 image (to modify)
        template: RGB uint8 image (target distribution)
        
    Returns:
        Histogram-matched RGB uint8 image
    """
    old_shape = source.shape
    source = source.ravel()
    template = template.ravel()
    
    # Get unique pixel values, their indices, and counts
    s_vals, bin_idx, s_counts = np.unique(source, return_inverse=True, return_counts=True)
    t_vals, t_counts = np.unique(template, return_counts=True)
    
    # Cumulative distributions
    s_quantiles = np.cumsum(s_counts).astype(np.float64) / source.size
    t_quantiles = np.cumsum(t_counts).astype(np.float64) / template.size
    
    # Interpolate template values onto source quantiles
    interp_t_vals = np.interp(s_quantiles, t_quantiles, t_vals)
    
    return interp_t_vals[bin_idx].reshape(old_shape).astype(np.uint8)


def edge_enhancement(image: np.ndarray, strength: float = 0.5) -> np.ndarray:
    """
    Apply unsharp masking edge enhancement to sharpen the image.
    
    Args:
        image: RGB uint8 image
        strength: Blending weight of detail (higher = sharper)
        
    Returns:
        Sharpened RGB uint8 image
    """
    # Blurring with Gaussian filter
    blurred = cv2.GaussianBlur(image, (0, 0), 3.0)
    sharpened = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def guided_filter(I: np.ndarray, p: np.ndarray, r: int = 4, eps: float = 0.01) -> np.ndarray:
    """
    Guided Filter implementation for edge-preserving smoothing.
    Suitable for skin smoothing when I = guidance image (e.g. grayscale) and p = input image.
    
    Args:
        I: Guidance image (grayscale or RGB, float32 normalized to [0,1])
        p: Input image (grayscale or RGB, float32 normalized to [0,1])
        r: Local window radius
        eps: Regularization parameter
        
    Returns:
        Filtered image (float32 [0,1])
    """
    # Normalize to [0, 1] if input is uint8
    i_is_uint8 = I.dtype == np.uint8
    p_is_uint8 = p.dtype == np.uint8
    
    if i_is_uint8:
        I = I.astype(np.float32) / 255.0
    if p_is_uint8:
        p = p.astype(np.float32) / 255.0
        
    # Expand dimensions of guidance image if it is grayscale and input is color
    if I.ndim == 2 and p.ndim == 3:
        I = np.expand_dims(I, axis=-1)
        
    # Helper to calculate local mean
    def mean_filter(img):
        res = cv2.boxFilter(img, -1, (r, r), borderType=cv2.BORDER_REFLECT)
        if img.ndim == 3 and res.ndim == 2:
            res = np.expand_dims(res, axis=-1)
        return res
        
    mean_I = mean_filter(I)
    mean_p = mean_filter(p)
    mean_Ip = mean_filter(I * p)
    
    # Covariance of (I, p)
    cov_Ip = mean_Ip - mean_I * mean_p
    
    mean_II = mean_filter(I * I)
    # Variance of I
    var_I = mean_II - mean_I * mean_I
    
    # Linear coefficients a and b
    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I
    
    mean_a = mean_filter(a)
    mean_b = mean_filter(b)
    
    q = mean_a * I + mean_b
    
    if p_is_uint8:
        q = np.clip(q * 255.0, 0, 255).astype(np.uint8)
        
    return q
