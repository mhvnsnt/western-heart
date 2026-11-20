#!/usr/bin/env python3
"""Round 5: build search signatures for RAM dumps.
For each of the 76 GZIP containers: container header words, raw container
prefix (64B from container start), body prefix (64B from +0x14), and the
Python decoder's output head (64B) + a 64B slice at 50% of output.
PASS/FAIL per the adler oracle in tekken6_gzip.py."""
import json, struct, sys, zlib
sys.path.insert(0, '/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools')
import tekken6_gzip as tg

ROOT = '/home/hatch/workspace/_t6r4-work'
MAN = json.load(open(f'{ROOT}/recon/x/tekken6/work/decrypt3/manifest.json'))
GZ = [f for f in MAN['files'] if f['magic'].startswith('GZIP')]
bulk = open(f'{ROOT}/recon/x/tekken6/work/decrypt3/bulk_decrypted.bin', 'rb')

def tolerant_decompress(data):
    """History-aware decode (zero 32K window) like round-4 dict_sweep:
    dist>len(out) reads into the zero window instead of raising, so FAIL
    containers still yield their partial output for RAM signatures."""
    br = tg.BitReader(data)
    out = bytearray()
    hist = bytearray(32768)  # zero window preceding output
    while True:
        bfinal = br.bits(1); btype = br.bits(2)
        if btype == 0:
            br.pos = (br.pos + 7) & ~7
            ln = struct.unpack('<H', data[br.pos >> 3:(br.pos >> 3) + 2])[0]; br.pos += 16
            br.pos += 16
            out.extend(data[br.pos >> 3:(br.pos >> 3) + ln]); br.pos += ln * 8
        elif btype in (1, 2):
            if btype == 2:
                hlit = br.bits(5); hdist = br.bits(5)
                lit_lens, dist_lens = tg.decode_dynamic(br, hlit + 257, hdist + 1)
                lit_t = tg.build_huffman(lit_lens); dist_t = tg.build_huffman(dist_lens)
            else:
                lit_t = tg.build_huffman([8] * 144 + [9] * 112 + [7] * 24 + [8] * 8)
                dist_t = tg.build_huffman([5] * 32)
            while True:
                sym = tg.decode_symbol(br, lit_t)
                if sym < 256: out.append(sym)
                elif sym == 256: break
                else:
                    li = sym - 257
                    length = tg.LBASE[li] + br.bits(tg.LEXT[li])
                    dsym = tg.decode_symbol(br, dist_t)
                    if btype == 1:
                        dist = tg.DBASE_STD[dsym] + br.bits(tg.DEXT_STD[dsym])
                    else:
                        base = tg.DBASE_EBOOT[dsym]
                        extra = br.bits(30 - tg.clz32(base)) if base >= 4 else 0
                        dist = base + extra + 1
                    full = hist + out
                    for _ in range(length):
                        out.append(full[len(full) - dist]); full.append(out[-1])
        else:
            raise ValueError('reserved btype')
        if bfinal: break
    return bytes(out), br.pos

sigs = []
for idx, f in enumerate(GZ):
    bulk.seek(f['start_rel'] * 2048)
    fdata = bulk.read(f['size'])
    raw = fdata
    if f['magic'] == 'GZIP+prefix16':
        fdata = fdata[16:]
    w = struct.unpack('<5I', fdata[:20])
    body = fdata[20:]
    out, ok, err = b'', False, ''
    try:
        out, bits_used = tolerant_decompress(body[2:])
        adler_off = (bits_used + 7) // 8
        trailer = struct.unpack('>I', body[2 + adler_off:2 + adler_off + 4])[0]
        ok = len(out) == w[3] and zlib.adler32(out) == trailer
    except Exception as e:
        err = str(e)
    mid = out[len(out)//2:len(out)//2 + 64] if len(out) > 256 else b''
    sigs.append({'idx': idx, 'entry': f['entry'], 'sub': f['sub'],
                 'w': list(w), 'size': f['size'], 'prefix16': f['magic'].endswith('prefix16'),
                 'pass': bool(ok), 'out_len': len(out), 'expect': w[3], 'err': err,
                 'cont_head': raw[:64].hex(), 'body_head': body[:64].hex(),
                 'out_head': out[:64].hex(), 'out_mid': mid.hex()})
    print(f"idx{idx} entry{f['entry']}: pass={ok} out={len(out)}/{w[3]} {err}")
json.dump(sigs, open(f'{ROOT}/r5_signatures.json', 'w'), indent=1)
print('PASS count:', sum(1 for s in sigs if s['pass']), '/ 76')
