#!/bin/bash
# W7 run A: connect gdb to the waiting Dolphin GDB stub, set the 3 Ghidra
# breakpoints, continue ~75s, screenshot. Dolphin must already be listening
# on :9090 (see w7_gdb2.sh).
cat > /tmp/w7_gdbA.txt <<'EOF'
set architecture powerpc:common
set pagination off
set confirm off
target remote localhost:9090
info registers
x/8xw $pc
break *0x800364F0
break *0x8007609C
break *0x80075FB8
info breakpoints
continue
EOF
timeout 75 gdb-multiarch -q -batch -x /tmp/w7_gdbA.txt > /tmp/w7_gdbA.log 2>&1
echo "gdb exit: $?"
cat /tmp/w7_gdbA.log
export DISPLAY=:99
xwd -root -silent | convert xwd:- /data/wmxix/w7-gdbA.png
ls -la /data/wmxix/w7-gdbA.png
