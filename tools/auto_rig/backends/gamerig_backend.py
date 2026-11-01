#!/usr/bin/env python3
"""tools/auto_rig/backends/gamerig_backend.py — GameRig auto-rig backend.

Rigs an unrigged humanoid static (e.g. a Tripo GLB) with GameRig
(Arminando's game-engine Rigify feature set, vendored at
tools/open-source/gamerig/) and exports a game-ready GLB whose deform
skeleton uses the WH canonical (Mixamo-style) joint names, so it passes
tools/auto_rig/validate.py and plays the game's existing clips.

Pipeline (all headless, one Blender run):
  1. Install the vendored GameRig as a Rigify feature set into Blender's
     user scripts dir (rigify/gamerig) and enable Rigify.
  2. Import the static GLB; normalize in Blender space (uniform scale to
     --height, feet on z=0, centered) and yaw it to face -Y (Rigify's
     convention) using a foot-vs-leg centroid facing estimate.
  3. Add the Rigify human metarig, strip the face subtree (WH skeletons
     have no face bones), fit it to the mesh: uniform scale, arm-chain
     X stretch from the mesh's arm-span/height ratio, leg X stretch from
     the hip-band width, and (T-pose statics) flatten the arm chain onto
     the shoulder line so the skeleton's rest pose IS the mesh's T-pose.
  4. Generate the game rig with GameRig's own operator
     (bpy.ops.pose.gamerig_generate): rig types are converted to their
     game.* equivalents, producing ONE deform hierarchy (DEF-* bones),
     no bendy bones, no deform-bone scaling.
  5. Skin with Blender bone heat (ARMATURE_AUTO) + nearest-bone fixup
     for unweighted verts (same fixup as blender_heat.py).
  6. Optionally transfer a real clip from a donor WH GLB (e.g. pantera's
     embedded Idle) onto the new rig with the rest-relative delta method
     of tools/anim-retarget/retarget_blender.py, keyframed onto the DEF
     bones, and export it with the model.
  7. Export GLB with deform bones only, then rename the skin joints to
     WH canonical names in the GLB JSON (post-export rename, the same
     canonicalization philosophy as backends/retarget.py).

Blender 4.0.2 note: the vendored GameRig targets Blender 4.5.4. Its
Generator_gamerig._create_root_bone predates Rigify's noparent_bones
bookkeeping in 4.0.2 and would parent the root bone to itself, so this
driver substitutes stock Rigify 4.0.2's create_root_bone for that one
method (the game.* rig modules — the actual GameRig deform logic — run
unmodified). See tools/open-source/gamerig/USAGE.md.

Run (mirrors blender_heat.py):
    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup \
        --python gamerig_backend.py -- --in STATIC.glb --out RIGGED.glb \
        [--height 1.8] [--donor game/assets/models/pantera.glb] \
        [--clip Idle] [--gamerig-dir ../../open-source/gamerig] \
        [--render-dir DIR] [--metrics-out M.json]
"""

import argparse
import json
import math
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GAMERIG_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "open-source", "gamerig"))

# ---------------------------------------------------------------------------
# Pure-python part (no bpy): DEF-bone -> WH canonical joint renaming.
# Importable without Blender so tools/auto_rig/tests can unit-test it.

CANONICAL_MAP = {
    "DEF-spine": "Hips",
    "DEF-spine.001": "Spine",
    "DEF-spine.002": "Spine1",
    "DEF-spine.003": "Spine2",
    "DEF-spine.004": "Neck",
    "DEF-spine.005": "Head",
    "DEF-spine.006": "HeadTop",
    "DEF-shoulder.L": "LeftShoulder",
    "DEF-shoulder.R": "RightShoulder",
    "DEF-upper_arm.L": "LeftArm",
    "DEF-upper_arm.R": "RightArm",
    "DEF-forearm.L": "LeftForeArm",
    "DEF-forearm.R": "RightForeArm",
    "DEF-hand.L": "LeftHand",
    "DEF-hand.R": "RightHand",
    "DEF-thigh.L": "LeftUpLeg",
    "DEF-thigh.R": "RightUpLeg",
    "DEF-shin.L": "LeftLeg",
    "DEF-shin.R": "RightLeg",
    "DEF-foot.L": "LeftFoot",
    "DEF-foot.R": "RightFoot",
    "DEF-toe.L": "LeftToeBase",
    "DEF-toe.R": "RightToeBase",
    "DEF-pelvis.L": "LeftPelvis",
    "DEF-pelvis.R": "RightPelvis",
    "DEF-breast.L": "LeftBreast",
    "DEF-breast.R": "RightBreast",
}

_FINGERS = {
    "thumb": "Thumb", "f_index": "Index", "f_middle": "Middle",
    "f_ring": "Ring", "f_pinky": "Pinky",
}


def def_to_canonical(name):
    """Map a GameRig/Rigify DEF bone name to the WH canonical joint name.

    Exact table first (spine chain, limbs, pelvis, breast); finger chains
    by pattern (DEF-thumb.01.L -> LeftHandThumb1); palm bones become
    Left/RightHandPalm<n>; leaf segment duplicates (DEF-upper_arm.L.001)
    keep a cleaned name (UpperArm.L.001 -> LeftArmLeaf1 style is NOT
    invented: they become 'LeftArm.001' via the prefix rule on the base
    name). Anything else loses only its DEF- prefix.
    """
    if name in CANONICAL_MAP:
        return CANONICAL_MAP[name]
    # leaf duplicates of a mapped bone: DEF-upper_arm.L.001
    for suffix in (".001", ".002"):
        if name.endswith(suffix) and name[:-4] in CANONICAL_MAP:
            return CANONICAL_MAP[name[:-4]] + suffix
    if name.startswith("DEF-"):
        body = name[4:]
        for src, dst in _FINGERS.items():
            for side, prefix in ((".L", "LeftHand"), (".R", "RightHand")):
                head = src + "."
                if body.startswith(head) and body.endswith(side):
                    num = body[len(head):-len(side)]
                    if num.isdigit():
                        return "%s%s%d" % (prefix, dst, int(num))
        for side, prefix in ((".L", "Left"), (".R", "Right")):
            if body.startswith("palm.") and body.endswith(side):
                num = body[len("palm."):-len(side)]
                if num.isdigit():
                    return "%sHandPalm%d" % (prefix, int(num))
        return body
    return name


def rename_glb_joints(path, mapping_fn=def_to_canonical):
    """Rename skin-joint node names in a GLB in place (JSON chunk only).

    Returns {old: new} for the joints that changed. Skinning data refers
    to joints by index, so renaming node names cannot break the skin.
    """
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        raise ValueError("not a GLB file: %s" % path)
    jlen = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    rest = data[20 + jlen:]
    nodes = js.get("nodes", [])
    changed = {}
    for skin in js.get("skins", []):
        for j in skin.get("joints", []):
            old = nodes[j].get("name", "")
            new = mapping_fn(old)
            if new != old:
                nodes[j]["name"] = new
                changed[old] = new
    if changed:
        raw = json.dumps(js, separators=(",", ":")).encode()
        raw += b" " * ((4 - len(raw) % 4) % 4)
        out = (data[:12] + struct.pack("<I", len(raw)) + b"JSON" + raw + rest)
        # fix total length in header
        out = out[:8] + struct.pack("<I", len(out)) + out[12:]
        with open(path, "wb") as f:
            f.write(out)
    return changed


def joint_names_of_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    jlen = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    nodes = js.get("nodes", [])
    skins = js.get("skins", [])
    if not skins:
        return []
    return [nodes[j].get("name", "") for j in skins[0].get("joints", [])]


# ---------------------------------------------------------------------------
# Blender part.

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=float, default=1.8)
    ap.add_argument("--donor", default=None,
                    help="animation source: a GLB with embedded clips, "
                         "or a BVH mocap file (CMU layout supported)")
    ap.add_argument("--clip", default="Idle",
                    help="GLB donor: clip name to transfer. BVH donor: "
                         "name for the baked action (default: donor stem)")
    ap.add_argument("--clip-start", type=int, default=0,
                    help="first source frame of the transfer window")
    ap.add_argument("--clip-frames", type=int, default=96,
                    help="output frames in the transfer window")
    ap.add_argument("--clip-step", type=int, default=1,
                    help="source frames per output frame")
    ap.add_argument("--gamerig-dir", default=DEFAULT_GAMERIG_DIR)
    ap.add_argument("--render-dir", default=None,
                    help="if set, render rest + mid-clip frames of the "
                         "EXPORTED glb into this dir")
    ap.add_argument("--metrics-out", default=None)
    ap.add_argument("--facing", choices=sorted(GLTF_FACING_TO_BLENDER), default=None,
                    help="the static mesh's glTF facing axis (read from a rest "
                         "render); overrides the foot-vs-shin estimate")
    ap.add_argument("--heat-proxy-verts", type=int, default=200000,
                    help="meshes above this vertex count are bone-heat "
                         "weighted through a voxel-remeshed, decimated proxy "
                         "and the weights data-transferred back")
    ap.add_argument("--heat-voxel", type=float, default=0.008,
                    help="proxy voxel remesh size in meters (after normalize)")
    ap.add_argument("--heat-proxy-faces", type=int, default=48000)
    ap.add_argument("--keep-face", action="store_true",
                    help="keep the metarig face subtree (default: strip; "
                         "WH skeletons have no face bones)")
    return ap.parse_args(argv)


def install_gamerig(gamerig_dir):
    """Copy the vendored GameRig into <user scripts>/rigify/gamerig."""
    import bpy
    dest = os.path.join(bpy.utils.script_path_user(), "rigify", "gamerig")
    marker = os.path.join(dest, "gamerig_generate.py")
    src_marker = os.path.join(gamerig_dir, "gamerig_generate.py")
    if not os.path.exists(src_marker):
        raise RuntimeError("GameRig not found at %s" % gamerig_dir)
    need = True
    if os.path.exists(marker):
        with open(marker, "rb") as f1, open(src_marker, "rb") as f2:
            need = f1.read() != f2.read()
    if need:
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(gamerig_dir, dest,
                        ignore=shutil.ignore_patterns("images", ".git*"))
    return dest


def enable_gamerig():
    """Enable Rigify, register the GameRig feature set, verify it stuck."""
    import bpy
    bpy.ops.preferences.addon_enable(module="rigify")
    prefs = bpy.context.preferences.addons["rigify"].preferences
    prefs.refresh_installed_feature_sets()
    if not hasattr(bpy.ops.pose, "gamerig_generate"):
        prefs.register_feature_sets(True)
    prefs.update_external_rigs()
    from rigify import rig_lists
    game_types = [k for k in rig_lists.rigs if k.startswith("game.")]
    if not game_types:
        raise RuntimeError("GameRig rig types failed to load")
    if not hasattr(bpy.ops.pose, "gamerig_generate"):
        raise RuntimeError("pose.gamerig_generate operator missing")
    return game_types


def apply_blender402_shim():
    """Substitute stock 4.0.2 create_root_bone (noparent_bones-safe)."""
    from rigify.feature_sets.gamerig import gamerig_generate
    from rigify.generate import Generator as stock_generator
    gamerig_generate.Generator_gamerig._Generator__create_root_bone = \
        stock_generator._Generator__create_root_bone


def mesh_world_stats(meshes):
    """Combined world-space vertex stats for the imported static."""
    import numpy as np
    from mathutils import Matrix  # noqa: F401  (keeps Blender context clear)
    xs, ys, zs = [], [], []
    for o in meshes:
        n = len(o.data.vertices)
        if not n:
            continue
        arr = np.empty(n * 3, dtype=np.float64)
        o.data.vertices.foreach_get("co", arr)
        arr = arr.reshape(-1, 3)
        m = np.array(o.matrix_world)
        w = arr @ m[:3, :3].T + m[:3, 3]
        xs.append(w[:, 0]); ys.append(w[:, 1]); zs.append(w[:, 2])
    import numpy as np
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(zs)


# glTF facing axis -> the facing vector in Blender space ((x,y,z)_gltf -> (x,-z,y))
GLTF_FACING_TO_BLENDER = {"+X": (1.0, 0.0), "-X": (-1.0, 0.0), "+Z": (0.0, -1.0), "-Z": (0.0, 1.0)}


def normalize_and_face(meshes, height, facing=None):
    """Uniform-scale to height, feet z=0, center x/y=0, yaw facing to -Y.

    Facing: `facing` (the mesh's glTF facing axis, read from rest renders)
    when given — exact. Otherwise estimated: the foot band's horizontal
    centroid sits forward of the shin band's centroid (toes). The estimate
    can land well off-axis (-74 deg instead of -90 on the demonio-a1 Tripo
    pull, 2026-10-20), which puts the metarig's arms outside the mesh's arms
    and makes bone heat fail for every vertex. Returns a metrics dict.
    """
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    x, y, z = mesh_world_stats(meshes)
    mn = Vector((x.min(), y.min(), z.min()))
    mx = Vector((x.max(), y.max(), z.max()))
    size = mx - mn
    if size.z <= 0:
        raise RuntimeError("degenerate mesh (zero height)")
    s = height / size.z
    # facing from foot (bottom 8%) vs shin (18-30%) horizontal centroids
    h = size.z
    foot = (z < mn.z + 0.08 * h)
    shin = (z > mn.z + 0.18 * h) & (z < mn.z + 0.30 * h)
    fvec = np.array([x[foot].mean() - x[shin].mean(),
                     y[foot].mean() - y[shin].mean()])
    yaw = 0.0
    if facing:
        fvec = np.array(GLTF_FACING_TO_BLENDER[facing])
    if np.linalg.norm(fvec) > 1e-6:
        # rotate facing vector onto (0,-1): yaw about Z
        ang_now = math.atan2(fvec[1], fvec[0])
        ang_tgt = math.atan2(-1.0, 0.0)
        yaw = ang_tgt - ang_now
    t = (Matrix.Rotation(yaw, 4, "Z") @ Matrix.Scale(s, 4) @
         Matrix.Translation(Vector((-(mn.x + mx.x) / 2.0,
                                     -(mn.y + mx.y) / 2.0, -mn.z))))
    for o in meshes:
        o.matrix_world = t @ o.matrix_world
    bpy.context.view_layer.update()
    x, y, z = mesh_world_stats(meshes)
    return {
        "scale_applied": s, "yaw_deg": math.degrees(yaw),
        "height_m": float(z.max() - z.min()),
        "span_m": float(max(x.max() - x.min(), y.max() - y.min())),
        "bbox_min": [float(v) for v in (x.min(), y.min(), z.min())],
        "bbox_max": [float(v) for v in (x.max(), y.max(), z.max())],
        "_verts": (x, y, z),
    }


def fit_metarig(meta, stats):
    """Fit the human metarig to the normalized mesh (edit-mode bone moves).

    Uniform object scale to the mesh height, then: arm chains stretched
    in X by the mesh/template arm-span ratio with the chain flattened
    onto the shoulder line (T-pose statics), legs stretched in X by the
    hip-band width ratio. Returns fit metrics.
    """
    import bpy
    from mathutils import Vector
    x, y, z = stats["_verts"]
    height = stats["height_m"]
    # template measurements before scaling
    bones = meta.data.bones
    tpl_height = max(b.tail_local.z for b in bones)
    tpl_span = 2.0 * max(abs(b.tail_local.x) for b in bones
                         if b.name.startswith(("hand", "f_", "thumb", "palm")))
    s = height / tpl_height
    meta.scale = (s, s, s)
    bpy.context.view_layer.objects.active = meta
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # mesh ratios
    mesh_span_ratio = stats["span_m"] / height
    tpl_span_ratio = tpl_span / tpl_height
    kx_arm = max(0.8, min(1.5, mesh_span_ratio / tpl_span_ratio))
    hip_band = (z > 0.46 * height) & (z < 0.58 * height)
    hip_half = float(max(abs(x[hip_band]).max(), 1e-4)) if hip_band.any() else 0.1 * height
    # template thigh head x (scaled) + rough leg radius allowance 0.055*H
    thigh_x = abs(bones["thigh.L"].head_local.x) * s
    kx_leg = max(0.8, min(1.4, (hip_half - 0.055 * height) / max(thigh_x, 1e-4)))
    kx_leg = max(0.8, min(1.4, kx_leg)) if thigh_x > 0 else 1.0

    # A-POSE (2026-10-20): measure each arm's droop from the mesh itself —
    # centroid of the outer-arm vertices (beyond the torso, outer quarter of
    # the reach) relative to the shoulder. T-pose ~0 deg; Tripo A-poses ~35-50.
    # Above 15 deg the chain is rotated down onto the measured arm line and
    # the X stretch uses the arm length (span / cos(droop)), not the span.
    # OUTER QUARTER, not half (2026-10-22, measured on torch-a1): the half
    # sample catches mass that hangs beside the torso but is not arm — on
    # torch-a1 the windswept hair mass (median height 57% of the body,
    # lateral band overlapping the inner arm sample) dragged the centroid
    # down and read a 46.6 deg droop on a statue whose own arm line reads
    # 7.4 deg from its outer quarter; the false A-pose rotation parked the
    # arm chains ~0.46 m below the real arms (fitted hand z 1.01 vs the
    # mesh's 1.47 shoulder line). The outer quarter of a straight arm chain
    # lies on the same line, so true A-pose readings are unchanged.
    import numpy as _np
    droop = {}
    for side, sgn in ((".L", 1.0), (".R", -1.0)):
        sh = bones["upper_arm" + side].head_local * s
        sx = sgn * x
        band = (sx > abs(sh.x) + 0.08 * height) & (z > 0.30 * height) & (z < 0.95 * height)
        if band.sum() < 50:
            droop[side] = 0.0
            continue
        reach = sx[band].max()
        outer = band & (sx > abs(sh.x) + 0.75 * (reach - abs(sh.x)))
        if outer.sum() < 20:
            droop[side] = 0.0
            continue
        cx, cz = float(sx[outer].mean()), float(z[outer].mean())
        droop[side] = max(0.0, math.degrees(math.atan2(sh.z - cz, cx - abs(sh.x))))
    a_pose = max(droop.values()) > 15.0
    if a_pose:
        cosd = max(0.35, math.cos(math.radians(sum(droop.values()) / 2.0)))
        kx_arm = max(0.8, min(1.6, (mesh_span_ratio / cosd) / tpl_span_ratio))

    bpy.ops.object.mode_set(mode="EDIT")
    eb = meta.data.edit_bones
    leg_prefixes = ("thigh.", "shin.", "foot.", "toe.", "heel.")
    # Arm fit (per side): stretch X by the span ratio, pull the chain
    # 85% of the way onto the shoulder line (T-pose statics), and keep
    # 15% of the template's natural droop — Rigify's limb pole-angle
    # computation divides by the elbow bend, so a perfectly straight
    # chain is a zero-length pole vector and generation fails.
    # The palm/finger subtree keeps its internal shape and is translated
    # rigidly by the hand head's displacement.
    # Every target is computed from a snapshot of the template, never from
    # bones already edited in this loop: forearm.tail and hand.head are one
    # connected joint, and reading hand.head after the forearm edit (the
    # pre-2026-10-21 code) captured an already-moved point, so the hand
    # displacement came out ~0 and the palm/finger subtree stayed at the
    # template droop, ~0.23 m below the hand (measured on zui-attire1).
    from mathutils import Vector as _V
    orig = {b.name: (b.head.copy(), b.tail.copy()) for b in eb}
    for side in (".L", ".R"):
        shoulder_z, shoulder_y = orig["upper_arm" + side][0].z, orig["upper_arm" + side][0].y

        def place(v, flatten):
            w = _V((v.x * kx_arm, v.y, v.z))
            if flatten:
                w.y = shoulder_y + (w.y - shoulder_y) * 0.15
                w.z = shoulder_z + (w.z - shoulder_z) * 0.15
            return w
        for name in ("shoulder", "upper_arm", "forearm", "hand"):
            b = eb[name + side]
            h, t = orig[name + side]
            b.head = place(h, name != "shoulder")
            b.tail = place(t, name != "shoulder")
        # palm/finger subtree: rigid move with the hand — rotated by the hand
        # bone's own rotation (template direction -> fitted direction) about
        # the hand head, so the fingers stay in line with the flattened hand.
        oh, ot = orig["hand" + side]
        nh, nt = eb["hand" + side].head.copy(), eb["hand" + side].tail.copy()
        rot = (ot - oh).rotation_difference(nt - nh).to_matrix()
        for b in eb:
            if b.name.endswith(side) and b.name.startswith(
                    ("palm.", "f_", "thumb.")):
                h, t = orig[b.name]
                b.head = nh + rot @ (h - oh)
                b.tail = nh + rot @ (t - oh)
        if a_pose and droop[side] > 15.0:
            # rotate the flattened chain (and its hand subtree) down about the
            # shoulder pivot, in the character's frontal (XZ) plane
            from mathutils import Matrix
            piv = eb["upper_arm" + side].head.copy()
            # right-hand rotation about +Y: x' = x cos + z sin, z' = -x sin + z cos,
            # so the +X (.L) arm goes down for a positive angle, the .R arm for negative
            ang = math.radians(droop[side]) * (1.0 if side == ".L" else -1.0)
            R = Matrix.Rotation(ang, 3, "Y")
            for b in eb:
                if b.name.endswith(side) and b.name.startswith(
                        ("upper_arm", "forearm", "hand", "palm.", "f_", "thumb.")):
                    b.head = piv + R @ (b.head - piv)
                    b.tail = piv + R @ (b.tail - piv)
    for b in eb:
        if b.name.startswith(leg_prefixes):
            b.head.x *= kx_leg
            b.tail.x *= kx_leg
    # LEG TAPER (2026-10-22, measured on torch-a1): the uniform kx_leg
    # spread is set by the hip band, but on statues whose legs taper hard
    # from hip to ankle (torch-a1 per-side lateral centroids at 1.8 m:
    # hip 0.283 m, knee 0.173 m, ankle 0.086 m) the straight leg columns
    # park the shin/foot bones ~6 cm outside the tapered lower legs.
    # Re-anchor the knee and ankle joints to the measured per-side
    # vertex centroids at those heights so the chain follows the actual
    # leg columns. On untapered bodies the centroids match the kx-scaled
    # positions and this is a no-op; anchors are clamped to [0.35x, 1.6x]
    # of the kx position and skipped when a band has too few vertices.
    leg_anchors = {}
    for side, sgn in ((".L", 1.0), (".R", -1.0)):
        sxa = sgn * x

        def _anchor(zlo, zhi, _sx=sxa):
            bandv = (z > zlo * height) & (z < zhi * height) & (_sx > 0.01 * height)
            if bandv.sum() < 50:
                return None
            return float(_sx[bandv].mean())

        def _clamped(val, ref):
            return max(0.35 * abs(ref), min(1.6 * abs(ref), abs(val)))

        entry = {}
        knee_x = _anchor(0.22, 0.32)
        if knee_x is not None:
            kv = _clamped(knee_x, eb["shin" + side].head.x) * sgn
            eb["thigh" + side].tail.x = kv
            eb["shin" + side].head.x = kv
            entry["knee_x"] = round(kv, 4)
        ankle_x = _anchor(0.02, 0.10)
        if ankle_x is not None:
            av = _clamped(ankle_x, eb["foot" + side].head.x) * sgn
            eb["shin" + side].tail.x = av
            eb["foot" + side].head.x = av
            eb["foot" + side].tail.x = av
            for bn in ("toe", "heel"):
                bb = eb.get(bn + side)
                if bb is not None:
                    bb.head.x = av
                    bb.tail.x = av
            entry["ankle_x"] = round(av, 4)
        leg_anchors[side] = entry
    bpy.ops.object.mode_set(mode="OBJECT")
    return {"metarig_scale": s, "kx_arm": kx_arm, "kx_leg": kx_leg,
            "template_height": tpl_height, "template_span": tpl_span,
            "arm_droop_deg": {k: round(v, 1) for k, v in droop.items()}, "a_pose": a_pose,
            "leg_anchors": leg_anchors}


def strip_face(meta):
    import bpy
    bpy.context.view_layer.objects.active = meta
    bpy.ops.object.mode_set(mode="EDIT")
    eb = meta.data.edit_bones
    removed = 0
    if "face" in eb:
        face = eb["face"]
        stack = [face]
        all_b = []
        while stack:
            b = stack.pop()
            all_b.append(b)
            stack.extend(list(b.children))
        for b in all_b:
            eb.remove(b)
        removed = len(all_b)
    bpy.ops.object.mode_set(mode="OBJECT")
    return removed


def strip_to_deform(rig):
    """Reduce the generated control rig to its game skeleton.

    GameRig guarantees the DEF bones form a single hierarchy whose
    parents are all DEF bones, so every non-DEF bone (controls, MCH,
    ORG, widgets' targets) can be deleted without orphaning a deform
    bone. Constraints/drivers that drove DEF bones from the control
    rig are cleared too: what remains is a plain FK deform skeleton,
    ready to be keyframed and exported as-is.
    Returns (kept, removed).
    """
    import bpy
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones
    removed = 0
    for b in list(eb):
        if not rig.data.bones[b.name].use_deform:
            eb.remove(b)
            removed += 1
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        for _ in range(len(pb.constraints)):
            pb.constraints.remove(pb.constraints[0])
    if rig.animation_data:
        rig.animation_data_clear()
    if rig.data.animation_data:
        rig.data.animation_data_clear()
    kept = len(rig.data.bones)
    return kept, removed


def drop_micro_components(obj, min_verts=32):
    """Remove connected components smaller than min_verts from a mesh.

    Voxel-remeshing wispy statues leaves single-voxel islands (8-9 verts:
    one voxel cube) floating off hair/fur tips. Measured on torch-a1
    (2026-10-22): the 48k-tri heat proxy had 39 components — a 23,885-vert
    body plus 38 islands of 8-9 verts — and Blender's bone heat failed for
    EVERY vertex ("failed to find solution for one or more bones", all
    24,068 proxy verts unweighted); the body alone solved with 0
    unweighted. A degenerate island poisons the global heat solve, so drop
    the islands from the PROXY only — the full-resolution mesh still
    receives weights in those spots via the Data Transfer and the
    nearest-bone fixup. Returns the number of vertices removed.
    """
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    seen = set()
    doomed = []
    for v in bm.verts:
        if v in seen:
            continue
        comp = []
        stack = [v]
        seen.add(v)
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o not in seen:
                    seen.add(o)
                    stack.append(o)
        if len(comp) < min_verts:
            doomed.extend(comp)
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="VERTS")
        bm.to_mesh(obj.data)
        obj.data.update()
    bm.free()
    return len(doomed)


def continuous_limit(mesh_obj, limit=4):
    """Limit every vertex to `limit` influences CONTINUOUSLY: subtract the (limit+1)-th largest weight from the top
    `limit`, renormalize. Blender's vertex_group_limit_total drops the 5th bone outright, so neighbours whose 4th/5th
    bones swap rank keep different bones and tear (measured on Negativo 2026-11-01: the whole strict-stretch plateau;
    attire 2 started smoothing at p99.9 9.39). Here a bone reaches 0 exactly where it leaves the top `limit`.
    Returns how many vertices had more than `limit` influences."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    dl = bm.verts.layers.deform.active
    n = 0
    if dl is not None:
        for v in bm.verts:
            d = v[dl]
            if len(d) <= limit:
                continue
            items = sorted(d.items(), key=lambda kv: -kv[1])
            t = items[limit][1]
            top = [(g, w - t) for g, w in items[:limit]]
            s = sum(w for _, w in top)
            if s <= 1e-9:
                top, s = items[:limit], sum(w for _, w in items[:limit]) or 1.0
            d.clear()
            for g, w in top:
                if w > 0:
                    d[g] = w / s
            n += 1
    bm.to_mesh(mesh_obj.data)
    bm.free()
    mesh_obj.data.update()
    return n


def heat_via_proxy(rig, m, voxel, target_faces):
    """Bone heat on a watertight decimated proxy, transferred to `m`.

    Blender's bone heat fails outright on ~1M-vertex Tripo statics ("failed
    to find solution for one or more bones": every vertex came back
    unweighted on demonio-a1, 2026-10-20). Standard production workaround,
    Blender built-ins only: Voxel Remesh a copy (watertight, solvable),
    Decimate it, heat-weight the copy, then Data Transfer the vertex-group
    weights onto the full-resolution mesh (nearest face, interpolated).
    Returns proxy stats."""
    import bpy
    def build_proxy(tri_target):
        bpy.ops.object.select_all(action="DESELECT")
        m.select_set(True)
        bpy.context.view_layer.objects.active = m
        bpy.ops.object.duplicate()
        proxy = bpy.context.object
        proxy.name = m.name + "_heatproxy"
        proxy.data.materials.clear()
        rem = proxy.modifiers.new("wh_remesh", "REMESH")
        rem.mode = "VOXEL"
        # voxel size is in object units; normalize leaves the object scale
        # unapplied, so convert the world-space size (measured: 0.008 local on
        # a 1.83-scaled Tripo gave 14.7 mm voxels)
        rem.voxel_size = voxel / max(proxy.scale)
        bpy.ops.object.modifier_apply(modifier=rem.name)
        quads = len(proxy.data.polygons)
        # Always decimate: Blender 4.0.2 bone heat failed for EVERY vertex on
        # raw voxel-remesh grids (28k and 43k faces) yet solved a decimated
        # proxy of the same mesh at 16k-48k faces with only stray islands
        # unweighted (measured on demonio-a1, 2026-10-20). Decimate counts
        # TRIANGLES (a remesh quad = 2): the old quad-based ratio left
        # zui-attire1's proxy at 96k triangles and heat failed for all 48k
        # verts; at 51k triangles it solved with 88 stray verts (2026-10-21).
        dec = proxy.modifiers.new("wh_decimate", "DECIMATE")
        dec.ratio = min(0.6, tri_target / max(1, 2 * quads))
        bpy.ops.object.modifier_apply(modifier=dec.name)
        # Merge duplicate verts first (Leopard King proxy, 2026-10-22: doubles plus 3-5 vertex specks
        # made the solve fail for every vertex, 24,006/24,006 unweighted -> 0), then drop the micro
        # components (torch-a1, same day — see drop_micro_components).
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(proxy.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.1 * voxel / max(proxy.scale))
        bm.to_mesh(proxy.data)
        bm.free()
        proxy.data.update()
        drop_micro_components(proxy)
        bpy.ops.object.select_all(action="DESELECT")
        rig.select_set(True)
        proxy.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        unw = sum(1 for v in proxy.data.vertices if not v.groups)
        return proxy, quads, unw

    # Retry with coarser proxies when the solve fails (a failed solve leaves
    # most verts unweighted; the nearest-bone fixup would then rigid-bind the
    # whole mesh — the torn "cronenberg" look). Accept < 5% stray verts.
    attempts = []
    proxy = None
    for tri_target in (target_faces, target_faces * 0.6, target_faces * 0.35):
        if proxy is not None:
            bpy.data.objects.remove(proxy, do_unlink=True)
        proxy, faces_remeshed, unweighted_proxy = build_proxy(tri_target)
        attempts.append({"tri_target": int(tri_target), "proxy_verts": len(proxy.data.vertices),
                         "unweighted": unweighted_proxy})
        if unweighted_proxy < 0.05 * len(proxy.data.vertices):
            break
    else:
        bpy.data.objects.remove(proxy, do_unlink=True)
        raise RuntimeError("bone heat failed on every proxy: %s" % attempts)
    proxy_faces = len(proxy.data.polygons)
    proxy_verts_n = list(range(len(proxy.data.vertices)))
    proxy_groups = len(proxy.vertex_groups)
    for g in proxy.vertex_groups:
        if m.vertex_groups.get(g.name) is None:
            m.vertex_groups.new(name=g.name)
    bpy.ops.object.select_all(action="DESELECT")
    m.select_set(True)
    bpy.context.view_layer.objects.active = m
    dt = m.modifiers.new("wh_weights", "DATA_TRANSFER")
    dt.object = proxy
    dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}
    dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"
    dt.layers_vgroup_select_dst = "NAME"
    while m.modifiers.find(dt.name) > 0:
        bpy.ops.object.modifier_move_up(modifier=dt.name)
    bpy.ops.object.modifier_apply(modifier=dt.name)
    bpy.data.objects.remove(proxy, do_unlink=True)
    # bind the full mesh to the rig with its transferred groups
    mw = m.matrix_world.copy()
    m.parent = rig
    m.matrix_world = mw
    am = m.modifiers.new("Armature", "ARMATURE")
    am.object = rig
    # keep at most 4 influences, normalized (what glTF/three.js skin with): CONTINUOUSLY first (the data transfer
    # leaves 5-8 influences in blend zones; a hard cut flips the 4th bone between neighbours and tears them),
    # so the hard cut below only guards
    limited = continuous_limit(m, 4)
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    return {"voxel_m": voxel, "continuous_limit_verts": limited, "faces_remeshed": faces_remeshed, "faces_proxy_after_decimate": proxy_faces,
            "proxy_verts": len(proxy_verts_n), "unweighted_proxy_verts": unweighted_proxy,
            "mesh_scale": list(m.scale), "mesh_dims": list(m.dimensions),
            "proxy_groups": proxy_groups, "attempts": attempts}


HEAT_PROXY = {"verts": 200000, "voxel": 0.008, "faces": 48000}
PROXY_STATS = []


def skin_meshes(rig, meshes):
    """Bone-heat skinning + nearest-bone fixup for unweighted verts.
    Dense meshes (> HEAT_PROXY['verts']) are weighted through a proxy."""
    import bpy
    dense = [m for m in meshes if len(m.data.vertices) > HEAT_PROXY["verts"]]
    light = [m for m in meshes if m not in dense]
    for m in dense:
        PROXY_STATS.append(heat_via_proxy(rig, m, HEAT_PROXY["voxel"], HEAT_PROXY["faces"]))
    if light:
        bpy.ops.object.select_all(action="DESELECT")
        rig.select_set(True)
        for m in light:
            m.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    # fixup (ported from blender_heat.py): unweighted verts crash the
    # glTF exporter and snap to origin at runtime; pin them to the
    # nearest deform bone head with weight 1.
    deform = [(b.name, rig.data.bones[b.name].head_local)
              for b in rig.data.bones if b.use_deform]
    fixed = 0
    for m in meshes:
        for v in m.data.vertices:
            if not v.groups:
                co = m.matrix_world @ v.co
                bn = min(deform, key=lambda b: (b[1] - co).length)[0]
                vg = m.vertex_groups.get(bn)
                if vg is None:
                    vg = m.vertex_groups.new(name=bn)
                vg.add([v.index], 1.0, "REPLACE")
                fixed += 1
    return fixed


# Per-donor source-name aliases for canonical bones (filled at runtime
# for CMU BVH donors: canonical -> source bone name).
SRC_ALIASES = {}

# donor canonical name -> GameRig DEF name (inverse of CANONICAL_MAP core)
DONOR_TO_DEF = {
    "Hips": "DEF-spine", "Spine": "DEF-spine.001",
    "Spine1": "DEF-spine.002", "Spine2": "DEF-spine.003",
    "Neck": "DEF-spine.004", "Head": "DEF-spine.005",
    "LeftShoulder": "DEF-shoulder.L", "RightShoulder": "DEF-shoulder.R",
    "LeftArm": "DEF-upper_arm.L", "RightArm": "DEF-upper_arm.R",
    "LeftForeArm": "DEF-forearm.L", "RightForeArm": "DEF-forearm.R",
    "LeftHand": "DEF-hand.L", "RightHand": "DEF-hand.R",
    "LeftUpLeg": "DEF-thigh.L", "RightUpLeg": "DEF-thigh.R",
    "LeftLeg": "DEF-shin.L", "RightLeg": "DEF-shin.R",
    "LeftFoot": "DEF-foot.L", "RightFoot": "DEF-foot.R",
    "LeftToeBase": "DEF-toe.L", "RightToeBase": "DEF-toe.R",
    "LeftHandThumb1": "DEF-thumb.01.L", "RightHandThumb1": "DEF-thumb.01.R",
    "LeftHandThumb2": "DEF-thumb.02.L", "RightHandThumb2": "DEF-thumb.02.R",
    "LeftHandThumb3": "DEF-thumb.03.L", "RightHandThumb3": "DEF-thumb.03.R",
    "LeftHandIndex1": "DEF-f_index.01.L",
    "RightHandIndex1": "DEF-f_index.01.R",
    "LeftHandIndex2": "DEF-f_index.02.L",
    "RightHandIndex2": "DEF-f_index.02.R",
    "LeftHandIndex3": "DEF-f_index.03.L",
    "RightHandIndex3": "DEF-f_index.03.R",
    "LeftHandMiddle1": "DEF-f_middle.01.L",
    "RightHandMiddle1": "DEF-f_middle.01.R",
    "LeftHandMiddle2": "DEF-f_middle.02.L",
    "RightHandMiddle2": "DEF-f_middle.02.R",
    "LeftHandMiddle3": "DEF-f_middle.03.L",
    "RightHandMiddle3": "DEF-f_middle.03.R",
    "LeftHandRing1": "DEF-f_ring.01.L",
    "RightHandRing1": "DEF-f_ring.01.R",
    "LeftHandRing2": "DEF-f_ring.02.L",
    "RightHandRing2": "DEF-f_ring.02.R",
    "LeftHandRing3": "DEF-f_ring.03.L",
    "RightHandRing3": "DEF-f_ring.03.R",
    "LeftHandPinky1": "DEF-f_pinky.01.L",
    "RightHandPinky1": "DEF-f_pinky.01.R",
    "LeftHandPinky2": "DEF-f_pinky.02.L",
    "RightHandPinky2": "DEF-f_pinky.02.R",
    "LeftHandPinky3": "DEF-f_pinky.03.L",
    "RightHandPinky3": "DEF-f_pinky.03.R",
}


def transfer_clip(rig, donor_path, clip_name, clip_start=0,
                  clip_frames=96, clip_step=1):
    """World-space rotation-delta FK retarget of a donor GLB clip.

    Why not the armature-space delta of retarget_blender.py? That form
    applies the source's rest-relative motion in the target bone's
    local frame, which is only valid when both skeletons share bone
    roll conventions. A glTF donor's bone frames (importer-built from
    node rotations) and Rigify's bone frames differ in roll, and the
    local form visibly corkscrews the limbs. The world-space form is
    frame-correct for arbitrary rest frames:

        R_world_delta(bone) = R_pose_s @ R_rest_s^-1      (world space)
        R_world_t(bone)     = R_world_delta @ R_rest_t
        pos_t(bone)         = FK down the target hierarchy from rest
                              offsets (root pinned: WH clips are
                              in-place, cf. retarget_blender.py)

    Unmapped DEF bones (pelvis, breast, palms, leaf segments) inherit
    their parent's world delta, so they follow rigidly.
    Returns (action_name, frames, mapped_bones).
    """
    import bpy
    from mathutils import Matrix
    # snapshot current objects so the donor import can be cleaned up
    before = set(bpy.context.scene.objects)
    is_bvh = donor_path.lower().endswith(".bvh")
    if is_bvh:
        bpy.ops.import_anim.bvh(filepath=donor_path)
    else:
        bpy.ops.import_scene.gltf(filepath=donor_path)
    new_objs = [o for o in bpy.context.scene.objects if o not in before]
    donors = [o for o in new_objs if o.type == "ARMATURE"]
    if not donors:
        raise RuntimeError("donor %s has no armature" % donor_path)
    src = max(donors, key=lambda a: len(a.data.bones))
    if is_bvh:
        # CMU layout: the WH spine chain sits one link lower
        # (Hips -> LowerBack -> Spine -> Spine1 -> Neck -> Head), and
        # thumbs are single bones named LThumb/RThumb.
        cmu = {"Spine": "LowerBack", "Spine1": "Spine",
               "Spine2": "Spine1",
               "LeftHandThumb1": "LThumb", "RightHandThumb1": "RThumb"}
        for canon, src_name in cmu.items():
            if src_name in src.data.bones:
                SRC_ALIASES[canon] = src_name
    # pick the clip: GLB import names actions "<Clip>_<Armature>";
    # a BVH import creates exactly one action on the source armature.
    if is_bvh:
        action = src.animation_data.action if src.animation_data else None
        out_name = clip_name
        if out_name == "Idle":
            out_name = os.path.splitext(os.path.basename(donor_path))[0]
    else:
        out_name = clip_name
        action = bpy.data.actions.get(clip_name)
        if action is None:
            for a in bpy.data.actions:
                if a.name == clip_name or a.name.startswith(clip_name + "_"):
                    action = a
                    break
        if action is None:
            cands = [a for a in bpy.data.actions if "TPose" not in a.name]
            action = cands[0] if cands else None
    if action is None:
        raise RuntimeError("donor has no usable action (wanted %s)" % clip_name)
    if src.animation_data is None:
        src.animation_data_create()
    # The donor's other clips live in NLA tracks; mute them all so the
    # evaluated pose is ONLY the chosen clip.
    for track in src.animation_data.nla_tracks:
        track.mute = True
    src.animation_data.action = action
    act_f0, act_f1 = (int(v) for v in action.frame_range)
    # transfer window (source frames -> output frames, renumbered from 0)
    win_start = act_f0 + clip_start
    win_end = min(act_f1, win_start + (clip_frames - 1) * clip_step)
    scene = bpy.context.scene

    def rest_world(arm, bone_name):
        return arm.matrix_world @ arm.data.bones[bone_name].matrix_local

    # donor rest world rotations (per canonical bone, via source names)
    def src_name(canon):
        return SRC_ALIASES.get(canon, canon)
    src_rest_rot = {}
    for canon in DONOR_TO_DEF:
        sn = src_name(canon)
        if sn in src.data.bones:
            src_rest_rot[canon] = rest_world(src, sn).to_quaternion()
    # target FK data, in ARMATURE space (the rig sits at the origin
    # with identity world matrix, so armature == world here): rest
    # matrix per DEF bone + rest offset of each bone's head in its
    # parent's rest frame. NOTE: bone.matrix_local IS the
    # armature-space rest matrix.
    tgt_rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    tgt_parent = {b.name: (b.parent.name if b.parent else None)
                  for b in rig.data.bones}
    tgt_offset = {}
    for name, rw in tgt_rest.items():
        p = tgt_parent[name]
        if p is None:
            tgt_offset[name] = rw.translation.copy()
        else:
            pr = tgt_rest[p]
            tgt_offset[name] = pr.to_quaternion().inverted() @ (
                rw.translation - pr.translation)
    # parent-first order
    order = []
    seen = set()
    def visit(n):
        if n in seen:
            return
        seen.add(n)
        if tgt_parent[n]:
            visit(tgt_parent[n])
        order.append(n)
    for n in tgt_rest:
        visit(n)
    def_for_canon = {c: d for c, d in DONOR_TO_DEF.items()
                      if src_name(c) in src.data.bones
                      and d in rig.data.bones}
    if not def_for_canon:
        raise RuntimeError("no mappable bones between donor and GameRig rig")
    canon_for_def = {d: c for c, d in def_for_canon.items()}

    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    out_action = bpy.data.actions.new(name=out_name)
    if rig.animation_data is None:
        rig.animation_data_create()
    rig.animation_data.action = out_action
    from mathutils import Quaternion, Vector
    src_frames = list(range(win_start, win_end + 1, clip_step))
    for out_frame, frame in enumerate(src_frames):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        # world delta rotation per mapped DEF bone
        delta = {}
        for defname, canon in canon_for_def.items():
            pw_rot = (src.matrix_world @
                      src.pose.bones[src_name(canon)].matrix).to_quaternion()
            delta[defname] = pw_rot @ src_rest_rot[canon].inverted()
        # FK down the target hierarchy (unmapped bones inherit the
        # parent's world delta and follow rigidly)
        world_rot, world_pos, eff_delta = {}, {}, {}
        for name in order:
            p = tgt_parent[name]
            if name in delta:
                d = delta[name]
            elif p is not None:
                d = eff_delta[p]
            else:
                d = Quaternion((1, 0, 0, 0))
            eff_delta[name] = d
            rest_rot = tgt_rest[name].to_quaternion()
            world_rot[name] = d @ rest_rot
            if p is None:
                world_pos[name] = tgt_offset[name].copy()
            else:
                world_pos[name] = world_pos[p] + (
                    world_rot[p] @ tgt_offset[name])
            m = Matrix.Translation(world_pos[name]) @ \
                world_rot[name].to_matrix().to_4x4()
            # Assign via matrix_basis computed from OUR matrices.
            # (PoseBone.matrix's setter reads the parent's evaluated
            # matrix, which lags one depsgraph tick behind the values
            # set in this loop — that lag visibly scrambled the first
            # frames of earlier bakes.)
            if p is None:
                local_m = m
                rest_local = tgt_rest[name]
            else:
                parent_m = Matrix.Translation(world_pos[p]) @ \
                    world_rot[p].to_matrix().to_4x4()
                local_m = parent_m.inverted() @ m
                rest_local = tgt_rest[p].inverted() @ tgt_rest[name]
            basis = rest_local.inverted() @ local_m
            bloc, bquat, bscl = basis.decompose()
            t_pb = rig.pose.bones[name]
            t_pb.location = bloc
            t_pb.rotation_quaternion = bquat
            t_pb.scale = bscl
            t_pb.keyframe_insert(data_path="location", frame=out_frame)
            t_pb.keyframe_insert(data_path="rotation_quaternion",
                                 frame=out_frame)
            t_pb.keyframe_insert(data_path="scale", frame=out_frame)
    bpy.ops.object.mode_set(mode="OBJECT")
    scene.frame_start, scene.frame_end = 0, len(src_frames) - 1
    if os.environ.get("GAMERIG_DEBUG_POSE"):
        for f in (0, 1, 2, len(src_frames) // 2):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            pts = {}
            for bn in ("DEF-spine", "DEF-spine.005", "DEF-foot.L",
                       "DEF-foot.R", "DEF-hand.L"):
                pb = rig.pose.bones[bn]
                pts[bn] = tuple(round(v, 2) for v in
                                (rig.matrix_world @ pb.matrix).translation)
            print("DEBUG_POSE frame", f, pts, flush=True)
    # remove donor objects AND its actions, so the exporter ships only
    # the baked clip (it otherwise exports every action in the file)
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for act in list(bpy.data.actions):
        if act != out_action:
            bpy.data.actions.remove(act)
    bpy.context.view_layer.update()
    return out_action.name, len(src_frames), len(def_for_canon)


def render_proof(glb_path, render_dir, clip_name):
    """Re-import the EXPORTED glb and render rest + mid-clip frames."""
    import bpy
    from mathutils import Vector
    os.makedirs(render_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb_path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    center = (mn + mx) / 2
    height = mx.z - mn.z
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    cam_data = bpy.data.cameras.new("cam")
    cam_data.clip_start = 0.01
    cam_data.clip_end = 100.0
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    # front three-quarter view (character faces -Y after this pipeline)
    cam.location = (center.x - height * 0.9, center.y - height * 1.6,
                    center.z + height * 0.15)
    d = Vector(center) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    frames = [("bind", int(scene.frame_start))]
    act = None
    if arms:
        for a in bpy.data.actions:
            act = a
            break
    if act is not None:
        f0, f1 = (int(v) for v in act.frame_range)
        frames = [("clip_first", f0), ("clip_mid", int((f0 + f1) / 2))]
    written = []
    for label, fr in frames:
        scene.frame_set(fr)
        bpy.context.view_layer.update()
        p = os.path.join(render_dir, "gamerig_%s_f%03d.png" % (label, fr))
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        written.append(p)
    return written


def main():
    import bpy
    a = parse_args()
    metrics = {"backend": "gamerig", "input": a.inp, "output": a.out}

    bpy.ops.wm.read_factory_settings(use_empty=True)
    install_dir = install_gamerig(a.gamerig_dir)
    metrics["gamerig_install"] = install_dir
    game_types = enable_gamerig()
    metrics["game_rig_types"] = len(game_types)
    apply_blender402_shim()
    metrics["shim"] = "Generator_gamerig.create_root_bone = stock 4.0.2"

    bpy.ops.import_scene.gltf(filepath=a.inp)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError(
            "no meshes imported from %s (EXT_meshopt_compression? decode "
            "first: npx @gltf-transform/cli copy in.glb out.glb)" % a.inp)
    metrics["input_meshes"] = len(meshes)
    metrics["input_verts"] = sum(len(o.data.vertices) for o in meshes)
    if any(o.type == "ARMATURE" for o in bpy.context.scene.objects):
        raise RuntimeError("input already has an armature; gamerig "
                           "backend is for unrigged statics")

    stats = normalize_and_face(meshes, a.height, a.facing)
    stats["facing_source"] = ("given: " + a.facing) if a.facing else "estimated (foot vs shin)"
    verts = stats.pop("_verts")
    stats["_verts"] = verts
    metrics["normalize"] = {k: v for k, v in stats.items() if k != "_verts"}

    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.object
    if not a.keep_face:
        metrics["face_bones_stripped"] = strip_face(meta)
    fit = fit_metarig(meta, stats)
    stats.pop("_verts", None)
    metrics["fit"] = fit
    metrics["metarig_bones"] = len(meta.data.bones)

    bpy.ops.object.select_all(action="DESELECT")
    meta.select_set(True)
    bpy.context.view_layer.objects.active = meta
    bpy.ops.pose.gamerig_generate()
    cands = [o for o in bpy.context.scene.objects
             if o.type == "ARMATURE" and o != meta]
    if not cands:
        raise RuntimeError("GameRig generation produced no rig")
    rig = max(cands, key=lambda o: len(o.data.bones))
    metrics["rig_bones_total"] = len(rig.data.bones)
    def_bones = [b.name for b in rig.data.bones if b.use_deform]
    metrics["def_bones"] = len(def_bones)
    # GameRig's promise, verified: every DEF bone's parent is DEF or None
    bad_parents = [b.name for b in rig.data.bones if b.use_deform
                   and b.parent is not None and not b.parent.use_deform]
    metrics["def_bones_with_nondef_parent"] = bad_parents
    if bad_parents:
        raise RuntimeError("DEF hierarchy not clean, refusing to strip: "
                           + ", ".join(bad_parents))
    kept, removed = strip_to_deform(rig)
    metrics["strip"] = {"kept_def_bones": kept, "removed_control_bones": removed}

    HEAT_PROXY.update(verts=a.heat_proxy_verts, voxel=a.heat_voxel,
                      faces=a.heat_proxy_faces)
    metrics["heat_proxy"] = dict(HEAT_PROXY)
    metrics["unweighted_fixed"] = skin_meshes(rig, meshes)
    metrics["heat_proxy_stats"] = PROXY_STATS

    clip_info = None
    if a.donor:
        name, nframes, npairs = transfer_clip(
            rig, a.donor, a.clip, clip_start=a.clip_start,
            clip_frames=a.clip_frames, clip_step=a.clip_step)
        clip_info = {"action": name, "frames": nframes, "bones": npairs,
                     "donor": a.donor}
        metrics["clip"] = clip_info

    # delete the metarig + widgets; keep rig + meshes only
    keep = set(meshes) | {rig}
    for o in list(bpy.context.scene.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(
        filepath=a.out, export_format="GLB", use_selection=True,
        export_skins=True, export_def_bones=True,
        export_animations=bool(clip_info), export_yup=True)
    changed = rename_glb_joints(a.out)
    metrics["renamed_joints"] = changed
    joints = joint_names_of_glb(a.out)
    metrics["joint_count"] = len(joints)
    metrics["joints"] = joints
    print("GAMERIG_METRICS", json.dumps(metrics))
    if a.metrics_out:
        with open(a.metrics_out, "w") as f:
            json.dump(metrics, f, indent=2)
    if a.render_dir:
        written = render_proof(a.out, a.render_dir, a.clip)
        print("GAMERIG_RENDERS", written)
    print("GAMERIG_OK", a.out)


if __name__ == "__main__":
    main()
