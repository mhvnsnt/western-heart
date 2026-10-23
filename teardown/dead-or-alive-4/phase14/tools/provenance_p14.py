#!/usr/bin/env python3
"""DOA4 phase 14 Job 3: mirror-vs-ISO provenance pass.

Byte-compares the four AFS members of the mirror tar (release
doa4-mirror-20261017, extracted-tar parts; member data offsets from
the phase-6 map) against the same-named files extracted from the
assembled ISO (XDVDFS tree: phase13/xdvdfs_tree_full.json; ISO-side
bytes read from the sparse assembly, whose landed parts were each
sha256-verified against release doa4-iso-v1 before writing).

Per file: tar-header name+size (read from the 512 B ustar header
immediately before the member data), ISO size, mirror sha256,
ISO sha256, verdict IDENTICAL/DIFFERENT, and for DIFFERENT files
the first differing byte offset + count of identical bytes
(byte-wise over the common length).

Mirror bytes are range-fetched with the phase-6 fetch tool
(tools/phase6/fetch.py). ISO bytes are read locally. Comparison is
chunk-wise (4 MiB) so no full copy of either side is materialized.

Usage: provenance_p14.py OUT.json [name ...]
"""
import hashlib, json, os, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/tools/phase6')
from fetch import fetch  # phase-6 range fetch (proven)

ISO = '/home/hatch/workspace/_doa4p2-scratch/p13/doa4.iso'
TREE = '/home/hatch/workspace/_doa4p2-scratch/p13/xdvdfs_tree_full.json'
MIRROR = {  # phase-6 tar member data offsets + expected sizes
    'chrone.afs':   (1212324864, 366094336),
    'chrtwo.afs':   (1578419712, 548042752),
    'chrthree.afs': (2135433728, 762955776),
    'anm.afs':      (2898390016, 2949120),
}
CH = 1 << 22


def tar_header(goff):
    h = fetch(goff - 512, 512)
    name = h[:100].split(b'\x00')[0].decode()
    size = int(h[124:136].split(b'\x00')[0].strip() or b'0', 8)
    return name, size


def main():
    out_path = sys.argv[1]
    names = sys.argv[2:] or list(MIRROR)
    tree = {e['path']: e for e in json.load(open(TREE))['entries']}
    res = json.load(open(out_path)) if os.path.exists(out_path) else {}
    iso = open(ISO, 'rb')
    for name in names:
        moff, msize_exp = MIRROR[name]
        tname, tsize = tar_header(moff)
        e = tree[name]
        isize = e['size']
        n = min(tsize, isize)
        mh, ih = hashlib.sha256(), hashlib.sha256()
        first_diff = None
        same_bytes = 0
        done = 0
        while done < n:
            take = min(CH, n - done)
            mb = fetch(moff + done, take)
            iso.seek(e['iso_offset'] + done)
            ib = iso.read(take)
            assert len(mb) == take and len(ib) == take
            mh.update(mb); ih.update(ib)
            if mb != ib:
                for i in range(take):
                    if mb[i] != ib[i]:
                        if first_diff is None:
                            first_diff = done + i
                    else:
                        same_bytes += 1
            else:
                same_bytes += take
            done += take
            print(f'{name}: {done}/{n}', flush=True)
        # tail beyond common length (sizes differ case)
        verdict = 'IDENTICAL' if (tsize == isize and first_diff is None) else 'DIFFERENT'
        res[name] = {
            'tar_member_name': tname, 'mirror_size': tsize,
            'mirror_size_expected': msize_exp, 'iso_size': isize,
            'mirror_sha256': mh.hexdigest(), 'iso_sha256': ih.hexdigest(),
            'verdict': verdict, 'first_diff_offset': first_diff,
            'identical_bytes': same_bytes, 'compared_bytes': n,
            'pct_identical': round(100.0 * same_bytes / n, 4) if n else 100.0,
        }
        json.dump(res, open(out_path, 'w'), indent=1)
        print(name, res[name], flush=True)
    print('WROTE', out_path)


if __name__ == '__main__':
    main()
