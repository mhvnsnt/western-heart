#!/usr/bin/env bash
# tools/accelerators/rig/rig-batch.sh — STAGE 3: RIGGING.
#
# Overnight batch: automatic bone-heat skinning for a whole directory of
# models. Each mesh gets parented to its armature with AUTOMATIC weights
# (Blender's bone heat), no GUI. This is the fast pass — the full GameRig
# pipeline (tools/auto_rig/) remains the quality path for hero characters.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

find_blender() {
  local prefix="${ACCEL_TOOLCHAIN:-$HOME/workspace/tools}"
  local b="$prefix/blender/blender-4.0.2-linux-x64/blender"
  if [ -x "$b" ]; then echo "$b"; return 0; fi
  if command -v blender >/dev/null 2>&1; then command -v blender; return 0; fi
  return 1
}

usage() {
  cat <<EOF
usage: $0 <indir> <outdir> [--reweight] [--suffix .rigged] [--force]

  Auto-weight every GLB/FBX in <indir> (bone heat) -> rigged GLBs in <outdir>.
  Files with no armature are logged and skipped. Already-parented meshes are
  kept unless --reweight is given.
EOF
}

[ $# -ge 2 ] || { usage; exit 1; }
indir=$1 outdir=$2; shift 2
extra=() force=0
while [ $# -gt 0 ]; do case "$1" in
  --reweight) extra+=(--reweight); shift;;
  --suffix) extra+=(--suffix "$2"); shift 2;;
  --force) force=1; shift;;
  *) echo "unknown: $1"; usage; exit 1;;
esac; done

[ -d "$indir" ] || { echo "indir not found: $indir"; exit 1; }
blender=$(find_blender) || { echo "Blender 4.0.2 not found. Run: bash $REPO_ROOT/tools/setup/setup_toolchain.sh"; exit 1; }
if [ -e "$outdir" ] && [ -n "$(ls -A "$outdir" 2>/dev/null)" ] && [ "$force" != 1 ]; then
  echo "refusing: output dir $outdir is not empty (use --force)"; exit 1
fi
mkdir -p "$outdir"

echo "==> stage 3 rigging: $indir -> $outdir (blender: $blender)"
xvfb-run -a "$blender" -b --python "$SCRIPT_DIR/auto-weights-batch.py" -- \
  --indir "$indir" --outdir "$outdir" "${extra[@]}" 2>&1 | tee "$outdir/rig-batch.log"
echo "==> done. log: $outdir/rig-batch.log"
