# Tekken 6 PSP — ROUND 6 JOB 1: bulk regeneration + derivative audit

Date: 2026-10-21 (attempt 4 banking attempt 2/3's verified scratch
results). Branch: `teardown/tekken6-round6-com-gmo`, PR #479.
Scripts + raw outputs in this directory:
`r6_bulk_verify.py` / `r6_bulk_verify.json` / `bulk_verify.log`,
`r6_ndpp_scan.py` / `r6_ndpp_scan.json`.
Workdir retained (never deleted): `~/workspace/_t6r4-work/` —
`bulk_decrypted_r6.bin` (367M / 384,073,728 bytes) + `decoded76/`.

## Regenerated bulk — VERIFIED (not trusted blind)

`bulk_decrypted_r6.bin` was regenerated with the corrected per-1024
decryptor (`tools/bulk_decrypt.py`) and then verified three ways:

| Check | Result |
|---|---|
| Size vs corrupt round-3 bulk | identical: 384,073,728 bytes both |
| 1024-byte block diff vs corrupt bulk | **187,536 / 375,072 blocks differ (exactly 50.0%); differing blocks by global parity: odd = 187,536, even = 0** — exactly the round-5 prediction (per-2048 driver corrupted every odd block, no even block) |
| Top-76 decode FROM the regenerated bulk file (not direct-from-ISO) | **76/76 adler-exact** |
| Fresh-decrypt spot check: 40 random ISO sectors (seed 6) re-decrypted per-1024 and compared to the bulk file | **40/40 byte-identical** |

Verdict: the regenerated bulk is the clean bulk. The round-3
`bulk_decrypted.bin` is corrupt in every odd 1024-byte block and must
not be used for any further derivation.

## NDPP embedded scan — CORRECTED COUNT (the known case)

Re-ran the embedded-GZIP scan on the entry-87 slice
(bulk offset `38592*2048`, 81,591,641 bytes) on BOTH bulks with the
same scanner (`r6_ndpp_scan.py`: find `GZIP`, validate 20-byte header
fields, require `0x78 0xda`, zlib-decompress, check length + adler32):

| Bulk | `GZIP` magics found | Header-OK | Adler-exact | Decompressed total |
|---|---|---|---|---|
| OLD corrupt (round-3) | 2,760 | 2,720 | **94** | 91,184 bytes |
| NEW clean (round-6) | **5,470** | **5,470** | **5,470 / 5,470** | 153,684,864 bytes |

**Corrected count: 5,470 embedded containers, 5,470/5,470
adler-exact** — the old "94/2,720" was a corrupt-bytes artifact
(magics and bodies in odd blocks were garbled, so most containers
were invisible or undecodable). Decoded first-4-bytes on clean bytes:
`0d000000` × 3,731 + `06000000` × 1,739 (= 5,470).
Related magic counts: NDPP occurrences in the entry-87 slice:
old 798 → **new 1,565**. `GMO\0` whole bulk: 0 old, **0 new**
(still-valid). `MOTA` whole clean bulk: 265.

## Derivative audit — every rounds 2–4 claim derived from the corrupt bulk

| # | Derivative / claim (source) | Verdict | Why (byte evidence) |
|---|---|---|---|
| 1 | Embedded-GZIP scan "94/2,720" (round-3 session-2, WIRING-INVENTORY) | **CORRECTED** | Re-scan above: 5,470/5,470 adler-exact on clean bytes |
| 2 | "2,546 embedded GZIP containers" in entry-87 archive (ROUND2 §5, NDPP archive) | **CORRECTED** | Same slice, clean bytes: 5,470 magics, all adler-exact. The 2,546 figure undercounted corrupt-garbled magics |
| 3 | NDPP section counts "357 chained + 441 scattered = 798" (`models/NDPP-FORMAT.md`) | **CORRECTED** | Clean slice holds 1,565 NDPP occurrences — roughly double; the old census missed sections whose magics sat in odd blocks |
| 4 | `ndpp_bounding_volumes.glb` — 1,103 boxes / 357 sections (PR #187, on main) | **INCOMPLETE — re-extraction owed** | Boxes extracted from intact sections are real geometry, but the section census it was built from (798) missed ~half the sections now visible (1,565). Do not treat the GLB as the complete set |
| 5 | NDPP-FORMAT "What NDPP does NOT contain" (no vertex arrays, no index buffers, exhaustive scan) | **WITHDRAWN as exhaustive** | The scan ran on corrupt bytes: odd-block content was garbage, so absence claims over those bytes prove nothing. Header/descriptor/bbox format for the sections actually found remains **still-valid** (validated min<max, chain-walk by size field); negative/completeness claims must be re-derived on the clean bulk |
| 6 | "GMO magic: zero hits in the bulk; GMO→GLB pipeline does not apply" (NDPP-FORMAT) | **STILL-VALID** | Whole clean bulk re-counted: `GMO\0` = 0 (same as corrupt). Literal-GMO absence is not a corrupt artifact |
| 7 | Scoreboard "20/76 byte-exact, 56 fail" (rounds 2–4, `round3-evidence/scoreboard_strict.txt`) | **CORRECTED (already, round 5)** | 76/76 adler-exact with per-1024 decrypt; the 20 passing containers are still-valid — they were the streams the round-5 analysis showed end before odd-block damage dominates |
| 8 | "Custom gzip / custom inflate" format claims + idx0 "98.7% decode, 1,418-byte gap" (rounds 2–4, NDPP-FORMAT file0 note) | **CORRECTED (already, round 5)** | No custom gzip exists; bodies are plain zlib. idx0 (entry 454) now decodes 100% adler-exact (105,472 bytes); the 1,418-byte gap was corrupt-bulk damage, not a format feature |
| 9 | Round-2 GMO→GLB pipeline proof (`cloud.glb`, PR #388) | **STILL-VALID** | Built from Dissidia sample GMOs in the recon release, never from the T6 corrupt bulk; unaffected |
| 10 | EBOOT-side findings (wrapper/inflate semantics, sector cipher, loader chain; rounds 2–5 Ghidra/PPSSPP work) | **STILL-VALID** | Derived from the decrypted EBOOT and live traces, not from bulk bytes |
| 11 | COM container existence/counts (18 files, counts 7–16, 176 total) | **STILL-VALID, now byte-exact** | Round-5 decode of idx58–75 is adler-exact on clean decryption; round 2–4 could only see clean prefixes. Full framing = JOB 3 |

## Storage note

The regenerated bulk (384,073,728 bytes) stays in the retained
workdir only for now; it is fully reproducible from the ISO with
`tools/bulk_decrypt.py` (verified 40/40 above), so no 100MB-part
release upload was made this attempt. If a stored copy is wanted,
that reproducibility + the ISO release (`tekken6-psp-v1`) is the
retrieval path.
