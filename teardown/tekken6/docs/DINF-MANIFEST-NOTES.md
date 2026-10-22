# DINF Manifest — Parse Verification (T6 Lane A, 2026-10-21)

Re-verified end-to-end this run from the sweep lane's ISO, read-only
(`/home/hatch/workspace/_t6r4-work/iso/tekken6-psp.iso`, 855,638,016 B —
never copied, never written). Reproducer: `teardown/tekken6/tools/dinf_decrypt_verify.py`.

## Source bytes
- `DINF_400.BIN`: LBA **230192**, 120 bytes, full entropy (93 unique byte values).
  - encrypted sha256: `a5d314491b3e762f833584788917c7c00a0424b5003e2d7e166d59020ca3aac0`
- Decrypt: `cipher_block(K1=0xEBCF9603, K2=0xB3BEF6A4, buf, 120)` — the banked
  0x8AA2CA8 stream-cipher model (`teardown/tekken6/tools/sector_cipher.py`,
  bit-exact vs EBOOT via unicorn 768/768 words, 2026-10-14). Keyset B is
  hardcoded at EBOOT VA 0x88985BC, applied at call 0x8AA2E58
  (see `docs/K1K2-CALL-SITE-ANALYSIS.md` row 2).
  - Model quirk honored: for length=120 the ROM processes
    t3 = 256 + ((120+3)>>2) = **286 words**; the keystream is data-independent,
    so the first 30 words decrypt identically from a 286-word zero-padded buffer.
  - decrypted sha256 (120 B): `e79c563320b1edd9b4c5ae26d36e40c2f99d9064cf7046cf37cb957e3aba0b1c`

## Verified field layout (120 bytes = 0x78)
| Offset | Type    | Value | Meaning |
|--------|---------|-------|---------|
| +0x00  | char[4] | `DINF` | magic — CONFIRMED this run |
| +0x04  | u32     | 1 | version (?) |
| +0x08  | u32     | 0x800 (2048) | sector size |
| +0x0C  | u32     | 1 | unknown |
| +0x10  | u32[4]  | 0 | reserved |
| +0x20  | u32     | **2169** | entry count — CONFIRMED |
| +0x24  | u32     | **384,051,200** | total bulk data bytes — CONFIRMED |
| +0x28  | char[16]| `DATA401.BIN` | bulk name |
| +0x38  | char[16]| `DATA401.IDX` | index name |
| +0x48  | char[48]| `hdd65/psp/DATA401/20091109_092921/` | build path (2009-11-09 09:29:21) |

CORRECTION vs 2026-10-14 notes: the entry count is at **+0x20** and the byte
total at **+0x24**, not at +0x04/+0x08 as the earlier summary implied. The
values (2169 / 384,051,200) were correct; only the field offsets were
misdescribed. Fixed here with the full hex dump as evidence (see reproducer output).

## Cross-checks
- 384,051,200 / 2048 = **187,525 sectors** exactly — matches the earlier
  full-ISO CRC scan target ("187,525 data sectors").
- Bulk region: raw LBN read starts at sector **230253** (first sector after the
  13-sector IDX at 230240–230252). 230253 + 187,525 = sector **417778**;
  sectors 417778–417792 (15) are slack past the manifest total.
- Sector **230256** is the only one of 417,807 passing the 0x8AA2E88 CRC
  (re-confirmed 2026-10-15); single-pass decrypt with its extracted keys
  (0x24cfa8a4, 0x564928df) still yields random bytes — sector path does NOT
  decode the bulk.

## What the manifest does NOT contain
The 120-byte header carries **no per-entry table**. Entry offsets/sizes live
in `DATA401.IDX` (LBA 230240, **26,028 bytes = 2169 × 12 bytes exactly**,
encrypted sha256 `9b73e352dea5a764bfdb60acef945bc4bc9eae8b731c175cd1b338588fccc4bf`).
IDX decrypt is unresolved: it goes through imported `openPac` (invisible
statically); the keyset-A attempt (K1=0xE11CF772, K2=0xA0DC9EB4 @ 0x8898404)
produced no structure (2026-10-14). Entry-indexed work (motion-data offsets,
per-entry compression tests) is BLOCKED on the IDX decrypt — owned by the
teardown-sweep lane's live/encode-context work; lane A does not re-hunt it.

## Banked this step
- `teardown/tekken6/tools/dinf_decrypt_verify.py` — read-only ISO →
  decrypt → parse reproducer (this doc's evidence source).
- This file: `teardown/tekken6/docs/DINF-MANIFEST-NOTES.md`.
