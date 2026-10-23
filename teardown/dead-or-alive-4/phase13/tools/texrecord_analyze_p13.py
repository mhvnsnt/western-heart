#!/usr/bin/env python3
"""DOA4 phase 13 Job 3 analysis over the TX2D census JSONs.
L1 analysis runs on texrecord_census_l1.json; L2 (payload-hash)
analysis activates automatically when texrecord_census.json (with l2
fields) exists and is merged in.

Families (phase 10 HEAD-ATTACHMENT + phase 11 HEAD-ORIGIN-RESEAT,
anchor Δ=0.000 proven):
  fam486: bodies chrone00-05;            heads 17,18,19,20,29,30,34,35
  fam478: bodies chrone10,chrone13,chrtwo46,chrtwo49,chrthree01; heads 08,09,33
  fam468: bodies chrone17,18,20,21,22,chrthree18,19; heads 04,07,21
  fam477: bodies chrtwo50-55,chrthree02-07; heads 22,25,41,42,43,44
  fam581: bodies chrone14,15,16;        heads 10,11
  famC:   bodies chrone06-09,chrtwo00,chrtwo31,chrthree29-31; head 31
Unpaired heads: 05,06,23,24,26,27,28,32 (all chrtwo).
Controls: identical head copies pkg11-16, pkg35-40, pkg44=45.
"""
import json, sys
from collections import defaultdict

SCR = '/home/hatch/workspace/_doa4p2-scratch/p13/'
FAMS = {
    'fam486': (['chrone-pkg%02d' % i for i in range(0, 6)], [17, 18, 19, 20, 29, 30, 34, 35]),
    'fam478': (['chrone-pkg10', 'chrone-pkg13', 'chrtwo-pkg46', 'chrtwo-pkg49', 'chrthree-pkg01'], [8, 9, 33]),
    'fam468': (['chrone-pkg17', 'chrone-pkg18', 'chrone-pkg20', 'chrone-pkg21', 'chrone-pkg22', 'chrthree-pkg18', 'chrthree-pkg19'], [4, 7, 21]),
    'fam477': (['chrtwo-pkg%02d' % i for i in range(50, 56)] + ['chrthree-pkg%02d' % i for i in range(2, 8)], [22, 25, 41, 42, 43, 44]),
    'fam581': (['chrone-pkg14', 'chrone-pkg15', 'chrone-pkg16'], [10, 11]),
    'famC':   (['chrone-pkg%02d' % i for i in range(6, 10)] + ['chrtwo-pkg00'] + ['chrthree-pkg%02d' % i for i in range(29, 32)], [31]),  # phase-13 fix: chrtwo-pkg31 removed — it is head31's OWN package (head range 04-45); phase-11's 'chrtwo00/31' body list made it a self-match artifact (21/21)
}
UNPAIRED = [5, 6, 23, 24, 26, 27, 28, 32]
BODIES = sorted({b for bs, _ in FAMS.values() for b in bs})

def load():
    c = json.load(open(SCR + 'texrecord_census_l1.json'))
    try:
        c2 = json.load(open(SCR + 'texrecord_census.json'))
        for k, v in c2.items():
            if k in c and 'tex' in v:
                c[k] = v
    except FileNotFoundError:
        pass
    return c

def keys(c, pkg, level):
    out = []
    for t in c[pkg].get('tex', []):
        if level == 'l1':
            out.append(tuple(t['l1']))
        elif t.get('l2'):
            out.append(t['l2'])
    return out

def report(level):
    c = load()
    print(f'==== {level.upper()} ====')
    # control: identical copies
    for grp in ([11, 12, 13, 14, 15, 16], [35, 36, 37, 38, 39, 40], [44, 45]):
        sets = [set(keys(c, 'chrtwo-pkg%02d' % i, level)) for i in grp]
        inter = set.intersection(*sets) if sets else set()
        union = set.union(*sets) if sets else set()
        print(f'control {grp}: |inter|={len(inter)} |union|={len(union)} sizes={[len(s) for s in sets]}')
    # premise: proven head vs own-family bodies vs other bodies
    print('-- premise test (proven heads): shared-key count own-family vs best-other --')
    for fam, (bodies, heads) in FAMS.items():
        others = [b for b in BODIES if b not in bodies]
        for h in heads:
            hk = set(keys(c, 'chrtwo-pkg%02d' % h, level))
            own = max((len(hk & set(keys(c, b, level))) for b in bodies), default=0)
            oth = max((len(hk & set(keys(c, b, level))) for b in others), default=0)
            print(f'  head{h:02d} ({fam}): |keys|={len(hk)} own-max={own} other-max={oth}')
    print('-- unpaired heads: shared-key count per family (max over family bodies) --')
    for h in UNPAIRED:
        hk = set(keys(c, 'chrtwo-pkg%02d' % h, level))
        row = []
        for fam, (bodies, _) in FAMS.items():
            m = max((len(hk & set(keys(c, b, level))) for b in bodies), default=0)
            row.append(f'{fam}={m}')
        print(f'  head{h:02d}: |keys|={len(hk)} ' + ' '.join(row))

if __name__ == '__main__':
    report('l1')
    c = load()
    if any(t.get('l2') for v in c.values() for t in v.get('tex', [])):
        report('l2')
