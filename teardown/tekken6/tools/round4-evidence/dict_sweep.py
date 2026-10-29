import json, struct, sys, zlib, os
sys.path.insert(0,'/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools')
import tekken6_gzip as tg
ROOT='/home/hatch/workspace/_t6r4-work/recon/x/tekken6/work/decrypt3'
man=json.load(open(f'{ROOT}/manifest.json'))
bulk=open(f'{ROOT}/bulk_decrypted.bin','rb')
gz=[f for f in man['files'] if f['magic'].startswith('GZIP')]
def getraw(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
def get(i):
    f=gz[i]; d=getraw(f)
    if f['magic']=='GZIP+prefix16': d=d[16:]
    return f,d

def decode_hist(data, hist):
    """hist = bytes preceding output (window). Returns (out, bits, viols)."""
    br=tg.BitReader(data); out=bytearray(); viols=0
    full=bytearray(hist)
    while True:
        bfinal=br.bits(1); btype=br.bits(2)
        if btype==0:
            br.pos=(br.pos+7)&~7
            ln=struct.unpack('<H', data[br.pos>>3:(br.pos>>3)+2])[0]; br.pos+=32
            chunk=data[br.pos>>3:(br.pos>>3)+ln]; out.extend(chunk); full.extend(chunk); br.pos+=ln*8
        elif btype in (1,2):
            if btype==2:
                hlit=br.bits(5); hdist=br.bits(5)
                lit_lens,dist_lens=tg.decode_dynamic(br,hlit+257,hdist+1)
                lit_t=tg.build_huffman(lit_lens); dist_t=tg.build_huffman(dist_lens)
            else:
                lit_t=tg.build_huffman([8]*144+[9]*112+[7]*24+[8]*8); dist_t=tg.build_huffman([5]*32)
            while True:
                sym=tg.decode_symbol(br,lit_t)
                if sym<256: out.append(sym); full.append(sym)
                elif sym==256: break
                else:
                    li=sym-257; length=tg.LBASE[li]+br.bits(tg.LEXT[li])
                    dsym=tg.decode_symbol(br,dist_t)
                    if btype==1: dist=tg.DBASE_STD[dsym]+br.bits(tg.DEXT_STD[dsym])
                    else:
                        base=tg.DBASE_EBOOT[dsym]; nb=(30-tg.clz32(base)) if base>=4 else 0
                        dist=base+br.bits(nb)+1
                    if dist>len(full): viols+=1; dist=len(full)  # clamp, count
                    for _ in range(length):
                        b=full[-dist]; out.append(b); full.append(b)
        else: raise ValueError("btype3")
        if bfinal: break
    return bytes(out), br.pos, viols

# candidate dictionaries: name -> bytes (we use last 32768)
cands={}
cands['zeros']=bytes(32768)
cands['ff']=b'\xff'*32768
# PASS plaintexts concat
passtext=b''
for i in [19,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,56,57]:
    f,d=get(i); o,_=tg.decompress(d[22:]); passtext+=o
cands['pass_concat']=passtext
# EBOOT
eb=open('/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF','rb').read()
cands['eboot_tail']=eb[-32768:]; cands['eboot_head']=eb[:32768]
# all bulk plaintext (non-GZIP) files: individual tails tested per-file below in bulk loop
# IDX decrypted if present
for p in ['/home/hatch/workspace/_t6r4-work/recon/x/tekken6/work/decrypt2/idx_final.bin']:
    if os.path.exists(p): cands['idx']=open(p,'rb').read()

targets=[0,11,40]
td={}
for idx in targets:
    f,d=get(idx); td[idx]=(f,d)
    print(f"target idx{idx} expect={struct.unpack('<5I',d[:20])[3]}")

def score(name, hist):
    h=hist[-32768:]
    line=[]
    for idx in targets:
        f,d=td[idx]; expect=struct.unpack('<5I',d[:20])[3]; data=d[22:]
        try:
            out,bits,viols=decode_hist(data,h)
            ao=(bits+7)//8; trailer=struct.unpack('>I', data[ao:ao+4])[0] if ao+4<=len(data) else None
            line.append(f"idx{idx}: out={len(out)}(d{len(out)-expect}) viols={viols} adler={zlib.adler32(out)==trailer}")
        except Exception as e:
            line.append(f"idx{idx}: FAIL {type(e).__name__}")
    print(f"  {name}: "+" | ".join(line))

score('NONE', b'')
for n,h in cands.items(): score(n,h)
# predecessor files: for each target, the manifest file immediately before it in bulk order, and same-entry sibling
allf=man['files']
for idx in targets:
    f,_=td[idx]
    pos=allf.index(f)
    for back in [1,2,3]:
        pf=allf[pos-back]
        try: score(f'idx{idx}_pred{back}_entry{pf["entry"]}', getraw(pf))
        except Exception as e: print(e)
