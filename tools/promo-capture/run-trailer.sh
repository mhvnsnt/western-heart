#!/bin/bash
# resume-until-complete wrapper: restarts trailer-capture.mjs from the first incomplete shot after a browser crash
OUT=$1; shift
cd "$(dirname "$0")"
declare -A N=([S1_hero_orbit]=120 [S2_walk_in]=180 [S3_one_two]=60 [S4_fwd2]=60 [S5_zen_attacks]=60 [S6_fwd3_kick]=60 [S7_left_kick]=60 [S8_exchange_ai]=120 [S9_big_kick_slowmo]=120 [S10_hero_hold]=60)
ORDER="S1_hero_orbit S2_walk_in S3_one_two S4_fwd2 S5_zen_attacks S6_fwd3_kick S7_left_kick S8_exchange_ai S9_big_kick_slowmo S10_hero_hold"
for try in 1 2 3 4 5 6; do
  first=""; for s in $ORDER; do c=$(ls $OUT/$s 2>/dev/null | wc -l); if [ "$c" -lt "${N[$s]}" ]; then first=$s; break; fi; done
  [ -z "$first" ] && { echo COMPLETE; exit 0; }
  echo "try $try from $first"; rm -rf "$OUT/$first"
  timeout 5400 node trailer-capture.mjs "$OUT" "$first" 2>&1 | grep -E "done|Error|closed" | head -20
done
