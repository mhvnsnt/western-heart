import bpy, bmesh, math
import numpy as np
bpy.ops.wm.open_mainfile(filepath='/home/hatch/workspace/_parvati-redress-20261107/blend/Parvati-Commission.blend')
src=bpy.data.objects['Hair']
hair=src.copy(); hair.data=src.data.copy(); hair.name='AngelStraight'
bpy.context.collection.objects.link(hair)
mesh=hair.data
matnames=[m.name if m else '' for m in mesh.materials]
bm=bmesh.new(); bm.from_mesh(mesh); bm.faces.ensure_lookup_table()
bangs={i for i,n in enumerate(matnames) if n.startswith('Bangs')}
kill=[f for f in bm.faces if f.material_index in bangs]
bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(mesh); bm.free()
bm=bmesh.new(); bm.from_mesh(mesh)
loose=[v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS'); bm.to_mesh(mesh); bm.free()
print('verts:', len(mesh.vertices))
# wave relax harder + gentle vertical stretch below the crown
bpy.context.view_layer.objects.active=hair; hair.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bm=bmesh.from_edit_mesh(mesh)
for v in bm.verts: v.select = v.co.z < 1.62
bmesh.update_edit_mesh(mesh)
bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=3)
bpy.ops.object.mode_set(mode='OBJECT'); hair.select_set(False)
for v in mesh.vertices:
    if v.co.z < 1.60: v.co.z = 1.60 + (v.co.z-1.60)*1.05
# --- tinted-texture materials (canonical Blender->glTF baseColorFactor path) ---
hair_img=bpy.data.images['20WFFloraHair']
if max(hair_img.size)>1024: hair_img.scale(1024,1024)
cap_img=bpy.data.images.get('WFFloraCapT')
if cap_img and max(cap_img.size)>1024: cap_img.scale(1024,1024)
cap_n=bpy.data.images.get('WFFloraCapN')
def clean_mat(name, img, tint, rough=0.5, normal=None):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value=rough
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=img
    mix=nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'
    mix.inputs[0].default_value=1.0; mix.inputs[2].default_value=(*tint,1.0)
    nt.links.new(tex.outputs['Color'], mix.inputs[1]); nt.links.new(mix.outputs[0], bsdf.inputs['Base Color'])
    if normal:
        t2=nt.nodes.new('ShaderNodeTexImage'); t2.image=normal; t2.image.colorspace_settings.name='Non-Color'
        nm=nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(t2.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return m
m_black=clean_mat('AngelBlack', hair_img, (0.055,0.045,0.040))
m_blond=clean_mat('AngelBlonde', hair_img, (0.90,0.62,0.27))
m_cap=clean_mat('AngelCap', cap_img or hair_img, (0.06,0.05,0.045), 0.6, cap_n)
cap_idx={i for i,n in enumerate(matnames) if n.startswith('Cap')}
front_idx={i for i,n in enumerate(matnames) if n.startswith('Front') or n.startswith('SideBangs')}
bm=bmesh.new(); bm.from_mesh(mesh); bm.faces.ensure_lookup_table()
targets=[]; n_blond=0
for f in bm.faces:
    old=f.material_index
    if old in cap_idx: targets.append(0)
    elif old in front_idx:
        c=f.calc_center_median()
        if -0.115 < c.x < -0.015 and c.y < -0.055 and c.z > 1.30:
            targets.append(2); n_blond+=1
        else: targets.append(1)
    else: targets.append(1)
bm.to_mesh(mesh); bm.free()
mesh.materials.clear()
mesh.materials.append(m_cap); mesh.materials.append(m_black); mesh.materials.append(m_blond)
for i,t in enumerate(targets): mesh.polygons[i].material_index=t
print('blonde faces:', n_blond)
# headband: import v1, +0.33 Z, skin to head via armature modifier + parent
bpy.ops.import_scene.gltf(filepath='/home/hatch/workspace/_hair-wire-20261108/straight/v1-straight.glb')
band=None
for ob in list(bpy.context.scene.objects):
    if ob.name=='AngelHeadband': band=ob
    elif ob.name in ('AngelHairScalpCap','AngelHairStraight','Icosphere.001') or 'StraightMesh' in ob.name:
        bpy.data.objects.remove(ob, do_unlink=True)
band.name='AngelHeadband'
for v in band.data.vertices: v.co.z += 0.33
vg=band.vertex_groups.new(name='head'); vg.add(list(range(len(band.data.vertices))),1.0,'REPLACE')
arm=bpy.data.objects['Parvati']
am=band.modifiers.new('Armature','ARMATURE'); am.object=arm
band.parent=arm
mb=bpy.data.materials.new('AngelHeadbandMat'); mb.use_nodes=True
mb.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.02,0.02,0.022,1.0)
mb.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.35
band.data.materials.clear(); band.data.materials.append(mb)
print('band skinned + rematerialed')
bpy.ops.wm.save_as_mainfile(filepath='/home/hatch/workspace/_hair-fix-20261108/work/straight-build3.blend')
print('STRAIGHT BUILD2 DONE')
