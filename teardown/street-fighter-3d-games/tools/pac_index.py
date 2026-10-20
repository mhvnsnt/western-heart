#!/usr/bin/env python3
"""Chunk-index Arika PL/*.PAC files (SF EX Plus Alpha PS1).
Documented format (TEARDOWN.md 2d): 44-entry LE offset table, then 44 chunks
(TMD model parts, TIM textures, animation data). Index only; no format guessing."""
import os, struct, sys, json
TYPE_HINTS = {0x41: 'TMD (model)', 0x10: 'TIM (texture)'}
def index_pac(path):
    with open(path, 'rb') as f: data = f.read()
    if len(data) < 44*4: return {'file': path, 'error': 'too small for 44-entry table'}
    offs = struct.unpack('<44I', data[:176]); size = len(data); chunks = []
    for i, o in enumerate(offs):
        nxt = offs[i+1] if i+1 < len(offs) else size
        if o >= size or nxt > size or nxt < o:
            chunks.append({'idx': i, 'offset': o, 'size': None, 'error': 'bad offset'}); continue
        magic = struct.unpack('<I', data[o:o+4])[0] if nxt-o >= 4 else None
        hint = TYPE_HINTS.get((magic & 0xFF) if magic is not None else -1, 'unknown')
        chunks.append({'idx': i, 'offset': o, 'size': nxt-o,
                       'magic': f'{magic:#010x}' if magic is not None else None, 'type_hint': hint})
    return {'file': os.path.basename(path), 'bytes': size, 'chunks': chunks}
def main(root, out):
    manifest = []
    for fn in sorted(os.listdir(root)):
        if fn.upper().endswith('.PAC'):
            manifest.append(index_pac(os.path.join(root, fn)))
            print(fn, manifest[-1]['bytes'], 'bytes')
    with open(out, 'w') as f:
        json.dump({'source': 'PL/*.PAC chunk index (documented 44-entry Arika table format, TEARDOWN.md 2d)',
                   'files': manifest}, f, indent=1)
    print('wrote', out)
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
