#!/bin/bash
# fetch-mpfb2.sh — fetch MPFB 2 on demand. Large zips are NEVER committed.
# This script IS the install.
#
# Usage: bash tools/mpfb2/fetch-mpfb2.sh [dest-dir] [--with-blender]
#   default dest: <this-dir>/vendor
#   --with-blender: also pull a portable Blender 4.2+ for the LIVE path
#                   (MPFB2 requires Blender >= 4.2; our pipeline pins 4.0.2)
#
# READ FIRST: tools/mpfb2/README.md (GPL-3.0 code, CC0 assets).
set -euo pipefail

DEST="${1:-$(dirname "$0")/vendor}"
WITH_BLENDER=0
for a in "$@"; do [ "$a" = "--with-blender" ] && WITH_BLENDER=1; done

# MPFB2 nightlies live here; extension-platform zips work too.
NIGHTLY_BASE="https://files2.makehumancommunity.org/plugins"
EXT_PLATFORM="https://extensions.blender.org/add-ons/mpfb/"

echo "==> MPFB2 fetch -> ${DEST}"
mkdir -p "$DEST"

have_mpfb=0
if [ -f "$DEST/mpfb/__init__.py" ]; then have_mpfb=1; fi
if [ -d "$DEST/mpfb2-addon" ] && [ -f "$DEST/mpfb2-addon/__init__.py" ]; then have_mpfb=1; fi

if [ "$have_mpfb" = "1" ]; then
  echo "==> MPFB2 already present, skipping download"
else
  echo "==> resolving latest nightly from ${NIGHTLY_BASE} ..."
  INDEX="$(curl -sSL --retry 3 "$NIGHTLY_BASE/" | grep -oE 'mpfb2-[0-9]+\.zip' | sort -u | tail -1)"
  if [ -z "$INDEX" ]; then
    echo "!! could not resolve a nightly zip."
    echo "   GUI alternative: Blender 4.2+ > Preferences > Get Extensions > search 'MPFB' > Install"
    echo "   (${EXT_PLATFORM})"
    echo "   then copy the installed 'mpfb' dir to $DEST/ and re-run."
    exit 1
  fi
  echo "==> downloading ${INDEX} ..."
  curl -sSL --retry 3 -o "$DEST/${INDEX}" "${NIGHTLY_BASE}/${INDEX}"
  echo "==> unpacking ..."
  python3 -c "
import zipfile, os
z = zipfile.ZipFile('$DEST/${INDEX}')
names = z.namelist()
# nightly zips contain the mpfb/ package at top level
z.extractall('$DEST')
print('   entries:', len(names))
"
  # normalize: ensure $DEST/mpfb/__init__.py exists
  if [ ! -f "$DEST/mpfb/__init__.py" ]; then
    CAND="$(find "$DEST" -maxdepth 3 -name '__init__.py' -path '*mpfb*' | head -1)"
    if [ -n "$CAND" ]; then
      echo "==> addon found at $(dirname "$CAND"), linking as $DEST/mpfb"
      ln -sfn "$(dirname "$CAND")" "$DEST/mpfb"
    else
      echo "!! unpacked but no mpfb/__init__.py found — inspect $DEST"
      exit 1
    fi
  fi
fi

python3 - "$DEST" <<'EOF'
import sys, os
dest = sys.argv[1]
init = os.path.join(dest, 'mpfb', '__init__.py')
src = open(init).read()
import re
m = re.search(r'"version"\s*:\s*\(([^)]+)\)', src)
print('==> MPFB2 addon verified, version:', m.group(1) if m else 'unknown')
EOF

if [ "$WITH_BLENDER" = "1" ]; then
  B42="$DEST/blender42"
  if [ -x "$B42/blender" ]; then
    echo "==> Blender 4.2+ already present at $B42"
  else
    echo "==> pulling portable Blender 4.2 LTS (~350MB) for the MPFB2 live path..."
    mkdir -p "$B42"
    # Blender 4.2 LTS, linux-x64 (pinned patch; bump deliberately)
    BURL="https://download.blender.org/release/Blender4.2/blender-4.2.9-lts-linux-x64.tar.xz"
    curl -sSL --retry 3 "$BURL" | tar -xJ -C "$B42" --strip-components=1
    "$B42/blender" --version | head -1
  fi
  echo "==> live-path Blender: $B42/blender"
fi

echo "==> done."
echo "    data path (4.0.2, works now): sliders in suite BODY panel -> apply_mpfb_morphs.py bake"
echo "    live path (needs 4.2+):      tools/suite-jobs/run_job.py --spec jobs/mpfb2-live-01.json"
