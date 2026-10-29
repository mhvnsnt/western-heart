#!/bin/bash
# rig-seq2.sh — RAM-GATED sequential auto-rig driver (pose-isolation lane).
# Pass 1 (rig-seq.sh) proved the failure mode: heats are OOM-killed (SIGKILL,
# logs literally read "Killed") whenever MemAvailable is low — other lanes'
# Blender jobs hold the 8GB VM. Sam-ur-a1 passed in a quiet window; scimitar
# passed with a small (13MB) model. This driver adopts the gate discipline
# other lanes already use: before each prenorm and each heat, wait until
# MemAvailable >= GATE_MB (poll 20s, give up after GATE_MAX_WAIT s and skip
# the model for this pass). One heat at a time, 3600s timeout, full logs.
# Restart-safe: rows with a validate-passing rigged/<id>_ship.glb are skipped
# (checked via validate.py, not mere file existence).
S=~/workspace/wh-pose-survey; BL=~/workspace/tools/blender/blender-4.0.2-linux-x64/blender
PLAN=${1:-$S/rig-plan-3.tsv}; GATE_MB=${GATE_MB:-3800}; GATE_MAX_WAIT=${GATE_MAX_WAIT:-3600}
cd $S; mkdir -p rigwork rigged work
exec 9>$S/work/rig-seq2.lock
flock -n 9 || { echo "rig-seq2 already running (lock held)"; exit 1; }
wait_ram() { # $1 = stage label
  local waited=0 avail
  while true; do
    avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
    if [ "$avail" -ge "$GATE_MB" ]; then echo "GATE_OPEN $1 avail=${avail}MB waited=${waited}s"; return 0; fi
    if [ "$waited" -ge "$GATE_MAX_WAIT" ]; then echo "GATE_TIMEOUT $1 avail=${avail}MB waited=${waited}s"; return 1; fi
    sleep 20; waited=$((waited+20))
  done
}
while IFS=$'\t' read -r id src facing meshopt; do
  [ -z "$id" ] && continue
  case "$id" in \#*) continue;; esac
  if [ -f "rigged/${id}_ship.glb" ] && python3 autorig/validate.py --in "rigged/${id}.glb" > /dev/null 2>&1; then
    echo "SKIP $id (ship exists + validate pass)"; continue
  fi
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
    wait_ram "$id prenorm" || { echo "SKIP $id (ram gate)"; continue; }
    timeout 900 xvfb-run -a env -u PYTHONPATH $BL -b --python autorig/prenorm.py -- "$in" "$work/norm.glb" >> work/rig2_${id}.log 2>&1
  fi
  [ -f "$work/norm.glb" ] || { echo "FAIL $id prenorm (see work/rig2_${id}.log)"; continue; }
  wait_ram "$id heat" || { echo "SKIP $id (ram gate)"; continue; }
  timeout 3600 xvfb-run -a env -u PYTHONPATH $BL -b --factory-startup --python autorig/backends/blender_heat.py -- --in "$work/norm.glb" --out "$S/rigged/${id}.glb" --mesh-facing="$facing" >> work/rig2_${id}.log 2>&1
  [ -f "$S/rigged/${id}.glb" ] || { echo "FAIL $id heat (see work/rig2_${id}.log)"; continue; }
  python3 autorig/validate.py --in "$S/rigged/${id}.glb" >> work/rig2_${id}.log 2>&1
  (cd $work && timeout 600 npx -y @gltf-transform/cli copy "$S/rigged/${id}.glb" "$S/rigged/${id}_ship.glb" >> $S/work/rig2_${id}.log 2>&1)
  ls -la "$S/rigged/${id}_ship.glb" 2>/dev/null || echo "FAIL $id recompress"
done < "$PLAN"
echo RIG-SEQ2-DONE
