"""W7e driver: reproduce T5 costume packs from the tekken5-disc-v1 release by
HTTP Range (no full-disc download), verify each pack against the E5 word-sum
checksum (raw or LCG-XOR decrypt, FileTableGetPS2 method as W7b), split
sub01 TIM2 / sub02 NUDP, convert sub02 -> OBJ (ModelMagic) and decode only the
TIM2 pictures the model's materials reference (tim2dump). Blender GLB step is
separate (blender_batch.py). Resumable via /var/tmp/w7e/manifest.json +
staging GLB presence. Usage: fetch_convert.py BATCH_START BATCH_COUNT
"""
import struct, sys, os, json, subprocess, urllib.request, hashlib
import numpy as np

E5 = open('/home/hatch/workspace/tk5-lanes/e5e6/out/E5_dec.bin', 'rb').read()
TS, CS = 0x27B5B0, 0x27E838
PART = 500_000_000
ASSETS = {0: 660170147 + 0}  # filled below by part index
ASSETS = {0: None, 1: 660239719, 2: 660245217}
# part_00 asset id resolved at runtime if ever needed (packs live in parts 1-2)
import os as _os
W7E_DIR = _os.environ.get('W7E_DIR', '/var/tmp/w7e')
SCRATCH = os.path.join(W7E_DIR, 'batch')
MANIFEST = os.path.join(W7E_DIR, 'manifest.json')
TOOLS = '/home/hatch/workspace/_w7e-stage/tools'
TIM2DUMP = '/home/hatch/workspace/tk5-lanes/research/dl/tim2dump/build/tim2dump'

sys.path.insert(0, TOOLS)
from nudp2obj_uv import convert

token = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
_redirects = {}
def asset_url(asset_id):
    if asset_id not in _redirects:
        req = urllib.request.Request(
            f'https://api.github.com/repos/mhvnsnt/game-reverse-engineering/releases/assets/{asset_id}',
            headers={'Authorization': f'Bearer {token}', 'Accept': 'application/octet-stream'})
        class NoRedir(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a): return None
        try:
            urllib.request.build_opener(NoRedir).open(req)
        except urllib.error.HTTPError as e:
            _redirects[asset_id] = e.headers['Location']
    return _redirects[asset_id]

def fetch_range(asset_id, start, length):
    req = urllib.request.Request(asset_url(asset_id), headers={'Range': f'bytes={start}-{start + length - 1}'})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    assert len(data) == length, f'range short read {len(data)}/{length}'
    return data

def fetch_pack(idx):
    sec, size = struct.unpack_from('<II', E5, TS + idx * 8)
    glob = sec * 2048
    out = bytearray(); pos = glob; end = glob + size
    while pos < end:
        part = pos // PART; local = pos - part * PART
        n = min(end - pos, PART - local)
        out += fetch_range(ASSETS[part], local, n)
        pos += n
    return bytes(out)

def wsum(data, size):
    arr = np.frombuffer(data[:(size // 4) * 4], dtype='<u4')
    acc = int(arr.sum(dtype=np.uint64)) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

def decrypt(data, seed, size):
    ks = np.empty(512, dtype='<u4'); key = seed & 0xFFFFFFFF
    for j in range(512): ks[j] = key; key = (key * 5 + 3) & 0xFFFFFFFF
    out = np.frombuffer(data[:(len(data) // 4) * 4], dtype='<u4').copy()
    nfull = (size >> 11) * 512
    if nfull: out[:nfull] ^= np.tile(ks, nfull // 512)
    rem = ((size & 0x7FF) + 3) >> 2
    if rem: out[nfull:nfull + rem] ^= ks[:rem]
    return out.tobytes()[:size]

def main():
    start, count = int(sys.argv[1]), int(sys.argv[2])
    packs = json.load(open(os.path.join(W7E_DIR, 'pack_indices.json')))
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    jobs = []
    for idx in packs[start:start + count]:
        key = str(idx)
        if man.get(key, {}).get('stage') == 'obj':
            jobs.append(man[key]['job']); continue
        if man.get(key, {}).get('stage') == 'glb_ok':
            continue
        os.makedirs(SCRATCH, exist_ok=True)
        pdir = os.path.join(SCRATCH, f'p{idx}')
        os.makedirs(pdir, exist_ok=True)
        data = fetch_pack(idx)
        sec, size = struct.unpack_from('<II', E5, TS + idx * 8)
        chk = struct.unpack_from('<I', E5, CS + idx * 4)[0]
        kind = 'raw'
        if wsum(data, size) != chk:
            data = decrypt(data, idx, size); kind = 'decrypted'
            assert wsum(data, size) == chk, f'checksum FAIL pack {idx}'
        cnt, _ = struct.unpack_from('<II', data, 0)
        assert cnt == 19, f'pack {idx} count {cnt}'
        subs = {}
        for s in range(cnt):
            off, sz = struct.unpack_from('<II', data, 4 + s * 8)
            subs[s] = data[off:off + sz]
        assert subs[1][:4] == b'TIM2' and subs[2][:4] == b'NUDP', f'pack {idx} sub magics'
        nudp_path = os.path.join(pdir, 'costume.nudp')
        tm2_path = os.path.join(pdir, 'textures.tm2')
        open(nudp_path, 'wb').write(subs[2]); open(tm2_path, 'wb').write(subs[1])
        info = convert(nudp_path, os.path.join(pdir, 'costume.obj'))
        # decode only referenced TIM2 pictures; a referenced index that does
        # not exist in this pack's TIM2 is logged as missing (pack 1109's
        # sub01 is a 192-byte placeholder: 1 picture, model references #4)
        mtl = []
        missing = []
        for ti in info['tex_indices']:
            sub = os.path.join(pdir, f't{ti}'); os.makedirs(sub, exist_ok=True)
            r = subprocess.run([TIM2DUMP, 'export', tm2_path, 'png', '-p', str(ti)],
                               cwd=sub, capture_output=True, text=True)
            src_png = os.path.join(sub, 'textures.png')
            if not os.path.exists(src_png):
                missing.append(ti)
                mtl.append(f'newmtl tex{ti:03d}\nKd 0.8 0.8 0.8\n')
                continue
            os.rename(src_png, os.path.join(pdir, f'tex{ti:03d}.png'))
            mtl.append(f'newmtl tex{ti:03d}\nKd 1 1 1\nmap_Kd tex{ti:03d}.png\n')
        info['missing_tex_indices'] = missing
        open(os.path.join(pdir, 'costume.mtl'), 'w').write('\n'.join(mtl))
        obj = open(os.path.join(pdir, 'costume.obj')).read()
        open(os.path.join(pdir, 'costume_tex.obj'), 'w').write('mtllib costume.mtl\n' + obj)
        job = {'obj': os.path.join(pdir, 'costume_tex.obj'),
               'glb': os.path.join(pdir, f'pack{idx:04d}-costume.glb'), 'idx': idx}
        man[key] = {'stage': 'obj', 'checksum': kind, 'pack_size': size,
                    'sub01_size': len(subs[1]), 'sub02_size': len(subs[2]),
                    'sub02_sha256': hashlib.sha256(subs[2]).hexdigest(),
                    'sub01_sha256': hashlib.sha256(subs[1]).hexdigest(),
                    **info, 'job': job}
        jobs.append(job)
        json.dump(man, open(MANIFEST, 'w'), indent=1)
        print('PREPED', idx, kind, info, flush=True)
    json.dump(jobs, open(os.path.join(W7E_DIR, 'jobs.json'), 'w'), indent=1)
    print('JOBS', len(jobs))

if __name__ == '__main__':
    main()
