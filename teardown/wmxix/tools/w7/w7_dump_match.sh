#!/bin/bash
# W7 in-match dump runner: Dolphin + GDB stub + obs1.dtm, interrupt mid-match,
# dump MEM1. Usage: w7_dump_match.sh <wait_seconds> <tag>
set -x
WAIT="${1:-300}"; TAG="${2:-match}"
export DISPLAY=:99
for i in 1 2 3; do
  pkill -x dolphin-emu 2>/dev/null; sleep 3
  pgrep -x dolphin-emu >/dev/null || break
  pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
done
U=~/.var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu
C=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu
rm -rf "$U/GC" "$U/Wii/shared2" "$U/Cache" "$C/Qt.ini" "$C/TimePlayed.ini"
printf '[Analytics]\nID = 3ef0eebbdbf7bd40ff182abcea4a4cc4\n\n[General]\nGDBPort = 9090\n' > "$C/Dolphin.ini"
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
mkdir -p /data/wmxix/w7shots
rm -f /data/wmxix/w7shots/${TAG}_*.png
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  -m /data/wmxix/w7/obs1.dtm --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-${TAG}.log 2>&1 &
# Screenshot loop (every 20s) to confirm the match state at interrupt time.
( i=0; while [ $i -lt 700 ]; do
    xwd -root -silent | convert xwd:- /data/wmxix/w7shots/${TAG}_$(printf %03d $i).png 2>/dev/null
    sleep 20; i=$((i+20));
  done ) &
for i in $(seq 1 90); do
  ss -ltn 2>/dev/null | grep -q ':9090' && break
  sleep 2
done
ss -ltn 2>/dev/null | grep -q ':9090' && echo "GDB stub listening" || { echo "GDB STUB NOT LISTENING"; pkill -9 -x dolphin-emu; exit 1; }
python3 /data/wmxix/w7_dump_match.py --wait "$WAIT" --out /data/wmxix/w7/mem1_${TAG}.bin > /data/wmxix/w7/dump_${TAG}.log 2>&1
cat /data/wmxix/w7/dump_${TAG}.log
montage /data/wmxix/w7shots/${TAG}_*.png -tile 3x -geometry 426x240+2+2 /data/wmxix/w7shots/${TAG}_sheet.png 2>/dev/null
ls -la /data/wmxix/w7/mem1_${TAG}.bin /data/wmxix/w7shots/${TAG}_sheet.png 2>/dev/null
pkill -9 -x dolphin-emu; sleep 2
echo DUMP-DONE
