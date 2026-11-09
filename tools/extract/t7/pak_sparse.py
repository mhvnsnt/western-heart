#!/usr/bin/env python3
"""tools/extract/t7/pak_sparse.py - read a split UE4 .pak straight from a GitHub release, fetching only what is needed.

Why (2026-11-09): the Tekken 7 game files (release `tekken7-gamefiles-v1`, from the owner's Steam copy) include
pakchunk0-WindowsNoEditor.pak, 20.1 GB in 43 parts: every character's skeletal meshes with Namco's skeleton and skin
weights. The cloud containers have about 8 GB of disk. A UE4 pak keeps its file index at the END and every file at a
recorded offset, so this tool:

1. builds a SPARSE file of the pak's full size;
2. fetches the footer and the index with HTTP Range requests, mapping absolute offsets onto the release parts;
3. fetches only the entries you ask for (each entry's header plus its data) into their own offsets.

UE Viewer (umodel, teardown/tekken7/tools/umodel_linux, -game=tekken7) then reads the sparse pak as if it were whole.
Only the fetched bytes take disk space.

    python3 tools/extract/t7/pak_sparse.py index --release URL --pak NAME --out SPARSE.pak --json index.json
    python3 tools/extract/t7/pak_sparse.py fetch  --release URL --pak NAME --out SPARSE.pak --json index.json --match REGEX
    python3 tools/extract/t7/pak_sparse.py probe  --release URL --pak NAME     # parse the first entry header (part 00)

URL is the release download base, e.g. https://github.com/mhvnsnt/western-heart/releases/download/tekken7-gamefiles-v1.
NAME is the pak file name; parts are NAME.part-00, -01, ... (sizes read from the release API, or --part-size).
Format: UE4 FPakInfo / FPakEntry, pak versions 1-9 (Tekken 7 is UE 4.14). Raw game bytes are never committed.
"""
import argparse
import json
import os
import re
import struct
import sys
import urllib.request

MAGIC = 0x5A6F12E1


def http_range(url, start, end_incl, tries=4):
    req = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end_incl}', 'User-Agent': 'wh-pak-sparse'})
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) != end_incl - start + 1:
                raise IOError(f'short read {len(data)} of {end_incl - start + 1}')
            return data
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
    raise last


class Parts:
    """Absolute pak offset -> (part url, offset in part)."""

    def __init__(self, base, name, sizes):
        self.urls = [f'{base}/{name}.part-{i:02d}' for i in range(len(sizes))]
        self.sizes = sizes
        self.starts = [sum(sizes[:i]) for i in range(len(sizes))]
        self.total = sum(sizes)

    def read(self, off, n):
        out = bytearray()
        while n > 0:
            i = max(k for k, s in enumerate(self.starts) if s <= off)
            inpart = off - self.starts[i]
            take = min(n, self.sizes[i] - inpart)
            out += http_range(self.urls[i], inpart, inpart + take - 1)
            off += take
            n -= take
        return bytes(out)


def release_part_sizes(base, name):
    m = re.match(r'https://github.com/([^/]+)/([^/]+)/releases/download/([^/]+)$', base)
    if not m:
        sys.exit('pass --part-size and --parts for a non-GitHub base URL')
    owner, repo, tag = m.groups()
    api = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}'
    with urllib.request.urlopen(urllib.request.Request(api, headers={'User-Agent': 'wh-pak-sparse'}), timeout=60) as r:
        rel = json.load(r)
    parts = {}
    for a in rel['assets']:
        mm = re.match(re.escape(name) + r'\.part-(\d+)$', a['name'])
        if mm:
            parts[int(mm.group(1))] = a['size']
    if not parts:
        sys.exit(f'no parts of {name} in {tag}')
    n = max(parts) + 1
    missing = [i for i in range(n) if i not in parts]
    if missing:
        sys.exit(f'{name}: parts not uploaded yet: {missing[:10]}{"..." if len(missing) > 10 else ""}')
    return [parts[i] for i in range(n)]


class Rd:
    def __init__(self, b, o=0):
        self.b, self.o = b, o

    def u8(self):
        self.o += 1
        return self.b[self.o - 1]

    def i32(self):
        self.o += 4
        return struct.unpack_from('<i', self.b, self.o - 4)[0]

    def u32(self):
        self.o += 4
        return struct.unpack_from('<I', self.b, self.o - 4)[0]

    def i64(self):
        self.o += 8
        return struct.unpack_from('<q', self.b, self.o - 8)[0]

    def raw(self, n):
        self.o += n
        return self.b[self.o - n:self.o]

    def fstring(self):
        n = self.i32()
        if n == 0:
            return ''
        if n > 0:
            s = self.raw(n)
            return s[:-1].decode('latin1')
        s = self.raw(-n * 2)
        return s[:-2].decode('utf-16-le')


def parse_entry(r, version):
    """FPakEntry (versions 1-9). Returns a dict and leaves r after it."""
    e = {'offset': r.i64(), 'size': r.i64(), 'usize': r.i64(), 'comp': r.i32()}
    if version <= 1:
        r.i64()  # timestamp
    r.raw(20)  # sha1
    if version >= 3:
        if e['comp'] != 0:
            n = r.i32()
            e['blocks'] = [(r.i64(), r.i64()) for _ in range(n)]
        e['encrypted'] = r.u8()
        e['block_size'] = r.u32()
    return e


def entry_header_size(e, version):
    n = 8 + 8 + 8 + 4 + (8 if version <= 1 else 0) + 20
    if version >= 3:
        if e['comp'] != 0:
            n += 4 + 16 * len(e.get('blocks', []))
        n += 1 + 4
    return n


def find_footer(tail):
    for k in range(len(tail) - 44, -1, -1):
        if struct.unpack_from('<I', tail, k)[0] == MAGIC:
            version, off, size = struct.unpack_from('<iqq', tail, k + 4)
            if 1 <= version <= 11 and off > 0 and size > 0:
                return version, off, size
    sys.exit('pak footer magic not found in the last bytes')


def sparse_write(path, total, off, data):
    mode = 'r+b' if os.path.exists(path) else 'w+b'
    with open(path, mode) as f:
        if mode == 'w+b':
            f.truncate(total)
        f.seek(off)
        f.write(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['index', 'fetch', 'probe'])
    ap.add_argument('--release', required=True)
    ap.add_argument('--pak', required=True)
    ap.add_argument('--out')
    ap.add_argument('--json')
    ap.add_argument('--match', help='regex over entry file names (fetch)')
    a = ap.parse_args()
    if a.cmd == 'probe':
        head = http_range(f'{a.release}/{a.pak}.part-00', 0, 4095)
        for v in (3, 4, 5, 7, 8):
            try:
                e = parse_entry(Rd(head), v)
                print('as version', v, {k: e[k] for k in ('offset', 'size', 'usize', 'comp')},
                      'encrypted', e.get('encrypted'), 'block_size', e.get('block_size'),
                      'blocks', len(e.get('blocks', [])))
            except Exception as ex:  # noqa: BLE001 - diagnostic
                print('as version', v, 'unparseable:', ex)
        return
    sizes = release_part_sizes(a.release, a.pak)
    P = Parts(a.release, a.pak, sizes)
    if a.cmd == 'index':
        tail = P.read(P.total - 256, 256)
        version, ioff, isize = find_footer(tail)
        print(f'pak {a.pak}: {P.total} bytes in {len(sizes)} parts, version {version}, index at {ioff} ({isize} bytes)')
        idx = P.read(ioff, isize)
        r = Rd(idx)
        mount = r.fstring()
        n = r.i32()
        entries = []
        for _ in range(n):
            name = r.fstring()
            e = parse_entry(r, version)
            e['name'] = name
            e['hdr'] = entry_header_size(e, version)
            entries.append(e)
        if a.out:
            sparse_write(a.out, P.total, P.total - 256, tail)
            sparse_write(a.out, P.total, ioff, idx)
        json.dump({'pak': a.pak, 'total': P.total, 'version': version, 'mount': mount, 'index_offset': ioff,
                   'index_size': isize, 'entries': [{k: e[k] for k in ('name', 'offset', 'size', 'usize', 'comp', 'hdr')}
                                                     for e in entries]}, open(a.json, 'w'))
        print(f'mount {mount!r}, {n} entries -> {a.json}')
        return
    idx = json.load(open(a.json))
    rx = re.compile(a.match, re.I)
    want = [e for e in idx['entries'] if rx.search(e['name'])]
    total_bytes = sum(e['hdr'] + e['size'] for e in want)
    print(f'{len(want)} entries match, {total_bytes / 1e6:.1f} MB to fetch')
    for e in want:
        data = P.read(e['offset'], e['hdr'] + e['size'])
        sparse_write(a.out, idx['total'], e['offset'], data)
        print(f'  {e["name"]}  {e["size"]} B')


if __name__ == '__main__':
    main()
