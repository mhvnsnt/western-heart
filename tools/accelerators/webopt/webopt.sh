#!/usr/bin/env bash
# tools/accelerators/webopt/webopt.sh — STAGE 5: WEB OPTIMIZE.
#
# Batch-optimize a whole directory of GLBs for the web, overnight:
#   gltfpack -cc  -> meshopt compression (vertex/index buffer codecs)
#   gltf-transform -> dedup, prune, weld, optional KTX2 texture compression
#
# Both tools are fetched on demand into ./bin — never vendored.
# Output requires EXT_meshopt_compression on the loader side (three.js r122+
# with the meshopt decoder, Babylon.js 5.0+).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"
GLTFPACK="$BIN_DIR/gltfpack"
GTF_NODE="$BIN_DIR/gltf-node"
GTF="$GTF_NODE/node_modules/.bin/gltf-transform"

GLTFPACK_VER="v1.3"
GLTFPACK_URL="https://github.com/zeux/meshoptimizer/releases/download/${GLTFPACK_VER}/gltfpack-ubuntu.zip"
GTF_CLI_VER="4.1.1"   # matches the @gltf-transform 4.1.x line in tools/setup/setup_toolchain.sh

cmd_install() {
  mkdir -p "$BIN_DIR"
  if [ -x "$GLTFPACK" ]; then echo "gltfpack already at $GLTFPACK";
  else
    echo "Fetching gltfpack ${GLTFPACK_VER} (linux)..."
    curl -fL --max-time 120 -o /tmp/gltfpack.zip "$GLTFPACK_URL"
    python3 -c "import zipfile; zipfile.ZipFile('/tmp/gltfpack.zip').extractall('$BIN_DIR')"
    chmod +x "$GLTFPACK"; rm -f /tmp/gltfpack.zip
    echo "Installed: $GLTFPACK"
  fi
  if [ -x "$GTF" ]; then echo "gltf-transform already at $GTF";
  else
    echo "Installing @gltf-transform/cli@${GTF_CLI_VER} (one-time npm)..."
    mkdir -p "$GTF_NODE" && ( cd "$GTF_NODE" && npm init -y >/dev/null 2>&1
      npm i --no-audit --no-fund "@gltf-transform/cli@${GTF_CLI_VER}" )
    echo "Installed: $GTF"
  fi
  echo "stage-5 tools ready under $BIN_DIR"
}

cmd_optimize() { # optimize <indir> <outdir> [--ktx2] [--no-meshopt] [--force]
  local indir=$1 outdir=$2; shift 2
  local ktx2=0 meshopt=1 force=0
  while [ $# -gt 0 ]; do case "$1" in
    --ktx2) ktx2=1; shift;;
    --no-meshopt) meshopt=0; shift;;
    --force) force=1; shift;;
    *) echo "unknown: $1"; exit 1;;
  esac; done
  [ -d "$indir" ] || { echo "indir not found: $indir"; exit 1; }
  [ -x "$GLTFPACK" ] || { echo "run: $0 install"; exit 1; }
  if [ -e "$outdir" ] && [ -n "$(ls -A "$outdir" 2>/dev/null)" ] && [ "$force" != 1 ]; then
    echo "refusing: output dir $outdir is not empty (use --force)"; exit 1
  fi
  mkdir -p "$outdir"
  local n=0 ok=0 fail=0
  shopt -s nullglob nocaseglob
  for src in "$indir"/*.glb; do
    n=$((n+1))
    local base; base="$(basename "$src")"
    local tmp="$outdir/.tmp-$base" dest="$outdir/$base"
    local s0; s0=$(stat -c%s "$src")
    if [ "$meshopt" = 1 ]; then
      "$GLTFPACK" -i "$src" -o "$tmp" -cc >"$outdir/.$base.log" 2>&1 || { fail=$((fail+1)); echo "FAIL(glbpack) $base"; continue; }
    else
      cp "$src" "$tmp"
    fi
    if [ "$ktx2" = 1 ]; then
      [ -x "$GTF" ] || { echo "run: $0 install (need gltf-transform for --ktx2)"; exit 1; }
      "$GTF" etc1s "$tmp" "$dest" >>"$outdir/.$base.log" 2>&1 || { fail=$((fail+1)); echo "FAIL(ktx2) $base"; rm -f "$tmp"; continue; }
      rm -f "$tmp"
    else
      mv "$tmp" "$dest"
    fi
    local s1; s1=$(stat -c%s "$dest")
    local pct; pct=$(awk "BEGIN{printf \"%.1f\", $s1/$s0*100}")
    echo "OK $base: $s0 -> $s1 bytes (${pct}% of original)"
    ok=$((ok+1))
  done
  shopt -u nullglob nocaseglob
  [ "$n" -gt 0 ] || { echo "no .glb files in $indir"; exit 1; }
  echo "==> web-optimize: $ok/$n ok, $fail failed -> $outdir"
  [ "$fail" -gt 0 ] && return 1 || return 0
}

case "${1:-}" in
  install) cmd_install ;;
  optimize) shift; cmd_optimize "$@" ;;
  *) echo "usage: $0 install | optimize <indir> <outdir> [--ktx2] [--no-meshopt] [--force]"; exit 1 ;;
esac
