#!/usr/bin/env bash
# tools/accelerators/cleanup/cleanup-batch.sh — STAGE 4: CLEANUP.
#
# Overnight batch: weld doubles, delete loose geometry, recalculate normals,
# decimate, (optionally) triangulate — a whole directory, headless Blender.
# Everything here is a native Blender op; nothing exotic, nothing hand-tuned.
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
usage: $0 <indir> <outdir> [--decimate 0.5] [--merge-dist 0.0001]
                          [--triangulate] [--no-normals] [--force]

  Clean every GLB/FBX in <indir> -> <outdir>.
  --decimate 0 disables decimation.
EOF
}

[ $# -ge 2 ] || { usage; exit 1; }
indir=$1 outdir=$2; shift 2
extra=() force=0
while [ $# -gt 0 ]; do case "$1" in
  --decimate|--merge-dist) extra+=("$1" "$2"); shift 2;;
  --triangulate|--no-normals) extra+=("$1"); shift;;
  --force) force=1; shift;;
  *) echo "unknown: $1"; usage; exit 1;;
esac; done

[ -d "$indir" ] || { echo "indir not found: $indir"; exit 1; }
blender=$(find_blender) || { echo "Blender 4.0.2 not found. Run: bash $REPO_ROOT/tools/setup/setup_toolchain.sh"; exit 1; }
if [ -e "$outdir" ] && [ -n "$(ls -A "$outdir" 2>/dev/null)" ] && [ "$force" != 1 ]; then
  echo "refusing: output dir $outdir is not empty (use --force)"; exit 1
fi
mkdir -p "$outdir"

echo "==> stage 4 cleanup: $indir -> $outdir (blender: $blender)"
xvfb-run -a "$blender" -b --python "$SCRIPT_DIR/cleanup-batch.py" -- \
  --indir "$indir" --outdir "$outdir" "${extra[@]}" 2>&1 | tee "$outdir/cleanup-batch.log"
echo "==> done. log: $outdir/cleanup-batch.log"
