#!/usr/bin/env bash
# depot-pull.sh — partial Steam depot downloads via DepotDownloader.
# NEVER use this to download a full game. See DISK-RULES.md first.
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")" && pwd)/bin"
DD="$BIN_DIR/DepotDownloader"

cmd_install() {
  mkdir -p "$BIN_DIR"
  if [ -x "$DD" ]; then echo "DepotDownloader already at $DD"; return 0; fi
  echo "Fetching latest DepotDownloader (linux-x64 standalone)..."
  local url
  url=$(curl -sL --max-time 60 https://api.github.com/repos/SteamRE/DepotDownloader/releases/latest \
    | python3 -c "import json,sys; print([a['browser_download_url'] for a in json.load(sys.stdin)['assets'] if 'linux-x64' in a['name']][0])")
  curl -sL --max-time 120 -o /tmp/dd.zip "$url"
  python3 -c "import zipfile; zipfile.ZipFile('/tmp/dd.zip').extractall('$BIN_DIR')"
  chmod +x "$DD"
  rm -f /tmp/dd.zip
  echo "Installed: $DD"
}

cmd_list() { # list <app> <depot>
  [ -x "$DD" ] || { echo "run: $0 install"; exit 1; }
  "$DD" -app "$1" -depot "$2" -manifest-only
}

cmd_get() { # get <app> <depot> <filelist> <outdir> <steam_username>
  [ -x "$DD" ] || { echo "run: $0 install"; exit 1; }
  local app=$1 depot=$2 list=$3 out=$4 user=$5
  echo "==> disk check:"; df -h "$out" 2>/dev/null | tail -1 || df -h . | tail -1
  mkdir -p "$out"
  "$DD" -app "$app" -depot "$depot" -filelist "$list" -dir "$out" -username "$user"
  echo "==> done. EXTRACT WHAT YOU NEED, THEN DELETE THE DOWNLOADS. See DISK-RULES.md."
}

case "${1:-}" in
  install) cmd_install ;;
  list)    cmd_list "$2" "$3" ;;
  get)     cmd_get "$2" "$3" "$4" "$5" "$6" ;;
  *) echo "usage: $0 install | list <app> <depot> | get <app> <depot> <filelist> <outdir> <steam_user>"; exit 1 ;;
esac
