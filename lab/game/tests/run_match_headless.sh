#!/bin/sh
# Headless gameplay test: full CPU-vs-CPU match through the real input path; must finish with a winner.
cd "$(dirname "$0")/.." && out=$(godot --headless --path . --quit-after 20000 -- --autoplay --quit-after-match 2>&1 | grep "MATCH RESULT")
echo "$out"; echo "$out" | grep -qE "wins=\[(2, [01]|[01], 2)\]" && echo "MATCH TEST: PASS" || { echo "MATCH TEST: FAIL"; exit 1; }
