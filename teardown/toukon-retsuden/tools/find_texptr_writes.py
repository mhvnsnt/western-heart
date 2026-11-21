#!/usr/bin/env python3
"""Find code that writes the T1/T2/T3 texture-pointer globals.

Globals (from the 0x80011AE8 dispatcher):
  T1 ptr: 0x80079F6C
  T2 ptr: 0x8007A14C
  T3 ptr: 0x80079F1C
MIPS pattern: lui $r, 0x8007  then  sw $s, 0x9F6C($r) (or lw).
Byte-scan for lui 0x8007, disassemble forward with Capstone, report
any access to the three globals.
"""
import struct
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

EXE = "/home/hatch/workspace/toukon-english/work/tr1-files/SLPS_000.84"
data = open(EXE, "rb").read()

TARGETS = {0x80079F6C: "T1ptr", 0x8007A14C: "T2ptr", 0x80079F1C: "T3ptr"}

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
md.detail = False

# The compiler accesses the globals via lui 0x8008 + NEGATIVE offset:
#   T1ptr 0x80079F6C = lui 0x8008, lw/sw -0x6094
#   T2ptr 0x8007A14C = lui 0x8008, lw/sw -0x5EB4
#   T3ptr 0x80079F1C = lui 0x8008, lw/sw -0x60E4
TARGET_OFFS = {-0x6094: "T1ptr", -0x5EB4: "T2ptr", -0x60E4: "T3ptr"}

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
md.detail = False

# lui $rt, 0x8008 -> (w>>26)==0x0F and imm==0x8008
hits = []
for i in range(0x800, len(data) - 4, 4):
    w = struct.unpack_from("<I", data, i)[0]
    if (w >> 26) == 0x0F and (w & 0xFFFF) == 0x8008:
        hits.append(i)
print(f"lui 0x8008 sites: {len(hits)}")

for foff in hits:
    ram = foff - 0x800 + 0x80010000
    code = data[foff:foff + 24*4]
    reg = None
    for ins in md.disasm(code, ram):
        if ins.mnemonic == "lui" and ins.op_str.endswith("0x8008"):
            reg = ins.op_str.split(",")[0].strip()
        elif reg and ins.mnemonic in ("sw", "lw"):
            try:
                parts = ins.op_str.split(",")
                off_s, base = parts[1].strip().rstrip(")").split("(")
                offv = int(off_s, 0)
                if base == reg and offv in TARGET_OFFS:
                    print(f"  {TARGET_OFFS[offv]} {ins.mnemonic} at RAM 0x{ins.address:08x} "
                          f"(lui at 0x{ram:08x}) : {ins.mnemonic} {ins.op_str}")
            except Exception:
                pass
print("done")
