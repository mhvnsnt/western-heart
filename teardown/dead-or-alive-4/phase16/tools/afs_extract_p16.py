#!/usr/bin/env python3
"""DOA4 phase 16 Job 3 (p15 tool, p16 paths): parse the ISO's chrone/chrtwo/chrthree/mot/cmn
AFS containers from the VERIFIED assembled ISO and extract every
named entry to p15 scratch. AFS layout (proven phases 13-14):
magic 'AFS\\0', u32LE count, count x (u32LE offset, u32LE size),
then (attr_offset, attr_size); attribute block = count x 48B records
(32B name + date fields). Extraction asserts each entry span is
inside the container and records sha256 per entry.
Refuses to run unless the whole-ISO sha256 file in p15 matches the
phase-14 closeout value (the ISO must be verified before any byte
is trusted)."""
import hashlib, json, os, struct, sys

SCR = '/home/hatch/workspace/_doa4p16-scratch'
ISO = os.path.join(SCR, 'doa4.iso')
TREE = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase13/xdvdfs_tree_full.json'
EXPECTED_WHOLE = '4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa'
OUT = os.path.join(SCR, 'afs_extract')
CH = 1 << 22

def sha256_bytes_stream(f, off, n):
    h = hashlib.sha256(); f.seek(off); left = n
    while left > 0:
        b = f.read(min(CH, left))
        assert b, 'short read'
        h.update(b); left -= len(b)
    return h.hexdigest()

def parse_afs(f, base, size):
    f.seek(base); hdr = f.read(8)
    assert hdr[:4] == b'AFS\x00', hdr[:8]
    cnt = struct.unpack('<I', hdr[4:8])[0]
    f.seek(base + 8); raw = f.read(cnt * 8 + 8)
    ents = [struct.unpack_from('<II', raw, i * 8) for i in range(cnt)]
    ao, asz = struct.unpack_from('<II', raw, cnt * 8)
    names = []
    if ao and asz >= cnt * 48:
        f.seek(base + ao); ab = f.read(cnt * 48)
        for i in range(cnt):
            nm = ab[i * 48:i * 48 + 32].split(b'\x00')[0].decode('ascii', 'replace')
            names.append(nm)
    else:
        names = [''] * cnt
    out = []
    for i, (off, sz) in enumerate(ents):
        assert off + sz <= size, (i, off, sz, size)
        out.append({'index': i, 'name': names[i], 'offset': off, 'size': sz})
    return {'count': cnt, 'attr_offset': ao, 'attr_size': asz, 'entries': out}

def main():
    whole = open(os.path.join(SCR, 'whole_iso_sha256.txt')).read().split()[0]
    assert whole == EXPECTED_WHOLE, ('ISO NOT VERIFIED', whole)
    tree = {e['path']: e for e in json.load(open(TREE))['entries']}
    os.makedirs(OUT, exist_ok=True)
    iso = open(ISO, 'rb')
    manifest = {}
    for name in ['chrone.afs', 'chrtwo.afs', 'chrthree.afs', 'mot.afs', 'cmn.afs']:
        e = tree[name]
        info = parse_afs(iso, e['iso_offset'], e['size'])
        info['container'] = {'iso_offset': e['iso_offset'], 'size': e['size'],
                             'sha256': sha256_bytes_stream(iso, e['iso_offset'], e['size'])}
        d = os.path.join(OUT, name.replace('.afs', ''))
        os.makedirs(d, exist_ok=True)
        for ent in info['entries']:
            ent['sha256'] = sha256_bytes_stream(iso, e['iso_offset'] + ent['offset'], ent['size'])
            if name.startswith('chr'):
                dst = os.path.join(d, ent['name'] or f"entry{ent['index']:03d}")
                with open(dst, 'wb') as o:
                    iso.seek(e['iso_offset'] + ent['offset']); left = ent['size']
                    while left > 0:
                        b = iso.read(min(CH, left)); o.write(b); left -= len(b)
        manifest[name] = info
        print(name, info['count'], 'entries; container sha256', info['container']['sha256'][:16],
              '; first', info['entries'][0]['name'], '; last', info['entries'][-1]['name'], flush=True)
        if name.startswith('chr'):
            v = [x for x in info['entries'] if x['name'].endswith('_version.bin')]
            for x in v:
                iso.seek(e['iso_offset'] + x['offset'])
                print('  ', x['name'], 'size', x['size'], 'bytes:', iso.read(x['size']).hex(), flush=True)
    json.dump(manifest, open(os.path.join(SCR, 'afs_manifest_p16.json'), 'w'), indent=1)
    print('WROTE afs_manifest_p16.json')

if __name__ == '__main__':
    main()
