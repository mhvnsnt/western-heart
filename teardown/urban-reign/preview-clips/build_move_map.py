#!/usr/bin/env python3
"""Build ur_move_map.json: all 1,151 UR moves -> motion data + P1/P2 roles.

Sources (all local, read-only):
  * bannon-upgrade/assets/moves/urban-reign-named-moves.json (1,151 moves:
    fighter, pmot bank, clip, ur_name or null, frames)
  * wrestling-full-pull/.../urban-reign/motion-names/name-bridge-*-proven.json
    (proven cross-bank twins: a fighter's move == a general-bank motion,
    proven by root-stream match, maxDev ~0.01 mm)
  * .../anim-banks/*/clips.json (general-bank motion frame counts, for
    the frame-count cross-check on every twin link)
  * docs/BANK-COMPLETION.md (the 5 no-bank P1 records)

A move is CONVERTIBLE now iff its (fighter, name) has a proven general-bank
twin with a matching frame count. Everything else is pmot-only: the motion
data lives in the per-fighter .ppk banks, whose range-coded tracks need the
ELF tables (SLUS_212.09) — not available locally. The 5 no-bank records
have no source bank in the shipped disc at all (emulator capture only).

Roles: _f suffix = P1 (attacker half), _y suffix = P2 (receiver half);
partner = same fighter, same base name, complementary suffix. _z/_b and
other suffixes are recorded as data, not interpreted. Unnamed moves keep
ur_name null — never guessed.
"""
import glob
import json
from collections import Counter, defaultdict

BASE = '/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign'
NAMED = '/home/hatch/workspace/bannon-upgrade/assets/moves/urban-reign-named-moves.json'

NO_BANK_NAMES = {'cbco_screw_r', 'moco_d_jumpk_f', 'moco_d_jumpk_y1',
                 'moco_d_jumpk_y2', 'moco_doubleairk_f'}

GENERAL_DIRS = {'general_normal': 'ur-general-normal',
                'general_30frame': 'ur-general-30frame',
                'general_weapon': 'ur-general-weapon'}


def load_general_frames():
    frames = {}
    for short, d in GENERAL_DIRS.items():
        cl = json.load(open(f'{BASE}/anim-banks/{d}/clips.json'))['clips']
        for m in cl:
            frames[(short, m['motion'])] = m['frames']
    return frames


def load_twins():
    """Two link sets, both proven by root-stream match (maxDev ~0.01 mm):

    pmot_links: (pmot bank, motion) -> general (bank, motion). A pmot clip
    is convertible iff it is PROVEN identical to a general motion. Proven
    two ways: a provenPair's alsoIn (own-bank motion == general motion),
    or an unproven record's cross-bank hit set containing BOTH that pmot
    motion and a general motion with the same root stream.
    NOTE: name matching alone is NOT proof — the bridge explicitly tested
    same-name pairs and most failed the root gate (different motion, same
    name), e.g. char001 cbco_wp2h_kokyu01: own-bank m001 fails (652 mm),
    general_weapon m033 matches (0.0014 mm).

    moveset_links: (fighter, motdat record name) -> general (bank, motion).
    The move the fighter PERFORMS using the general pool (its own-bank clip
    for that name, if any, is a different motion). This is the moveset
    coverage story, separate from pmot-clip coverage.
    """
    pmot_links = {}
    moveset_links = defaultdict(list)
    banks = json.load(open(f'{BASE}/brutal-fist/ur-banks.json'))
    f2b = {f: v['bank'].replace('.ppk', '')
           for f, v in banks.items()}
    for f in sorted(glob.glob(f'{BASE}/motion-names/name-bridge-*-proven.json')):
        d = json.load(open(f))
        fighter = d['fighter']
        own_bank = f2b.get(fighter)
        for p in d.get('provenPairs', []):
            if 'alsoIn' in p:
                a = p['alsoIn']
                if a['bank'].startswith('general_') and own_bank:
                    pmot_links[(own_bank, p['bankMotion'])] = (
                        a['bank'], a['motion'], a.get('clip'),
                        p.get('maxDev'))
        for r in d.get('unprovenRecords', []):
            hits = r.get('crossBankHits', [])
            pmots = [(h['bank'], h['bankMotion'], h.get('maxDev'))
                     for h in hits if h['bank'].startswith('pmot')]
            gens = [(h['bank'], h['bankMotion'], h.get('clip'),
                     h.get('maxDev'))
                    for h in hits if h['bank'].startswith('general_')]
            for g in gens:
                moveset_links[(fighter, r['name'])].append(g)
            for pb, pm, _ in pmots:
                for g in gens:
                    pmot_links.setdefault((pb, pm), g)
    return pmot_links, moveset_links


def main():
    moves = json.load(open(NAMED))['moves']
    gen_frames = load_general_frames()
    pmot_links, moveset_links = load_twins()
    print(f'pmot->general links: {len(pmot_links)}; '
          f'moveset->general links: {len(moveset_links)}')

    # (fighter, name) uniqueness check for the join
    seen = Counter((m['fighter'], m['ur_name']) for m in moves
                   if m['ur_name'])
    dupes = {k: v for k, v in seen.items() if v > 1}
    print(f'(fighter, name) duplicates: {len(dupes)} {list(dupes)[:5]}')

    # partner index: (fighter, base name) -> suffixes present
    by_base = defaultdict(dict)
    for m in moves:
        n = m['ur_name']
        if n and (n.endswith('_f') or n.endswith('_y')):
            by_base[(m['fighter'], n[:-2])][n[-1]] = m['clip']

    out_moves = []
    stats = Counter()
    frame_mismatch = []
    for m in moves:
        n = m['ur_name']
        fighter = m['fighter']
        role = 'solo'
        partner = None
        if n:
            if n.endswith('_f'):
                role = 'P1'
                partner = by_base.get((fighter, n[:-2]), {}).get('y')
            elif n.endswith('_y'):
                role = 'P2'
                partner = by_base.get((fighter, n[:-2]), {}).get('f')
        category = n.split('_')[0] if n else 'unnamed'
        entry = {'fighter': fighter, 'bank': m['bank'], 'clip': m['clip'],
                 'ur_name': n, 'frames': m['frames'],
                 'duration_s': m['duration_s'], 'role': role,
                 'partner_clip': partner, 'category': category,
                 'convertible': False, 'general_clip': None,
                 'gap_reason': None}
        bank_short = m['bank'].replace('.ppk', '')
        motion_idx = int(m['clip'].split('_m')[1])
        link = pmot_links.get((bank_short, motion_idx))
        if n in NO_BANK_NAMES:
            entry['gap_reason'] = ('no-bank: source bank not in the shipped '
                                   'disc (emulator capture only)')
        elif link:
            bank, motion, clip, maxdev = link
            gf = gen_frames.get((bank, motion))
            if gf == m['frames']:
                entry['convertible'] = True
                entry['general_clip'] = {
                    'bank': GENERAL_DIRS[bank], 'motion': motion,
                    'clip': clip or f'ur_m{motion:03d}',
                    'maxDev_mm': maxdev,
                    'preview_file': f"ur_{bank}_{clip or f'ur_m{motion:03d}'}.json"}
            else:
                frame_mismatch.append((fighter, n, link, m['frames']))
                entry['gap_reason'] = ('twin frame-count mismatch '
                                       f'(pmot {m["frames"]}f vs general '
                                       f'{gf}f)')
        elif n:
            entry['gap_reason'] = ('pmot-only: motion data in the '
                                   'per-fighter .ppk bank; needs ELF '
                                   'range-decoder tables')
        else:
            entry['gap_reason'] = ('unnamed pmot clip: no name and no '
                                   'general-bank twin; needs ELF tables')
        # moveset coverage: does this fighter PERFORM this named move from
        # the general pool (separate from the pmot clip itself)?
        if n and (fighter, n) in moveset_links:
            g = moveset_links[(fighter, n)][0]
            entry['moveset_general'] = {
                'bank': GENERAL_DIRS[g[0]], 'motion': g[1],
                'clip': g[2] or f"ur_m{g[1]:03d}",
                'preview_file': f"ur_{g[0]}_{g[2] or f'ur_m{g[1]:03d}'}.json"}
        out_moves.append(entry)
        stats['total'] += 1
        stats['named' if n else 'unnamed'] += 1
        stats[f"role_{role}"] += 1
        stats['convertible' if entry['convertible'] else 'blocked'] += 1
        stats[f"cat_{category}"] += 1
        if 'moveset_general' in entry:
            stats['moveset_general'] += 1
        if entry['gap_reason']:
            stats['gap_' + entry['gap_reason'].split(':')[0]] += 1

    # per-general-motion coverage: which general clips serve how many moves
    cover = Counter(e['general_clip']['preview_file'] for e in out_moves
                    if e['general_clip'])
    ms_cover = Counter(e['moveset_general']['preview_file']
                       for e in out_moves if 'moveset_general' in e)
    summary = {
        'total_moves': stats['total'],
        'named': stats['named'],
        'unnamed': stats['unnamed'],
        'convertible_now': stats['convertible'],
        'blocked': stats['blocked'],
        'moveset_performable_from_general': stats['moveset_general'],
        'moveset_general_motions_used': len(ms_cover),
        'roles': {k[5:]: v for k, v in stats.items()
                  if k.startswith('role_')},
        'categories': {k[4:]: v for k, v in stats.items()
                       if k.startswith('cat_')},
        'gaps': {k[4:]: v for k, v in stats.items()
                 if k.startswith('gap_')},
        'general_motions_covering_moves': len(cover),
        'general_coverage': dict(sorted(cover.items())),
        'moveset_general_coverage': dict(sorted(ms_cover.items())),
        'frame_mismatches': frame_mismatch,
        'fighter_name_duplicates': {f'{k[0]}:{k[1]}': v
                                    for k, v in dupes.items()},
        'notes': [
            'Convertible = pmot clip PROVEN identical to a general-bank '
            'motion (root-stream match, maxDev ~0.01 mm) with matching '
            'frame count. Name matching alone is NOT proof: the bridge '
            'tested same-name pairs and most failed the root gate.',
            'moveset_performable_from_general: named moves the fighter '
            'PERFORMS from the general pool (its own-bank clip for that '
            'name is a different motion). Separate from pmot-clip '
            'coverage.',
            'The 5 no-bank names (cbco_screw_r, moco_d_jumpk_f/_y1/_y2, '
            'moco_doubleairk_f) have no source bank in the shipped disc '
            '(BANK-COMPLETION.md); only a PCSX2 runtime capture could '
            'source them. None of the 1,151 pmot clips carries these '
            'names — they are moveset-level gaps (motdat records with no '
            'clip in any bank).',
            '2 of the 5 convertible pmot clips are UNNAMED in their bank '
            '(char005 ur_m022/ur_m023) — the motion identity was proven '
            'by root stream, not by name. Their general twins are named '
            'moco_golemnage1_f/_y, but the pmot clips themselves keep '
            'ur_name null (never guessed).',
            '41 proxy-only fighters (no native animation) are not in the '
            '1,151 (those are the 31 fighters with pmot banks); they can '
            'only use general-pool motions.',
            '_f = P1 attacker half, _y = P2 receiver half (fighting-game '
            'convention; suffix semantics not confirmed in teardown docs).',
            'D3 (which UR moves enter the library) and D5 (verbatim vs '
            'Bannon-rename) are Mars calls — not decided here.',
        ],
    }
    # Moveset coverage (separate universe from the 1,151 pmot clips): the
    # (fighter, motdat record) pairs whose motion is a general-bank motion.
    # These moves have no pmot clip of their own — the fighter performs
    # them from the shared pool. 67 entries.
    ms_list = []
    for (fighter, name), cands in sorted(moveset_links.items()):
        g = cands[0]
        ms_list.append({'fighter': fighter, 'ur_name': name,
                        'general_bank': GENERAL_DIRS[g[0]],
                        'general_motion': g[1],
                        'general_clip': g[2] or f"ur_m{g[1]:03d}",
                        'preview_file': f"ur_{g[0]}_{g[2] or f'ur_m{g[1]:03d}'}.json",
                        'maxDev_mm': g[3]})
    out = {'summary': summary, 'moves': out_moves,
           'moveset_coverage': ms_list}
    path = '/home/hatch/workspace/preview-clips/urban-reign/ur_move_map.json'
    json.dump(out, path and open(path, 'w'), indent=1)
    print(json.dumps(summary, indent=1)[:3000])
    print(f'wrote {path} ({len(out_moves)} moves)')


if __name__ == '__main__':
    main()
