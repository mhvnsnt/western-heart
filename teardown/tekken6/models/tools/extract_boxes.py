#!/usr/bin/env python3
"""Extract 8-vertex bounding boxes from Tekken 6 NDPP sections (81MB archive).
Reads bulk_decrypted.bin via offsets (read-only, no full copies).
Outputs: boxes.json with per-section box vertex lists.
"""
import struct, json
import numpy as np

BULK = '/home/hatch/workspace/game-reverse-engineering/tekken6/work/decrypt3/bulk_decrypted.bin'
ARC_OFF = 38592 * 2048
OUT = '/home/hatch/workspace/game-reverse-engineering/tekken6/work/extract/boxes.json'

def read_at(off, n):
    with open(BULK, 'rb') as f:
        f.seek(off)
        return f.read(n)

# chain-walk sections
cur = ARC_OFF + 66636400
sections = []
guard = 0
while cur < ARC_OFF + 72140288 and guard < 5000:
    guard += 1
    hdr = read_at(cur, 20)
    if struct.unpack_from('<I', hdr, 0)[0] != 0x5050444e:
        buf = read_at(cur, 1024 * 1024)
        j = buf.find(b'NDPP')
        if j < 0:
            break
        cur = cur + j
        continue
    size, flags = struct.unpack_from('<II', hdr, 4)
    f5 = struct.unpack_from('<f', hdr, 16)[0]
    sections.append({'rel': cur - ARC_OFF, 'size': size, 'flags': flags, 'f5': f5})
    if size < 20:
        break
    cur += size

print(f"sections: {len(sections)}")

def find_boxes(payload):
    fl = np.frombuffer(payload, dtype='<f4')
    n = len(fl)
    boxes = []
    i = 0
    while i <= n - 24:
        win = fl[i:i + 24]
        if np.all(np.abs(win) < 2.0) and np.all(np.isfinite(win)):
            verts = win.reshape(8, 3)
            ok = True
            for ax in range(3):
                u = np.unique(np.round(verts[:, ax], 4))
                if len(u) > 3 or len(u) < 2:
                    ok = False
                    break
            if ok:
                boxes.append({'word_off': i, 'verts': verts.tolist()})
                i += 24
                continue
        i += 1
    return boxes

result = []
for idx, s in enumerate(sections):
    payload = read_at(ARC_OFF + s['rel'] + 20, s['size'] - 20)
    boxes = find_boxes(payload)
    result.append({
        'section': idx,
        'rel': s['rel'],
        'size': s['size'],
        'flags': s['flags'],
        'boxes': boxes,
    })
    if idx % 50 == 0:
        print(f"  section {idx}: {len(boxes)} boxes")

total = sum(len(r['boxes']) for r in result)
print(f"total boxes: {total}")

with open(OUT, 'w') as f:
    json.dump(result, f)
print(f"wrote {OUT}")
