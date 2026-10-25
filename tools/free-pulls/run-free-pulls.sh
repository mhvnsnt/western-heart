#!/usr/bin/env bash
# run-free-pulls.sh — one-pass check/pull for the WH free-pulls kit.
#   --check : no network. Syntax-checks scripts, validates JSON. Safe for CI.
#   --pull  : small live list/search calls against no-auth APIs + font fetch.
#             Auth-gated/dead endpoints run honest check/probe paths only.
# Never overwrites sources. Never prints credentials (none are used here).
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0
say() { printf '%s\n' "$*"; }
ok()   { say "PASS $1"; }
bad()  { say "FAIL $1"; FAIL=1; }

if [ "${1:-}" = "--check" ]; then
  for f in "$DIR"/apis/*.py "$DIR"/gpu/*.py "$DIR"/gpu/gpu-queue/*.py "$DIR"/tools/*.py; do
    [ -f "$f" ] || continue
    if python3 -m py_compile "$f" 2>/dev/null; then ok "$f"; else bad "$f"; fi
  done
  for f in "$DIR"/tools/*.sh; do
    [ -f "$f" ] || continue
    if bash -n "$f" 2>/dev/null; then ok "$f"; else bad "$f"; fi
  done
  for f in "$DIR"/apis/*.json "$DIR"/gpu/*.json; do
    [ -f "$f" ] || continue
    if python3 -m json.tool "$f" >/dev/null 2>&1; then ok "$f"; else bad "$f"; fi
  done
  [ -f "$DIR"/gpu/webgpu_demo.html ] && ok "$DIR/gpu/webgpu_demo.html"
  say "check done, FAIL=$FAIL"
  exit $FAIL
fi

if [ "${1:-}" = "--pull" ]; then
  OUT="${2:-$DIR/pull-out}"
  mkdir -p "$OUT"
  say "pull-out dir: $OUT"
  python3 "$DIR/apis/polyhaven.py" --list --type textures --limit 2 || bad "polyhaven list"
  python3 "$DIR/apis/ambientcg.py" --search fabric --limit 2 || bad "ambientcg search"
  python3 "$DIR/apis/huggingface.py" --models image-to-3d --limit 2 || bad "huggingface models"
  python3 "$DIR/apis/sketchfab.py" --search torso --count 2 || bad "sketchfab search"
  python3 "$DIR/apis/fma.py" --probe || say "NOTE fma probe: endpoint dead, expected (see README)"
  python3 "$DIR/apis/opengameart.py" --probe || say "NOTE opengameart probe: no JSON API, expected (see README)"
  python3 "$DIR/apis/kaggle.py" || say "NOTE kaggle: check-only without auth, expected (see README)"
  python3 "$DIR/apis/google_fonts.py" --families "Bebas Neue" "Inter:400;700" "Oswald:600;700" --out "$OUT/fonts" || bad "google fonts"
  say "pull done, FAIL=$FAIL"
  exit $FAIL
fi

say "usage: run-free-pulls.sh --check | --pull [outdir]"
exit 2
