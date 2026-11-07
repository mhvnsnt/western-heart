"""Generalized FIGHT-slot mapper for TTT2 joins (Fill 3, stage 3).

Validated against the shipped Roger bank's clip provenance
(work/shipped-slots.json): reproduces 14/15 shipped picks exactly and
gaps t3_light exactly as production did (Roger's join holds only a
cross-character Ak_lp00). Rules encode the roster's naming dialects,
each learned from the joins themselves:

- neutral: sKAM00 move / *_IKI00 move with a 'kamae' anim (Roger/Jun rule).
- attacks: the character's OWN prefix, derived by census over the
  *_lp00/_lk00/_rk00 classes (Marduk=Va, Sebastian=Mn, Steve=Uk -
  their stance records carry no usable prefix). Cross-character
  records never substitute (the Roger Ak_lp00 rule).
- walk: sWALKFLp/sWALK_00FLp (loop variant preferred, production's
  Roger pick) > sWALKF/sWALK_00F > Mv variants; back mirrored.
- dash: sDASHF / own-prefixed *sDASHF (Lw_sDASHF, Pl_sDASHF); plain
  preferred over Lp loop variants (production). backdash: sDASHB /
  *sDASHB / sDASH_00B / sDASH_00BLp.
- crouch: move containing 'st2cr' (Roger/Jun rule). crouch_hold:
  cKAM__00_ or own-prefixed *cKAM00_ (Pl_cKAM00_, Va_cKAM00_).
- jumps: sJUMP_00_/00F/00B or own-prefixed *sJUMP_/*sJUMPF/*sJUMPB
  (Steve: Uk_sJUMP_); rope variants (sJUMPrrp*) excluded.
- hit: sDm_Aokimid00. block: the Zco_PSgu02(DVD) record.
- sidesteps: sSTEP_01L / sSTEP_01R (production picks).
- grab: Thrmv_B1_00 / Thrmv_B2_00i (exact or own-prefixed) in bank 1;
  Tco_ntukami(DVD) anim preferred when several candidates.
- ko / hit_launch: no slot source identified in any join (shipped
  Roger/Jun banks ship neither) - standing gaps, never invented.
Bank-0 picks become gaps: the shipped tooling never wired bank 0.
"""
import re
from collections import Counter

SYSTEM_PREFIXES = {'Co', 'sDm', 'sGrd', 'Tco', 'Bco', 'G', 'SE', 'Esc', 'Fall',
                   'aDw', 'dwDWN', 'dwup', 'sDw', 'wDm', 'cKAM', 'sJUMP', 'sSTEP',
                   'sWALK', 'sDASH', 'Zco', 'Thrmv'}


def prefix_of(name):
    m = re.match(r'^([A-Za-z]+)_', name)
    return m.group(1) if m else None


def pick(rec):
    return {'move': rec['name'], 'anim': rec['anim'], 'bank': rec['bank'],
            'idx': rec['idx'], 'join_i': rec['i']}


def map_slots(join):
    recs = join['records']
    by_name = {}
    for r in recs:
        by_name.setdefault(r['name'], []).append(r)
    slots, gaps = {}, {}

    def put(slot, candidates, why_gap):
        for r in candidates:
            if r['bank'] == 0:
                continue
            slots[slot] = pick(r)
            gaps.pop(slot, None)
            return
        gaps[slot] = why_gap

    # --- neutral (stance) ---
    neu = None
    for pred in (lambda r: 'sKAM00' in r['name'] and 'kamae' in r['anim'],
                 lambda r: r['name'].endswith('_IKI00') and 'kamae' in r['anim'],
                 lambda r: 'kamae' in r['anim'] and ('KAM' in r['name'] or 'IKI' in r['name'])):
        for r in recs:
            if pred(r):
                neu = r
                break
        if neu is not None:
            break
    if neu is not None and neu['bank'] != 0:
        slots['t3_neutral'] = pick(neu)
    else:
        gaps['t3_neutral'] = 'no sKAM00/*_IKI00 kamae-anim record in join'

    # --- own attack prefix by census over the basic-attack classes ---
    cnt = Counter()
    for suf in ('_lp00', '_lk00', '_rk00'):
        for r in recs:
            if r['name'].endswith(suf):
                p = prefix_of(r['name'])
                if p and p not in SYSTEM_PREFIXES:
                    cnt[p] += 1
    own_prefix = None
    if neu is not None:
        np_ = prefix_of(neu['name'])
        if np_ and cnt.get(np_, 0) > 0:
            own_prefix = np_
    if own_prefix is None and cnt:
        own_prefix = cnt.most_common(1)[0][0]

    def atk(slot, suf):
        cands = [r for r in recs if r['name'].endswith(suf)
                 and prefix_of(r['name']) == own_prefix]
        put(slot, cands, 'no own-prefix %s record in join' % suf)

    atk('t3_light', '_lp00')
    atk('t3_medium', '_lk00')
    atk('t3_heavy', '_rk00')

    put('t3_hit', [r for r in recs if r['name'] == 'sDm_Aokimid00'],
        'no sDm_Aokimid00 record in join')
    put('t3_block', [r for r in recs if r['anim'] == 'Zco_PSgu02(DVD)'],
        'no Zco_PSgu02(DVD) record in join')

    def named(slot, names, why):
        cands = []
        for n in names:
            cands += by_name.get(n, [])
        put(slot, cands, why)

    def matching(slot, pred, order, why):
        cands = [r for r in recs if pred(r['name'])]
        cands.sort(key=lambda r: order(r['name']))
        put(slot, cands, why)

    # --- locomotion (dialects: plain, _00 infix, own-prefixed) ---
    matching('t3_walk_fwd',
             lambda n: 'sWALK' in n and 'F' in n.split('sWALK')[1] and not n.rstrip('_').endswith('B'),
             lambda n: (0 if 'Lp' in n else 1 if 'Mv' not in n else 2, len(n)),
             'no sWALK*F record in join')
    matching('t3_walk_back',
             lambda n: 'sWALK' in n and 'B' in n.split('sWALK')[1] and 'F' not in n.split('sWALK')[1],
             lambda n: (0 if 'Mv' not in n else 1, len(n)),
             'no sWALK*B record in join')
    matching('t3_dash_fwd',
             lambda n: n == 'sDASHF' or n.endswith('sDASHF'),
             lambda n: (0 if 'Lp' not in n else 1, len(n)),
             'no sDASHF record in join')
    matching('t3_backdash',
             lambda n: n in ('sDASHB', 'sDASH_00B', 'sDASH_00BLp') or n.endswith('sDASHB'),
             lambda n: (0 if 'Lp' not in n else 1, len(n)),
             'no sDASHB/sDASH_00B record in join')

    # --- crouch ---
    put('t3_crouch', [r for r in recs if 'st2cr' in r['name']],
        'no *st2cr* record in join')
    matching('t3_crouch_hold',
             lambda n: n == 'cKAM__00_' or n.endswith('cKAM00_') or n.endswith('cKAM__00_'),
             lambda n: len(n),
             'no cKAM hold record in join')

    # --- jumps ---
    named('t3_jump_up', ['sJUMP_00_'], 'no sJUMP_00_ record in join')
    if 't3_jump_up' not in slots:
        matching('t3_jump_up',
                 lambda n: n.endswith('sJUMP_') and 'rrp' not in n and 'JUMPr' not in n,
                 lambda n: len(n), 'no *sJUMP_ record in join')
    named('t3_jump_fwd', ['sJUMP_00F'], 'no sJUMP_00F record in join')
    if 't3_jump_fwd' not in slots:
        matching('t3_jump_fwd',
                 lambda n: n.endswith('sJUMPF') and 'rrp' not in n,
                 lambda n: len(n), 'no *sJUMPF record in join')
    named('t3_jump_back', ['sJUMP_00B'], 'no sJUMP_00B record in join')
    if 't3_jump_back' not in slots:
        matching('t3_jump_back',
                 lambda n: n.endswith('sJUMPB') and 'rrp' not in n,
                 lambda n: len(n), 'no *sJUMPB record in join')

    # --- sidesteps ---
    named('t3_sidestep_a', ['sSTEP_01L'], 'no sSTEP_01L record in join')
    named('t3_sidestep_b', ['sSTEP_01R'], 'no sSTEP_01R record in join')

    # --- grab ---
    grabs = [r for r in recs if r['bank'] == 1 and
             (r['name'] in ('Thrmv_B1_00', 'Thrmv_B2_00i') or
              r['name'].endswith('_Thrmv_B1_00') or r['name'].endswith('_Thrmv_B2_00i') or
              (own_prefix and r['name'] in (own_prefix + 'ThrmvB1R0',)))]
    grabs.sort(key=lambda r: (0 if r['anim'] == 'Tco_ntukami(DVD)' else 1,
                              0 if 'B1' in r['name'] else 1))
    put('t3_grab', grabs, 'no Thrmv_B1_00/Thrmv_B2_00i bank-1 record in join')

    # --- standing gaps (no source identified anywhere; shipped banks agree) ---
    gaps['t3_ko'] = ('no slot source identified (shipped Roger/Jun banks '
                     'also ship no t3_ko clip)')
    gaps['t3_hit_launch'] = ('no slot source identified (shipped Roger/Jun '
                             'banks also ship no t3_hit_launch clip)')
    return slots, gaps
