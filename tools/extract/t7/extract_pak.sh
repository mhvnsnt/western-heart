#!/usr/bin/env bash
# Reusable Tekken 7 (Steam app 389730, depot 389731) extractor. One PAK at a time to save disk.
# Needs: DepotDownloader (logged in with -remember-password; NEVER commit its token files),
#        repak (github.com/trumank/repak), UModel built from github.com/gildor2/UEViewer (./build.sh),
#        python3 + pycryptodome + pygltflib + pillow.
# usage: extract_pak.sh <pak-name e.g. pakchunk0-WindowsNoEditor.pak> <work-dir> <dest-in-repo>
set -euo pipefail
PAK=$1; W=$2; DEST=$3; H=$(cd "$(dirname "$0")" && pwd)
DD=${DD:-/workspace/tools/depotdl/DepotDownloader}; REPAK=${REPAK:-repak}; UMODEL=${UMODEL:-umodel}
# Public community pak key (TekkenMods / Gneiss). Not a secret.
K=0x3d64366e7736595936452374493d366c69367049354356614243406679257652
mkdir -p "$W"; echo "TekkenGame/Content/Paks/$PAK" > "$W/fl.txt"
"$DD" -app 389730 -depot 389731 -username "${STEAM_USER:-vil3m}" -remember-password -filelist "$W/fl.txt" -dir "$W/dl"
P="$W/dl/TekkenGame/Content/Paks/$PAK"
"$REPAK" --aes-key $K unpack -o "$W/pak" \
  -i 'TekkenGame/Content/Character/Item/Meshes/*/*/*_???_1p/**' -i 'TekkenGame/Content/Character/Item/Meshes/*/*/*_fac/**' \
  -i 'TekkenGame/Content/Character/Common/**' -i 'TekkenGame/Content/UI_common/flash/SW_UI_*/**' "$P"
rm -f "$P"   # raw pak is re-downloadable; free disk immediately
python3 "$H/t7_decrypt.py" "$W/pak"
cd "$W/pak"
for f in $(ls TekkenGame/Content/Character/Item/Meshes/*/*/*/Meshes/SK_CH_*.uasset 2>/dev/null); do
  "$UMODEL" -game=tekken7 -path=. -export -gltf -notex -out="$W/out" "$f" >/dev/null 2>&1 || echo "FAIL $f" >> "$W/fail.txt"; done
for f in $(find TekkenGame -path '*Texture*' -name 'T_*.uasset' -o -path '*UI_common*' -name '*.uasset'); do
  "$UMODEL" -game=tekken7 -path=. -export -out="$W/tex" "$f" >/dev/null 2>&1 || true; done
python3 "$H/convert.py" "$W/out" "$W/tex" "$DEST"
