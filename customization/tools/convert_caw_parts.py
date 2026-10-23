#!/usr/bin/env python3
"""CAW part converter — Creation Suite data layer (Worker A, 2026-10-20).

Converts torn-down creation-system parts into suite-ready assets:

  No Mercy (.obj + .vc vertex colors)  -> GLB  (Blender headless batch)
      customization/parts/no-mercy/**.obj
      -> customization/parts-converted/no-mercy/<category>/<part_id>.glb
      Vertex colors from the sibling .vc file (one "R G B" line per OBJ
      vertex, in OBJ vertex order) become a COLOR_0 attribute + a
      Principled material fed by a Vertex Color node. Per the extractor
      (teardown/wwf-no-mercy/tools/extract_all_models.py), the AKI vertex
      record stores r,g,b per vertex in the ROM itself — these are the
      game's per-vertex Gouraud shading colors, meant to multiply the
      part's texture (raw, they render as gradients; that is the source
      data carried faithfully, not a conversion artifact). UVs from the
      OBJ are preserved (the game's face/skin PNG atlases map by UV).

  WMXIX .tex (GameCube texture containers) -> PNG texture parts
      customization/parts/wmxix/textures/**.tex
      -> customization/parts-converted/wmxix-textures/<...>.png
      1,044 of the 1,470 .tex files embed one or more standard GC TPL
      textures (magic 0x0020AF30); the first TPL's first image is decoded
      with the in-repo TPL decoder (teardown/wmxix/decode_tpl.py, format
      code vendored here with credit). The remaining .tex files carry no
      embedded TPL (name-table-only containers, e.g. TEX/64gara) and are
      logged as blocked, not faked.

  WMXIX .ymg meshes -> NOT converted. The YOBJ vertex assembly for CAW
      edit parts is unsolved with existing tooling (see
      customization/SYSTEMS-WIRING.md 2026-10-20 section for the evidence:
      batch-strip renders are fragments, the 2026-10-15 "solution" was
      disproven by own-eyes Lane-A re-test, and the 2026-10-17 assembly
      claim's artifacts are absent from the repo). Every .ymg is still
      cataloged with status "blocked_ymg_decode" so the suite can count
      and surface the gap honestly.

  Catalog: customization/parts-converted/CATALOG.json
      entries {id, name, source_game, slot, category, glb, origin_file,
      status} — slot ids are Tekken 7 slot TITLES from
      customization/parts/tekken/tekken7-slot-catalog.json.
      For texture parts, `glb` is null and an extra `texture` field
      carries the PNG path (meshes: `glb` set, no `texture` field).

Resumable: existing outputs are skipped (pass --force to redo).
Per-file status is appended to customization/parts-converted/convert-log.jsonl.

Usage:
  python3 convert_caw_parts.py nm [--force]           # No Mercy -> GLB (Blender)
  python3 convert_caw_parts.py wmxix-tex [--force]   # WMXIX .tex -> PNG
  python3 convert_caw_parts.py catalog               # (re)build CATALOG.json
  python3 convert_caw_parts.py sheet                 # contact-sheet renders
  python3 convert_caw_parts.py all                   # nm + wmxix-tex + catalog

Blender: xvfb-run -a env -u PYTHONPATH <blender> -b --python <batch script>,
with LD_LIBRARY_PATH=<egl stack> and XDG_RUNTIME_DIR=/tmp (owner machine
notes, TOOLS.md). Paths default to this VM's install; override with
WH_BLENDER / WH_EGL_LIB env vars.
"""
import json, os, struct, subprocess, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
CUSTOM = os.path.dirname(HERE)                      # customization/
REPO = os.path.dirname(CUSTOM)
PARTS = os.path.join(CUSTOM, 'parts')
OUT = os.path.join(CUSTOM, 'parts-converted')
LOG = os.path.join(OUT, 'convert-log.jsonl')
BLENDER = os.environ.get('WH_BLENDER',
    os.path.expanduser('~/workspace/tools/blender/blender-4.0.2-linux-x64/blender'))
EGL_LIB = os.environ.get('WH_EGL_LIB',
    os.path.expanduser('~/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu'))

def rel(p):
    return os.path.relpath(p, REPO).replace(os.sep, '/')

def log(rec):
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec) + '\n')

def logged_ok():
    ok = set()
    if os.path.exists(LOG):
        for line in open(LOG):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('status') == 'converted':
                ok.add(r['origin_file'])
    return ok

# ---------------------------------------------------------------- slot map
# Tekken 7 slot titles (customization/parts/tekken/tekken7-slot-catalog.json)
NM_SLOT = {
    'attire_parts': 'UPPER',
    'body_parts': 'FULL_BODY',
    'face': 'FACE',
    'weapon': 'EXTRA',
    'faces': 'FACE',        # PNG face textures
    'skins': 'FULL_BODY',   # PNG body-skin textures
}
WMXIX_SLOT = {
    'faces': 'FACE', 'hair': 'HAIR', 'upper_body': 'UPPER',
    'lower_body': 'LOWER', 'shoes': 'LOWER_ACC', 'gloves': 'UPPER_ACC',
    'gears': 'EXTRA', 'textures': 'MAKE_UP', 'colors': None,
}
WMXIX_ACC_SLOT = {'Wrist': 'UPPER_ACC', 'Elbow': 'UPPER_ACC',
                  'Knee': 'LOWER_ACC', '64gara': 'EXTRA'}

def wmxix_slot(relpath):
    parts = relpath.split('/')
    cat = parts[0]
    if cat == 'accessories':
        return WMXIX_ACC_SLOT.get(parts[2] if len(parts) > 2 else '', 'UPPER_ACC')
    return WMXIX_SLOT.get(cat)

# ------------------------------------------------------------- No Mercy GLB
NM_BATCH = r'''
import bpy, json, os, sys

def parse_obj(path):
    verts, uvs, faces = [], [], []
    for line in open(path):
        if line.startswith('v '):
            p = line.split()
            verts.append((float(p[1]), float(p[2]), float(p[3])))
        elif line.startswith('vt '):
            p = line.split()
            uvs.append((float(p[1]), float(p[2])))
        elif line.startswith('f '):
            idx = []
            for tok in line.split()[1:]:
                seg = tok.split('/')
                vi = int(seg[0]) - 1
                ti = int(seg[1]) - 1 if len(seg) > 1 and seg[1] else vi
                idx.append((vi, ti))
            for k in range(1, len(idx) - 1):
                faces.append((idx[0], idx[k], idx[k + 1]))
    return verts, uvs, faces

def parse_vc(path, n):
    cols = []
    if os.path.exists(path):
        for line in open(path):
            p = line.split()
            if len(p) == 3:
                cols.append(tuple(min(255, max(0, int(c))) / 255.0 for c in p) + (1.0,))
    if len(cols) != n:
        return None
    return cols

def convert(src, dst, logf):
    verts, uvs, faces = parse_obj(src)
    if not verts or not faces:
        logf.write(json.dumps({'origin_file': SRCREL[0], 'status': 'failed',
                               'detail': 'empty obj'}) + '\n'); logf.flush()
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new('part')
    mesh.from_pydata(verts, [], [tuple(v for v, t in f) for f in faces])
    mesh.update()
    cols = parse_vc(os.path.splitext(src)[0] + '.vc', len(verts))
    if cols:
        attr = mesh.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
        for i, c in enumerate(cols):
            attr.data[i].color = c
        mesh.color_attributes.active_color = attr
    if uvs and len(uvs) >= len(verts):
        layer = mesh.uv_layers.new(name='UVMap')
        for loop in mesh.loops:
            layer.data[loop.index].uv = uvs[loop.vertex_index]
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new('part', mesh)
    bpy.context.collection.objects.link(obj)
    mat = bpy.data.materials.new('part_mat')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.9
    if cols:
        vc = mat.node_tree.nodes.new('ShaderNodeVertexColor')
        vc.layer_name = 'Color'
        mat.node_tree.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
    mesh.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB',
                              export_apply=False, export_yup=True)
    logf.write(json.dumps({'origin_file': SRCREL[0], 'status': 'converted',
                           'glb': DSTREL[0], 'verts': len(verts),
                           'faces': len(faces), 'vertex_colors': bool(cols)}) + '\n')
    logf.flush()

jobs = json.load(open(JOBS_PATH))
logf = open(LOG_PATH, 'a')
for job in jobs:
    SRCREL[0] = job['origin_file']; DSTREL[0] = job['glb']
    try:
        convert(job['src'], job['dst'], logf)
    except Exception as e:
        logf.write(json.dumps({'origin_file': job['origin_file'],
                               'status': 'failed', 'detail': repr(e)}) + '\n')
        logf.flush()
logf.close()
'''

def run_nm(force=False):
    ok = set() if force else logged_ok()
    jobs = []
    for src in sorted(glob.glob(os.path.join(PARTS, 'no-mercy', '**', '*.obj'),
                                recursive=True)):
        category = os.path.relpath(src, os.path.join(PARTS, 'no-mercy')).split(os.sep)[0]
        stem = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(OUT, 'no-mercy', category, stem + '.glb')
        origin = rel(src)
        if origin in ok and os.path.exists(dst):
            continue
        jobs.append({'src': src, 'dst': dst, 'origin_file': origin, 'glb': rel(dst)})
    print(f'no-mercy: {len(jobs)} parts to convert')
    if not jobs:
        return
    jobs_path = '/tmp/cs_nm_jobs.json'
    json.dump(jobs, open(jobs_path, 'w'))
    batch = '/tmp/cs_nm_batch.py'
    with open(batch, 'w') as f:
        f.write('import json\nJOBS_PATH = %r\nLOG_PATH = %r\nSRCREL = [""]\nDSTREL = [""]\n'
                % (jobs_path, LOG))
        f.write(NM_BATCH)
    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = EGL_LIB + ':' + env.get('LD_LIBRARY_PATH', '')
    env['XDG_RUNTIME_DIR'] = '/tmp'
    env.pop('PYTHONPATH', None)
    cmd = ['xvfb-run', '-a', 'nice', '-n', '15', BLENDER, '-b', '--python', batch]
    print('running:', ' '.join(cmd))
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()
    print('\n'.join(tail[-5:]))
    done = sum(1 for j in jobs if os.path.exists(j['dst']))
    print(f'no-mercy: {done}/{len(jobs)} GLBs on disk after run')

# ------------------------------------------------- WMXIX textures (TPL)
# TPL tile decoding vendored from teardown/wmxix/decode_tpl.py (in-repo,
# measured on WMXIX; standard GameCube TPL). See that file for the format
# write-up. Only the first embedded TPL's first image is decoded per .tex.
def _u16(b, i): return struct.unpack('>H', b[i:i + 2])[0]
def _u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def _rgb5a3(px):
    if px & 0x8000:
        r = (px >> 10) & 0x1F; g = (px >> 5) & 0x1F; b = px & 0x1F
        return (r * 255 // 31, g * 255 // 31, b * 255 // 31, 255)
    a = (px >> 12) & 0x7; r = (px >> 8) & 0xF; g = (px >> 4) & 0xF; b = px & 0xF
    return (r * 17, g * 17, b * 17, a * 255 // 7)

def _rgb565(px):
    r = (px >> 11) & 0x1F; g = (px >> 5) & 0x3F; b = px & 0x1F
    return (r * 255 // 31, g * 255 // 63, b * 255 // 31, 255)

def _ia8(px): return (px & 0xFF,) * 3 + ((px >> 8),)
def _ia4(px):
    a = (px >> 4) & 0xF; i = px & 0xF
    return (i * 17, i * 17, i * 17, a * 17)

_PAL = {0: _ia8, 1: _rgb565, 2: _rgb5a3}
_TILE = {0: (8, 8, 32), 1: (8, 4, 32), 2: (8, 4, 32), 3: (4, 4, 64),
         4: (4, 4, 32), 5: (4, 4, 32), 6: (4, 4, 64),
         8: (8, 8, 32), 9: (8, 4, 32), 10: (8, 4, 32), 14: (8, 8, 32)}

def _tile(data, off, fmt, pal):
    if fmt == 0:
        px = []
        for i in range(32):
            b = data[off + i]
            v = (b >> 4) * 17; px.append((v, v, v, 255))
            v = (b & 0xF) * 17; px.append((v, v, v, 255))
        return px
    if fmt == 1:
        return [(b, b, b, 255) for b in data[off:off + 32]]
    if fmt == 2:
        return [_ia4(b) for b in data[off:off + 32]]
    if fmt == 3:
        return [_ia8(_u16(data, off + i * 2)) for i in range(32)]
    if fmt == 4:
        return [_rgb565(_u16(data, off + i * 2)) for i in range(16)]
    if fmt == 5:
        return [_rgb5a3(_u16(data, off + i * 2)) for i in range(16)]
    if fmt == 6:
        px = []
        for i in range(16):
            a = data[off + i * 2]; r = data[off + i * 2 + 1]
            b = data[off + 32 + i * 2]; g = data[off + 32 + i * 2 + 1]
            px.append((r, g, b, a))
        return px
    if fmt in (8, 9, 10):
        tw, th = (8, 8) if fmt == 8 else (8, 4)
        raw = data[off:off + tw * th * (4 if fmt == 8 else 8) // 8]
        idx = []
        if fmt == 8:
            for b in raw:
                idx += [b >> 4, b & 0xF]
        else:
            idx = list(raw)
        return [pal[i] for i in idx]
    if fmt == 14:
        px = [(0, 0, 0, 0)] * 64
        for s in range(4):
            so = off + s * 8
            c0 = _rgb565(_u16(data, so)); c1 = _rgb565(_u16(data, so + 2))
            bits = _u32(data, so + 4)
            if _u16(data, so) > _u16(data, so + 2):
                lut = [c0, c1,
                       tuple((2 * c0[i] + c1[i]) // 3 for i in range(3)) + (255,),
                       tuple((c0[i] + 2 * c1[i]) // 3 for i in range(3)) + (255,)]
            else:
                lut = [c0, c1, tuple((c0[i] + c1[i]) // 2 for i in range(3)) + (255,),
                       (0, 0, 0, 0)]
            for p in range(16):
                c = lut[(bits >> (p * 2)) & 3]
                px[(s // 2) * 4 * 8 + (p // 4) * 8 + (s % 2) * 4 + p % 4] = c
        return px
    raise ValueError(f'unsupported TPL format {fmt}')

def decode_first_tpl(tex_bytes):
    """Return a PIL Image for the first image of the first embedded TPL."""
    from PIL import Image
    j = tex_bytes.find(b'\x00\x20\xaf\x30')
    if j < 0:
        return None
    data = tex_bytes[j:]
    n = _u32(data, 4); toff = _u32(data, 8)
    h = _u32(data, toff)
    height, width = _u16(data, h), _u16(data, h + 2)
    fmt = _u32(data, h + 4); doff = _u32(data, h + 8)
    pal = None
    if fmt in (8, 9, 10):
        ph = h + 36
        nent = _u16(data, ph); pfmt = _u32(data, ph + 4); poff = _u32(data, ph + 8)
        dec = _PAL[pfmt]
        pal = [dec(_u16(data, poff + i * 2)) for i in range(nent)]
    tw, th, tb = _TILE[fmt]
    img = Image.new('RGBA', (width, height))
    px = img.load()
    off = doff
    for ty in range(0, height, th):
        for tx in range(0, width, tw):
            tile = _tile(data, off, fmt, pal)
            off += tb
            for y in range(th):
                for x in range(tw):
                    if tx + x < width and ty + y < height:
                        px[tx + x, ty + y] = tile[y * tw + x]
    return img

def run_wmxix_tex(force=False):
    ok = set() if force else logged_ok()
    n_ok = n_blocked = n_fail = 0
    for src in sorted(glob.glob(os.path.join(PARTS, 'wmxix', 'textures', '**', '*.tex'),
                                recursive=True)):
        origin = rel(src)
        sub = os.path.relpath(src, os.path.join(PARTS, 'wmxix', 'textures'))
        dst = os.path.join(OUT, 'wmxix-textures', os.path.splitext(sub)[0] + '.png')
        if origin in ok and os.path.exists(dst):
            n_ok += 1
            continue
        try:
            img = decode_first_tpl(open(src, 'rb').read())
        except Exception as e:
            log({'origin_file': origin, 'status': 'failed', 'detail': repr(e)})
            n_fail += 1
            continue
        if img is None:
            log({'origin_file': origin, 'status': 'blocked_no_tpl',
                 'detail': 'no embedded TPL magic (name-table-only container)'})
            n_blocked += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        img.save(dst)
        log({'origin_file': origin, 'status': 'converted', 'texture': rel(dst),
             'size': list(img.size)})
        n_ok += 1
    print(f'wmxix-tex: converted={n_ok} blocked_no_tpl={n_blocked} failed={n_fail}')

# ---------------------------------------------------------------- catalog
def build_catalog():
    entries = []
    conv = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            try:
                r = json.loads(line)
            except Exception:
                continue
            conv[r['origin_file']] = r
    # No Mercy meshes
    for src in sorted(glob.glob(os.path.join(PARTS, 'no-mercy', '**', '*.obj'),
                                 recursive=True)):
        category = os.path.relpath(src, os.path.join(PARTS, 'no-mercy')).split(os.sep)[0]
        stem = os.path.splitext(os.path.basename(src))[0]
        origin = rel(src)
        r = conv.get(origin, {})
        glb = r.get('glb') if r.get('status') == 'converted' else None
        e = {'id': f'nm-{category}-{stem}'.lower(), 'name': stem,
             'source_game': 'no-mercy', 'slot': NM_SLOT.get(category),
             'category': category, 'glb': glb, 'origin_file': origin,
             'status': r.get('status', 'not_run')}
        if r.get('status') == 'failed':
            e['detail'] = r.get('detail', '')
        entries.append(e)
    # No Mercy PNG texture parts (faces + skins)
    for src in sorted(glob.glob(os.path.join(PARTS, 'no-mercy', '**', '*.png'),
                                recursive=True)):
        category = os.path.relpath(src, os.path.join(PARTS, 'no-mercy')).split(os.sep)[0]
        stem = os.path.splitext(os.path.basename(src))[0]
        entries.append({'id': f'nm-{category}-{stem}'.lower(), 'name': stem,
                        'source_game': 'no-mercy', 'slot': NM_SLOT.get(category),
                        'category': category, 'glb': None,
                        'origin_file': rel(src), 'status': 'texture_part',
                        'texture': rel(src)})
    # WMXIX meshes (.ymg) — blocked, cataloged honestly
    for src in sorted(glob.glob(os.path.join(PARTS, 'wmxix', '**', '*.ymg'),
                                recursive=True)):
        sub = os.path.relpath(src, os.path.join(PARTS, 'wmxix'))
        category = sub.split(os.sep)[0]
        stem = os.path.splitext(os.path.basename(src))[0]
        magic = open(src, 'rb').read(4)
        status = 'blocked_dumy_placeholder' if magic == b'DUMY' else 'blocked_ymg_decode'
        entries.append({'id': 'wmxix-' + sub.replace(os.sep, '-').lower().replace('.ymg', ''),
                        'name': stem, 'source_game': 'wmxix',
                        'slot': wmxix_slot(sub.replace(os.sep, '/')),
                        'category': category, 'glb': None,
                        'origin_file': rel(src), 'status': status})
    # WMXIX textures (.tex -> PNG where decoded; texture source otherwise)
    for src in sorted(glob.glob(os.path.join(PARTS, 'wmxix', 'textures', '**', '*.tex'),
                                recursive=True)):
        sub = os.path.relpath(src, os.path.join(PARTS, 'wmxix'))
        origin = rel(src)
        r = conv.get(origin, {})
        e = {'id': 'wmxix-' + sub.replace(os.sep, '-').lower().replace('.tex', ''),
             'name': os.path.splitext(os.path.basename(src))[0],
             'source_game': 'wmxix', 'slot': 'MAKE_UP', 'category': 'textures',
             'glb': None, 'origin_file': origin,
             'status': r.get('status', 'not_run')}
        if r.get('status') == 'converted':
            e['texture'] = r['texture']
        entries.append(e)
    # WMXIX colors (.ycg palettes)
    for src in sorted(glob.glob(os.path.join(PARTS, 'wmxix', 'colors', '**', '*.ycg'),
                                recursive=True)):
        sub = os.path.relpath(src, os.path.join(PARTS, 'wmxix'))
        entries.append({'id': 'wmxix-' + sub.replace(os.sep, '-').lower().replace('.ycg', ''),
                        'name': os.path.splitext(os.path.basename(src))[0],
                        'source_game': 'wmxix', 'slot': None, 'category': 'colors',
                        'glb': None, 'origin_file': rel(src),
                        'status': 'palette_only'})
    # WMXIX leftovers (ymm/tga/tpl/tm2/tpg/psd/txt in parts tree)
    known = {e['origin_file'] for e in entries}
    for src in sorted(glob.glob(os.path.join(PARTS, 'wmxix', '**', '*.*'),
                                recursive=True)):
        origin = rel(src)
        if origin in known or origin.endswith('PARTS-INDEX.jsonl'):
            continue
        sub = os.path.relpath(src, os.path.join(PARTS, 'wmxix'))
        entries.append({'id': 'wmxix-' + sub.replace(os.sep, '-').lower(),
                        'name': os.path.basename(src), 'source_game': 'wmxix',
                        'slot': wmxix_slot(sub.replace(os.sep, '/')),
                        'category': sub.split(os.sep)[0], 'glb': None,
                        'origin_file': origin, 'status': 'not_converted'})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'CATALOG.json'), 'w') as f:
        json.dump({'generated': '2026-10-20', 'tool': 'customization/tools/convert_caw_parts.py',
                   'count': len(entries), 'parts': entries}, f, indent=1)
    from collections import Counter
    print('catalog entries:', len(entries))
    print(Counter((e['source_game'], e['status']) for e in entries))

# ------------------------------------------------------------ contact sheet
SHEET_BATCH = r'''
import bpy, json, math, os
from mathutils import Vector
jobs = json.load(open(JOBS_PATH))
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
tiles = []
for job in jobs:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=job['glb'])
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    # No Mercy GLBs face -Y (docs/RENDER-ORIENTATION.md): Rz(-90) -> faces -X
    for o in objs:
        o.rotation_euler.z = math.radians(-90)
    bpy.context.view_layer.update()
    corners = []
    for o in objs:
        corners += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not corners:
        continue
    mn = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    mx = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    center = (mn + mx) / 2
    span = mx - mn
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new('cam')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 1.12 * max(span.y, span.z, 0.001)
    cam = bpy.data.objects.new('cam', cam_data)
    scene.collection.objects.link(cam)
    cam.location = (center.x - 10, center.y, center.z)
    cam.rotation_euler = (math.radians(90), 0, math.radians(-90))
    scene.camera = cam
    light_data = bpy.data.lights.new('sun', 'SUN')
    light_data.energy = 3
    light = bpy.data.objects.new('sun', light_data)
    light.rotation_euler = (math.radians(50), 0, math.radians(-30))
    scene.collection.objects.link(light)
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    scene.world = world
    # Workbench (vertex colors shown directly): Cycles at 512px under full
    # machine load died twice to runtime restarts before finishing 12 tiles.
    # Camera/framing/background stay the locked method
    # (docs/RENDER-ORIENTATION.md): ortho, front camera on -X after the
    # faceY Rz(-90) rotation, white bg, ortho_scale = 1.12 x max span.
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'VERTEX'
    scene.display.shading.background_type = 'WORLD'
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    out = job['tile']
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    tiles.append(out)
    print('tile:', out)
json.dump(tiles, open(TILES_PATH, 'w'))
'''

def run_sheet():
    from PIL import Image, ImageDraw
    picks = []
    base = os.path.join(OUT, 'no-mercy')
    want = [('body_parts', 6), ('face', 3), ('weapon', 2), ('attire_parts', 1)]
    for cat, n in want:
        glbs = sorted(glob.glob(os.path.join(base, cat, '*.glb')))[:n]
        picks += glbs
    picks = picks[:12]
    tile_dir = '/tmp/cs_sheet_tiles'
    os.makedirs(tile_dir, exist_ok=True)
    jobs = [{'glb': g, 'tile': os.path.join(
        tile_dir, f'{i:02d}_' + os.path.basename(g).replace('.glb', '.png'))}
        for i, g in enumerate(picks)]
    json.dump(jobs, open('/tmp/cs_sheet_jobs.json', 'w'))
    batch = '/tmp/cs_sheet_batch.py'
    with open(batch, 'w') as f:
        f.write('JOBS_PATH = "/tmp/cs_sheet_jobs.json"\nOUT_PATH = %r\nTILES_PATH = "/tmp/cs_sheet_tiles.json"\n'
                % os.path.join(OUT, 'contact-sheet-nm.png'))
        f.write(SHEET_BATCH)
    env = dict(os.environ)
    env['LD_LIBRARY_PATH'] = EGL_LIB + ':' + env.get('LD_LIBRARY_PATH', '')
    env['XDG_RUNTIME_DIR'] = '/tmp'
    env.pop('PYTHONPATH', None)
    r = subprocess.run(['xvfb-run', '-a', 'nice', '-n', '15', BLENDER, '-b',
                        '--python', batch], env=env, capture_output=True, text=True)
    print('\n'.join((r.stdout + r.stderr).strip().splitlines()[-4:]))
    tiles = json.load(open('/tmp/cs_sheet_tiles.json'))
    cols, rows, T = 4, 3, 512
    sheet = Image.new('RGB', (cols * T, rows * (T + 24)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(tiles):
        x, y = (i % cols) * T, (i // cols) * (T + 24)
        sheet.paste(Image.open(t).convert('RGB'), (x, y))
        label = os.path.basename(picks[i]).replace('.glb', '') + ' / ' + \
            os.path.basename(os.path.dirname(picks[i]))
        d.text((x + 6, y + T + 5), label, fill='black')
    sheet.save(os.path.join(OUT, 'contact-sheet-nm.png'))
    print('sheet:', os.path.join(OUT, 'contact-sheet-nm.png'), len(tiles), 'tiles')
    # WMXIX texture sheet (pure PIL)
    texs = sorted(glob.glob(os.path.join(OUT, 'wmxix-textures', '**', '*.png'),
                            recursive=True))
    step = max(1, len(texs) // 12)
    chosen = texs[::step][:12]
    T2 = 256
    sheet2 = Image.new('RGB', (4 * T2, 3 * (T2 + 24)), 'white')
    d2 = ImageDraw.Draw(sheet2)
    for i, t in enumerate(chosen):
        x, y = (i % 4) * T2, (i // 4) * (T2 + 24)
        im = Image.open(t).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        sheet2.paste(bg.convert('RGB').resize((T2, T2)), (x, y))
        d2.text((x + 6, y + T2 + 5), os.path.basename(t), fill='black')
    sheet2.save(os.path.join(OUT, 'contact-sheet-wmxix-textures.png'))
    print('sheet2:', os.path.join(OUT, 'contact-sheet-wmxix-textures.png'),
          len(chosen), 'of', len(texs), 'textures')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    force = '--force' in sys.argv
    if cmd in ('nm', 'all'):
        run_nm(force)
    if cmd in ('wmxix-tex', 'all'):
        run_wmxix_tex(force)
    if cmd in ('catalog', 'all'):
        build_catalog()
    if cmd == 'sheet':
        run_sheet()
