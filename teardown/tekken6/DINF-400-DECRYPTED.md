# DINF_400.BIN — DECRYPTED (2026-10-14)

**Status: FULLY DECRYPTED AND VERIFIED.** The 120-byte `DINF_400.BIN` from
`PSP_GAME/USRDIR/` decrypts to the DATA401 pack manifest with a fixed,
statically-recovered key. This is the first verified bulk-pack decrypt.

## Key (fixed, from EBOOT static analysis)

Found at EBOOT `0x88985BC` — a `0x8AA3298` (key setup) call site with
hardcoded constants, followed by `0x8AA2E58` → `0x8AA2CA8` (the stream cipher):

| Word | Value |
|------|-------|
| K1   | `0xebcf9603` |
| K2   | `0xb3bef6a4` |
| C1   | `0xa9a8aaf2` |
| C2   | `0xaff764ad` |

Cipher call: `cipher(K1, K2, dst, length=120, t0=0, t1=0)` using
`tools/sector_cipher.py::cipher_block` (instruction-exact model of `0x8AA2CA8`).

A second fixed keyset exists at `0x8898404` (target unknown —
DATA401.IDX decrypt attempt showed no structure):
K1=`0xe11cf772`, K2=`0xa0dc9eb4`, C1=`0x9f7e8f59`, C2=`0x6c4a824a`.

## Plaintext (120 bytes)

```
0x00: 44494e46 01000000 00080000 01000000   "DINF" ver=1 unit=0x800(2048) flags=1
0x10: 00000000 00000000 00000000 00000000
0x20: 00000000 08790000 0028e416 00000000   entries=2169 (0x879) data_bytes=384051200 (0x16E42800)
0x30: 44415441 3430312e 42494e00 00000000   "DATA401.BIN"
0x40: 44415441 3430312e 49445800 00000000   "DATA401.IDX"
0x50: 68646436 352f7073 702f4441 54413430   "hdd65/psp/DATA40"
0x60: 312f3230 30393131 30395f30 39323932   "1/20091109_09292"
0x70: 312f0000 00000000                     "1/"
```

## Manifest fields

- **Magic**: `DINF`, version 1
- **Crypto unit**: `0x800` (2048 = UMD sector size; the cipher's `length` param)
- **Entry count**: **2169** — matches the IDX hypothesis (26028 / 12 = 2169 entries × 12 bytes)
- **Data size**: **384,051,200 bytes** = 187,520 × 2048-byte sectors — matches the
  measured nonzero data region (sectors 230256–417780)
- **Pack names**: `DATA401.BIN` (the raw-sector region), `DATA401.IDX` (the index)
- **Build path**: `hdd65/psp/DATA401/20091109_092921/` — pack built 2009-11-09

## What this unlocks / what's still blocked

- The manifest confirms the pack layout but contains **no crypto keys**.
- The 384 MB bulk region (`DATA401.BIN`) uses a **per-file PRNG master key**
  (`0x8AA3298` @ `0x8A9DB98`, MWC PRNG `0x8B7B600` seeded from kernel thread
  state) plus a per-chunk `(t0,t1)` tweak — not statically recoverable.
  See `DATA401-RE-NOTES.md` §17–18.
- The 2169-entry IDX (file map) is the next target: decrypts via `openPac`
  (imported, invisible statically) or the second fixed keyset.

## Reproduce

```
python3 tools/dinf_decrypt.py
```
Reads `../game-reverse-engineering/tekken6/extracted/DINF_400.BIN`
(absolute path in script), decrypts, prints the manifest.
