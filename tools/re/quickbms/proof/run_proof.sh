#!/bin/sh
# Proof run for tools/re/quickbms (reference tooling only).
# Static lint only — no QuickBMS binary is executed, no game file is
# read, and nothing is written anywhere except stdout.
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$DIR/bms_lint.py" "$DIR"/scripts/*.bms
echo "PROOF PASS: all bundled .bms scripts lint-clean"
