import struct, collections, math, hashlib
d=open('/home/hatch/workspace/_doa4p2-scratch/p7/data/anm.afs','rb').read()
H=d[:0x6B000]; n=len(H)//16
recs=[struct.unpack_from('>8h',H,i*16) for i in range(n)]
for ch in range(8):
    vals=[r[ch] for r in recs]
    grid=sum(1 for v in vals if (v+1)%32==0)/n
    grid0=sum(1 for v in vals if v%32==0)/n
    dif=[abs(vals[i+1]-vals[i]) for i in range(n-1)]
    print(f'ch{ch}: min={min(vals)} max={max(vals)} mean={sum(vals)/n:.0f} grid(v+1)%32={grid:.3f} grid v%32={grid0:.3f} mean|step|={sum(dif)/len(dif):.0f} step0%={sum(1 for x in dif if x==0)/len(dif):.3f}')
# quaternion norm tests for channel quadruples (Q15 scale)
def normstats(idxs):
    ns=[]
    for r in recs[::37]:
        s=sum((r[i]/32768.0)**2 for i in idxs); ns.append(s)
    ns.sort(); print(f'norm2 {idxs}: median={ns[len(ns)//2]:.3f} p10={ns[len(ns)//10]:.3f} p90={ns[9*len(ns)//10]:.3f}')
for q in [(0,1,2,3),(1,2,3,4),(2,3,4,5),(3,4,5,6),(4,5,6,7),(0,1,2,7),(4,5,6,6)]:
    normstats(q)
# ch6 vs ch7 equality / diff distribution
eq=sum(1 for r in recs if r[6]==r[7])/n; close=sum(1 for r in recs if abs(r[6]-r[7])<=64)/n
print(f'ch6==ch7: {eq:.3f}  |diff|<=64: {close:.3f}')
# segment structure: where do records change abruptly? (candidate clip boundaries: large total step)
steps=[]
for i in range(n-1):
    steps.append(sum(abs(recs[i+1][c]-recs[i][c]) for c in range(8)))
big=[i for i,s in enumerate(steps) if s>20000]
print('abrupt boundaries (total step>20000):',len(big),'first 40:',big[:40])
import statistics; print('median total step:',statistics.median(steps))
# round-trip proof: parse -> int16 array -> reserialize
raw=b''.join(struct.pack('>8h',*r) for r in recs)
print('ROUNDTRIP byte-exact:', raw==H, 'sha256 orig:', hashlib.sha256(H).hexdigest()[:16], 'reser:', hashlib.sha256(raw).hexdigest()[:16])
