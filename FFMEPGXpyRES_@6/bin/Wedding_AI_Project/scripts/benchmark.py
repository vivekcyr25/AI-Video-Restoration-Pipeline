"""
scripts/benchmark.py
====================
Reproducible baseline benchmarking script for AI Video Restoration Pipeline.
Measures wall-clock time, GPU VRAM allocation, disk consumption, and captures
the Stage 5 regression reference (top-5 matches per frame) across all eight stages.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Ensure local FFmpeg/ffprobe binaries are on PATH if they exist
_local_bin = Path(__file__).resolve().parent.parent.parent
if _local_bin.exists() and str(_local_bin) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = str(_local_bin) + os.pathsep + os.environ.get("PATH", "")

# Insert project root to path for absolute imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [benchmark] %(message)s"
)
logger = logging.getLogger("benchmark")


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def compute_dir_sha256(dir_path: Path) -> str:
    """Compute deterministic composite SHA-256 hash of all files in a directory."""
    if not dir_path.is_dir():
        return ""
    h = hashlib.sha256()
    for p in sorted(dir_path.glob("*")):
        if p.is_file():
            h.update(p.name.encode("utf-8"))
            h.update(compute_file_sha256(p).encode("utf-8"))
    return h.hexdigest()


def get_dir_size_bytes(path: Path) -> int:
    """Recursively calculate total byte size of a directory or single file."""
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            p = Path(root) / f
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def get_hardware_info() -> Dict[str, Any]:
    """Collect host hardware and system software metadata."""
    info: Dict[str, Any] = {
        "os": platform.platform(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "hostname": platform.node(),
    }
    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["cuda_version"] = torch.version.cuda
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["total_vram_bytes"] = torch.cuda.get_device_properties(0).total_memory
            info["total_vram_mb"] = round(info["total_vram_bytes"] / (1024 * 1024), 2)
        else:
            info["cuda_version"] = None
            info["gpu_name"] = "CUDA Unavailable"
    except ImportError:
        info["torch_version"] = "Not Installed"
        info["cuda_available"] = False
    return info


class MemoryTracker:
    """Tracks CUDA memory before, during, and after an execution stage."""

    def __init__(self, device: str = "cuda"):
        self.device = device
        self.cuda_available = False
        try:
            import torch
            self.torch = torch
            self.cuda_available = torch.cuda.is_available() and device.startswith("cuda")
        except ImportError:
            self.torch = None

    def start(self) -> Dict[str, Any]:
        if not self.cuda_available:
            return {"status": "unavailable"}
        self.torch.cuda.synchronize()
        self.torch.cuda.reset_peak_memory_stats()
        init_allocated = self.torch.cuda.memory_allocated()
        return {
            "status": "active",
            "initial_allocated_bytes": init_allocated,
            "initial_allocated_mb": round(init_allocated / (1024 * 1024), 3),
        }

    def stop(self, start_info: Dict[str, Any]) -> Dict[str, Any]:
        if not self.cuda_available or start_info.get("status") != "active":
            return {
                "initial_allocated_mb": "unavailable",
                "peak_allocated_mb": "unavailable",
                "incremental_peak_mb": "unavailable",
            }
        self.torch.cuda.synchronize()
        peak_allocated = self.torch.cuda.max_memory_allocated()
        init_allocated = start_info["initial_allocated_bytes"]
        incremental = max(0, peak_allocated - init_allocated)
        return {
            "initial_allocated_mb": round(init_allocated / (1024 * 1024), 3),
            "peak_allocated_mb": round(peak_allocated / (1024 * 1024), 3),
            "incremental_peak_mb": round(incremental / (1024 * 1024), 3),
        }


def mux_audio(original_video: Path, silent_video: Path, final_video: Path) -> bool:
    """Losslessly stream-copy audio track into restored video."""
    logger.info(f"Muxing audio from {original_video} into {silent_video} -> {final_video}")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(original_video),
        "-map", "0:v",
        "-map", "1:a?",
        "-c:v", "copy",
        "-c:a", "copy",
        "-shortest",
        str(final_video)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"FFmpeg audio muxing failed:\n{res.stderr}")
        return False
    return True


def run_benchmark(
    config_path: Path,
    video_override: Optional[Path] = None,
    album_override: Optional[Path] = None,
    output_reports_dir: Optional[Path] = None,
    force: bool = True
) -> Dict[str, Any]:
    """Execute complete reproducible pipeline benchmark and produce reports."""
    from pipeline import (
        VideoRepairStage,
        FrameExtractorStage,
        CLIPEmbedderStage,
        FaceEmbedderStage,
        ReferenceSelectorStage,
        ReferenceRestorer,
        VideoPropagationStage,
    )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Apply benchmark config overrides if specified
    b_cfg = config.get("benchmark", {})
    if video_override:
        config["global"]["video_path"] = str(video_override)
    elif b_cfg.get("test_video"):
        config["global"]["video_path"] = str(b_cfg["test_video"])

    if album_override:
        config["global"]["albums_dir"] = str(album_override)
    elif b_cfg.get("test_album"):
        config["global"]["albums_dir"] = str(b_cfg["test_album"])

    video_path = Path(config["global"]["video_path"])
    albums_dir = Path(config["global"]["albums_dir"])
    device = config["global"].get("device", "cuda")

    if not video_path.exists():
        raise FileNotFoundError(f"Test video not found: {video_path}")
    if not albums_dir.exists():
        raise FileNotFoundError(f"Test albums directory not found: {albums_dir}")

    reports_dir = output_reports_dir or (_project_root / "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    baseline_frames_dir = reports_dir / "baseline_frames"
    baseline_frames_dir.mkdir(parents=True, exist_ok=True)

    hardware = get_hardware_info()
    logger.info(f"Hardware: {hardware['gpu_name']} | PyTorch: {hardware.get('torch_version')} | CUDA: {hardware.get('cuda_version')}")

    # Compute input media hashes for reproducibility
    dataset_info = {
        "video_path": str(video_path),
        "video_size_bytes": video_path.stat().st_size,
        "video_sha256": compute_file_sha256(video_path),
        "albums_dir": str(albums_dir),
        "albums_count": len([p for p in albums_dir.glob("*") if p.is_file()]),
        "albums_composite_sha256": compute_dir_sha256(albums_dir),
    }

    mem_tracker = MemoryTracker(device=device)
    stage_results: Dict[str, Any] = {}
    total_start = time.perf_counter()

    # ─────────────────────────────────────────────────────────────
    # Stage 1: Video Repair & CFR Conversion
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 1: Video Repair ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage1 = VideoRepairStage(config)
    stage1.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage1_time = t1 - t0
    stage1_disk = get_dir_size_bytes(Path(config["video_repair"]["repaired_video_path"])) + \
                  get_dir_size_bytes(Path(config["video_repair"]["scene_csv_path"]))
    stage_results["stage_1"] = {
        "name": "Video Repair & CFR Transcode",
        "wall_time_sec": round(stage1_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage1_disk,
        "output_disk_mb": round(stage1_disk / (1024 * 1024), 3),
    }

    # ─────────────────────────────────────────────────────────────
    # Stage 2: Representative Frame Extraction
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 2: Frame Extraction ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage2 = FrameExtractorStage(config)
    stage2.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage2_time = t1 - t0
    stage2_disk = get_dir_size_bytes(Path(config["frame_extractor"]["output_dir"]))
    stage_results["stage_2"] = {
        "name": "Representative Frame Extraction",
        "wall_time_sec": round(stage2_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage2_disk,
        "output_disk_mb": round(stage2_disk / (1024 * 1024), 3),
    }

    # ─────────────────────────────────────────────────────────────
    # Stage 3: CLIP Embeddings
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 3: CLIP Embeddings ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage3 = CLIPEmbedderStage(config)
    stage3.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage3_time = t1 - t0
    m_dir = Path(config["global"]["models_dir"])
    stage3_disk = get_dir_size_bytes(m_dir / "album_embeddings.npy") + \
                  get_dir_size_bytes(m_dir / "frames_embeddings.npy")
    stage_results["stage_3"] = {
        "name": "Batch CLIP Semantic Embeddings",
        "wall_time_sec": round(stage3_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage3_disk,
        "output_disk_mb": round(stage3_disk / (1024 * 1024), 3),
    }

    # ─────────────────────────────────────────────────────────────
    # Stage 4: InsightFace Face Embeddings
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 4: Face Embeddings ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage4 = FaceEmbedderStage(config)
    stage4.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage4_time = t1 - t0
    stage4_disk = get_dir_size_bytes(Path(config["face_embeddings"]["face_cache_path"])) + \
                  get_dir_size_bytes(m_dir / "album_face_embeddings.npy") + \
                  get_dir_size_bytes(m_dir / "frame_face_embeddings.npy")
    stage_results["stage_4"] = {
        "name": "InsightFace Identity Detection & Cache",
        "wall_time_sec": round(stage4_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage4_disk,
        "output_disk_mb": round(stage4_disk / (1024 * 1024), 3),
    }

    # ─────────────────────────────────────────────────────────────
    # Stage 5: Hybrid Reference Matching
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 5: Reference Selection ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage5 = ReferenceSelectorStage(config)
    stage5.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage5_time = t1 - t0
    stage5_csv = Path(config["global"]["output_dir"]) / "advanced_matches.csv"
    stage5_disk = get_dir_size_bytes(stage5_csv)
    stage_results["stage_5"] = {
        "name": "Hybrid Coarse-to-Fine Matcher",
        "wall_time_sec": round(stage5_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage5_disk,
        "output_disk_mb": round(stage5_disk / (1024 * 1024), 3),
    }

    # Save Stage 5 Top-5 regression reference
    stage5_top5_data = {
        "metadata": {
            "top_k": int(config["hybrid_matching"]["top_k"]),
            "weights": config["hybrid_matching"]["weights"],
            "lpips_backbone": config["hybrid_matching"]["lpips_backbone"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "frames": {},
    }
    if stage5_csv.exists():
        with open(stage5_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                f_name = row["Frame"]
                if f_name not in stage5_top5_data["frames"]:
                    stage5_top5_data["frames"][f_name] = []
                stage5_top5_data["frames"][f_name].append({
                    "rank": int(row["Rank"]),
                    "album_image": row["AlbumImage"],
                    "clip_score": float(row["CLIPScore"]),
                    "face_score": float(row["FaceScore"]),
                    "scene_score": float(row["SceneScore"]),
                    "color_score": float(row["ColorScore"]),
                    "lpips_score": float(row["LPIPSScore"]),
                    "final_score": float(row["FinalScore"]),
                })

    top5_json_path = reports_dir / "baseline_stage5_top5.json"
    with open(top5_json_path, "w", encoding="utf-8") as f:
        json.dump(stage5_top5_data, f, indent=2)
    logger.info(f"Saved Stage 5 Top-5 regression reference to: {top5_json_path}")

    # ─────────────────────────────────────────────────────────────
    # Stage 6: Reference-guided Restoration
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 6: Restoration ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage6 = ReferenceRestorer(config)
    stage6.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage6_time = t1 - t0
    restored_frames_dir = Path(config["restoration"]["output_dir"])
    stage6_disk = get_dir_size_bytes(restored_frames_dir)
    stage_results["stage_6"] = {
        "name": "Reference-Guided Face & Frame Restoration",
        "wall_time_sec": round(stage6_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage6_disk,
        "output_disk_mb": round(stage6_disk / (1024 * 1024), 3),
    }

    # Preserve three representative restored frames for baseline visual comparison
    restored_files = sorted(restored_frames_dir.glob("*.jpg"))
    preserved_frames: List[str] = []
    if restored_files:
        indices = [0, len(restored_files) // 2, len(restored_files) - 1]
        for idx in indices:
            src = restored_files[idx]
            dst = baseline_frames_dir / src.name
            shutil.copy2(src, dst)
            preserved_frames.append(src.name)
            logger.info(f"Preserved baseline reference frame: {dst}")

    # ─────────────────────────────────────────────────────────────
    # Stage 7: Video Detail Propagation (RAFT)
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 7: Optical Flow Propagation ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    stage7 = VideoPropagationStage(config)
    stage7.run(force=force)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    stage7_time = t1 - t0
    silent_video_path = Path(config["video_propagation"]["output_silent"])
    stage7_disk = get_dir_size_bytes(silent_video_path)
    stage_results["stage_7"] = {
        "name": "Batched RAFT Optical Flow Detail Propagation",
        "wall_time_sec": round(stage7_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage7_disk,
        "output_disk_mb": round(stage7_disk / (1024 * 1024), 3),
    }

    # ─────────────────────────────────────────────────────────────
    # Stage 8: Lossless Audio Muxing
    # ─────────────────────────────────────────────────────────────
    logger.info("--- Benchmarking Stage 8: Lossless Audio Muxing ---")
    st_mem = mem_tracker.start()
    t0 = time.perf_counter()
    final_video_path = Path(config["video_propagation"]["output_final"])
    success = mux_audio(video_path, silent_video_path, final_video_path)
    t1 = time.perf_counter()
    end_mem = mem_tracker.stop(st_mem)
    if not success:
        raise RuntimeError("Stage 8 Audio muxing failed.")
    stage8_time = t1 - t0
    stage8_disk = get_dir_size_bytes(final_video_path)
    stage_results["stage_8"] = {
        "name": "Lossless Audio Stream Multiplexing",
        "wall_time_sec": round(stage8_time, 3),
        "vram": end_mem,
        "output_disk_bytes": stage8_disk,
        "output_disk_mb": round(stage8_disk / (1024 * 1024), 3),
    }

    total_time = time.perf_counter() - total_start

    # Summary of disk breakdown
    total_disk_bytes = sum(s["output_disk_bytes"] for s in stage_results.values())

    baseline_data = {
        "benchmark_version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardware": hardware,
        "dataset": dataset_info,
        "pipeline_config": config,
        "stage_timings": stage_results,
        "total_execution_time_sec": round(total_time, 3),
        "total_disk_consumption_bytes": total_disk_bytes,
        "total_disk_consumption_mb": round(total_disk_bytes / (1024 * 1024), 3),
        "preserved_baseline_frames": preserved_frames,
        "stage5_reference_file": str(top5_json_path.relative_to(_project_root)),
    }

    baseline_json_path = reports_dir / "baseline.json"
    with open(baseline_json_path, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=2)
    logger.info(f"Saved complete baseline benchmark report to: {baseline_json_path}")

    return baseline_data


def main() -> None:
    p = argparse.ArgumentParser(description="AI Video Restoration Baseline Benchmark Runner")
    p.add_argument(
        "--config",
        type=Path,
        default=_project_root / "configs" / "pipeline_config.yaml",
        help="Path to pipeline configuration YAML file."
    )
    p.add_argument(
        "--video",
        type=Path,
        default=None,
        help="Optional override path to test video file."
    )
    p.add_argument(
        "--album",
        type=Path,
        default=None,
        help="Optional override path to test album directory."
    )
    p.add_argument(
        "--reports-dir",
        type=Path,
        default=_project_root / "reports",
        help="Path to directory where benchmark reports will be written."
    )
    p.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Force execution across all stages ignoring cached checkpoints."
    )
    args = p.parse_args()

    run_benchmark(
        config_path=args.config,
        video_override=args.video,
        album_override=args.album,
        output_reports_dir=args.reports_dir,
        force=args.force
    )


if __name__ == "__main__":
    main()

