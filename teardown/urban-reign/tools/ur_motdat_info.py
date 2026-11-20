#!/usr/bin/env python3
"""Urban Reign motdat .info parser — Job 3 (name mapping) evidence tool.

FORMAT (proven this attempt against all 10 held .info files; every file
satisfies the size formula EXACTLY):
  [u32 count N][N x u32 table][N x 60-byte records]
  total size = 4 + 64*N. Table entry k = k*60 (byte offset of record
  k's payload — verified: steps are uniformly 60, first entry 0).
  Record (60 B): [u32 index][32 B name, NUL-padded ASCII]
                 [20 B date string, space/NUL padded]
                 [4 B trailer: 00 01 02 03]
  The record index runs 0..N-1 sequentially in file order — the file's
  own ordering proof.

The parser VERIFIES: size formula, trailer pattern + sequential idx,
name printability. Anything failing verification is reported, not
silently parsed. It makes NO claim that list position = bank motion
index; that correlation needs the companion .bin records + pmotID
tables (see the Job-3 assessment doc).

Usage: ur_motdat_info.py <dir-with-.info-files> <out.json>
Stdlib only.
"""
import struct, sys, os, json, collections, hashlib

def parse(path):
    d = open(path, 'rb').read()
    R = {'file': os.path.basename(path), 'size': len(d),
         'sha256': hashlib.sha256(d).hexdigest()}
    if len(d) < 4:
        R['error'] = 'too small'; return R
    n = struct.unpack('<I', d[:4])[0]
    R['count_field'] = n
    R['size_formula_ok'] = (4 + 64*n == len(d))
    if not R['size_formula_ok']:
        R['error'] = f'size formula fails: 4+64*{n} != {len(d)}'
        return R
    tbl = struct.unpack(f'<{n}I', d[4:4+4*n])
    steps = collections.Counter(tbl[i+1]-tbl[i] for i in range(n-1))
    R['table'] = {'first': tbl[0], 'last': tbl[-1],
                  'step_hist': {str(k): v for k, v in steps.most_common(5)}}
    recs, bad = [], []
    base = 4 + 4*n
    for i in range(n):
        r = d[base+i*60: base+(i+1)*60]
        prefix = struct.unpack('<I', r[:4])[0]
        name = r[4:36].split(b'\x00')[0].decode('ascii', 'replace')
        date = r[36:56].decode('ascii', 'replace').strip('\x00 ')
        tr = r[56:60]
        ok = (tr == b'\x00\x01\x02\x03' and prefix == i
              and all(32 <= ord(c) < 127 for c in name) and name)
        if not ok: bad.append(i)
        recs.append({'idx': i, 'prefix': prefix, 'name': name,
                     'date': date})
    R['records_ok'] = len(recs) - len(bad)
    R['records_bad'] = bad[:20]
    R['sequence_proven'] = (len(bad) == 0)
    R['prefix_hist'] = {k: v for k, v in collections.Counter(
        r['name'].split('_')[0] for r in recs).most_common()}
    R['names'] = [r['name'] for r in recs]
    R['records'] = recs
    return R

def main():
    srcdir, outp = sys.argv[1], sys.argv[2]
    files = sorted(f for f in os.listdir(srcdir) if f.endswith('.info'))
    out = {}
    for f in files:
        r = parse(os.path.join(srcdir, f))
        out[f] = r
        print(f"{f}: N={r.get('count_field')} formula_ok="
              f"{r.get('size_formula_ok')} seq_proven={r.get('sequence_proven')} "
              f"bad={len(r.get('records_bad', []))} prefixes={r.get('prefix_hist')}")
    json.dump(out, open(outp, 'w'), indent=1)
    print('->', outp)

if __name__ == '__main__':
    main()
