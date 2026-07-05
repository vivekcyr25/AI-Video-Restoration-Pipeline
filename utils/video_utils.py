"""
utils/video_utils.py
====================
FFmpeg and OpenCV helper wrappers used throughout the pipeline.

These utilities standardise common video I/O operations and provide
helpful error messages when FFmpeg or OpenCV operations fail.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import cv2
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  Video metadata
# ─────────────────────────────────────────────────────────────────────────────

def get_video_info(video_path: Path) -> dict:
    """
    Return basic metadata for a video file using OpenCV.

    Returns
    -------
    dict with keys: fps, width, height, frame_count, duration_seconds

    Raises
    ------
    RuntimeError if the video cannot be opened or metadata is invalid.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps         = float(cap.get(cv2.CAP_PROP_FPS))
    width       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if not math.isfinite(fps) or fps <= 0:
        raise RuntimeError(f"Invalid FPS ({fps}) for video: {video_path}")
    if width <= 0 or height <= 0:
        raise RuntimeError(f"Invalid dimensions ({width}x{height}) for video: {video_path}")

    return {
        "fps":              fps,
        "width":            width,
        "height":           height,
        "frame_count":      frame_count,
        "duration_seconds": frame_count / fps,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Frame extraction helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_frame(
    video_path: Path,
    frame_index: int,
    output_path: Path,
    quality: int = 2,
) -> bool:
    """
    Extract a single frame at *frame_index* from *video_path* using FFmpeg.

    Args:
        video_path:  Path to the source video.
        frame_index: Zero-based frame number to extract.
        output_path: Where to write the JPEG (created if missing).
        quality:     JPEG quality (FFmpeg -q:v, 1=best, 31=worst).

    Returns:
        True on success, False if FFmpeg returned a non-zero exit code.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"select=eq(n\\,{frame_index})",
        "-vframes", "1",
        "-q:v", str(quality),
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def read_frame_at(cap: cv2.VideoCapture, frame_index: int) -> np.ndarray:
    """
    Seek to *frame_index* and read one frame using an already-open VideoCapture.

    Raises RuntimeError if the frame cannot be read.
    """
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"Cannot read frame {frame_index} from video")
    return frame


# ─────────────────────────────────────────────────────────────────────────────
#  Video writer
# ─────────────────────────────────────────────────────────────────────────────

def open_video_writer(
    path: Path,
    fps: float,
    width: int,
    height: int,
    fourcc: str = "mp4v",
) -> cv2.VideoWriter:
    """
    Open an OpenCV VideoWriter for writing MP4 frames.

    Args:
        path:   Output file path (parent directory created if needed).
        fps:    Frame rate.
        width:  Frame width in pixels.
        height: Frame height in pixels.
        fourcc: FourCC codec code (default: 'mp4v' for H.264-compatible MP4).

    Returns:
        An opened cv2.VideoWriter instance.

    Raises:
        RuntimeError if the writer cannot be opened.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*fourcc),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Cannot open video writer: {path}")
    return writer


# ─────────────────────────────────────────────────────────────────────────────
#  FFmpeg wrappers
# ─────────────────────────────────────────────────────────────────────────────

def merge_audio(
    silent_video: Path,
    audio_source: Path,
    output: Path,
) -> None:
    """
    Mux the audio track from *audio_source* into *silent_video* using FFmpeg.

    Both video and audio are stream-copied (no re-encoding).

    Args:
        silent_video: Path to the reconstructed video with no audio.
        audio_source: Path to the original video containing the audio stream.
        output:       Path to write the final muxed video.

    Raises:
        RuntimeError if FFmpeg exits with a non-zero code.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(audio_source),
        "-c:v", "copy",
        "-c:a", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg audio merge failed:\n{result.stderr}")


def run_ffprobe(video_path: Path) -> str:
    """
    Return raw ffprobe JSON output for *video_path*.

    Useful for debugging codec, container, and stream details.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


# ─────────────────────────────────────────────────────────────────────────────
#  Image resize helpers
# ─────────────────────────────────────────────────────────────────────────────

def resize_fit(image: np.ndarray, target_hw: tuple[int, int]) -> np.ndarray:
    """
    Scale *image* to fit within *target_hw* (height, width) while preserving
    aspect ratio. Pads with black to fill the remaining area.
    """
    th, tw = target_hw
    sh, sw = image.shape[:2]
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (nw, nh), interpolation=interp)
    canvas = np.zeros((th, tw, image.shape[2]), dtype=image.dtype)
    y0, x0 = (th - nh) // 2, (tw - nw) // 2
    canvas[y0:y0 + nh, x0:x0 + nw] = resized
    return canvas


def resize_cover(image: np.ndarray, target_hw: tuple[int, int]) -> np.ndarray:
    """
    Scale *image* to cover *target_hw* completely (no black bars),
    cropping the overflow from the centre.
    """
    th, tw = target_hw
    sh, sw = image.shape[:2]
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (nw, nh), interpolation=interp)
    x0, y0 = max(0, (nw - tw) // 2), max(0, (nh - th) // 2)
    return resized[y0:y0 + th, x0:x0 + tw].copy()
