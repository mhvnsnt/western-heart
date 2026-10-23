#!/usr/bin/env python3
"""DOA4 phase 16 (p15 tool, p16 paths): resumable MIRROR part fetcher (same mechanism as
iso_fetch_driver_p15.py; asset ids/digests are the phase-14 table
for release doa4-mirror-20261017 extracted-tar parts 02-05).
Appends/resumes per 16 MiB chunk; digest-verified on completion.
Usage: mirror_fetch_driver_p15.py Replaces the gh
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

SCR = '/home/hatch/workspace/_doa4p16-scratch/mirrorparts'
CH = 1 << 24
_tok = None

def tok():
    global _tok
    if _tok is None:
        _tok = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
    return _tok


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

ASSETS = {2: 651173731, 3: 651189144, 4: 651243921, 5: 651266911}
SIZES = {2: 524288000, 3: 524288000, 4: 524288000, 5: 506081280}
DIGESTS = {2: 'fc7b95e598442890ebd61c2e09aaf02d6b02ab907a277917988674bfbf10aae6',
           3: '24656e3afcd4777027532301bc2643b93cdfe08b33f2b02f161acecb594ba8c4',
           4: 'c5d119db3ac6fd06c340371ff32534542fbef0301b66778f3594d21c0f669ef3',
           5: 'cccd3eed44b668434fa36b020127f269ca4b6856ad1ecb24f12524e5e1d32f80'}

def fetch_part(n):
    name = f'doa4-mirror-extracted-20261017.tar.part-{n:02d}'
    path = os.path.join(SCR, name)
    size = SIZES[n]
    if os.path.exists(path) and os.path.getsize(path) == size and sha256_file(path) == DIGESTS[n]:
        print(name, 'already present, DIGEST OK', flush=True); return True
    for round_ in (1, 2):
        done = 0
        if os.path.exists(path):
            done = (os.path.getsize(path) // CH) * CH
            with open(path, 'r+b') as f: f.truncate(done)
            if done: print(f'{name}: resuming at {done}/{size}', flush=True)
        with open(path, 'ab') as f:
            while done < size:
                take = min(CH, size - done)
                f.write(fetch_range(ASSETS[n], done, done + take - 1))
                done += take
                if done % (CH * 8) == 0: print(f'{name}: {done}/{size}', flush=True)
        sha = sha256_file(path)
        print(f'{name}: sha256 {sha} (round {round_})', flush=True)
        if sha == DIGESTS[n]:
            print(f'{name}: DIGEST OK', flush=True); return True
        os.remove(path)
    return False

def main():
    for n in (2, 3, 4, 5):
        if not fetch_part(n):
            print('ABORT part', n, flush=True); return 1
    print('MIRROR PARTS 02-05 ALL DIGEST-VERIFIED', flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
