# 🎬 State-of-the-Art reference-Guided AI Video Restoration Pipeline

> A research-grade, scene-aware, and identity-preserving AI pipeline designed to restore compressed, degraded legacy video footage using high-quality still photographs as reference anchors.

This repository contains the complete codebase, configuration files, and wrapper scripts for executing the restoration pipeline.

---

## 🏗️ Architecture & Core Components

The pipeline is structured into sequential stages, coordinated through a central configuration system and optimized to run efficiently on consumer-grade GPUs:

1. **Stage 1 — Video Repair & CFR Conversion**: Re-encodes and repairs containers, then detects scenes using `PySceneDetect`.
2. **Stage 2 — Representative Frame Extraction**: Extracts midpoint keyframes of detected scenes via fast `FFmpeg` seeking.
3. **Stage 3 — Batch CLIP Embeddings**: Generates 512-dimensional semantic embeddings for album photos and frames using OpenCLIP.
4. **Stage 4 — Face Detection & ArcFace Embeddings**: Detects faces using `InsightFace` (ORT CUDA ArcFace) and generates face cache.
5. **Stage 5 — Hybrid Matcher**: Merges CLIP, ArcFace, scene context, color histogram, and VGG perceptual similarities.
6. **Stage 6 — Reference-Guided Face Restoration**: Warps face landmarks and transfers high-frequency texture details from matching album photos onto frames.
7. **Stage 7 — Video Detail Propagation**: Warp and propagate keyframe deltas smoothly using `torchvision` RAFT-small optical flow.
8. **Stage 8 — Lossless Audio Muxing**: Muxes original AAC streams back into restored footage.

---

## 🚀 Performance Optimizations & Bug Fixes

We recently upgraded the codebase with major performance optimizations and quality bug fixes:

### 1. ⚡ Speed & Throughput Optimizations (reducing execution from 18 to 2-3 hours)
* **Batched Optical Flow (Stage 7)**: Flow calculation now groups target frames into chunks of **16** and runs them in a single GPU pass, leading to a **3x–4x GPU speedup**.
* **Rollback Trigger**: If propagation confidence drops below `0.55` (due to occlusion or extreme motion), the pipeline rollbacks/discards remaining precomputed batch items, triggers keyframe restoration on-the-fly, updates the local anchor, and resumes batching.
* **Grid Coordinate Cache**: Caches the coordinate grids dynamically based on tensor shape in `warp_flow`, eliminating redundant `torch.meshgrid` and matching memory allocations.
* **Model FLOPS Reduction**: Reduced default RAFT updates from 12 to 8 iterations, saving **33% model time** with sub-pixel flow quality difference.
* **Redundant Disk I/O & Inferences Caching (Stage 5)**: Precomputes album VGG features and histograms once at start, reducing disk reads from 11,000 to 600 operations and model forward passes from 5,500 to 600.
* **Album image cache (Stage 6)**: Implemented in-memory caching for loaded reference photos during face warping, eliminating redundant disk reads.
* **Torch Global Performance Flags**: Enabled global CUDA auto-tuning (`torch.backends.cudnn.benchmark`) and TensorFloat-32 (`allow_tf32`) operations.

### 2. 🎨 Quality Restoration Bug Fixes (Resolving "Oily Ghost Painting" Artifacts)
* **Real-ESRGAN Channel Order Fix**: Real-ESRGAN was previously receiving raw BGR arrays instead of RGB. This inverted the Red and Blue channels during inference, resulting in texture distortions. We added BGR-to-RGB conversion on input, and RGB-to-BGR conversion on output.
* **Face Skin Blending Channel Alignment**: Fixed color space mismatches in Reinhard `color_transfer` (which expects RGB inputs but was passed BGR, returning RGB). We now convert inputs to RGB before calling color transfer, and convert the output back to BGR prior to guided filtering and final alpha mask blending. This resolves ghostly bluish skin tones and blurry face masks.

---

## 📁 Repository Layout

```
├── README.md                        # Root documentation
├── scripts/
│   ├── 00_preflight_check.py        # Pipeline environment check script
│   ├── 01_extract_scenes.sh         # Scene boundary extraction shell wrapper
│   ├── 02_extract_frames.sh         # Frame extraction shell wrapper
│   └── 09_merge_audio.sh            # Audio muxing shell wrapper
└── FFMEPGXpyRES_@6/
    └── bin/
        └── Wedding_AI_Project/      # Subproject containing core pipeline code
            ├── configs/
            │   └── pipeline_config.yaml  # Config settings (device, batch_size, etc.)
            ├── pipeline/
            │   ├── video_repair.py
            │   ├── frame_extractor.py
            │   ├── clip_embedder.py
            │   ├── face_embedder.py
            │   ├── reference_selector.py
            │   ├── main_restoration.py
            │   └── video_propagation.py
            ├── scripts/
            │   └── run_pipeline.py  # Unified pipeline manager
            └── tests/
                └── test_pipeline_redesign.py
```

---

## 💻 Installation & Execution

### 1. Virtual Environment Setup
Ensure you have Python 3.10+ and FFmpeg 6.0+ installed.

```bash
# Navigate to the subproject folder
cd FFMEPGXpyRES_@6/bin/Wedding_AI_Project

# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Pipeline Stages
You can execute stages using the unified pipeline manager:

```bash
# Run all stages
python scripts/run_pipeline.py --stage all

# Run specific stage (e.g., scene detection)
python scripts/run_pipeline.py --stage 1
```

### 3. Run Verification Tests
Verify all configurations and restoration mathematical helpers:
```bash
pytest tests/
```
