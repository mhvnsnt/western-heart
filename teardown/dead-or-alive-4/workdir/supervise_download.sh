#!/bin/bash
# Watchdog-installed supervisor for the DOA4 ISO download (2026-10-16 ~18:05 CDT).
# Runs resume_download.sh (strict sequential append) in passes until the ISO is
# complete: 29*262144000 + 232716288 = 7834892288 bytes.
# Single writer only -- never run alongside download_parallel.sh (retired: it
# appended parts out of order and raced resume_download.sh on the same files).
set -u
cd ~/workspace/doa4-bass
mkdir -p parts
EXPECTED=7834892288
for i in $(seq 1 40); do
  echo "=== supervisor pass $i $(date -u +%FT%TZ) ===" >> download_fixed.log
  ./resume_download.sh >> download_fixed.log 2>&1
  ACTUAL=$(stat -c%s doa4.iso 2>/dev/null || echo 0)
  echo "pass $i done: iso=$ACTUAL / $EXPECTED" >> download_fixed.log
  if [ "$ACTUAL" = "$EXPECTED" ]; then
    echo "SUCCESS - doa4.iso complete ($ACTUAL bytes)" >> download_fixed.log
    break
  fi
  sleep 60
done
echo "supervisor exiting $(date -u +%FT%TZ)" >> download_fixed.log
