#!/usr/bin/env python3
"""Minimal ISO9660 extractor for raw PS1 .bin (2352-byte Mode-2 sectors).
Handles Mode2/Form1 (data @ +24, 2048B) and plain 2048B sectors.
Usage: iso9660_extract.py <image.bin> <outdir> [--list-only]
"""
import os, sys, struct

SECTOR = 2352
DATA_OFF = 24
DATA_LEN = 2048

def read_sector(f, n):
    f.seek(n * SECTOR)
    raw = f.read(SECTOR)
    if len(raw) < SECTOR:
        return None
    # detect mode: check sync pattern
    if raw[0:12] == b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00':
        mode = raw[15]
        if mode == 2:
            return raw[DATA_OFF:DATA_OFF + DATA_LEN]
        return raw[:DATA_LEN]
    return raw[:DATA_LEN]  # assume 2048-byte sectors

def both_endian(b):
    return struct.unpack('<I', b[:4])[0]

def parse_dir_record(b):
    if len(b) < 34 or b[0] == 0:
        return None
    ln = b[0]
    extent = both_endian(b[2:10])
    size = both_endian(b[10:18])
    flags = b[25]
    fn_len = b[32]
    name = b[33:33+fn_len]
    return {'len': ln, 'extent': extent, 'size': size, 'flags': flags, 'name': name}

def list_dir(f, extent, size):
    entries = []
    sec = extent
    remaining = size
    buf = b''
    while remaining > 0:
        d = read_sector(f, sec)
        if d is None: break
        buf += d
        sec += 1
        remaining -= DATA_LEN
    off = 0
    while off < len(buf):
        if off + 34 > len(buf): break
        ln = buf[off]
        if ln == 0:
            # pad to next sector
            off = ((off // DATA_LEN) + 1) * DATA_LEN
            continue
        rec = parse_dir_record(buf[off:off+ln])
        if rec: entries.append(rec)
        off += ln
    return entries

def clean_name(raw):
    # strip version ;1 and handle \x00/\x01 for . and ..
    if raw == b'\x00': return '.'
    if raw == b'\x01': return '..'
    s = raw.split(b';')[0]
    return s.decode('ascii', errors='replace').rstrip('.')

def extract(f, rec, outdir, prefix=''):
    name = clean_name(rec['name'])
    if name in ('.', '..'): return
    path = os.path.join(outdir, prefix, name)
    if rec['flags'] & 2:  # directory
        os.makedirs(path, exist_ok=True)
        for e in list_dir(f, rec['extent'], rec['size']):
            extract(f, e, outdir, os.path.join(prefix, name))
    else:
        os.makedirs(os.path.dirname(path) or outdir, exist_ok=True)
        with open(path, 'wb') as out:
            sec = rec['extent']; rem = rec['size']
            while rem > 0:
                d = read_sector(f, sec)
                if d is None: break
                chunk = d[:min(rem, DATA_LEN)]
                out.write(chunk)
                rem -= len(chunk); sec += 1

def main():
    img, outdir = sys.argv[1], sys.argv[2]
    list_only = '--list-only' in sys.argv
    with open(img, 'rb') as f:
        pvd = read_sector(f, 16)
        if pvd[1:6] != b'CD001':
            print('Not an ISO9660 image (no CD001 at sector 16)'); sys.exit(1)
        vol_id = pvd[40:72].decode('ascii', errors='replace').strip()
        print('Volume:', vol_id)
        root = parse_dir_record(pvd[156:156+34])
        entries = list_dir(f, root['extent'], root['size'])
        print(f'Root entries: {len(entries)}')
        if list_only:
            def show(es, pre=''):
                for e in es:
                    n = clean_name(e['name'])
                    if n in ('.', '..'): continue
                    print(f"{pre}{n}  [{e['size']}B]{'/' if e['flags']&2 else ''}")
                    if e['flags'] & 2:
                        show(list_dir(f, e['extent'], e['size']), pre + '  ')
            show(entries)
        else:
            os.makedirs(outdir, exist_ok=True)
            for e in entries:
                extract(f, e, outdir)
            print('Extraction complete ->', outdir)

if __name__ == '__main__':
    main()
