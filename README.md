# 🎬 AI Video Restoration Pipeline

> A scene-aware, AI-driven pipeline that restores a degraded legacy wedding
> video using CLIP visual embeddings, InsightFace identity matching, optical
> flow propagation, and FFmpeg video reconstruction.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-8.x-green?logo=ffmpeg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenCLIP](https://img.shields.io/badge/OpenCLIP-ViT--B--32-purple)](https://github.com/mlfoundations/open_clip)
[![InsightFace](https://img.shields.io/badge/InsightFace-buffalo__l-orange)](https://github.com/deepinsight/insightface)

---

## 📖 Project Overview

This repository contains the complete research engineering toolkit used to
restore a compressed, degraded wedding video recorded on legacy hardware.
The video suffered from compression artefacts, loss of fine detail, and
reduced colour fidelity. The project applies a multi-stage AI pipeline to
recover perceptual quality without access to the original raw footage.

The pipeline matches video scenes to a curated album of high-quality
reference photographs using semantic and identity embeddings, then
propagates the enhancement from representative keyframes across every
frame in each scene using dense optical flow.

> **Note:** This is a polished portfolio archive of a real completed
> experiment. The pipeline is fully functional but not structured as an
> installable package.

---

## 💡 Motivation

Old videos are irreplaceable. When the original recording is compressed
with aggressive codecs — losing sharpness, colour depth, and fine detail —
re-shooting is not an option. This project answers the question:

> *Can AI recover visual quality in a degraded video by leveraging
> high-quality still photos taken at the same event?*

The key insight: Studio photographers capture the same moments at full
quality. If we can match video frames to album photos with high accuracy
(especially for the same people and scenes), we can use those photos as
enhancement references for the corresponding video frames.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Scene-aware processing** | PySceneDetect divides the video into shots; only one representative frame per scene is AI-processed |
| 🤖 **Dual embedding matching** | Combines CLIP semantic similarity (30%) and InsightFace face identity (70%) for accurate frame–album pairing |
| 👤 **Face-guided alignment** | InsightFace detects and aligns faces using an affine transform for sub-pixel face-region accuracy |
| 🌊 **Optical flow propagation** | Farnebäck dense flow propagates restoration deltas to all frames in a scene, ensuring temporal coherence |
| 🎛️ **Confidence-weighted blending** | Per-pixel confidence masks prevent over-restoration in regions where the reference photo doesn't match |
| 🎵 **Lossless audio preservation** | FFmpeg stream-copies the original AAC audio track — no re-encoding |
| 📊 **Full processing logs** | Every restoration decision is logged to CSV with status codes and similarity scores |
| 🔄 **Dual restoration modes** | SIFT homography (v1) and face-affine detail transfer (v2) with automatic fallback cascade |

---

## 🛠️ Technology Stack

| Component | Tool / Model | Version |
|---|---|---|
| Video processing | **FFmpeg** | 8.x |
| Scene detection | **PySceneDetect** | 0.6+ |
| Visual embeddings | **OpenCLIP ViT-B-32** | LAION-2B weights |
| Face detection | **InsightFace RetinaFace** | buffalo_l |
| Face embeddings | **InsightFace ArcFace** | ResNet-50, buffalo_l |
| Feature matching | **SIFT / ORB** | OpenCV 4.8+ |
| Optical flow | **Farnebäck** | OpenCV dense flow |
| Image enhancement | **CLAHE, bilateral filter, unsharp mask** | OpenCV |
| Data processing | **NumPy, Pandas** | Latest |
| Progress display | **tqdm** | Latest |
| Deep learning | **PyTorch** | 2.0+ |

---

## 🏗️ Pipeline Workflow

The pipeline consists of 7 stages executed sequentially:

```
Input Video
    │
    ├─ Stage 1 ── PySceneDetect
    │               Scene boundary detection
    │               Output: scenes.csv
    │
    ├─ Stage 2 ── FFmpeg frame extractor
    │               One representative JPEG per scene (midpoint frame)
    │               Output: Representative_Frames/
    │
    ├─ Stage 3A ─ OpenCLIP ViT-B-32
    │               512-dim semantic embeddings for frames + album photos
    │               Output: models/*.npy
    │
    ├─ Stage 3B ─ InsightFace buffalo_l
    │               512-dim face identity embeddings
    │               Output: models/*_face_*.npy + *.csv
    │
    ├─ Stage 4 ── Hybrid Matcher
    │               CLIP × 0.30 + Face × 0.70 → ranked album matches
    │               Output: output/advanced_matches.csv
    │
    ├─ Stage 5 ── Frame Restoration (v1 or v2)
    │               Geometric alignment + detail transfer + CLAHE
    │               Output: output/Restored_Frames/
    │
    ├─ Stage 6 ── Video Reconstruction
    │               Optical flow propagation of enhancement delta
    │               Output: output/Restored_Wedding_silent.mp4
    │
    └─ Stage 7 ── FFmpeg audio mux
                    Stream-copy original AAC audio
                    Output: output/Restored_Wedding_final.mp4
```

For a detailed technical explanation of each stage including algorithms,
parameters, and data flow, see [docs/pipeline_stages.md](docs/pipeline_stages.md).

For the Mermaid architecture diagram, see [docs/architecture.md](docs/architecture.md).

---

## 📁 Directory Structure

```
ai-video-restoration/
│
├── scripts/                         # Numbered pipeline scripts (run in order)
│   ├── 01_extract_scenes.sh         # Stage 1: PySceneDetect scene boundary detection
│   ├── 02_extract_frames.sh         # Stage 2: FFmpeg representative frame extraction
│   ├── 03_clip_embeddings.py        # Stage 3A: OpenCLIP visual embedding generation
│   ├── 04_face_embeddings.py        # Stage 3B: InsightFace face embedding generation
│   ├── 05_advanced_matcher.py       # Stage 4: Hybrid CLIP + face frame matching
│   ├── 06_restore_frame.py          # Stage 5A: SIFT homography restoration (v1)
│   ├── 07_restore_frame_v2.py       # Stage 5B: Face-affine detail transfer (v2)
│   ├── 08_rebuild_video.py          # Stage 6: Optical flow video reconstruction
│   └── 09_merge_audio.sh            # Stage 7: FFmpeg audio mux
│
├── utils/                           # Shared helper modules
│   ├── __init__.py
│   ├── matcher_utils.py             # Embedding loading, normalization, similarity
│   └── video_utils.py               # FFmpeg wrappers, frame I/O, resize helpers
│
├── docs/                            # Project documentation
│   ├── architecture.md              # Full pipeline Mermaid diagram + data flow
│   ├── pipeline_stages.md           # Detailed per-stage technical documentation
│   └── sample_commands.md           # Copy-paste CLI reference for all stages
│
├── data/
│   └── sample/
│       └── example-Scenes.csv       # Sample PySceneDetect output (reference format)
│
├── models/                          # Pre-computed embeddings (git-ignored)
│   └── .gitkeep
│
├── output/                          # Generated outputs (git-ignored)
│   └── .gitkeep
│
├── .gitignore                       # Excludes videos, models, outputs, caches
├── LICENSE                          # MIT License
├── README.md                        # This file
├── CONTRIBUTING.md                  # Contribution guidelines
└── requirements.txt                 # Python dependencies
```

**Directories you supply (not included in repo):**

| Directory | Contents |
|---|---|
| `Albums/` | High-quality reference photos from the wedding photographer |
| `Representative_Frames/` | Auto-generated by Stage 2 |
| `data/raw/` | Source video file |

---

## ⚙️ Installation

### 1. Prerequisites

| Dependency | Install |
|---|---|
| Python ≥ 3.10 | [python.org](https://www.python.org/downloads/) |
| FFmpeg ≥ 6.0 | [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (Windows) · `brew install ffmpeg` (macOS) · `apt install ffmpeg` (Linux) |
| PySceneDetect ≥ 0.6 | `pip install scenedetect[opencv]` |
| Git | [git-scm.com](https://git-scm.com/) |

Verify FFmpeg is on your system PATH:

```bash
ffmpeg -version
ffprobe -version
```

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-video-restoration.git
cd ai-video-restoration
```

### 3. Create a Virtual Environment

```bash
# Create environment
python -m venv .venv

# Activate — Windows:
.venv\Scripts\activate

# Activate — macOS / Linux:
source .venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **GPU acceleration (optional but recommended):**
> ```bash
> # Replace the CPU PyTorch build with a CUDA build:
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
>
> # Replace onnxruntime with GPU version for InsightFace:
> pip uninstall onnxruntime
> pip install onnxruntime-gpu
> ```

### 5. Prepare Your Data

Create the following directories and populate them:

```bash
mkdir -p Albums data/raw Representative_Frames
```

| Directory | What to put there |
|---|---|
| `data/raw/` | Your source video file (`.mp4`) |
| `Albums/` | High-quality reference photos (`.jpg`, `.jpeg`, `.png`) |

> The `Representative_Frames/` directory is created automatically by Stage 2.

### 6. Verify InsightFace Model Download

The `buffalo_l` model (~350 MB) is downloaded automatically on first run:

```bash
python -c "from insightface.app import FaceAnalysis; a = FaceAnalysis(name='buffalo_l'); a.prepare(ctx_id=-1)"
```

---

## 🚀 Usage

Run the pipeline stages in order. Each stage produces outputs consumed by the next.

### Stage 1 — Detect Scenes

```bash
bash scripts/01_extract_scenes.sh \
    data/raw/your_video.mp4 \
    data/scenes.csv
```

### Stage 2 — Extract Representative Frames

```bash
bash scripts/02_extract_frames.sh \
    data/raw/your_video.mp4 \
    data/scenes.csv \
    Representative_Frames/
```

### Stage 3A — Generate CLIP Embeddings

```bash
python scripts/03_clip_embeddings.py \
    --albums Albums/ \
    --frames Representative_Frames/ \
    --models models/
```

### Stage 3B — Generate Face Embeddings

```bash
python scripts/04_face_embeddings.py \
    --albums Albums/ \
    --frames Representative_Frames/ \
    --models models/
# Add --gpu for faster inference
```

### Stage 4 — Match Frames to Album Photos

```bash
python scripts/05_advanced_matcher.py \
    --models models/ \
    --output output/ \
    --top-k 5 \
    --face-weight 0.70
```

### Stage 5 — Restore Representative Frames

**v2 (recommended)** — face-affine + detail transfer:

```bash
python scripts/07_restore_frame_v2.py \
    --csv output/advanced_matches.csv \
    --frames Representative_Frames/ \
    --albums Albums/ \
    --output output/
```

**v1 (fallback)** — SIFT homography:

```bash
python scripts/06_restore_frame.py \
    --csv output/advanced_matches.csv \
    --frames Representative_Frames/ \
    --albums Albums/ \
    --output output/
```

### Stage 6 — Reconstruct Full Video

```bash
python scripts/08_rebuild_video.py \
    --video data/raw/your_video.mp4 \
    --scenes data/scenes.csv \
    --restored-dir output/Restored_Frames/ \
    --output output/Restored_Wedding_silent.mp4 \
    --strength 0.72 \
    --temporal-strength 0.68 \
    --detail-strength 0.35
```

### Stage 7 — Merge Original Audio

```bash
bash scripts/09_merge_audio.sh \
    output/Restored_Wedding_silent.mp4 \
    data/raw/your_video.mp4 \
    output/Restored_Wedding_final.mp4
```

---

## 🖥️ Sample Commands

For a complete reference of all commands including quality comparison,
PSNR/SSIM measurement, and utility scripts, see [docs/sample_commands.md](docs/sample_commands.md).

**Quick side-by-side quality comparison:**

```bash
ffmpeg \
  -i data/raw/your_video.mp4 \
  -i output/Restored_Wedding_final.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2" \
  -c:v libx264 -crf 18 \
  output/comparison.mp4
```

---

## ⚡ Performance

| Stage | CPU Time | GPU Time | Notes |
|---|---|---|---|
| Scene Detection | ~2 min | — | Per hour of 1080p video |
| Frame Extraction | ~3 min | — | Per hour of video |
| CLIP Embeddings | ~8 min | ~1 min | 500 images, ViT-B-32 |
| Face Embeddings | ~12 min | ~2 min | 500 images, buffalo_l |
| Hybrid Matching | <1 min | — | 200 frames × 500 album |
| Frame Restoration v2 | ~15 min | ~3 min | 200 frames |
| Video Reconstruction | ~45 min | — | Farnebäck flow, 1080p, 1 hour video |
| Audio Merge | ~30 sec | — | Stream copy, no re-encoding |

> Benchmarks on: Intel i7-12700H, NVIDIA RTX 3060, 32 GB RAM.
> GPU times require CUDA + onnxruntime-gpu.

---

## ⚠️ Known Limitations

1. **SIFT homography failures** — When album photos and video frames have very
   different crops, angles, or lighting, SIFT finds insufficient matches and
   the frame falls back to unrestored.

2. **Face-alignment dependency** — v2 restoration quality is highest when both
   the video frame and the album photo contain a clear, large, frontal face of
   the same person. Side profiles or occluded faces degrade alignment.

3. **Temporal flickering at scene boundaries** — Optical flow cannot compensate
   for hard cuts. Frames at the very start of a scene may show brief
   enhancement discontinuities.

4. **No multi-GPU support** — CLIP inference and InsightFace run on a single
   GPU. Batch sizes could be tuned for larger GPU memory.

5. **Album photo quality ceiling** — The restoration can only recover detail
   that exists in the reference album photos. If the album photos are also
   compressed or blurry, restoration quality is limited.

6. **Audio synchronisation** — If the reconstructed video frame rate drifts
   from the source (e.g., due to codec rounding), audio may drift slightly.
   The `-shortest` flag mitigates but does not fully resolve this.

---

## 🔮 Future Improvements

- [ ] **Real-ESRGAN integration** — Replace CLAHE + unsharp with a trained
  super-resolution model for higher perceptual quality.
- [ ] **RAFT optical flow** — Replace Farnebäck with learning-based RAFT flow
  for more accurate propagation on complex motion.
- [ ] **Batch parallelism** — Process multiple scenes concurrently using
  `multiprocessing` or `concurrent.futures`.
- [ ] **PySceneDetect adaptive threshold** — Automatically tune detection
  threshold based on video motion statistics.
- [ ] **Confidence score calibration** — Use a held-out validation set to
  calibrate the CLIP/face weighting (70/30) rather than hand-tuning.
- [ ] **Web interface** — A simple Gradio or Streamlit UI for non-technical
  users to run the pipeline with drag-and-drop inputs.
- [ ] **VMAF quality metric** — Replace PSNR/SSIM with VMAF for perceptually
  accurate quality measurement.

---

## 🙏 Credits

This project would not be possible without these outstanding open-source
projects:

| Project | Authors | Use |
|---|---|---|
| [FFmpeg](https://ffmpeg.org/) | FFmpeg developers | Video processing, audio mux, frame extraction |
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | Brandon Castellano | Scene boundary detection |
| [OpenCLIP](https://github.com/mlfoundations/open_clip) | ML Foundations / LAION | Visual semantic embeddings |
| [InsightFace](https://github.com/deepinsight/insightface) | DeepInsight | Face detection and identity embeddings |
| [OpenCV](https://opencv.org/) | OpenCV team | Image processing, optical flow, feature matching |
| [PyTorch](https://pytorch.org/) | Meta AI | Deep learning backend |
| [ONNX Runtime](https://onnxruntime.ai/) | Microsoft | InsightFace CPU/GPU inference |
| [NumPy](https://numpy.org/) | NumPy community | Numerical computing |
| [pandas](https://pandas.pydata.org/) | pandas community | CSV/dataframe processing |
| [tqdm](https://github.com/tqdm/tqdm) | tqdm community | Progress bars |

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute this code for any purpose,
including commercial use, with attribution.

---

<div align="center">

Made with ❤️ — an engineering project born from the desire to preserve an
irreplaceable memory.

</div>
