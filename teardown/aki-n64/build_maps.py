#!/usr/bin/env python3
"""Build move -> (P1 anim, P2 anim) maps for the five AKI N64 games.

Inputs (all read-only, in ~/workspace/bannon-tier0-moves/aki-n64-five/):
  output/aki-n64-five/move_library.json  9,890 moves (the move universe)
  per-wrestler-all.json                  per-wrestler moves + roles
  *-anims.json                           anim manifests (frames, labels)
  named-anim-maps.json                   NM + WM2000 anim -> name
  *-twinmap.json                         early-game twin names
  library.json (moveset-creator-features)  nm_* library ids (No Mercy)

P2 RULE (validated on VPW2 vs the main lane's vpw2-map.json: 512/512
recall, 0.981 precision; the only 10 false positives are unnamed moves
with no labels at all):
  1. +1 label contains '(P2)' with a matching move name -> ACCEPT.
  2. +1 label contains '(P1)' -> REJECT (attacker anim).
  3. +1 missing from the manifest or attacker-referenced -> REJECT.
  4. +1 label names a different move, or is a taunt/stance/entrance/
     victory anim -> REJECT.
  5. P1 is a solo kind (strike/dive/stance/taunt/attempt, from the
     move kind, the P1 label category, or name keywords) -> REJECT.
  6. Else ACCEPT P2 = P1+1.
Role-based recv_anim_file_id from the Tier 0b pooling (620 early-game
pairs, from real P2-role moveset slots) takes precedence over the rule;
conflicts are flagged, never silently overridden.

No Mercy library-id matching (nm_* -> P1 fid), fallback chain:
  1. VPWStudio label (name, category) in nomercy-anims.json
     (single / consecutive P1+P2 pair / P1-role-marked).
  2. Same with parenthetical qualifiers stripped ('(Win)', ...).
  3. Library-added trailing number stripped.
  4. Per-wrestler in-game menu name (+ category).
  5. named-anim-maps nm_anim_names name (+ context).
  6. move_library display name.
Unmatched library ids and unmapped moves go to <game>-gaps.json with
reasons. Nothing is invented: undeterminable P2 = null + NEEDS-P2 flag.

Outputs (maps/):
  <game>-map.json   {move_id: {p1_fid, p2_fid, name, source, ...}}
  <game>-gaps.json  {unmapped_library_ids, unmapped_moves, p2_flags}
  build-report.json
Map keys: No Mercy uses nm_* library ids where matched, else the
move_library id; the other four games use their move_library ids
(the games' own ids — no library ids invented).
"""
import json
import os
import re
import sys
from collections import defaultdict

WORK = os.path.dirname(os.path.abspath(__file__))
FIVE = '/home/hatch/workspace/bannon-tier0-moves/aki-n64-five'
OUT = os.path.join(WORK, 'maps')
os.makedirs(OUT, exist_ok=True)

GAMES = ['nomercy', 'wm2k', 'revenge', 'vpw64', 'worldtour']

SOLO_CATS = ['striking', 'strike', 'taunt', 'stance', 'diving', 'dive',
             'entrance', 'victory', 'introduction', 'downed strike',
             'apron strike', 'corner striking']
SOLO_KINDS = {'strike', 'dive', 'stance'}
TWO_PERSON_KINDS = {'grapple', 'submission', 'tag', 'reversal'}
STRIKE_WORDS = ['chop', 'kick', 'punch', 'elbow', 'slap', 'lariat',
                'dropkick', 'headbutt', 'boot', 'uppercut',
                'knee strike', 'knife edge']
BAD_LABEL_WORDS = ['taunt', 'stance', 'entrance', 'victory', 'introduction']


def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def parse_label(lab):
    """'[Category] Name P1' -> (category, name, role)."""
    if not lab:
        return None, None, None
    m = re.match(r'^\[(.*?)\]\s*(.*)$', lab)
    if not m:
        return None, lab.strip(), None
    cat, name = m.group(1).strip(), m.group(2).strip()
    role = None
    mm = re.search(r'\bP([12])\b', name)
    if mm:
        role = 'P' + mm.group(1)
    name = re.sub(r'\s*\(?P[12]\)?', '', name).strip()
    name = re.sub(r'\s+', ' ', name)
    return cat, name, role


def label_cat(lab):
    m = re.match(r'\[(.*?)\]', lab or '')
    return m.group(1).lower() if m else ''


def names_match(a, b):
    na, nb = norm(a), norm(b)
    return bool(na and nb) and (na == nb or na in nb or nb in na)


def strip_num(n):
    m = re.match(r'^(.*\D)\s+(\d+)$', n)
    return (m.group(1), int(m.group(2))) if m else (n, None)


def strip_parens(n):
    return re.sub(r'\s*\([^)]*\)', '', n or '').strip()


# ---- No Mercy library-id matching (H3) ----
# The library lane pooled VPWStudio labels by (category, name) — P1/P2
# pairs share a label — then numbered same-base-name collisions in
# DESCENDING P1-fid order (first keeps the name, rest get bare numbers
# 2,3,4...). Validated: reproduces 628/628 independently-confident
# matches with 0 diffs, and all 7 Axe Kick + all 7 DX-family entries.
# Direct unique-pool lookup runs FIRST (the library's category is
# authoritative for pool identity); H3 numbering is only the tiebreak
# for bare-numbered entries with several same-(name, cat) pools.
def build_h3_table(gd):
    pools = defaultdict(list)
    for f, lab in gd.labels.items():
        cat, name, role = parse_label(lab)
        if not name:
            continue
        pools[(cat, name)].append((f[2:].upper(), role))
    moves = []
    for (cat, name), lst in pools.items():
        lst = sorted(lst, key=lambda t: int(t[0], 16))
        p1s = [x for x, r in lst if r == 'P1']
        p2s = [x for x, r in lst if r == 'P2']
        p1 = p1s[0] if len(p1s) == 1 else lst[0][0]
        p2 = None
        if len(p2s) == 1:
            p2 = p2s[0]
        elif ('%04X' % (int(p1, 16) + 1)) in [x for x, r in lst]:
            p2 = '%04X' % (int(p1, 16) + 1)
        moves.append((p1, p2, cat, name))
    by_base = defaultdict(list)
    for p1, p2, cat, name in moves:
        b, _ = strip_num(name)
        by_base[b].append((p1, p2, cat, name))
    assigned = {}
    for base, lst in by_base.items():
        lst = sorted(lst, key=lambda t: int(t[0], 16), reverse=True)
        taken = set()
        n = 1
        for p1, p2, cat, name in lst:
            if name not in taken:
                disp = name
                taken.add(name)
            else:
                n += 1
                disp = f'{base} {n}'
                while disp in taken:
                    n += 1
                    disp = f'{base} {n}'
                taken.add(disp)
            assigned[(norm(disp), norm(cat))] = (p1, p2)
    # direct unique-pool index: (norm name, norm cat) -> (p1, p2).
    # Also indexed by qualifier-stripped name (a pool whose ONLY anims
    # carry a qualifier, e.g. 'Sweet Chin Music (Break Up)', is the
    # library's 'Sweet Chin Music'); the unqualified pool wins ties.
    direct = {}
    for p1, p2, cat, name in moves:
        direct.setdefault((norm(name), norm(cat)), (p1, p2))
    for p1, p2, cat, name in moves:
        direct.setdefault((norm(strip_parens(name)), norm(cat)), (p1, p2))
    return assigned, direct, moves


def strip_parens(n):
    return re.sub(r'\s*\([^)]*\)', '', n or '').strip()


class GameData:
    def __init__(self, game):
        self.game = game
        man = json.load(open(f'{FIVE}/{game}-anims.json'))['anims']
        self.man = {a['fid'].lower(): a for a in man}
        self.labels = {f: a.get('label', '') for f, a in self.man.items()}
        self.frames = {f: a['frames'] for f, a in self.man.items()}
        pw = json.load(open(f'{FIVE}/per-wrestler-all.json'))[game]
        self.attacker_refs = set()
        self.p2_refs = set()
        self.pw_by_name = defaultdict(set)
        self.pw_by_nc = defaultdict(set)
        for w in pw:
            for m in w['moves']:
                fid = (m.get('anim_file_id') or '').upper()
                if not fid:
                    continue
                if m.get('role') == 'P2':
                    self.p2_refs.add(fid)
                else:
                    self.attacker_refs.add(fid)
                nm = m.get('name') or ''
                if nm:
                    self.pw_by_name[norm(nm)].add(fid)
                    for c in m.get('categories', []):
                        self.pw_by_nc[(norm(nm), norm(c))].add(fid)
        # label index: (norm name, norm cat) -> [(fid, role)]
        self.by_nc = defaultdict(list)
        self.by_n = defaultdict(list)
        for f, lab in self.labels.items():
            cat, name, role = parse_label(lab)
            if name:
                self.by_nc[(norm(name), norm(cat))].append((f[2:].upper(), role))
                self.by_n[norm(name)].append((f[2:].upper(), cat, role))
        # named-anim-maps / twinmap names: fid -> [name, context]
        self.names = {}
        if game in ('nomercy', 'wm2k'):
            key = 'nm_anim_names' if game == 'nomercy' else 'wm_anim_names'
            nam = json.load(open(f'{FIVE}/named-anim-maps.json'))[key]
            for fid, (n, c) in nam.items():
                self.names[fid[2:].upper()] = (n, c)
        else:
            tw = json.load(open(f'{FIVE}/{game}-twinmap.json'))
            for fid, v in tw.items():
                for k in ('nm_name', 'wm_name'):
                    if v.get(k):
                        self.names[fid[2:].upper()] = tuple(v[k])
                        break

    def anim_name(self, fid):
        """Best-known move name for an anim fid (or None)."""
        fid = fid.upper()
        if fid in self.names:
            return self.names[fid][0]
        cat, name, role = parse_label(self.labels.get('0x' + fid.lower(), ''))
        return name


def solo_kind(move, gd, p1_fid):
    """True if the move is solo (no receiver anim expected)."""
    kind = move.get('bannon_2k_kind')
    if kind in SOLO_KINDS:
        return True
    name = (move.get('display_name') or move.get('name') or '').lower()
    if 'attempt' in name or 'taunt' in name or name.endswith('pose'):
        return True
    if any(w in name for w in STRIKE_WORDS):
        return True
    c = label_cat(gd.labels.get('0x' + p1_fid.lower(), ''))
    return any(s in c for s in SOLO_CATS)


def rule_p2(move, gd, p1_fid):
    """Validated +1 rule. Returns (p2_fid_or_None, reason, confidence)."""
    nxt = '%04X' % (int(p1_fid, 16) + 1)
    a2 = gd.man.get('0x' + nxt.lower())
    if a2 is None:
        return None, 'p1+1 not in manifest', None
    lab2 = a2.get('label', '') or ''
    p1_name = move.get('display_name') or move.get('name') or ''
    # Unnamed moves carry 'Unnamed Move 0xXXXX' as their name — the P1
    # label's parsed name is the real name for matching purposes
    # (e.g. VPW64 1B30 'Double German Suplex (P1)' vs 1B31 '(P2)').
    if move.get('unnamed') or 'Unnamed Move' in p1_name:
        p1_lab = gd.man.get('0x' + p1_fid.lower(), {}).get('label', '') or ''
        _, p1_lab_name, _ = parse_label(p1_lab)
        if p1_lab_name:
            p1_name = p1_lab_name
    nm2 = gd.anim_name(nxt)
    # 1. decisive (P2) mark with matching name
    if '(P2)' in lab2 or re.search(r'\bP2\b', lab2):
        if nm2 is None or names_match(nm2, p1_name):
            return nxt, 'label-marked P2', 'label'
        return None, 'P2-marked but different move name', None
    # 2. (P1) mark -> attacker anim
    if '(P1)' in lab2 or re.search(r'\bP1\b', lab2):
        return None, 'p1+1 is label-marked P1 (another move)', None
    # 3. attacker-referenced
    if nxt in gd.attacker_refs:
        return None, 'p1+1 is another move attacker anim', None
    # 4. different name / taunt-ish label
    low2 = lab2.lower()
    if any(s in low2 for s in BAD_LABEL_WORDS):
        return None, 'p1+1 label is taunt/stance/entrance', None
    if nm2 and p1_name and not names_match(nm2, p1_name):
        return None, f'p1+1 named differently ({nm2!r})', None
    # 5. solo kind
    if solo_kind(move, gd, p1_fid):
        return None, 'solo kind (strike/dive/stance/taunt/attempt)', 'solo'
    # 6. accept
    conf = 'rule'
    if not p1_name or move.get('unnamed'):
        conf = 'unnamed-inferred'
    return nxt, 'p1+1 rule (validated on VPW2)', conf


def build_game_map(game, gd, moves):
    """moves: move_library entries for this game. Returns (map, gaps)."""
    mmap = {}
    gaps = {'moves_no_p1_in_bank': [], 'p2_conflicts': [],
            'p2_flags': defaultdict(int)}
    for m in moves:
        mid = m['move_id']
        p1 = (m.get('anim_file_id') or '').upper()
        if not p1 or ('0x' + p1.lower()) not in gd.man:
            gaps['moves_no_p1_in_bank'].append(
                {'move_id': mid, 'name': m.get('display_name'),
                 'anim_file_id': p1 or None})
            continue
        entry = {'p1_fid': p1, 'p2_fid': None,
                 'name': m.get('display_name') or '',
                 'source': game,
                 'p2_source': None, 'p2_confidence': None}
        recv = (m.get('recv_anim_file_id') or '').upper() or None
        if recv:
            # role-based recv takes precedence; verify + conflict-check
            if ('0x' + recv.lower()) not in gd.man:
                gaps['p2_flags']['role-recv-missing-from-manifest'] += 1
                recv = None
            else:
                entry['p2_fid'] = recv
                entry['p2_source'] = 'role-based'
                entry['p2_confidence'] = 'role'
                rp2, _, _ = rule_p2(m, gd, p1)
                if rp2 and rp2 != recv:
                    gaps['p2_conflicts'].append(
                        {'move_id': mid, 'name': entry['name'], 'p1': p1,
                         'role_recv': recv, 'rule_p2': rp2})
                    gaps['p2_flags']['role-vs-rule-conflict'] += 1
        if entry['p2_fid'] is None:
            p2, reason, conf = rule_p2(m, gd, p1)
            entry['p2_fid'] = p2
            if p2:
                entry['p2_source'] = 'plus-one-rule'
                entry['p2_confidence'] = conf
                gaps['p2_flags'][f'p2-{conf}'] += 1
            else:
                entry['p2_source'] = None
                entry['p2_reason'] = reason
                kind = m.get('bannon_2k_kind')
                if conf == 'solo' or kind in SOLO_KINDS:
                    entry['p2_flag'] = 'SOLO'
                    gaps['p2_flags']['solo'] += 1
                elif kind in TWO_PERSON_KINDS:
                    entry['p2_flag'] = 'NEEDS-P2'
                    gaps['p2_flags']['needs-p2'] += 1
                else:
                    entry['p2_flag'] = 'P2-UNKNOWN'
                    gaps['p2_flags']['p2-unknown'] += 1
        mmap[mid] = entry
    gaps['p2_flags'] = dict(gaps['p2_flags'])
    return mmap, gaps


def match_nm_library_id(lid, e, gd, h3_assigned=None, h3_direct=None):
    """Match one nm_* library id to a No Mercy P1 fid.

    Returns (fid_or_None, how, p2_or_None, candidates)."""
    n, c = e['n'], e.get('c', '')
    n_stripped = re.sub(r'^No Mercy\s+', '', n)

    # 0. H3 direct unique-pool lookup: (name, category) identifies the
    #    pool outright; the library's category is authoritative.
    if h3_direct is not None:
        for cand_name in (n_stripped, strip_parens(n_stripped)):
            hit = h3_direct.get((norm(cand_name), norm(c)))
            if hit:
                return hit[0], 'label-unique', hit[1], None
        # 0b. H3 numbering table (bare-numbered collisions).
        hit = h3_assigned.get((norm(n_stripped), norm(c)))
        if hit:
            return hit[0], 'h3-numbered', hit[1], None

    def resolve(cands):
        """[(fid, role)] -> (fid, p2, how)."""
        if not cands:
            return None, None, None
        cands = sorted(set(cands))
        roles = {f: r for f, r in cands}
        p1s = [f for f, r in cands if r == 'P1']
        p2s = [f for f, r in cands if r == 'P2']
        if len(p1s) == 1:
            p2 = p2s[0] if len(p2s) == 1 else None
            return p1s[0], p2, 'role-marked'
        if len(cands) == 1:
            return cands[0][0], None, 'single'
        if len(cands) == 2 and int(cands[1][0], 16) == int(cands[0][0], 16) + 1:
            return cands[0][0], cands[1][0], 'consecutive-pair'
        return None, None, 'ambiguous'

    # 1. label (name, cat)
    f, p2, how = resolve(gd.by_nc.get((norm(n), norm(c)), []))
    if f:
        return f, 'label:' + how, p2, None
    # 2. parens stripped from the library name
    n2 = strip_parens(n)
    if n2 != n:
        f, p2, how = resolve(gd.by_nc.get((norm(n2), norm(c)), []))
        if f:
            return f, 'label-noparens:' + how, p2, None
    # 3. library-added trailing number stripped
    base, num = strip_num(n)
    if num is not None:
        f, p2, how = resolve(gd.by_nc.get((norm(base), norm(c)), []))
        if f:
            return f, 'label-stripnum:' + how, p2, None
    # 4. per-wrestler in-game menu name (+ category)
    cands = sorted(gd.pw_by_nc.get((norm(n), norm(c)), []))
    if len(cands) == 1:
        return cands[0], 'per-wrestler:name+cat', None, None
    cands = sorted(gd.pw_by_name.get(norm(n), []))
    if len(cands) == 1:
        return cands[0], 'per-wrestler:name', None, None
    if len(cands) == 2 and int(cands[1], 16) == int(cands[0], 16) + 1:
        return cands[0], 'per-wrestler:consecutive-pair', cands[1], None
    if cands:
        return None, 'ambiguous-per-wrestler', None, cands
    # 5. named-anim-maps name
    nm_hits = [fid for fid, (nm, ctx) in gd.names.items()
               if norm(nm) == norm(n)]
    if len(nm_hits) == 1:
        return nm_hits[0], 'named-anim-map', None, None
    if len(nm_hits) == 2 and int(nm_hits[1], 16) == int(nm_hits[0], 16) + 1:
        return sorted(nm_hits)[0], 'named-anim-map:pair', sorted(nm_hits)[1], None
    if nm_hits:
        return None, 'ambiguous-named-map', None, nm_hits
    return None, 'no-match', None, None


def main():
    ml = json.load(open(f'{FIVE}/output/aki-n64-five/move_library.json'))['moves']
    by_game = defaultdict(list)
    for m in ml:
        by_game[m['source_game']].append(m)
    lib = json.load(open('/home/hatch/workspace/moveset-creator-features/'
                          'app/data/library.json'))['moves']
    nm_lib = {k: v for k, v in lib.items() if k.startswith('nm_')}
    report = {}
    for game in GAMES:
        gd = GameData(game)
        mmap, gaps = build_game_map(game, gd, by_game[game])
        if game == 'nomercy':
            # re-key by library nm_ id where matched
            h3_assigned, h3_direct, h3_moves = build_h3_table(gd)
            # candidate pools for unmatched ids: (base name, cat) -> fids
            h3_cands = defaultdict(list)
            for p1, p2, cat, name in h3_moves:
                b, _ = strip_num(name)
                h3_cands[(norm(b), norm(cat))].append(p1)
            nm_map = {}
            lib_gaps = {'unmatched_library_ids': [], 'ambiguous': []}
            match_how = defaultdict(int)
            used_mids = set()
            # index move_library NM entries by anim fid for reuse
            by_fid = {}
            for mid, e in mmap.items():
                by_fid.setdefault(e['p1_fid'], []).append((mid, e))
            for lid, e in sorted(nm_lib.items()):
                fid, how, p2, cands = match_nm_library_id(
                    lid, e, gd, h3_assigned, h3_direct)
                if fid is None:
                    if cands:
                        lib_gaps['ambiguous'].append(
                            {'library_id': lid, 'name': e['n'],
                             'cat': e.get('c'), 'how': how,
                             'candidates': cands})
                    else:
                        n2 = re.sub(r'^No Mercy\s+', '', e['n'])
                        b2, _ = strip_num(n2)
                        pool_cands = sorted(set(
                            h3_cands.get((norm(b2), norm(e.get('c', ''))),
                                         [])))
                        lib_gaps['unmatched_library_ids'].append(
                            {'library_id': lid, 'name': e['n'],
                             'cat': e.get('c'), 'how': how,
                             'candidate_pools_same_name_cat': pool_cands})
                    match_how['unmatched'] += 1
                    continue
                match_how[how.split(':')[0]] += 1
                # reuse the move_library entry for this fid if one exists
                cands_e = by_fid.get(fid, [])
                base = None
                if cands_e:
                    # prefer the entry whose name best matches
                    for mid, en in cands_e:
                        if names_match(en['name'], e['n']):
                            base = (mid, en)
                            break
                    if base is None:
                        base = cands_e[0]
                if base is not None:
                    mid, en = base
                    used_mids.add(mid)
                    entry = dict(en)
                    entry['name'] = e['n']
                    entry['library_name'] = e['n']
                    entry['move_library_id'] = mid
                    entry['match_how'] = how
                    if p2 and entry['p2_fid'] is None:
                        entry['p2_fid'] = p2
                        entry['p2_source'] = 'label-pair'
                        entry['p2_confidence'] = 'label'
                        entry.pop('p2_flag', None)
                        entry.pop('p2_reason', None)
                    nm_map[lid] = entry
                else:
                    # fid matched but no move_library move uses it:
                    # build a minimal entry from the label data
                    fake = {'display_name': e['n'],
                            'bannon_2k_kind': None, 'unnamed': False}
                    rp2, reason, conf = rule_p2(fake, gd, fid)
                    entry = {'p1_fid': fid,
                             'p2_fid': p2 or rp2,
                             'name': e['n'], 'source': 'nomercy',
                             'p2_source': ('label-pair' if p2 else
                                           ('plus-one-rule' if rp2 else None)),
                             'p2_confidence': ('label' if p2 else conf),
                             'match_how': how,
                             'move_library_id': None}
                    if entry['p2_fid'] is None:
                        entry['p2_reason'] = reason
                        entry['p2_flag'] = 'NEEDS-P2'
                    nm_map[lid] = entry
            # NM moves with no library id keep their move_library id
            for mid, en in mmap.items():
                if mid not in used_mids:
                    en = dict(en)
                    en['move_library_id'] = mid
                    en['match_how'] = 'no-library-id'
                    nm_map[mid] = en
            mmap = nm_map
            gaps['library_match'] = dict(match_how)
            gaps.update(lib_gaps)
        json.dump(mmap, open(os.path.join(OUT, f'{game}-map.json'), 'w'),
                  indent=1)
        json.dump(gaps, open(os.path.join(OUT, f'{game}-gaps.json'), 'w'),
                  indent=1)
        n_p2 = sum(1 for e in mmap.values() if e.get('p2_fid'))
        report[game] = {'moves': len(mmap), 'with_p2': n_p2,
                        'p2_null': len(mmap) - n_p2,
                        'gaps': {k: (len(v) if isinstance(v, list) else v)
                                 for k, v in gaps.items()}}
        print(f'{game}: {len(mmap)} moves, {n_p2} with P2, '
              f'{len(mmap) - n_p2} without; gaps: {report[game]["gaps"]}')
    json.dump(report, open(os.path.join(OUT, 'build-report.json'), 'w'),
              indent=1)
    print('wrote maps to', OUT)


if __name__ == '__main__':
    main()
