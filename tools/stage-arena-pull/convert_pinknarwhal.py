#!/usr/bin/env python3
"""convert_pinknarwhal.py — Pink Narwhal (SmutBase strip-club map) -> game-ready GLB.

Stage 3 (detail pass) of the arena upgrade pipeline for HELIX PALACE
("Land of Desire"): the Virt-A-Mate club interior becomes the teardown-sourced
geometry behind the canon five desire rooms.

Pipeline:
  1. Arena transform M = S @ T @ R: rotate +90 deg about Z so the big pole stage
     sits on the FAR (north/background) side, translate the main fabric floor
     to the origin, scale 1.2x so the venue floor covers the 16.8 fight lane.
     Fighting surface ends at y=0.
  2. Dollhouse the venue: remove the camera-side wall, walls that would cross
     the fight lane after rotation, and the roof (fighting-game arenas are open).
  3. Clearance rules (evaluated in FINAL arena space, parents intact):
     - fight-rect: anything taller than 0.35 m whose footprint intersects
       |x| < 8.4, |z| < 2.5 is excluded — fighters need a clear floor;
     - camera: anything taller than 1.0 m in |x| < 6, 2.5 < z < 9.5 would sit
       between the fight camera and the fighters — excluded.
     Structural floors/walls and the showpiece stage always stay. (Same class
     of curation as the No Mercy lane omitting placement-less ROM template
     pieces — not hand-modeling.)
  4. Drop non-venue data (armatures, fonts, cameras, empties, lights — the game
     runs its own lighting rig) and downscale textures >1024px.
  5. Bake M into deduplicated mesh data (flat, parent-free), export GLB.

Usage:
  blender -b <ThePinkNarwhal_std.blend> --python convert_pinknarwhal.py -- <out.glb>
"""
import bpy
import math
import sys
from mathutils import Matrix, Vector

# ---------------------------------------------------------------- config
FIGHT_HALF_X = 8.4          # Tekken-standard clamp; keep clear
FIGHT_HALF_Z = 2.5          # lane depth to keep clear
CLEAR_HEIGHT = 0.35         # objects shorter than this never block fighters
CAM_CLEAR_X = 6.0           # camera corridor half-width
CAM_ZMIN, CAM_ZMAX = 2.5, 9.5   # between lane and camera
CAM_CLEAR_HEIGHT = 1.0
TEX_MAX = 1024
ARENA_SCALE = 1.2

# Prefix removals (the .blend carries .001/.002/... duplicates of each piece).
REMOVE_PREFIXES = (
    "Struct.WallW.001",      # camera-side wall after rotation
    "Struct.WallS.",          # side walls that would cross the fight lane
    "Struct.WallN.001",       # runs longitudinally through the lane after rotation
    "Struct.Roof.",           # roof (open dollhouse top)
    "Plane.004",              # mirror divider across the fight line
    "cupB_low15__BarUnique00",  # bar counter: lands between camera and fighters
    "SmallPole1", "SmallPole2", "SmallPoleBase1", "SmallPoleBase2",
)
REMOVE_COLLECTIONS = {"Club Cans and Sodas"}
KEEP_PREFIXES = ("Struct.", "polySurface9753__FloorFabric2",
                 "PoleDanceBigStage", "PoleBigStage")
FLOOR_SINK = {"Struct.Floor.001": -0.02}  # outer shell floor sits just under fabric


def final_bbox(o, M):
    MW = M @ o.matrix_world
    ws = [MW @ Vector(c) for c in o.bound_box]
    mn = [min(v[i] for v in ws) for i in range(3)]
    mx = [max(v[i] for v in ws) for i in range(3)]
    return mn, mx


def main():
    argv = sys.argv
    out = argv[argv.index("--") + 1] if "--" in argv else "/tmp/pink-narwhal.glb"
    bpy.context.view_layer.update()

    # -- arena transform ------------------------------------------------------
    R = Matrix.Rotation(math.radians(90), 4, "Z")
    floor = bpy.data.objects.get("polySurface9753__FloorFabric2.002")
    ws = [floor.matrix_world @ Vector(c) for c in floor.bound_box]
    fc = sum(ws, Vector()) / 8
    rfc = R @ fc
    S = Matrix.Scale(ARENA_SCALE, 4)
    M = S @ Matrix.Translation((-rfc.x, -rfc.y, 0.0)) @ R
    print(f"arena transform: floor center {tuple(round(v, 2) for v in fc)} -> origin, scale {ARENA_SCALE}")

    # -- evaluate removals FIRST (parents intact -> correct world bboxes) ------
    clutter = set()
    for cname in REMOVE_COLLECTIONS:
        c = bpy.data.collections.get(cname)
        if c:
            clutter.update(c.all_objects)

    to_remove = []
    for o in list(bpy.data.objects):
        if o.type in {"ARMATURE", "FONT", "CAMERA", "EMPTY", "LIGHT"}:
            to_remove.append((o, "non-venue"))
            continue
        if o.type != "MESH":
            continue
        if any(o.name.startswith(p) for p in REMOVE_PREFIXES):
            to_remove.append((o, "dollhouse/curation"))
            continue
        if o in clutter:
            to_remove.append((o, "clutter"))
            continue
        mn, mx = final_bbox(o, M)
        tall = (mx[2] - mn[2]) > CLEAR_HEIGHT and mx[2] > CLEAR_HEIGHT
        # glTF/three.js Y-up: three_x = x, three_z = -y.
        # lane |z|<2.5 is symmetric in y; the camera corridor z in (2.5,9.5)
        # maps to y in (-9.5,-2.5).
        in_lane = (mn[0] < FIGHT_HALF_X and mx[0] > -FIGHT_HALF_X
                   and mn[1] < FIGHT_HALF_Z and mx[1] > -FIGHT_HALF_Z)
        cam_block = (mx[2] > CAM_CLEAR_HEIGHT
                     and mn[0] < CAM_CLEAR_X and mx[0] > -CAM_CLEAR_X
                     and mn[1] < -CAM_ZMIN and mx[1] > -CAM_ZMAX)
        structural = o.name.startswith(KEEP_PREFIXES)
        if (tall and in_lane or cam_block) and not structural:
            to_remove.append((o, "clearance rule"))

    # -- bake M into deduplicated mesh data BEFORE unparenting -------------------
    # (world matrices are only valid while parents still exist)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in meshes:
        if o.data.users > 1:
            o.data = o.data.copy()
    bpy.context.view_layer.update()
    baked = {}
    for o in meshes:
        MW = M @ o.matrix_world
        if o.name in FLOOR_SINK:
            MW = Matrix.Translation((0, 0, FLOOR_SINK[o.name])) @ MW
        o.data.transform(MW)
        baked[o.name] = True
    # -- now delete the marked objects -----------------------------------------
    for o, why in to_remove:
        print(f"  - {o.name} ({why})")
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"removed {len(to_remove)} objects")
    # -- flatten surviving meshes ------------------------------------------------
    # (recompute: the pre-delete `meshes` list holds stale refs)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in meshes:
        o.parent = None
        o.matrix_parent_inverse.identity()
        o.location = (0.0, 0.0, 0.0)
        o.rotation_euler = (0.0, 0.0, 0.0)
        o.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()

    # -- downscale oversize textures -------------------------------------------
    for img in bpy.data.images:
        if img.packed_file and max(img.size) > TEX_MAX:
            w, h = img.size
            s = TEX_MAX / max(w, h)
            img.scale(int(w * s), int(h * s))

    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format="GLB",
        use_selection=False,  # scene now contains venue meshes only
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
    )
    import os
    print(f"wrote {out} ({os.path.getsize(out)/1e6:.1f} MB, {len(meshes)} meshes)")


main()
