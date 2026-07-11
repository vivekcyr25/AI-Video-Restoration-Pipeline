"""
tests/test_scene_utils.py
=========================
Unit tests for utils/scene_utils.py.

All tests use in-memory CSV content written to tmp_path fixtures —
no real scene CSV files from the pipeline are required.
"""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest

from utils.scene_utils import (
    Scene,
    load_scenes,
    find_scene_for_frame,
    iter_scene_representative_frames,
    filter_scenes_by_duration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "scenes.csv"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


SAMPLE_CSV = """
    Scene Number,Start Frame,End Frame,Start Time (seconds),End Time (seconds)
    1,0,29,0.0,1.0
    2,30,89,1.0,3.0
    3,90,119,3.0,4.0
"""


# ---------------------------------------------------------------------------
# Scene dataclass
# ---------------------------------------------------------------------------

class TestSceneDataclass:
    def _scene(self, start=0, end=29):
        return Scene(
            scene_number=1,
            start_frame=start,
            end_frame=end,
            start_time=0.0,
            end_time=1.0,
        )

    def test_frame_count(self):
        s = self._scene(0, 29)
        assert s.frame_count == 30

    def test_duration_seconds(self):
        s = Scene(1, 0, 29, 0.0, 2.5)
        assert s.duration_seconds == pytest.approx(2.5)

    def test_midpoint_frame(self):
        s = self._scene(0, 30)
        assert s.midpoint_frame == 15

    def test_frame_indices_range(self):
        s = self._scene(5, 9)
        assert list(s.frame_indices()) == [5, 6, 7, 8, 9]

    def test_is_frozen(self):
        s = self._scene()
        with pytest.raises((AttributeError, TypeError)):
            s.scene_number = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_scenes
# ---------------------------------------------------------------------------

class TestLoadScenes:
    def test_load_basic_csv(self, tmp_path):
        p = _write_csv(tmp_path, SAMPLE_CSV)
        scenes = load_scenes(p)
        assert len(scenes) == 3
        assert scenes[0].scene_number == 1
        assert scenes[0].start_frame == 0
        assert scenes[0].end_frame == 29
        assert scenes[1].start_frame == 30
        assert scenes[2].end_frame == 119

    def test_sorted_by_scene_number(self, tmp_path):
        # Write in reverse order
        content = """
            Scene Number,Start Frame,End Frame,Start Time (seconds),End Time (seconds)
            3,90,119,3.0,4.0
            1,0,29,0.0,1.0
            2,30,89,1.0,3.0
        """
        p = _write_csv(tmp_path, content)
        scenes = load_scenes(p)
        numbers = [s.scene_number for s in scenes]
        assert numbers == sorted(numbers)

    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_scenes(tmp_path / "nonexistent.csv")

    def test_raises_on_missing_frame_columns(self, tmp_path):
        content = "SceneNum,StartTime,EndTime\n1,0.0,1.0\n"
        p = tmp_path / "bad.csv"
        p.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError):
            load_scenes(p)

    def test_float_frame_values_cast_correctly(self, tmp_path):
        """Some exporters write frame numbers as floats (e.g. 29.0)."""
        content = """
            Scene Number,Start Frame,End Frame,Start Time (seconds),End Time (seconds)
            1,0.0,29.0,0.0,1.0
        """
        p = _write_csv(tmp_path, content)
        scenes = load_scenes(p)
        assert isinstance(scenes[0].start_frame, int)
        assert scenes[0].start_frame == 0


# ---------------------------------------------------------------------------
# find_scene_for_frame
# ---------------------------------------------------------------------------

class TestFindSceneForFrame:
    def _scenes(self):
        return [
            Scene(1, 0, 29, 0.0, 1.0),
            Scene(2, 30, 89, 1.0, 3.0),
            Scene(3, 90, 119, 3.0, 4.0),
        ]

    def test_finds_first_scene(self):
        result = find_scene_for_frame(self._scenes(), 0)
        assert result is not None
        assert result.scene_number == 1

    def test_finds_last_scene(self):
        result = find_scene_for_frame(self._scenes(), 119)
        assert result is not None
        assert result.scene_number == 3

    def test_returns_none_for_out_of_range(self):
        result = find_scene_for_frame(self._scenes(), 200)
        assert result is None

    def test_boundary_frame(self):
        result = find_scene_for_frame(self._scenes(), 30)
        assert result is not None
        assert result.scene_number == 2


# ---------------------------------------------------------------------------
# iter_scene_representative_frames
# ---------------------------------------------------------------------------

class TestIterSceneRepresentativeFrames:
    def test_yields_midpoint_frames(self):
        scenes = [Scene(1, 0, 10, 0.0, 1.0), Scene(2, 11, 20, 1.0, 2.0)]
        pairs = list(iter_scene_representative_frames(scenes))
        assert pairs[0][0] == 5   # midpoint of [0, 10]
        assert pairs[1][0] == 15  # midpoint of [11, 20]

    def test_yields_correct_scene_objects(self):
        scenes = [Scene(1, 0, 10, 0.0, 1.0)]
        frame, scene = next(iter(iter_scene_representative_frames(scenes)))
        assert scene.scene_number == 1


# ---------------------------------------------------------------------------
# filter_scenes_by_duration
# ---------------------------------------------------------------------------

class TestFilterScenesByDuration:
    def _scenes(self):
        return [
            Scene(1, 0, 14, 0.0, 0.5),   # 0.5 s  — on the boundary
            Scene(2, 15, 59, 0.5, 2.0),  # 1.5 s  — should pass
            Scene(3, 60, 89, 2.0, 3.0),  # 1.0 s  — should pass
            Scene(4, 90, 91, 3.0, 3.067), # 0.067 s — too short
        ]

    def test_default_min_filters_very_short_scenes(self):
        result = filter_scenes_by_duration(self._scenes(), min_seconds=0.5)
        # Scene 4 (0.067 s) should be excluded
        assert all(s.duration_seconds >= 0.5 for s in result)
        assert not any(s.scene_number == 4 for s in result)

    def test_max_seconds_filters_long_scenes(self):
        result = filter_scenes_by_duration(self._scenes(), min_seconds=0.0, max_seconds=1.0)
        assert all(s.duration_seconds <= 1.0 for s in result)

    def test_empty_input_returns_empty(self):
        assert filter_scenes_by_duration([]) == []
