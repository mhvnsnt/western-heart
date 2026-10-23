import struct
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
p='/home/hatch/workspace/doa4-bass/default_pe.bin'
d=open(p,'rb').read()
TEXT_RAW=0x2d1800; TEXT_RVA=0x2e0000; TEXT_SZ=0x86ae00; BASE=0x82000000
targets={0x82047890:'err_adxf_stat',0x820479a8:'err_adxf_parallel',0x83022eda:'bss_table',0x82c48fa0:'afs_struct',0x8221e9ac:'str_chrone',0x8221e988:'str_chrtwo',0x8221e964:'str_chrthree',0x8221e908:'str_mot',0x8221e8ec:'str_snd',0x8221e924:'str_cmn',0x8221e8cd:'str_spr_cache'}
md=Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN|CS_MODE_32)
code=d[TEXT_RAW:TEXT_RAW+TEXT_SZ]
base_va=BASE+TEXT_RVA
insns=[]  # (va, mnemonic, op_str, reg, imm)
off=0
while off < len(code)-3:
    got=None
    for ins in md.disasm(code[off:off+4], base_va+off):
        got=ins; break
    if got is None:
        off+=4; continue
    insns.append(got)
    off+=4
print('decoded insns:', len(insns))
hits=[]
for i,ins in enumerate(insns):
    if ins.mnemonic!='lis': continue
    parts=ins.op_str.split(',')
    if len(parts)!=2: continue
    reg=parts[0].strip()
    try: hi=int(parts[1].strip(),0)&0xffff
    except Exception: continue
    for va,label in targets.items():
        if (va>>16)!=hi: continue
        for j in range(i+1, min(i+8,len(insns))):
            n=insns[j]
            if n.mnemonic not in ('addi','ori'): continue
            np_=n.op_str.split(',')
            if np_[0].strip()!=reg: continue
            try: lo=int(np_[-1].strip(),0)
            except Exception: continue
            if n.mnemonic=='addi' and lo>=0x8000: lo-=0x10000
            val=((hi<<16)+lo)&0xffffffff
            if val==va:
                hits.append((ins.address,label))
                print(f"HIT {label} lis@{ins.address:#x} complete@{n.address:#x}")
            break
print('total complete-address hits:', len(hits))
from collections import Counter
c=Counter()
for ins in insns:
    if ins.mnemonic=='lis':
        try: hi=int(ins.op_str.split(',')[1].strip(),0)&0xffff
        except Exception: continue
        for va,label in targets.items():
            if (va>>16)==hi: c[label]+=1
print('lis-hi counts:', dict(c))
