#!/usr/bin/env python3
"""
Direct mesh extractor for BLENDER17-01 custom format files (v2).

Bypasses Blender entirely. Parses 32-byte block headers, uses the embedded
DNA for struct layouts, and resolves old save-time pointers through the
block-header pointer map.

File layout (reverse-engineered 2026-10-22, see docs/research/
blend17-01-variant-repair-2026-10-22.md on PR #722):
  - 17-byte header: BLENDER17-01v050X (often wrapped in a zstd stream
    mislabeled ".blend")
  - 32-byte block headers: code(4) sdna_idx(4) old_ptr(8) size(4) unk(4)
    count(4) pad(4). sdna_idx is the STRC struct index. Mesh arrays
    (mvert/mloop/mpoly) are stored as *untyped* DATA blocks (struct
    'raw_data', sdna 0) matched by size; struct pointers in Mesh are NULL.

Extracts per mesh: vertices, faces, UV layers, material slots (name +
base color), deform weights. Per file: armatures (bone tree).

Outputs per mesh: <name>.obj (+ shared .mtl), <name>.json (meta+weights).
Per file: armature_<n>.json.

Usage:
    python3 extract.py <decompressed.blend> <output_dir>/
    python3 extract.py --auto <file.blend> <output_dir>/   # auto-decompress zstd
"""
import struct
import sys
import os
import re
import json
import tempfile

ZSTD_MAGIC = b'\x28\xb5\x2f\xfd'
HEADER_MAGIC = b'BLENDER17-01'


def detect(path):
    """Return 'blend17-01' / 'zstd' / None for a file path."""
    with open(path, 'rb') as f:
        head = f.read(17)
    if head.startswith(HEADER_MAGIC):
        return 'blend17-01'
    if head[:4] == ZSTD_MAGIC:
        return 'zstd'
    return None


def decompress_zstd(src, dst):
    import zstandard
    dctx = zstandard.ZstdDecompressor()
    with open(src, 'rb') as fin, open(dst, 'wb') as fout:
        dctx.copy_stream(fin, fout)


def parse_dna(dna_data):
    """Parse SDNA -> (types, type_lens, structs dict, struct_order list)."""
    assert dna_data[0:4] == b'SDNA'
    off = 12
    num_names, = struct.unpack('<I', dna_data[8:12])
    names = []
    for _ in range(num_names):
        end = dna_data.index(b'\x00', off)
        names.append(dna_data[off:end].decode('ascii', errors='replace'))
        off = end + 1
    while off % 4:
        off += 1

    assert dna_data[off:off + 4] == b'TYPE'
    num_types, = struct.unpack('<I', dna_data[off + 4:off + 8])
    off += 8
    types = []
    for _ in range(num_types):
        end = dna_data.index(b'\x00', off)
        types.append(dna_data[off:end].decode('ascii', errors='replace'))
        off = end + 1
    while off % 4:
        off += 1

    assert dna_data[off:off + 4] == b'TLEN'
    off += 4
    lengths = struct.unpack(f'<{num_types}H', dna_data[off:off + num_types * 2])
    off += num_types * 2
    while off % 4:
        off += 1

    assert dna_data[off:off + 4] == b'STRC'
    num_structs, = struct.unpack('<I', dna_data[off + 4:off + 8])
    off += 8
    structs = {}
    order = []
    for _ in range(num_structs):
        type_idx, = struct.unpack('<H', dna_data[off:off + 2])
        num_fields, = struct.unpack('<H', dna_data[off + 2:off + 4])
        off += 4
        fields = []
        for _ in range(num_fields):
            t_idx, n_idx = struct.unpack('<HH', dna_data[off:off + 4])
            off += 4
            fields.append((types[t_idx], names[n_idx]))
        structs[types[type_idx]] = fields
        order.append(types[type_idx])

    return types, lengths, structs, order


def field_offset(structs, types, lengths, struct_name, field_name):
    """Return (byte_offset, field_size, is_pointer) for a struct field."""
    offset = 0
    for tname, fname in structs[struct_name]:
        is_ptr = fname.startswith('*')
        clean = fname.lstrip('*')
        m = re.match(r'(.+)\[(\d+)\]', clean)
        if m:
            base, arr = m.group(1), int(m.group(2))
        else:
            base, arr = clean, 1
        fsize = 8 * arr if is_ptr else lengths[types.index(tname)] * arr
        if base == field_name:
            return offset, fsize, is_ptr
        offset += fsize
    return None


def struct_size(structs, types, lengths, struct_name):
    total = 0
    for tname, fname in structs[struct_name]:
        is_ptr = fname.startswith('*')
        clean = fname.lstrip('*')
        m = re.match(r'(.+)\[(\d+)\]', clean)
        arr = int(m.group(2)) if m else 1
        total += 8 * arr if is_ptr else lengths[types.index(tname)] * arr
    return total


def walk_blocks(data):
    """Walk 32-byte block headers. Returns list of dicts."""
    off = 17
    blocks = []
    n = len(data)
    while off < n - 32:
        code = data[off:off + 4]
        sdna, = struct.unpack('<I', data[off + 4:off + 8])
        old_ptr, = struct.unpack('<Q', data[off + 8:off + 16])
        size, = struct.unpack('<I', data[off + 16:off + 20])
        count, = struct.unpack('<I', data[off + 24:off + 28])
        if size < 0 or off + 32 + size > n:
            print(f"  invalid block at {off} ({code}), stopping walk")
            break
        blocks.append({'code': code, 'off': off, 'ptr': old_ptr,
                       'size': size, 'sdna': sdna, 'count': count})
        off += 32 + size
    return blocks


def block_bytes(data, blk):
    return data[blk['off'] + 32:blk['off'] + 32 + blk['size']]


def id_name(buf, name_off):
    raw = buf[name_off:name_off + 66].split(b'\x00')[0]
    try:
        s = raw.decode('ascii', errors='replace')
    except Exception:
        s = ''
    s = s[2:] if len(s) > 2 else s  # strip 2-char ID prefix (ME/MA/...)
    s = re.sub(r'[^\w\-]', '_', s)
    return s or 'unnamed'


def is_raw_block(blk, struct_order):
    """Untyped array DATA block? (struct 'raw_data', 0 fields)."""
    return blk['code'] == b'DATA' and struct_order[blk['sdna']] == 'raw_data'


def classify_loop_block(buf, totvert, sample=512):
    """Is an untyped totloop*8 block MLoop (int v,e pairs) or UV (float2)?

    MLoop entries are small non-negative ints (v < totvert); UV floats
    reinterpreted as int32 are almost always huge. Score both readings.
    """
    n = min(len(buf) // 8, sample)
    if n == 0:
        return 'uv'
    mloop_ok = 0
    uv_ok = 0
    for i in range(n):
        v, e = struct.unpack('<2i', buf[i * 8:i * 8 + 8])
        if 0 <= v < totvert and 0 <= e < 100_000_000:
            mloop_ok += 1
        u, w = struct.unpack('<2f', buf[i * 8:i * 8 + 8])
        if -100.0 <= u <= 100.0 and -100.0 <= w <= 100.0:
            uv_ok += 1
    # A real MLoop block scores ~1.0 as mloop; a real UV block scores ~1.0
    # as uv and ~0 as mloop (float bit patterns are huge as int32).
    if mloop_ok == n and uv_ok < n:
        return 'mloop'
    if uv_ok == n and mloop_ok < n:
        return 'uv'
    # Tie-break: every mesh needs exactly one MLoop block; handled by caller.
    return 'mloop' if mloop_ok >= uv_ok else 'uv'

def extract_materials(data, blocks, structs, types, lengths, struct_order):
    """MA blocks -> ordered list of {name, r, g, b, roughness, metallic}."""
    mats = []
    id_off = field_offset(structs, types, lengths, 'ID', 'name')[0]
    r_off = field_offset(structs, types, lengths, 'Material', 'r')[0]
    rough_off = field_offset(structs, types, lengths, 'Material', 'roughness')[0]
    metal_off = field_offset(structs, types, lengths, 'Material', 'metallic')[0]
    for blk in blocks:
        if blk['code'] != b'MA\x00\x00':
            continue
        buf = block_bytes(data, blk)
        name = id_name(buf, id_off)
        r, g, b = struct.unpack('<3f', buf[r_off:r_off + 12])
        rough, = struct.unpack('<f', buf[rough_off:rough_off + 4])
        metal, = struct.unpack('<f', buf[metal_off:metal_off + 4])
        mats.append({'name': name, 'r': r, 'g': g, 'b': b,
                     'roughness': rough, 'metallic': metal,
                     'ptr': blk['ptr']})
    return mats


def _ptr(buf, off):
    return struct.unpack('<Q', buf[off:off + 8])[0]


def _cstr(b):
    return b.split(b'\x00')[0].decode('utf-8', errors='replace')


# Principled/BSDF input socket -> MTL channel
_SOCKET_CHANNEL = {'Base Color': 'map_Kd', 'Color': 'map_Kd',
                   'Emission': 'map_Ke', 'Emission Color': 'map_Ke',
                   'Normal': 'norm', 'Roughness': 'map_Pr',
                   'Metallic': 'map_Pm', 'Alpha': 'map_d'}


def _resolve_external(path, src_dir):
    """Blender '//rel\\path.png' -> existing file under src_dir (or None)."""
    if not path or not src_dir:
        return None
    rel = path[2:] if path.startswith('//') else path
    rel = rel.replace('\\', '/')
    while '//' in rel:
        rel = rel.replace('//', '/')
    base = os.path.basename(rel)
    for cand in (os.path.join(src_dir, rel), os.path.join(src_dir, 'textures', base),
                 os.path.join(src_dir, base)):
        if os.path.isfile(cand):
            return cand
    return None


def extract_images(data, blocks, structs, types, lengths, ptr_map,
                   src_dir=None):
    """IM blocks -> {old_ptr: {name, packed: bytes|None}} (packed data
    followed Image.packedfiles -> ImagePackedFile -> PackedFile -> data)."""
    fo = lambda s, f: (field_offset(structs, types, lengths, s, f) or (None,))[0]
    id_off = fo('ID', 'name')
    pfs_off = fo('Image', 'packedfiles')
    pf_off = fo('Image', 'packedfile')
    ipf_pf = fo('ImagePackedFile', 'packedfile')
    pf_size, pf_data = fo('PackedFile', 'size'), fo('PackedFile', 'data')
    path_off = fo('Image', 'filepath')
    if path_off is None:
        path_off = fo('Image', 'name')
    images = {}
    for blk in blocks:
        if blk['code'] != b'IM\x00\x00':
            continue
        buf = block_bytes(data, blk)
        name = _cstr(buf[id_off + 2:id_off + 66])
        pfb = None
        if pfs_off is not None:
            ipf = ptr_map.get(_ptr(buf, pfs_off))
            if ipf and ipf_pf is not None:
                pfb = ptr_map.get(_ptr(block_bytes(data, ipf), ipf_pf))
        if pfb is None and pf_off is not None:
            pfb = ptr_map.get(_ptr(buf, pf_off))
        packed = None
        if pfb is not None:
            pbuf = block_bytes(data, pfb)
            size, = struct.unpack('<i', pbuf[pf_size:pf_size + 4])
            db = ptr_map.get(_ptr(pbuf, pf_data))
            if db is not None and size > 0:
                packed = block_bytes(data, db)[:size]
        filepath = _cstr(buf[path_off:path_off + 1024]) if path_off is not None else ''
        if packed is None:
            ext = _resolve_external(filepath, src_dir)
            if ext:
                with open(ext, 'rb') as ef:
                    packed = ef.read()
        images[blk['ptr']] = {'name': name, 'packed': packed,
                              'filepath': filepath}
    return images


def material_textures(data, mat_blk, structs, types, lengths, ptr_map,
                      images):
    """Walk a Material's node tree: for every Image Texture node, follow
    links downstream to the shader input it feeds and return
    {channel: image_ptr}. Unlinked image nodes fall back to map_Kd."""
    fo = lambda s, f: (field_offset(structs, types, lengths, s, f) or (None,))[0]
    nt_off = fo('Material', 'nodetree')
    if nt_off is None:
        return {}
    nt = ptr_map.get(_ptr(block_bytes(data, mat_blk), nt_off))
    if nt is None:
        return {}
    nbuf = block_bytes(data, nt)
    nodes = {}
    cur = _ptr(nbuf, fo('bNodeTree', 'nodes'))
    seen = set()
    o_idn, o_id, o_next = fo('bNode', 'idname'), fo('bNode', 'id'), fo('bNode', 'next')
    while cur and cur in ptr_map and cur not in seen:
        seen.add(cur)
        b = block_bytes(data, ptr_map[cur])
        nodes[cur] = {'idname': _cstr(b[o_idn:o_idn + 64]),
                      'id': _ptr(b, o_id)}
        cur = _ptr(b, o_next)
    links = []
    cur = _ptr(nbuf, fo('bNodeTree', 'links'))
    seen = set()
    l_next, l_fn, l_tn, l_ts = (fo('bNodeLink', f) for f in
                                ('next', 'fromnode', 'tonode', 'tosock'))
    s_name = fo('bNodeSocket', 'name')
    while cur and cur in ptr_map and cur not in seen:
        seen.add(cur)
        b = block_bytes(data, ptr_map[cur])
        sock = ptr_map.get(_ptr(b, l_ts))
        sname = _cstr(block_bytes(data, sock)[s_name:s_name + 64]) if sock else ''
        links.append((_ptr(b, l_fn), _ptr(b, l_tn), sname))
        cur = _ptr(b, l_next)
    shaders = ('ShaderNodeBsdf', 'ShaderNodeEmission')

    def downstream(node, depth=0):
        """-> socket name on the first shader node this node feeds."""
        if depth > 12:
            return None
        best = None
        for fn, tn, sname in links:
            if fn != node or tn not in nodes:
                continue
            tid = nodes[tn]['idname']
            if tid.startswith(shaders):
                if tid == 'ShaderNodeEmission':
                    return 'Emission'
                if sname in _SOCKET_CHANNEL:
                    return sname
                continue
            if tid == 'ShaderNodeNormalMap':
                return 'Normal'
            r = downstream(tn, depth + 1)
            if r and (best is None or r in ('Base Color', 'Color')):
                best = r
        return best

    out = {}
    for np_, n in nodes.items():
        if n['idname'] != 'ShaderNodeTexImage' or n['id'] not in images:
            continue
        ch = _SOCKET_CHANNEL.get(downstream(np_) or 'Base Color', 'map_Kd')
        out.setdefault(ch, n['id'])
    return out


def mesh_material_slots(data, me_buf, totcol, structs, types, lengths,
                        ptr_map):
    """Mesh.mat (array of Material*) -> list of MA blocks (or None),
    indexed by the mesh's own material slot (poly mat_nr)."""
    off = (field_offset(structs, types, lengths, 'Mesh', 'mat') or (None,))[0]
    if off is None or totcol <= 0:
        return []
    arr = ptr_map.get(_ptr(me_buf, off))
    if arr is None:
        return [None] * totcol
    abuf = block_bytes(data, arr)
    return [ptr_map.get(_ptr(abuf, i * 8)) if (i + 1) * 8 <= len(abuf)
            else None for i in range(totcol)]


def object_material_overrides(data, blocks, structs, types, lengths,
                              ptr_map):
    """{mesh_old_ptr: {slot: MA block}} for Object-linked slots
    (Object.matbits[i] != 0 means slot i is linked to the object)."""
    fo = lambda s, f: (field_offset(structs, types, lengths, s, f) or (None,))[0]
    o_data, o_mat, o_bits, o_tc = (fo('Object', f) for f in
                                   ('data', 'mat', 'matbits', 'totcol'))
    res = {}
    if None in (o_data, o_mat, o_bits, o_tc):
        return res
    for blk in blocks:
        if blk['code'] != b'OB\x00\x00':
            continue
        b = block_bytes(data, blk)
        tc, = struct.unpack('<i', b[o_tc:o_tc + 4])
        mats, bits = ptr_map.get(_ptr(b, o_mat)), ptr_map.get(_ptr(b, o_bits))
        if tc <= 0 or not mats or not bits:
            continue
        mb, bb = block_bytes(data, mats), block_bytes(data, bits)
        for i in range(min(tc, len(bb), len(mb) // 8)):
            if bb[i]:
                ma = ptr_map.get(_ptr(mb, i * 8))
                if ma is not None:
                    res.setdefault(_ptr(b, o_data), {})[i] = ma
    return res


def extract_armatures(data, blocks, structs, types, lengths, struct_order,
                      ptr_map):
    """AR blocks -> bone trees via bonebase/childbase ListBase chains."""
    armatures = []
    id_off = field_offset(structs, types, lengths, 'ID', 'name')[0]
    bb_off = field_offset(structs, types, lengths, 'bArmature', 'bonebase')[0]
    # Bone field offsets
    bone_offs = {}
    for fn in ['name', 'head', 'tail', 'parent', 'next', 'prev', 'childbase']:
        r = field_offset(structs, types, lengths, 'Bone', fn)
        bone_offs[fn] = r[0] if r else None

    def read_bone(blk, parent_name):
        buf = block_bytes(data, blk)
        name = buf[bone_offs['name']:bone_offs['name'] + 64] \
            .split(b'\x00')[0].decode('ascii', errors='replace')
        head = struct.unpack('<3f', buf[bone_offs['head']:bone_offs['head'] + 12])
        tail = struct.unpack('<3f', buf[bone_offs['tail']:bone_offs['tail'] + 12])
        node = {'name': name, 'head': list(head), 'tail': list(tail),
                'parent': parent_name, 'children': []}
        # children via childbase ListBase (first pointer)
        cb_first, = struct.unpack('<Q', buf[bone_offs['childbase']:
                                            bone_offs['childbase'] + 8])
        cur = cb_first
        seen = set()
        while cur and cur not in seen:
            seen.add(cur)
            child_blk = ptr_map.get(cur)
            if not child_blk:
                break
            nxt_buf = block_bytes(data, child_blk)
            nxt, = struct.unpack('<Q', nxt_buf[bone_offs['next']:
                                               bone_offs['next'] + 8])
            node['children'].append(read_bone(child_blk, name))
            cur = nxt
        return node

    for blk in blocks:
        if blk['code'] != b'AR\x00\x00':
            continue
        buf = block_bytes(data, blk)
        name = id_name(buf, id_off)
        first, _ = struct.unpack('<2Q', buf[bb_off:bb_off + 16])
        bones = []
        cur = first
        seen = set()
        while cur and cur not in seen:
            seen.add(cur)
            bblk = ptr_map.get(cur)
            if not bblk:
                break
            bbuf = block_bytes(data, bblk)
            nxt, = struct.unpack('<Q', bbuf[bone_offs['next']:
                                           bone_offs['next'] + 8])
            bones.append(read_bone(bblk, None))
            cur = nxt
        armatures.append({'name': name, 'bones': bones})
    return armatures


def count_bones(bones):
    n = 0
    for b in bones:
        n += 1 + count_bones(b['children'])
    return n


def extract_weights(data, blocks, structs, types, lengths, struct_order,
                    ptr_map, totvert, anchor_off):
    """MDeformVert typed block (size totvert*16) -> {vidx: [[def_nr, w]]}.

    anchor_off: file offset to prefer (near the mesh's other arrays).
    Returns (weights, deformvert_block_or_None).
    """
    dv_size = struct_size(structs, types, lengths, 'MDeformVert')
    cands = [b for b in blocks
             if b['code'] == b'DATA'
             and struct_order[b['sdna']] == 'MDeformVert'
             and b['size'] == totvert * dv_size]
    if not cands:
        return {}, None
    # prefer the candidate nearest the mesh's arrays
    cands.sort(key=lambda b: abs(b['off'] - anchor_off))
    dvb = cands[0]
    buf = block_bytes(data, dvb)
    weights = {}
    for v in range(totvert):
        dw_ptr, = struct.unpack('<Q', buf[v * dv_size:v * dv_size + 8])
        totw, = struct.unpack('<i', buf[v * dv_size + 8:v * dv_size + 12])
        if not dw_ptr or totw <= 0:
            continue
        wblk = ptr_map.get(dw_ptr)
        if not wblk:
            continue
        wbuf = block_bytes(data, wblk)
        pairs = []
        for k in range(totw):
            if (k + 1) * 8 > len(wbuf):
                break
            w, dn = struct.unpack('<fi', wbuf[k * 8:k * 8 + 8])
            if w > 0:
                pairs.append([dn, round(float(w), 6)])
        if pairs:
            weights[v] = pairs
    return weights, dvb

def sanitize(name):
    s = re.sub(r'[^\w\-]', '_', name)
    return s or 'unnamed'


def extract_blend17(blend_path, out_dir, include_weights=True, src_dir=None):
    """src_dir: folder of the ORIGINAL .blend, used to resolve external
    (non-packed) '//textures/..' image paths."""
    with open(blend_path, 'rb') as f:
        data = f.read()

    header = data[:17]
    assert header.startswith(HEADER_MAGIC), f"Not a BLENDER17-01 file: {header}"
    print(f"Header: {header}")
    print(f"File size: {len(data)}")

    blocks = walk_blocks(data)
    print(f"Total blocks: {len(blocks)}")
    ptr_map = {b['ptr']: b for b in blocks if b['ptr']}

    dna_blocks = [b for b in blocks if b['code'] == b'DNA1']
    if not dna_blocks:
        raise RuntimeError(
            f"{blend_path}: no DNA1 block found ({len(blocks)} blocks) — "
            f"file is truncated or not a real BLENDER17-01 mesh file")
    dnab = dna_blocks[0]
    types, lengths, structs, struct_order = parse_dna(
        block_bytes(data, dnab))
    print(f"DNA: {len(types)} types, {len(structs)} structs")
    # NOTE: this fork does NOT write legacy MVert/MLoop/MPoly arrays.
    # Mesh arrays are raw_data blocks: positions tv*12 float3,
    # loop_verts tl*4 int32, loop_uvs tl*8 float2,
    # poly_offsets (tp+1)*4 int32, poly_matidx tp*1 uint8.

    id_off = field_offset(structs, types, lengths, 'ID', 'name')[0]
    tv_off = field_offset(structs, types, lengths, 'Mesh', 'totvert')[0]
    tl_off = field_offset(structs, types, lengths, 'Mesh', 'totloop')[0]
    tp_off = field_offset(structs, types, lengths, 'Mesh', 'totpoly')[0]
    tc_off = field_offset(structs, types, lengths, 'Mesh', 'totcol')[0]

    materials = extract_materials(data, blocks, structs, types, lengths,
                                  struct_order)
    print(f"Materials: {len(materials)}")
    mat_by_ptr = {m['ptr']: m for m in materials}
    ma_blocks = {b['ptr']: b for b in blocks if b['code'] == b'MA\x00\x00'}
    images = extract_images(data, blocks, structs, types, lengths, ptr_map,
                            src_dir or os.path.dirname(os.path.abspath(blend_path)))
    tex_dir = os.path.join(out_dir, 'textures')
    image_files = {}  # image ptr -> relative path
    for ip, im in images.items():
        if im['packed'] is None:
            continue
        os.makedirs(tex_dir, exist_ok=True)
        fn = sanitize(os.path.splitext(im['name'])[0])
        ext = '.png' if im['packed'][:4] == b'\x89PNG' else (
            '.jpg' if im['packed'][:2] == b'\xff\xd8' else '.bin')
        rel = f"textures/{fn}{ext}"
        with open(os.path.join(out_dir, rel), 'wb') as tf:
            tf.write(im['packed'])
        image_files[ip] = rel
    print(f"Images: {len(images)} ({len(image_files)} packed/resolved -> textures/)")
    for ip, im in images.items():
        if ip not in image_files and im['name'] not in ('Render Result', 'Viewer Node'):
            print(f"  [no data] image {im['name']!r} path={im['filepath']!r}")
    mat_tex = {mp: {ch: image_files[ip] for ch, ip in material_textures(
        data, mb, structs, types, lengths, ptr_map, images).items()
        if ip in image_files} for mp, mb in ma_blocks.items()}
    ob_over = object_material_overrides(data, blocks, structs, types,
                                        lengths, ptr_map)
    armatures = extract_armatures(data, blocks, structs, types, lengths,
                                  struct_order, ptr_map)
    nbones = sum(count_bones(a['bones']) for a in armatures)
    print(f"Armatures: {len(armatures)} ({nbones} bones)")

    os.makedirs(out_dir, exist_ok=True)
    claimed = set()  # raw block offsets already assigned
    mesh_count = 0
    used_names = set()

    def unique_name(base):
        n = base
        i = 1
        while n in used_names:
            n = f"{base}_{i}"
            i += 1
        used_names.add(n)
        return n

    def claim_raw_valid(size, anchor_off, validator):
        """Nearest unclaimed raw_data block of `size` passing validator."""
        cands = [b for b in blocks
                 if b['off'] not in claimed
                 and is_raw_block(b, struct_order)
                 and b['size'] == size]
        cands.sort(key=lambda b: abs(b['off'] - anchor_off))
        for c in cands:
            if validator(block_bytes(data, c)):
                claimed.add(c['off'])
                return c
        return None

    def v_pos(buf, tv):
        n = min(tv, 200)
        for i in range(n):
            x, y, z = struct.unpack('<3f', buf[i * 12:i * 12 + 12])
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6
                    and x == x and y == y and z == z):
                return False
        return n > 0

    def v_loopv(buf, tl, tv):
        n = min(tl, 500)
        for i in range(n):
            v, = struct.unpack('<i', buf[i * 4:i * 4 + 4])
            if not 0 <= v < tv:
                return False
        return n > 0

    def v_uv(buf, tl):
        n = min(tl, 200)
        for i in range(n):
            u, w = struct.unpack('<2f', buf[i * 8:i * 8 + 8])
            if not (-100.0 <= u <= 100.0 and -100.0 <= w <= 100.0
                    and u == u and w == w):
                return False
        return n > 0

    def v_polyoff(buf, tp, tl):
        n = tp + 1
        if len(buf) < n * 4:
            return False
        prev = -1
        for i in range(n):
            v, = struct.unpack('<i', buf[i * 4:i * 4 + 4])
            if v < prev or v > tl:
                return False
            prev = v
        first, = struct.unpack('<i', buf[0:4])
        last, = struct.unpack('<i', buf[(n - 1) * 4:n * 4])
        return first == 0 and last == tl

    def v_matidx(buf, tp):
        return all(v < 64 for v in buf[:min(tp, 200)])

    for blk in blocks:
        if blk['code'] != b'ME\x00\x00':
            continue
        me_data = block_bytes(data, blk)
        totvert, = struct.unpack('<i', me_data[tv_off:tv_off + 4])
        totloop, = struct.unpack('<i', me_data[tl_off:tl_off + 4])
        totpoly, = struct.unpack('<i', me_data[tp_off:tp_off + 4])
        totcol, = struct.unpack('<H', me_data[tc_off:tc_off + 2])
        mesh_name = unique_name(sanitize(id_name(me_data, id_off)))
        anchor = blk['off']
        # This mesh's OWN material slots (poly mat_nr indexes these, not
        # the file-wide MA list); object-linked slots override.
        slot_blks = mesh_material_slots(data, me_data, totcol, structs,
                                        types, lengths, ptr_map)
        for si, ma in ob_over.get(blk['ptr'], {}).items():
            if si < len(slot_blks):
                slot_blks[si] = ma
        slot_mats = [mat_by_ptr.get(b['ptr']) if b else None
                     for b in slot_blks]

        if totvert <= 0 or totloop <= 0 or totpoly <= 0:
            print(f"  [skip] {mesh_name}: {totvert}v {totloop}l {totpoly}p (empty)")
            continue

        # BLENDER17-01 mesh arrays (validated, not just size-matched):
        #   positions tv*12 float3 | loop_verts tl*4 int32 |
        #   loop_uvs tl*8 float2 | poly_offsets (tp+1)*4 int32 |
        #   poly_matidx tp*1 uint8 (optional)
        pos_b = claim_raw_valid(totvert * 12, anchor,
                                lambda b: v_pos(b, totvert))
        lv_b = claim_raw_valid(totloop * 4, anchor,
                               lambda b: v_loopv(b, totloop, totvert))
        uv_b = claim_raw_valid(totloop * 8, anchor,
                               lambda b: v_uv(b, totloop))
        po_b = claim_raw_valid((totpoly + 1) * 4, anchor,
                               lambda b: v_polyoff(b, totpoly, totloop))
        if not pos_b or not lv_b or not po_b:
            print(f"  [skip] {mesh_name}: missing arrays "
                  f"(pos={pos_b is not None} loopv={lv_b is not None} "
                  f"uv={uv_b is not None} polyoff={po_b is not None})")
            continue
        # Blender 4.x stores material_index as an int32 attribute; older
        # saves used a per-poly byte array. Values must index this mesh's
        # slots.
        ncol = max(totcol, 1)
        mat_b = None
        mat_w = 4
        if totcol > 1:
            mat_b = claim_raw_valid(
                totpoly * 4, anchor,
                lambda b: all(0 <= v < ncol for v in struct.unpack(
                    f'<{totpoly}i', b[:totpoly * 4])) and
                any(struct.unpack(f'<{totpoly}i', b[:totpoly * 4])))
        if not mat_b:
            mat_w = 1
            mat_b = claim_raw_valid(totpoly, anchor,
                                    lambda b: v_matidx(b, totpoly))

        # --- vertices ---
        pbuf = block_bytes(data, pos_b)
        verts = [struct.unpack('<3f', pbuf[v * 12:v * 12 + 12])
                 for v in range(totvert)]
        # --- loop -> vert ---
        lbuf = block_bytes(data, lv_b)
        loopverts = [struct.unpack('<i', lbuf[l * 4:l * 4 + 4])[0]
                     for l in range(totloop)]
        # --- uvs (per loop) ---
        uvs = []
        if uv_b:
            ubuf = block_bytes(data, uv_b)
            uvs = [struct.unpack('<2f', ubuf[l * 8:l * 8 + 8])
                   for l in range(totloop)]
        # --- poly offsets -> faces; vt index == loop id + 1 ---
        obuf = block_bytes(data, po_b)
        polyoff = [struct.unpack('<i', obuf[p * 4:p * 4 + 4])[0]
                   for p in range(totpoly + 1)]
        matidx = None
        if mat_b:
            mb = block_bytes(data, mat_b)
            matidx = (struct.unpack(f'<{totpoly}i', mb[:totpoly * 4])
                      if mat_w == 4 else mb)
        faces = []  # (loop_ids_0based, mat_nr)
        for p in range(totpoly):
            ls, le = polyoff[p], polyoff[p + 1]
            if 0 <= ls < le <= totloop and le - ls <= 64:
                lids = list(range(ls, le))
                if all(0 <= loopverts[l] < totvert for l in lids):
                    mn = matidx[p] if matidx else 0
                    faces.append((lids, mn))
        if not faces:
            print(f"  [skip] {mesh_name}: 0 valid faces")
            continue

        # --- weights (best effort) ---
        weights = {}
        if include_weights:
            weights, _ = extract_weights(data, blocks, structs, types,
                                         lengths, struct_order, ptr_map,
                                         totvert, anchor)

        # --- write OBJ + MTL ---
        obj_path = os.path.join(out_dir, f"{mesh_name}.obj")
        mtl_name = f"{mesh_name}.mtl"
        with open(obj_path, 'w') as out:
            out.write(f"# {mesh_name} from {os.path.basename(blend_path)}\n")
            out.write(f"# {totvert} verts, {len(faces)} faces, "
                      f"uv={'yes' if uvs else 'no'}, "
                      f"{len(weights)} weighted verts\n")
            out.write(f"mtllib {mtl_name}\n")
            for x, y, z in verts:
                out.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
            for u, w in uvs:
                out.write(f"vt {u:.6f} {w:.6f}\n")
            cur_mat = None
            for lids, mn in faces:
                # Blender clamps out-of-range mat_nr to the last slot
                m = slot_mats[min(mn, len(slot_mats) - 1)] if slot_mats else None
                mname = sanitize(m['name']) if m else 'default'
                if mname != cur_mat:
                    out.write(f"usemtl {mname}\n")
                    cur_mat = mname
                if uvs:
                    out.write("f " + " ".join(
                        f"{loopverts[l] + 1}/{l + 1}" for l in lids) + "\n")
                else:
                    out.write("f " + " ".join(
                        str(loopverts[l] + 1) for l in lids) + "\n")

        with open(os.path.join(out_dir, mtl_name), 'w') as mtl:
            written = set()
            for m in slot_mats:
                if not m or m['name'] in written:
                    continue
                written.add(m['name'])
                mtl.write(f"newmtl {sanitize(m['name'])}\n")
                mtl.write(f"Kd {m['r']:.4f} {m['g']:.4f} {m['b']:.4f}\n")
                for ch, rel in sorted(mat_tex.get(m['ptr'], {}).items()):
                    mtl.write(f"{ch} {rel}\n")
            if any(m is None for m in slot_mats) or not slot_mats:
                mtl.write("newmtl default\nKd 0.8 0.8 0.8\n")

        meta = {'mesh': mesh_name, 'totvert': totvert, 'totloop': totloop,
                'totpoly': totpoly, 'faces': len(faces),
                'has_uv': bool(uvs), 'has_poly_matidx': bool(mat_b),
                'totcol': totcol,
                'materials': [m['name'] if m else None for m in slot_mats],
                'material_textures': {m['name']: mat_tex.get(m['ptr'], {})
                                      for m in slot_mats if m},
                'weighted_verts': len(weights), 'weights': weights}
        with open(os.path.join(out_dir, f"{mesh_name}.json"), 'w') as jf:
            json.dump(meta, jf)

        print(f"  [{mesh_count}] {mesh_name}: {totvert}v {len(faces)}f "
              f"uv={'y' if uvs else 'n'} {len(weights)}w -> {mesh_name}.obj")
        mesh_count += 1

    for i, arm in enumerate(armatures):
        ap = os.path.join(out_dir, f"armature_{i}_{sanitize(arm['name'])}.json")
        with open(ap, 'w') as f:
            json.dump(arm, f)
        print(f"  armature {arm['name']}: {count_bones(arm['bones'])} bones -> "
              f"{os.path.basename(ap)}")

    print(f"\nExtracted {mesh_count} meshes to {out_dir}")
    return mesh_count


def main():
    args = sys.argv[1:]
    auto = False
    if args and args[0] == '--auto':
        auto = True
        args = args[1:]
    if len(args) < 2:
        print(f"Usage: {sys.argv[0]} [--auto] <input.blend> <output_dir>")
        sys.exit(1)
    src, out_dir = args[0], args[1]
    src_dir = os.path.dirname(os.path.abspath(src))
    if auto and detect(src) == 'zstd':
        tmp = tempfile.mkdtemp(prefix='blend17-')
        dec = os.path.join(tmp, 'decompressed.blend')
        print(f"decompressing zstd -> {dec}")
        decompress_zstd(src, dec)
        src = dec
    extract_blend17(src, out_dir, src_dir=src_dir)


if __name__ == '__main__':
    main()
