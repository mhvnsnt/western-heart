# DOA4 Phase 10 — Job 1: ANM reader (G4) — environment unblocked, reader hunt executed, layout still NOT cracked

## Environment fix (the phase-9 blocker, now dead)
Phase 9 reported "no Java runtime on this VM." **False**: the JDK was present but not on PATH. `JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1` (Temurin 21.0.12.1) + `analyzeHeadless … -process default_pe.bin` runs Ghidra scripts to completion (verified repeatedly this session; logs in scratch `p10/ghidra_*.log`). Note: omitting `-process default_pe.bin` leaves `currentProgram == null` (script NPE) — the other trap behind phase 9's failure.

## What the reader hunt found (FindAnmReader.java → v2 → v3 → v4, all committed in `phase10/tools/`)
- Phase-9 script **crashes** at line 22 (substring out-of-bounds after a `replaceAll` shrank the string) after printing 25 CRI-ADX library error strings — it never reached its xref stage in any phase.
- v2 raw memory byte-scan: 413 pattern hits. The XEX contains a **file table at 0x61E8CD–0x61E9DC**: `cache:\` + `d:\` path pairs for spr/snd/mot/cmn/avt/stg/chrone/chrtwo/chrthree .afs files. **`anm.afs` appears only as `d:\anm.afs` @ 0x61E940** (no cache: twin). Other anm strings: `anm%d.afs` @ 0x685F3C, `D:\bin\anime_cm.bin`, `anm_version.bin`.
- v3: dumped the table; **ZERO xrefs** to any address in the table range in Ghidra's reference manager.
- v4: scanned all memory for BE u32 pointer values into the table: **5 pointer locations** (0x4766B1→0x61E961, 0x47A5CD→0x61E821, 0x4808CD→0x61E861, 0x49276D→0x61E961, 0x583B49→0x61E861) — a data-side descriptor array points at the table, but **ZERO code xrefs to those pointer locations either**. The PPC code reaches the table by computed addressing that this project's analysis never materialized as references. Tracing further needs a PPC lis/addi constant scan for the table's high half (0x0061) filtered to the anm entry index — named as the exact next step.
- **No decompiled reader function was obtained, so no shift/mask pattern, no bit-level field layout, and no record→stream mapping. No parser beyond the phase-8 structural one, and NO CLIPS shipped (gate discipline: no index → no speculative clips). G4 stays open.**

## New container fact
`anm.afs` does **not** start with AFS magic (first bytes `c1 ff 28 52`) — despite the name it is not a plain CRI AFS container; there is no TOC to walk. (chr/mot/stg heads sampled in phase 7 were plaintext; anm's head is the structured exception.)

## Secondary route (ANM-READER.md fallback) — EXECUTED, negative
Bit-unpack of the head at field widths 9–13 bits, MSB-first and LSB-first (`scratch p10/bitunpack.py`): the (v+1)%32 grid fraction is ≈0.11–0.15 at every width (= chance; the real grid is 99.7% in BE s16 ch4/ch5). LE re-interpretation destroys the grid (0.00). The packing is therefore NOT a uniform-width bitstream across the head; if fields are packed, the packing is per-record or variable — indistinguishable without the reader.

## Exact remaining unknown (unchanged in substance, narrowed in route)
Bit-level field layout of the 16B head records + record→stream mapping into the float body regions. Next decisive step: PPC constant-scan (lis/addi pairs materializing 0x61E940 / the descriptor array at 0x4766B1…) → containing function → decompile → shift/mask widths. All tooling for it is committed (`phase10/tools/FindAnmReader2/3/4.java` + logs pattern).
