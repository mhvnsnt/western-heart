#!/bin/bash
# fetch-mb-lab.sh — fetch MB-Lab on demand. MB-Lab is NEVER committed to git
# (hundreds of MB with the humanoid library). This script IS the install.
#
# Usage: bash tools/mb-lab/fetch-mb-lab.sh [dest-dir]
#   default dest: <this-dir>/vendor
#
# What it does:
#   1. Shallow-clones animate1978/MB-Lab at the pinned tag (Blender 4.0+ line).
#   2. Verifies the checkout (addon __init__.py + humanoid library present).
#   3. Prints the Blender registration path for headless runs.
#
# READ FIRST: tools/mb-lab/README.md (license: GPL-3.0 code, AGPL-3.0 database).
set -euo pipefail

MBLAB_TAG="${MBLAB_TAG:-v1.8.1}"
MBLAB_REPO="https://github.com/animate1978/MB-Lab.git"
DEST="${1:-$(dirname "$0")/vendor}"

echo "==> MB-Lab fetch (tag ${MBLAB_TAG}) -> ${DEST}"
mkdir -p "$DEST"

if [ -f "$DEST/MB-Lab/__init__.py" ]; then
  INSTALLED_TAG="$(git -C "$DEST/MB-Lab" describe --tags --exact-match 2>/dev/null || echo unknown)"
  if [ "$INSTALLED_TAG" = "$MBLAB_TAG" ]; then
    echo "==> MB-Lab ${MBLAB_TAG} already present, skipping download"
  else
    echo "==> different version present (${INSTALLED_TAG}), re-fetching ${MBLAB_TAG}"
    rm -rf "$DEST/MB-Lab"
  fi
fi

if [ ! -f "$DEST/MB-Lab/__init__.py" ]; then
  echo "==> cloning (shallow, tag ${MBLAB_TAG}) — this is ~200MB, one time..."
  git clone --depth 1 --branch "$MBLAB_TAG" "$MBLAB_REPO" "$DEST/MB-Lab"
fi

# verify
[ -f "$DEST/MB-Lab/__init__.py" ] || { echo "!! missing __init__.py"; exit 1; }
[ -f "$DEST/MB-Lab/data/humanoid_library.blend" ] || { echo "!! missing humanoid_library.blend"; exit 1; }
echo "==> verified: addon + humanoid library present"

BLENDER="${BLENDER:-$HOME/workspace/tools/blender/blender-4.0.2-linux-x64/blender}"
if [ -x "$BLENDER" ]; then
  echo "==> Blender 4.0.2 found: $BLENDER"
else
  echo "!! WARNING: Blender 4.0.2 not at $BLENDER"
  echo "   install it with: bash tools/setup/setup_toolchain.sh"
fi

echo "==> done. Headless run:"
echo "    blender -b --python tools/mb-lab/run_mblab_job.py -- --spec <spec.json> --out <file.glb>"
echo "    addon path for Blender: $DEST/MB-Lab"
