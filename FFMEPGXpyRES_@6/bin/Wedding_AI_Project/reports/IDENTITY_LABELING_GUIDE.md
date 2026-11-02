# Identity Labeling Guide for Human Evaluation Session

This guide outlines the rules and procedure for human labeling of video face candidates in `reports/identity_labels.csv` using the interactive labeling sheet [`reports/labeling_sheet.html`](file:///c:/Users/hp/Downloads/ffmpeg-8.1.2-essentials_build/FFMEPGXpyRES_@6/bin/Wedding_AI_Project/reports/labeling_sheet.html).

---

## 1. Core Labeling Rules

1. **Independent Verification**:
   - Label a face **only if you are confident who it is** by comparing it with the album reference photos yourself.
   - Do **NOT** use the pipeline's top-1 match, similarity scores, or model suggestions as a basis for your labels. Model predictions have been hidden on the review sheet to eliminate confirmation bias.

2. **Allowed Person Identifiers**:
   - Use only the person IDs from `reports/album_face_names.csv` (or the reference image names without `.jpg`, e.g., `20260704_161931`, `20260704_162832`), spelled exactly, OR consistent human person roles (e.g., `groom`, `bride`, `person_1`).
   - If using photo IDs as person proxies, click any album photo thumbnail in `labeling_sheet.html` to automatically apply that reference ID.

3. **When to Leave Values Blank (Unsure)**:
   - Leave the `true_person_id` column blank for:
     - Faces where you are unsure of the identity.
     - Side profiles or steep angles where facial identity is unclear.
     - Severely blurred, noisy, or low-resolution crops.
     - Faces of individuals who do not appear anywhere in the album reference set.

4. **Multi-Person Diversity Requirement**:
   - Aim for **at least 20 labeled faces** from **at least 3 different people** (if the album contains them).
   - A benchmark test containing only a single person does not constitute a valid identity discrimination test.

5. **Saving and Submitting**:
   - When labeling is complete in `labeling_sheet.html`, click **"Download identity_labels.csv"**.
   - Move or save the exported CSV to `reports/identity_labels.csv`.
   - Ensure the commit is saved with your own Git author name.

---

## 2. Review Sheet Quick Start

Open the self-contained review interface in your browser:
```powershell
Start-Process "reports\labeling_sheet.html"
```
The review sheet displays:
- All 30 candidate video face crops from `reports/identity_review/` with their frame names and face indices.
- An interactive reference drawer with all 65 album photographs.
- Input boxes with live progress tracking and an instant **"Download identity_labels.csv"** export button.
