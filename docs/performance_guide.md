# Performance Guide (Redesigned Research Pipeline)

This guide describes how to run and optimize the redesigned AI Video Restoration Pipeline. The pipeline has been engineered to run efficiently on low-VRAM hardware, specifically targetting the **NVIDIA RTX 3050 4GB GPU**, while maintaining high-fidelity restoration and modern optical flow propagation.

---

## 1. Hardware Recommendations

| Component | Minimum | Recommended | Redesign Optimization Target |
|---|---|---|---|
| **GPU** | CPU-only (fallback) | NVIDIA RTX 3060 (12 GB VRAM) | **NVIDIA RTX 3050 (4 GB VRAM)** |
| **RAM** | 8 GB | 16 GB | 16 GB |
| **Storage** | HDD | NVMe SSD | NVMe SSD (Highly Recommended) |
| **CPU** | 4-core | 6-core+ | 6-core+ |

---

## 2. Low-VRAM Memory Bottleneck Management

Running multiple deep neural networks concurrently (CLIP, InsightFace, VGG16 Perceptual LPIPS, RAFT, and Real-ESRGAN) will easily exceed the 4GB memory boundary, causing CUDA Out-Of-Memory (OOM) crashes. The redesign implements several memory-handling mechanisms:

### A. Sequential Model Lifecycles
Models are loaded on-demand when a stage executes, and are completely deleted followed by a CUDA cache release before the next stage starts:
```python
# Free memory after execution
del model
torch.cuda.empty_cache()
```

### B. Coarse-to-Fine Search
To avoid running VGG16 Perceptual feature extraction on all combination pairs of video frames and album photos, we perform a coarse selection (using fast matrix dot-products of CLIP and ArcFace embeddings) and run the heavy LPIPS-like evaluation **only on the top-10 candidate images**.

### C. FP16 Inference Mode
All PyTorch networks are cast to `FP16` (half-precision) and executed inside `torch.inference_mode()`. This disables autograd tracking entirely, saving up to 50% activation VRAM.

### D. Direct FFmpeg Piping
In Stage 7 (Optical Flow detail propagation), instead of holding the entire output video sequence in CPU memory or using slow, uncompressed intermediate frames, reconstructed BGR frames are streamed directly to FFmpeg via a subprocess pipe. This maintains constant system memory consumption throughout the propagation run.

---

## 3. Configuration Tuning

All parameters are configured in [configs/pipeline_config.yaml](file:///c:/Users/hp/Downloads/ffmpeg-8.1.2-essentials_build/configs/pipeline_config.yaml):

### CLIP Batch Size
```yaml
clip_embeddings:
  batch_size: 32   # Set to 16 if experiencing OOM on older GPUs, or 64/128 on larger GPUs (e.g. RTX 3060/4090)
```

### RAFT Flow Model
```yaml
video_propagation:
  model_type: "raft_small"  # Options: "raft_small" (approx. 1.2 GB VRAM) or "raft_large" (approx. 2.5 GB VRAM)
```
*Use `raft_small` for 4GB GPUs. It provides sub-pixel motion details with 2× faster throughput and half the VRAM footprint.*

---

## 4. Expected Resource Overhead (RTX 3050 4GB)

Estimated resource requirements for a **1-minute 1080p 30 FPS video** and a **100-image reference album**:

| Stage | Model / Tool | VRAM Usage | CPU / IO Overhead | Execution Time |
|---|---|---|---|---|
| **Stage 1 (Video Repair)** | FFmpeg / PySceneDetect | < 100 MB | High CPU | ~15 seconds |
| **Stage 2 (Frame Extract)** | FFmpeg Seeking | < 50 MB | High Disk IO | ~10 seconds |
| **Stage 3 (CLIP Embed)** | OpenCLIP ViT-B-32 (FP16) | ~450 MB | Low | ~10 seconds |
| **Stage 4 (InsightFace)** | ORT CUDA / RetinaFace / ArcFace | ~700 MB | Low | ~20 seconds |
| **Stage 5 (Hybrid Match)** | VGG16 Perceptual (FP16) | ~550 MB | Medium | ~12 seconds |
| **Stage 6 (Restoration)** | Real-ESRGAN / Alignment | ~1.5 GB | High Disk IO | ~90 seconds |
| **Stage 7 (Propagation)** | torchvision RAFT-small (FP16) | ~1.2 GB | Very High Disk IO | ~180 seconds |
| **Stage 8 (Audio Mux)** | FFmpeg copy | < 50 MB | Low | ~2 seconds |

---

## 5. Troubleshooting & Tips

### ONNX Runtime CUDA Execution Provider Fails
If InsightFace warns that `CUDAExecutionProvider` is not available, check your CUDA/cuDNN version matching with ONNX Runtime, or allow it to fall back to `CPUExecutionProvider` (this happens automatically and runs fine, but is slightly slower).

### Slower Disk Write Rates
Ensure your `output/` directory resides on an SSD. Video propagation reads original frames and writes upscaled restored frames in a fast loop; traditional HDDs will bottleneck CPU and GPU pipelines.
