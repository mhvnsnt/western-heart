#!/usr/bin/env bash
# Re-author customization/templates/decal-placements.json in Blender (and optionally render proofs).
# Usage: tools/creation-suite/decals/run_author.sh [proof_dir]
# Needs: node, blender (4.3 tested; its python needs numpy for the glTF importer — see the
# sys.path line at the top of author_placements_blender.py).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
DEC=$(mktemp -d)
node tools/creation-suite/decals/decode_glb.mjs "$DEC" customization/templates/meshes/*.glb
node -e "import('./game/js/decal-layers.js').then(m=>process.stdout.write(JSON.stringify(m.BODY_REGIONS)))" > "$DEC/regions.json"
blender -b --python tools/creation-suite/decals/author_placements_blender.py -- \
  "$DEC" "$DEC/regions.json" customization/templates/decal-placements.json ${1:-}
