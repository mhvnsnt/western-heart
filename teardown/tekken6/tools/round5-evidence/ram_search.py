#!/usr/bin/env python3
"""Round 5 RAM-dump analysis (breakpoint-independent).
Usage: ram_search.py <ram.bin> [tag]
Searches the 32MB RAM image (base 0x8800000) for:
 - every container's raw container-head (64B) and body-head (64B)
 - every decoder output head (64B) and mid (64B) — PASS full + FAIL partial
 - all 'GZIP' magic occurrences with their header words
 - EBOOT image presence/extent (first/last match of EBOOT code slices)
 - overlay scan: 4KB blocks OUTSIDE the EBOOT VA span with high MIPS
   opcode plausibility (candidate overlay code), reported by density.
Writes r5_ram_<tag>.json + prints summary."""
import json, struct, sys
ROOT = '/home/hatch/workspace/_t6r4-work'
BASE = 0x8800000
ram_path, tag = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'x')
ram = open(ram_path, 'rb').read()
sigs = json.load(open(f'{ROOT}/r5_signatures.json'))
res = {'ram': ram_path, 'ram_len': len(ram), 'containers': [], 'gzip_magics': [], 'overlay_blocks': []}

def find_all(hay, needle):
    out, i = [], hay.find(needle)
    while i >= 0:
        out.append(i); i = hay.find(needle, i + 1)
    return out

for s in sigs:
    e = {'idx': s['idx'], 'entry': s['entry'], 'pass': s['pass']}
    for key in ('cont_head', 'body_head', 'out_head', 'out_mid'):
        n = bytes.fromhex(s[key]) if s[key] else b''
        e[key] = [hex(BASE + o) for o in find_all(ram, n)] if len(n) >= 32 else []
    res['containers'].append(e)

# all GZIP magics
for o in find_all(ram, b'GZIP'):
    w = struct.unpack_from('<5I', ram, o) if o + 20 <= len(ram) else None
    res['gzip_magics'].append({'va': hex(BASE + o), 'w': list(w) if w else None})

# EBOOT extent: ELF is not loaded linearly; use two known code slices:
# wrapper entry bytes from the decrypted ELF file offset mapping is not
# linear, so instead locate the loader address bytes pattern: search for
# the exact 64B at VA 0x89d27a0 in RAM (identity check of the dump itself)
probe_off = 0x89D27A0 - BASE
res['loader_probe'] = {'va': '0x89d27a0', 'bytes': ram[probe_off:probe_off + 32].hex()}

# overlay scan: MIPS plausibility = fraction of words whose opcode field
# is a common opcode and low bytes aren't all zero/ff
COMMON = {0x00, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0C,
          0x0D, 0x0F, 0x10, 0x12, 0x18, 0x19, 0x1A, 0x1B, 0x20, 0x21, 0x22,
          0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2E, 0x2F}
EBOOT_LO, EBOOT_HI = 0x8804000, 0x8C40000  # generous EBOOT VA span
for blk in range(0, len(ram) - 4096, 4096):
    va = BASE + blk
    if EBOOT_LO <= va < EBOOT_HI: continue
    words = struct.unpack_from('<1024I', ram, blk)
    nz = sum(1 for w in words if w not in (0, 0xFFFFFFFF))
    if nz < 512: continue
    pl = sum(1 for w in words if (w >> 26) in COMMON and w not in (0, 0xFFFFFFFF)) / nz
    jr = sum(1 for w in words if w == 0x03E00008)
    if pl > 0.92 and jr >= 2:
        res['overlay_blocks'].append({'va': hex(va), 'nz': nz, 'plaus': round(pl, 3), 'jr_ra': jr})
json.dump(res, open(f'{ROOT}/r5_ram_{tag}.json', 'w'), indent=1)
nc = sum(1 for c in res['containers'] if c['cont_head'] or c['body_head'])
no = sum(1 for c in res['containers'] if c['out_head'])
print(f"RAM {tag}: containers with raw bytes in RAM: {nc}/76; with output head: {no}/76")
print(f"GZIP magics in RAM: {len(res['gzip_magics'])}")
print(f"overlay-candidate blocks outside EBOOT span: {len(res['overlay_blocks'])}")
for c in res['containers']:
    if c['cont_head'] or c['body_head'] or c['out_head'] or c['out_mid']:
        print(' ', c)
