#!/bin/bash
# rig-seq.sh — SEQUENTIAL auto-rig driver (pose-isolation recovery lane).
# Same proven chain as rig-batch.sh (decompress -> prenorm -> blender_heat ->
# validate -> meshopt recompress) with the two fixes the 2026-10-20 batch
# failure proved necessary:
#   1. ONE heat at a time, heat timeout 3600s (batch 1c ran under load ~15 on
#      2 CPUs / 8GB RAM and EVERY heat — including sam-ur-a1, the model+chain
#      with a proven AUTO_RIG_OK pass — burned its full 1200s timeout and was
#      killed with no output).
#   2. FULL unfiltered Blender output per model to work/rig2_<id>.log
#      (the batch's grep filters hid every error).
# Lockfile prevents double-runs. Skips models whose rigged/<id>_ship.glb
# already exists. Safe to re-fire after a restart: finished rows skip.
S=~/workspace/wh-pose-survey; BL=~/workspace/tools/blender/blender-4.0.2-linux-x64/blender
PLAN=${1:-$S/rig-plan-2.tsv}; cd $S; mkdir -p rigwork rigged work
exec 9>$S/work/rig-seq.lock
flock -n 9 || { echo "rig-seq already running (lock held)"; exit 1; }
while IFS=$'\t' read -r id src facing meshopt; do
  [ -z "$id" ] && continue
  case "$id" in \#*) continue;; esac
  if [ -f "rigged/${id}_ship.glb" ]; then echo "SKIP $id (ship exists)"; continue; fi
  echo "=== RIG $id facing=$facing $(date '+%F %T')"
  work=$S/rigwork/$id; mkdir -p $work
  in=$src
  if [ "$meshopt" = "1" ]; then
    if [ ! -f "$work/raw.glb" ]; then
      (cd $work && timeout 600 npx -y @gltf-transform/cli copy "$src" raw.glb >> $S/work/rig2_${id}.log 2>&1)
    fi
    in=$work/raw.glb
  fi
  if [ ! -f "$work/norm.glb" ]; then
    timeout 900 xvfb-run -a env -u PYTHONPATH $BL -b --python autorig/prenorm.py -- "$in" "$work/norm.glb" >> work/rig2_${id}.log 2>&1
  fi
  [ -f "$work/norm.glb" ] || { echo "FAIL $id prenorm (see work/rig2_${id}.log)"; continue; }
  timeout 3600 xvfb-run -a env -u PYTHONPATH $BL -b --factory-startup --python autorig/backends/blender_heat.py -- --in "$work/norm.glb" --out "$S/rigged/${id}.glb" --mesh-facing="$facing" >> work/rig2_${id}.log 2>&1
  [ -f "$S/rigged/${id}.glb" ] || { echo "FAIL $id heat (see work/rig2_${id}.log)"; continue; }
  python3 autorig/validate.py --in "$S/rigged/${id}.glb" >> work/rig2_${id}.log 2>&1
  (cd $work && timeout 600 npx -y @gltf-transform/cli copy "$S/rigged/${id}.glb" "$S/rigged/${id}_ship.glb" >> $S/work/rig2_${id}.log 2>&1)
  ls -la "$S/rigged/${id}_ship.glb" 2>/dev/null || echo "FAIL $id recompress"
done < "$PLAN"
echo RIG-SEQ-DONE
