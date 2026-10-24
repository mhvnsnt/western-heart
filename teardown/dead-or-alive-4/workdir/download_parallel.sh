#!/bin/bash
# Parallel DOA4 ISO downloader - 4 parts at a time via CDN
# Usage: ./download_parallel.sh
set -e
cd ~/workspace/doa4-bass
mkdir -p parts

# Get all asset IDs first
echo "Fetching asset list..."
gh api repos/mhvnsnt/western-heart/releases/tags/doa4-iso-v1 --jq '.assets[] | "\(.id) \(.name) \(.size)"' > asset_list.txt

get_cdn_url() {
  local ID=$1
  curl -s -H "Accept: application/octet-stream" -H "Authorization: Bearer $(gh auth token)" \
    "https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/$ID" \
    -D - -o /dev/null 2>/dev/null | grep -i "^location:" | tr -d '\r' | cut -d' ' -f2
}

download_part() {
  local ID=$1 NAME=$2 SIZE=$3
  local OUT="parts/$NAME"
  # Skip if already complete
  if [ -f "$OUT" ] && [ "$(stat -c%s "$OUT")" = "$SIZE" ]; then
    echo "SKIP $NAME (complete)"
    return 0
  fi
  local URL=$(get_cdn_url $ID)
  if [ -z "$URL" ]; then
    echo "FAIL $NAME (no URL)"
    return 1
  fi
  echo "DL $NAME..."
  curl -L -C - -o "$OUT" "$URL" --retry 3 --retry-delay 5 -s
  local ACTUAL=$(stat -c%s "$OUT" 2>/dev/null || echo 0)
  if [ "$ACTUAL" = "$SIZE" ]; then
    echo "OK $NAME"
  else
    echo "PARTIAL $NAME ($ACTUAL/$SIZE)"
    return 1
  fi
}

# Process in batches of 4
BATCH=()
while read -r ID NAME SIZE; do
  BATCH+=("$ID $NAME $SIZE")
  if [ ${#BATCH[@]} -eq 4 ]; then
    for item in "${BATCH[@]}"; do
      download_part $item &
    done
    wait
    BATCH=()
    # Append completed parts in order and clean up
    for i in $(seq -w 1 30); do
      PART="doa4-250m.part_$i"
      if [ -f "parts/$PART" ] && ! grep -q "^$i$" progress.txt 2>/dev/null; then
        # Verify size before appending
        EXPECTED_SIZE=$(grep "$PART" asset_list.txt | awk '{print $3}')
        ACTUAL_SIZE=$(stat -c%s "parts/$PART")
        if [ "$ACTUAL_SIZE" = "$EXPECTED_SIZE" ]; then
          cat "parts/$PART" >> doa4.iso
          rm -f "parts/$PART"
          echo "$i" >> progress.txt
          echo "Appended part $i"
        fi
      fi
    done
    df -h /home/hatch | tail -1
  fi
done < asset_list.txt

# Handle remaining batch
for item in "${BATCH[@]}"; do
  download_part $item &
done
wait

# Final append
for i in $(seq -w 1 30); do
  PART="doa4-250m.part_$i"
  if [ -f "parts/$PART" ] && ! grep -q "^$i$" progress.txt 2>/dev/null; then
    EXPECTED_SIZE=$(grep "$PART" asset_list.txt | awk '{print $3}')
    ACTUAL_SIZE=$(stat -c%s "parts/$PART")
    if [ "$ACTUAL_SIZE" = "$EXPECTED_SIZE" ]; then
      cat "parts/$PART" >> doa4.iso
      rm -f "parts/$PART"
      echo "$i" >> progress.txt
      echo "Appended part $i"
    fi
  fi
done

# Verify
EXPECTED=7833796608
ACTUAL=$(stat -c%s doa4.iso 2>/dev/null || echo 0)
echo "Final: $ACTUAL / $EXPECTED"
[ "$ACTUAL" = "$EXPECTED" ] && echo "SUCCESS" || echo "INCOMPLETE"
