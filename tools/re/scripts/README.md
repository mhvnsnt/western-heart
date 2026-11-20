# RE scripts

## Headless (no Ghidra needed)

| Script | What it does |
|--------|--------------|
| `elf_matrix_hunt.py` | Parses an ELF's PT_LOAD segments, scans for 4x4/3x4 float affine matrices (bind poses), reports **virtual addresses** for Ghidra xref. Usage: `python3 elf_matrix_hunt.py <binary>`. First run (Urban Reign SLUS_212.09, 2026-10-19): 11 hits, all false positives — bind matrices are NOT plain floats in the ELF. |
| `psp_elf_xref.py` | PSP ELF static pass (no Ghidra): vaddr↔offset map, `lui`+`addiu`/`ori` xref scan, string watchlist (DATA401/DINF/openPac/ktRead/…), crypto-constant hunt (AES S-box, TEA delta, CRC32 table, XOR-0xA5 idiom), `jr $ra` import-stub census, optional capstone disasm. Usage: `python3 psp_elf_xref.py <elf> --t6 --out report.json`. First run (T6 decrypted EBOOT, 2026-10-22): reproduced every DATA401-RE-NOTES finding exactly + 2 new leads (`DINF_400.BIN` xref @ 0x8899834, static CRC32 table @ 0x8BB0FF8) — see `teardown/tekken6/T6-KEYHUNT-REPORT-2026-10-22.md`. |

## Ghidra headless (Java, via analyzeHeadless)

Run: `analyzeHeadless <projdir> <proj> -process <program> -noanalysis -scriptPath <this-dir> -postScript <Name>.java`
(Java scripts must compile — test with `javac -cp $(find $GHIDRA_HOME/Ghidra -name '*.jar' | tr '\n' ':')`.)

| Script | What it does |
|--------|--------------|
| `find_matrices.py` | PyGhidra version of the matrix hunt (needs PyGhidra init — currently fails headless; use the ELF script instead). |
| `FindBoneRefs.java` | Finds a string's xrefs and decompiles referencing functions. Edit the `pat` bytes for your target. First run: "BONE NUM" @ 0x006b05d8, **0 xrefs** (dynamically referenced or debug-only). |

## Urban Reign notes (2026-10-19)

- SLUS_212.09: LE MIPS ELF, 2 PT_LOAD segs (0x00100000, 0x0034b580).
- Ghidra 12.1.4 headless analysis: ✅ succeeded (R5900 MMI Pcode errors are noise).
- Bind matrices: NOT as plain 4x4/3x4 floats in ELF, NOT as identity tables in char PPKs (see `~/workspace/ur-decode/work/ur_bone_hunt.py`).
- Next: decompile the PPK chunk parser / .gyu loader — the skeleton is loaded at runtime, not hardcoded.
