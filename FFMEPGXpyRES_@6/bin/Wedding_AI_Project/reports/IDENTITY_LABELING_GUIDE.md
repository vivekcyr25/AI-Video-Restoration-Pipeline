# Identity Labeling Guide for Video Face Benchmarking

This guide describes how to populate `reports/identity_labels.csv` for measuring identity precision of the AI Video Restoration Pipeline.

---

## 1. File Structure
The file `reports/identity_labels.csv` contains:
```csv
frame_path,face_index,true_person_id
```

Each row corresponds to a detected face candidate from the video clip, with review crops stored in `reports/identity_review/`:
- Format: `reports/identity_review/frame_{frame_number:04d}_face_{face_index}.jpg`

---

## 2. Labeling Instructions

1. **Open review crops**:
   - Inspect the face crops in `reports/identity_review/`.
   - Compare with album photographs in `Albums_sample/`.

2. **Assign `true_person_id`**:
   - Assign a consistent identifier corresponding to the true person (for example: `groom`, `bride`, `priest`, `guest_01`, or the album photo filename containing that person like `20260704_161931`).
   - If multiple crops represent the same individual, use the **exact same** `true_person_id`.

3. **Ground Truth Independence**:
   - **DO NOT** use the pipeline's suggested matches from `reports/identity_candidates.csv` as ground-truth labels. Label faces based on independent human visual inspection of the album.

4. **Uncertainty**:
   - If a face is too blurry, occluded, or ambiguous to confidently identify, **leave `true_person_id` empty**.
   - Empty rows are automatically skipped by `scripts/identity_precision.py` without penalizing precision.

5. **Minimum Requirement**:
   - At least **20 labeled faces** must have non-empty `true_person_id` entries to compute statistically valid precision with 95% Wilson score confidence intervals.
