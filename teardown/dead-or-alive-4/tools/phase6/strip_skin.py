import json, struct, sys
raw = open(sys.argv[1], 'rb').read()
jlen = struct.unpack('<I', raw[12:16])[0]
gltf = json.loads(raw[20:20 + jlen])
blen = struct.unpack('<I', raw[20 + jlen:24 + jlen])[0]
blob = raw[28 + jlen:28 + jlen + blen]
gltf.pop('skins', None)
keep = []
for n in gltf['nodes']:
    n.pop('skin', None)
    keep.append(n)
# drop joint nodes (they carried transforms only); keep mesh nodes + scene roots pointing at meshes
mesh_node_idx = [i for i, n in enumerate(gltf['nodes']) if 'mesh' in n]
remap = {old: i for i, old in enumerate(mesh_node_idx)}
gltf['nodes'] = [gltf['nodes'][i] for i in mesh_node_idx]
gltf['scenes'][0]['nodes'] = [remap[i] for i in gltf['scenes'][0]['nodes'] if i in remap]
for m in gltf['meshes']:
    for p in m['primitives']:
        p['attributes'].pop('JOINTS_0', None); p['attributes'].pop('WEIGHTS_0', None)
js = json.dumps(gltf).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(blob))
out += struct.pack('<II', len(js), 0x4E4F534A) + js
out += struct.pack('<II', len(blob), 0x004E4942) + blob
open(sys.argv[2], 'wb').write(out)
print('wrote', sys.argv[2])
