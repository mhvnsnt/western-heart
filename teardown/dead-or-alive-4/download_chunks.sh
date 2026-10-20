#!/bin/bash
# Chunked download of DOA4 ISO -> GitHub Release (disk-safe)
# v2: 250MB chunks (Archive.org truncates 500MB range requests at ~518.9MB)
#     + retry logic with resume. PROVEN WORKING 2026-10-13.
# DO NOT REPLACE without verifying the replacement actually works.
ISO_URL="https://archive.org/download/dead-or-alive-4-pal-ntscu/Dead%20or%20Alive%204%20%5BPAL%5D%5BNTSCU%5D.iso"
TOTAL_SIZE=7834892288  # 7.30GB
CHUNK_SIZE=262144000   # 250MB
RELEASE="doa4-iso-v1"
REPO="mhvnsnt/western-heart"
LOG="doa4-chunk-upload.log"
MAX_RETRIES=5

cd ~/workspace/game-reverse-engineering/dead-or-alive/doa4 || exit 1

gh release view $RELEASE --repo $REPO >/dev/null 2>&1 || gh release create $RELEASE --repo $REPO --title "Dead or Alive 4 ISO" --notes "DOA4 Xbox 360 ISO split into 250MB chunks. Reassemble: cat doa4-250m.part_* > 'DOA4.iso'" 2>&1 | head -3

UPLOADED=$(gh release view $RELEASE --repo $REPO --json assets -q '.assets[].name' 2>/dev/null)

NUM_CHUNKS=$(( (TOTAL_SIZE + CHUNK_SIZE - 1) / CHUNK_SIZE ))
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Starting chunked download v2: $NUM_CHUNKS chunks of 250MB" | tee -a $LOG

for i in $(seq 1 $NUM_CHUNKS); do
  CHUNK_NAME=$(printf "doa4-250m.part_%02d" $i)
  if echo "$UPLOADED" | grep -q "$CHUNK_NAME"; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Skipping $CHUNK_NAME (already on release)" | tee -a $LOG
    continue
  fi

  START=$(( (i-1) * CHUNK_SIZE ))
  END=$(( i * CHUNK_SIZE - 1 ))
  if [ $END -ge $TOTAL_SIZE ]; then END=$(( TOTAL_SIZE - 1 )); fi
  EXPECTED=$(( END - START + 1 ))

  SUCCESS=0
  for retry in $(seq 1 $MAX_RETRIES); do
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Downloading chunk $i/$NUM_CHUNKS: $CHUNK_NAME (bytes $START-$END) attempt $retry/$MAX_RETRIES" | tee -a $LOG
    if [ -f "$CHUNK_NAME" ]; then
      LOCAL_SIZE=$(stat -c%s "$CHUNK_NAME" 2>/dev/null || echo 0)
      if [ "$LOCAL_SIZE" -lt "$EXPECTED" ] && [ "$LOCAL_SIZE" -gt 0 ]; then
        RESUME_START=$(( START + LOCAL_SIZE ))
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Resuming from byte $RESUME_START" | tee -a $LOG
        curl -sL -r ${RESUME_START}-${END} -o "${CHUNK_NAME}.tmp" "$ISO_URL"
        cat "${CHUNK_NAME}.tmp" >> "$CHUNK_NAME" && rm -f "${CHUNK_NAME}.tmp"
      else
        rm -f "$CHUNK_NAME"
        curl -sL -r ${START}-${END} -o "$CHUNK_NAME" "$ISO_URL"
      fi
    else
      curl -sL -r ${START}-${END} -o "$CHUNK_NAME" "$ISO_URL"
    fi

    LOCAL_SIZE=$(stat -c%s "$CHUNK_NAME" 2>/dev/null || echo 0)
    if [ "$LOCAL_SIZE" = "$EXPECTED" ]; then
      SUCCESS=1
      break
    fi
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) SIZE MISMATCH $CHUNK_NAME attempt $retry: local=$LOCAL_SIZE expected=$EXPECTED" | tee -a $LOG
    sleep 5
  done

  if [ "$SUCCESS" != "1" ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FAILED $CHUNK_NAME after $MAX_RETRIES attempts, moving on" | tee -a $LOG
    rm -f "$CHUNK_NAME"
    continue
  fi

  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Uploading $CHUNK_NAME ($LOCAL_SIZE bytes)" | tee -a $LOG
  for uretry in 1 2 3 4 5; do
    gh release upload $RELEASE "$CHUNK_NAME" --repo $REPO --clobber 2>&1 | tail -1
    REMOTE_SIZE=$(gh release view $RELEASE --repo $REPO --json assets -q ".assets[] | select(.name==\"$CHUNK_NAME\") | .size" 2>/dev/null)
    if [ "$REMOTE_SIZE" = "$LOCAL_SIZE" ]; then break; fi
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Upload verify retry $uretry for $CHUNK_NAME" | tee -a $LOG
    sleep 10
  done

  REMOTE_SIZE=$(gh release view $RELEASE --repo $REPO --json assets -q ".assets[] | select(.name==\"$CHUNK_NAME\") | .size" 2>/dev/null)
  if [ "$REMOTE_SIZE" = "$LOCAL_SIZE" ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFIED $CHUNK_NAME ($LOCAL_SIZE bytes), deleting local" | tee -a $LOG
    rm -f "$CHUNK_NAME"
    UPLOADED="$UPLOADED $CHUNK_NAME"
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY FAILED $CHUNK_NAME: local=$LOCAL_SIZE remote=$REMOTE_SIZE" | tee -a $LOG
  fi
done

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Done" | tee -a $LOG
