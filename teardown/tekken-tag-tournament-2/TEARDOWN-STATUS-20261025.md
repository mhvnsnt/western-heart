# TTT2 Teardown — Status 2026-10-25 (watchdog resume)

Branch: `feat/ttt2-teardown-100`. Checkpoint: `agent-ops/checkpoints/ttt2-resume-100.json`
(status `running`; extraction phase completed this run, teardown phase in progress).

## EXTRACTION COMPLETE — 2026-10-25 14:46Z (own-eyes verified this run)

- Archive `ttt2.7z` reassembled 2026-10-25 09:12:50Z from GitHub release
  `ttt2-7z-v1` (26 chunks, 13,363,624,393 bytes), sha256
  `444ebc43959eb3277bc700dbf199e67b6ec27bf862be638658f34ec2c6c995c6` — MATCH.
- Full extraction tree at `~/workspace/_ttt2-work/reassemble/_verify-extract/`
  (`Tekken Tag Tournament 2 (EU)/`, 72 files, 13 GB):
  - `final-tree-verify-20261025.log`: **checked=72 bad=0** (14:46:41Z).
  - `7zz 25.01` full archive test: "Everything is Ok", 72 files.
  - Data0050 (170,459,136 B): py7zr fresh-process extract, crc32 `eb284c37` = header.
  - Data0051 (54 MB): 7zz single-file extract, "Everything is Ok".
- The `_verify-extract` tree IS the full extraction — no second 13.45 GB
  extract was done (disk gate: 86% full at the time). Do NOT re-extract.
- Archive master stays at `~/workspace/_ttt2-work/reassemble/ttt2.7z`;
  GitHub release `ttt2-7z-v1` is the safe source.

## INNER PULLS — 9 files (manifest landed; binaries NOT in repo)

Pulled 2026-10-23/24 via `tools/ttt2_virtual_god.py --pull` (virtual
remote-7z stream, GoD bare game partition, XDVDFS sector 32). All 9
re-verified sha256 OK against `pulls/pull-manifest.json` this run
(2026-10-25 10:12 CDT).

Per this repo's AGENTS.md rule 8 (no copyrighted game files in a public
repo), the pulled `.bin` binaries are NOT committed here — only the
manifest (sha256 + sizes + sectors + magic bytes) and this status doc.
The binaries remain on local disk at `~/workspace/_ttt2-work/pulls/` and
are re-producible at any time from GitHub release `ttt2-7z-v1` with
`ttt2_virtual_god.py --pull <inner-path>` (no re-download of the 13 GB
archive needed — the tool streams from the release).

| file | bytes | sha256 (first 16) | header |
|------|-------|-------------------|--------|
| data026.bin | 256 | 19c276688d6ebd52 | `ftypnrfi` — plain NRFI box container |
| data019.bin | 31,624 | 135520fc12da20bd | `0f f5 12 ed` Namco container |
| data053.bin | 412,736 | a057a7f623fdd88a | `0f f5 12 ed` |
| data018.bin | 557,332 | 7e06ad5336374973 | `0f f5 12 ed` |
| data052.bin | 2,659,880 | 8d85d8f2340c353 | `0f f5 12 ed` |
| data050.bin | 3,683,036 | 60b9d02a3a38c4b2 | `0f f5 12 ed` |
| data004.bin | 4,075,114 | d8c73be427171538 | `0f f5 12 ed` |
| data000.bin | 4,064,970 | 375b1ab445cbc0b0 | `0f f5 12 ed` |
| nrfo.bin | 298,696 | 52214bbef1208d87 | `ftypnrfo` boxes + offset table |

## CONTAINER FORMAT — what we know

- `data026.bin` is a plain ISO-BMFF-style box file: boxes `ftyp nrfi`,
  `head`, `idgt` — uncompressed, directly parseable. Likely an index/
  manifest-style container (256 bytes).
- `nrfo.bin` is `ftypnrfo` boxes with an offset table — also plain.
- The other seven carry the `0f f5 12 ed 01 00 00 00` header followed by
  what looks like an offset/size table, then high-entropy payload:
  Namco's encrypted/compressed container. Cracking this header is the
  teardown's next hard step — it gates the character/model data.
- The 7 large `00000002/` blobs (51 MB–2.03 GB) are NOT yet pulled or
  examined; they are title-data STFS blobs, separate from the GoD stream.

## REMAINING — do not pull blindly

- 33 of 42 `dataNNN.bin` files are NOT yet pulled (largest: data027
  613 MB, data037 380 MB, data038 306 MB, data039 465 MB, data041
  436 MB, data044 438 MB, data047 429 MB — full inner set is 8.4 GB).
- Disk is 86% (15 GB free) as of this run. Pulling the rest at once
  would push disk past 95%. Pull selectively (one file at a time,
  delete or land after analysis) or after disk frees up.
- `$SystemUpdate/` (32 files) is dash payload — skip.
- Priority (owner 2026-10-14/15): **character models + moveset data FIRST**,
  then stages, then audio. No dataNNN.bin has yet been mapped to a
  character — that mapping is the next lane's job once the `0f f5 12 ed`
  container is cracked.

## ENTRY POINTS (local disk)

- Extracted tree: `~/workspace/_ttt2-work/reassemble/_verify-extract/`
- Inner listing: `~/workspace/_ttt2-work/ttt2-inner-listing.json`
  (78 files, 8,402,073,168 bytes inner)
- Tools: `~/workspace/_ttt2-work/tools/` (`ttt2_virtual_god.py --pull`,
  `xdvdfs_reader.py`, `stfs_blobs.py`, `god_surgical.py`,
  `dinf_decrypt.py`) + `~/workspace/tools/zarmanager`
- This branch dir: `teardown/tekken-tag-tournament-2/`
  (`INNER-LISTING.md`, `tools/ttt2_virtual_god.py`, `pulls/`)
