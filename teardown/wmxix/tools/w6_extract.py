#!/usr/bin/env python3
"""W6 WMXIX extraction driver — runs on the Oracle VM against the verified ISO.

Usage: python3 w6_extract.py <phase> [phase ...]
Phases: raw | caw-mesh | caw-tex | wrestler-tex | mpc | arenas | all-extract

Reads /data/wmxix/wmxix-rvz.iso (GW9E78, SHA1 4746c3b9... verified vs
archive.org). Writes to /data/wmxix/extracted/ (raw) and /data/wmxix/out/.
Reuses the western-heart decoders in /data/wmxix/tools-src/tools/:
  gcn_fst, extract_wrestlers (YOBJ batch/strip), decode_tpl,
  extract_arena_textures.parse_tex_container, extract_yanm (YANM decode).
"""
import sys, os, json, struct, math, hashlib

ISO = '/data/wmxix/wmxix-rvz.iso'
TOOLS = '/data/wmxix/tools-src/tools'
DOCS = '/data/wmxix/tools-src/docs'
RAW = '/data/wmxix/extracted'
OUT = '/data/wmxix/out'
sys.path.insert(0, TOOLS)

from gcn_fst import read_header, read_entries, flat_listing
import decode_tpl
from extract_arena_textures import parse_tex_container
import extract_wrestlers as ew
import extract_yanm as ey
import w6_decode2 as dec2


class ISOFile:
    def __init__(self, path=ISO):
        self.f = open(path, 'rb')
        h = read_header(self.f)
        assert h['game_id'] == 'GW9E78', h
        entries, names = read_entries(self.f, h['fst_off'], h['fst_size'])
        self.files = {p.strip('/'): (o, l)
                      for p, isdir, o, l in flat_listing(entries, names)
                      if not isdir}
        print(f'ISO: {len(self.files)} files')

    def read(self, path):
        o, l = self.files[path]
        self.f.seek(o)
        data = self.f.read(l)
        assert len(data) == l, f'short read {path}'
        return data

    def close(self):
        self.f.close()


def sha16(data):
    return hashlib.sha256(data).hexdigest()[:16]


# ---------------------------------------------------------------- raw
RAW_PREFIXES = ('edit_data/', 'model/', 'motion/', 'bg/', 'viewer/',
                'ringmotion/', 'Entrance/', 'paint_tool/')
RAW_FILES = ('menu/menu.mpq', 'menupause', 'com_dt.mpc', 'static.mpc',
             'static_jp.mpc', 'system.cfg', 'opening.bnr', 'nowload.tex',
             'pass8.tpl', 'ringmotion.txt', 'viewlist.txt')


def phase_raw(iso):
    n = 0
    for p in sorted(iso.files):
        if p.startswith(RAW_PREFIXES) or p in RAW_FILES:
            dest = os.path.join(RAW, p)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(iso.read(p))
            n += 1
    # main.dol lives outside the FST: header 0x420 = DOL offset, 0x424 = FST off
    iso.f.seek(0)
    hdr = iso.f.read(0x440)
    dol_off, = struct.unpack('>I', hdr[0x420:0x424])
    fst_off, = struct.unpack('>I', hdr[0x424:0x428])
    dol_size = fst_off - dol_off
    iso.f.seek(dol_off)
    dol = iso.f.read(dol_size)
    with open(os.path.join(RAW, 'main.dol'), 'wb') as f:
        f.write(dol)
    print(f'raw: {n} FST files + main.dol ({dol_size} B @ 0x{dol_off:X})')
    return n


# ---------------------------------------------------------------- CAW meshes
def decode_ymg_obj(data, out_path, header_lines):
    """YOBJ -> OBJ via the v2 CAW decoder (w6_decode2). Returns status dict."""
    r = dec2.decode_ymg_v2(data)
    if r['status'] != 'ok' and r['status'] != 'pool-scan':
        return {'status': r['status'], 'size': len(data),
                'version': r.get('version'),
                'dumy_wrapper': r.get('dumy_wrapper', False)}
    batches = r['batches']
    nv, nt = ew.write_obj(out_path, batches, header=header_lines +
                          [f"# decode: {r['method']} "
                           f"ver={r.get('version', 0):#x} "
                           f"dumy_wrapper={r.get('dumy_wrapper', False)}"])
    return {'status': r['status'], 'method': r['method'], 'size': len(data),
            'version': r.get('version'), 'batches': len(batches),
            'verts': nv, 'tris': nt,
            'dumy_wrapper': r.get('dumy_wrapper', False)}


def phase_caw_mesh(iso):
    ymgs = sorted(p for p in iso.files
                  if p.startswith('edit_data/MODEL/') and p.endswith('.ymg'))
    print(f'caw-mesh: {len(ymgs)} .ymg files')
    outdir = os.path.join(OUT, 'caw-mesh')
    manifest = {}
    counts = {}
    for i, p in enumerate(ymgs):
        data = iso.read(p)
        rel = p[len('edit_data/MODEL/'):]
        opath = os.path.join(outdir, rel[:-4] + '.obj')
        os.makedirs(os.path.dirname(opath), exist_ok=True)
        st = decode_ymg_obj(data, opath, [f'# WMXIX {p} -> strip OBJ (s16/64)',
                                          f'# sha256:{sha16(data)}'])
        manifest[p] = st
        counts[st['status']] = counts.get(st['status'], 0) + 1
        if (i + 1) % 200 == 0:
            print(f'  {i + 1}/{len(ymgs)} {counts}', flush=True)
    tot_v = sum(m.get('verts', 0) for m in manifest.values())
    tot_t = sum(m.get('tris', 0) for m in manifest.values())
    print(f'caw-mesh DONE: {counts} verts={tot_v} tris={tot_t}')
    with open(os.path.join(OUT, 'caw-mesh-manifest.json'), 'w') as f:
        json.dump({'counts': counts, 'total_verts': tot_v, 'total_tris': tot_t,
                   'files': manifest}, f, indent=1)
    return counts


# ---------------------------------------------------------------- textures
def normalize_tpl(tpl):
    """Accept TPL magic 0x0020AF30 and the 0x0120AF30 variant seen in CAW
    .tex entries (top byte is a version/flags byte; the rest of the header
    parses as standard TPL). Returns bytes with the magic forced to the
    canonical value, or None if not a TPL at all."""
    if len(tpl) < 4:
        return None
    if decode_tpl.u32(tpl, 0) & 0x00FFFFFF != 0x0020AF30:
        return None
    return b'\x00\x20\xaf\x30' + tpl[4:]


def decode_tex_file(data, outdir, base):
    """Decode one .tex file (container or raw TPL) -> PNGs. Returns entries."""
    results = []
    raw = normalize_tpl(data)
    if raw is not None:
        # raw TPL
        try:
            imgs = decode_tpl.parse_tpl(raw)
            for i, im in enumerate(imgs):
                img = decode_tpl.decode_image(raw, im)
                name = base if len(imgs) == 1 else f'{base}_img{i}'
                img.save(os.path.join(outdir, name + '.png'))
                results.append({'entry': name, 'w': im['width'],
                                'h': im['height'], 'fmt': im['format'],
                                'kind': 'raw-tpl'})
        except Exception as e:
            results.append({'entry': base, 'error': f'raw-tpl: {e}'})
        return results
    try:
        entries = parse_tex_container(data)
    except Exception as e:
        return [{'entry': base, 'error': f'container-parse: {e}'}]
    if not entries:
        return [{'entry': base, 'error': 'empty-container'}]
    for (name, magic, size, off) in entries:
        ename = name or base
        tpl = normalize_tpl(data[off:off + size])
        if tpl is None:
            results.append({'entry': ename, 'error': 'entry-not-tpl',
                            'magic': magic.decode('ascii', 'replace'),
                            'size': size})
            continue
        try:
            imgs = decode_tpl.parse_tpl(tpl)
            for i, im in enumerate(imgs):
                img = decode_tpl.decode_image(tpl, im)
                oname = ename if len(imgs) == 1 else f'{ename}_img{i}'
                img.save(os.path.join(outdir, oname + '.png'))
                results.append({'entry': oname, 'w': im['width'],
                                'h': im['height'], 'fmt': im['format'],
                                'kind': 'container'})
        except Exception as e:
            # Retry with the TPL read to end-of-file: a few entries declare
            # image/palette data that runs past the container's stated size.
            try:
                tpl2 = normalize_tpl(data[off:])
                imgs = decode_tpl.parse_tpl(tpl2)
                for i, im in enumerate(imgs):
                    img = decode_tpl.decode_image(tpl2, im)
                    oname = ename if len(imgs) == 1 else f'{ename}_img{i}'
                    img.save(os.path.join(outdir, oname + '.png'))
                    results.append({'entry': oname, 'w': im['width'],
                                    'h': im['height'], 'fmt': im['format'],
                                    'kind': 'container-fullbuf'})
            except Exception as e2:
                results.append({'entry': ename,
                                'error': f'tpl-decode: {e} / retry: {e2}'})
    return results


def phase_tex(iso, prefix, outname, manifest_name):
    texs = sorted(p for p in iso.files
                  if p.startswith(prefix) and p.endswith('.tex'))
    print(f'{outname}: {len(texs)} .tex files under {prefix}')
    outdir = os.path.join(OUT, outname)
    manifest = {}
    npng = nerr = 0
    for i, p in enumerate(texs):
        data = iso.read(p)
        rel = p[len(prefix):]
        tdir = os.path.join(outdir, os.path.dirname(rel))
        os.makedirs(tdir, exist_ok=True)
        base = os.path.basename(rel)[:-4]
        # one subdir per .tex file to avoid entry-name collisions
        fdir = os.path.join(tdir, base)
        os.makedirs(fdir, exist_ok=True)
        res = decode_tex_file(data, fdir, base)
        manifest[p] = res
        npng += sum(1 for r in res if 'w' in r)
        nerr += sum(1 for r in res if 'error' in r)
        if (i + 1) % 300 == 0:
            print(f'  {i + 1}/{len(texs)} png={npng} err={nerr}', flush=True)
    print(f'{outname} DONE: {len(texs)} tex files -> {npng} PNGs, {nerr} errors')
    with open(os.path.join(OUT, manifest_name), 'w') as f:
        json.dump({'tex_files': len(texs), 'pngs': npng, 'errors': nerr,
                   'files': manifest}, f, indent=1)
    return npng, nerr


# ---------------------------------------------------------------- move.mpc clips
def load_hashmap():
    m = json.load(open(os.path.join(DOCS, 'ycg-group-mapping.json')))
    h = {}
    for g in m['groups']:
        for hh in g['hashes']:
            h[hh] = {'anatomy': g['anatomy'], 'confidence': g['confidence']}
    return h


def decode_yanm_bytes(data, name, hashmap):
    """Bytes-based variant of extract_yanm.decode_yag (same math)."""
    size = len(data)
    if size < 0x50 + 29 * 32 or data[:4] != b'YANM':
        return {'file': name, 'size': size, 'stub': True,
                'note': 'too small or bad magic; not a decodable YANM clip'}
    hdr = {'payload_size': ey.u32(data, 0x04),
           'sec_per_tick': ey.f32(data, 0x3C),
           'params': [round(ey.f32(data, 0x40 + i * 4), 6) for i in range(3)]}
    tracks = []
    for r in range(29):
        o = 0x50 + r * 32
        h = f'{ey.u32(data, o):08X}'
        a = ey.u32(data, o + 4)
        ks = ey.u32(data, o + 8)
        triple = [round(ey.f32(data, o + 16 + i * 4), 9) for i in range(3)]
        w24 = ey.u32(data, o + 24)
        kw = ey.u32(data, o + 28)
        hm = hashmap.get(h)
        t = {'hash': h, 'dir_off': o,
             'anatomy': hm['anatomy'] if hm else 'UNRESOLVED',
             'confidence': hm['confidence'] if hm else 'NONE'}
        if a == 0:
            keys = ey.decode_single_keys(data[ks:ks + kw * 5]) if kw else []
            t.update(kind='single', nkeys=kw, keys=keys,
                     ticks=sum(k[0] for k in keys), static=not keys)
            if h in ey.LEG_HASHES and keys:
                t['half_angle_deg'] = ey.half_angle_series(keys)
        else:
            ca, cb = kw >> 16, kw & 0xFFFF
            head, akeys = ey.decode_dual_a(data, a, ca)
            bkeys = ey.decode_single_keys(data[ks:ks + cb * 5]) if cb else []
            t.update(kind='dual', ca=ca, cb=cb, a_head_hex=head,
                     a_keys=akeys, b_keys=bkeys,
                     a_ticks=sum(k[0] for k in akeys),
                     b_ticks=sum(k[0] for k in bkeys),
                     triple=triple, w24=w24)
        tracks.append(t)
    ticks = max([t.get('ticks', t.get('b_ticks', 0)) for t in tracks] + [0])
    return {'file': name, 'size': size, 'header': hdr,
            'n_tracks': len(tracks),
            'est_seconds': round(ticks * hdr['sec_per_tick'], 3)
                           if hdr['sec_per_tick'] else None,
            'tracks': tracks}


def phase_mpc(iso):
    idx = json.load(open(os.path.join(DOCS, 'WMXIX-MPC-INDEX.json')))
    meta = idx['_meta']
    data_start = int(meta['header']['data_start'], 16)
    mpc = iso.read('motion/move.mpc')
    assert len(mpc) == meta['file_size_bytes'], (len(mpc), meta)
    hashmap = load_hashmap()
    outdir = os.path.join(OUT, 'mpc-clips')
    os.makedirs(outdir, exist_ok=True)
    manifest = {}
    nok = nstub = nfail = 0
    total = sum(len(m['clips']) for m in idx['motions'])
    done = 0
    for motion in idx['motions']:
        mid = motion['motion_id']
        for clip in motion['clips']:
            sub = clip['sub']
            off = data_start + clip['data_offset']
            raw = mpc[off:off + clip['size_bytes']]
            name = f'{mid}_{sub}'
            try:
                dec = decode_yanm_bytes(raw, f'move.mpc:{mid}/{sub}', hashmap)
            except Exception as e:
                manifest[name] = {'motion_id': mid, 'sub': sub,
                                  'size_bytes': clip['size_bytes'],
                                  'status': 'FAIL', 'error': str(e)}
                nfail += 1
                continue
            dec['motion_id'] = mid
            dec['sub'] = sub
            dec['mpc_offset'] = off
            with open(os.path.join(outdir, name + '.json'), 'w') as f:
                json.dump(dec, f, separators=(',', ':'))
            if dec.get('stub'):
                nstub += 1
                manifest[name] = {'motion_id': mid, 'sub': sub,
                                  'size_bytes': clip['size_bytes'],
                                  'status': 'stub',
                                  'est_seconds': dec.get('est_seconds')}
            else:
                nok += 1
                manifest[name] = {'motion_id': mid, 'sub': sub,
                                  'size_bytes': clip['size_bytes'],
                                  'status': 'ok',
                                  'est_seconds': dec.get('est_seconds'),
                                  'sec_per_tick': dec['header']['sec_per_tick']}
            done += 1
            if done % 400 == 0:
                print(f'  {done}/{total} ok={nok} stub={nstub} fail={nfail}',
                      flush=True)
    print(f'mpc DONE: {total} clips ok={nok} stub={nstub} fail={nfail}')
    with open(os.path.join(OUT, 'mpc-clips-manifest.json'), 'w') as f:
        json.dump({'total': total, 'ok': nok, 'stub': nstub, 'fail': nfail,
                   'clips': manifest}, f, indent=1)
    return nok, nstub, nfail


def main():
    phases = sys.argv[1:] or ['all-extract']
    iso = ISOFile()
    os.makedirs(OUT, exist_ok=True)
    if 'all-extract' in phases:
        phases = ['raw', 'caw-mesh', 'caw-tex', 'wrestler-tex', 'mpc']
    for ph in phases:
        if ph == 'raw':
            phase_raw(iso)
        elif ph == 'caw-mesh':
            phase_caw_mesh(iso)
        elif ph == 'caw-tex':
            phase_tex(iso, 'edit_data/TEX/', 'caw-tex', 'caw-tex-manifest.json')
        elif ph == 'wrestler-tex':
            phase_tex(iso, 'model/wrestler/', 'wrestler-tex',
                      'wrestler-tex-manifest.json')
        elif ph == 'mpc':
            phase_mpc(iso)
        else:
            print(f'unknown phase: {ph}')
    iso.close()
    print('ALL DONE')


if __name__ == '__main__':
    main()
