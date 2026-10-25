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
W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
def kraft(l): return sum(2**-x for x in l if x)
for idx, eob in ((59, 9374), (58, 29125)):
    t=gz[idx]; fd=readdata(t)
    data=fd[20:][2:]
    print(f'=== idx{idx} EOB at {eob}', flush=True)
    for k in range(-20, 21):
        br=ti.BitReader(data); br.pos=eob+k
        try:
            bfinal=br.bits(1); btype=br.bits(2)
            if btype!=2: continue
            hlit=br.bits(5); hdist=br.bits(5)
            ll,dl=decode_dynamic_fixed(br,hlit+257,hdist+1)
            kl, kd = kraft(ll), kraft(dl)
            print(f' k={k:+d} bfinal={bfinal} hlit={hlit+257} hdist={hdist+1} kraftL={kl:.5f} kraftD={kd:.5f} hdrend={br.pos}', flush=True)
        except Exception as e:
            pass
print('DONE')
