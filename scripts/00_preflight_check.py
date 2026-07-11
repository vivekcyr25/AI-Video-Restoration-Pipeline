#!/usr/bin/env python3
"""
Stage 0 — Pre-flight Environment Check
=======================================
Validates that all required tools, Python packages, and input directories
are present before running the restoration pipeline.

Run this script first to diagnose environment issues without starting any
expensive computation.

Usage
-----
    python scripts/00_preflight_check.py [--video VIDEO_PATH]
                                          [--albums ALBUMS_DIR]
                                          [--frames FRAMES_DIR]

Exit codes
----------
    0 — All checks passed (safe to proceed)
    1 — One or more critical checks failed
"""

from __future__ import annotations

import argparse
import importlib
import shutil
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
#  Check definitions
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_BINARIES = [
    ("ffmpeg",  "https://ffmpeg.org/download.html"),
    ("ffprobe", "https://ffmpeg.org/download.html"),
]

REQUIRED_PYTHON_PACKAGES = [
    ("cv2",        "opencv-python"),
    ("numpy",      "numpy"),
    ("tqdm",       "tqdm"),
    ("PIL",        "Pillow"),
    ("torch",      "torch"),
    ("open_clip",  "open-clip-torch"),
    ("insightface","insightface"),
    ("pandas",     "pandas"),
]

OPTIONAL_PYTHON_PACKAGES = [
    ("pytest",     "pytest"),
    ("line_profiler", "line_profiler"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Colours (ANSI, disabled on Windows if no ANSI support)
# ─────────────────────────────────────────────────────────────────────────────

def _supports_ansi() -> bool:
    import os
    return os.name != "nt" or "ANSICON" in os.environ or "WT_SESSION" in os.environ

_ANSI = _supports_ansi()
OK    = "\033[32m✔\033[0m" if _ANSI else "[OK]"
WARN  = "\033[33m⚠\033[0m" if _ANSI else "[WARN]"
FAIL  = "\033[31m✘\033[0m" if _ANSI else "[FAIL]"
SKIP  = "·"


# ─────────────────────────────────────────────────────────────────────────────
#  Individual checks
# ─────────────────────────────────────────────────────────────────────────────

def check_binary(name: str) -> bool:
    found = shutil.which(name) is not None
    symbol = OK if found else FAIL
    note = shutil.which(name) or "NOT FOUND"
    print(f"  {symbol}  {name:<12} {note}")
    return found


def check_python_package(import_name: str, pip_name: str, optional: bool = False) -> bool:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "?")
        print(f"  {OK}  {pip_name:<25} v{version}")
        return True
    except ImportError:
        symbol = WARN if optional else FAIL
        print(f"  {symbol}  {pip_name:<25} NOT INSTALLED  →  pip install {pip_name}")
        return optional  # optional failures don't count as errors


def check_cuda() -> None:
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory // (1024 ** 2)
            print(f"  {OK}  CUDA            {name} ({vram} MB VRAM)")
        else:
            print(f"  {WARN}  CUDA            Not available — CPU-only mode")
    except ImportError:
        print(f"  {SKIP}  CUDA            (torch not installed)")


def check_directory(label: str, path: Path, required: bool = True) -> bool:
    if path.exists() and path.is_dir():
        n_files = sum(1 for f in path.iterdir() if f.is_file())
        print(f"  {OK}  {label:<25} {path}  ({n_files} files)")
        return True
    symbol = FAIL if required else WARN
    print(f"  {symbol}  {label:<25} NOT FOUND: {path}")
    return not required


def check_video_file(label: str, path: Path | None) -> bool:
    if path is None:
        print(f"  {SKIP}  {label:<25} (not specified)")
        return True
    if not path.exists():
        print(f"  {FAIL}  {label:<25} NOT FOUND: {path}")
        return False
    size_mb = path.stat().st_size / (1024 ** 2)
    print(f"  {OK}  {label:<25} {path}  ({size_mb:.1f} MB)")
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pre-flight environment check for the AI Video Restoration pipeline."
    )
    parser.add_argument("--video", type=Path, default=None,
                        help="Path to the input video file to validate.")
    parser.add_argument(
        "--albums",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Albums",
    )
    parser.add_argument(
        "--frames",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Representative_Frames",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = 0

    print("\n" + "=" * 62)
    print("  AI VIDEO RESTORATION — PRE-FLIGHT CHECK")
    print("=" * 62)

    # ── System binaries ──────────────────────────────────────────────────────
    print("\n[1/4] System Binaries")
    for name, url in REQUIRED_BINARIES:
        if not check_binary(name):
            failures += 1

    # ── Python packages ──────────────────────────────────────────────────────
    print("\n[2/4] Python Packages (required)")
    for import_name, pip_name in REQUIRED_PYTHON_PACKAGES:
        if not check_python_package(import_name, pip_name, optional=False):
            failures += 1

    print("\n[2/4] Python Packages (optional)")
    for import_name, pip_name in OPTIONAL_PYTHON_PACKAGES:
        check_python_package(import_name, pip_name, optional=True)

    # ── CUDA ─────────────────────────────────────────────────────────────────
    print("\n[3/4] GPU / CUDA")
    check_cuda()

    # ── Directories and files ─────────────────────────────────────────────────
    print("\n[4/4] Input Paths")
    if not check_video_file("Input video", args.video):
        failures += 1
    if not check_directory("Albums dir", args.albums, required=False):
        pass  # warning only
    if not check_directory("Frames dir", args.frames, required=False):
        pass  # warning only

    # ── Result ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 62)
    if failures == 0:
        print(f"  {OK}  All critical checks passed.  Pipeline is ready.")
    else:
        print(f"  {FAIL}  {failures} critical check(s) failed. Fix issues above first.")
    print("=" * 62 + "\n")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
