# Sample Commands Reference

> Preview the algorithm interactively: [preview.md](preview.md)

Practical, copy-paste commands for running every stage of the pipeline.

---

## Prerequisites

```bash
# Verify FFmpeg is installed
ffmpeg -version

# Verify Python environment
python --version  # Must be >= 3.10
pip install -r requirements.txt

# Verify PySceneDetect
scenedetect version
```

---

## Stage 1 — Scene Detection

```bash
# Detect scenes with default sensitivity (threshold=27)
scenedetect \
  --input "data/raw/Wedding_Compressed_AAC.mp4" \
  --output "data/" \
  detect-content \
  --threshold 27 \
  --min-scene-len 15 \
  list-scenes \
  --output "data/scenes.csv"

# Stricter detection (fewer, longer scenes)
scenedetect \
  --input "data/raw/Wedding_Compressed_AAC.mp4" \
  detect-content --threshold 40 \
  list-scenes --output "data/scenes_strict.csv"

# Looser detection (more, shorter scenes)
scenedetect \
  --input "data/raw/Wedding_Compressed_AAC.mp4" \
  detect-content --threshold 15 \
  list-scenes --output "data/scenes_loose.csv"
```

---

## Stage 2 — Frame Extraction

```bash
# Extract ALL frames (for manual inspection)
ffmpeg \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -q:v 2 \
  "Representative_Frames/frame_%06d.jpg"

# Extract one frame at a specific timecode (HH:MM:SS)
ffmpeg \
  -ss 00:05:30 \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -vframes 1 \
  -q:v 2 \
  "Representative_Frames/scene_test.jpg"

# Extract one frame at a specific frame number (N=1500)
ffmpeg \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -vf "select=eq(n\,1500)" \
  -vframes 1 \
  -q:v 2 \
  "Representative_Frames/scene_0001.jpg"

# Inspect video metadata
ffprobe \
  -v quiet \
  -print_format json \
  -show_format \
  -show_streams \
  "data/raw/Wedding_Compressed_AAC.mp4"
```

---

## Stage 3A — CLIP Embeddings

```bash
# Generate CLIP embeddings for album photos and representative frames
python scripts/03_clip_embeddings.py

# Expected output:
# Using Device: cuda
# Album Images : 342
# Frame Images : 187
# Saved 342 album embeddings.
# Saved 187 frames embeddings.
# DONE
```

---

## Stage 3B — Face Embeddings

```bash
# Generate InsightFace embeddings (requires buffalo_l model)
# Model is downloaded automatically on first run (~350 MB)
python scripts/04_face_embeddings.py

# Expected output:
# Loading InsightFace...
# Album Images : 342
# Frame Images : 187
# Saved 289 embeddings  (frames where a face was detected)
# ...
# FACE EMBEDDINGS COMPLETED SUCCESSFULLY
```

---

## Stage 4 — Hybrid Matching

```bash
# Run advanced matcher (CLIP 30% + Face 70%)
python scripts/05_advanced_matcher.py

# Expected output:
# Loading models...
# Loading face maps...
# Matching...
# Frames: 100%|████████████| 187/187 [00:12<00:00, 14.8frame/s]
# Saving CSV...
# Completed.
```

---

## Stage 5A — Frame Restoration v1

```bash
# Restore representative frames using SIFT homography method
python scripts/06_restore_frame.py

# Inspect restoration log
cat output/restore_log.csv | head -20
```

---

## Stage 5B — Frame Restoration v2 (Recommended)

```bash
# Restore using face-affine + detail transfer (requires buffalo_l model)
python scripts/07_restore_frame_v2.py

# This version produces better results when album photos contain clear faces
# matching the video subjects.
```

---

## Stage 6 — Video Reconstruction

```bash
# Reconstruct full video with default parameters
python scripts/08_rebuild_video.py \
  --video "data/raw/Wedding_Compressed_AAC.mp4" \
  --scenes "data/scenes.csv" \
  --restored-dir "output/Restored_Frames" \
  --output "output/Restored_Wedding_silent.mp4"

# Stronger enhancement (may introduce artifacts)
python scripts/08_rebuild_video.py \
  --strength 0.90 \
  --temporal-strength 0.80 \
  --detail-strength 0.50 \
  --output "output/Restored_strong.mp4"

# Conservative enhancement (safer for noisy sources)
python scripts/08_rebuild_video.py \
  --strength 0.50 \
  --temporal-strength 0.55 \
  --detail-strength 0.20 \
  --output "output/Restored_conservative.mp4"

# Use a custom project directory
python scripts/08_rebuild_video.py \
  --project-dir /path/to/project \
  --video my_video.mp4 \
  --scenes my_scenes.csv \
  --restored-dir custom_restored/ \
  --output final_output.mp4
```

---

## Stage 7 — Audio Merge

```bash
# Mux original audio into the reconstructed silent video
ffmpeg \
  -i "output/Restored_Wedding_silent.mp4" \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -c:v copy \
  -c:a copy \
  -map 0:v:0 \
  -map 1:a:0 \
  -shortest \
  "output/Restored_Wedding_final.mp4"

# Verify audio stream was muxed correctly
ffprobe -v quiet -show_streams "output/Restored_Wedding_final.mp4" \
  | grep codec_type
# Expected: codec_type=video
#           codec_type=audio
```

---

## Quality Comparison

```bash
# Side-by-side visual comparison (plays original left / restored right)
ffmpeg \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -i "output/Restored_Wedding_final.mp4" \
  -filter_complex "[0:v][1:v]hstack=inputs=2" \
  -c:v libx264 -crf 18 \
  "output/comparison_side_by_side.mp4"

# Compute PSNR between original and restored (higher = closer to original)
ffmpeg \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -i "output/Restored_Wedding_final.mp4" \
  -lavfi "psnr" \
  -f null -

# Compute SSIM between original and restored
ffmpeg \
  -i "data/raw/Wedding_Compressed_AAC.mp4" \
  -i "output/Restored_Wedding_final.mp4" \
  -lavfi "ssim" \
  -f null -
```

---

## Utility Commands

```bash
# Count scenes in CSV
python -c "import pandas as pd; df=pd.read_csv('data/scenes.csv'); print(f'{len(df)} scenes detected')"

# Check how many frames were successfully restored
python -c "
import pandas as pd
log = pd.read_csv('output/restore_log.csv')
print(log['Status'].value_counts())
"

# Check GPU availability for PyTorch
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Check GPU availability for ONNX (InsightFace)
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

