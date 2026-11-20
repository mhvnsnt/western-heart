#!/usr/bin/env python3
"""WMXIX texture remainder decoder — Creation Suite gap-fill Job 2 (2026-10-20).

Worker A's converter (customization/tools/convert_caw_parts.py, PR #398)
decoded 1,044 of the 1,470 WMXIX .tex textures: it scans each .tex for the
standard GameCube TPL magic bytes 00 20 AF 30 and decodes the first hit.
The remaining 446 catalog entries were left as blocked_no_tpl (426),
not_converted (12) and palette_only (8). This tool finishes that batch.
Forensic findings (measured on the files, 2026-10-20 — see the Job 2
conversion report in customization/parts-converted/):

  * .tex is a little-endian CONTAINER, not a bare TPL:
      u32 entry_count, 12 header bytes, then entry_count x 32-byte
      directory records {name[16], type[4]="tpl", u32 size, u32 offset,
      u32 pad}, payloads at the recorded offsets.
    Every entry of every blocked .tex carries a TPL whose magic is
    01 20 AF 30 instead of 00 20 AF 30 — a variant header byte the first
    pass's byte-scan could not see. All blocked entries are format 9
    (C8, 256-entry palette; palette formats IA8 / RGB5A3 / RGB565 all
    occur). Payload layout after the magic is byte-identical to a
    standard TPL, so the validated decoder (teardown/wmxix/decode_tpl.py,
    tile code vendored here the same way convert_caw_parts.py vendored
    it) decodes them once the variant magic is accepted. Many of these
    are makeup / face-option overlays whose pixel data is a single
    palette index (a faithful near-blank image, e.g. a "none" option) —
    that is the source data, not a decode failure.
    Rule (mirrors convert_caw_parts.py): decode the container's FIRST
    directory entry's first image -> one PNG per .tex.

  * The 12 not_converted leftovers in textures/Woman/Face/tq0_417 (+
    its faces/ twin script) are a mixed build folder:
      - 2 standalone .tpl files: standard TPL, decode directly.
      - 2 .tga files: truecolor TGA, decode via PIL.
      - 1 .tm2 file: PS2 TIM2, 64x32 8-bit indexed, 256-color RGBA32
        CLUT. Pixels are linear; the CLUT is stored in PS2 CSM1 order
        (middle two 8-entry groups swapped per 32) — verified against
        the sibling .tga of the same texture (mean abs channel diff
        1.13 with CSM1 unswizzle vs 3.53 without). Alpha is PS2-style
        (0x80 = opaque), scaled x2 capped at 255.
      - 2 .psd files: real Photoshop composites (8BPS v1, RLE). One
        opens in PIL; the other (256x128, 5 channels) PIL rejects, so
        a minimal PackBits composite reader is included (channels 0-2
        = RGB, channel 3 = alpha; extra spot channels ignored).
      - 1 script.txt: a 3D MAX build path list. Not an image.
      - 3 .ymm files (hair/.../c0.ymm): YOBJ mesh data (magic "YOBJ"),
        the same unsolved mesh family as .ymg. Not textures.
      - 1 .tpg file: a texture-page index listing sibling file paths
        (embedded strings name c3_c_00l.tga / c3_c_00.tm2). Not an image.

  * The 8 palette_only .ycg files (colors/COL/) are YCG color/gradient
    data records (no image header, no dimensions, sizes 228-2356 B in
    a repeating 4-file pattern). They are palette DATA consumed with a
    mesh, not standalone textures; status stays palette_only with the
    reason recorded in the catalog entry's detail field.

Outputs mirror convert_caw_parts.py: PNGs under
customization/parts-converted/wmxix-textures/<path under
customization/parts/wmxix/textures/> with the stem kept and the
extension replaced by .png (the .tm2 output keeps a .tm2.png suffix
because the same stem's .tga decodes to the plain .png name — both are
kept, neither clobbers the other).
CATALOG.json is updated in place: converted entries get
status="converted" + a texture field (the exact shape Worker A used);
entries that stay blocked keep their status and gain a detail field
with the proven reason. Per-file records are appended to
customization/parts-converted/convert-log.jsonl.

NOTE (pre-existing converter limitation, flagged not fixed here):
convert_caw_parts.py build_catalog() regenerates the leftover entries
(.tpl/.tga/.tm2/.psd/.ymm/.txt/.tpg) with a hardcoded not_converted
status, so a full rebuild with that tool would revert those entries'
catalog status even though their PNGs and log records exist. The
blocked_no_tpl (.tex) entries DO survive a rebuild via the log.

Writes are verified (re-open + size check) and retried: this VM has an
intermittent write-denial fault (Errno 1 on flush) that silently
truncates files, so no write is trusted without read-back.

Usage:
  python3 decode_wmxix_tex_remainder.py [--force] [--only <substr>]
"""
import io, json, os, struct, subprocess, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CUSTOM = os.path.dirname(HERE)
REPO = os.path.dirname(CUSTOM)
PARTS = os.path.join(CUSTOM, 'parts')
OUT = os.path.join(CUSTOM, 'parts-converted')
CATALOG = os.path.join(OUT, 'CATALOG.json')
LOG = os.path.join(OUT, 'convert-log.jsonl')
SRC_TEX_ROOT = os.path.join(PARTS, 'wmxix', 'textures')
DST_TEX_ROOT = os.path.join(OUT, 'wmxix-textures')

TARGET_STATUSES = ('blocked_no_tpl', 'not_converted', 'palette_only')


def rel(p):
    return os.path.relpath(p, REPO).replace(os.sep, '/')


# ------------------------------------------------------------ safe writes
def write_verified(path, data: bytes, tries=8):
    """Write bytes and prove it by read-back; retry, then perl fallback.

    The VM intermittently denies flushes (Errno 1) leaving 0-byte files.
    A write only counts when the bytes read back identical.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for i in range(tries):
        try:
            with open(path, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            with open(path, 'rb') as f:
                if f.read() == data:
                    return True
        except Exception:
            pass
        time.sleep(0.5 * (i + 1))
    # Fallback: hand the bytes to perl over a pipe (a writer that has
    # proven reliable while python file writes are being denied).
    script = ('local $/; my $d=<STDIN>; open(F,">",$ARGV[0]) or die $!;'
              ' binmode F; print F $d; close F;'
              ' my $s=-s $ARGV[0]; print $s;')
    try:
        r = subprocess.run(['perl', '-e', script, path], input=data,
                           capture_output=True, timeout=60)
        if r.returncode == 0 and int(r.stdout.strip() or 0) == len(data):
            with open(path, 'rb') as f:
                return f.read() == data
    except Exception:
        pass
    return False


def save_png_verified(img, path):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return write_verified(path, buf.getvalue())


# ------------------------------------------- TPL decoding (vendored from
# teardown/wmxix/decode_tpl.py via convert_caw_parts.py, identical tile
# math; the only extension is accepting the 01 20 AF 30 variant magic)
def _u16(b, i): return struct.unpack('>H', b[i:i + 2])[0]
def _u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def _rgb5a3(px):
    if px & 0x8000:
        r = (px >> 10) & 0x1F; g = (px >> 5) & 0x1F; b = px & 0x1F
        return (r * 255 // 31, g * 255 // 31, b * 255 // 31, 255)
    a = (px >> 12) & 0x7; r = (px >> 8) & 0xF; g = (px >> 4) & 0xF; b = px & 0xF
    return (r * 17, g * 17, b * 17, a * 255 // 7)

def _rgb565(px):
    r = (px >> 11) & 0x1F; g = (px >> 5) & 0x3F; b = px & 0x1F
    return (r * 255 // 31, g * 255 // 63, b * 255 // 31, 255)

def _ia8(px): return (px & 0xFF,) * 3 + ((px >> 8),)
def _ia4(px):
    a = (px >> 4) & 0xF; i = px & 0xF
    return (i * 17, i * 17, i * 17, a * 17)

_PAL = {0: _ia8, 1: _rgb565, 2: _rgb5a3}
_TILE = {0: (8, 8, 32), 1: (8, 4, 32), 2: (8, 4, 32), 3: (4, 4, 64),
         4: (4, 4, 32), 5: (4, 4, 32), 6: (4, 4, 64),
         8: (8, 8, 32), 9: (8, 4, 32), 10: (8, 4, 32), 14: (8, 8, 32)}
TPL_MAGICS = (0x0020AF30, 0x0120AF30)


def _tile(data, off, fmt, pal):
    if fmt == 0:
        px = []
        for i in range(32):
            b = data[off + i]
            v = (b >> 4) * 17; px.append((v, v, v, 255))
            v = (b & 0xF) * 17; px.append((v, v, v, 255))
        return px
    if fmt == 1:
        return [(b, b, b, 255) for b in data[off:off + 32]]
    if fmt == 2:
        return [_ia4(b) for b in data[off:off + 32]]
    if fmt == 3:
        return [_ia8(_u16(data, off + i * 2)) for i in range(32)]
    if fmt == 4:
        return [_rgb565(_u16(data, off + i * 2)) for i in range(16)]
    if fmt == 5:
        return [_rgb5a3(_u16(data, off + i * 2)) for i in range(16)]
    if fmt == 6:
        px = []
        for i in range(16):
            a = data[off + i * 2]; r = data[off + i * 2 + 1]
            b = data[off + 32 + i * 2]; g = data[off + 32 + i * 2 + 1]
            px.append((r, g, b, a))
        return px
    if fmt in (8, 9, 10):
        tw, th = (8, 8) if fmt == 8 else (8, 4)
        raw = data[off:off + tw * th * (4 if fmt == 8 else 8) // 8]
        idx = []
        if fmt == 8:
            for b in raw:
                idx += [b >> 4, b & 0xF]
        else:
            idx = list(raw)
        return [pal[i] for i in idx]
    if fmt == 14:
        px = [(0, 0, 0, 0)] * 64
        for s in range(4):
            so = off + s * 8
            c0 = _rgb565(_u16(data, so)); c1 = _rgb565(_u16(data, so + 2))
            bits = _u32(data, so + 4)
            if _u16(data, so) > _u16(data, so + 2):
                lut = [c0, c1,
                       tuple((2 * c0[i] + c1[i]) // 3 for i in range(3)) + (255,),
                       tuple((c0[i] + 2 * c1[i]) // 3 for i in range(3)) + (255,)]
            else:
                lut = [c0, c1, tuple((c0[i] + c1[i]) // 2 for i in range(3)) + (255,),
                       (0, 0, 0, 0)]
            for p in range(16):
                c = lut[(bits >> (p * 2)) & 3]
                px[(s // 2) * 4 * 8 + (p // 4) * 8 + (s % 2) * 4 + p % 4] = c
        return px
    raise ValueError(f'unsupported TPL format {fmt}')


def decode_tpl_bytes(data):
    """Decode the first image of a TPL payload (standard or variant magic)."""
    from PIL import Image
    magic = _u32(data, 0)
    if magic not in TPL_MAGICS:
        raise ValueError(f'not a TPL payload (magic 0x{magic:08x})')
    n = _u32(data, 4); toff = _u32(data, 8)
    if n < 1:
        raise ValueError('TPL with zero images')
    h = _u32(data, toff)
    height, width = _u16(data, h), _u16(data, h + 2)
    fmt = _u32(data, h + 4); doff = _u32(data, h + 8)
    pal = None
    if fmt in (8, 9, 10):
        ph = h + 36
        nent = _u16(data, ph); pfmt = _u32(data, ph + 4); poff = _u32(data, ph + 8)
        dec = _PAL[pfmt]
        pal = [dec(_u16(data, poff + i * 2)) for i in range(nent)]
    tw, th, tb = _TILE[fmt]
    img = Image.new('RGBA', (width, height))
    px = img.load()
    off = doff
    for ty in range(0, height, th):
        for tx in range(0, width, tw):
            tile = _tile(data, off, fmt, pal)
            off += tb
            for y in range(th):
                for x in range(tw):
                    if tx + x < width and ty + y < height:
                        px[tx + x, ty + y] = tile[y * tw + x]
    return img


def tex_container_entries(data):
    """Parse a .tex container directory -> [(name, payload_bytes), ...]."""
    if len(data) < 16:
        raise ValueError('.tex too small for a container header')
    count = struct.unpack('<I', data[0:4])[0]
    if count < 1 or count > 4096:
        raise ValueError(f'.tex directory count implausible: {count}')
    entries = []
    for i in range(count):
        off = 16 + i * 32
        if off + 32 > len(data):
            raise ValueError('.tex directory overruns file')
        name = data[off:off + 16].split(b'\x00')[0].decode('ascii', 'replace')
        typ = data[off + 16:off + 20].split(b'\x00')[0].decode('ascii', 'replace')
        size, poff = struct.unpack('<II', data[off + 20:off + 28])
        if poff + size > len(data):
            raise ValueError(f'.tex entry {name} overruns file')
        entries.append((name, typ, data[poff:poff + size]))
    return entries


def decode_tex_container(data):
    """First directory entry's first TPL image (mirrors the PR #398 rule)."""
    entries = tex_container_entries(data)
    for name, typ, payload in entries[:1]:
        if typ != 'tpl':
            raise ValueError(f'first .tex entry type is {typ!r}, not tpl')
        return decode_tpl_bytes(payload)
    raise ValueError('.tex with no entries')


# ------------------------------------------------------------- TIM2 (PS2)
def _csm1_index(i):
    """PS2 CSM1 palette order: per 32 entries, the middle two groups of
    8 are swapped (entries 8-15 <-> 16-23)."""
    block, r = i & ~31, i & 31
    if 8 <= r < 16:
        r += 8
    elif 16 <= r < 24:
        r -= 8
    return block + r


def decode_tm2(data):
    from PIL import Image
    if data[:4] != b'TIM2':
        raise ValueError('not TIM2')
    npics = struct.unpack('<H', data[6:8])[0]
    if npics != 1:
        raise ValueError(f'TIM2 with {npics} pictures (only 1 supported)')
    total, clut_size, img_size = struct.unpack('<III', data[16:28])
    hdr_size, clut_colors = struct.unpack('<HH', data[28:32])
    img_type = data[35]
    width, height = struct.unpack('<HH', data[36:40])
    if img_type != 5:
        raise ValueError(f'TIM2 image type {img_type} (only 5 = 8-bit indexed supported)')
    off = 16 + hdr_size
    imgdata = data[off:off + img_size]
    clut = data[off + img_size:off + img_size + clut_size]
    if len(imgdata) < width * height or len(clut) < clut_colors * 4:
        raise ValueError('TIM2 payload truncated')
    pal = []
    for i in range(clut_colors):
        r, g, b, a = clut[i * 4:i * 4 + 4]
        pal.append((r, g, b, min(255, a * 2)))
    pal = [pal[_csm1_index(i)] for i in range(len(pal))]
    img = Image.new('RGBA', (width, height))
    px = img.load()
    for y in range(height):
        for x in range(width):
            px[x, y] = pal[imgdata[y * width + x]]
    return img


# --------------------------------------------- PSD composite (RLE only)
def _packbits(buf, expected):
    out = bytearray(); i = 0
    while i < len(buf) and len(out) < expected:
        n = buf[i]; i += 1
        if n < 128:
            out += buf[i:i + n + 1]; i += n + 1
        elif n > 128:
            out += bytes([buf[i]]) * (257 - n); i += 1
    return bytes(out[:expected])


def decode_psd_composite(data):
    """Minimal PSD merged-image reader for RLE-compressed composites
    (PIL rejects the 256x128 5-channel source in this batch). Channels
    0-2 are R/G/B, channel 3 (when present) is alpha; spot channels
    beyond alpha are not part of the composite color."""
    from PIL import Image
    if data[:4] != b'8BPS':
        raise ValueError('not PSD')
    chans = struct.unpack('>H', data[12:14])[0]
    height, width = struct.unpack('>II', data[14:22])
    depth, mode = struct.unpack('>HH', data[22:26])
    if depth != 8 or mode != 3:
        raise ValueError(f'PSD depth/mode {depth}/{mode} (only 8-bit RGB supported)')
    p = 26
    for _ in range(3):
        ln = struct.unpack('>I', data[p:p + 4])[0]; p += 4 + ln
    comp = struct.unpack('>H', data[p:p + 2])[0]; p += 2
    if comp != 1:
        raise ValueError(f'PSD compression {comp} (only 1 = RLE supported)')
    counts = struct.unpack('>%dH' % (chans * height),
                           data[p:p + 2 * chans * height])
    p += 2 * chans * height
    planes = []
    for c in range(chans):
        plane = bytearray()
        for r in range(height):
            cnt = counts[c * height + r]
            plane += _packbits(data[p:p + cnt], width); p += cnt
        planes.append(bytes(plane))
    img = Image.new('RGBA', (width, height))
    px = img.load()
    for y in range(height):
        for x in range(width):
            i = y * width + x
            a = planes[3][i] if chans >= 4 else 255
            px[x, y] = (planes[0][i], planes[1][i], planes[2][i], a)
    return img


# ---------------------------------------------------------------- batch
STILL_BLOCKED_DETAILS = {
    '.txt': 'Build script (3D MAX source path list), not image data — '
            'nothing to decode (Job 2 forensic inspection, 2026-10-20).',
    '.ymm': 'YOBJ mesh data (magic "YOBJ") — mesh family, not a texture; '
            'blocked on the same unsolved YOBJ assembly as .ymg parts.',
    '.tpg': 'Texture-page index file: 91% zero bytes; embedded strings '
            'list sibling texture paths (c3_c_00l.tga, c3_c_00.tm2). '
            'No pixel or palette data — nothing to decode.',
    '.ycg': 'YCG color/gradient data records (no image header or '
            'dimensions; file sizes 228-2356 B in a repeating 4-file '
            'pattern). Palette data consumed with a mesh, not a '
            'standalone texture — status palette_only stands.',
}


def dst_for(origin_rel, keep_ext_suffix=False):
    """Mirror a source path under parts/wmxix/textures/ into
    parts-converted/wmxix-textures/, replacing the extension with .png
    (or .<ext>.png when keep_ext_suffix)."""
    sub = os.path.relpath(origin_rel, 'customization/parts/wmxix/textures')
    stem, ext = os.path.splitext(sub)
    name = stem + (ext + '.png' if keep_ext_suffix else '.png')
    return os.path.join(DST_TEX_ROOT, name)


def convert_entry(entry):
    """Return (img_or_None, note) for a target catalog entry."""
    origin = entry['origin_file']
    src = os.path.join(REPO, origin)
    ext = os.path.splitext(origin)[1].lower()
    data = open(src, 'rb').read()
    if entry['status'] == 'blocked_no_tpl' or ext == '.tex':
        return decode_tex_container(data), 'tex-container first TPL (variant magic accepted)'
    if ext == '.tpl':
        return decode_tpl_bytes(data), 'standalone TPL'
    if ext == '.tga':
        from PIL import Image
        img = Image.open(io.BytesIO(data)); img.load()
        return img.convert('RGBA'), 'TGA via PIL'
    if ext == '.tm2':
        return decode_tm2(data), 'TIM2 indexed8 + CSM1 CLUT'
    if ext == '.psd':
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(data)); img.load()
            return img.convert('RGBA'), 'PSD via PIL'
        except Exception:
            return decode_psd_composite(data), 'PSD RLE composite reader'
    return None, STILL_BLOCKED_DETAILS.get(ext, f'no decoder for {ext}')


def main():
    force = '--force' in sys.argv
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    catalog = json.load(open(CATALOG))
    parts = catalog['parts']
    targets = [e for e in parts if e.get('source_game') == 'wmxix'
               and e.get('status') in TARGET_STATUSES
               and (only is None or only in e['origin_file'])]
    print(f'targets: {len(targets)}')
    converted = blocked = failed = 0
    reasons = Counter()
    details = {}
    log_records = []
    for e in targets:
        origin = e['origin_file']
        ext = os.path.splitext(origin)[1].lower()
        dst = dst_for(origin, keep_ext_suffix=(ext == '.tm2'))
        if e['status'] in ('not_converted', 'palette_only') and \
                ext in STILL_BLOCKED_DETAILS:
            e['detail'] = STILL_BLOCKED_DETAILS[ext]
            blocked += 1
            reasons[ext] += 1
            log_records.append({'origin_file': origin, 'status': e['status'],
                                'detail': e['detail'],
                                'tool': 'decode_wmxix_tex_remainder.py'})
            continue
        if not force and e.get('status') == 'converted':
            continue
        try:
            img, note = convert_entry(e)
        except Exception as ex:
            failed += 1
            reasons[f'failed:{ext}'] += 1
            details[origin] = repr(ex)
            log_records.append({'origin_file': origin, 'status': 'failed',
                                'detail': repr(ex),
                                'tool': 'decode_wmxix_tex_remainder.py'})
            continue
        if img is None:
            e['detail'] = note
            blocked += 1
            reasons[ext] += 1
            log_records.append({'origin_file': origin, 'status': e['status'],
                                'detail': note,
                                'tool': 'decode_wmxix_tex_remainder.py'})
            continue
        if not save_png_verified(img, dst):
            failed += 1
            reasons['write_failed'] += 1
            details[origin] = 'write verification failed after retries'
            continue
        e['status'] = 'converted'
        e['texture'] = rel(dst)
        e.pop('detail', None)
        converted += 1
        reasons[f'converted:{ext}'] += 1
        log_records.append({'origin_file': origin, 'status': 'converted',
                            'texture': rel(dst), 'size': list(img.size),
                            'tool': 'decode_wmxix_tex_remainder.py',
                            'detail': note})
    if write_verified(CATALOG, (json.dumps(catalog, indent=1) + '\n').encode()):
        print('catalog updated')
    else:
        print('CATALOG WRITE FAILED'); return 1
    if log_records:
        blob = ''.join(json.dumps(r) + '\n' for r in log_records).encode()
        old = open(LOG, 'rb').read() if os.path.exists(LOG) else b''
        if write_verified(LOG, old + blob):
            print(f'log appended: {len(log_records)} records')
        else:
            print('LOG WRITE FAILED'); return 1
    print(f'converted={converted} still_blocked={blocked} failed={failed}')
    print('reasons:', dict(reasons))
    if details:
        print('failure details:', json.dumps(details, indent=1)[:2000])
    return 0 if failed == 0 else 2


if __name__ == '__main__':
    sys.exit(main())
