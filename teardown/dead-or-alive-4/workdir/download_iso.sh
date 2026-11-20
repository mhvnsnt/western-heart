#!/bin/bash
# Download DOA4 ISO parts one at a time, append to doa4.iso, delete part immediately
# Expected final size: 7,833,796,608 bytes (29x262144000 + 232716288)
set -e
cd ~/workspace/doa4-bass
EXPECTED=7833796608

for i in $(seq -w 1 30); do
  PART="doa4-250m.part_$i"
  # Skip if already appended (check a progress file)
  if grep -q "^$i$" progress.txt 2>/dev/null; then
    echo "Part $i already done, skipping"
    continue
  fi
  echo "=== Downloading part $i/30 ==="
  gh release download doa4-iso-v1 --repo mhvnsnt/western-heart --pattern "$PART" --dir parts/ --clobber
  echo "Appending part $i to doa4.iso..."
  cat "parts/$PART" >> doa4.iso
  rm -f "parts/$PART"
  echo "$i" >> progress.txt
  # Check disk
  FREE=$(df /home/hatch | tail -1 | awk '{print $4}')
  echo "Disk free: ${FREE}K"
  if [ "$FREE" -lt 104857 ]; then  # < 100MB
    echo "WARNING: Disk critically low! Stopping."
    exit 1
  fi
done

ACTUAL=$(stat -c%s doa4.iso)
echo "Final size: $ACTUAL (expected $EXPECTED)"
if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "SUCCESS: ISO reassembled correctly"
else
  echo "ERROR: Size mismatch!"
  exit 1
fi
