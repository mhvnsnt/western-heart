import sys
sys.path.insert(0,'/home/hatch/workspace/_t6r4-work/venv/lib/python3.12/site-packages')
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
img=open('/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF','rb').read()
def va2off(va): return va-0x8803000
md=Cs(CS_ARCH_MIPS, CS_MODE_MIPS32+CS_MODE_LITTLE_ENDIAN)
md.skipdata=True
for start,end in [(0x8b55de0,0x8b55fa8)]:
    off=va2off(start); blob=img[off:off+(end-start)]
    for ins in md.disasm(blob, start):
        raw=img[va2off(ins.address):va2off(ins.address)+4].hex()
        print(f"  {ins.address:#010x}: [{raw}] {ins.mnemonic:8s} {ins.op_str}")
