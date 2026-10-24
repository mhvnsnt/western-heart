#!/usr/bin/env bash
# locate_paks.sh — find Tekken 8 game containers on the box / mounted storage.
# T8 (UE5, IoStore) ships Polaris/Content/Paks/*.utoc + *.ucas + *.pak (+ .sig).
# Usage: tools/extract/t8/locate_paks.sh [extra_root ...]   -> prints T8_PAKS=<dir> when found.
set -euo pipefail
roots=("$@" /workspace /home/box /cursor/stores /mnt /media /opt)
found=""
for r in "${roots[@]}"; do
  [ -d "$r" ] || continue
  while IFS= read -r f; do
    d=$(dirname "$f"); case "$found" in *"$d"*) ;; *) found="$found $d";; esac
  done < <(find "$r" -xdev \( -iname 'pakchunk*-Windows*.utoc' -o -iname 'Polaris*.utoc' -o -iname 'global.utoc' \) 2>/dev/null)
done
if [ -z "$found" ]; then
  echo "NO T8 PAKS FOUND. Owner step: copy <Steam>/steamapps/common/TEKKEN 8/Polaris/Content/Paks/ to the box (see docs/tech/T8-EXTRACTION.md §1)." >&2
  exit 2
fi
for d in $found; do
  echo "T8_PAKS=$d  ($(ls "$d" | wc -l) files, $(du -sh "$d" | cut -f1))"
done
