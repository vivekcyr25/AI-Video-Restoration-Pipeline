# Pipeline Status & Session Handoff Report

**Date:** 2026-11-03  
**Repository:** https://github.com/vivekcyr25/AI-Video-Restoration-Pipeline  
**Subproject:** `FFMEPGXpyRES_@6/bin/Wedding_AI_Project/`  
**Environment:** Windows, NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM), `venv_gpu`, PyTorch 2.14.1+cu126, ONNX Runtime GPU 1.24.1, CUDA 12.6, FFmpeg 8.1.2.  
**Test Clip:** `1_Aug.mp4` (30 s, 448 frames) | **Album:** `Albums_sample` (65 images)

---

## 1. Preconditions Status (Gate Verification)

| # | Precondition | Status | Evidence / Notes |
|---|--------------|--------|------------------|
| 1 | **Identity Precision >= 0.95 (>= 20 labeled faces)** | **OPEN (Unmeasured)** | Ground-truth labels are not yet entered by a human. `reports/identity_labels.csv` has 30 rows with empty `true_person_id`. Precision cannot be calculated until human labeling is performed. |
| 2 | **Real-ESRGAN uses RealESRGAN_x4plus (nb=23)** | **DONE** | Config updated from anime model (`RealESRGAN_x4plus_anime_6B`) to `RealESRGAN_x4plus` ($nb=23$, 64 MB weights, `conv_first.weight` shape `[64, 3, 3, 3]`). Verified in `configs/pipeline_config.yaml`. |
| 3 | **InsightFace on CUDAExecutionProvider** | **DONE** | Config enforces `stage4.require_gpu: true`. Dynamic PATH injection in `pipeline/face_embedder.py` ensures PyTorch CUDA runtime DLLs are loaded by ONNX Runtime. Stage 4 execution runtime dropped from **191.5 s** on CPU to **11.6 s** on CUDA. |
| 4 | **All Tests Pass (103 expected)** | **DONE** | Ran `pytest tests/` in `venv_gpu`: **103 passed, 0 failed** in 9.16 s. |
| 5 | **Baseline Report Exists** | **DONE** | `reports/baseline_after_fix.json` generated for `1_Aug.mp4` and `Albums_sample`, recording 139.24 s total runtime. |

### Config Diff for Precondition 2 (Real-ESRGAN)
```diff
 realesrgan:
-  model_name: "RealESRGAN_x4plus_anime_6B"
-  model_path: "models/RealESRGAN_x4plus_anime_6B.pth"
+  model_name: "RealESRGAN_x4plus"
+  model_path: "models/RealESRGAN_x4plus.pth"
   tile: 400
   tile_pad: 10
   pre_pad: 0
   half: true
```

---

## 2. Identity Gate (Stage 5)
- **Status:** **UNVERIFIED / PENDING VERIFICATION**
- Requirements for Stage 5 identity gate:
  - ArcFace embeddings only for face reference selection (CLIP excluded from face reference assignment).
  - Each detected face processed individually (not frame-level reference assignment).
  - Rejection if `best_sim < identity.min_sim` (threshold 0.40).
  - Rejection if `(best_sim - second_sim) < identity.min_margin` (threshold 0.05), where second match belongs to a different album person.
  - Rejection logs reason and disables texture transfer.
  - Texture blend capped by `texture.blend_max` (threshold 0.35).
- **Current State:** Stage 5 reference matching has not been measured against verified human labels. Do not claim this gate works until human labels are provided and verified against `reports/stage5_gated.csv`.

---

## 3. Visual Check of Restored Output
- **Status:** **NOT DONE**
- Inspection of output frames generated with strict identity gating and Real-ESRGAN photo model will take place after the identity gate is verified.

---

## 4. C++ Acceleration Decision
- **Status:** **DEFERRED**
- **Decision rationale:**
  1. Gated on Precondition #1 (identity precision).
  2. Profiling in `reports/profile_before_cpp.md` shows that GPU-bound deep learning stages consume **~96%** of total runtime (Real-ESRGAN: 24.3%, RAFT: 61.1%, ArcFace: 8.3%, CLIP: 2.1%).
  3. Host CPU components (candidate pruning, score fusion, color stats, frame I/O, python loops) consume **< 0.1%** of total runtime combined (< 0.15 s out of 139.24 s). None meet the 10% threshold required to justify C++ acceleration. See `reports/cpp_decision.md`.

---

## 5. Invalidated Earlier Results (Audit Record)
- **Invalid Result 1:** 100% identity precision reported prior to the label provenance audit.
- **Invalid Result 2:** Commit `7139876` labels, which were machine-generated via assistant script rather than human review.
- **Resolution:** All labels in `reports/identity_labels.csv` were cleared in commit `af32d6c`, invalid `reports/identity_precision.json` was deleted, and an interactive review sheet was built in `reports/labeling_sheet.html`.

---

## 6. Next Steps for Resuming Work
1. **Human Labeling:**
   - Open `reports/labeling_sheet.html` in a web browser.
   - Review face crops from `reports/identity_review/` against reference photos in `Albums_sample/`.
   - Assign true person IDs according to `reports/IDENTITY_LABELING_GUIDE.md`.
   - Export or save true person IDs to `reports/identity_labels.csv` (aim for >= 20 confident labels across >= 3 people; leave ambiguous faces blank).
2. **Precision Evaluation:**
   - Run `python scripts/identity_precision.py` to evaluate precision and Wilson 95% confidence intervals on the labeled faces.
3. **Identity Gate Verification:**
   - Run Stage 5 with gating enabled and verify coverage on `1_Aug.mp4`.
4. **Visual Inspection:**
   - Visually check restored face crops and scene reconstructions.
5. **Revisit C++ Integration:**
   - Re-evaluate only if bottlenecks shift after full pipeline verification.
