#!/bin/bash
# W7 probe runner: play a .dtm in Dolphin (NO gdb), screenshot every 8s,
# montage a contact sheet. Usage: w7_probe.sh <dtm> <seconds> <tag>
set -x
DTM="$1"; SECS="${2:-150}"; TAG="${3:-probe}"; SHOT_EVERY="${4:-8}"
export DISPLAY=:99
# Kill any leftover Dolphin and VERIFY it is dead before relaunching.
for i in 1 2 3; do
  pkill -x dolphin-emu 2>/dev/null; sleep 3
  pgrep -x dolphin-emu >/dev/null || break
  pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
done
pgrep -x dolphin-emu && { echo "DOLPHIN STILL ALIVE - ABORT"; exit 1; }
echo "dolphin confirmed dead"
# Reset corruptible Dolphin user state. A SIGKILLed Dolphin (our normal
# shutdown) can corrupt SYSCONF / the GCI save / Qt.ini; the next movie run
# then dies at boot with a GetDirectoryForRegion panic dialog (nav4/nav3b,
# 2026-11-19). Wiping these before each run fixes it; the game recreates
# its save. Backup of the pre-wipe state: /tmp/dolphin-user-backup-20261119.
U=~/.var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu
C=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu
rm -rf "$U/GC" "$U/Wii/shared2" "$U/Cache" "$C/Qt.ini" "$C/TimePlayed.ini"
CONF=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Dolphin.ini
printf '[Analytics]\nID = 3ef0eebbdbf7bd40ff182abcea4a4cc4\n' > "$CONF"
printf '[Options]\nWriteToFile = True\nWriteToConsole = False\n[LogTypes]\nMOVIE = True\nCORE = True\nBOOT = True\n' > ~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Logger.ini
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
mkdir -p /data/wmxix/w7shots
rm -f /data/wmxix/w7shots/${TAG}_*.png
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  -m "$DTM" --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-${TAG}.log 2>&1 &
DPID=$!
# screenshot loop
( i=0; while [ $i -lt $SECS ]; do
    xwd -root -silent | convert xwd:- /data/wmxix/w7shots/${TAG}_$(printf %03d $i).png 2>/dev/null
    sleep $SHOT_EVERY; i=$((i+SHOT_EVERY));
  done ) &
sleep $SECS
# TERM does not kill flatpak-wrapped Dolphin (it holds the ssh pipe open and
# hangs the session); use KILL on the emulator and its wrappers.
pkill -9 -x dolphin-emu 2>/dev/null; pkill -9 -f dolphin-emu-wrapper 2>/dev/null; sleep 2
pgrep -x dolphin-emu >/dev/null && echo "WARNING: dolphin still alive" || echo "dolphin dead"
ls /data/wmxix/w7shots/${TAG}_*.png | head -20
# contact sheet: up to 9 shots, 3 cols
montage /data/wmxix/w7shots/${TAG}_*.png -tile 3x -geometry 426x240+2+2 /data/wmxix/w7shots/${TAG}_sheet.png 2>/dev/null
ls -la /data/wmxix/w7shots/${TAG}_sheet.png
grep -i -E "movie|dtm|md5|error|panic" /tmp/dolphin-${TAG}.log | head -10
