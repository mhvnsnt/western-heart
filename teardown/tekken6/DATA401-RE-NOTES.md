# DATA401 Decrypt — Reverse Engineering Notes (watchdog run 2026-10-14)

Task: decrypt Tekken 6 PSP DATA401 and extract character models / stages / audio / movesets.
Checkpoint: `~/workspace/agent-ops/checkpoints/tekken6-data401-decrypt.json`

## Confirmed findings

### 1. The "384MB data region" is raw disc sectors, not a file
ISO9660 listing of `tekken6-psp.iso` (855,638,016 bytes) shows NO data file in
`PSP_GAME/USRDIR/` — only `DATA401.IDX` (26,028 B) and `DINF_400.BIN` (120 B).
Sector-gap analysis: all filesystem files end at sector 230253; sectors
**230253–417792 = 384.1 MB** of unlisted tail space = the encrypted data region.
The game reads it via raw-sector paths: EBOOT contains the format string
`disc0:/sce_lbn0x%x_size0x%llx` (vaddr 0x8BCE740).

### 2. The region is uniformly encrypted
Sampled every ~2000 sectors across the tail: entropy 7.90–7.91 everywhere,
first sector all zeros, no plaintext magic (no GMO/TIM2) anywhere. Both
`DATA401.IDX` and `DINF_400.BIN` are also full-entropy (encrypted).

### 3. EBOOT layout (decrypted ELF, MIPS32 LE)
- Single PT_LOAD: file 0x1018 → vaddr 0x8804018, entry 0x8804124.
- Import stub block: 268 stubs at 0x8B88C68–0x8B894C8 (`jr $ra` stubs).
- Import directory decoded (custom 20-byte entries: attr, counts, NIDs, stubs, name;
  **numFuncs = high 16 bits** of the counts word — low byte undercounts).
  30 libs, 268 funcs total. Notably **no sceChnnlsv / sceDrm imports** → no KIRK
  hardware crypto; the pack cipher is software (or plain XOR). No AES S-box found
  in the binary.

### 4. Pack system call sites (vaddrs)
- `openPac` pool creation at **0x8AA1090–0x8AA10AC**: calls UtilsForUser func#30
  (stub 0x8B88EE0, NID 0x446D8DE6) with
  `a0="openPac"`, `a1=0x8AA2A34`, `a2=0x20`, `a3=0x1000`, `t0=0x4000`, `t1=0`.
  Only ONE xref to the "openPac" string exists in the whole binary.
- Nearby pack code: 0x8AA0FA0–0x8AA1200 (init, pool setup). XOR instruction
  density peaks at 0x8AA3000 (31 xors / 4KB) but no tight decrypt loop was found
  there — the cipher is not an obvious inline XOR loop.

### 5. IDX structure hypothesis
26028 = 12 × 2169 → possibly **2169 entries × 12 bytes** (offset/size/flags?).
Unverified — needs the key.

## What's still blocked
The IDX decryption key/algorithm. DINF_400.BIN (120 B, encrypted) may carry key
material. The decrypt routine lives near the pack code (~0x8AA0000–0x8AB0000)
but is not yet isolated.

## Next steps (for the next watchdog run or a dedicated worker)
1. Static: disassemble the pack functions around 0x8AA1000 fully; trace where the
   IDX buffer goes after `openPac`; identify the decrypt routine (watch for
   UtilsForUser crypto NIDs: SHA1/MD5 are 0x27CC57F0-style libc — the cipher may
   use them for key scheduling).
2. Known-plaintext: if IDX entries are (lba, size, flags) with the data region at
   LBA 230253, try XOR key recovery on entry 0.
3. Live: PPSSPP memory dump per `PPSSPP-LIVE-RUN-GUIDE.md` (needs display session;
   game must reach a fight so models are decrypted in RAM; dump regions with GMO
   `GMO\0` / TIM2 magic).

## Tooling built this run
MIPS static helpers used ad-hoc (capstone-based): ELF program-header parse,
`lui`+`ori`/`addiu` xref scanner (raw word-level — capstone operand parsing was
unreliable), PSP import-directory decoder. Worth promoting to
`~/workspace/tools/tekken-decrypt/` as `psp_elf_xref.py` on a later pass.

## 2026-10-14 ~10:30 EDT watchdog attempt 2 — NEW findings

### 6. openPac call site CONFIRMED at 0x8AA1090 (exact args)
`lui $a0,0x8BD; addiu $a0,$a0,-6396` loads `"openPac"` (vaddr 0x8BCE704)
into $a0; `lui $a1,0x8AA; addiu $a1,$a1,10804` loads 0x8AA2A34 (the IDX
buffer) into $a1; $a2=0x20, $a3=0x1000, $t0=0x4000, $t1=0; `jal 0x8B88EE0`.
Followed by a 4-byte read (`jal 0x8B88E70`, $a1=4, $a2=$sp) of the returned
handle — likely reading the entry count / header.

### 7. Import stubs are `jr $ra` placeholders at load
All of 0x8B88EA0–0x8B88F3C disassembles as `jr $ra; nop` pairs — the import
stubs are patched by the PSP loader at runtime, so the true targets of
`openPac`/`ktRead` call sites (0x8B88EE0, 0x8B88E70, 0x8B88DA0…) cannot be
resolved statically. The decrypt routine therefore cannot be reached by
static xref from here — it lives inside the imported function or behind the
loader-resolved stubs.

### 8. ktRead string consumers: two call sites
`"ktRead"` (vaddr 0x8BCE73C) is loaded at exactly two sites: 0x8AA1A70 and
0x8AA2098 — both in the pack-read path near the sce_lbn format string.
These are the raw-sector read wrappers; the per-read decrypt (if any) is
called from these functions.

### 9. XOR-0xA5 string-decrypt helpers at 0x8AA1940–0x8AA1A2C (BREAKTHROUGH)
Three tiny loops in the pack code each XOR bytes with **0xA5** (`addiu $x,$0,-91`)
and normalize with `seb` (SPECIAL3, opcode 0x1F — decoded properly now):
- 0x8AA1954 loop: `v0=byte[a0++]; v0^=0xA5; v1=seb(v0); sb v1,(a2++)` until NUL
- 0x8AA1988 loop: same shape, src = `a0 + a3 - 3752`
- 0x8AA1A08 loop: pipelined variant (`sb a1,(a2)` stores the PREVIOUS
  iteration's decrypted byte), `dst[i] = src[i] ^ 0xA5` until decrypted byte is NUL
These are **NUL-terminated string decryptors** — the pack encrypts its
filenames/paths with XOR 0xA5. This is the first recovered piece of the cipher.

### 10. XOR-0xA5 does NOT decode the IDX as (lba,size,flags) entries
Tried: 4-byte repeating XOR keyed on entry0=LBA 230253 (both endians) →
entry1 LBAs garbage (~3.1e9 / 9.3e8). Tried full-buffer XOR 0xA5 → 12-byte
LE words still out of range (min LBA 1,029,069; only 9 coincidental ASCII
runs ≥8 chars). Autocorrelation over key lengths 1–64 ≈ baseline (no
repeating key). Conclusion: the IDX body uses a different cipher (likely a
stream cipher with per-buffer key, decrypted inside `openPac` at runtime);
the 0xA5 helpers cover strings only.

## What's still blocked (updated)
The IDX body cipher. New lead: since short strings use XOR 0xA5, the IDX
buffer decrypt may be a slightly stronger variant (XOR 0xA5 + rotation, or
keyed stream). Next static target: the functions at 0x8AA1A70 / 0x8AA2098
(ktRead wrappers) — look for the post-read decrypt call. Live route unchanged:
PPSSPP memdump per PPSSPP-LIVE-RUN-GUIDE.md (needs a display session).

## 2026-10-14 ~11:00 EDT cipher hunt (subagent) — SECTOR CRYPTO STACK MAPPED

### 11. Raw-sector read path: 0x8AA2100 → 0x8AA1204
- `0x8AA2100`: formats `disc0:/sce_lbn0x%x_size0x%llx` (fmt string at
  **0x8BCE744** — note: prior notes said 0x8BCE740, actual is +4) via internal
  snprintf `0x8B7C444`, opens via stub, calls `0x8AA1204`.
- `0x8AA1204`: reads 0x800-byte sectors in a loop, calls `0x8AA2E88`
  (CRC verify + key extract), then `0x8AA3298` (crypto header setup) with
  constants **0xBCBD1C51** ($a3) and **0xE8BDE039** ($t0).

### 12. Sector integrity: CRC32 in last 4 bytes (0x8AA2E88)
- Each 0x800-byte sector: first 0x7FC bytes + CRC32 (standard poly
  0xEDB88320, table built at runtime at **0x8CBBA00** by `0x8AA2F54`).
- If CRC matches: extracts **2 key words** per sector via offset table at
  **0x8BCE788** (offsets 0xF1, 0x1AB words) XORed with masks at
  **0x8BCE780** (`38bfe591`, `d3610818`), sanity-checked `< 0x800`,
  double-dereferenced from the sector.
- Returns 1 on success, 0 on CRC failure. Verified via unicorn emulation:
  returns 0 on encrypted IDX chunks (CRC mismatch, as expected).

### 13. Crypto header setup: 0x8AA3298 (NOT the bulk decrypt)
- Writes 16-byte header: `C1=0xBCBD1C51` @+0, `C2=0xE8BDE039` @+4,
  `K1` @+8, `K2` @+12 (keys from sector or generated via PRNG `0x8B7B600`
  with nonzero-mixing if keys are zero).
- Contains an 8-byte decrypt loop (0x8AA34AC) for a fixed blob at
  **0x8CB9F8** using stack key material + permutation table at
  **0x8BCE790** (20-byte permutation of 0x00–0x13). This decrypts the
  in-memory key blob, not file data.

### 14. Block cipher: 0x8AA2CA8 (partially reversed)
- Called twice per sector by `0x8AA305C`. Uses PSP DSP ASE instructions
  (e.g. `0x7C041D20` at 0x8AA2D64 — SPECIAL3, capstone can't decode).
- Full reversal blocked on DSP ASE. Emulation via unicorn is possible
  (shadow-mapping workaround for kseg0: map at 0x1000000, patch
  `lui 0x8xx` → shadow high bits; see `/tmp/t6_emu2.py`).

### 15. IDX does NOT use the sector scheme
- DATA401.IDX (26,028 bytes) fails CRC check on all 12 full 0x800 chunks
  (expected — it's encrypted, CRC is over ciphertext or IDX uses different
  scheme). 26,028 is not a multiple of 0x800.
- IDX goes through imported `openPac` (0x8B88EE0, unresolvable statically).
  The IDX decrypt is inside the imported PRX, not in the EBOOT.

### 16. DINF_400.BIN: 120 bytes, high entropy (93 unique bytes)
Not plaintext; may be key material or encrypted header. Role unknown.

## What's still blocked (updated)
1. **Bulk sector decrypt** (0x8AA2CA8): DSP ASE instructions need manual
   decode or full unicorn emulation with key material from a valid sector.
2. **IDX decrypt**: inside imported `openPac` — invisible statically.
3. **Practical path**: PPSSPP live memory dump (see PPSSPP-LIVE-RUN-GUIDE.md).
   Needs a display/browser session. Dump the IDX buffer (0x8AA2A34) after
   `openPac` returns, and sector buffers after `0x8AA1204`.

## Tooling built this run
- `/tmp/mips_re.py`: capstone MIPS64-LE disassembler (handles `daddu`),
  `lui`+`addiu` xref scanner, ELF vaddr→file offset.
- `/tmp/t6_emu2.py`: unicorn MIPS emulator with kseg0 shadow-mapping
  workaround + CRC32 table builder. Successfully emulates 0x8AA2E88.

## 2026-10-14 ~22:00 EDT bulk-decrypt worker — DINF CRACKED + BULK ARCHITECTURE MAPPED

### 17. DINF_400.BIN FULLY DECRYPTED (verified, see DINF-400-DECRYPTED.md)
- Fixed keyset at EBOOT **0x88985BC** (`0x8AA3298` with hardcoded constants, then
  `0x8AA2E58` → `0x8AA2CA8`): **K1=0xebcf9603, K2=0xb3bef6a4**
  (C1=0xa9a8aaf2, C2=0xaff764ad). `cipher(K1,K2,dst,120,0,0)` → magic `DINF`.
- Manifest: ver=1, unit=0x800, **2169 entries**, **384051200 bytes**,
  names `DATA401.BIN` / `DATA401.IDX`, build path
  `hdd65/psp/DATA401/20091109_092921/`. 2169×12 = 26028 = IDX size ✓.
  384051200 = 187520 sectors — matches measured nonzero region
  (sectors 230256–417780; first/last partial sectors are zero).
- Reproduce: `python3 tools/dinf_decrypt.py` (self-contained cipher model).

### 18. Second fixed keyset at 0x8898404 (target unknown)
K1=0xe11cf772, K2=0xa0dc9eb4, C1=0x9f7e8f59, C2=0x6c4a824a.
Same struct shape as the DINF loader (decrypts `*(s0+0x48+0xc)`, len `*(s0+0x48+0x18)`).
DATA401.IDX decrypt attempt with this keyset: no 12-byte-entry structure found
(no 2169 count, no plausible LBA runs). IDX likely goes through imported
`openPac`, not this path.

### 19. Bulk decrypt architecture: 0x8AA305C is VERIFY-decrypt (returns 1/0)
- Prologue derives d0..d3 = `buf[0xF1/0x1AB] ^ mask` from each of the two
  0x800-byte input buffers (same tables as the CRC-key extract).
- `cipher(keystructA, bufA, 0x800, 0, 0)` then `cipher(keystructB, bufB, 0x800, 0, 0)`.
- Post-loop (`0x8AA3188`): walks both DECRYPTED buffers word-wise; skips indices
  {0xF1, 0x1AB, d0, d1, d2, d3}; **returns 0 on first mismatch, 1 if all 0x200
  words match**. The two inputs are two encryptions of the SAME plaintext.
- Caller `0x8AA2400`-loop: `0x8AA1204` CRC-reads a header unit into stack (keys
  extracted → header at s2), then a bulk unit is read into s4 with NO CRC check,
  then `0x8AA305C(s2, sp, s4, s1+0x2c)`. The bulk unit uses the PERSISTENT
  file keystruct at s1+0x2c.

### 20. Bulk master key: per-file PRNG (NOT statically recoverable) — BLOCKER
- `0x8A9DB98`: `0x8AA3298(fp, 0,0,0,0)` → K1/K2 from MWC PRNG `0x8B7B600`
  (a=0x4C957F2D), C1/C2 from decrypted blob at 0x8CB9F8.
- `0x8A9DCA4`: `cipher(fp, 8(s5), s7, s1, t0=s6, t1=s1)` — per-chunk tweak:
  t0 = chunk index, t1 = sub-index. Same (K1,K2) per file, keystream varies
  per chunk via the cipher's block counter + warm-up.
- PRNG state lives at +0xA8/+0xAC of the kernel thread struct (`$k0`-derived
  via `0x8B793A4`) — **runtime state, not in the ELF**. Zero-init gives
  degenerate all-zero keys (infinite retry in `0x8AA3298`), so the real seed
  is nonzero and unknowable statically. **Static bulk decrypt is blocked here.**

### 21. Full-region CRC scan: 1 / 187,525 units pass (NEGATIVE RESULT)
Slid 0x800-byte windows over sectors 230256–417780 with the exact EBOOT CRC
(init 0xFFFFFFFF, no final xor): exactly ONE hit — unit 0 (sector 230256,
K1=0x24cfa8a4, K2=0x564928df, confirmed by unicorn emulation of `0x8AA2E88`
returning v0=1). The overnight "bulk does NOT use per-sector CRC-key scheme"
finding is CONFIRMED. (Decrypting unit 0 with its extracted keys yields
high-entropy output — no GMO/TIM2; likely a pack header, not file data.)

### 22. PPSSPP live-dump attempt — ENVIRONMENT BLOCKED
- PPSSPP v1.20.4 SDL AppImage is **static-pie**: LD_PRELOAD shims cannot
  intercept its internal SDL calls.
- No PulseAudio daemon on VM; `SDL_AUDIODRIVER=dummy` is ignored (PPSSPP-side);
  SDL init fails with "Could not setup connection to PulseAudio".
- X11 works in foreground exec but fails ("x11 not available") in background
  exec sessions — live run needs a display-holding parent or root session.
- Recommendation: run PPSSPP from the main agent with a live display, boot the
  ISO to title (pack mount decrypts IDX/DINF into RAM), attach gdb to dump
  emulated PSP RAM (64 MB), scan for `GMO\0`/`TIM2`/`DINF`.

## What's still blocked (updated 2026-10-14 22:15 EDT)
1. **Bulk DATA401.BIN decrypt** — needs the PRNG master key (runtime state) or
   the IDX file map (→ per-file keys). Static path exhausted.
2. **IDX decrypt** — `openPac` (imported PRX) or keyset A; unresolved.
3. Practical path: PPSSPP live RAM dump (see §22).
