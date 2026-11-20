#!/bin/bash
# Resume Def Jam: Fight for NY ISO download (lane A, 2026-10-16)
# Re-runnable: curl -C - resumes from current partial size.
cd "$(dirname "$0")"
URL='https://archive.org/download/slus-210.04.-def-jam-fight-for-ny/SLUS_210.04.Def%20Jam%20-%20Fight%20for%20NY.iso'
EXPECTED=4694573056
echo "[$(date -u +%FT%TZ)] resume starting at $(stat -c%s "SLUS_210.04.Def Jam - Fight for NY.iso") bytes" >> curl-defjam-laneA.log
for i in 1 2 3 4 5 6 7 8; do
  curl -L -C - --retry 10 --retry-delay 20 --retry-all-errors \
       --speed-limit 30000 --speed-time 180 \
       -o "SLUS_210.04.Def Jam - Fight for NY.iso" "$URL" \
       >> curl-defjam-laneA.log 2>&1
  SIZE=$(stat -c%s "SLUS_210.04.Def Jam - Fight for NY.iso")
  echo "[$(date -u +%FT%TZ)] pass $i ended at $SIZE bytes (expected $EXPECTED)" >> curl-defjam-laneA.log
  if [ "$SIZE" -ge "$EXPECTED" ]; then
    echo "[$(date -u +%FT%TZ)] DONE: $SIZE bytes" >> curl-defjam-laneA.log
    break
  fi
  sleep 30
done
