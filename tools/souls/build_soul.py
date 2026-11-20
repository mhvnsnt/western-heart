"""tools/souls/build_soul.py — build a Nine Souls fighter body from its Eastern Mind design, rigged for the game.

Why (owner 2026-11-10): "u have kai and tou looking like Paul Phoenix and Eddy, they are souls and if u research the
eastern mind games and canon and images you will see what they really look like". The souls' own designs are Osamu
Sato's Eastern Mind incarnation art, in the repo's teardown: teardown/eastern-mind/prologue-ending/bitmaps/CHARA/
(full bodies: CHARA_b006 = KAI, CHARA_b012 = TOU) and incarnation-system/bitmaps/R_KAI, R_TOH (head studies). Sato
built them from 3D primitives (ellipsoids, spheres, tubes, rings, cones) in 1994; this builds each soul the same way,
part by part, measured off its full-body art, in a T-pose on the game's skeleton (Mixamo joint names, Hips .. ToeBase).
Every part is bound RIGIDLY to one bone (the standard rig for segmented characters: puppets, mechs, toys), so no
part ever stretches; a part spanning a joint is split at the joint.

Run inside Blender 4.0.2 (always --factory-startup):
    blender -b --factory-startup --python tools/souls/build_soul.py -- --soul kai --out kai-soul.glb [--render ref.png]
Specs live in tools/souls/specs.py (one function per soul, all dimensions in metres, Blender Z-up, the soul facing -Y,
its left = +X; the glTF export turns that into the game's Y-up / +Z-facing convention).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import specs  # noqa: E402

JOINTS_REQUIRED = ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck', 'Head',
                   'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightShoulder', 'RightArm', 'RightForeArm',
                   'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase', 'RightUpLeg', 'RightLeg',
                   'RightFoot', 'RightToeBase']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = {'soul': None, 'out': None, 'render': None}
    i = 0
    while i < len(a):
        k = a[i].lstrip('-')
        out[k] = a[i + 1]
        i += 2
    return out


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


_MATS = {}


TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')


def material(name, rgb, rough=0.32, metal=0.0, emit=None, tex=None):
    """tex: a file in tools/souls/tex/ (tools/souls/textures.py: Sato's own pixels) for the base colour."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*rgb, 1.0)
    if tex:
        node = m.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = bpy.data.images.load(os.path.join(TEX_DIR, tex))
        m.node_tree.links.new(node.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1.0)
        b.inputs['Emission Strength'].default_value = 1.0
    _MATS[name] = m
    return m


def _finish(obj, mat, bone):
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    vg = obj.vertex_groups.new(name=bone)
    vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    return obj


def _apply():
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def ellipsoid(c, r, mat, bone, seg=32, rings=20, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1.0, location=c, rotation=rot)
    o = bpy.context.active_object
    o.scale = r
    _apply()
    return _finish(o, mat, bone)


def tube(p0, p1, r0, mat, bone, r1=None, seg=16):
    """Tapered cylinder from p0 to p1 (radius r0 at p0, r1 at p1)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    L = d.length
    r1 = r0 if r1 is None else r1
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r0, radius2=r1, depth=L, location=(0, 0, 0))
    o = bpy.context.active_object
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    o.matrix_world = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4()
    _apply()
    return _finish(o, mat, bone)


def cone(base, tip, r, mat, bone, seg=12):
    return tube(base, tip, r, mat, bone, r1=0.0005, seg=seg)


def torus(c, R, r, mat, bone, axis='Y', seg=48, mseg=16):
    rot = {'Y': (math.pi / 2, 0, 0), 'X': (0, math.pi / 2, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_torus_add(major_segments=seg, minor_segments=mseg, major_radius=R, minor_radius=r,
                                     location=c, rotation=rot)
    o = bpy.context.active_object
    _apply()
    return _finish(o, mat, bone)


def disc(c, r, thick, mat, bone, normal=(0, -1, 0), seg=32):
    n = Vector(normal).normalized()
    p0 = Vector(c) - n * thick / 2
    p1 = Vector(c) + n * thick / 2
    return tube(p0, p1, r, mat, bone, seg=seg)


def box(c, size, mat, bone, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=c, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    _apply()
    return _finish(o, mat, bone)


def build_armature(bones):
    """bones: list of (name, head, tail, parent)."""
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm = bpy.context.active_object
    arm.name = 'Armature'
    eb = arm.data.edit_bones
    for b in list(eb):
        eb.remove(b)
    made = {}
    for name, head, tail, parent in bones:
        e = eb.new(name)
        e.head, e.tail = Vector(head), Vector(tail)
        if parent:
            e.parent = made[parent]
            e.use_connect = False
        made[name] = e
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def main():
    a = args()
    spec = getattr(specs, a['soul'])()
    clear()
    arm = build_armature(spec['bones'])
    api = dict(material=material, ellipsoid=ellipsoid, tube=tube, cone=cone, torus=torus, disc=disc, box=box)
    parts = spec['parts'](api)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.active_object
    body.name = spec['name']
    body.data.name = spec['name']
    mod = body.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm
    body.parent = arm
    names = {b.name for b in arm.data.bones}
    missing = [j for j in JOINTS_REQUIRED if j not in names]
    if missing:
        raise SystemExit('missing joints: %s' % missing)
    zs = [(body.matrix_world @ v.co).z for v in body.data.vertices]
    print('SOUL_BUILT', spec['name'], 'verts', len(body.data.vertices), 'height %.3f' % (max(zs) - min(zs)),
          'min z %.3f' % min(zs), 'materials', len(body.data.materials))
    if a.get('render'):
        render(a['render'], spec)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    body.select_set(True)
    bpy.ops.export_scene.gltf(filepath=a['out'], export_format='GLB', use_selection=True, export_skins=True,
                              export_animations=False, export_yup=True, export_apply=False)
    print('SOUL_EXPORTED', a['out'])


def render(path, spec):
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_EEVEE'
    scn.render.resolution_x, scn.render.resolution_y = 700, 900
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.02, 0.025, 1)
    scn.world = world
    h = spec.get('height', 1.9)
    bpy.ops.object.camera_add(location=(0, -5.2, h * 0.52), rotation=(math.pi / 2, 0, 0))
    cam = bpy.context.active_object
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = h * 1.12
    scn.camera = cam
    for loc, en in (((2, -4, 4), 900), ((-3, -2, 2), 400), ((0, 3, 3), 300)):
        bpy.ops.object.light_add(type='AREA', location=loc)
        L = bpy.context.active_object
        L.data.energy = en
        L.data.size = 3
        L.rotation_euler = (Vector((0, 0, h / 2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
