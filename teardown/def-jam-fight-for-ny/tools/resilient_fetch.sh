#!/bin/bash
# Resilient range-fetch: retries missing tails until byte-exact completion.
HOST="https://dn721808.ca.archive.org/0/items/slus-210.04.-def-jam-fight-for-ny/SLUS_210.04.Def%20Jam%20-%20Fight%20for%20NY.iso"
D=~/workspace/defjam-work/surgical
fetch_one() { # name lba size
  local n=$1 lba=$2 sz=$3 base=$((lba*2048)) f="$D/$n"
  local tries=0
  while [ $tries -lt 40 ]; do
    local cur=0
    [ -f "$f" ] && cur=$(stat -c%s "$f")
    if [ "$cur" -ge "$sz" ]; then
      truncate -s "$sz" "$f" 2>/dev/null
      echo "$n COMPLETE $(stat -c%s "$f")"
      return 0
    fi
    if [ "$cur" -gt 0 ]; then
      curl -s --retry 3 --max-time 900 -r $((base+cur))-$((base+sz-1)) -o "$f.tail" "$HOST" \
        && cat "$f.tail" >> "$f" && rm -f "$f.tail" && echo "$n +$(stat -c%s "$f" 2>/dev/null) ($((100*$(stat -c%s "$f")/sz))%)"
    else
      curl -s --retry 3 --max-time 900 -r ${base}-$((base+sz-1)) -o "$f" "$HOST" \
        && echo "$n got $(stat -c%s "$f" 2>/dev/null)"
    fi
    tries=$((tries+1))
    sleep 3
  done
  echo "$n FAILED after 40 tries"
  return 1
}
fetch_one "caw/V2CP_0.VIV" 1716969 9282398 &
fetch_one "caw/V2CP_1.VIV" 1721502 101383672 &
fetch_one "caw/V2CP_2.VIV" 1771006 81486122 &
fetch_one "caw/V2CP_3.VIV" 1810795 26554644 &
fetch_one "motion/WRES_ALL.VIV" 1968777 64166308 &
fetch_one "venues/V2BG.VIV" 1943736 50614733 &
wait
echo "RESILIENT_FETCH_DONE $(date)"
