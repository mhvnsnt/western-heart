#!/usr/bin/env python3
"""Anim-motion audit: does each move play a clip whose ACTUAL motion matches
the move (limb, hit level, stance, direction, travel)?

Replicates game/js/fighter.js _attackClipPlan (own > notation > anim > donor >
match > generic) over the decoded T3 banks in game/assets/anim/t3/, then checks
the played clip with forward kinematics (not JSON labels):
- stance from root_t Y trajectory, relative to each bank's own neutral height
- striking limb from the decoded branch button when that limb participates,
  else the dominant limb; for legs the FOOT decides (lift at/near active)
- hit level from the decoded attack word vs the move's T7/T8 level
  (h<->l HARD, m<->l MED, h<->m note; s matches m/l, u matches anything)
- string-vs-chord: a string ender on a chord row is HARD only when the
  motion itself is multi-limb or the wrong limb (a chord BRANCH mask alone,
  e.g. king row 113 f+3, is INFO); throws are exempt (chord branches legit)
- jab identity: duck-dip or travel > 0.5 m on a jab is HARD

Usage: python3 tools/combat-qa/anim_motion_audit.py [--out FILE] [--fighters a,b]
Output: JSON with per-move played row, pick kind, flags, and counts.
Simulation/scan proof only -- this does NOT play the game.
Button names in output docs use LP1/RP2/LK3/RK4 (Tekken 1/2/3/4).
"""
import json, math, base64, re, struct
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
ANIM = ROOT / 'game/assets/anim/t3'
MS = ROOT / 'game/assets/movesets'

BANK_DIR = {'king': 'king_on_pantera_leoman', 'jin': 'jin', 'bryan': 'bryan',
            'heihachi': 'heihachi_on_jin', 'yoshimitsu': 'yoshimitsu'}
SOURCE_TO_BANK = {'king': 'king', 'jin': 'jin', 'bryan': 'bryan', 'heihachi': 'heihachi',
                  'yoshimitsu': 'yoshimitsu', 'demonio': 'jin', 'deviljin': 'jin'}
BUTTON_LIMB = {1: 'armL', 2: 'armR', 4: 'legL', 8: 'legR'}
LIMB_JOINTS = {'armL': ('LeftArm', 'LeftForeArm', 'LeftHand'),
               'armR': ('RightArm', 'RightForeArm', 'RightHand'),
               'legL': ('LeftUpLeg', 'LeftLeg', 'LeftFoot'),
               'legR': ('RightUpLeg', 'RightLeg', 'RightFoot')}
SWAP = lambda n: n.replace('Left', '\x00').replace('Right', 'Left').replace('\x00', 'Right') \
    if n.startswith(('Left', 'Right')) else n

def qmul(a, b):
    return [a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],
            a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],
            a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],
            a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]]

def qrot(q, v):
    x, y, z, w = q
    tx = 2*(y*v[2]-z*v[1]); ty = 2*(z*v[0]-x*v[2]); tz = 2*(x*v[1]-y*v[0])
    return [v[0]+w*tx+(y*tz-z*ty), v[1]+w*ty+(z*tx-x*tz), v[2]+w*tz+(x*ty-y*tx)]

def dist(a, b):
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))

def b64i16(s):
    raw = base64.b64decode(s)
    return list(struct.unpack('<%dh' % (len(raw)//2), raw))

def level_of_word(w):
    if w is None: return None
    w = int(w); post = w & 7; guard = w & 0x18
    if not post: return 't' if (w & 0x800) else None
    if post == 2: return 'h'
    if guard == 0x08: return 'l'
    if guard == 0x18: return 's'
    if guard == 0: return 'u'
    return 'm'

class Bank:
    def __init__(self, bank_id):
        self.id = bank_id
        d = ANIM / BANK_DIR[bank_id]
        self.dir = d
        skel = json.load(open(d / 'skeleton.json'))
        self.joints = skel['joints']
        self.P = {j['name']: j['rest'] for j in self.joints}
        self.par = {j['name']: j['parent'] for j in self.joints}
        self.order = [j['name'] for j in self.joints]
        pack = json.load(open(d / 'rows.pack.json'))
        self.bones = pack['bones']; self.fps = pack.get('fps', 30.0)
        self.rows = {}
        for row, rec in pack['rows'].items():
            q = b64i16(rec['q']); rx = b64i16(rec['rx']); ry = b64i16(rec['ry']); rz = b64i16(rec['rz'])
            nb = len(self.bones); n = rec['n']
            rot = {}
            for bi, b in enumerate(self.bones):
                rot[b] = [[q[(f*nb+bi)*4+k]/32767 for k in range(4)] for f in range(n)]
            root_t = [[rx[f]/1000, ry[f]/1000, rz[f]/1000] for f in range(n)]
            self.rows[int(row)] = {'rec': rec, 'rot': rot, 'root_t': root_t, 'n': n}
        hf = json.load(open(d / 'hit_frames.json'))
        self.hit = {int(k): v for k, v in hf['rows'].items()}
        # named action clips for facing detection
        self.actions = {}
        for name, fn in [('stance', 't3_neutral.json'), ('walkFwd', 't3_walk_fwd.json'),
                         ('crouchHold', 't3_crouch_hold.json'), ('block', 't3_block.json'),
                         ('light', 't3_light.json'), ('medium', 't3_medium.json'),
                         ('heavy', 't3_heavy.json'), ('grab', 't3_grab.json')]:
            p = d / fn
            if p.exists():
                self.actions[name] = json.load(open(p))
        self.turned = self._facing()
        # per-bank standing height = median root_t Y of the neutral clip
        # (yoshimitsu's root_t scale does not match its skeleton, so all
        # stance thresholds are relative to this, never absolute)
        import statistics as _st
        neut = self.actions.get('stance')
        self.standingY = _st.median([t[1] for t in neut['root_t']]) if neut and neut.get('root_t') else None
        skel_root = None
        try:
            skel_root = json.load(open(d / 'skeleton.json')).get('root_rest_y')
        except Exception:
            pass
        self.rootY = skel_root
        # strike pool (JS bankAttackPool equivalent, on turned labels)
        self.pool_strike, self.pool_throw = self._pools()

    def fk(self, rot, f):
        G, X = {}, {}
        for j in self.order:
            r = rot.get(j)
            q = r[min(f, len(r)-1)] if r else [0, 0, 0, 1]
            p = self.par[j]
            if p and p in G:
                G[j] = qmul(G[p], q)
                o = qrot(G[p], [self.P[j][i]-self.P[p][i] for i in range(3)])
                X[j] = [X[p][i]+o[i] for i in range(3)]
            else:
                G[j] = q; X[j] = list(self.P[j])
        return G, X

    def _facing(self):
        fwd = left = 0.0; samples = 0
        for name in ['stance', 'walkFwd', 'crouchHold', 'block']:
            data = self.actions.get(name)
            if not data or 'rot_xyzw' not in data: continue
            rot = data['rot_xyzw']
            n = max((len(v) for v in rot.values()), default=0)
            for f in range(n):
                G, X = self.fk(rot, f)
                if 'Hips' not in G: continue
                hx = qrot(G['Hips'], [1, 0, 0])
                fx, fz = -hx[2], hx[0]
                fl = math.hypot(fx, fz)
                if fl < 1e-6: continue
                fx /= fl; fz /= fl
                for s in ['Left', 'Right']:
                    a, k, e = X.get(s+'UpLeg'), X.get(s+'Leg'), X.get(s+'Foot')
                    if not a or not k or not e: continue
                    ox = k[0]-(a[0]+e[0])/2; oz = k[2]-(a[2]+e[2])/2
                    fwd += ox*fx+oz*fz; left += ox*fz-oz*fx; samples += 1
        return samples > 0 and fwd < 0

    def _lab(self, raw):
        # apply turn: swap L/R joint names in the label space
        return SWAP(raw) if self.turned else raw

    def profile(self, row):
        """Return dict for a row clip: dominant limb (turned labels), ext per limb,
        root_t Y trajectory class, peak frame, end height at peak, travel."""
        if not hasattr(self, '_prof'):
            self._prof = {}
        if row in self._prof:
            return self._prof[row]
        p = self._profile_uncached(row)
        self._prof[row] = p
        return p

    def _profile_uncached(self, row):
        rec = self.rows.get(row)
        if rec is None: return None
        rot, rt, n = rec['rot'], rec['root_t'], rec['n']
        # single FK pass; heights/distances are turn-invariant, labels swap at the end
        Xs = [self.fk(rot, f)[1] for f in range(n)]
        limbs = {}
        for limb, ch in LIMB_JOINTS.items():
            lab = self._lab(limb)
            if any(c not in self.P for c in ch) or 'Hips' not in self.P: continue
            length = dist(self.P[ch[0]], self.P[ch[1]]) + dist(self.P[ch[1]], self.P[ch[2]])
            ds = [dist(X[ch[2]], X['Hips']) for X in Xs]
            pf = max(range(n), key=lambda f: ds[f])
            limbs[lab] = {'peakF': pf, 'ext': (ds[pf]-ds[0])/length if length else 0,
                          'reach': ds[pf]/length if length else 0, 'd0': ds[0], 'dpeak': ds[pf],
                          'endY': Xs[pf][ch[2]][1] + rt[pf][1] - (self.rootY or 0),
                          'endAboveHips': Xs[pf][ch[2]][1] - (self.rootY or 0)}
        dom = max(limbs, key=lambda k: limbs[k]['ext']) if limbs else None
        ys = [t[1] for t in rt]
        y0, ymin, ymax = ys[0], min(ys), max(ys)
        sy = self.standingY if self.standingY is not None else y0
        meanY = sum(ys)/len(ys)
        # stance class, all thresholds relative to the bank's own neutral
        # height (crouch holds sit 0.13-0.21 below neutral; jumps peak +0.8)
        if y0 - sy > 0.25:
            stance = 'starts-airborne'
        elif ymax - sy > 0.30 and ys[-1] < sy + 0.15:
            stance = 'jump'
        elif ymin < sy - 0.55:
            stance = 'ground'
        elif meanY < sy - 0.12 and ys[-1] < sy - 0.08:
            stance = 'crouch'
        elif ymin < sy - 0.25:
            stance = 'duck-dip'
        else:
            stance = 'standing'
        # end height at dominant peak (FK end Y + root_t Y; height is turn-invariant)
        endY = limbs[dom]['endY'] if dom else None
        travel = math.hypot(rt[-1][0]-rt[0][0], rt[-1][2]-rt[0][2])
        travel_max = max(math.hypot(t[0]-rt[0][0], t[2]-rt[0][2]) for t in rt)
        # foot lift per leg (turned labels): world foot Y + root_t Y, relative
        # to frame 0. Extension is useless for kicks (a straight leg rotating
        # up keeps hip distance ~constant); foot lift is what makes a kick.
        feet = {}
        for raw, lab in (('LeftFoot', 'legL'), ('RightFoot', 'legR')):
            if raw in self.P and 'Hips' in self.P:
                fy = [Xs[f][raw][1] + rt[f][1] - (self.rootY or 0) for f in range(n)]
                feet[self._lab(lab)] = {'lift': max(fy) - fy[0], 'y0': fy[0],
                                        'at_active': None}
        hf = self.hit.get(row)
        if hf and hf[0] > 0 and feet:
            b = max(0, min((hf[0] - 1) // 2, n - 1))
            for lab in feet:
                raw = 'LeftFoot' if (lab == 'legL') != self.turned else 'RightFoot'
                feet[lab]['at_active'] = Xs[b][raw][1] + rt[b][1] - (self.rootY or 0)
        return {'row': row, 'limbs': limbs, 'dominant': dom, 'stance': stance, 'feet': feet,
                'y0': y0, 'ymin': ymin, 'ymax': ymax, 'meanY': meanY, 'standingY': sy,
                'peakF': limbs[dom]['peakF'] if dom else None,
                'endY': endY, 'travel': travel, 'travel_max': travel_max,
                'hit': hf, 'throw': bool(hf and hf[4]),
                'level': level_of_word(hf[3]) if hf else None,
                'btn': hf[5] if hf and len(hf) > 5 else 0,
                'btn_limb': BUTTON_LIMB.get(hf[5]) if hf and len(hf) > 5 else None,
                'active': (hf[0], hf[1]) if hf else None}

    def _pools(self):
        strike, throw = [], []
        for row in sorted(self.rows):
            prof = self.profile(row)
            hf = self.hit.get(row)
            if not hf or not (hf[0] > 0): continue
            btn = hf[5] if len(hf) > 5 else 0
            limb = BUTTON_LIMB.get(btn)
            limbSrc = 'button'
            if not limb and not btn:
                if prof and prof['dominant'] and (hf[4] or prof['limbs'][prof['dominant']]['ext'] >= 0.1):
                    limb = prof['dominant']; limbSrc = 'measured'
                elif not hf[4]:
                    continue
            t0 = hf[0]/60.0
            entry = {'row': row, 'btn': btn, 'limb': limb, 'limbSrc': limbSrc,
                     'level': 't' if hf[4] else level_of_word(hf[3]), 't0': t0}
            (throw if hf[4] else strike).append(entry)
        return strike, throw

    def action_profile(self, name):
        """Generic action clip (light/medium/heavy/grab): move_row + throw flag + limb."""
        data = self.actions.get(name)
        if not data: return None
        mr = data.get('move_row')
        hf = self.hit.get(mr) if mr is not None else None
        # measured dominant from its own frames
        rot = data.get('rot_xyzw')
        dom = None; exts = {}
        if rot:
            n = max((len(v) for v in rot.values()), default=0)
            for limb, ch in LIMB_JOINTS.items():
                lab = self._lab(limb)
                length = dist(self.P[ch[0]], self.P[ch[1]]) + dist(self.P[ch[1]], self.P[ch[2]])
                ds = []
                for f in range(n):
                    _, X = self.fk(rot, f)
                    ds.append(dist(X[ch[2]], X['Hips']))
                exts[lab] = (max(ds)-ds[0])/length if length else 0
            dom = max(exts, key=exts.get) if exts else None
        return {'name': name, 'move_row': mr, 'hit': hf,
                'throw': bool(hf and hf[4]),
                'btn_limb': BUTTON_LIMB.get(hf[5]) if hf and len(hf) > 5 else None,
                'dominant': dom, 'exts': exts}

BANKS = {}
def bank(bid):
    if bid not in BANKS: BANKS[bid] = Bank(bid)
    return BANKS[bid]

# ---- move expectations -------------------------------------------------
def last_button(notation):
    """Last hit's button(s) of a notation, e.g. 'd/f+2,1' -> ['1']; '1+2' -> ['1','2']."""
    if not notation: return []
    last = str(notation).split(',')[-1].strip()
    last = last.split(':')[0].split('~')[0]
    m = None
    import re
    mm = re.search(r'([1-4](?:\+[1-4])*)\s*$', last)
    return mm.group(1).split('+') if mm else []

def expected_stance(notation):
    n = str(notation or '')
    first = n.split(',')[0].strip().upper()
    if first.startswith(('WS.', 'WS')): return 'ws'
    if first.startswith(('FC.', 'FC')): return 'crouch'
    if first.startswith('SS.'): return 'sidestep'
    if first.startswith('BT.'): return 'backturned'
    if first.startswith(('U/F', 'U/B', 'UF', 'UB', 'U+')): return 'jump'
    if first.startswith(('D+','D/')) or first.startswith('D,'): return 'crouch'
    if 'D+3+4' in first or first.startswith('D+'): return 'crouch'
    if first.startswith('F+') or first.startswith('B+'): return 'standing'
    return 'standing'

def t7_level(move):
    t7 = move.get('t7') or {}
    lab = t7.get('hit_level') or move.get('hit_level') or ''
    toks = [t.strip() for t in str(lab).split(',') if t.strip()]
    if not toks: return None
    t = toks[-1].lower().replace('!', '').replace('(', '').replace(')', '').strip()
    if t.startswith('throw') or t == 't': return 't'
    if t.startswith('s'): return 's'
    if t in ('h', 'high'): return 'h'
    if t in ('m', 'mid'): return 'm'
    if t in ('l', 'low'): return 'l'
    if t.startswith('sl'): return 'l'
    return None

def is_grab_move(move, notation):
    if move.get('isGrab') or move.get('throw'): return True
    if move.get('move_class') in ('throw', 'grapple'): return True
    if t7_level(move) == 't': return True
    if str(notation) in ('1+3', '2+4'): return True
    return False

def limb_from_buttons(btns):
    m = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}
    if len(btns) == 1: return m.get(btns[0])
    return 'both' if btns else None

FIGHTERS = {'pantera': 'king', 'burger': 'bryan', 'demonio': 'jin', 'diablo': 'heihachi',
            'kinpo': 'jin', 'phantom': 'yoshimitsu', 'scimitar': 'jin', 'skull': 'bryan'}
NEAR = {'h': ['h', 'm'], 'm': ['m', 's', 'u'], 's': ['s', 'l', 'm'], 'l': ['l', 's'], 'u': ['u', 'm']}

def donor_keys(inp, limb):
    n = re.sub(r'^[A-Z_]+\.', '', str(inp or '')).strip()
    last = n.split(',')[-1].strip()
    keys = ['c:' + n, 's:' + last]
    m = re.match(r'^(d/f|d/b|u/f|u/b|f|b|u|d)?\+?([1-4](?:\+[1-4])*)', last, re.I)
    if m:
        keys.append('db:' + (m.group(1) or 'n').lower() + '+' + m.group(2))
        keys.append('b:' + m.group(2))
        keys.append('b:' + m.group(2).split('+')[-1])
    if limb: keys.append('l:' + limb)
    return keys

def attack_buttons(attack_name, limb):
    last = re.split(r'[,.~:]', str(attack_name or ''))[-1]
    m = 0
    for b in re.findall(r'(?<![a-z/])[1-4](?![0-9])', last, re.I):
        m |= 1 << (int(b) - 1)
    if m: return m
    return {'armL': 1, 'armR': 2, 'legL': 4, 'legR': 8}.get(limb, 0)

class Sim:
    def __init__(self, fid, bank_id):
        self.fid = fid; self.bk = bank(bank_id)
        self.ms = json.load(open(MS / (fid + '.json')))
        self.moves = self.ms.get('moves', {})
        self.slots = dict(self.ms.get('slots', {}))
        for k in self.moves:
            if k not in self.slots: self.slots[k] = k
        self.hit_words = self.ms.get('hit_words', {}) or {}
        self.bank_id = bank_id
        self._build_indexes()

    def _src_maps(self, src):
        return SOURCE_TO_BANK.get(src, src) == self.bank_id or (src == 'king' and self.bank_id == 'armorking')

    def _own(self, mv):
        """(row, kind) or None — mirrors _ownRow('own') then ('anim')."""
        src = mv.get('t3_source') or (self.ms.get('t3_source') if mv.get('t3_row') is not None else None)
        r = mv.get('t3_row')
        if r is not None:
            r = r[-1] if isinstance(r, list) else r
            if self._src_maps(src) and r in self.bk.rows:
                return (r, 'own')
        return None

    def _anim(self, mv):
        a = mv.get('anim_t3')
        if not a: return None
        src = a.get('bank')
        r = a.get('row')
        if r is not None:
            r = r[-1] if isinstance(r, list) else r
            if (SOURCE_TO_BANK.get(src, src) == self.bank_id or (src == 'king' and self.bank_id == 'armorking')) \
               and r in self.bk.rows:
                return (r, 'anim')
        return None

    def _build_indexes(self):
        # _attackRowIndex: keyRow by key, slots, input
        key_row = {}
        for k, mv in self.moves.items():
            o = self._own(mv)
            if o: key_row[k] = o[0]
        by_input = {}
        def add(n, row):
            by_input.setdefault(n, [])
            if row not in by_input[n]: by_input[n].append(row)
        for k, row in key_row.items(): add(k, row)
        for n, k in self.ms.get('slots', {}).items():
            if k in key_row: add(n, key_row[k])
        for k, row in key_row.items():
            inp = self.moves[k].get('input')
            if inp: add(inp, row)
        self.by_input = by_input
        # donor index: first move (JSON order) wins per key
        idx = {}
        for mv in self.moves.values():
            if mv.get('t3_row') is None: continue
            src = mv.get('t3_source') or self.ms.get('t3_source')
            if not self._src_maps(src): continue
            r = mv['t3_row']; r = r[-1] if isinstance(r, list) else r
            for kk in donor_keys(mv.get('input', ''), mv.get('limb')):
                if kk not in idx: idx[kk] = r
        self.donor_idx = idx
        # generic actions
        self.generics = {}
        for name in ['light', 'medium', 'heavy', 'grab']:
            ap = self.bk.action_profile(name)
            if ap: self.generics[name] = ap

    def _row_clip(self, row):
        """(throw, is_attack) for a row clip, as clipIsThrow + hit window check."""
        prof = self.bk.profile(row)
        if not prof: return None
        hf = prof['hit']
        return {'throw': prof['throw'], 'atk': bool(hf and hf[0] > 0), 'prof': prof}

    def plan(self, key):
        mv = self.moves[key]
        inp = key  # tekkenInput = resolved notation
        attack_name = key
        limb = mv.get('limb') if mv.get('limb') in ('armL', 'armR', 'legL', 'legR') else None
        if not limb:
            b = (re.search(r'[1-4]', str(attack_name).split(',')[-1]) or [None])[0]
            limb = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}.get(b, 'armR')
        # level: hit_words first, else t7
        hw = self.hit_words.get(key)
        level = level_of_word(hw) if hw is not None else t7_level(mv)
        grab = is_grab_move(mv, key)
        rejected = []
        def fits_row(row, kind):
            c = self._row_clip(row)
            if not c: return None
            if grab:
                if c['throw'] or not c['atk']: return {'name': 'row:%d' % row, 'kind': kind, 'row': row, 'prof': c['prof']}
                rejected.append('%s row:%d is a strike row' % (kind, row)); return None
            if not c['throw']:
                return {'name': 'row:%d' % row, 'kind': kind, 'row': row, 'prof': c['prof']}
            if c['atk']:
                rejected.append('%s row:%d is a throw row' % (kind, row)); return None
            return {'name': 'row:%d' % row, 'kind': kind, 'row': row, 'prof': c['prof']}
        pick = None
        o = self._own(mv)
        if o: pick = fits_row(o[0], 'own')
        if not pick:
            for n in [inp, attack_name, mv.get('input')]:
                if not n: continue
                for row in self.by_input.get(n, []):
                    pick = fits_row(row, 'notation')
                    if pick: break
                if pick: break
        anim = self._anim(mv)
        anim_nearest = bool(mv.get('anim_t3') and 'nearest' in str(mv['anim_t3'].get('match', '')))
        if not pick and anim and not anim_nearest: pick = fits_row(anim[0], 'anim')
        if not pick:
            for kk in donor_keys(inp, mv.get('limb')):
                r = self.donor_idx.get(kk)
                if r is not None and r in self.bk.rows:
                    pick = fits_row(r, 'donor')
                    if pick: break
        btn = attack_buttons(attack_name, mv.get('limb'))
        btn_limb = BUTTON_LIMB.get(btn, limb)
        relaxed = False
        if not pick:
            pool = self.bk.pool_throw if grab else self.bk.pool_strike
            tiers = []
            for sub in ([c for c in pool if c['btn'] == btn] if btn else [],
                        [c for c in pool if c['limb'] == btn_limb]):
                if not grab and level and level in NEAR:
                    for lv in NEAR[level]: tiers.append([c for c in sub if c['level'] == lv])
                tiers.append(sub)
            if grab: tiers.append(pool)
            S = mv.get('startup') if isinstance(mv.get('startup'), (int, float)) else 0
            for tier in tiers:
                if not tier: continue
                best = min(tier, key=lambda c: abs(c['t0'] - S))
                if level and best['level'] != level and best['level'] not in NEAR.get(level, []):
                    relaxed = True
                pick = {'name': 'row:%d' % best['row'], 'kind': 'match', 'row': best['row'],
                        'prof': self.bk.profile(best['row']), 'match': best, 'relaxed': relaxed}
                break
        if not pick and anim and anim_nearest: pick = fits_row(anim[0], 'anim')
        if not pick:
            # generic
            def limb_of(name):
                ap = self.generics[name]
                return ap['btn_limb'] or ap['dominant']
            cands = ([ 'grab'] if grab else []) + ['light', 'medium', 'heavy']
            cands = [n for n in cands if n in self.generics and self.generics[n]['throw'] == grab]
            best = None
            if grab and 'grab' in self.generics and self.generics['grab']['throw']: best = 'grab'
            if not best:
                for want in (lambda d: d == btn_limb, lambda d: (d or '').startswith('arm') == btn_limb.startswith('arm')):
                    for n in cands:
                        if want(limb_of(n)): best = n; break
                    if best: break
            best = best or ('grab' if grab else ('light' if btn_limb.startswith('arm') else 'medium'))
            if best in self.generics:
                ap = self.generics[best]
                pick = {'name': best, 'kind': 'generic', 'row': ap['move_row'], 'generic': ap,
                        'prof': self.bk.profile(ap['move_row']) if ap['move_row'] in self.bk.rows else None}
        return {'move': mv, 'key': key, 'pick': pick, 'rejected': rejected, 'limb': limb,
                'level': level, 'grab': grab, 'btn': btn, 'btn_limb': btn_limb}

def played_limb(pick):
    """Striking limb of a row clip: the decoded T3 branch-command button when
    it names one limb AND that limb actually participates in the motion
    (ext >= 0.2); if the button limb barely moves while another limb
    extends >= 0.5, the motion's dominant limb is what the eye sees
    (e.g. jin row 97, btn LP1, armR ext 0.83 / armL ext 0.10: a right-arm
    motion mislabeled by its branch command). Chord/unknown rows: dominant.
    Generic actions: decoded button, else dominant."""
    if not pick: return None
    if pick['kind'] == 'generic':
        ap = pick['generic']
        return ap['btn_limb'] or ap['dominant']
    prof = pick.get('prof')
    if not prof: return None
    dom = prof['dominant']
    dom_ext = prof['limbs'].get(dom, {}).get('ext', 0) if dom else 0
    if prof['btn_limb']:
        # Leg branch: the foot decides. A real kick lifts its foot even when
        # arm swing dominates extension; a leg row with no foot lift is not
        # a kick (e.g. king row 108 back-3 family) even if labeled by button.
        if prof['btn_limb'] in ('legL', 'legR'):
            lift = (prof.get('feet') or {}).get(prof['btn_limb'], {}).get('lift', 0)
            if lift >= 0.3:
                return prof['btn_limb']
            if dom_ext >= 0.5:
                return dom
            return dom if (dom and dom_ext >= 0.15) else prof['btn_limb']
        btn_ext = prof['limbs'].get(prof['btn_limb'], {}).get('ext', 0)
        if btn_ext < 0.2 and dom_ext >= 0.5:
            return dom
        return prof['btn_limb']
    # Chord/unknown row with no extension-dominant limb: a kicking leg still
    # shows in foot lift (king row 113, btn 12, is a legL kick by foot 1.35 m
    # at active despite armR 0.49 being the largest extension).
    if dom_ext < 0.5 and prof.get('feet'):
        lifts = {k: v.get('lift', 0) for k, v in prof['feet'].items()}
        kick = [k for k, v in lifts.items() if v >= 0.5]
        other = [k for k, v in lifts.items() if k not in kick]
        if len(kick) == 1 and all(lifts[k] < 0.3 for k in other):
            return kick[0]
    if dom and dom_ext >= 0.15:
        return dom
    return dom

def played_level(pick):
    if not pick: return None
    if pick['kind'] == 'generic':
        ap = pick['generic']
        return 't' if ap['throw'] else level_of_word(ap['hit'][3]) if ap['hit'] else None
    prof = pick.get('prof')
    return prof['level'] if prof else None

def played_stance(pick):
    if not pick: return None
    if pick['kind'] == 'generic':
        # generic action clips: approximate from their move_row profile
        return pick['prof']['stance'] if pick.get('prof') else None
    return pick['prof']['stance'] if pick.get('prof') else None

VARIANT_RE = re.compile(r'_[rc]\d|__')
def is_variant(key):
    if VARIANT_RE.search(str(key)): return True
    if str(key) in ('b', 'f', 'u', 'd', 'b,n', 'f,n'): return True
    return False

def stance_expect(key):
    n = str(key)
    first = n.split(',')[0].strip()
    u = first.upper()
    if u.startswith('WS'): return 'ws'
    if u.startswith('FC'): return 'crouch'
    if u.startswith('SS'): return 'sidestep'
    if u.startswith('BT'): return 'backturned'
    if u.startswith(('U/F', 'U/B', 'UF', 'UB')) or u.startswith('U+'): return 'jump'
    if u.startswith('D+') or u.startswith('D/'): return 'crouch'
    return 'standing'

def y_active(prof, bk):
    if not prof or not prof.get('hit'): return None
    row = prof['row']
    rec = bk.rows[row]
    f = int(round((prof['hit'][0]-1)/2))
    f = max(0, min(f, rec['n']-1))
    return rec['root_t'][f][1]

def audit_fighter(fid, bank_id):
    sim = Sim(fid, bank_id)
    bk = sim.bk
    sy = bk.standingY
    out = {'fighter': fid, 'bank': bank_id, 'bank_turned': bk.turned, 'standingY': sy,
           'moves': [], 'counts': {}}
    for key, mv in sim.moves.items():
        cls = mv.get('move_class')
        if cls == 'parry':
            continue
        r = sim.plan(key)
        pick = r['pick']
        rec = {'key': key, 'name': mv.get('name'), 'class': cls, 'input': mv.get('input'),
               'limb_declared': mv.get('limb'), 't7_level': t7_level(mv),
               'stance_expect': stance_expect(key), 'variant': '__' in key,
               'own_row': (mv.get('t3_row') if mv.get('t3_row') is not None else
                           (mv.get('anim_t3') or {}).get('row')),
               'pick_kind': pick['kind'] if pick else None,
               'pick_name': pick['name'] if pick else None,
               'flags': []}
        if r['rejected']:
            # Guarded by fighter.js fits(): the game skips the wrong-type row
            # and falls back. A data bug, not a visible mismatch by itself.
            rec['flags'].append(('DATA', 'own-row-type-reject', '; '.join(sorted(set(r['rejected'])))))
        if pick is None:
            rec['flags'].append(('UNMAPPED', 'no-clip', 'plan found no clip (no bank row, no donor, no match, no generic)'))
            out['moves'].append(rec); continue
        prof = pick.get('prof')
        plimb = played_limb(pick)
        plevel = played_level(pick)
        pstance = played_stance(pick)
        rec['played_limb'] = plimb; rec['played_level'] = plevel; rec['played_stance'] = pstance
        rec['played_row'] = pick.get('row')
        variant = is_variant(key)
        rec['variant'] = variant
        btns = last_button(key) if not variant else []
        exp_limb = limb_from_buttons(btns) if btns else mv.get('limb')
        # --- chord / single-button checks ---
        # Throws legitimately use chord branches (1+3/2+4 etc.): skip chord flags for them.
        # A chord BRANCH mask is not the motion: HARD only when the motion itself is
        # multi-limb or the wrong limb; a matching single-limb motion on a chord-branch
        # row (e.g. king f+3 row 113: btn 12 but a legL kick by shape) is INFO only.
        prow_btn = prof['btn'] if prof else None
        is_chord_row = bool(prow_btn and bin(prow_btn).count('1') > 1)
        is_grab = bool(mv.get('isGrab') or mv.get('throw') or mv.get('move_class') in ('grab', 'throw'))
        if is_chord_row and not is_grab:
            exts = sorted((prof['limbs'][k]['ext'] for k in prof['limbs']), reverse=True)
            multi_limb = len(exts) > 1 and exts[1] >= 0.5
            motion_bad = multi_limb or (exp_limb and exp_limb != 'both' and plimb and plimb != exp_limb)
            sev = 'HARD' if motion_bad else 'INFO'
            if len(btns) == 1:
                rec['flags'].append((sev, 'single-on-chord-row',
                    'last hit %s plays chord row %s (btn mask %d)' % (btns[0], pick['name'], prow_btn)))
            if ',' in key and len(btns) == 1:
                rec['flags'].append((sev, 'string-ender-on-chord-row',
                    'string %s ender plays chord row %s' % (key, pick['name'])))
        if len(btns) > 1 and not is_chord_row and pick['kind'] in ('own', 'notation', 'anim'):
            rec['flags'].append(('HARD', 'chord-on-single-row',
                'chord %s plays single-button row %s' % (key, pick['name'])))
        # --- kick reality check: a leg move whose clip never lifts that foot is not a kick ---
        if exp_limb in ('legL', 'legR') and prof and prof.get('feet'):
            lift = prof['feet'].get(exp_limb, {}).get('lift', 0)
            if lift is not None and lift < 0.15:
                rec['flags'].append(('HARD', 'no-kick-motion',
                    'expected %s kick, clip %s never lifts that foot (lift %.2f)' % (exp_limb, pick['name'], lift)))
        # --- limb ---
        if exp_limb and exp_limb != 'both' and plimb and plimb != exp_limb:
            conf = True
            if prof and not prof['btn_limb'] and prof['limbs'].get(plimb, {}).get('ext', 0) < 0.15:
                conf = False
            if conf:
                rec['flags'].append(('HARD', 'limb-mismatch',
                    'expected %s, clip %s plays %s' % (exp_limb, pick['name'], plimb)))
        # --- level (decoded word vs T7) ---
        el = rec['t7_level']
        if el and plevel and el not in ('s', 'u') and plevel not in ('s', 'u'):
            if {el, plevel} == {'h', 'l'}:
                rec['flags'].append(('HARD', 'level-mismatch',
                    'T7 %s but clip %s is %s' % (el, pick['name'], plevel)))
            elif {el, plevel} == {'m', 'l'}:
                rec['flags'].append(('MED', 'level-mismatch',
                    'T7 %s but clip %s is %s' % (el, pick['name'], plevel)))
        # --- class ---
        if r['grab'] and pick['kind'] == 'generic' and not pick['generic']['throw']:
            rec['flags'].append(('HARD', 'throw-on-strike-clip',
                'throw %s falls back to generic %s, which is not a throw row' % (key, pick['name'])))
        # --- stance: whole-clip classes ---
        if prof:
            if prof['stance'] == 'starts-airborne' and rec['stance_expect'] != 'jump':
                rec['flags'].append(('HARD', 'starts-airborne',
                    'clip %s starts %.2f m above neutral (%.2f) then falls' % (pick['name'], prof['y0']-sy, sy)))
            if prof['stance'] == 'jump' and rec['stance_expect'] != 'jump':
                rec['flags'].append(('HARD', 'jump-clip-for-ground-move',
                    'clip %s arcs to %.2f m above neutral' % (pick['name'], prof['ymax']-sy)))
            if prof['stance'] == 'ground':
                rec['flags'].append(('HARD', 'ground-clip',
                    'clip %s falls to %.2f m (floor) — not a strike clip' % (pick['name'], prof['ymin'])))
            if prof['stance'] == 'crouch' and rec['stance_expect'] == 'standing':
                rec['flags'].append(('HARD', 'crouch-clip-for-standing-move',
                    'clip %s stays crouched (mean %.2f vs neutral %.2f)' % (pick['name'], prof['meanY'], sy)))
            # active-frame posture
            ya = y_active(prof, bk)
            rec['y_active'] = ya
            if ya is not None:
                se = rec['stance_expect']
                if se == 'standing' and (ya < sy - 0.18 or ya > sy + 0.25):
                    rec['flags'].append(('MED', 'posture-at-hit',
                        'standing move %s: body at %.2f vs neutral %.2f when the hit lands' % (key, ya, sy)))
                elif se == 'crouch' and ya > sy - 0.08:
                    rec['flags'].append(('MED', 'posture-at-hit',
                        'crouch move %s: body still at %.2f vs neutral %.2f when the hit lands' % (key, ya, sy)))
                elif se == 'jump' and ya < sy + 0.15:
                    rec['flags'].append(('MED', 'posture-at-hit',
                        'jump move %s: body only at %.2f vs neutral %.2f when the hit lands' % (key, ya, sy)))
                elif se == 'ws' and (ya < sy - 0.18 or ya > sy + 0.25):
                    rec['flags'].append(('MED', 'posture-at-hit',
                        'WS move %s: body at %.2f vs neutral %.2f when the hit lands' % (key, ya, sy)))
            # jab identity: basics 1/2 must not duck or travel (incl. the
            # T8-resolved basics the buttons actually fire, e.g. 1~t8.king)
            import re as _re2
            if (key in ('1', '2') or _re2.match(r'^[12]~t8\.', key)) and prof['stance'] == 'duck-dip':
                rec['flags'].append(('HARD', 'jab-ducks',
                    'jab %s clip %s ducks to %.2f (neutral %.2f)' % (key, pick['name'], prof['ymin'], sy)))
            if (key in ('1', '2') or _re2.match(r'^[12]~t8\.', key)) and prof['travel_max'] > 0.5:
                rec['flags'].append(('HARD', 'jab-travels',
                    'jab %s clip %s travels %.2f m' % (key, pick['name'], prof['travel_max'])))
        if pick['kind'] in ('donor', 'match', 'generic'):
            rec['flags'].append(('INFO', 'fallback-clip',
                'no own/notation row; plays %s %s' % (pick['kind'], pick['name'])))
        if pick['kind'] == 'match' and pick.get('relaxed'):
            rec['flags'].append(('MED', 'match-relaxed-level',
                'match pool had no %s-level row; played %s-level row %s' % (r['level'], plevel, pick['name'])))
        if cls == 'signature':
            rec['flags'].append(('INFO', 'signature-no-t7-truth', 'canon move; limb/level checked against declared fields only'))
        out['moves'].append(rec)
    # counts, split pressable vs T3-table-variant keys
    from collections import Counter
    c = Counter()
    for m in out['moves']:
        sev = set(f[0] for f in m['flags'])
        bucket = 'variant' if m.get('variant') else 'pressable'
        if 'HARD' in sev: c[bucket + '_hard'] += 1
        elif 'MED' in sev: c[bucket + '_med'] += 1
        elif 'UNMAPPED' in sev: c[bucket + '_unmapped'] += 1
        else: c[bucket + '_ok_or_info'] += 1
        if any(f[0] == 'DATA' for f in m['flags']): c[bucket + '_guarded_reject'] += 1
        c[bucket + '_total'] += 1
        c['total'] += 1
        if m['pick_kind'] in ('donor', 'match', 'generic'): c['fallback_' + m['pick_kind']] += 1
        elif m['pick_kind']: c['direct_' + m['pick_kind']] += 1
        else: c['no_pick'] += 1
    out['counts'] = dict(c)
    return out

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='anim_motion_audit_results.json')
    ap.add_argument('--fighters', default=None, help='comma list, default all 8')
    ns = ap.parse_args()
    _sel = set(ns.fighters.split(',')) if ns.fighters else None
    results = {}
    for fid, bid in FIGHTERS.items():
        if _sel and fid not in _sel: continue
        print('=== auditing', fid, 'bank', bid, '...', flush=True)
        results[fid] = audit_fighter(fid, bid)
        print(fid, results[fid]['counts'], flush=True)
    json.dump(results, open(ns.out, 'w'), indent=1)
    print('wrote', ns.out)
