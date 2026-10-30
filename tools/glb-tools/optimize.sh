#!/bin/bash
# WH GLB pipeline — validate, then optimize. Wiring target: tools/glb-tools/.
# Order is load-bearing: gltfpack on an invalid GLB fails cryptically
# ("buffer too short"); the validator names the actual broken accessor.
# Proven 2026-10-24 on probe/server-gnm.glb (1,424,252 bytes):
#   gltfpack  -> 570,760 bytes (-60%)
#   gltf-transform optimize (meshopt) -> 148,900 bytes (-89.5%)
# Usage: ./optimize.sh <in.glb> <outdir>
set -e
cd "$(dirname "$0")"
IN="$1"; OUTDIR="${2:-./out}"; mkdir -p "$OUTDIR"
BASE=$(basename "$IN" .glb)
echo "--- 1. validate (fail = stop, fix the source export) ---"
node validate.mjs "$IN"
echo "--- 2. gltfpack (geometry + cache optimization) ---"
./node_modules/.bin/gltfpack -i "$IN" -o "$OUTDIR/$BASE.packed.glb"
echo "--- 3. gltf-transform optimize (meshopt compression) ---"
./node_modules/.bin/gltf-transform optimize "$IN" "$OUTDIR/$BASE.opt.glb"
ls -la "$IN" "$OUTDIR/$BASE.packed.glb" "$OUTDIR/$BASE.opt.glb"
echo "NOTE: ship the .opt.glb only if the game's loader supports EXT_meshopt_compression;"
echo "three.js does (with meshopt decoder). Keep the uncompressed original."
