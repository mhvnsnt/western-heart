#!/bin/bash
# v71 bake driver for GitHub Actions (ubuntu-latest, 16GB RAM).
# Mirrors intake/conv7/run_chain18_mj.sh (Hara/Matara/Juniper sections) with
# the local RAM gates removed (runner has 16GB) and the pair-shoot step
# deferred (shoot_glb.py needs the local harness server; pairs are shot
# locally by the watch lane after pull-back). No Blender launched locally;
# this runs ONLY in the Actions runner. Usage: bash v71-bake-driver.sh <hara|matara|juniper>
set -u
MODEL=${1:?model required: hara|matara|juniper}
BL="$PWD/blender-5.2.4-linux-x64/blender"
IN="$PWD/inputs"
BAKE="$PWD/bake"
OUT="$PWD/out"
mkdir -p "$BAKE" "$OUT" "$OUT/glb_raw" "$OUT/final" "$OUT/bakes"
cp "$IN/bakefix.py" "$IN/export52.py" "$BAKE/"
say(){ echo "[v71-bake] $*"; }
png_nonzero(){
  python3 -c "
from PIL import Image
import numpy as np, sys
a = np.asarray(Image.open('$1').convert('RGB'))
nz = int((a.sum(2)>0).sum())
print(nz)
sys.exit(0 if nz > 0 else 1)
"
}
bake_p1(){ # mini substr mat samples
  local mini=$1 substr=$2 mat=$3 samples=$4
  local png="$BAKE/fixups/bakes/$mat.png"
  say "=== p1 $MODEL/$mat (samples $samples)"
  printf '{"blend_substr": "%s", "materials": ["%s"], "size": 1024, "samples": %s, "strip_scene": true, "inner": true, "phase": 1}' "$substr" "$mat" "$samples" > "$BAKE/bake_targets.json"
  rm -f "$png" "$BAKE/fixups/bakes/${mat}_emit.png"
  "$BL" -b "$mini" --python "$BAKE/bakefix.py" > "$OUT/bake-$mat.log" 2>&1
  local rc=$?
  grep -E "STRIP-SCENE|UV-TILES|UV-TILE-SHIFT|INNER-REWIRE|BAKED|BAKE-FAIL|BAKE-SKIP|PHASE1" "$OUT/bake-$mat.log" | tail -8
  if [ -s "$png" ] && png_nonzero "$png" > /dev/null; then say "P1-OK $mat"; return 0; fi
  say "P1-FAIL $mat rc=$rc"; return 1
}
make_mini(){ # blend substr mats-json minipath
  local blend=$1 substr=$2 mats=$3 mini=$4
  [ -s "$mini" ] && { say "MINI-SKIP (exists)"; return 0; }
  say "=== mini $MODEL"
  printf '{"blend_substr": "%s", "materials": %s, "strip_scene": true, "phase": 1, "save_mini": "%s"}' "$substr" "$mats" "$mini" > "$BAKE/bake_targets.json"
  "$BL" -b "$blend" --python "$BAKE/bakefix.py" > "$OUT/mini-$MODEL.log" 2>&1
  grep -E "STRIP-SCENE|MINI-SAVED" "$OUT/mini-$MODEL.log" | tail -4
  [ -s "$mini" ] && { say "MINI-OK $(stat -c%s "$mini")"; return 0; }
  say "MINI-FAIL"; return 1
}
bake_p2(){ # blend substr mats-json outblend
  local blend=$1 substr=$2 mats=$3 out=$4
  say "=== p2 $MODEL"
  printf '{"blend_substr": "%s", "materials": %s, "phase": 2, "save_blend": "%s"}' "$substr" "$mats" "$out" > "$BAKE/bake_targets.json"
  rm -f "$out"
  "$BL" -b "$blend" --python "$BAKE/bakefix.py" > "$OUT/bake-p2-$MODEL.log" 2>&1
  grep -E "REBUILT|EMIT-BAKE-WIRED|EMISSION-PRESERVED|PHASE2|SAVED-BLEND|P2-INCOMPLETE" "$OUT/bake-p2-$MODEL.log" | tail -12
  [ -s "$out" ] && { say "P2-OK $(stat -c%s "$out")"; return 0; }
  say "P2-FAIL"; return 1
}
export_glb(){ # baked-blend final-glb
  local baked=$1 final=$2
  say "=== export $MODEL"
  "$BL" -b "$baked" --python "$BAKE/export52.py" -- "$OUT/glb_raw/$final" - ACTIONS > "$OUT/export-$MODEL.log" 2>&1
  [ -s "$OUT/glb_raw/$final" ] && { say "EXPORT-OK $(stat -c%s "$OUT/glb_raw/$final")"; return 0; }
  say "EXPORT-FAIL"; tail -5 "$OUT/export-$MODEL.log"; return 1
}
finish_glb(){ # final-glb strip-csv
  local final=$1 strip=$2
  say "=== finish $MODEL (node rebuild + strip_vcol)"
  mkdir -p "$PWD/gt-tools"
  cp "$IN/rebuild2.mjs" "$IN/strip_vcol.mjs" "$IN/package.json" "$IN/package-lock.json" "$PWD/gt-tools/"
  ( cd "$PWD/gt-tools" && npm ci --no-audit --no-fund > "$OUT/npm-$MODEL.log" 2>&1 ) || { say "NPM-FAIL"; tail -5 "$OUT/npm-$MODEL.log"; return 1; }
  ( cd "$PWD/gt-tools" && node --stack-size=100000 rebuild2.mjs "$OUT/glb_raw/$final" "$OUT/final/$final" 1024 > "$OUT/rebuild-$MODEL.log" 2>&1 ) || { say "REBUILD-FAIL"; tail -5 "$OUT/rebuild-$MODEL.log"; return 1; }
  ( cd "$PWD/gt-tools" && node --stack-size=100000 strip_vcol.mjs "$OUT/final/$final" "$strip" > "$OUT/strip-$MODEL.log" 2>&1 ) || { say "STRIP-FAIL"; tail -5 "$OUT/strip-$MODEL.log"; return 1; }
  [ -s "$OUT/final/$final" ] && { say "FINISH-OK $(stat -c%s "$OUT/final/$final")"; return 0; }
  say "FINISH-FAIL"; return 1
}
manifest(){
  mkdir -p "$OUT/bakes"
  cp "$BAKE/fixups/bakes/"*.png "$OUT/bakes/" 2>/dev/null || true
  python3 - "$OUT" <<'PY'
import hashlib, json, os, sys
out = sys.argv[1]
man = {"files": {}}
for root, _, files in os.walk(out):
    for fn in files:
        p = os.path.join(root, fn)
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for ch in iter(lambda: f.read(1 << 20), b""):
                h.update(ch)
        man["files"][os.path.relpath(p, out)] = {"size": os.path.getsize(p), "sha256": h.hexdigest()}
json.dump(man, open(os.path.join(out, "MANIFEST.json"), "w"), indent=2)
print("MANIFEST", len(man["files"]), "files")
PY
}

case "$MODEL" in
hara)
  MINI="$IN/hara_mini.blend"
  for m in Torso-10 Arms-10 Legs-10 Lips-10 Irises-10; do
    bake_p1 "$MINI" hara_mini "$m" 8 || { say "HARA-P1-INCOMPLETE"; manifest; exit 1; }
  done
  bake_p2 "$IN/Hara_0.1.blend" Hara '["Torso-10","Face-11","Arms-10","Legs-10","Lips-10","Irises-10"]' "$OUT/hara_baked.blend" || { manifest; exit 1; }
  export_glb "$OUT/hara_baked.blend" Hara.glb || { manifest; exit 1; }
  finish_glb Hara.glb "Torso-10,Face-11,Arms-10,Legs-10,Lips-10,Irises-10" || { manifest; exit 1; }
  ;;
matara)
  MINI="$IN/matara_mini.blend"
  bake_p1 "$MINI" matara_mini "MataraKanFace" 16 || { say "MATARA-P1-INCOMPLETE"; manifest; exit 1; }
  bake_p1 "$MINI" matara_mini "MataraKanTorso" 16 || { say "MATARA-P1-INCOMPLETE"; manifest; exit 1; }
  bake_p2 "$IN/MataraKan.blend" MataraKan '["MataraKanFace","MataraKanTorso"]' "$OUT/matara_baked.blend" || { manifest; exit 1; }
  export_glb "$OUT/matara_baked.blend" MataraKan.glb || { manifest; exit 1; }
  finish_glb MataraKan.glb "MataraKanFace,MataraKanFace.1001,MataraKanTorso,MataraKanTorso.1001" || { manifest; exit 1; }
  ;;
juniper)
  MINI="$PWD/juniper_mini.blend"
  make_mini "$IN/JuniperActias.blend" JuniperActias '["JuniperFace","JuniperTorso"]' "$MINI" || { manifest; exit 1; }
  bake_p1 "$MINI" juniper_mini "JuniperFace" 8 || { say "JUNIPER-P1-INCOMPLETE"; manifest; exit 1; }
  bake_p1 "$MINI" juniper_mini "JuniperTorso" 8 || { say "JUNIPER-P1-INCOMPLETE"; manifest; exit 1; }
  bake_p2 "$IN/JuniperActias.blend" JuniperActias '["JuniperFace","JuniperTorso"]' "$OUT/juniper_baked.blend" || { manifest; exit 1; }
  export_glb "$OUT/juniper_baked.blend" JuniperActias.glb || { manifest; exit 1; }
  finish_glb JuniperActias.glb "JuniperFace,JuniperFace.1001,JuniperTorso,JuniperTorso.1001" || { manifest; exit 1; }
  ;;
*) say "unknown model $MODEL"; exit 2 ;;
esac

# Collect the mini blend into out/ for the artifact (rebuild input for later runs)
cp "$MINI" "$OUT/" 2>/dev/null || true
manifest
say "BAKE-DRIVER-DONE $MODEL"
