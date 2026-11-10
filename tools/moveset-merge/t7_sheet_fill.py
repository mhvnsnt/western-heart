#!/usr/bin/env python3
"""tools/moveset-merge/t7_sheet_fill.py: put a fighter's own T7 frame-sheet rows back on the inputs that
Tekken 3 stand-in rows were holding.

Why (2026-11-10, Thor): Thor's canon base is Ganryu ("Ganryu is Thor, the literal norse god of lightning"; "Built
on Ganryu's sumo frame"). Ganryu is not in Tekken 3, so the T3 bank pass gave Thor Bryan's T3 rows as
stand-ins ('THOR 1 (T3 bryan r49)'). The 2026-10-20 T7 import (FULL MOVESET LAW cluster B, Ganryu via the rbnorway
sheet) kept existing moves verbatim and DEDUPED BY INPUT. So 6 of Ganryu's 139 sheet rows never entered the file:
1, 2, 2,1, 2,1,2, 3 and d/f+2. Those inputs still fire Bryan's T3 rows. The owner's rule on Gyou applies the same
way here ("gyou has someone else's moves" / "so many things mixed like that").

For every sheet row the file lacks (matched on t7_command):
  * the input key is free             -> the T7 row is added under it;
  * the key is held by a STAND-IN row -> the stand-in moves to '<key>~t3proxy' (kept, with its own hit word; it keeps
    its input, so the game's 'notation' animation fallback still finds its T3 clip) and the T7 row takes the key;
  * the key is held by anything else  -> left alone and reported. That covers the base character's own rows,
    signatures and canon rows.
A stand-in row has t3_source == --proxy-source and no T7/T8/merge source.
--split-or also makes an existing T7 row whose sheet command lists alternatives ('4 or f+4': the same move on 4 and
on f+4) reachable on each alternative under the same rule (only plain single inputs: '4', 'f+4').

The WH fields of a new row follow the file's OWN T7 rows. The rule is read off the 2026-10-20 import and is checked
here against every existing T7 row of the same class before anything is written; any disagreement aborts:
startup = first frame / 60 (0.3 s when the sheet has none); damage = sum of the hits; weight class by damage (0: active 0.3, recovery 0.3, knock 0,
light; <= 14: recovery 0.45, knock 2.2, light; <= 24: 0.55 / 4.2 / heavy; else 0.7 / 5.0 / heavy; active 2 frames
when damage > 0); soulGain = round(damage / 2) clamped to 3..15; limb = the last hit's last button (1 armL, 2 armR,
3 legL, 4 legR; 'both' when it has none); move_class string when the command has a comma, else strike (multi_hit on
those strings when the damage lists several hits); input_slots = the string's prefixes;
anim_ref t7:<base>:<command slug>; the import's own note format. Hit words: merge_sources.annotate's rule for a row
with no T3 row (word_from_label of the T7 hit level). The name is '<DISPLAY> <command>' (no source names in
player-facing text). The old file is archived byte for byte first.

    python3 tools/moveset-merge/t7_sheet_fill.py --moveset game/assets/movesets/thor.json \\
        --sheet game/data/t7-frame-data/t7-ganryu-lp-rp-lk-rk.json --base ganryu --display THOR \\
        --proxy-source bryan --split-or --archive docs/archive/movesets/thor-pre-t7-fill-2026-11-10.json \\
        --out game/assets/movesets/thor.json
"""
import argparse
import copy
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_sources import word_from_label  # noqa: E402  (the same hit-word rule the merge's annotate() uses)

LIMB = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}
NOTE_TAIL = 'rbnorway sheet carries no move names; labeled by T7 command'


def first_int(s):
    m = re.search(r'-?\d+', str(s if s is not None else ''))
    return int(m.group(0)) if m else None


def hits_of(damage):
    return [first_int(x) for x in str(damage or '').split(',') if first_int(x) is not None]


def weight(total):
    if total <= 0:
        return dict(active=0.3, recovery=0.3, knock=0.0, heavy=False)
    if total <= 14:
        return dict(active=0.033, recovery=0.45, knock=2.2, heavy=False)
    if total <= 24:
        return dict(active=0.033, recovery=0.55, knock=4.2, heavy=True)
    return dict(active=0.033, recovery=0.7, knock=5.0, heavy=True)


def key_of(cmd):
    return re.sub(r'\s*,\s*', ',', str(cmd).strip())


def derive(cmd, sheet, base, display, key=None):
    """WH fields for one sheet row, by the file's own T7 import rule."""
    key = key or key_of(cmd)
    hits = hits_of(sheet['damage'])
    total = sum(hits)
    last = ([x for x in key.split(',') if x.strip()] or [''])[-1]  # '3,4,3,4,,': the last hit that has buttons
    digits = re.findall(r'[1-4]', last)
    parts = key.split(',')
    note = 'T7 [%s] startup %s | block %s | hit %s | CH %s' % (sheet['hit_level'], sheet['speed'], sheet['on_block'],
                                                             sheet['on_hit'], sheet['on_ch'])
    if sheet.get('notes'):
        note += ' | ' + str(sheet['notes'])
    row = {
        'name': '%s %s' % (display, cmd),
        'input': key,
        't7_source': None,  # filled by the caller (the file's own t7_dataset label)
        't7_command': cmd,
        't7_hit_level': sheet['hit_level'],
        't7_damage_raw': sheet['damage'],
        't7_startup_frames': sheet['speed'],
        't7_on_block': sheet['on_block'],
        't7_on_hit': sheet['on_hit'],
        't7_on_ch': sheet['on_ch'],
        # no startup on the sheet ('??', 's', None): the import used 0.3 s, the same as its zero-damage rows
        'startup': round(first_int(sheet['speed']) / 60.0, 3) if first_int(sheet['speed']) is not None else 0.3,
        **weight(total),
        'damage': total,
        'limb': LIMB.get(digits[-1]) if digits else 'both',  # no button ('SIT d,d or u'): the import's 'both'
        'soulGain': min(15, max(3, round(total / 2))),
        'anim_ref': 't7:%s:%s' % (base, re.sub(r'[^a-z0-9]+', '_', str(cmd).lower()).strip('_')),
        'input_slots': [','.join(parts[:i + 1]) for i in range(len(parts))],
        'move_class': 'string' if ',' in key else 'strike',
        'note': note + ' | ' + NOTE_TAIL,
    }
    if ',' in key and len(hits) > 1:  # the import wrote multi_hit on comma strings only ('b+1~2' carries none)
        row['multi_hit'] = {'hits': hits, 'total': total}
    return row


def same_format(data, raw):
    """(indent, ensure_ascii, trailing) that reproduce the file byte for byte, so a rewrite keeps its layout."""
    for ind in (2, 1, 4):
        for ea in (True, False):
            for nl in ('\n', ''):
                if json.dumps(data, indent=ind, ensure_ascii=ea) + nl == raw:
                    return (ind, ea, nl)
    raise SystemExit('cannot reproduce the input file layout byte for byte; refusing to rewrite it')


CHECK = ('startup', 'active', 'recovery', 'knock', 'heavy', 'damage', 'limb', 'soulGain', 'anim_ref', 'input_slots',
         'move_class', 'note', 'multi_hit')


def check_rule(moves, dataset, sheet_by_cmd, base, classes):
    """Every existing T7 row of the classes being added must be reproduced exactly by derive()."""
    seen, bad = 0, []
    for k, m in moves.items():
        if m.get('t7_source') != dataset or m.get('move_class') not in classes:
            continue
        s = sheet_by_cmd.get(m.get('t7_command'))
        if not s:
            continue
        d = derive(m['t7_command'], s, base, 'X', key=m.get('input'))
        seen += 1
        for f in CHECK:
            if f in ('input_slots', 'anim_ref') and ' or ' in str(m.get('t7_command')):
                continue  # 'X or Y' rows keep the whole command as one input
            if json.dumps(m.get(f)) != json.dumps(d.get(f)):
                bad.append((k, f, m.get(f), d.get(f)))
    return seen, bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--moveset', required=True)
    ap.add_argument('--sheet', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--display', required=True)
    ap.add_argument('--proxy-source', required=True)
    ap.add_argument('--split-or', action='store_true')
    ap.add_argument('--archive', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--owner-quote', action='append', default=[])
    a = ap.parse_args()
    raw = open(a.moveset, encoding='utf-8').read()
    ms = json.loads(raw)
    fmt = same_format(ms, raw)
    sheet = json.load(open(a.sheet))
    dataset = ms.get('t7_dataset')
    if not dataset:
        raise SystemExit('%s has no t7_dataset label' % a.moveset)
    moves = ms['moves']
    by_cmd = {r['notation_original']: r for r in sheet['moves']}
    seen, bad = check_rule(moves, dataset, by_cmd, a.base, {'strike', 'string'})
    if bad:
        for b in bad[:20]:
            print('RULE MISMATCH', b)
        raise SystemExit('the import rule does not reproduce %d field(s) of %d existing T7 rows: nothing written' % (len(bad), seen))
    print('rule check: %d existing T7 strike/string rows reproduced exactly (fields: %s)' % (seen, ', '.join(CHECK)))

    have = {m.get('t7_command') for m in moves.values() if m.get('t7_source') == dataset}
    words = ms.setdefault('hit_words', {})
    stance_after = ms.get('stance_after') or {}

    def is_proxy(m):
        return (m.get('t3_source') == a.proxy_source and not m.get('t7_source') and not m.get('t8_id')
                and not m.get('merge_source') and '[WH SIGNATURE]' not in str(m.get('name')))

    added, displaced, skipped = [], [], {}

    def place(key, row, why):
        holder = moves.get(key)
        if holder is not None and not is_proxy(holder):
            skipped[key] = 'held by %r (not a %s stand-in): %s' % (holder.get('name'), a.proxy_source, why)
            return
        if holder is not None:
            pk = key + '~t3proxy'
            if pk in moves:
                raise SystemExit('%s already exists' % pk)
            moves[pk] = holder
            if key in words:
                words[pk] = words.pop(key)
            if key in stance_after:
                stance_after[pk] = stance_after.pop(key)
            displaced.append({'key': key, 'now': pk, 'name': holder.get('name')})
        moves[key] = row
        w = word_from_label(row.get('t7_hit_level'))
        if w is not None:
            words[key] = w
        added.append({'key': key, 'why': why})

    for cmd, s in by_cmd.items():
        if cmd in have:
            continue
        row = derive(cmd, s, a.base, a.display)
        row['t7_source'] = dataset
        place(row['input'], row, 'sheet row %r was dropped by the 2026-10-20 import (deduped by input)' % cmd)
    if a.split_or:
        for k, m in list(moves.items()):
            cmd = str(m.get('t7_command') or '')
            if m.get('t7_source') != dataset or ' or ' not in cmd or ',' in cmd:
                continue
            alts = [x.strip() for x in cmd.split(' or ')]
            if not all(re.fullmatch(r'(?:(?:d/b|d/f|u/b|u/f|[udfb])\+)?[1-4](?:\+[1-4])*', x) for x in alts):
                continue  # only plain single inputs ('4', 'f+4'); stance / motion alternatives stay as they are
            for alt in alts:
                if alt in moves and moves[alt].get('t7_command') == cmd:
                    continue
                row = derive(cmd, by_cmd[cmd], a.base, a.display, key=alt)
                row['t7_source'] = dataset
                row['input'], row['input_slots'], row['name'] = alt, [alt], '%s %s' % (a.display, alt)
                row['note'] = row['note'] + ' | same move as %r (the sheet lists both inputs)' % k
                place(alt, row, 'the sheet row %r lists %r as one of its inputs' % (cmd, alt))
    if stance_after:
        ms['stance_after'] = stance_after

    os.makedirs(os.path.dirname(a.archive), exist_ok=True)
    shutil.copyfile(a.moveset, a.archive)
    ms['t7_sheet_fill'] = {
        'date': '2026-11-10', 'tool': 'tools/moveset-merge/t7_sheet_fill.py', 'owner': a.owner_quote,
        'sheet': a.sheet, 'base': a.base, 'proxy_source': a.proxy_source, 'old_file_archived_as': a.archive,
        'rule_checked_on_existing_t7_rows': seen, 'added': added, 'displaced_to_t3proxy': displaced, 'skipped': skipped,
    }
    with open(a.out, 'w', encoding='utf-8') as f:  # in the file's own JSON layout, so the diff is only the change
        f.write(json.dumps(ms, indent=fmt[0], ensure_ascii=fmt[1]) + fmt[2])
    print(json.dumps(ms['t7_sheet_fill'], indent=1))


if __name__ == '__main__':
    main()
