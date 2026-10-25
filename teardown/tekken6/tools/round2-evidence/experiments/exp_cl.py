import json, struct, sys
sys.path.insert(0,'/home/hatch/workspace/_t6lane')
import t6inflate2 as ti
W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
ORDER=[16,19,27,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]

def cl_decode(data, sem19, sem27, want_total):
    br=ti.BitReader(data)
    bfinal=br.bits(1); btype=br.bits(2)
    hlit=br.bits(5); hdist=br.bits(5); hclen=br.bits(4)
    cl_lens=[0]*28
    for i in range(hclen+4): cl_lens[ORDER[i]]=br.bits(3)
    cl_table=ti.build_huffman(cl_lens)
    total=(hlit+257)+(hdist+1)
    lens=[]; steps=[]
    while len(lens)<total:
        bp=br.pos
        sym=ti.decode_symbol(br, cl_table)
        if sym<=15: lens.append(sym); steps.append((bp,sym))
        elif sym==16:
            rep=3+br.bits(2); prev=lens[-1] if lens else 0
            lens.extend([prev]*rep); steps.append((bp,f'16x{rep}'))
        elif sym==19:
            bits,base=sem19; rep=base+br.bits(bits); lens.extend([0]*rep); steps.append((bp,f'19x{rep}'))
        elif sym==27:
            bits,base=sem27; rep=base+br.bits(bits); lens.extend([0]*rep); steps.append((bp,f'27x{rep}'))
        else: return None, steps, f'bad sym {sym}'
        if len(lens)>total+2000: return None, steps, 'runaway'
    return lens, steps, (hlit+257, hdist+1, br.pos)

target=gz[3]
fdata=readdata(target)
w=struct.unpack('<5I', fdata[:20]); body=fdata[20:]
data=body[2:]
# current semantics
lens, steps, info = cl_decode(data, (10,3), (18,11), 315)
print('CURRENT sem: info=', info, 'steps with 19/27:', [s for s in steps if isinstance(s[1],str) and s[1][0] in '12'], flush=True)
# standard-like semantics
lens2, steps2, info2 = cl_decode(data, (3,3), (7,11), 315)
print('STD-LIKE sem: info=', info2, flush=True)
if lens2:
    ll=lens2[:info2[0]]; dl=lens2[info2[0]:info2[0]+info2[1]]
    def kraft(l): return sum(2**-x for x in l if x)
    print(f'  lit kraft={kraft(ll):.5f} dist kraft={kraft(dl):.5f} dist_lens={dl}', flush=True)
    print('  steps with 19/27:', [s for s in steps2 if isinstance(s[1],str) and s[1][0] in '12'], flush=True)
# also scan ALL 76: which files' CL headers contain 19/27 under current sem?
print('--- CL 19/27 usage across all 76 (current sem)', flush=True)
for idx,t in enumerate(gz):
    fd=readdata(t)
    if t['magic']=='GZIP+prefix16': fd=fd[16:]
    b=fd[20:]; d=b[2:]
    try:
        lens, steps, info = cl_decode(d, (10,3), (18,11), 0)
        used=[s for s in steps if isinstance(s[1],str) and (s[1].startswith('19') or s[1].startswith('27'))]
        print(f'idx{idx}: total_lens={len(lens) if lens else None} hdr_info={info} cl_repeats={used}', flush=True)
    except Exception as e:
        print(f'idx{idx}: EXC {type(e).__name__} {e}', flush=True)
print('DONE')
