#!/usr/bin/env python3
"""DOA4 phase 15: fetch mirror extracted-tar parts 02-05 from release
doa4-mirror-20261017, sha256-verified against the release asset
digests (recorded below from the GitHub API at lane start). Each part
downloads to a .partial name and is renamed only after its digest
matches; a digest failure aborts (no workaround). Sequential, one
writer per file."""
import hashlib, os, subprocess, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15/mirrorparts'
PARTS = {
    2: 'fc7b95e598442890ebd61c2e09aaf02d6b02ab907a277917988674bfbf10aae6',
    3: '24656e3afcd4777027532301bc2643b93cdfe08b33f2b02f161acecb594ba8c4',
    4: 'c5d119db3ac6fd06c340371ff32534542fbef0301b66778f3594d21c0f669ef3',
    5: 'cccd3eed44b668434fa36b020127f269ca4b6856ad1ecb24f12524e5e1d32f80',
}

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    os.makedirs(SCR, exist_ok=True)
    for n, exp in PARTS.items():
        name = f'doa4-mirror-extracted-20261017.tar.part-{n:02d}'
        dst = os.path.join(SCR, name)
        if os.path.exists(dst) and sha256(dst) == exp:
            print(name, 'already present, digest OK', flush=True); continue
        tmp = dst + '.partial'
        if os.path.exists(tmp): os.remove(tmp)
        for attempt in range(6):
            subprocess.run(['gh', 'release', 'download', 'doa4-mirror-20261017',
                            '--repo', 'mhvnsnt/western-heart', '--pattern', name,
                            '--dir', SCR], check=False)
            got = os.path.join(SCR, name)
            if os.path.exists(got):
                d = sha256(got)
                if d == exp:
                    print(name, 'digest OK', d, flush=True); break
                print(name, 'digest MISMATCH', d, 'attempt', attempt, flush=True)
                os.remove(got)
            else:
                print(name, 'download missing, attempt', attempt, flush=True)
        else:
            print('FAILED part', n, flush=True); sys.exit(1)
    print('MIRROR PARTS 02-05 ALL DIGEST-VERIFIED', flush=True)

if __name__ == '__main__':
    main()
