"""Build pkg00 GLB with decl textured by candidate A, then byte-patch the
embedded PNG for other candidates (image view is the last bufferView)."""
import json, struct, sys, io, os
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
import build6 as B

WIN = '/home/hatch/workspace/_doa4p2-scratch/p6/chrone_pkg00_window.bin'
GRAPH = '/home/hatch/workspace/_doa4p2-scratch/work/chrone_pkg00_graph.json'
TEXDIR = '/home/hatch/workspace/_doa4p2-scratch/p6/tex_pkg00'

def build_with(decl_mesh, tex_png_name, out):
    png = open(os.path.join(TEXDIR, tex_png_name), 'rb').read()
    B.build(WIN, GRAPH, out, 'texcand', matmap={decl_mesh: png})

def patch_png(glb_in, new_png_name, glb_out):
    raw = open(glb_in, 'rb').read()
    jlen = struct.unpack('<I', raw[12:16])[0]
    gltf = json.loads(raw[20:20 + jlen])
    blen = struct.unpack('<I', raw[20 + jlen:24 + jlen])[0]
    blob = bytearray(raw[28 + jlen:28 + jlen + blen])
    iv = gltf['images'][0]['bufferView']
    off, ln = gltf['bufferViews'][iv]['byteOffset'], gltf['bufferViews'][iv]['byteLength']
    new = open(os.path.join(TEXDIR, new_png_name), 'rb').read()
    blob[off:off + ln] = new + b'\x00' * ((4 - len(new) % 4) % 4)
    gltf['bufferViews'][iv]['byteLength'] = len(new)
    gltf['buffers'][0]['byteLength'] = len(blob)
    js = json.dumps(gltf).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(blob))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    out += struct.pack('<II', len(blob), 0x004E4942) + bytes(blob)
    open(glb_out, 'wb').write(out)
    print('patched', glb_out, new_png_name)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'build':
        build_with(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        patch_png(sys.argv[2], sys.argv[3], sys.argv[4])
