#!/usr/bin/env bash
# tools/proofs/ffmpeg-deliver.sh — WH PROOFS ONLY delivery (not fight code).
#
# Renders/delivers a proof clip from WH renders using FFmpeg (free, open source).
# Inputs are proof renders only: an image sequence, a single proof image, or a
# single proof video. Nothing in this script touches fight code, game logic,
# or any commercial asset. Outputs are proof-delivery files, not game assets.
#
# Usage:
#   tools/proofs/ffmpeg-deliver.sh --input <path> --out-dir <dir> [--fps N]
#                                  [--slug NAME] [--audio <file>]
#   tools/proofs/ffmpeg-deliver.sh --input frames/ --out-dir proof-out/
#   tools/proofs/ffmpeg-deliver.sh --input render.mp4 --out-dir proof-out/
#   tools/proofs/ffmpeg-deliver.sh --input still.png --out-dir proof-out/ --fps 30
#
# Inputs:
#   --input   Directory of PNG/JPG frames, a single image, or a video file.
#             A directory is read as a frame sequence sorted by filename.
#   --out-dir Directory created for the delivery (fails if it already exists,
#             so a delivery is never silently overwritten).
#   --fps     Frame rate for sequences / stills (default 30).
#   --slug    Output basename (default: proof). Sanitised to [A-Za-z0-9_-].
#   --audio   Optional audio file mixed in; proofs are silent by default.
#
# Outputs (all inside --out-dir):
#   <slug>.mp4        H.264 / yuv420p proof clip, web-playable, no audio unless given.
#   <slug>-thumb.jpg  First-frame thumbnail.
#   delivery.json     Manifest: tool versions, input, output size + SHA-256,
#                     duration, fps, resolution. This is the proof record.
#
# Requirements: ffmpeg + ffprobe in PATH. Tested with ffmpeg 8.1.2 on this VM.
# Exit codes: 0 ok, 2 usage/input error, 3 ffmpeg/ffprobe failure.
set -euo pipefail

INPUT=""; OUT_DIR=""; FPS="30"; SLUG="proof"; AUDIO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --input)   INPUT="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --fps)     FPS="$2"; shift 2 ;;
    --slug)    SLUG="$2"; shift 2 ;;
    --audio)   AUDIO="$2"; shift 2 ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$INPUT" ] && [ -n "$OUT_DIR" ] || { echo "error: --input and --out-dir are required" >&2; exit 2; }
[ -e "$INPUT" ] || { echo "error: input not found: $INPUT" >&2; exit 2; }
[ -e "$OUT_DIR" ] && { echo "error: out-dir already exists (refusing to overwrite): $OUT_DIR" >&2; exit 2; }
command -v ffmpeg >/dev/null || { echo "error: ffmpeg not in PATH" >&2; exit 3; }
command -v ffprobe >/dev/null || { echo "error: ffprobe not in PATH" >&2; exit 3; }
SLUG="$(printf '%s' "$SLUG" | tr -c 'A-Za-z0-9_-' '_')"
case "$FPS" in ''|*[!0-9]*) echo "error: --fps must be a positive integer" >&2; exit 2 ;; esac

mkdir -p "$OUT_DIR"
FFMPEG_VER="$(ffmpeg -version | head -n 1)"
TMP_SEQ=""
cleanup() { [ -n "$TMP_SEQ" ] && rm -rf "$TMP_SEQ"; return 0; }  # return 0: a trap failure must not mask the real exit code
trap cleanup EXIT

# Build the video input arguments for the three accepted input shapes.
if [ -d "$INPUT" ]; then
  # Frame sequence: symlink sorted frames into a numbered sequence dir so
  # ffmpeg gets a stable %06d pattern regardless of source filenames.
  mapfile -t FRAMES < <(find "$INPUT" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) | sort)
  [ "${#FRAMES[@]}" -gt 0 ] || { echo "error: no PNG/JPG frames in $INPUT" >&2; exit 2; }
  # A pattern input only matches one extension, so mixed PNG/JPG sequences
  # are rejected rather than silently dropping frames.
  EXT="$(printf '%s' "${FRAMES[0]##*.}" | tr 'A-Z' 'a-z')"
  for f in "${FRAMES[@]}"; do
    e="$(printf '%s' "${f##*.}" | tr 'A-Z' 'a-z')"
    [ "$e" = "$EXT" ] || { echo "error: mixed frame extensions in $INPUT (found .$e and .$EXT); use one format" >&2; exit 2; }
  done
  TMP_SEQ="$(mktemp -d)"
  i=0
  for f in "${FRAMES[@]}"; do
    i=$((i + 1)); ln -s "$(readlink -f "$f")" "$TMP_SEQ/$(printf '%06d' "$i").$EXT"
  done
  VIDEO_ARGS=(-framerate "$FPS" -i "$TMP_SEQ/%06d.$EXT")
elif [ -f "$INPUT" ]; then
  case "$(printf '%s' "$INPUT" | tr 'A-Z' 'a-z')" in
    *.png|*.jpg|*.jpeg)
      VIDEO_ARGS=(-loop 1 -framerate "$FPS" -t 3 -i "$INPUT") ;;  # 3s still clip
    *.mp4|*.mov|*.mkv|*.webm|*.avi)
      VIDEO_ARGS=(-i "$INPUT") ;;
    *) echo "error: unsupported input file type: $INPUT" >&2; exit 2 ;;
  esac
else
  echo "error: input is neither a file nor a directory: $INPUT" >&2; exit 2
fi

if [ -n "$AUDIO" ]; then
  [ -f "$AUDIO" ] || { echo "error: audio not found: $AUDIO" >&2; exit 2; }
  ffmpeg -hide_banner -loglevel error -y "${VIDEO_ARGS[@]}" -i "$AUDIO" \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -pix_fmt yuv420p \
    -c:a aac -shortest -movflags +faststart "$OUT_DIR/$SLUG.mp4"
else
  ffmpeg -hide_banner -loglevel error -y "${VIDEO_ARGS[@]}" \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -pix_fmt yuv420p \
    -an -movflags +faststart "$OUT_DIR/$SLUG.mp4"
fi

ffmpeg -hide_banner -loglevel error -y -i "$OUT_DIR/$SLUG.mp4" -frames:v 1 "$OUT_DIR/$SLUG-thumb.jpg"

PROBE="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name \
  -show_entries format=duration -of json "$OUT_DIR/$SLUG.mp4")"
W="$(printf '%s' "$PROBE" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["streams"][0]["width"])')"
H="$(printf '%s' "$PROBE" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["streams"][0]["height"])')"
DUR="$(printf '%s' "$PROBE" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["format"]["duration"])')"
SIZE="$(stat -c %s "$OUT_DIR/$SLUG.mp4")"
SHA="$(sha256sum "$OUT_DIR/$SLUG.mp4" | cut -d' ' -f1)"
INPUT_DESC="$( [ -d "$INPUT" ] && echo "frame-sequence dir: $INPUT (${#FRAMES[@]} frames)" || echo "file: $INPUT" )"

python3 - "$OUT_DIR/delivery.json" <<EOF
import json, sys
manifest = {
  "scope": "western-heart PROOF ONLY (not fight code, not a game asset)",
  "tool": "ffmpeg",
  "ffmpeg_version": """$FFMPEG_VER""",
  "input": """$INPUT_DESC""",
  "fps": $FPS,
  "output": "$SLUG.mp4",
  "width": $W, "height": $H, "duration_seconds": $DUR,
  "size_bytes": $SIZE, "sha256": "$SHA",
  "thumbnail": "$SLUG-thumb.jpg",
  "audio": "included" if """$AUDIO""" else "silent (default)",
}
open(sys.argv[1], "w").write(json.dumps(manifest, indent=2) + "\n")
EOF

echo "proof delivered -> $OUT_DIR/$SLUG.mp4 (${W}x${H}, ${DUR}s, ${SIZE} bytes)"
echo "manifest -> $OUT_DIR/delivery.json"
