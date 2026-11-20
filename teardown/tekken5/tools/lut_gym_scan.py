#!/usr/bin/env python3
"""Sample every PS2 LUT entry in TK5DATA1.BIN for gym (motion) files.

The 6 DW files with no data in TK5DATA2 (gym_ozhe_1ckj66a,
gym_ikt5_katgym_Bbr_bbblow, gym_ikt5_katgym_Gan_mekin,
gym_init_obj_testchr1/2/3) carry no size in the index and their names
appear NOWHERE in TK5DATA1 (full string stream-scan: 0 'gym_' hits),
so no entry can be attributed to one of them by name. This scan
answers the coarser question: which LUT entries ARE gym files, and
what are their bone/frame counts — the inventory the 6 would have
to hide in.

Method (stream-scan, no whole-file download, no big disk writes):
  - Read the PS2 LUT from the local Code blob (TABLESTART 0x0027B5B0,
    1571 entries: offset u32 x 0x800, size u32).
  - For each entry (size != 0xFFFFFFFF): HTTP Range-fetch only the
    first 2048 bytes from TK5DATA1 inside the ISO
    (ISO offset 2074302464 + sector*2048), in parallel, discard after.
  - Check GYM1 magic at offset 64 on the raw bytes; if absent,
    decrypt the sector with the sector cipher (seed = entry index,
    same 2048-byte keystream per block) and check again.
  - On a hit, parse the gym header: bones h[1], frames h[2],
    field12 h[12]; field12 should equal frames*bones*12.

Output: small JSON only (per-entry gym hits + summary counts).
Usage: python3 lut_gym_scan.py <TK5DATA3_code.bin> <out.json> [nstreams]
"""
import json, struct, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from romd_extract import decrypt_sector_data_fast

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"
ISO_OFF = 2074302464
TABLESTART = 0x0027B5B0
TABLECOUNT = 1571
SECTOR = 0x800


def fetch(iso_start, nbytes, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                URL, headers={"Range": f"bytes={iso_start}-{iso_start + nbytes - 1}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status}")
                data = r.read()
            if len(data) != nbytes:
                raise RuntimeError(f"short read {len(data)} != {nbytes}")
            return data
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(5)


def scan_entry(args):
    indx, sector, size = args
    if size == 0xFFFFFFFF or size < 104:
        return {'index': indx, 'sector': sector, 'size': size, 'status': 'skipped'}
    nbytes = min(size, 2048)
    try:
        raw = fetch(ISO_OFF + sector * SECTOR, nbytes)
    except Exception as e:
        return {'index': indx, 'sector': sector, 'size': size,
                'status': 'fetch_error', 'error': str(e)[:200]}
    for mode, buf in (('raw', raw), ('decrypted', None)):
        b = buf
        if mode == 'decrypted':
            b = bytearray(raw)
            decrypt_sector_data_fast(b, indx, len(b))
            b = bytes(b)
        if len(b) >= 68 and b[64:68] == b'GYM1':
            h = struct.unpack_from('<16I', b, 0)
            bones, frames, field12 = h[1], h[2], h[12]
            return {'index': indx, 'sector': sector, 'size': size,
                    'status': 'gym', 'crypto': mode,
                    'bones': bones, 'frames': frames, 'field12': field12,
                    'field12_ok': field12 == frames * bones * 12}
    return {'index': indx, 'sector': sector, 'size': size, 'status': 'not_gym'}


def main():
    code_path, out_path = sys.argv[1], sys.argv[2]
    nstreams = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    code = open(code_path, 'rb').read()
    entries = []
    for i in range(TABLECOUNT):
        sector, size = struct.unpack_from('<II', code, TABLESTART + i * 8)
        entries.append((i, sector, size))
    print(f'{len(entries)} LUT entries; sampling first sector each, {nstreams} streams', flush=True)
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=nstreams) as ex:
        for res in ex.map(scan_entry, entries):
            results.append(res)
            done += 1
            if done % 200 == 0:
                gyms = sum(1 for r in results if r['status'] == 'gym')
                print(f'  {done}/{len(entries)} entries, {gyms} gym hits so far', flush=True)
    gyms = [r for r in results if r['status'] == 'gym']
    summary = {
        'entries': len(entries),
        'skipped': sum(1 for r in results if r['status'] == 'skipped'),
        'fetch_errors': sum(1 for r in results if r['status'] == 'fetch_error'),
        'not_gym': sum(1 for r in results if r['status'] == 'not_gym'),
        'gym': len(gyms),
        'gym_raw': sum(1 for r in gyms if r['crypto'] == 'raw'),
        'gym_encrypted': sum(1 for r in gyms if r['crypto'] == 'decrypted'),
    }
    out = {
        'format': 'western-heart dw-lut-gym-scan v1',
        'source': 'TK5DATA1.BIN via PS2 LUT (Code blob TABLESTART 0x0027B5B0), '
                  'Internet Archive item slus-210.59.-tekken-5',
        'method': 'first 2048 bytes per LUT entry, range-fetch + discard; '
                  'GYM1 magic at offset 64, raw then sector-cipher (seed = entry index)',
        'note': 'No entry can be attributed to one of the 6 missing DW files '
                'by name: their names appear nowhere in TK5DATA1 (0 gym_ hits '
                'in the full string stream-scan) and the index records no sizes.',
        'summary': summary,
        'gym_entries': gyms,
        'fetch_errors': [r for r in results if r['status'] == 'fetch_error'],
    }
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f"done: {summary} -> {out_path}", flush=True)


if __name__ == '__main__':
    main()
