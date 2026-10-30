import sys, struct, re, math, json
sys.path.insert(0, '/home/user/western-heart/tools/anim')
from t7_anim64 import Anim64, mota_anims, is_short
ARC = '/home/user/game-reverse-engineering/teardown/tekken7-steam/tkdata/mothead/mask/kinrotsm.arc'
d = open(ARC, 'rb').read()
def c8(d, o):
    le = d[o] != 0; e = '<' if le else '>'
    typ, nb = struct.unpack_from(e+'HH', d, o); n = struct.unpack_from(e+'I', d, o+4)[0]
    desc = struct.unpack_from(e+'%dI' % nb, d, o+8)
    p = o + 8 + 4*nb
    fr = [struct.unpack_from(e+'%df' % (3*nb), d, p + 12*nb*i) for i in range(n)]
    return desc, fr
C8, A64 = [], []
for m in re.finditer(b'MOTA', d):
    M = m.start()
    try: offs = sorted(set(mota_anims(d, M)))
    except Exception: continue
    for o in offs:
        t = d[M+o+1] if d[M+o] == 0 else d[M+o]
        try:
            if t == 0xC8: C8.append((M, o) + c8(d, M+o))
            elif t == 0x64:
                a = Anim64(d, M+o); A64.append((M, o, a.desc, a.frames()))
        except Exception as ex: pass
print('C8 clips', len(C8), 'A64 clips', len(A64))
print('C8 desc sample', C8[0][2][:23] if C8 else None)
print('64 desc sample', A64[0][2][:23])
from collections import Counter
print('C8 bonecounts', Counter(len(c[2]) for c in C8)); print('64 bonecounts', Counter(len(a[2]) for a in A64))
def stats(clips, first_only=False):
    out = []
    for ch in range(69):
        vals = []
        for c in clips:
            frs = c[3][:1] if first_only else c[3]
            for f in frs:
                v = f[ch//3][ch%3] if isinstance(f[0], list) else f[ch]
                vals.append(v)
        vals.sort(); n=len(vals)
        out.append((vals[n//20], vals[n//2], vals[n*19//20]))
    return out
C8=[c for c in C8 if len(c[2])==23]; A64=[a for a in A64 if len(a[2])>=23 and tuple(a[2][:23])==tuple(C8[0][2][:23])]
print('23-bone', len(C8), len(A64))
sc, s6 = stats(C8), stats(A64)
names = ['mvX','mvY','mvZ','posX','posY','posZ','f6','f7','f8','rotX','rotY','rotZ','sp1X','sp1Y','sp1Z','hipX','hipY','hipZ','sp2a','sp2b','sp2c','nk21','nk22','nk23','hd24','hd25','hd26','RiS27','RiS28','RiS29','RoS30','RoS31','RoS32','REl33','REl34','REl35','RHd36','RHd37','RHd38','LiS39','LiS40','LiS41','LoS42','LoS43','LoS44','LEl45','LEl46','LEl47','LHd48','LHd49','LHd50','RUL51','RUL52','RUL53','RLg54','RLg55','RLg56','RFt57','RFt58','RFt59','LUL60','LUL61','LUL62','LLg63','LLg64','LLg65','LFt66','LFt67','LFt68']
for ch in range(69):
    a, b = sc[ch], s6[ch]
    print('%3d %-6s C8 p5/50/95 %9.2f %9.2f %9.2f | 64 %9.2f %9.2f %9.2f' % (ch, names[ch], *a, *b))
