#!/bin/sh
# Proof run for tools/re/iso9660 (reference tooling only).
# Everything it creates lives under /tmp and is deleted at the end.
# It never writes into this repo and never touches a commercial image.
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK=$(mktemp -d /tmp/wh-iso9660-proof.XXXXXX)
trap 'rm -rf "$WORK"' EXIT INT TERM
python3 "$DIR/proof/make_test_iso.py" "$WORK/test.iso"
python3 "$DIR/iso9660_extract.py" "$WORK/test.iso" --list-only
python3 "$DIR/iso9660_extract.py" "$WORK/test.iso" --outdir "$WORK/out"
test "$(cat "$WORK/out/HELLO.TXT")" = "hello world!"
test "$(cat "$WORK/out/DOCS/INNER.TXT")" = "inner file"
# Same image wrapped as 2352-byte raw Mode-2 sectors:
python3 "$DIR/proof/make_test_iso.py" "$WORK/test.bin" --raw
python3 "$DIR/iso9660_extract.py" "$WORK/test.bin" --outdir "$WORK/out-raw"
test "$(cat "$WORK/out-raw/HELLO.TXT")" = "hello world!"
test "$(cat "$WORK/out-raw/DOCS/INNER.TXT")" = "inner file"
echo "PROOF PASS: synthetic ISO9660 listed and extracted, contents match"
