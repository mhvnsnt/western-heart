import bpy, math, random
from mathutils import Vector, Matrix
random.seed(20261108)
SRC='/home/hatch/workspace/_parvati-redress-20261107/blend/Parvati-Commission.blend'
SAVE='/home/hatch/workspace/_hair-fix-20261108/work/afro-fix-build12.blend'
bpy.ops.wm.open_mainfile(filepath=SRC)
def unexclude(lc):
    lc.exclude=False
    for c in lc.children: unexclude(c)
for vl in bpy.context.scene.view_layers: unexclude(vl.layer_collection)
arm=bpy.data.objects['Parvati']; hair=bpy.data.objects['Hair']

# ---------- hairline profile measured from Flora cap lower edge (probe 2026-11-08) ----------
HL_PTS=[(0,1.715),(15,1.715),(30,1.714),(45,1.699),(60,1.638),(75,1.645),(90,1.638),(105,1.626),(120,1.618),(135,1.610),(150,1.605),(165,1.602),(180,1.598)]
def hairline(az_deg):
    a=abs(az_deg)
    for i in range(len(HL_PTS)-1):
        a0,z0=HL_PTS[i]; a1,z1=HL_PTS[i+1]
        if a0 <= a <= a1:
            f=(a-a0)/(a1-a0) if a1>a0 else 0.0
            return z0+(z1-z0)*f
    return HL_PTS[-1][1]
def azimuth_deg(v):
    return math.degrees(math.atan2(v.x, -v.y))


def edge(az_deg):
    # afro bottom edge: front follows the measured hairline; sides/back descend to jaw/nape (ears covered)
    a=abs(az_deg)
    if a <= 55.0: return hairline(a) - 0.008
    if a >= 80.0: return 1.50
    f=(a-55.0)/25.0; s=f*f*(3.0-2.0*f)
    return hairline(55.0)*(1.0-s) + 1.50*s

CENTER=Vector((0.0, 0.0, 1.635)); RADII=Vector((0.180, 0.175, 0.230))


def deform(p, dirv):
    # FIX11: NO pull-in. The fix4-fix10 pull-in (x/y x0.55 at the front band) put the
    # whole front clump screen BEHIND her forehead plane (measured: joined-mesh front
    # max |y| 0.146 vs envelope 0.170; forehead at -0.095..-0.098) — her crown poked
    # through the recessed screen = the "panel". Roots stay on the raw envelope,
    # ~6cm in front of the forehead; wall/apron/fringe layers tile the corridor.
    return p

# ---------- materials (FIX: no sheen anywhere; dome separate matte-black) ----------
curl_mat=bpy.data.materials.new('AngelAfroMat'); curl_mat.use_nodes=True
b=curl_mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.010,0.008,0.006,1.0)
b.inputs['Roughness'].default_value=0.9
try: b.inputs['Sheen Weight'].default_value=0.0
except Exception: pass
dome_mat=bpy.data.materials.new('AngelAfroDomeMat'); dome_mat.use_nodes=True
b=dome_mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.004,0.004,0.004,1.0)
b.inputs['Roughness'].default_value=1.0
try: b.inputs['Sheen Weight'].default_value=0.0
except Exception: pass

# ---------- 1. scalp cap from Flora ----------
cap_idx=[i for i,s in enumerate(hair.material_slots) if s.material and s.material.name.startswith('Cap')]
cap_faces=[p for p in hair.data.polygons if p.material_index in cap_idx]
import bmesh
bm=bmesh.new(); bm.from_mesh(hair.data)
bm.faces.ensure_lookup_table()
keep=set(p.index for p in cap_faces)
for f in list(bm.faces):
    if f.index not in keep: bm.faces.remove(f)
loose=[v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS')
cap_mesh=bpy.data.meshes.new('AfroCapMesh'); bm.to_mesh(cap_mesh); bm.free()
cap_mesh.materials.append(curl_mat)
for p in cap_mesh.polygons: p.material_index=0
cap_obj=bpy.data.objects.new('AfroCap', cap_mesh)
bpy.context.collection.objects.link(cap_obj)
cap_obj.matrix_world=hair.matrix_world.copy()
g=cap_obj.vertex_groups.new(name='head'); g.add(list(range(len(cap_mesh.vertices))),1.0,'REPLACE')
print('cap verts:', len(cap_mesh.vertices))

# ---------- 2. envelope dome: shrunk 0.97, cut at measured hairline ----------
RADII_D=RADII*0.97
bpy.ops.mesh.primitive_uv_sphere_add(segments=56, ring_count=36, location=CENTER)
dome_obj=bpy.context.active_object; dome_obj.name='AfroDome'
dome_obj.scale=RADII_D
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
dome_mesh=dome_obj.data
for v in dome_mesh.vertices:
    l=v.co.copy()
    dv=Vector((l.x/RADII_D.x, l.y/RADII_D.y, l.z/RADII_D.z))
    w=deform(l+CENTER, dv)
    v.co=w-CENTER
cut=[]
for p in dome_mesh.polygons:
    c=p.center + CENTER
    if c.z < edge(azimuth_deg(c-CENTER)) + 0.010: cut.append(p.index)
import bmesh as _bd
_b=_bd.new(); _b.from_mesh(dome_mesh); _b.faces.ensure_lookup_table()
_bd.ops.delete(_b, geom=[_b.faces[i] for i in cut], context='FACES')
_b.to_mesh(dome_mesh); _b.free()
dome_mesh.materials.append(dome_mat)
g=dome_obj.vertex_groups.new(name='head'); g.add(list(range(len(dome_mesh.vertices))),1.0,'REPLACE')
print('dome faces cut:', len(cut), 'remaining:', len(dome_mesh.polygons), 'verts:', len(dome_mesh.vertices))

# ---------- 3. helix curl clump prototype (v1 shape, slightly thicker tube) ----------
def clump_mesh():
    pts=[]
    turns=4.5; n=22; R=0.0038; length=0.030
    for i in range(n+1):
        f=i/n; ang=f*turns*2*math.pi
        pts.append(Vector((R*math.cos(ang), R*math.sin(ang), f*length)))
    cu=bpy.data.curves.new('clump','CURVE'); cu.dimensions='3D'
    cu.bevel_depth=0.0026; cu.bevel_resolution=1; cu.resolution_u=1
    sp=cu.splines.new('POLY'); sp.points.add(n)
    for i,p in enumerate(pts):
        jx=(random.random()-0.5)*0.0016; jy=(random.random()-0.5)*0.0016
        sp.points[i].co=(p.x+jx,p.y+jy,p.z,1.0)
    ob=bpy.data.objects.new('clump_proto', cu); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH'); ob.select_set(False)
    ob.data.materials.append(curl_mat)
    return ob
proto=clump_mesh()
PROTO_V=len(proto.data.vertices)
print('clump proto verts:', PROTO_V, 'tris:', len(proto.data.polygons))

# ---------- 4. spring chain bones (unchanged) + anchors ----------
bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode='EDIT')
eb=arm.data.edit_bones
head_eb=eb.get('head')
anchors={}
def add_chain(name, surf_pt):
    base=CENTER + (surf_pt-CENTER)*0.35
    tip=surf_pt + (surf_pt-CENTER).normalized()*0.030
    b1=eb.new(name+'1'); b1.head=base; b1.tail=surf_pt; b1.parent=head_eb; b1.use_connect=False
    b2=eb.new(name+'2'); b2.head=surf_pt; b2.tail=tip; b2.parent=b1; b2.use_connect=False
    anchors[name]=(base, surf_pt, tip)
add_chain('hairFront', Vector((0.0,-0.185,1.66)))
add_chain('hairBack',  Vector((0.0, 0.190,1.64)))
add_chain('hairLeft',  Vector((-0.198,0.0,1.62)))
add_chain('hairRight', Vector((0.198,0.0,1.62)))
add_chain('hairTop',   Vector((0.0, 0.0,1.815)))
add_chain('hairTopB',  Vector((0.0, 0.10,1.79)))
bpy.ops.object.mode_set(mode='OBJECT')
anchor_list=[(name, anchors[name][1]) for name in anchors]
print('chains added:', list(anchors.keys()))

# ---------- 5. distribute clumps; weights assigned per-object BEFORE join ----------
GA=math.pi*(3.0-math.sqrt(5.0))
def distribute(target, root_off, tilt_lo, tilt_hi, sc_lo, sc_hi, phase):
    cands=[]; K=int(target*3.4)
    for k in range(1, K+1):
        y=1.0-(k/(K+1.0))*2.0
        rr=math.sqrt(max(0.0,1.0-y*y)); th=GA*(k+phase)
        dirv=Vector((math.cos(th)*rr, math.sin(th)*rr, y))
        p=CENTER+Vector((dirv.x*RADII.x, dirv.y*RADII.y, dirv.z*RADII.z))
        if p.z < edge(azimuth_deg(dirv)) - 0.006: continue
        cands.append((deform(p, dirv), dirv))
    if len(cands) > target:
        idxs=sorted(set(round(i*(len(cands)-1)/(target-1)) for i in range(target)))
        sel=[cands[i] for i in idxs]
    else:
        sel=cands
    print('  pass candidates:', len(cands), 'placing:', len(sel))
    objs=[]
    for p, dirv in sel:
        nrm=Vector((dirv.x/RADII.x, dirv.y/RADII.y, dirv.z/RADII.z)).normalized()
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        p2=p - nrm*root_off
        tilt=math.radians(random.uniform(tilt_lo,tilt_hi)); az=random.uniform(0, 2*math.pi)
        zaxis=(nrm*math.cos(tilt) + Vector((math.cos(az), math.sin(az), 0))*math.sin(tilt)).normalized()
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - zaxis*xaxis.dot(zaxis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=zaxis.cross(xaxis)
        sc2=random.uniform(sc_lo,sc_hi)
        rot=Matrix((xaxis, yaxis, zaxis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
main_objs = distribute(2100, 0.012, 25, 80, 0.85, 1.5, 0)
print('main clumps:', len(main_objs))
frizz_objs = distribute(800, 0.017, 45, 90, 0.45, 0.65, 12345)
print('frizz clumps:', len(frizz_objs))
clump_objs=main_objs+frizz_objs

# ---------- 5b. front fringe: clumps rooted on the hairline ring, axes pointing forward-down so the curl wall starts AT the hairline ----------
def fringe_pass(target):
    objs=[]
    for i in range(target):
        az=math.radians(random.uniform(-75.0, 75.0))
        zz=edge(math.degrees(az)) + random.uniform(-0.005, 0.03)
        dz=max(-0.98, min(0.98, (zz-CENTER.z)/RADII.z))
        rr=math.sqrt(max(0.0, 1.0-dz*dz))
        dirv=Vector((rr*math.sin(az), -rr*math.cos(az), dz))
        p=CENTER+Vector((dirv.x*RADII.x, dirv.y*RADII.y, dirv.z*RADII.z))
        p=deform(p, dirv)
        nrm=Vector((dirv.x/RADII.x, dirv.y/RADII.y, dirv.z/RADII.z)).normalized()
        p2=p - nrm*0.004
        axis=Vector((0.35*math.sin(az), -math.cos(az), -0.70))
        axis+=Vector((random.uniform(-0.18,0.18), random.uniform(-0.18,0.18), random.uniform(-0.15,0.15)))
        zaxis=axis.normalized()
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - zaxis*xaxis.dot(zaxis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=zaxis.cross(xaxis)
        sc2=random.uniform(0.75,1.15)
        rot=Matrix((xaxis, yaxis, zaxis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
fringe_objs = fringe_pass(500)

def wall_fill(target):
    # filled front wall: clumps over the whole front-bottom patch of the deformed envelope,
    # two depth layers, axes blending from forward-down at the hairline to the surface normal higher up
    objs=[]
    for i in range(target):
        az=math.radians(random.uniform(-80.0, 80.0))
        e=edge(math.degrees(az))
        zz=e + random.uniform(-0.03, 0.11)
        dz=max(-0.98, min(0.98, (zz-CENTER.z)/RADII.z))
        rr=math.sqrt(max(0.0, 1.0-dz*dz))
        dirv=Vector((rr*math.sin(az), -rr*math.cos(az), dz))
        p=CENTER+Vector((dirv.x*RADII.x, dirv.y*RADII.y, dirv.z*RADII.z))
        p=deform(p, dirv)
        nrm=Vector((dirv.x/RADII.x, dirv.y/RADII.y, dirv.z/RADII.z)).normalized()
        root_off=0.004 if i%2==0 else 0.022
        p2=p - nrm*root_off
        faxis=Vector((0.35*math.sin(az), -math.cos(az), -0.42))
        faxis+=Vector((random.uniform(-0.15,0.15), random.uniform(-0.15,0.15), random.uniform(-0.12,0.12)))
        blendf=max(0.0, min(1.0, (zz-e-0.09)/0.08))
        axis=(faxis.normalized()*(1.0-blendf) + nrm*blendf).normalized()
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - axis*xaxis.dot(axis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=axis.cross(xaxis)
        sc2=random.uniform(0.75,1.2)
        rot=Matrix((xaxis, yaxis, axis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
wall_objs = wall_fill(900)
print('wall clumps:', len(wall_objs))

print('fringe clumps:', len(fringe_objs))


def apron_pass(target):
    # hanging edge curls rooted ON the dome's front band, axes down-forward,
    # so their bodies lie over the dome face between the hairline and the main wall
    objs=[]
    for i in range(target):
        az=math.radians(random.uniform(-68.0, 68.0))
        e=edge(math.degrees(az))
        zz=e + random.uniform(-0.005, 0.105)
        dz=max(-0.98, min(0.98, (zz-CENTER.z)/RADII.z))
        rr=math.sqrt(max(0.0, 1.0-dz*dz))
        dirv=Vector((rr*math.sin(az), -rr*math.cos(az), dz))
        p=CENTER+Vector((dirv.x*RADII.x, dirv.y*RADII.y, dirv.z*RADII.z))
        p=deform(p, dirv)
        nrm=Vector((dirv.x/RADII.x, dirv.y/RADII.y, dirv.z/RADII.z)).normalized()
        p2=p - nrm*0.002
        axis=Vector((0.30*math.sin(az), -math.cos(az), -0.55))
        axis+=Vector((random.uniform(-0.15,0.15), random.uniform(-0.15,0.15), random.uniform(-0.12,0.12)))
        zaxis=axis.normalized()
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - zaxis*xaxis.dot(zaxis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=zaxis.cross(xaxis)
        sc2=random.uniform(0.8,1.25)
        rot=Matrix((xaxis, yaxis, zaxis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
apron_objs = apron_pass(800)
print('apron clumps:', len(apron_objs))


# ---------- 5c. cap fill: curls rooted on the scalp cap itself, so the face opening
# shows curl volume down to the scalp and the smooth cap never reads as a panel ----------
def cap_fill(target):
    faces=[]
    mw=cap_obj.matrix_world
    for p in cap_obj.data.polygons:
        c=mw @ p.center
        n=(mw.to_3x3() @ p.normal).normalized()
        faces.append((c, n, p.area))
    total_area=sum(f[2] for f in faces)
    objs=[]; tries=0
    while len(objs) < target and tries < target*40:
        tries+=1
        r=random.uniform(0, total_area); acc=0.0; fc=None; fn=None
        for c, n, a in faces:
            acc+=a
            if r <= acc: fc, fn = c, n; break
        if fc is None: continue
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        p2=fc + fn*0.003
        axis=(fn + Vector((0,0,0.38)) + Vector((random.uniform(-0.2,0.2), random.uniform(-0.2,0.2), random.uniform(-0.1,0.1)))).normalized()
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - axis*xaxis.dot(axis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=axis.cross(xaxis)
        sc2=random.uniform(0.85,1.35)
        rot=Matrix((xaxis, yaxis, axis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
cap_objs = cap_fill(850)
print('cap clumps:', len(cap_objs))

# ---------- 5d. hairline seal: SHORT curls rooted on the cap right at the hairline ring,
# axes tilted forward-down — the last screen between the camera and the scalp at the edge ----------
def seal_pass(target):
    faces=[]
    mw=cap_obj.matrix_world
    for p in cap_obj.data.polygons:
        c=mw @ p.center
        n=(mw.to_3x3() @ p.normal).normalized()
        az=azimuth_deg(c-CENTER)
        if abs(az) <= 70 and abs(c.z - hairline(az)) <= 0.028:
            faces.append((c, n, p.area))
    print('seal band faces:', len(faces))
    total_area=sum(f[2] for f in faces)
    objs=[]; tries=0
    while len(objs) < target and tries < target*60:
        tries+=1
        r=random.uniform(0, total_area); acc=0.0; fc=None; fn=None
        for c, n, a in faces:
            acc+=a
            if r <= acc: fc, fn = c, n; break
        if fc is None: continue
        ob=bpy.data.objects.new('clump', proto.data.copy())
        bpy.context.collection.objects.link(ob)
        p2=fc + fn*0.002
        axis=(fn*0.5 + Vector((0,-0.55,-0.62)) + Vector((random.uniform(-0.15,0.15), random.uniform(-0.15,0.15), random.uniform(-0.1,0.1)))).normalized()
        xaxis=Vector((random.random()-0.5, random.random()-0.5, random.random()-0.5))
        xaxis=(xaxis - axis*xaxis.dot(axis)).normalized() if xaxis.length>1e-4 else Vector((1,0,0))
        yaxis=axis.cross(xaxis)
        sc2=random.uniform(0.5,0.8)
        rot=Matrix((xaxis, yaxis, axis)).transposed()
        ob.matrix_world=Matrix.Translation(p2) @ rot.to_4x4() @ Matrix.Scale(sc2,4)
        name, surf = min(anchor_list, key=lambda kv: (kv[1]-p2).length)
        gname=name+('2' if (p2-CENTER).length>0.155 else '1')
        gg=ob.vertex_groups.new(name=gname)
        gg.add(list(range(len(ob.data.vertices))),1.0,'REPLACE')
        objs.append(ob)
    return objs
seal_objs = seal_pass(350)
print('seal clumps:', len(seal_objs))

clump_objs=main_objs+frizz_objs+fringe_objs+wall_objs+apron_objs+cap_objs+seal_objs
print('total clumps:', len(clump_objs))

# ---------- 6. join dome + cap + clumps ----------
bpy.ops.object.select_all(action='DESELECT')
for ob in clump_objs+[dome_obj, cap_obj]: ob.select_set(True)
bpy.context.view_layer.objects.active=dome_obj
bpy.ops.object.join()
afro=dome_obj; afro.name='AngelAfro'
bpy.data.objects.remove(proto, do_unlink=True)
print('afro materials:', [m.name if m else None for m in afro.data.materials])
print('afro vgroups:', [g.name for g in afro.vertex_groups])
mod=afro.modifiers.new('Armature','ARMATURE'); mod.object=arm
afro.parent=arm
print('Afro verts:', len(afro.data.vertices), 'polys:', len(afro.data.polygons))
bpy.context.view_layer.objects.active=afro
bpy.ops.wm.save_as_mainfile(filepath=SAVE)
print('BUILD DONE + SAVED')
