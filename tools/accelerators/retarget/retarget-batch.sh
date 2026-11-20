#!/usr/bin/env bash
# tools/accelerators/retarget/retarget-batch.sh — STAGE 2: RETARGET.
#
# Batch-retarget a whole directory of source animations (FBX/BVH — whatever
# tools/anim-retarget/retarget_blender.py accepts) onto one Western
# Heart-rigged target GLB, headless in Blender.
#
# This stage CONSUMES the retargeting lane's work — it does NOT define bone
# maps. The bone map lives in tools/anim-retarget/bone_maps/ and the retarget
# math lives in tools/anim-retarget/retarget_blender.py (rest-relative delta
# retarget). If the Tekken bone-map hasn't landed yet, this script FAILS
# LOUDLY and tells you who owns it. It never silently substitutes a map.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RETARGET_PY="$REPO_ROOT/tools/anim-retarget/retarget_blender.py"
BONEMAP_DIR="$REPO_ROOT/tools/anim-retarget/bone_maps"
DEFAULT_BONEMAP="$BONEMAP_DIR/tekken_to_wh.json"   # owned by the retargeting lane

find_blender() {
  local prefix="${ACCEL_TOOLCHAIN:-$HOME/workspace/tools}"
  local b="$prefix/blender/blender-4.0.2-linux-x64/blender"
  if [ -x "$b" ]; then echo "$b"; return 0; fi
  if command -v blender >/dev/null 2>&1; then command -v blender; return 0; fi
  return 1
}

usage() {
  cat <<EOF
usage: $0 <animdir> <target_glb> <outdir> [--bonemap PATH] [--fps 30] [--in-place] [--force]

  Batch-retarget every animation in <animdir> onto <target_glb> (WH-rigged).
  Default bone map: tools/anim-retarget/bone_maps/tekken_to_wh.json
  (the retargeting lane's artifact — this script consumes it, never defines it).
EOF
}

main() {
  [ $# -ge 3 ] || { usage; exit 1; }
  local animdir=$1 target=$2 out=$3; shift 3
  local bonemap="$DEFAULT_BONEMAP" fps=30 inplace="" force=0
  while [ $# -gt 0 ]; do case "$1" in
    --bonemap) bonemap=$2; shift 2;;
    --fps) fps=$2; shift 2;;
    --in-place) inplace="--in-place"; shift;;
    --force) force=1; shift;;
    *) echo "unknown: $1"; usage; exit 1;;
  esac; done

  [ -d "$animdir" ] || { echo "animdir not found: $animdir"; exit 1; }
  [ -f "$target" ] || { echo "target GLB not found: $target"; exit 1; }
  [ -f "$RETARGET_PY" ] || { echo "missing: $RETARGET_PY (retargeting lane's script)"; exit 1; }
  if [ ! -f "$bonemap" ]; then
    cat >&2 <<EOF
ERROR: bone map not found: $bonemap
The Tekken bone-map is owned by the retargeting lane
(tools/anim-retarget/bone_maps/) and hasn't landed yet.
Either wait for the lane, or pass an explicit map you trust, e.g.:
  $0 <animdir> <target> <outdir> --bonemap $BONEMAP_DIR/mixamo_to_wh.json
EOF
    exit 1
  fi
  local blender; blender=$(find_blender) || {
    echo "Blender 4.0.2 not found. Run: bash $REPO_ROOT/tools/setup/setup_toolchain.sh"; exit 1; }

  if [ -e "$out" ] && [ -n "$(ls -A "$out" 2>/dev/null)" ] && [ "$force" != 1 ]; then
    echo "refusing: output dir $out is not empty (use --force)"; exit 1
  fi
  mkdir -p "$out"

  local n=0 ok=0 fail=0 failed_list=""
  shopt -s nullglob nocaseglob
  for src in "$animdir"/*.fbx "$animdir"/*.bvh; do
    n=$((n+1))
    local clip; clip="$(basename "$src")"; clip="${clip%.*}"
    local dest="$out/${clip}.glb"
    echo "--- [$n] $clip"
    # shellcheck disable=SC2086
    if xvfb-run -a "$blender" -b --python "$RETARGET_PY" -- \
        --source "$src" --target "$target" --out "$dest" \
        --bonemap "$bonemap" --clip-name "$clip" --fps "$fps" $inplace \
        >"$out/${clip}.log" 2>&1; then
      ok=$((ok+1))
    else
      fail=$((fail+1)); failed_list="$failed_list $clip"
      echo "  FAILED (see $out/${clip}.log)"
    fi
  done
  shopt -u nullglob nocaseglob
  [ "$n" -gt 0 ] || { echo "no animations found in $animdir"; exit 1; }
  echo "==> retargeted $ok/$n ok, $fail failed -> $out"
  [ -n "$failed_list" ] && echo "failed:$failed_list"
  [ "$fail" -gt 0 ] && return 1 || return 0
}

main "$@"
