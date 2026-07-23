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
from typing import Optional

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


def validate_video_file(video_path: Path) -> None:
    """
    Perform pre-flight validation checks on a video file.

    Checks that the file exists, is non-empty, and can be opened by OpenCV.
    Raises a descriptive exception on the first failure so callers get a clear
    error message before attempting any processing.

    Args:
        video_path: Path to the video file to validate.

    Raises:
        FileNotFoundError: File does not exist.
        ValueError:        File is empty (zero bytes).
        RuntimeError:      OpenCV cannot open the file.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if video_path.stat().st_size == 0:
        raise ValueError(f"Video file is empty (0 bytes): {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    opened = cap.isOpened()
    cap.release()
    if not opened:
        raise RuntimeError(
            f"OpenCV cannot open video (unsupported codec or corrupted file): {video_path}"
        )


def get_video_aspect_ratio(video_path: Path) -> tuple[int, int]:
    """
    Return the display aspect ratio of a video as a reduced integer pair.

    For example, a 1920×1080 video returns (16, 9) and a 640×480 video
    returns (4, 3).

    Args:
        video_path: Path to the source video.

    Returns:
        Tuple (width_ratio, height_ratio) in lowest terms.

    Raises:
        RuntimeError: If the video cannot be opened or dimensions are invalid.
    """
    info = get_video_info(video_path)
    w, h = info["width"], info["height"]
    divisor = math.gcd(w, h)
    return (w // divisor, h // divisor)


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


def extract_frame_range(
    video_path: Path,
    start_frame: int,
    end_frame: int,
    output_dir: Path,
    quality: int = 2,
    name_template: str = "frame_{:06d}.jpg",
) -> list[Path]:
    """
    Extract a consecutive range of frames [start_frame, end_frame) to *output_dir*.

    Each frame is saved as a JPEG named according to *name_template* (which
    must contain exactly one ``{}`` positional placeholder for the frame index).

    Args:
        video_path:     Path to the source video.
        start_frame:    First frame index to extract (inclusive, zero-based).
        end_frame:      Last frame index (exclusive).
        output_dir:     Directory where extracted frames are saved (created if
                        it does not exist).
        quality:        JPEG quality passed to FFmpeg ``-q:v`` (1=best, 31=worst).
        name_template:  Filename format string, e.g. ``"frame_{:06d}.jpg"``.

    Returns:
        List of Paths that were successfully written.

    Raises:
        ValueError: If start_frame >= end_frame.
    """
    if start_frame >= end_frame:
        raise ValueError(
            f"start_frame ({start_frame}) must be less than end_frame ({end_frame})"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for idx in range(start_frame, end_frame):
        out_path = output_dir / name_template.format(idx)
        if extract_frame(video_path, idx, out_path, quality=quality):
            written.append(out_path)
    return written


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


def get_codec_info(video_path: Path) -> dict:
    """
    Return a structured summary of codec and container information for a video.

    Uses ``ffprobe`` under the hood and parses the JSON output to extract the
    most commonly needed fields.  Falls back to ``"unknown"`` for any field
    that ffprobe does not report.

    Args:
        video_path: Path to the video file.

    Returns:
        dict with keys:
            video_codec   — e.g. ``"h264"``
            pixel_fmt     — e.g. ``"yuv420p"``
            bit_rate_kbps — overall container bit-rate in kbps (int or None)
            audio_codec   — e.g. ``"aac"`` or ``None`` if no audio stream
    """
    import json

    raw = run_ffprobe(video_path)
    if not raw.strip():
        return {
            "video_codec": "unknown",
            "pixel_fmt": "unknown",
            "bit_rate_kbps": None,
            "audio_codec": None,
        }
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "video_codec": "unknown",
            "pixel_fmt": "unknown",
            "bit_rate_kbps": None,
            "audio_codec": None,
        }

    streams = data.get("streams", [])
    fmt = data.get("format", {})

    video_codec = "unknown"
    pixel_fmt = "unknown"
    audio_codec = None

    for stream in streams:
        ctype = stream.get("codec_type", "")
        if ctype == "video" and video_codec == "unknown":
            video_codec = stream.get("codec_name", "unknown")
            pixel_fmt = stream.get("pix_fmt", "unknown")
        elif ctype == "audio" and audio_codec is None:
            audio_codec = stream.get("codec_name")

    bit_rate_raw = fmt.get("bit_rate")
    bit_rate_kbps: Optional[int] = None
    if bit_rate_raw is not None:
        try:
            bit_rate_kbps = int(bit_rate_raw) // 1000
        except (ValueError, TypeError):
            pass

    return {
        "video_codec": video_codec,
        "pixel_fmt": pixel_fmt,
        "bit_rate_kbps": bit_rate_kbps,
        "audio_codec": audio_codec,
    }


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
