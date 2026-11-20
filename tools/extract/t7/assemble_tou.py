#!/usr/bin/env python3
"""Assemble tou-body.glb from Paul's own T7 parts (Batch C, roster wire-up).

Inputs: per-part umodel glTF exports WITH textures (face, face-hair, hair,
upper, lower). All parts are Paul's own (code pau, pakchunk0) — no other
character's geometry, textures, or weights.

Production rules (repo precedents):
- ONE merged skin on the shared T7 base skeleton (union of part joint sets).
- Core bones renamed to the game's canonical names (kinpo-t8/phantom-t8
  precedent: native skeleton kept, names canonicalized) so the game's
  name-indexed banks bind: Hip->Hips, L_Arm->LeftArm, etc. Facial/helper/
  offset bones keep their T7 names (inert extras; the game ignores them).
- Inverse bind matrices RECOMPUTED from the final node tree (verified
  against the parts' shipped IBMs before scaling: same skeleton).
- Uniform scale so total bounds = 1.75 m with feet at y=0 (the soul-body
  class height: rin/kai/sha/retsu/gyou all 1.75 m in MODEL-STATUS).
- Textures embedded (tga->png), materials carried from the umodel exports.
"""
import json, os, struct, sys
import numpy as np
from pygltflib import GLTF2

RENAME = {}
def _side(t7, wh):
    RENAME[t7] = wh
_side('Hip', 'Hips')
for s_t7, s_wh in [('L', 'Left'), ('R', 'Right')]:
    RENAME[f'{s_t7}_Shoulder'] = f'{s_wh}Shoulder'
    RENAME[f'{s_t7}_Arm'] = f'{s_wh}Arm'
    RENAME[f'{s_t7}_ForeArm'] = f'{s_wh}ForeArm'
    RENAME[f'{s_t7}_Hand'] = f'{s_wh}Hand'
    for f_t7, f_wh in [('Thumb', 'Thumb'), ('Index', 'Index'), ('Middle', 'Middle'),
                       ('Ring', 'Ring'), ('Pinky', 'Pinky')]:
        for i in (1, 2, 3):
            RENAME[f'{s_t7}_{f_t7}{i}'] = f'{s_wh}Hand{f_wh}{i}'
    RENAME[f'{s_t7}_UpLeg'] = f'{s_wh}UpLeg'
    RENAME[f'{s_t7}_Leg'] = f'{s_wh}Leg'
    RENAME[f'{s_t7}_Foot'] = f'{s_wh}Foot'
    RENAME[f'{s_t7}_Toe'] = f'{s_wh}ToeBase'
# Spine1/Spine2/Neck/Head are already canonical in the T7 skeleton.

# Paul's face package skins against a face-variant skeleton whose root/head
# bones are spelled 'Base'/'HEAD' where the body skeleton uses 'BASE'/'Head'.
# PROVEN the same bones: inverse bind matrices match to <=5e-7 (Base weights
# zero vertices in the face mesh; HEAD weights 1,469).
ALIAS = {'Base': 'BASE', 'HEAD': 'Head'}

def node_matrix(n):
    if n.matrix:
        return np.array(n.matrix, dtype=np.float64).reshape(4, 4).T  # column-major -> row
    t = np.array(n.translation or [0, 0, 0], dtype=np.float64)
    r = np.array(n.rotation or [0, 0, 0, 1], dtype=np.float64)
    s = np.array(n.scale or [1, 1, 1], dtype=np.float64)
    x, y, z, w = r
    R = np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=np.float64)
    M = np.eye(4)
    M[:3, :3] = R * s
    M[:3, 3] = t
    return M

def parse_mat(path):
    """umodel .mat dump: Diffuse=<tex>, Normal=<tex>, Other[0]=<mask>."""
    d = {}
    for line in open(path):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            d[k.strip()] = v.strip()
    return d

def find_file(root, basename):
    for dp, _, fs in os.walk(root):
        if basename in fs:
            return os.path.join(dp, basename)
    return None

def main(parts, out_path, target_h=1.75):
    # parts: list of (slot, export_dir) — umodel textured export dirs
    loaded = []
    for slot, d in parts:
        gltfs = []
        for dp, _, fs in os.walk(d):
            for f in fs:
                if f.endswith('.gltf'):
                    gltfs.append(os.path.join(dp, f))
        assert len(gltfs) == 1, (slot, gltfs)
        g = GLTF2().load(gltfs[0])
        mats = {}
        for dp, _, fs in os.walk(d):
            for f in fs:
                if f.endswith('.mat'):
                    mats[os.path.splitext(f)[0]] = parse_mat(os.path.join(dp, f))
        loaded.append((slot, d, g, mats))
    # canonical skeleton: the part with the most joints (upper/lower, 213)
    canon_slot, _, canon, _ = max(loaded, key=lambda t: len(t[2].skins[0].joints) if t[2].skins else 0)
    cnodes = canon.nodes
    cname2idx = {}
    for i, n in enumerate(cnodes):
        if n.name:
            cname2idx[n.name] = i
    # union: add any joint nodes other parts have that canon lacks (by name),
    # appended as children of the scene root bone tree is unsafe — instead
    # require: extra joints must already exist as nodes in canon's tree.
    # (umodel exports the full node tree in every part; skins are subsets.)
    joint_names = []          # merged skin joint order (canonical names)
    joint_raw_names = []      # same order, T7 names (remap key)
    joint_src_node = []       # node index in canon tree
    seen = set()
    for slot, p, g, _m in loaded:
        if not g.skins:
            continue
        for j in g.skins[0].joints:
            nm = ALIAS.get(g.nodes[j].name, g.nodes[j].name)
            if nm in seen:
                continue
            seen.add(nm)
            if nm not in cname2idx:
                raise SystemExit(f'{slot}: joint {nm} has no node in canonical tree')
            joint_names.append(RENAME.get(nm, nm))
            joint_raw_names.append(nm)
            joint_src_node.append(cname2idx[nm])
    print(f'canonical skeleton from {canon_slot}: {len(cnodes)} nodes, merged skin {len(joint_names)} joints')

    # ---- measure total bounds across parts (bind pose, unscaled) ----
    mn = np.array([1e9]*3); mx = np.array([-1e9]*3)
    for slot, p, g, _m in loaded:
        for m in g.meshes or []:
            for pr in m.primitives:
                a = g.accessors[pr.attributes.POSITION]
                mn = np.minimum(mn, a.min); mx = np.maximum(mx, a.max)
    span = mx[1] - mn[1]
    s = target_h / span
    print(f'bounds y [{mn[1]:.3f},{mx[1]:.3f}] span {span:.3f} -> scale {s:.4f}, ground shift {-mn[1]*s:.4f}')

    # ---- build output with pygltflib by hand-rolling JSON + one BIN ----
    # Strategy: start from canon GLB structure via GLTF2, then graft.
    # Simpler + fully controlled: assemble raw JSON and buffers manually.
    import io
    from PIL import Image

    buffers = bytearray()
    bviews = []   # (offset,len)
    accessors = []
    def add_buffer(data: bytes, target=None):
        off = len(buffers)
        pad = (4 - (len(data) % 4)) % 4
        buffers.extend(data); buffers.extend(b'\x00' * pad)
        bviews.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data),
                       **({'target': target} if target else {})})
        return len(bviews) - 1
    def add_accessor(data: bytes, comp, typ, count, mn_=None, mx_=None, target=34962):
        bv = add_buffer(data, target)
        acc = {'bufferView': bv, 'componentType': comp, 'type': typ, 'count': count}
        if mn_ is not None: acc['min'] = mn_
        if mx_ is not None: acc['max'] = mx_
        accessors.append(acc)
        return len(accessors) - 1

    CT = {'SCALAR': 5126, 'UNSIGNED_BYTE': 5121, 'UNSIGNED_SHORT': 5123, 'UNSIGNED_INT': 5125, 'FLOAT': 5126}
    blob_cache = {}
    def part_blob(g, expdir):
        if id(g) not in blob_cache:
            b = g.binary_blob()
            if b is None:
                uri = os.path.basename(g.buffers[0].uri)
                with open(find_file(expdir, uri), 'rb') as fh:
                    b = fh.read()
            blob_cache[id(g)] = b
        return blob_cache[id(g)]
    def read_accessor(g, ai, expdir=None):
        a = g.accessors[ai]
        bv = g.bufferViews[a.bufferView]
        buf = part_blob(g, expdir)
        off = (bv.byteOffset or 0) + (a.byteOffset or 0)
        ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a.type]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a.componentType]
        arr = np.frombuffer(buf, dtype=dt, count=a.count * ncomp, offset=off)
        arr = arr.reshape(a.count, ncomp) if ncomp > 1 else arr.copy()
        if getattr(a, 'normalized', False):
            # umodel exports WEIGHTS_0 as normalized ubyte (0-255 == 0.0-1.0)
            denom = {5121: 255.0, 5123: 65535.0}[a.componentType]
            arr = arr.astype(np.float32) / denom
        return arr, a

    out = {'asset': {'version': '2.0', 'generator': 'wh-tou-assemble (umodel parts, Paul pau)'},
           'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
           'skins': [], 'materials': [], 'textures': [], 'images': [], 'samplers': [],
           'accessors': accessors, 'bufferViews': bviews, 'buffers': []}

    # ---- nodes: clone canon tree (skip its mesh node 0), rename + scale ----
    # canon node 0 is the part's mesh node; skeleton root is its child.
    mesh_node = cnodes[0]
    skel_root = mesh_node.children[0]
    keep = []
    stack = [skel_root]
    while stack:
        i = stack.pop(); keep.append(i); stack.extend(cnodes[i].children or [])
    keep_set = set(keep)
    old2new = {}
    for i in keep:
        n = cnodes[i]
        nn = {'name': RENAME.get(n.name, n.name)}
        if n.translation:
            t = np.array(n.translation) * s
            if i == skel_root:
                t[1] += -mn[1] * s
            nn['translation'] = t.tolist()
        if n.rotation: nn['rotation'] = list(n.rotation)
        if n.scale: nn['scale'] = list(n.scale)
        if n.matrix: raise SystemExit('matrix nodes unsupported')
        old2new[i] = len(out['nodes'])
        out['nodes'].append(nn)
    for i in keep:
        ch = [old2new[c] for c in (cnodes[i].children or []) if c in keep_set]
        if ch: out['nodes'][old2new[i]]['children'] = ch
    out['scenes'][0]['nodes'].append(old2new[skel_root])
    joint_new_idx = [old2new[i] for i in joint_src_node]

    # ---- IBMs recomputed from the final tree ----
    parent = {}
    for i, n in enumerate(out['nodes']):
        for c in n.get('children', []):
            parent[c] = i
    def dict_matrix(n):
        t = np.array(n.get('translation', [0, 0, 0]), dtype=np.float64)
        r = np.array(n.get('rotation', [0, 0, 0, 1]), dtype=np.float64)
        sc = np.array(n.get('scale', [1, 1, 1]), dtype=np.float64)
        x, y, z, w = r
        R = np.array([
            [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=np.float64)
        M = np.eye(4); M[:3, :3] = R * sc; M[:3, 3] = t
        return M
    def global_mat(i):
        chain = []
        while i is not None:
            chain.append(i); i = parent.get(i)
        M = np.eye(4)
        for i in reversed(chain):
            M = M @ dict_matrix(out['nodes'][i])
        return M
    ibms = []
    for ni in joint_new_idx:
        ibms.append(np.linalg.inv(global_mat(ni)))
    ibm_arr = np.stack([M.T.reshape(-1) for M in ibms]).astype(np.float32)  # column-major
    ibm_acc = add_accessor(ibm_arr.tobytes(), 5126, 'MAT4', len(ibms), target=None)
    out['skins'].append({'joints': joint_new_idx, 'inverseBindMatrices': ibm_acc,
                         'name': 'SKT_CH_base (pau)'})

    # ---- materials/images: built from umodel .mat dumps + exported TGAs ----
    img_cache = {}
    def embed_tga(path, name):
        if path in img_cache: return img_cache[path]
        im = Image.open(path)
        if im.mode in ('RGBA', 'LA', 'PA'):
            alpha = im.getchannel('A')
            if alpha.getextrema()[0] == 255:
                im = im.convert('RGB')   # opaque texture: alpha carries nothing
            else:
                im = im.convert('RGBA')
        else:
            im = im.convert('RGB')
        bio = io.BytesIO(); im.save(bio, 'PNG')
        bv = add_buffer(bio.getvalue())
        out['images'].append({'bufferView': bv, 'mimeType': 'image/png', 'name': name})
        img_cache[path] = len(out['images']) - 1
        return img_cache[path]
    def add_tex(path, name):
        oi = embed_tga(path, name)
        out['textures'].append({'sampler': 0, 'source': oi})
        return len(out['textures']) - 1
    out['samplers'].append({'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497})

    name2merged_joint = {nm: k for k, nm in enumerate(joint_raw_names)}
    unresolved = []

    total_verts = 0
    for slot, expdir, g, matdumps in loaded:
        # material remap for this part, keyed by the gltf material name
        mat_map = {}
        for mi, m in enumerate(g.materials or []):
            mname = m.name or f'{slot}_mat{mi}'
            nm = {'name': mname}
            dump = matdumps.get(mname)
            pbr = {'metallicFactor': 0.0, 'roughnessFactor': 0.9}
            if dump and dump.get('Flat'):
                pbr['baseColorFactor'] = [float(x) for x in dump['Flat'].split(',')]
                mat_map[mi] = len(out['materials'])
                nm['pbrMetallicRoughness'] = pbr
                out['materials'].append(nm)
                continue
            if dump and dump.get('Diffuse'):
                tga = find_file(expdir, dump['Diffuse'] + '.tga')
                if tga:
                    pbr['baseColorTexture'] = {'index': add_tex(tga, dump['Diffuse'])}
            if dump and dump.get('Normal'):
                tga = find_file(expdir, dump['Normal'] + '.tga')
                if tga:
                    nm['normalTexture'] = {'index': add_tex(tga, dump['Normal'])}
            if 'baseColorTexture' not in pbr:
                # No diffuse from the game's own material dump: authored flat
                # colour (the material audit's authoredFlat class; kai's hair
                # repair precedent). Recorded in the build report, never a
                # borrowed texture.
                unresolved.append(f'{slot}:{mname}')
                pbr['baseColorFactor'] = [0.35, 0.27, 0.22, 1.0]
            nm['pbrMetallicRoughness'] = pbr
            mat_map[mi] = len(out['materials'])
            out['materials'].append(nm)
        # joint remap for this part: part skin joint k -> merged joint index
        part_joint_names = [ALIAS.get(g.nodes[j].name, g.nodes[j].name) for j in g.skins[0].joints] if g.skins else []
        remap = np.array([name2merged_joint[nm] for nm in part_joint_names], dtype=np.uint32)
        for mi, m in enumerate(g.meshes or []):
            prims = []
            for pr in m.primitives:
                attrs = {}
                pos, pa = read_accessor(g, pr.attributes.POSITION, expdir)
                pos = pos.astype(np.float32) * s
                pos[:, 1] += -mn[1] * s
                attrs['POSITION'] = add_accessor(pos.tobytes(), 5126, 'VEC3', len(pos),
                                                 pos.min(axis=0).tolist(), pos.max(axis=0).tolist())
                total_verts += len(pos)
                if pr.attributes.NORMAL is not None:
                    arr, _ = read_accessor(g, pr.attributes.NORMAL, expdir)
                    attrs['NORMAL'] = add_accessor(arr.astype(np.float32).tobytes(), 5126, 'VEC3', len(arr))
                if pr.attributes.TEXCOORD_0 is not None:
                    arr, _ = read_accessor(g, pr.attributes.TEXCOORD_0, expdir)
                    attrs['TEXCOORD_0'] = add_accessor(arr.astype(np.float32).tobytes(), 5126, 'VEC2', len(arr))
                jts, _ = read_accessor(g, pr.attributes.JOINTS_0, expdir)
                jts = remap[jts.astype(np.uint32)].astype(np.uint16 if len(joint_names) < 65536 else np.uint32)
                attrs['JOINTS_0'] = add_accessor(jts.tobytes(), 5123 if jts.dtype == np.uint16 else 5125, 'VEC4', len(jts), target=34962)
                wts, _ = read_accessor(g, pr.attributes.WEIGHTS_0, expdir)
                attrs['WEIGHTS_0'] = add_accessor(wts.astype(np.float32).tobytes(), 5126, 'VEC4', len(wts))
                idx, ia = read_accessor(g, pr.indices, expdir)
                idx = idx.astype(np.uint32)
                iacc = add_accessor(idx.tobytes(), 5125, 'SCALAR', len(idx), target=34963)
                np_ = {'attributes': attrs, 'indices': iacc}
                if pr.material is not None: np_['material'] = mat_map[pr.material]
                prims.append(np_)
            out['meshes'].append({'name': f'{slot}_{m.name or mi}', 'primitives': prims})
            out['nodes'].append({'name': f'tou_{slot}_{mi}', 'mesh': len(out['meshes']) - 1, 'skin': 0})
            out['scenes'][0]['nodes'].append(len(out['nodes']) - 1)
    out['buffers'].append({'byteLength': len(buffers)})
    js = json.dumps(out).encode()
    pad = (4 - (len(js) % 4)) % 4
    js += b' ' * pad
    binpad = (4 - (len(buffers) % 4)) % 4
    buffers.extend(b'\x00' * binpad)
    with open(out_path, 'wb') as f:
        f.write(b'glTF')
        f.write(struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(buffers)))
        f.write(struct.pack('<I4s', len(js), b'JSON')); f.write(js)
        f.write(struct.pack('<I4s', len(buffers), b'BIN\x00')); f.write(buffers)
    print(f'wrote {out_path}: {os.path.getsize(out_path)} B, {total_verts} verts, '
          f'{len(out["meshes"])} meshes, {len(joint_names)} joints, {len(out["images"])} images, {len(out["materials"])} materials')
    if unresolved:
        print('UNRESOLVED materials (authored flat colour used):', unresolved)

if __name__ == '__main__':
    parts = []
    for a in sys.argv[1:-1]:
        slot, p = a.split('=', 1)
        parts.append((slot, p))
    main(parts, sys.argv[-1])
