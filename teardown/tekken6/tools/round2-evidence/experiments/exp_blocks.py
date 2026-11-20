import json, struct, sys
sys.path.insert(0,'/home/hatch/workspace/_t6lane')
import t6inflate2 as ti
# fixed CL semantics
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
ti.decode_dynamic = decode_dynamic_fixed

W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
def clz(x): return 32-x.bit_length() if x else 32
DBS=[1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577]
DES=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]

def trace(idx):
    t=gz[idx]; fd=readdata(t)
    if t['magic']=='GZIP+prefix16': fd=fd[16:]
    w=struct.unpack('<5I', fd[:20]); body=fd[20:]
    data=body[2:]
    br=ti.BitReader(data); out=bytearray(); blk=0
    print(f'=== idx{idx} entry{t["entry"]} expect={w[3]} body={len(body)}', flush=True)
    while True:
        startbit=br.pos; bfinal=br.bits(1); btype=br.bits(2); blk+=1
        print(f' block{blk}: startbit={startbit} bfinal={bfinal} btype={btype} out_at_start={len(out)}', flush=True)
        if btype==0:
            br.pos=(br.pos+7)&~7
            ln=struct.unpack('<H', data[br.pos>>3:(br.pos>>3)+2])[0]; br.pos+=16
            nln=struct.unpack('<H', data[br.pos>>3:(br.pos>>3)+2])[0]; br.pos+=16
            print(f'   stored ln={ln} nln={nln} ok={ln^0xFFFF==nln}', flush=True)
            out.extend(data[br.pos>>3:(br.pos>>3)+ln]); br.pos+=ln*8
        elif btype in (1,2):
            if btype==2:
                hlit=br.bits(5); hdist=br.bits(5)
                ll,dl=ti.decode_dynamic(br,hlit+257,hdist+1)
                lit_t=ti.build_huffman(ll); dist_t=ti.build_huffman(dl)
            else:
                lit_t=ti.build_huffman([8]*144+[9]*112+[7]*24+[8]*8); dist_t=ti.build_huffman([5]*32)
            nm=0
            while True:
                sym=ti.decode_symbol(br,lit_t)
                if sym<256: out.append(sym)
                elif sym==256: break
                else:
                    li=sym-257; length=ti.LBASE[li]+br.bits(ti.LEXT[li])
                    dsym=ti.decode_symbol(br,dist_t)
                    if btype==1: dist=DBS[dsym]+br.bits(DES[dsym])
                    else:
                        b=ti.DBASE_EBOOT[dsym]; dist=b+(br.bits(30-clz(b)) if b>=4 else 0)+1
                    nm+=1
                    if dist>len(out):
                        out.extend(b'\x00'*length)
                        if nm<3: print(f'   viol match{nm} out={len(out)} dist={dist}', flush=True)
                    else:
                        for _ in range(length): out.append(out[-dist])
            print(f'   block{blk} end: out={len(out)} endbit={br.pos} matches={nm}', flush=True)
        else:
            print('   RESERVED BTYPE — parse desync here', flush=True); return
        if bfinal: break
    print(f' TOTAL out={len(out)} bits_used={br.pos} bits_avail={len(data)*8}', flush=True)

for idx in (59, 0, 58):
    try: trace(idx)
    except Exception as e: print(f'idx{idx} EXC {type(e).__name__}: {e}', flush=True)
print('DONE')
