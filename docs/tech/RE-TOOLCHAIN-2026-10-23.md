# RE Toolchain — 2026-10-23

Complete reverse-engineering toolchain for tearing down game files. Installed on the VM at `~/workspace/tools/`.

Owner directive: *"Use ghidra and mcp and a whatever else needed we have most in the repo and whatever else u can find anywhere else"*

## What's installed

### Ghidra 12.1.4 (NSA RE platform)
- **Path:** `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/`
- **Java:** Temurin JDK 21 at `~/workspace/tools/ghidra/jdk-21.0.12.1+1/`
- **Size:** ~1.8GB
- **Verified:** headless analysis works (`analyzeHeadless` launches and initializes)
- **Install method:** repo's `tools/re/fetch-ghidra.sh` (downloads from NSA GitHub releases)
- **Usage:**
  ```bash
  source ~/workspace/tools/ghidra/env.sh  # sets GHIDRA_HOME, JAVA_HOME
  $GHIDRA_HOME/support/analyzeHeadless /tmp/proj MyProj -import /path/to/binary
  ```

### GhidraMCP 2.0.0 (AI wire into Ghidra)
- **Extension:** installed at `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/Ghidra/Extensions/GhidraMCP/`
- **Python bridge:** `~/workspace/tools/ghidra-mcp/venv/` (venv with ghidra-mcp 2.0.0)
- **Size:** ~60MB
- **Usage:**
  ```bash
  ~/workspace/tools/ghidra-mcp/venv/bin/python -m ghidra_mcp --transport stdio
  ```
- **What it does:** exposes Ghidra to AI agents via MCP — decompile functions, list methods/imports/exports, rename symbols

### MCP for Blender 2.2.2
- **Path:** `~/workspace/tools/mcp-venv/` (venv)
- **Size:** ~58MB
- **Usage:**
  ```bash
  DISABLE_TELEMETRY=true ~/workspace/tools/mcp-venv/bin/python -m blender_mcp.server
  ```
- **What it does:** lets AI agents drive Blender directly (scene info, execute code, viewport, export)
- **Note:** the Blender addon side needs a display (not this VM); the MCP server runs anywhere

### UE Asset Tools (Tekken 8)
- **repak:** `~/workspace/tools/t8extract/repak` — UE .pak file tool (info, list, unpack)
- **CUE4ParseTool:** `~/workspace/tools/t8extract/CUE4ParseTool/` — UE4/UE5 asset parser
- **What for:** Tekken 8 uses Unreal Engine 4 — these extract models, textures, and data from .pak files

### Tekken 3 Tools
- **t3r:** `~/workspace/tools/t3r/` — Tekken3Remake RE tools (fight_sim.py, pose.py, motion.py)
- **tekken3remake:** `~/workspace/tools/tekken3remake/` — additional T3 tooling

### Binary Analysis
- **System tools:** `7z`, `7za`, `unrar`, `file`, `objdump`, `readelf`, `strings` (all at /usr/bin/)
- **capstone 5.0.7** (Python): disassembly library for scripted analysis
- **pygltflib** (Python): glTF file parsing
- **gitleaks 8.21.2:** `~/workspace/tools/bin/gitleaks` — secrets scanner (run before every push)

### 3D Tools
- **Blender:** 4.0.2, 4.2.0, 4.5.3 at `~/workspace/tools/blender/`
- **glTF tools:** `~/workspace/tools/gltf/` (Node.js: @gltf-transform 4.1.1, meshoptimizer 0.22.0)
- **DepotDownloader:** `~/workspace/tools/depotdownloader/` — Steam depot downloads

## Repo integration

The repo already has the RE bench at `tools/re/`:
- `fetch-ghidra.sh` — Ghidra + JDK installer (used for this setup)
- `env.sh` — environment setup script
- `analyze.sh` — headless analysis wrapper
- `scripts/` — PyGhidra analysis scripts
- `mcp/` — GhidraMCP plugin + client config
- `cli/README.md` — CLI decoder inventory
- `QUEUE.md` — game teardown queue

MCP servers are documented at `tools/mcp/README.md`.

## Disk usage

| Tool | Size |
|------|------|
| Ghidra + JDK | 1.8GB |
| GhidraMCP | 60MB |
| MCP Blender venv | 58MB |
| Blender (3 versions) | 3.6GB |
| Everything else | <500MB |

**Freed during setup:** ~1GB (deleted Blender .tar.xz files — extracted versions remain)

**Current disk:** 89% (12GB free)

## What's NOT installed (documented for later)

- **QuickBMS:** 64-bit build needed (32-bit segfaults). Compile from https://github.com/aluigi/quickbms on a better network.
- **binwalk v3:** needs Rust toolchain (cargo). Low priority for game ISOs.
- **vgmstream:** game audio (PS2 ADX/VAG). Build from source with cmake. Medium priority.
- **xdelta3:** binary diffing. Low priority.

## Quick start

```bash
# Ghidra headless analysis
export GHIDRA_HOME=~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC
export JAVA_HOME=~/workspace/tools/ghidra/jdk-21.0.12.1+1
export PATH="$JAVA_HOME/bin:$PATH"
$GHIDRA_HOME/support/analyzeHeadless /tmp/myproj MyGame -import /path/to/game.elf

# GhidraMCP server (for AI agent RE sessions)
~/workspace/tools/ghidra-mcp/venv/bin/python -m ghidra_mcp --transport stdio

# Blender MCP server
DISABLE_TELEMETRY=true ~/workspace/tools/mcp-venv/bin/python -m blender_mcp.server

# UE pak extraction (Tekken 8)
~/workspace/tools/t8extract/repak info /path/to/game.pak
```
