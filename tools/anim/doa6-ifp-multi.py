"""Lane 1D second pass: convert the [IFP]/<char>.ifp MULTI-ANIMATION packages
(one file, 143-304 anims each) into wh-anim/1 clips and merge them into the
fighter's bank JSON (bank/doa6-<Char>.json) under keys "[IFP]/<animname>".
Fast path: whole-file rwfury parse (19/20 packs are clean).
Fallback (christie.ifp: anim CRI00127_CRI carries trailing extra objects,
declared size 2x): tolerant per-anim split — walk anim headers; after an
anim's declared objects, skip any trailing object-like headers (type 3/4,
sane count) + their frames until the next anim header; rebuild a single-anim
ANP3 per anim and convert with clip_to_wh() (which has its own fallback).
Clips already present in the bank (same key) are NOT overwritten.
"""
import json, os, sys, struct, hashlib, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools_convert_ifp import clip_to_wh
import rwfury

def _is_obj_header(d, off):
    if off + 36 > len(d):
        return False
    name = d[off:off+24].split(b'\x00')[0]
    if not name or not all(32 <= c < 127 for c in name):
        return False
    ft, fc, bid = struct.unpack('<III', d[off+24:off+36])
    return ft in (3, 4) and 0 < fc <= 5000

def _is_anim_header(d, off):
    if off + 36 > len(d):
        return False
    name = d[off:off+24].split(b'\x00')[0]
    if not name or not all(32 <= c < 127 for c in name):
        return False
    oc, fs, unk = struct.unpack('<III', d[off+24:off+36])
    return 0 < oc <= 200 and fs > 0 and unk == 1

def split_multi(data):
    """Yield (anim_name, single_anim_bytes) for each animation in a multi ANP3."""
    if data[:4] != b'ANP3':
        raise ValueError('not ANP3')
    anim_count = struct.unpack('<I', data[32:36])[0]
    off = 36
    for a in range(anim_count):
        start = off
        if not _is_anim_header(data, off):
            raise ValueError(f'anim {a}: bad anim header at offset {off}')
        aname = data[off:off+24].split(b'\x00')[0].decode(errors='replace')
        oc, fs, unk = struct.unpack('<III', data[off+24:off+36])
        off += 36
        for o in range(oc):
            if not _is_obj_header(data, off):
                raise ValueError(f'anim {aname}: bad obj header {o} at offset {off}')
            ft, fc, bid = struct.unpack('<III', data[off+24:off+36])
            off += 36 + fc * (16 if ft == 4 else 10)
        # skip trailing extra-object headers (KAS00246 / CRI00127 pattern)
        while _is_obj_header(data, off):
            ft, fc, bid = struct.unpack('<III', data[off+24:off+36])
            off += 36 + fc * (16 if ft == 4 else 10)
        anim_bytes = data[start:off]
        # ANP3 size field = file size - 8 = 24 (internal) + 4 (count) + anim bytes
        single = (b'ANP3' + struct.pack('<I', 24 + 4 + len(anim_bytes))
                  + data[8:32] + struct.pack('<I', 1) + anim_bytes)
        yield aname, single

def convert_multi_bytes(data, src_zip, src_sha256):
    """Return ({anim_name: clip}, [(anim_name, error)]) for a multi-anim file.
    Tolerant per-anim split; anims converted before any split error are kept."""
    out, errs = {}, []
    try:
        for aname, single in split_multi(data):
            try:
                out[aname] = clip_to_wh(f'[IFP]:{aname}', single, src_zip, src_sha256)
            except Exception as e2:
                errs.append((aname, type(e2).__name__ + ': ' + str(e2)))
    except Exception as e3:
        errs.append(('<split>', type(e3).__name__ + ': ' + str(e3)))
    return out, errs

def process_pack(zip_path, bank_path):
    zsha = hashlib.sha256(open(zip_path, 'rb').read()).hexdigest()
    zname = os.path.basename(zip_path)
    bank = json.load(open(bank_path))
    clips = bank.setdefault('clips', {})
    failed = bank.setdefault('failed', [])
    added = 0; skipped = 0
    with zipfile.ZipFile(zip_path) as zf:
        multis = [n for n in zf.namelist() if n.startswith('[IFP]/') and n.lower().endswith('.ifp')]
        for m in multis:
            data = zf.read(m)
            got, errs = convert_multi_bytes(data, zname, zsha)
            for aname, clip in got.items():
                key = f'[IFP]/{aname}'
                if key in clips:
                    skipped += 1
                else:
                    clips[key] = clip
                    added += 1
            for aname, err in errs:
                failed.append({"ifp_file": f'[IFP]/{aname}', "error": err,
                               "ifp_sha256": hashlib.sha256(data).hexdigest(),
                               "ifp_bytes": len(data)})
    bank['multi_anim'] = {"added": added, "already_present": skipped, "failed": len(failed)}
    with open(bank_path, 'w') as f:
        json.dump(bank, f, separators=(',', ':'))
    return added, skipped, len(failed)

if __name__ == '__main__':
    for zp, bp in zip(sys.argv[1::2], sys.argv[2::2]):
        a, s, f = process_pack(zp, bp)
        print(f"{zp}: multi added={a} already_present={s} failed_total={f}")
