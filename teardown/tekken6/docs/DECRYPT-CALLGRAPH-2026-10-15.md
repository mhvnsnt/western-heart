# Tekken 6 PSP — Decrypt Call Graph FULLY REVERSED (watchdog 2026-10-15)

All addresses are runtime VAs. File offsets = VA − 0x8803000
(PT_LOAD: file 0x1018 → VA 0x8804018). Source: `decrypted/EBOOT.DECRYPTED.ELF`.

## Functions (all verified by disassembly this run)

### 0x8AA2E88 — CRC verify + key extraction (EXACT)
```
CRC32(poly 0xEDB88320, init 0xFFFFFFFF, NO final xor) over buf[0, 0x7FC)
must equal u32 buf[0x7FC]. Else return 0.
idx_i = buf_words[off_i] ^ mask_i,  off=[0xF1,0x1AB] @ 0x8BCE788,
                                    mask=[0x38BFE591,0xD3610818] @ 0x8BCE780
require idx_i < 0x800 (word index; may read past the 512-word unit in RAM)
key_i = buf_words[idx_i]  → written to the two caller output slots
return 1
```
Note: previous `tools/k1k2_extract.py` matches this exactly (validated again
against machine code this run).

### 0x8AA3298 — keystruct build (EXACT)
`keystruct(a0, a1, a2, a3, t0)` → writes `[C1, C2, K1, K2]` at +0/+4/+8/+12:
- `(a1|a2) != 0` → K1=a1, K2=a2. Else K1/K2 from PRNG 0x8B7B600 (MWC,
  consts 0x4C957F2D/0x5851F42D, nonzero-mix retry).
- `a3 != 0`:
  - `t0 != 0` → C1=a3, C2=t0
  - `t0 == 0` → C1/C2 = [0x8B2B9F8], [0x8B2B9FC] (if table[0] != 0)
- `a3 == 0` → C1/C2 = [0x8B2B9F8], [0x8B2B9FC]
(Cipher 0x8AA2CA8 only ever consumes K1=[+8], K2=[+12]; C1/C2 unused by it.)

### 0x8AA305C — dual-decrypt + verify (EXACT, NEW)
`f(keystructA, dst, src, keystructB)`:
1. Prologue: `derived[0..1] = dst_words[off_i]^mask_i`,
   `derived[2..3] = src_words[off_i]^mask_i` (same off/mask tables).
2. `cipher(keystructA, dst, 0x800, 0, 0)` then `cipher(keystructB, src, 0x800, 0, 0)`
   (0x8AA2CA8 — the stream cipher; XOR keystream, symmetric).
3. Verify: for i in 0..0x1FF, skip i in {0xF1, 0x1AB, derived[0..3]};
   require decrypted_dst[i] == decrypted_src[i]. Return 1/0.
**Implication:** with a stream cipher and identical ciphertext in dst/src, the
verify passes iff (K1A,K2A)==(K1B,K2B). It is a key-confirmation check.
Previous single-pass decrypts were INCOMPLETE vs this — but for equal keys the
dual pass reduces to the single pass (already tried → random on sector 230256).

### 0x8AA2E80 — decrypt entry (NEW)
Literally `j 0x8AA2CA8` — decrypt with keystruct, no verify. Called once from
0x8A9DCB0 (see below).

### 0x8AA1204 — sector read + verify + keystruct (EXACT)
Reads 0x800 bytes, calls 0x8AA2E88; on CRC pass builds keystruct at a2:
- t0&0xFF != 0 (path X): `0x8AA3298(ks, ext0, ext1, 0xBCBD1C51, 0xE8BDE039)`
- t0&0xFF == 0 (path Y): `0x8AA3298(ks, s1 /* caller's a3 */, ext1, 0, 0)`
  → K1 = caller's a3 value (!), K2 = ext1, C1/C2 from table.

### Callers
- `0x8AA2100` (openPac-ish): calls `0x8AA1204(a0=pac, a1=fd, a2=pac+0x2C, a3=sp, t0=1)`
  → **path X** → keystructB @ pac+0x2C = {C1=0xBCBD1C51, C2=0xE8BDE039,
  K1=ext0, K2=ext1} from the open-time sector.
- `0x8AA22E8` (sector read): calls `0x8AA1204(a0=pac, a1=fd, a2=s2, a3=sp, t0=0)`
  → **path Y** → keystructA @ s2 = {K1=caller's sp value, K2=ext1, C1/C2=table};
  then re-reads the sector and calls
  `0x8AA305C(keystructA=s2, dst=sp, src=sp+0x800, keystructB=pac+0x2C)`.
- `0x8AA135C` (other read path): `0x8AA305C(s2, s3, sp, s0+0x2C)` — same shape.

### 0x8A9DA88 — PAC-open with SESSION keys (NEW)
Builds keystruct on stack via `0x8AA3298(ks, 0,0,0,0)` → **K1/K2 = PRNG-derived**
(0x8B7B600 reads state from kernel thread ctx via $k0 → [ctx+0xA8]/[ctx+0xAC]),
then `0x8AA2E80(ks, buf, len, t0, t1)` and `0x8AA3548(ks, 0,0,0)` (key evolution).
PRNG seed is unknown (kernel thread state) — likely per-boot. This path is
probably SAVE-DATA (`ms0:/PSP/SAVEDATA/%sDATA` string sits in the same cluster),
not DATA401 bulk.

### Cipher call sites (complete)
- 0x8AA2CA8 ← 0x8AA3104, 0x8AA311C (the two passes inside 0x8AA305C)
- 0x8AA2E80 (= j 0x8AA2CA8) ← 0x8A9DCB0 (session-key path)
The bulk DATA401 data does NOT go through this cipher in any path found so far.
`ktRead` (0x08a9cdd0) is C++ vtable plumbing — its decrypt (if any) is deeper.

## Full-ISO CRC scan (NEW, definitive)
Scanned all 417,807 ISO sectors with the exact 0x8AA2E88 CRC: **exactly ONE
sector passes — 230256.** The earlier "187K scan" result is confirmed and
extended: the per-sector CRC-key scheme covers a single sector, not the bulk.

## ISO layout findings (NEW)
- `DATA401.IDX`: extent LBA **230240**, 26,028 bytes (13 sectors: 230240–230252),
  entropy 7.99 (encrypted).
- `DINF_400.BIN`: LBA 230192, 120 bytes, high entropy.
- **Sector 230256 is in an ISO filesystem GAP** (no file covers it) — it is the
  first sector of the raw data region, right after the IDX. The game reads the
  region via raw LBN (`disc0:/sce_lbn0x%x_size0x%llx` string in EBOOT).
- PAC dispatch table found at file 0x3cb6c0: 6 function pointers
  (0x08a9d098, 0x08a9e2e4, 0x08a9e214, 0x08a9f68c, 0x08a9f7c0, 0x08a9cdd0=ktRead),
  counts 0x1F/0x2C, then strings: `ReadInfo`, `openPac`, `%s/DATA401.IDX`,
  `disc0:/PSP_GAME/USRDIR`, `disc0:`, `ktRead`, `disc0:/sce_lbn0x%x_size0x%llx`,
  `ms0:/PSP/SAVEDATA/%sDATA`.

## Empirical decrypt attempts (this run)
- Sector 230256 single-pass with exact extracted keys (0x24cfa8a4, 0x564928df):
  random (7.9) — reproduces prior result.
- All 13 IDX sectors with (ext0,ext1), swapped, table@0x8B2B9F8
  (0x10400012, 0x402021 — looks like code, not keys), (0xBCBD1C51, 0xE8BDE039):
  all random, no 12/16-byte entry structure, ascii ratio ~0.37.
- PPSSPP live-dump path re-confirmed blocked: AppImage AND extracted
  `AppDir/bin/PPSSPPSDL` are both **static-pie** (LD_PRELOAD impossible);
  Xvfb exists but no audio server and static SDL ignores SDL_AUDIODRIVER
  (prior finding stands).

## What remains
1. Bulk DATA401 decrypt path: trace `ktRead` (0x08a9cdd0) → its callees
   (0x8a8cee4, 0x8a8ca88 are vtable thunks; the real read/decrypt is deeper).
   The bulk almost certainly does NOT use the 0x8AA2CA8 cipher.
2. Alternative: unicorn-emulate the game's actual PAC read on the IDX sectors
   with the openPac keystructB — needs the open-time sector's ext keys
   (se
...[truncated 1335 chars]