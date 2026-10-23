# DOA4 Phase 17 — Job 1: faithful per-section Ghidra project

Binary: `default.xex` retail sha256
`56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f`
(release `doa4-iso-extracts-20261022`, re-verified this lane),
analyzed as its decrypted PE form `default_pe.bin` (23,068,672 B,
sha256 `eaa1885a2322df0cf1e8c236a0405a37eeb31b7fdb12b5392a6acc2cabce99d0`).
Tooling: `phase17/tools/build_ghidra_project_p17.sh`,
`phase17/tools/ghidra-scripts/SetBaseP17.java`,
`phase17/tools/ghidra-scripts/ExportP17.java`,
`phase17/tools/ghidra-scripts/SeedFunctionsP17.java`,
`phase17/tools/pdata_parse_p17.py`. Grades as before.

## §1 The phase-16 blocker, root-caused (PROVEN)

Phase 16 §3b: "the reconstructed PE imports at image base 0 with
an address space ending at 0x10FFEF". Reproduced exactly this
lane, then diagnosed with a probe script against the saved
project: the program had language `x86:LE:16:Real Mode`, one
0x450-byte CODE block, and a 21-bit `ram` space (max offset
0x10FFEF). **Ghidra's MZ loader claims `default_pe.bin`** (the
file starts with the MZ magic and carries a `.bin` name), so the
stock import never reaches the PE loader at all. It is a loader
misdetection, not a PE reconstruction problem.

Fix (in the banked build script): force the loader and the
language on the headless import — `-loader PeLoader -processor
PowerPC:BE:32:default`.

## §2 The faithful project (PROVEN)

With the PE loader forced, sections land at header image base
0x400000 + RVA. `SetBaseP17.java` (pre-script, runs BEFORE
analysis) shifts the image base to the TRUE XEX VA base
0x82000000. Because every true VA is 0x82000000 + RVA, the
uniform shift places every section exactly:

| block | VA range | mapping |
|---|---|---|
| Headers | 82000000–820003FF | |
| .rdata | 82000400–822B3EF7 | VA = file + 0x82000000 |
| .pdata | 822B4000–822D166F | |
| .text | 822E0000–82B4ADFF | VA = file + 0x8200E800 |
| PSFD00 | 82B4AE00–82B50943 | |
| .data | 82B60000–835A18B7 | VA = file + 0x8201DE00 |
| .idata | 835B0000–835B05FF | |

(the per-section raw->virtual deltas were derived from the PE's
own section table this lane; they agree with phases 11–16's
three known mappings.) Evidence: `phase17/data/ghidra-acceptance.txt`
(imageBase=82000000, block map as above).

Function map: auto-analysis alone discovers almost nothing
here (the XEX entry flow does not seed the command-system
functions). The PE's `.pdata` section is an exact function
table — 8-byte entries, u32 BE begin VA (absolute) + packed
word with the instruction count at bits 8..27 — parsed by
`phase17/tools/pdata_parse_p17.py`: **15,054 functions, begins
strictly increasing, every phase-16 proven VA inside exactly
one entry** (open helper 0x8238ED10 ∈ 8238EA20–8238ED38;
initializer 0x82406E48 ∈ 824069D0–82406F5C; validator 0x824091F0
∈ 82408930–82409434; token decode 0x823F6D2C ∈ 823F6CE8–823F6EC4;
translator 0x823F6FA0 ∈ 823F6EC8–823F701C; loader cluster
0x823918E8 ∈ 823912B0–82391BBC; registry helper 0x8238AC90 ∈
8238A808–8238B374; classifier 0x82408290 ∈ 82408108–824085DC —
the same body as the initializer's 0x82408170 call target, i.e.
0x82408170 is an interior entry of the classifier function;
dispatcher 0x824F388C ∈ 824F3880–824F39CC).
`SeedFunctionsP17.java` created 14,687 further functions from
that table (23,832 total in the saved project;
`phase17/data/ghidra-seed-report.txt`).

## §3 Acceptance checks (task-named)

1. **Registry string block resolves xrefs — PASS.**
   `D:\bin\zack.bin` @ 0x82278660 carries a DATA xref from
   0x82C6B38C (the .bin registry table); `D:\bin\janlee.mot` @
   0x82284860 carries a DATA xref from 0x82C69A88 — the .mot
   registry record 0's +0x18 field itself. Ghidra's memory reads
   the first 8 registry records' name pointers back to their
   strings (janlee/ninja/gokei/t_fa_ay/t_kl_gy/t_ks_kt/t_sa_fa/
   t_bo_su .mot) — `phase17/data/ghidra-acceptance.txt`.
2. **Registry table @ 0x82C69A70 xref'd by the proven loader
   code — PASS (instruction level, Capstone-verified; Ghidra's
   reference manager records no ref TO the table base because
   the address is computed, not loaded as a literal — and the
   value 0x82C69A70 appears nowhere as a stored u32 either).**
   In the loader cluster: at 0x82391AD4 `bl 0x8238AC90` returns
   the runtime index in r3; 0x82391ADC `mulli r7, r3, 0x6C`
   (registry stride); r11 was loaded with 0x82C69A88
   (lis -0x7D39 / addi -0x6578 = 0x82C69A88 = registry + 0x18);
   0x82391AFC `add r7, r7, r11` => r7 = &registry[idx].name,
   passed to the open helper 0x8238ED10 at 0x82391B04 with entry
   id 0x1DD. The loader resolves .mot records exactly as
   phase 15/16 stated, now pinned to instructions.
3. **Target functions decompile readably at correct VAs —
   PASS for the token path; PARTIAL for the loader cluster.**
   Decompiles banked in `phase17/data/decompile/` (12 files).
   The token decode FUN_823F6CE8 decompiles to readable C that
   independently confirms phase 16's field-level read: two
   players, record pointers `DAT_83099E04` / `DAT_83099BA8`,
   u16s at +0x00/+0x02, bit-0 / bits 0xC00 -> classes 1/2/3/5,
   xor-compare of the two u16s' bitfields, and a per-player
   byte array stepped by 0x9C from &DAT_830201A9. The loader
   cluster FUN_823912B0 and the registry-helper body resist
   clean decompilation (Ghidra flags bad instruction data at
   their entries — the .pdata ranges there span several
   sub-functions); their evidence in this phase is the Capstone
   disassembly, which is byte-exact.

## §4 The artifact

The build is reproducible end-to-end from
`phase17/tools/build_ghidra_project_p17.sh` (forced PeLoader +
PowerPC:BE:32:default, `-Xmx1024M` via JAVA_TOOL_OPTIONS,
SetBase pre-script, Export post-script; the seed pass is a
second headless invocation with `SeedFunctionsP17.java` and the
CSV from `pdata_parse_p17.py`). The built project DB (78 MB)
is stored as a GitHub release asset (see PHASE17-STATE.md for
the release tag + sha256) per the one-store rule; the local
copy is cleared at lane end, logged.
