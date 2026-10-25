import json, struct, sys, zlib
sys.path.insert(0,'/home/hatch/workspace/_t6lane')
from unicorn import *
from unicorn.mips_const import *

W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]

IMG_BASE=0x8800000
IMG_SIZE=0x800000
img=open('/home/hatch/workspace/_t6lane/eboot_raw.bin','rb').read()
assert len(img)<=IMG_SIZE

def run_inflate(idx, use_wrapper=True):
    t=gz[idx]; fd=readdata(t)
    if t['magic']=='GZIP+prefix16': fd=fd[16:]
    w=struct.unpack('<5I', fd[:20]); body=fd[20:]
    expect=w[3]
    mu=Uc(UC_ARCH_MIPS, UC_MODE_MIPS32+UC_MODE_LITTLE_ENDIAN)
    mu.mem_map(IMG_BASE, IMG_SIZE)
    mu.mem_write(0x8804018, img)
    OUT=0x20000000; mu.mem_map(OUT, 0x1000000)
    INP=0x30000000; mu.mem_map(INP, 0x400000)
    mu.mem_write(INP, body)
    STK=0x7f000000; mu.mem_map(STK, 0x100000)
    sp=STK+0x80000
    RET=0x8804018  # jump back to image start (zeros = nop sled? use a dedicated trap addr)
    TRAP=0x40000000; mu.mem_map(TRAP, 0x1000)
    mu.mem_write(TRAP, struct.pack('<I', 0x0000000d))  # break instruction? use jalr zero loop: jr ra with ra=TRAP loops
    mu.mem_write(TRAP, struct.pack('<I', 0x03e00008))  # jr $ra -> self loop at TRAP when ra=TRAP
    mu.reg_write(UC_MIPS_REG_SP, sp)
    mu.reg_write(UC_MIPS_REG_RA, TRAP)
    mu.reg_write(UC_MIPS_REG_A0, OUT)
    mu.reg_write(UC_MIPS_REG_A1, expect+65536)
    mu.reg_write(UC_MIPS_REG_A2, INP)
    mu.reg_write(UC_MIPS_REG_A3, OUT+0xF00000)  # param_4: consumed-ptr out (wrapper signature: dest,len,src,&consumed?) actually fn_1bf0(param1=dest,param2=len,param3=src_addr_int,param4=&bytes_consumed_out_len?)
    entry = 0x8b559c8 if use_wrapper else 0x8b55bf0
    try:
        mu.emu_start(entry, TRAP, count=200_000_000)
        status='returned'
    except UcError as e:
        status=f'UcError: {e} pc={mu.reg_read(UC_MIPS_REG_PC):#x}'
    v0=mu.reg_read(UC_MIPS_REG_V0)
    out=mu.mem_read(OUT, min(expect+64, 0x1000000))
    consumed=struct.unpack('<I', mu.mem_read(OUT+0xF00000,4))[0]
    print(f'idx{idx} entry={hex(entry)} status={status} v0={v0} ({v0-2**32 if v0>=2**31 else v0}) expect={expect} consumed_out={consumed}', flush=True)
    if v0>=0 and v0==expect:
        adler_stored=struct.unpack('>I', body[2+v0*0+ (struct.unpack("<I", mu.mem_read(OUT+0xF00000,4))[0] if False else 0):][:0] or b'\0\0\0\0') if False else None
        print('  FULL SIZE MATCH; adler(out)=', hex(zlib.adler32(bytes(out[:expect]))), flush=True)
        return bytes(out[:expect])
    else:
        nonzero=sum(1 for b in out[:expect] if b!=0)
        print(f'  out nonzero bytes in expect range: {nonzero}/{expect}', flush=True)
        return None

for idx in (19, 56, 0):
    run_inflate(idx)
print('DONE')
