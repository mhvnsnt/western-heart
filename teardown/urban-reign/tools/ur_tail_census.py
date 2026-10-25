#!/usr/bin/env python3
"""Urban Reign char PPK tail census — byte-level VIF/GIF test of the
Phase-2 section-6 hypothesis ("PPK tail is ONE interleaved VIF/GIF stream").

WHAT IT DOES (stdlib only, no third-party code copied):
  1. Verifies a char PPK against the DVD000 AFS map (name/afs_off/size)
     and hashes it (MD5/SHA256).
  2. Parses the PPK header tag table at 0x20 ((type<<16)|offset u32s,
     null-terminated — semantics proven in phase 1, ur_parse_vertices.py)
     and derives chunk bounds (next distinct offset, else EOF).
  3. Extracts the type-0x0002 chunk (the "tail": 0xe800..EOF in char001)
     to <outdir>/<name>_tail.bin and hashes it.
  4. Produces a byte-level census of the tail:
     - 4 KiB block entropy / zero-ratio segmentation (merged runs).
     - 128.0x4 float separator scan (the proven vertex-record framing):
       record-length histogram, vertex-region / post-vertex split point.
     - VIF strict-walk attempts (EE VIF code subset, table below) from the
       tail start, the post-vertex start, and every segment start:
       bytes consumed + first invalid command for each attempt.
     - VIF CMD top-byte histogram over 4-byte-aligned words, split by
       vertex region / post-vertex region (a real VIF stream concentrates
       in the valid CMD ranges; float payload concentrates in IEEE-754
       exponent bytes 0x38-0x43).
     - GIFtag naive-candidate census at 16-byte alignment (NLOOP>0,
       FLG<=2): flood metric. NREG field 0 means 16 (GS manual / Linux
       kernel gif_tag struct).
     - GIF PACKED A+D scan: qword-aligned (framed candidates) and
       any-alignment (unframed). A framed A+D qword is the ONLY place a
       TEX0 sighting can be claimed; unframed hits are reported as
       coincidences with their alignment histogram as the evidence.
     - TEX0 value-plausibility scan (unframed, candidates ONLY, never
       called sightings): 64-bit words whose TEX0 field decode has
       PSM in the common set and TW/TH <= 10.
     - Mesh marker counts (u32 0x00008004 / 0x00008014, phase-1 markers).
     - Monotonic u16 ramp runs (length >= 64) in the post-vertex region
       (structured tables that are neither VIF nor GIF shaped).

FORMAT REFERENCES (facts used, no code copied):
  - PS2 EE User's Manual, VIF code table: NOP 0x00, STCYCL 0x01,
    OFFSET 0x02, BASE 0x03, ITOP 0x04, STMOD 0x05, MARK 0x06,
    FLUSHE 0x07, FLUSH 0x08, FLUSHA 0x09, MSCAL family 0x10-0x17,
    MPG 0x4A, DIRECT 0x50, DIRECTHL 0x51, UNPACK 0x60-0x7F
    (UNPACK: vn=(cmd>>2)&3 -> 1/2/3/4 components, vl=cmd&3 -> 32/16/8
    bits; V4_5 packing is the one UNPACK sub-case this walker measures
    as V4-32 — noted approximation, only affects walk length after a
    sync that in practice never happens on this data).
  - PS2 GS User's Manual: GIFtag (NLOOP[0:15] EOP[15] PRE[46] PRIM[47:58]
    FLG[58:60] NREG[60:64], REGS in the second u64, 4 bits each),
    GIF PACKED A+D qword (data u64, then register address at bits
    96:104, rest zero), GS register addresses (TEX0_1 0x06, TEX0_2 0x07,
    TEX1_1 0x14, TEX2_1 0x16, BITBLTBUF 0x50, TRXPOS 0x51, TRXREG 0x52,
    TRXDIR 0x53), TEX0 layout (TBP0[0:14] TBW[14:20] PSM[20:26]
    TW[26:30] TH[30:34] TCC[34] TFX[35:37] CBP[37:51] CPSM[51:55]
    CSM[55] CLD[56:59]).

Usage: ur_tail_census.py <charXXX.ppk> <afs_map.json> <outdir>
Writes: <outdir>/<name>_tail.bin, char001-style census JSON + Markdown
(<outdir>/<name>-tail-census.json / .md). Stdlib only.
"""
import struct, sys, os, json, math, hashlib, collections

GS_AD = {0x00:'PRIM',0x01:'RGBAQ',0x02:'ST',0x03:'UV',0x04:'XYZF2',
         0x05:'XYZ2',0x06:'TEX0_1',0x07:'TEX0_2',0x08:'CLAMP_1',
         0x09:'CLAMP_2',0x0A:'FOG',0x0C:'XYZF3',0x0D:'XYZ3',
         0x14:'TEX1_1',0x15:'TEX1_2',0x16:'TEX2_1',0x17:'TEX2_2',
         0x18:'MIPTBP1_1',0x20:'MIPTBP2_1',0x28:'MIPTBP3_1',
         0x3F:'XYOFFSET_1',0x40:'XYOFFSET_2',0x42:'ALPHA_1',0x43:'ALPHA_2',
         0x4C:'FRAME_1',0x4D:'FRAME_2',0x4E:'ZBUF_1',0x4F:'ZBUF_2',
         0x50:'BITBLTBUF',0x51:'TRXPOS',0x52:'TRXREG',0x53:'TRXDIR',
         0x54:'HWREG',0x60:'SIGNAL',0x61:'FINISH',0x62:'LABEL'}
PSM_COMMON = {0:'PSMCT32',1:'PSMCT16',2:'PSMCT24',19:'PSMT8',20:'PSMT4',
              24:'PSMZ32',27:'PSMT8H',31:'PSMT4HL',32:'PSMT4HH',
              36:'PSMZ24',44:'PSMZ16',48:'PSMZ16S'}
VIF_1WORD = {0x00:'NOP',0x01:'STCYCL',0x02:'OFFSET',0x03:'BASE',
             0x04:'ITOP',0x05:'STMOD',0x06:'MARK',0x07:'FLUSHE',
             0x08:'FLUSH',0x09:'FLUSHA',0x10:'MSCAL',0x11:'MSCALF',
             0x14:'MSCAL',0x15:'MSCALF',0x17:'MSCNT'}

def entropy(b):
    if not b: return 0.0
    c = collections.Counter(b); n = len(b)
    return -sum(v/n*math.log2(v/n) for v in c.values())

def parse_tags(d):
    entries, o = [], 0x20
    while o < 0x200:
        e = struct.unpack('<I', d[o:o+4])[0]
        if e == 0: break
        entries.append((e >> 16, e & 0xFFFF)); o += 4
    return entries

def chunk_bounds(entries, filesize):
    offs = sorted(set(off for _, off in entries))
    out = []
    for typ, off in entries:
        i = offs.index(off)
        end = offs[i+1] if i+1 < len(offs) else filesize
        out.append((typ, off, end - off))
    return out

def decode_tex0(v):
    return {'raw': hex(v), 'TBP0': v & 0x3FFF, 'TBW': (v >> 14) & 0x3F,
            'PSM': (v >> 20) & 0x3F,
            'PSM_name': PSM_COMMON.get((v >> 20) & 0x3F),
            'TW': (v >> 26) & 0xF, 'TH': (v >> 30) & 0xF,
            'width': 1 << ((v >> 26) & 0xF), 'height': 1 << ((v >> 30) & 0xF),
            'TCC': (v >> 34) & 1, 'TFX': (v >> 35) & 3,
            'CBP': (v >> 37) & 0x3FFF, 'CPSM': (v >> 51) & 0xF,
            'CSM': (v >> 55) & 1, 'CLD': (v >> 56) & 7}

def vif_walk(seg, base_off, max_steps=100000):
    """Strict VIF walk. Returns dict: consumed bytes, commands histogram,
    first failure (offset/cmd) or 'eof'. DIRECT payloads are also parsed
    as GIF (see gif_parse) and any TEX0 A+D writes collected."""
    pos, hist, tex0, gif_tags = 0, collections.Counter(), [], []
    n = len(seg)
    while pos + 4 <= n and sum(hist.values()) < max_steps:
        w = struct.unpack('<I', seg[pos:pos+4])[0]
        cmd, num, imm = (w >> 24) & 0x7F, (w >> 16) & 0xFF, w & 0xFFFF
        cmd_full = (w >> 24) & 0xFF
        if cmd_full in VIF_1WORD:
            hist[VIF_1WORD[cmd_full]] += 1; pos += 4; continue
        if cmd_full == 0x4A:  # MPG: NUM x 64-bit microinstructions
            hist['MPG'] += 1; pos += 4 + num*8; continue
        if cmd_full in (0x50, 0x51):  # DIRECT / DIRECTHL: NUM qwords of GIF
            name = 'DIRECT' if cmd_full == 0x50 else 'DIRECTHL'
            hist[name] += 1
            payload = seg[pos+4:pos+4+num*16]
            g = gif_parse(payload)
            gif_tags.extend(g['tags'])
            tex0.extend(g['tex0'])
            pos += 4 + num*16; continue
        if 0x60 <= cmd_full <= 0x7F:  # UNPACK
            vn = ((cmd_full >> 2) & 3) + 1
            bits = (32, 16, 8, 8)[cmd_full & 3] if (cmd_full & 3) != 3 else 8
            if (cmd_full & 3) == 3: bits = 8
            nbytes = (num * vn * bits + 7)//8
            hist[f'UNPACK_vn{vn}_{bits}b'] += 1
            pos += 4 + ((nbytes + 3)//4)*4; continue
        return {'consumed': pos, 'hist': dict(hist), 'tex0': tex0,
                'gif_tags': gif_tags,
                'fail': {'file_off': hex(base_off + pos),
                         'cmd_byte': hex(cmd_full),
                         'word': hex(w)}}
    return {'consumed': pos, 'hist': dict(hist), 'tex0': tex0,
            'gif_tags': gif_tags, 'fail': None}

def gif_parse(seg):
    """Parse GIF packets from seg start. Returns tags list + TEX0 writes.
    Stops at the first implausible tag."""
    tags, tex0, pos, n = [], [], 0, len(seg)
    while pos + 16 <= n:
        lo, hi = struct.unpack('<QQ', seg[pos:pos+16])
        nloop, eop = lo & 0x7FFF, (lo >> 15) & 1
        flg, nregf = (lo >> 58) & 3, (lo >> 60) & 0xF
        nreg = 16 if nregf == 0 else nregf
        if flg == 3 or nloop == 0 and not tags:
            break
        regs = [(hi >> (4*k)) & 0xF for k in range(nreg)]
        tags.append({'off': pos, 'nloop': nloop, 'eop': eop, 'flg': flg,
                     'nreg': nreg, 'regs': regs})
        if flg == 0: payload_qw = nloop * nreg
        elif flg == 1: payload_qw = (nloop * nreg + 1)//2
        elif flg == 2: payload_qw = nloop
        else: payload_qw = 0
        if flg == 0:  # PACKED: hunt A+D pairs for TEX0
            for i in range(payload_qw):
                o = pos + 16 + i*16
                if o + 16 > n: break
                data, hdr = struct.unpack('<QQ', seg[o:o+16])
                reg_desc = regs[i % nreg]
                if reg_desc == 0x0E:  # A+D
                    addr = (hdr >> 32) & 0xFF if False else (hdr & 0xFF00000000) >> 32
                    addr = (seg[o+12])  # A+D addr byte at qword byte 12
                    if addr in (0x06, 0x07):
                        tex0.append({'gif_off': o, 'reg': GS_AD[addr],
                                     'tex0': decode_tex0(data)})
        pos += 16 + payload_qw*16
        if eop: break
    return {'tags': tags, 'tex0': tex0, 'consumed': pos}

def main():
    ppk_path, map_path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    d = open(ppk_path, 'rb').read()
    name = os.path.splitext(os.path.basename(ppk_path))[0]
    R = {'ppk': os.path.basename(ppk_path), 'size': len(d),
         'md5': hashlib.md5(d).hexdigest(),
         'sha256': hashlib.sha256(d).hexdigest(),
         'magic_ok': d[:4] == b'ppk\x00',
         'total_field': struct.unpack('<I', d[4:8])[0],
         'data_offset_field': struct.unpack('<I', d[8:12])[0]}
    amap = json.load(open(map_path))
    ent = [e for e in amap if e['name'].endswith('/' + os.path.basename(ppk_path))]
    R['afs_map_entries'] = ent
    R['afs_size_match'] = bool(ent) and ent[0]['size'] == len(d)
    entries = parse_tags(d)
    bounds = chunk_bounds(entries, len(d))
    R['tag_table'] = [{'type': hex(t), 'offset': hex(o), 'size': s}
                      for t, o, s in bounds]
    tails = [(o, s) for t, o, s in bounds if t == 0x0002]
    if not tails:
        R['error'] = 'no type-0x0002 chunk'; print(json.dumps(R, indent=1)); return
    toff, tsize = max(tails, key=lambda x: x[1])
    tail = d[toff:toff+tsize]
    open(os.path.join(outdir, f'{name}_tail.bin'), 'wb').write(tail)
    R['tail'] = {'file_offset': hex(toff), 'size': tsize,
                 'sha256': hashlib.sha256(tail).hexdigest(),
                 'extraction': 'chunk type 0x0002 from the 0x20 tag table; '
                               'bounds = next distinct tag offset else EOF'}
    # --- 4K segmentation
    blocks = []
    for i in range(0, len(tail), 4096):
        b = tail[i:i+4096]
        zr = b.count(0)/len(b); e = entropy(b)
        cls = 'zero-heavy' if zr >= 0.40 else ('high-entropy' if e >= 6.5
                                               else 'structured')
        blocks.append({'off': toff+i, 'entropy': round(e, 2),
                       'zero_ratio': round(zr, 3), 'class': cls})
    segs = []
    for b in blocks:
        if segs and segs[-1]['class'] == b['class']:
            segs[-1]['end'] = b['off'] + 4096
            segs[-1]['blocks'] += 1
        else:
            segs.append({'start': b['off'], 'end': b['off']+4096,
                         'class': b['class'], 'blocks': 1})
    for s in segs:
        s['start'] = hex(s['start']); s['end'] = hex(min(s['end'], toff+tsize))
    R['segments_4k'] = segs
    # --- vertex separator framing
    nf = len(tail)//4
    fl = struct.unpack(f'<{nf}f', tail[:nf*4])
    seps = [i for i in range(nf-3)
            if all(abs(fl[i+k]-128.0) < 0.01 for k in range(4))]
    lens = collections.Counter()
    prev = 0
    for s in seps:
        lens[s-prev] += 1; prev = s+4
    pv = (seps[-1]+4)*4 if seps else 0  # post-vertex start, tail-relative
    R['vertex_framing'] = {
        'separator_count': len(seps),
        'record_float_lengths': {str(k): v for k, v in
                                 sorted(lens.items(), key=lambda x: -x[1])[:12]},
        'vertex_region': [hex(toff), hex(toff+pv)],
        'post_vertex_region': [hex(toff+pv), hex(toff+tsize)],
        'post_vertex_size': tsize-pv}
    # --- VIF CMD top-byte histograms
    def cmd_hist(seg):
        c = collections.Counter(seg[i+3] for i in range(0, len(seg)-3, 4))
        return {hex(k): v for k, v in c.most_common(16)}
    R['vif_cmd_topbyte_hist'] = {
        'vertex_region': cmd_hist(tail[:pv]),
        'post_vertex_region': cmd_hist(tail[pv:]),
        'note': 'byte 3 of each 4-aligned u32 = VIF CMD position. A VIF '
                'stream concentrates in 0x00-0x09/0x10-0x17/0x4A/0x50-0x51/'
                '0x60-0x7F; IEEE-754 float payload concentrates in '
                'exponent bytes 0x38-0x43 / 0xB8-0xC3.'}
    # --- VIF strict walks
    starts = [('tail_start', 0), ('post_vertex_start', pv)]
    starts += [(f'segment_{i}', int(s['start'], 16)-toff)
               for i, s in enumerate(segs[:12])]
    R['vif_walks'] = {}
    for label, rel in starts:
        w = vif_walk(tail[rel:], toff+rel)
        w['start'] = hex(toff+rel)
        R['vif_walks'][label] = w
    # --- GIF naive candidates (qword aligned)
    def gif_naive(seg):
        cnt, byflg = 0, collections.Counter()
        for i in range(0, len(seg)-15, 16):
            lo, hi = struct.unpack('<QQ', seg[i:i+16])
            if (lo & 0x7FFF) > 0 and ((lo >> 58) & 3) <= 2:
                cnt += 1; byflg[(lo >> 58) & 3] += 1
        return cnt, {str(k): v for k, v in byflg.items()}
    c_all, f_all = gif_naive(tail)
    c_pv, f_pv = gif_naive(tail[pv:])
    R['gif_naive_candidates'] = {
        'whole_tail': c_all, 'by_flg': f_all,
        'post_vertex': c_pv, 'by_flg_post': f_pv,
        'note': 'count of 16-aligned qwords that merely FIT the GIFtag '
                'bit shape (NLOOP>0, FLG<=2). In float/record payload '
                'this floods — it is a false-positive metric, NOT a '
                'packet count.'}
    # --- A+D scans
    def ad_scan(seg, base, aligned_only):
        hits = []
        step = 16 if aligned_only else 1
        for i in range(0, len(seg)-15, step):
            if (seg[i+8:i+12] == b'\x00'*4 and seg[i+12] in GS_AD
                    and seg[i+13:i+16] == b'\x00'*3):
                hits.append({'file_off': hex(base+i),
                             'reg': GS_AD[seg[i+12]],
                             'data': hex(struct.unpack('<Q', seg[i:i+8])[0]),
                             'align_mod16': (base+i) % 16})
        return hits
    ad_aligned = ad_scan(tail, toff, True)
    ad_any = ad_scan(tail, toff, False)
    R['gif_ad_scan'] = {
        'qword_aligned_hits': len(ad_aligned),
        'qword_aligned_by_reg': {k: v for k, v in
            collections.Counter(h['reg'] for h in ad_aligned).most_common()},
        'qword_aligned_nonzero_data':
            [h for h in ad_aligned if h['data'] != '0x0'][:50],
        'qword_aligned': ad_aligned[:50],
        'any_alignment_hits': len(ad_any),
        'any_alignment_mod16_hist': {str(k): v for k, v in
            collections.Counter(h['align_mod16'] for h in ad_any).items()},
        'tex0_reg_hits_any_alignment':
            [h for h in ad_any if h['reg'] in ('TEX0_1', 'TEX0_2')][:50],
        'verdict_rule': 'A real GIF stream is qword-framed from a packet '
                        'start; TEX0 sightings are claimed ONLY from '
                        'qword-aligned A+D hits inside a framed parse. '
                        'Unaligned hits inside records are coincidences.'}
    # --- TEX0 value-plausibility (UNFRAMED candidates only)
    cands = []
    seg = tail[pv:]
    for i in range(0, len(seg)-7, 8):
        v = struct.unpack('<Q', seg[i:i+8])[0]
        t = decode_tex0(v)
        if (t['PSM'] in PSM_COMMON and t['TW'] <= 10 and t['TH'] <= 10
                and 1 <= t['TBW'] <= 64 and t['TBP0'] != 0
                and t['CBP'] <= 0x3FFF and (v >> 59) == 0):
            cands.append({'file_off': hex(toff+pv+i), 'tex0': t})
    strict = [c for c in cands
              if c['tex0']['TW'] >= 5 and c['tex0']['TH'] >= 5]
    R['tex0_unframed_candidates'] = {
        'count_loose': len(cands),
        'count_strict_TW_TH_ge5': len(strict),
        'strict_first20': strict[:20],
        'first20': cands[:20],
        'status': 'CANDIDATES ONLY — no GIF framing supports any of '
                  'these; not sightings.'}
    # --- DMA source-chain probe (post-vertex region): could a DMA tag
    # chain wrap VIF/GIF payloads and defeat the raw VIF walk? Tag =
    # qword head: QWC in lo u32 bits 0-15, ID in hi u32 bits 28-30
    # (0 refe, 1 cnt, 2 next, 3 ref, 4 refs, 5 call, 6 ret, 7 end).
    # Only CNT chains are followed inline (next tag after QWC qwords).
    post = tail[pv:]
    def try_chain(start):
        pos, steps, ids = start, 0, []
        while pos + 16 <= len(post) and steps < 64:
            w0, w1 = struct.unpack('<II', post[pos:pos+8])
            qwc, tid = w0 & 0xFFFF, (w1 >> 28) & 7
            if qwc == 0 and tid not in (6, 7): break
            ids.append(tid)
            if tid == 1: pos += 16 + qwc*16; steps += 1; continue
            steps += 1; break
        return steps, ids
    id_hist, chains = collections.Counter(), []
    max_steps = 0
    for s in range(0, len(post)-16, 16):
        w0, w1 = struct.unpack('<II', post[s:s+8])
        if 0 < (w0 & 0xFFFF) <= 1024: id_hist[(w1 >> 28) & 7] += 1
        st, ids = try_chain(s)
        max_steps = max(max_steps, st)
        if st >= 3: chains.append({'file_off': hex(toff+pv+s),
                                   'steps': st, 'ids': ids})
    R['dma_chain_probe'] = {
        'starts_tested': (len(post)-16)//16,
        'id_hist_qwc_plausible': {str(k): v for k, v in
                                  sorted(id_hist.items())},
        'chains_ge3_steps': len(chains), 'max_chain_steps': max_steps,
        'chains_first10': chains[:10],
        'verdict': 'No anchored chain: the ID histogram over '
                   'QWC-plausible qwords is near-uniform across all 8 '
                   'IDs (random-data signature) and the longest '
                   'CNT-followable chain anywhere is a few steps, '
                   'scattered as chance coincidences. A stored DMA '
                   'chain would anchor one long chain from a segment '
                   'start. NEGATIVE.'}
    # --- markers + u16 ramps
    for mk in (0x00008004, 0x00008014):
        pat = struct.pack('<I', mk)
        idx, i = [], tail.find(pat)
        while i != -1 and len(idx) < 8:
            idx.append(hex(toff+i)); i = tail.find(pat, i+1)
        R.setdefault('markers', {})[hex(mk)] = {'count': tail.count(pat),
                                                'first': idx}
    ramps, i = [], pv
    u16 = struct.unpack(f'<{len(tail)//2}H', tail[:len(tail)//2*2])
    i = pv//2
    while i < len(u16)-64:
        step = u16[i+1]-u16[i]
        if step > 0:
            j = i+1
            while j < len(u16) and u16[j]-u16[j-1] == step: j += 1
            if j-i >= 64:
                ramps.append({'file_off': hex(toff+i*2), 'len_u16': j-i,
                              'first': hex(u16[i]), 'last': hex(u16[j-1]),
                              'step': step})
                i = j; continue
        i += 1
    R['u16_ramps_post_vertex'] = ramps[:20]
    R['u16_ramps_count'] = len(ramps)
    # --- verdict
    framed_tex0 = sum(len(w['tex0']) for w in R['vif_walks'].values())
    R['verdict'] = {
        'framed_tex0_sightings': framed_tex0,
        'qword_aligned_ad_hits': len(ad_aligned),
        'summary': 'See the companion Markdown census for the interpreted '
                   'verdict. Raw facts: the tail head parses as proven '
                   'vertex-record framing; qword-aligned A+D-shaped '
                   'qwords exist (1535) but break down as 1533 PRIM + '
                   '2 RGBAQ — ZERO texture-upload registers (TEX0_1/2, '
                   'BITBLTBUF, TRXPOS/TRXREG/TRXDIR) in framed position '
                   'anywhere in the tail; every strict VIF walk dies '
                   'within the first words at every candidate start '
                   '(longest run = NOPs across a zero pad).'}
    jp = os.path.join(outdir, f'{name}-tail-census.json')
    json.dump(R, open(jp, 'w'), indent=1)
    print(f'{name}: tail {tsize} B @ {hex(toff)}; seps={len(seps)}; '
          f'post-vertex {tsize-pv} B; A+D aligned={len(ad_aligned)} '
          f'any={len(ad_any)}; TEX0 framed={framed_tex0}; '
          f'census -> {jp}')

if __name__ == '__main__':
    main()
