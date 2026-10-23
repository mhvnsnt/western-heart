#!/usr/bin/env bash
# tools/accelerators/extract/extract.sh — STAGE 1: EXTRACTION.
#
# Batch-extract Unreal Engine game assets (meshes, animations, textures)
# from .pak files into working formats (PSK/PSA + PNG/TGA, FBX/GLB via Blender).
#
# Tools — ALL fetched on demand into ./bin, NEVER vendored in the repo:
#   repak          UE pak unpacker (Rust, Linux-native single binary)
#   umodel         Gildor's UE Viewer CLI: batch export to PSK/PSA + textures.
#                  Native Linux build has no GUI — it is CLI-only, perfect here.
#                  (Gildor asks that download links not be reposted: the script
#                  does NOT hardcode his download URL. Bring your own binary or
#                  point UMODEL_BIN at it. The Windows umodel.exe from his
#                  GitHub repo is fetched as a Wine fallback.)
#   cue4parse-tool bundled C# console app (list pak contents, export textures
#                  to PNG) — built on demand with the dotnet SDK (also fetched).
#
# > ALL AGENTS — READ THIS FIRST. See ../depot-pull/DISK-RULES.md:
# > never download a full game; df-check first; extract, convert, DELETE the
# > downloads. Paks are a means, not an end.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"
REPAK="$BIN_DIR/repak"
UMODEL_EXE="$BIN_DIR/umodel.exe"          # windows build, runs under wine
CUE4P_DIR="$BIN_DIR/cue4parse-tool"
CUE4P_TOOL="$CUE4P_DIR/publish/CUE4ParseTool"

REPAK_VER="v0.2.3"
REPAK_URL="https://github.com/trumank/repak/releases/download/${REPAK_VER}/repak_cli-x86_64-unknown-linux-gnu.tar.xz"
REPAK_SHA_URL="${REPAK_URL}.sha256"
# Gildor's own repo (his FAQ points here for executables); runs under wine.
UMODEL_EXE_URL="https://raw.githubusercontent.com/gildor2/UEViewer/master/umodel.exe"
CUE4PARSE_VER="1.2.2.202610"              # FabianFG/CUE4Parse release tag

disk_check() { # disk_check <dir>
  echo "==> disk check:"; df -h "$1" 2>/dev/null | tail -1 || df -h . | tail -1
}

find_umodel() {
  # Prefer a native Linux umodel (CLI-only, no GUI) if the user provided one.
  for c in "${UMODEL_BIN:-}" "$BIN_DIR/umodel" "$(command -v umodel || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return 0; }
  done
  if [ -f "$UMODEL_EXE" ] && command -v wine >/dev/null 2>&1; then
    echo "wine $UMODEL_EXE"; return 0
  fi
  return 1
}

cmd_install() { # install [--umodel] [--cue4parse]
  mkdir -p "$BIN_DIR"
  local with_umodel=0 with_cue4p=0
  for a in "$@"; do
    case "$a" in
      --umodel) with_umodel=1 ;;
      --cue4parse) with_cue4p=1 ;;
      *) echo "unknown flag: $a"; exit 1 ;;
    esac
  done

  if [ -x "$REPAK" ]; then echo "repak already at $REPAK";
  else
    echo "Fetching repak ${REPAK_VER} (linux-x64)..."
    local fname="repak_cli-x86_64-unknown-linux-gnu.tar.xz"
    curl -fL --max-time 120 -o "/tmp/$fname" "$REPAK_URL"
    curl -fsL --max-time 60 -o "/tmp/$fname.sha256" "$REPAK_SHA_URL" || true
    if [ -f "/tmp/$fname.sha256" ]; then
      ( cd /tmp && sha256sum -c "$fname.sha256" ) || { echo "SHA MISMATCH on repak download"; exit 1; }
    fi
    tar -xJ --strip-components=1 -C "$BIN_DIR" -f "/tmp/$fname"
    chmod +x "$REPAK"; rm -f "/tmp/$fname" "/tmp/$fname.sha256"
    echo "Installed: $REPAK"
  fi

  if [ "$with_umodel" = 1 ]; then
    if find_umodel >/dev/null 2>&1; then echo "umodel already available: $(find_umodel)";
    else
      echo "Fetching umodel.exe (Windows build, runs under wine) from Gildor's repo..."
      curl -fL --max-time 120 -o "$UMODEL_EXE" "$UMODEL_EXE_URL"
      echo "Installed: $UMODEL_EXE"
      echo "NOTE: for the native Linux CLI build (no GUI, CLI-only), download it"
      echo "from https://www.gildor.org/projects/umodel and set UMODEL_BIN=<path>."
      echo "(Gildor asks that direct download links not be reposted — hence no hardcoded URL.)"
      command -v wine >/dev/null 2>&1 || echo "WARNING: wine not found — install wine to run umodel.exe, or use the Linux build."
    fi
  fi

  if [ "$with_cue4p" = 1 ]; then cmd_cue4parse_build; fi
  echo "stage-1 tools ready under $BIN_DIR"
}

dotnet_sdk() {
  # Fetch the .NET SDK on demand (needed to build the CUE4Parse tool).
  # Channel 10.0: current CUE4Parse releases target net10.0 only.
  local sdk_dir="$BIN_DIR/dotnet-sdk"
  if [ -x "$sdk_dir/dotnet" ]; then echo "$sdk_dir/dotnet"; return 0; fi
  local channel="10.0"
  echo "Resolving latest .NET $channel SDK..." >&2
  local ver
  ver=$(curl -fsL --max-time 60 "https://builds.dotnet.microsoft.com/dotnet/release-metadata/${channel}/releases.json" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['latest-sdk'])")
  echo "Fetching dotnet SDK $ver (~220MB, one-time; streamed, no temp file)..." >&2
  mkdir -p "$sdk_dir"
  # NOTE: streamed straight into tar — /tmp is a 512M tmpfs on this VM,
  # too small to stage the tarball. (DISK-RULES: keep 10GB free; the SDK
  # lives under ./bin and is reused, not re-downloaded.)
  curl -fL --max-time 900 \
    "https://builds.dotnet.microsoft.com/dotnet/Sdk/${ver}/dotnet-sdk-${ver}-linux-x64.tar.gz" \
    | tar -xz -C "$sdk_dir" \
    || { echo "dotnet SDK download/extract FAILED"; return 1; }
  [ -x "$sdk_dir/dotnet" ] || { echo "dotnet SDK install incomplete"; return 1; }
  echo "$sdk_dir/dotnet"
}

cmd_cue4parse_build() {
  mkdir -p "$CUE4P_DIR"
  if [ -x "$CUE4P_TOOL" ]; then echo "cue4parse-tool already at $CUE4P_TOOL"; return 0; fi
  local dotnet; dotnet=$(command -v dotnet || dotnet_sdk)
  echo "Building CUE4ParseTool (CUE4Parse $CUE4PARSE_VER)..."
  ( cd "$SCRIPT_DIR/cue4parse-tool" && \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 "$dotnet" publish \
      -c Release -r linux-x64 --self-contained true \
      -p:PublishSingleFile=true -p:CUE4ParseVersion="$CUE4PARSE_VER" \
      -o "$CUE4P_DIR/publish" )
  echo "Installed: $CUE4P_TOOL"
}

cmd_unpack() { # unpack <pak> <outdir> [--aes KEY]
  local pak=$1 out=$2; shift 2
  local aes=""
  while [ $# -gt 0 ]; do case "$1" in --aes) aes=$2; shift 2;; *) echo "unknown: $1"; exit 1;; esac; done
  [ -x "$REPAK" ] || { echo "run: $0 install"; exit 1; }
  [ -f "$pak" ] || { echo "pak not found: $pak"; exit 1; }
  disk_check "$out"; mkdir -p "$out"
  if [ -n "$aes" ]; then "$REPAK" unpack --aes-key "$aes" "$pak" --output "$out";
  else "$REPAK" unpack "$pak" --output "$out"; fi
  echo "==> unpacked -> $out"
  echo "REMINDER (DISK-RULES): convert what you need, then DELETE the extracted bulk."
}

cmd_unpack_dir() { # unpack-dir <pakdir> <outdir> [--aes KEY]
  local pakdir=$1 out=$2; shift 2
  [ -x "$REPAK" ] || { echo "run: $0 install"; exit 1; }
  disk_check "$out"; mkdir -p "$out"
  local n=0 fail=0
  for pak in "$pakdir"/*.pak; do
    [ -e "$pak" ] || { echo "no .pak files in $pakdir"; exit 1; }
    n=$((n+1))
    echo "--- [$n] $(basename "$pak")"
    if "$0" unpack "$pak" "$out/$(basename "$pak" .pak)" "$@"; then :; else fail=$((fail+1)); fi
  done
  echo "==> unpacked $n paks, $fail failures -> $out"
}

cmd_umodel_export() { # umodel-export <game_dir> <outdir> --ue <tag> [--pkg glob] [--extra "flags"]
  local gamedir=$1 out=$2; shift 2
  local ue="" pkg="*.uasset" extra=""
  while [ $# -gt 0 ]; do case "$1" in
    --ue) ue=$2; shift 2;; --pkg) pkg=$2; shift 2;; --extra) extra=$2; shift 2;;
    *) echo "unknown: $1"; exit 1;; esac; done
  [ -n "$ue" ] || { echo "--ue <tag> required (see ue-versions.txt; umodel -taglist)"; exit 1; }
  local umodel; umodel=$(find_umodel) || {
    echo "no umodel found. Run: $0 install --umodel"; echo "or set UMODEL_BIN=/path/to/umodel (Linux CLI build from https://www.gildor.org/projects/umodel)"; exit 1; }
  disk_check "$out"; mkdir -p "$out"
  # shellcheck disable=SC2086
  $umodel -path="$gamedir" -game="$ue" -export -out="$out" $extra "$pkg"
  echo "==> umodel export -> $out"
}

cmd_cue4parse() { # cue4parse <list|export-tex> <pak...> --ue <v> [--aes KEY] [--filter GLOB] [--out DIR]
  [ -x "$CUE4P_TOOL" ] || cmd_cue4parse_build
  "$CUE4P_TOOL" "$@"
}

usage() {
  cat <<EOF
usage: $0 <command> [args]

  install [--umodel] [--cue4parse]   fetch tools on demand into ./bin (never vendored)
  unpack <pak> <outdir> [--aes KEY]  unpack one .pak via repak
  unpack-dir <pakdir> <outdir> [--aes KEY]
                                     unpack every .pak in a directory
  umodel-export <game_dir> <outdir> --ue <tag> [--pkg GLOB] [--extra "flags"]
                                     batch-export meshes/anims/textures via UModel CLI
                                     (PSK/PSA + TGA/DDS; see ue-versions.txt)
  cue4parse <list|export-tex> ...    scripted UE asset reads via CUE4Parse
                                     (run without args for its own help)

READ ../depot-pull/DISK-RULES.md BEFORE pulling anything.
EOF
}

case "${1:-}" in
  install) shift; cmd_install "$@" ;;
  unpack) shift; cmd_unpack "$@" ;;
  unpack-dir) shift; cmd_unpack_dir "$@" ;;
  umodel-export) shift; cmd_umodel_export "$@" ;;
  cue4parse) shift; cmd_cue4parse "$@" ;;
  *) usage; exit 1 ;;
esac
