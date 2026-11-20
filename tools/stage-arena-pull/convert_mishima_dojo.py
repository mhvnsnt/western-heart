# Converts teardown/tekken7/arenas/mishima-dojo_2024-map.rar (-> Mishima_Dojo_Final_2_17_24.blend)
# into an optimized phone GLB. Extract the .rar with 7-Zip 24.09 (7zz), then:
#   blender -b Mishima_Dojo_Final_2_17_24.blend -P convert_mishima_dojo.py
# Drops break-state duplicates (fragment/_sepA/center hashira), candle FX, moon; decimates;
# exports without normals/UVs/skins (the .rar shipped no textures; normals rebuilt in-game).
import bpy
for o in list(bpy.data.objects):
  if o.type!='MESH' or o.name.startswith(('moon','T7_SM_ENV_s0bonfire_base No Fire')) or 'Candle_fire' in o.name or 'fragment' in o.name or '_sepA' in o.name:
    if o.type=='MESH': bpy.data.objects.remove(o)
import mathutils
for o in list(bpy.data.objects):
  if o.type!='MESH': continue
  cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
  mn=[min(c[i] for c in cs) for i in range(3)];mx=[max(c[i] for c in cs) for i in range(3)]
  if mn[0]<1 and mx[0]>-1 and mn[1]<1 and mx[1]>-1 and mx[2]>0.6 and mn[2]<6 and o.dimensions.x<20 and o.dimensions.y<20:
    print('DROP',o.name); bpy.data.objects.remove(o)
tot=sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH')
r=0.06;print('TOT',tot,'ratio',r)
for o in bpy.data.objects:
  if o.type=='MESH' and len(o.data.polygons)>3000:
    pass
  if o.type=='MESH' and 400<len(o.data.polygons)<=3000:
    m=o.modifiers.new('d2','DECIMATE');m.ratio=0.35
  if o.type=='MESH' and len(o.data.polygons)>3000:
    m=o.modifiers.new('d','DECIMATE');m.ratio=(0.2 if 'floor' in o.name else 0.25 if 'staue' in o.name else r)
bpy.ops.export_scene.gltf(filepath='/workspace/md/mishima-dojo.glb',export_format='GLB',export_apply=True,export_draco_mesh_compression_enable=False,export_draco_mesh_compression_level=7,export_image_format='NONE',export_yup=True,export_texcoords=False,export_normals=False,export_skins=False,export_vertex_color='NONE',export_all_vertex_colors=False,export_materials='EXPORT')
