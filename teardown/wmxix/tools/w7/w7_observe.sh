#!/bin/bash
# W7 observation runner: Dolphin + GDB stub + DTM + raw RSP logging client.
# Usage: w7_observe.sh <dtm> <seconds> <tag> [bps] [hits]
#   bps: comma-separated hex breakpoint addresses (default: 800364F0 only)
#   hits: max breakpoint hits to log (default 300)
set -x
DTM="$1"; SECS="${2:-600}"; TAG="${3:-obs1}"
BPS="${4:-800364F0}"; HITS="${5:-300}"
export DISPLAY=:99
# Kill leftovers and verify dead.
for i in 1 2 3; do
  pkill -x dolphin-emu 2>/dev/null; sleep 3
  pgrep -x dolphin-emu >/dev/null || break
  pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
done
pgrep -x dolphin-emu && { echo "DOLPHIN STILL ALIVE - ABORT"; exit 1; }
# Reset corruptible Dolphin user state (see w7_probe.sh).
U=~/.var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu
C=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu
rm -rf "$U/GC" "$U/Wii/shared2" "$U/Cache" "$C/Qt.ini" "$C/TimePlayed.ini"
# Dolphin.ini WITH the GDB port (the [General] GDBPort key is the only way
# to start the stub; the -C CLI override does not work).
printf '[Analytics]\nID = 3ef0eebbdbf7bd40ff182abcea4a4cc4\n[General]\nGDBPort = 9090\n' > "$C/Dolphin.ini"
printf '[Options]\nWriteToFile = True\nWriteToConsole = False\n[LogTypes]\nMOVIE = True\nCORE = True\nBOOT = True\n' > "$C/Logger.ini"
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
mkdir -p /data/wmxix/w7shots /data/wmxix/w7
rm -f /data/wmxix/w7shots/${TAG}_*.png /data/wmxix/w7/${TAG}_hits.jsonl
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  -m "$DTM" --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-${TAG}.log 2>&1 &
# Wait for the GDB stub to listen (boot blocks in accept() until we attach).
# Use ss (no connection): Dolphin's stub accepts exactly ONE client and then
# closes its listen socket, so a /dev/tcp probe would consume the only slot.
for i in $(seq 1 60); do
  ss -ltn 2>/dev/null | grep -q ':9090' && break
  sleep 2
done
ss -ltn 2>/dev/null | grep -q ':9090' && echo "GDB stub listening" || { echo "GDB STUB NOT LISTENING"; pkill -9 -x dolphin-emu; exit 1; }
# Screenshot loop (every 20s).
( i=0; while [ $i -lt $SECS ]; do
    xwd -root -silent | convert xwd:- /data/wmxix/w7shots/${TAG}_$(printf %03d $i).png 2>/dev/null
    sleep 20; i=$((i+20));
  done ) &
# RSP logging client (runs until hit cap or timeout).
timeout $SECS python3 /data/wmxix/w7_rsp.py --host 127.0.0.1 --port 9090 \
  --bps "$BPS" --hits "$HITS" --out /data/wmxix/w7/${TAG}_hits.jsonl \
  --timeout $SECS > /data/wmxix/w7/${TAG}_rsp.log 2>&1
echo "RSP client exit: $?"
pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
montage /data/wmxix/w7shots/${TAG}_*.png -tile 3x -geometry 426x240+2+2 /data/wmxix/w7shots/${TAG}_sheet.png 2>/dev/null
ls -la /data/wmxix/w7shots/${TAG}_sheet.png /data/wmxix/w7/${TAG}_hits.jsonl 2>/dev/null
wc -l /data/wmxix/w7/${TAG}_hits.jsonl 2>/dev/null
tail -5 /data/wmxix/w7/${TAG}_rsp.log
