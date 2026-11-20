#!/usr/bin/env python3
"""Disassemble SLUS_212.09 .text with Capstone (MIPS32 LE) into an indexed text dump.
One instruction per line: ADDR: mnemonic operands ; raw hex.
Also dumps .rodata string table (addr -> string) for xref work.
Standard tool (Capstone), no hand-written disassembler.
"""
import struct, re, sys
from pathlib import Path

ELF = Path.home() / "workspace/urban-reign-redux/decoded/inputs/iso/SLUS_212.09"
OUT = Path.home() / "workspace/urban-reign-redux/decoded/iso/slus_text.asm"
STRS = Path.home() / "workspace/urban-reign-redux/decoded/inputs/iso/slus_rodata_strings.txt"

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

b = ELF.read_bytes()
text_off, text_addr, text_size = 0x1000, 0x100000, 2387256
ro_off, ro_addr, ro_size = 0x5AAD00, 0x6A9D00, 400500
code = b[text_off:text_off + text_size]

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
md.detail = False
md.skipdata = True
md.skipdata_setup = ("db", None, None)
n = 0
with open(OUT, "w") as f:
    for ins in md.disasm(code, text_addr):
        f.write(f"{ins.address:08x}: {ins.mnemonic} {ins.op_str} ; {ins.bytes.hex()}\n")
        n += 1
print(f"disassembled {n} instructions -> {OUT}")

# rodata strings with vaddr
ro = b[ro_off:ro_off + ro_size]
with open(STRS, "w") as f:
    for m in re.finditer(rb"[ -~]{4,}", ro):
        f.write(f"{ro_addr + m.start():08x}: {m.group().decode()}\n")
print(f"rodata strings -> {STRS}")
