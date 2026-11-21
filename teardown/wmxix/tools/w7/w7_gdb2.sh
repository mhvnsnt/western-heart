#!/bin/bash
# W7 test 2: GDB stub via Dolphin.ini [General] GDBPort=9090 (not -C).
# Run on the Oracle VM. Logs to /tmp/w7_gdb2.log.
set -x
export DISPLAY=:99
pkill -x dolphin-emu 2>/dev/null; sleep 2
CONF=~/.var/app/org.DolphinEmu.dolphin-emu/config/dolphin-emu/Dolphin.ini
printf '[Analytics]\nID = 3ef0eebbdbf7bd40ff182abcea4a4cc4\n\n[General]\nGDBPort = 9090\n' > "$CONF"
cat "$CONF"
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-gdb2.log 2>&1 &
echo "dolphin started"
for i in $(seq 1 15); do ss -ltn 2>/dev/null | grep -q ':9090' && break; sleep 2; done
ss -ltn 2>/dev/null | grep ':9090' && echo PORT-OPEN || echo PORT-CLOSED
ps aux | grep -c "[d]olphin-emu"
