#!/usr/bin/env bash
# tools/setup/setup_toolchain.sh — install the exact external toolchain the 2026-10-20/21
# Claude session used (see tools/TOOLS-INDEX.md). Everything is free / open source and pinned.
#
#   bash tools/setup/setup_toolchain.sh [PREFIX]      # default PREFIX=$HOME/workspace/tools
#
# Installs:
#   Blender 4.0.2 (GPL)            -> $PREFIX/blender/blender-4.0.2-linux-x64/blender
#                                     (path tools/auto_rig/auto_rig.py expects; GameRig is vendored
#                                      in tools/auto_rig/vendor and installed by the backend itself)
#   gitleaks 8.21.2 (MIT)          -> $PREFIX/bin/gitleaks          (run before every push)
#   @gltf-transform 4.1.1 + meshoptimizer 0.22.0 (MIT)
#                                  -> $PREFIX/gltf/node_modules      (tools/anim/gltf_codec.mjs:
#                                      NODE_PATH=$PREFIX/gltf/node_modules)
#   n0madic/Tekken3Remake @ e59c4da1 (PolyForm Noncommercial; T3 RE tools: fight_sim.py,
#                                      pose.py, motion.py used by the T3 decoders)
#                                  -> $PREFIX/t3r          (export T3REMAKE_RESEARCH=$PREFIX/t3r/tools/research)
#   python: numpy scipy pygltflib
# Playwright + Chromium are pre-installed in the cloud container (/opt/pw-browsers); elsewhere:
#   npm i -g playwright@1.56 && npx playwright install chromium
set -euo pipefail
PREFIX="${1:-$HOME/workspace/tools}"
mkdir -p "$PREFIX/bin" "$PREFIX/blender" "$PREFIX/gltf"

if [ ! -x "$PREFIX/blender/blender-4.0.2-linux-x64/blender" ]; then
  curl -fL https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz \
    | tar -xJ -C "$PREFIX/blender"
fi

if [ ! -x "$PREFIX/bin/gitleaks" ]; then
  curl -fL https://github.com/gitleaks/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz \
    | tar -xz -C "$PREFIX/bin" gitleaks
fi

( cd "$PREFIX/gltf" && [ -f package.json ] || npm init -y >/dev/null
  npm i --no-audit --no-fund @gltf-transform/core@4.1.1 @gltf-transform/extensions@4.1.1 \
        @gltf-transform/functions@4.1.1 meshoptimizer@0.22.0 )

if [ ! -d "$PREFIX/t3r/.git" ]; then
  git clone https://github.com/n0madic/Tekken3Remake "$PREFIX/t3r"
  git -C "$PREFIX/t3r" checkout e59c4da179f39b4e915ccdc547567c8479a9f611
fi

python3 -m pip install --quiet numpy scipy pygltflib

# mcp-for-blender (MIT) — MCP server letting agents drive Blender directly.
# Venv because system pip is PEP 668 externally-managed on some VMs.
# The Blender *addon* side needs a display (xvfb+EGL); the MCP server runs anywhere.
# Smoke test (no Blender needed): $PREFIX/mcp-venv/bin/python tools/mcp/smoke_mcp_server.py
if [ ! -x "$PREFIX/mcp-venv/bin/python" ]; then
  python3 -m venv "$PREFIX/mcp-venv"
  DISABLE_TELEMETRY=true "$PREFIX/mcp-venv/bin/pip" install --quiet "mcp-for-blender==2.2.2"
fi

cat <<EOF
toolchain ready under $PREFIX
  export T3REMAKE_RESEARCH=$PREFIX/t3r/tools/research
  export NODE_PATH=$PREFIX/gltf/node_modules
  export PATH=$PREFIX/bin:\$PATH
  export MCP_BLENDER_PY=$PREFIX/mcp-venv/bin/python   # python -m blender_mcp.server (stdio)
  export DISABLE_TELEMETRY=true
EOF
