#!/usr/bin/env bash
# wh_optimize_glb.sh — WH web-delivery optimizer.
#   fighter.glb -> fighter.web.glb  (meshopt compression + quantization + dedup)
# Usage: wh_optimize_glb.sh INPUT.glb [OUTPUT.web.glb] [--texture-webp]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HERE/bin"
IN="${1:?usage: wh_optimize_glb.sh INPUT.glb [OUTPUT.web.glb] [--texture-webp]}"
OUT="${2:-${IN%.glb}.web.glb}"
MODE="${3:-}"

[ -x "$BIN/gltfpack" ] || { echo "run install.sh first"; exit 1; }

# Stage 1: gltfpack — meshopt + quantize + simplify-safe defaults.
# -cc            : EXT_meshopt_compression
# -tc            : keep texture references (we handle textures in stage 2)
# -kn -ke        : keep node names + extras (WH tooling reads them)
"$BIN/gltfpack" -i "$IN" -o "$OUT" -cc -kn -ke

# Stage 2 (optional): WebP texture transcode via glTF-Transform (KHR EXT_texture_webp).
if [ "$MODE" = "--texture-webp" ]; then
  [ -x "$BIN/gltf-transform" ] || { echo "run install.sh first"; exit 1; }
  "$BIN/gltf-transform" webp --slots 'baseColor,emissive' "$OUT" "$OUT"
fi

echo "--- sizes ---"
du -h "$IN" "$OUT"
echo "--- inspect ---"
"$BIN/gltf-transform" inspect "$OUT" 2>/dev/null | head -20 || true
