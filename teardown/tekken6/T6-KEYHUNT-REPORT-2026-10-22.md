# Tekken 6 PSP — DATA401 Key-Hunt Report (2026-10-22)

**Tool:** `tools/re/scripts/psp_elf_xref.py` (new permanent RE-bench stage; stdlib +
optional capstone — no Ghidra needed, runs on any Linux VM)
**Target:** `teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` (4,158,144 bytes,
ELF32-LE MIPS, entry 0x8804124, single PT_LOAD file 0x1018 → vaddr 0x8804018)
**Runtime:** ~5s on this VM. Full JSON: regenerate with
`python3 tools/re/scripts/psp_elf_xref.py teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF --t6 --out report.json`

## Verification against DATA401-RE-NOTES.md (watchdog ground truth)

Every previously known finding reproduces exactly:

| Known finding | Tool result |
|---|---|
| `openPac` string @ 0x8BCE704, single xref @ 0x8AA1090 | ✅ exact |
| `ktRead` @ 0x8BCE73C, xrefs @ 0x8AA1A70, 0x8AA2098 | ✅ exact |
| `disc0:/sce_lbn0x%x_size0x%llx` @ 0x8BCE744 | ✅ exact (the +4 correction) |
| 268 import stubs @ 0x8B88C68–0x8B894C8 (`jr $ra` loader-patched) | ✅ exact — 268 stubs in range 0x8B88C68–0x8B894C0 |
| XOR-0xA5 string-decrypt loops @ 0x8AA1940–0x8AA1A2C | ✅ — idiom (`addiu $x,$zero,-91`) at 0x8AA1930/1950/198C/1A04, i.e. 4 bytes before each loop entry |
| Key-extract masks `38bfe591`, `d3610818` @ 0x8BCE780 | ✅ exact |
| No AES S-box, no TEA delta anywhere | ✅ confirmed (still none) |

## NEW leads this run

1. **`DINF_400.BIN` has exactly one code xref: 0x8899834.**
   The 120-byte encrypted DINF file (suspected key material per RE-NOTES §16) is
   referenced by string at 0x8B94E48 and loaded at 0x8899834 — far from the pack
   code (0x8AAxxxx). Disassemble `0x8899834 ± 0x200` next: whatever function this
   is reads DINF_400.BIN, and its caller chain is the shortest path to the
   IDX/data-region key.
2. **A static CRC32 table exists at 0x8BB0FF8** (standard poly 0xEDB88320).
   RE-NOTES §12 says the sector-CRC table is *built at runtime* at 0x8CBBA00 by
   0x8AA2F54 — but a second, static table is baked into the binary. Two CRC
   users → check which functions reference 0x8BB0FF8 via the lui-xref map; the
   IDX path may use the static table (different integrity scheme than sectors).
3. **16 XOR-0xA5 idiom sites total** (not just the 3 pack-code loops): clusters at
   0x886Bxxx, 0x898Axxx/0x898Fxxx, 0x8A7Axxx. The string-decrypt helper is a shared
   utility — any newly decrypted string table in the pack path is worth dumping.
4. **`%s/DATA401.IDX` format string @ 0x8BCE70C, xref @ 0x8AA17E0** — the IDX open
   path sits 0x700 bytes before the ktRead wrappers; the decrypt-on-read hook (if
   any) is between 0x8AA17E0 and 0x8AA2098.
5. **Import-stub census:** 2,361 `jr $ra;nop` pairs binary-wide; only the
   0x8B88C68 range (268) is the PSP import table — the other six ranges
   (16/13/12/49/73/13 stubs) are internal dispatch tables, not loader imports.
   Static call-graph builders should treat only the 268-range as opaque.

## Still blocked (unchanged)

- Bulk sector decrypt 0x8AA2CA8 (DSP ASE instructions — needs unicorn emulation
  with real key material, or Ghidra with a DSP ASE SLEIGH patch).
- IDX decrypt inside imported `openPac` (invisible statically; PPSSPP live dump
  per `PPSSPP-LIVE-RUN-GUIDE.md` remains the practical path).

## Next static target (concrete)

`python3 tools/re/scripts/psp_elf_xref.py EBOOT.DECRYPTED.ELF --disasm 0x8899700:0x400`
— disassemble the DINF_400.BIN reader at 0x8899834 and follow its callers.
The lui-xref map in the JSON report already lists every code address that loads
the DINF string address; start there, not from the pack code.
