#!/usr/bin/env python3
"""Phase 14 Job 3 (local variant): compare mirror AFS members from
LOCAL tar part files vs ISO-side bytes in the assembled ISO.
Tar stream = p02/part-02 + mirrorparts/part-03 + part-04 + part-05
(concatenated in order). Reads only each member's byte range.
Usage: prov_local.py OUT.json name [name ...]"""
import hashlib, json, os, sys
PARTS = [
    '/home/hatch/workspace/_doa4p2-scratch/p14/mirrorparts/p02/doa4-mirror-extracted-20261017.tar.part-02',
    '/home/hatch/workspace/_doa4p2-scratch/p14/mirrorparts/doa4-mirror-extracted-20261017.tar.part-03',
    '/home/hatch/workspace/_doa4p2-scratch/p14/mirrorparts/doa4-mirror-extracted-20261017.tar.part-04',
    '/home/hatch/workspace/_doa4p2-scratch/p14/mirrorparts/doa4-mirror-extracted-20261017.tar.part-05',
]
PART = 524288000
BASE = 2 * PART  # tar offset where part-02 begins
ISO = '/home/hatch/workspace/_doa4p2-scratch/p13/doa4.iso'
TREE = '/home/hatch/workspace/_doa4p2-scratch/p13/xdvdfs_tree_full.json'
MIRROR = {'chrone.afs': (1212324864, 366094336), 'chrtwo.afs': (1578419712, 548042752),
          'chrthree.afs': (2135433728, 762955776), 'anm.afs': (2898390016, 2949120)}
CH = 1 << 22

def tread(goff, n):
    out = bytearray()
    while n > 0:
        rel = goff - BASE
        pi = rel // PART; lo = rel % PART
        take = min(n, PART - lo)
        with open(PARTS[pi], 'rb') as f:
            f.seek(lo); b = f.read(take)
        assert len(b) == take, (PARTS[pi], lo, take, len(b))
        out += b; goff += take; n -= take
    return bytes(out)

def main():
    out_path, names = sys.argv[1], sys.argv[2:]
    tree = {e['path']: e for e in json.load(open(TREE))['entries']}
    res = json.load(open(out_path)) if os.path.exists(out_path) else {}
    iso = open(ISO, 'rb')
    for name in names:
        moff, msize = MIRROR[name]
        hdr = tread(moff - 512, 512)
        tname = hdr[:100].split(b'\x00')[0].decode()
        tsize = int(hdr[124:136].split(b'\x00')[0].strip() or b'0', 8)
        e = tree[name]; n = min(tsize, e['size'])
        mh, ih = hashlib.sha256(), hashlib.sha256()
        first_diff = None; same = 0; done = 0
        while done < n:
            take = min(CH, n - done)
            mb = tread(moff + done, take)
            iso.seek(e['iso_offset'] + done); ib = iso.read(take)
            assert len(ib) == take
            mh.update(mb); ih.update(ib)
            if mb != ib:
                for i in range(take):
                    if mb[i] != ib[i]:
                        if first_diff is None: first_diff = done + i
                    else: same += 1
            else: same += take
            done += take
            print(f'{name}: {done}/{n}', flush=True)
        res[name] = {'tar_member_name': tname, 'mirror_size': tsize, 'iso_size': e['size'],
                     'mirror_sha256': mh.hexdigest(), 'iso_sha256': ih.hexdigest(),
                     'verdict': 'IDENTICAL' if (tsize == e['size'] and first_diff is None) else 'DIFFERENT',
                     'first_diff_offset': first_diff, 'identical_bytes': same,
                     'compared_bytes': n, 'pct_identical': round(100.0 * same / n, 4) if n else 100.0}
        json.dump(res, open(out_path, 'w'), indent=1)
        print(name, res[name], flush=True)
    print('WROTE', out_path)

if __name__ == '__main__':
    main()
