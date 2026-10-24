# Tekken 6 PSP — Sector Cipher FULLY REVERSED (0x8AA2CA8)

Watchdog run 2026-10-14 ~17:00 EDT. Checkpoint: `tekken6-data401-decrypt.json`.

## What was done this run
1. Rebuilt MIPS disassembly tooling (`tools/mips_dis.py`) — capstone could not
   decode Allegrex-specific instructions, so the missing pieces were resolved
   from PPSSPP's own CPU tables (`Core/MIPS/MIPSTables.cpp`, `tableALLEGREX0`):
   opcode `0x1F`/funct `0x20`/sub-field selects `wsbh`/`wsbw`/`seb`/`bitrev`/`seh`.
   **The "DSP ASE" instruction at 0x8AA2D64 (`0x7C041D20`) is Allegrex `bitrev
   $v1, $a0`** — full 32-bit reversal. Not DSP ASE at all.
2. Fully disassembled 0x8AA2CA8 (the "block cipher"), its caller 0x8AA305C
   (calls it twice per sector), the key-setup 0x8AA3298, and the PRNG 0x8B7B600.
3. Wrote `tools/sector_cipher.py` — an instruction-exact Python model.
4. **Validated two ways**: (a) involution — encrypt twice restores plaintext;
   (b) **byte-identical to the real machine code** — unicorn emulation of the
   actual EBOOT bytes vs the Python model on identical inputs: 768/768 words match.

## The cipher (custom stream cipher, NOT AES)
Call: `cipher(K1, K2, dst, length, t0=0, t1=0)` — K1/K2 are the per-sector key
words at header+8/+12 (see key schedule below). Symmetric (XOR): same routine
decrypts.

- Per 32-bit word: `dst[i] ^= k`, then `k = 5*rotr(k,29) + 1`
- Per-block reseed (block counter `ctr`, multiplier state `m = 3*a0 + 3*block`):
  - `r = m mod 29` — via reciprocal multiply, magic `0x8D3DCB09`
    (`q = ((HI(s32(m)*s32(M)) + m) >> 4) - (m>>31)`, signed division;
    verified exact for the practical range)
  - `s = rotr((ctr + K1) + bitrev(ctr + K1), r + 2)`
  - `k0 = s ^ K2`
- Optional keystream warm-up: if `t1 = (((t1_in<<30)|(t0_in>>2)) & 0xFF) > 0`,
  the `5*rotr+1` recurrence is spun `t1` times before use.
- Tail bytes (`length & 3`): masked with table at `0x8BCE7A4`
  (`ffffff00 / ffff0000 / ff000000`).

## Key schedule (0x8AA3298) → 16-byte header [C1, C2, K1, K2]
- K1/K2: taken from caller args when `(a1|a2) != 0`, else generated from the
  internal PRNG (0x8B7B600, MWC-style, constants 0x4C957F2D / 0x5851F42D)
  with nonzero-mixing (`s0 = ((s0+v)<<18) ^ (s1<<3) ^ (v>>1)`, retried if 0).
- C1/C2: from caller args (a3/t0), else copied from table at 0x8C2B9F8.
  (Notes previously recorded C1=0xBCBD1C51, C2=0xE8BDE039.)

## Call graph (sector path)
- `0x8AA305C(keystructA, dst, src, keystructB)`:
  1. derives 4 key words on stack via table-XOR prologue,
  2. `0x8AA2CA8(keystructA, dst, 0x800, 0, 0)`,
  3. `0x8AA2CA8(keystructB, src, 0x800, 0, 0)`.
- Callers read a 0x800-byte encrypted unit via import then call 0x8AA305C
  (seen at 0x8AA13BC and 0x8AA247C).

## OPEN QUESTION — 768 words vs 0x800-byte buffer
With the standard call `(K1, K2, dst, 0x800, 0, 0)` the code provably processes
**768 words = 0xC00 bytes** (`t3 = 256 - t1 + ((len+3)>>2)` = 768 for len=0x800).
Confirmed by unicorn emulation of the real bytes (768 stores). Both in-tree
callers pass 0x800 and at least one target is a 0x800-byte stack buffer, so a
literal reading implies a 0x400-byte overrun — yet the game runs fine on PPSSPP.
Possibilities: the dst buffers are actually larger than the read size; the
overrun lands on dead stack; or the length parameter has a different unit in
the real call path. **Do not "fix" the model** — it is bit-exact to the ROM.
Resolve by decrypting a real sector once the ISO is available and checking
which prefix (512 vs 768 words) yields valid GMO/TIM2 data.

## What's still blocked
1. **Encrypted sector bytes** — the ISO was offloaded to GitHub release
   `mhvnsnt/western-heart:tekken6-psp-v1` (disk is at 91%; re-download needs
   owner call). With the ISO: decrypt sectors 230253–417792 with
   `sector_cipher.py` + per-sector K1/K2, scan for GMO/TIM2 magics.
2. **Per-sector K1/K2 values** — need the 0x8AA3298 call sites (who passes
   keys vs PRNG) — traceable once live data is available.
3. **DATA401.IDX** — still goes through imported `openPac` (invisible
   statically). Not strictly needed: sector decrypt + magic scan recovers
   content without the file map.
4. PPSSPP live memdump path (needs display) is now REDUNDANT for sectors —
   static reversal is complete and validated.
