#!/bin/bash
export LD_LIBRARY_PATH=$HOME/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu XDG_RUNTIME_DIR=/tmp
BL=~/workspace/tools/blender/blender-4.0.2-linux-x64/blender
cd ~/workspace/_cs-round2-work || exit 1
L=/tmp/swap2.log; : > $L
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render-head.py -- customization/tools/proof/cs-round2-swap/model-kevin-head-swap.glb customization/tools/proof/cs-round2/kevin-head-swap-v2 >> $L 2>&1
echo REN1 >> $L
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/apply_customization.py -- customization/tools/proof/cs-round2-swap/customization-both.json >> $L 2>&1
echo BAKEBOTH >> $L
xvfb-run -a env -u PYTHONPATH $BL -b --python customization/tools/proof/cs-round2-render.py -- customization/tools/proof/cs-round2-swap/model-swap.glb customization/tools/proof/cs-round2/swap-both >> $L 2>&1
echo SWAP2-DONE >> $L
