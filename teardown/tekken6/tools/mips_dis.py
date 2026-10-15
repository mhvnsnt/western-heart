import struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN
ELF = '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
data = open(ELF,'rb').read()
LOAD_OFF, LOAD_VA = 0x1018, 0x8804018
def v2o(v): return v - LOAD_VA + LOAD_OFF
def word(v): return struct.unpack_from('<I', data, v2o(v))[0]
RN=['$zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
def allegrex0(w):
    sub=(w>>6)&0x1f; rt=(w>>16)&0x1f; rd=(w>>11)&0x1f
    if sub<16: name='wsbh' if sub%2==0 else 'wsbw'
    elif sub<20: name='seb'
    elif sub<24: name='bitrev'
    elif sub<28: name='seh'
    else: name='bitrev'
    return f"{name:12s} {RN[rd]}, {RN[rt]}"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_LITTLE_ENDIAN)
def one(v):
    w=word(v)
    if (w>>26)==0x1F and (w&0x3f)==0x20:
        return f"{w:08x} {allegrex0(w)}"
    ins=list(md.disasm(struct.pack('<I',w), v, count=1))
    if ins:
        i=ins[0]; return f"{i.bytes.hex():10s} {i.mnemonic:12s} {i.op_str}"
    return f"{w:08x} {'???':12s}"
if __name__=='__main__':
    v=int(sys.argv[1],16); vend=int(sys.argv[2],16)
    while v<vend:
        print(f"{v:#010x}: {one(v)}"); v+=4
