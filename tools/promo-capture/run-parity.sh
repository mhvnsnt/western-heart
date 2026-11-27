#!/bin/bash
# run-parity.sh <outDir> <nShards> [override-root]: one resumable browser per shard
OUT=$1; N=$2; mkdir -p $OUT
if [ -n "$3" ]; then export WH_OVERRIDE_ROOT=$3 WH_OVERRIDE_FILES=game/js/fighter.js,game/js/t3anims.js,game/assets/anim/t7/king/moves.pack.json; fi
for s in $(seq 0 $((N-1))); do
  ( for try in $(seq 1 25); do timeout 1800 node pantera-parity.mjs $OUT $s $N >> $OUT/log-$s.txt 2>&1 && break; echo "retry $try" >> $OUT/log-$s.txt; done; echo SHARDEXIT >> $OUT/log-$s.txt ) &
done
wait; echo ALLDONE > $OUT/ALLDONE
