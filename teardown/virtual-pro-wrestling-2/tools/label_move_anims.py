#!/usr/bin/env python3
"""Label the 734 unlabeled VPW2 move animations.

Evidence sources (all in-repo or in the lane workdir):
  - moveset/move_anim_map.json : 4,813 move anims, 734 unlabeled
  - moveset/edit_mode_moves.json (file 0x0061) + raw/0278.bin : P1 anim per menu item
  - raw/0279.bin + moveset/move_damage.json : damage record per mod value
  - moveset/decoded_movesets.json : menu item -> category (85 items, pure 1:1)
  - stage-bannon vpw2-moveset-summary.json : 326 signature moves (P1/P2/Block pattern)

Verified structural facts (see MOVE-ANIM-LABELS.md):
  - Moves come in P1/P2 pairs (note field); P1/P2 share the Toki1 damage window.
  - Block is a SINGLE anim (71/72 labeled cases), note P2, exactly 1 AnimID after
    the base pair; never more than one Block per move.
  - Multi-anim moves: Base, Loop, Finish Normal, Finish Submit/Pinfall/Special,
    Finish Breakup, Reversal -- each a P1/P2 pair, strictly consecutive.
    Base+Loop present => Finish Normal always at base+4,5 (0 exceptions).
  - Combo Strike order: Base, Block, [?(0,0) single], Finish Combo, Push Reversal.
  - File 0x0061 P1s are never components: an anim reachable via 0x0061 is a move
    P1, so it can never be a P2/Block/Finish component.

Output: move_anim_labels.json -- one entry per unlabeled anim with the assigned
move_name / category / note / menu_item where the evidence supports it, plus a
method + confidence tag on every assignment. Unresolvable anims keep empty
names (honestly unlabeled) with the best available category/menu-item context.
"""
import json, struct, collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.environ.get('VPW2_DIR') or os.path.join(
    os.path.expanduser('~/workspace/grok-declined-items/lane-jp-sourcing/vpw2/extracted'))
# Also support the in-repo layout (tools/ -> ../moveset, ../raw)
if not os.path.isdir(VPW2):
    alt = os.path.join(HERE, '..')
    if os.path.isdir(os.path.join(alt, 'moveset')):
        VPW2 = alt


def load_u16(fid):
    data = open(os.path.join(VPW2, 'raw', f'{fid:04X}.bin'), 'rb').read()
    return struct.unpack(f'>{len(data)//2}H', data[:len(data)//2 * 2])


SUFFIXES = [
    ' Knees Up Landing', ' Missed Landing', ' Normal Landing',
    ' Finish Breakup', ' Finish Pinfall', ' Finish Special', ' Finish Mask Rip',
    ' Finish Submit', ' Finish Normal', ' Finish Combo',
    ' Armbar Reversal', ' Ducking Reversal', ' Back Grapple Reversal',
    ' Elbow Reversal', ' Push Reversal', ' Reversal',
    ' Pin Loop', ' Loop', ' Dodge', ' Block',
]


def split_name(n):
    """(base_name, component) -- component '' means the base pair itself."""
    for s in SUFFIXES:
        if n.endswith(s):
            return n[:-len(s)], s.strip()
    return n, ''


# Canonical component order (multi-anim grapple/submission moves).
MULTI_ORDER = ['', 'Loop', 'Pin Loop', 'Finish Normal', 'Finish Submit',
               'Finish Pinfall', 'Finish Special', 'Finish Mask Rip',
               'Finish Breakup', 'Reversal']
FINISH_ALTS = {'Finish Submit', 'Finish Pinfall', 'Finish Special', 'Finish Mask Rip'}


def main():
    mam = json.load(open(os.path.join(VPW2, 'moveset', 'move_anim_map.json')))
    by_anim = {a['anim_id']: a for a in mam['animations'] if a.get('anim_id') is not None}
    unl = sorted(a['anim_id'] for a in mam['animations']
                 if a.get('anim_id') is not None and not a.get('move_name'))

    def toki(a):
        t = a.get('toki1') or {}
        return (t.get('damage_frame_start'), t.get('damage_frame_end'),
                t.get('first_vulnerable_frame'), t.get('reversal_frame'),
                t.get('breakaway_frame'))

    def dmgwin(a):
        t = a.get('toki1') or {}
        return (t.get('damage_frame_start'), t.get('damage_frame_end'))

    # ---- file 0x0061 -> P1 anims + menu items ----
    f278 = load_u16(0x278)
    f279 = load_u16(0x279)
    em = json.load(open(os.path.join(VPW2, 'moveset', 'edit_mode_moves.json')))
    vals = em['values']
    pairs = [(vals[2 * i], vals[2 * i + 1]) for i in range(133)]
    sec2 = vals[266:]
    anim_items = collections.defaultdict(set)
    anim_mod = collections.defaultdict(set)
    item_anims = collections.defaultdict(set)
    for i, (s, c) in enumerate(pairs):
        for mv in sec2[s:s + c]:
            aid = f278[mv]
            if aid == 0:
                continue
            anim_items[aid].add(i)
            anim_mod[aid].add(mv)
            item_anims[i].add(aid)
    dmg = json.load(open(os.path.join(VPW2, 'moveset', 'move_damage.json')))
    recs = dmg['records']

    # ---- menu item -> category (from labeled P1 anims; pure 1:1) ----
    item_cats = {}
    for it, aids in item_anims.items():
        cats = {by_anim[a]['category'] for a in aids if by_anim.get(a, {}).get('category')}
        if len(cats) == 1:
            item_cats[it] = list(cats)[0]

    # ---- base-name families from labeled anims ----
    fams = collections.defaultdict(list)  # (category, base) -> [(anim_id, comp, note, name)]
    for a in mam['animations']:
        n = a.get('move_name')
        if n and a.get('anim_id') is not None:
            base, comp = split_name(n)
            fams[(a.get('category'), base)].append(
                (a['anim_id'], comp, a.get('note'), n))
    for k in fams:
        fams[k].sort()
    fam_range = {k: (min(i for i, _, _, _ in v), max(i for i, _, _, _ in v))
                 for k, v in fams.items()}

    labels = {}  # anim_id -> dict(move_name, category, note, menu_item, method, confidence)

    def assign(aid, name=None, cat=None, note=None, method='', conf='',
               menu_item=None, extra=None):
        d = {'anim_id': aid, 'file_id': by_anim[aid]['file_id'],
             'move_name': name or '', 'category': cat or '',
             'note': note or '', 'menu_item': menu_item,
             'method': method, 'confidence': conf}
        if extra:
            d.update(extra)
        labels[aid] = d

    # ============ Rule A: file-0x0061 P1s (never components) ============
    for u in unl:
        if u in anim_items:
            items = sorted(anim_items[u])
            cats = {item_cats[it] for it in items if it in item_cats}
            ds = [recs[f279[mv]]['damage'] for mv in anim_mod[u]]
            assign(u, None, list(cats)[0] if len(cats) == 1 else None, 'P1',
                   'menu-item-p1', 'certain',
                   menu_item=items[0] if len(items) == 1 else items,
                   extra={'damage': ds,
                          'note_text': 'P1 of an unnamed move (menu item %s)' %
                                       (items if len(items) > 1 else items[0])})

    # ============ Rule B: within-family gaps ============
    for u in unl:
        if u in labels:
            continue
        # find family whose labeled range strictly contains u
        fam = None
        for k, (lo, hi) in fam_range.items():
            if lo < u < hi:
                fam = k
                break
        if fam is None:
            continue
        cat, base = fam
        comps = fams[fam]
        pos = {i: (c, n, nm) for i, c, n, nm in comps}
        prev_ids = [i for i, _, _, _ in comps if i < u]
        next_ids = [i for i, _, _, _ in comps if i > u]
        if not prev_ids or not next_ids:
            continue
        p, nx = max(prev_ids), min(next_ids)
        pc, pn, pnm = pos[p]
        nc, nn, nnm = pos[nx]
        w = dmgwin(by_anim[u])
        # B1: P1 slot -- next anim is a P2 of some component, window matches
        if nn == 'P2' and w == dmgwin(by_anim[nx]) and w != (0, 0):
            assign(u, nnm, cat, 'P1', 'within-family-p1-slot', 'high',
                   extra={'family': base})
            continue
        # B2: missing canonical multi-anim component between two labeled ones
        # gap pair between Finish Normal P2 and Finish Breakup P1 -> Finish Submit
        if (pc == 'Finish Normal' and pn == 'P2' and nc == 'Finish Breakup'
                and nn == 'P1' and nx == u + 2 and (u + 1) in unl
                and (u + 1) not in labels):
            assign(u, base + ' Finish Submit', cat, 'P1',
                   'within-family-finish-submit', 'high', extra={'family': base})
            assign(u + 1, base + ' Finish Submit', cat, 'P2',
                   'within-family-finish-submit', 'high', extra={'family': base})
            continue
        # B3: single Block directly after the base pair
        if (pc == '' and pn == 'P2' and u == p + 1
                and w == dmgwin(by_anim[p]) and w != (0, 0)
                and not any(c == 'Block' for _, c, _, _ in comps)):
            assign(u, base + ' Block', cat, 'P2', 'within-family-block', 'high',
                   extra={'family': base})
            continue
        # B4 is deferred until after the trailing rules (C1-C3) so a precise
        # trailing rule can name a gap anim first; see "Rule B4" below.

    # ============ Rule C1: multi-anim completion (trailing FS/FB) ============
    for (cat, base), comps in sorted(fams.items()):
        sufs = {c for _, c, _, _ in comps}
        if 'Loop' not in sufs and 'Pin Loop' not in sufs:
            continue
        if '' not in sufs:
            continue
        base_ids = sorted(i for i, c, _, _ in comps if c == '')
        if len(base_ids) != 2 or base_ids[1] != base_ids[0] + 1:
            continue
        b0 = base_ids[0]
        pos = {i: c for i, c, _, _ in comps}
        loop = 'Loop' if pos.get(b0 + 2) == 'Loop' else 'Pin Loop'
        if pos.get(b0 + 2) != loop or pos.get(b0 + 3) != loop:
            continue
        if pos.get(b0 + 4) != 'Finish Normal' or pos.get(b0 + 5) != 'Finish Normal':
            continue
        # Finish Submit slot at b0+6,7 (only if the move has no Finish alt there)
        a1, a2 = b0 + 6, b0 + 7
        if (a1 in unl and a2 in unl and a1 not in labels and a2 not in labels
                and pos.get(a1) is None and pos.get(a2) is None):
            # the following pair must be Finish Breakup (labeled) or also unlabeled
            nxt = pos.get(b0 + 8)
            if nxt in (None, 'Finish Breakup'):
                assign(a1, base + ' Finish Submit', cat, 'P1',
                       'multi-anim-completion', 'high', extra={'family': base})
                assign(a2, base + ' Finish Submit', cat, 'P2',
                       'multi-anim-completion', 'high', extra={'family': base})
        # Finish Breakup slot at b0+8,9 (only if Submit is present now)
        a1, a2 = b0 + 8, b0 + 9
        if (a1 in unl and a2 in unl and a1 not in labels and a2 not in labels
                and pos.get(a1) is None and pos.get(a2) is None
                and (labels.get(b0 + 6, {}).get('move_name', '').endswith('Finish Submit')
                     or pos.get(b0 + 6) in FINISH_ALTS)):
            assign(a1, base + ' Finish Breakup', cat, 'P1',
                   'multi-anim-completion', 'high', extra={'family': base})
            assign(a2, base + ' Finish Breakup', cat, 'P2',
                   'multi-anim-completion', 'high', extra={'family': base})
        # NOTE: no Reversal extension -- unbounded, too risky.

    # ============ Rule C2: trailing Push Reversal after Finish Combo ============
    for u in unl:
        if u in labels or (u + 1) not in unl or (u + 1) in labels:
            continue
        prev = by_anim.get(u - 1)
        prev2 = by_anim.get(u - 2)
        if not prev or not prev2 or not prev.get('move_name'):
            continue
        b1, c1 = split_name(prev['move_name'])
        b2, c2 = split_name(prev2['move_name'])
        if b1 != b2 or c1 != 'Finish Combo' or c2 != 'Finish Combo':
            continue
        if prev.get('note') != 'P2':
            continue
        # family must not already have a Push Reversal labeled
        fam = fams.get((prev.get('category'), b1), [])
        if any(c == 'Push Reversal' for _, c, _, _ in fam):
            continue
        w = dmgwin(by_anim[u])
        if w != dmgwin(prev) or w == (0, 0):
            continue
        if dmgwin(by_anim[u + 1]) != w:
            continue
        assign(u, b1 + ' Push Reversal', prev.get('category'), 'P1',
               'trailing-push-reversal', 'medium', extra={'family': b1})
        assign(u + 1, b1 + ' Push Reversal', prev.get('category'), 'P2',
               'trailing-push-reversal', 'medium', extra={'family': b1})

    # ============ Rule C3: trailing single Block after a base pair ============
    for u in unl:
        if u in labels:
            continue
        prev = by_anim.get(u - 1)
        prev2 = by_anim.get(u - 2)
        if not prev or not prev2 or not prev.get('move_name'):
            continue
        b1, c1 = split_name(prev['move_name'])
        b2, c2 = split_name(prev2['move_name'])
        if b1 != b2 or c1 != '' or c2 != '':
            continue
        if prev.get('note') != 'P2' or prev2.get('note') != 'P1':
            continue
        fam = fams.get((prev.get('category'), b1), [])
        if any(c == 'Block' for _, c, _, _ in fam):
            continue
        w = dmgwin(by_anim[u])
        if w != dmgwin(prev) or w == (0, 0):
            continue
        # the next anim must start a different family (or be unlabeled with a
        # different window) -- otherwise u might belong to the next move
        nxt = by_anim.get(u + 1)
        if nxt and nxt.get('move_name'):
            nb, _ = split_name(nxt['move_name'])
            if nb == b1:
                continue
        assign(u, b1 + ' Block', prev.get('category'), 'P2',
               'trailing-block', 'high', extra={'family': b1})

    # ============ Rule B4: small unresolvable within-family gaps ============
    # Category + family only, and ONLY for gaps of <=2 anims between consecutive
    # family members whose window matches the family (or is (0,0)). Families
    # with widely scattered labeled anims (a taunt at 4555 and 4739, a strike
    # at 2430 and 2522) must not swallow the unrelated blocks between them.
    for u in unl:
        if u in labels:
            continue
        fam = None
        for k, (lo, hi) in fam_range.items():
            if lo < u < hi:
                fam = k
                break
        if fam is None:
            continue
        cat, base = fam
        comps = fams[fam]
        pos = {i: (c, n, nm) for i, c, n, nm in comps}
        prev_ids = [i for i, _, _, _ in comps if i < u]
        next_ids = [i for i, _, _, _ in comps if i > u]
        if not prev_ids or not next_ids:
            continue
        p, nx = max(prev_ids), min(next_ids)
        if nx - p - 1 > 2:
            continue  # gap too big to be this family's components
        w = dmgwin(by_anim[u])
        fam_wins = {dmgwin(by_anim[i]) for i, _, _, _ in comps} - {(0, 0)}
        if w != (0, 0) and w not in fam_wins:
            continue  # window belongs to another move; fall through to Rule D
        _, _, pnm = pos[p]
        _, _, nnm = pos[nx]
        assign(u, None, cat, None, 'within-family-gap', 'category-only',
               extra={'family': base,
                      'note_text': 'component of %s (between %s and %s)' % (base, pnm, nnm)})

    # ============ Rule D: category bracketing (effective categories) ============
    # Uses the nearest categorized anim on each side (not just the immediate
    # neighbor), so runs wedged between uncategorized P1s still get bounds.
    def effcat(aid):
        a = by_anim.get(aid)
        if not a:
            return None
        if a.get('category'):
            return a['category']
        if aid in labels and labels[aid]['category']:
            return labels[aid]['category']
        return None

    def nearest_cat(aid, direction, limit=120):
        """Nearest categorized anim id in direction (-1/+1); (anim_id, cat, dist)."""
        i = aid + direction
        while 0 <= i <= 4812 and abs(i - aid) <= limit:
            c = effcat(i)
            if c:
                return i, c, abs(i - aid)
            i += direction
        return None, None, None

    def nearest_p1(aid, direction, limit=120):
        """Nearest menu-item P1 (Rule A) in direction; (anim_id, menu_item)."""
        i = aid + direction
        while 0 <= i <= 4812 and abs(i - aid) <= limit:
            l = labels.get(i)
            if l and l['method'] == 'menu-item-p1':
                return i, l['menu_item']
            i += direction
        return None, None

    remaining = sorted(u for u in unl if u not in labels)
    runs = []
    cur = [remaining[0]] if remaining else []
    for u in remaining[1:]:
        if u == cur[-1] + 1:
            cur.append(u)
        else:
            runs.append(cur)
            cur = [u]
    if cur:
        runs.append(cur)
    for r in runs:
        li, lc, ld = nearest_cat(r[0], -1)
        hi, hc, hd = nearest_cat(r[-1], +1)
        p1l, p1li = nearest_p1(r[0], -1)
        p1r, p1ri = nearest_p1(r[-1], +1)
        p1ctx = ''
        if p1l is not None or p1r is not None:
            p1ctx = ' [nearest menu-item P1s: %s / %s]' % (
                ('anim %d item %s' % (p1l, p1li)) if p1l is not None else '-',
                ('anim %d item %s' % (p1r, p1ri)) if p1r is not None else '-')
        if lc and lc == hc:
            conf = 'medium' if (ld or 99) <= 10 and (hd or 99) <= 10 else 'low'
            for u in r:
                assign(u, None, lc, None, 'category-bracket', conf,
                       extra={'note_text': 'bracketed by %s (anim %s, %d away; '
                              'anim %s, %d away)%s' % (lc, li, ld, hi, hd, p1ctx)})
        elif lc or hc:
            for u in r:
                assign(u, None, None, None, 'category-bracket-ambiguous', 'low',
                       extra={'note_text': 'between %s (anim %s) and %s (anim %s)%s'
                              % (lc, li, hc, hi, p1ctx)})
        else:
            for u in r:
                assign(u, None, None, None, 'unresolved', 'none',
                       extra={'note_text': 'no categorized neighbors within 120 anims%s'
                              % p1ctx})

    # ---- report ----
    out = {
        'source': 'move_anim_map.json (4,813 move anims, 734 unlabeled)',
        'methods': 'see MOVE-ANIM-LABELS.md',
        'counts': {},
        'labels': [labels[u] for u in unl],
    }
    by_method = collections.Counter(labels[u]['method'] for u in unl)
    named = sum(1 for u in unl if labels[u]['move_name'])
    catted = sum(1 for u in unl if labels[u]['category'])
    out['counts'] = {
        'unlabeled_total': len(unl),
        'named': named,
        'categorized': catted,
        'menu_item_known': sum(1 for u in unl if labels[u]['menu_item'] is not None),
        'by_method': dict(by_method),
    }
    with open(os.path.join(HERE, 'move_anim_labels.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out['counts'], indent=1))
    print(f"\nnamed examples:")
    for u in unl:
        if labels[u]['move_name']:
            print(f"  {u}: {labels[u]['move_name']} [{labels[u]['category']}] "
                  f"({labels[u]['method']}, {labels[u]['confidence']})")
            if sum(1 for v in unl[:unl.index(u) + 1] if labels[v]['move_name']) >= 15:
                break


if __name__ == '__main__':
    main()
