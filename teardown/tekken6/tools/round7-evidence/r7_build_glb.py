"""Round 7: build the complete NDPP bounding-volume GLB from the clean
re-extraction (r7_boxes.json). Same construction as the round-2 builder
(models/tools/build_glb.py): one object per section, boxes as 12-tri
cuboids, sections arranged on a grid, single orange material. These are
bounding volumes (collision/culling), NOT character meshes - labeled as
such in the file and docs. Run under Blender:
xvfb-run -a env -u PYTHONPATH <blender> -b -P r7_build_glb.py"""
import bpy, json, os, math, mathutils
BOXES_JSON='/home/hatch/workspace/_t6r4-work/r7scratch/r7_boxes.json'
GLB_PATH='/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/models/ndpp_bounding_volumes_r7.glb'
REND_DIR='/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools/round7-evidence/renders'
sections=json.load(open(BOXES_JSON))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
def box_tris(verts):
    mins=[min(v[i] for v in verts) for i in range(3)]
    maxs=[max(v[i] for v in verts) for i in range(3)]
    c2v={}
    for vi,v in enumerate(verts):
        ci=0
        for ax in range(3):
            if abs(v[ax]-maxs[ax])<abs(v[ax]-mins[ax]): ci|=(1<<ax)
        if ci not in c2v: c2v[ci]=vi
    quads=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    tris=[]
    for q in quads:
        try: a,b,c,d=(c2v[x] for x in q)
        except KeyError: continue
        tris.append((a,b,c)); tris.append((a,c,d))
    return tris
COLS=35; CELL=4.0
objs=[]
for idx,s in enumerate(sections):
    gx=(idx%COLS)*CELL; gz=(idx//COLS)*CELL
    verts=[]; faces=[]; voff=0
    for b in s['boxes']:
        bv=b['verts']
        verts.extend([(v[0]+gx, v[1], v[2]+gz) for v in bv])
        for t in box_tris(bv): faces.append((t[0]+voff,t[1]+voff,t[2]+voff))
        voff+=8
    if not faces: continue
    mesh=bpy.data.meshes.new(f'section_{idx:04d}')
    mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(f'section_{idx:04d}',mesh)
    bpy.context.collection.objects.link(obj); objs.append(obj)
print('objects:',len(objs))
bpy.ops.export_scene.gltf(filepath=GLB_PATH, export_format='GLB', export_apply=True)
print('exported',GLB_PATH,os.path.getsize(GLB_PATH))
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1920; scene.render.resolution_y=1080
scene.world.use_nodes=True
cam_data=bpy.data.cameras.new('cam'); cam=bpy.data.objects.new('cam',cam_data)
bpy.context.collection.objects.link(cam); scene.camera=cam
center=mathutils.Vector((COLS*CELL/2,0,COLS*CELL/2))
cam.location=center+mathutils.Vector((90,90,90))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
ld=bpy.data.lights.new('sun','SUN'); ld.energy=3.0
li=bpy.data.objects.new('sun',ld); bpy.context.collection.objects.link(li)
li.rotation_euler=(math.radians(45),0,math.radians(30))
mat=bpy.data.materials.new('boxmat'); mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(1.0,0.45,0.1,1.0)
for o in objs: o.data.materials.append(mat)
scene.render.filepath=os.path.join(REND_DIR,'r7ndpp_grid.png')
bpy.ops.render.render(write_still=True)
print('rendered grid')
cam.location=mathutils.Vector((10,10,10))
cam.rotation_euler=(mathutils.Vector((4,0,4))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=os.path.join(REND_DIR,'r7ndpp_closeup.png')
bpy.ops.render.render(write_still=True)
print('rendered closeup')
