"""
utils/scene_utils.py
====================
Scene boundary parsing and frame-range helpers for the AI Video Restoration
pipeline.

Provides utilities for loading the scenes CSV produced by Stage 1
(``01_extract_scenes.sh``) and converting scene metadata into the frame
index ranges needed by later pipeline stages.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# ─────────────────────────────────────────────────────────────────────────────
#  Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Scene:
    """
    Represents a single detected scene with its frame boundaries.

    Attributes:
        scene_number: 1-based scene index as written by PySceneDetect.
        start_frame:  First frame of the scene (inclusive, zero-based).
        end_frame:    Last frame of the scene (inclusive, zero-based).
        start_time:   Scene start time in seconds.
        end_time:     Scene end time in seconds.
    """
    scene_number: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float

    @property
    def frame_count(self) -> int:
        """Number of frames in the scene."""
        return max(0, self.end_frame - self.start_frame + 1)

    @property
    def duration_seconds(self) -> float:
        """Duration of the scene in seconds."""
        return max(0.0, self.end_time - self.start_time)

    @property
    def midpoint_frame(self) -> int:
        """Zero-based index of the central frame in the scene."""
        return (self.start_frame + self.end_frame) // 2

    def frame_indices(self) -> range:
        """Return a range of all frame indices in this scene."""
        return range(self.start_frame, self.end_frame + 1)


# ─────────────────────────────────────────────────────────────────────────────
#  CSV loading
# ─────────────────────────────────────────────────────────────────────────────

# Expected column names produced by PySceneDetect CSV output.
_COL_SCENE   = ("scene number", "scene", "scene_number", "number")
_COL_START_F = ("start frame", "start_frame", "start frame #")
_COL_END_F   = ("end frame", "end_frame", "end frame #")
_COL_START_T = ("start time (seconds)", "start_time", "start time")
_COL_END_T   = ("end time (seconds)", "end_time", "end time")


def _find_col(fieldnames: list[str], candidates: tuple[str, ...]) -> str | None:
    lowered = {f.lower().strip(): f for f in fieldnames}
    for cand in candidates:
        for key, orig in lowered.items():
            if cand in key:
                return orig
    return None


def load_scenes(csv_path: Path) -> list[Scene]:
    """
    Parse the PySceneDetect scenes CSV and return a sorted list of
    :class:`Scene` objects.

    The CSV is expected to have (at minimum) columns for scene number,
    start frame, end frame, start time, and end time.  Column names are
    matched case-insensitively and flexibly (e.g. "Start Frame #" matches).

    Args:
        csv_path: Path to the scenes CSV file.

    Returns:
        List of :class:`Scene` objects sorted by ``scene_number``.

    Raises:
        FileNotFoundError: If *csv_path* does not exist.
        ValueError:        If required columns cannot be found.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Scenes CSV not found: {csv_path}")

    scenes: list[Scene] = []

    with csv_path.open("r", newline="", encoding="utf-8-sig") as fh:
        lines = [line for line in fh if line.strip()]
        reader = csv.DictReader(lines)
        fields = list(reader.fieldnames or [])

        col_scene   = _find_col(fields, _COL_SCENE)
        col_start_f = _find_col(fields, _COL_START_F)
        col_end_f   = _find_col(fields, _COL_END_F)
        col_start_t = _find_col(fields, _COL_START_T)
        col_end_t   = _find_col(fields, _COL_END_T)

        if col_start_f is None or col_end_f is None:
            raise ValueError(
                f"Could not find start/end frame columns in {csv_path}. "
                f"Available columns: {fields}"
            )

        for row_num, row in enumerate(reader, start=1):
            try:
                scene = Scene(
                    scene_number=int(row[col_scene]) if col_scene else row_num,
                    start_frame=int(float(row[col_start_f])),
                    end_frame=int(float(row[col_end_f])),
                    start_time=float(row[col_start_t]) if col_start_t else 0.0,
                    end_time=float(row[col_end_t]) if col_end_t else 0.0,
                )
                scenes.append(scene)
            except (ValueError, KeyError):
                continue  # skip malformed rows

    return sorted(scenes, key=lambda s: s.scene_number)


# ─────────────────────────────────────────────────────────────────────────────
#  Frame lookup helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_scene_for_frame(scenes: list[Scene], frame_index: int) -> Scene | None:
    """
    Return the scene that contains *frame_index*, or ``None`` if not found.

    Uses a linear scan; for large scene lists a binary search can be
    substituted if performance is critical.

    Args:
        scenes:      List of :class:`Scene` objects (sorted by start frame).
        frame_index: Zero-based frame number to look up.

    Returns:
        The matching :class:`Scene` or ``None``.
    """
    for scene in scenes:
        if scene.start_frame <= frame_index <= scene.end_frame:
            return scene
    return None


def iter_scene_representative_frames(
    scenes: list[Scene],
) -> Iterator[tuple[int, Scene]]:
    """
    Yield ``(representative_frame_index, scene)`` pairs for all scenes.

    The representative frame is the scene's midpoint frame, matching the
    selection strategy used in ``02_extract_frames.sh``.

    Args:
        scenes: List of :class:`Scene` objects.

    Yields:
        ``(midpoint_frame_index, scene)`` tuples.
    """
    for scene in scenes:
        yield scene.midpoint_frame, scene


def filter_scenes_by_duration(
    scenes: list[Scene],
    min_seconds: float = 0.5,
    max_seconds: float | None = None,
) -> list[Scene]:
    """
    Return only scenes whose duration falls within [*min_seconds*, *max_seconds*].

    Args:
        scenes:      List of :class:`Scene` objects.
        min_seconds: Minimum duration to keep (default 0.5 s).
        max_seconds: Maximum duration to keep (``None`` = no upper bound).

    Returns:
        Filtered list of scenes.
    """
    result = []
    for scene in scenes:
        dur = scene.duration_seconds
        if dur < min_seconds:
            continue
        if max_seconds is not None and dur > max_seconds:
            continue
        result.append(scene)
    return result
