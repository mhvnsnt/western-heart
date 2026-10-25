#!/bin/bash
# fetch-ghidra.sh — download Ghidra 12.1.4 + Temurin JDK 21, verify SHA-256, unpack.
# Ghidra is ~1.3GB unpacked: it is NEVER committed to git. This script is the install.
# Usage: ./fetch-ghidra.sh [dest-dir]   (default: ./vendor)
set -euo pipefail

VERSION="$(cat "$(dirname "$0")/GHIDRA-VERSION" | tr -d '[:space:]')"
DEST="${1:-$(dirname "$0")/vendor}"
GHIDRA_ZIP="ghidra_${VERSION}_PUBLIC_20260921.zip"
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${VERSION}_build/${GHIDRA_ZIP}"
# Pinned SHA-256 — re-verify at https://github.com/NationalSecurityAgency/ghidra/releases
GHIDRA_SHA256="REPLACE_WITH_PUBLISHED_SHA256"

JDK_URL="https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz"
JDK_DIR="jdk-21.0.12.1+1"

mkdir -p "$DEST"
cd "$DEST"

if [ ! -f "$GHIDRA_ZIP" ]; then
  echo "==> downloading Ghidra $VERSION (~450MB zip)..."
  curl -sSL --retry 3 -o "$GHIDRA_ZIP" "$GHIDRA_URL"
else
  echo "==> Ghidra zip already present, skipping download"
fi

if [ "$GHIDRA_SHA256" != "REPLACE_WITH_PUBLISHED_SHA256" ]; then
  echo "==> verifying SHA-256..."
  echo "${GHIDRA_SHA256}  ${GHIDRA_ZIP}" | sha256sum -c -
else
  echo "!! WARNING: SHA-256 pin not set — fill GHIDRA_SHA256 from the release page before trusting this artifact"
fi

if [ ! -d "ghidra_${VERSION}_PUBLIC" ]; then
  echo "==> unpacking..."
  unzip -q "$GHIDRA_ZIP"
fi

if [ ! -d "$JDK_DIR" ]; then
  echo "==> downloading Temurin JDK 21 (~190MB)..."
  curl -sSL --retry 3 -o jdk21.tar.gz "$JDK_URL"
  tar xzf jdk21.tar.gz
  rm jdk21.tar.gz
fi

echo "==> installing GhidraMCP extension (if present in mcp/)..."
if [ -f "../mcp/ghidra-mcp-plugin.zip" ]; then
  mkdir -p /tmp/gmcp-install && cd /tmp/gmcp-install
  unzip -q -o "$OLDPWD/../mcp/ghidra-mcp-plugin.zip"
  INNER="$(find . -name 'ghidra_*_GhidraMCP.zip' | head -1)"
  if [ -n "$INNER" ]; then
    unzip -q -o "$INNER" -d ext
    cp -r ext/* "$OLDPWD/ghidra_${VERSION}_PUBLIC/Ghidra/Extensions/"
    echo "    GhidraMCP extension installed"
  fi
  cd "$OLDPWD"
fi

echo "==> done. Run: source ../env.sh"
echo "    GHIDRA_HOME=$DEST/ghidra_${VERSION}_PUBLIC"
