#!/bin/bash
# gdrive-dl.sh <file-id> <output-name>  -- downloads a public Google Drive file
# Handles the virus-scan "Download anyway" confirm gate. Resume-capable (wget -c).
set -u
ID="$1"; OUT="$2"
TMP="$(mktemp /tmp/gd-XXXXXX.html)"
wget -q --timeout=60 -O "$TMP" "https://drive.google.com/uc?export=download&id=$ID" || { echo "FAIL: initial page"; rm -f "$TMP"; exit 1; }
UUID=$(grep -o 'name="uuid" value="[^"]*"' "$TMP" | head -1 | sed 's/.*value="//;s/"//')
CONFIRM=$(grep -o 'name="confirm" value="[^"]*"' "$TMP" | head -1 | sed 's/.*value="//;s/"//')
rm -f "$TMP"
if [ -z "$UUID" ]; then
  # no virus gate — direct download
  wget -c --timeout=90 --tries=10 -O "$OUT" "https://drive.google.com/uc?export=download&id=$ID"
else
  wget -c --timeout=90 --tries=10 -O "$OUT" "https://drive.usercontent.google.com/download?confirm=${CONFIRM:-t}&id=$ID&uuid=$UUID"
fi
echo "DONE: $OUT"
ls -la "$OUT"
