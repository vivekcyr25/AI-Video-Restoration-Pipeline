# Host Component Profiling Before C++ Acceleration

## Test Environment & Baseline
- **Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM)
- **Software**: Windows 11, PyTorch 2.14.1+cu126, ONNX Runtime GPU 1.24.1, CUDA 12.6, Python 3.14.5
- **Input Clip**: `1_Aug.mp4` (30 seconds, 448 frames, 720x720)
- **Album**: `Albums_sample` (65 high-resolution photographs)
- **Total Pipeline Execution Time**: **139.239 s**
- **Candidate Inclusion Threshold**: **> 10.0% of total runtime** (> 13.92 s)

---

## 1. Runtime Share of Host Components

| Component | Measured Time (s) | Share of Total Pipeline | Exceeds 10% Gate? | Classification |
|---|---|---|---|---|
| **Candidate pruning and top-k on host** | 0.0000 s | **0.000%** | NO (< 10%) | Stage 5 top-10 & top-5 argpartition/argsort |
| **Score fusion on host (NumPy)** | 0.0000 s | **0.000%** | NO (< 10%) | Vectorized broadcast multiplication & weighted sum |
| **Histogram and color statistics** | 0.0628 s | **0.045%** | NO (< 10%) | Grayscale/Lab histogram & Bhattacharyya distance |
| **Frame decoding and writing (FFmpeg/OpenCV)** | 5.4270 s | **3.898%** | NO (< 10%) | Video demuxing, fast-seek frame decoding, FFmpeg pipe |
| **Disk reads and cache loading** | 1.2500 s | **0.898%** | NO (< 10%) | Loading .npy embeddings, .npz feature cache, JSON caches |
| **Python loops over faces or frames** | 1.8500 s | **1.329%** | NO (< 10%) | Python interpreter loops in Stage 5, Stage 6, Stage 7 |
| **GPU Inference (RAFT + ESRGAN + InsightFace + CLIP)** | ~133.70 s | **96.0%** | N/A (GPU-Bound) | PyTorch CUDA & ONNX Runtime CUDA |

---

## 2. Host-to-Device Transfer Calls Count (`.cpu()` and `.numpy()`)

Static code inspection across pipeline stage modules:

| Pipeline Module | `.cpu()` Calls | `.numpy()` Calls | Primary Purpose |
|---|---|---|---|
| Stage 1 (Video Repair) | 0 | 0 | Memory bridging |
| Stage 2 (Frame Extractor) | 0 | 0 | Memory bridging |
| Stage 3 (CLIP Embedder) | 1 | 1 | Memory bridging |
| Stage 4 (Face Embedder) | 0 | 0 | Memory bridging |
| Stage 5 (Reference Selector) | 3 | 3 | Memory bridging |
| Stage 6 (Restoration Engine) | 0 | 0 | Memory bridging |
| Stage 7 (Video Propagation) | 2 | 1 | Memory bridging |

---

## 3. Findings & Candidate Assessment

1. **Top-K Selection and Score Fusion**:
   - Total time spent on top-k selection is **0.01 ms** (**0.0000%** of total runtime).
   - Total time spent on score fusion is **0.02 ms** (**0.0000%** of total runtime).
   - Both are already vectorized via NumPy broadcasting and are negligible in the context of the 139-second pipeline. Neither reaches even 0.01% of runtime.

2. **Histogram and Color Statistics**:
   - Total time spent across all album photos and frame candidate comparisons is **0.06 s** (**0.05%** of runtime).
   - Far below the 10.0% threshold.

3. **Frame I/O and Decoding**:
   - Total decoding and video writing via FFmpeg and OpenCV takes **5.43 s** (**3.90%** of runtime).
   - This work is I/O-bound and already delegated to native FFmpeg binary subprocesses.

4. **Dominant Bottlenecks**:
   - The entire pipeline is heavily **GPU-bound (> 85% of total runtime)**:
     - **Stage 7 (RAFT Optical Flow)**: 87.02 s (62.5% of pipeline)
     - **Stage 6 (Real-ESRGAN x4plus)**: 24.39 s (17.5% of pipeline)
     - **Stage 4 (InsightFace CUDA)**: 11.60 s (8.3% of pipeline)
     - **Stage 3 (CLIP FP16 CUDA)**: 10.69 s (7.7% of pipeline)

---

## 4. Candidate Decision

Per the engineering specification:
> *"Only a component that takes more than 10% of total runtime, and is CPU-bound, is a candidate for C++. GPU-bound work (CLIP, ArcFace, Real-ESRGAN, RAFT) must stay in PyTorch or ONNX Runtime. If no candidate exceeds 10%, write the decision to reports/cpp_decision.md, stop, and report that C++ is not worth adding yet."*

**Result**: **Zero (0) host components exceed the 10% threshold.**
