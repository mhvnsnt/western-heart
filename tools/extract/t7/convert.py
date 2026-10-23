#!/usr/bin/env python3
"""gltf->glb (pygltflib) and tga->webp/png for UModel exports. usage: convert.py <umodel_out> <tex_out> <dest>"""
import sys, os, glob, json
from pygltflib import GLTF2
from PIL import Image
src, tex, dst = sys.argv[1:4]
man = {'meshes': [], 'textures': []}
for f in glob.glob(f'{src}/**/*.gltf', recursive=True):
    rel = os.path.relpath(f, src)[:-5] + '.glb'
    out = os.path.join(dst, 'models', rel); os.makedirs(os.path.dirname(out), exist_ok=True)
    g = GLTF2().load(f); g.convert_buffers('binary_blob'); g.save_binary(out)
    man['meshes'].append({'file': 'models/' + rel, 'joints': max([len(s.joints) for s in g.skins] or [0])})
for f in glob.glob(f'{tex}/**/*.tga', recursive=True):
    rel = os.path.relpath(f, tex)[:-4]
    ui = 'UI_common' in f
    out = os.path.join(dst, 'textures', rel + ('.png' if ui else '.webp')); os.makedirs(os.path.dirname(out), exist_ok=True)
    im = Image.open(f)
    if ui: im.save(out, optimize=True)
    else: im.save(out, quality=90, method=4)
    man['textures'].append(os.path.relpath(out, dst))
json.dump(man, open(os.path.join(dst, 'manifest.json'), 'w'), indent=1)
print(len(man['meshes']), 'glb', len(man['textures']), 'tex')
