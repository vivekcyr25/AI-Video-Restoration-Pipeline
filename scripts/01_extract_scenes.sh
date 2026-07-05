#!/usr/bin/env bash
# =============================================================================
#  Stage 1 — Scene Detection
#  Uses PySceneDetect to detect scene boundaries in the input video.
#
#  Prerequisites:
#    pip install scenedetect[opencv]
#
#  Usage:
#    bash scripts/01_extract_scenes.sh <input_video> <output_csv>
#
#  Example:
#    bash scripts/01_extract_scenes.sh \
#      data/raw/Wedding_Compressed_AAC.mp4 \
#      data/scenes.csv
# =============================================================================

set -euo pipefail

INPUT_VIDEO="${1:?Usage: $0 <input_video> <output_csv>}"
OUTPUT_CSV="${2:?Usage: $0 <input_video> <output_csv>}"
OUTPUT_DIR="$(dirname "$OUTPUT_CSV")"
THRESHOLD="${THRESHOLD:-27}"
MIN_SCENE_LEN="${MIN_SCENE_LEN:-15}"

echo "============================================================"
echo "  AI Video Restoration — Stage 1: Scene Detection"
echo "============================================================"
echo "  Input  : $INPUT_VIDEO"
echo "  Output : $OUTPUT_CSV"
echo "  Threshold   : $THRESHOLD"
echo "  Min scene   : $MIN_SCENE_LEN frames"
echo "============================================================"

if [[ ! -f "$INPUT_VIDEO" ]]; then
    echo "ERROR: Input video not found: $INPUT_VIDEO" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Run PySceneDetect
scenedetect \
    --input "$INPUT_VIDEO" \
    --output "$OUTPUT_DIR" \
    detect-content \
        --threshold "$THRESHOLD" \
        --min-scene-len "$MIN_SCENE_LEN" \
    list-scenes \
        --output "$OUTPUT_CSV" \
        --filename "$(basename "$OUTPUT_CSV")"

echo ""
echo "Scene detection complete."
echo "CSV saved to: $OUTPUT_CSV"
echo ""

# Print summary
python3 - <<'EOF'
import sys, pandas as pd
try:
    df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "data/scenes.csv")
    print(f"  Total scenes detected : {len(df)}")
    if "Length (frames)" in df.columns:
        avg = df["Length (frames)"].mean()
        print(f"  Average scene length  : {avg:.1f} frames")
except Exception as e:
    print(f"  (Could not parse CSV: {e})")
EOF
