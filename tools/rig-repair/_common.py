"""Shared GLB skinning-surgery helpers for tools/rig-repair/.

Pure-Python, surgical: weight edits rewrite accessor bytes in place (no JSON
changes); bone additions append nodes / skin joints / inverse-bind matrices.
Validated against three.js: IBM == inv(jointWorld) to <1e-6.
"""
import struct
import json
import numpy as np

COMP_DT = {5120: '<i1', 5121: '<u1', 5122: '<i2', 5123: '<u2',
           5125: '<u4', 5126: '<f4'}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4,
         'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
INT_MAX = {'<i1': 127, '<u1': 255, '<i2': 32767, '<u2': 65535,
           '<u4': 4294967295}


# ---------------------------------------------------------------- I/O
class Glb:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.data = f.read()
        ln = struct.unpack('<I', self.data[12:16])[0]
        assert self.data[16:20] == b'JSON'
        self.g = json.loads(self.data[20:20 + ln])
        blen = struct.unpack('<I', self.data[20 + ln:24 + ln])[0]
        assert self.data[24 + ln:28 + ln] == b'BIN\x00'
        stored = self.data[28 + ln:28 + ln + blen]
        # materialize every bufferView as decoded bytes (meshopt-aware)
        self.views = {}
        for vi, bv in enumerate(self.g.get('bufferViews', [])):
            ext = bv.get('extensions', {}).get('EXT_meshopt_compression')
            if ext is not None:
                import meshopt
                cbuf = ext['buffer']
                # compressed bytes live in the stored chunk only for buffer 0;
                # (multi-buffer meshopt files are not supported)
                assert cbuf == 0, "meshopt from non-zero buffer unsupported"
                comp = stored[ext['byteOffset']:
                              ext['byteOffset'] + ext['byteLength']]
                dec = meshopt.decode_gltf_buffer(
                    bytes(comp), ext['count'], ext['byteStride'],
                    ext['mode'], ext.get('filter'))
                self.views[vi] = bytearray(dec.tobytes())
            else:
                buf = bv.get('buffer', 0)
                assert buf == 0, "multi-buffer GLB without meshopt unsupported"
                off = bv.get('byteOffset', 0)
                self.views[vi] = bytearray(
                    stored[off:off + bv['byteLength']])
        self._new_views = []  # bytearrays appended by add_accessor

    # -- accessors -------------------------------------------------
    def _acc_info(self, idx):
        a = self.g['accessors'][idx]
        bv = self.g['bufferViews'][a['bufferView']]
        return a, bv, a.get('byteOffset', 0)

    def _read_elems(self, idx):
        """Raw element bytes for an accessor (stride-aware)."""
        a, bv, off = self._acc_info(idx)
        data = self.views[a['bufferView']]
        dt = np.dtype(COMP_DT[a['componentType']])
        esz = dt.itemsize * NCOMP[a['type']]
        stride = bv.get('byteStride', esz)
        if stride == esz:
            return np.frombuffer(data, dtype=dt, count=a['count'] * esz // dt.itemsize,
                                 offset=off).reshape(a['count'], NCOMP[a['type']])
        # interleaved: gather per-element
        out = np.empty((a['count'], NCOMP[a['type']]), dtype=dt)
        for i in range(a['count']):
            out[i] = np.frombuffer(data, dtype=dt, count=NCOMP[a['type']],
                                   offset=off + i * stride)
        return out

    def decode(self, idx, normalize=True):
        """Decode accessor to float64 (normalized ints -> float)."""
        a, _, _ = self._acc_info(idx)
        arr = self._read_elems(idx)
        if normalize and a.get('normalized'):
            arr = arr.astype(np.float64) / INT_MAX[COMP_DT[a['componentType']]]
        return arr

    def decode_int(self, idx):
        return self._read_elems(idx).astype(np.int64)

    def encode_into(self, idx, float_data):
        """Write float data back into an accessor in place.

        Requires identical shape and byte length (same count + component
        type) and a tightly packed bufferView. Quantizes normalized
        integer types with rounding.
        """
        a, bv, off = self._acc_info(idx)
        dt = np.dtype(COMP_DT[a['componentType']])
        esz = dt.itemsize * NCOMP[a['type']]
        assert bv.get('byteStride', esz) == esz, \
            f"accessor {idx}: cannot encode into strided view"
        flat = np.asarray(float_data, dtype=np.float64).reshape(-1)
        assert flat.shape[0] == a['count'] * NCOMP[a['type']], \
            f"shape mismatch on accessor {idx}"
        if a.get('normalized'):
            mx = INT_MAX[COMP_DT[a['componentType']]]
            vals = np.clip(np.round(flat * mx), 0, mx).astype(dt)
        else:
            vals = flat.astype(dt)
        raw = vals.tobytes()
        data = self.views[a['bufferView']]
        data[off:off + len(raw)] = raw

    def add_accessor(self, float_data, component_type, acc_type,
                     normalized=False):
        """Append a new accessor (+bufferView); return its index."""
        dt = np.dtype(COMP_DT[component_type])
        flat = np.asarray(float_data, dtype=np.float64).reshape(-1)
        if normalized:
            mx = INT_MAX[COMP_DT[component_type]]
            vals = np.clip(np.round(flat * mx), 0, mx).astype(dt)
        else:
            vals = flat.astype(dt)
        raw = vals.tobytes()
        self._new_views.append(bytearray(raw))
        bv_idx = len(self.g['bufferViews']) + len(self._new_views) - 1
        acc_idx = len(self.g['accessors'])
        self.g['accessors'].append({
            'bufferView': bv_idx, 'componentType': component_type,
            'count': int(flat.shape[0] // NCOMP[acc_type]),
            'type': acc_type, **({'normalized': True} if normalized else {})})
        return acc_idx

    def save(self, path):
        # rebuild one flat BIN: original views in order, then new views
        blob = bytearray()
        new_bvs = []
        for vi in range(len(self.g.get('bufferViews', []))):
            data = self.views[vi]
            off = len(blob)
            pad = (-len(data)) % 4
            blob.extend(data + b'\x00' * pad)
            bv = self.g['bufferViews'][vi]
            nbv = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
            if 'target' in bv:
                nbv['target'] = bv['target']
            if 'name' in bv:
                nbv['name'] = bv['name']
            if 'byteStride' in bv:
                nbv['byteStride'] = bv['byteStride']
            # drop EXT_meshopt_compression: data is now plain
            new_bvs.append(nbv)
        for data in self._new_views:
            off = len(blob)
            pad = (-len(data)) % 4
            blob.extend(data + b'\x00' * pad)
            new_bvs.append({'buffer': 0, 'byteOffset': off,
                            'byteLength': len(data)})
        self.g['bufferViews'] = new_bvs
        # single plain buffer
        self.g['buffers'] = [{'byteLength': len(blob)}]
        for ext in ('extensionsUsed', 'extensionsRequired'):
            if ext in self.g and 'EXT_meshopt_compression' in self.g[ext]:
                self.g[ext] = [e for e in self.g[ext]
                               if e != 'EXT_meshopt_compression']
                if not self.g[ext]:
                    del self.g[ext]
        js = json.dumps(self.g, separators=(',', ':')).encode('utf-8')
        jpad = (-len(js)) % 4
        with open(path, 'wb') as f:
            f.write(struct.pack('<III', 0x46546C67, 2,
                                12 + 8 + len(js) + jpad + 8 + len(blob)))
            f.write(struct.pack('<II', len(js) + jpad, 0x4E4F534A))
            f.write(js + b' ' * jpad)
            f.write(struct.pack('<II', len(blob), 0x004E4942))
            f.write(blob)


# ---------------------------------------------------------------- nodes
def node_local(node):
    m = np.eye(4)
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=np.float64).reshape(4, 4).T
    t = node.get('translation')
    r = node.get('rotation')
    s = node.get('scale')
    if r:
        x, y, z, w = r
        m[:3, :3] = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    if s:
        m[:3, :3] = m[:3, :3] * np.array(s, dtype=np.float64)
    if t:
        m[:3, 3] = t
    return m


def node_world_matrices(g):
    world = {}

    def walk(i, parent):
        w = parent @ node_local(g['nodes'][i])
        world[i] = w
        for c in g['nodes'][i].get('children', []):
            walk(c, w)

    for s in g['scenes']:
        for n in s['nodes']:
            walk(n, np.eye(4))
    return world


def skin_joints(g, skin_idx=0):
    skin = g['skins'][skin_idx]
    return [g['nodes'][i].get('name', f'node{i}') for i in skin['joints']]


def skeleton_root(g, skin_idx=0):
    """Lowest common ancestor node of the skin's joints (armature space)."""
    skin = g['skins'][skin_idx]
    world = node_world_matrices(g)
    parents = {}
    for s in g['scenes']:
        stack = [(n, None) for n in s['nodes']]
        while stack:
            i, p = stack.pop()
            parents[i] = p
            stack.extend((c, i) for c in g['nodes'][i].get('children', []))
    joints = set(skin['joints'])
    # walk up from first joint until the ancestor covers all joints
    anc = []
    i = skin['joints'][0]
    while i is not None:
        anc.append(i)
        i = parents.get(i)
    def covers(a):
        # every joint is a itself or a descendant of a
        desc = set()
        stack = [a]
        while stack:
            x = stack.pop()
            desc.add(x)
            stack.extend(g['nodes'][x].get('children', []))
        return joints <= desc
    for a in anc:
        if covers(a):
            return a
    return skin['joints'][0]


# ---------------------------------------------------------------- naming
def detect_side(name):
    n = strip_infix(name)
    if n.startswith('Left'):
        return 'L'
    if n.startswith('Right'):
        return 'R'
    nl = name.lower()
    if nl.endswith('_l') or 'left' in nl:
        return 'L'
    if nl.endswith('_r') or 'right' in nl:
        return 'R'
    return None


def strip_infix(name):
    """Remove a 'Lower' infix so side/part/digit parsing keeps working."""
    for side in ('Left', 'Right'):
        if name.startswith(side + 'Lower'):
            return side + name[len(side) + 5:]
    return name


def detect_digit(name):
    nl = strip_infix(name).lower()
    for d in ('thumb', 'index', 'middle', 'ring', 'pinky', 'little'):
        if d in nl:
            return 'pinky' if d == 'little' else d
    return None


def seg_num(name):
    import re
    m = re.search(r'(\d+)\s*$', strip_infix(name))
    return int(m.group(1)) if m else None


def mirror_name(name):
    if name.startswith('Left'):
        return 'Right' + name[4:]
    if name.startswith('Right'):
        return 'Left' + name[5:]
    return None


def region(bone_name):
    """Anatomical region used by the cross-region weight rules."""
    b = strip_infix(bone_name)
    bl = b.lower()
    if 'tail' in bl:
        return 'tail'
    if any(k in bl for k in ('breast', 'pelvis', 'hips', 'spine', 'chest',
                             'neck', 'head', 'jaw')):
        return 'core'
    if b.startswith('Left') and b[4:].startswith(
            ('Hand', 'Shoulder', 'Arm', 'ForeArm')):
        return 'armL'
    if b.startswith('Right') and b[5:].startswith(
            ('Hand', 'Shoulder', 'Arm', 'ForeArm')):
        return 'armR'
    if b.startswith('Left'):
        return 'legL'
    if b.startswith('Right'):
        return 'legR'
    return 'other'


# (dominant-region, other-region) pairs that are never valid above threshold.
# Symmetric: bleed is illegitimate in both directions. Deliberately NOT
# included: arm<->core, leg<->core (legitimate blending at the shoulder/hip
# boundaries) and core<->tail-root (tail grows out of the pelvis; see
# tail_root_joints / is_suspicious_pair).
SUSPICIOUS = {
    ('armL', 'tail'), ('armR', 'tail'),
    ('tail', 'armL'), ('tail', 'armR'),
    ('armL', 'legL'), ('armL', 'legR'),
    ('armR', 'legL'), ('armR', 'legR'),
    ('legL', 'armL'), ('legL', 'armR'),
    ('legR', 'armL'), ('legR', 'armR'),
    ('core', 'tail'), ('tail', 'core'),
    ('legL', 'tail'), ('legR', 'tail'),
    ('tail', 'legL'), ('tail', 'legR'),
    ('armL', 'armR'), ('armR', 'armL'),
}

FLAG_T = 0.12  # influence threshold, matches the 2026-10-23 audit


def tail_root_joints(g, joints):
    """Names of tail-region joints whose parent is not a tail joint.

    Blending between the tail root and the core (hips/pelvis) is anatomically
    expected - the tail grows out of the pelvis - and is exempt from the
    core<->tail cross-region rule.
    """
    name_to_node = {}
    for ni, node in enumerate(g['nodes']):
        if node.get('name'):
            name_to_node[node['name']] = ni
    node_parent = {}
    for ni, node in enumerate(g['nodes']):
        for c in node.get('children', []):
            node_parent[c] = ni
    roots = set()
    for name in joints:
        if region(name) != 'tail':
            continue
        ni = name_to_node.get(name)
        p = node_parent.get(ni)
        pname = g['nodes'][p].get('name') if p is not None else None
        if pname is None or region(pname) != 'tail':
            roots.add(name)
    return roots


def is_suspicious_pair(dreg, oreg, dname, oname, tail_roots):
    if (dreg, oreg) not in SUSPICIOUS:
        return False
    # Exempt tail-root blending with the surrounding body (core/legs): the
    # tail root is anatomically continuous with the pelvis/buttock region.
    # Mid-tail (non-root) blending with non-tail bones is always bleed.
    if 'tail' in (dreg, oreg):
        tail_side = dname if dreg == 'tail' else oname
        other_reg = oreg if dreg == 'tail' else dreg
        if tail_side in tail_roots and other_reg in ('core', 'legL', 'legR'):
            return False
    return True


# ---------------------------------------------------------------- skinning
def skinned_meshes(glb):
    """Yield (node_idx, skin_idx, mesh, prim_idx, prim) for skinned prims."""
    g = glb.g
    out = []
    for ni, node in enumerate(g['nodes']):
        if 'mesh' not in node or 'skin' not in node:
            continue
        mesh = g['meshes'][node['mesh']]
        for pi, prim in enumerate(mesh['primitives']):
            if 'JOINTS_0' in prim['attributes'] and \
               'WEIGHTS_0' in prim['attributes']:
                out.append((ni, node['skin'], mesh, pi, prim))
    return out


def normalize_cap(joints, weights):
    """Normalize to sum 1 and cap at 4 influences (keep largest)."""
    jw = [(int(j), float(w)) for j, w in zip(joints, weights) if w > 1e-9]
    jw.sort(key=lambda t: -t[1])
    jw = jw[:4]
    s = sum(w for _, w in jw)
    if s <= 1e-9:
        return [], []
    jw = [(j, w / s) for j, w in jw]
    return [j for j, _ in jw], [w for _, w in jw]


def nearest_neighbors(src, dst, chunk=20000):
    """For each src point, index of nearest dst point (brute force, chunked)."""
    src = np.asarray(src, dtype=np.float64)
    dst = np.asarray(dst, dtype=np.float64)
    best_i = np.zeros(len(src), dtype=np.int64)
    best_d = np.full(len(src), np.inf)
    for i in range(0, len(src), chunk):
        d = np.linalg.norm(
            src[i:i + chunk, None, :] - dst[None, :, :], axis=2)
        j = d.argmin(axis=1)
        dd = d[np.arange(len(j)), j]
        m = dd < best_d[i:i + chunk]
        best_i[i:i + chunk][m] = j[m]
        best_d[i:i + chunk][m] = dd[m]
    return best_i, best_d


class BoneAdder:
    """Surgical bone creation: new nodes + skin joints + one IBM accessor.

    Usage: adder = BoneAdder(glb); j = adder.add(name, parent, world4x4);
    ...weight work referencing joint indices...; adder.finalize(); glb.save().
    Aborts if the file's IBM convention is not inv(jointWorld).
    """

    def __init__(self, glb):
        self.glb = glb
        self.g = glb.g
        self.world = node_world_matrices(self.g)
        self.name_to_node = {}
        for ni, node in enumerate(self.g['nodes']):
            if node.get('name'):
                self.name_to_node[node['name']] = ni
        self.node_parent = {}
        for ni, node in enumerate(self.g['nodes']):
            for c in node.get('children', []):
                self.node_parent[c] = ni
        self.skin = self.g['skins'][0]
        ibm = glb.decode(self.skin['inverseBindMatrices'],
                         normalize=False).reshape(-1, 4, 4).transpose(0, 2, 1)
        worst = 0.0
        for k, ni in enumerate(self.skin['joints']):
            worst = max(worst,
                        float(np.abs(np.linalg.inv(self.world[ni])
                                     - ibm[k]).max()))
        if worst > 1e-3:
            raise RuntimeError(
                f"IBM convention check failed (max err {worst:.4f}); refusing "
                "bone surgery")
        self._ibm_base = ibm
        self.new = []  # (joint_idx, world_matrix)

    def add(self, name, parent_name, world_matrix):
        if name in self.name_to_node:
            raise RuntimeError(f"bone {name} already exists")
        p_ni = self.name_to_node[parent_name]
        local = np.linalg.inv(self.world[p_ni]) @ np.asarray(
            world_matrix, dtype=np.float64)
        new_ni = len(self.g['nodes'])
        self.g['nodes'].append({
            'name': name,
            'matrix': [float(v) for v in local.T.reshape(-1)],
            'children': [],
        })
        self.g['nodes'][p_ni].setdefault('children', []).append(new_ni)
        self.name_to_node[name] = new_ni
        self.node_parent[new_ni] = p_ni
        self.world[new_ni] = np.asarray(world_matrix, dtype=np.float64)
        joint_idx = len(self.skin['joints'])
        self.skin['joints'].append(new_ni)
        self.new.append((joint_idx, self.world[new_ni]))
        return joint_idx

    def finalize(self):
        if not self.new:
            return
        base = self._ibm_base.transpose(0, 2, 1).reshape(-1, 16)
        extra = np.array([np.linalg.inv(w).T.reshape(16)
                          for _, w in self.new])
        all_ibm = np.concatenate([base, extra], axis=0)
        self.skin['inverseBindMatrices'] = self.glb.add_accessor(
            all_ibm, 5126, 'MAT4')


MIRROR_X = np.diag([-1.0, 1.0, 1.0, 1.0])


def mirror_rigid_x(w):
    """Mirror a rigid transform across the YZ plane (x -> -x)."""
    w = np.asarray(w, dtype=np.float64)
    p = w[:3, 3]
    r = w[:3, :3]
    m = np.diag([-1.0, 1.0, 1.0])
    out = np.eye(4)
    out[:3, :3] = m @ r @ m
    out[:3, 3] = np.array([-p[0], p[1], p[2]])
    return out
