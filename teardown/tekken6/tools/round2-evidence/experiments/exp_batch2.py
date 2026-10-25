import json, struct, sys, zlib
sys.path.insert(0,'/home/hatch/workspace/_t6lane')
import t6inflate2 as ti
# Patch decode_dynamic repeat semantics: 19 -> (3 bits, base 3); 27 -> (7 bits, base 11)
src_lens = None
def decode_dynamic_fixed(br, hlit_n, hdist_n):
    hclen = br.bits(4)
    cl_lens = [0]*28
    ORDER=[16,19,27,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]
    for i in range(hclen+4):
        cl_lens[ORDER[i]] = br.bits(3)
    cl_table = ti.build_huffman(cl_lens)
    total = hlit_n + hdist_n
    lens = []
    while len(lens) < total:
        sym = ti.decode_symbol(br, cl_table)
        if sym <= 15: lens.append(sym)
        elif sym == 16:
            rep = 3 + br.bits(2); prev = lens[-1] if lens else 0
            lens.extend([prev]*rep)
        elif sym == 19:
            rep = 3 + br.bits(3); lens.extend([0]*rep)
        elif sym == 27:
            rep = 11 + br.bits(7); lens.extend([0]*rep)
        else: raise ValueError(f'unexpected repeat symbol {sym}')
    return lens[:hlit_n], lens[hlit_n:hlit_n+hdist_n]
ti.decode_dynamic = decode_dynamic_fixed

W='/home/hatch/workspace/_t6lane/restore/tekken6/work/'
m=json.load(open(W+'decrypt3/manifest.json'))
files=m['files']
bulk=open(W+'decrypt3/bulk_decrypted.bin','rb')
def readdata(f):
    bulk.seek(f['start_rel']*2048); return bulk.read(f['size'])
gz=[f for f in files if f['magic'].startswith('GZIP')]
exact=[]; partial=[]; fail=[]
import os
os.makedirs('/home/hatch/workspace/_t6lane/decoded', exist_ok=True)
for idx,t in enumerate(gz):
    fd=readdata(t)
    if t['magic']=='GZIP+prefix16': fd=fd[16:]
    w=struct.unpack('<5I', fd[:20]); body=fd[20:]
    try:
        out, stats = ti.decompress(body[2:], zero_dict_fallback=False)
        if len(out)==w[3]:
            # adler check: trailer after stream end
            bytepos=(stats['bits_used']+7)//8
            trailer=body[2+bytepos:2+bytepos+4]
            adler_ok = len(trailer)==4 and struct.unpack('>I',trailer)[0]==zlib.adler32(out)
            exact.append((idx, t['entry'], len(out), adler_ok, stats['blocks']))
            open(f'/home/hatch/workspace/_t6lane/decoded/file_{idx:02d}.bin','wb').write(out)
        else:
            partial.append((idx, t['entry'], w[3], len(out), stats['dist_violations'], stats['blocks']))
    except Exception as e:
        fail.append((idx, t['entry'], w[3], f'{type(e).__name__}: {e}'[:60]))
print(f'EXACT={len(exact)} PARTIAL={len(partial)} FAIL={len(fail)}', flush=True)
for r in exact: print('EXACT', r, flush=True)
for r in partial: print('PART', r, flush=True)
for r in fail: print('FAIL', r, flush=True)
print('DONE')
