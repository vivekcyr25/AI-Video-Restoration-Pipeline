#!/usr/bin/env bash
# =============================================================================
#  Stage 2 — Representative Frame Extraction
#  Extracts one representative (midpoint) frame per scene using FFmpeg.
#
#  Prerequisites:
#    FFmpeg >= 6.0 on PATH
#    Python >= 3.10 with pandas installed
#
#  Usage:
#    bash scripts/02_extract_frames.sh <input_video> <scenes_csv> <output_dir>
#
#  Example:
#    bash scripts/02_extract_frames.sh \
#      data/raw/Wedding_Compressed_AAC.mp4 \
#      data/scenes.csv \
#      Representative_Frames/
# =============================================================================

set -euo pipefail

INPUT_VIDEO="${1:?Usage: $0 <input_video> <scenes_csv> <output_dir>}"
SCENES_CSV="${2:?Usage: $0 <input_video> <scenes_csv> <output_dir>}"
OUTPUT_DIR="${3:-Representative_Frames}"
QUALITY="${QUALITY:-2}"   # JPEG quality 1-31 (lower = better)

echo "============================================================"
echo "  AI Video Restoration — Stage 2: Frame Extraction"
echo "============================================================"
echo "  Input video : $INPUT_VIDEO"
echo "  Scenes CSV  : $SCENES_CSV"
echo "  Output dir  : $OUTPUT_DIR"
echo "  JPEG quality: $QUALITY"
echo "============================================================"

if [[ ! -f "$INPUT_VIDEO" ]]; then
    echo "ERROR: Input video not found: $INPUT_VIDEO" >&2
    exit 1
fi

if [[ ! -f "$SCENES_CSV" ]]; then
    echo "ERROR: Scenes CSV not found: $SCENES_CSV" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Use Python to parse the scenes CSV and extract midpoint frame numbers,
# then invoke FFmpeg for each one.
python3 - "$INPUT_VIDEO" "$SCENES_CSV" "$OUTPUT_DIR" "$QUALITY" <<'PYEOF'
import sys
import subprocess
import pandas as pd
from pathlib import Path

video_path  = sys.argv[1]
csv_path    = sys.argv[2]
output_dir  = Path(sys.argv[3])
quality     = int(sys.argv[4])

df = pd.read_csv(csv_path)

# Normalise column names
df.columns = [c.strip() for c in df.columns]

# Try to find start-frame and length columns
start_col  = next((c for c in df.columns if "start" in c.lower() and "frame" in c.lower()), None)
length_col = next((c for c in df.columns if "length" in c.lower() and "frame" in c.lower()), None)
end_col    = next((c for c in df.columns if "end" in c.lower() and "frame" in c.lower()), None)

if start_col is None:
    print("ERROR: Cannot find 'Start Frame' column in scenes CSV", file=sys.stderr)
    sys.exit(1)

extracted = 0
for i, row in df.iterrows():
    start  = int(row[start_col])
    if length_col:
        length = int(row[length_col])
        midpoint = start + max(0, length - 1) // 2
    elif end_col:
        end = int(row[end_col])
        midpoint = (start + end) // 2
    else:
        midpoint = start

    out_path = output_dir / f"scene_{i+1:04d}.jpg"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"select=eq(n\\,{midpoint})",
        "-vframes", "1",
        "-q:v", str(quality),
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        extracted += 1
        print(f"  [{i+1:>4}/{len(df)}] Frame {midpoint:>6d} → {out_path.name}")
    else:
        print(f"  [{i+1:>4}/{len(df)}] FAILED frame {midpoint}: {result.stderr[-200:]}")

print(f"\nExtracted {extracted}/{len(df)} representative frames → {output_dir}/")
PYEOF
