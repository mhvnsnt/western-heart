#!/bin/bash
# W7 probe runner: Dolphin + GDB stub, NO movie; attach w7_rsp_probe.py.
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
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-probe.log 2>&1 &
# Screenshot loop (every 15s) so we can see whether the game resumes after
# the probe's final continue.
mkdir -p /data/wmxix/w7shots
rm -f /data/wmxix/w7shots/probe_*.png
( i=0; while [ $i -lt 240 ]; do
    xwd -root -silent | convert xwd:- /data/wmxix/w7shots/probe_$(printf %03d $i).png 2>/dev/null
    sleep 15; i=$((i+15));
  done ) &
# Wait up to 180s for the stub (Dolphin startup is slow under VM load).
for i in $(seq 1 90); do
  ss -ltn 2>/dev/null | grep -q ':9090' && break
  sleep 2
done
ss -ltn 2>/dev/null | grep -q ':9090' && echo "GDB stub listening" || { echo "GDB STUB NOT LISTENING"; pkill -9 -x dolphin-emu; exit 1; }
python3 /data/wmxix/w7_rsp_probe.py --host 127.0.0.1 --port 9090 --dump-mem1 /data/wmxix/w7/mem1_title.bin > /data/wmxix/w7/probe_result.log 2>&1
cat /data/wmxix/w7/probe_result.log
montage /data/wmxix/w7shots/probe_*.png -tile 3x -geometry 426x240+2+2 /data/wmxix/w7shots/probe_sheet.png 2>/dev/null
ls -la /data/wmxix/w7shots/probe_sheet.png /data/wmxix/w7/mem1_title.bin 2>/dev/null
pkill -9 -x dolphin-emu; sleep 2
echo PROBE-DONE
