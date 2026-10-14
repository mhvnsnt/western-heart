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
