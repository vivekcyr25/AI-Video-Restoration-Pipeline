# Changelog

All notable changes to this project are documented here.

## [1.2.0] - 2026-07-12

### Added
- `utils/image_utils.py` — Image I/O (RGB), colour-space conversion (LAB/grayscale),
  histogram comparison (Bhattacharyya), blur estimation, and PSNR quality metric
- `utils/audio_utils.py` — FFmpeg-backed audio detection, extraction, segment
  cutting, and EBU R128 loudness analysis
- `utils/video_utils.py` — `validate_video_file`, `get_video_aspect_ratio`,
  `extract_frame_range`, and `get_codec_info` (structured ffprobe parsing)
- `utils/matcher_utils.py` — `batch_cosine_similarity` (chunked, memory-efficient),
  `embedding_stats` (diagnostic), `filter_low_confidence`, `save_match_results`
- `scripts/00_preflight_check.py` — Stage 0 environment validation script
- `scripts/10_quality_report.py` — Per-frame PSNR / sharpness / histogram report
- `tests/test_video_utils.py` — pytest suite for video utility functions
- `tests/test_matcher_utils.py` — pytest suite for matcher utility functions
- `tests/test_image_utils.py` — pytest suite for image utility functions
- `pytest.ini` — Project-level pytest configuration
- `.github/workflows/tests.yml` — CI workflow (Python 3.10/3.11/3.12)
- `docs/troubleshooting.md` — Common pipeline failure modes with diagnostics
- `docs/performance_guide.md` — Per-stage GPU/CPU tuning and profiling guide

### Changed
- `scripts/03_clip_embeddings.py` — Batch inference with `--batch-size` flag;
  automatic FP16 on CUDA devices; `np.concatenate` for correctness
- `utils/__init__.py` — Full package docstring with submodule descriptions and `__all__`



### Added
- Documentation batch: preview guides, credits, changelog

## [Unreleased]

### Added
- Interactive algorithm preview site (React + Tailwind + WebGL shaders)
- GitHub Pages deployment workflow
- Background ambient music at 30% volume with mute toggle
- Scroll-driven intro narrative and pipeline walkthrough

### Changed
- Preview copy uses generic asset terminology
- Improved intro beat visibility and section overlap fixes

### Documentation
- Added CHANGELOG, CREDITS, and preview development guide
- Linked live demo from README

### Credits
- Preview engineered by Vivek Sharma
- Background music: Galaxy's Endless Expanse — FesliyanStudios.com


