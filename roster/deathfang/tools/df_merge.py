import numpy as np, struct, os
from pygltflib import GLTF2, BufferView, Accessor, Image as GImage, Texture, Material, PbrMetallicRoughness, Mesh, Primitive, Attributes, Node

base = os.path.expanduser("~/workspace/_wh-work/deathfang-yamazaki")
src = base + "/roster/iori/attires/attire1/model.glb"
out = base + "/roster/deathfang/attires/attire1/model.glb"

g = GLTF2().load(src)
blob = g.binary_blob()
print("orig: nodes", len(g.nodes), "meshes", len(g.meshes), "images", len(g.images), "mats", len(g.materials), "skins", len(g.skins))
# find JOINTS_0 accessor of first mesh to reuse component type
jtype = None
for m in g.meshes:
    for p in m.primitives:
        ji = getattr(p.attributes, 'JOINTS_0', None)
        if ji is not None:
            jtype = g.accessors[ji].componentType
print("JOINTS_0 componentType:", jtype)

skin = g.skins[0]
joint_ord = {}
for ord_, node_idx in enumerate(skin.joints):
    joint_ord[g.nodes[node_idx].name] = ord_
obj10_idx = next(i for i, n in enumerate(g.nodes) if n.name == 'Object_10')
print("Object_10 node:", obj10_idx, "children:", g.nodes[obj10_idx].children)

segs = []   # (bytes, target)
def add_seg(data, target=None):
    b = bytes(data)
    segs.append((b, target))
    return len(segs) - 1

reskin = open(base + '/_df_tools/reskin_image0.png', 'rb').read()
reskin_seg = add_seg(reskin)

chains = np.load(base + '/_df_tools/chains.npz', allow_pickle=True)
jmap = np.load(base + '/_df_tools/chains_joints.npz', allow_pickle=True)
meta = np.load(base + '/_df_tools/chains_meta.npz')
names = ['wristL', 'wristR', 'ankleL', 'ankleR', 'anklechain', 'collar', 'chest1', 'chest2']

# materials
iron = Material(name='DEATHFANG_IRON',
    pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=[0.055, 0.055, 0.07, 1.0], metallicFactor=0.9, roughnessFactor=0.42))
iron_idx = len(g.materials); g.materials.append(iron)

new_blob = bytearray(blob)
bvs = []
def push_seg(data, target=None):
    global new_blob
    off = len(new_blob)
    new_blob += data
    pad = (-len(new_blob)) % 4
    new_blob += b'\x00' * pad
    bv = BufferView(buffer=0, byteOffset=off, byteLength=len(data), target=target)
    g.bufferViews.append(bv)
    return len(g.bufferViews) - 1

# process segments in append order; reskin first
reskin_bv = push_seg(reskin)
g.images[0].bufferView = reskin_bv
print("images[0] -> bufferView", reskin_bv, "(reskinned texture)")

ARRAY, ELEMENT = 34962, 34963
def acc(data, comp, atype, target):
    a = np.asarray(data)
    bv = push_seg(a.tobytes(), target)
    mn = [float(x) for x in a.min(axis=0)] if a.ndim > 1 else [float(a.min())]
    mx = [float(x) for x in a.max(axis=0)] if a.ndim > 1 else [float(a.max())]
    g.accessors.append(Accessor(bufferView=bv, componentType=comp, count=len(a), type=atype, min=mn, max=mx))
    return len(g.accessors) - 1

aL = meta['aL_local']; aR = meta['aR_local']
split_axis = int(np.argmax(np.abs(aL - aR)))
split_mid = float((aL[split_axis] + aR[split_axis]) / 2)
print("split axis", split_axis, "mid", split_mid)

mesh_idx0 = len(g.meshes)
new_node_idxs = []
for name in names:
    V = chains[name].astype('float32')
    N = chains[name + '_n'].astype('float32')
    I = chains[name + '_i'].astype('uint32')
    j = str(jmap[name].item() if hasattr(jmap[name], 'item') else jmap[name])
    if '|' in j:
        bL, bR = j.split('|')
        oL, oR = joint_ord[bL], joint_ord[bR]
        vpl = 135  # (14+1)*(8+1) verts per torus link, contiguous
        nl = len(V)//vpl
        ords = np.zeros(len(V), dtype='uint16')
        for li in range(nl):
            seg = V[li*vpl:(li+1)*vpl]
            o = oL if float(seg[:, split_axis].mean()) < split_mid else oR
            ords[li*vpl:(li+1)*vpl] = o
    else:
        o = joint_ord[j]
        ords = np.full(len(V), o, dtype='uint16')
    J = np.zeros((len(V), 4), dtype='uint16'); J[:, 0] = ords
    Wv = np.zeros((len(V), 4), dtype='float32'); Wv[:, 0] = 1.0
    a_pos = acc(V, 5126, 'VEC3', ARRAY)
    a_nor = acc(N, 5126, 'VEC3', ARRAY)
    a_j = acc(J, 5123, 'VEC4', ARRAY)
    a_w = acc(Wv, 5126, 'VEC4', ARRAY)
    a_idx = acc(I, 5125, 'SCALAR', ELEMENT)
    attrs = Attributes(); attrs.POSITION = a_pos; attrs.NORMAL = a_nor
    attrs.JOINTS_0 = a_j; attrs.WEIGHTS_0 = a_w
    prim = Primitive(attributes=attrs, indices=a_idx, material=iron_idx)
    g.meshes.append(Mesh(name='DF_' + name, primitives=[prim]))
    mi = len(g.meshes) - 1
    g.nodes.append(Node(name='DF_' + name, mesh=mi, skin=0))
    ni = len(g.nodes) - 1
    new_node_idxs.append(ni)
    print("mesh", name, "verts", len(V), "node", ni)

g.nodes[obj10_idx].children = list(g.nodes[obj10_idx].children or []) + new_node_idxs
g.buffers[0].byteLength = len(new_blob)
g.set_binary_blob(bytes(new_blob))
g.save_binary(out)
print("SAVED", out, os.path.getsize(out))

# verify
g2 = GLTF2().load(out)
print("verify: nodes", len(g2.nodes), "meshes", len(g2.meshes), "skins", len(g2.skins), "anims", len(g2.animations))
sk = g2.skins[0]
jo = {g2.nodes[i].name: o for o, i in enumerate(sk.joints)}
for m in g2.meshes:
    if m.name and m.name.startswith('DF_'):
        p = m.primitives[0]
        ja = g2.accessors[p.attributes.JOINTS_0]
        print(m.name, "mat", g2.materials[p.material].name, "verts", g2.accessors[p.attributes.POSITION].count)
print("iron mat:", g2.materials[iron_idx].name, g2.materials[iron_idx].pbrMetallicRoughness.metallicFactor)
