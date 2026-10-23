#!/usr/bin/env python3
"""DOA4 phase 16 Job 3: materialize the three mirror streams as
files (for mmap-based scatter) from the digest-verified extracted-
tar parts in scratch/mirrorparts (release doa4-mirror-20261017;
part digests asserted here against the phase-15 table before any
byte is copied). Stream layout in the extracted tar (phase 14/15):
chrone @1212324864 (366,094,336 B), chrtwo @1578419712
(548,042,752 B), chrthree @2135433728 (762,955,776 B); parts are
524,288,000 B each, tar base = part 02 start.
Output: scratch/mirror_streams/<vol>.bin + sha256 of each stream.
"""
import hashlib, os, sys

SCR = '/home/hatch/workspace/_doa4p16-scratch'
PART = 524288000
DIGESTS = {2: 'fc7b95e598442890ebd61c2e09aaf02d6b02ab907a277917988674bfbf10aae6',
           3: '24656e3afcd4777027532301bc2643b93cdfe08b33f2b02f161acecb594ba8c4',
           4: 'c5d119db3ac6fd06c340371ff32534542fbef0301b66778f3594d21c0f669ef3',
           5: 'cccd3eed44b668434fa36b020127f269ca4b6856ad1ecb24f12524e5e1d32f80'}
STREAMS = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
           'chrthree': (2135433728, 762955776)}
MBASE = 2 * PART

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    parts = {}
    for n in (2, 3, 4, 5):
        p = os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
        assert os.path.exists(p), p
        d = sha256_file(p)
        assert d == DIGESTS[n], (n, d)
        parts[n] = p
        print(f'part {n}: DIGEST OK', flush=True)
    outdir = os.path.join(SCR, 'mirror_streams')
    os.makedirs(outdir, exist_ok=True)
    for vol, (off, size) in STREAMS.items():
        dst = os.path.join(outdir, vol + '.bin')
        h = hashlib.sha256(); left = size; goff = off
        with open(dst, 'wb') as o:
            while left > 0:
                rel = goff - MBASE; pi, lo = rel // PART, rel % PART
                take = min(left, PART - lo)
                with open(parts[pi + 2], 'rb') as f:
                    f.seek(lo); b = f.read(take)
                assert len(b) == take
                o.write(b); h.update(b)
                goff += take; left -= take
        print(vol, size, 'sha256', h.hexdigest(), flush=True)
    print('MIRROR STREAMS MATERIALIZED')

if __name__ == '__main__':
    main()
