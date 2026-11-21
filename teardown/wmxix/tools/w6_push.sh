#!/bin/bash
# W6: stage the WMXIX extraction into western-heart on 3 branches and push.
# Reads the GitHub PAT from stdin (one line, never stored in a file or
# in the remote URL). Run: printf '%s' "$PAT" | ssh ... 'bash w6_push.sh'
set -e
read -r TOKEN
if [ -z "$TOKEN" ]; then echo "no token on stdin"; exit 1; fi
PUSH_URL="https://x-access-token:${TOKEN}@github.com/mhvnsnt/western-heart.git"
unset TOKEN

cd /data/wmxix/wh-push
git config user.name mhvnsnt
git config user.email fmmg.mars@gmail.com
git config http.postBuffer 268435456
git fetch origin main 2>&1 | tail -1
git checkout main
git reset --hard origin/main

OUT=/data/wmxix/out
SRC=/data/wmxix/tools-src
W=teardown/wmxix

# ---------- PR 1: CAW meshes + tools + docs ----------
git checkout -b w6/wmxix-caw-mesh
mkdir -p $W/caw-parts/meshes $W/tools $W/docs
cp -r $OUT/caw-mesh/Man $OUT/caw-mesh/Woman $W/caw-parts/meshes/
cp $OUT/caw-mesh-manifest.json $W/caw-parts/meshes/
for f in w6_extract.py w6_decode2.py w6_arena.py w6_hhh.py w6_contact.py \
         w6_probe_nogeom.py w6_probe_arena.py w6_probe_tiny.py \
         w6_probe_skel.py w6_probe_hhh_err.py w6_probe_hhh_arm.py \
         w6_probe_strips.py w6_probe_profile.py \
         w6_dolphin_boot.sh w6_dolphin_debug.sh; do
  cp $SRC/$f $W/tools/ 2>/dev/null || echo "missing tool (skipped): $f"
done
cp $SRC/W6-EXTRACTION-2026-11-19.md $W/docs/
git add $W/caw-parts/meshes $W/tools $W/docs/W6-EXTRACTION-2026-11-19.md
git commit -m "W6: WMXIX CAW meshes (1,141 OBJs) + extraction tools + notes

Decoded from the GW9E78 ISO (SHA1 4746c3b9...): 1,128 ok + 13 pool-scan
meshes, 287,044 verts / 220,321 tris. DUMY files are NOT all empty -
170/202 decode to real geometry. 59 NO-GEOMETRY files are all Gears
accessories, verified empty by brute-force scan. Decoder v2 (run path
for v3, batch path for v4, small-batch path for tiny Gears parts) in
tools/w6_decode2.py; method notes in docs/W6-EXTRACTION-2026-11-19.md." 2>&1 | tail -2
git push "$PUSH_URL" w6/wmxix-caw-mesh 2>&1 | tail -2
echo "PR1 pushed"

# ---------- PR 2: textures + contact sheets ----------
git checkout main
git reset --hard origin/main
git checkout -b w6/wmxix-textures
mkdir -p $W/caw-parts/textures $W/wrestlers/face-contact
cp -r $OUT/caw-tex/* $W/caw-parts/textures/
cp $OUT/caw-tex-manifest.json $W/caw-parts/textures/
for d in $OUT/wrestler-tex/*/; do
  base=$(basename "$d")
  slot=${base%_*}
  var=${base#*_}
  mkdir -p "$W/wrestlers/$slot/tex/$var"
  cp "$d"*.png "$W/wrestlers/$slot/tex/$var/"
done
cp $OUT/wrestler-tex-manifest.json $W/wrestlers/
cp $OUT/contact/face-contact-*.png $OUT/contact/slot-index.json \
   $W/wrestlers/face-contact/
git add $W/caw-parts/textures $W/wrestlers
git commit -m "W6: WMXIX textures (9,410 PNGs) + face contact sheets

CAW textures: 5,613 PNGs from 1,469 .tex files (caw-parts/textures/).
Wrestler textures: 3,797 PNGs from 162 .tex files, 77 slots
(wrestlers/<slot>/tex/<variant>/). 0 decode errors in both sets (TPL
0x0120AF30 magic variant + end-of-file retry). Face contact sheets for
slot identification (wrestlers/face-contact/): 73/77 slots with faces;
texture-name hints incl. slot 019 'big' (Big Show lead - needs Mars's
eye). Slot 000 = Triple H remains the only confirmed identity." 2>&1 | tail -2
git push "$PUSH_URL" w6/wmxix-textures 2>&1 | tail -2
echo "PR2 pushed"

# ---------- PR 3: mpc clips + arenas + Triple H ----------
git checkout main
git reset --hard origin/main
git checkout -b w6/wmxix-clips-arenas-hhh
mkdir -p $W/animations/mpc $W/arenas/faced
cp $OUT/mpc-clips/*.json $W/animations/mpc/
cp $OUT/mpc-clips-manifest.json $W/animations/mpc/
cp $OUT/arena-faced/*.obj $W/arenas/faced/
cp $OUT/arena-faced/arena-manifest.json $W/arenas/faced/
cp $OUT/triple-h/triple-h-000_0.obj $OUT/triple-h/triple-h-000_1.obj \
   $OUT/triple-h/triple-h-000_0.png $OUT/triple-h/triple-h-000_1.png \
   $OUT/triple-h/hhh-manifest.json $W/wrestlers/000/
cp $SRC/TRIPLE-H-RETRIANGULATION.md $W/wrestlers/000/
git add $W/animations/mpc $W/arenas/faced $W/wrestlers/000
git commit -m "W6: WMXIX gameplay clips (1,905) + faced arenas + Triple H

move.mpc: 1,900 clips decoded to JSON + 5 stubs, 0 failures
(animations/mpc/). NOTE: est_seconds is NOT calibrated - use raw tick
counts. Arenas: 35 faced OBJs, 2,087 faces total (PARTIAL coverage,
1-19% - the bulk face format is still uncracked; see extraction notes).
Triple H re-triangulation (wrestlers/000/): 606v/383f per attire,
positions reproduce the verified solution to 0.0002 m, bbox exact,
bad faces 227 -> 33, 0 cross-batch faces." 2>&1 | tail -2
git push "$PUSH_URL" w6/wmxix-clips-arenas-hhh 2>&1 | tail -2
echo "PR3 pushed"

git checkout main
git branch -v | grep w6/
git ls-remote --heads origin 'w6/*' | head -5
echo "ALL PUSHES DONE"
