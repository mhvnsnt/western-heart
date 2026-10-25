#!/usr/bin/env python3
"""Build textured GLB from phase-1 GLB + PPK textures.
Assignment: per face-component edge-continuity scoring, smoothed by
majority vote over neighbouring components in vertex-index order
(components of one DMA piece are contiguous in index space and share
one draw texture). Undecided components keep no material.
Geometry untouched: same POSITION accessor, same total index count.
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0])
import ur_tex_extract as tx

def load_glb(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'glTF'
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20+ln])
    bofs = 20 + ln
    bln = struct.unpack('<I', d[bofs:bofs+4])[0]
    bin_ = d[bofs+8:bofs+8+bln]
    return j, bin_

def acc_data(j, bin_, ai):
    a = j['accessors'][ai]; bv = j['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = a['count']; t = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    arr = np.frombuffer(bin_, dtype=dt, count=n*t, offset=off)
    return arr.reshape(n, t) if t > 1 else arr

def decode_textures(ppk_path):
    pd = open(ppk_path, 'rb').read()
    pk, ups = tx.find_uploads(pd)
    tex0s = tx.find_tex0s(pd)
    def pick_img(t):
        iw = t['TBW']*64
        for u in sorted([u for u in ups if u['dbp']==t['TBP0']], key=lambda u:-u['bytes']):
            if t['PSM']==19 and u['bytes'] % iw == 0:
                ih = u['bytes']//iw
                mx = max(tx.psmt8_addr(x,y,t['TBW']) for y in (0,ih-1) for x in (0,iw-1))
                if (mx>>2) < u['trx_w']*u['trx_h']: return u
            if t['PSM']==20 and (u['bytes']*2) % iw == 0: return u
        return None
    def pick_clut(t):
        need = 1024 if t['PSM']==19 else 64
        cands = [u for u in ups if u['dbp']==t['CBP']]
        for u in cands:
            if u['bytes']==need: return u
        return cands[0] if cands else None
    pairs = []
    for t in tex0s:
        im, cl = pick_img(t), pick_clut(t)
        if im and cl: pairs.append((t, im, cl))
    base, score = tx.discover_base(pd, [(c['src_ref'], c['bytes']) for _,_,c in pairs])
    out = []  # (tex_index_in_pairs, tex0, rgba_bytes, w, h, arr)
    pngs = {}
    for k,(t,im,cl) in enumerate(pairs):
        try:
            iw, ih, rgba = tx.decode(pd, base, im, t, cl)
        except Exception:
            out.append(None); continue
        arr = np.frombuffer(rgba, dtype=np.uint8).reshape(ih, iw, 4).astype(np.float64)
        out.append({'k': k, 'tex0': t, 'w': iw, 'h': ih, 'rgba': rgba, 'arr': arr})
    return out, base, score

def main():
    glb_in, ppk, glb_out, assign_out = sys.argv[1:5]
    j, bin_ = load_glb(glb_in)
    prim = j['meshes'][0]['primitives'][0]
    pos = acc_data(j, bin_, prim['attributes']['POSITION']).astype(np.float64)
    uv = acc_data(j, bin_, prim['attributes']['TEXCOORD_0']).astype(np.float64)
    idx = acc_data(j, bin_, prim['indices']).reshape(-1, 3).astype(np.int64)
    texs, base, bscore = decode_textures(ppk)
    good = [t for t in texs if t]
    print(f'textures decoded: {len(good)}/{len(texs)} base={hex(base)} score={bscore:.3f}')

    # components
    parent = list(range(len(pos)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b, c in idx:
        for x, y in ((a,b),(b,c)):
            ra, rb = find(int(x)), find(int(y))
            if ra != rb: parent[ra] = rb
    from collections import defaultdict
    comp_faces = defaultdict(list)
    for f, (a, b, c) in enumerate(idx):
        comp_faces[find(int(a))].append(f)
    comps = sorted(comp_faces.values(), key=lambda fs: min(int(v) for f in fs for v in idx[f]))

    def sample(arr, uvs):
        ih, iw = arr.shape[:2]
        x = (np.mod(uvs[:,0],1.0)*iw).astype(int) % iw
        y = (np.mod(uvs[:,1],1.0)*ih).astype(int) % ih
        return arr[y, x, :3]

    # per-component scores
    comp_best = []
    for faces in comps:
        es = set()
        for f in faces:
            a, b, c = (int(v) for v in idx[f])
            for x, y in ((a,b),(b,c),(c,a)): es.add((min(x,y), max(x,y)))
        es = np.array(sorted(es))
        scores = []
        for t in good:
            col = sample(t['arr'], uv)
            scores.append((float(np.abs(col[es[:,0]]-col[es[:,1]]).mean()), t['k']))
        scores.sort()
        comp_best.append(scores)
    # smoothing: majority vote in sliding window of 15 components (by index order)
    assign = {}
    W = 15
    for ci in range(len(comps)):
        lo, hi = max(0, ci-W//2), min(len(comps), ci+W//2+1)
        votes = defaultdict(float)
        for cj in range(lo, hi):
            s = comp_best[cj]
            if s: votes[s[0][1]] += 1.0 / (1.0 + s[0][0])
        if not votes: continue
        best_k = max(votes, key=votes.get)
        # own score check: component's own best must not strongly disagree
        own = comp_best[ci]
        assign[ci] = best_k
    face_tex = {}
    for ci, faces in enumerate(comps):
        for f in faces: face_tex[f] = assign.get(ci)
    from collections import Counter
    print('face texture histogram:', Counter(face_tex.values()))

    # ---- rebuild GLB ----
    # new binary: original bin + PNG data + new index arrays
    newbin = bytearray(bin_)
    def pad4():
        while len(newbin) % 4: newbin.append(0)
    # PNG bytes for each good texture (regenerate via tx.write_png to temp)
    import os, tempfile
    png_views = {}
    for t in good:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tf:
            tmp = tf.name
        tx.write_png(tmp, t['w'], t['h'], t['rgba'])
        data = open(tmp, 'rb').read(); os.unlink(tmp)
        pad4()
        off = len(newbin); newbin += data
        j['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data)})
        png_views[t['k']] = len(j['bufferViews'])-1
    # images/textures/materials
    j['images'] = []; j['textures'] = []
    j.setdefault('samplers', [{'magFilter': 9729, 'minFilter': 9729, 'wrapS': 10497, 'wrapT': 10497}])
    mat_of = {}
    for t in good:
        ii = len(j['images'])
        j['images'].append({'bufferView': png_views[t['k']], 'mimeType': 'image/png',
                            'name': f"tex{t['k']:02d}_tbp{t['tex0']['TBP0']}"})
        j['textures'].append({'sampler': 0, 'source': ii})
        mat_of[t['k']] = len(j.get('materials', []))
        j.setdefault('materials', []).append({
            'name': f"tex{t['k']:02d}_tbp{t['tex0']['TBP0']}_psm{t['tex0']['PSM']}",
            'pbrMetallicRoughness': {'baseColorTexture': {'index': ii}, 'metallicFactor': 0.0, 'roughnessFactor': 1.0}})
    # group faces
    groups = defaultdict(list)
    for f in range(len(idx)):
        groups[face_tex[f]].append(f)
    new_prims = []
    for k in sorted(groups, key=lambda x: (x is None, x)):
        faces = groups[k]
        sub = idx[faces].ravel().astype(np.uint32)
        pad4()
        off = len(newbin); raw = sub.tobytes(); newbin += raw
        j['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(raw), 'target': 34963})
        ai = len(j['accessors'])
        j['accessors'].append({'bufferView': len(j['bufferViews'])-1, 'componentType': 5125,
                                'count': len(sub), 'type': 'SCALAR'})
        p = {'attributes': prim['attributes'], 'indices': ai, 'mode': 4}
        if k is not None: p['material'] = mat_of[k]
        new_prims.append(p)
    j['meshes'][0]['primitives'] = new_prims
    j['buffers'][0]['byteLength'] = len(newbin)
    js = json.dumps(j).encode()
    while len(js) % 4: js += b' '
    out = b'glTF' + struct.pack('<II', 2, 12 + 8 + len(js) + 8 + len(newbin))
    out += struct.pack('<I', len(js)) + b'JSON' + js
    out += struct.pack('<I', len(newbin)) + b'BIN\x00' + bytes(newbin)
    open(glb_out, 'wb').write(out)
    json.dump({'base': hex(base), 'base_score': bscore,
               'face_tex': {str(k): len(v) for k, v in groups.items()}},
              open(assign_out, 'w'), indent=1)
    print('wrote', glb_out, len(out), 'bytes; prims', len(new_prims), 'images', len(j['images']))

if __name__ == '__main__':
    main()
