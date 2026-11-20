#!/bin/bash
# fetch-charmorph.sh — fetch CharMorph on demand. Large checkouts are NEVER committed.
# This script IS the install.
#
# Usage: bash tools/charmorph/fetch-charmorph.sh [dest-dir]
#   default dest: <this-dir>/vendor
#
# What it does:
#   1. Shallow-clones Upliner/CharMorph at the pinned commit (with
#      submodules — CharMorph's data/ dir is a submodule, and its
#      README says to clone --recursive) and verifies the checkout
#      (addon __init__.py present).
#   2. Prints what is still owed: the character library. CharMorph
#      0.4 downloads characters inside Blender; the Vitruvian base
#      used by this family is NOT in the main repo checkout. Until
#      characters/vitruvian/char.blend + config.yaml are present
#      (in-Blender downloader, or the CharMorph-db checkout into the
#      addon's data dir), run_charmorph_job.py fails honestly instead
#      of exporting a fake base.
#
# READ FIRST: tools/charmorph/README.md (per-base licences: Vitruvian
# CC0, Antonia/Reom CC-BY, MB-Lab base AGPL — only Vitruvian is wired).
set -euo pipefail

CHARMORPH_SHA="${CHARMORPH_SHA:-ec5e13dcd5a7330b35fa7474b3abd2f406d77bd2}"
CHARMORPH_REPO="https://github.com/Upliner/CharMorph.git"
DEST="${1:-$(dirname "$0")/vendor}"

echo "==> CharMorph fetch (commit ${CHARMORPH_SHA}) -> ${DEST}"
mkdir -p "$DEST"

if [ -f "$DEST/CharMorph/__init__.py" ]; then
  INSTALLED_SHA="$(git -C "$DEST/CharMorph" rev-parse HEAD 2>/dev/null || echo unknown)"
  if [ "$INSTALLED_SHA" = "$CHARMORPH_SHA" ]; then
    echo "==> CharMorph ${CHARMORPH_SHA} already present, skipping download"
  else
    echo "==> different commit present (${INSTALLED_SHA}), re-fetching ${CHARMORPH_SHA}"
    rm -rf "$DEST/CharMorph"
  fi
fi

if [ ! -f "$DEST/CharMorph/__init__.py" ]; then
  echo "==> cloning (shallow, recursive) ..."
  git clone --depth 1 --recursive "$CHARMORPH_REPO" "$DEST/CharMorph"
  GOT_SHA="$(git -C "$DEST/CharMorph" rev-parse HEAD)"
  if [ "$GOT_SHA" != "$CHARMORPH_SHA" ]; then
    echo "!! pinned commit ${CHARMORPH_SHA} is no longer HEAD (${GOT_SHA})."
    echo "   Re-pin CHARMORPH_SHA deliberately (or full-clone and checkout it);"
    echo "   refusing to silently install a different commit."
    rm -rf "$DEST/CharMorph"
    exit 1
  fi
fi

# verify
[ -f "$DEST/CharMorph/__init__.py" ] || { echo "!! missing __init__.py" ; exit 1; }
echo "==> verified: addon __init__.py present"

if [ -f "$DEST/CharMorph/data/characters/vitruvian/char.blend" ]; then
  echo "==> Vitruvian base present in checkout data dir"
else
  echo "!! Vitruvian base NOT in this checkout (expected: it ships via"
  echo "   CharMorph 0.4's in-Blender character downloader, or the"
  echo "   CharMorph-db library into the addon's data dir)."
  echo "   Until characters/vitruvian/char.blend + config.yaml exist,"
  echo "   tools/charmorph/run_charmorph_job.py will refuse to run."
fi

echo "==> done. Addon path for Blender: $DEST/CharMorph"
