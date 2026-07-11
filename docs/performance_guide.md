# Performance Guide

This document describes how to tune each pipeline stage for faster processing
on both GPU and CPU-only systems.

---

## Table of Contents

1. [Hardware Recommendations](#1-hardware-recommendations)
2. [Stage 3A — CLIP Embedding (GPU bottleneck)](#2-stage-3a--clip-embedding)
3. [Stage 3B — Face Embedding](#3-stage-3b--face-embedding)
4. [Stage 4 — Hybrid Matching](#4-stage-4--hybrid-matching)
5. [Stage 5 — Frame Restoration](#5-stage-5--frame-restoration)
6. [Stage 6 — Video Reconstruction](#6-stage-6--video-reconstruction)
7. [Memory Management](#7-memory-management)
8. [Profiling Tips](#8-profiling-tips)

---

## 1. Hardware Recommendations

| Component | Minimum | Recommended |
|---|---|---|
| GPU | None (CPU fallback) | NVIDIA RTX 3060 (12 GB VRAM) |
| RAM | 8 GB | 32 GB |
| Storage | HDD | NVMe SSD |
| CPU | 4-core | 8-core (for OpenCV ops) |

> [!TIP]
> An NVMe SSD alone can cut frame I/O time by 3–5× compared to a spinning HDD,
> particularly during Stage 6 where every frame in the video is read and written.

---

## 2. Stage 3A — CLIP Embedding

**Typical runtime**: 2–10 minutes depending on album size and hardware.

### GPU tuning

```bash
# Maximise throughput — increase batch size until VRAM is 80% full
python scripts/03_clip_embeddings.py --batch-size 128   # RTX 4090 (24 GB)
python scripts/03_clip_embeddings.py --batch-size 64    # RTX 3060 (12 GB)
python scripts/03_clip_embeddings.py --batch-size 16    # GTX 1060 (6 GB)
```

FP16 is enabled automatically on CUDA devices.  If you see NaN embeddings,
force FP32 by patching `use_fp16 = False` in `create_embeddings()`.

### CPU tuning

```bash
# Reduce memory pressure
python scripts/03_clip_embeddings.py --batch-size 4

# Parallelise preprocessing with multiple DataLoader workers
# (edit the script to add: num_workers=os.cpu_count() // 2)
```

---

## 3. Stage 3B — Face Embedding

InsightFace processes images one at a time.  On a modern CPU this runs at
~5–15 frames/second; on a GPU, ~30–60 frames/second.

**Speed tips**:

- Pre-filter blurry frames using `estimate_blur()` (threshold < 50) to skip
  images where InsightFace will produce unreliable embeddings anyway.
- Run on GPU: InsightFace uses ONNX Runtime; set `ctx_id=0` for CUDA.

---

## 4. Stage 4 — Hybrid Matching

Matching is a pure NumPy matrix multiplication and runs in seconds even for
thousands of frames × hundreds of album photos.

For very large datasets (>10,000 gallery images), use the chunked variant:

```python
from utils.matcher_utils import batch_cosine_similarity

# Processes gallery in 512-row chunks to avoid OOM
sim_matrix = batch_cosine_similarity(query_emb, gallery_emb, chunk_size=512)
```

---

## 5. Stage 5 — Frame Restoration

### v1 (SIFT homography)

- **SIFT** is single-threaded.  Set `nfeatures=2000` (default 0 = unlimited)
  to cap keypoint extraction time on high-resolution images.
- **RANSAC** timeout: reduce `RANSAC_THRESHOLD` from 5.0 to 3.0 on clean
  album photos to converge faster.

### v2 (Face affine)

- Face detection on each frame adds ~50–200 ms per frame.
- Pre-compute and cache face landmarks during Stage 3B to avoid redundant
  detection in Stage 5B.

---

## 6. Stage 6 — Video Reconstruction

Optical flow propagation is the most CPU-intensive stage.

```bash
# Reduce search window to speed up flow computation
# (edit 08_rebuild_video.py — change winsize from 15 to 9)
flow = cv2.calcOpticalFlowFarneback(
    prev_gray, curr_gray, None,
    pyr_scale=0.5, levels=3, winsize=9,   # was 15
    iterations=3, poly_n=5, poly_sigma=1.2, flags=0
)
```

> [!NOTE]
> Using `winsize=9` reduces accuracy on scenes with fast camera movement but
> gives a ~2× speedup on the flow computation per frame.

**Parallel processing**: Process independent scenes in parallel using Python's
`multiprocessing.Pool` or `concurrent.futures.ProcessPoolExecutor`.

---

## 7. Memory Management

| Stage | Peak RAM | Reduction strategy |
|---|---|---|
| CLIP embedding | Batch × model size (~600 MB) | Reduce `--batch-size` |
| Similarity matrix | N_frames × N_album × 4 bytes | Use `batch_cosine_similarity` |
| Optical flow | 3 × frame_bytes | Process one scene at a time |
| Video writer | Output buffer | Flush after each scene |

---

## 8. Profiling Tips

```bash
# Profile a single script to find bottlenecks
python -m cProfile -o profile.pstats scripts/06_restore_frame.py
python -c "import pstats; p = pstats.Stats('profile.pstats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Line-by-line profiling (requires line_profiler)
pip install line_profiler
kernprof -l -v scripts/08_rebuild_video.py
```

### Common bottleneck patterns

| Symptom | Likely cause |
|---|---|
| `cv2.resize` takes > 1s per frame | High-resolution input — downscale first |
| SIFT `detect` is slow | Too many keypoints — set `nfeatures=2000` |
| `np.load` is slow | Large `.npy` files on HDD — move to NVMe |
| `subprocess.run` stalls | FFmpeg encoding is the bottleneck — use `-preset ultrafast` |
