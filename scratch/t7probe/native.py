"""Native-frame FK hypothesis for T7 0x64 (Tekken-3-style): local = Euler(anim) and a fixed joint offset
along the parent bone's X (lengths from King's own T7 skeleton). Native world: X = fight axis, Y = up, Z = side.
python3 native.py <out.png> <order e.g. 012> <signs e.g. ++-> <side +|-> <clip-spec>..."""
import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe')
from render import frame_of
from fk import Rx, Ry, Rz
import numpy as np
from PIL import Image, ImageDraw

PARENT = {'BASE': None, 'Spine1': 'BASE', 'Spine2': 'Spine1', 'Neck': 'Spine2', 'Head': 'Neck',
          'R_Shoulder': 'Spine2', 'R_Arm': 'R_Shoulder', 'R_ForeArm': 'R_Arm', 'R_Hand': 'R_ForeArm',
          'L_Shoulder': 'Spine2', 'L_Arm': 'L_Shoulder', 'L_ForeArm': 'L_Arm', 'L_Hand': 'L_ForeArm',
          'Hip': 'BASE', 'R_UpLeg': 'Hip', 'R_Leg': 'R_UpLeg', 'R_Foot': 'R_Leg',
          'L_UpLeg': 'Hip', 'L_Leg': 'L_UpLeg', 'L_Foot': 'L_Leg'}
LEN = {'Spine2': 0.158, 'Neck': 0.317, 'Head': 0.174, 'R_Arm': 0.137, 'R_ForeArm': 0.336, 'R_Hand': 0.258,
       'L_Arm': 0.137, 'L_ForeArm': 0.336, 'L_Hand': 0.258, 'R_Leg': 0.466, 'R_Foot': 0.445, 'L_Leg': 0.466, 'L_Foot': 0.445}
SLOT = {'BASE': 3, 'Spine1': 4, 'Hip': 5, 'Neck': 7, 'Head': 8, 'R_Shoulder': 9, 'R_Arm': 10, 'R_ForeArm': 11,
        'R_Hand': 12, 'L_Shoulder': 13, 'L_Arm': 14, 'L_ForeArm': 15, 'L_Hand': 16, 'R_UpLeg': 17, 'R_Leg': 18,
        'R_Foot': 19, 'L_UpLeg': 20, 'L_Leg': 21, 'L_Foot': 22}
ORDER = list(PARENT)
AXF = (Rx, Ry, Rz)

def offset(b, side):
    if b in LEN: return np.array([LEN[b], 0, 0])
    s = side if b.startswith('R_') else -side
    if b in ('R_Shoulder', 'L_Shoulder'): return np.array([0.268, 0, s * 0.122])
    if b in ('R_UpLeg', 'L_UpLeg'): return np.array([0.17, 0, s * 0.106])
    return np.zeros(3)

def euler(order, signs, e):
    m = np.eye(3)
    for k in order: m = AXF[k](signs[k] * e[k]) @ m
    return m

def fk(frame, order, signs, side, base=True):
    W = {}
    for b in ORDER:
        s = SLOT.get(b)
        R = euler(order, signs, frame[3*s:3*s+3]) if (s is not None and (base or b != 'BASE')) else np.eye(3)
        p = PARENT[b]
        if p is None: W[b] = (R, np.array([0, frame[4] / 1000.0, 0]))
        else:
            PR, PP = W[p]; W[b] = (PR @ R, PP + PR @ offset(b, side))
    return {b: W[b][1] for b in W}

LINKS = [(PARENT[b], b) for b in ORDER if PARENT[b]]
def col(a, b):
    return (220, 40, 40) if 'R_' in a + b else (40, 90, 230) if 'L_' in a + b else (30, 30, 30)

def draw(pos, img, ox, oy, view, scale=120):
    d = ImageDraw.Draw(img)
    def P(v):
        h = v[0] if view == 'sagittal' else v[2]
        return (ox + h * scale, oy - v[1] * scale)
    d.line([(ox - 100, oy), (ox + 100, oy)], fill=(170, 170, 170))
    for a, b in LINKS: d.line([P(pos[a]), P(pos[b])], fill=col(a, b), width=4)
    hx, hy = P(pos['Head']); d.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], outline=(0, 0, 0), width=2)

if __name__ == '__main__':
    out, order, signs, side = sys.argv[1:5]
    order = tuple(int(c) for c in order); signs = tuple(1 if c == '+' else -1 for c in signs); side = 1 if side == '+' else -1
    specs = sys.argv[5:]
    img = Image.new('RGB', (220 * 2 * len(specs), 300), 'white'); d = ImageDraw.Draw(img)
    for k, sp in enumerate(specs):
        pos = fk(frame_of(sp), order, signs, side)
        for j, view in enumerate(('sagittal', 'frontal')):
            draw(pos, img, 220 * (2 * k + j) + 110, 280, view)
            d.text((220 * (2 * k + j) + 4, 4), '%s %s' % (sp, view), fill=(0, 0, 0))
    d.text((4, 288), 'order %s signs %s side %s' % (order, signs, side), fill=(0, 0, 0))
    img.save(out)
