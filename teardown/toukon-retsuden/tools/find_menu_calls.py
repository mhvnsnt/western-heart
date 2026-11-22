#!/usr/bin/env python3
"""Find all callers of the text dispatcher 0x80011AE8 and the a3 (glyph/text
index) each one passes. This maps T1 rect indices to the code that draws them.

jal 0x80011AE8 = word 0x0C0046BA. Scan .text for it, disassemble backwards
to find the a3 assignment (ori/addiu/li $a3, imm).
"""
import struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

EXE = "/home/hatch/workspace/toukon-english/work/tr1-files/SLPS_000.84"
data = open(EXE, "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)

JAL = 0x0C0046BA
calls = []
for i in range(0x800, len(data) - 4, 4):
    w = struct.unpack_from("<I", data, i)[0]
    if w == JAL:
        calls.append(i)
print(f"jal 0x80011AE8 sites: {len(calls)}")

for foff in calls:
    ram = foff - 0x800 + 0x80010000
    # disassemble 16 instructions before the jal
    start = max(0x800, foff - 16 * 4)
    code = data[start:foff + 4]
    insns = list(md.disasm(code, start - 0x800 + 0x80010000))
    a3 = None
    a0 = a1 = a2 = None
    for ins in insns:
        if ins.address >= ram:
            break
        # track $a0-$a3 immediate loads
        if ins.mnemonic in ("ori", "addiu", "li", "move"):
            parts = ins.op_str.replace(" ", "").split(",")
            if len(parts) == 2:
                dst, src = parts
                if dst == "$a3":
                    try:
                        a3 = int(src, 0)
                    except ValueError:
                        a3 = src  # register move
                elif dst == "$a0":
                    try: a0 = int(src, 0)
                    except ValueError: a0 = src
                elif dst == "$a1":
                    try: a1 = int(src, 0)
                    except ValueError: a1 = src
                elif dst == "$a2":
                    try: a2 = int(src, 0)
                    except ValueError: a2 = src
        elif ins.mnemonic == "lui":
            pass
    print(f"  call at 0x{ram:08x}: a3={a3} a0={a0} a1={a1} a2={a2}")
