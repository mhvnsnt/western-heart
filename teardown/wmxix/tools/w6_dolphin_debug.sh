#!/bin/bash
# W6: relaunch WMXIX in Dolphin with the debugger pane (-d), single-core
# (CPUThread=False, required for reliable debugging), screenshot the UI.
set -x
export DISPLAY=:99
# Xvfb :99 should still be running from the boot script; restart if not.
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
nohup flatpak run org.DolphinEmu.dolphin-emu -d \
  -C Main.Core.CPUThread=False \
  --exec /data/wmxix/wmxix-rvz.iso \
  > /tmp/dolphin-debug.log 2>&1 &
echo "dolphin-debug pid $!"
sleep 40
xdotool search --name "Dolphin" getwindowname %@ 2>/dev/null | head -10
import -window root /data/wmxix/dolphin-debug-40s.png
ls -la /data/wmxix/dolphin-debug-40s.png
