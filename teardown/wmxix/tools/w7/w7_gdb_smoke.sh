#!/bin/bash
# W7 smoke test: start the Dolphin GDB stub via config key Main.General.GDBPort,
# connect gdb-multiarch, set the three Ghidra breakpoints, run, screenshot.
# Run on the Oracle VM. Leaves Dolphin running at the end (killed by caller if wanted).
set -x
export DISPLAY=:99
pkill -f dolphin-emu 2>/dev/null; pkill Xvfb 2>/dev/null; sleep 2
Xvfb :99 -screen 0 1280x720x24 > /tmp/xvfb.log 2>&1 &
sleep 2
flatpak override --user --filesystem=/data/wmxix org.DolphinEmu.dolphin-emu
nohup flatpak run org.DolphinEmu.dolphin-emu \
  -C Main.Core.CPUThread=False \
  -C Main.General.GDBPort=9090 \
  --exec /data/wmxix/wmxix-rvz.iso > /tmp/dolphin-gdb.log 2>&1 &
echo "dolphin pid $!"
# Wait for the GDB stub to listen (boot blocks in accept() until gdb connects).
for i in $(seq 1 30); do ss -ltn 2>/dev/null | grep -q ':9090' && break; sleep 2; done
ss -ltn 2>/dev/null | grep ':9090' || echo "PORT 9090 NOT LISTENING"
cat > /tmp/w7_gdb1.txt <<'EOF'
set architecture powerpc:common
set pagination off
set confirm off
target remote localhost:9090
info registers
x/4xw $pc
break *0x800364F0
break *0x8007609C
break *0x80075FB8
info breakpoints
continue
EOF
timeout 100 gdb-multiarch -q -batch -x /tmp/w7_gdb1.txt > /tmp/w7_gdb1.log 2>&1
echo "gdb exit: $?"
wc -l /tmp/w7_gdb1.log
tail -60 /tmp/w7_gdb1.log
xwd -root -silent | convert xwd:- /data/wmxix/w7-gdb-smoke.png
ls -la /data/wmxix/w7-gdb-smoke.png
ps aux | grep -i dolphin | grep -v grep | head -3
