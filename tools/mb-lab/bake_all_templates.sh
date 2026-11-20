#!/bin/bash
# bake_all_templates.sh — re-bake every creation-suite template body with real
# morph targets, then pack it for the phone budget, into
# customization/templates/meshes/<id>.glb.
#
#   bash tools/mb-lab/bake_all_templates.sh [template-id ...]
#
# Env:
#   BLENDER    blender binary (default: blender on PATH; 4.3.2 verified headless)
#   MBLAB_DIR  MB-Lab 1.8.1 checkout (default tools/mb-lab/vendor/MB-Lab;
#              fetch with: bash tools/mb-lab/fetch-mb-lab.sh)
#   GLTFPACK   gltfpack command (default: npx -y gltfpack@0.24.0)
#   WORK       scratch dir for the unpacked bakes + reports (default /tmp/wh-morph-bake)
#
# Pack flags: -cc (meshopt, decoded by three/addons/libs/meshopt_decoder.js),
# -kn -km -ke (keep node / material names and the targetNames extras the suite
# keys sliders on), -vp 16 (16-bit positions: face targets are 0.5-10 mm, 14-bit
# lost up to 11% of the smallest ones). No simplification, no texture re-encode
# (the bake already writes JPEG colour maps).
set -euo pipefail
cd "$(dirname "$0")/../.."
BLENDER="${BLENDER:-blender}"
MBLAB_DIR="${MBLAB_DIR:-tools/mb-lab/vendor/MB-Lab}"
GLTFPACK="${GLTFPACK:-npx -y gltfpack@0.24.0}"
WORK="${WORK:-/tmp/wh-morph-bake}"
mkdir -p "$WORK"
IDS=("$@")
if [ ${#IDS[@]} -eq 0 ]; then
  mapfile -t IDS < <(python3 -c "import json;[print(t['id']) for t in json.load(open('customization/templates/body-templates.json'))['templates']]")
fi
for id in "${IDS[@]}"; do
  echo "==> $id"
  "$BLENDER" -b --factory-startup --python tools/mb-lab/bake_morph_templates.py -- \
    --template "$id" --out "$WORK/$id.raw.glb" --mblab-dir "$MBLAB_DIR" \
    --report "$WORK/$id.report.json" 2>&1 | grep -E '^\[bake\]|Error|Traceback' || true
  [ -s "$WORK/$id.raw.glb" ] || { echo "!! bake failed for $id"; exit 1; }
  $GLTFPACK -i "$WORK/$id.raw.glb" -o "customization/templates/meshes/$id.glb" -cc -kn -km -ke -vp 16
  node tools/mb-lab/morph_glb_report.mjs "customization/templates/meshes/$id.glb" --json "$WORK/$id.packed.json"
done
