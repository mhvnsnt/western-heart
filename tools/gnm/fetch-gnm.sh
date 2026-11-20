#!/bin/bash
# fetch-gnm.sh — fetch Google's GNM on demand. Model weights are large and
# NEVER committed to git. This script IS the install.
#
# Usage: bash tools/gnm/fetch-gnm.sh [dest-dir]
#   default dest: <this-dir>/vendor
#
# READ FIRST: tools/gnm/README.md (Apache-2.0 — verified).
set -euo pipefail

# Pinned commit of google/GNM. Bump deliberately, then re-run the bake test:
#   python3 tools/gnm/run_gnm_job.py --spec tools/gnm/specs/face-determined.json --out /tmp/gnm-verify.glb
GNM_PIN="${GNM_PIN:-main}"
GNM_REPO="https://github.com/google/GNM.git"
DEST="${1:-$(dirname "$0")/vendor}"

echo "==> GNM fetch (pin ${GNM_PIN}) -> ${DEST}"
mkdir -p "$DEST"

if [ -f "$DEST/GNM/gnm/__init__.py" ] || [ -f "$DEST/GNM/README.md" ]; then
  echo "==> GNM already present at $DEST/GNM, skipping clone"
else
  echo "==> cloning google/GNM ..."
  git clone --depth 1 --branch "$GNM_PIN" "$GNM_REPO" "$DEST/GNM"
fi

[ -d "$DEST/GNM/gnm" ] || { echo "!! missing $DEST/GNM/gnm package"; exit 1; }
[ -f "$DEST/GNM/LICENSE" ] || { echo "!! missing LICENSE"; exit 1; }
grep -q "Apache" "$DEST/GNM/LICENSE" && echo "==> license check: Apache-2.0 confirmed" \
  || { echo "!! LICENSE is not Apache-2.0 — STOP, re-verify"; exit 1; }

echo "==> pulling released model assets (see $DEST/GNM/assets/)..."
if [ -d "$DEST/GNM/assets" ] && [ -n "$(ls -A "$DEST/GNM/assets" 2>/dev/null)" ]; then
  echo "==> assets present"
else
  echo "!! WARNING: no model assets found in $DEST/GNM/assets."
  echo "   Follow the download links in $DEST/GNM/README.md, place the files"
  echo "   under $DEST/GNM/assets/, and re-run this script."
fi

python3 -c "import numpy" 2>/dev/null || { echo "!! numpy missing: pip install numpy"; exit 1; }

# Minimal runtime deps for the numpy-backend headless bake
# (run_gnm_job.py). Full GNM dev deps (tensorflow, jax, torch, notebook...)
# are NOT needed for baking heads. Installs are best-effort: on PEP-668
# systems (Debian/Ubuntu) add --break-system-packages or use a venv.
echo "==> installing minimal GNM runtime deps (absl-py etils opt-einsum scipy tqdm)..."
if python3 -c "import absl, etils, opt_einsum, scipy, tqdm" 2>/dev/null; then
  echo "==> runtime deps already present"
elif pip install absl-py etils opt-einsum scipy tqdm 2>/dev/null; then
  echo "==> runtime deps installed"
else
  echo "!! WARNING: could not pip-install runtime deps (PEP-668 or no network)."
  echo "   Run manually: pip install --break-system-packages absl-py etils opt-einsum scipy tqdm"
  echo "   The bake path needs them; semantic identity sampling additionally needs tensorflow."
fi

echo "==> done. Headless run:"
echo "    python3 tools/gnm/run_gnm_job.py --spec <spec.json> --out <head.glb>"
