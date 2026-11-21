#!/bin/bash
# W7 run B: relaunch Dolphin (GDB stub via Dolphin.ini), connect gdb, set the
# 3 breakpoints, continue ~75s, screenshot. No memory reads before continue
# (PC is garbage until boot proceeds).
set -x
export DISPLAY=:99
pkill -x dolphin-emu 2>/dev/null; sleep 2
if ! xdotool search --name ".*" > /dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
  sleep 2
fi
nohup flatpak run org.DolphinEmu.dolphin-emu -C Main.Core.CPUThread=False --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-gdbB.log 2>&1 &
for i in $(seq 1 15); do ss -ltn 2>/dev/null | grep -q ':9090' && break; sleep 2; done
ss -ltn 2>/dev/null | grep ':9090' || { echo PORT-CLOSED; exit 1; }
cat > /tmp/w7_gdbB.txt <<'EOF'
set architecture powerpc:common
set pagination off
set confirm off
target remote localhost:9090
info registers
break *0x800364F0
break *0x8007609C
break *0x80075FB8
info breakpoints
continue
EOF
timeout 75 gdb-multiarch -q -batch -x /tmp/w7_gdbB.txt > /tmp/w7_gdbB.log 2>&1
echo "gdb exit: $?"
cat /tmp/w7_gdbB.log
xwd -root -silent | convert xwd:- /data/wmxix/w7-gdbB.png
ls -la /data/wmxix/w7-gdbB.png
ps aux | grep "[d]olphin-emu -C" | awk '{print $3, $4}'
