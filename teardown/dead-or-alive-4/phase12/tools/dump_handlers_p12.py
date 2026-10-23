#!/usr/bin/env python3
"""Phase 12 Job 1 (corrected frame): VA_true(.text/.rdata) = 0x82000000 + fileoff.
Dumps the translator mega-function + builder + the two known ring writers,
and per-case feature extraction."""
import struct, io, contextlib, re
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
SRC='/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d=open(SRC,'rb').read()
md=Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN|CS_MODE_32)
def VA(foff): return 0x82000000+foff
def dump(foff, size, label, fh):
    fh.write(f"\n===== {label} fileoff {foff:#x} VA {VA(foff):#x} ({size} bytes) =====\n")
    for ins in md.disasm(d[foff:foff+size], VA(foff)):
        fh.write(f"{ins.address:08x}  {ins.bytes.hex():8s}  {ins.mnemonic:10s} {ins.op_str}\n")
CASES={0:0x42F638,1:0x42F9C8,2:0x42FCCC,3:0x42FFD0,4:0x430360,5:0x430664,6:0x430A3C,7:0x430C18,11:0x430CF0,12:0x430EA4,13:0x430FDC,14:0x431114,15:0x431184}
fh=open('/home/hatch/workspace/_doa4p2-scratch/p12/translator_full.txt','w')
dump(0x42F508, 0x431400-0x42F508, "TRANSLATOR MEGA-FUNCTION (prologue..finalize)", fh)
fh.close()
fh=open('/home/hatch/workspace/_doa4p2-scratch/p12/builder.txt','w')
dump(0x42EFB8, 0x42F508-0x42EFB8, "BUILDER 0x8242EFB8", fh)
dump(0x42EF58, 0x42EFB8-0x42EF58, "RING HELPERS D758/D780 (true VA 0x8242EF58/0x8242EF80)", fh)
fh.close()
fh=open('/home/hatch/workspace/_doa4p2-scratch/p12/writers.txt','w')
dump(0x41AF00, 0x200, "TAG-8 WRITER region (true VA ~0x8241AF4C)", fh)
dump(0x436400, 0x200, "TAG-7 WRITER region (true VA ~0x82436444)", fh)
fh.close()
# per-case features
def feats(foff, end):
    insns=list(md.disasm(d[foff:end], VA(foff)))
    calls=sorted(set(i.op_str for i in insns if i.mnemonic=='bl'))
    entry_loads=[f"{i.mnemonic} {i.op_str}" for i in insns if '(r30)' in i.op_str]
    shifts=[f"{i.mnemonic} {i.op_str}" for i in insns if i.mnemonic in ('srwi','slwi','srawi','rlwinm','rlwimi','srw','slw','andi.','andis.','extsb','extsh','cntlzw')]
    floats=[i.mnemonic for i in insns if i.mnemonic.startswith(('f','lfs','stfs','lfd','stfd'))]
    objacc=sorted(set(re.findall(r'0x([0-9a-f]+)\(r31\)', ' '.join(i.op_str for i in insns))))
    return len(insns), calls, entry_loads, shifts, floats, objacc
order=sorted(CASES.items(), key=lambda kv: kv[1])
print(f"{'tag':>4} {'VA':>10} {'nins':>5}  calls / entry(r30) loads / obj+offsets(r31)")
for idx,(tag,foff) in enumerate(order):
    end=order[idx+1][1] if idx+1<len(order) else 0x431400
    n,calls,el,sh,fl,oa=feats(foff,end)
    print(f"{tag:>4} {VA(foff):#010x} {n:>5}  calls={calls}")
    print(f"      entry loads: {el}")
    print(f"      shifts/masks ({len(sh)}): {sh[:14]}")
    print(f"      float insns: {sorted(set(fl))}  obj offsets: {oa}")
