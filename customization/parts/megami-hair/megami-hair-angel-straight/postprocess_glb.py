"""Author the Angel straight GLB's color sections at the glTF level:
AngelBlack/AngelCap get a darkening baseColorFactor; AngelBlonde gets its own
baked blonde variant of Flora's hair texture (embedded image), since a <=1
factor cannot brighten the dark source texture toward blonde.
FIX PASS (2026-11-08): AngelCap darkened + roughness 1.0 so the exposed cap
no longer catches a glossy dome highlight above the headband."""
import json, struct, io, sys
import numpy as np
from PIL import Image
SRC='straight-raw.glb'; OUT='straight-v2.glb'
d=open(SRC,'rb').read()
jl=struct.unpack('<I',d[12:16])[0]; g=json.loads(d[20:20+jl])
off=20+jl; bl=struct.unpack('<I',d[off:off+4])[0]; binchunk=bytearray(d[off+8:off+8+bl])
def img_bytes(i):
    bv=g['bufferViews'][g['images'][i]['bufferView']]
    o=bv.get('byteOffset',0); return bytes(binchunk[o:o+bv['byteLength']])
# find the hair texture image used by AngelBlack
mats={m['name']:m for m in g['materials']}
hair_tex_idx=mats['AngelBlack']['pbrMetallicRoughness']['baseColorTexture']['index']
hair_img_idx=g['textures'][hair_tex_idx]['source']
im=Image.open(io.BytesIO(img_bytes(hair_img_idx))).convert('RGB')
px=np.asarray(im).astype(np.float32)/255.0
px=px*np.array([3.6,3.1,2.2],dtype=np.float32)+np.array([0.16,0.13,0.05],dtype=np.float32)
lum=(px*np.array([0.299,0.587,0.114],dtype=np.float32)).sum(axis=2,keepdims=True)
px=np.clip(px*0.55+lum*0.45,0,1)
out_im=Image.fromarray((px*255).astype(np.uint8))
buf=io.BytesIO(); out_im.save(buf,'JPEG',quality=92); jb=buf.getvalue()
while len(binchunk)%4: binchunk+=b'\0'
g['bufferViews'].append({'buffer':0,'byteOffset':len(binchunk),'byteLength':len(jb)})
binchunk+=jb
g['images'].append({'name':'AngelHairBlondeTex','mimeType':'image/jpeg','bufferView':len(g['bufferViews'])-1})
g['textures'].append({'source':len(g['images'])-1,'sampler':g['textures'][hair_tex_idx].get('sampler',0)})
mats['AngelBlonde']['pbrMetallicRoughness']['baseColorTexture']={'index':len(g['textures'])-1}
mats['AngelBlack']['pbrMetallicRoughness']['baseColorFactor']=[0.18,0.15,0.13,1.0]
mats['AngelCap']['pbrMetallicRoughness']['baseColorFactor']=[0.012,0.011,0.010,1.0]
mats['AngelCap']['pbrMetallicRoughness']['roughnessFactor']=1.0
g['buffers'][0]['byteLength']=len(binchunk)
gj=json.dumps(g).encode()
while len(gj)%4: gj+=b' '
total=12+8+len(gj)+8+len(binchunk)
with open(OUT,'wb') as f:
    f.write(struct.pack('<III',0x46546C67,2,total))
    f.write(struct.pack('<I4s',len(gj),b'JSON')); f.write(gj)
    f.write(struct.pack('<I4s',len(binchunk),b'BIN\0')); f.write(binchunk)
import os; print('FINAL', os.path.getsize(OUT))
