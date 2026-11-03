#!/bin/bash
cd /workspace/work/clothpipe
export WH_SAMPLES=24
for j in 07 08; do
  echo "START $j $(date -u +%T)"
  blender -b -P cloth_render.py -- jobs_$j.json > logs/render_$j.log 2>&1
  echo "END $j rc=$? $(date -u +%T)"
done
echo ALLDONE
