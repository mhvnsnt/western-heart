#!/bin/bash
# Phase 17 Job 1: faithful per-section Ghidra project for DOA4 default.xex.
# Input : the XEX's decrypted PE (default_pe.bin lineage, phases 11-15),
#         sha256 eaa1885a2322df0cf1e8c236a0405a37eeb31b7fdb12b5392a6acc2cabce99d0.
# Method: FORCED PE loader import (-loader PE -processor
#         PowerPC:BE:32:default). Without the force, Ghidra's MZ
#         loader claims the .bin file (MZ magic) and imports it as
#         x86:LE:16 Real Mode with a 21-bit ram space ending
#         0x10FFEF -- that misdetection IS phase 16 SS3b's blocker.
#         With the PE loader, sections land at header imagebase
#         0x400000 + RVA), then SetBaseP17.java pre-script shifts the
#         image base to the TRUE XEX VA base 0x82000000 BEFORE analysis,
#         so every section sits at its true VA:
#           .rdata VA=file+0x82000000  .text VA=file+0x8200E800
#           .data  VA=file+0x8201DE00  (uniform shift: VA=0x82000000+RVA)
#         ExportP17.java post-script emits the acceptance evidence
#         (block map, registry/string xrefs, target decompiles).
# RAM   : VM is low-memory; heap capped at 1024M (phase-16 proven size).
set -euo pipefail
export JAVA_TOOL_OPTIONS="-Xmx1024M"
export JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1
GHIDRA=/home/hatch/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC
PE=${1:?usage: build_ghidra_project_p17.sh <default_pe.bin> <workdir>}
WORK=${2:?usage: build_ghidra_project_p17.sh <default_pe.bin> <workdir>}
SCRIPTS="$(cd "$(dirname "$0")" && pwd)/ghidra-scripts"
mkdir -p "$WORK/proj" "$WORK/out"
"$GHIDRA/support/analyzeHeadless" "$WORK/proj" doa4_p17 \
  -import "$PE" \
  -loader PeLoader \
  -processor PowerPC:BE:32:default \
  -max-cpu 2 \
  -scriptPath "$SCRIPTS" \
  -preScript SetBaseP17.java \
  -postScript ExportP17.java "$WORK/out" \
echo "--- acceptance ---"
cat "$WORK/out/acceptance.txt" || true
