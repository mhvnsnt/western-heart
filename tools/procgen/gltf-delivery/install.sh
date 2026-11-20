#!/usr/bin/env bash
# WH glTF delivery toolchain installer.
# Installs: gltfpack (zeux/meshoptimizer, MIT) + @gltf-transform/cli (donmccurdy, MIT)
# into tools/procgen/gltf-delivery/bin/ (repo-local, no sudo, no global npm).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$HERE/bin"
mkdir -p "$BIN"

echo "==> gltfpack (meshoptimizer)"
if [ ! -x "$BIN/gltfpack" ]; then
  TMP="$(mktemp -d)"
  gh release download -R zeux/meshoptimizer --pattern 'gltfpack-ubuntu.zip' -D "$TMP"
  unzip -o -q "$TMP/gltfpack-ubuntu.zip" -d "$TMP"
  # zip contains a versioned dir; find the binary
  find "$TMP" -name gltfpack -type f -exec cp {} "$BIN/gltfpack" \;
  chmod +x "$BIN/gltfpack"
  rm -rf "$TMP"
fi
"$BIN/gltfpack" -v 2>&1 | head -1

echo "==> @gltf-transform/cli"
if [ ! -x "$BIN/gltf-transform" ]; then
  # local npm install inside the tool dir (no -g, no sudo)
  (cd "$HERE" && npm install --no-audit --no-fund "@gltf-transform/cli@4.5.1")
  ln -sf "$HERE/node_modules/.bin/gltf-transform" "$BIN/gltf-transform"
fi
"$BIN/gltf-transform" --version

echo "OK: toolchain ready in $BIN"
