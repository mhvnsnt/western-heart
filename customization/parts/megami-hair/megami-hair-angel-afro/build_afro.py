import bpy, math, random, os
from mathutils import Vector
random.seed(20261108)
SRC='/home/hatch/workspace/_parvati-redress-20261107/blend/Parvati-Commission.blend'
OUT='/home/hatch/workspace/_hair-wire-20261108/afro/megami-hair-angel-afro.glb'
PROOF='/home/hatch/workspace/_hair-wire-20261108/afro'
bpy.ops.wm.open_mainfile(filepath=SRC)
def unexclude(lc):
    lc.exclude=False
    for c in lc.children: unexclude(c)
for vl in bpy.context.scene.view_layers: unexclude(vl.layer_collection)
arm=bpy.data.objects['Parvati']; hair=bpy.data.objects['Hair']

# ---------- 1. scalp cap from Flora (real held geometry) ----------
cap_idx=[i for i,s in enumerate(hair.material_slots) if s.material and s.material.name.startswith('Cap')]
print('cap material slots:', cap_idx)
cap_faces=[p for p in hair.data.polygons if p.material_index in cap_idx]
print('cap faces:', len(cap_faces))
import bmesh
bm=bmesh.new(); bm.from_mesh(hair.data)
bm.faces.ensure_lookup_table()
keep=set(p.index for p in cap_faces)
for f in list(bm.faces):
    if f.index not in keep: bm.faces.remove(f)
# drop loose vertices left over from removed faces
loose=[v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS')
cap_mesh=bpy.data.meshes.new('AfroCapMesh'); bm.to_mesh(cap_mesh); bm.free()
print('cap verts:', len(cap_mesh.vertices))
cap_obj=bpy.data.objects.new('AfroCap', cap_mesh)
bpy.context.collection.objects.link(cap_obj)
cap_obj.matrix_world=hair.matrix_world.copy()

# ---------- 2. envelope dome: ellipsoid shell + unprojected cap inner layer ----------
CENTER=Vector((0.0, 0.0, 1.635)); RADII=Vector((0.180, 0.175, 0.230))
bpy.ops.mesh.primitive_uv_sphere_add(segments=56, ring_count=36, location=CENTER)
dome_obj=bpy.context.active_object; dome_obj.name='AfroDome'
dome_obj.scale=RADII
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
dome_mesh=dome_obj.data
cut=[]
for p in dome_mesh.polygons:
    c=p.center + CENTER  # object sits at CENTER, no rotation: local+loc = world
    d=(c-CENTER).normalized()
    if c.z < 1.415 or (d.y < -0.45 and c.z < 1.665): cut.append(p.index)
import bmesh as _bd
_b=_bd.new(); _b.from_mesh(dome_mesh); _b.faces.ensure_lookup_table()
_bd.ops.delete(_b, geom=[_b.faces[i] for i in cut], context='FACES')
_b.to_mesh(dome_mesh); _b.free()
print('ellipsoid dome faces cut:', len(cut), 'remaining:', len(dome_mesh.polygons))
DOME_V=len(dome_mesh.vertices)
mw=dome_obj.matrix_world

# ---------- 3. helix curl clump prototype ----------
def clump_mesh():
    pts=[]
    turns=4.5; n=22; R=0.0038; length=0.030
    for i in range(n+1):
        f=i/n; ang=f*turns*2*math.pi
        pts.append(Vector((R*math.cos(ang), R*math.sin(ang), f*length)))
    cu=bpy.data.curves.new('clump','CURVE'); cu.dimensions='3D'
    cu.bevel_depth=0.0021; cu.bevel_resolution=1; cu.resolution_u=1
    sp=cu.splines.new('POLY'); sp.points.add(n)
    for i,p in enumerate(pts):
        jx=(random.random()-0.5)*0.0016; jy=(random.random()-0.5)*0.0016
        sp.points[i].co=(p.x+jx,p.y+jy,p.z,1.0)
    ob=bpy.data.objects.new('clump_proto', cu); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    return ob
proto=clump_mesh()
PROTO_V=len(proto.data.vertices)
print('clump tris:', len(proto.data.polygons))

# ---------- 4. spring chain bones on the armature ----------
bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode='EDIT')
eb=arm.data.edit_bones
head_eb=eb.get('head')
anchors={}  # chain name -> (base Vector, tip Vector) in armature space
def add_chain(name, surf_pt):
    base=CENTER+ (surf_pt-CENTER)*0.35
    tip=surf_pt + (surf_pt-CENTER).normalized()*0.030
    b1=eb.new(name+'1'); b1.head=base; b1.tail=surf_pt; b1.parent=head_eb; b1.use_connect=False
    b2=eb.new(name+'2'); b2.head=surf_pt; b2.tail=tip; b2.parent=b1; b2.use_connect=False
    anchors[name]=(base, surf_pt, tip)
# surface anchor points (blend space, face = -Y assumed DAZ; symmetric anyway except front)
add_chain('hairFront', Vector((0.0,-0.185,1.66)))
add_chain('hairBack',  Vector((0.0, 0.190,1.64)))
add_chain('hairLeft',  Vector((-0.198,0.0,1.62)))
add_chain('hairRight', Vector((0.198, 0.0,1.62)))
add_chain('hairTop',   Vector((0.0, 0.0,1.815)))
add_chain('hairTopB',  Vector((0.0, 0.10,1.79)))
bpy.ops.object.mode_set(mode='OBJECT')
print('chains added:', list(anchors.keys()))

# ---------- 5. distribute clumps over the envelope (fibonacci, even coverage) ----------
N=1700
clump_objs=[]
GA=math.pi*(3.0-math.sqrt(5.0))
placed=0; idx=0
while placed < N:
    idx+=1
    y=1.0-(idx/(N*1.35))*2.0
    if y < -1.0: break
    rr=math.sqrt(max(0.0,1.0-y*y)); th=GA*idx
    d=Vector((math.cos(th)*rr, math.sin(th)*rr, y))  # unit dir (x, y=depth, z=up-ish via y here is z)
    # map: use d.z as up
    dirv=Vector((d.x, d.y, d.z))
    p=CENTER+Vector((dirv.x*RADII.x, dirv.y*RADII.y, dirv.z*RADII.z))
    # hairline mask: rim plane 1.44, front (blend -Y) raised to ~1.50
    frontness=max(0.0, -dirv.y)
    rim=1.44+0.055*frontness
    if p.z < rim: continue
    if dirv.y < -0.45 and p.z < 1.665: continue  # face opening (bone-space hairline)
    nrm=Vector((dirv.x/RADII.x, dirv.y/RADII.y, dirv.z/RADII.z)).normalized()
    ob=bpy.data.objects.new(f'clump{placed}', proto.data.copy())
    bpy.context.collection.objects.link(ob)
    p2=p - nrm*0.012
    tilt=math.radians(random.uniform(30,80)); az=random.uniform(0, 2*math.pi)
    zaxis=(nrm*math.cos(tilt) + Vector((math.cos(az), math.sin(az), 0))*math.sin(tilt)).normalized()
    xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
    xaxis=(xaxis - zaxis*xaxis.dot(zaxis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
    yaxis=zaxis.cross(xaxis)
    from mathutils import Matrix
    sc2=random.uniform(0.85,1.5)
    rot=Matrix((xaxis, yaxis, zaxis)).transposed()
    m=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
    ob.matrix_world=m
    clump_objs.append(ob); placed+=1
print('clumps placed:', placed)

# ---------- 6. join dome + clumps into one Afro mesh ----------
bpy.ops.object.select_all(action='DESELECT')
for ob in clump_objs+[dome_obj, cap_obj]: ob.select_set(True)
bpy.context.view_layer.objects.active=dome_obj
bpy.ops.object.join()
afro=dome_obj; afro.name='AngelAfro'
# remove prototype + cap helper objects (cap kept only as dome source; dome carries the shape)
bpy.data.objects.remove(proto, do_unlink=True)

# ---------- 7. material: opaque dark hair ----------
mat=bpy.data.materials.new('AngelAfroMat'); mat.use_nodes=True
bsdf=mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(0.012,0.009,0.007,1.0)
bsdf.inputs['Roughness'].default_value=0.8
try: bsdf.inputs['Sheen Weight'].default_value=0.35
except Exception: pass
afro.data.materials.clear(); afro.data.materials.append(mat)

# ---------- 8. weights: dome->head; clumps->nearest chain ----------
# (after join, vertex order: dome verts first, then clumps in placement order)
afro.vertex_groups.clear()
g_head=afro.vertex_groups.new(name='head')
chain_groups={}
for name in anchors: 
    chain_groups[name+'1']=afro.vertex_groups.new(name=name+'1')
    chain_groups[name+'2']=afro.vertex_groups.new(name=name+'2')
n_dome=DOME_V+len(cap_mesh.vertices)
proto_verts=len(bpy.data.meshes[-1].vertices) if False else None
# recompute: dome vert count = cap verts; clump verts appended in order — get per-clump counts from proto mesh before removal impossible; use stored: each clump shares proto vert count
# proto was removed; count via total: (total - n_dome) / N assumed uniform
total_v=len(afro.data.vertices); per=PROTO_V
print('verts: dome', n_dome, 'per clump', per, 'total', total_v)
for vi in range(n_dome): g_head.add([vi],1.0,'REPLACE')
anchor_list=[(name, anchors[name][1]) for name in anchors]
for ci in range(N):
    start=n_dome+ci*per
    c=afro.data.vertices[start].co
    # clump center approx from first vert + offset — use matrix-less: average of first 8 verts
    cc=Vector((0,0,0))
    for k in range(min(per,8)): cc+=afro.data.vertices[start+k].co
    cc/=min(per,8)
    wpt=afro.matrix_world @ cc
    name, surf = min(anchor_list, key=lambda kv: (kv[1]-wpt).length)
    gname=name+('2' if (wpt-CENTER).length>0.155 else '1')
    for vi in range(start, start+per): chain_groups[gname].add([vi],1.0,'REPLACE')
# armature modifier + parent (Flora pattern: parent to armature object, modifier binds)
mod=afro.modifiers.new('Armature','ARMATURE'); mod.object=arm
afro.parent=arm
print('Afro verts:', total_v, 'polys:', len(afro.data.polygons))
bpy.context.view_layer.objects.active=afro
bpy.ops.wm.save_as_mainfile(filepath='/home/hatch/workspace/_hair-wire-20261108/afro/afro-build10.blend')
print('BUILD DONE + SAVED')
