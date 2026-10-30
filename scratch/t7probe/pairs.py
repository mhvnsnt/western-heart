import sys, struct, re, math, pickle
sys.path.insert(0, '/home/user/western-heart/tools/anim')
from t7_anim64 import Anim64, mota_anims
ARC = sys.argv[1]
d = open(ARC, 'rb').read()
def c8(d, o):
    e = '<' if d[o] != 0 else '>'
    typ, nb = struct.unpack_from(e+'HH', d, o); n = struct.unpack_from(e+'I', d, o+4)[0]
    desc = struct.unpack_from(e+'%dI' % nb, d, o+8); p = o + 8 + 4*nb
    return desc, [struct.unpack_from(e+'%df' % (3*nb), d, p + 12*nb*i) for i in range(n)]
C8, A64 = [], []
for m in re.finditer(b'MOTA', d):
    M = m.start()
    try: offs = mota_anims(d, M)
    except Exception: continue
    for idx, o in enumerate(offs):
        t = d[M+o+1] if d[M+o] == 0 else d[M+o]
        try:
            if t == 0xC8:
                desc, fr = c8(d, M+o)
                if len(desc) == 23: C8.append(dict(M=M, i=idx, fr=[list(f) for f in fr]))
            elif t == 0x64:
                a = Anim64(d, M+o)
                if a.nb >= 23: A64.append(dict(M=M, i=idx, fr=[sum((b for b in f[:23]), []) for f in a.frames()]))
        except Exception: pass
pickle.dump((C8, A64), open(sys.argv[2], 'wb'))
print(len(C8), len(A64))
from collections import Counter
print('C8 lengths', sorted(Counter(len(c['fr']) for c in C8).items())[:40])
L64 = Counter(len(a['fr']) for a in A64)
both = [L for L in set(len(c['fr']) for c in C8) if L in L64]
print('lengths in both:', sorted(both)[:60])
# height curve match
res = []
for c in C8:
    h1 = [f[4] for f in c['fr']]
    for a in A64:
        if len(a['fr']) != len(c['fr']): continue
        h2 = [f[4] for f in a['fr']]
        rms = math.sqrt(sum((x-y)**2 for x, y in zip(h1, h2)) / len(h1))
        res.append((rms, c['M'], c['i'], a['M'], a['i'], len(h1)))
res.sort()
for r in res[:15]: print('rms %.1f  C8 M%d#%d  64 M%d#%d  len %d' % r)
