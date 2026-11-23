#!/bin/bash
# W6: boot WMXIX in Dolphin under Xvfb, screenshot, report.
# Run on the Oracle VM. Leaves Dolphin running for follow-up steps.
set -x
export DISPLAY=:99
Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
sleep 2
# Flatpak needs the filesystem override for /data (already set for convert;
# re-apply to be safe) and the display.
flatpak override --user --filesystem=/data/wmxix org.DolphinEmu.dolphin-emu
nohup flatpak run org.DolphinEmu.dolphin-emu --exec /data/wmxix/wmxix-rvz.iso \
  > /tmp/dolphin-boot.log 2>&1 &
echo "dolphin pid $!"
sleep 45
xdotool search --name "Dolphin" getwindowname %@ 2>/dev/null | head
import -window root /data/wmxix/dolphin-boot-45s.png 2>/dev/null || \
  xwd -root -silent | convert xwd:- /data/wmxix/dolphin-boot-45s.png
ls -la /data/wmxix/dolphin-boot-45s.png
ps aux | grep -i dolphin | grep -v grep | head -3
