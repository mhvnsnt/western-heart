import struct
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
p='/home/hatch/workspace/doa4-bass/default_pe.bin'
d=open(p,'rb').read()
def va2off(va): return va - 0x82000000 - 0x2e0000 + 0x2d1800  # .text only
md=Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN|CS_MODE_32)
md.detail=False
# TEARDOWN lead: S-box generation code at VA 0x822f06d0; dump 0x822f0000-0x822f0900
start=0x822f0400; end=0x822f0900
off=va2off(start)
code=d[off:off+(end-start)]
for ins in md.disasm(code, start):
    print(f"{ins.address:#010x}: {ins.mnemonic:8s} {ins.op_str}")
