# 🎬 State-of-the-Art reference-Guided AI Video Restoration Pipeline

> A research-grade, scene-aware, and identity-preserving AI pipeline designed to restore compressed, degraded legacy video footage using high-quality still photographs as reference anchors. 

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-6.x%2F8.x-green?logo=ffmpeg)](https://ffmpeg.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red?logo=pytorch)](https://pytorch.org/)
[![InsightFace](https://img.shields.io/badge/InsightFace-buffalo__l-orange)](https://github.com/deepinsight/insightface)
[![OpenCLIP](https://img.shields.io/badge/OpenCLIP-ViT--B--32-purple)](https://github.com/mlfoundations/open_clip)

---

## 🏗️ Redesigned Pipeline Architecture

This pipeline is structured into 8 sequential stages, coordinated through a central configuration system and optimized to execute on consumer-grade GPUs (such as the **RTX 3050 4GB VRAM**) without Out-Of-Memory (OOM) failures.

```
Input Video & Album
    │
    ├─ Stage 1 ── Video Repair & CFR Conversion (FFmpeg & PySceneDetect)
    │               Output: repaired_video.mp4, cfr_video.mp4, scenes.csv
    │
    ├─ Stage 2 ── Representative Frame Extraction (FFmpeg seeking)
    │               Output: Representative_Frames/scene_XXXX.jpg
    │
    ├─ Stage 3 ── Batch CLIP Embeddings (OpenCLIP ViT-B-32 FP16)
    │               Output: models/album_embeddings.npy, models/frames_embeddings.npy
    │
    ├─ Stage 4 ── InsightFace & Face Cache (ORT CUDA ArcFace & face_cache.json)
    │               Output: models/face_cache.json, models/*_face_embeddings.npy
    │
    ├─ Stage 5 ── Hybrid Coarse-to-Fine Matcher (Face + CLIP + Scene + Color + VGG-LPIPS)
    │               Output: output/advanced_matches.csv
    │
    ├─ Stage 6 ── Reference-Guided Face Restoration & Real-ESRGAN BG
    │               Output: output/Restored_Frames/scene_XXXX.jpg, output/restore_log.csv
    │
    ├─ Stage 7 ── Video Detail Propagation (torchvision RAFT-small FP16)
    │               Output: output/Restored_Wedding_silent.mp4
    │
    └─ Stage 8 ── Lossless Audio Muxing (FFmpeg Stream-Copy)
                    Output: output/Restored_Wedding_final.mp4
```

---

## 💡 Key Design Decisions & Optimizations

* **Identity Preservation (No Face Hallucination)**: Standard face restoration models (like GFPGAN or CodeFormer) often hallucinate facial details, altering the subject's identity. This pipeline warps the *actual* album photo face using a **5-point affine alignment** (based on InsightFace landmarks), extracts real high-frequency facial textures (pores, hair, eye reflections), and blends them into target frames using soft segment masks (eyes, lips, skin, hair, jewellery).
* **Modern Optical Flow Propagation**: Replaced the classical Farnebäck flow with **RAFT-small** (Recurrent All-Pairs Field Transforms). RAFT maps sub-pixel motion details and occlusion masks, allowing the restored keyframe deltas to propagate smoothly across video shots without temporal blurring.
* **Low-VRAM Sequential Lifecycles**: Each stage loads its required deep neural networks on-demand, executes in `FP16` half-precision under `torch.inference_mode()`, and completely deletes models followed by `torch.cuda.empty_cache()` before the next stage initializes.
* **Incremental Face Cache**: Bounding boxes, landmarks, and ArcFace embeddings are cached in a central `models/face_cache.json` file. If a run is interrupted, the pipeline skips face detection for cached files, saving massive amounts of compute time.

---

## 📁 Repository Layout

```
├── configs/
│   └── pipeline_config.yaml         # Centralized stage parameters & paths
├── pipeline/
│   ├── __init__.py
│   ├── video_repair.py              # Container repair, CFR transcode, PySceneDetect
│   ├── frame_extractor.py           # representative frame extract
│   ├── clip_embedder.py             # Batch CLIP embedder (DataLoaders + Pinned memory)
│   ├── face_embedder.py             # InsightFace CUDA generator & persistent cache
│   ├── hybrid_matcher.py            # Coarse-to-fine multi-similarity matcher
│   ├── main_restoration.py          # Reference-guided face blend + Real-ESRGAN BG
│   └── video_propagation.py         # RAFT dense optical flow propagator & Lab de-flicker
├── scripts/
│   ├── run_pipeline.py              # Unified pipeline manager CLI
│   ├── 01_extract_scenes.py         # Stage 1 command wrapper
│   ├── 02_extract_frames.py         # Stage 2 command wrapper
│   ├── 03_clip_embeddings.py        # Stage 3 command wrapper
│   ├── 04_face_embeddings.py        # Stage 4 command wrapper
│   ├── 05_advanced_matcher.py       # Stage 5 command wrapper
│   ├── 06_restore_frame.py          # Stage 6 wrapper (v1)
│   ├── 07_restore_frame_v2.py       # Stage 6 wrapper (v2)
│   ├── 08_rebuild_video.py          # Stage 7 command wrapper
│   └── 09_merge_audio.py            # Stage 8 command wrapper
├── utils/
│   ├── image_enhancement.py         # Reinhard color transfer, guided filter, CLAHE, unsharp
│   ├── temporal_utils.py            # Global rolling Lab de-flicker, temporal EMA
│   └── video_utils.py               # OpenCV metadata, FFmpeg seek wrappers
├── tests/
│   └── test_pipeline_redesign.py    # Unit tests for image/temporal utils
└── requirements.txt                 # Python dependencies
```

---

## 🚀 Installation & Execution

### 1. Prerequisites
Ensure you have `FFmpeg >= 6.0` on your system path.
```bash
ffmpeg -version
```

### 2. Virtual Environment Setup
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

### 3. Execution

#### The Easiest Way: Run the Unified Pipeline
To execute the complete pipeline from repair to audio merge sequentially:
```bash
python scripts/run_pipeline.py --stage all
```

#### Resume From Interruption
If the pipeline is interrupted, re-run without the `--force` flag. It will read cache files, skip completed frames/embeddings, and resume from the exact block where it stopped:
```bash
python scripts/run_pipeline.py --stage all
```

#### Running Specific Stages
You can execute individual stages or override parameters:
```bash
# Run scene detection only
python scripts/run_pipeline.py --stage 1

# Re-run matching, forcing overwrite
python scripts/run_pipeline.py --stage 5 --force
```

#### Backward Compatibility Runners
You can also invoke the original numbered scripts directly:
```bash
python scripts/03_clip_embeddings.py --batch-size 32
python scripts/05_advanced_matcher.py --top-k 5
```

---

## 🧪 Testing & Verification

Run the test suite using `pytest` to verify image and temporal enhancement functions:
```bash
pytest tests/
```
