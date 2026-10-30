# tools/ttt2-section-decode — TTT2 section decoder

Decodes `0ff512ed` TTT2 container files section by section, using the head
table each file carries after its 12-byte header (BE u32 per 128 KB section;
entry `k+1` is section `k`'s decoded size). This is the decoder that closed
the data001 section-1570 and data028 chunk-2383 blockers
(see `teardown/tekken-tag-tournament-2/DATA001-DATA028-DECODE-20261030.md`).

## Files

- `lzx_exact.c` — the ReactOS/cabextract LZX decoder (LGPL; see its header)
  with a bit-exact resume extension: `ex_base`, `ex_next_byte`,
  `ex_next_bit`, `ex_entry_bit` on `LZXstate`. At every return the next
  unconsumed bit position is saved; at entry it is restored, so slices
  resume exactly inside verbatim/aligned blocks. Uncompressed blocks resume
  byte-exact. No other decoder behavior is changed.
- `lzx.h` — the decoder header, including the resume-extension fields.
- `secdec3.c` — single-section decoder (debug / spot-check one section).
  Usage: `secdec3 <file> <sec_start> <sec_inlen> <expected_out> <outpath>`.
- `batchdec3.c` — whole-file batch decoder: loads the file once, decodes
  every head-table section in order, concatenates output, logs one line per
  section. Usage:
  `batchdec3 <file> <outpath> <logpath> <ntab> <sec0_stream_start>`.
  Section 0's stream starts at `sec0_stream_start` (after header + table);
  later sections start at file offsets `k*131072`; the last section ends
  at EOF.

## Build

    gcc -O2 -o secdec3 secdec3.c
    gcc -O2 -o batchdec3 batchdec3.c

Both are self-contained (they `#include "lzx_exact.c"`); no extra linking.

## Reproduce the data001 / data028 decodes

Pull the sources from release `ttt2-7z-v1` (no game binaries are committed
in this repo):

    python3 tools/ttt2_virtual_god.py --pull

Then:

    ./batchdec3 pulls/data001.bin decoded-data001.bin batchdec-data001.log 2944 11788
    ./batchdec3 pulls/data028.bin decoded-data028.bin batchdec-data028.log 781 3136

Expected: every log line reads `EXACT` (or `STORED`); data001 totals
851,749,584 B; data028 totals 120,285,856 B. Section 440 of data028 is the
interesting one: it needs 1 chunk-start resync and 2 block-scans (see the
decode doc); everything else decodes straight.

## Method (summary)

Fresh LZX state per section; chunk starts use fresh bits. A section
starting with BE u16 0 whose table entry equals input length minus 2 is a
stored raw copy. A chunk is done at a block boundary with 16 or fewer bytes
of chunk input left (bit padding; no real block fits in 16 bytes). On a
chunk-start failure, retry the size prefix at -1/+1. On a mid-chunk failure
at a block boundary, scan forward up to 32 bytes for the next valid
compressed block header (type 1/2, length at most 32768, full table
validation). Chunk data never crosses its section end. Final partial
blocks are recovered by binary-searching the largest succeeding output
length. See the decode doc for the full account, including dead ends.
