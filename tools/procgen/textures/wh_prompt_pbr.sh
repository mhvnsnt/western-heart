#!/usr/bin/env bash
# wh_prompt_pbr.sh — text prompt -> tileable PBR set via Pollinations + wh_seamless_pbr.py.
# Mirrors the TEXTtoPBR (MIT) pipeline: Pollinations.AI (Flux) albedo, local processing.
# Usage: wh_prompt_pbr.sh "mossy stone wall" OUTDIR/ [--size 1024]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT="${1:?usage: wh_prompt_pbr.sh \"prompt\" OUTDIR/ [--size N]}"
OUTDIR="$2"
SIZE="1024"
[ "${3:-}" = "--size" ] && SIZE="$4"
mkdir -p "$OUTDIR"

# Pollinations image API (zero-signup, already our tested backend).
# Enhance prompt for texture use: seamlessable, top-down, no objects.
Q="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" \
  "seamless texture, top-down flat surface, $PROMPT, game PBR albedo, no objects, no text, uniform lighting")"
curl -sL --retry 3 --max-time 120 \
  "https://image.pollinations.ai/prompt/${Q}?width=${SIZE}&height=${SIZE}&nologo=true&model=flux" \
  -o "$OUTDIR/_albedo_raw.png"
[ -s "$OUTDIR/_albedo_raw.png" ] || { echo "Pollinations fetch failed"; exit 1; }

python3 "$HERE/wh_seamless_pbr.py" "$OUTDIR/_albedo_raw.png" "$OUTDIR" --size "$SIZE"
rm -f "$OUTDIR/_albedo_raw.png"
echo "PBR set for '$PROMPT' -> $OUTDIR/"
