import json, struct, sys, zlib
sys.path.insert(0,'/home/hatch/workspace/_t6lane')
import t6inflate2 as ti
def decode_dynamic_fixed(br, hlit_n, hdist_n):
    hclen = br.bits(4)
    cl_lens = [0]*28
    ORDER=[16,19,27,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]
    for i in range(hclen+4): cl_lens[ORDER[i]] = br.bits(3)
    cl_table = ti.build_huffman(cl_lens)
    total = hlit_n + hdist_n; lens = []
    while len(lens) < total:
        sym = ti.decode_symbol(br, cl_table)
        if sym <= 15: lens.append(sym)
        elif sym == 16:
            rep = 3 + br.bits(2); prev = lens[-1] if lens else 0
            lens.extend([prev]*rep)
        elif sym == 19: rep = 3 + br.bits(3); lens.extend([0]*rep)
        elif sym == 27: rep = 11 + br.bits(7); lens.extend([0]*rep)
        else: raise ValueError(f'cl sym {sym}')
    return lens[:hlit_n], lens[hlit_n:hlit_n+hdist_n]
W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
LT=[-25,-48,-64,-80,-96,-112,-128,-144,-160,-161,-193,-225,-257,-297,-361,-425,-489,-549,-677,-805,-933,-1069,-1325,-1581,-1837,-2083,-2595,-3107,-3619,-4128,-1,-1]  # EBOOT @0x8bd637c
def clz(x): return 32-x.bit_length() if x else 32
DBS=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577]
DES=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]

def run(idx, mode):
    t=gz[idx]; fd=readdata(t)
    if t['magic']=='GZIP+prefix16': fd=fd[16:]
    w=struct.unpack('<5I', fd[:20]); body=fd[20:]
    data=body[2:]; expect=w[3]
    trailer=struct.unpack('>I', body[-4:])[0]
    br=ti.BitReader(data); out=bytearray()
    while True:
        bfinal=br.bits(1); btype=br.bits(2)
        if btype==0:
            br.pos=(br.pos+7)&~7
            ln=struct.unpack('<H', data[br.pos>>3:(br.pos>>3)+2])[0]; br.pos+=16
            br.pos+=16
            out.extend(data[br.pos>>3:(br.pos>>3)+ln]); br.pos+=ln*8
        elif btype in (1,2):
            if btype==2:
                hlit=br.bits(5); hdist=br.bits(5)
                ll,dl=decode_dynamic_fixed(br,hlit+257,hdist+1)
                lit_t=ti.build_huffman(ll); dist_t=ti.build_huffman(dl)
            else:
                lit_t=ti.build_huffman([8]*144+[9]*112+[7]*24+[8]*8); dist_t=ti.build_huffman([5]*32)
            while True:
                sym=ti.decode_symbol(br,lit_t)
                if sym<256: out.append(sym)
                elif sym==256: break
                else:
                    i=sym-257; X=LT[i]
                    neb=ti.LEXT[i]
                    extra=br.bits(neb) if neb else 0
                    if mode=='L1': length=-(X>>4)+extra
                    elif mode=='L2': length=-(X>>4)+extra+1
                    elif mode=='L3': length=-(X>>4)-extra
                    elif mode=='L4': length=-(X>>4)-extra+1
                    dsym=ti.decode_symbol(br,dist_t)
                    if btype==1: dist=DBS[dsym]+br.bits(DES[dsym])
                    else:
                        b=ti.DBASE_EBOOT[dsym]; dist=b+(br.bits(30-clz(b)) if b>=4 else 0)+1
                    if dist>len(out): raise ValueError(f'dist {dist}>out {len(out)}')
                    for _ in range(length): out.append(out[-dist])
        else: raise ValueError('btype 3')
        if bfinal: break
    ok = len(out)==expect and zlib.adler32(bytes(out))==trailer
    print(f'idx{idx} {mode}: out={len(out)} expect={expect} diff={len(out)-expect} adler_ok={zlib.adler32(bytes(out))==trailer} EXACT={ok}', flush=True)
    return ok
for mode in ('L1','L2','L3','L4'):
    try: run(0, mode)
    except Exception as e: print(f'idx0 {mode}: EXC {e}', flush=True)
print('DONE')
