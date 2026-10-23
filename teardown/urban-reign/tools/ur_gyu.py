#!/usr/bin/env python3
"""ur_gyu.py - Urban Reign .gyu motion bank decoder.

Decodes SLUS_212.09 .gyu animation banks (general_normal / general_30frame /
general_weapon / pmot*.gyu) into per-motion, per-bone keyframe tracks.

Format (proven from the files + Ghidra decompilation of the game's own
sampler FUN_00292670 and track getter FUN_00299130, SLUS_212.09 MD5
0fa29bd55638f9ebe49feb494d4decd5):

Bank:  [u32 n_motions][u32 n_bones][u32 0][n_bones x u32 flags]
       [n_motions x u32 cumulative motion end offsets, rel. to data start]
       motions back to back.
Motion: [n_bones x u32 track offsets, rel. to track-data base]
        track data.
Track header: s16 type @+0, s16 frames_per_key @+2, s16 n_keys @+4, s16 0 @+6.
Track types (sampler dispatch on type):
  8  : u16 keys at +36 (3 per key); out_c = base_c + key_c * step_c with
       bases float @+12,+16,+20 and steps float @+24,+28,+32.
  12 : arithmetic/range-coded s12 deltas (tables set 1 in the ELF:
       total u16 @0x662aa8, prob @0x65eaa8, cum @0x660aa8, guess @0x662ab0).
       Block table: s16 offsets @+36 (one per 8 keys). Per block, 24 symbols
       = 8 triples; key r = s16-wrapped cumulative sum of triples 0..r.
       out_c = base_c + key_c * step_c (float pairs @+12/+24, +16/+28, +20/+32).
  13 : arithmetic-coded with tables set 2 (total @0x663ec0, prob @0x663ac0,
       cum @0x663cc0, guess @0x663ec8; 256 symbols, s8 values). Block table:
       s16 offsets @+8. [decode pending validation]
  14 : like 13 but header layout of 12 (float pairs @+12..+32, block table
       @+36). Root-bone track in general banks. [CRACKED Phase 5: symbol
       pairs are BIG-ENDIAN s16 second differences; per 8-key block the
       sampler double-integrates (pos[0]=v[0], vel[0]=0, vel+=v, pos+=vel,
       s16 wrap); out = base + pos*step. Proven exact (max dev 0.0014 mm
       over 80 frames) against motdatP1 record 7's payload root stream vs
       general_weapon motion 33. See PHASE5-JOB2-TYPE14.md.]

Sampler semantics (FUN_00292670): output is a vec3 (x, y, z, 1.0). For
rotation tracks the caller (FUN_002918xx) feeds it to FUN_00101628
(Euler -> matrix); the per-bone flag word (anim+8) selects rotation (x1)
vs translation (x0.001 in the caller) handling.
"""
import struct, sys

ELF_PATH = None  # set by load_tables()

def load_tables(elf_path):
    elf = open(elf_path, 'rb').read()
    def u16s(vaddr, n):
        off = vaddr - 0xFF000
        return [struct.unpack('<H', elf[off+i*2:off+i*2+2])[0] for i in range(n)]
    set1 = {
        'total': u16s(0x662aa8, 1)[0],
        'prob': u16s(0x65eaa8, 4096),
        'cum': u16s(0x660aa8, 4097),
        'guess': u16s(0x662ab0, 1024),
        'bits': 12,
    }
    set2 = {
        'total': u16s(0x663ec0, 1)[0],
        'prob': u16s(0x663ac0, 256),
        'cum': u16s(0x663cc0, 257),
        'guess': u16s(0x663ec8, 1024),
        'bits': 8,
    }
    return set1, set2

class RangeDecoder:
    """Faithful transliteration of the sampler's range decoder."""
    def __init__(self, data, pos, tab):
        self.d = data; self.p = pos; self.tab = tab
        self.code = 0
        for _ in range(3):
            self.code = (self.code << 8) | self.d[self.p]; self.p += 1
        self.unit = 0x1000000 // tab['total']
        self.rng = self.unit * tab['total']
        self.first = True
    def symbol(self):
        tab = self.tab
        if self.first:
            unit = self.unit; self.first = False
        else:
            unit = self.rng // tab['total']
        q = self.code // unit
        idx = tab['guess'][(q >> 6) & 0x3ff] if (q >> 6) < 1024 else tab['guess'][1023]
        cum = tab['cum']
        while cum[idx] <= q:
            idx += 1
        sym = idx - 1
        self.code -= cum[sym] * unit
        self.rng = unit * tab['prob'][sym]
        while self.rng < 0x10000:
            self.rng <<= 8
            self.code = (self.code << 8) | self.d[self.p]; self.p += 1
        bits = tab['bits']
        if sym >= (1 << (bits - 1)):
            sym -= (1 << bits)
        return sym

def s16(x):
    x &= 0xffff
    return x - 0x10000 if x >= 0x8000 else x

class Track:
    def __init__(self, d, off, size):
        self.off = off; self.size = size
        self.type = struct.unpack('<h', d[off:off+2])[0]
        self.fpk = struct.unpack('<h', d[off+2:off+4])[0]   # frames per key
        self.nkeys = struct.unpack('<h', d[off+4:off+6])[0]
        self.floats = [struct.unpack('<f', d[off+4*i:off+4*i+4])[0] for i in range(3, 9)]  # @+12..+32

    def decode(self, d, set1, set2):
        t = self.type
        if t == 8:
            out = []
            for k in range(self.nkeys):
                o = self.off + 36 + k * 6
                kv = struct.unpack('<3H', d[o:o+6])
                out.append(tuple(self.floats[c] + kv[c] * self.floats[3 + c] for c in range(3)))
            return out
        if t == 12:
            nb = (self.nkeys + 7) // 8
            boffs = [struct.unpack('<h', d[self.off + 36 + 2*i:self.off + 38 + 2*i])[0] for i in range(nb)]
            out = []
            for b in range(nb):
                rd = RangeDecoder(d, self.off + boffs[b], set1)
                acc = [0, 0, 0]
                for r in range(min(8, self.nkeys - 8 * b)):
                    trip = [rd.symbol() for _ in range(3)]
                    acc = [s16(acc[c] + trip[c]) for c in range(3)]
                    out.append(tuple(self.floats[c] + acc[c] * self.floats[3 + c] for c in range(3)))
            return out[:self.nkeys]
        raise NotImplementedError(f'track type {t}')

class Bank:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        d = self.d
        self.n_motions = struct.unpack('<I', d[0:4])[0]
        self.n_bones = struct.unpack('<I', d[4:8])[0]
        nb = self.n_bones
        self.flags = [struct.unpack('<I', d[12+4*i:16+4*i])[0] for i in range(nb)]
        hdr = 12 + nb * 4
        self.tab = [struct.unpack('<I', d[hdr+4*i:hdr+4*i+4])[0] for i in range(self.n_motions)]
        self.data = hdr + self.n_motions * 4
    def motion_range(self, mi):
        s = self.data + (self.tab[mi-1] if mi > 0 else 0)
        e = self.data + self.tab[mi] if mi < self.n_motions - 1 else len(self.d)
        return s, e
    def tracks(self, mi):
        s, e = self.motion_range(mi)
        nb = self.n_bones
        offs = [struct.unpack('<I', self.d[s+4*b:s+4*b+4])[0] for b in range(nb)]
        tbase = s + nb * 4
        out = []
        for b in range(nb):
            t = tbase + offs[b]
            tend = tbase + offs[b+1] if b < nb - 1 else e
            out.append(Track(self.d, t, tend - t))
        return out

if __name__ == '__main__':
    elf = sys.argv[1] if len(sys.argv) > 1 else '/home/hatch/workspace/ur-decode/work/SLUS_212.09'
    set1, set2 = load_tables(elf)
    print('set1 total', set1['total'], 'set2 total', set2['total'])
    bank = Bank(sys.argv[2] if len(sys.argv) > 2 else '/tmp/gyu/gyu_debug.gyu')
    print('motions', bank.n_motions, 'bones', bank.n_bones, 'flags', bank.flags)
    for mi in [0]:
        print('motion', mi)
        for b, tr in enumerate(bank.tracks(mi)):
            try:
                vals = tr.decode(bank.d, set1, set2)
                print(f' bone {b} type {tr.type} fpk {tr.fpk} keys {tr.nkeys}: first {vals[0]} mid {vals[len(vals)//2]} last {vals[-1]}')
            except Exception as ex:
                print(f' bone {b} type {tr.type} fpk {tr.fpk} keys {tr.nkeys}: FAIL {ex}')

def _decode_pairs_track(tr, d, tab, hdr_floats):
    """Types 13/14: set-2 range-coded s16 values built from symbol pairs.
    Type 13: per key step, 6 symbols -> 3 s16 (little-endian byte pairs)
    -> s16 cumulative sum within the block. [still pending validation]
    Type 14 (CRACKED, UR Phase 5): symbol pairs are BIG-ENDIAN (hi byte
    first) and encode SECOND differences: per block, pos[0] = v[0],
    vel[0] = 0; vel[k] += v[k]; pos[k] += vel[k] (s16 wrap throughout);
    out = base + pos*step. Proven exact against motdat payload root
    streams (see module docstring)."""
    nb = (tr.nkeys + 7) // 8
    boff_base = 36 if tr.type == 14 else 8
    boffs = [struct.unpack('<h', d[tr.off + boff_base + 2*i:tr.off + boff_base + 2*i + 2])[0] for i in range(nb)]
    out = []
    for b in range(nb):
        rd = RangeDecoder(d, tr.off + boffs[b], tab)
        acc = [0, 0, 0]
        pos = [0, 0, 0]; vel = [0, 0, 0]
        for r in range(min(8, tr.nkeys - 8 * b)):
            vals = []
            for c in range(3):
                if tr.type == 14:
                    hi = rd.symbol(); lo = rd.symbol()
                    vals.append(s16(((hi & 0xff) << 8) | (lo & 0xff)))
                else:
                    lo = rd.symbol(); hi = rd.symbol()
                    vals.append(s16((lo & 0xff) | ((hi & 0xff) << 8)))
            if tr.type == 14:
                if r == 0:
                    pos = vals[:]
                else:
                    vel = [s16(vel[c] + vals[c]) for c in range(3)]
                    pos = [s16(pos[c] + vel[c]) for c in range(3)]
                out.append(tuple(hdr_floats[c] + pos[c] * hdr_floats[3 + c] for c in range(3)))
            else:
                acc = [s16(acc[c] + vals[c]) for c in range(3)]
                out.append(tuple(acc[c] * (1.0 / 16383.0) for c in range(3)))
    return out[:tr.nkeys]

_orig_decode = Track.decode
def _decode2(self, d, set1, set2):
    if self.type == 13:
        return _decode_pairs_track(self, d, set2, self.floats)
    if self.type == 14:
        return _decode_pairs_track(self, d, set2, self.floats)
    return _orig_decode(self, d, set1, set2)
Track.decode = _decode2
