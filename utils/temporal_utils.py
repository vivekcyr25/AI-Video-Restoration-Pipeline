"""
utils/temporal_utils.py
======================
Temporal smoothing and flicker removal utilities for ensuring inter-frame
consistency in restored videos.
"""

from __future__ import annotations

import cv2
import numpy as np


def remove_flicker_global(
    frames: list[np.ndarray],
    window_size: int = 5,
) -> list[np.ndarray]:
    """
    Remove global exposure flicker across a sequence of frames.
    It computes the rolling average of the luminance (L) channel mean and
    scales the L channel of each frame to match it, preserving original colors.
    
    Args:
        frames: List of RGB uint8 images
        window_size: Odd integer for the rolling window size
        
    Returns:
        List of flicker-reduced RGB uint8 images
    """
    if len(frames) < 3:
        return [f.copy() for f in frames]
        
    # Standardize window size to be odd
    if window_size % 2 == 0:
        window_size += 1
        
    # Convert frames to Lab and compute mean of L channel
    lab_frames = [cv2.cvtColor(f, cv2.COLOR_RGB2Lab) for f in frames]
    l_means = [np.mean(lab[:, :, 0]) for lab in lab_frames]
    
    # Pad boundaries to handle rolling average
    pad_width = window_size // 2
    padded_means = np.pad(l_means, pad_width, mode="edge")
    
    # Compute rolling average
    kernel = np.ones(window_size) / window_size
    smoothed_means = np.convolve(padded_means, kernel, mode="valid")
    
    restored_frames = []
    for t, lab in enumerate(lab_frames):
        l, a, b = cv2.split(lab)
        current_mean = l_means[t]
        target_mean = smoothed_means[t]
        
        if current_mean > 0:
            scale = target_mean / current_mean
            l_new = np.clip(l.astype(np.float32) * scale, 0, 255).astype(np.uint8)
        else:
            l_new = l
            
        merged = cv2.merge((l_new, a, b))
        restored_frames.append(cv2.cvtColor(merged, cv2.COLOR_Lab2RGB))
        
    return restored_frames


def smooth_temporal_guided(
    frames: list[np.ndarray],
    alpha: float = 0.65,
) -> list[np.ndarray]:
    """
    Smooth consecutive frames temporally using an exponential moving average (EMA)
    blending, reducing high-frequency jitter and temporal noise.
    
    Args:
        frames: List of RGB uint8 images
        alpha: Smoothing weight (higher = closer to current frame, lower = smoother)
        
    Returns:
        Temporally smoothed list of RGB uint8 images
    """
    if not frames:
        return []
        
    smoothed = [frames[0].copy()]
    for t in range(1, len(frames)):
        prev = smoothed[-1].astype(np.float32)
        curr = frames[t].astype(np.float32)
        
        # Simple temporal smoothing blended with current frame
        blend = prev * (1 - alpha) + curr * alpha
        smoothed.append(np.clip(blend, 0, 255).astype(np.uint8))
        
    return smoothed
