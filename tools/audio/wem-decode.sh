#!/bin/bash
# WH audio pipeline — Wwise .wem -> .wav via vgmstream-cli (already in
# ~/workspace/king-mods/vgmstream/ as a binary; vgmstream is MIT-licensed
# upstream code, see vgmstream repo LICENSE). Wiring target: tools/audio/.
# Usage: ./wem-decode.sh <in.wem> [out.wav]
#   default out = same name, .wav extension.
# NOTES (read before use):
#  - vgmstream-cli decodes LOOSE .wem files. A .bnk bank file is a container:
#    extract its .wem entries FIRST with a Wwise bank extractor, then run
#    this script per file. .bnk extraction is a documented remaining gap
#    (see INDEX.md) — do not feed a .bnk straight to vgmstream-cli.
#  - vgmstream cannot reproduce in-game mixing 1:1 (resampling, filters,
#    volume); decoded WAVs are source material, final mix happens in game.
set -e
VGM="${VGMSTREAM_CLI:-$HOME/workspace/king-mods/vgmstream/vgmstream-cli}"
if [ ! -x "$VGM" ]; then echo "vgmstream-cli not found at $VGM (set VGMSTREAM_CLI)"; exit 1; fi
IN="$1"; OUT="${2:-${IN%.*}.wav}"
"$VGM" -o "$OUT" "$IN"
ls -la "$OUT"
