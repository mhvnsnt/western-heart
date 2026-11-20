#!/usr/bin/env bash
# ============================================================================
# build_wasm.sh — compile AMD FEMFX to WebAssembly for the WH game runtime.
#
# Produces game/vendor/femfx/femfx.wasm.js + femfx.wasm.wasm exposing the C API
# in tools/femfx/femfx_bind.cpp (femfx_create / femfx_add_tetmesh /
# femfx_step / femfx_get_positions / femfx_apply_impulse /
# femfx_poll_fractures / femfx_destroy), consumed by game/js/femfx-adapter.js.
#
# Requires: Emscripten SDK (emsdk) on PATH (emcc).
#   git clone https://github.com/emscripten-core/emsdk.git
#   cd emsdk && ./emsdk install latest && ./emsdk activate latest
#
# FEMFX source is cloned fresh at build time (not vendored) to keep the repo
# lean; pin FEMFX_REV for reproducible builds.
# ============================================================================
set -euo pipefail

FEMFX_REPO="https://github.com/GPUOpen-Effects/FEMFX.git"
FEMFX_REV="${FEMFX_REV:-master}"   # pin to a SHA for release builds
BUILD_DIR="${BUILD_DIR:-/tmp/wh-femfx-build}"
OUT_DIR="$(cd "$(dirname "$0")/../../game/vendor/femfx" && pwd)"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> fetching FEMFX (${FEMFX_REV})"
if [ ! -d "${BUILD_DIR}/FEMFX" ]; then
  git clone --depth 1 "${FEMFX_REPO}" "${BUILD_DIR}/FEMFX"
fi
cd "${BUILD_DIR}/FEMFX"
git fetch --depth 1 origin "${FEMFX_REV}" || true
git checkout "${FEMFX_REV}" || true

echo "==> compiling with emcc"
emcc \
  -O3 \
  -I amd_femfx/inc \
  amd_femfx/src/Bvh/*.cpp \
  amd_femfx/src/Common/*.cpp \
  amd_femfx/src/ConstraintSolver/*.cpp \
  amd_femfx/src/FindContacts/*.cpp \
  amd_femfx/src/PrimitiveCollision/*.cpp \
  amd_femfx/src/Scene/*.cpp \
  amd_femfx/src/Simulation/*.cpp \
  amd_femfx/src/SparseSolvers/*.cpp \
  amd_femfx/src/Threading/*.cpp \
  "${SRC_DIR}/femfx_bind.cpp" \
  -o "${OUT_DIR}/femfx.wasm.js" \
  -s WASM=1 \
  -s MODULARIZE=1 \
  -s EXPORT_NAME=createFemfxModule \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s EXPORTED_FUNCTIONS='["_femfx_create","_femfx_add_tetmesh","_femfx_step","_femfx_get_positions","_femfx_apply_impulse","_femfx_poll_fractures","_femfx_destroy","_malloc","_free"]' \
  -s EXPORTED_RUNTIME_METHODS='["cwrap","HEAPF32","HEAPU8","HEAPU32"]' \
  -s ENVIRONMENT=web \
  -s SINGLE_FILE=0 \
  -flto

echo "==> done: ${OUT_DIR}/femfx.wasm.js"
ls -la "${OUT_DIR}/"
echo "Wire it up: game/js/femfx-adapter.js auto-loads this module when"
echo "WH_PHYSICS_BACKEND='femfx' (falls back to Jolt SoftBody if absent)."
