#!/usr/bin/env python3
"""DOA4 phase 14: resumable range-fetch of doa4-mirror-20261017
extracted-tar parts (the egress proxy kills long gh downloads;
a failed part restarts from zero under gh). Fetches 16 MiB
ranges with per-chunk retries via the GitHub asset API (same
mechanism as tools/phase6/fetch.py, but streaming to a file),
then verifies the part's sha256 against the release digest.
A digest failure restarts the part once; a second failure is
reported, not worked around.
Usage: fetch_part_resume_p14.py PARTNO OUTDIR
"""
import hashlib, os, subprocess, sys, time
import requests

ASSETS = {0: 651130101, 1: 651155986, 2: 651173731,
          3: 651189144, 4: 651243921, 5: 651266911}
SIZES = {0: 524288000, 1: 524288000, 2: 524288000,
         3: 524288000, 4: 524288000, 5: 506081280}
DIGESTS = {2: 'fc7b95e598442890ebd61c2e09aaf02d6b02ab907a277917988674bfbf10aae6',
           3: '24656e3afcd4777027532301bc2643b93cdfe08b33f2b02f161acecb594ba8c4',
           4: 'c5d119db3ac6fd06c340371ff32534542fbef0301b66778f3594d21c0f669ef3',
           5: 'cccd3eed44b668434fa36b020127f269ca4b6856ad1ecb24f12524e5e1d32f80'}
CH = 1 << 24
_tok = None


def tok():
    global _tok
    if _tok is None:
        _tok = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
    return _tok


def fetch_range(asset, lo, hi):
    url = f'https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/{asset}'
    last = None
    for attempt in range(10):
        try:
            r = requests.get(url, headers={
                'Authorization': f'token {tok()}',
                'Accept': 'application/octet-stream',
                'Range': f'bytes={lo}-{hi}'}, timeout=300)
            assert r.status_code == 206, r.status_code
            assert len(r.content) == hi - lo + 1, (len(r.content), hi - lo + 1)
            return r.content
        except Exception as e:
            last = e
            global _tok
            _tok = None
            time.sleep(3 * (attempt + 1))
    raise last


def fetch_part(part, outdir):
    name = f'doa4-mirror-extracted-20261017.tar.part-{part:02d}'
    path = os.path.join(outdir, name)
    size = SIZES[part]
    for round_ in (1, 2):
        h = hashlib.sha256()
        with open(path, 'wb') as f:
            done = 0
            while done < size:
                take = min(CH, size - done)
                b = fetch_range(ASSETS[part], done, done + take - 1)
                f.write(b); h.update(b); done += take
                if done % (CH * 8) == 0:
                    print(f'{name}: {done}/{size}', flush=True)
        sha = h.hexdigest()
        print(f'{name}: sha256 {sha} (round {round_})', flush=True)
        if sha == DIGESTS[part]:
            print(f'{name}: DIGEST OK', flush=True)
            return 0
        print(f'{name}: DIGEST MISMATCH, expected {DIGESTS[part]}', flush=True)
    print(f'{name}: FAILED after 2 rounds', flush=True)
    return 1


if __name__ == '__main__':
    sys.exit(fetch_part(int(sys.argv[1]), sys.argv[2]))
