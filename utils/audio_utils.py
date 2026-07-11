"""
utils/audio_utils.py
====================
Audio extraction and analysis helpers for the AI Video Restoration pipeline.

Provides FFmpeg-backed utilities for extracting audio tracks, checking audio
stream presence, and computing basic loudness statistics used by the audio
merge stage.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Audio stream detection
# ─────────────────────────────────────────────────────────────────────────────

def has_audio_stream(video_path: Path) -> bool:
    """
    Return True if *video_path* contains at least one audio stream.

    Uses ``ffprobe`` to inspect stream metadata without decoding any frames.

    Args:
        video_path: Path to the video (or audio) file.

    Returns:
        ``True`` if an audio stream is detected, ``False`` otherwise.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() == "audio"


def get_audio_duration(video_path: Path) -> Optional[float]:
    """
    Return the duration of the first audio stream in seconds, or ``None``.

    Args:
        video_path: Path to the video or audio file.

    Returns:
        Duration in seconds as a float, or ``None`` if no audio stream exists
        or the duration cannot be determined.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    raw = result.stdout.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Audio extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_audio(
    video_path: Path,
    output_path: Path,
    sample_rate: int = 44100,
    channels: int = 2,
) -> None:
    """
    Extract the audio track from *video_path* and write it to *output_path*.

    The audio is re-encoded to PCM WAV (lossless) at the given sample rate
    and channel count.  Use this when you need a raw waveform for further
    analysis; for simple audio pass-through use :func:`~utils.video_utils.merge_audio`.

    Args:
        video_path:  Path to the source video containing audio.
        output_path: Destination ``.wav`` file path.
        sample_rate: Output sample rate in Hz (default: 44100).
        channels:    Number of audio channels (1=mono, 2=stereo).

    Raises:
        RuntimeError: If FFmpeg exits with a non-zero code.
        ValueError:   If the source video has no audio stream.
    """
    if not has_audio_stream(video_path):
        raise ValueError(f"No audio stream found in: {video_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",                          # drop video stream
        "-acodec", "pcm_s16le",         # 16-bit PCM (WAV)
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg audio extraction failed for {video_path}:\n{result.stderr}"
        )


def extract_audio_segment(
    video_path: Path,
    output_path: Path,
    start_seconds: float,
    duration_seconds: float,
    sample_rate: int = 44100,
) -> None:
    """
    Extract a time-bounded segment of audio from *video_path*.

    Useful for processing only the audio that corresponds to a specific scene
    without loading the entire track.

    Args:
        video_path:       Path to the source video.
        output_path:      Destination ``.wav`` file path.
        start_seconds:    Segment start time in seconds.
        duration_seconds: Segment duration in seconds.
        sample_rate:      Output sample rate in Hz.

    Raises:
        RuntimeError: If FFmpeg exits with a non-zero code.
        ValueError:   If duration_seconds <= 0.
    """
    if duration_seconds <= 0:
        raise ValueError(f"duration_seconds must be positive, got {duration_seconds}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_seconds),
        "-t", str(duration_seconds),
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg audio segment extraction failed:\n{result.stderr}"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Loudness helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_loudness_stats(video_path: Path) -> dict:
    """
    Compute integrated loudness statistics using FFmpeg's ``ebur128`` filter.

    Runs FFmpeg in loudness-scan mode (no output file) and parses the summary
    line for Integrated loudness, True Peak, and Loudness Range values.

    Args:
        video_path: Path to the video or audio file.

    Returns:
        dict with keys:
            integrated_lufs — Integrated loudness in LUFS (float or None)
            true_peak_dbtp  — True peak in dBTP (float or None)
            lra_lu          — Loudness range in LU (float or None)

    Note:
        Returns ``None`` values for all fields if the file has no audio or
        ffmpeg output cannot be parsed.
    """
    empty: dict = {
        "integrated_lufs": None,
        "true_peak_dbtp": None,
        "lra_lu": None,
    }
    if not has_audio_stream(video_path):
        return empty

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-af", "ebur128=peak=true",
        "-f", "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    stats = dict(empty)
    for line in stderr.splitlines():
        line = line.strip()
        if "I:" in line and "LUFS" in line:
            try:
                stats["integrated_lufs"] = float(line.split("I:")[1].split("LUFS")[0].strip())
            except (IndexError, ValueError):
                pass
        if "True peak:" in line:
            try:
                stats["true_peak_dbtp"] = float(line.split("True peak:")[1].split("dBTP")[0].strip())
            except (IndexError, ValueError):
                pass
        if "LRA:" in line and "LU" in line:
            try:
                stats["lra_lu"] = float(line.split("LRA:")[1].split("LU")[0].strip())
            except (IndexError, ValueError):
                pass
    return stats
