#!/bin/bash
# CLOTHING + ACCESSORIES contact sheets (ImageMagick montage) -> /workspace/work/renders/sheets/
R=/workspace/work/renders/cloth; S=/workspace/work/renders/sheets; mkdir -p $S
T="super-heavyweight powerhouse showman technician highflyer luchador powerhouse-w athletic-w striker-w"
nm() { python3 -c "import json,sys;d={i['id']:i['name'] for i in json.load(open('/workspace/work/clothpipe/items.json'))};j=[x for x in json.load(open('/workspace/work/clothpipe/jobs_$2.json')) if x['template']=='$1'][0];print(', '.join(d[i] for i in j['items']))"; }
args=(); for t in $T; do n=$(nm $t 07); args+=(-label "$t\n$n" $R/07_${t}_front.png -label "$t\nback" $R/07_${t}_back.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 12 -background '#2b2d31' -fill white -tile 6x -geometry 300x300+3+3 \
  -title "Clothing (12 CC0 garments generated in Blender on each body) — skinned, body hidden under cloth — Cycles" $S/07-clothing.png
args=(); for t in $T; do args+=(-label "$t — front" $R/08_${t}_front.png -label "$t — arms" $R/08_${t}_upper.png -label "$t — legs" $R/08_${t}_legs.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 13 -background '#2b2d31' -fill white -tile 6x -geometry 280x280+3+3 \
  -title "Accessories: Headband, Arm Bands, Elbow Pads, Wrist Tape, Waist Belt, Knee Pads (+ trunks) — all 9 bodies — Cycles" $S/08-accessories.png
for f in 07-clothing 08-accessories; do convert $S/$f.png -resize 1400x\> -quality 85 $S/${f}-small.jpg; done
ls -la $S/07* $S/08*
