#!/bin/bash
# DOA4 ISO downloader v2 - BULLETPROOF sequential assembly
# - Downloads 4 parts in parallel (NO resume, fresh downloads to avoid corruption)
# - Appends STRICTLY in order 01,02,03,...,30
# - Verifies ISO size before each append: ISO must be exactly (N-1)*262144000 before appending part N
# - Verifies part size matches expected before appending
set -e
cd ~/workspace/doa4-bass
mkdir -p parts

PART_SIZE=262144000

get_cdn_url() {
  local ID=$1
  curl -s -H "Accept: application/octet-stream" -H "Authorization: Bearer $(gh auth token)" \
    "https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/$ID" \
    -D - -o /dev/null 2>/dev/null | grep -i "^location:" | tr -d '\r' | cut -d' ' -f2
}

# Get next part number (first missing from progress.txt, starting at 1)
get_next_part() {
  local n=1
  while grep -q "^$(printf "%02d" $n)$" progress.txt 2>/dev/null; do
    n=$((n + 1))
  done
  echo $n
}

# Download a single part (FRESH, no resume to avoid corruption)
download_part_fresh() {
  local ID=$1 NAME=$2 SIZE=$3
  local OUT="parts/$NAME"
  # Skip if already correct on disk
  if [ -f "$OUT" ] && [ "$(stat -c%s "$OUT")" = "$SIZE" ]; then
    echo "SKIP $NAME (already correct)"
    return 0
  fi
  # Delete any corrupt/partial file first
  rm -f "$OUT"
  local URL=$(get_cdn_url $ID)
  if [ -z "$URL" ]; then
    echo "FAIL $NAME (no CDN URL)"
    return 1
  fi
  echo "DL $NAME..."
  curl -L -o "$OUT" "$URL" --retry 3 --retry-delay 5 -s
  local ACTUAL=$(stat -c%s "$OUT" 2>/dev/null || echo 0)
  if [ "$ACTUAL" = "$SIZE" ]; then
    echo "OK $NAME ($ACTUAL bytes)"
    return 0
  else
    echo "CORRUPT $NAME ($ACTUAL/$SIZE) - deleting"
    rm -f "$OUT"
    return 1
  fi
}

# Append the next sequential part if ready
# Returns 0 if appended, 1 if not ready
append_next() {
  local NEXT=$(get_next_part)
  if [ "$NEXT" -gt 30 ]; then
    return 1
  fi
  local PADDED=$(printf "%02d" $NEXT)
  local PART="doa4-250m.part_$PADDED"
  local EXPECTED_SIZE=$(grep "$PART" asset_list.txt | awk '{print $3}')
  local PART_FILE="parts/$PART"

  # Check part exists and is correct size
  if [ ! -f "$PART_FILE" ]; then
    return 1
  fi
  local ACTUAL_SIZE=$(stat -c%s "$PART_FILE")
  if [ "$ACTUAL_SIZE" != "$EXPECTED_SIZE" ]; then
    echo "SKIP append $PADDED (wrong size $ACTUAL_SIZE != $EXPECTED_SIZE)"
    return 1
  fi

  # CRITICAL: Verify ISO is at the correct size before appending
  # ISO should be (NEXT-1) * PART_SIZE bytes
  local EXPECTED_ISO_SIZE=$(( (NEXT - 1) * PART_SIZE ))
  local ACTUAL_ISO_SIZE=$(stat -c%s doa4.iso 2>/dev/null || echo 0)
  if [ "$ACTUAL_ISO_SIZE" != "$EXPECTED_ISO_SIZE" ]; then
    echo "FATAL: ISO size mismatch before appending part $PADDED"
    echo "  Expected ISO: $EXPECTED_ISO_SIZE, Actual: $ACTUAL_ISO_SIZE"
    echo "  Refusing to append out of order. Manual intervention required."
    return 2
  fi

  # Append
  cat "$PART_FILE" >> doa4.iso
  rm -f "$PART_FILE"
  echo "$PADDED" >> progress.txt
  echo "APPENDED part $PADDED (ISO now $(stat -c%s doa4.iso) bytes)"
  return 0
}

# Keep appending while the next part is ready
drain_sequential() {
  while append_next; do
    :
  done
}

echo "=== DOA4 Download v2 ==="
echo "Next part: $(get_next_part)"
echo "ISO size: $(stat -c%s doa4.iso 2>/dev/null || echo 0)"
echo ""

# Drain any already-complete sequential parts first
drain_sequential

# Main loop: download next 4 needed parts in parallel, then drain
while true; do
  NEXT=$(get_next_part)
  if [ "$NEXT" -gt 30 ]; then
    echo "All 30 parts appended!"
    break
  fi

  # Build batch of next 4 needed parts
  BATCH=()
  for i in $(seq $NEXT $((NEXT + 3))); do
    if [ "$i" -gt 30 ]; then break; fi
    PADDED=$(printf "%02d" $i)
    LINE=$(grep "doa4-250m.part_$PADDED" asset_list.txt)
    ID=$(echo "$LINE" | awk '{print $1}')
    NAME=$(echo "$LINE" | awk '{print $2}')
    SIZE=$(echo "$LINE" | awk '{print $3}')
    # Skip if already in progress.txt
    if grep -q "^$PADDED$" progress.txt 2>/dev/null; then
      continue
    fi
    # Skip if already correct on disk
    if [ -f "parts/$NAME" ] && [ "$(stat -c%s "parts/$NAME")" = "$SIZE" ]; then
      continue
    fi
    BATCH+=("$ID $NAME $SIZE")
  done

  if [ ${#BATCH[@]} -eq 0 ]; then
    # Nothing to download, try draining
    drain_sequential
    AFTER=$(get_next_part)
    if [ "$AFTER" = "$NEXT" ]; then
      echo "STUCK: next=$NEXT, nothing to download, nothing to append"
      break
    fi
    continue
  fi

  # Download batch in parallel
  for item in "${BATCH[@]}"; do
    download_part_fresh $item &
  done
  wait

  # Drain sequentially appended parts
  drain_sequential

  echo "--- Progress: next=$(get_next_part)/30, ISO=$(stat -c%s doa4.iso) bytes ---"
  df -h /home/hatch | tail -1
  echo ""
done

# Final verification
EXPECTED_TOTAL=7834892288
ACTUAL_TOTAL=$(stat -c%s doa4.iso 2>/dev/null || echo 0)
echo "=== FINAL ==="
echo "ISO: $ACTUAL_TOTAL / $EXPECTED_TOTAL"
if [ "$ACTUAL_TOTAL" = "$EXPECTED_TOTAL" ]; then
  echo "SUCCESS - ISO complete and verified"
else
  echo "INCOMPLETE"
fi
