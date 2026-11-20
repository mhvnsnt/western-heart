#!/usr/bin/env python3
"""Urban Reign char PPK texture extractor — THE CRACK (Phase 3 Attempt 6).

THE FORMAT (proven end-to-end on char001; proof renders viewed:
two hands, and the fighter's face in real colors):

1. UPLOAD DESCRIPTOR TABLE in the type-0x0002 chunk's post-vertex
   region: 128-byte packets, each a literal DMA/GIF upload program:
     [DMA CNT tag QWC=6][GIFtag PACKED NLOOP=4 NREG=1 A+D]
     [A+D BITBLTBUF][A+D TRXPOS=0][A+D TRXREG w,h][A+D TRXDIR=0]
     [GIFtag IMAGE nloop][DMA REF tag: QWC, src_addr]
   A+D register address is at qword BYTE 8 in these packets
   (data u64, addr u32, pad u32). Every upload is PSMCT32-shaped
   (DPSM=0): bytes = w*h*4 = IMAGE QWC*16 = REF QWC*16 (all checked).
   REF src_addr values tile a contiguous pool with zero gaps.
2. DRAW DESCRIPTOR TABLE: A+D TEX1_1/TEX0_1 register pairs (same
   byte-8 framing). TEX0.PSM is 19 (PSMT8) or 20 (PSMT4) — the real
   textures are INDEXED. TEX0.TBP0 == the image upload's BITBLTBUF
   DBP; TEX0.CBP == the CLUT upload's DBP. CLUT uploads are the
   16x16 transfers (256 RGBA entries, PSMT8) and 8x2 transfers
   (16 RGBA entries, PSMT4); CLUT entries are stored LINEAR RGBA
   in the pool.
3. PIXEL POOL: REF src_addr is relative to a per-file pool base
   (char001: 0x57480). This tool DISCOVERS the base per file by
   sliding it and scoring CLUT-likeness (alpha byte in {0xFF,0x80})
   over all CLUT-upload REF offsets — the true base is the sharp
   argmax (char001: 0.656 at 0x57480, exact CLUT start verified).
4. DECODE = composed GS mapping (this is the part that makes the
   images come out right): the loader's CT32-shaped transfer writes
   each stream word to its CT32-swizzled VRAM address; the draw
   samples the same VRAM as PSMT8/PSMT4. So:
     pixel(x,y) -> PSM addr A -> VRAM word A>>2 (T8) / A>>3 (T4
     nibbles) -> inverse-CT32 map over the transfer rect -> stream
     word -> byte/nibble -> CLUT entry -> RGBA.
   Image dims: PSMT8: w = TBW*64, h = bytes/w. PSMT4: w = TBW*64,
   h = bytes*2/w. (char001 proof: 64x64 transfer -> 128x128 PSMT8
   hands; 128x128 transfer -> 256x256 PSMT8 face.)
   Swizzle tables: canonical GS tables as published in the
   urban-reign-recomp project's GS memory headers (GPL project;
   tables are Sony GS hardware facts, re-typed here).

Usage: ur_tex_extract.py <charXXX.ppk> <outdir>
Writes decoded PNGs + <name>-textures.json inventory. Stdlib only.
"""
import struct, sys, os, json, zlib, collections

BT = [[0,1,4,5,16,17,20,21],[2,3,6,7,18,19,22,23],
      [8,9,12,13,24,25,28,29],[10,11,14,15,26,27,30,31]]
CT32 = [[0,1,4,5,8,9,12,13],[2,3,6,7,10,11,14,15],
        [16,17,20,21,24,25,28,29],[18,19,22,23,26,27,30,31],
        [32,33,36,37,40,41,44,45],[34,35,38,39,42,43,46,47],
        [48,49,52,53,56,57,60,61],[50,51,54,55,58,59,62,63]]
CT8 = [[0,4,16,20,32,36,48,52,2,6,18,22,34,38,50,54],
       [8,12,24,28,40,44,56,60,10,14,26,30,42,46,58,62],
       [33,37,49,53,1,5,17,21,35,39,51,55,3,7,19,23],
       [41,45,57,61,9,13,25,29,43,47,59,63,11,15,27,31],
       [96,100,112,116,64,68,80,84,98,102,114,118,66,70,82,86],
       [104,108,120,124,72,76,88,92,106,110,122,126,74,78,90,94],
       [65,69,81,85,97,101,113,117,67,71,83,87,99,103,115,119],
       [73,77,89,93,105,109,121,125,75,79,91,95,107,111,123,127],
       [128,132,144,148,160,164,176,180,130,134,146,150,162,166,178,182],
       [136,140,152,156,168,172,184,188,138,142,154,158,170,174,186,190],
       [161,165,177,181,129,133,145,149,163,167,179,183,131,135,147,151],
       [169,173,185,189,137,141,153,157,171,175,187,191,139,143,155,159],
       [224,228,240,244,192,196,208,212,226,230,242,246,194,198,210,214],
       [232,236,248,252,200,204,216,220,234,238,250,254,202,206,218,222],
       [193,197,209,213,225,229,241,245,195,199,211,215,227,231,243,247],
       [201,205,217,221,233,237,249,253,203,207,219,223,235,239,251,255]]
BT4 = [[0,2,8,10],[1,3,9,11],[4,6,12,14],[5,7,13,15],
       [16,18,24,26],[17,19,25,27],[20,22,28,30],[21,23,29,31]]
CT4 = [[0,8,32,40,64,72,96,104,2,10,34,42,66,74,98,106,4,12,36,44,68,76,100,108,6,14,38,46,70,78,102,110],
       [16,24,48,56,80,88,112,120,18,26,50,58,82,90,114,122,20,28,52,60,84,92,116,124,22,30,54,62,86,94,118,126],
       [65,73,97,105,1,9,33,41,67,75,99,107,3,11,35,43,69,77,101,109,5,13,37,45,71,79,103,111,7,15,39,47],
       [81,89,113,121,17,25,49,57,83,91,115,123,19,27,51,59,85,93,117,125,21,29,53,61,87,95,119,127,23,31,55,63],
       [192,200,224,232,128,136,160,168,194,202,226,234,130,138,162,170,196,204,228,236,132,140,164,172,198,206,230,238,134,142,166,174],
       [208,216,240,248,144,152,176,184,210,218,242,250,146,154,178,186,212,220,244,252,148,156,180,188,214,222,246,254,150,158,182,190],
       [129,137,161,169,193,201,225,233,131,139,163,171,195,203,227,235,133,141,165,173,197,205,229,237,135,143,167,175,199,207,231,239],
       [145,153,177,185,209,217,241,249,147,155,179,187,211,219,243,251,149,157,181,189,213,221,245,253,151,159,183,191,215,223,247,255],
       [256,264,288,296,320,328,352,360,258,266,290,298,322,330,354,362,260,268,292,300,324,332,356,364,262,270,294,302,326,334,358,366],
       [272,280,304,312,336,344,368,376,274,282,306,314,338,346,370,378,276,284,308,316,340,348,372,380,278,286,310,318,342,350,374,382],
       [321,329,353,361,257,265,289,297,323,331,355,363,259,267,291,299,325,333,357,365,261,269,293,301,327,335,359,367,263,271,295,303],
       [337,345,369,377,273,281,305,313,339,347,371,379,275,283,307,315,341,349,373,381,277,285,309,317,343,351,375,383,279,287,311,319],
       [448,456,480,488,384,392,416,424,450,458,482,490,386,394,418,426,452,460,484,492,388,396,420,428,454,462,486,494,390,398,422,430],
       [464,472,496,504,400,408,432,440,466,474,498,506,402,410,434,442,468,476,500,508,404,412,436,444,470,478,502,510,406,414,438,446],
       [385,393,417,425,449,457,481,489,387,395,419,427,451,459,483,491,389,397,421,429,453,461,485,493,391,399,423,431,455,463,487,495],
       [401,409,433,441,465,473,497,505,403,411,435,443,467,475,499,507,405,413,437,445,469,477,503,511,407,415,439,447,471,479,503,511]]

def ct32_addr(x, y, bw):
    page = (y >> 5)*(bw >> 6) + (x >> 6)
    return page*2048 + BT[(y >> 3) & 3][(x >> 3) & 7]*64 + CT32[y & 7][x & 7]

def psmt8_addr(x, y, tbw):
    ppr = max(tbw >> 1, 1)
    page = (y >> 6)*ppr + (x >> 7)
    return page*8192 + BT[(y >> 4) & 3][(x >> 4) & 7]*256 + CT8[y & 15][x & 15]

def psmt4_addr(x, y, tbw):  # returns NIBBLE address
    ppr = max(tbw >> 1, 1)
    page = (y >> 7)*ppr + (x >> 7)
    blk = BT4[(y >> 4) & 7][(x >> 5) & 3]
    return page*16384 + blk*512 + CT4[y & 15][x & 31]

def parse_tag(q):
    lo, hi = struct.unpack('<QQ', q)
    return {'nloop': lo & 0x7FFF, 'eop': (lo >> 15) & 1,
            'flg': (lo >> 58) & 3, 'nregf': (lo >> 60) & 0xF,
            'regs': [(hi >> (4*k)) & 0xF for k in range(16)]}

def find_uploads(d):
    out = []
    for i in range(16, len(d)-112, 16):
        t = parse_tag(d[i:i+16])
        if not (t['nloop'] == 4 and t['flg'] == 0 and t['nregf'] == 1
                and t['regs'][0] == 0x0E):
            continue
        if [d[i+16+k*16+8] for k in range(4)] != [0x50, 0x51, 0x52, 0x53]:
            continue
        bb = struct.unpack('<Q', d[i+16:i+24])[0]
        tr = struct.unpack('<Q', d[i+48:i+56])[0]
        t2 = parse_tag(d[i+80:i+96])
        ref = struct.unpack('<4I', d[i+96:i+112])
        w, h = tr & 0xFFF, (tr >> 32) & 0xFFF
        if t2['flg'] != 2:
            continue
        out.append({'packet_off': i, 'dbp': (bb >> 32) & 0x3FFF,
                    'dbw': (bb >> 48) & 0x3F, 'dpsm': (bb >> 56) & 0x3F,
                    'trx_w': w, 'trx_h': h, 'bytes': t2['nloop']*16,
                    'src_ref': ref[1],
                    'size_check': w*h*4 == t2['nloop']*16})
    uniq = {}
    for p in out:
        uniq.setdefault(p['src_ref'], p)
    return out, sorted(uniq.values(), key=lambda p: p['src_ref'])

def find_tex0s(d):
    out, seen = [], set()
    for i in range(0, len(d)-16, 4):
        if d[i+8] == 0x06 and d[i+9:i+16] == b'\x00'*7:
            v = struct.unpack('<Q', d[i:i+8])[0]
            t = {'TBP0': v & 0x3FFF, 'TBW': (v >> 14) & 0x3F,
                 'PSM': (v >> 20) & 0x3F, 'TW': (v >> 26) & 0xF,
                 'TH': (v >> 30) & 0xF, 'CBP': (v >> 37) & 0x3FFF,
                 'CPSM': (v >> 51) & 0xF}
            key = (t['TBP0'], t['CBP'], t['PSM'], t['TBW'])
            if (t['PSM'] in (19, 20) and t['TBW'] > 0 and key not in seen):
                seen.add(key); out.append(t)
    return out

def discover_base(d, clut_refs):
    n = len(d)
    flag = [0]*(n//4 + 1)
    for i in range(n//4):
        flag[i+1] = flag[i] + (1 if d[4*i+3] in (0xFF, 0x80) else 0)
    maxoff = max(o + s for o, s in clut_refs)
    best, bestr = 0, -1
    for B in range(0, n - maxoff, 4):
        s = tot = 0
        for off, size in clut_refs:
            a = (B + off)//4; c = size//4
            tot += c; s += flag[a+c] - flag[a]
        if tot and s/tot > bestr:
            bestr, best = s/tot, B
    return best, bestr

def write_png(path, w, h, rgba):
    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
    raw = b''.join(b'\x00' + rgba[y*w*4:(y+1)*w*4] for y in range(h))
    open(path, 'wb').write(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))

def decode(d, base, up, tex0, clut_up):
    stream = d[base+up['src_ref']: base+up['src_ref']+up['bytes']]
    inv = {}
    for y in range(up['trx_h']):
        for x in range(up['trx_w']):
            inv[ct32_addr(x, y, up['dbw']*64)] = y*up['trx_w'] + x
    ncl = 256 if tex0['PSM'] == 19 else 16
    craw = d[base+clut_up['src_ref']: base+clut_up['src_ref']+ncl*4]
    cl = [craw[i*4:i*4+4] for i in range(ncl)]
    iw = tex0['TBW']*64
    if tex0['PSM'] == 19:
        ih = up['bytes']//iw
        out = bytearray()
        for y in range(ih):
            for x in range(iw):
                A = psmt8_addr(x, y, tex0['TBW'])
                out += cl[stream[inv[A >> 2]*4 + (A & 3)]]
    else:
        ih = (up['bytes']*2)//iw
        out = bytearray()
        for y in range(ih):
            for x in range(iw):
                A = psmt4_addr(x, y, tex0['TBW'])  # nibble addr
                byte = stream[inv[A >> 3]*4 + ((A >> 1) & 3)]
                nib = (byte & 0xF) if (A & 1) == 0 else (byte >> 4)
                out += cl[nib]
    return iw, ih, bytes(out)

def main():
    ppk_path, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    d = open(ppk_path, 'rb').read()
    name = os.path.splitext(os.path.basename(ppk_path))[0]
    pk, ups = find_uploads(d)
    tex0s = find_tex0s(d)
    # Several uploads can share one DBP (palette variants reuse an
    # image slot; small aux uploads coexist). Image pick = the DBP
    # candidate whose byte count exactly satisfies the composed
    # geometry (image bytes == transfer bytes for T8, == transfer
    # bytes*2 pixels for T4 at width TBW*64). CLUT pick = candidate
    # at CBP with exactly the CLUT byte size (1024 T8 / 64 T4).
    def pick_img(t):
        iw = t['TBW']*64
        cands = [u for u in ups if u['dbp'] == t['TBP0']]
        for u in sorted(cands, key=lambda u: -u['bytes']):
            if t['PSM'] == 19 and u['bytes'] % iw == 0:
                ih = u['bytes']//iw
                mx = max(psmt8_addr(x, y, t['TBW'])
                         for y in (0, ih-1) for x in (0, iw-1))
                if (mx >> 2) < u['trx_w']*u['trx_h']:
                    return u
            if t['PSM'] == 20 and (u['bytes']*2) % iw == 0:
                return u
        return None
    def pick_clut(t):
        need = 1024 if t['PSM'] == 19 else 64
        cands = [u for u in ups if u['dbp'] == t['CBP']]
        for u in cands:
            if u['bytes'] == need:
                return u
        return cands[0] if cands else None
    pairs, clut_refs = [], []
    for t in tex0s:
        img, clut = pick_img(t), pick_clut(t)
        if img and clut:
            pairs.append((t, img, clut))
            clut_refs.append((clut['src_ref'], clut['bytes']))
    base, score = discover_base(d, clut_refs)
    inv = {'ppk': os.path.basename(ppk_path), 'upload_packets': len(pk),
           'unique_uploads': len(ups), 'tex0_records': len(tex0s),
           'paired_textures': len(pairs), 'pool_base': hex(base),
           'pool_base_clut_score': round(score, 3), 'textures': []}
    for k, (t, img, clut) in enumerate(pairs):
        try:
            iw, ih, rgba = decode(d, base, img, t, clut)
        except (KeyError, IndexError):
            inv['textures'].append({
                'png': None, 'psm': t['PSM'], 'tbp0': t['TBP0'],
                'tbw': t['TBW'], 'cbp': t['CBP'],
                'img_ref': hex(img['src_ref']),
                'clut_ref': hex(clut['src_ref']),
                'undecoded': 'composed-geometry check failed '
                             '(narrow-buffer page layout differs)'})
            continue
        fn = (f"{name}_tex{k:02d}_psm{'t8' if t['PSM']==19 else 't4'}"
              f"_{iw}x{ih}_tbp{t['TBP0']}.png")
        write_png(os.path.join(outdir, fn), iw, ih, rgba)
        inv['textures'].append({
            'png': fn, 'psm': t['PSM'], 'w': iw, 'h': ih,
            'tbp0': t['TBP0'], 'tbw': t['TBW'], 'cbp': t['CBP'],
            'img_ref': hex(img['src_ref']), 'clut_ref': hex(clut['src_ref']),
            'trx': [img['trx_w'], img['trx_h']], 'dbw': img['dbw']})
    json.dump(inv, open(os.path.join(outdir, f'{name}-textures.json'), 'w'),
              indent=1)
    print(f"{name}: {len(pk)} packets, {len(ups)} uploads, "
          f"{len(tex0s)} TEX0, {len(pairs)} paired, base={hex(base)} "
          f"score={score:.3f}")
    for t in inv['textures']:
        print(' ', t['png'])

if __name__ == '__main__':
    main()
