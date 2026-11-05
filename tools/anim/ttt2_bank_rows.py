#!/usr/bin/env python3
"""ttt2_bank_rows.py: produce rows.pack.json + hit_frames.json for a TTT2 bank
(roger / jun) from the shipped join tables and the decoded clip data.

Roster-100 Wave 1 item S5 (docs/handoffs/ROSTER-100-FIX-2026-11-04.md),
closing follow-up #3 of the TTT2 banks handoff (WH #1558/#1561). Formats are
the kuma bank's: wh-anim-pack/1 for rows.pack.json, wh-hitframes/1 for
hit_frames.json — the exact shapes game/js/t3anims.js loadT3Clips() consumes.

ROW SPACE: the character's motbin move-table (grid) index in
data006-decoded.bin. The grid index IS the join record's `i`: the tool parses
the raw grid itself and cross-validates every join record against it
(name/anim/anim_ref triple at the same index) and aborts on any mismatch, so
the join lane's validation is inherited, never bypassed. Grid records the
join rejected are NOT produced.

MOTBIN LAYOUT (big-endian, 0x70-byte records; field map validated in
docs/tech/ttt2-mota/RECORD-FIELDS.md): block base = (file offset of the
bracketed character name) - 0x20C (the string pool starts at base + 0x20C,
first pool string = the bracketed name). Roger: movelist = header section
pair 12 at base + 0x140 + 8*12. Jun: the header pairs do not carry the
movelist; the grid begins at block + 0xA2D7C (anchored on record
sDm_IKAO_plB's triple and validated against jun-join 742/742). Per record:
name ptr @+0x4C, anim ptr @+0x50, anim_ref @+0x54 (pool-relative),
first_active_frame u32 @+0x40, last_active_frame u32 @+0x44, attack word +
flags u32 @+0x5C (low 16 bits = the attack word the engine's
attackLevelOfWord classifies; bit 0x400000 = the character's own throw).

ROW SET (per bank): every JOIN record with first_active > 0, every
throw-flagged record, and every record a shipped bank slot clip was baked
from (slot sources, movement/stance included — the T3 packs likewise carry
non-attack rows). Row 48 is withheld (see WITHHELD below). hit_frames.json
follows the T3 inclusion rule: attack rows (first_active > 0) and throw
rows only.

hit_frames row = [first_active, last_active, stream_frames, attack_word,
throw, button], copied from the move record; stream_frames is the decoded
clip length. Damage is not a hit_frames field in any bank (kuma included)
and could not be produced from the motbin data (RECORD-FIELDS.md) — none
was invented. Buttons are 0 (unknown, the format's sanctioned value)
except the bank's slot identities — the T3 branch-command production has
no cracked TTT2 analog yet: t3_medium = LK (4), t3_heavy = RK (8),
Thrmv_B1_00 = 1+3 (5, Roger's grab, probe-verified #1558/#1577),
Thrmv_B2_00i = 2+4 (10, Jun's grab, #1561).

GATES for pack rows: decode integrity exactly as the bank bake gated slots
(entry type 0x64/0xC8, >= 23 tracks, >= 2 frames, finite values, FK
self-check <= 1e-3 m), plus the inter-frame jump check from the same gate
code (a limb teleporting >= 1.5 m between frames is a broken unwrap, not
motion). The slot gate's PRESENTATION checks (upright start, floor at
-0.08 m) are NOT applied to library rows: the T3 row packs
(tools/anim/t3_row_bake.py) carry every referenced row ungated — crouching,
falling and downed motions included — and a row clip is only ever played
when a move resolves to it. Each row's presentation verdict under the slot
standard is still computed and recorded in the bake report
(presentation_gate_failures), so nothing is hidden. Records that fail an
integrity gate keep their hit row (the window is a fact of the move
record) but get no pack row; records whose entry fails to decode get
neither and land in "missing". Bank-0 records (anim_ref bank 0) are not
produced: the per-character data006 MOTA tables for roger/jun were never
located (bank-tables.json wires only Paul's); they land in "missing".

Clips are converted with the bank bake's own pipeline (decode ->
unwrap_rotations -> pose_synth.Synthesizer.pose -> ttt2_bank_bake.convert)
and encoded with t3_row_bake.py's quantization (canonical-sign quats,
int16 x 32767, frame-major [frame][bone][xyzw]; root translation int16 mm).
Unwrap branch selection: forward chain first; the backward-anchored chain
wins when it fixes a jump failure, passes the presentation gate the
forward chain fails, or breaches the floor no deeper. For entries that are
themselves shipped slot clips, the shipped clip is the proven conversion
of that exact entry (the shipped banks are heterogeneous — Jun's stance
is the ref-anchored backward chain, her #1568-re-baked grab the unanchored
forward chain): if the selected chain does not reproduce the shipped clip
(quat error <= 1e-4), the remaining unwrap variants are tried and the
reproducing one is kept. Selection was validated against all 20 shipped
roger+jun slot clips (every one reproduced to <= 2.3e-5).

--write-move-rows also stamps each shipped slot clip in --bank-dir with the
top-level "move_row" field T3 slot clips carry (kuma t3_light.json has
move_row 119), keyed from the clip's own ttt2_source provenance, so the
engine attaches the decoded hit window to the action clip. Clips whose
source record is not in this bank's move table (Jun's Unknown-sourced and
bank-2 slots) are left untouched — there is no row in this bank to key to.

Usage:
  python3 tools/anim/ttt2_bank_rows.py --bank roger \
     --data004 <path> --data005 <path> --data006 <path> \
     --decoder64 tools/ttt2_mota_decode64.py \
     --calib tools/anim/ttt2-mannequin-calib.json \
     --root-affine tools/anim/ttt2-root-affine.json \
     --rest tools/anim/ttt2-mannequin-rest.json \
     --join docs/tech/ttt2-mota/join/roger-join.json \
     --bank-dir game/assets/anim/t3/roger --fighter menajerii \
     --out-dir game/assets/anim/t3/roger \
     --report docs/proof/2026-11-05/roster-100-s5/bake-report-roger.json \
     [--write-move-rows] [--jobs N]
"""
import argparse, base64, hashlib, importlib.util, json, math, os, re, struct, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ttt2_bank_bake as BB
from pose_synth import Synthesizer

# Legacy class-stamp row: 135 Megami moves carry anim_t3 {bank jun, row 48}
# and 139 Menajerii moves {tekken-wiki, 48}; whether the stamp class retires
# or is defined is an open owner ruling (roster-100 handoff). Neither bank's
# grid record 48 is an attack (both first_active 0), so withholding loses
# nothing playable and keeps the ruling un-foreclosed.
WITHHELD = {48: 'grid row 48 withheld: the legacy row-48 class stamp '
                '(roster-100 owner ruling pending); this record is not an '
                'attack (first_active 0)'}

SLOT_BUTTONS = {'t3_medium': 4, 't3_heavy': 8}           # LK / RK identities
GRAB_BUTTONS = {'Thrmv_B1_00': 5, 'Thrmv_B2_00i': 10}   # 1+3 / 2+4

BANK1_TABLE = {'roger': 90926084, 'jun': 193068196}     # data005 offsets (bank-tables.json)
CHAR_NAME = {'roger': b'[ROGER]', 'jun': b'[JUN_KAZAMA]'}
BODY_KMD = {'roger': 'ROGER (Roger Jr.)', 'jun': 'JUN_KAZAMA (Jun Kazama)'}
JUN_GRID_OFF = 0xA2D7C


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def attack_level(word):
    """Mirror of attackLevelOfWord in game/js/t3anims.js (for reporting)."""
    posture, guard = word & 7, word & 0x18
    if posture == 0 and (word & 0x800):
        return 't'
    if posture == 2:
        return 'h'
    if guard == 0x08:
        return 'l'
    if guard == 0x18:
        return 's'
    if guard == 0:
        return 'u'
    return 'm'


class Motbin:
    """One character's motbin move grid in data006-decoded.bin."""

    def __init__(self, data, bank):
        self.data = data
        name = CHAR_NAME[bank]
        off = data.find(name)
        if off < 0:
            raise ValueError('character name %r not found in data006' % name)
        self.base = off - 0x20C
        self.pool = self.base + 0x20C
        u32 = lambda o: struct.unpack('>I', data[o:o + 4])[0]
        if bank == 'roger':
            ptr, count = u32(self.base + 0x140 + 8 * 12), u32(self.base + 0x140 + 8 * 12 + 4)
            self.start, self.count = self.base + ptr, count + 400
        else:
            self.start, self.count = self.base + JUN_GRID_OFF, 1600
        self.grid = [self._record(i) for i in range(self.count)]

    def _str(self, off):
        if off <= 0 or self.pool + off >= len(self.data):
            return None
        end = self.data.find(b'\x00', self.pool + off)
        if end < 0:
            return None
        try:
            s = self.data[self.pool + off:end].decode('ascii')
        except UnicodeDecodeError:
            return None
        return s if s and all(32 <= ord(c) < 127 for c in s) else None

    def _record(self, i):
        o = self.start + i * 0x70
        if o + 0x70 > len(self.data):
            return None
        u32 = lambda k: struct.unpack('>I', self.data[o + k:o + k + 4])[0]
        name, anim = self._str(u32(0x4C)), self._str(u32(0x50))
        if name is None or anim is None:
            return None
        return (name, anim, u32(0x54))

    def fields(self, i):
        """(first_active, last_active, attack_word_u32) for grid record i."""
        o = self.start + i * 0x70
        u32 = lambda k: struct.unpack('>I', self.data[o + k:o + k + 4])[0]
        return u32(0x40), u32(0x44), u32(0x5C)


def load_join(path, mb):
    """Cross-validate the shipped join against the raw grid. Returns
    (records_by_grid_index, unmapped_join_records). Aborts on misalignment."""
    join = json.load(open(path))
    by_i, unmapped = {}, []
    triples = {}
    for gi, rec in enumerate(mb.grid):
        if rec is not None:
            triples.setdefault(rec, []).append(gi)
    for r in join['records']:
        gi = r['i']
        want = (r['name'], r['anim'], r['ref'])
        if gi < len(mb.grid) and mb.grid[gi] == want:
            by_i[gi] = r
        elif want in triples:
            raise SystemExit('JOIN/GRID MISALIGNMENT: join record %r claims grid %d '
                             'but its triple sits at %s' % (r['name'], gi, triples[want]))
        else:
            unmapped.append(r)
    return join, by_i, unmapped


_CTX = {}  # per-process bake context (fork-inherited under multiprocessing)


def bake_entry(key):
    """One unique MOTA entry -> (status, payload, stream_frames).
    status 'ok': payload (clip, presentation_verdict); 'gate': payload is
    the integrity-gate reason (hit row kept, no pack row); 'decode': payload
    is the decode reason (neither row). Mirrors ttt2_bank_bake.main()'s
    per-slot flow (decode, sanity, unwrap, synth, convert, FK check,
    backward-unwrap retry, toe-graze classification)."""
    dec64, synth, ref_triples = _CTX['dec64'], _CTX['synth'], _CTX['ref_triples']
    data, tab = _CTX['tables'][key[0]]
    bank, idx = key
    u32 = lambda d, o: struct.unpack('>I', d[o:o + 4])[0]
    try:
        eoff = tab + u32(data, tab + 16 + 4 * idx)
        if eoff + 2 > len(data):
            return key, ('decode', 'entry offset 0x%x is past the end of the binary' % eoff, None)
        typ = struct.unpack('>H', data[eoff:eoff + 2])[0]
        if typ == 100:
            r = dec64.decode_clip(data, eoff)
            frames, fmt, ntr = r['frames'], '0x64', r['header']['N']
        elif typ == 200:
            frames, fmt = BB.decode_c8(data[eoff:eoff + 8_000_000]), '0xC8'
            ntr = len(frames[0])
        else:
            return key, ('decode', 'entry type %d is not a body clip format (0x64/0xC8)' % typ, None)
    except Exception as e:
        return key, ('decode', 'decode failed: %s' % e, None)
    if ntr < 23 or len(frames) < 2:
        return key, ('decode', 'not a 23-track body clip (%d tracks, %d frames)' % (ntr, len(frames)), None)
    bad = False
    for row in frames:
        for t in range(23):
            for v in row[t]:
                if not math.isfinite(v) or abs(v) > 1e4:
                    bad = True
    if bad:
        return key, ('decode', 'decoded values non-finite/out of range (unidentified encoder variant)', None)
    stream_frames = len(frames)
    try:
        posed = synth.pose(BB.unwrap_rotations(frames, ref_triples) if fmt == '0x64' else frames,
                           '64' if fmt == '0x64' else 'c8')
        skel, clip, worst = BB.convert(posed, {}, {'file': '', 'by': '', 'sha256': '', 'url': ''})
    except Exception as e:
        return key, ('gate', 'conversion failed: %s' % e, stream_frames)
    if worst > 1e-3:
        return key, ('gate', 'FK self-check failed: %.6f m' % worst, stream_frames)

    def jump_failure(cl, sk):
        fr = BB.fk_frames(cl, sk)
        prev = None
        for f, X in enumerate(fr):
            if prev:
                for n, q in X.items():
                    if n == 'Hips':
                        continue
                    d = sum((q[i] - X['Hips'][i] - (prev[n][i] - prev['Hips'][i])) ** 2
                            for i in range(3)) ** 0.5
                    if d >= BB.JUMP_TOL:
                        return '%s jumps %.2f m on frame %d' % (n, d, f)
            prev = X
        return None

    why = BB.implausible(clip, skel)          # slot-standard presentation verdict
    jf = jump_failure(clip, skel)             # integrity: broken unwrap check
    skel_b = None
    if (why or jf) and fmt == '0x64':
        # Branch selection in unwrap_rotations is heuristic: also try the
        # backward-anchored chain. Selection rule: the chain the bank's own
        # shipped slot clips embody — for Jun's stance the backward chain
        # reproduces the shipped t3_neutral EXACTLY (max 1-|dot| = 0.0)
        # while the forward chain does not, so at equal-or-shallower floor
        # depth the backward chain wins; a jump-fixing backward chain
        # always wins. (Validated against all 20 shipped roger+jun slot
        # clips: see the S5 bake reports.)
        try:
            posed_b = synth.pose(list(reversed(BB.unwrap_rotations(list(reversed(frames)), ref_triples))), '64')
            skel_b, clip_b, worst_b = BB.convert(posed_b, {}, {'file': '', 'by': '', 'sha256': '', 'url': ''})
        except Exception:
            skel_b = None
        if skel_b is not None and worst_b <= 1e-3:
            why_b = BB.implausible(clip_b, skel_b)
            jf_b = jump_failure(clip_b, skel_b)

            def floor_depth(w):
                return float(w.split(' ')[1]) if w and 'below the floor' in w else None

            better = False
            if jf and not jf_b:
                better = True
            elif not jf and not jf_b:
                if why_b is None:
                    better = True
                elif why is not None:
                    df, db = floor_depth(why), floor_depth(why_b)
                    if df is not None and db is not None:
                        better = db <= df
                    elif df is None and db is not None:
                        better = True    # forward fails non-floor, backward floor-only
            if better:
                skel, clip, worst, why, jf = skel_b, clip_b, worst_b, why_b, jf_b
    if jf:
        return key, ('gate', 'inter-frame jump check failed: ' + jf, stream_frames)
    ship = _CTX.get('ship_refs', {}).get(key)
    if ship is not None and fmt == '0x64':
        # This entry is a shipped slot clip: the bank's own conversion of it
        # is proven in-game, and the shipped banks are heterogeneous (Jun's
        # stance is the ref-anchored backward chain; her grab, re-baked in
        # #1568, is the unanchored forward chain). If the selected chain
        # does not reproduce the shipped clip, try the remaining unwrap
        # variants and keep the one that does.
        def quat_err(cl):
            err = 0.0
            for b in cl['bones']:
                sq = np.array(ship['rot'][b])
                pq = np.array(cl['rot_xyzw'][b])
                if len(sq) != len(pq):
                    return 9.9
                err = max(err, 1.0 - float(np.abs(np.sum(sq * pq, axis=1)).min()))
            return err

        if quat_err(clip) > 1e-4:
            tried = {'ref_fwd'}
            if skel_b is not None:
                tried.add('ref_bwd')
            for vn in ('ref_bwd', 'none_fwd', 'none_bwd', 'ref_fwd'):
                if vn in tried:
                    continue
                tried.add(vn)
                vref = ref_triples if vn.startswith('ref') else None
                try:
                    if vn.endswith('fwd'):
                        posed_v = synth.pose(BB.unwrap_rotations(frames, vref), '64')
                    else:
                        posed_v = synth.pose(list(reversed(BB.unwrap_rotations(list(reversed(frames)), vref))), '64')
                    skel_v, clip_v, worst_v = BB.convert(posed_v, {}, {'file': '', 'by': '', 'sha256': '', 'url': ''})
                except Exception:
                    continue
                if worst_v <= 1e-3 and quat_err(clip_v) <= 1e-4:
                    skel, clip, worst = skel_v, clip_v, worst_v
                    why = BB.implausible(clip, skel)
                    break
            else:
                why = (why or '') + ' [slot reference not reproduced by any unwrap variant]'
    presentation = why
    if why:
        m = re.match(r'(Left|Right)ToeBase ([\d.]+) m below the floor on frame (\d+)', why)
        if m and float(m.group(2)) <= 0.12:
            why2 = BB.implausible_excl(clip, skel, {'LeftToeBase', 'RightToeBase'})
            fk = BB.fk_frames(clip, skel)
            ankle_min = min(min(X['LeftFoot'][1], X['RightFoot'][1]) for X in fk)
            if why2 is None and ankle_min >= -0.02:
                presentation = ('toe graze %.2f m (frame %s) — passes the bank bake\'s '
                                'second-pass rule' % (float(m.group(2)), m.group(3)))
    return key, ('ok', (clip, presentation), stream_frames)


def slot_sources(bank_dir, mb, by_i):
    """Map shipped slot name -> grid index via each clip's own ttt2_source
    provenance (move name + anim + anim_ref must all match the grid)."""
    out, unmatched = {}, []
    for f in sorted(os.listdir(bank_dir)):
        if not (f.startswith('t3_') and f.endswith('.json')):
            continue
        slot = f[:-5]
        src = json.load(open(os.path.join(bank_dir, f))).get('ttt2_source')
        if not src:
            continue
        want = (src['moves'][0], src['anim'], (src['bank'] << 14) | src['clip'])
        gi = None
        for cand, r in by_i.items():           # join-authoritative match first
            if (r['name'], r['anim'], r['ref']) == want:
                gi = cand
                break
        if gi is None:
            for cand, rec in enumerate(mb.grid):
                if rec == want:
                    gi = cand
                    break
        if gi is None:
            unmatched.append(slot)
        else:
            out[slot] = gi
    return out, unmatched


def enc_quats(clip, bones):
    n = len(clip['root_t'])
    arr = np.empty((n, len(bones), 4), dtype='<i2')
    for bi, b in enumerate(bones):
        q = np.array(clip['rot_xyzw'][b], float)
        q[q[:, 3] < 0] = -q[q[:, 3] < 0]
        arr[:, bi, :] = np.round(np.clip(q, -1, 1) * 32767).astype('<i2')
    return base64.b64encode(arr.tobytes()).decode()


def enc_root(clip, axis):
    v = np.array([r[axis] for r in clip['root_t']], float)
    return base64.b64encode(np.round(v * 1000).astype('<i2').tobytes()).decode()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bank', required=True, choices=('roger', 'jun'))
    ap.add_argument('--data004', required=True)
    ap.add_argument('--data005', required=True)
    ap.add_argument('--data006', required=True)
    ap.add_argument('--decoder64', required=True)
    ap.add_argument('--calib', required=True)
    ap.add_argument('--root-affine', required=True)
    ap.add_argument('--rest', required=True)
    ap.add_argument('--join', required=True)
    ap.add_argument('--bank-dir', required=True)
    ap.add_argument('--fighter', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--write-move-rows', action='store_true')
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    import time
    t0 = time.time()

    d4 = open(a.data004, 'rb').read()
    d5 = open(a.data005, 'rb').read()
    d6 = open(a.data006, 'rb').read()
    shas = {'data004-decoded.bin': sha256_bytes(d4), 'data005-decoded.bin': sha256_bytes(d5),
            'data006-decoded.bin': sha256_bytes(d6)}
    spec = importlib.util.spec_from_file_location('dec64', a.decoder64)
    dec64 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dec64)
    u32 = lambda d, o: struct.unpack('>I', d[o:o + 4])[0]
    tables = {1: (d5, BANK1_TABLE[a.bank]), 2: (d4, 0x100)}

    mb = Motbin(d6, a.bank)
    join, by_i, unmapped = load_join(a.join, mb)
    print('grid: %d slots scanned, %d valid records' % (len(mb.grid), sum(1 for r in mb.grid if r)))
    print('join: %d records, %d mapped to the grid, %d unmapped' % (len(join['records']), len(by_i), len(unmapped)))
    for r in unmapped:
        print('  unmapped join record: %s (i=%s, ref=%s)' % (r['name'], r['i'], r['ref']))

    slots, unmatched_slots = slot_sources(a.bank_dir, mb, by_i)
    print('slot sources on the %s grid: %s' % (a.bank, slots))
    if unmatched_slots:
        print('  slots with no record in this motbin: %s' % unmatched_slots)
    slot_idx = set(slots.values())

    # frame-0 branch reference: the bank's own stance entry triples.
    neutral = json.load(open(os.path.join(a.bank_dir, 't3_neutral.json')))['ttt2_source']
    ndata, ntab = tables[neutral['bank']]
    neoff = ntab + u32(ndata, ntab + 16 + 4 * neutral['clip'])
    ref_triples = dec64.decode_clip(ndata, neoff)['frames'][0]

    jobs, withheld = {}, {}
    for gi in sorted(by_i):
        if gi in WITHHELD:
            withheld[str(gi)] = WITHHELD[gi]
            continue
        fa, la, w32 = mb.fields(gi)
        if fa > 0 or (w32 & 0x400000) or gi in slot_idx:
            jobs[gi] = by_i[gi]
    print('row set: %d records (%d withheld)' % (len(jobs), len(withheld)))

    entries, bank0_rows = set(), []
    for gi, r in jobs.items():
        if (r['ref'] >> 14) == 0:
            bank0_rows.append(gi)
        else:
            entries.add((r['ref'] >> 14, r['ref'] & 0x3FFF))
    entries = sorted(entries)
    print('unique MOTA entries to bake: %d' % len(entries))

    _CTX['dec64'] = dec64
    _CTX['synth'] = Synthesizer(a.calib, json.load(open(a.rest)), a.root_affine)
    _CTX['ref_triples'] = ref_triples
    _CTX['tables'] = tables
    ship_refs = {}
    for slot, gi in slots.items():
        r = by_i[gi]
        clip = json.load(open(os.path.join(a.bank_dir, slot + '.json')))
        ship_refs[(r['ref'] >> 14, r['ref'] & 0x3FFF)] = {'rot': clip['rot_xyzw']}
    _CTX['ship_refs'] = ship_refs
    results = {}
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs) as pool:
            for n, (key, res) in enumerate(pool.imap_unordered(bake_entry, entries)):
                results[key] = res
                if (n + 1) % 50 == 0:
                    print('  baked %d/%d entries' % (n + 1, len(entries)), flush=True)
    else:
        for key in entries:
            results[key] = bake_entry(key)[1]

    bones = None
    pack_rows, hit_rows, missing = {}, {}, dict(withheld)
    presentation_failures = {}
    sanity = {'first_gt_last': 0, 'first_gt_stream': 0, 'word_classes': {}}
    buttons = {}
    for gi in bank0_rows:
        missing[str(gi)] = 'bank-0 table not wired in this production'
    for gi, r in sorted(jobs.items()):
        if (r['ref'] >> 14) == 0:
            continue
        fa, la, w32 = mb.fields(gi)
        word, throw = w32 & 0xFFFF, 1 if (w32 & 0x400000) else 0
        status, payload, stream = results[(r['ref'] >> 14, r['ref'] & 0x3FFF)]
        if status == 'decode':
            missing[str(gi)] = payload
            continue
        # hit row (T3 inclusion rule: attacks and throws only); the window
        # facts come from the move record, the stream from the decode
        if fa > 0 or throw:
            btn = 0
            slot = next((s for s, g in slots.items() if g == gi), None)
            if slot in SLOT_BUTTONS:
                btn = SLOT_BUTTONS[slot]
            elif r['name'] in GRAB_BUTTONS:
                btn = GRAB_BUTTONS[r['name']]
            if btn:
                buttons[str(gi)] = {'move': r['name'], 'button': btn, 'via': slot or 'grab record'}
            hit_rows[str(gi)] = [fa, la, stream, word, throw, btn]
            if fa > la:
                sanity['first_gt_last'] += 1
            if fa > stream:
                sanity['first_gt_stream'] += 1
            sanity['word_classes'][attack_level(word)] = \
                sanity['word_classes'].get(attack_level(word), 0) + 1
        if status == 'gate':
            missing[str(gi)] = payload
            continue
        clip, presentation = payload
        if presentation and not presentation.startswith('toe graze'):
            presentation_failures[str(gi)] = presentation
        if bones is None:
            bones = clip['bones']
        pack_rows[str(gi)] = {'slot': r['ref'] & 0x3FFF, 'move_row': gi, 'stream_frames': stream,
                              'n': len(clip['root_t']), 'used_by': [a.fighter],
                              'q': enc_quats(clip, bones),
                              'rx': enc_root(clip, 0), 'ry': enc_root(clip, 1), 'rz': enc_root(clip, 2)}

    label = 'data006-decoded.bin [%s] motbin' % ('ROGER' if a.bank == 'roger' else 'JUN_KAZAMA')
    pack = {'format': 'wh-anim-pack/1', 'bank': label, 'body_kmd': BODY_KMD[a.bank],
            'target_rig': 'ttt2-mannequin-21 (game/assets/anim/t3/%s/skeleton.json)' % a.bank,
            'bones': bones, 'fps': 60.0, 'hand_keyed': False,
            'decoder': 'tools/ttt2_mota_decode64.py (0x64) + ttt2_bank_bake.decode_c8 (0xC8)',
            'tool': 'tools/anim/ttt2_bank_rows.py -> tools/anim/ttt2_bank_bake.py '
                    '(pipeline of WH #1558/#1561)',
            'sha256': shas, 'rows': pack_rows, 'missing': missing}
    hit = {'format': 'wh-hitframes/1', 'bank': label,
           'source': 'data006-decoded.bin motbin move records (first_active @+0x40, '
                     'last_active @+0x44, attack word + throw flag @+0x5C) joined by '
                     'docs/tech/ttt2-mota/join/%s-join.json; stream_frames decoded via '
                     'bank tables (bank 1 data005 @%d, bank 2 data004 @0x100)'
                     % (a.bank, BANK1_TABLE[a.bank]),
           'sha256': shas,
           'tool': 'tools/anim/ttt2_bank_rows.py', 'fps': 60,
           'fields': ['active_first', 'active_last', 'stream_frames', 'attack_word', 'throw', 'button'],
           'rows': hit_rows}
    os.makedirs(a.out_dir, exist_ok=True)
    pack_path = os.path.join(a.out_dir, 'rows.pack.json')
    hit_path = os.path.join(a.out_dir, 'hit_frames.json')
    with open(pack_path, 'w') as f:
        json.dump(pack, f, separators=(',', ':'))
    with open(hit_path, 'w') as f:
        json.dump(hit, f, separators=(',', ':'))

    stamped = []
    if a.write_move_rows:
        for slot, gi in sorted(slots.items()):
            p = os.path.join(a.bank_dir, slot + '.json')
            clip = json.load(open(p))
            if clip.get('move_row') != gi:
                clip['move_row'] = gi
                with open(p, 'w') as f:
                    json.dump(clip, f, separators=(',', ':'))
            stamped.append({'slot': slot, 'move_row': gi})

    report = {'bank': a.bank, 'fighter': a.fighter, 'tool': 'tools/anim/ttt2_bank_rows.py',
              'join_records': len(join['records']), 'join_mapped': len(by_i),
              'join_unmapped': [{'i': r['i'], 'name': r['name'], 'ref': r['ref']} for r in unmapped],
              'grid_valid_records': sum(1 for r in mb.grid if r),
              'slot_sources': slots, 'slots_without_grid_record': unmatched_slots,
              'row_set': len(jobs), 'unique_entries': len(entries),
              'pack_rows': len(pack_rows), 'hit_rows': len(hit_rows), 'missing': missing,
              'presentation_gate_failures': presentation_failures,
              'sanity': sanity, 'buttons_assigned': buttons,
              'move_rows_stamped': stamped,
              'pack_bytes': os.path.getsize(pack_path), 'hit_bytes': os.path.getsize(hit_path),
              'sha256': shas, 'elapsed_s': round(time.time() - t0, 1)}
    with open(a.report, 'w') as f:
        json.dump(report, f, indent=1)
    print('ROWS_DONE %s: pack %d rows (%.2f MB), hit_frames %d rows, missing %d -> %s'
          % (a.bank, len(pack_rows), report['pack_bytes'] / 1e6, len(hit_rows), len(missing), a.out_dir))


if __name__ == '__main__':
    main()
