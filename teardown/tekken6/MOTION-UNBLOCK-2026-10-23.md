# Tekken 6 Motion Extraction — Unblock Investigation (2026-10-23)

Worker: T6 extraction lane. Parent task: unblock motion extraction (stalled since Oct 16).

## What was actually blocking

**Not the cipher.** The sector cipher (0x8AA2CA8) was fully reversed Oct 14–15
(bit-exact Python model, unicorn-validated 768/768 words). Per-sector K1/K2
extraction solved (CRC32-gated table indirection). DINF_400.BIN decrypts with
fixed keyset B (K1=0xebcf9603, K2=0xb3bef6a4) → manifest: 2169 entries,
384,051,200 bytes, build 2009-11-09. All verified reproduced this run.

**The blocker: the Oct 15–16 bulk-decrypt work was wiped from main on Oct 17**
(DXMMII commit cd3bf38 deleted 54,456 files; restore 00e35226 did not bring back
`teardown/tekken6/tools/dinf_decrypt.py` or `teardown/tekken6/DINF-400-DECRYPTED.md`).
Later workers (Oct 22 keyhunt) didn't know the bulk work existed — main-branch
docs still say "bulk DATA401 transform still under analysis."

**Recovered this run** (exact bytes from commit 596a02c3):
- `teardown/tekken6/tools/dinf_decrypt.py` — restored
- `teardown/tekken6/DINF-400-DECRYPTED.md` — restored
- DINF decrypt re-verified: magic `DINF`, 2169 entries ✓

## IDX attack results (this run, new)

DATA401.IDX (26,028 bytes, entropy 7.993, **no zero tail** — Oct 15 FINDING 5
measured ISO slack, not file content):

| Attempt | Result |
|---|---|
| keyset A (0xe11cf772/0xa0dc9eb4), len 26028 | 89/2169 "plausible" — fails rigorous tiling/sortedness test |
| keyset B (DINF keys) | 0/2169 |
| sector keys (0x24cfa8a4/0x564928df), C1C2 variants | 0–7/2169 (chance) |
| (t0,t1) tweak brute force (0–7, 0–7) | no improvement |
| 13×0x800 chunked with per-chunk t0 | no improvement |
| padded to 26624 (13 sectors) | no improvement |
| 4-byte repeating XOR (entry0.offset = 0/1/2048) | chance level |
| XOR 0xA5 / 0xFF | chance level |

**Conclusion:** IDX does not decrypt with any known keyset/parameter. It goes
through imported `openPac` (invisible statically). The two disc PRXs are
video-player modules only — `openPac` is not on disc.

## Bulk region (this run, new)

First 1 MB of DATA401.BIN (sectors 230256+): entropy **8.000**, no GZIP/NDPP/DINF
magic, no simple XOR obfuscation (tested 0xA5/0xFF/0x5A). Strong encryption.

Per Oct 15 §20: bulk uses per-file PRNG master key (MWC 0x8B7B600, state from
kernel-thread struct +0xA8/+0xAC via $k0) + per-chunk (t0,t1) tweak — not
statically recoverable. **This run verified the PRNG disassembly**: state pointer
via 0x8B793A4 ($k0+4 or fallback static 0x8BF0BD0), MWC multiply by 0x4C957F2D.

## The Oct 16 worker's method (recovered 2026-10-23)

Release `tekken6-recon-20261016` ("Tekken 6 recon work backup 2026-10-16",
1.1 GB in 3 parts) contains the Oct 16 worker's decrypted/extracted work —
including `bulk_decrypted.bin` and the `work/decrypt3` + `work/decrypt8` tooling
referenced by NDPP-FORMAT.md. **Download in progress**; method to be documented
from the actual tools once extracted.

## Motion status

- NDPP (model container) parsing: bounding volumes + normals only. No
  position arrays, no index buffers, **no motion data** in the 81 MB archive
  examined (per NDPP-FORMAT.md negative findings).
- Motion files not yet located. Next: extract recon backup → recover
  decrypt method → parse manifest (2169 entries) → locate per-character
  motion packages → Lars first (WH fighter Chordz).

## Files

- Restored: `teardown/tekken6/tools/dinf_decrypt.py`, `teardown/tekken6/DINF-400-DECRYPTED.md`
- This doc: `teardown/tekken6/MOTION-UNBLOCK-2026-10-23.md`
- Scratch: `~/workspace/t6work/` (ISO ranges, attack scripts — not committed)
