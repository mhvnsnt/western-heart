#!/bin/bash
# check-blender-pin.sh — verify the Western Heart Blender pin.
#
# Pin (see docs/handoffs/BLENDER-PIN-20261102.md):
#   * Blender 5.2.3 LTS is the Western Heart Blender standard for
#     rig / render / GLB export work.
#   * MB-Lab 1.8.1 IS verified on this pin: a headless run on
#     2026-11-02 generated and GLB-exported a character on Blender
#     5.2.3 (see docs/handoffs/BLENDER-PIN-20261102.md for the log,
#     sizes and SHA). tools/mb-lab/README.md still lists the older
#     4.0.2 pipeline standard as previously verified; this pin adds
#     5.2.3, it does not erase the 4.0.2 history.
#
# Usage:
#   BLENDER=/path/to/blender bash tools/blender/check-blender-pin.sh
#   bash tools/blender/check-blender-pin.sh          # auto-detect
#   MBLAB_DIR=/path/to/MB-Lab bash tools/blender/check-blender-pin.sh
#
# No network, no secrets, no writes outside a temp probe dir. Exit 0
# only when the detected Blender reports exactly 5.2.3 LTS.
set -euo pipefail

PIN="5.2.3"
BLENDER="${BLENDER:-}"

# $HOME is deliberately set to /tmp for Blender config writes (home quota),
# so also resolve the real user home from the passwd entry for detection.
REAL_HOME="$(getent passwd "$(id -un)" 2>/dev/null | cut -d: -f6 || true)"
if [ -z "$BLENDER" ]; then
  for cand in \
    "$HOME/workspace/tools-industry/blender-5.2.3-linux-x64/blender" \
    "$REAL_HOME/workspace/tools-industry/blender-5.2.3-linux-x64/blender" \
    "$HOME/workspace/tools/blender/blender-5.2.3-linux-x64/blender" \
    "$REAL_HOME/workspace/tools/blender/blender-5.2.3-linux-x64/blender" \
    /home/*/workspace/tools-industry/blender-5.2.3-linux-x64/blender \
    "$(command -v blender || true)"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then BLENDER="$cand"; break; fi
  done
fi

if [ -z "$BLENDER" ] || [ ! -x "$BLENDER" ]; then
  echo "FAIL: no Blender binary found. Set BLENDER=/path/to/blender (5.2.3 LTS)."
  echo "  Expected location on this VM: ~/workspace/tools-industry/blender-5.2.3-linux-x64/blender"
  exit 1
fi

# HOME=/tmp avoids the home-disk quota that blocked Blender config writes.
VERSION_OUT="$(HOME=/tmp "$BLENDER" --version 2>&1 | head -n 1)"
echo "blender: $BLENDER"
echo "version: $VERSION_OUT"

if ! printf '%s\n' "$VERSION_OUT" | grep -q "Blender $PIN"; then
  echo "FAIL: expected Blender $PIN LTS, got: $VERSION_OUT"
  exit 1
fi
echo "PASS: Blender $PIN LTS pin verified (CPU-only on this VM; no GPU required for the check)."

if [ -n "${MBLAB_DIR:-}" ]; then
  if [ -f "$MBLAB_DIR/__init__.py" ]; then
    echo "mblab: $MBLAB_DIR/__init__.py present"
    grep -m1 '"blender"' "$MBLAB_DIR/__init__.py" || true
    echo "NOTE: MB-Lab presence is not a compatibility verdict — see docs/handoffs/BLENDER-PIN-20261102.md."
  else
    echo "WARN: MBLAB_DIR set but $MBLAB_DIR/__init__.py missing (fetch with: bash tools/mb-lab/fetch-mb-lab.sh)"
  fi
fi
