"""Report every base-colour image in a GLB: decodes? truncated? alpha range. python3 -I glb_images.py FILE"""
import io, json, struct, sys
from PIL import Image
b = open(sys.argv[1], 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + jl]); binoff = 20 + jl + 8
used = {}
for mt in j.get('materials', []):
    t = mt.get('pbrMetallicRoughness', {}).get('baseColorTexture', {}).get('index')
    if t is not None: used.setdefault(j['textures'][t]['source'], []).append((mt.get('name', '')[:24], mt.get('alphaMode', 'OPAQUE')))
bad = 0
for idx, im in enumerate(j.get('images', [])):
    if 'bufferView' not in im: continue
    bv = j['bufferViews'][im['bufferView']]
    data = b[binoff + bv.get('byteOffset', 0): binoff + bv.get('byteOffset', 0) + bv['byteLength']]
    try:
        I = Image.open(io.BytesIO(data)); I.load(); a = I.getchannel('A').getextrema() if 'A' in I.getbands() else None; st = f'ok {I.mode} {I.size} alpha {a}'
    except Exception as e:
        st = f'BROKEN ({e})'; bad += 1
    if idx in used or st.startswith('BROKEN'):
        print(idx, im.get('name'), len(data), st, used.get(idx))
print('broken images:', bad)
