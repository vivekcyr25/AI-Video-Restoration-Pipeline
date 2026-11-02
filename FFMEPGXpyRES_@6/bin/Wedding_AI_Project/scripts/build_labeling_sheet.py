"""
scripts/build_labeling_sheet.py
===============================
Generates reports/labeling_sheet.html: a self-contained, clean human-labeling
interface for ground-truth identity verification.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent

def build_labeling_sheet():
    candidates_csv = _project_root / "reports" / "identity_candidates.csv"
    album_csv = _project_root / "reports" / "album_face_names.csv"
    if not album_csv.exists():
        album_csv = _project_root / "Models" / "album_face_names.csv"

    candidates = []
    with open(candidates_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            candidates.append({
                "frame_path": r["frame_path"],
                "face_index": r["face_index"],
                "crop_rel": f"identity_review/{Path(r['crop_path']).name}",
            })

    album_photos = []
    with open(album_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            album_photos.append(r["image"])

    album_photos = sorted(list(set(album_photos)))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Face Identity Ground-Truth Labeling Sheet</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --success: #10b981;
      --warning: #f59e0b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 24px; min-height: 100vh; }}
    
    header {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 24px;
      position: sticky;
      top: 12px;
      z-index: 100;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .header-info h1 {{ font-size: 20px; font-weight: 700; color: var(--accent); margin-bottom: 6px; }}
    .header-info p {{ font-size: 13px; color: var(--text-muted); }}
    
    .stats-bar {{
      display: flex;
      gap: 16px;
      align-items: center;
      background: #0f172a;
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      font-size: 13px;
    }}
    .stat-badge {{ font-weight: 600; color: var(--text); }}
    .stat-badge span {{ color: var(--accent); }}
    
    .actions {{ display: flex; gap: 12px; }}
    button.btn {{
      background: var(--accent);
      color: #0f172a;
      border: none;
      padding: 10px 18px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
    }}
    button.btn:hover {{ background: var(--accent-hover); color: white; }}
    button.btn-secondary {{ background: #334155; color: var(--text); }}
    button.btn-secondary:hover {{ background: #475569; }}

    /* Instructions box */
    .guide-banner {{
      background: rgba(56, 189, 248, 0.08);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 24px;
      font-size: 13px;
      line-height: 1.5;
    }}
    .guide-banner strong {{ color: var(--accent); }}

    /* Reference album drawer */
    details.album-ref {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 24px;
    }}
    details.album-ref summary {{
      font-size: 14px;
      font-weight: 600;
      color: var(--accent);
      cursor: pointer;
      user-select: none;
    }}
    .album-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 12px;
      margin-top: 14px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 6px;
    }}
    .album-item {{
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px;
      text-align: center;
      cursor: pointer;
      transition: transform 0.15s, border-color 0.15s;
    }}
    .album-item:hover {{
      transform: scale(1.03);
      border-color: var(--accent);
    }}
    .album-item img {{
      width: 100%;
      height: 100px;
      object-fit: cover;
      border-radius: 4px;
      margin-bottom: 6px;
    }}
    .album-item .name {{
      font-size: 11px;
      color: var(--text-muted);
      word-break: break-all;
    }}

    /* Candidate cards grid */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }}
    .candidate-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .candidate-card.labeled {{
      border-color: var(--success);
      box-shadow: 0 0 0 1px var(--success);
    }}
    .candidate-card.unsure {{
      border-color: var(--warning);
      opacity: 0.7;
    }}
    .crop-wrapper {{
      width: 160px;
      height: 160px;
      background: #000;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
      border: 2px solid #334155;
    }}
    .crop-wrapper img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }}
    .card-meta {{
      text-align: center;
      margin-bottom: 12px;
      font-size: 13px;
    }}
    .card-meta .frame-title {{
      font-weight: 700;
      color: var(--text);
    }}
    .card-meta .face-sub {{
      font-size: 12px;
      color: var(--text-muted);
    }}
    
    .input-group {{
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .input-group input {{
      width: 100%;
      padding: 8px 12px;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      font-size: 13px;
      outline: none;
    }}
    .input-group input:focus {{
      border-color: var(--accent);
    }}
    .button-row {{
      display: flex;
      gap: 6px;
      width: 100%;
    }}
    .btn-small {{
      flex: 1;
      padding: 6px 10px;
      font-size: 11px;
      border: 1px solid var(--border);
      border-radius: 4px;
      background: #334155;
      color: var(--text);
      cursor: pointer;
      text-align: center;
    }}
    .btn-small:hover {{ background: #475569; }}
    .btn-small.active-unsure {{ background: var(--warning); color: #000; font-weight: 700; }}
  </style>
</head>
<body>

  <header>
    <div class="header-info">
      <h1>Face Identity Review & Ground-Truth Labeling</h1>
      <p>Independent human evaluation sheet. Unbiased: model predictions are strictly hidden.</p>
    </div>
    
    <div class="stats-bar">
      <div class="stat-badge">Total: <span id="stat-total">{len(candidates)}</span></div>
      <div class="stat-badge">Labeled: <span id="stat-labeled">0</span></div>
      <div class="stat-badge">Unsure / Blank: <span id="stat-unsure">0</span></div>
    </div>
    
    <div class="actions">
      <button class="btn btn-secondary" onclick="clearAll()">Reset Form</button>
      <button class="btn" onclick="exportCSV()">Download identity_labels.csv</button>
    </div>
  </header>

  <div class="guide-banner">
    <strong>Labeling Guidelines:</strong>
    Compare each candidate face crop with the album photos below. Enter a consistent identifier for each person (e.g., <code>groom</code>, <code>bride</code>, or click any album photo to insert its reference ID like <code>20260704_161931</code>). If identity cannot be determined with confidence, click <strong>Mark Unsure</strong> to leave it blank. Aim for &ge; 20 labeled faces across distinct people.
  </div>

  <details class="album-ref" open>
    <summary>&#128247; Album Reference Photos Gallery ({len(album_photos)} photos available - click any to select ID)</summary>
    <div class="album-grid">
"""
    for photo_name in album_photos:
        ref_id = photo_name.replace(".jpg", "")
        html_content += f"""      <div class="album-item" onclick="applyToActiveInput('{ref_id}')">
        <img src="../Albums_sample/{photo_name}" alt="{ref_id}" loading="lazy">
        <div class="name">{ref_id}</div>
      </div>\n"""

    html_content += """    </div>
  </details>

  <div class="cards-grid">
"""

    for idx, c in enumerate(candidates):
        fpath = c["frame_path"]
        fidx = c["face_index"]
        crop_rel = c["crop_rel"]
        row_id = f"face_{idx}"

        html_content += f"""    <div class="candidate-card" id="card_{row_id}">
      <div class="crop-wrapper">
        <img src="{crop_rel}" alt="{fpath} face {fidx}">
      </div>
      <div class="card-meta">
        <div class="frame-title">{fpath}</div>
        <div class="face-sub">Face Index #{fidx} (Candidate #{idx+1})</div>
      </div>
      <div class="input-group">
        <input type="text" id="input_{row_id}" data-frame="{fpath}" data-index="{fidx}" 
               placeholder="Person ID (e.g. groom, bride, 161931)..." oninput="onInputChange('{row_id}')" onfocus="setActiveInput('{row_id}')">
        <div class="button-row">
          <button class="btn-small" onclick="markUnsure('{row_id}')">Mark Unsure</button>
          <button class="btn-small" onclick="clearField('{row_id}')">Clear</button>
        </div>
      </div>
    </div>\n"""

    html_content += """  </div>

  <script>
    let activeInputId = null;

    function setActiveInput(id) {
      activeInputId = 'input_' + id;
    }

    function applyToActiveInput(idValue) {
      if (!activeInputId) {
        alert("Please click on a candidate face text input box first, then click an album photo to assign its ID.");
        return;
      }
      const el = document.getElementById(activeInputId);
      if (el) {
        el.value = idValue;
        const rowId = activeInputId.replace('input_', '');
        onInputChange(rowId);
      }
    }

    function onInputChange(rowId) {
      const input = document.getElementById('input_' + rowId);
      const card = document.getElementById('card_' + rowId);
      const val = input.value.trim();
      
      if (val === '') {
        card.classList.remove('labeled');
        card.classList.remove('unsure');
      } else {
        card.classList.add('labeled');
        card.classList.remove('unsure');
      }
      updateStats();
      saveProgress();
    }

    function markUnsure(rowId) {
      const input = document.getElementById('input_' + rowId);
      const card = document.getElementById('card_' + rowId);
      input.value = '';
      card.classList.remove('labeled');
      card.classList.add('unsure');
      updateStats();
      saveProgress();
    }

    function clearField(rowId) {
      const input = document.getElementById('input_' + rowId);
      const card = document.getElementById('card_' + rowId);
      input.value = '';
      card.classList.remove('labeled');
      card.classList.remove('unsure');
      updateStats();
      saveProgress();
    }

    function clearAll() {
      if (confirm("Reset all entered labels on this sheet?")) {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
          input.value = '';
          const rowId = input.id.replace('input_', '');
          const card = document.getElementById('card_' + rowId);
          card.classList.remove('labeled');
          card.classList.remove('unsure');
        });
        localStorage.removeItem('identity_labeling_progress');
        updateStats();
      }
    }

    function updateStats() {
      const inputs = document.querySelectorAll('input[type="text"]');
      let labeled = 0;
      let unsure = 0;
      
      inputs.forEach(input => {
        const val = input.value.trim();
        const rowId = input.id.replace('input_', '');
        const card = document.getElementById('card_' + rowId);
        if (val !== '') {
          labeled++;
        } else if (card.classList.contains('unsure')) {
          unsure++;
        }
      });
      
      document.getElementById('stat-labeled').innerText = labeled;
      document.getElementById('stat-unsure').innerText = unsure + (inputs.length - labeled - unsure);
    }

    function saveProgress() {
      const data = {};
      const inputs = document.querySelectorAll('input[type="text"]');
      inputs.forEach(input => {
        data[input.id] = input.value;
      });
      localStorage.setItem('identity_labeling_progress', JSON.stringify(data));
    }

    function loadProgress() {
      const saved = localStorage.getItem('identity_labeling_progress');
      if (!saved) return;
      try {
        const data = JSON.parse(saved);
        for (const [id, val] of Object.entries(data)) {
          const input = document.getElementById(id);
          if (input && val) {
            input.value = val;
            const rowId = id.replace('input_', '');
            const card = document.getElementById('card_' + rowId);
            card.classList.add('labeled');
          }
        }
        updateStats();
      } catch (e) {
        console.error(e);
      }
    }

    function exportCSV() {
      const rows = [["frame_path", "face_index", "true_person_id"]];
      const inputs = document.querySelectorAll('input[type="text"]');
      
      inputs.forEach(input => {
        const fpath = input.getAttribute('data-frame');
        const fidx = input.getAttribute('data-index');
        const val = input.value.trim();
        rows.push([fpath, fidx, val]);
      });
      
      let csvContent = "";
      rows.forEach(r => {
        csvContent += r.map(x => '"' + (x.toString().replace(/"/g, '""')) + '"').join(",") + "\\n";
      });
      
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", "identity_labels.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    window.addEventListener('DOMContentLoaded', () => {
      loadProgress();
      updateStats();
    });
  </script>
</body>
</html>
"""

    out_file = _project_root / "reports" / "labeling_sheet.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated labeling sheet at: {out_file}")

if __name__ == "__main__":
    build_labeling_sheet()
