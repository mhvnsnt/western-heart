#!/usr/bin/env python3
"""pose_gate.py — per-character isolation pre-flight gate for WH models.

Run this on ANY model before wiring it as a playable fighter/attire
(see docs/PER-CHARACTER-ISOLATION.md). It answers, from the file itself:

  SHIPPABLE    skinned, canonical WH bone coverage complete, and an idle
               source exists (embedded 'Idle' clip, a native Battle_Idle /
               Stage_Idle, or rest pose is a natural stance — note the
               fighter's moveset-source bank stance covers idle in-game
               when a bank exists; the gate reports which source applies)
  NEEDS-RIG    no skin/skeleton (statue) — route through the auto-rig
               pipeline into the character's OWN directory first
  FOREIGN-RIG  skinned but canonical bones missing — bank clips and the
               embedded-name conventions cannot fully bind; wire only
               with the character's own native clips, or re-rig
  NO-IDLE      canonical rig but no idle source at all — the fighter
               would stand in rest pose; check bank coverage

Usage: pose_gate.py <model.glb> [<model.glb> ...]
Exit code 0 if all SHIPPABLE, 1 otherwise. Stdlib only.
"""
import json, math, struct, sys

CANON = ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck', 'Head',
         'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
         'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
         'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase',
         'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase']


def load_glb(path):
    raw = open(path, 'rb').read()
    if raw[:4] != b'glTF':
        raise ValueError('not a GLB')
    jlen = struct.unpack_from('<I', raw, 12)[0]
    return json.loads(raw[20:20 + jlen])


def q2m(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mv(A, v):
    return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]


def rest_world(j, skin):
    nodes = j['nodes']
    name, par = {}, {}
    for idx in skin['joints']:
        n = nodes[idx]
        name[n.get('name', '?')] = idx
    for idx in skin['joints']:
        for c in nodes[idx].get('children', []):
            if c in skin['joints']:
                par[c] = idx
    W = {}

    def world(idx):
        if idx in W:
            return W[idx]
        n = nodes[idx]
        R = q2m(n.get('rotation', [0, 0, 0, 1]))
        t = n.get('translation', [0, 0, 0])
        s = n.get('scale', [1, 1, 1])
        if idx in par:
            Rp, tp = world(par[idx])
            R = mul(Rp, R)
            t = [tp[i] + mv(Rp, [t[k] * s[k] for k in range(3)])[i] for i in range(3)]
        W[idx] = (R, t)
        return W[idx]

    return {nm: world(idx)[1] for nm, idx in name.items()}


def ang(a, b, c):
    v1 = [a[i] - b[i] for i in range(3)]
    v2 = [c[i] - b[i] for i in range(3)]
    n1 = math.sqrt(sum(x * x for x in v1)) or 1e-9
    n2 = math.sqrt(sum(x * x for x in v2)) or 1e-9
    d = max(-1.0, min(1.0, sum(v1[i] * v2[i] for i in range(3)) / (n1 * n2)))
    return math.degrees(math.acos(d))


def gate(path):
    try:
        j = load_glb(path)
    except Exception as e:
        return (path, 'UNREADABLE', [str(e)])
    skins = j.get('skins') or []
    anims = [a.get('name', '?') for a in j.get('animations', [])]
    notes = []
    if not skins:
        return (path, 'NEEDS-RIG',
                ['no skin/skeleton — frozen statue in game; auto-rig into '
                 "the character's own directory before wiring"])
    joints = skins[0]['joints']
    names = [j['nodes'][i].get('name', '?') for i in joints]
    missing = [b for b in CANON if b not in names]
    if missing:
        notes.append(f'missing canonical bones: {missing}')
        verdict = 'FOREIGN-RIG'
    else:
        verdict = 'SHIPPABLE'
    idle_src = None
    if 'Idle' in anims:
        idle_src = "embedded 'Idle'"
    elif 'Battle_Idle' in anims:
        idle_src = "native 'Battle_Idle' (registered as Idle by assets.js)"
    elif 'Stage_Idle' in anims:
        idle_src = "native 'Stage_Idle' (registered as Idle by assets.js)"
    if idle_src:
        notes.append(f'idle source: {idle_src}')
    else:
        notes.append('no embedded idle — idle must come from the '
                     "fighter's own moveset-source bank stance")
        if verdict == 'SHIPPABLE':
            verdict = 'NO-IDLE'
    try:
        pos = rest_world(j, skins[0])
        if all(k in pos for k in ('Hips', 'Head', 'LeftFoot', 'RightFoot')):
            up = [pos['Head'][i] - pos['Hips'][i] for i in range(3)]
            nu = math.sqrt(sum(x * x for x in up)) or 1e-9
            up = [x / nu for x in up]
            proj = [sum(pos[k][i] * up[i] for i in range(3)) for k in pos]
            notes.append(f'rest height ~{max(proj) - min(proj):.2f} (file units)')
        if all(k in pos for k in ('LeftUpLeg', 'LeftLeg', 'LeftFoot')):
            notes.append(f"rest L knee {ang(pos['LeftUpLeg'], pos['LeftLeg'], pos['LeftFoot']):.0f}deg "
                         f"(180 = straight)")
        if all(k in pos for k in ('Hips', 'Spine2', 'Head')):
            notes.append(f"rest spine pitch {ang(pos['Hips'], pos['Spine2'], pos['Head']):.0f}deg "
                         f"(180 = straight)")
    except Exception as e:
        notes.append(f'posture check skipped: {e}')
    notes.append(f'bones={len(joints)} clips={len(anims)}')
    return (path, verdict, notes)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    bad = 0
    for p in sys.argv[1:]:
        path, verdict, notes = gate(p)
        print(f'{verdict:12s} {path}')
        for n in notes:
            print(f'             - {n}')
        if verdict != 'SHIPPABLE':
            bad += 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
