#!/bin/bash
set -u; C=$1; T=$2; R=/workspace/wh-cape8; BL=/workspace/oss/blender/blender-4.2.3-linux-x64/blender
mkdir -p $R/anims/show/$C
while read slot src skip inplace; do
  extra=""; [ "$inplace" = 1 ] && extra="--in-place"
  timeout 300 xvfb-run -a env -u PYTHONPATH $BL -b --python $R/tools/anim-retarget/retarget_rot.py -- --source $R/.cmu/$src --target $T --out $R/anims/show/$C/$slot.glb --bonemap $R/tools/anim-retarget/bone_maps/cmu_to_wh.json --clip-name $slot --step 4 --skip $skip --max-frames 150 --anim-only $extra 2>&1 | grep -E "WROTE|Error" | sed "s/^/$C $slot: /"
done <<L
idle 140_06.bvh 120 1
guard_stance 13_17.bvh 120 1
walk 02_01.bvh 0 0
run 02_03.bvh 0 0
sit_idle 13_05.bvh 120 1
sit_stand 13_01.bvh 0 0
talk_gesture 18_08.bvh 60 1
wave 13_26.bvh 60 1
react_laugh 13_14.bvh 60 1
react_anger 18_10.bvh 60 1
drink 13_09.bvh 60 1
prefight_intro 13_17.bvh 0 1
L
echo DONE $C
