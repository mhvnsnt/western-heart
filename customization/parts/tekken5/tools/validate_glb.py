"""Minimal GLB validator: parse header + JSON chunk, report meshes/primitives,
images, materials-with-baseColorTexture, total POSITION verts and index tris."""
import struct, json, sys

def validate(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'glTF', 'bad magic'
    ver, total = struct.unpack_from('<II', data, 4)
    assert total == len(data), f'length field {total} != file {len(data)}'
    jlen, jtype = struct.unpack_from('<II', data, 12)
    assert jtype == 0x4E4F534A, 'first chunk not JSON'
    g = json.loads(data[20:20 + jlen])
    verts = tris = 0
    for mesh in g.get('meshes', []):
        for prim in mesh['primitives']:
            acc = g['accessors'][prim['attributes']['POSITION']]
            verts += acc['count']
            if 'indices' in prim:
                tris += g['accessors'][prim['indices']]['count'] // 3
    mats = g.get('materials', [])
    textured = sum(1 for m in mats if m.get('pbrMetallicRoughness', {}).get('baseColorTexture') is not None)
    return {'meshes': len(g.get('meshes', [])), 'images': len(g.get('images', [])),
            'materials': len(mats), 'materials_textured': textured,
            'verts': verts, 'tris': tris, 'size': len(data)}

if __name__ == '__main__':
    print(json.dumps(validate(sys.argv[1])))
