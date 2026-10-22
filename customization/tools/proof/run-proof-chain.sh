#!/bin/bash
# Creation Suite round-2 proof chain — serial Blender jobs (one at a time).
cd ~/workspace/_cs-round2-work || exit 1
export LD_LIBRARY_PATH=$HOME/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu
export XDG_RUNTIME_DIR=/tmp
BL=~/workspace/tools/blender/blender-4.0.2-linux-x64/blender
LOG=customization/tools/proof/chain.log
echo "=== CHAIN START $(date) ===" >> $LOG

# 1. Placement rebake C (socket-skin representation)
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/apply_customization.py -- \
  customization/tools/proof/cs-round2-scratch/customization-c.json >> $LOG 2>&1
echo "bake C done rc=$?" >> $LOG
python3 customization/tools/proof/cs-round2-roundtrip.py measure \
  customization/tools/proof/cs-round2-scratch/model-rt-c.glb > customization/tools/proof/cs-round2/measure-rt-c-v2.json 2>>$LOG
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render-head.py -- \
  customization/tools/proof/cs-round2-scratch/model-rt-c.glb customization/tools/proof/cs-round2/rt-c2 >> $LOG 2>&1
echo "render C done rc=$?" >> $LOG

# 2. DEATHFANG eye-part proof
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/apply_customization.py -- \
  customization/tools/proof/cs-round2-eyes/customization.json >> $LOG 2>&1
echo "bake eyes done rc=$?" >> $LOG
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render-head.py -- \
  customization/tools/proof/cs-round2-eyes/deathfang-eyed.glb customization/tools/proof/cs-round2/df-eyes >> $LOG 2>&1
echo "render eyes done rc=$?" >> $LOG

# 3. Master White real record bake (morphs via MPFB)
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/apply_customization.py -- \
  roster/baek/attires/master-white/customization.json \
  --mpfb-src ~/workspace/cape-jones/production/tools/mpfb2/src >> $LOG 2>&1
echo "bake MW done rc=$?" >> $LOG
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render.py -- \
  roster/baek/attires/master-white/model-kevin-diff.glb customization/tools/proof/cs-round2/mw-final >> $LOG 2>&1
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render-head.py -- \
  roster/baek/attires/master-white/model-kevin-diff.glb customization/tools/proof/cs-round2/mw-final-head >> $LOG 2>&1
echo "=== CHAIN END $(date) ===" >> $LOG
