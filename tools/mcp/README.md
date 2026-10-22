# tools/mcp/ — MCP servers wired into the teardown pipeline

Model Context Protocol servers that let AI agents drive the teardown tools
directly. Evaluated 2026-10-22 (see `docs/research/TEARDOWN-TOOLING-EVAL-2026-10-22.md`).
Owner directive: *"use Ghidra, MCP servers, and any open-source tooling that helps…
wire the useful ones into the pipeline permanently."*

## Server registry

| Server | Version | What it drives | Pipeline use | Status |
|---|---|---|---|---|
| **GhidraMCP** (LaurieWired/GhidraMCP, Apache-2.0) | 2.0.0 — latest release (2026-10-10), matches vendored | Ghidra: decompile, list/rename functions, imports/exports | RE bench agent sessions (`tools/re/mcp/`) | ✅ wired; needs Ghidra 12.1.4 + JDK 21 (see `tools/re/`) |
| **mcp-for-blender** (ahujasid, MIT) | pip `mcp-for-blender` 2.2.2 (server reports 1.30.0) | Blender 3.0+: scene/objects, `execute_blender_code`, viewport `look`, asset search, export | Rig/anim/model lanes: agents drive Blender directly instead of generated scripts | ✅ MCP protocol verified (see below); ⚠️ Blender addon needs a display (xvfb+EGL), not this VM |

## mcp-for-blender — test results (2026-10-22, this VM)

- `pip install mcp-for-blender` → venv install clean (system pip blocked by PEP 668 —
  use a venv; the toolchain script does this).
- Addon installs + enables on Blender 4.0.2 headless: ✅ (`addon_install` → `addon_enable` OK).
- MCP stdio handshake: ✅ server `MCP for Blender 1.30.0`, `tools/list` returns 9 tools
  (`get_scene_info`, `execute_blender_code`, `look`, `get_addon_status`, `search_assets`,
  `generate_3d`, …). Without a Blender connected, tool calls fail gracefully:
  `Could not connect to Blender. Make sure the Blender addon is running.`
- **Blocked:** the addon's socket server refuses `blender --background`
  ("commands would never execute — run Blender with a GUI, or xvfb-run"), and the
  GUI path aborts on this VM (no `libEGL.so.1`). So: MCP server runs anywhere;
  the Blender side needs a display machine (the lanes' GPU workstation).
- Telemetry: server sends anonymous usage records by default — set
  `DISABLE_TELEMETRY=true` (done in the smoke test + toolchain script).

## Files

- `smoke_mcp_server.py` — stdio MCP smoke test: `initialize` → `tools/list` →
  one graceful-failure call. Stdlib only; needs `mcp-for-blender` installed
  (the venv `tools/setup/setup_toolchain.sh` creates). Run in CI to prove the
  server package still loads: `python3 tools/mcp/smoke_mcp_server.py`.
- MCP client config for agents: point the client at
  `<venv>/bin/python -m blender_mcp.server` (stdio), env `DISABLE_TELEMETRY=true`.

## Setup (display machine)

```bash
bash tools/setup/setup_toolchain.sh            # installs Blender 4.0.2 + mcp venv
<venv>/bin/python -m blender_mcp.server install-addon   # or via Blender: install addon.py
# Blender side: enable the addon, press "Connect to Claude" (port 9876)
# MCP client: {"command": "<venv>/bin/python", "args": ["-m", "blender_mcp.server"]}
```

## Not wired (evaluated, rejected)

- Blender Lab official MCP (Blender 5.1+ required; we pin Blender 4.0.2 — revisit on upgrade).
- RFingAdam/mcp-blender, PoBruno/mcp-blender-agent (218/216 tools — broader but
  untested here; mcp-for-blender's 29k stars + protocol verification won).
- Radare2/rizin MCP servers (no maintained project found 2026-10-22; GhidraMCP covers RE).
