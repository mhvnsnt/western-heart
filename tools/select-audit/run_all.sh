#!/usr/bin/env bash
# run_all.sh <baseUrl> <outDir> — one fresh node+browser per fighter (crash-isolated), appends results.jsonl
set -u; base=$1; out=$2; here=$(cd "$(dirname "$0")" && pwd)
export PUPPETEER=${PUPPETEER:-/tmp/whp/node_modules/puppeteer-core}
mkdir -p "$out"; : > "$out/results.jsonl"
[ -s "$out/ids.txt" ] || timeout 120 node "$here/capture.js" "$base" "$out" __none__ >/dev/null 2>&1
grep -q . "$out/ids.txt" 2>/dev/null || { node -e "1"; }
for id in $(cat "$out/ids.txt"); do
  timeout 180 node "$here/capture.js" "$base" "$out" "$id" 2>&1 | tail -1
  grep -q "\"id\":\"$id\"" "$out/results.jsonl" || echo "{\"id\":\"$id\",\"error\":\"capture timeout/crash\"}" >> "$out/results.jsonl"
done
