# RE QUEUE — every teardown game, lined up for the Ghidra+MCP treatment

**Updated:** 2026-10-19. Grounded in `teardown/TEARDOWN-STATUS.md` + this week's decode lanes.
Rule: one game at a time through the bench. Urban Reign is the proof run.

## The queue (priority order)

| # | Game | Platform | Teardown % | RE target (next) | Status |
|---|------|----------|-----------|------------------|--------|
| 1 | **Urban Reign** | PS2 | ~95% | SLUS_212.09 bind matrices + vertex→bone mapping | 🔥 IN GHIDRA NOW (2026-10-19): 6.3MB ELF under headless analysis; `scripts/find_matrices.py` queued |
| 2 | Tekken 6 | PSP | ~30% | DATA401 key derivation from decrypted EBOOT (4.0MB ELF, PAC symbols confirmed: `packdatas_t`, `ReadInfo`, `ktRead`) | 🔥 ACTIVE (2026-10-22): `tools/re/scripts/psp_elf_xref.py` key-hunt reproduced all watchdog findings + 2 new leads — `DINF_400.BIN` single code xref @ 0x8899834 (next static target: disassemble the DINF reader), static CRC32 table @ 0x8BB0FF8. Report: `teardown/tekken6/T6-KEYHUNT-REPORT-2026-10-22.md`. IDX decrypt still inside imported `openPac` → PPSSPP live dump remains the practical path |
| 3 | WWE WrestleMania XIX | GC | ~80% | Format semantics (watchdog lane active) | QUEUED |
| 4 | Tekken 3 | PS1 | 100% | Moveset/anim deep RE (teardown complete; RE for gaps) | QUEUED |
| 5 | WWF No Mercy | N64 | 100% | Systems RE (teardown complete; RE for gaps) | QUEUED |
| 6 | Virtua Fighter 5 | PS3 | 100% | Customization/moveset RE (teardown complete) | QUEUED |
| 7 | Tekken 7 | PS4/PC | ~40% | Full game acquisition first (never fully acquired) | BLOCKED — acquisition |
| 8 | Eastern Mind | PC-98 | ~20% | Extraction (game safe on release `eastern-mind-v1`) | QUEUED — extract first |
| 9 | Tekken Tag Tournament 2 | X360 | ~15% | STFS extraction (26/26 chunks on release) | 🔥 ACTIVE (2026-10-22): TTT2-PC static-recomp port (shihabal3amri, XenonRecomp) — its installer builds assets from X360 disc+TU3, i.e. a working TTT2 asset pipeline (PAC/PACH, BPE textures, XMA via FFmpeg, LZX via libmspack). Assessment: `teardown/tekken-tag-tournament-2/TTT2-PC-PORT-ASSESSMENT.md`. Next: read their `tools/`+`re/recomp/` instead of reversing STFS blind |
| 10 | Dead or Alive 4 | X360 | ~15% | Reassemble ISO + extract (30/30 chunks on release `doa4-iso-v1`) | QUEUED — extract first |
| 11 | Soulcalibur II | Xbox/PS2 | ~60% | PS2 filesystem RE (owner decision needed) | QUEUED — needs decision |
| 12 | Soulcalibur VI | PC | ~10% | Acquire binary (32GB) | BLOCKED — acquisition |
| 13 | Dead or Alive 6 | PC | ~10% | Acquire binary (50GB+) | BLOCKED — acquisition |
| 14 | Tekken 8 | PC | — | Acquire / assess | BLOCKED — acquisition |
| 15 | Def Jam: Fight for NY | PS2/Xbox | — | Assess teardown dir | QUEUED — assess |
| 16 | Street Fighter EX series / 3D SF games | PS1/PS2 | — | Assess teardown dirs | QUEUED — assess |

## WWE 2K18 / 2K19 note (owner 2026-10-19)

Owner asked whether WWE 2K18/2K19-level games were ever pulled in. **They were not**
— no 2K18/2K19 teardown exists in `teardown/`. The WWE 2K pull plan lives in
western-heart #253 (MERGED). 2K18/2K19 acquisition + teardown is a new work item,
not a continuation. Added to the backlog below.

## Backlog (not yet torn down)

- WWE 2K18 / 2K19 (PC): acquire → teardown → RE queue
- DOA / Virtua Fighter moveset extraction for Tekken-style input mapping (owner 2026-10-19)

## How a game moves through the bench

1. `tools/re/analyze.sh <binary> <game>` — import + auto-analysis, headless
2. `scripts/` — targeted hunts (matrices, strings, format magics)
3. GhidraMCP session — agent-driven decompilation of the loader/format code
4. Findings → `teardown/<game>/` docs + extracted assets → repo
5. QUEUE.md status updated
