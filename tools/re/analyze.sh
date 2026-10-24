#!/bin/bash
# analyze.sh — headless Ghidra import + auto-analysis, one command.
# Usage: ./analyze.sh <binary> <project-name> [post-script.py]
# Output: ./projects/<project-name>/ (Ghidra project), ./logs/<project-name>.log
set -euo pipefail
RE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$RE_DIR/env.sh" >/dev/null

BIN="$1"; PROJ="$2"; SCRIPT="${3:-}"
mkdir -p "$RE_DIR/projects" "$RE_DIR/logs"

ARGS=("$RE_DIR/projects" "$PROJ" -import "$BIN")
if [ -n "$SCRIPT" ]; then
  ARGS+=(-postScript "$SCRIPT")
fi

echo "==> analyzing $BIN -> project $PROJ"
"$GHIDRA_HOME/support/analyzeHeadless" "${ARGS[@]}" 2>&1 | tee "$RE_DIR/logs/${PROJ}.log"
echo "==> log: $RE_DIR/logs/${PROJ}.log"
