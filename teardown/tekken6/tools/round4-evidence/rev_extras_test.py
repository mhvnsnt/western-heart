import json, struct, sys, zlib
sys.path.insert(0,'/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools')
import tekken6_gzip as tg
ROOT='/home/hatch/workspace/_t6r4-work/recon/x/tekken6/work/decrypt3'
man=json.load(open(f'{ROOT}/manifest.json'))
bulk=open(f'{ROOT}/bulk_decrypted.bin','rb')
gz=[f for f in man['files'] if f['magic'].startswith('GZIP')]
def get(i):
    f=gz[i]; bulk.seek(f['start_rel']*2048); d=bulk.read(f['size'])
    if f['magic']=='GZIP+prefix16': d=d[16:]
    return f,d

def revbits(v,n):
    r=0
    for i in range(n): r=(r<<1)|((v>>i)&1)
    return r

def decode(data, rev_len=False, rev_dist=False, rev_cl=False):
    br=tg.BitReader(data); out=bytearray(); viols=0
    def bits(n, rev=False):
        v=br.bits(n)
        return revbits(v,n) if rev else v
    while True:
        bfinal=br.bits(1); btype=br.bits(2)
        if btype==0:
            br.pos=(br.pos+7)&~7
            ln=struct.unpack('<H', data[br.pos>>3:(br.pos>>3)+2])[0]; br.pos+=32
            out.extend(data[br.pos>>3:(br.pos>>3)+ln]); br.pos+=ln*8
        elif btype in (1,2):
            if btype==2:
                hlit=br.bits(5); hdist=br.bits(5)
                # dynamic header with standard CL (rev_cl not applied to counts)
                lit_lens,dist_lens=tg.decode_dynamic(br,hlit+257,hdist+1)
                lit_t=tg.build_huffman(lit_lens); dist_t=tg.build_huffman(dist_lens)
            else:
                lit_t=tg.build_huffman([8]*144+[9]*112+[7]*24+[8]*8); dist_t=tg.build_huffman([5]*32)
            while True:
                sym=tg.decode_symbol(br,lit_t)
                if sym<256: out.append(sym)
                elif sym==256: break
                else:
                    li=sym-257; length=tg.LBASE[li]+bits(tg.LEXT[li], rev_len)
                    dsym=tg.decode_symbol(br,dist_t)
                    if btype==1: dist=tg.DBASE_STD[dsym]+bits(tg.DEXT_STD[dsym], rev_dist)
                    else:
                        base=tg.DBASE_EBOOT[dsym]; nb=(30-tg.clz32(base)) if base>=4 else 0
                        dist=base+bits(nb, rev_dist)+1
                    if dist>len(out):
                        viols+=1
                        for k in range(length):
                            s=len(out)-dist; out.append(out[s] if s>=0 else 0)
                    else:
                        for _ in range(length): out.append(out[-dist])
        else: raise ValueError("btype3")
        if bfinal: break
    return bytes(out), br.pos, viols

for idx in [0,40,11]:
    f,d=get(idx); w=struct.unpack('<5I',d[:20]); expect=w[3]
    data=d[22:]
    for name,kw in [('std',{}),('revL',{'rev_len':True}),('revD',{'rev_dist':True}),('revLD',{'rev_len':True,'rev_dist':True})]:
        try:
            out,bits,viols=decode(data,**kw)
            adler_off=(bits+7)//8
            trailer=struct.unpack('>I', data[adler_off:adler_off+4])[0] if adler_off+4<=len(data) else None
            print(f"idx{idx} {name}: out={len(out)} expect={expect} d={len(out)-expect} viols={viols} endbit={bits} adler_ok={zlib.adler32(out)==trailer}")
        except Exception as e:
            print(f"idx{idx} {name}: FAIL {type(e).__name__} {e}")
