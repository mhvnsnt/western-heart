# Teardown Tooling Evaluation — 2026-10-22

Owner directive: *"use Ghidra, MCP servers, and any open-source tooling that helps
(parsers, converters, retargeters). Wire the useful ones into the pipeline permanently."*

Method per tool: research → pull → **test on this VM** → wire in or document why not.
Prior pull-ins (2026-10-19: TKMovesets, Wiggle 2, Keemap, GameRig) are in
`tools/open-source/` and `docs/research/OPEN-SOURCE-PULL-INS-2026-10-19.md` — not re-evaluated here.

## 1. MCP servers

### ✅ WIRED — mcp-for-blender (ahujasid, MIT)
The community Blender MCP (29k stars, renamed 2026-09). **Tested on this VM:**
- `pip install mcp-for-blender` 2.2.2 → venv (system pip blocked by PEP 668; toolchain script uses a venv).
- Addon installs and enables on Blender 4.0.2 headless. ✅
- MCP stdio handshake: server `MCP for Blender 1.30.0`, `tools/list` → 9 tools
  (`get_scene_info`, `execute_blender_code`, `look`, `get_addon_status`, `search_assets`,
  `generate_3d`, `import_asset`, `disable_telemetry`, `record_trajectory_feedback`). ✅
- No-Blender call fails gracefully ("Could not connect to Blender…"), no crash. ✅
- **Limit:** the addon's socket server refuses `blender --background` and the GUI
  path aborts here (no `libEGL.so.1`). The Blender side needs a display machine
  (lanes' GPU workstation); the MCP server itself runs anywhere.
- Wired as: `tools/mcp/README.md` (registry) + `tools/mcp/smoke_mcp_server.py`
  (CI-runnable stdio smoke test, stdlib only) + venv install in
  `tools/setup/setup_toolchain.sh`. Telemetry off via `DISABLE_TELEMETRY=true`.

### ✅ WIRED (already) — GhidraMCP (LaurieWired, Apache-2.0)
Checked latest release via API: **2.0** (2026-10-10) — the vendored 2.0.0 in
`tools/re/mcp/` is current. No update needed. Needs Ghidra 12.1.4 + JDK 21
(`tools/re/fetch-ghidra.sh`).

### ❌ Not wired
- **Blender Lab official MCP** — requires Blender 5.1+; we pin 4.0.2. Revisit on upgrade.
- **RFingAdam/mcp-blender, PoBruno/mcp-blender-agent** — 200+ tools each, but untested
  here; mcp-for-blender's protocol verification won.
- **Rizin/radare2 MCP** — no maintained project found 2026-10-22; GhidraMCP covers RE.

## 2. Tekken-specific parsers / extractors

### ✅ WIRED — psp_elf_xref.py (new, `tools/re/scripts/`)
Promotes the T6 DATA401 watchdog's ad-hoc helpers (`/tmp/mips_re.py`, never committed)
into a permanent stage: ELF32-LE parse → vaddr map → `lui`+`addiu`/`ori` xref scan →
string watchlist → crypto-constant hunt (AES S-box, TEA delta, CRC32 table, XOR-0xA5
idiom) → `jr $ra` import-stub census → optional capstone disasm. Stdlib + optional capstone.
**Tested on the decrypted T6 EBOOT:** reproduces every watchdog finding exactly
(openPac/ktRead xrefs, 268 import stubs, XOR-0xA5 sites, key-extract masks) and adds
two new leads — `DINF_400.BIN`'s single code xref at 0x8899834, and a static CRC32
table at 0x8BB0FF8. Full report: `teardown/tekken6/T6-KEYHUNT-REPORT-2026-10-22.md`.
~5s runtime. This is the NO-HAND-TOOLING answer to "MIPS static helpers used ad-hoc".

### 📋 Documented (no code yet) — TTT2-PC static-recomp port
shihabal3amri/tekken-tag-tournament-2-pc (created 2026-10-12, XenonRecomp-based).
Its installer **builds game assets from the X360 disc + TU3** — i.e. a working,
documented TTT2 asset pipeline (PAC/PACH, BPE textures, XMA via FFmpeg, LZX via
libmspack). Changes the TTT2 unblock from "reverse STFS blind" to "read their
installer code". Full assessment: `teardown/tekken-tag-tournament-2/TTT2-PC-PORT-ASSESSMENT.md`.
Next: pull `tools/` + `re/recomp/` source-only into `tools/open-source/` (TTT2 lane).

### 📋 Documented — umodel / UE Viewer (gildor2, for Tekken 7 UE4)
The T7 modding standard: reads UE4 `.pak`/`.uasset`, exports skeletal meshes to
**.glTF 2.0** + PNG/DDS (CDDTreborn Tekken7_PC-Modding-Guides). Builds with gcc/make
(genmake), so a Linux build is feasible. **Not wired yet:** no T7 game data on any
VM to test against (51GB acquisition blocker stands). When the T7 lane acquires the
game, the lane is: build umodel → batch-export `Game/Character/.../SK_*.uasset` →
glTF → existing rig pipeline. FModel is the GUI alternative (Windows).

### 📋 Documented — Iso2God (Chilano, for TTT2/DOA4 STFS on X360)
Open-source C# STFS/GoD reader. Needs .NET (not on this VM) — recipe for a .NET
machine, or superseded by the TTT2-PC installer pipeline above for TTT2 specifically.
Still the fallback for DOA4's X360 ISO.

## 3. Converters / retargeters

- **glTF:** `@gltf-transform` 4.1.1 + `meshoptimizer` 0.22.0 already in the toolchain
  (`tools/anim/gltf_codec.mjs`, `tools/setup/setup_toolchain.sh`). No gap — umodel's
  glTF export plugs straight into this.
- **Retargeting:** Keemap already vendored + tested (`tools/open-source/`); runtime
  T3 retarget in `game/js/t3anims.js`. No new retargeter evaluated better on 2026-10-22.
- **Audio:** vgmstream-cli still unbuilt (`tools/re/cli/README.md` recipe stands);
  the TTT2-PC port's FFmpeg XMA path is now the documented alternative for TTT2 audio.

## 4. Ghidra on this VM

Not installed here (1.3GB + JDK 21; bench already documents it at `tools/re/` and it
was verified on the prior VM). `psp_elf_xref.py` deliberately covers the no-Ghidra
static pass so RE lanes aren't blocked where Ghidra isn't installed.

## Scoreboard

| Tool | Verdict | Wired as |
|---|---|---|
| mcp-for-blender | ✅ wire | `tools/mcp/` + toolchain venv + smoke test |
| GhidraMCP | ✅ current (2.0) | already in `tools/re/mcp/` |
| psp_elf_xref.py | ✅ wire | `tools/re/scripts/` + T6 report |
| TTT2-PC port knowledge | 📋 next lane step | `teardown/tekken-tag-tournament-2/TTT2-PC-PORT-ASSESSMENT.md` |
| umodel (T7) | 📋 when T7 acquired | documented above |
| Iso2God (STFS) | 📋 fallback / .NET machine | documented above |
| Blender Lab MCP, rizin MCP | ❌ | rejected with reason |
