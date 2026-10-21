#!/usr/bin/env python3
"""Creation Suite bake pipeline — turn a suite `customization.json` into a real game GLB.

THE TOOL for the Creation Suite Pass (Worker B). Input: an attire folder (or an
explicit customization.json path). Output: the baked `out_glb` written INTO the
attire folder, plus a regenerated `game/js/attire-customizations.js` registry
(the game hook in game/js/assets.js overrides MODEL_URLS from that registry).

Schema: customization/CUSTOMIZATION-JSON-SCHEMA.md (fixed contract; the UI lane
and the proof lane build against it).

Apply order (mirrors packages/creation-suite semantics — parts.js / attire.js /
morphs.js — in headless Blender):
  (a) MPFB morphs   — suite ids -> MPFB targets via customization/body-morphs/
                      MANIFEST.json. Existing MPFB_<id> shape keys are driven to
                      the saved values; absent keys are transferred + baked with
                      a height-normalized KD-tree transfer (the mpfb_wire_cj.py
                      method: MPFB base scaled/aligned to the target, nearest
                      base vert per target vert). Result is BAKED into the
                      Basis — the exported GLB carries the deformed geometry,
                      not live keys. Face-shape morphs included.
  (b) Textures      — eye/decal/hair images composited into the base GLB's
                      embedded textures at registry placements / schema rects,
                      then re-packed so the GLB re-embeds them. Target
                      resolution order: explicit material/texture in the entry
                      -> PARTS-REGISTRY character_mappings[fighter][kind]
                      -> PARTS-REGISTRY part placement
                      -> customization/parts/<fighter>-eyes/MANIFEST.json
                         (eye_texture, the baek-eyes pattern)
                      -> customization/eye-library/MANIFEST.json mappings.
                      Registry mode "full_replace" replaces the whole texture
                      (alpha-blended); a schema `rect` composites at
                      [x, y, w, h] in top-left pixel space.
  (c) Mesh parts    — part GLBs: if the part carries an armature whose bone
                      names exist on the base rig, its meshes are re-bound to
                      the base armature (skinning preserved by bone name);
                      otherwise the part is bone-parented at the slot socket
                      (aliases mirror packages/creation-suite/src/attire.js
                      SOCKETS) with the schema placement offsets applied in
                      bone-local space. EYES ARE MESH PARTS (owner verdict
                      2026-10-20): eyeball/eyelash/eyebrow attach at the `eye`
                      socket like any other part — the textures kind:"eye" path
                      is only the legacy eye-texture-variant swap, never the
                      eye system.
  (d) Colors        — colors.hair / colors.skin tint the Principled base-color
                      factor (multiplied with the texture at render time) of
                      materials resolved by registry mapping or by material
                      name containing hair/skin. Unresolvable -> loud error.

Every step logs. A missing input FAILS LOUDLY per-item (collected in the final
CSBAKE report, exit code 2) — nothing is ever silently skipped. A missing base
GLB aborts before export (exit 1).

Usage (Blender headless — bare -b segfaults on this VM, always xvfb-run):
  xvfb-run -a env -u PYTHONPATH \
    LD_LIBRARY_PATH=~/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu \
    XDG_RUNTIME_DIR=/tmp \
    ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender -b \
    --python customization/tools/apply_customization.py -- \
    roster/baek/attires/master-white [--mpfb-src ~/workspace/cape-jones/production/tools/mpfb2]

Registry-only regeneration (no Blender needed):
  python3 customization/tools/apply_customization.py --emit-registry [--repo-root .]
"""
import json, os, re, struct, sys

# ---------------------------------------------------------------- emit (pure python)

def _rel_to_game(repo_root, path):
    game_dir = os.path.join(repo_root, 'game')
    rel = os.path.relpath(path, game_dir).replace(os.sep, '/')
    return rel if rel.startswith('.') else './' + rel


def _model_url_keys(repo_root):
    """Parse MODEL_URLS from game/js/assets.js -> {resolved repo-rel glb path: key}."""
    assets = os.path.join(repo_root, 'game', 'js', 'assets.js')
    out = {}
    if not os.path.exists(assets):
        return out
    text = open(assets, encoding='utf-8').read()
    m = re.search(r'const MODEL_URLS = \{(.*?)\n\};', text, re.S)
    body = m.group(1) if m else text
    for km in re.finditer(r"(?:'([^']+)'|(\w[\w-]*))\s*:\s*'([^']+\.glb)'", body):
        key = km.group(1) or km.group(2)
        url = km.group(3)
        resolved = os.path.normpath(os.path.join(repo_root, 'game', url)).replace(os.sep, '/')
        out[resolved] = key
    return out


def find_customization_files(repo_root):
    hits = []
    roster = os.path.join(repo_root, 'roster')
    for dirpath, _dirnames, filenames in os.walk(roster):
        if 'customization.json' in filenames:
            hits.append(os.path.join(dirpath, 'customization.json'))
    return sorted(hits)


def emit_registry(repo_root, log=print):
    """Regenerate game/js/attire-customizations.js from every customization.json."""
    key_by_path = _model_url_keys(repo_root)
    mapping = {}
    for cpath in find_customization_files(repo_root):
        try:
            cfg = json.load(open(cpath, encoding='utf-8'))
        except Exception as e:  # loud, never silent
            log(f'CSBAKE ERROR: cannot parse {cpath}: {e}')
            continue
        attire_dir = os.path.dirname(cpath)
        base = os.path.join(attire_dir, cfg.get('base_glb', ''))
        out_glb = os.path.join(attire_dir, cfg.get('out_glb', 'model-custom.glb'))
        base_key = os.path.normpath(base).replace(os.sep, '/')
        key = key_by_path.get(base_key) or f"{cfg.get('fighter', 'fighter')}-{cfg.get('attire', 'attire')}"
        mapping[key] = _rel_to_game(repo_root, out_glb)
        log(f'CSBAKE registry: {key} -> {mapping[key]}')
    lines = [
        '// GENERATED by customization/tools/apply_customization.py — do not hand-edit.',
        '// Creation Suite Pass: baked customization overrides for game/js/assets.js.',
        '// One entry per attire folder containing a customization.json with an out_glb.',
        '// Key = the MODEL_URLS key of the attire\'s base_glb in game/js/assets.js.',
        'export const ATTIRE_CUSTOMIZATIONS = {',
    ]
    for k in sorted(mapping):
        lines.append(f"  '{k}': '{mapping[k]}',")
    lines.append('};')
    lines.append('')
    dest = os.path.join(repo_root, 'game', 'js', 'attire-customizations.js')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    log(f'CSBAKE registry written: {dest} ({len(mapping)} entries)')
    return mapping


def find_repo_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(p, 'customization', 'PARTS-REGISTRY.json')):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            raise SystemExit(f'CSBAKE FATAL: no repo root (customization/PARTS-REGISTRY.json) above {start}')
        p = parent


# ---------------------------------------------------------------- blender bake

def bake(cfg_path, repo_root, mpfb_src, log=print):
    import bpy
    from mathutils import Vector, Matrix
    from mathutils.kdtree import KDTree

    errors = []
    def fail(item, msg):
        errors.append((item, msg))
        log(f'CSBAKE ERROR [{item}]: {msg}')

    cfg_dir = os.path.dirname(os.path.abspath(cfg_path))
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    if cfg.get('app') != 'wh-creation-suite' or cfg.get('version') != 1:
        fail('schema', f"expected version=1 app=wh-creation-suite, got version={cfg.get('version')} app={cfg.get('app')}")
    fighter = cfg.get('fighter')
    base_glb = os.path.join(cfg_dir, cfg.get('base_glb', ''))
    out_glb = os.path.join(cfg_dir, cfg.get('out_glb', 'model-custom.glb'))
    if not os.path.exists(base_glb):
        log(f'CSBAKE FATAL: base_glb missing: {base_glb}')
        return 1, errors
    log(f'CSBAKE bake: {base_glb} -> {out_glb} (fighter={fighter} attire={cfg.get("attire")})')

    def hex_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    registry_path = os.path.join(repo_root, 'customization', 'PARTS-REGISTRY.json')
    registry = json.load(open(registry_path, encoding='utf-8'))
    reg_parts = {p['id']: p for p in registry.get('parts', [])}
    char_maps = registry.get('character_mappings', {})

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=base_glb)
    scene = bpy.context.scene
    meshes = [o for o in scene.objects if o.type == 'MESH']
    armatures = [o for o in scene.objects if o.type == 'ARMATURE']
    base_arm = armatures[0] if armatures else None
    log(f'CSBAKE imported: {len(meshes)} meshes, {len(armatures)} armatures, '
        f'{sum(len(o.data.vertices) for o in meshes)} verts')

    # ---- (a) MPFB morphs -------------------------------------------------
    morphs = {k: float(v) for k, v in (cfg.get('morphs') or {}).items() if float(v) != 0.0}
    if morphs:
        manifest = json.load(open(os.path.join(
            repo_root, 'customization', 'body-morphs', 'MANIFEST.json'), encoding='utf-8'))
        suite_targets = {}   # suite id -> [mpfb target rel paths]
        for m in manifest.get('macro_morphs', []):
            suite_targets[m['id']] = m['mpfb'] if isinstance(m['mpfb'], list) else [m['mpfb']]
        for group in (manifest.get('face_shape_morphs') or {}).values():
            for e in group:
                suite_targets[e['suite']] = [e['mpfb']]
        unknown = [k for k in morphs if k not in suite_targets]
        for k in unknown:
            fail('morphs', f'unknown suite morph id "{k}" (not in body-morphs/MANIFEST.json)')
        morphs = {k: v for k, v in morphs.items() if k in suite_targets}

        # Which meshes already carry which MPFB_<id> keys?
        def has_key(obj, mid):
            return obj.data.shape_keys and ('MPFB_' + mid) in obj.data.shape_keys.key_blocks
        need_transfer = [mid for mid in morphs if not all(has_key(o, mid) for o in meshes)]
        transferred = {}
        if need_transfer:
            if not mpfb_src or not os.path.isdir(mpfb_src):
                for mid in need_transfer:
                    fail('morphs', f'MPFB_{mid} key absent and --mpfb-src not given/found; cannot transfer+bake')
                need_transfer = []
            else:
                import gzip
                targets_dir = os.path.join(mpfb_src, 'src', 'mpfb', 'data', 'targets')
                base_obj = os.path.join(mpfb_src, 'src', 'mpfb', 'data', '3dobjs', 'base.obj')
                bverts = []
                with open(base_obj) as f:
                    for line in f:
                        if line.startswith('v '):
                            _, x, y, z = line.split()
                            # MPFB obj space: x=right, y=UP, z=depth -> Blender (x, z, y)
                            bverts.append(Vector((float(x), float(z), float(y))))
                bmin = Vector((min(v.x for v in bverts), min(v.y for v in bverts), min(v.z for v in bverts)))
                bmax = Vector((max(v.x for v in bverts), max(v.y for v in bverts), max(v.z for v in bverts)))
                bheight = bmax.z - bmin.z
                bcx, bcy = (bmin.x + bmax.x) / 2, (bmin.y + bmax.y) / 2
                # per-morph MPFB-space delta per base vert (signed decr-incr semantics;
                # {min,max} macro picks the side file, scaled by |value|)
                # MANIFEST rels are MPFB *logical* names; on disk a logical
                # "x-decr-incr" is a -decr/-incr file pair, often split l-/r-
                # (arms/upperarm-muscle -> arms/l-upperarm-muscle-incr + r-...).
                PAIRS = [('-decr-incr', ('decr', 'incr')), ('-down-up', ('down', 'up')),
                         ('-in-out', ('in', 'out'))]
                def resolve_target(rel, val):
                    """-> [(rel_path, signed_weight)] for one MANIFEST target."""
                    def exists(r):
                        return (os.path.exists(os.path.join(targets_dir, r + '.target.gz')) or
                                os.path.exists(os.path.join(targets_dir, r + '.target')))
                    if '{min,max}' in rel:
                        r = rel.replace('{min,max}', 'max' if val >= 0 else 'min')
                        return [(r, abs(val))] if exists(r) else []
                    for suf, (lo, hi) in PAIRS:
                        if rel.endswith(suf):
                            stem = rel[:-len(suf)]
                            group, _, name = stem.rpartition('/')
                            pick = hi if val >= 0 else lo
                            cands = [f'{stem}-{pick}', f'{group}/l-{name}-{pick}',
                                     f'{group}/r-{name}-{pick}']
                            return [(c, abs(val)) for c in cands if exists(c)]
                    return [(rel, val)] if exists(rel) else []
                def load_target_file(r):
                    path = os.path.join(targets_dir, r + '.target.gz')
                    if not os.path.exists(path):
                        path = os.path.join(targets_dir, r + '.target')
                    opener = gzip.open if path.endswith('.gz') else open
                    deltas = {}
                    with opener(path, 'rt') as fh:
                        for line in fh:
                            parts = line.split()
                            if len(parts) < 4 or line.lstrip().startswith('#'):
                                continue
                            i = int(parts[0])
                            # MPFB (x, y-up, z) -> Blender frame (x, z, y-up)
                            deltas[i] = Vector((float(parts[1]), float(parts[3]), float(parts[2])))
                    return deltas
                morph_deltas = {}
                for mid in need_transfer:
                    val = morphs[mid]
                    acc = {}
                    rels = suite_targets[mid]
                    for rel in rels:
                        files = resolve_target(rel, val)
                        if not files:
                            fail('morphs', f'MPFB target missing on disk: {rel}')
                            continue
                        for r, w in files:
                            for i, d in load_target_file(r).items():
                                acc[i] = acc.get(i, Vector((0, 0, 0))) + d * (w / len(rels))
                    morph_deltas[mid] = acc
                # normalized KD transfer, per mesh, in world space
                bpy.context.view_layer.update()
                allw = []
                for o in meshes:
                    allw += [o.matrix_world @ v.co for v in o.data.vertices]
                tmin = Vector((min(v.x for v in allw), min(v.y for v in allw), min(v.z for v in allw)))
                tmax = Vector((max(v.x for v in allw), max(v.y for v in allw), max(v.z for v in allw)))
                theight = tmax.z - tmin.z
                tcx, tcy = (tmin.x + tmax.x) / 2, (tmin.y + tmax.y) / 2
                def norm_mpfb(v):
                    return Vector(((v.x - bcx) / bheight, (v.y - bcy) / bheight, (v.z - bmin.z) / bheight))
                def norm_tgt(v):
                    return Vector(((v.x - tcx) / theight, (v.y - tcy) / theight, (v.z - tmin.z) / theight))
                kd = KDTree(len(bverts))
                for i, v in enumerate(bverts):
                    kd.insert(norm_mpfb(v), i)
                kd.balance()
                for o in meshes:
                    mesh = o.data
                    if not mesh.shape_keys:
                        o.shape_key_add(name='Basis', from_mix=False)
                    basis = mesh.shape_keys.key_blocks['Basis']
                    new_keys = {}
                    for mid in need_transfer:
                        if has_key(o, mid):
                            continue
                        sk = o.shape_key_add(name='MPFB_' + mid, from_mix=False)
                        sk.value = 0.0  # deltas below are pre-scaled by the saved value
                        new_keys[mid] = sk
                    if not new_keys:
                        continue
                    inv3 = o.matrix_world.inverted().to_3x3()
                    for vi, v in enumerate(mesh.vertices):
                        w = o.matrix_world @ v.co
                        _, bidx, _ = kd.find(norm_tgt(w))
                        for mid, sk in new_keys.items():
                            d = morph_deltas[mid].get(bidx)
                            if d:
                                dl = inv3 @ (d * (theight / bheight))
                                sk.data[vi].co = basis.data[vi].co + dl
                    transferred[o.name] = list(new_keys)
                log(f'CSBAKE morphs transferred+baked keys: {transferred}')
        # Drive every MPFB_<id> key to its saved value, then bake the evaluated
        # mix into a new Basis. (Writing Basis key data directly does NOT move
        # the evaluated mesh — verified empirically; the from_mix promotion is
        # the reliable path: add a from-mix key, remove the morph keys, then
        # remove the old Basis so the mix key is promoted to Basis.)
        baked = []
        for o in meshes:
            mesh = o.data
            if not mesh.shape_keys:
                continue
            kb = mesh.shape_keys.key_blocks
            active = [mid for mid in morphs if ('MPFB_' + mid) in kb]
            if not active:
                continue
            for mid in active:
                # transferred keys carry deltas pre-scaled by the saved value
                kb['MPFB_' + mid].value = 1.0 if mid in (transferred.get(o.name) or []) else morphs[mid]
            mix_key = o.shape_key_add(name='CSBAKE_MIX', from_mix=True)
            for name in [k.name for k in mesh.shape_keys.key_blocks
                         if k.name not in ('Basis', 'CSBAKE_MIX')]:
                o.shape_key_remove(mesh.shape_keys.key_blocks[name])
            o.shape_key_remove(mesh.shape_keys.key_blocks['Basis'])
            try:
                mix_key.name = 'Basis'
            except Exception:
                pass
            baked.append((o.name, active))
        log(f'CSBAKE morphs baked into Basis: {baked}')

    # ---- (a2) hide base meshes (round 2: base-hair hide toggle etc.) -------
    for pat in (cfg.get('hide_meshes') or []):
        pat_l = str(pat).lower()
        hits = [o for o in list(scene.objects) if o.type == 'MESH' and
                (pat_l in o.name.lower() or pat_l in o.data.name.lower() or
                 any(ms.material and pat_l in ms.material.name.lower()
                     for ms in o.material_slots))]
        for o in hits:
            log(f'CSBAKE hide_meshes: removing base mesh {o.name} (matched "{pat}")')
            bpy.data.objects.remove(o, do_unlink=True)
        if not hits:
            fail('hide_meshes', f'pattern "{pat}" matched no base mesh or material')
        meshes = [o for o in scene.objects if o.type == 'MESH']

    # ---- (a3) region swaps (round 2: PIECE SWAPS, Tekken-style) -------------
    # customization.json "region_swaps": [{region, from_glb, from_fighter?,
    # from_attire?, yaw_deg?, scale?}]. The region is CUT from the base
    # (verts whose dominant bone is in the region) and CUT from the source,
    # then the source piece is fit (neck-anchor + region-height scale + yaw
    # from the head-centroid forward estimate) and re-skinned onto the base
    # rig: by canonical bone name when the source is skinned, by distance to
    # the region's bones when it is not. Unskinned sources support "head"
    # (spatial neck-pinch cut) — other regions fail loudly.
    import bmesh

    def canon_bone(name):
        c = re.sub(r'[^a-z0-9]', '', str(name).lower())
        for pre in ('mixamorig', 'bip01', 'def', 'org'):
            if c.startswith(pre) and len(c) > len(pre) + 2:
                c = c[len(pre):]
                break
        return c

    def bone_in_region(c, region):
        if region == 'head':
            return c in ('head', 'headtop', 'headdummy')
        if region == 'torso':
            return c.startswith('spine') or c in ('chest', 'leftbreast', 'rightbreast')
        if region == 'arm_l':
            return c.startswith(('leftshoulder', 'leftarm', 'leftforearm', 'lefthand'))
        if region == 'arm_r':
            return c.startswith(('rightshoulder', 'rightarm', 'rightforearm', 'righthand'))
        if region == 'legs':
            return c.startswith(('leftupleg', 'leftleg', 'leftfoot', 'lefttoebase',
                                   'rightupleg', 'rightleg', 'rightfoot', 'righttoebase'))
        return False

    REGION_ANCHORS = {
        'head': ['Head', 'Neck'],
        'torso': ['Spine2', 'Spine1', 'Spine', 'Hips'],
        'arm_l': ['LeftArm', 'LeftForeArm', 'LeftHand'],
        'arm_r': ['RightArm', 'RightForeArm', 'RightHand'],
        'legs': ['LeftUpLeg', 'LeftLeg', 'RightUpLeg', 'RightLeg'],
    }

    def dominant_canon(obj, vert):
        best, bw = None, 0.0
        for g in vert.groups:
            if g.weight > bw:
                bw = g.weight
                best = obj.vertex_groups[g.group].name
        return canon_bone(best) if best else None

    def world_verts(obj):
        mw = obj.matrix_world
        return [mw @ v.co for v in obj.data.vertices]

    def cut_region_from(obj, region):
        """Remove verts whose dominant bone is in region. Returns removed count."""
        if not obj.vertex_groups:
            return 0
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        # dominant bone per vert from the MESH data (bmesh BMDeformVert is
        # not iterable on Blender 4.0 — iterating v[dl] raised TypeError and
        # killed every swap bake; mesh Vertex.groups is the stable API).
        kill_idx = set()
        for v in obj.data.vertices:
            dc = dominant_canon(obj, v)
            if dc and bone_in_region(dc, region):
                kill_idx.add(v.index)
        kill = []
        if kill_idx:
            bm.verts.ensure_lookup_table()
            kill = [bm.verts[i] for i in sorted(kill_idx)]
        if kill:
            bmesh.ops.delete(bm, geom=kill, context='VERTS')
            bm.to_mesh(obj.data)
            obj.data.update()
        bm.free()
        return len(kill)

    def region_ref(objs_verts, region):
        """(neck_point, height, forward) from world-space region verts."""
        zs = [v.z for v in objs_verts]
        z0, z1 = min(zs), max(zs)
        band = [v for v in objs_verts if v.z <= z0 + 0.15 * (z1 - z0)]
        top = [v for v in objs_verts if v.z >= z0 + 0.5 * (z1 - z0)]
        neck = sum(band, Vector()) / len(band)
        cen = sum(top, Vector()) / len(top)
        fwd = Vector((cen.x - neck.x, cen.y - neck.y, 0))
        return neck, z1 - z0, (fwd.normalized() if fwd.length > 1e-4 else None)

    def prepare_swap_source(src_path, item):
        """Decode meshopt/quantized sources (Tripo exports) via gltf-transform."""
        exts = []
        try:
            if src_path.lower().endswith('.glb'):
                with open(src_path, 'rb') as f:
                    head = f.read(20)
                    clen = struct.unpack('<I', head[12:16])[0]
                    doc = json.loads(f.read(clen))
                exts = doc.get('extensionsUsed', [])
            elif src_path.lower().endswith('.gltf'):
                exts = json.load(open(src_path, encoding='utf-8')).get('extensionsUsed', [])
        except Exception as e:
            fail(item, f'cannot read source header {src_path}: {e}')
            return None
        if not any(e in exts for e in ('EXT_meshopt_compression', 'KHR_mesh_quantization')):
            return src_path
        import shutil, subprocess, tempfile
        if not shutil.which('npx'):
            fail(item, f'source needs decode ({exts}) but npx is unavailable; '
                       f'pre-decode it with: npx @gltf-transform/cli copy + dequantize')
            return None
        tmp = tempfile.mkdtemp(prefix='csbake-swap-')
        mid, out = os.path.join(tmp, 'mid.glb'), os.path.join(tmp, 'decoded.glb')
        for cmd, i_, o_ in ((['npx', '--yes', '@gltf-transform/cli', 'copy'], src_path, mid),
                            (['npx', '--yes', '@gltf-transform/cli', 'dequantize'], mid, out)):
            r = subprocess.run(cmd + [i_, o_], capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                fail(item, f'gltf-transform failed on {src_path}: {r.stderr.strip()[:300]}')
                return None
        log(f'CSBAKE swap source decoded: {src_path} -> {out} (was {exts})')
        return out

    for si, swap in enumerate(cfg.get('region_swaps') or []):
        item = f'region_swaps[{si}]'
        region = swap.get('region')
        src_rel = swap.get('from_glb')
        if region not in REGION_ANCHORS or not src_rel:
            fail(item, f'bad swap spec (region={region}, from_glb={src_rel})')
            continue
        src_path = src_rel if os.path.isabs(src_rel) else os.path.join(repo_root, src_rel)
        if not os.path.exists(src_path):
            fail(item, f'source glb missing: {src_path}')
            continue
        if not base_arm:
            fail(item, 'base GLB has no armature; cannot re-skin a swapped region')
            continue
        # target region reference BEFORE the cut
        tgt_verts = []
        for o in meshes:
            if not o.vertex_groups:
                continue
            wv = world_verts(o)
            for v in o.data.vertices:
                dc = dominant_canon(o, v)
                if dc and bone_in_region(dc, region):
                    tgt_verts.append(wv[v.index])
        if not tgt_verts:
            fail(item, f'no base verts found in region "{region}" (dominant-bone rule)')
            continue
        t_neck, t_h, t_fwd = region_ref(tgt_verts, region)
        cut_total = sum(cut_region_from(o, region) for o in list(meshes))
        log(f'CSBAKE swap {item}: cut {cut_total} base verts in region {region}')
        meshes = [o for o in scene.objects if o.type == 'MESH']
        # source: decode if needed, import, isolate the region
        dec_path = prepare_swap_source(src_path, item)
        if not dec_path:
            continue
        before = set(bpy.context.scene.objects)
        try:
            bpy.ops.import_scene.gltf(filepath=dec_path)
        except Exception as e:
            fail(item, f'source import failed ({dec_path}): {e}')
            continue
        src_objs = [o for o in bpy.context.scene.objects if o not in before]
        src_meshes = [o for o in src_objs if o.type == 'MESH']
        src_arms = [o for o in src_objs if o.type == 'ARMATURE']
        bpy.context.view_layer.update()
        # Normalize every source mesh to evaluated WORLD-space geometry
        # (vertex groups/materials/UVs preserved), unparented, identity
        # basis — from here on, data verts ARE world verts for both the
        # skinned and unskinned paths.
        dg = bpy.context.evaluated_depsgraph_get()
        norm_meshes = []
        for o in src_meshes:
            ev = o.evaluated_get(dg)
            me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
            me.transform(o.matrix_world)
            old = o.data
            o.data = me
            o.parent = None
            o.matrix_basis = Matrix.Identity(4)
            if old.users == 0:
                bpy.data.meshes.remove(old)
            norm_meshes.append(o)
        src_meshes = norm_meshes
        graft = []
        src_skinned = any(len(o.vertex_groups) > 0 and
                          any(len(v.groups) for v in o.data.vertices[:64])
                          for o in src_meshes)
        keep_verts = []
        if src_skinned:
            for o in src_meshes:
                for v in o.data.vertices:
                    dc = dominant_canon(o, v)
                    if dc and bone_in_region(dc, region):
                        keep_verts.append(v.co.copy())
            # cut = remove everything NOT in the region
            for o in src_meshes:
                if not o.vertex_groups:
                    bpy.data.objects.remove(o, do_unlink=True)
                    continue
                bm = bmesh.new(); bm.from_mesh(o.data)
                kill_idx = set()
                for v in o.data.vertices:
                    dc = dominant_canon(o, v)
                    if not dc or not bone_in_region(dc, region):
                        kill_idx.add(v.index)
                kill = []
                if kill_idx:
                    bm.verts.ensure_lookup_table()
                    kill = [bm.verts[i] for i in sorted(kill_idx)]
                if kill:
                    bmesh.ops.delete(bm, geom=kill, context='VERTS')
                bm.to_mesh(o.data); bm.free(); o.data.update()
                if len(o.data.vertices):
                    graft.append(o)
                else:
                    bpy.data.objects.remove(o, do_unlink=True)
            if not keep_verts:
                fail(item, f'skinned source has no verts in region "{region}"')
        else:
            # spatial neck-pinch cut (head only): scan bands along Z (Blender
            # up after import), find the narrowest cross-section in the
            # upper body, keep what is above it.
            if region != 'head':
                fail(item, f'unskinned source only supports region "head" (got "{region}")')
            allw = []
            for o in src_meshes:
                allw += [v.co.copy() for v in o.data.vertices]
            if not allw:
                fail(item, 'unskinned source imported with no verts')
                allw = None
            if allw:
                zs = [v.z for v in allw]
                z0, z1 = min(zs), max(zs)
                best_z, best_span = None, None
                steps = 24
                for i in range(steps + 1):
                    zc = z0 + (z1 - z0) * (0.55 + 0.40 * i / steps)
                    band = [v for v in allw if abs(v.z - zc) <= 0.02 * (z1 - z0)]
                    if len(band) < 8:
                        continue
                    span = (max(v.x for v in band) - min(v.x for v in band)) * \
                           (max(v.y for v in band) - min(v.y for v in band))
                    if best_span is None or span < best_span:
                        best_span, best_z = span, zc
                log(f'CSBAKE swap {item}: neck pinch at z={best_z:.3f} (model z {z0:.2f}..{z1:.2f})')
                keep_verts = [v for v in allw if v.z >= best_z]
                for o in src_meshes:
                    bm = bmesh.new(); bm.from_mesh(o.data)
                    kill = [v for v in bm.verts if v.co.z < best_z]
                    if kill:
                        bmesh.ops.delete(bm, geom=kill, context='VERTS')
                    bm.to_mesh(o.data); bm.free(); o.data.update()
                    if len(o.data.vertices):
                        graft.append(o)
        if not graft or not keep_verts:
            for o in src_objs:
                bpy.data.objects.remove(o, do_unlink=True)
            if not graft:
                fail(item, 'nothing left of the source after the region cut')
            continue
        s_neck, s_h, s_fwd = region_ref(keep_verts, region)
        k = float(swap.get('scale') or (t_h / s_h if s_h > 1e-6 else 1.0))
        yaw = 0.0
        if t_fwd and s_fwd:
            from math import atan2
            yaw = atan2(t_fwd.y, t_fwd.x) - atan2(s_fwd.y, s_fwd.x)
        if swap.get('yaw_deg'):
            from math import radians
            yaw += radians(float(swap['yaw_deg']))
        from math import cos, sin
        R = Matrix(((cos(yaw), -sin(yaw), 0), (sin(yaw), cos(yaw), 0), (0, 0, 1)))
        arm_inv = base_arm.matrix_world.inverted()
        tgt_bone_by_canon = {}
        for b in base_arm.data.bones:
            tgt_bone_by_canon.setdefault(canon_bone(b.name), b.name)
        anchors = []
        for an in REGION_ANCHORS[region]:
            ab = base_arm.data.bones.get(an)
            if ab:
                anchors.append((an, ab.head_local, ab.tail_local))
        for o in graft:
            me = o.data
            for v in me.vertices:
                v.co = t_neck + R @ ((v.co - s_neck) * k)
            me.transform(arm_inv)   # world -> base armature space
            o.matrix_world = Matrix.Identity(4)
            # --- re-skin onto the base rig
            if src_skinned:
                remap = {}
                for g in list(o.vertex_groups):
                    tgt = tgt_bone_by_canon.get(canon_bone(g.name))
                    if tgt and tgt != g.name:
                        remap[g.name] = tgt
                for old, new in remap.items():
                    if new in o.vertex_groups:
                        # merge weights into the existing group
                        og, ng = o.vertex_groups[old], o.vertex_groups[new]
                        for v in me.vertices:
                            w = {e.group: e.weight for e in v.groups}
                            if og.index in w:
                                ng.add([v.index], w.get(ng.index, 0.0) + w[og.index], 'REPLACE')
                        o.vertex_groups.remove(og)
                    else:
                        o.vertex_groups[old].name = new
                drop = [g for g in list(o.vertex_groups) if g.name not in base_bones]
                for g in drop:
                    o.vertex_groups.remove(g)
            else:
                for g in list(o.vertex_groups):
                    o.vertex_groups.remove(g)
                groups = {}
                for an, h, t in anchors:
                    groups[an] = o.vertex_groups.new(name=an)
                for v in me.vertices:
                    ws = {}
                    for an, h, t in anchors:
                        seg = t - h
                        L2 = max(seg.length_squared, 1e-9)
                        u = min(1.0, max(0.0, (v.co - h).dot(seg) / L2))
                        d = (v.co - (h + seg * u)).length
                        ws[an] = 1.0 / (d * d + 1e-5)
                    tot = sum(ws.values())
                    for an, w in ws.items():
                        if w / tot > 0.01:
                            groups[an].add([v.index], w / tot, 'REPLACE')
            for mod in list(o.modifiers):
                if mod.type == 'ARMATURE':
                    o.modifiers.remove(mod)
            mod = o.modifiers.new(name='Armature', type='ARMATURE')
            mod.object = base_arm
            o.parent = base_arm
            o.matrix_parent_inverse = Matrix.Identity(4)
        for a in src_arms:
            if a.name in bpy.context.scene.objects:
                bpy.data.objects.remove(a, do_unlink=True)
        meshes = [o for o in scene.objects if o.type == 'MESH']
        log(f'CSBAKE swap {item}: grafted {region} from {src_rel} '
            f'({len(graft)} mesh(es), scale {k:.3f}, yaw {yaw:.2f} rad, skinned-src={src_skinned})')

    # ---- (b) textures ------------------------------------------------------
    def find_material(pred, what):
        for o in meshes:
            for slot in o.data.materials:
                if slot and pred(slot):
                    return slot
        fail('textures', f'no material matched {what}')
        return None

    def base_color_image(mat):
        if not mat or not mat.use_nodes:
            return None
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                link = node.inputs['Base Color'].links
                if link and link[0].from_node.type == 'TEX_IMAGE':
                    return link[0].from_node.image
        return None

    def resolve_texture_target(entry):
        """-> (material, placement_dict) using the documented resolution order."""
        placement = {}
        part = reg_parts.get(entry.get('part_id'))
        if part:
            placement.update(part.get('placement') or {})
        kind = entry.get('kind')
        # Character-specific mappings OVERRIDE the part's default placement
        # (mirrors parts.js resolveEntry: character_mappings win).
        cmap = char_maps.get(fighter, {})
        kind_map = cmap.get(kind) or (cmap.get(kind.replace('_logo', '')) if kind else None)
        if kind_map:
            placement.update({k: v for k, v in kind_map.items() if v})
        # baek-eyes pattern: customization/parts/<fighter>-eyes/MANIFEST.json
        if kind == 'eye':
            man = os.path.join(repo_root, 'customization', 'parts', f'{fighter}-eyes', 'MANIFEST.json')
            if os.path.exists(man):
                try:
                    mj = json.load(open(man, encoding='utf-8'))
                    et = mj.get('eye_texture', '')
                    tok = et.split('(')[0].strip()
                    mat_tok = et[et.find('(') + 1:et.find(')')].split()[0] if '(' in et else ''
                    if tok:
                        placement['texture'] = tok
                    if mat_tok:
                        placement['material'] = mat_tok
                    um = mj.get('universal_mapping') or {}
                    if isinstance(um, dict):
                        placement.setdefault('mode', um.get('mode', 'full_replace'))
                except Exception as e:
                    fail('textures', f'cannot parse {man}: {e}')
        # Explicit entry fields win over everything.
        if entry.get('material'):
            placement['material'] = entry['material']
        if entry.get('texture'):
            placement['texture'] = entry['texture']
        mat = None
        want_mat = (placement.get('material') or '').lower()
        want_tex = (placement.get('texture') or '').lower()
        for o in meshes:
            for slot in o.data.materials:
                if not slot:
                    continue
                img = base_color_image(slot)
                img_name = (img.name if img else '').lower()
                if want_mat and want_mat in slot.name.lower():
                    mat = slot; break
                if want_tex and (want_tex in img_name or want_tex in slot.name.lower()):
                    mat = slot; break
            if mat:
                break
        return mat, placement

    for ti, entry in enumerate(cfg.get('textures') or []):
        item = f"textures[{ti}] part_id={entry.get('part_id')}"
        src_rel = entry.get('image')
        part = reg_parts.get(entry.get('part_id'))
        if not src_rel and part:
            src_rel = part.get('asset')
        if not src_rel:
            fail(item, 'no image in entry and no asset on the registry part')
            continue
        src_path = src_rel if os.path.isabs(src_rel) else os.path.join(repo_root, src_rel)
        if not os.path.exists(src_path):
            fail(item, f'image missing: {src_path}')
            continue
        mat, placement = resolve_texture_target(entry)
        if not mat:
            fail(item, f'placement resolved to no material (placement={placement})')
            continue
        img = base_color_image(mat)
        if not img:
            fail(item, f'material {mat.name} has no base-color image')
            continue
        import numpy as np
        src = bpy.data.images.load(src_path)
        W, H = img.size
        SW, SH = src.size
        tpix = np.empty(W * H * 4, dtype=np.float32)
        img.pixels.foreach_get(tpix)
        timg = tpix.reshape(H, W, 4)
        rect = entry.get('rect')
        mode = placement.get('mode')
        if rect:
            x, y, w, h = [int(v) for v in rect]
            region = (x, y, w, h)
        elif mode == 'full_replace' or not rect:
            region = (0, 0, W, H)
        x, y, w, h = region
        # resize source to region via Blender scale, sample its pixels
        if (SW, SH) != (w, h):
            src.scale(w, h)
            SW, SH = w, h
        spix = np.empty(SW * SH * 4, dtype=np.float32)
        src.pixels.foreach_get(spix)
        simg = spix.reshape(SH, SW, 4)
        # Blender image rows are bottom-up; schema rect is top-left origin.
        yb = H - y - h
        if x < 0 or yb < 0 or x + w > W or yb + h > H:
            fail(item, f'rect {region} outside target texture {W}x{H}')
            continue
        dst = timg[yb:yb + h, x:x + w]
        # Both images live in Blender's bottom-up pixel space, so copying rows
        # directly preserves the source file's visual orientation in the rect.
        src_flip = simg
        alpha = src_flip[:, :, 3:4]
        dst[:, :, :] = src_flip * alpha + dst * (1 - alpha)
        img.pixels.foreach_set(timg.ravel())
        img.update()
        try:
            img.pack()
        except Exception:
            pass
        bpy.data.images.remove(src)
        log(f'CSBAKE texture applied: {item} -> material {mat.name} image {img.name} region {region} mode={mode}')

    # ---- (c) mesh parts ----------------------------------------------------
    # ROUND 2 (2026-10-21): placement is EXACT bone-local, by construction.
    # Round 1 set matrix_parent_inverse = armature_world^-1 only, which left
    # the socket bone's own matrix inside the transform — the saved numbers
    # were world-compensations, not bone-local offsets, and parts landed
    # "close but wrong" (owner graded the Master White hair/beard 40/100).
    # Now: a part's evaluated world geometry is re-expressed in the part's
    # OWN socket-bone frame, the placement transform is applied in that
    # frame, and the result is skinned rigidly (100% weight) to the base
    # socket bone:
    #   world = base_bone_world x T(placement) x part_bone_local_geometry
    # Placement (0,0,0 / 0deg / scale 1) = the part in its native registration
    # on the socket bone. (Bone-PARENTED objects were tried first and
    # rejected: the glTF exporter bakes their world transform into the
    # geometry while keeping the node TRS, so importers double-transform
    # them. Skinning evaluates identically everywhere.) Provable from the
    # output GLB alone (customization/tools/proof/cs-round2-roundtrip.py).
    SOCKETS = {  # mirrors packages/creation-suite/src/attire.js SOCKETS
        # 'eye' (owner verdict 2026-10-20: eyes are real placeable mesh parts)
        # uses the Head-bone aliases, same as 'face'.
        'eye': ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head', 'DEF-head'],
        'face': ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head', 'DEF-head'],
        'head': ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head', 'DEF-head'],
        'hair': ['Head', 'mixamorig:Head', 'head', 'DEF-head'],
        'torso': ['Chest', 'Spine2', 'mixamorig:Spine2', 'Spine', 'DEF-spine.003'],
        'jacket': ['Chest', 'Spine2', 'mixamorig:Spine2', 'DEF-spine.003'],
        'waist': ['Hips', 'mixamorig:Hips', 'pelvis', 'DEF-hips'],
        'hands': ['RightHand', 'mixamorig:RightHand'],
        'accessory': ['Chest', 'Neck'],
    }

    def apply_part_tint(objs, tint_hex, item):
        """Tint a part's materials (round-2 per-part tint). Textured
        materials get the tint multiplied into a CLONE of their base-color
        image (a Principled default-value multiply is a no-op under a
        texture, and node-graph tricks don't survive glTF export);
        untextured materials get the factor multiply. Materials are cloned
        first so a tint can never leak into the base model or another part."""
        if not tint_hex:
            return
        import numpy as np
        r, g, b = hex_rgb(tint_hex)
        seen = {}
        for o in objs:
            for idx, ms in enumerate(o.material_slots):
                if not ms.material:
                    continue
                if ms.material.name not in seen:
                    seen[ms.material.name] = ms.material.copy()
                o.material_slots[idx].material = seen[ms.material.name]
        tinted_imgs = set()
        for mat in seen.values():
            if not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type != 'BSDF_PRINCIPLED':
                    continue
                link = node.inputs['Base Color'].links
                if link and link[0].from_node.type == 'TEX_IMAGE':
                    img = link[0].from_node.image
                    if img and img.name not in tinted_imgs:
                        tinted_imgs.add(img.name)
                        clone = img.copy()
                        link[0].from_node.image = clone
                        px = np.empty(len(clone.pixels), dtype=np.float32)
                        clone.pixels.foreach_get(px)
                        px = px.reshape(-1, 4)
                        px[:, 0] *= r; px[:, 1] *= g; px[:, 2] *= b
                        clone.pixels.foreach_set(px.ravel())
                        clone.update()
                        try:
                            clone.pack()
                        except Exception:
                            pass
                else:
                    cur = node.inputs['Base Color'].default_value
                    cur[0] *= r; cur[1] *= g; cur[2] *= b
        log(f'CSBAKE part tint: {item} {tint_hex} -> {len(seen)} material(s), '
            f'{len(tinted_imgs)} texture(s) multiplied')

    _base_skin_cache = {}

    def skin_part_from_base(part_obj, arm_obj):
        """Copy skin weights onto a part from the nearest base verts.

        Base = every non-cs_ mesh in the scene carrying vertex groups (the
        imported base model's own skin). Vert coords are armature space on
        both sides (imported mesh objects sit at identity under the
        armature; part geometry was transformed into armature space by the
        caller). Built once per bake and cached.
        """
        if 'tree' not in _base_skin_cache:
            pts, wsets = [], []
            for bo in bpy.context.scene.objects:
                if bo.type != 'MESH' or bo.name.startswith('cs_'):
                    continue
                if not bo.vertex_groups:
                    continue
                gnames = [g.name for g in bo.vertex_groups]
                for v in bo.data.vertices:
                    ws = [(gnames[g.group], g.weight) for g in v.groups
                          if g.weight > 0.0 and g.group < len(gnames)]
                    if ws:
                        pts.append(v.co.copy())
                        wsets.append(ws)
            tree = KDTree(len(pts))
            for i, p in enumerate(pts):
                tree.insert(p, i)
            tree.balance()
            _base_skin_cache['tree'] = tree
            _base_skin_cache['wsets'] = wsets
            log(f'CSBAKE base skin field: {len(pts)} verts indexed')
        tree, wsets = _base_skin_cache['tree'], _base_skin_cache['wsets']
        groups = {}
        for v in part_obj.data.vertices:
            _co, idx, _dist = tree.find(v.co)
            for gname, w in wsets[idx]:
                vg = groups.get(gname)
                if vg is None:
                    vg = part_obj.vertex_groups.get(gname) or \
                        part_obj.vertex_groups.new(name=gname)
                    groups[gname] = vg
                vg.add([v.index], w, 'REPLACE')

    def placement_xform(placement):
        from math import radians
        s = placement.get('s', 1)
        return {
            'location': Vector((placement.get('px', 0), placement.get('py', 0), placement.get('pz', 0))),
            'rotation': (radians(placement.get('rx', 0)), radians(placement.get('ry', 0)),
                         radians(placement.get('rz', 0))),
            'scale': Vector((placement.get('sx', s), placement.get('sy', s), placement.get('sz', s))),
        }

    for slot, spec in (cfg.get('parts') or {}).items():
        item = f'parts.{slot}'
        if not spec:
            continue
        glb_rel = spec.get('glb')
        part = reg_parts.get(spec.get('part_id'))
        if not glb_rel and part:
            glb_rel = part.get('asset')
        if not glb_rel:
            fail(item, 'no glb in spec and no asset on the registry part')
            continue
        glb_path = glb_rel if os.path.isabs(glb_rel) else os.path.join(repo_root, glb_rel)
        if not os.path.exists(glb_path):
            fail(item, f'part glb missing: {glb_path}')
            continue
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=glb_path)
        new_objs = [o for o in bpy.context.scene.objects if o not in before]
        new_arms = [o for o in new_objs if o.type == 'ARMATURE']
        new_meshes = [o for o in new_objs if o.type == 'MESH']
        if new_arms:
            # Source scenes can carry helper props that are not part of the
            # piece (the CC0 hair files ship a root-level Icosphere). Only
            # meshes tied to the part's own rig are the part.
            keep = [o for o in new_meshes
                    if o.parent in new_arms or len(o.vertex_groups) > 0 or
                    any(m.type == 'ARMATURE' and m.object in new_arms for m in o.modifiers)]
            for o in new_meshes:
                if o not in keep:
                    log(f'CSBAKE part: dropping non-part prop {o.name} from {glb_rel}')
                    bpy.data.objects.remove(o, do_unlink=True)
                    new_objs.remove(o)
            new_meshes = keep
        placement = spec.get('placement') or {}
        base_bones = {b.name for b in base_arm.data.bones} if base_arm else set()
        part_bones = set()
        for a in new_arms:
            part_bones |= {b.name for b in a.data.bones}
        if new_arms and part_bones and part_bones <= base_bones:
            # Skinned-merge: the part's own rig IS the base rig — skinning
            # carries the registration, so a bone-local placement offset has
            # no frame to act on. Warn loudly if one was saved anyway.
            if any(placement.get(k) for k in ('px', 'py', 'pz', 'rx', 'ry', 'rz')) or \
               placement.get('s', 1) != 1:
                log(f'CSBAKE WARN [{item}]: placement ignored on skinned-merge part '
                    f'(its rig matches the base rig; placement only applies to socket-attached parts)')
            for o in new_meshes:
                for mod in o.modifiers:
                    if mod.type == 'ARMATURE' and mod.object in new_arms:
                        mod.object = base_arm
                if o.parent in new_arms:
                    o.parent = None
            for a in new_arms:
                bpy.data.objects.remove(a, do_unlink=True)
            apply_part_tint(new_meshes, spec.get('tint'), item)
            log(f'CSBAKE part skinned-merge: {item} ({len(new_meshes)} meshes re-bound to base rig)')
        else:
            if not base_arm:
                fail(item, 'base GLB has no armature; cannot bone-parent part')
                continue
            aliases = []
            if part and (part.get('placement') or {}).get('bone_aliases'):
                aliases = part['placement']['bone_aliases']
            aliases = aliases or SOCKETS.get(slot, [])
            bone = next((n for n in aliases if n in base_bones), None)
            if not bone:
                fail(item, f'no socket bone for slot "{slot}" (aliases tried: {aliases})')
                continue
            # The part's own socket frame: the alias bone on the part's rig
            # if it has one, else the bone its verts are weighted to most,
            # else identity (unskinned part: attach by bbox centre, below).
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            frame_inv = None
            frame_desc = 'identity (unskinned, bbox-centre attach)'
            part_arm = new_arms[0] if new_arms else None
            if part_arm:
                pbones = {b.name for b in part_arm.data.bones}
                p_bone = next((n for n in aliases if n in pbones), None)
                if not p_bone:
                    from collections import Counter
                    cnt = Counter()
                    for o in new_meshes:
                        for g in o.vertex_groups:
                            cnt[g.name] += 1
                    p_bone = next((n for n, _ in cnt.most_common() if n in pbones), None)
                if p_bone:
                    frame_inv = (part_arm.matrix_world @
                                 part_arm.data.bones[p_bone].matrix_local).inverted()
                    frame_desc = f'part bone {p_bone}'
            attached = []
            xf = placement_xform(placement)
            from mathutils import Euler
            T_place = (Matrix.Translation(xf['location']) @
                       Euler(xf['rotation'], 'XYZ').to_matrix().to_4x4() @
                       Matrix.Diagonal(xf['scale']).to_4x4())
            bone_local_mtx = base_arm.data.bones[bone].matrix_local
            for o in new_meshes:
                ev = o.evaluated_get(dg)
                me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
                me.transform(o.matrix_world)          # world-space bind geometry
                if frame_inv is not None:
                    me.transform(frame_inv)            # -> part socket-bone local
                else:
                    vs = [v.co for v in me.vertices]
                    if vs:
                        c = sum(vs, Vector()) / len(vs)
                        me.transform(Matrix.Translation(-c))
                # Skin the part rigidly to the socket bone (100% weight),
                # geometry in base-armature space. Bone-PARENTED objects are
                # a portability trap — the glTF exporter bakes their world
                # transform into the geometry while keeping the node TRS,
                # so importers double-transform them (found the hard way:
                # perfect measurements, parts hanging off the head in the
                # render). Plain skinning is the one path every consumer
                # (Blender, three.js, the game) evaluates identically.
                me.transform(bone_local_mtx @ T_place)   # -> base armature space
                no = bpy.data.objects.new(f'cs_{slot}_{o.name}', me)
                bpy.context.collection.objects.link(no)
                # Weight the part from the BASE's own skin field (nearest
                # base vert's full weight set), NOT a flat 100% socket bone:
                # the surface a part sits on blends several bones (Head/Neck/
                # Spine), and wherever those frames differ — T7 Baek's bind
                # has a turned head/neck — a rigid one-bone part shears away
                # from the surface (the Master White "ring": perfect bind
                # numbers, parts visibly rotated off the head in renders).
                # Copying the local field makes the part deform WITH the
                # surface it sits on, in bind and in animation alike.
                skin_part_from_base(no, base_arm)
                mod = no.modifiers.new(name='Armature', type='ARMATURE')
                mod.object = base_arm
                no.parent = base_arm
                no.matrix_parent_inverse = Matrix.Identity(4)
                attached.append(no)
            for o in new_objs:
                bpy.data.objects.remove(o, do_unlink=True)
            apply_part_tint(attached, spec.get('tint'), item)
            log(f'CSBAKE part socket-skinned: {item} -> bone {bone} frame={frame_desc} placement={placement}')

    # ---- (d) colors ----------------------------------------------------------
    for kind, hexval in (cfg.get('colors') or {}).items():
        if not hexval:
            continue
        item = f'colors.{kind}'
        targets = []
        cmap = char_maps.get(fighter, {})
        kind_map = cmap.get(kind) or {}
        # A mapping names ONE material via "material" (the texture-part path)
        # and may name MORE via "materials" — colors like skin tone live on
        # many materials at once (round 2: Baek's skin spans 10 pek1u mats).
        want_mats = [m.lower() for m in
                     ([kind_map.get('material')] if kind_map.get('material') else []) +
                     (kind_map.get('materials') or [])]
        for o in meshes:
            for slot in o.data.materials:
                if not slot:
                    continue
                if any(w in slot.name.lower() for w in want_mats) or \
                   (not want_mats and kind in slot.name.lower()):
                    if slot not in targets:
                        targets.append(slot)
        if not targets:
            fail(item, f'no material resolved for color "{kind}" (registry mapping or material name must name it)')
            continue
        r, g, b = hex_rgb(hexval)
        for mat in targets:
            for node in mat.node_tree.nodes if mat.use_nodes else []:
                if node.type == 'BSDF_PRINCIPLED':
                    cur = node.inputs['Base Color'].default_value
                    cur[0] *= r; cur[1] *= g; cur[2] *= b
            log(f'CSBAKE color tint: {item} {hexval} -> material {mat.name}')

    # ---- validate + export ---------------------------------------------------
    import numpy as np
    for o in [x for x in scene.objects if x.type == 'MESH']:
        co = np.empty(len(o.data.vertices) * 3, dtype=np.float64)
        if len(o.data.vertices):
            o.data.vertices.foreach_get('co', co)
            if not np.isfinite(co).all():
                fail('validate', f'NaN/Inf vertex coords in {o.name}')
    if any(i == 'validate' for i, _ in errors):
        log('CSBAKE FATAL: validation failed, not exporting')
        return 2, errors
    os.makedirs(os.path.dirname(out_glb), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB')
    log(f'CSBAKE wrote {out_glb} ({os.path.getsize(out_glb)} bytes)')
    return (2 if errors else 0), errors


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    # plain-python emit mode
    if '--emit-registry' in argv:
        root = '.'
        if '--repo-root' in argv:
            root = argv[argv.index('--repo-root') + 1]
        emit_registry(find_repo_root(root))
        return 0
    positional = [a for a in argv if not a.startswith('--') and a not in
                  (argv[argv.index('--mpfb-src') + 1] if '--mpfb-src' in argv else [])]
    if not positional:
        print(__doc__)
        return 1
    target = positional[0]
    cfg_path = target if target.endswith('.json') else os.path.join(target, 'customization.json')
    if not os.path.exists(cfg_path):
        print(f'CSBAKE FATAL: customization.json not found: {cfg_path}')
        return 1
    repo_root = find_repo_root(os.path.dirname(os.path.abspath(cfg_path)))
    mpfb_src = None
    if '--mpfb-src' in argv:
        mpfb_src = argv[argv.index('--mpfb-src') + 1]
    else:
        default_mpfb = os.path.expanduser('~/workspace/cape-jones/production/tools/mpfb2')
        mpfb_src = default_mpfb if os.path.isdir(default_mpfb) else None
    try:
        import bpy  # noqa: F401
    except ImportError:
        print('CSBAKE FATAL: bpy unavailable — run under Blender headless (see docstring)')
        return 1
    code, errors = bake(cfg_path, repo_root, mpfb_src)
    if '--no-emit' not in argv:
        emit_registry(repo_root)
    if errors:
        print('CSBAKE ERRORS:')
        for item, msg in errors:
            print(f'  - [{item}] {msg}')
    print(f'CSBAKE DONE exit={code}')
    return code


if __name__ == '__main__':
    sys.exit(main())
