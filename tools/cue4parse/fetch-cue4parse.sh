#!/bin/bash
# fetch-cue4parse.sh — fetch CUE4Parse on demand. Binaries are NEVER committed.
# Usage: bash tools/cue4parse/fetch-cue4parse.sh [dest-dir]
set -euo pipefail
PIN="${CUE4PARSE_PIN:-0.3.1.164}"
DEST="${1:-$(dirname "$0")/vendor}"
mkdir -p "$DEST"
if [ -x "$DEST/CUE4Parse" ]; then
  echo "==> CUE4Parse already present at $DEST/CUE4Parse"
  exit 0
fi
command -v dotnet >/dev/null 2>&1 || {
  echo "!! dotnet not found — CUE4Parse CLI needs the .NET runtime."
  echo "   Install: https://dotnet.microsoft.com/download  (then re-run)"
  exit 1
}
echo "==> downloading CUE4Parse ${PIN} ..."
curl -sSL --retry 3 -o "$DEST/cue4parse.zip" \
  "https://github.com/FabianFG/CUE4Parse/releases/download/${PIN}/CUE4Parse-${PIN}-linux-x64.zip" \
  || { echo "!! release asset not found for ${PIN} — check https://github.com/FabianFG/CUE4Parse/releases"; exit 1; }
python3 -c "import zipfile; zipfile.ZipFile('$DEST/cue4parse.zip').extractall('$DEST')"
chmod +x "$DEST/CUE4Parse"
echo "==> CUE4Parse ready at $DEST/CUE4Parse"
