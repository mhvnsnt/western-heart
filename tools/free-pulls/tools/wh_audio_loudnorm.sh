#!/usr/bin/env bash
# WH audio pipeline: loudnorm to -14 LUFS (streaming-style target for web game
# music/SFX previews) + WAV -> Opus, with before/after size report.
# Usage: ./wh_audio_loudnorm.sh INPUT.wav [OUTPUT.opus]
#   INPUT must be a WAV (or any ffmpeg-decodable audio). No copyrighted audio
#   is bundled; generate a test tone with:
#     ffmpeg -f lavfi -i "sine=frequency=440:duration=3" test_tone.wav
# Two-pass loudnorm is used (measured values feed the second pass), which is
# the correct loudnorm workflow; single-pass with linear=true is NOT used here
# because it can clip on loud material.
set -euo pipefail
IN="${1:?usage: $0 INPUT.wav [OUTPUT.opus]}"
OUT="${2:-${IN%.*}_loudnorm.opus}"
TMPDIR_WORK="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_WORK"' EXIT
echo "== input =="
ls -l "$IN"
ffprobe -hide_banner "$IN" 2>&1 | grep -E 'Duration|Audio:' || true
echo "== pass 1: measure =="
ffmpeg -hide_banner -i "$IN" -vn -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | sed -n '/Parsed_loudnorm/,/}/p' | tee "$TMPDIR_WORK/measured.json"
# Extract measured values with python3 (no jq dependency).
read -r M_I M_TP M_LRA M_THR M_OFF < <(python3 - "$TMPDIR_WORK/measured.json" <<'PY'
import json, re, sys
txt = open(sys.argv[1]).read()
m = re.search(r'\{.*\}', txt, re.S)
d = json.loads(m.group(0))
print(d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"], d["target_offset"])
PY
)
echo "measured: I=$M_I TP=$M_TP LRA=$M_LRA thresh=$M_THR offset=$M_OFF"
echo "== pass 2: normalize + encode Opus =="
ffmpeg -y -hide_banner -i "$IN" -vn \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$M_I:measured_TP=$M_TP:measured_LRA=$M_LRA:measured_thresh=$M_THR:offset=$M_OFF:linear=false" \
  -c:a libopus -b:a 96k "$OUT"
echo "== output =="
ls -l "$OUT"
ffprobe -hide_banner "$OUT" 2>&1 | grep -E 'Duration|Audio:' || true
python3 - "$IN" "$OUT" <<'PY'
import os, sys
a, b = os.path.getsize(sys.argv[1]), os.path.getsize(sys.argv[2])
print(f"before: {a} bytes | after: {b} bytes | ratio: {b/a:.3f} | saved: {100*(1-b/a):.1f}%")
PY
