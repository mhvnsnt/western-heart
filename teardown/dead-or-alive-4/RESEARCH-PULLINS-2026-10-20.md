# DOA4 Research + Pull-ins — 2026-10-20 (sweep lane 3, research mandate)

Owner order 2026-10-20 ~07:59 CDT: heavy research, pull in and wire up
everything needed, highest quality. Note on scope: DOA4 is an **Xbox 360**
(XEX2/XGD) title, not original Xbox — the OG-Xbox ecosystem items below are
recorded with that correction.

## Pull-ins (landed in this PR)

| What | Source | License | Landed at | What it unlocked |
|---|---|---|---|---|
| simontime/XPR2 (C# XPR2 archive extractor/repacker) | https://github.com/simontime/XPR2 | **The Unlicense** (public domain) | `tools/open-source/XPR2-simontime/` (source + LICENSE, verbatim) | Reference implementation for the Xbox 360 XPR2 bundle layout (header/resource records) to cross-check our XPR2 carving of the 219 DOA4 textures; candidate converter base for TX2D→DDS |
| Ghidra audit script Doa4Audit19.java | this lane, run against existing project `~/workspace/ghidra-projects/doa4/` (Ghidra 12.1.4) | our own work | `tools/ghidra-audits/Doa4Audit19.java` + `findings-audit19.txt` | Closed the 00dfxxxx lead: the region is the XDK CRT `_savegprlr/_restgprlr` helper block (see findings) |
| Capstone 5.0.7 (already installed system-wide) | https://github.com/capstone-engine/capstone | BSD-3-Clause | used in place, not vendored | PPC disassembly of the 64-bit-encoding CRT block that Ghidra's 32-bit PPC language rejects — the decisive Audit 19 evidence |

## Researched, documented, NOT pulled (with reason)

| What | Source | License | Why not pulled |
|---|---|---|---|
| parkerallan/doa4-recomp — full XenonRecomp recompilation of this exact XEX to C++ (23,651 functions) + RexGlue app scaffolding | https://github.com/parkerallan/doa4-recomp | **No license file** (all rights reserved by default) | Studied locally as research evidence (Audit 19 cross-check: `__savegprlr_28` naming; AFS paths `d:\chrone.afs`, `cache:\` mount notes in `src/dead_or_alive_4_app.h`). Code not vendored into this repo without a license. Its existence is the strongest future lever: the whole guest code as searchable C++. |
| hedge-dev/XenonRecomp (the recompiler toolchain) | https://github.com/hedge-dev/XenonRecomp | MIT | Toolchain, not a DOA4 artifact; pulling the full toolchain is a separate lane's call. Referenced here because doa4-recomp's generated code derives from it. |
| XboxDev/ghidra-xbe (Ghidra XBE loader) | https://github.com/XboxDev/ghidra-xbe | No license file shown | Original-Xbox XBE only — DOA4 is XEX2 (Xbox 360); our PE was already extracted with 360tools and loads in Ghidra as PPC BE. Not applicable; recorded to close the OG-Xbox branch of the research mandate honestly. |
| Noesis (Rich Whitehouse) + DOA5/NG3 Noesis plugins | noesisengine.com; community plugins target DOA5/Ninja Gaiden 3 (TMC/TTM formats) | Noesis is closed-source freeware; plugins vary | No published Noesis plugin handles DOA4's AFS/XPR2-table layout (DOA4 predates the DOA5 TMC format family). Documented as a dead end after search; the DOA4 model path stays our XPR2-table decoder. |
| AFS Explorer / CRI AFS tooling lineage | community tools (PES-era AFS Explorer and successors) | varies/closed | They parse STANDARD CRI AFS only. DOA4's six archives have an obfuscated TOC (16-byte periodic cipher) over plaintext payloads — standard tools reject them, which is consistent with every finding since 2026-10-16. Our `tools/afs_extract.py` already covers the standard archives (961 files). |

## Research findings that mattered

1. **The recomp project proves the game opens the original .afs files
   directly** (`cache:\chrone.afs` etc. symlinked to the game data dir) —
   no external decryption step exists outside the XEX; whatever unscrambles
   the TOC happens inside the CRI adxf code in the binary.
2. **The AFS loader is table-indirect**: six 28-byte-stride partition
   descriptor tables in .data point at the filename strings (Audit 19).
   This is why 19 audits of string-xref hunting found nothing, and it names
   the next static target (the adxf open path that consumes those tables).
3. **No community tool or published format doc cracks the DOA4 TOC cipher.**
   GitHub code search for the archive names and XPR2-in-DOA4, plus web
   search of the DOA modding scene, returned no extractor/converter for
   DOA4's chr*/anm/mot/stg archives. The 4-byte header keys remain
   known-plaintext recoveries, derivation unknown (0/6 by algorithm).
