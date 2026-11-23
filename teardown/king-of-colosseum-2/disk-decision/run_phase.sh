#!/bin/bash
# Run a phase of KoC2 push batches in order. Stops on first failure.
# Usage: run_phase.sh <phase-name> <spec1> <spec2> ...
# Each spec is a name under specs/ (without .json).
set -uo pipefail
WD=~/workspace/koc2-disk-decision
PHASE="$1"; shift
echo "=== PHASE $PHASE starting $(date) ===" | tee "$WD/batches/phase-$PHASE.log"
FAILED=0
for spec in "$@"; do
  echo "--- $spec $(date) ---" | tee -a "$WD/batches/phase-$PHASE.log"
  if python3 -u "$WD/push_batch.py" "$WD/specs/$spec.json" 2>&1 | tee "$WD/batches/$spec.log"; then
    echo "$spec OK" | tee -a "$WD/batches/phase-$PHASE.log"
  else
    echo "$spec FAILED (exit ${PIPESTATUS[0]})" | tee -a "$WD/batches/phase-$PHASE.log"
    FAILED=1
    break
  fi
done
if [ "$FAILED" = 0 ]; then
  echo "=== PHASE $PHASE COMPLETE $(date) ===" | tee -a "$WD/batches/phase-$PHASE.log"
else
  echo "=== PHASE $PHASE STOPPED ON FAILURE $(date) ===" | tee -a "$WD/batches/phase-$PHASE.log"
  exit 1
fi
