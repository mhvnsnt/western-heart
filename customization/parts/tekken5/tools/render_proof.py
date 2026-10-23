"""Textured front render of a converted GLB (Cycles CPU, one pack per run so
renders stay one-at-a-time). Camera placed from the model bbox along -Y
(Blender front after the OBJ->GLB round-trip), plus a 3/4 view.
Usage: blender -b --python render_proof.py -- in.glb out_prefix"""
import bpy, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
src, prefix = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mn = Vector((1e18,) * 3); mx = Vector((-1e18,) * 3)
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
ctr = (mn + mx) / 2; size = mx - mn; H = max(size.y, size.z, 0.001)
print('BBOX', tuple(round(v, 3) for v in mn), tuple(round(v, 3) for v in mx), flush=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.device = 'CPU'
scene.render.resolution_x = 512; scene.render.resolution_y = 640
world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
bpy.context.scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = 1.1
sun_data = bpy.data.lights.new('sun', 'SUN'); sun_data.energy = 3.0
sun = bpy.data.objects.new('sun', sun_data); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
# strong frontal fill so the front proof reads the textures honestly
fill_data = bpy.data.lights.new('fill', 'AREA'); fill_data.energy = 60000.0; fill_data.shape = 'DISK'; fill_data.size = 4000.0
fill = bpy.data.objects.new('fill', fill_data); scene.collection.objects.link(fill)
cam_data = bpy.data.cameras.new('cam'); cam_data.type = 'ORTHO'; cam_data.clip_start = 1.0; cam_data.clip_end = 50000.0
cam = bpy.data.objects.new('cam', cam_data); scene.collection.objects.link(cam)
scene.camera = cam
cam_data.ortho_scale = H * 1.08
fill.location = ctr + Vector((0, -H * 2.0, H * 0.4))
fill.rotation_euler = (ctr - fill.location).to_track_quat('-Z', 'Y').to_euler()
for name, loc, look in [
    ('front', ctr + Vector((0, -H * 2.2, 0)), ctr),
    ('threequarter', ctr + Vector((H * 1.4, -H * 1.8, H * 0.35)), ctr),
]:
    cam.location = loc
    cam.rotation_euler = (look - loc).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = f'{prefix}-{name}.png'
    bpy.ops.render.render(write_still=True)
    print('RENDERED', scene.render.filepath, flush=True)
