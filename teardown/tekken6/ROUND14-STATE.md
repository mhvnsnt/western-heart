# Tekken 6 PSP — ROUND 14 STATE

Branch: `teardown/tekken6-round14-textures-vtype7` stacked on PR #558
(`teardown/tekken6-round13-renderer-batches` @ f9170bd8).
Started: 2026-10-22.

## Input note (recorded at lane start, own-eyes)

`~/workspace/_t6r4-work/` (the read-only CLEAN bulk + decode_all76
outputs named in the round-13 docs) is NOT present on this VM at lane
start — verified by direct `ls`. The EBOOT used by rounds 11–13 is
in-tree at `teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` (4.0 MB),
and the bulk/decoded76 inputs are regenerable byte-exactly from the
ISO on GitHub release `tekken6-psp-v1` (repo `mhvnsnt/western-heart`)
using the in-tree proven chain: `tools/bulk_decrypt.py` (per-1024B
sector cipher) → `tools/decode_all76.py` (76/76 adler-exact oracle).
Regeneration, when run, lands in scratch OUTSIDE the repo
(`~/workspace/_t6r14-work/`) and is verified against the round-5/13
hashes/counts before any job consumes it. No job result below rests
on an unverified regeneration.

## Jobs

1. **NTPP PIXELS — descriptor factory** — IN PROGRESS.
   Hunt: archive-loader-side code that populates the proven shared
   image descriptor (desc+0x08 format word / +0x0a width / +0x0c
   height / +0x28 pixel pointer; CLUT = sibling pointer, format =
   descriptor format word itself; builders CMODE/CBP/CLOAD
   @0x08acce14/0x08acce50, texture bind @0x08acd030) from NTPP
   section bytes. Gate: per-section field derivation proven from
   code → one-section textured GLB with viewed render + embedded
   image counted; batch only if the factory resolves. Exhaustive
   negative + STOP is the honest alternative — no header guessing.

2. **VTYPE COLOR-FORMAT 7 LAYOUT** — PENDING.
   The 400-failure class from round 13 (`0x*33d` family, stride
   measured 20/24 B). Derive field widths from the VTYPE nibbles;
   validate against descriptor bbox containment (all verts),
   unit normals, weights summing to 128, and a VIEWED render.
   Ship only on >=3 sections from different packages validating.

3. **COM B4 CONTINUATION** — PENDING.
   (a) Font glyph→button map from the game font's glyph order;
   proven when >=2 known move names decode to known inputs; then
   additive v2 moveset JSONs with glyph-decoded command fields.
   (b) Compression probes on pointer-table slots 25/26/30
   (zlib/gzip, LZ77/LZ4 magic, raw-deflate trial, per-1024 cipher);
   'compressed' only on a structured successful decode.

4. **CLOSEOUT** — PENDING. This file final + WIRING-INVENTORY
   round-14 section appended.

## Method notes
- Capstone targeted disassembly only; NO full Ghidra analysis
  (VM RAM ~1.6 GB free at lane start in the brief; measured
  7.7 GiB total / ~0.6 GiB available at start — targeted reads only).
- Skeletons: ONLY the r11 set (`models/SKELETON-SUPERSEDE.md`).
- Palette unit→bone: CAPTURE-ONLY (round 12 terminal) — not re-hunted.
- Additions-only; no `git add -A`; pathspec commits after EVERY job.
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU, unique filename per render.
- `/tmp` is a volatile 512 MB tmpfs — scratch lives in
  `~/workspace/_t6r14-work/` or the repo tree, never `/tmp`.

## Deletions
None.
