#!/usr/bin/env bash
# extract.sh — Tekken 8 Paks -> exported assets, repeatable, no Steam needed once Paks are on disk.
# Needs: dotnet 8 SDK (installs to ~/.dotnet if missing), T8_AES_KEY in env (NEVER committed), T8_PAKS dir.
# Usage: T8_AES_KEY=0x... tools/extract/t8/extract.sh <T8_PAKS> <OUT> [filter ...]
#   default filters = Alisa anims + skeleton, menu/select UI, chara select data:
#   Polaris/Content/Character/Common/Anim  (paths verified on first run; see MANIFEST written to OUT)
set -euo pipefail
PAKS=${1:?T8 Paks dir}; OUT=${2:?out dir}; shift 2
: "${T8_AES_KEY:?set T8_AES_KEY (0x + 64 hex) in the environment; never write it to a file in the repo}"
HERE=$(cd "$(dirname "$0")" && pwd)
command -v dotnet >/dev/null || { curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0 --install-dir "$HOME/.dotnet"; export PATH="$HOME/.dotnet:$PATH"; }
mkdir -p "$OUT"
FILTERS=("$@"); [ ${#FILTERS[@]} -eq 0 ] && FILTERS=(alisa Alisa /UI/ Select CharaSelect Customize Menu)
dotnet run --project "$HERE/cue4-export" -c Release -- \
  --paks "$PAKS" --out "$OUT" --game GAME_UE5_LATEST --filters "${FILTERS[@]}"
echo "done -> $OUT (MANIFEST.tsv lists every exported package with size and type)"
