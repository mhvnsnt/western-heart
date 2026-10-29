import json, struct, sys
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
ti.decode_dynamic = decode_dynamic_fixed
W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
def clz(x): return 32-x.bit_length() if x else 32
t=gz[59]; fd=readdata(t)
w=struct.unpack('<5I', fd[:20]); body=fd[20:]
data=body[2:]
br=ti.BitReader(data); out=bytearray()
bfinal=br.bits(1); btype=br.bits(2)
hlit=br.bits(5); hdist=br.bits(5)
ll,dl=ti.decode_dynamic(br,hlit+257,hdist+1)
print('lit_lens[250:290]:', ll[250:290], flush=True)
print('len of sym256 code:', ll[256], flush=True)
lit_t=ti.build_huffman(ll); dist_t=ti.build_huffman(dl)
nm=0; events=[]
while True:
    bp=br.pos
    sym=ti.decode_symbol(br,lit_t)
    if sym<256: out.append(sym); events.append((bp,f'lit {sym}'))
    elif sym==256: events.append((bp,'EOB 256')); break
    else:
        li=sym-257; length=ti.LBASE[li]+br.bits(ti.LEXT[li])
        dsym=ti.decode_symbol(br,dist_t)
        b=ti.DBASE_EBOOT[dsym]; dist=b+(br.bits(30-clz(b)) if b>=4 else 0)+1
        nm+=1; events.append((bp,f'match{nm} sym{sym} len{length} dsym{dsym} dist{dist} out={len(out)}'))
        if dist>len(out): out.extend(b'\x00'*length)
        else:
            for _ in range(length): out.append(out[-dist])
print('matches:', nm, 'out:', len(out), 'endbit:', br.pos, flush=True)
for e in events[-14:]: print(e, flush=True)
print('next 48 raw bits after EOB:', ''.join(str((data[br.pos>>3]>>(br.pos&7))&1) if False else ''), flush=True)
# dump bits from endbit-8 to endbit+64 as ints LSB-first per byte stream order
def bitat(p): return (data[p>>3]>>(p&7))&1
s=''.join(str(bitat(p)) for p in range(br.pos-4, br.pos+64))
print('bits[endbit-4 .. endbit+64]:', s, flush=True)
print('DONE')
