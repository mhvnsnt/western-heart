#!/usr/bin/env bash
# face_proof.sh MODEL_REL_PATH OUT_PREFIX [facez]  -> OUT_PREFIX_<pose>.png (front|side)
# Serves the repo root on :${PORT:-8765} (start it yourself: python3 -m http.server 8765)
set -e
CH=${CHROME:-google-chrome}
for p in ${POSES:-bind stance jab uppercut hook lean}; do
  timeout 150 "$CH" --headless=new --user-data-dir=/tmp/fcp-$$ --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader \
    --window-size=900,450 --virtual-time-budget=120000 --run-all-compositor-stages-before-draw \
    --screenshot="${2}_${p}.png" "http://127.0.0.1:${PORT:-8765}/tools/rig/face_proof.html?model=/$1&pose=$p&facez=${3:-1}" >/dev/null 2>&1
done
