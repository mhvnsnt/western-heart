#!/usr/bin/env bash
# tools/setup/setup_re_toolchain.sh — install the reverse-engineering toolchain.
# Complements tools/setup/setup_toolchain.sh (which covers Blender, gltf, T3R, MCP).
#
#   bash tools/setup/setup_re_toolchain.sh [PREFIX]      # default PREFIX=$HOME/workspace/tools
#
# Installs:
#   Ghidra 12.1.4 (Apache 2.0)      -> $PREFIX/ghidra/ghidra_12.1.4_PUBLIC/
#   Eclipse Temurin JDK 21           -> $PREFIX/ghidra/jdk-21.0.12.1+1/  (Ghidra's runtime)
#   ghidra-mcp 2.0.0 (MIT)           -> $PREFIX/ghidra-mcp/  (MCP bridge for Ghidra)
#   DepotDownloader (latest)         -> $PREFIX/depotdownloader/DepotDownloader  (Steam depot pulls)
#   aider (Apache 2.0)               -> $PREFIX/aider-venv/  (AI pair programming)
#   unrar (free)                     -> $PREFIX/unrar/unrar
#   TKMovesets @ main               -> $PREFIX/t7-pipeline/TKMovesets
#   TekkenMovesetExtractor @ main   -> $PREFIX/t7-pipeline/TekkenMovesetExtractor
#   BlenderTekkenAnimationImporter   -> $PREFIX/t7-pipeline/BlenderTekkenAnimationImporter
#
# Everything is free/open-source and pinned where it matters.
# If the VM dies, run this script to rebuild. Nothing in $PREFIX is irreplaceable.
set -euo pipefail
PREFIX="${1:-$HOME/workspace/tools}"

GHIDRA_VER="12.1.4"
GHIDRA_DATE="20260921"
JDK_VER="21.0.12.1+1"
JDK_BUILD="21.0.12.1_1"

mkdir -p "$PREFIX/ghidra" "$PREFIX/ghidra-mcp" "$PREFIX/depotdownloader" "$PREFIX/t7-pipeline" "$PREFIX/unrar"

# --- Ghidra ---
if [ ! -x "$PREFIX/ghidra/ghidra_${GHIDRA_VER}_PUBLIC/ghidraRun" ]; then
  echo "==> Ghidra $GHIDRA_VER"
  curl -fL "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VER}_build/ghidra_${GHIDRA_VER}_PUBLIC_${GHIDRA_DATE}.zip" \
    -o "$PREFIX/ghidra/ghidra.zip"
  ( cd "$PREFIX/ghidra" && unzip -q -o ghidra.zip )
  rm -f "$PREFIX/ghidra/ghidra.zip"
fi

# --- Eclipse Temurin JDK 21 (Ghidra runtime) ---
if [ ! -x "$PREFIX/ghidra/jdk-${JDK_VER}/bin/java" ]; then
  echo "==> Temurin JDK 21"
  curl -fL "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-${JDK_VER}%2B1/OpenJDK21U-jdk_x64_linux_hotspot_${JDK_BUILD}.tar.gz" \
    | tar -xz -C "$PREFIX/ghidra"
fi

# --- ghidra-mcp (MCP bridge) ---
if [ ! -d "$PREFIX/ghidra-mcp/GhidraMCP-release-2-0" ]; then
  echo "==> ghidra-mcp 2.0.0"
  curl -fL "https://github.com/bugsbugsbux/ghidra-mcp/releases/download/v2.0.0/ghidra-mcp-plugin.zip" \
    -o "$PREFIX/ghidra-mcp/ghidra-mcp-plugin.zip"
  ( cd "$PREFIX/ghidra-mcp" && unzip -q -o ghidra-mcp-plugin.zip )
  rm -f "$PREFIX/ghidra-mcp/ghidra-mcp-plugin.zip"
  python3 -m venv "$PREFIX/ghidra-mcp/venv"
  "$PREFIX/ghidra-mcp/venv/bin/pip" install --quiet "ghidra-mcp==2.0.0"
fi

# --- DepotDownloader ---
if [ ! -x "$PREFIX/depotdownloader/DepotDownloader" ]; then
  echo "==> DepotDownloader"
  DD_URL=$(curl -sL --max-time 60 https://api.github.com/repos/SteamRE/DepotDownloader/releases/latest \
    | python3 -c "import json,sys; print([a['browser_download_url'] for a in json.load(sys.stdin)['assets'] if 'linux-x64' in a['name']][0])")
  curl -fL -o /tmp/dd.zip "$DD_URL"
  mkdir -p "$PREFIX/depotdownloader"
  python3 -c "import zipfile; zipfile.ZipFile('/tmp/dd.zip').extractall('$PREFIX/depotdownloader')"
  chmod +x "$PREFIX/depotdownloader/DepotDownloader"
  rm -f /tmp/dd.zip
fi

# --- aider ---
if [ ! -x "$PREFIX/aider-venv/bin/aider" ]; then
  echo "==> aider"
  python3 -m venv "$PREFIX/aider-venv"
  "$PREFIX/aider-venv/bin/pip" install --quiet aider-chat
fi

# --- unrar ---
if [ ! -x "$PREFIX/unrar/unrar" ]; then
  echo "==> unrar"
  curl -fL "https://www.rarlab.com/rar/rarlinux-x64-712.tar.gz" | tar -xz -C /tmp
  cp /tmp/rar/unrar "$PREFIX/unrar/"
  rm -rf /tmp/rar
fi

# --- T7 pipeline tools (Kiloutre) ---
for repo in TKMovesets TekkenMovesetExtractor BlenderTekkenAnimationImporter; do
  if [ ! -d "$PREFIX/t7-pipeline/$repo/.git" ]; then
    echo "==> $repo"
    git clone --depth 1 "https://github.com/Kiloutre/$repo.git" "$PREFIX/t7-pipeline/$repo"
  fi
done


# --- T8 extraction tools ---
if [ ! -x "$PREFIX/t8extract/repak" ]; then
  echo "==> repak"
  mkdir -p "$PREFIX/t8extract"
  REPAK_VER="0.9.0"
  curl -fL "https://github.com/trumank/repak/releases/download/v${REPAK_VER}/repak_cli-x86_64-unknown-linux-gnu.tar.gz" \
    | tar -xz -C "$PREFIX/t8extract"
fi
# CUE4ParseTool: build from source (https://github.com/wmltogether/CUE4ParseTool)
# Or download release if available. Pinned to working version.

cat <<EOF
RE toolchain ready under $PREFIX
  Ghidra:  $PREFIX/ghidra/ghidra_${GHIDRA_VER}_PUBLIC/ghidraRun
  JDK:     $PREFIX/ghidra/jdk-${JDK_VER}/bin/java
  MCP:     $PREFIX/ghidra-mcp/venv/bin/python -m ghidra_mcp
  DepotDL: $PREFIX/depotdownloader/DepotDownloader
  aider:   $PREFIX/aider-venv/bin/aider
EOF
