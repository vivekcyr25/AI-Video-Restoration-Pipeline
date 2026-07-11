# Troubleshooting Guide

Common issues encountered when running the AI Video Restoration pipeline,
with step-by-step diagnosis and fixes.

---

## Table of Contents

1. [FFmpeg / ffprobe not found](#1-ffmpeg--ffprobe-not-found)
2. [OpenCV cannot open video](#2-opencv-cannot-open-video)
3. [CUDA out-of-memory during CLIP embedding](#3-cuda-out-of-memory-during-clip-embedding)
4. [InsightFace: no face detected](#4-insightface-no-face-detected)
5. [Matcher produces only low-confidence matches](#5-matcher-produces-only-low-confidence-matches)
6. [Restoration output looks blurry or washed out](#6-restoration-output-looks-blurry-or-washed-out)
7. [Audio merge produces silent video](#7-audio-merge-produces-silent-video)
8. [Scene detection misses cuts or over-segments](#8-scene-detection-misses-cuts-or-over-segments)
9. [Optical flow propagation artifacts (flickering)](#9-optical-flow-propagation-artifacts-flickering)
10. [Import errors / missing packages](#10-import-errors--missing-packages)

---

## 1. FFmpeg / ffprobe not found

**Symptom**: `FileNotFoundError: [WinError 2] The system cannot find the file specified`
or `subprocess returned exit code 1` when running any pipeline stage.

**Cause**: FFmpeg is not on the system `PATH`.

**Fix**:

```bash
# Windows — add the FFmpeg bin directory to PATH permanently
setx PATH "%PATH%;C:\ffmpeg\bin"

# Verify
ffmpeg -version
ffprobe -version
```

If you downloaded the FFmpeg essentials build bundled with this project,
ensure you added its `bin/` subdirectory to `PATH`, not the root folder.

---

## 2. OpenCV cannot open video

**Symptom**: `RuntimeError: Cannot open video: path/to/video.mp4`

**Possible causes and fixes**:

| Cause | Fix |
|---|---|
| File path contains non-ASCII characters | Move file to a path with ASCII characters only |
| Codec not supported by OpenCV (e.g. HEVC) | Re-encode: `ffmpeg -i input.mp4 -c:v libx264 output.mp4` |
| File is corrupted | Run `ffprobe input.mp4` to check stream integrity |
| OpenCV built without FFmpeg backend | Reinstall: `pip install opencv-python` (includes FFmpeg) |

---

## 3. CUDA out-of-memory during CLIP embedding

**Symptom**: `torch.cuda.OutOfMemoryError: CUDA out of memory`

**Fix**: Reduce the batch size using the `--batch-size` flag:

```bash
# Start small and increase until stable
python scripts/03_clip_embeddings.py --batch-size 8
python scripts/03_clip_embeddings.py --batch-size 16
```

On GPUs with ≥ 8 GB VRAM, `--batch-size 64` works reliably.
On 4 GB GPUs, use `--batch-size 8` or `--batch-size 16`.

The script automatically enables FP16 on CUDA devices, which halves VRAM
usage.  If OOM persists even at `--batch-size 4`, run on CPU instead:

```bash
CUDA_VISIBLE_DEVICES="" python scripts/03_clip_embeddings.py --batch-size 4
```

---

## 4. InsightFace: no face detected

**Symptom**: Script completes but `face_embeddings.npy` has fewer rows than
expected, and the log shows many "No face detected" warnings.

**Possible causes and fixes**:

- **Low-resolution frames**: Frames smaller than 112×112 px may not produce
  valid face detections.  Re-extract at higher resolution.
- **Heavy motion blur**: Use `estimate_blur()` from `utils/image_utils.py`
  to flag and skip frames with variance < 50.
- **Faces too small**: InsightFace `buffalo_l` works best when the face is
  at least 5% of the frame area.  Crop or zoom the region of interest.
- **Wrong model path**: Ensure the `models/buffalo_l/` directory exists and
  was fully downloaded.  Delete and re-download if checksums differ.

---

## 5. Matcher produces only low-confidence matches

**Symptom**: `advanced_matches.csv` shows combined scores < 0.3 for most
frames.

**Diagnostic steps**:

```python
from utils.matcher_utils import load_embeddings, embedding_stats

album = load_embeddings("models/album_embeddings.npy")
frames = load_embeddings("models/frames_embeddings.npy")

print(embedding_stats(album))   # check for zero vectors / NaN
print(embedding_stats(frames))  # check for zero vectors / NaN
```

**Common causes**:

| Issue | Fix |
|---|---|
| Album photos are different event / wrong folder | Confirm `--albums` path points to the correct wedding album |
| Embeddings contain NaN (failed images) | Re-run `03_clip_embeddings.py`; check for corrupt JPEGs |
| Face embeddings are all-zero | Re-run `04_face_embeddings.py` with a valid InsightFace model |
| Threshold too high in advanced matcher | Lower `CLIP_WEIGHT` or check matcher CSV for actual score distribution |

---

## 6. Restoration output looks blurry or washed out

**Symptom**: Restored frames in `output/Restored_Frames/` have lower
perceived sharpness than the original frames.

**Possible causes and fixes**:

- **CLAHE strength too high**: Reduce `clipLimit` in the CLAHE call inside
  `06_restore_frame.py` from 3.0 to 1.5.
- **Confidence mask too aggressive**: Lower `FRAME_ALPHA` (currently 0.82)
  toward 0.90 to lean more on the original frame.
- **Album photo is heavily compressed**: Use a higher-quality scan; JPEG
  artifacts in the album photo propagate into the blend.
- **SIFT failed (< MIN_GOOD_MATCHES)**: The log entry will show `no_homography`.
  Try lowering `MIN_GOOD_MATCHES` from 12 to 8 for scenes with few keypoints.

---

## 7. Audio merge produces silent video

**Symptom**: Final `Restored_Wedding.mp4` plays video but has no audio.

**Diagnostic**:

```bash
ffprobe -v error -show_entries stream=codec_type output/Restored_Wedding.mp4
```

If no audio stream appears, the issue is in the merge step.

**Fixes**:

```bash
# Check that the source video has an audio stream
ffprobe -select_streams a:0 -show_entries stream=codec_type input_video.mp4

# Re-run audio merge manually
ffmpeg -i output/silent_video.mp4 -i input_video.mp4 \
       -c copy -map 0:v:0 -map 1:a:0 -shortest output/final.mp4
```

If the source video has no audio stream (e.g. it was already silent),
the merge will silently produce a video-only output — this is expected
behaviour, not a bug.

---

## 8. Scene detection misses cuts or over-segments

**Symptom**: Too many or too few scenes detected; `scenes.csv` has an
unexpected number of rows.

**Fix**: Adjust the content-detector threshold in `01_extract_scenes.sh`:

```bash
# Lower threshold → more sensitive (detects subtle cuts)
scenedetect -i input.mp4 detect-content --threshold 20

# Higher threshold → less sensitive (only hard cuts)
scenedetect -i input.mp4 detect-content --threshold 40
```

Default is 27.0.  For music videos or fast-cut content, try 15–20.
For slow documentary-style footage, try 35–45.

---

## 9. Optical flow propagation artifacts (flickering)

**Symptom**: The final video shows flicker or ghosting at frame boundaries
within each scene.

**Possible causes**:

- **Large camera motion within scene**: Optical flow cannot handle motion
  > ~20% of frame width per frame.  Use `--max-flow-magnitude` flag to
  skip propagation for frames with excessive motion.
- **Scene boundary off by one frame**: Double-check `scenes.csv` start/end
  frame indices match the frame rate used for extraction.
- **Blend weight too high**: Reduce `PROPAGATION_ALPHA` in `08_rebuild_video.py`
  to blend less of the restoration delta into edge frames.

---

## 10. Import errors / missing packages

**Symptom**: `ModuleNotFoundError` on any pipeline script.

**Fix**: Install all dependencies from the requirements file:

```bash
pip install -r requirements.txt
```

If you are using the `.venv` created with this project:

```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

For GPU (CUDA 12.x) support, install PyTorch separately before the rest:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```
