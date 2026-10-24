#!/usr/bin/env bash
# face_cone_batch.sh FILE...   (run from repo root, sparse worktree OK)
# For each GLB: materialise it, weight_audit.py fix in place, verify mesh counts
# unchanged (no content cut), re-audit, render jab/uppercut proof into
# docs/proof/face-cone/, append residuals to tools/rig/face_cone_baseline.txt.
set -u
PORT=${PORT:-8765}
(python3 -m http.server "$PORT" >/dev/null 2>&1 &) ; sleep 1
for f in "$@"; do
  git sparse-checkout add "/$f" 2>/dev/null; git checkout -- "$f" 2>/dev/null
  [ -f "$f" ] || { echo "MISSING $f"; continue; }
  cp "$f" /tmp/fc_in.glb
  python3 tools/rig/weight_audit.py fix /tmp/fc_in.glb /tmp/fc_out.glb >/tmp/fc_fix.json 2>&1 || { echo "FIXERR $f"; continue; }
  python3 - "$f" <<'PY' || { echo "COUNTMISMATCH $1"; exit 1; }
import sys,os; sys.path.insert(0,'tools/rig'); from _glb_common import Glb
a,b=Glb('/tmp/fc_in.glb'),Glb('/tmp/fc_out.glb')
ca=[(x.get('count'),x.get('type')) for x in a.g['accessors']]
cb=[(x.get('count'),x.get('type')) for x in b.g['accessors']]
sys.exit(0 if ca==cb else 1)
PY
  cp /tmp/fc_out.glb "$f"
  n=$(python3 tools/rig/weight_audit.py audit "$f" | awk '/^(ok|FAIL)/{print $2; exit}')
  b=$(echo "$f" | tr '/' '_' | sed 's/\.glb$//')
  POSES="jab uppercut" PORT=$PORT bash tools/rig/face_proof.sh "$f" "docs/proof/face-cone/$b" || true
  if [ "${n:-0}" -gt 0 ]; then grep -v "^$f	" tools/rig/face_cone_baseline.txt 2>/dev/null > /tmp/bl; printf '%s\t%s\n' "$f" "$n" >> /tmp/bl; sort /tmp/bl > tools/rig/face_cone_baseline.txt; fi
  echo "DONE $f residual=${n:-?}"
done
rm -f /tmp/fc_in.glb /tmp/fc_out.glb
