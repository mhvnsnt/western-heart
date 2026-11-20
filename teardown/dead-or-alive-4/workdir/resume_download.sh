#!/bin/bash
# Fixed DOA4 ISO downloader - parallel downloads, STRICT sequential append
# Fixes the out-of-order bug from download_parallel.sh
set -e
cd ~/workspace/doa4-bass
mkdir -p parts

# next_part: the next part number we expect to append (1-30)
# Read from progress.txt - find the highest consecutive number starting from 1
get_next_part() {
  local n=1
  while grep -q "^$(printf "%02d" $n)$" progress.txt 2>/dev/null; do
    n=$((n + 1))
  done
  echo $n
}

get_cdn_url() {
  local ID=$1
  curl -s -H "Accept: application/octet-stream" -H "Authorization: Bearer $(gh auth token)" \
    "https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/$ID" \
    -D - -o /dev/null 2>/dev/null | grep -i "^location:" | tr -d '\r' | cut -d' ' -f2
}

download_part() {
  local ID=$1 NAME=$2 SIZE=$3
  local OUT="parts/$NAME"
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
  # -C - resumes partial downloads
  curl -L -C - -o "$OUT" "$URL" --retry 3 --retry-delay 5 -s
  local ACTUAL=$(stat -c%s "$OUT" 2>/dev/null || echo 0)
  if [ "$ACTUAL" = "$SIZE" ]; then
    echo "OK $NAME"
  else
    echo "PARTIAL $NAME ($ACTUAL/$SIZE)"
    return 1
  fi
}

# Try to append the next sequential part(s)
# Returns 0 if at least one part was appended
try_append_sequential() {
  local appended=0
  while true; do
    local NEXT=$(get_next_part)
    if [ "$NEXT" -gt 30 ]; then
      break
    fi
    local PADDED=$(printf "%02d" $NEXT)
    local PART="doa4-250m.part_$PADDED"
    local EXPECTED_SIZE=$(grep "$PART" asset_list.txt | awk '{print $3}')
    if [ -f "parts/$PART" ] && [ "$(stat -c%s "parts/$PART")" = "$EXPECTED_SIZE" ]; then
      # SPECIAL CASE: part 01 when ISO already has 02+03+04 (prepend fix)
      if [ "$NEXT" = "1" ] && [ -f "doa4.iso" ] && [ "$(stat -c%s doa4.iso)" = "786432000" ]; then
        echo "PREPEND part 01 to existing ISO (fixing order)..."
        cat "parts/$PART" doa4.iso > doa4.iso.new
        mv doa4.iso.new doa4.iso
      else
        cat "parts/$PART" >> doa4.iso
      fi
      rm -f "parts/$PART"
      echo "$PADDED" >> progress.txt
      echo "Appended part $PADDED (sequential)"
      appended=1
    else
      break
    fi
  done
  return $appended
}

# Main loop: download in batches of 4, append sequentially after each batch
echo "Starting. Next expected part: $(get_next_part)"

# First, try to append anything that's already complete and sequential
try_append_sequential || true

BATCH=()
while read -r ID NAME SIZE; do
  # Skip parts already in progress.txt
  PARTNUM=$(echo "$NAME" | grep -o 'part_[0-9]*' | grep -o '[0-9]*' | sed 's/^0*//')
  [ -z "$PARTNUM" ] && PARTNUM=0
  PADDED=$(printf "%02d" $PARTNUM)
  if grep -q "^$PADDED$" progress.txt 2>/dev/null; then
    continue
  fi
  # Skip if already complete on disk
  if [ -f "parts/$NAME" ] && [ "$(stat -c%s "parts/$NAME")" = "$SIZE" ]; then
    continue
  fi
  
  BATCH+=("$ID $NAME $SIZE")
  if [ ${#BATCH[@]} -eq 4 ]; then
    for item in "${BATCH[@]}"; do
      download_part $item &
    done
    wait
    BATCH=()
    # Append sequentially (only in-order parts)
    try_append_sequential || true
    echo "Progress: $(get_next_part)/30 next, ISO: $(stat -c%s doa4.iso 2>/dev/null || echo 0) bytes"
    df -h /home/hatch | tail -1
  fi
done < asset_list.txt

# Handle remaining batch
for item in "${BATCH[@]}"; do
  download_part $item &
done
wait
try_append_sequential || true

# Verify: 29*262144000 + 232716288 = 7834892288
EXPECTED=7834892288
ACTUAL=$(stat -c%s doa4.iso 2>/dev/null || echo 0)
echo "Final: $ACTUAL / $EXPECTED"
if [ "$ACTUAL" = "$EXPECTED" ]; then
  echo "SUCCESS - ISO complete"
else
  echo "INCOMPLETE - next part: $(get_next_part)"
fi
