"""tools/souls/specs.py — the Nine Souls' Eastern Mind designs as primitive specs for tools/souls/build_soul.py.

Each soul is measured off its own full-body art in teardown/eastern-mind/prologue-ending/bitmaps/CHARA/ (pixel
positions converted at the scale noted per soul, feet at z = 0) and re-posed into the game's T-pose. Blender Z-up,
the soul faces -Y, its left is +X. Colours are linear RGB read off the art. Every part names the ONE bone it rides.
"""
import math

M = lambda x: x  # noqa: E731  (metres; kept for readability)


def _mirror(fn):
    """Call fn(side, sx) for the left (+X) and right (-X) sides."""
    out = []
    for side, sx in (('Left', 1.0), ('Right', -1.0)):
        out += fn(side, sx)
    return out


def kai():
    """KAI 海 (the sea). CHARA_b006 (286 x 463 px; 1 px = 4.1 mm, feet at y = 460 px) + R_KAI head studies.
    A red egg head crowned with long red spikes, a blue mask with gold ornaments down the face and two disc eyes, a blue
    neck, a chest of red spheres with gold spirals, a red pelvis with two red bulbs, thin blue limbs, red feet."""
    H = dict(hips=0.44, spine=0.53, spine1=0.62, spine2=0.72, neck=0.86, head=1.02, top=1.80,
             sh=0.77, hipj=0.37, knee=0.21, ankle=0.06)
    bones = [
        ('Hips', (0, 0, H['hips']), (0, 0, H['spine']), None),
        ('Spine', (0, 0, H['spine']), (0, 0, H['spine1']), 'Hips'),
        ('Spine1', (0, 0, H['spine1']), (0, 0, H['spine2']), 'Spine'),
        ('Spine2', (0, 0, H['spine2']), (0, 0, H['neck'] - 0.02), 'Spine1'),
        ('Neck', (0, 0, H['neck']), (0, 0, H['head']), 'Spine2'),
        ('Head', (0, 0, H['head']), (0, 0, H['top']), 'Neck'),
    ]
    for side, sx in (('Left', 1.0), ('Right', -1.0)):
        bones += [
            (side + 'Shoulder', (sx * 0.06, 0, 0.80), (sx * 0.29, 0, H['sh']), 'Spine2'),
            (side + 'Arm', (sx * 0.29, 0, H['sh']), (sx * 0.51, 0, H['sh']), side + 'Shoulder'),
            (side + 'ForeArm', (sx * 0.51, 0, H['sh']), (sx * 0.71, 0, H['sh']), side + 'Arm'),
            (side + 'Hand', (sx * 0.71, 0, H['sh']), (sx * 0.81, 0, H['sh']), side + 'ForeArm'),
            (side + 'UpLeg', (sx * 0.075, 0, H['hipj']), (sx * 0.08, 0, H['knee']), 'Hips'),
            (side + 'Leg', (sx * 0.08, 0, H['knee']), (sx * 0.085, 0, H['ankle']), side + 'UpLeg'),
            (side + 'Foot', (sx * 0.085, 0, H['ankle']), (sx * 0.09, -0.08, 0.02), side + 'Leg'),
            (side + 'ToeBase', (sx * 0.09, -0.08, 0.02), (sx * 0.09, -0.15, 0.02), side + 'Foot'),
        ]

    def parts(api):
        mat = api['material']
        red = mat('kai_red', (0.62, 0.025, 0.035), rough=0.28)
        blue = mat('kai_blue', (0.04, 0.16, 0.72), rough=0.3)
        gold = mat('kai_gold', (0.86, 0.55, 0.10), rough=0.25, metal=0.75)
        teal = mat('kai_eye_teal', (0.10, 0.48, 0.52), rough=0.2)
        pupil = mat('kai_eye_pupil', (0.02, 0.05, 0.26), rough=0.15)
        P = []
        E, T, D, C, X, B = api['ellipsoid'], api['tube'], api['disc'], api['cone'], api['torus'], api['box']
        # head: the red egg (px y 20..210 -> 1.02..1.80 m, half-width 45 px -> 0.185 m)
        hc = (0, 0, 1.41)
        P.append(E(hc, (0.20, 0.17, 0.40), red, 'Head', seg=48, rings=32))
        # spikes radiating from the upper head, in the frontal plane and two backward (lengths off the art)
        # (the art's spikes are long and thin and reach far out sideways: span ~2.5x the head's width)
        for ang, L in ((-100, 0.58), (-80, 0.62), (-60, 0.56), (-40, 0.48), (-20, 0.42), (0, 0.40), (20, 0.42),
                       (40, 0.48), (60, 0.56), (80, 0.62), (100, 0.58)):
            a = math.radians(ang)
            dx, dz = math.sin(a), math.cos(a)
            base = (hc[0] + 0.19 * dx, 0.02, hc[2] + 0.38 * dz)
            tip = (base[0] + L * dx, 0.05, base[2] + L * dz * 0.8)
            P.append(C(base, tip, 0.02, red, 'Head'))
        for sx in (-1, 1):
            base = (sx * 0.08, 0.13, 1.66)
            P.append(C(base, (sx * 0.22, 0.42, 1.92), 0.024, red, 'Head'))
        # the blue mask down the face (px y 60..230 -> 1.03..1.64 m)
        P.append(E((0, -0.135, 1.34), (0.055, 0.04, 0.31), blue, 'Head'))
        P.append(E((0, -0.16, 1.58), (0.022, 0.012, 0.045), gold, 'Head'))        # forehead jewel
        P.append(C((0, -0.17, 1.40), (0, -0.175, 1.30), 0.026, gold, 'Head'))     # the gold arrow emblem
        P.append(E((0, -0.172, 1.20), (0.03, 0.012, 0.022), gold, 'Head'))
        # disc eyes flanking the mask (px y 155 -> 1.25 m, x +-22 px -> +-0.09 m): teal ring, gold, pupil
        for sx in (-1, 1):
            c = (sx * 0.095, -0.15, 1.25)
            P.append(D(c, 0.052, 0.02, teal, 'Head', normal=(sx * 0.25, -1, 0)))
            P.append(D((c[0] + sx * 0.002, c[1] - 0.012, c[2]), 0.036, 0.02, gold, 'Head', normal=(sx * 0.25, -1, 0)))
            P.append(D((c[0] + sx * 0.004, c[1] - 0.022, c[2]), 0.018, 0.02, pupil, 'Head', normal=(sx * 0.25, -1, 0)))
        # blue chin + neck (px y 210..250 -> 0.86..1.03 m)
        P.append(E((0, -0.02, 1.04), (0.07, 0.06, 0.07), blue, 'Neck'))
        P.append(T((0, 0, 0.84), (0, 0, 1.03), 0.055, blue, 'Neck'))
        # the chest: red spheres with gold spirals (px y 250..330 -> 0.53..0.86 m, x +-55 px -> +-0.225 m)
        rows = (('Spine2', 0.79, (-0.21, -0.07, 0.07, 0.21), 0.085), ('Spine1', 0.665, (-0.235, -0.08, 0.08, 0.235), 0.09),
                ('Spine', 0.56, (-0.12, 0.0, 0.12), 0.075))
        for bone, z, xs, r in rows:
            for x in xs:
                y = 0.01 * (1 if abs(x) > 0.1 else -1)
                P.append(E((x, y, z), (r, r * 0.9, r), red, bone, seg=24, rings=16))
                P.append(D((x, y - r * 0.86, z), r * 0.62, 0.012, gold, bone))   # the gold spiral: rings
                P.append(D((x, y - r * 0.91, z), r * 0.42, 0.012, red, bone))
                P.append(D((x, y - r * 0.95, z), r * 0.22, 0.012, gold, bone))
        # pelvis + its two red bulbs (px y 330..370 -> 0.37..0.53 m)
        P.append(E((0, 0, 0.47), (0.12, 0.09, 0.075), red, 'Hips'))
        for sx in (-1, 1):
            P.append(E((sx * 0.09, -0.01, 0.40), (0.09, 0.085, 0.085), red, 'Hips'))

        def limbs(side, sx):
            q = []
            # arms: thin blue tubes, small blue hands (T-pose)
            q.append(E((sx * 0.29, 0, H['sh']), (0.035, 0.035, 0.035), blue, side + 'Shoulder'))
            q.append(T((sx * 0.29, 0, H['sh']), (sx * 0.51, 0, H['sh']), 0.027, blue, side + 'Arm', r1=0.024))
            q.append(E((sx * 0.51, 0, H['sh']), (0.027, 0.027, 0.027), blue, side + 'ForeArm'))
            q.append(T((sx * 0.51, 0, H['sh']), (sx * 0.71, 0, H['sh']), 0.024, blue, side + 'ForeArm', r1=0.02))
            q.append(E((sx * 0.75, 0, H['sh']), (0.045, 0.02, 0.035), blue, side + 'Hand'))
            for k, (dy, dz) in enumerate(((-0.02, 0.012), (-0.007, 0.006), (0.007, 0.0), (0.02, -0.006))):
                q.append(T((sx * 0.785, dy, H['sh'] + dz), (sx * 0.84, dy * 1.4, H['sh'] + dz - 0.01), 0.008, blue,
                           side + 'Hand'))
            q.append(T((sx * 0.75, -0.03, H['sh']), (sx * 0.78, -0.07, H['sh'] - 0.01), 0.009, blue, side + 'Hand'))
            # legs: blue, red feet
            q.append(T((sx * 0.075, 0, H['hipj']), (sx * 0.08, 0, H['knee']), 0.032, blue, side + 'UpLeg', r1=0.028))
            q.append(E((sx * 0.08, 0, H['knee']), (0.032, 0.032, 0.032), blue, side + 'Leg'))
            q.append(T((sx * 0.08, 0, H['knee']), (sx * 0.085, 0, H['ankle']), 0.028, blue, side + 'Leg', r1=0.024))
            q.append(E((sx * 0.088, -0.02, 0.04), (0.05, 0.065, 0.04), red, side + 'Foot'))
            q.append(E((sx * 0.09, -0.10, 0.03), (0.045, 0.06, 0.03), red, side + 'ToeBase'))
            return q
        P += _mirror(limbs)
        return P
    return {'name': 'KaiSoul', 'bones': bones, 'parts': parts, 'height': 1.95}


def tou():
    """TOU 闘 (battle). CHARA_b012 (478 x 428 px; 1 px = 4.6 mm) + R_TOH head studies, re-posed into a T-pose from the
    art's reaching pose. A teal head behind square glasses with red-iris eyes, a crown of knobbed stalks, an orange ring
    mouth between bulbous cheeks; a neck of beads; a big teal ring for a torso; long thin arms with knobbed elbows and
    huge five-fingered hands with bulb tips; short thin legs."""
    H = dict(hips=0.27, spine=0.40, spine1=0.55, spine2=0.72, neck=0.95, head=1.22, top=1.84, sh=0.86, knee=0.14,
             ankle=0.04)
    bones = [
        ('Hips', (0, 0, H['hips']), (0, 0, H['spine']), None),
        ('Spine', (0, 0, H['spine']), (0, 0, H['spine1']), 'Hips'),
        ('Spine1', (0, 0, H['spine1']), (0, 0, H['spine2']), 'Spine'),
        ('Spine2', (0, 0, H['spine2']), (0, 0, H['neck'] - 0.02), 'Spine1'),
        ('Neck', (0, 0, H['neck']), (0, 0, H['head']), 'Spine2'),
        ('Head', (0, 0, H['head']), (0, 0, H['top']), 'Neck'),
    ]
    for side, sx in (('Left', 1.0), ('Right', -1.0)):
        bones += [
            (side + 'Shoulder', (sx * 0.06, 0, 0.90), (sx * 0.25, 0, H['sh']), 'Spine2'),
            (side + 'Arm', (sx * 0.25, 0, H['sh']), (sx * 0.55, 0, H['sh']), side + 'Shoulder'),
            (side + 'ForeArm', (sx * 0.55, 0, H['sh']), (sx * 0.83, 0, H['sh']), side + 'Arm'),
            (side + 'Hand', (sx * 0.83, 0, H['sh']), (sx * 0.93, 0, H['sh']), side + 'ForeArm'),
            (side + 'UpLeg', (sx * 0.08, 0, H['hips']), (sx * 0.09, 0, H['knee']), 'Hips'),
            (side + 'Leg', (sx * 0.09, 0, H['knee']), (sx * 0.10, 0, H['ankle']), side + 'UpLeg'),
            (side + 'Foot', (sx * 0.10, 0, H['ankle']), (sx * 0.10, -0.06, 0.015), side + 'Leg'),
            (side + 'ToeBase', (sx * 0.10, -0.06, 0.015), (sx * 0.10, -0.11, 0.015), side + 'Foot'),
        ]

    def parts(api):
        mat = api['material']
        teal = mat('tou_teal', (0.07, 0.40, 0.31), rough=0.3)
        head_g = mat('tou_head_green', (0.10, 0.36, 0.24), rough=0.32)
        frame = mat('tou_glasses_frame', (0.30, 0.10, 0.62), rough=0.25, metal=0.3)
        white = mat('tou_eye_white', (0.95, 0.88, 0.70), rough=0.15)
        iris = mat('tou_eye_iris', (0.72, 0.04, 0.10), rough=0.2)
        pupil = mat('tou_eye_pupil', (0.04, 0.02, 0.08), rough=0.15)
        stalk = mat('tou_stalk', (0.38, 0.62, 0.08), rough=0.35)
        knob = mat('tou_knob', (0.80, 0.78, 0.12), rough=0.3)
        mouth = mat('tou_mouth', (0.90, 0.28, 0.04), rough=0.25)
        inside = mat('tou_mouth_in', (0.08, 0.01, 0.02), rough=0.6)
        gold = mat('tou_gold', (0.86, 0.60, 0.10), rough=0.25, metal=0.7)
        P = []
        E, T, D, C, X, B = api['ellipsoid'], api['tube'], api['disc'], api['cone'], api['torus'], api['box']
        # the ring torso, seen through from the front (outer diameter ~150 px -> 0.70 m)
        P.append(X((0, 0, 0.60), 0.29, 0.062, teal, 'Spine1', axis='Y', seg=64, mseg=20))
        # the bead neck from the ring top to the head (6 beads)
        for i, z in enumerate((0.965, 1.015, 1.065, 1.115, 1.165, 1.21)):
            bone = 'Spine2' if z < 0.99 else ('Neck' if z < 1.19 else 'Head')
            P.append(E(((-1) ** i * 0.008, 0, z), (0.034, 0.034, 0.03), teal, bone, seg=20, rings=12))
        # head: a wide rounded bulb with two cheek lobes below the glasses
        P.append(E((0, 0, 1.44), (0.25, 0.19, 0.18), head_g, 'Head', seg=48, rings=32))
        for sx in (-1, 1):
            P.append(E((sx * 0.125, -0.06, 1.31), (0.145, 0.14, 0.12), head_g, 'Head'))
        # square glasses (two frames + bridge) with big eyes behind them
        for sx in (-1, 1):
            cx, cy, cz, w, h, t = sx * 0.12, -0.2, 1.47, 0.205, 0.175, 0.018
            for (dx, dz, sw, sh) in ((0, h / 2, w, t), (0, -h / 2, w, t), (w / 2, 0, t, h), (-w / 2, 0, t, h)):
                P.append(B((cx + dx, cy, cz + dz), (sw, 0.022, sh), frame, 'Head'))
            P.append(E((cx, -0.165, cz), (0.082, 0.045, 0.078), white, 'Head'))
            P.append(D((cx, -0.206, cz), 0.046, 0.012, iris, 'Head'))
            P.append(D((cx, -0.212, cz), 0.02, 0.012, pupil, 'Head'))
        P.append(B((0, -0.2, 1.475), (0.04, 0.02, 0.018), frame, 'Head'))
        P.append(C((0, -0.19, 1.41), (0, -0.215, 1.35), 0.022, gold, 'Head'))           # yellow nose emblem
        # the open ring mouth between the cheeks
        P.append(X((0, -0.19, 1.26), 0.045, 0.016, mouth, 'Head', axis='Y'))
        P.append(D((0, -0.185, 1.26), 0.032, 0.01, inside, 'Head'))
        # the crown of knobbed stalks (5)
        for x, tx in ((-0.12, -0.17), (-0.06, -0.08), (0.0, 0.0), (0.06, 0.08), (0.12, 0.17)):
            base = (x, 0.0, 1.58 - abs(x) * 0.3)
            tip = (tx, 0.01, 1.86 - abs(x) * 0.25)
            P.append(T(base, tip, 0.012, stalk, 'Head', r1=0.009, seg=10))
            P.append(E(tip, (0.026, 0.026, 0.026), knob, 'Head', seg=16, rings=10))

        def limbs(side, sx):
            q = []
            # shoulder knob where the arm leaves the ring, long thin arm, knobbed elbow, huge hand
            q.append(E((sx * 0.25, 0, H['sh']), (0.045, 0.045, 0.045), teal, side + 'Shoulder'))
            q.append(T((sx * 0.25, 0, H['sh']), (sx * 0.55, 0, H['sh'] + 0.01), 0.021, teal, side + 'Arm', r1=0.019))
            q.append(E((sx * 0.55, 0, H['sh'] + 0.01), (0.048, 0.048, 0.048), teal, side + 'ForeArm'))
            q.append(T((sx * 0.55, 0, H['sh'] + 0.01), (sx * 0.83, 0, H['sh']), 0.019, teal, side + 'ForeArm', r1=0.017))
            pc = (sx * 0.895, 0, H['sh'])
            q.append(E(pc, (0.08, 0.065, 0.065), teal, side + 'Hand'))
            # five long wavy fingers fanned in the horizontal plane, bulb tips (the art's hands are huge: ~0.32 m fingers)
            for k, ang in enumerate((-56, -28, 0, 28, 56)):
                a = math.radians(ang)
                d = (sx * math.cos(a), -math.sin(a), 0.0)
                pts = []
                for j, t in enumerate((0.06, 0.15, 0.24, 0.33, 0.40)):
                    wave = 0.022 * math.sin(j * 1.7 + k)
                    pts.append((pc[0] + d[0] * t, pc[1] + d[1] * t, pc[2] + wave))
                for j in range(len(pts) - 1):
                    q.append(T(pts[j], pts[j + 1], 0.012 - j * 0.0012, teal, side + 'Hand', seg=10))
                q.append(E(pts[-1], (0.024, 0.024, 0.024), teal, side + 'Hand', seg=14, rings=10))
            # short thin legs, knobbed knees, small feet
            q.append(T((sx * 0.08, 0, H['hips']), (sx * 0.09, 0, H['knee']), 0.02, teal, side + 'UpLeg', r1=0.018))
            q.append(E((sx * 0.09, 0, H['knee']), (0.03, 0.03, 0.03), teal, side + 'Leg'))
            q.append(T((sx * 0.09, 0, H['knee']), (sx * 0.10, 0, H['ankle']), 0.018, teal, side + 'Leg', r1=0.016))
            q.append(E((sx * 0.10, -0.02, 0.025), (0.035, 0.05, 0.025), teal, side + 'Foot'))
            q.append(E((sx * 0.10, -0.075, 0.02), (0.03, 0.04, 0.02), teal, side + 'ToeBase'))
            return q
        P += _mirror(limbs)
        return P
    return {'name': 'TouSoul', 'bones': bones, 'parts': parts, 'height': 1.90}
