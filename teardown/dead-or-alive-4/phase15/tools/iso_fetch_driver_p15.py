#!/usr/bin/env python3
"""DOA4 phase 15: resumable ISO assembly driver. Replaces the gh
one-shot download path (the egress proxy kills long downloads at
~90% and gh restarts from zero) with the phase-14 range-fetch
mechanism: 16 MiB range chunks with per-chunk retries via the
GitHub asset API, appended to the part file (resume = truncate to
the last chunk boundary and continue; a pre-existing gh partial is
a true sequential prefix and is reused the same way). Each part's
sha256 is verified against the release digest BEFORE the proven
phase-13 assembler (p15 paths) is invoked for that part; the
assembler re-verifies, writes the part into the sparse ISO, and
deletes the part file. Digest failure restarts the part once;
a second failure aborts the driver (reported, not worked around).
Usage: iso_fetch_driver_p15.py [start_part]"""
import hashlib, json, os, subprocess, sys, time
import requests

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
LOG = os.path.join(SCR, 'iso_assembly_log.json')
ASM = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase15/tools/iso_assemble_p15.py'
CH = 1 << 24
PART_SIZE = 262144000
TOTAL = 7834892288
_tok = None

def tok():
    global _tok
    if _tok is None:
        _tok = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
    return _tok

def assets():
    out = subprocess.check_output(['gh', 'api', 'repos/mhvnsnt/western-heart/releases/tags/doa4-iso-v1',
                                   '--jq', '.assets[] | "\(.id) \(.name) \(.size) \(.digest)"']).decode()
    m = {}
    for line in out.strip().splitlines():
        aid, name, size, digest = line.split()
        m[name] = {'id': int(aid), 'size': int(size), 'digest': digest.split(':')[1]}
    return m

def fetch_range(asset, lo, hi):
    global _tok
    url = f'https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/{asset}'
    last = None
    for attempt in range(12):
        try:
            r = requests.get(url, headers={'Authorization': f'token {tok()}',
                                            'Accept': 'application/octet-stream',
                                            'Range': f'bytes={lo}-{hi}'}, timeout=300)
            assert r.status_code == 206, r.status_code
            assert len(r.content) == hi - lo + 1, (len(r.content), hi - lo + 1)
            return r.content
        except Exception as e:
            last = e; _tok = None; time.sleep(3 * (attempt + 1))
    raise last

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b: break
            h.update(b)
    return h.hexdigest()

def fetch_part(nn, amap):
    name = f'doa4-250m.part_{nn:02d}'
    meta = amap[name]
    path = os.path.join(SCR, name)
    size = meta['size']
    for round_ in (1, 2):
        done = 0
        if os.path.exists(path):
            done = (os.path.getsize(path) // CH) * CH
            with open(path, 'r+b') as f: f.truncate(done)
            if done: print(f'{name}: resuming at {done}/{size}', flush=True)
        with open(path, 'ab') as f:
            while done < size:
                take = min(CH, size - done)
                f.write(fetch_range(meta['id'], done, done + take - 1))
                done += take
                if done % (CH * 8) == 0: print(f'{name}: {done}/{size}', flush=True)
        sha = sha256_file(path)
        print(f'{name}: sha256 {sha} (round {round_})', flush=True)
        if sha == meta['digest']:
            print(f'{name}: DIGEST OK', flush=True)
            return True
        os.remove(path)
        print(f'{name}: DIGEST MISMATCH vs {meta["digest"]}', flush=True)
    return False

def landed():
    if os.path.exists(LOG):
        return set(json.load(open(LOG)).get('landed', {}))
    return set()

def main():
    amap = assets()
    for nn in range(1, 31):
        name = f'doa4-250m.part_{nn:02d}'
        if name in landed():
            print(name, 'already landed, skip', flush=True); continue
        if not fetch_part(nn, amap):
            print('DRIVER ABORT: digest failed twice on', name, flush=True); return 1
        r = subprocess.run([sys.executable, ASM, str(nn)])
        if r.returncode != 0 or name not in landed():
            print('DRIVER ABORT: assembler failed on', name, flush=True); return 1
        print(name, 'LANDED', len(landed()), '/30', flush=True)
    print('DRIVER DONE: 30/30', flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
