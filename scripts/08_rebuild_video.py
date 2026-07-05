#!/usr/bin/env python3
"""
Stage 6 — Full Video Reconstruction via Optical Flow Propagation
=================================================================
Reconstructs the fully restored video by propagating enhancement deltas
from restored representative frames to every frame within each scene,
using Farnebäck dense optical flow to ensure temporal coherence.

Algorithm overview
------------------
For each scene:
1. Read the original representative frame from the source video.
2. Load the corresponding restored frame from disk.
3. Compute the enhancement delta (colour/detail difference) between them.
4. For each frame in the scene:
   a. Compute dense optical flow from the current frame to the reference.
   b. Warp the delta field to the current frame's pixel grid.
   c. Compute a per-pixel confidence weight based on flow residual.
   d. Optionally blend with the previous frame's propagated delta for
      temporal smoothness.
   e. Apply the weighted delta to the original frame.
5. Write each processed frame to the output video stream.

Usage
-----
    python scripts/08_rebuild_video.py [--video VIDEO]
                                        [--scenes SCENES_CSV]
                                        [--restored-dir DIR]
                                        [--output OUTPUT]
                                        [--project-dir DIR]
                                        [--strength F]
                                        [--temporal-strength F]
                                        [--detail-strength F]

Tunable parameters
------------------
    --strength           0.72   Global enhancement intensity (0.0 – 1.0)
    --temporal-strength  0.68   Weight of previous-frame delta (temporal smoothing)
    --detail-strength    0.35   Amplification of high-frequency detail delta

Outputs
-------
    <output>.mp4   Silent reconstructed video (audio added by Stage 7)

Requirements
------------
    pip install opencv-python numpy pandas tqdm
"""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────────────────────
#  Configuration defaults
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class Scene:
    index: int
    start: int           # First frame (inclusive)
    end: int             # Last frame (exclusive)
    representative: int  # Frame number used as restoration anchor
    restored_path: Path  # Path to the restored representative frame JPEG


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(
        description="Reconstruct full video by propagating frame restorations with optical flow."
    )
    p.add_argument("--project-dir",      type=Path,  default=root)
    p.add_argument("--video",            type=Path,  default=Path("data/raw/Wedding_Compressed_AAC.mp4"))
    p.add_argument("--scenes",           type=Path,  default=Path("data/scenes.csv"))
    p.add_argument("--restored-dir",     type=Path,  default=Path("output/Restored_Frames"))
    p.add_argument("--output",           type=Path,  default=Path("output/Restored_Wedding_silent.mp4"))
    p.add_argument("--strength",         type=float, default=0.72,
                   help="Global enhancement intensity (default: 0.72).")
    p.add_argument("--temporal-strength",type=float, default=0.68,
                   help="Weight of previous-frame delta in temporal smoothing (default: 0.68).")
    p.add_argument("--detail-strength",  type=float, default=0.35,
                   help="High-frequency detail amplification factor (default: 0.35).")
    return p.parse_args()


def resolve(project_dir: Path, path: Path) -> Path:
    return path if path.is_absolute() else project_dir / path


# ─────────────────────────────────────────────────────────────────────────────
#  CSV parsing
# ─────────────────────────────────────────────────────────────────────────────

def _norm_col(name: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(name).strip().lower())


def _first_col(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    normalized = {_norm_col(c): c for c in df.columns}
    for cand in candidates:
        key = _norm_col(cand)
        if key in normalized:
            return normalized[key]
    return None


def _to_seconds(value: object) -> float | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    try:
        return float(text)
    except ValueError:
        pass
    parts = text.split(":")
    if len(parts) != 3:
        return None
    try:
        h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
        return h * 3600.0 + m * 60.0 + s
    except ValueError:
        return None


def _to_frame(value: object, fps: float) -> int | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)) and math.isfinite(float(value)):
        return int(round(float(value)))
    text = str(value).strip()
    num = pd.to_numeric(text, errors="coerce")
    if not pd.isna(num):
        return int(round(float(num)))
    s = _to_seconds(text)
    return None if s is None else int(round(s * fps))


def read_scenes_csv(path: Path, fps: float, frame_count: int) -> list[tuple[int, int, int]]:
    """
    Parse a PySceneDetect-format CSV and return a list of
    (scene_number, start_frame, end_frame_exclusive) tuples.
    """
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"No scenes in {path}")

    scene_col  = _first_col(df, ["Scene Number", "Scene", "Scene Index", "Index"])
    start_f    = _first_col(df, ["Start Frame", "StartFrame", "Start"])
    end_f      = _first_col(df, ["End Frame", "EndFrame", "End"])
    length_f   = _first_col(df, ["Length (frames)", "Length Frames", "Frame Count", "Frames"])
    start_t    = _first_col(df, ["Start Time (seconds)", "Start Time Seconds", "Start Timecode", "Start Time"])
    end_t      = _first_col(df, ["End Time (seconds)", "End Time Seconds", "End Timecode", "End Time"])

    raw: list[tuple[int, int, int]] = []
    for ri, row in df.iterrows():
        sn = int(ri) + 1
        if scene_col and not pd.isna(row[scene_col]):
            parsed = pd.to_numeric(row[scene_col], errors="coerce")
            if not pd.isna(parsed):
                sn = int(parsed)

        start = _to_frame(row[start_f], fps) if start_f else None
        if start is None and start_t:
            start = _to_frame(_to_seconds(row[start_t]), fps)

        end = None
        length = _to_frame(row[length_f], fps) if length_f else None
        if start is not None and length and length > 0:
            end = start + length
        elif end_f:
            parsed_end = _to_frame(row[end_f], fps)
            end = parsed_end + 1 if parsed_end is not None else None
        elif end_t:
            end = _to_frame(_to_seconds(row[end_t]), fps)

        if start is None:
            raise ValueError(f"Cannot determine scene start at CSV row {ri + 1}")
        if end is None:
            end = frame_count if ri == len(df) - 1 else -1

        raw.append((sn, max(0, start), end))

    starts = [s[1] for s in raw]
    completed: list[tuple[int, int, int]] = []
    for i, (sn, start, end) in enumerate(raw):
        if end < 0:
            end = starts[i + 1] if i + 1 < len(starts) else frame_count
        if frame_count > 0:
            start = min(start, frame_count)
            end = min(max(end, start + 1), frame_count)
        else:
            end = max(end, start + 1)
        completed.append((sn, start, end))

    completed.sort(key=lambda x: x[1])
    return completed


# ─────────────────────────────────────────────────────────────────────────────
#  Restored frame matching
# ─────────────────────────────────────────────────────────────────────────────

def list_restored(restored_dir: Path) -> list[Path]:
    if not restored_dir.exists():
        raise FileNotFoundError(f"Restored frames directory not found: {restored_dir}")
    images = sorted(
        (p for p in restored_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    )
    if not images:
        raise FileNotFoundError(f"No restored frames found in {restored_dir}")
    return images


def _nums(path: Path) -> list[int]:
    return [int(m) for m in re.findall(r"\d+", path.stem)]


def choose_restored(
    scene_number: int,
    start: int,
    end: int,
    restored: list[Path],
    position: int,
) -> tuple[Path, int]:
    mid = start + max(0, end - start - 1) // 2
    exact = [
        re.compile(rf"(?:^|[^a-z0-9])scene[^0-9]*0*{scene_number}(?:[^0-9]|$)", re.I),
        re.compile(rf"(?:^|[^a-z0-9])sc[^0-9]*0*{scene_number}(?:[^0-9]|$)", re.I),
    ]
    for img in restored:
        if any(pat.search(img.stem) for pat in exact):
            nums = _nums(img)
            rep = min(nums, key=lambda n: abs(n - mid)) if nums else mid
            return img, int(np.clip(rep, start, max(start, end - 1)))

    numbered = [(img, _nums(img)) for img in restored]
    candidates = []
    for order, (img, nums) in enumerate(numbered):
        if not nums:
            continue
        ns = min(nums, key=lambda n: abs(n - scene_number))
        nf = min(nums, key=lambda n: min(abs(n - start), abs(n - mid)))
        ss, sf = abs(ns - scene_number), min(abs(nf - start), abs(nf - mid))
        score = min(ss * 1000, sf)
        rep = nf if sf <= ss * 1000 else mid
        candidates.append((score, order, img, rep))

    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        _, _, img, rep = candidates[0]
        return img, int(np.clip(rep, start, max(start, end - 1)))

    if position < len(restored):
        return restored[position], mid
    return restored[-1], mid


def build_scene_plan(
    scenes_csv: Path,
    restored_dir: Path,
    fps: float,
    frame_count: int,
) -> list[Scene]:
    scene_rows = read_scenes_csv(scenes_csv, fps, frame_count)
    restored_images = list_restored(restored_dir)
    plan = []
    for pos, (sn, start, end) in enumerate(scene_rows):
        path, rep = choose_restored(sn, start, end, restored_images, pos)
        plan.append(Scene(index=sn, start=start, end=end, representative=rep, restored_path=path))
    return plan


# ─────────────────────────────────────────────────────────────────────────────
#  Optical flow & delta propagation
# ─────────────────────────────────────────────────────────────────────────────

def read_frame_at(cap: cv2.VideoCapture, idx: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"Cannot read frame {idx} from video")
    return frame


def resize_to(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    w, h = size
    if image.shape[1] == w and image.shape[0] == h:
        return image
    return cv2.resize(image, (w, h), interpolation=cv2.INTER_CUBIC)


def make_grid(w: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    return np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))


def warp(image: np.ndarray, flow: np.ndarray, grid: tuple) -> np.ndarray:
    gx, gy = grid
    mx = (gx + flow[..., 0]).astype(np.float32)
    my = (gy + flow[..., 1]).astype(np.float32)
    return cv2.remap(image, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def dense_flow(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    return cv2.calcOpticalFlowFarneback(
        src, dst, None,
        pyr_scale=0.5, levels=4, winsize=21,
        iterations=3, poly_n=7, poly_sigma=1.5, flags=0,
    )


def compute_delta(orig: np.ndarray, restored: np.ndarray, detail_strength: float) -> np.ndarray:
    raw = restored.astype(np.float32) - orig.astype(np.float32)
    low = cv2.GaussianBlur(raw, (0, 0), sigmaX=2.0, sigmaY=2.0)
    detail = raw - cv2.GaussianBlur(raw, (0, 0), sigmaX=6.0, sigmaY=6.0)
    return low + detail * float(detail_strength)


def confidence(cur_g: np.ndarray, ref_g: np.ndarray, flow: np.ndarray, grid: tuple) -> np.ndarray:
    warped_ref = warp(ref_g, flow, grid)
    diff = cv2.absdiff(cur_g, warped_ref).astype(np.float32)
    conf = np.exp(-diff / 42.0)
    conf = cv2.GaussianBlur(conf, (0, 0), sigmaX=1.2, sigmaY=1.2)
    return conf[..., None].astype(np.float32)


def apply_delta(frame: np.ndarray, delta: np.ndarray, conf: np.ndarray, strength: float) -> np.ndarray:
    adjusted = frame.astype(np.float32) + delta * conf * float(strength)
    return np.clip(adjusted, 0, 255).astype(np.uint8)


def open_writer(path: Path, fps: float, w: int, h: int) -> cv2.VideoWriter:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    if not writer.isOpened():
        raise RuntimeError(f"Cannot open output video for writing: {path}")
    return writer


# ─────────────────────────────────────────────────────────────────────────────
#  Scene reconstruction
# ─────────────────────────────────────────────────────────────────────────────

def reconstruct_scene(
    cap: cv2.VideoCapture,
    writer: cv2.VideoWriter,
    scene: Scene,
    size: tuple[int, int],
    grid: tuple,
    strength: float,
    temporal_strength: float,
    detail_strength: float,
    progress: tqdm,
) -> None:
    orig_ref = resize_to(read_frame_at(cap, scene.representative), size)
    restored_ref = cv2.imread(str(scene.restored_path), cv2.IMREAD_COLOR)
    if restored_ref is None:
        raise RuntimeError(f"Cannot read restored frame: {scene.restored_path}")
    restored_ref = resize_to(restored_ref, size)

    ref_delta = compute_delta(orig_ref, restored_ref, detail_strength)
    ref_gray = cv2.cvtColor(orig_ref, cv2.COLOR_BGR2GRAY)

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(scene.start))
    prev_gray: np.ndarray | None = None
    prev_delta: np.ndarray | None = None

    for fi in range(scene.start, scene.end):
        ok, frame = cap.read()
        if not ok or frame is None:
            raise RuntimeError(f"Cannot read frame {fi}")

        frame = resize_to(frame, size)
        cur_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if fi == scene.representative:
            direct_delta = ref_delta.copy()
            conf = np.ones((*cur_gray.shape, 1), dtype=np.float32)
        else:
            flow = dense_flow(cur_gray, ref_gray)
            direct_delta = warp(ref_delta, flow, grid)
            conf = confidence(cur_gray, ref_gray, flow, grid)

        if prev_gray is not None and prev_delta is not None:
            t_delta = warp(prev_delta, dense_flow(cur_gray, prev_gray), grid)
            propagated = t_delta * float(temporal_strength) + direct_delta * (1.0 - float(temporal_strength))
        else:
            propagated = direct_delta

        propagated = cv2.GaussianBlur(propagated, (0, 0), sigmaX=0.45, sigmaY=0.45)
        writer.write(apply_delta(frame, propagated, conf, strength))
        prev_gray, prev_delta = cur_gray, propagated
        progress.update(1)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    project_dir = args.project_dir.resolve()
    video_path   = resolve(project_dir, args.video)
    scenes_path  = resolve(project_dir, args.scenes)
    restored_dir = resolve(project_dir, args.restored_dir)
    output_path  = resolve(project_dir, args.output)

    for path in (video_path, scenes_path, restored_dir):
        if not path.exists():
            raise FileNotFoundError(f"Required input not found: {path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if not math.isfinite(fps) or fps <= 0:
        raise RuntimeError("Cannot determine source video FPS")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if w <= 0 or h <= 0:
        raise RuntimeError("Cannot determine source video dimensions")

    print(f"Video   : {video_path.name}  ({w}×{h} @ {fps:.3f} fps, {frame_count} frames)")
    print(f"Scenes  : {scenes_path.name}")
    print(f"Restored: {restored_dir}")
    print(f"Output  : {output_path}")

    plan = build_scene_plan(scenes_path, restored_dir, fps, frame_count)
    total = sum(max(0, s.end - s.start) for s in plan)
    writer = open_writer(output_path, fps, w, h)
    grid = make_grid(w, h)

    try:
        with tqdm(total=total, unit="frame", desc="Rebuilding") as pbar:
            for scene in plan:
                reconstruct_scene(
                    cap, writer, scene, (w, h), grid,
                    args.strength, args.temporal_strength, args.detail_strength, pbar,
                )
    finally:
        writer.release()
        cap.release()

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
