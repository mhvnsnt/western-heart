"""W7d driver: reproduce the 9 ctype-5 containers of TK5DATA1.BIN from the
tekken5-disc-v1 release by HTTP Range (no full-disc download), verify each
against the E5 word-sum checksum (raw or LCG-XOR decrypt, FileTableGetPS2
method as W7b/W7e), split sub01 TIM2 / sub02 NUDP set, decode every NUDP
model with the VIF 0x82 decoder (vif082.py), decode TIM2 picture 0 with
tim2dump, and build the 8 unique-geometry GLBs (ctype5_glb.py).

Usage: fetch_decode_ctype5.py OUTDIR
Prints a JSON manifest: per unique model - source DATA1 files, NUDP
sha256, verts/tris, GLB size + sha256.
"""
import struct, sys, os, json, subprocess, urllib.request, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vif082 import decode_model          # noqa: E402
from ctype5_glb import write_glb         # noqa: E402

E5 = open('/home/hatch/workspace/tk5-lanes/e5e6/out/E5_dec.bin', 'rb').read()
TS, CS = 0x27B5B0, 0x27E838
PART = 500_000_000
ASSETS = {1: 660239719, 2: 660245217}   # TK5DATA1.BIN.part_01 / part_02
TIM2DUMP = '/home/hatch/workspace/tk5-lanes/research/dl/tim2dump/build/tim2dump'
FILES = [22, 687, 698, 753, 764, 1061, 1072, 1083, 1094]
# unique geometries: slug -> (representative nud path key, all source files)
UNIQUES = [
    ('ctype5-f0022-m0', (22, 0), [22]),
    ('ctype5-f0022-m1', (22, 1), [22]),
    ('ctype5-f0022-m2', (22, 2), [22]),
    ('ctype5-f0022-m3', (22, 3), [22]),
    ('ctype5-f0687-m0', (687, 0), [687, 698]),
    ('ctype5-f0753-m0', (753, 0), [753, 764]),
    ('ctype5-f1061-m0', (1061, 0), [1061, 1072, 1083, 1094]),
    ('ctype5-f1061-m1', (1061, 1), [1061, 1072, 1083, 1094]),
]

token = os.environ.get('GH_TOKEN') or subprocess.run(
    ['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
_redirects = {}


def asset_url(asset_id):
    if asset_id not in _redirects:
        req = urllib.request.Request(
            f'https://api.github.com/repos/mhvnsnt/game-reverse-engineering/releases/assets/{asset_id}',
            headers={'Authorization': f'Bearer {token}',
                     'Accept': 'application/octet-stream'})

        class NoRedir(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a):
                return None
        try:
            urllib.request.build_opener(NoRedir).open(req)
        except urllib.error.HTTPError as e:
            _redirects[asset_id] = e.headers['Location']
    return _redirects[asset_id]


def fetch_range(asset_id, start, length):
    req = urllib.request.Request(asset_url(asset_id),
                                 headers={'Range': f'bytes={start}-{start + length - 1}'})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    assert len(data) == length, f'range short read {len(data)}/{length}'
    return data


def decrypt(buf, seed, size):
    """tk5psp_crypt.decrypt_sector_data_fast (FileTableGetPS2 method)."""
    key = seed & 0xFFFFFFFF
    ks = []
    for _ in range(512):
        ks.append(key)
        key = (key * 5 + 3) & 0xFFFFFFFF
    ks_bytes = struct.pack('<512I', *ks)
    out = bytearray(buf)
    off = 0
    while off + 2048 <= size:
        chunk = int.from_bytes(out[off:off + 2048], 'little') ^ int.from_bytes(ks_bytes, 'little')
        out[off:off + 2048] = chunk.to_bytes(2048, 'little')
        off += 2048
    rem = ((size & 0x7FF) + 3) >> 2
    if rem:
        n = rem * 4
        chunk = int.from_bytes(out[off:off + n], 'little') ^ int.from_bytes(ks_bytes[:n], 'little')
        out[off:off + n] = chunk.to_bytes(n, 'little')
    return bytes(out)


def wordsum(data, size):
    n = size >> 2
    acc = sum(struct.unpack_from(f'<{n}I', data, 0)) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF


def fetch_container(idx):
    sec, size = struct.unpack_from('<II', E5, TS + idx * 8)
    glob = sec * 2048
    out = bytearray()
    pos, end = glob, glob + size
    while pos < end:
        part = pos // PART
        local = pos - part * PART
        take = min(end - pos, PART - local)
        out += fetch_range(ASSETS[part], local, take)
        pos += take
    want = struct.unpack_from('<I', E5, CS + idx * 4)[0]
    if wordsum(bytes(out), size) == want:
        return bytes(out), 'raw'
    dec = decrypt(bytes(out), idx, size)
    assert wordsum(dec, size) == want, f'checksum FAIL file {idx}'
    return dec, 'decrypted'


def split_sub(data, which):
    off, size = struct.unpack_from('<II', data, 4 + 8 * which)
    return data[off:off + size]


def inner_entries(sub):
    """(payload_offset, size) entries of an 80-byte-header sub-archive."""
    out = []
    p, cum = 8, 80
    while cum < len(sub):
        sz, end = struct.unpack_from('<II', sub, p)
        p += 8
        out.append((cum, sz))
        cum = end
    return out


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    work = os.path.join(outdir, '_work')
    os.makedirs(work, exist_ok=True)
    containers, tex_png = {}, {}
    for idx in FILES:
        data, how = fetch_container(idx)
        containers[idx] = data
        print(f'file {idx}: {len(data)} B checksum-verified ({how})', file=sys.stderr)
        tim2 = split_sub(data, 0)
        eo, es = inner_entries(tim2)[0]
        tpath = os.path.join(work, f'f{idx:04d}_tex0.tim2')
        open(tpath, 'wb').write(tim2[eo:eo + es])
        subprocess.run([TIM2DUMP, 'export', tpath, 'png', '-o', f'f{idx:04d}_tex0'],
                       check=True, capture_output=True, cwd=work)
        tex_png[idx] = open(os.path.join(work, f'f{idx:04d}_tex0_pic0.png'), 'rb').read()
    manifest = {}
    for slug, (fidx, midx), files in UNIQUES:
        nudp_set = split_sub(containers[fidx], 1)
        eo, es = inner_entries(nudp_set)[midx]
        nud_bytes = nudp_set[eo:eo + es]
        npath = os.path.join(work, slug + '.nudp')
        open(npath, 'wb').write(nud_bytes)
        _nud, subs = decode_model(npath)
        v, f = write_glb(os.path.join(outdir, slug + '.glb'), subs, tex_png[fidx])
        glb_bytes = open(os.path.join(outdir, slug + '.glb'), 'rb').read()
        manifest[slug] = {
            'data1_files': files, 'nudp_sha256': hashlib.sha256(nud_bytes).hexdigest(),
            'nudp_size': es, 'vif_blobs': len(subs), 'verts': v, 'tris': f,
            'glb_size': len(glb_bytes), 'glb_sha256': hashlib.sha256(glb_bytes).hexdigest(),
        }
        print(f'{slug}: {v} verts {f} tris', file=sys.stderr)
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
