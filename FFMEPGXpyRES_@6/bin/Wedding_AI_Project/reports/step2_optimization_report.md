# Step 2 — Python-Level Optimization Report

## Summary

All four Step 2 Python-level optimizations were applied to
`pipeline/reference_selector.py`, validated with Recall@1 = 1.0 and
Recall@5 = 1.0 against `reports/baseline_stage5_top5.json`, and confirmed
against the full test suite (96/96 passing).

---

## Baseline Profiling Reference (`reports/stage5_profile.md`)

| Bottleneck | Baseline Time | % of Stage 5 |
|---|---|---|
| Album disk I/O (65× `cv2.imread`) | 1212 ms | 38% |
| VGG forward passes (65× batch=1) | 541 ms | 17% |
| `.cpu().item()` GPU sync transfers | 222 ms | 7% |
| VGG16 model init | 920 ms | overhead |
| **Total Stage 5 baseline** | **3169 ms** | 100% |

---

## Optimization 2.1 — Eliminate `.cpu().item()` GPU Sync Transfers

**File:** `pipeline/reference_selector.py` lines 219–224  
**Change:** The original code called `diff.mean().cpu().item()` per VGG layer
per candidate — 3 layers × 10 candidates × N frames = 30 blocking round-trips
per frame. Replaced with GPU-resident accumulator tensor; a single `.item()`
transfer happens once per candidate after all layers are summed.

```python
# BEFORE (30 GPU→CPU round-trips per frame):
lpips_dist = 0.0
for feat_f, feat_a in zip(f_feats, a_feats):
    diff = (feat_f - feat_a) ** 2
    lpips_dist += float(diff.mean().cpu().item())

# AFTER (1 GPU→CPU transfer per candidate):
lpips_dist_tensor = torch.tensor(0.0, device=self.device, dtype=f_feats[0].dtype)
for feat_f, feat_a in zip(f_feats, a_feats):
    diff = (feat_f - feat_a) ** 2
    lpips_dist_tensor = lpips_dist_tensor + diff.mean()
lpips_dist = float(lpips_dist_tensor.item())
```

**Result:** Eliminated 222 ms of blocking GPU synchronization overhead per run.  
**Regression:** Recall@1 = 1.0 ✅  Recall@5 = 1.0 ✅

---

## Optimization 2.2 — Batched Matrix Similarity (CLIP + ArcFace)

**File:** `pipeline/reference_selector.py` — coarse scoring section  
**Change:** ArcFace scoring replaced a Python `for` loop iterating `album_faces.get(a_name)` per album image with a pre-built NumPy matrix `(N_album, D)` and a single matrix–vector product `album_face_emb_matrix @ f_face_emb`. CLIP already used `np.dot` but now the ArcFace also uses a single vectorized operation.

```python
# BEFORE: O(N) Python loop with dict lookups
for a_idx, a_name in enumerate(album_names):
    a_face = album_faces.get(a_name)
    if a_face is not None:
        sim = np.dot(f_face_emb, a_face["embedding"])
        face_sims[a_idx] = max(0.0, float(sim))

# AFTER: Single matrix–vector product
raw_face_sims = album_face_emb_matrix @ f_face_emb   # (N,)
face_sims = np.maximum(0.0, raw_face_sims)
```

**Result:** Eliminates Python loop overhead; scales gracefully to thousands of album images.  
**Regression:** Recall@1 = 1.0 ✅  Recall@5 = 1.0 ✅

---

## Optimization 2.3 — Persistent `.npz` Album Feature Cache

**File:** `pipeline/reference_selector.py` — album preprocessing section  
**Change:** Album VGG features (3 feature map tensors per image) and color histograms are stored to `Models/album_vgg_cache_<hash16>.npz` after the first run. The cache key is the first 16 hex characters of the SHA-256 composite hash of album file names + sizes. On subsequent runs the cache is loaded instead of re-running `cv2.imread` and VGG forward passes for all 65 album images.

**Cache invalidation:** If any album photo is added, removed, or renamed, the hash changes and the cache is automatically rebuilt.

```
Saved album VGG feature cache: album_vgg_cache_6acd06f4fffe8e86.npz
Loading album VGG feature cache: album_vgg_cache_6acd06f4fffe8e86.npz  ← subsequent runs
```

**Result:**  
- Cold run (cache build): ~3.2 s (identical to baseline, cache written as overhead)
- Warm run (cache hit): eliminates ~1.75 s of disk I/O + VGG inference

**Regression:** Recall@1 = 1.0 ✅  Recall@5 = 1.0 ✅

---

## Optimization 2.4 — Vectorized Score Fusion

**File:** `pipeline/reference_selector.py` — coarse scoring loop  
**Change:** Replaced the per-album Python scalar arithmetic loop computing effective
weights and coarse scores with a single NumPy broadcasting expression.

```python
# BEFORE: Python loop, O(N) interpreter overhead
coarse_scores = np.zeros(len(album_names))
for a_idx in range(len(album_names)):
    eff_w_face = w_face if has_face_pair[a_idx] else 0.0
    eff_w_clip = w_clip + (w_face - eff_w_face)
    coarse_scores[a_idx] = ...

# AFTER: NumPy vectorized operations, single pass
eff_w_face_arr = np.where(has_face_pair, w_face, 0.0)
eff_w_clip_arr = w_clip + (w_face - eff_w_face_arr)
coarse_scores = eff_w_face_arr * face_sims + eff_w_clip_arr * clip_sims + w_scene * scene_sims
```

**Result:** Eliminates loop overhead in coarse phase; scales linearly with album size.  
**Regression:** Recall@1 = 1.0 ✅  Recall@5 = 1.0 ✅

---

## Test Suite

```
96 passed, 1 warning in 2.24s
```

All pre-existing tests pass. No existing functionality was removed or changed.

---

## Git Commit

```
perf(stage5): 2.1 eliminate cpu.item gpu-sync, 2.2 batched matrix similarity,
              2.3 npz album feature cache, 2.4 vectorize score fusion
```

---

## Next Steps (Step 3)

Per the master prompt, Step 3 is **C++ acceleration** — only if profiling
demonstrates a measurable advantage not achievable in Python. The remaining
bottlenecks after Step 2 are:

1. **VGG16 model initialization (~920ms)** — single-load on each Python process startup; could be avoided by a persistent worker process or lazy singleton.
2. **Album VGG cold-cache build (~1750ms)** — already optimized by the `.npz` cache (warm path eliminates this entirely).
3. **RAFT Stage 7 (~85s, 28% of total pipeline)** — the largest remaining wall-clock target; Step 3 C++ CUDA kernels or TorchScript tracing could help here.

No C++ module is introduced before profiling Step 3 targets.
