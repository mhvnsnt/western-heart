#!/usr/bin/env python3
"""Structural survey of TK5DATA2.BIN: enumerate CRLF name-list blocks,
BDPK positions, and the gaps between blocks. No extraction, read-only."""
import re, json
data = open('/home/hatch/workspace/devil-within-decode/raw/TK5DATA2.BIN','rb').read()
N = len(data)
print('size', N)
# maximal runs of lines matching name\r\n where name is printable, ends .dat/.evd/.bin or has no ext but no spaces
line_re = re.compile(rb'([ -~]{1,80})\r\n')
blocks = []
pos = 0
# find all .dat/.evd line occurrences, then group consecutive ones
hits = []
for m in re.finditer(rb'[ -~]{1,80}\.(?:dat|evd)\r\n', data):
    hits.append((m.start(), m.end(), m.group(0)[:-2].decode('ascii','replace')))
print('name-line hits:', len(hits))
# group: consecutive if next start == prev end
groups = []
cur = [hits[0]]
for h in hits[1:]:
    if h[0] == cur[-1][1]:
        cur.append(h)
    else:
        groups.append(cur); cur = [h]
groups.append(cur)
print('name-list blocks:', len(groups))
out = []
for g in groups:
    out.append({'start': g[0][0], 'end': g[-1][1], 'count': len(g),
                'first': g[0][2], 'last': g[-1][2],
                'names': [x[2] for x in g]})
    print(f"block @{g[0][0]:#x}-{g[-1][1]:#x} count={len(g)} first={g[0][2]} last={g[-1][2]}")
json.dump(out, open('/home/hatch/workspace/devil-within-decode/raw/romd_blocks.json','w'), indent=1)
# BDPK offsets
bdpk = [m.start() for m in re.finditer(b'BDPK', data)]
print('BDPK count:', len(bdpk))
# which block/gap is each BDPK in?
def context(off):
    for i, g in enumerate(groups):
        if g[0][0] <= off < g[-1][1]:
            return f'in-block-{i}'
    return 'in-gap'
from collections import Counter
print(Counter(context(o) for o in bdpk))
# gap sizes between consecutive blocks
for i in range(len(groups)-1):
    print(f"gap {i}->{i+1}: {groups[i+1][0][0]-groups[i][-1][1]} bytes")
print('head gap (0 to first block):', groups[0][0][0])
print('tail gap (last block end to EOF):', N - groups[-1][-1][1])
# dump region 0x100..0x1b30 as text-ish
print('--- region 0x400..0x1b30 repr (first 1500 chars) ---')
print(repr(data[0x400:0x1b30][:1500]))
