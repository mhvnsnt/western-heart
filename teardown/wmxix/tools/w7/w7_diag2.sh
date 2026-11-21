#!/bin/bash
# W7 diag2: launch Dolphin with GDBPort + movie, screenshot every 10s for 90s,
# poll the GDB port. Does NOT kill Dolphin on port failure (inspect state).
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
rm -f /data/wmxix/w7shots/diag2_*.png
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  -m /data/wmxix/w7/obs1.dtm --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-diag2.log 2>&1 &
for t in 10 20 30 40 50 60 70 80 90; do
  sleep 10
  xwd -root -silent | convert xwd:- /data/wmxix/w7shots/diag2_$(printf %03d $t).png 2>/dev/null
  if ss -ltn 2>/dev/null | grep -q ':9090'; then echo "t=$t PORT-LISTENING"; else echo "t=$t port-closed"; fi
  ps aux | grep "[d]olphin-emu -C" | awk '{print "  dolphin cpu%="$3" mem%="$4}'
done
xdotool search --name ".*" getwindowname %@ 2>/dev/null | head -10
montage /data/wmxix/w7shots/diag2_*.png -tile 3x -geometry 426x240+2+2 /data/wmxix/w7shots/diag2_sheet.png 2>/dev/null
ls -la /data/wmxix/w7shots/diag2_sheet.png
# leave Dolphin running for inspection; caller kills it
echo DIAG2-DONE-DOLPHIN-STILL-RUNNING
