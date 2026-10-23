# DOA4 Phase 14 — Job 1: ISO assembly CLOSEOUT

**Verification, stated plainly:** the local assembly of
release `doa4-iso-v1` is complete and verified.

- **Size: exactly 7,834,892,288 B** (29 × 262,144,000 B parts
  + part_30 at 232,716,288 B).
- **Per-part digests: all 30 matched** the GitHub release
  asset sha256 digests before their bytes were written into
  the sparse ISO (phase-13 assembler discipline; log:
  scratch `p13/iso_assembly_log.json`, 30 landed entries with
  per-part sha256 + offset).
- **Whole-ISO sha256 (computed 2026-10-22 over the assembled
  file): `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa`.**

Assembly history (phase 14): resumed at 10/30 from phase 13;
part_10's in-flight download finished on its own (never
killed, never duplicated) and verified; parts 12–30 landed
under the assembler, with two transport incidents — the
egress proxy intermittently killed gh downloads (stream
CANCEL / connection refused), aborting the assembler on
parts 17 and 25; each time the unverified partial was
deleted and the lane relaunched under the supervisor
(`phase14/tools/iso_supervisor_p14.py`), which re-runs the
assembler (still digest-verifying every part) until 30/30.
No part was ever written without its digest matching.

Pre-clear extracts (taken from the assembled ISO BEFORE the
clear, per the task order — the provenance pass's ISO reads
also all happened before the clear):

- `mot.afs` whole (75,393,024 B, sha256 5329bc05…) and
  `default.xex` whole (16,367,616 B, sha256 56b68dec…),
  dic/ximejp*.dic (3, whole), 256 KiB TOC snapshots of
  cmn/snd/spr/stg/avt .afs → release
  `doa4-iso-extracts-20261022` (asset `iso_extracts.tar`,
  94,049,280 B, sha256 09e3ecc2…, API-verified; per-file
  manifest `phase14/iso-extracts-manifest.json`).
- The 26 definition files were already released in phase 13
  (`doa4-anime-definition-20261022`, manifest in git).

Clear (one-store rule; the ISO is byte-safe in release
`doa4-iso-v1` — every byte of the local assembly came from
digest-verified parts of that release): the local
`p13/doa4.iso`, the mirror tar part copies under
`p14/mirrorparts/` (all digest-verified against
`doa4-mirror-20261017`; their provenance results are in
`phase14/PROVENANCE.md`), the local `iso_extracts.tar`
(released), and this lane's extracted-file scratch copies
were deleted after this verification was recorded. The full
clear log is in `phase14/PHASE14-STATE.md`. The assembled
ISO is recoverable at any time by re-running the phase-13
assembler against `doa4-iso-v1`; its whole-ISO sha256 above
is the re-assembly check value.
