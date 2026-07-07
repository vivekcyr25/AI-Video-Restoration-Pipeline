> Visual walkthrough: [preview.md](preview.md)

# Pipeline Stages — Detailed Documentation

Complete technical reference for every processing stage in the AI Video
Restoration pipeline.

---

## Stage 1 — Scene Detection

**Script:** `scripts/01_extract_scenes.sh`  
**Tool:** PySceneDetect + FFmpeg  
**Input:** Source video file (`.mp4`)  
**Output:** `data/scenes.csv` containing scene boundaries

### What it does

Analyzes the video for shot/scene changes by detecting large inter-frame
differences in pixel histograms. Each scene boundary marks where the camera
cut to a new shot.

### Algorithm

PySceneDetect uses the **ContentDetector** algorithm:

1. Compute per-channel HSV histogram for each frame.
2. Calculate the weighted sum of histogram differences between consecutive frames.
3. When the difference exceeds a configurable threshold (default: 27.0), mark a scene boundary.

### Output CSV columns

| Column | Description |
|---|---|
| `Scene Number` | 1-based scene index |
| `Start Frame` | First frame index (inclusive) |
| `End Frame` | Last frame index (inclusive) |
| `Start Time (seconds)` | Scene start in wall-clock seconds |
| `End Time (seconds)` | Scene end in wall-clock seconds |
| `Length (frames)` | Total frame count of scene |

### Parameters

```bash
# Sensitivity threshold (lower = more scenes detected)
--threshold 27.0

# Minimum scene length in frames
--min-scene-len 15
```

---

## Stage 2 — Representative Frame Extraction

**Script:** `scripts/02_extract_frames.sh`  
**Tool:** FFmpeg  
**Input:** Source video + `data/scenes.csv`  
**Output:** `Representative_Frames/scene_XXXX.jpg`

### What it does

For each scene detected in Stage 1, extracts exactly one frame — the midpoint
of the scene — as a high-quality JPEG. This frame becomes the target for AI
restoration and the anchor for optical flow propagation across the entire scene.

### Frame selection strategy

The **midpoint frame** is preferred over the first or last frame because:
- First frames often capture motion blur at the cut point.
- Last frames may anticipate the next cut.
- Midpoints represent the "settled" composition of the shot.

### FFmpeg command pattern

```bash
ffmpeg -i input.mp4 \
  -vf "select=eq(n\,FRAME_NUMBER)" \
  -vframes 1 \
  -q:v 2 \
  output/scene_0001.jpg
```

`-q:v 2` gives near-lossless JPEG quality (scale 1–31, lower = better).

---

## Stage 3A — CLIP Visual Embeddings

**Script:** `scripts/03_clip_embeddings.py`  
**Model:** OpenCLIP ViT-B-32 (pretrained: `laion2b_s34b_b79k`)  
**Input:** `Albums/` + `Representative_Frames/`  
**Output:** `models/album_embeddings.npy`, `models/frames_embeddings.npy`, name lists

### What it does

Encodes every album photo and every representative frame into a 512-dimensional
semantic vector using OpenAI's CLIP visual encoder. These vectors capture
high-level semantic content (scene, objects, colors, composition) and are
invariant to small geometric transforms.

### Model details

| Property | Value |
|---|---|
| Architecture | Vision Transformer, Patch size 32 |
| Embedding dim | 512 |
| Training data | LAION-2B (2 billion image-text pairs) |
| Input resolution | 224×224 (auto-resized + center-cropped) |
| Inference | `torch.no_grad()`, float32 |

### Processing

```python
image = preprocess(Image.open(path).convert("RGB")).unsqueeze(0)
embedding = model.encode_image(image)
embedding /= embedding.norm(dim=-1, keepdim=True)  # L2 normalize
```

### Output format

- `album_embeddings.npy` — shape `(N_album, 512)`, float32
- `frames_embeddings.npy` — shape `(N_frames, 512)`, float32
- `album_names.npy` — shape `(N_album,)`, string filenames
- `frames_names.npy` — shape `(N_frames,)`, string filenames

---

## Stage 3B — Face Identity Embeddings

**Script:** `scripts/04_face_embeddings.py`  
**Model:** InsightFace `buffalo_l` (ArcFace ResNet-50)  
**Input:** `Albums/` + `Representative_Frames/`  
**Output:** `models/album_face_embeddings.npy`, `models/frame_face_embeddings.npy`, CSV manifests

### What it does

Detects the largest face in each image using RetinaFace, then extracts a
512-dimensional ArcFace identity embedding. These embeddings are highly
discriminative for person identity even across large pose, lighting, and
expression changes.

### Pipeline per image

1. **Detection** — RetinaFace finds all face bounding boxes + confidence scores.
2. **Selection** — Largest face by bounding box area is chosen (primary subject heuristic).
3. **Alignment** — Face is aligned to a canonical 5-point landmark configuration.
4. **Embedding** — ArcFace ResNet-50 backbone produces the 512-dim embedding.

### Output CSV columns (`*_face_names.csv`)

| Column | Description |
|---|---|
| `image` | Source filename |
| `embedding_index` | Row index in the `.npy` embedding matrix |
| `x1, y1, x2, y2` | Face bounding box coordinates |
| `score` | Detection confidence score |

---

## Stage 4 — Hybrid Frame–Album Matching

**Script:** `scripts/05_advanced_matcher.py`  
**Input:** All four `.npy` embedding arrays + CSV manifests  
**Output:** `output/advanced_matches.csv`

### What it does

For every representative frame, computes a ranked list of top-K album photos
using a weighted combination of CLIP semantic similarity and face identity
similarity.

### Scoring formula

```
final_score = 0.70 × face_score + 0.30 × clip_score
```

Face scoring is only applied when:
- A face was detected in the frame.
- A face was detected in the album candidate.
- Both embeddings have matching dimensionality (512).

When no face is detected, the score falls back to pure CLIP similarity.

### Cosine similarity computation

```python
# Efficient batch cosine similarity (embeddings are pre-L2-normalized)
clip_similarity = frame_embeddings @ album_embeddings.T  # (N_frames, N_album)
face_similarity = album_face_embeddings @ frame_face_embedding  # (N_album,)
```

### Output CSV columns

| Column | Description |
|---|---|
| `Frame` | Representative frame filename |
| `Rank` | 1 = best match, up to `TOP_K` (default: 5) |
| `AlbumImage` | Matched album photo filename |
| `CLIPScore` | Raw CLIP cosine similarity [0, 1] |
| `FaceScore` | Face cosine similarity [0, 1] or empty |
| `FinalScore` | Weighted combined score |

---

## Stage 5A — Frame Restoration v1 (SIFT Homography)

**Script:** `scripts/06_restore_frame.py`  
**Input:** `output/advanced_matches.csv` + frames + album photos  
**Output:** `output/Restored_Frames/frame_XXXX.jpg`

### What it does

Geometrically aligns the best-matched album photo to the representative frame
using feature-point homography, then blends high-frequency detail from the
album photo into the frame using a confidence mask.

### Processing pipeline per frame

```
1. Load frame + album photo (Rank 1 match)
2. Resize album preserving aspect ratio → fit within frame canvas
3. Detect SIFT keypoints (5000 features) on both images
4. BFMatcher (L2) with Lowe ratio test (0.75) → good matches
5. RANSAC homography (threshold=5.0 px) → warp album to frame geometry
6. Build confidence mask:
   - Canny edge agreement score
   - Sobel gradient agreement score
   - Pixel difference score (exp decay)
7. Apply CLAHE luminance enhancement (LAB color space)
8. Bilateral filter (d=5, sigmaColor=35, sigmaSpace=35)
9. Unsharp mask (amount=0.65, sigma=1.2)
10. Confidence-weighted blend: frame × (1-w) + restored × w
```

### Fallback behaviour

If SIFT fails to find enough inliers (< 12 matches), the frame is logged with
status `not_enough_matches` or `homography_failure` and the original frame is
preserved.

---

## Stage 5B — Frame Restoration v2 (Face-Affine + Detail Transfer)

**Script:** `scripts/07_restore_frame_v2.py`  
**Input:** `output/advanced_matches.csv` + frames + album photos  
**Output:** `output/Restored_Frames/<frame_name>.jpg`

### What it does

An upgraded restoration pipeline that prioritises face regions using an affine
transform (instead of full homography), paired with a texture-aware confidence
map and adaptive frequency detail transfer.

### Processing pipeline per frame

```
1. Load frame + album photo (Rank 1 match)
2. Resize album using cover-crop strategy → same size as frame
3. Detect faces in both images using InsightFace
4. If faces found in both:
   a. Compute affine matrix from face center + scale
   b. Warp album to align face with frame face
   c. Build face region mask (Gaussian-softened)
5. Build confidence map:
   - Canny edge similarity
   - Sobel gradient similarity
   - Local texture similarity (Laplacian + variance + gradient combined)
6. High-frequency detail transfer:
   - album_detail = album - GaussianBlur(album, sigma=1.25)
   - detail_gain = |album_detail| / (|frame_detail| + 8.0)  [clamped to 1.25]
   - frame += album_detail × confidence × gain × 0.32
7. Adaptive CLAHE (LAB space, clipLimit=2.0, tileGrid=8×8)
8. Bilateral denoising (d=5, sigmaColor=32)
9. Adaptive unsharp mask (strength proportional to confidence map)
10. Final weighted blend with original frame
```

### Fallback cascade

| Condition | Action |
|---|---|
| Faces found in both | Face-affine detail transfer |
| No matching faces, high confidence area | Confidence-guided detail transfer |
| Low confidence everywhere | Adaptive CLAHE-only enhancement |
| Album image missing | Frame-only adaptive restoration |

---

## Stage 6 — Full Video Reconstruction

**Script:** `scripts/08_rebuild_video.py`  
**Input:** Source video + `data/scenes.csv` + `output/Restored_Frames/`  
**Output:** `output/Restored_Wedding_silent.mp4`

### What it does

Propagates the restoration enhancement from each representative frame to every
frame in its corresponding scene using dense optical flow. This produces a
temporally coherent restored video without requiring individual per-frame
AI enhancement.

### Processing per scene

```
1. Read original representative frame from video
2. Load restored representative frame from disk
3. Compute enhancement delta:
   delta = (restored - original) decomposed into:
     - low_freq: GaussianBlur(delta, sigma=2.0)
     - detail:   delta - GaussianBlur(delta, sigma=6.0)
   propagated_delta = low_freq + detail × detail_strength

4. For each frame in scene:
   a. Farnebäck optical flow: current_gray → reference_gray
   b. Warp delta to current frame using flow field
   c. Compute confidence from flow residual:
      confidence = exp(-|current - warped_reference| / 42.0)
   d. Optional temporal smoothing from previous frame delta
   e. Apply: output = frame + delta × confidence × strength
```

### Optical flow parameters (Farnebäck)

| Parameter | Value | Effect |
|---|---|---|
| `pyr_scale` | 0.5 | Pyramid downscale factor |
| `levels` | 4 | Pyramid levels |
| `winsize` | 21 | Averaging window size |
| `iterations` | 3 | Iterations per level |
| `poly_n` | 7 | Pixel neighborhood size |
| `poly_sigma` | 1.5 | Gaussian std for polynomial expansion |

### Tunable parameters (CLI flags)

| Flag | Default | Description |
|---|---|---|
| `--strength` | 0.72 | Global enhancement intensity |
| `--temporal-strength` | 0.68 | Weight of previous-frame delta |
| `--detail-strength` | 0.35 | Amplification of high-frequency delta |

---

## Stage 7 — Audio Merge

**Script:** `scripts/09_merge_audio.sh`  
**Tool:** FFmpeg  
**Input:** Silent reconstructed video + original source video  
**Output:** `output/Restored_Wedding.mp4` (with original audio)

### What it does

Copies the original AAC audio stream from the source video and muxes it into
the reconstructed video container. No audio re-encoding is performed — the
stream is copied byte-for-byte, preserving quality and minimising processing
time.

### FFmpeg command

```bash
ffmpeg \
  -i output/Restored_Wedding_silent.mp4 \
  -i input/Wedding_Compressed_AAC.mp4 \
  -c:v copy \
  -c:a copy \
  -map 0:v:0 \
  -map 1:a:0 \
  -shortest \
  output/Restored_Wedding_final.mp4
```

`-c:v copy` and `-c:a copy` ensure no re-encoding; both streams are stream-copied.
`-shortest` truncates to the shorter stream, handling any length discrepancy.

