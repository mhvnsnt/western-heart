# tools/anim/exe_re — static reverse engineering of TekkenGame-Win64-Shipping.exe (read-only)

The exe lives ONLY in the private GRE repo's release `t7-shipping-exe-20261031` (download through the API asset
endpoint, see docs/handoff/HANDOFF-CLAUDE-2026-10-31.md). Never commit it, never run it, keep it in its own folder,
and run these scripts with `python3 -I` from a different directory (`pip install --user capstone pefile`; with `-I`
the scripts add the user site-packages themselves).

| Script | Use |
|---|---|
| `string_xrefs.py EXE str...` | where strings live and which instructions reference them (RIP-relative scan) |
| `magic_compare_funcs.py EXE` | functions that compare against both 0x64 and 0xC8 (found the anim sampler) |
| `pdata_near.py EXE lo hi` | function boundaries (.pdata), incl. chained fragments |
| `disasm_range.py EXE lo-hi ...` | Intel-syntax disassembly of RVA ranges |
| `rip_constants.py EXE lo hi` | resolve every RIP-relative operand in a range: .rdata floats, imported functions (sinf/cosf/modff) |

Findings: docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md, section "SOLVED IN THE EXE".
