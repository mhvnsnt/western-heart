import bpy, os, math, collections, json
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

base = os.path.expanduser("~/workspace/_wh-work/deathfang-yamazaki")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=base+"/roster/iori/attires/attire1/model.glb")
if 'Icosphere' in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)
bpy.context.view_layer.update()
arm = bpy.data.objects['Object_10']
meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
base_img = bpy.data.images['Image_0']
W, H = base_img.size
print("base img:", base_img.name, (W, H))

def cat_of(group_names):
    for g in group_names:
        if 'Hair' in g: return 'HAIR'
    for g in group_names:
        if any(k in g for k in ('Head_019','Neck001','Eye L','Eye R')): return 'HEAD'
    for g in group_names:
        if any(k in g for k in ('Hand','Finger')): return 'HEAD'
    for g in group_names:
        if any(k in g for k in ('Thigh','Calf','Foot','Toe','Claf')): return 'LEGS'
    return 'TORSO'

masks = {c: Image.new('L', (W, H), 0) for c in ('HAIR','HEAD','LEGS','TORSO')}
for m in meshes:
    uv = m.data.uv_layers.active
    vg = m.vertex_groups
    for p in m.data.polygons:
        votes = collections.Counter(); uvs = []
        for li in p.loop_indices:
            lp = m.data.loops[li]; v = m.data.vertices[lp.vertex_index]
            if v.groups:
                best = max(v.groups, key=lambda g: g.weight)
                votes[cat_of([vg[best.group].name])] += 1
            uvs.append(uv.data[li].uv)
        cat = votes.most_common(1)[0][0] if votes else 'TORSO'
        ImageDraw.Draw(masks[cat]).polygon([(u*W, (1-v)*H) for (u, v) in uvs], fill=255)
mask_np = {c: (np.flipud(np.array(masks[c]))/255.0) for c in masks}

pix = np.array(base_img.pixels[:], dtype=np.float64).reshape(H, W, 4)
_r, _g, _b = pix[..., 0], pix[..., 1], pix[..., 2]
_crimson = ((_r > 0.30) & (_r > 1.5*_g) & (_r > 1.5*_b)).astype(np.float64)
_hm_extra = _crimson * np.clip(mask_np['HEAD'] + mask_np['HAIR'], 0, 1)
mask_np['HAIR'] = np.clip(mask_np['HAIR'] + _hm_extra, 0, 1)
mask_np['HEAD'] = mask_np['HEAD'] * (1 - mask_np['HAIR'])
for c in mask_np: print("mask", c, round(float(mask_np[c].mean()), 4))

rgb = pix[..., :3]
lum = (0.299*rgb[..., 0] + 0.587*rgb[..., 1] + 0.114*rgb[..., 2])[..., None]
hm = mask_np['HAIR'][..., None]
rgb = rgb*(1-hm) + (lum*0.30*np.array([1.0, 0.92, 0.96]))*hm          # hair -> emo black
lm = mask_np['LEGS'][..., None]
rgb = rgb*(1-lm) + (lum*0.30)*lm                                       # pants -> charcoal
tm = mask_np['TORSO'][..., None]
factor = 0.35 + 0.65*(1-np.clip(lum, 0, 1))
rgb = rgb*(1-tm) + np.clip(rgb*factor, 0, 1)*tm                        # jacket/shirt -> dark
sm = mask_np['HEAD'][..., None]
pale = np.clip(rgb*1.05 + 0.02, 0, 1)
plum = (0.299*pale[..., 0] + 0.587*pale[..., 1] + 0.114*pale[..., 2])[..., None]
pale = pale*0.65 + plum*np.array([1.03, 1.0, 0.97])*0.35
rgb = rgb*(1-sm) + pale*sm                                             # skin -> pale
pix[..., :3] = np.clip(rgb, 0, 1)
print("color reskin done")

# ---- NO FUTURE tattoo, drawn on the face region of the texture ----
small = np.array(Image.fromarray((mask_np['HEAD']*255).astype('uint8')).resize((128, 128))) > 100
Hh, Hw = small.shape
seen = np.zeros_like(small, bool); best = []
for sy in range(Hh):
    for sx in range(Hw):
        if small[sy, sx] and not seen[sy, sx]:
            q = deque([(sy, sx)]); seen[sy, sx] = True; comp = []
            while q:
                y, x = q.popleft(); comp.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y+dy, x+dx
                    if 0 <= ny < Hh and 0 <= nx < Hw and small[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            if len(comp) > len(best): best = comp
bys = [c[0] for c in best]; bxs = [c[1] for c in best]
# mask_np is bottom-up (v up); PIL coords are top-down: flip y
gx0, gx1 = min(bxs)/128, max(bxs)/128
gy_top, gy_bot = (1-max(bys)/128), (1-min(bys)/128)   # in PIL-normalized (top=0)
fx0, fx1 = int(gx0*W), int(gx1*W)
fy0, fy1 = int(gy_top*H), int(gy_bot*H)
print("face blob PIL bbox:", fx0, fy0, fx1, fy1)
tpil = Image.fromarray((np.clip(pix[..., :3], 0, 1)*255).astype('uint8'))
td = ImageDraw.Draw(tpil)
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fs = max(10, int((fy1-fy0)*0.30))
font = ImageFont.truetype(F, fs)
txt = 'NO FUTURE'
tb = td.textbbox((0, 0), txt, font=font)
fs = max(10, int(fs * ((fx1-fx0)*0.88) / max(1, tb[2]-tb[0])))
font = ImageFont.truetype(F, fs)
tb = td.textbbox((0, 0), txt, font=font)
fs2 = max(10, int(fs * ((fx1-fx0)*0.42) / max(1, tb[2]-tb[0])))
font = ImageFont.truetype(F, fs2)
tb = td.textbbox((0, 0), txt, font=font)
tx = fx0 + ((fx1-fx0)-(tb[2]-tb[0]))/2 - tb[0]
ty = fy0 + (fy1-fy0)*0.52 - tb[1]
td.text((tx, ty), txt, font=font, fill=(12, 8, 12, 255), stroke_width=2, stroke_fill=(12, 8, 12, 255))
pix[..., :3] = np.array(tpil).astype(np.float64)/255.0
print("tattoo at PIL", round(tx), round(ty), "font", fs)

base_img.pixels.foreach_set(list(pix.ravel()))
base_img.update()
base_img.filepath_raw = base + '/_df_tools/reskin_image0.png'
base_img.save()
print("saved reskin png")

# ---- CHAINS (numpy torus) in rest world space -> mesh-local space ----
def bw_head(bn): return np.array([float(x) for x in (arm.matrix_world @ arm.data.bones[bn].head_local)])
def bw_tail(bn): return np.array([float(x) for x in (arm.matrix_world @ arm.data.bones[bn].tail_local)])
def bw_dir(bn): return (bw_tail(bn) - bw_head(bn)) / np.linalg.norm(bw_tail(bn) - bw_head(bn))

def rot_to(axis):
    z = np.array([0., 0., 1.]); a = np.array(axis, float); a = a/np.linalg.norm(a)
    v = np.cross(z, a); c = float(np.dot(z, a))
    if np.linalg.norm(v) < 1e-8:
        return np.eye(3) if c > 0 else np.diag([1., -1., -1.])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0/(1.0+c))

def torus(center, axis, R, r, ms=14, ns=8):
    Rm = rot_to(axis)
    verts = []; norms = []
    for i in range(ms+1):
        u = 2*math.pi*i/ms
        cu, su = math.cos(u), math.sin(u)
        for j in range(ns+1):
            v = 2*math.pi*j/ns
            n = np.array([cu*math.cos(v), su*math.cos(v), math.sin(v)])
            p = np.array([R*cu, R*su, 0.]) + r*n
            verts.append(Rm @ p + np.array(center)); norms.append(Rm @ n)
    idx = []
    w = ns+1
    for i in range(ms):
        for j in range(ns):
            a = i*w + j; b2 = a + w
            idx += [a, b2, a+1, b2, b2+1, a+1]
    return np.array(verts, 'float64'), np.array(norms, 'float64'), np.array(idx, 'uint32')

DOWN = np.array([0., 0., -1.]); FX = np.array([1., 0., 0.])
sets = {}   # name -> (verts, norms, indices, joint_name or ('split', boneL, boneR))
def newset(name, joint): sets[name] = ([], [], [], joint)
def add(name, tv, tn, ti):
    v, n, ix = sets[name][0], sets[name][1], sets[name][2]
    off = sum(len(x) for x in v)
    v.append(tv); n.append(tn)
    ix.append(ti + off)

def shackle(name, bone, axis_bone, R, r):
    add(name, *torus(bw_head(bone), bw_dir(axis_bone), R, r))
def hang(name, start, count, R, r, step):
    c = np.array(start, float)
    for i in range(count):
        add(name, *torus(c, DOWN if i % 2 == 0 else FX, R, r))
        c = c + DOWN*step
def line(name, p0, p1, count, R, r):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    tang = (p1-p0)/np.linalg.norm(p1-p0)
    alt = np.cross(tang, [1., 0., 0.]) if abs(tang[0]) < 0.9 else np.cross(tang, [0., 1., 0.])
    alt = alt/np.linalg.norm(alt)
    for i in range(count):
        t = i/(count-1) if count > 1 else 0.
        add(name, *torus(p0 + (p1-p0)*t, tang if i % 2 == 0 else alt, R, r))

for side, hand, fore in (('L', 'Bip001 L Hand_029', 'Bip001 L Forearm_028'), ('R', 'Bip001 R Hand_046', 'Bip001 R Forearm_045')):
    newset('wrist'+side, hand)
    shackle('wrist'+side, hand, fore, 0.00135, 0.00045)
    c = bw_head(hand); c[2] -= 0.0016
    hang('wrist'+side, c, 5, 0.00095, 0.0003, 0.00155)
for side, foot, calf in (('L', 'Bip001 L Foot_05', 'Bip001 L Calf_04'), ('R', 'Bip001 R Foot_012', 'Bip001 R Calf_011')):
    newset('ankle'+side, foot)
    shackle('ankle'+side, foot, calf, 0.00155, 0.0005)
aL = bw_head('Bip001 L Foot_05'); aR = bw_head('Bip001 R Foot_012'); amid = (aL+aR)/2
newset('anklechain', ('split', 'Bip001 L Foot_05', 'Bip001 R Foot_012'))
pts = []
for i in range(7):
    t = i/6; p = aL + (aR-aL)*t; p[2] -= 0.0052*math.sin(math.pi*t); pts.append(p)
for i, p in enumerate(pts):
    tang = pts[min(i+1, 6)] - pts[max(i-1, 0)]; tang = tang/np.linalg.norm(tang)
    alt = np.cross(tang, [0., 0., 1.]); alt = alt/max(np.linalg.norm(alt), 1e-9)
    add('anklechain', *torus(p, tang if i % 2 == 0 else alt, 0.00085, 0.00028))
newset('collar', 'Bip001 Neck_018')
shackle('collar', 'Bip001 Neck_018', 'Bip001 Neck_018', 0.0021, 0.00055)
c = bw_head('Bip001 Neck_018') + np.array([-1., 0., 0.])*0.0022; c[2] -= 0.0022
hang('collar', c, 3, 0.00095, 0.0003, 0.00155)
FRONT = np.array([-1., 0., 0.])
cl_ = bw_head('Bip001 L Clavicle_026') + FRONT*0.0026
cr_ = bw_head('Bip001 R Clavicle_043') + FRONT*0.0026
pl_ = bw_head('Bip001 Pelvis_01') + np.array([0., -0.0022, 0.0006]) + FRONT*0.0028
pr_ = bw_head('Bip001 Pelvis_01') + np.array([0.,  0.0022, 0.0006]) + FRONT*0.0028
newset('chest1', 'Bip001 Spine1_017'); line('chest1', cl_, pr_, 6, 0.0008, 0.00027)
newset('chest2', 'Bip001 Spine1_017'); line('chest2', cr_, pl_, 6, 0.0008, 0.00027)

T13 = np.array([[float(bpy.data.objects['Object_13'].matrix_world[r][c]) for c in range(4)] for r in range(4)])
Tinv = np.linalg.inv(T13)
print("T det:", float(np.linalg.det(T13)), "Tinv ok")

out = {}
for name, (vs, ns_, ixs, joint) in sets.items():
    V = np.concatenate(vs); N = np.concatenate(ns_); I = np.concatenate(ixs)
    ones = np.ones((len(V), 1))
    Vl = (Tinv @ np.concatenate([V, ones], axis=1).T).T[:, :3]
    Nl = N @ np.linalg.inv(Tinv[:3, :3]).T
    Nl = Nl / np.linalg.norm(Nl, axis=1, keepdims=True)
    out[name] = (Vl.astype('float32'), Nl.astype('float32'), I.astype('uint32'), joint, amid.copy())
    print(name, "verts", len(Vl), "joint", joint)
np.savez(base + '/_df_tools/chains_blender_DO_NOT_USE.npz',
         **{k: v[0] for k, v in out.items()},
         **{k+'_n': v[1] for k, v in out.items()},
         **{k+'_i': v[2] for k, v in out.items()},
         **{k+'_j': np.array(v[3] if isinstance(v[3], str) else v[3][1] + '|' + v[3][2]) for k, v in out.items()},
         ankle_mid=aL + (aR-aL)*0)
def to_local(p): return (Tinv @ np.array([p[0], p[1], p[2], 1.0]))[:3]
np.savez(base + '/_df_tools/chains_blender_meta_DO_NOT_USE.npz', aL_local=to_local(aL), aR_local=to_local(aR))
print("chains saved")
