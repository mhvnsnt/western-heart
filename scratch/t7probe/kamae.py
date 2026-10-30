import sys, re, struct, json
sys.path.insert(0, '/home/user/western-heart/tools/anim')
from t7_anim64 import Anim64, mota_anims
G = '/home/user/game-reverse-engineering/teardown/tekken7-steam/tkdata/mothead/mask/common.arc'
d = open(G, 'rb').read(); m0 = re.search(b'MOTA', d).start(); offs = mota_anims(d, m0)
def clip(i):
    o = m0 + offs[i]; t = d[o+1] if d[o] == 0 else d[o]
    if t == 0x64:
        a = Anim64(d, o); return '64', [sum((b for b in f[:23]), []) for f in a.frames()]
    e = '<' if d[o] != 0 else '>'
    nb = struct.unpack_from(e+'H', d, o+2)[0]; n = struct.unpack_from(e+'I', d, o+4)[0]; p = o + 8 + 4*nb
    return 'C8', [list(struct.unpack_from(e+'%df' % (3*nb), d, p + 12*nb*k))[:69] for k in range(n)]
names = ['mvX','mvY','mvZ','posX','posY','posZ','b2x','b2y','b2z','rotX','rotY','rotZ','sp1X','sp1Y','sp1Z','hipX','hipY','hipZ','b6a','b6b','b6c','nkX','nkY','nkZ','hdX','hdY','hdZ','RiSx','RiSy','RiSz','RoSx','RoSy','RoSz','RElx','REly','RElz','RHdx','RHdy','RHdz','LiSx','LiSy','LiSz','LoSx','LoSy','LoSz','LElx','LEly','LElz','LHdx','LHdy','LHdz','RULx','RULy','RULz','RLgx','RLgy','RLgz','RFtx','RFty','RFtz','LULx','LULy','LULz','LLgx','LLgy','LLgz','LFtx','LFty','LFtz']
k = clip(185)   # kopl_kamae (0x64 stance)
c1 = clip(75)   # round2 1p m1_01 (C8)
c2 = clip(79)   # round2 2p m1_01 (C8)
print(k[0], len(k[1]), c1[0], len(c1[1]), c2[0], len(c2[1]))
print('ch  name     kamae64[f1]  kamae64[f35]   C8-1p[last]  C8-2p[last]  C8-1p[first]')
for ch in range(69):
    print('%2d %-6s %11.3f %12.3f %13.3f %12.3f %12.3f' % (ch, names[ch], k[1][0][ch], k[1][34][ch], c1[1][-1][ch], c2[1][-1][ch], c1[1][0][ch]))
