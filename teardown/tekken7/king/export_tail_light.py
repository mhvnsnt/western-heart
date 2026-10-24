import bpy, os
KDIR = os.getcwd()
PDIR = os.path.join(KDIR, "pantera")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(KDIR, '5PMH7G85GYN7P71W3BD1V0249.fbx'))
for o in bpy.context.scene.objects:
    o.scale = tuple(s*100 for s in o.scale)
bpy.context.view_layer.update()
# Decimate all meshes to 10%
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
    mod = o.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = 0.1
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="Decimate")
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
minx=miny=minz=1e9; maxx=maxy=maxz=-1e9
for o in meshes:
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        minx,maxx=min(minx,w.x),max(maxx,w.x)
        miny,maxy=min(miny,w.y),max(maxy,w.y)
        minz,maxz=min(minz,w.z),max(maxz,w.z)
cx,cy,cz=(minx+maxx)/2,(miny+maxy)/2,(minz+maxz)/2
height=maxz-minz; widthx=maxx-minx; widthy=maxy-miny
print(f"BOUNDS: x[{minx:.1f},{maxx:.1f}] y[{miny:.1f},{maxy:.1f}] z[{minz:.1f},{maxz:.1f}]")
print(f"CENTER:{cx:.1f},{cy:.1f},{cz:.1f} HEIGHT:{height:.1f}")
tail_base_x = maxx - widthx*0.06
tail_base_y = cy + widthy*0.10
tail_base_z = minz + height*0.52
L = height*0.28
print(f"TAIL_BASE:{tail_base_x:.1f},{tail_base_y:.1f},{tail_base_z:.1f} LEN:{L:.1f}")
bpy.ops.curve.primitive_bezier_curve_add(location=(tail_base_x, tail_base_y, tail_base_z))
curve_obj = bpy.context.active_object
curve_obj.name = "PanteraTail"
spline = curve_obj.data.splines[0]
pts = [(0,0,0), (L*0.25,L*0.05,-L*0.30), (L*0.35,L*0.35,-L*0.55), (L*0.25,L*0.70,-L*0.60)]
while len(spline.bezier_points) < 4:
    spline.bezier_points.add(1)
for i, (px,py,pz) in enumerate(pts):
    bp = spline.bezier_points[i]
    bp.co = (px,py,pz)
    bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
curve_obj.data.bevel_depth = height*0.018
curve_obj.data.bevel_resolution = 3
curve_obj.data.fill_mode = 'FULL'
mat = bpy.data.materials.new("TailBlack")
mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.02,0.02,0.02,1.0)
curve_obj.data.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT')
curve_obj.select_set(True)
bpy.context.view_layer.objects.active = curve_obj
bpy.ops.object.convert(target='MESH')
bpy.context.active_object.name = "PanteraTail"
# Simple gray material for body
for o in [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name != "PanteraTail"]:
    if not o.data.materials:
        m = bpy.data.materials.new("Gray")
        m.use_nodes=True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.6,0.6,0.6,1.0)
        o.data.materials.append(m)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(PDIR, "pantera_light.glb"), export_format='GLB', use_selection=True, export_materials='EXPORT')
print("EXPORTED_LIGHT")
