#!/usr/bin/env bash
# Western Heart asset pipeline — glTF/GLB optimize + LOD batch step.
# Tool: gltfpack 1.3 (meshoptimizer, MIT) — pulled 2026-10-24, verified on real WH assets.
#   hand stance GLB: 158,884 -> 72,812 bytes (-54%), nodes 95->95, animations 1->1, skins 1->1
#   jungle outpost: 1,669,744 -> 680,460 bytes (-59%), materials 15->15, meshes merged 203->111
# Usage:
#   ./wh-asset-pipeline.sh <input-dir-or-file> <output-dir> [simplify-ratio]
#   simplify-ratio: 0 = no simplification (default, safe for skinned rigs).
#                   0.5 = LOD1-style 50% triangle target (stages/props ONLY — never skinned fighters
#                   without an owner eye-check; simplification can change silhouette).
# Rules (standing):
#   - ALWAYS -kn (keep node names): bone/node names are load-bearing for fighter rigs.
#   - NEVER -c (meshopt compression) unless the game loader sets MeshoptDecoder first;
#     default output loads in any three.js GLTFLoader (r111+ KHR_mesh_quantization).
#   - NEVER overwrite source: outputs go to a separate dir; sources stay immutable.
#   - -tc (KTX2/BasisU) is opt-in per asset: requires KHR_texture_basisu loader support.
set -euo pipefail
GLTFPACK="${GLTFPACK:-$(dirname "$0")/tools/gltfpack}"
INPUT="${1:?usage: wh-asset-pipeline.sh <input> <output-dir> [simplify-ratio]}"
OUTDIR="${2:?usage: wh-asset-pipeline.sh <input> <output-dir> [simplify-ratio]}"
SI="${3:-0}"
[ -x "$GLTFPACK" ] || { echo "gltfpack not found at $GLTFPACK"; exit 1; }
mkdir -p "$OUTDIR"
REPORT="$OUTDIR/_pipeline-report.txt"
: > "$REPORT"
process_one() {
  local src="$1" base out args
  base="$(basename "$src" .glb)"
  out="$OUTDIR/${base}-opt.glb"
  args=(-i "$src" -o "$out" -kn)
  if [ "$SI" != "0" ]; then args+=(-si "$SI"); fi
  local before after
  before="$(stat -c%s "$src")"
  if "$GLTFPACK" "${args[@]}" > /dev/null 2>&1; then
    after="$(stat -c%s "$out")"
    echo "$base: $before -> $after bytes" | tee -a "$REPORT"
  else
    echo "$base: FAILED (kept source untouched)" | tee -a "$REPORT"
  fi
}
if [ -f "$INPUT" ]; then
  process_one "$INPUT"
else
  shopt -s nullglob
  for f in "$INPUT"/*.glb; do process_one "$f"; done
fi
echo "Report: $REPORT"
