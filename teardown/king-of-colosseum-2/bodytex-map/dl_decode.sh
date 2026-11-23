#!/bin/bash
# usage: dl_decode.sh <fileid> [<fileid>...] — download + tim2-decode from .001
T=~/workspace/koc2-vpw2-moveside/sources/koc2/github-kactusken/tools/tim2.py
cd ~/workspace/koc2-bodytex-map/textures
for id in "$@"; do
  f=$(printf "file%05d.bin" $id)
  if [ ! -f "$f" ]; then
    curl -s -o "$f" "https://raw.githubusercontent.com/mhvnsnt/western-heart/muse/koc2-raw/raw/king-of-colosseum-2/jp/kc2fire001/$f" || echo "FAIL $id"
  fi
  python3 $T png "$f" "f${id}" 2>&1 | grep -v "^$" | head -3
done
