#!/usr/bin/env python3
"""Build game/data/menajerii_source_frame_table.json: MENAJERII's source kit (Roger Jr.,
Tekken Tag Tournament 2) as exact move + frame data, joined to her moveset, animation PENDING.

Owner instruction (2026-11-03): "get the roger moves from whatever game he's in and from the
modding community". This is the move/frame half of that job. No motion is produced here and no
other character's clips are bound: every row says `animation: "pending"` until a real Roger Jr.
motion bank exists (see docs/anim/ROGER-JR-SOURCES-2026-11-03.md).

Inputs (all already in the repo, nothing fetched at build time):
  docs/t7t8-reference/frame-data-ttt2/roger_jr.wavu.json      wavu.wiki TTT2 movelist, CC0-1.0  (PRIMARY)
  docs/t7t8-reference/frame-data-ttt2/roger_jr.rbnorway.json  RBNorway TTT2 frames via harounb, MIT (cross-check)
  docs/t7t8-reference/frame-data-t5/roger_jr.wavu.json        wavu.wiki Tekken 5/DR movelist, CC0-1.0 (lineage)
  teardown/tekken6/movesets/t6psp-roger-moveset-v3.json       our own T6 PSP COM decode (command list, no frames)
  game/assets/ttt2/movesets/rog.json                          our own TTT2 MVLT decode (in-game move list rows)
  game/assets/movesets/menajerii.json                         her current moveset (read only, never written)

Refresh the wavu inputs with tools/frame-data/wavu_movelist_wikitext.py, then re-run this script.

Row shape: the wh-frame-row/1 fields (command, hit_level, damage, startup, on_block, on_hit,
on_ch, tags, transitions) that game/js/frame-data-schema.js validates, written only where the
source value parses exactly; the verbatim source strings always ride in `source_values`.
Normalisations (documented, deterministic, nothing invented):
  * startup: a parenthetical input-buffer note is dropped ("i15(16~)" -> "i15"); if the rest
    still does not parse (e.g. "i28~29,i33~34"), `startup` is left out and the raw value kept.
  * on_hit / on_ch: "JG" (juggle) and other states that are not frame counts are left out of
    the wh fields (the schema only accepts numbers / KND / STUN) and kept raw.
  * damage: the per-hit list of the whole string (parent chain joined).
Join to menajerii.json is by normalised notation (d/f = df, ROS x = ROC.x = b+1+2,x,
BOB x = b+3+4,x, WS+1 = ws1, FC,d/f+2 = FC.df+2, RN/WR x, qcf+1 = d,df,f+1,
f,hcf+1 = f,b,db,d,df,f+1, f,F = f,f, Left/Right/Back Throw = 1+3~L / 2+4~R / BT 1+3).
`menajerii.status`:
  same_move          her move at that input is this move (same name, or same notation with no
                     conflicting name)
  input_conflict     her move at that input is a different move (e.g. a bear-themed move sitting
                     on a Roger input) - reported, NOT changed
  absent             no move at that input in her file
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
OUT = P('game/data/menajerii_source_frame_table.json')


def load(rel, optional=False):
    path = P(rel)
    if optional and not os.path.exists(path):
        return None
    return json.load(open(path, encoding='utf-8'))


DIAG = [('d/f', 'df'), ('d/b', 'db'), ('u/f', 'uf'), ('u/b', 'ub'), ('D/F', 'DF'), ('D/B', 'DB'), ('U/F', 'UF'), ('U/B', 'UB')]
MOTION = {'qcf': 'd,df,f', 'qcb': 'd,db,b', 'hcf': 'b,db,d,df,f', 'hcb': 'f,df,d,db,b'}
THROW_ALIAS = {'left throw': '1+3~l', 'right throw': '2+4~r', 'back throw': 'bt1+3'}


def norm(s):
    """Canonical notation key for matching across the three notations in play."""
    if s is None:
        return None
    s = s.strip()
    low = s.lower()
    if low in THROW_ALIAS:
        return THROW_ALIAS[low]
    for a, b in DIAG:
        s = s.replace(a, b)
    s = re.sub(r'\s*\((close|far)\)\s*', '', s, flags=re.I)
    s = s.lower().replace(' ', '')
    s = s.replace('~hold', '*').replace('#', '*')
    # stance prefixes
    s = re.sub(r'^(ros|roc)[.+]?', 'b+1+2,', s)
    s = re.sub(r'^bob[.+]?', 'b+3+4,', s)
    s = re.sub(r'^ws[.+]?', 'ws', s)
    s = re.sub(r'^fc[.,+]?', 'fc', s)
    s = re.sub(r'^ss[.+]?', 'ss', s)
    s = re.sub(r'^bt[.+]?', 'bt', s)
    s = re.sub(r'^(wr|rn)[.+]?', 'wr', s)
    s = s.replace(',,', ',')
    for k, v in MOTION.items():
        s = re.sub(r'(^|,)' + k + r'(?=\+)', lambda m: m.group(1) + v, s)
    return s


def name_key(n):
    # spelling variants between the three sources (wavu typos "Bycicle", "Doormant"; Bobbing/Bobbin)
    return re.sub(r'[^a-z0-9]', '', (n or '').lower().replace('bycicle', 'bicycle').replace('doormant', 'doormat')
                  .replace('bobbing', 'bobbin').replace('charged', 'charge').replace('kicks', 'kick'))


def clean_startup(v):
    if not v:
        return None
    s = re.sub(r'\([^)]*\)', '', v).replace(' ', '')
    return s or None


def startup_ok(s):
    # mirror game/js/frame-data-schema.js parseStartup
    if s is None:
        return False
    parts = [p.strip().lstrip('i') for p in s.lower().lstrip('i').split(',') if p.strip()]
    return bool(parts) and all(re.fullmatch(r'\d+(~\d+)?', p) for p in parts)


def adv_ok(v):
    if v is None or v == '':
        return False
    return bool(re.search(r'[+-]?\d+', v)) or v.strip().upper() in ('KND', 'STUN', '?')


def dmg_ok(v):
    return bool(v) and all(re.fullmatch(r'-?\d+', p.strip()) for p in v.split(','))


def wh_hit_level(t):
    # wavu: h m l L(grounded low) M SM sm t sp ! ; keep tokens the schema knows, verbatim string
    return t or None


def main():
    wavu = load('docs/t7t8-reference/frame-data-ttt2/roger_jr.wavu.json')
    rbn = load('docs/t7t8-reference/frame-data-ttt2/roger_jr.rbnorway.json')
    t5 = load('docs/t7t8-reference/frame-data-t5/roger_jr.wavu.json')
    t6 = load('teardown/tekken6/movesets/t6psp-roger-moveset-v3.json', optional=True)
    rog = load('game/assets/ttt2/movesets/rog.json')
    men = load('game/assets/movesets/menajerii.json')

    # --- menajerii index: normalised notation -> [key]
    men_idx = {}
    for k, v in men['moves'].items():
        for cand in {k, v.get('input'), *(v.get('input_slots') or [])}:
            n = norm(cand)
            if n:
                men_idx.setdefault(n, [])
                if k not in men_idx[n]:
                    men_idx[n].append(k)

    # --- cross-check indexes
    rbn_idx = {}
    for part in ('basic', 'normal'):
        for m in rbn[part]['moves']:
            for alt in re.split(r'\s+or\s+', m['notation']):
                rbn_idx.setdefault(norm(alt), m)
    t5_idx = {}
    for m in t5['moves']:
        t5_idx.setdefault(norm(m['input_full']), m)
    rog_idx = {}
    for r in rog['records']:
        if r.get('kind') != 'move':
            continue
        for alt in re.split(r'\s+or\s+', r.get('notation_std') or ''):
            rog_idx.setdefault(norm(alt), r)
    t6_names = set()
    if t6:
        t6_names = {name_key(m['name']) for m in t6['moves']}

    rows, used_keys = [], set()
    for m in wavu['moves']:
        cmd = m['input_full']
        n = norm(cmd)
        alts = [a.strip() for a in (m.get('alt') or '').split(';') if a.strip()]
        keys = list(men_idx.get(n, []))
        for a in alts:
            for k in men_idx.get(norm(a), []):
                if k not in keys:
                    keys.append(k)
        src_name = m.get('name') or ''
        # pick menajerii entry. Provenance first: her file stamps every move with tekken_base /
        # merge_source / anim_ref, so a Kuma-sourced move on a Roger input is a conflict even when
        # unnamed, and a Roger-sourced move is the same move even when its WH-side name differs
        # (e.g. "Rolling Torpedo" carries anim_ref ttt2:rog:row:56 = MVLT "Rolling Toe Drop").
        status, mk = 'absent', None
        if keys:
            def origin(k):
                mn = men['moves'][k]
                base = (mn.get('tekken_base') or '').lower()
                ref = str(mn.get('anim_ref') or '')
                if 'kuma' in base or ref.startswith('t3:kuma'):
                    return 'kuma'
                if 'roger' in base or ref.startswith('ttt2:rog') or mn.get('merge_source') == 'ttt2:roger':
                    return 'roger'
                if ref.startswith('wh:'):
                    return 'canon'
                return 'other'
            same = [k for k in keys if src_name and name_key(men['moves'][k].get('name')) == name_key(src_name)]
            roger = [k for k in keys if origin(k) == 'roger']
            if same and origin(same[0]) != 'kuma':
                status, mk = 'same_move', same[0]
            elif roger:
                status, mk = 'same_move', roger[0]
            else:
                status, mk = 'input_conflict', keys[0]
        if mk:
            used_keys.add(mk)
        startup = clean_startup(m.get('startup'))
        wh = {'command': cmd}
        tgt = m.get('target_full')
        if tgt:
            wh['hit_level'] = wh_hit_level(tgt)
        if dmg_ok(m.get('damage_full')):
            wh['damage'] = m['damage_full']
        if startup_ok(startup):
            wh['startup'] = startup
        for f_src, f_wh in (('block', 'on_block'), ('hit', 'on_hit'), ('ch', 'on_ch')):
            v = m.get(f_src)
            if adv_ok(v):
                wh[f_wh] = v
        tags = []
        crush = (m.get('crush') or '').strip()
        if crush:
            tags.append(crush)  # 'js' / 'cs' (no frame window given by the source)
        if re.search(r'\bHoming\b', m.get('notes') or ''):
            tags.append('hb')
        wh['tags'] = ' '.join(tags)
        recv = (m.get('recv') or '').strip()
        wh['transitions'] = [recv] if recv else []
        row = {
            **wh,
            'name': src_name or None,
            'source_id': m['id'],
            'source_values': {k: m.get(k) for k in ('input', 'alt', 'target', 'damage', 'startup', 'block', 'hit', 'ch',
                                                       'crush', 'recv', 'notes') if m.get(k)},
            'cross_check': {},
            'menajerii': {'status': status, 'key': mk},
            'animation': 'pending',
        }
        if mk:
            cur = men['moves'][mk]
            row['menajerii']['current'] = {'name': cur.get('name'), 'damage': cur.get('damage'), 'startup_s': cur.get('startup'),
                                           'hit_range': cur.get('hit_range'), 'tekken_base': cur.get('tekken_base'),
                                           'anim_ref': cur.get('anim_ref')}
        r = rbn_idx.get(n)
        if r:
            row['cross_check']['rbnorway_ttt2'] = {'notation': r['notation'], 'damage': r['damage'], 'speed': r['speed'],
                                                   'on_block': r['on_block'], 'on_hit': r['on_hit'], 'on_ch': r['on_ch']}
        t = t5_idx.get(n)
        if t:
            row['cross_check']['wavu_t5'] = {'id': t['id'], 'damage': t.get('damage_full'), 'startup': t.get('startup'),
                                             'block': t.get('block'), 'hit': t.get('hit')}
        g = rog_idx.get(n)
        if g:
            row['cross_check']['ttt2_mvlt'] = {'row': g['row'], 'name': g['name'], 'anim_ref': g.get('anim_ref')}
        if t6 and src_name:
            row['cross_check']['t6psp_com_name_present'] = name_key(src_name) in t6_names
        rows.append(row)

    # menajerii moves not covered by any source row
    uncovered = []
    for k, v in men['moves'].items():
        if k in used_keys:
            continue
        uncovered.append({'key': k, 'name': v.get('name'), 'tekken_base': v.get('tekken_base'), 'merge_source': v.get('merge_source'),
                          'anim_ref': v.get('anim_ref')})

    counts = {
        'source_rows': len(rows),
        'same_move': sum(r['menajerii']['status'] == 'same_move' for r in rows),
        'input_conflict': sum(r['menajerii']['status'] == 'input_conflict' for r in rows),
        'absent': sum(r['menajerii']['status'] == 'absent' for r in rows),
        'rows_with_startup': sum('startup' in r for r in rows),
        'rows_with_block': sum('on_block' in r for r in rows),
        'rbnorway_cross_checked': sum('rbnorway_ttt2' in r['cross_check'] for r in rows),
        'ttt2_mvlt_cross_checked': sum('ttt2_mvlt' in r['cross_check'] for r in rows),
        'menajerii_moves_total': len(men['moves']),
        'menajerii_moves_not_in_source': len(uncovered),
        'menajerii_moves_kuma_sourced': sum('kuma' in (v.get('tekken_base') or '').lower() or str(v.get('anim_ref') or '').startswith('t3:kuma')
                                            for v in men['moves'].values()),
        'conflicts_with_kuma_sourced_move': sum(r['menajerii']['status'] == 'input_conflict' and 'kuma' in
                                                ((r['menajerii'].get('current') or {}).get('tekken_base') or '').lower() for r in rows),
    }
    doc = {
        'schema': 'wh-frame-row/1',
        'fps': 60,
        'fighter': 'menajerii',
        'purpose': 'Exact source move list + frame data for this fighter\'s kit. Data table only: nothing here is shown to the '
                   'player and the moveset file is not modified. Applying these numbers to the moveset is a follow-up '
                   '(damage-source decision owed, docs/movesets/ROGER-BANK-AUDIT-2026-11-02.md).',
        'animation': 'pending - no source motion bank exists yet; no other character\'s clips are bound by this table',
        'provenance': {
            'primary': {'name': 'wavu.wiki TTT2 movelist', 'url': wavu['source'], 'permalink': wavu['permalink'],
                        'revid': wavu['revid'], 'license': wavu['license'], 'file': 'docs/t7t8-reference/frame-data-ttt2/roger_jr.wavu.json'},
            'cross_check': [
                {'name': 'RBNorway TTT2 frame data via harounb/tekken-frame-data', 'url': rbn['source'], 'license': rbn['license'],
                 'file': 'docs/t7t8-reference/frame-data-ttt2/roger_jr.rbnorway.json'},
                {'name': 'wavu.wiki Tekken 5/DR movelist (lineage)', 'url': t5['source'], 'permalink': t5['permalink'],
                 'license': t5['license'], 'file': 'docs/t7t8-reference/frame-data-t5/roger_jr.wavu.json'},
                {'name': 'in-repo TTT2 MVLT decode (in-game move list)', 'file': 'game/assets/ttt2/movesets/rog.json'},
                {'name': 'in-repo Tekken 6 PSP COM decode (command list)', 'file': 'teardown/tekken6/movesets/t6psp-roger-moveset-v3.json',
                 'present': bool(t6)},
            ],
            'generator': 'tools/frame-data/build_menajerii_source_table.py',
        },
        'counts': counts,
        'rows': rows,
        'menajerii_moves_not_in_source': uncovered,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    print(os.path.relpath(OUT, ROOT), json.dumps(counts))


if __name__ == '__main__':
    sys.exit(main())
