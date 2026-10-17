#!/usr/bin/env bash
# wh_fetch_cc0.sh — fetch named CC0 PBR materials on demand (no bulk vendoring).
# Source: AmbientCG (ambientcg.com, CC0, no account). Verified 2026-10-16:
#   https://ambientcg.com/get?file=<ID>_2K-JPG.zip  -> 302 to signed CDN download.
# Usage: wh_fetch_cc0.sh ./assets/pbr/ Asphalt013 MetalPlates012
set -euo pipefail
OUTDIR="$1"; shift
mkdir -p "$OUTDIR"
for id in "$@"; do
  echo "==> $id"
  zip="$OUTDIR/${id}_2K-JPG.zip"
  curl -sL --retry 2 --max-time 120 "https://ambientcg.com/get?file=${id}_2K-JPG.zip" -o "$zip"
  if [ "$(stat -c%s "$zip")" -gt 10000 ] && unzip -l "$zip" >/dev/null 2>&1; then
    mkdir -p "$OUTDIR/$id" && unzip -o -q "$zip" -d "$OUTDIR/$id"
    echo "    -> $OUTDIR/$id/"
  else
    echo "    !! download failed for $id (check the ID at https://ambientcg.com)"
  fi
  rm -f "$zip"
done
echo "CC0: free for any use, no attribution required (logged anyway in PULL-LOG.md)."
