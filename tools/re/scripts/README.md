# RE scripts

## Headless (no Ghidra needed)

| Script | What it does |
|--------|--------------|
| `elf_matrix_hunt.py` | Parses an ELF's PT_LOAD segments, scans for 4x4/3x4 float affine matrices (bind poses), reports **virtual addresses** for Ghidra xref. Usage: `python3 elf_matrix_hunt.py <binary>`. First run (Urban Reign SLUS_212.09, 2026-10-19): 11 hits, all false positives — bind matrices are NOT plain floats in the ELF. |

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
