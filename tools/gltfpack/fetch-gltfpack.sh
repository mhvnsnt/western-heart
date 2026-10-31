#!/bin/bash
# fetch-gltfpack.sh — build (or fetch) meshoptimizer's gltfpack on demand.
# The binary is NEVER committed. This script IS the install.
# Usage: bash tools/gltfpack/fetch-gltfpack.sh [dest-dir]
set -euo pipefail
PIN="${GLTFPACK_PIN:-v0.22}"   # upstream tags are vX.Y (v0.22.0 does not exist)
DEST="${1:-$(dirname "$0")/vendor}"
mkdir -p "$DEST"
if [ -x "$DEST/gltfpack" ]; then
  echo "==> gltfpack already present at $DEST/gltfpack"
  "$DEST/gltfpack" -version 2>/dev/null | head -1 || true
  exit 0
fi
echo "==> building gltfpack ${PIN} (meshoptimizer)..."
if command -v cmake >/dev/null 2>&1 && command -v g++ >/dev/null 2>&1; then
  SRC="$DEST/src"
  [ -d "$SRC/.git" ] || git clone --depth 1 --branch "$PIN" https://github.com/zeux/meshoptimizer.git "$SRC"
  cmake -S "$SRC" -B "$SRC/build" -DCMAKE_BUILD_TYPE=Release -DMESHOPT_BUILD_GLTFPACK=ON >/dev/null
  cmake --build "$SRC/build" --target gltfpack -j"$(nproc)" >/dev/null
  cp "$SRC/build/gltfpack" "$DEST/gltfpack"
else
  echo "!! no cmake/g++ — downloading release binary instead"
  curl -sSL --retry 3 -o "$DEST/gltfpack.zip" \
    "https://github.com/zeux/meshoptimizer/releases/download/${PIN}/gltfpack-${PIN}-linux.tar.gz"
  tar xzf "$DEST/gltfpack.zip" -C "$DEST"
fi
chmod +x "$DEST/gltfpack"
"$DEST/gltfpack" -version 2>/dev/null | head -1 || echo "==> gltfpack ready"
