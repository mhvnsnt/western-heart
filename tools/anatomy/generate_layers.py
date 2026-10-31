#!/usr/bin/env python3
"""Procedural anatomical layer generation for the WH creation suite.

Takes a character's rigged GLB + skeleton and procedurally derives the five
separable volumetric anatomy layers used by the creation suite's deep body
morphing system (see docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md):

  BONE   - simplified bone volumes from the skeleton (skull, ribcage, pelvis,
           limb capsules) as analytic SDF primitives.
  MUSCLE - muscle-group volumes (pecs, abs, biceps, quads, ...) as analytic
           SDF primitives attached to bones, each with a bulk morph parameter.
  FAT    - offset shell layer: per-region thickness baselines, driven by
           fat-thickness morph parameters.
  SKIN   - the existing render mesh (referenced, never copied).
  ORGAN  - visceral organs (heart, lungs, liver, stomach, intestines) as
           analytic SDF primitives positioned from the rig skeleton, for
           X-ray sequences (schema wh.anatomy-layers/2, additive: v1 readers
           ignore the organ key).

Representation: every volumetric layer is a UNION OF ANALYTIC SDF PRIMITIVES
(capsule / ellipsoid / sphere) stored as plain JSON. Shippable because it is
tiny, closed-form (exact SDF evaluation anywhere, no meshing needed),
trivially morphable (scale a radius), and directly sampleable into voxel
grids / marching-cubes meshes / McGraw-style splats later. No cryosection
data: volumes are procedural from the skeleton + body-part regions measured
from the mesh — the game-art version of McGraw's "design the 3D texture
representing alien or monster anatomy" suggestion.

Robustness for intake rigs (learned from pantera_rigged.glb):
- Y-rotation rectification: mesh and skeleton may be authored in different
  Y-rotations. Detected via mirror-symmetry + face direction, snapped to 90°.
- Facing from bilateral naming: rig front derived from .L/.R joint placement.
- GEOMETRIC-FIRST: skin weights from auto-riggers are often garbage (pantera:
  arm verts assigned to 'head'). Regions, limb frames, and facing are derived
  from joint positions + mesh geometry (closest-bone assignment, T-pose arm
  detection); skin weights are only a fallback hint, never trusted.

Dependencies: Python 3, numpy, pygltflib. No Blender required.

Usage:
  python3 generate_layers.py --glb <rigged.glb> --fighter <id> \\
      --glb-relpath <repo-relative path> --out <dir> [--render-proof]
"""
import argparse, json, math, os, re, struct, sys, zlib
from datetime import date

import numpy as np

SCHEMA = "wh.anatomy-layers/2"
TODAY = date.today().isoformat()

# ----------------------------------------------------------------------------
# glTF / GLB loading
# ----------------------------------------------------------------------------

COMP_LUT = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2),
            5125: ('I', 4), 5126: ('f', 4)}
TYPE_LUT = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4,
            'MAT3': 9, 'MAT4': 16}


def load_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'glTF':
        raise ValueError(f"not a GLB file: {path}")
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jlen].decode('utf-8', errors='replace'))
    off = 20 + jlen
    clen, ctype = struct.unpack('<II', data[off:off + 8])
    if ctype != 0x004E4942:
        raise ValueError("GLB has no BIN chunk")
    return js, data[off + 8:off + 8 + clen]


def read_accessor(js, blob, idx):
    acc = js['accessors'][idx]
    bv = js['bufferViews'][acc['bufferView']]
    fmt, size = COMP_LUT[acc['componentType']]
    ncomp = TYPE_LUT[acc['type']]
    count = acc['count']
    byte_off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    stride = bv.get('byteStride', size * ncomp)
    arr = np.zeros((count, ncomp), dtype=np.float64)
    for i in range(count):
        chunk = blob[byte_off + i * stride: byte_off + i * stride + size * ncomp]
        arr[i] = struct.unpack('<' + fmt * ncomp, chunk)
    if ncomp == 1:
        arr = arr[:, 0]
    return arr


def joint_bind_positions(js, blob):
    """Joint world positions in bind pose from inverse bind matrices.

    jointMatrix * IBM == identity in bind pose, so joint world = inv(IBM).
    Exact, no hierarchy traversal (robust for orphaned bind nodes).
    Returns (dict name->pos, dict name->parent name).
    """
    skin = js['skins'][0]
    ibm = read_accessor(js, blob, skin['inverseBindMatrices'])
    joints = {}
    for k, node_idx in enumerate(skin['joints']):
        name = js['nodes'][node_idx].get('name', f'joint{k}')
        m = ibm[k].reshape(4, 4).astype(np.float64)
        joints[name] = np.linalg.inv(m)[:3, 3]
    if joints and max(float(np.linalg.norm(v)) for v in joints.values()) \
            < 1e-9:
        # Identity IBMs (bind pose carried in node TRS only): take the
        # joint world positions from the node hierarchy instead.
        world = _node_world_positions(js)
        joints = {name: world[node_idx]
                  for name, node_idx in
                  ((js['nodes'][j].get('name', f'joint{k}'), j)
                   for k, j in enumerate(skin['joints']))}
    node_parent = {}
    for i, n in enumerate(js['nodes']):
        for c in n.get('children', []):
            if c not in node_parent:  # first-wins: joint hierarchy before scene roots
                node_parent[c] = i
    joint_nodes = {js['nodes'][j].get('name', f'joint{k}'): j
                   for k, j in enumerate(skin['joints'])}
    parents = {}
    for name, node_idx in joint_nodes.items():
        p, parent_name = node_idx, None
        while p in node_parent:
            p = node_parent[p]
            pname = js['nodes'][p].get('name')
            if pname in joint_nodes:
                parent_name = pname
                break
        parents[name] = parent_name
    return joints, parents



# ----------------------------------------------------------------------------
# Joint-name canonicalization (2026-10-31, rig-continuation stage 3).
#
# The layer builders below key on the 13 canonical landmark names of the
# template skeleton (hips, spine, chest, neck, head, shoulder.L/R,
# thigh.L/R, shin.L/R, foot.L/R — exactly the skeleton of the proof
# fighter, roster/pantera). Roster rigs arrive in several naming
# dialects (repo template Title-Case, Mixamo, Unreal mannequin,
# lowercase variants), and before this stage every non-template rig
# silently produced empty bone/muscle/organ layers. This maps each
# rig's landmarks onto the canonical names so the SAME builders work
# on every rig. It renames only when the anatomical identity is
# unambiguous, never guesses a side; competing claims to one
# landmark resolve to the most specific stem (see below).
# joints would collide on one canonical name. The mapping used is
# recorded in the artifact under source.joint_name_map.
# ----------------------------------------------------------------------------

CANONICAL_LANDMARKS = ('hips', 'spine', 'chest', 'neck', 'head',
                       'shoulder.L', 'shoulder.R', 'thigh.L', 'thigh.R',
                       'shin.L', 'shin.R', 'foot.L', 'foot.R')

_AXIAL_STEMS = {'hips': ('hips', 0), 'pelvis': ('hips', 2),
                'hip': ('hips', 3), 'waist': ('hips', 1),
                'roothips': ('hips', 1),
                'spine': ('spine', 0), 'spine01': ('spine', 1),
                'spine1': ('spine', 2), 'stomach': ('spine', 1),
                'spinelower': ('spine', 1),
                'spine2': ('chest', 1), 'spine02': ('chest', 2),
                'spine03': ('chest', 0), 'chest': ('chest', 0),
                'thorax': ('chest', 2), 'spineupper': ('chest', 1),
                'neck': ('neck', 0), 'neck01': ('neck', 1),
                'neck1': ('neck', 1),
                'head': ('head', 0)}
_SIDED_STEMS = {'shoulder': ('shoulder', 0), 'clavicle': ('shoulder', 1),
                'thigh': ('thigh', 0), 'upleg': ('thigh', 1),
                'upperleg': ('thigh', 2),
                'shin': ('shin', 0), 'leg': ('shin', 2),
                'knee': ('shin', 1),
                'calf': ('shin', 3), 'lowerleg': ('shin', 4),
                'foot': ('foot', 0), 'ankle': ('foot', 1),
                'upperarm': ('upperarm', 0), 'arm': ('upperarm', 1),
                'forearm': ('forearm', 0), 'lowerarm': ('forearm', 1),
                'elbow': ('forearm', 1), 'hip': ('thigh', 2),
                'hand': ('hand', 0), 'wrist': ('hand', 1)}


def _split_side(name):
    """(side 'L'/'R' or None, remaining stem text)."""
    low = name.lower()
    if low.startswith('left'):
        return 'L', name[4:]
    if low.startswith('right'):
        return 'R', name[5:]
    if len(name) > 1 and name[0] in 'LR' and name[1].isupper():
        return name[0], name[1:]
    if low.endswith('left'):
        return 'L', name[:-4]
    if low.endswith('right'):
        return 'R', name[:-5]
    for tok, s in ((' left ', 'L'), (' right ', 'R')):
        i = low.find(tok)
        if i >= 0:
            return s, name[:i] + ' ' + name[i + len(tok):]
    if low.endswith('.l') or low.endswith('_l'):
        return 'L', name[:-2]
    if low.endswith('.r') or low.endswith('_r'):
        return 'R', name[:-2]
    if name.endswith(' l'):
        return 'L', name[:-2]
    if name.endswith(' r'):
        return 'R', name[:-2]
    return None, name


def _stem(name):
    s = name
    low = s.lower()
    for pre in ('mixamorig:', 'mixamorig1:', 'mixamorig'):
        if low.startswith(pre):
            s = s[len(pre):]
            break
    return re.sub(r'[^a-z0-9]', '', s.lower())


def canonicalize_joint_names(joint_names):
    """Map a rig's joint names onto the canonical landmarks.

    Returns {original: canonical} for the joints that were renamed
    ({} when the rig is already canonical). Only the 13 landmarks
    plus the arm chain (upperarm/forearm/hand per side) are ever
    renamed; every other joint keeps its authored name. When several
    joints claim one landmark (production rigs carry adjunct chains
    next to the template chain), the claim with the most specific
    stem wins - exact 'spine' beats 'spine1', 'LeftLeg' beats
    'leg left' - with shortest name, then alphabetical order, as
    deterministic tie-breaks. Losing claimants keep their names.
    A side is never guessed: sided landmarks require the side token
    in the joint's own name."""
    names = list(joint_names)
    if all(n in names for n in CANONICAL_LANDMARKS):
        return {}
    def claim_for(bare):
        """(target, rank) for one name form, or None."""
        side, rest = _split_side(bare)
        st = _stem(rest)
        if side is None and st in _AXIAL_STEMS:
            base, rank = _AXIAL_STEMS[st]
            return base, rank
        if side is not None and st in _SIDED_STEMS:
            base, rank = _SIDED_STEMS[st]
            return f'{base}.{side}', rank
        if 'finger' in st or 'toe' in st:
            return None  # digits never claim a landmark
        if side is not None:
            # Verbose dialects ('arm right shoulder 1', 'leg left
            # knee', VRoid chains): the anatomical keyword inside
            # the stem decides, at the lowest claim rank.
            for kw, base in (('shoulder', 'shoulder'),
                             ('elbow', 'forearm'), ('wrist', 'hand'),
                             ('hand', 'hand'), ('thigh', 'thigh'),
                             ('knee', 'shin'), ('ankle', 'foot'),
                             ('foot', 'foot')):
                if kw in st:
                    return f'{base}.{side}', 3
            if st.startswith('arm'):
                return f'upperarm.{side}', 3
            return None
        if 'neck' in st:
            return 'neck', 3
        if 'head' in st:
            return 'head', 3
        return None

    claims = {}
    for n in names:
        if n in CANONICAL_LANDMARKS:
            claims.setdefault(n, []).append((0, n))
            continue
        bare = n
        for pre in ('mixamorig:', 'mixamorig1:', 'mixamorig'):
            if bare.lower().startswith(pre):
                bare = bare[len(pre):]
                break
        hit = claim_for(bare)
        if hit is None:
            # Numbered-suffix dialects (VRoid 'Waist_06',
            # 'LShoulder_01', verbose 'arm right shoulder 1'):
            # retry with the trailing index stripped. Only as a
            # fallback - unstripped 'spine_02' must keep its own
            # chest claim instead of collapsing into 'spine'.
            stripped = re.sub(r'(_end)?_\d+$', '', bare)
            stripped = re.sub(r' \d+$', '', stripped)
            if stripped != bare:
                hit = claim_for(stripped)
        if hit is not None:
            target, rank = hit
            claims.setdefault(target, []).append((rank, n))
    mapping = {}
    for target, cands in claims.items():
        cands.sort(key=lambda rn: (rn[0], len(rn[1]), rn[1]))
        mapping[cands[0][1]] = target
    return {k: v for k, v in mapping.items() if k != v}



def _node_world_positions(js):
    """Joint world positions from the node hierarchy (TRS composition
    from the scene roots down). Used as a fallback when a rig's
    inverse bind matrices are identity (several exporters write
    identity IBMs and carry the bind pose purely in node TRS)."""
    nodes = js['nodes']
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i

    def local(n):
        if 'matrix' in n:
            return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
        t = n.get('translation', [0, 0, 0])
        x, y, z, w = n.get('rotation', [0, 0, 0, 1])
        s = n.get('scale', [1, 1, 1])
        R = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w),
             2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z),
             2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w),
             1 - 2 * (x * x + y * y)]], dtype=np.float64)
        M = np.eye(4)
        M[:3, :3] = R * np.array(s, dtype=np.float64)
        M[:3, 3] = t
        return M

    cache = {}

    def world(i):
        if i not in cache:
            m = local(nodes[i])
            if i in parent:
                m = world(parent[i]) @ m
            cache[i] = m
        return cache[i]

    return {i: world(i)[:3, 3] for i in range(len(nodes))}


def load_mesh(js, blob, mesh_index=0):
    """Returns (pos, tris, dom_joint, joint_names). dom_joint[i] = index into
    joint_names of the highest-weight joint for vertex i."""
    mesh = js['meshes'][mesh_index]
    joint_names = [js['nodes'][j].get('name', f'joint{k}')
                   for k, j in enumerate(js['skins'][0]['joints'])]
    pos_list, idx_list, dom_list = [], [], []
    voff = 0
    for prim in mesh['primitives']:
        pos = read_accessor(js, blob, prim['attributes']['POSITION'])
        pos_list.append(pos)
        if 'indices' in prim:
            idx = read_accessor(js, blob, prim['indices']).astype(np.int64)
            idx_list.append(idx.reshape(-1, 3) + voff)
        else:
            idx_list.append(np.arange(len(pos)).reshape(-1, 3) + voff)
        attrs = prim['attributes']
        if 'JOINTS_0' in attrs and 'WEIGHTS_0' in attrs:
            jn = read_accessor(js, blob, attrs['JOINTS_0']).astype(int)
            wt = read_accessor(js, blob, attrs['WEIGHTS_0'])
            if jn.ndim == 1:
                jn, wt = jn[:, None], wt[:, None]
            dom_list.append(jn[np.arange(len(jn)), np.argmax(wt, axis=1)])
        else:
            dom_list.append(np.zeros(len(pos), dtype=int))
        voff += len(pos)
    return (np.vstack(pos_list), np.vstack(idx_list),
            np.concatenate(dom_list), joint_names)


def vertex_normals(pos, tris):
    n = np.zeros_like(pos)
    p0, p1, p2 = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    l = np.linalg.norm(n, axis=1, keepdims=True)
    l[l == 0] = 1.0
    return n / l

# ----------------------------------------------------------------------------
# Mesh<->skeleton frame rectification.
#
# Intake rigs sometimes assemble a mesh authored in a different Y-rotation
# than the skeleton (pantera_rigged.glb: mesh z-symmetric, skeleton x-wide).
# We detect the needed Y-rotation (snapped to 90 deg) from:
#   1. mirror symmetry: a character is L/R (x) symmetric, not front/back (z).
#   2. facing: the snout direction -> the rig's front (from .L/.R naming).
# ----------------------------------------------------------------------------

def x_mirror_overlap(pos, angle_deg, tol=0.01):
    """Fraction of verts (1cm grid) with a mirror counterpart across x=0
    after Y-rotation by angle_deg. High = correct L/R symmetry plane."""
    r = np.deg2rad(angle_deg)
    c, s = np.cos(r), np.sin(r)
    x = c * pos[:, 0] + s * pos[:, 2]
    z = -s * pos[:, 0] + c * pos[:, 2]
    q = np.round(np.stack([x, pos[:, 1], z], axis=1) / tol).astype(np.int64)
    a = set(map(tuple, q))
    m = q.copy()
    m[:, 0] *= -1
    b = set(map(tuple, m))
    return len(a & b) / max(len(a), 1)


def find_face_dir(pos, dom_joint, joint_names):
    """Mesh facing direction (unit XZ vector) from the head.

    The snout/muzzle is the head's dominant horizontal protrusion. We use the
    head core (tight central box) to exclude misweighted limb verts that some
    auto-riggers leave in the head chunk.
    """
    heads = [n for n in joint_names if 'head' in n.lower()]
    if not heads:
        return None
    hp = pos[dom_joint == joint_names.index(heads[0])]
    if len(hp) < 50:
        return None
    med = np.median(hp, axis=0)
    core = hp[(np.abs(hp[:, 0] - med[0]) < 0.20) &
              (np.abs(hp[:, 2] - med[2]) < 0.20)]
    if len(core) < 50:
        core = hp
    c = core[:, [0, 2]].mean(axis=0)
    rel = core[:, [0, 2]] - c
    d2 = (rel ** 2).sum(axis=1)
    # mean direction of the farthest 3% (the protrusion, not noise)
    top = rel[d2 >= np.percentile(d2, 97)]
    v = top.mean(axis=0)
    n = float(np.linalg.norm(v))
    if n < 1e-6:
        return None
    return v / n


def rig_front_dir(joints):
    """Rig facing (unit XZ vector) from bilateral naming.

    Anatomical convention: a character facing +Z has anatomical left at +X.
    So '.L' at -X implies the rig faces -Z.
    """
    lefts = [p for k, p in joints.items() if k.lower().endswith('.l')]
    if lefts:
        lx = float(np.mean([p[0] for p in lefts]))
        return np.array([0.0, 1.0 if lx > 0 else -1.0])
    return np.array([0.0, 1.0])


def rectify_mesh_frame(pos, joints, dom_joint=None, joint_names=None):
    """Y-rotate the mesh into the skeleton's frame.

    1. Pick the Y-rotation (0/90/180/270) maximizing L/R (x) mirror symmetry.
    2. Among the two symmetry-equivalent options, keep the one sending the
       mesh's face direction to the rig's front (snapped, 90 deg grid).
    Face direction is geometric (head joint + protrusion), not from skin
    weights. dom_joint/joint_names are accepted for API compatibility but
    unused.
    Returns (rectified_pos, angle_deg, rig_front_xz).
    """
    scores = {a: x_mirror_overlap(pos, a) for a in (0, 90, 180, 270)}
    sym_ang = max(scores, key=scores.get)
    front = rig_front_dir(joints)
    face = find_face_dir_geometric(pos, joints)

    ang = sym_ang
    if face is not None:
        # angle from face to front about +Y (right-hand rule)
        cross_y = face[1] * front[0] - face[0] * front[1]
        dot = float(face @ front)
        theta = np.degrees(np.arctan2(cross_y, dot))
        face_ang = int(round(theta / 90.0) * 90.0) % 360
        # must be symmetry-compatible (differ by 0 or 180)
        if (face_ang - sym_ang) % 180 == 0:
            ang = face_ang
    r = np.deg2rad(ang)
    c, s = np.cos(r), np.sin(r)
    out = pos.copy()
    x, z = pos[:, 0], pos[:, 2]
    out[:, 0], out[:, 2] = c * x + s * z, -s * x + c * z
    return out, ang, front

# ----------------------------------------------------------------------------
# Analytic SDF primitives. A layer = union (min) of primitives, stored as
# plain JSON dicts: {"kind": "capsule"|"ellipsoid"|"sphere", ...}.
# ----------------------------------------------------------------------------

def sdf_capsule(p, a, b, r):
    pa = p - a
    ba = b - a
    h = np.clip(pa @ ba / (ba @ ba + 1e-12), 0.0, 1.0)
    return np.linalg.norm(pa - np.outer(h, ba), axis=1) - r


def sdf_sphere(p, c, r):
    return np.linalg.norm(p - c, axis=1) - r


def sdf_ellipsoid(p, c, radii):
    q = (p - c) / radii
    k0 = np.linalg.norm(q, axis=1)
    k1 = np.linalg.norm((p - c) / (radii * radii), axis=1) + 1e-12
    return k0 * (k0 - 1.0) / k1  # Knud Thomsen approximation


def eval_primitive(p, prim):
    kind = prim['kind']
    if kind == 'capsule':
        return sdf_capsule(p, np.array(prim['a']), np.array(prim['b']), prim['r'])
    if kind == 'sphere':
        return sdf_sphere(p, np.array(prim['center']), prim['r'])
    if kind == 'ellipsoid':
        return sdf_ellipsoid(p, np.array(prim['center']), np.array(prim['radii']))
    raise ValueError(f"unknown primitive kind: {kind}")


def eval_layer_sdf(p, primitives):
    d = np.full(len(p), 1e9)
    for prim in primitives:
        d = np.minimum(d, eval_primitive(p, prim))
    return d


def primitive_volume(prim):
    if prim['kind'] == 'sphere':
        return 4.0 / 3.0 * math.pi * prim['r'] ** 3
    if prim['kind'] == 'ellipsoid':
        rx, ry, rz = prim['radii']
        return 4.0 / 3.0 * math.pi * rx * ry * rz
    if prim['kind'] == 'capsule':
        a, b, r = np.array(prim['a']), np.array(prim['b']), prim['r']
        L = float(np.linalg.norm(b - a))
        return math.pi * r * r * L + 4.0 / 3.0 * math.pi * r ** 3
    return 0.0


# ----------------------------------------------------------------------------
# Body-part regions + data-driven limb frames.
# ----------------------------------------------------------------------------

def joint_region(joint_name):
    nl = joint_name.lower()
    if 'head' in nl or 'neck' in nl:
        return 'head'
    if any(k in nl for k in ('shoulder', 'elbow', 'wrist', 'hand', 'arm')):
        side = nl.split('.')[-1].upper() if '.' in nl else ''
        return f'arm.{side}' if side in ('L', 'R') else 'torso'
    if any(k in nl for k in ('thigh', 'shin', 'knee', 'foot', 'ankle', 'leg')):
        side = nl.split('.')[-1].upper() if '.' in nl else ''
        return f'leg.{side}' if side in ('L', 'R') else 'torso'
    return 'torso'


def assign_regions(dom_joint, joint_names):
    return np.array([joint_region(joint_names[d]) for d in dom_joint])


def chunk_radius(pts, origin, axis):
    if len(pts) < 8:
        return 0.03
    rel = pts - origin
    t = rel @ axis
    radial = np.linalg.norm(rel - np.outer(t, axis), axis=1)
    return float(np.percentile(radial, 90))


def fit_arm_frame(pts, j_shoulder):
    """Arm (leaf joint) frame: direction toward the farthest chunk point
    (hand end) — robust when the chunk includes lateral torso verts that would
    fool PCA. Radius from the distal 2/3 (past the deltoid blend)."""
    if len(pts) < 16:
        return None
    d2 = ((pts - j_shoulder) ** 2).sum(axis=1)
    axis = pts[np.argmax(d2)] - j_shoulder
    length = float(np.linalg.norm(axis))
    if length < 0.08:
        return None
    axis = axis / length
    t = (pts - j_shoulder) @ axis
    distal = pts[t > 0.35 * length]
    radius = chunk_radius(distal if len(distal) >= 8 else pts, j_shoulder, axis)
    return {'origin': j_shoulder, 'axis': axis, 'length': length,
            'radius': radius, 'count': int(len(pts))}


# ----------------------------------------------------------------------------
# GEOMETRIC-FIRST methods (robust to bad skin weights).
#
# Auto-riggers often produce garbage skin weights (pantera_rigged.glb: arm
# verts assigned to 'head', 'shoulder.L' getting torso verts). These methods
# derive everything from joint positions + mesh geometry instead.
# ----------------------------------------------------------------------------

def _point_segment_distance(p, a, b):
    """Distance from points p (N,3) to segment a-b. Returns (dist, t)."""
    ab = b - a
    denom = float(ab @ ab) + 1e-12
    t = np.clip((p - a) @ ab / denom, 0.0, 1.0)
    closest = a + np.outer(t, ab)
    return np.linalg.norm(p - closest, axis=1), t


def assign_regions_geometric(pos, joints, arm_frames):
    """Assign each vertex to a body region by closest bone segment.

    Bone segments: head (sphere at head joint), neck (neck->head),
    torso (hips->spine->chest->neck chain), arm.L/R (shoulder + arm frame),
    leg.L/R (thigh->shin->foot). Returns array of region strings.
    """
    N = len(pos)
    # Build list of (region, segment_a, segment_b, radius_for_tiebreak)
    segs = []
    J = joints
    chain = ['hips', 'spine', 'chest', 'neck']
    for i in range(len(chain) - 1):
        a, b = chain[i], chain[i + 1]
        if a in J and b in J:
            segs.append(('torso', J[a], J[b]))
    if 'neck' in J and 'head' in J:
        segs.append(('torso', J['neck'], J['head']))  # neck shaft -> torso
        segs.append(('head', J['head'], J['head']))    # head sphere
    for side in ('L', 'R'):
        sh = f'shoulder.{side}'
        if sh in J and sh in arm_frames and arm_frames[sh]:
            fr = arm_frames[sh]
            segs.append((f'arm.{side}', fr['origin'],
                         fr['origin'] + fr['axis'] * fr['length']))
        th, sn, ft = f'thigh.{side}', f'shin.{side}', f'foot.{side}'
        if th in J and sn in J:
            segs.append((f'leg.{side}', J[th], J[sn]))
        if sn in J and ft in J:
            segs.append((f'leg.{side}', J[sn], J[ft]))

    if not segs:
        return np.array(['torso'] * N)

    best_dist = np.full(N, 1e9)
    best_region = np.array(['torso'] * N, dtype=object)
    # Priority for ties: head > arm/leg > torso (limbs win over torso)
    priority = {'head': 0, 'arm.L': 1, 'arm.R': 1, 'leg.L': 1, 'leg.R': 1,
                'torso': 2}
    best_prio = np.full(N, 99)
    for region, a, b in segs:
        d, _ = _point_segment_distance(pos, a, b)
        pr = priority.get(region, 2)
        # win if clearly closer, or tie but higher priority
        win = (d < best_dist - 1e-4) | ((np.abs(d - best_dist) < 1e-4)
                                        & (pr < best_prio))
        best_dist[win] = d[win]
        best_region[win] = region
        best_prio[win] = pr
    return best_region


def fit_arm_frame_geometric(pos, joints, side):
    """Fit arm frame from T-pose geometry (not skin weights).

    Finds the arm as the horizontal protrusion at shoulder height on the
    given side. Works for T-pose and A-pose; falls back to None if the arm
    can't be isolated (then the caller skips arm muscles for that side).
    """
    sh_key = f'shoulder.{side}'
    if sh_key not in joints:
        return None
    S = joints[sh_key]
    sx = 1.0 if S[0] > 0 else -1.0  # outward sign from joint x

    # Candidate arm verts: at shoulder height, outward of the shoulder
    h = 0.18
    cand = ((np.abs(pos[:, 1] - S[1]) < h)
            & ((pos[:, 0] - S[0]) * sx > 0.04))
    pts = pos[cand]
    if len(pts) < 40:
        return None

    # Arm axis: from shoulder to centroid of farthest 25% (by outward dist)
    out = (pts[:, 0] - S[0]) * sx
    far = pts[out >= np.percentile(out, 75)]
    axis = far.mean(axis=0) - S
    length = float(np.linalg.norm(axis))
    if length < 0.10:
        return None
    axis = axis / length

    # Length: farthest vert along axis
    t = (pts - S) @ axis
    length = float(t.max())
    if length < 0.10:
        return None

    # Radius: 90th pct perpendicular distance in the middle 60% of the arm
    mid = pts[(t > 0.2 * length) & (t < 0.8 * length)]
    if len(mid) < 16:
        mid = pts
    rel = mid - S
    tt = np.clip(rel @ axis, 0, None)
    perp = np.linalg.norm(rel - np.outer(tt, axis), axis=1)
    radius = float(np.percentile(perp, 90))
    radius = max(min(radius, 0.12), 0.02)
    return {'origin': S, 'axis': axis, 'length': length, 'radius': radius,
            'count': int(len(pts)), 'method': 'geometric'}



def fit_arm_frame_skeleton(pos, joints, side):
    """Arm frame from the skeleton chain (shoulder -> hand): the leg
    method applied to arms. Fallback for when the T-pose protrusion
    fit fails — rigs whose bind pose is a fighting stance carry their
    arms down, so there is no horizontal protrusion to detect. The
    axis is the shoulder->hand line; the radius is measured
    geometrically from the mesh around that segment and clamped to
    the same range the geometric fit uses."""
    sh, hd = f'shoulder.{side}', f'hand.{side}'
    if sh not in joints or hd not in joints:
        return None
    A0, W = joints[sh], joints[hd]
    axis = W - A0
    L = float(np.linalg.norm(axis))
    if L < 0.10:
        return None
    axis = axis / L
    d, _ = _point_segment_distance(pos, A0, W)
    near = pos[d < 0.20]
    radius = chunk_radius(near, A0, axis)
    radius = max(min(radius, 0.12), 0.02)
    return {'origin': A0, 'axis': axis, 'length': L, 'radius': radius,
            'count': int(len(near)), 'method': 'skeleton'}


def find_face_dir_geometric(pos, joints):
    """Face direction from head joint + local mesh protrusion.

    Takes verts near the head joint, finds the dominant horizontal
    protrusion (snout/muzzle/face front). Does not use skin weights.
    """
    if 'head' not in joints:
        return None
    H = joints['head']
    d = np.linalg.norm(pos - H, axis=1)
    near = pos[d < 0.30]
    if len(near) < 50:
        return None
    c = near[:, [0, 2]].mean(axis=0)
    rel = near[:, [0, 2]] - c
    d2 = (rel ** 2).sum(axis=1)
    top = rel[d2 >= np.percentile(d2, 97)]
    v = top.mean(axis=0)
    n = float(np.linalg.norm(v))
    if n < 1e-6:
        return None
    return v / n

# ----------------------------------------------------------------------------
# LAYER 1 — BONE
# ----------------------------------------------------------------------------

def build_bone_layer(joints, parents, frames, torso_radius=0.14):
    prims = []
    J = joints

    def add(pid, prim, joint, morph):
        prim.update({'id': pid, 'joint': joint, 'morph': morph})
        prims.append(prim)

    def cap(a, b, r):
        return {'kind': 'capsule',
                'a': [round(float(x), 4) for x in a],
                'b': [round(float(x), 4) for x in b],
                'r': round(float(r), 4)}

    def ell(c, radii):
        return {'kind': 'ellipsoid',
                'center': [round(float(x), 4) for x in np.array(c, float)],
                'radii': [round(float(x), 4) for x in radii]}

    # Limb bones along fitted frames (bone ~ 42% of limb surface radius).
    for jname, fr in frames.items():
        if not fr:
            continue
        a = fr['origin']
        add(f'bone_{jname}', cap(a, a + fr['axis'] * fr['length'],
                                fr['radius'] * 0.42),
            jname, 'bone_scale_limbs')

    # Axial capsules along joint segments.
    for child, parent in parents.items():
        if parent is None or child not in J or parent not in J:
            continue
        nl = child.lower()
        if not any(k in nl for k in ('spine', 'neck', 'chest', 'hips')):
            continue
        L = float(np.linalg.norm(J[child] - J[parent]))
        if L < 1e-4:
            continue
        add(f'bone_{child}', cap(J[parent], J[child], L * 0.18),
            child, 'bone_scale_spine')

    # Skull.
    if 'head' in J and 'neck' in J:
        hr = float(np.linalg.norm(J['head'] - J['neck']))
        s = hr / 0.125
        c = J['head'] + np.array([0.0, hr * 0.35, 0.01])
        add('bone_skull', ell(c, [0.075 * s, 0.095 * s, 0.085 * s]),
            'head', 'bone_scale_skull')

    # Ribcage / pelvis nested inside the torso surface.
    chest_key = next((k for k in ('chest', 'spine') if k in J), None)
    if chest_key:
        tr = torso_radius
        add('bone_ribcage',
            ell(J[chest_key] + np.array([0.0, 0.02, 0.0]),
                [tr * 0.78, tr * 0.95, tr * 0.62]),
            chest_key, 'bone_scale_ribcage')
    if 'hips' in J:
        tr = torso_radius
        add('bone_pelvis',
            ell(J['hips'], [tr * 0.82, tr * 0.62, tr * 0.58]),
            'hips', 'bone_scale_pelvis')
    return {'primitives': prims}


# ----------------------------------------------------------------------------
# LAYER 2 — MUSCLE
# ----------------------------------------------------------------------------

def _side_names(base, joints):
    return [(s, f'{base}.{s}') for s in ('L', 'R') if f'{base}.{s}' in joints]


def _front_back(axis, front):
    f = np.array(front, dtype=float)
    f = f - axis * float(axis @ f)
    if float(np.linalg.norm(f)) < 1e-3:
        f = np.array([1.0, 0.0, 0.0])
        f = f - axis * float(axis @ f)
    f = f / (np.linalg.norm(f) + 1e-12)
    return f, -f


def build_muscle_layer(joints, parents, frames, torso_radius=0.14,
                       body_scale=1.0, front=(0.0, 0.0, 1.0)):
    """Muscle groups as SDF primitives. Radii are anatomically proportioned
    (scaled by body_scale = height/1.75) and hard-clamped inside the measured
    mesh surface so volumes never poke through the skin."""
    J = joints
    F = np.array([front[0], 0.0, front[2] if len(front) > 2 else front[1]],
                 dtype=float)
    F = F / (np.linalg.norm(F) + 1e-12)
    bs = body_scale
    groups = []

    def mrad(anatomical, measured):
        return min(anatomical * bs, max(measured * 0.75, 0.015))

    def cap(gid, label, side, a, b, r):
        return {'id': gid, 'label': label, 'side': side,
                'primitives': [{'kind': 'capsule',
                                'a': [round(float(x), 4) for x in a],
                                'b': [round(float(x), 4) for x in b],
                                'r': round(float(r), 4)}],
                'bulk_param': f"muscle_{gid.replace('.', '_')}",
                'base_radius': round(float(r), 4)}

    def ell(gid, label, side, center, radii):
        return {'id': gid, 'label': label, 'side': side,
                'primitives': [{'kind': 'ellipsoid',
                                'center': [round(float(x), 4)
                                           for x in np.array(center, float)],
                                'radii': [round(float(x), 4) for x in radii]}],
                'bulk_param': f"muscle_{gid.replace('.', '_')}",
                'base_radius': round(float(np.mean(radii)), 4)}

    chest_key = next((k for k in ('chest', 'spine') if k in J), None)

    if 'neck' in J and chest_key:
        w = float(np.linalg.norm(J[chest_key] - J['neck']))
        groups.append(ell('trapezius', 'Trapezius', 'C',
                          J['neck'] - np.array([0.0, 0.03, 0.0]),
                          (w * 0.38, 0.038, 0.042)))
    if 'neck' in J and 'head' in J:
        A, B = J['neck'], J['head']
        L = float(np.linalg.norm(B - A))
        groups.append(cap('neck', 'Neck', 'C', A, A + (B - A) * 0.9, L * 0.28))

    # Arms (data-driven frames).
    for side, sh in _side_names('shoulder', J):
        fr = frames.get(sh)
        if not fr:
            continue
        A0, ax, L, R = J[sh], fr['axis'], fr['length'], fr['radius']
        ff, bb = _front_back(ax, F)
        r_d = mrad(0.070, R)
        groups.append(ell(f'deltoid.{side}', 'Deltoid', side,
                          A0 + ax * 0.06 * L, (r_d, mrad(0.085, R), r_d)))
        r_bi, r_tr, r_fo = mrad(0.052, R), mrad(0.048, R), mrad(0.042, R)
        groups.append(cap(f'biceps.{side}', 'Biceps', side,
                          A0 + ax * 0.14 * L + ff * r_bi * 0.45,
                          A0 + ax * 0.46 * L + ff * r_bi * 0.45, r_bi))
        groups.append(cap(f'triceps.{side}', 'Triceps', side,
                          A0 + ax * 0.14 * L + bb * r_tr * 0.45,
                          A0 + ax * 0.46 * L + bb * r_tr * 0.45, r_tr))
        groups.append(cap(f'forearm.{side}', 'Forearm', side,
                          A0 + ax * 0.52 * L, A0 + ax * 0.94 * L, r_fo))

    # Torso (nested by torso_radius, front-relative).
    if chest_key:
        tr = torso_radius
        for side, sh in _side_names('shoulder', J):
            sx = -1.0 if side == 'L' else 1.0
            groups.append(ell(
                f'pectoralis.{side}', 'Pectoralis', side,
                J[chest_key] + np.array([sx * tr * 0.42, 0.03, 0.0])
                + F * tr * 0.60, (tr * 0.38, tr * 0.36, tr * 0.26)))
            groups.append(ell(
                f'latissimus.{side}', 'Latissimus', side,
                J[chest_key] + np.array([sx * tr * 0.70, -0.03, 0.0])
                - F * tr * 0.38, (tr * 0.30, tr * 0.48, tr * 0.28)))
    if 'spine' in J and chest_key:
        A, B = J['spine'], J[chest_key]
        tr = torso_radius
        groups.append(cap('abdominals', 'Abdominals', 'C',
                          A + F * tr * 0.55, B + F * tr * 0.55, tr * 0.52))
        for side in ('L', 'R'):
            sx = -1.0 if side == 'L' else 1.0
            groups.append(cap(
                f'obliques.{side}', 'Obliques', side,
                A + np.array([sx * tr * 0.72, 0, 0]) + F * tr * 0.18,
                B + np.array([sx * tr * 0.72, 0, 0]) + F * tr * 0.18,
                tr * 0.30))
    if 'hips' in J:
        for side, th in _side_names('thigh', J):
            sx = -1.0 if side == 'L' else 1.0
            gr = mrad(0.070, 0.10)
            groups.append(ell(
                f'gluteus.{side}', 'Gluteus', side,
                J['hips'] + np.array([sx * 0.085, -0.035, 0.0]) - F * 0.075,
                (gr, mrad(0.065, 0.10), mrad(0.055, 0.10))))

    # Legs (joint axes + chunk radii).
    for side, th in _side_names('thigh', J):
        fr = frames.get(th)
        if not fr or f'shin.{side}' not in J:
            continue
        T0, ax, R = J[th], fr['axis'], fr['radius']
        ff, bb = _front_back(ax, F)
        thigh_len = float(np.linalg.norm(J[f'shin.{side}'] - T0))
        r_qu, r_ha = mrad(0.078, R), mrad(0.066, R)
        groups.append(cap(f'quadriceps.{side}', 'Quadriceps', side,
                          T0 + ax * 0.10 * thigh_len + ff * r_qu * 0.40,
                          T0 + ax * 0.85 * thigh_len + ff * r_qu * 0.40, r_qu))
        groups.append(cap(f'hamstrings.{side}', 'Hamstrings', side,
                          T0 + ax * 0.10 * thigh_len + bb * r_ha * 0.40,
                          T0 + ax * 0.85 * thigh_len + bb * r_ha * 0.40, r_ha))
        sfr = frames.get(f'shin.{side}') or fr
        S0, sax, sR = J[f'shin.{side}'], sfr['axis'], sfr['radius']
        sf, sb = _front_back(sax, F)
        r_ca = mrad(0.055, sR)
        groups.append(cap(f'calves.{side}', 'Calves', side,
                          S0 + sax * 0.12 * sfr['length'] + sb * r_ca * 0.45,
                          S0 + sax * 0.68 * sfr['length'] + sb * r_ca * 0.45,
                          r_ca))
    return {'groups': groups}

# ----------------------------------------------------------------------------
# LAYER 3 — FAT. Per-region thickness baselines; morph params scale them.
# Baselines are small physiological defaults, refined per fighter by the
# suite (measured or authored). Clamped so bad input can't produce garbage.
# ----------------------------------------------------------------------------

FAT_REGIONS = ['head', 'torso', 'arm.L', 'arm.R', 'leg.L', 'leg.R']
FAT_DEFAULTS = {'head': 0.006, 'torso': 0.012, 'arm.L': 0.008,
                'arm.R': 0.008, 'leg.L': 0.010, 'leg.R': 0.010}


def build_fat_layer(body_scale=1.0):
    return {
        'baseline_global': round(0.010 * body_scale, 4),
        'regions': {
            r: {'thickness': round(FAT_DEFAULTS[r] * body_scale, 4),
                'param': f'fat_{r.replace(".", "_")}'}
            for r in FAT_REGIONS
        },
        'thickness_param': 'fat_thickness',
        'note': ('Per-region subcutaneous fat thickness. Morph params scale '
                 'these baselines; the skin rides muscle+fat via '
                 'bake_displacement.'),
    }


# ----------------------------------------------------------------------------
# LAYER 4 — SKIN. The render mesh, referenced (never copied).
# ----------------------------------------------------------------------------

def build_skin_layer(glb_relpath, mesh_index=0):
    return {
        'mesh_ref': f'{glb_relpath}#mesh{mesh_index}',
        'morph_targets': ['MPFB_bulk', 'MPFB_muscle', 'MPFB_fat'],
        'note': ('The skin layer IS the character mesh (referenced). MPFB '
                 'shape keys stay the surface-morph path; anatomy morphs bake '
                 'to per-vertex displacement along normals.'),
    }


# ----------------------------------------------------------------------------
# LAYER 5 — ORGAN. Visceral organs for X-ray sequences: heart, lungs, liver,
# stomach, intestines. Analytic SDF primitives positioned from the rig
# skeleton (chest / spine / hips) geometrically — no meshing, no cryosection
# data, same union-of-primitives representation as the other layers.
# Added in schema wh.anatomy-layers/2 (additive: v1 readers ignore the
# "organ" key).
# ----------------------------------------------------------------------------

def _anatomical_left(joints, front):
    """Unit vector of anatomical LEFT in rig frame (GEOMETRIC-FIRST).

    From the .L joints' x-sign; falls back to the rig-front convention
    left = up x front (anatomical left of a character facing front).
    """
    lefts = [p for k, p in joints.items() if k.lower().endswith('.l')]
    if lefts:
        mx = float(np.mean([p[0] for p in lefts]))
        if abs(mx) > 1e-4:
            return np.array([1.0 if mx > 0 else -1.0, 0.0, 0.0])
    f = np.array([front[0], 0.0, front[2] if len(front) > 2 else front[1]],
                 dtype=float)
    n = float(np.linalg.norm(f))
    f = f / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
    lv = np.cross(np.array([0.0, 1.0, 0.0]), f)
    n = float(np.linalg.norm(lv))
    return lv / n if n > 1e-9 else np.array([-1.0, 0.0, 0.0])


def build_organ_layer(joints, torso_radius=0.14, body_scale=1.0,
                      front=(0.0, 0.0, 1.0)):
    """Visceral organs as SDF primitives, positioned from rig joints.

    Anchors: chest (ribcage contents: heart, lungs), the spine->chest
    segment (abdomen: liver, stomach), hips/spine (intestines). Sizes are
    anatomically proportioned to torso_radius (the skeleton-derived torso
    half-width) and scaled by body_scale, so organs fit the character
    rather than a fixed human — and stay nested inside the ribcage/torso
    volumes of the BONE layer.
    """
    J = joints
    chest_key = next((k for k in ('chest', 'spine') if k in J), None)
    F = np.array([front[0], 0.0, front[2] if len(front) > 2 else front[1]],
                 dtype=float)
    F = F / (np.linalg.norm(F) + 1e-12)
    LV = _anatomical_left(joints, front)  # anatomical-left unit vector
    tr, bs = torso_radius, body_scale
    groups = []

    def clamp_r(radii):
        return [round(max(min(float(x), tr * 0.70), 0.015), 4)
                for x in radii]

    def ell(gid, label, side, center, radii):
        return {'id': gid, 'label': label, 'side': side,
                'primitives': [{'kind': 'ellipsoid',
                                'center': [round(float(x), 4)
                                           for x in np.array(center, float)],
                                'radii': clamp_r(radii)}],
                'bulk_param': f"organ_{gid.replace('.', '_')}",
                'base_radius': round(float(np.mean(radii)), 4)}

    def cap(gid, label, side, a, b, r):
        return {'id': gid, 'label': label, 'side': side,
                'primitives': [{'kind': 'capsule',
                                'a': [round(float(x), 4) for x in a],
                                'b': [round(float(x), 4) for x in b],
                                'r': round(max(min(float(r), tr * 0.70),
                                               0.015), 4)}],
                'bulk_param': f"organ_{gid.replace('.', '_')}",
                'base_radius': round(float(r), 4)}

    if chest_key and 'spine' in J:
        C, S = J[chest_key], J['spine']
        up = np.array([0.0, 1.0, 0.0])
        # Heart: left mid-chest, just below the chest joint.
        groups.append(ell('heart', 'Heart', 'L',
                          C + LV * tr * 0.30 + F * tr * 0.10
                          - up * tr * 0.35,
                          (0.045 * bs, 0.058 * bs, 0.048 * bs)))
        # Lungs: fill the ribcage above the heart, one per side.
        for side, sgn in (('L', 1.0), ('R', -1.0)):
            groups.append(ell(
                f'lung.{side}', 'Lung', side,
                C + LV * sgn * tr * 0.40 + up * tr * 0.12,
                (tr * 0.33, tr * 0.58, tr * 0.42)))
        # Liver: right abdomen, tucked under the ribcage.
        mid = S + (C - S) * 0.32
        groups.append(ell('liver', 'Liver', 'R',
                          mid - LV * tr * 0.30 + F * tr * 0.08,
                          (tr * 0.42, tr * 0.34, tr * 0.40)))
        # Stomach: left abdomen, in front of the spine.
        mid2 = S + (C - S) * 0.55
        groups.append(ell('stomach', 'Stomach', 'L',
                          mid2 + LV * tr * 0.22 + F * tr * 0.14,
                          (tr * 0.28, tr * 0.26, tr * 0.26)))
    if 'hips' in J and 'spine' in J:
        H, S = J['hips'], J['spine']
        up = np.array([0.0, 1.0, 0.0])
        # Intestines: simplified capsule cluster in the lower abdomen.
        groups.append(cap('intestines.1', 'Intestines', 'C',
                          H + up * 0.05 + F * tr * 0.10,
                          S - up * 0.04 + F * tr * 0.10,
                          tr * 0.30))
        groups.append(cap('intestines.2', 'Intestines', 'C',
                          S + LV * tr * 0.32 - up * 0.05 + F * tr * 0.08,
                          S - LV * tr * 0.32 - up * 0.07 + F * tr * 0.08,
                          tr * 0.24))
    return {'groups': groups}


# ----------------------------------------------------------------------------
# MORPH PARAMETER REGISTRY — the dials the creation-suite UI builds on.
# ----------------------------------------------------------------------------

MUSCLE_BULK_GAIN = 0.55  # radius *= 1 + gain * v, v in [-1, 1]
FAT_GAIN = 0.80          # thickness *= 1 + gain * v
BONE_GAIN = 0.25         # radii *= 1 + gain * v
ORGAN_GAIN = 0.25        # organ radii *= 1 + gain * v


def build_morph_params(muscle_groups, bone_primitives, organ_groups=None):
    params = []
    for g in muscle_groups:
        params.append({
            'id': g['bulk_param'], 'layer': 'muscle',
            'label': f"{g['label']} bulk" + (f" ({g['side']})"
                                             if g['side'] != 'C' else ""),
            'range': [-1, 1], 'default': 0.0,
            'effect': f'group radius *= 1 + {MUSCLE_BULK_GAIN}*v',
            'applies_to': [g['id']],
            'suite_dial': f"body.{g['id'].replace('.', '_')}",
        })
    for r in FAT_REGIONS:
        params.append({
            'id': f"fat_{r.replace('.', '_')}", 'layer': 'fat',
            'label': f'Fat: {r}', 'range': [-1, 1], 'default': 0.0,
            'effect': f'region thickness *= 1 + {FAT_GAIN}*v',
            'applies_to': [r],
            'suite_dial': f'body.fat_{r.replace(".", "_")}',
        })
    params.append({
        'id': 'fat_thickness', 'layer': 'fat', 'label': 'Fat (global)',
        'range': [-1, 1], 'default': 0.0,
        'effect': f'all regions thickness *= 1 + {FAT_GAIN}*v',
        'applies_to': FAT_REGIONS, 'suite_dial': 'body.fat_thickness',
    })
    bone_regions = sorted({p.get('morph', 'bone_scale_limbs')
                           for p in bone_primitives if 'morph' in p})
    for b in bone_regions:
        params.append({
            'id': b, 'layer': 'bone',
            'label': 'Bone: ' + b.replace('bone_scale_', '').replace('_', ' '),
            'range': [-1, 1], 'default': 0.0,
            'effect': f'bone radii *= 1 + {BONE_GAIN}*v',
            'applies_to': [p['id'] for p in bone_primitives
                            if p.get('morph') == b],
            'suite_dial': f'body.{b}',
        })
    for g in (organ_groups or []):
        params.append({
            'id': g['bulk_param'], 'layer': 'organ',
            'label': f"Organ: {g['label']}" + (f" ({g['side']})"
                                               if g['side'] != 'C' else ""),
            'range': [-1, 1], 'default': 0.0,
            'effect': f'organ radii *= 1 + {ORGAN_GAIN}*v',
            'applies_to': [g['id']],
            'suite_dial': f"body.{g['bulk_param']}",
        })
    return params


def apply_morphs(layers, values):
    """Pure function: morphed copies of the bone/muscle/fat/organ layer dicts."""
    import copy
    bone = copy.deepcopy(layers['bone'])
    muscle = copy.deepcopy(layers['muscle'])
    fat = copy.deepcopy(layers['fat'])
    organ = copy.deepcopy(layers.get('organ', {'groups': []}))
    v = lambda pid: float(values.get(pid, 0.0))

    for p in bone['primitives']:
        pid = p.get('morph')
        if pid and pid in values:
            s = 1.0 + BONE_GAIN * v(pid)
            if p['kind'] in ('capsule', 'sphere'):
                p['r'] = round(p['r'] * s, 5)
            elif p['kind'] == 'ellipsoid':
                p['radii'] = [round(x * s, 5) for x in p['radii']]

    for g in muscle['groups']:
        pid = g['bulk_param']
        if pid in values:
            s = 1.0 + MUSCLE_BULK_GAIN * v(pid)
            for prim in g['primitives']:
                if prim['kind'] in ('capsule', 'sphere'):
                    prim['r'] = round(prim['r'] * s, 5)
                elif prim['kind'] == 'ellipsoid':
                    prim['radii'] = [round(x * s, 5) for x in prim['radii']]

    for g in organ['groups']:
        pid = g['bulk_param']
        if pid in values:
            s = 1.0 + ORGAN_GAIN * v(pid)
            for prim in g['primitives']:
                if prim['kind'] in ('capsule', 'sphere'):
                    prim['r'] = round(prim['r'] * s, 5)
                elif prim['kind'] == 'ellipsoid':
                    prim['radii'] = [round(x * s, 5) for x in prim['radii']]

    vg = v('fat_thickness')
    for r, rd in fat['regions'].items():
        s = (1.0 + FAT_GAIN * vg) * (1.0 + FAT_GAIN * v(rd['param']))
        rd['thickness_morphed'] = round(rd['thickness'] * s, 5)
    return {'bone': bone, 'muscle': muscle, 'fat': fat, 'organ': organ}


def muscle_primitives_flat(muscle_layer):
    prims = []
    for g in muscle_layer['groups']:
        prims.extend(g['primitives'])
    return prims


def bake_displacement(pos, normals, regions, layers_base, layers_morphed):
    """Bake anatomy morphs to per-vertex displacement along normals.

    The skin rides the muscle surface: displacement =
      (d_base - d_morphed)      # muscle surface moved toward/away from skin
      + (fat_morphed - fat_base)  # fat shell thickened/thinned
    where d = muscle-layer SDF at the vertex (positive outside).
    Returns (displacement_vectors (N,3), displacement_scalars (N,)).
    """
    base_prims = muscle_primitives_flat(layers_base['muscle'])
    new_prims = muscle_primitives_flat(layers_morphed['muscle'])
    d_base = np.empty(len(pos))
    d_new = np.empty(len(pos))
    CH = 2048
    for s in range(0, len(pos), CH):
        c = pos[s:s + CH]
        d_base[s:s + CH] = eval_layer_sdf(c, base_prims)
        d_new[s:s + CH] = eval_layer_sdf(c, new_prims)
    disp = np.clip(d_base - d_new, -0.06, 0.20)
    fat_b, fat_m = layers_base['fat']['regions'], layers_morphed['fat']['regions']
    for r in FAT_REGIONS:
        m = regions == r
        if m.sum():
            delta = (fat_m[r].get('thickness_morphed', fat_m[r]['thickness'])
                     - fat_b[r]['thickness'])
            disp[m] += delta
    disp = np.clip(disp, -0.06, 0.25)
    return normals * disp[:, None], disp

# ----------------------------------------------------------------------------
# RENDERING — orthographic sphere tracing of layer SDFs (no Blender needed).
# ----------------------------------------------------------------------------

def write_png(path, rgb):
    h, w, _ = rgb.shape
    raw = b''.join(b'\x00' + np.ascontiguousarray(rgb[y]).tobytes()
                   for y in range(h))

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)


def render_sdf_layer(primitives, bounds, W=300, H=360, view=1):
    """Orthographic sphere trace of a primitive union, viewed from the front.

    view=+1: camera at +Z looking down -Z; view=-1: camera at -Z looking +Z
    (anatomical left kept on the image's left). Returns (H,W,3) uint8.
    """
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    xs = np.linspace(xmin, xmax, W)
    if view < 0:
        xs = xs[::-1]
    ys = np.linspace(ymax, ymin, H)
    gx, gy = np.meshgrid(xs, ys)
    z0 = zmax + 0.5 if view > 0 else zmin - 0.5
    rays_o = np.stack([gx.ravel(), gy.ravel(),
                       np.full(gx.size, z0)], axis=1)
    ray_d = np.array([0.0, 0.0, -1.0 if view > 0 else 1.0])
    light = np.array([-0.45, 0.75, 0.55 * view])
    light = light / np.linalg.norm(light)

    t = np.zeros(gx.size)
    hit = np.zeros(gx.size, dtype=bool)
    alive = np.ones(gx.size, dtype=bool)
    tmax = (zmax + 0.5) - (zmin - 0.5)
    for _ in range(90):
        p = rays_o[alive] + np.outer(t[alive], ray_d)
        s = eval_layer_sdf(p, primitives)
        idx = np.flatnonzero(alive)
        done = s < 1e-4
        hit[idx[done]] = True
        alive[idx[done]] = False
        t[alive] += np.clip(s[~done], 1e-4, 0.05)
        alive[t > tmax] = False
        if not alive.any():
            break

    img = np.ones((H, W, 3), dtype=np.float64) * 0.94
    if hit.any():
        ph = rays_o[hit] + np.outer(t[hit], ray_d)
        e = 1.5e-3
        n = np.stack([
            eval_layer_sdf(ph + [e, 0, 0], primitives)
            - eval_layer_sdf(ph - [e, 0, 0], primitives),
            eval_layer_sdf(ph + [0, e, 0], primitives)
            - eval_layer_sdf(ph - [0, e, 0], primitives),
            eval_layer_sdf(ph + [0, 0, e], primitives)
            - eval_layer_sdf(ph - [0, 0, e], primitives),
        ], axis=1)
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
        shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
        img[hit.reshape(H, W)] = np.array([0.72, 0.78, 0.86]) * shade[:, None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def render_mesh_points(pos, normals, bounds, W=300, H=360, view=1):
    """Skin-layer proof: orthographic point projection of the render mesh
    (painter's algorithm, shaded by facing)."""
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    img = np.ones((H, W, 3), dtype=np.float64) * 0.94
    if view > 0:
        order = np.argsort(pos[:, 2])
        xs = pos[:, 0]
    else:
        order = np.argsort(-pos[:, 2])
        xs = -pos[:, 0]
        xmin, xmax = -xmax, -xmin
    p, n = pos[order], normals[order]
    xs = xs[order]
    px = ((xs - xmin) / (xmax - xmin) * (W - 1)).astype(int)
    py = ((ymax - p[:, 1]) / (ymax - ymin) * (H - 1)).astype(int)
    ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
    shade = 0.30 + 0.70 * np.clip(n[ok, 2] * 0.5 + 0.5, 0, 1)
    img[py[ok], px[ok]] = np.array([0.45, 0.55, 0.68]) * shade[:, None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


# ----------------------------------------------------------------------------
# PIPELINE DRIVER
# ----------------------------------------------------------------------------


def pick_body_mesh(js):
    """Index of the mesh to build anatomy from: the skinned mesh with
    the most vertices (2026-10-31, rig-continuation stage 3).

    The generator originally hard-coded mesh 0; on multi-mesh rigs
    mesh 0 can be a tiny attachment (armor-king's is 16 verts) and the
    layers came out built on the prop instead of the body. Single-
    mesh rigs (pantera) are unaffected: the only mesh is picked."""
    best, best_key = 0, None
    for i, m in enumerate(js['meshes']):
        verts, skinned = 0, False
        for prim in m['primitives']:
            attrs = prim['attributes']
            if 'POSITION' in attrs:
                verts += js['accessors'][attrs['POSITION']]['count']
            if 'JOINTS_0' in attrs:
                skinned = True
        key = (1 if skinned else 0, verts)
        if best_key is None or key > best_key:
            best, best_key = i, key
    return best


def load_body_mesh(js, blob):
    """Merged body geometry: every skinned mesh concatenated
    (2026-10-31, rig-continuation stage 3).

    Some fighters' bodies are split across several skinned meshes
    (armor-king: five ~1.1k-vert shells, 5,660 verts total). Building
    the SDF body from only the largest piece produced partial
    anatomy that still passed containment checks against itself.
    The body is ALL skinned geometry; single-mesh rigs (pantera)
    merge to exactly their one mesh, unchanged."""
    used = []
    for i, m in enumerate(js['meshes']):
        if any('JOINTS_0' in p['attributes'] for p in m['primitives']):
            used.append(i)
    if not used:
        used = [pick_body_mesh(js)]
    if len(used) == 1:
        pos, tris, dom, names = load_mesh(js, blob, used[0])
        return pos, tris, dom, names, used
    pos_l, tris_l, dom_l, names = [], [], [], None
    voff = 0
    for i in used:
        p, t, d, names = load_mesh(js, blob, i)
        pos_l.append(p)
        tris_l.append(t + voff)
        dom_l.append(d)
        voff += len(p)
    return (np.vstack(pos_l), np.vstack(tris_l),
            np.concatenate(dom_l), names, used)


def generate(glb_path, fighter, glb_relpath):
    js, blob = load_glb(glb_path)
    joints, parents = joint_bind_positions(js, blob)
    name_map = canonicalize_joint_names(joints.keys())
    if name_map:
        joints = {name_map.get(k, k): v for k, v in joints.items()}
        parents = {name_map.get(k, k): (name_map.get(v) if v else None)
                   for k, v in parents.items()}
    pos, tris, dom_joint, joint_names, body_meshes = load_body_mesh(js, blob)
    mesh_index = body_meshes[0] if len(body_meshes) == 1 else 'merged'
    pos, rect_angle, rig_front = rectify_mesh_frame(pos, joints)
    normals = vertex_normals(pos, tris)

    chest_key = next((k for k in ('chest', 'spine') if k in joints), None)

    # Data-driven limb frames — GEOMETRIC (robust to bad skin weights).
    # Arms: T-pose protrusion detection. Legs: joint axes + geometric radii.
    frames = {}
    for side in ('L', 'R'):
        fr = fit_arm_frame_geometric(pos, joints, side)
        if not fr:
            fr = fit_arm_frame_skeleton(pos, joints, side)
        if fr:
            frames[f'shoulder.{side}'] = fr
        th, sn, ft = f'thigh.{side}', f'shin.{side}', f'foot.{side}'
        if th in joints and sn in joints:
            ax = joints[sn] - joints[th]
            L = float(np.linalg.norm(ax))
            if L > 1e-4:
                ax = ax / L
                # geometric radius: verts near the thigh segment
                d, _ = _point_segment_distance(pos, joints[th], joints[sn])
                near = pos[d < 0.20]
                frames[th] = {'origin': joints[th], 'axis': ax, 'length': L,
                              'radius': chunk_radius(near, joints[th], ax),
                              'count': int(len(near)), 'method': 'geometric'}
        if sn in joints and ft in joints:
            ax = joints[ft] - joints[sn]
            L = float(np.linalg.norm(ax))
            if L > 1e-4:
                ax = ax / L
                d, _ = _point_segment_distance(pos, joints[sn], joints[ft])
                near = pos[d < 0.15]
                frames[sn] = {'origin': joints[sn], 'axis': ax, 'length': L,
                              'radius': chunk_radius(near, joints[sn], ax),
                              'count': int(len(near)), 'method': 'geometric'}

    # Regions: geometric closest-bone assignment (not skin weights).
    regions = assign_regions_geometric(pos, joints, frames)

    # Torso radius from the skeleton (robust): half the shoulder half-width.
    torso_radius = 0.14
    sh_x = [abs(float(joints[k][0])) for k in joints
            if 'shoulder' in k.lower()]
    if sh_x:
        torso_radius = float(np.mean(sh_x)) * 0.5
    height = float(pos[:, 1].max() - pos[:, 1].min())
    body_scale = height / 1.75

    bone = build_bone_layer(joints, parents, frames, torso_radius)
    muscle = build_muscle_layer(joints, parents, frames, torso_radius,
                                body_scale, front=rig_front)
    organ = build_organ_layer(joints, torso_radius, body_scale,
                              front=rig_front)
    morph_params = build_morph_params(muscle['groups'], bone['primitives'],
                                      organ['groups'])
    fat = build_fat_layer(body_scale)
    skin = build_skin_layer(glb_relpath, mesh_index)
    if mesh_index == 'merged':
        skin['mesh_ref'] = (f'{glb_relpath}#meshes'
                            f'{",".join(str(i) for i in body_meshes)}-merged')

    layers = {
        '$schema': SCHEMA,
        'schema_version': SCHEMA,
        'fighter': fighter,
        'generated': TODAY,
        'generator': 'tools/anatomy/generate_layers.py',
        'units': 'meters',
        'source': {
            'glb': glb_relpath, 'mesh': mesh_index, 'skin': 0,
            'joint_name_map': name_map,
            'joints': len(joints), 'vertices': int(len(pos)),
            'mesh_rectification_y_deg': int(rect_angle),
            'mesh_rectification_note': (
                'mesh verts rotated about Y by this angle into skeleton '
                'space; 0 = already aligned'),
            'rig_front': [float(rig_front[0]), 0.0, float(rig_front[1])],
            'rig_front_note': ('rig facing from bilateral naming; '
                               'muscle "front" offsets use this direction'),
        },
        'skeleton': {
            name: {'pos': [round(float(x), 4) for x in p],
                   'parent': parents.get(name)}
            for name, p in joints.items()
        },
        'layers': {'bone': bone, 'muscle': muscle, 'organ': organ,
                   'fat': fat, 'skin': skin},
        'morph_params': morph_params,
    }
    aux = {'pos': pos, 'tris': tris, 'normals': normals, 'regions': regions,
           'joints': joints}
    return layers, aux


def layer_bounds(aux, pad=0.06):
    pos = aux['pos']
    return (float(pos[:, 0].min()) - pad, float(pos[:, 0].max()) + pad,
            float(pos[:, 1].min()) - pad, float(pos[:, 1].max()) + pad,
            float(pos[:, 2].min()) - pad, float(pos[:, 2].max()) + pad)


def proof_markdown(fighter, proof):
    v = proof['validation']
    return f"""# Anatomy layers — proof ({fighter})

Generated {proof['date']} by `tools/anatomy/generate_layers.py`.

## What was generated
Five separable volumetric layers from the rigged GLB's skeleton, stored as
unions of analytic SDF primitives in `anatomy-layers.json`.
Renders in `renders/`: `layer_bone.png`, `layer_muscle.png`, `layer_organ.png`,
`layer_fat.png`, `layer_skin.png`.

## Morph proof — `muscle_biceps_L`: 0.0 -> 1.0
- biceps.L capsule radius: {proof['biceps_L_radius_base']} m -> {proof['biceps_L_radius_morphed']} m (delta {proof['biceps_L_radius_delta']} m)
- biceps.L volume: {proof['biceps_L_volume_base_m3']} m^3 -> {proof['biceps_L_volume_morphed_m3']} m^3 (+{proof['biceps_L_volume_gain_pct']}%)
- baked skin displacement (whole mesh): mean {proof['skin_vert_displacement_mean_m']} m, max {proof['skin_vert_displacement_max_m']} m
- baked skin displacement (left arm region): mean {proof['skin_vert_displacement_armL_mean_m']} m, max {proof['skin_vert_displacement_armL_max_m']} m
- renders: `renders/morph_biceps_0.png` vs `renders/morph_biceps_1.png`

## Validation
- mesh<->skeleton Y rectification: {proof['rectification_deg']} deg (rig front {proof['rig_front']})
- joints inside bone layer: {v['joints_inside_bone_layer']} (bone volumes must contain their joints)
- organs inside body: {v['organs_inside_body']} (organ primitive centers must sit inside the body: wrapped in muscle or cradled by bone)
- morph params registered: {v['morph_param_count']}
"""


def main():
    ap = argparse.ArgumentParser(description='Generate anatomical layers.')
    ap.add_argument('--glb', required=True)
    ap.add_argument('--fighter', required=True)
    ap.add_argument('--glb-relpath', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--morph', default='{}')
    ap.add_argument('--render-proof', action='store_true')
    args = ap.parse_args()

    glb_rel = args.glb_relpath or os.path.basename(args.glb)
    layers, aux = generate(args.glb, args.fighter, glb_rel)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, 'anatomy-layers.json'), 'w') as f:
        json.dump(layers, f, indent=1)

    n_bone = len(layers['layers']['bone']['primitives'])
    n_muscle = len(layers['layers']['muscle']['groups'])
    n_organ = len(layers['layers']['organ']['groups'])
    print(f"fighter={args.fighter} joints={layers['source']['joints']} "
          f"verts={layers['source']['vertices']} "
          f"rect={layers['source']['mesh_rectification_y_deg']}deg "
          f"front={layers['source']['rig_front']}")
    print(f"bone: {n_bone} primitives | muscle: {n_muscle} groups | "
          f"organ: {n_organ} groups | "
          f"fat regions: {len(layers['layers']['fat']['regions'])} | "
          f"morph params: {len(layers['morph_params'])}")

    morph_values = json.loads(args.morph)
    if args.render_proof:
        rdir = os.path.join(args.out, 'renders')
        os.makedirs(rdir, exist_ok=True)
        bounds = layer_bounds(aux)
        view = 1 if layers['source']['rig_front'][2] > 0 else -1
        write_png(os.path.join(rdir, 'layer_bone.png'),
                  render_sdf_layer(layers['layers']['bone']['primitives'],
                                   bounds, view=view))
        mprims = muscle_primitives_flat(layers['layers']['muscle'])
        write_png(os.path.join(rdir, 'layer_muscle.png'),
                  render_sdf_layer(mprims, bounds, view=view))
        oprims = []
        for g in layers['layers']['organ']['groups']:
            oprims.extend(g['primitives'])
        write_png(os.path.join(rdir, 'layer_organ.png'),
                  render_sdf_layer(oprims, bounds, view=view))
        fg = layers['layers']['fat']['baseline_global']
        fat_shell = []
        for p in mprims:
            if p['kind'] == 'capsule':
                fat_shell.append({'kind': 'capsule', 'a': p['a'], 'b': p['b'],
                                  'r': p['r'] + fg})
            elif p['kind'] == 'sphere':
                fat_shell.append({'kind': 'sphere', 'center': p['center'],
                                  'r': p['r'] + fg})
            else:
                fat_shell.append({'kind': 'ellipsoid', 'center': p['center'],
                                  'radii': [x + fg for x in p['radii']]})
        write_png(os.path.join(rdir, 'layer_fat.png'),
                  render_sdf_layer(fat_shell, bounds, view=view))
        write_png(os.path.join(rdir, 'layer_skin.png'),
                  render_mesh_points(aux['pos'], aux['normals'], bounds,
                                     view=view))
        print('wrote 5 layer renders')

        morphed = apply_morphs(layers['layers'], {'muscle_biceps_L': 1.0})
        write_png(os.path.join(rdir, 'morph_biceps_0.png'),
                  render_sdf_layer(mprims, bounds, view=view))
        write_png(os.path.join(rdir, 'morph_biceps_1.png'),
                  render_sdf_layer(muscle_primitives_flat(morphed['muscle']),
                                   bounds, view=view))

        base_g = next((g for g in layers['layers']['muscle']['groups']
                       if g['id'] == 'biceps.L'), None)
        if base_g is None:
            print('WARNING: no biceps.L muscle group (arm frame '
                  'unfit) - morph proof skipped; layers + renders '
                  'still written.')
        else:
            base_g = next(g for g in layers['layers']['muscle']['groups']
                          if g['id'] == 'biceps.L')
            new_g = next(g for g in morphed['muscle']['groups']
                         if g['id'] == 'biceps.L')
            r0 = base_g['primitives'][0]['r']
            r1 = new_g['primitives'][0]['r']
            v0 = sum(primitive_volume(p) for p in base_g['primitives'])
            v1 = sum(primitive_volume(p) for p in new_g['primitives'])
            disp, disp_s = bake_displacement(
                aux['pos'], aux['normals'], aux['regions'],
                layers['layers'], morphed)
            arm = aux['regions'] == 'arm.L'
            proof = {
                'fighter': args.fighter,
                'date': TODAY,
                'rectification_deg': layers['source']['mesh_rectification_y_deg'],
                'rig_front': layers['source']['rig_front'],
                'biceps_L_radius_base': r0,
                'biceps_L_radius_morphed': r1,
                'biceps_L_radius_delta': round(r1 - r0, 5),
                'biceps_L_volume_base_m3': round(v0, 6),
                'biceps_L_volume_morphed_m3': round(v1, 6),
                'biceps_L_volume_gain_pct': round(100 * (v1 - v0) / v0, 2),
                'skin_vert_displacement_mean_m': round(float(disp_s.mean()), 5),
                'skin_vert_displacement_max_m': round(float(disp_s.max()), 5),
                'skin_vert_displacement_armL_mean_m':
                    round(float(disp_s[arm].mean()) if arm.sum() else 0.0, 5),
                'skin_vert_displacement_armL_max_m':
                    round(float(disp_s[arm].max()) if arm.sum() else 0.0, 5),
                'validation': {'joints_inside_bone_layer': None,
                               'organs_inside_body': None,
                               'morph_param_count': len(layers['morph_params'])},
            }
            J = np.stack([np.array(v['pos']) for v in layers['skeleton'].values()])
            inside = (eval_layer_sdf(J, layers['layers']['bone']['primitives']) < 0).sum()
            proof['validation']['joints_inside_bone_layer'] = f'{int(inside)}/{len(J)}'
            ocenters = []
            for g in layers['layers']['organ']['groups']:
                for p in g['primitives']:
                    if p['kind'] == 'capsule':
                        a, b = np.array(p['a']), np.array(p['b'])
                        ocenters.append((a + b) / 2.0)
                    else:
                        ocenters.append(np.array(p['center']))
            ocenters = np.stack(ocenters)
            # Organs nestle inside the body: either wrapped in muscle (thorax)
            # or cradled by bone (intestines in the pelvic bowl). A center is
            # valid if it is inside either union (small tolerance for SDF seams).
            d_muscle = eval_layer_sdf(
                ocenters, muscle_primitives_flat(layers['layers']['muscle']))
            d_bone = eval_layer_sdf(
                ocenters, layers['layers']['bone']['primitives'])
            o_inside = (np.minimum(d_muscle, d_bone) < 0.02).sum()
            proof['validation']['organs_inside_body'] = (
                f'{int(o_inside)}/{len(ocenters)}')
            with open(os.path.join(args.out, 'proof.json'), 'w') as f:
                json.dump(proof, f, indent=1)
            with open(os.path.join(args.out, 'PROOF.md'), 'w') as f:
                f.write(proof_markdown(args.fighter, proof))
            print(json.dumps(proof, indent=1))

    if morph_values and not args.render_proof:
        morphed = apply_morphs(layers['layers'], morph_values)
        with open(os.path.join(args.out, 'anatomy-layers.morphed.json'), 'w') as f:
            json.dump(morphed, f, indent=1)
        print('wrote anatomy-layers.morphed.json')


if __name__ == '__main__':
    main()
