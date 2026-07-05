#!/usr/bin/env bash
# =============================================================================
#  Stage 7 — Audio Merge
#  Muxes the original AAC audio stream into the reconstructed silent video.
#  No audio or video re-encoding is performed (stream copy).
#
#  Usage:
#    bash scripts/09_merge_audio.sh <silent_video> <source_video> <output>
#
#  Example:
#    bash scripts/09_merge_audio.sh \
#      output/Restored_Wedding_silent.mp4 \
#      data/raw/Wedding_Compressed_AAC.mp4 \
#      output/Restored_Wedding_final.mp4
# =============================================================================

set -euo pipefail

SILENT="${1:?Usage: $0 <silent_video> <source_video> <output>}"
SOURCE="${2:?Usage: $0 <silent_video> <source_video> <output>}"
OUTPUT="${3:?Usage: $0 <silent_video> <source_video> <output>}"
OUTPUT_DIR="$(dirname "$OUTPUT")"

echo "============================================================"
echo "  AI Video Restoration — Stage 7: Audio Merge"
echo "============================================================"
echo "  Reconstructed (silent) : $SILENT"
echo "  Original (audio source): $SOURCE"
echo "  Final output           : $OUTPUT"
echo "============================================================"

for f in "$SILENT" "$SOURCE"; do
    if [[ ! -f "$f" ]]; then
        echo "ERROR: File not found: $f" >&2
        exit 1
    fi
done

mkdir -p "$OUTPUT_DIR"

# Mux video stream from silent reconstruction + audio stream from source.
# -c:v copy  — no video re-encoding (lossless stream copy)
# -c:a copy  — no audio re-encoding (preserves original AAC)
# -map 0:v:0 — take video track from first input (silent reconstruction)
# -map 1:a:0 — take audio track from second input (original source)
# -shortest  — stop at the shorter of the two streams
ffmpeg \
    -i "$SILENT" \
    -i "$SOURCE" \
    -c:v copy \
    -c:a copy \
    -map 0:v:0 \
    -map 1:a:0 \
    -shortest \
    -y \
    "$OUTPUT"

echo ""
echo "Audio merge complete."
echo "Final output: $OUTPUT"
echo ""

# Verify both streams are present
echo "Stream verification:"
ffprobe -v quiet -show_streams "$OUTPUT" 2>/dev/null \
    | grep "codec_type" \
    | sed 's/^/  /'
