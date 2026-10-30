"""Stick-figure renders of T7 0x64 frames on King's own T7 skeleton under a channel convention.
python3 render.py <out.png> <perm e.g. 021> <signs e.g. ++-> <order e.g. 012> <mode bind*R|R*bind> <clip-spec>...
clip-spec: common:185:1  (bank file, clip index, 1-based frame)  or  kin:<clip>:<frame>"""
import sys, re, struct
sys.path.insert(0, '/home/user/western-heart/tools/anim')
sys.path.insert(0, '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe')
from t7_anim64 import Anim64, mota_anims
from fk import SK, ORDER, BIND, T, BONE_SLOT, Rx, Ry, Rz
import numpy as np
from PIL import Image, ImageDraw

FILES = {'common': '/home/user/game-reverse-engineering/teardown/tekken7-steam/tkdata/mothead/mask/common.arc',
         'kin': '/home/user/game-reverse-engineering/teardown/tekken7-steam/tkdata/mothead/mask/kinrotsm.arc'}
_cache = {}
def frame_of(spec):
    f, i, fr = spec.split(':'); i, fr = int(i), int(fr)
    if f not in _cache:
        d = open(FILES[f], 'rb').read(); m0 = re.search(b'MOTA', d).start(); _cache[f] = (d, m0, mota_anims(d, m0))
    d, m0, offs = _cache[f]
    a = Anim64(d, m0 + offs[i])
    return sum((b for b in a.frame(fr)[:23]), [])

AXF = (Rx, Ry, Rz)
def rot(order, perm, signs, e):
    m = np.eye(3)
    for k in order: m = AXF[perm[k]](signs[k] * e[k]) @ m
    return m

def fk(frame, perm, signs, order, mode, use_base=False):
    W = {}
    for b in ORDER:
        p = SK[b]['parent']; Rl = BIND[b]
        if b in BONE_SLOT and (use_base or b != 'BASE'):
            s = BONE_SLOT[b]; Re = rot(order, perm, signs, frame[3*s:3*s+3])
            Rl = BIND[b] @ Re if mode == 'bind*R' else Re @ BIND[b]
        if p in W: PR, PP = W[p]; W[b] = (PR @ Rl, PP + PR @ T[b])
        else: W[b] = (Rl, T[b].copy())
    return {b: W[b][1] for b in W}

LINKS = [('BASE','Spine1'),('Spine1','Spine2'),('Spine2','Neck'),('Neck','Head'),('Spine2','R_Shoulder'),('R_Shoulder','R_Arm'),
         ('R_Arm','R_ForeArm'),('R_ForeArm','R_Hand'),('Spine2','L_Shoulder'),('L_Shoulder','L_Arm'),('L_Arm','L_ForeArm'),
         ('L_ForeArm','L_Hand'),('BASE','Hip'),('Hip','R_UpLeg'),('R_UpLeg','R_Leg'),('R_Leg','R_Foot'),('Hip','L_UpLeg'),
         ('L_UpLeg','L_Leg'),('L_Leg','L_Foot')]
def color(a, b):
    if a.startswith('R_') or b.startswith('R_'): return (220, 40, 40)
    if a.startswith('L_') or b.startswith('L_'): return (40, 90, 230)
    return (30, 30, 30)

def draw(pos, img, ox, oy, view, scale=150):
    d = ImageDraw.Draw(img)
    def P(v):
        x = v[0] if view == 'front' else v[2]   # front: world X; side: world Z (King faces +Z -> right)
        return (ox + x*scale, oy - v[1]*scale)
    d.line([(ox-110, oy), (ox+110, oy)], fill=(160, 160, 160))
    for a, b in LINKS: d.line([P(pos[a]), P(pos[b])], fill=color(a, b), width=4)
    hx, hy = P(pos['Head']); d.ellipse([hx-9, hy-9, hx+9, hy+9], outline=(0,0,0), width=2)

if __name__ == '__main__':
    out, perm, signs, order, mode = sys.argv[1:6]
    perm = tuple(int(c) for c in perm); order = tuple(int(c) for c in order)
    signs = tuple(1 if c == '+' else -1 for c in signs)
    specs = sys.argv[6:]
    img = Image.new('RGB', (240*len(specs), 360), 'white'); d = ImageDraw.Draw(img)
    for k, sp in enumerate(specs):
        pos = fk(frame_of(sp), perm, signs, order, mode)
        draw(pos, img, 240*k + 120, 330, 'front' if k % 2 == 0 else 'side')
        d.text((240*k + 6, 6), sp + (' front' if k % 2 == 0 else ' side'), fill=(0, 0, 0))
    d.text((6, 345), 'perm %s signs %s order %s %s' % (perm, signs, order, mode), fill=(0, 0, 0))
    img.save(out)
