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
                      bone-local space.
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
import json, os, re, sys

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
    from mathutils import Vector
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
                morph_deltas = {}
                for mid in need_transfer:
                    val = morphs[mid]
                    acc = {}
                    rels = suite_targets[mid]
                    for rel in rels:
                        r = rel.replace('{min,max}', 'max' if val >= 0 else 'min')
                        path = os.path.join(targets_dir, r + '.target.gz')
                        if not os.path.exists(path):
                            path = os.path.join(targets_dir, r + '.target')
                        if not os.path.exists(path):
                            fail('morphs', f'MPFB target missing: {r}')
                            continue
                        opener = gzip.open if path.endswith('.gz') else open
                        with opener(path, 'rt') as fh:
                            for line in fh:
                                parts = line.split()
                                if len(parts) < 4 or line.lstrip().startswith('#'):
                                    continue
                                i = int(parts[0])
                                d = Vector((float(parts[1]), float(parts[3]), float(parts[2])))  # (x, z, y)
                                s = (abs(val) if '{min,max}' in rel else val) / len(rels)
                                acc[i] = acc.get(i, Vector((0, 0, 0))) + d * s
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
        # drive every MPFB_<id> key to its saved value, then bake the mix into Basis
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
                kb['MPFB_' + mid].value = 0.0 if mid in (transferred.get(o.name) or []) else morphs[mid]
            # new-coord = basis + sum(value * (key - basis)); transferred keys are
            # pre-scaled, so their effective value is 1.0 with the key itself set 0
            # -> fold them in explicitly:
            import numpy as np
            n = len(mesh.vertices)
            base_co = np.empty(n * 3, dtype=np.float64)
            kb['Basis'].data.foreach_get('co', base_co)
            mix = base_co.copy()
            for mid in active:
                key = kb['MPFB_' + mid]
                eff = 1.0 if mid in (transferred.get(o.name) or []) else morphs[mid]
                if eff == 0.0:
                    continue
                kc = np.empty(n * 3, dtype=np.float64)
                key.data.foreach_get('co', kc)
                mix += eff * (kc - base_co)
            kb['Basis'].data.foreach_set('co', mix)
            mesh.update()
            for mid in active:
                mesh.shape_keys.key_blocks.remove(kb['MPFB_' + mid])
            baked.append((o.name, active))
        log(f'CSBAKE morphs baked into Basis: {baked}')

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
        cmap = char_maps.get(fighter, {})
        kind_map = cmap.get(kind) or (cmap.get(kind.replace('_logo', '')) if kind else None)
        if kind_map:
            placement.update({k: v for k, v in kind_map.items() if v})
        if entry.get('material'):
            placement['material'] = entry['material']
        if entry.get('texture'):
            placement['texture'] = entry['texture']
        # baek-eyes pattern: customization/parts/<fighter>-eyes/MANIFEST.json
        if kind == 'eye' and not placement.get('texture'):
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
    SOCKETS = {  # mirrors packages/creation-suite/src/attire.js SOCKETS
        'face': ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head'],
        'head': ['Head', 'mixamorig:Head', 'head', 'J_Head', 'Bip01 Head'],
        'hair': ['Head', 'mixamorig:Head', 'head'],
        'torso': ['Chest', 'Spine2', 'mixamorig:Spine2', 'Spine'],
        'jacket': ['Chest', 'Spine2', 'mixamorig:Spine2'],
        'waist': ['Hips', 'mixamorig:Hips', 'pelvis'],
        'hands': ['RightHand', 'mixamorig:RightHand'],
        'accessory': ['Chest', 'Neck'],
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
        new_meshes = [o for o in new_objs if o.type == 'MESH']
        new_arms = [o for o in new_objs if o.type == 'ARMATURE']
        placement = spec.get('placement') or {}
        base_bones = {b.name for b in base_arm.data.bones} if base_arm else set()
        part_bones = set()
        for a in new_arms:
            part_bones |= {b.name for b in a.data.bones}
        if new_arms and part_bones and part_bones <= base_bones:
            for o in new_meshes:
                for mod in o.modifiers:
                    if mod.type == 'ARMATURE' and mod.object in new_arms:
                        mod.object = base_arm
                if o.parent in new_arms:
                    o.parent = None
            for a in new_arms:
                bpy.data.objects.remove(a, do_unlink=True)
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
            from math import radians
            for o in new_objs:
                if o.parent in new_objs:
                    continue
                o.parent = base_arm
                o.parent_type = 'BONE'
                o.parent_bone = bone
                o.matrix_parent_inverse = base_arm.matrix_world.inverted()
                if placement:
                    o.location = (placement.get('px', 0), placement.get('py', 0), placement.get('pz', 0))
                    o.rotation_euler = (radians(placement.get('rx', 0)), radians(placement.get('ry', 0)),
                                        radians(placement.get('rz', 0)))
                    s = placement.get('s', 1)
                    o.scale = (s, s, s)
            log(f'CSBAKE part bone-parented: {item} -> bone {bone} placement={placement}')

    # ---- (d) colors ----------------------------------------------------------
    def hex_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    for kind, hexval in (cfg.get('colors') or {}).items():
        if not hexval:
            continue
        item = f'colors.{kind}'
        targets = []
        cmap = char_maps.get(fighter, {})
        want_mat = ((cmap.get(kind) or {}).get('material') or '').lower()
        for o in meshes:
            for slot in o.data.materials:
                if not slot:
                    continue
                if (want_mat and want_mat in slot.name.lower()) or kind in slot.name.lower():
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
