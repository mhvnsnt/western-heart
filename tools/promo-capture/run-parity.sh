#!/bin/bash
# run-parity.sh <outDir> <nShards> [override-root]: one resumable browser per shard
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$1; N=$2; mkdir -p "$OUT"
python3 "$HERE/parity_tests.py" "$HERE/../../game/assets/anim/t7/king/moves.pack.json" > "$HERE/parity-tests.json"
if [ -n "$3" ]; then
  export WH_OVERRIDE_ROOT=$3
  export WH_OVERRIDE_FILES=game/js/fighter.js,game/js/t3anims.js,game/js/stagebreaks.js,game/assets/anim/t7/king/moves.pack.json,game/assets/movesets/pantera.json
fi
cd "$HERE"
for s in $(seq 0 $((N-1))); do
  ( for try in $(seq 1 25); do timeout 1800 node pantera-parity.mjs "$OUT" $s $N >> "$OUT/log-$s.txt" 2>&1 && break; echo "retry $try" >> "$OUT/log-$s.txt"; done; echo SHARDEXIT >> "$OUT/log-$s.txt" ) &
done
wait; echo ALLDONE > "$OUT/ALLDONE"
