#!/usr/bin/env python3
"""ur_name_bridge.py - Urban Reign motdat name bridge (Phases 4-5).

Matches motdat `.bin` record payload root streams against `.gyu` bank
motion root tracks to PROVE name<->motion pairs by identity.

.bin format (cracked Phase 4): [u32 N][N x u32 offset table][records];
record: +0 u32 globalId, +4 32B name (byte-identical to the .info name
of the same index), +36 20B date, +56 u32 marker, +60 u32 frames,
+64 u32 field, +68 u32 frames*132, +72 u32 M (segment count), +76 u32 0,
+80 (M-1) x u32 segment offsets, then payload: frames*33 f32 sampled
motion data whose first frames*3 f32 are the motion's ROOT track
sampled per frame, x1000 (millimetres).

Bank root = bone-0 track decoded by ur_gyu (same folder; type-14 uses
the Phase-5 cracked big-endian double-integrator decode), sampled per
frame (linear between keys, frame/fpk), x1000.

Gate (Phases 4-5): a pair is PROVEN only when max deviation over all
frames/components <= 0.10 mm AND the motion is the unique candidate
under the gate in the fighter's own bank. Never force a match.

Usage (library): parse_bin, parse_info, bank_roots, match.
Phase-5 results: teardown/urban-reign/motion-names/name-bridge-*.json
and PHASE5-NAME-BRIDGE-SUMMARY.md in the same folder.
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ur_gyu

ELF_DEFAULT = '/home/hatch/workspace/ur-decode/work/SLUS_212.09'
GATE = 0.10

def load_sets(elf_path=ELF_DEFAULT):
    return ur_gyu.load_tables(elf_path)

def parse_bin(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[0:4])[0]
    offs = [struct.unpack('<I', d[4+4*i:8+4*i])[0] for i in range(n)]
    base = 4 + 4*n
    recs = []
    for k in range(n):
        s = base + offs[k]
        gid = struct.unpack('<I', d[s:s+4])[0]
        name = d[s+4:s+36].split(b'\x00')[0].decode('ascii', 'replace')
        frames = struct.unpack('<I', d[s+60:s+64])[0]
        m = struct.unpack('<I', d[s+72:s+76])[0]
        pstart = s + 80 + 4*(m-1)
        vals = struct.unpack('<%df' % (frames*3), d[pstart:pstart+frames*12])
        root = [tuple(vals[3*i:3*i+3]) for i in range(frames)]
        recs.append(dict(record=k, globalId=gid, name=name, frames=frames, root=root))
    return recs

def parse_info(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[0:4])[0]
    base = 4 + 4*n
    return [d[base+60*k+4:base+60*k+36].split(b'\x00')[0].decode('ascii', 'replace')
            for k in range(n)]

def sample(vals, fpk, frame):
    p = frame / fpk
    i = min(int(p), len(vals)-1); fr = p - i
    j = min(i+1, len(vals)-1)
    a, b = vals[i], vals[j]
    return tuple(a[c]*(1-fr) + b[c]*fr for c in range(3))

def bank_roots(gyu_path, set1, set2):
    bank = ur_gyu.Bank(gyu_path)
    out = []
    for mi in range(bank.n_motions):
        trs = bank.tracks(mi)
        nframes = max((t.nkeys-1)*t.fpk for t in trs) + 1
        tr = trs[0]
        try:
            dec = tr.decode(bank.d, set1, set2)
            roots = [tuple(v*1000.0 for v in sample(dec, tr.fpk, f)) for f in range(nframes)]
            out.append(dict(motion=mi, frames=nframes, rootType=tr.type, roots=roots, err=None))
        except Exception as e:
            out.append(dict(motion=mi, frames=nframes, rootType=tr.type, roots=None, err=repr(e)))
    return bank, out

def maxdev(a, b):
    return max(abs(a[f][c]-b[f][c]) for f in range(len(a)) for c in range(3))

def match(recs, roots, gate=GATE):
    """Proven = exactly one own-bank motion under gate. Everything else
    is returned unproven with candidates and deviations."""
    proven, unproven = [], []
    byframes = {}
    for r in roots:
        byframes.setdefault(r['frames'], []).append(r)
    for rec in recs:
        hits = []
        cand_info = []
        for r in byframes.get(rec['frames'], []):
            if r['roots'] is None:
                cand_info.append(dict(motion=r['motion'], rootType=r['rootType'], err=r['err']))
                continue
            dev = maxdev(rec['root'], r['roots'])
            cand_info.append(dict(motion=r['motion'], rootType=r['rootType'], maxDev=round(dev, 4)))
            if dev <= gate:
                hits.append((r, dev))
        if len(hits) == 1:
            r, dev = hits[0]
            proven.append(dict(record=rec['record'], name=rec['name'], globalId=rec['globalId'],
                               frames=rec['frames'], bankMotion=r['motion'],
                               clip='ur_m%03d' % r['motion'], maxDev=round(dev, 4),
                               rootType=r['rootType']))
        else:
            unproven.append(dict(record=rec['record'], name=rec['name'], globalId=rec['globalId'],
                                 frames=rec['frames'], candidates=cand_info,
                                 ambiguous=(len(hits) > 1)))
    return proven, unproven
