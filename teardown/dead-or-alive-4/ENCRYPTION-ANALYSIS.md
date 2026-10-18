# DOA4 Custom AFS Encryption Analysis

**Date:** 2026-10-17  
**Analyst:** Subagent (Ghidra RE lane)  
**Status:** PARTIAL — Encryption scheme characterized, full keystream not recovered

## Summary

The 6 encrypted AFS archives (chrone.afs, chrtwo.afs, chrthree.afs, anm.afs, mot.afs, stg.afs — 2.4GB total) use a Team Ninja custom encryption layer on top of standard CRI AFS format. The encryption is a per-file keyed stream cipher (XOR-based). The 4-byte file-specific keys are recovered, but the full keystream generation algorithm remains unknown.

## Recovered File Keys (4-byte, Big-Endian XOR)

Each file's first 4 bytes decrypt to `AFS\0` (0x41465300) with these keys:

| File | Size | Key (BE) | Key Bytes |
|------|------|----------|-----------|
| anm.afs | 2.9MB | 0x80b97b52 | 80 b9 7b 52 |
| chrone.afs | 349MB | 0x7fc2f931 | 7f c2 f9 31 |
| chrtwo.afs | 522MB | 0x7ff843dc | 7f f8 43 dc |
| chrthree.afs | 727MB | 0xfe793a0f | fe 79 3a 0f |
| mot.afs | 71MB | 0x7d40a53e | 7d 40 a5 3e |
| stg.afs | 777MB | 0x7d4e3d2e | 7d 4e 3d 2e |

**Key observations:**
- Keys are unique per file (not shared)
- Keys are NOT stored in the PE binary (searched, not found)
- Keys are NOT simple hashes of filenames (tested MD5, SHA1, CRC32, djb2, sdbm, FNV-1a — no match)
- mot.afs and stg.afs keys are similar (both start with 0x7d), suggesting related derivation
- chrone.afs and chrtwo.afs keys both start with 0x7f

## Ciphertext Structure Analysis

### Repeating 8-byte Patterns

The encrypted files exhibit strong 8-byte repeating ciphertext patterns:

**chrthree.afs** (first 32 bytes):
```
[ 0]: bf3f690f 3eed06e3 | 3eae2660 3eed06e3
[16]: 3eae2660 3eed06e3 | 3eae2660 3f25c788
```
The 8-byte sequence `3eed06e33eae2660` repeats at offsets 0x4, 0xC, 0x14.

**chrtwo.afs**: 8-byte `3f31676a3eb35950` repeats 3x at 0x28, 0x30, 0x38.

**chrone.afs**: 8-byte `3f0b94d43e8542c1` repeats 3x at 0x2c, 0x34, 0x3c.

**anm.afs**: 8-byte `9bff641f6a636a63` repeats at 0x8, 0x18. Also `8bff7c1fafafafaf` repeats 8x at 0xC8-spaced intervals.

### Interpretation

The repeating ciphertext with 8-byte period suggests either:
1. **XOR with 8-byte repeating key** AND repeating plaintext, OR
2. **ECB block cipher** with 8-byte blocks, OR  
3. **Stream cipher** with short-period keystream

If (1) with 4-byte key extended: decrypting chrthree.afs[4:12] with key `fe793a0f` gives plaintext `c0943cecc0d71c6f` which repeats. This would imply the AFS header has repeating 8-byte plaintext — inconsistent with standard AFS format (would require num_files == entry0.offset, etc.).

**Most likely:** The keystream is longer than 4 bytes (not a simple repeat), and the observed repetitions are either coincidental or indicate a more complex keystream generation.

## Ghidra Analysis

### Setup
- **Ghidra:** 12.1.4 at `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/`
- **JDK:** 21 (Temurin) 
- **Target:** `default_pe.bin` (23,068,672 bytes, PE32 Xbox PowerPC big-endian)
- **Language:** `PowerPC:BE:32:default`
- **Project:** `~/workspace/ghidra-projects/doa4/` (56MB, analyzed)

### Findings

1. **AFS filename strings** located in .rdata:
   - `cache:\spr.afs` @ 0x0061e8cd
   - `cache:\snd.afs` @ 0x0061e8ec  
   - `cache:\mot.afs` @ 0x0061e908
   - `cache:\cmn.afs` @ 0x0061e924
   - `cache:\chrthree.afs` @ 0x0061e964
   - `cache:\chrtwo.afs` @ 0x0061e988
   - `cache:\chrone.afs` @ 0x0061e9ac
   - **No xrefs** to these strings (indirect addressing)

2. **Dynamic filename construction** discovered:
   - Format string `%ls.anm%d.afs` @ file offset 0x285f41 (VA 0x00685f41)
   - Format string `%s:\anm.afs` @ file offset 0x28684b (VA 0x0068684b)
   - **No xrefs** to these either (highly optimized code)

3. **CRI AFS library** statically linked:
   - Error strings found: `E0040701:Illigal format(not AFS).(adxf_GetPtStat)`
   - Error strings found: `E20040917 : It is impossible to load AFS files in parallel.`
   - No `adxf_*` symbols (static link, no imports)
   - Only 10 unnamed external functions (import table stripped)

4. **No XOR-heavy functions** found (checked 5000 functions, none with 5+ XOR instructions)
   - Suggests decryption may use ADD/SUB, table lookup, or is inlined

5. **No AFS magic constant** (0x41465300) found in code (checked 191k instructions)
   - Decryption verification may be implicit or use memcmp

### Scripts Developed
Located in `~/workspace/ghidra-projects/doa4/`:
- `FindAfsDecrypt.java` — Find AFS strings and xrefs
- `FindAfsXrefs.java` — Aggressive xref search with data refs
- `FindAfsCallers.java` — Find CRI library callers
- `FindAfsMagic.java` — Search for AFS magic constant in code
- `FindXorLoops.java` — Find XOR-heavy functions
- `FindLis61.java` — Find PowerPC address construction for AFS strings
- `DecompileAround.java` — Decompile around specific addresses
- `FindFmtXrefs.java` — Find xrefs to format strings
- `ListImports.java` — List imported functions

## Hypotheses Tested (Ruled Out)

| Hypothesis | Result |
|------------|--------|
| 4-byte repeating XOR key | ❌ Bytes 4+ decrypt to garbage |
| Incrementing 4-byte key (key+i) | ❌ Block 1+ garbage |
| Key = MD5/SHA1/CRC32(filename) | ❌ No match |
| Key = djb2/sdbm/FNV-1a(filename) | ❌ No match |
| Key stored in PE binary | ❌ Not found (searched all forms) |
| 16-byte repeating key with standard AFS header | ❌ No valid (N, header_size) found for N=1..500 |
| Key table in .data/.rdata | ❌ Only code pointers found |

## Recommended Next Steps

### Option A: Dynamic Analysis (Highest Success Probability)
Run DOA4 in Xenia (Xbox 360 emulator) and dump decrypted AFS from memory:
1. Set up Xenia Canary with DOA4 ISO
2. Breakpoint on file read or AFS parse
3. Dump memory buffers after decryption
4. Extract assets from decrypted dumps

### Option B: Advanced Ghidra Analysis
1. Use Ghidra's data flow analysis to trace from file read syscalls
2. Use P-code emulation to execute decryption function
3. Search for the key derivation function (takes filename, outputs key)

### Option C: Cryptanalysis
The 8-byte repeating ciphertext pattern is the strongest lead. A cryptographer should:
1. Analyze the repeating patterns across all 6 files
2. Determine if it's ECB, CTR with short nonce, or repeating XOR
3. Use the known "AFS\0" plaintext to bootstrap

## Files
- **Ghidra project:** `~/workspace/ghidra-projects/doa4/` (56MB)
- **Decrypted PE:** `~/workspace/doa4-bass/default_pe.bin` (23MB)
- **Encrypted AFS:** `~/workspace/doa4-bass/extracted/*.afs` (2.4GB)
- **Scripts:** `~/workspace/ghidra-projects/doa4/*.java`
- **Prior report:** `~/workspace/doa4-bass/EXTRACTION-REPORT.md`

## Conclusion

The encryption is a per-file keyed XOR stream cipher. The 4-byte keys are recovered, but the full keystream generation remains unknown. The keys are not stored in the binary and are not simple filename hashes — they are likely derived via a custom algorithm or decrypted from an obfuscated table at runtime.

**This is a solvable problem** but requires either dynamic analysis (Xenia) or deeper Ghidra work (data flow/emulation) than static xref analysis could provide.

### Deep-RE audit results — 2026-10-18 (all 8 audits rerun headless, findings banked in `tools/ghidra-audits/findings-audit*.txt`)

The 7 audits (+6b) did **not** crack the keystream generator, but they eliminated
several leads and mapped the code-reference landscape. Per-audit verdicts:

- **Audit1:** AFS filename strings (`cache:\*.afs`, `d:\*.afs`) live in `.rdata`
  (0x0061e8d0–0x0061e9c0) with **zero code xrefs** — nothing in the analyzed
  regions references them. CRI ADX strings (`adxf_GetPtStat`,
  `Illigal format(not AFS)`) confirm the CRI filesystem library is statically
  linked. The 0x822f06d0 S-box lead is **dead**: not in any memory block
  (a runtime/rebased address, not a file VA).
- **Audit2:** Lone `lis r10,0x61` at 0x007725cc; only 8% of `.text` is
  disassembled (193,898 of ~8.8MB). 10 import externals are **unnamed thunks**
  (Ghidra did not resolve the Xbox 360 XEX import table).
- **Audit3:** The lone lis-0x61 site is a **magic-number dispatch**, not the AFS
  path: it builds 0x00617061 / 0x00767061 / 0x21767061 (`!vpa`-family words) and
  compares them against a struct field — archive-format sniffing, not crypto.
  **Zero hits** for the 6 file keys as BE32 in .text/.rdata/.data — the keys are
  definitively not stored in the binary. No `lis *,0x4146` (AFS magic is never
  constructed in code). 7 `bl`→thunk sites feed Audit4/5.
- **Audit4:** Thunk bodies are empty; caller decomp is partial (bad-instruction
  warnings — auto-disassembly is unreliable in those regions). `FUN_00d9df70`
  is the most crypto-flavored caller: unnamed externals + constants
  0xfffe07d1 / 0x82b7e67c / 0x26404 and 0x10000/0x20000 mode flags.
- **Audit5:** All 7 import-calling functions disassembled; call graph mapped
  (00d9df70 → externals 0xf591d4/0xf587a4/0xf591c4; 00d9e1f0 → 0xf587c4 ×2,
  0xf587b4; the 00b8xxxx group → 0xf58984/0xf58974/0xf589e4).
- **Audit6/6b:** 22 `lis *,0x8261` sites (runtime-addressed `.rdata` refs), but
  their contexts are **vtable dispatches and struct/string refs** in
  0x00a0e1d0–0x00a2adcc — not AFS filename construction. No BE32 pointers to
  the strings stored anywhere.
- **Audit7 (the money scan):** **0** lis/ori|addi pairs build addresses in
  [0x8261e800, 0x8261ec00] (the AFS filename strings' runtime range).
  Combined with zero xrefs (Audit1) and no stored pointers (Audit6): **no
  analyzed code references the AFS filename strings at all.**

**What this proves about the keystream question:** the string-following strategy
(AFS filename → open call → decrypt routine) hit a wall — the decrypt path is
either in the **undisassembled 92% of `.text`** or reached through an idiom the
audits didn't scan (TOC-relative, register-indirect, or runtime-constructed
paths via the CRI library taking an index rather than a pointer).

**Next leads, in order:**
1. Expand disassembly coverage (8% → full `.text`) and re-run the string-xref
   hunt — the AFS-string-referencing code is most likely in the dark 92%.
2. Resolve the 10 unnamed externals against Xbox 360 XDK import ordinals /
   known CRI ADX signatures — unblocks Option B (data-flow from file-read
   syscalls to the keystream routine).
3. Follow up `FUN_00d9df70` (crypto-flavored constants + 4 externals) with a
   targeted disassembly/decompile pass.
4. Dynamic analysis under Xenia (break on AFS file reads, watch keystream
   generation) remains the highest-probability path if static work stalls.

## Deep-RE audit continuation — 2026-10-18 (watchdog-resumed)

**Context:** Prior teardown delivered everything except the 6 encrypted AFS header
keystreams (chrone/chrtwo/chrthree/anm/mot/stg). 129 triangulated GLBs merged via
PR #248. This pass continued the header-keystream deep-RE.

**What ran (05:55–06:25 CDT):** 8 headless Ghidra audit scripts against the
decrypted PE (default_pe.bin) in project `~/workspace/ghidra-projects/doa4/`
(script copies banked in `tools/ghidra-audits/`):
- Doa4Audit1: string-driven decrypt-path hunt (AFS filename strings, `cache:\*.afs`,
  `%ls.anm%d.afs` format strings; pointer-table detection; S-box VA 0x822f06d0 check)
- Doa4Audit2: idata externals + xref counts; `lis *,0x61` byte scan; rebased S-box lead
- Doa4Audit3: surgical strikes — disasm/decompile around 007725cc (lone lis-0x61
  site); `lis *,0x4146` (AFS magic construction) scan; 6 file keys as BE32 scan;
  `bl`-to-thunk scan; `d:\*.afs` string xrefs
- Doa4Audit4: disasm around bl->thunk call sites; decompile callers to identify
  the 10 externals (file I/O? alloc? crypto?)
- Doa4Audit5: (script present; see source)
- Doa4Audit6: `lis *,0x8261` in .text (unrelocated refs to runtime 0x8261xxxx
  .rdata strings), flagged when followed by ori/addi with 0xe8xx–0xe9xx
  (AFS filename string offsets)
- Doa4Audit6b: (script present; see source)
- Doa4Audit7: lis/ori|addi pairs building runtime addresses in [0x8261e800,
  0x8261ec00] (AFS filename strings)

**Outcome:** Cron execution timeout killed the worker at 06:25 CDT mid-Audit7.
The audit SCRIPT artifacts survived (banked here); the audits' FINDINGS output
was lost in the kill (never committed). Ghidra project saved with the 7 new
scripts + newly disassembled regions.

**Resume instructions (next deep-RE turn):**
1. Rerun Doa4Audit1–7 headless against `~/workspace/ghidra-projects/doa4/` —
   each script prints findings to stdout; capture each to a findings file.
2. COMMIT FINDINGS EARLY AND OFTEN (after EACH audit) — a timeout kill must
   never again lose uncommitted output. Net-zero rule: audit text is small.
3. Update this file's Conclusion with whatever the audits prove about the
   keystream generator, and chase Option B (data-flow from file-read syscalls
   to the keystream routine) before Option C cryptanalysis.

## Deep-RE audits 11–18 — 2026-10-18 (worker continuation)

**Context:** Audits 1–10 closed with the keystream NOT cracked (see findings-audit1..10).
This run continued with per-audit commit+push discipline on branch
`feat/gapfill-decode-all-agents` (commits 6ba6b56, 629952d, 88baa05, 611a1b7, 3f49de8,
7051821 — all pushed to origin). Headless Ghidra 12.1.4, program `default_pe.bin`,
project `~/workspace/ghidra-projects/doa4/`.

- **Audit11** (thunk-caller map): all 9 crypto/content thunks' callers mapped.
  Tight clusters: 00b8xxxx–00b9xxxx (SHA/content) and 00d9xxxx (content manager).
  6 call sites in "(none)" (no containing function) — the disassembly was
  incomplete in the crypto neighborhood.
- **Audit12** (cluster decompile): FUN_00b8ea08 identified as prime lead — SHA-style
  call whose output feeds TWICE into FUN_00b91ec8 with mode flag 1 (classic
  derive-key-then-decrypt shape). FUN_00b8dfd8 = plain XamContentOpenFile wrapper
  (excluded). Slot33/34 "XeCryptShaUpdate/Final" names flagged UNVERIFIED (call
  arity doesn't match XDK prototypes).
- **Audit13** (sweep 68.8%→85.6%): +369,141 instructions via 0x10-grid sweep;
  re-hunt over ALL new code: ZERO AFS-string xrefs, ZERO lis-0x8261 pairs, ZERO
  lis-0x4146, ZERO lis/ori key constructions (honest negative).
- **Audit14** (Xenia feasibility): NOT feasible — no GPU on this VM (no VGA, no
  /dev/dri, 2 vCPUs), Xenia-on-Linux experimental, DOA4 not documented playable,
  no bootable game image locally. Recommended alternative: Ghidra P-code emulator
  (CPU-only) once a candidate routine is bounded.
- **Audit15** (prime-candidate decompile): the Audit12 "lead functions" are 2-insn
  THUNKS — FUN_00b91ec8→FUN_00dfd4a8, FUN_00b92120→FUN_00dfd4c8. Real neighborhood
  is 00dfxxxx, never before analyzed. 5 unowned call sites persisted post-sweep.
- **Audit16** (createFunction): all 5 orphaned sites converted to functions
  (FUN_00b8c7b4/00b92058/00b91fdc/00b8dc94/00b8df88). Thunk targets 00dfd4a8/00dfd4c8
  would NOT disassemble (0 instructions; hand-verified the bl encoding is correct).
- **Audit17** (new functions + byte dump): the 5 are wrappers — SHA helpers
  (00b8c7b4, 00b8dc94), SHA-chaining loops (00b91fdc, 00b92058), content-open
  wrapper (00b8df88). Two NEW import slots found: 40 (thunk 0x00f589e4), 41
  (0x00f589f4). Two DIRECT BRANCHES into 00dfxxxx (b 0x00dfd4f8, b 0x00dfd518).
  Raw bytes at 0x00dfd4a8 hand-decode as 64-bit PPC (std/ld prologue/epilogue
  fragments + blr) — the 32-bit disassembler rejects them.
- **Audit18** (language + slot naming): language = **PowerPC:BE:32:default**
  (explains the 00dfxxxx refusal). Slot40 = XInputdFFGetDeviceInfo (xboxkrnl 642,
  already in audit9) — device path, not crypto. Slot41 = XAudioSubmitDigitalPacket
  per Xenia master (xboxkrnl 508) — BUT call-site arity (2 ptrs, byte return)
  contradicts the name; flagged UNVERIFIED (possible ordinal skew). Ghidra's
  IMPORTED table holds only 2 symbols; all naming comes from the raw IAT at file
  0x400 + Xenia tables.

**Net verdict after 18 audits:** the keystream routine's location is STILL UNKNOWN.
Every analyzed function in the crypto/content cluster is a wrapper or helper; the
cipher itself is not in any disassembled function. The only unexplored lead is the
00dfxxxx region (branch/bl targets 0x00dfd4a8/0x00dfd4c8/0x00dfd4f8/0x00dfd518)
whose bytes are 64-bit PPC encodings inside a 32-bit binary.

**Next leads, in order:**
1. 64-bit-aware look at 00dfxxxx (decode the std/ld stream fully by hand or with a
   64-bit PPC disassembler; determine code vs data vs encrypted code).
2. Verify slot41's true identity (kernel-version ordinal tables; Xenia Canary's
   newer xboxkrnl table).
3. Ghidra P-code emulation of the SHA-chaining loops (FUN_00b91fdc/00b92058) with
   stubbed imports — CPU-only, no GPU needed — to observe what the SHA outputs feed.
4. If 00dfxxxx proves to be a dead end, pivot to cryptanalysis of the AFS table
   cipher (16-byte periodic, per-file keys — characterized 2026-10-17) rather than
   more static hunting: 18 audits have exhausted the static signature space.
