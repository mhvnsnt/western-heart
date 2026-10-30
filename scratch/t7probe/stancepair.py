import sys, json, re, struct, statistics as st
sys.path.insert(0, '/home/user/western-heart/tools/anim')
from t7_anim64 import Anim64, mota_anims
P = '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe/'
ARC = '/home/user/game-reverse-engineering/teardown/tekken7-steam/tkdata/mothead/mask/kinrotsm.arc'
d = open(ARC, 'rb').read(); m0 = re.search(b'MOTA', d).start(); offs = mota_anims(d, m0)
def clip(i):
    o = m0 + offs[i]; t = d[o+1] if d[o] == 0 else d[o]
    if t == 0x64:
        a = Anim64(d, o); return '64', a.nb, [sum((b for b in f[:23]), []) for f in a.frames()]
    e = '<' if d[o] != 0 else '>'
    nb = struct.unpack_from(e+'H', d, o+2)[0]; n = struct.unpack_from(e+'I', d, o+4)[0]; p = o + 8 + 4*nb
    return 'C8', nb, [list(struct.unpack_from(e+'%df' % (3*nb), d, p + 12*nb*k))[:69] for k in range(n)]
king = json.load(open(P + 'kin_clipmap.json'))['moves']
stance = clip(132)
print('stance', stance[0], stance[1], len(stance[2]))
# attacks from the standing kamae: King's basic strikes (rotsm, 0x64), first frames
atk = [m for m in king if m['damage'] and m['bank'] == 'rotsm' and m.get('fmt') == '0x64']
names = {}
firsts = []
for m in atk:
    c = clip(m['clip'])
    if c[1] != 23: continue
    firsts.append((m['move'], c[2][0]))
print('0x64 attack first frames:', len(firsts))
lab = ['mvX','mvY','mvZ','posX','posY','posZ','b2x','b2y','b2z','rotX','rotY','rotZ','sp1X','sp1Y','sp1Z','hipX','hipY','hipZ','b6a','b6b','b6c','nkX','nkY','nkZ','hdX','hdY','hdZ','RiSx','RiSy','RiSz','RoSx','RoSy','RoSz','RElx','REly','RElz','RHdx','RHdy','RHdz','LiSx','LiSy','LiSz','LoSx','LoSy','LoSz','LElx','LEly','LElz','LHdx','LHdy','LHdz','RULx','RULy','RULz','RLgx','RLgy','RLgz','RFtx','RFty','RFtz','LULx','LULy','LULz','LLgx','LLgy','LLgz','LFtx','LFty','LFtz']
print('ch name   C8stance[f1]  C8stance[f30] | 64 attack-f1 median  (IQR)')
out = []
for ch in range(69):
    vals = sorted(f[ch] for _, f in firsts)
    q1, med, q3 = vals[len(vals)//4], vals[len(vals)//2], vals[3*len(vals)//4]
    out.append((ch, stance[2][0][ch], med))
    print('%2d %-5s %10.3f %10.3f   | %8.3f  (%6.3f..%6.3f)' % (ch, lab[ch], stance[2][0][ch], stance[2][29][ch], med, q1, q3))
json.dump({'stance_c8_f1': stance[2][0], 'atk64_first_median': [o[2] for o in out], 'n_attacks': len(firsts)}, open(P + 'stancepair.json', 'w'))
