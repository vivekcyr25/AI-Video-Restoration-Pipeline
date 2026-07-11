"""
AI Video Restoration — Utility Modules
=======================================

Shared helpers for the AI Video Restoration pipeline scripts.

Submodules
----------
video_utils
    FFmpeg and OpenCV wrappers for video I/O, frame extraction, codec
    inspection, and image resizing.

audio_utils
    FFmpeg-backed utilities for audio stream detection, extraction,
    segmentation, and EBU R128 loudness analysis.

image_utils
    Image I/O with RGB/LAB/grayscale conversion, histogram comparison,
    blur estimation, PSNR quality metrics, edge detection (Canny/Sobel),
    CLAHE luminance enhancement, and unsharp mask sharpening.

matcher_utils
    Embedding loading, L2 normalisation, cosine similarity (including
    memory-efficient batched variant), top-k selection, confidence
    filtering, and match-result persistence.

scene_utils
    PySceneDetect CSV parsing into typed Scene objects, frame-index
    lookup, representative frame iteration, and duration-based filtering.
"""

__all__ = [
    "video_utils",
    "audio_utils",
    "image_utils",
    "matcher_utils",
    "scene_utils",
]
