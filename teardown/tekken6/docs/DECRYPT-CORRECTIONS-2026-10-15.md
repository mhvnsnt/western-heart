# Tekken 6 PSP — Decrypt Corrections + ktRead Trace (watchdog 2026-10-15 ~15:15 EDT)

Follow-up to `DECRYPT-CALLGRAPH-2026-10-15.md`. All addresses are runtime VAs.

## CORRECTION 1 — 0x8AA1204 path Y: K1 = ext0, NOT the buffer address (delay-slot misread)

The old doc claimed path Y builds `keystructA = {K1 = caller's a3 (buffer
address!), K2 = ext1}`. That was WRONG — a MIPS delay-slot misread.

At 0x8aa1284: `beqz $s4, 0x8aa1324` (branch to path Y when `t0&0xFF == 0`).
Its DELAY SLOT at 0x8aa1288 is `lw $a1, ($sp)` — it executes on BOTH paths,
loading **ext0** into a1. So path Y calls:

```
0x8AA3298(a0=s3, a1=ext0, a2=ext1, a3=0, t0=0)
→ keystructA = {C1/C2 = table@0x8B2B9F8, K1 = ext0, K2 = ext1}
```

(a2 = ext1 is loaded at 0x8aa1324 `lw $a2, 4($sp)`; a1 still holds ext0 from
the delay slot — 0x8AA2E88 never writes a1, verified by full disassembly.)

**Empirical proof** (sector 230256, ext0=0x24cfa8a4, ext1=0x564928df,
bit-exact `tools/sector_cipher.py`, dual-decrypt+verify per 0x8AA305C):

| K1 used | verify mismatches (of 506 checked words) |
|---|---|
| K1 = ext0 (corrected) | **0** — verify PASSES |
| K1 = 0x09FFF000 (old "buffer address" reading) | 508 — verify always FAILS |

The old reading would make the game's own sector-read verify fail on every
call — impossible for a shipping game. The corrected reading makes
0x8AA305C a genuine **key-confirmation**: it passes iff the current sector's
(ext0, ext1) equal the open-time sector's (ext0, ext1).

## CORRECTION 2 — 0x8AA22E8 is the SAVE-DATA path, not DATA401 bulk

Its two `snprintf`-style calls (0x8b7c444) build paths from format strings:

- `0x8BCE764` = `ms0:/PSP/SAVEDATA/%sDATA`
- `0x8B94E30` = `%s/%s`

So 0x8AA22E8 (the single caller at 0x8aa29a0) reads save-data sectors through
the CRC-key scheme — consistent with the session-key cluster at 0x8A9DA88
(PRNG-derived K1/K2, same `ms0:/PSP/SAVEDATA/%sDATA` string neighborhood).
It is NOT the DATA401 bulk reader.

## FINDING 3 — ktRead (0x08a9cdd0) chain traced: plain I/O, NO crypto

```
0x8a9cdd0 (ktRead vtable entry)
 → 0x8a8cee4 / 0x8a8ca88 (thunks; 0x8a8ca88 tail-jumps to 0x8a76f2c)
 → 0x8a76f2c → 0x8a76cf8 (recursive; only calls 0x885edf4/0x885f3e0/0x885fa44/0x888bfa8)
 → 0x8a76f58 region calls: 0x885fa44, 0x8a752d0, 0x885edf4, 0x896dff8,
    0x8970390, 0x8a73e30, 0x885edb4, 0x885f528
```

Zero calls to 0x8AA2CA8 (stream cipher) or any 0x8AAxxxx crypto routine
anywhere in the chain. The ktRead C++ object is the PLAIN file-I/O path
(`disc0:/sce_lbn0x%x_size0x%llx` raw-LBN reads). The bulk DATA401 region is
read through here with no in-path decryption.

## FINDING 4 — 0x8AA135C ("other read path") is DEAD CODE

Zero `jal` callers in the entire EBOOT (byte-scanned for the jal encoding of
0x08aa135c) and zero data-pointer references. It is never reached. The
caller-driven dual-decrypt shape it implements is not used by the bulk path.

## FINDING 5 — IDX tail is ZERO in the clear (not stream-encrypted)

Sector 230252 (last IDX sector): bytes 0–1535 entropy ~7.1, bytes 1536–2047
ALL ZEROS. A stream cipher would leave keystream (random) over zero padding —
zeros in the clear mean the IDX tail is NOT covered by the 0x8AA2CA8 stream
cipher. IDX ≈ 26,028 bytes per ISO fs (13 sectors 230240–230252).

## FINDING 6 — bulk data region: uniformly random, no sector structure

Sectors 230256–230319: entropy 7.90–7.92, no ASCII runs >12 chars, no magic
at sector starts, first-u32 values uniformly distributed. Still encrypted by
an UNKNOWN mechanism, or compressed with an unknown scheme. NOT covered by:
the CRC-key sector scheme (only sector 230256 passes CRC — full-ISO scan),
the ktRead path (plain I/O), or 0x8AA135C (dead).

## What remains (next run)

1. Bulk transform hunt: the bulk is read plain via ktRead then transformed
   elsewhere — candidates: (a) custom decompressor (find inflate/LZ-like
   routines near the ktRead callers), (b) IDX-driven per-file keys applied
   after plain read, (c) unicorn-emulate the game's actual PAC open on the
   IDX sectors with openPac keystructB.
2. IDX structure: 26KB index with zero tail — analyze entry layout
   (candidate: 32-byte entries → ~813 files) once the obfuscation is
   identified. The IDX is NOT stream-cipher encrypted (zero tail).
3. Sector 230256's decrypted payload is still high-entropy (7.9) after the
   key-confirmation decrypt — that cipher layer is envelope-only; the
   payload protection is the bulk mechanism above.
