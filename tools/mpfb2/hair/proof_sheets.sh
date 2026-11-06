#!/bin/bash
# contact sheets (ImageMagick montage) -> /workspace/work/renders/sheets/
R=/workspace/work/renders; S=$R/sheets; mkdir -p $S
F="-font DejaVu-Sans -pointsize 18 -background '#2b2d31' -fill white"
T="super-heavyweight powerhouse showman technician highflyer luchador powerhouse-w athletic-w striker-w"
# 1. all 9 template bodies, front + 3/4
args=(); for t in $T; do args+=(-label "$t front" $R/bodies/${t}_front.png -label "$t 3/4" $R/bodies/${t}_34.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 16 -background '#2b2d31' -fill white -tile 6x -geometry 300x300+4+4 \
  -title "Template bodies (9) — Blender 4.3 Cycles" $S/01-template-bodies.png
# 2. body morph extremes (3/4 view), rows = template, cols = neutral / heavy / lean-toned / broad
args=(); for t in $T; do args+=(-label "$t base" $R/bodies/${t}_34.png); for m in heavy lean-toned broad; do args+=(-label "$t $m" $R/morphs/${t}_${m}_34.png); done; done
montage "${args[@]}" -font DejaVu-Sans -pointsize 14 -background '#2b2d31' -fill white -tile 8x -geometry 230x230+3+3 \
  -title "Body sliders at extremes (weight+, weight- & tone+, shoulders/chest/neck/traps+) — fitted hair/brows/lashes/beard ride along" $S/02-body-morph-extremes.png
# 3. face sliders neutral vs extreme (fitted hair/brows/lashes/beard follow the face shape keys)
args=(); for t in $T; do args+=(-label "$t neutral" $R/morphs/${t}_face-neutral_front.png -label "$t head/brow/jaw extreme" $R/morphs/${t}_face-extreme_front.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 14 -background '#2b2d31' -fill white -tile 6x -geometry 280x280+3+3 \
  -title "Face sliders (head width+, brow height+, head size+, square jaw+) — parts follow via transferred shape keys" $S/03-face-morph-extremes.png
# 4/5. every fitted part (generic names), front + 3/4 (hair: back 3/4)
name() { case $1 in
  mh-hair-short01) echo "Short Crop";; mh-hair-short02) echo "Textured Short";; mh-hair-short03) echo "Side Part";;
  mh-hair-short04) echo "Slick Back";; mh-hair-bob01) echo "Bob";; mh-hair-bob02) echo "Layered Bob";;
  mh-hair-long01) echo "Long Straight";; mh-hair-ponytail01) echo "High Ponytail";; mh-hair-braid01) echo "Single Braid";;
  mh-hair-afro01) echo "Rounded Afro";; mh-brows-001) echo "Natural Brows";; mh-brows-003) echo "Thick Brows";;
  mh-brows-006) echo "Arched Brows";; mh-brows-010) echo "Thin Brows";; mh-lashes-01) echo "Natural Lashes";;
  mh-lashes-02) echo "Long Lashes";; wh-beard-full) echo "Full Beard";; wh-beard-goatee) echo "Goatee";;
  wh-beard-moustache) echo "Moustache";; wh-beard-chinstrap) echo "Chin Strap";; wh-beard-stubble) echo "Stubble";; esac; }
args=(); for f in $(ls $R/parts/mh-hair-*_front.png | sort); do b=$(basename $f _front.png); id=${b%_*}; args+=(-label "$(name $id) — front" $f -label "$(name $id) — back 3/4" ${f%_front.png}_34.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 15 -background '#2b2d31' -fill white -tile 6x -geometry 280x280+3+3 \
  -title "Hairstyles (10) on template bodies — skinned head/neck/upper spine, shoulder clearance" $S/04-hairstyles.png
args=(); for f in $(ls $R/parts/mh-brows-*_front.png $R/parts/mh-lashes-*_front.png $R/parts/wh-beard-*_front.png | sort); do b=$(basename $f _front.png); id=${b%_*}; args+=(-label "$(name $id) — front" $f -label "$(name $id) — 3/4" ${f%_front.png}_34.png); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 15 -background '#2b2d31' -fill white -tile 6x -geometry 280x280+3+3 \
  -title "Eyebrows, eyelashes, facial hair (11) on the technician template" $S/05-brows-lashes-facial-hair.png
# 6. created fighters in a fight stance
args=(); for f in $(ls $R/fight/*.png | sort); do b=$(basename $f .png); args+=(-label "$b" $f); done
montage "${args[@]}" -font DejaVu-Sans -pointsize 15 -background '#2b2d31' -fill white -tile 4x -geometry 380x380+3+3 \
  -title "Created fighters in a fight stance — hair follows head turn + neck/upper spine" $S/06-created-fighters-fight-stance.png
ls -la $S
