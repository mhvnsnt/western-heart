#!/usr/bin/env python3
"""Build all 66 pool dicts (loose bound) once and cache as pickle."""
import struct, re, pickle, os
d6 = open(os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin'), 'rb').read()
u32 = lambda o: struct.unpack('>I', d6[o:o + 4])[0]

seen = {}
for m in re.finditer(rb'\[([A-Za-z0-9_\- ]{2,24})\]\x00', d6):
    nm = m.group(1).decode('ascii', 'replace')
    if nm not in seen:
        seen[nm] = m.start()
order = sorted(seen.items(), key=lambda kv: kv[1])

pools = {}
for nm, br in order:
    base = br - 0x20C
    if u32(base + 8) == 0 and 0x1000 < u32(base + 0x140) < 0x40000:
        span = u32(base + 0x140)
    else:
        span = 0x14000
    pool, off = {}, br
    while off < br + span:
        end = d6.index(b'\x00', off)
        pool[off - br] = d6[off:end].decode('ascii', 'replace')
        off = end + 1
    pools[nm] = pool
    print(nm, len(pool))
pickle.dump({'order': order, 'pools': pools},
            open(os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work/pools.pkl'), 'wb'))
print('cached pools.pkl')
