#!/usr/bin/env python3
"""DOA4 phase 13 Job 3(a) scoped L2: payload hashes for the decision
set only — all 42 head packages + the 43 proven-family bodies —
fetched per-texture (exact decoder byte counts from the L1 census)
instead of whole pool spans. Merges into the L1 census structure and
writes texrecord_census_l2scoped.json. The full-pool census
(texrecord_census_p13.py) remains the canonical all-148 artifact;
this scoped pass exists so the pairing matrix is computable without
waiting on the 38 non-family chrthree bodies.
"""
import hashlib, json, struct, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch

AFS = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
       'chrthree': (2135433728, 762955776)}
INV = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase6/inventory-%s.csv'
SCR = '/home/hatch/workspace/_doa4p2-scratch/p13/'
HEADS = ['chrtwo-pkg%02d' % i for i in range(4, 46)]
FAM_BODIES = (['chrone-pkg%02d' % i for i in range(0, 6)]
              + ['chrone-pkg10', 'chrone-pkg13', 'chrtwo-pkg46', 'chrtwo-pkg49', 'chrthree-pkg01']
              + ['chrone-pkg17', 'chrone-pkg18', 'chrone-pkg20', 'chrone-pkg21', 'chrone-pkg22', 'chrthree-pkg18', 'chrthree-pkg19']
              + ['chrtwo-pkg%02d' % i for i in range(50, 56)] + ['chrthree-pkg%02d' % i for i in range(2, 8)]
              + ['chrone-pkg14', 'chrone-pkg15', 'chrone-pkg16']
              + ['chrone-pkg%02d' % i for i in range(6, 10)] + ['chrtwo-pkg00']
              + ['chrthree-pkg%02d' % i for i in range(29, 32)])
WANT = HEADS + FAM_BODIES

def xp_of(pkg):
    afs = pkg.split('-')[0]
    for line in open(INV % afs):
        r = line.split(',')
        if r[0] == pkg:
            return afs, int(r[1], 16)
    raise KeyError(pkg)

def main():
    l1 = json.load(open(SCR + 'texrecord_census_l1.json'))
    out = {}
    for pkg in WANT:
        afs, xp = xp_of(pkg)
        base_afs = AFS[afs][0]
        d = fetch(base_afs + xp, 1 << 18)
        hdr_f1 = struct.unpack('>I', d[4:8])[0]
        pool = xp + ((hdr_f1 + 0xFFF) & ~0xFFF)
        texs = []
        for t in l1[pkg].get('tex', []):
            t2 = dict(t)
            if t.get('need') and t['need'] <= (1 << 24):
                raw = fetch(base_afs + pool + t['base'], t['need'])
                if len(raw) == t['need']:
                    t2['l2'] = hashlib.sha256(raw).hexdigest()
            texs.append(t2)
        out[pkg] = {'nrec': l1[pkg].get('nrec'), 'tex': texs}
        print(pkg, 'l2', sum(1 for x in texs if x.get('l2')), '/', len(texs), flush=True)
    json.dump(out, open(SCR + 'texrecord_census_l2scoped.json', 'w'), indent=1)
    print('WROTE texrecord_census_l2scoped.json')

if __name__ == '__main__':
    main()
