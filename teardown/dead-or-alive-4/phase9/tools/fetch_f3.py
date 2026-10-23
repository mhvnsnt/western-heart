#!/usr/bin/env python3
"""Phase 9 Job 1c: fetch the XPR2 header record (f1,f2,f3) for every phase-6
package via range reads on the doa4-mirror tar (phase-6 fetch.py), and dump
the package-wide f3 tag table. Hypothesis under test: f3 links head packages
(chrtwo small) to body packages of the same character."""
import struct, sys, json
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch

AFS = {'chrone': 1212324864, 'chrtwo': 1578419712, 'chrthree': 2135433728}
out = {}
for name, base in AFS.items():
    pkgs = json.load(open(f'/home/hatch/workspace/_doa4p2-scratch/p6/{name}_pkgs.json'))
    rows = []
    for i, h in enumerate(pkgs):
        d = fetch(base + h['xp'], 16)
        assert d[:4] == b'XPR2', (name, i, d[:4])
        f1, f2, f3 = struct.unpack('>3I', d[4:16])
        rows.append({'pkg': i, 'xp': h['xp'], 'f1': f1, 'f2': f2, 'f3': f3})
        print(name, i, 'f1', f1, 'f2', hex(f2), 'f3', f3, flush=True)
    out[name] = rows
json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p9/f3_table.json', 'w'), indent=1)
print('DONE')
