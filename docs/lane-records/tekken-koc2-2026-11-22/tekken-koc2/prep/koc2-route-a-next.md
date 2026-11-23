# KoC2 Route A — this lane's disassembly (2026-11-22/23)

Tool: `~/workspace/bannon-vm-unblock-prep/koc2-venv/bin/python`
(Capstone 5.0.7 + pyelftools, verified working this lane).
ELF: `~/workspace/bannon-precracked-koc2/work/SLPM_656.02`
(3,048,408 B, sha256 `824ef43ea1083527d681e861aef341048e8380a19dd02e7917b9c1a648ab34fe`,
re-verified this lane — matches the precracked lane).
Disassembler: `~/workspace/bannon-precracked-koc2/work/disasm_region.py`
(Capstone MIPS64 LE). No decode was produced; no joint data exists.
This is loader mapping only.

## What was already known (precracked lane, re-verified this lane)

- `0x1189B8` is a CODE address (`lui $a0, 0x3b` at 0x1189B8, then
  `addiu $a0, $a0, -0x7420` = 0x3a8be0, the "MotionBase" string). The
  old note ("chunk-name cross-reference at 0x1189B8") recorded the
  instruction's own address as if it were the referenced data address.
  Correct target: string at **0x3a8be0**, referenced from code at
  0x118994 and 0x1189B8. Confirmed in `xref-scan.log` (2 lui hits).
- MotionBase init function at **0x118970** (returns 0x1189d8); calls
  0x28b178 with chunk IDs 0x7d6 (2006) and 0x7d7 (2007), then calls
  **0x2894c0** with the "MotionBase" and "BasicMotion" strings.
- Motion evaluator at **0x2fe7d0** (per-frame evaluator/blender, NOT a
  bitstream reader — no lbu/sllv bit-extraction loop in its first
  0x130 bytes; Capstone MIPS64 chokes on PS2 MMI ops there).
- Byte 1 of an MVS file is probably NOT a frame count: file00000–
  file00003 share byte 1 = 218 at sizes 2,284 / 535 / 1,818 / 3,082 B.
  Do not build a decoder on byte 1 as frames.

## New this lane — three functions disassembled

### 0x2894c0 — chunk-name lookup (14 instructions, log: koc2-2894c0-chunk-lookup.log)

- Loads the list head from `gp-0x5008`, calls **0x30cf80** with
  a0 = head+0xc, a1 = the input name pointer, a2 = 0xf (15 — a length
  limit, consistent with a bounded string compare: "MotionBase" is
  10 chars). Then clears a flag byte at offset 0x1b of the head
  (`sb $zero, 0x1b($v1)`) and returns the 0x30cf80 result.
- Reading: this is the chunk-name lookup the init function calls with
  "MotionBase"/"BasicMotion". The real comparison/hash lives in
  **0x30cf80** — disassemble that next.
- The window also caught the neighbouring allocator (0x2894f0):
  rounds sizes to 0x80, links nodes into the gp-0x5008 list, and stamps
  each node with magic **0x4b4f4332 = "KOC2"** (lui 0x4b4f + ori 0x4332,
  stored at node+0x1c). NEW finding this lane: MVS chunk nodes are
  "KOC2"-stamped in memory — a usable signature when tracing the
  loader's allocations.

### 0x28b178 — chunk loader (0x40 stack frame, log: koc2-28b178-chunk-loader.log)

- Calls 0x28aea0 (chunk-table accessor), computes entry =
  table+0x1c + index*16 (`sll 4`).
- If a1 == 0: calls 0x28b0b8, then **0x289590** (the 0x80-aligned
  "KOC2"-stamping allocator above) to allocate the chunk node.
- Then calls **0x28b0a0** (entry fetch) and **0x28a6e8** (read/copy:
  takes a base + an offset, `lhu` count at entry+0xe, stride math
  ×13×4 = 52-byte table entries at 0x3f0000+0x5820 — `lui $at,0x3f`
  then `sw $s2, 0x5820($at)`).
- Reading: this loads a chunk by id into a registered table. It is
  NOT the MVS bitstream reader — it moves chunk buffers around. The
  reader is downstream of 0x28a6e8 or in a callee of the evaluator
  0x2fe7d0. Next: 0x28a6e8, 0x28aea0, 0x28b0a0, 0x28b0b8.

### 0x28b108 — range helper (log: koc2-28b108.log)

- Tiny: if a2 == a1, tail-jumps to 0x28b0b8; else returns. A
  bounds/equality test used by the loader. No motion logic.

## Next functions to reverse (in order)

1. **0x30cf80** — the compare/hash inside the chunk-name lookup.
2. **0x28a6e8** — the read/copy the loader calls per chunk entry.
3. **0x28aea0** — chunk-table accessor. **0x28b0a0** — entry fetch.
   **0x28b0b8** — the loader's fallback/validation target.
4. Callees of evaluator **0x2fe7d0**; find the function that consumes
   an MVS buffer (look for lbu + sllv + table-driven branch).
5. Re-fit MVS header statistics on all 16,660 files with header
   family as a covariate (13 samples are not enough).
6. Then file 01999 (WrestlerData, 2,285-byte records) to map moveset
   slots → MVS files → move names — only after the bitstream reads.

## Stale docs to correct (do not follow the old text)

- `~/workspace/bannon-vm-unblock-prep/koc2/koc2_motionbase.py`
  header: says "No KoC2 ELF exists in this workspace" (false since
  the precracked lane downloaded SLPM_656.02) and hunts 0x1189B8 as a
  data address (corrected above). The file was NOT edited here; treat
  its xref hunt as superseded by `xref_scan.py` + this note.
- Any doc citing "byte 1 = frame count (r=0.83)" as fact: doubtful
  per the four-file counterexample above. The r=0.83 fit came from
  the dominant header family only; re-fit before using.
- Capstone note: use MIPS32 + PS2 MMI decoding or Ghidra with the
  PS2 language for 0x2fe7d0 (MIPS64 mode emits `.byte` gaps there).
  The three windows disassembled this lane decoded cleanly in
  MIPS64 mode — no gaps.
