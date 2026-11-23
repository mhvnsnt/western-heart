#!/bin/bash
# W7 diag: launch Dolphin WITHOUT a movie to see if the GetDirectoryForRegion
# panic is caused by the DTM or by Dolphin state. Screenshots at 15/30/45s.
export DISPLAY=:99
for i in 1 2 3; do
  pkill -x dolphin-emu 2>/dev/null; sleep 3
  pgrep -x dolphin-emu >/dev/null || break
  pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
done
CONF=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Dolphin.ini
printf '[Analytics]\nID = 3ef0eebbdbf7bd40ff182abcea4a4cc4\n' > "$CONF"
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
mkdir -p /data/wmxix/w7shots
rm -f /data/wmxix/w7shots/diag_*.png
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False \
  --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-diag.log 2>&1 &
for t in 15 30 45; do
  sleep 15
  xwd -root -silent | convert xwd:- /data/wmxix/w7shots/diag_$(printf %03d $t).png 2>/dev/null
done
# list windows (to see dialog titles)
xdotool search --name ".*" getwindowname %@ 2>/dev/null | head -20
pkill -9 -x dolphin-emu 2>/dev/null; sleep 2
echo DIAG-DONE
