#!/usr/bin/env python3
"""Map DW kit-pack clips to moves (dw-followups, 2026-11-08).

The retarget rollout (PR #1654) baked 152 clips into 5 wh-dw-moves/1 packs
as DATA: the kit packs had moves = {} and every clip listed in `skipped`
("move mapping owed - not guessed"). This script claims those mappings from
the MEASURED moveset library (game/data/moveset-library/banks/dw.json,
165 moves built from dw-motion-bank.json) - never invented:

  * one `moves` entry per packed clip that has a library move, keyed by the
    library move id minus the 'dw:' prefix (e.g. 'warden:bakutyu',
    'surge:all-beam', 'unmasked:ozhe-power'). The key is the library id,
    so it traces back to the library file with no new naming.
  * entry shape is exactly the pilot's (moves.pantera.pack.json):
    {clip, input, dw_source, active_frames, verified} - input is null
    (the library carries no measured input for any DW move), active_frames
    null (the decode carries no hit timing), verified false.
  * the pilot's 4 pantera moves (surge, surge-trigger, 1+3, 2+4) are
    verified untouched, never rewritten: 'surge' is the beam clip
    dwhadoh00, which has NO library move; the throws are input-keyed
    (the game drives throws by input), not library-keyed.
  * a clip with no library move stays in `skipped` with its reason.
    After this run every packed clip has a library move except dwhadoh00
    (already mapped as 'surge'), so `skipped` is empty everywhere.
  * bank moves whose clip was never baked (15: the 11 x 4-bone part-clips,
    djin_newhane01-03, dwup00 - dropped from the pantera pack by the
    trigger swap) stay unmapped and are listed in DW-MOVE-MAP-LOG.md
    with their measured reason. They map onto nothing - there is no clip
    to bind them to.

Run: python3 tools/anim/dw_map_kit_moves.py [--check | --apply]
  --check (default): verify the mapping table, print it, write nothing.
  --apply: rewrite the 5 packs (moves + skipped, indent=1, same key order
    as dw_curve_bake.py writes them) and DW-MOVE-MAP-LOG.md in the packs
    dir. Idempotent: a second run changes nothing.
Re-bake safety: tools/anim/dw_curve_bake.py preserves an existing pack's
moves on re-bake; if a pack is baked from scratch, re-run this script.

Sources (SHA-256 logged in the map log, per docs/RULES_NO_GUESSING.md):
  game/data/moveset-library/banks/dw.json
  teardown/tekken5/dw-motion-curves.json (kit cross-check)
  game/assets/anim/dw/moves.*.pack.json (the 5 packs)
"""
import argparse
import hashlib
import json
import os
import re
import sys

PACK_FILES = [
    'moves.pantera.pack.json',
    'moves.warden.pack.json',
    'moves.unmasked.pack.json',
    'moves.drowned-ogre.pack.json',
    'moves.wave-echo.pack.json',
]
SKIPPED_REASON = 'baked as data, move mapping owed — not guessed'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path) as f:
        return json.load(f)


def bank_by_clip(bank_path):
    """library move id -> move, keyed by clip stem (gym_<clip>.dat)."""
    bank = load_json(bank_path)
    out = {}
    for mv in bank['moves']:
        m = re.search(r'gym_([a-z0-9_]+)\.dat', mv['provenance']['note'])
        if not m:
            raise SystemExit(f"bank move {mv['id']} has no gym_ source file in its provenance note")
        clip = m.group(1)
        if clip in out:
            raise SystemExit(f"bank has two moves for clip {clip}: {out[clip]['id']} and {mv['id']}")
        out[clip] = mv
    return out


def build_mapping(repo, packs_dir, bank_path):
    by_clip = bank_by_clip(bank_path)
    packs = {}
    problems = []
    missing = []
    for fname in PACK_FILES:
        ppath = os.path.join(packs_dir, fname)
        if not os.path.exists(ppath):
            # A single-set re-bake dir holds only that set's pack; the other
            # packs are not missing from the repo, just not in this dir.
            missing.append(fname)
            continue
        pack = load_json(ppath)
        mapped = {m['clip'] for m in pack['moves'].values()}
        new_moves = {}
        for clip in sorted(pack['clips']):
            if clip in mapped:
                continue
            mv = by_clip.get(clip)
            if mv is None:
                problems.append(f"{fname}: clip {clip} has no moveset-library move — stays UNMAPPED")
                continue
            key = mv['id'][3:] if mv['id'].startswith('dw:') else mv['id']
            if key in pack['moves'] or key in new_moves:
                problems.append(f"{fname}: key collision on {key} (clip {clip})")
                continue
            new_moves[key] = {
                'clip': clip,
                'input': None,
                'dw_source': 'gym_' + clip + '.dat',
                'active_frames': None,
                'verified': False,
            }
        packs[fname] = (pack, new_moves)
    return by_clip, packs, problems


def main():
    ap = argparse.ArgumentParser(description='Map DW kit-pack clips to moves from the measured moveset library.')
    ap.add_argument('--repo', default=None, help='repo root (default: two levels up from this script)')
    ap.add_argument('--packs-dir', default=None, help='packs dir (default: <repo>/game/assets/anim/dw)')
    ap.add_argument('--bank', default=None, help='moveset-library dw bank (default: <repo>/game/data/moveset-library/banks/dw.json)')
    ap.add_argument('--check', action='store_true', help='verify only, write nothing (default)')
    ap.add_argument('--apply', action='store_true', help='rewrite packs + DW-MOVE-MAP-LOG.md')
    args = ap.parse_args()
    repo = args.repo or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    packs_dir = args.packs_dir or os.path.join(repo, 'game', 'assets', 'anim', 'dw')
    bank_path = args.bank or os.path.join(repo, 'game', 'data', 'moveset-library', 'banks', 'dw.json')
    curves_path = os.path.join(repo, 'teardown', 'tekken5', 'dw-motion-curves.json')

    by_clip, packs, problems = build_mapping(repo, packs_dir, bank_path)
    if not packs:
        print('no pack files found in ' + packs_dir)
        return 1
    total_new = sum(len(nm) for _, nm in packs.values())
    total_moves = sum(len(p['moves']) + len(nm) for p, nm in packs.values())
    total_clips = sum(len(p['clips']) for p, _ in packs.values())
    print(f'library moves: {len(by_clip)}; pack clips: {total_clips}; '
          f'moves after mapping: {total_moves} (new: {total_new})')
    for fname in packs:
        pack, new_moves = packs[fname]
        print(f'  {fname}: {len(pack["clips"])} clips, {len(pack["moves"])} mapped already, '
              f'+{len(new_moves)} new, skipped after: '
              f'{len([c for c in pack["clips"] if c not in {m["clip"] for m in pack["moves"].values()} and c not in {m["clip"] for m in new_moves.values()}])}')
    if problems:
        print('PROBLEMS (unmapped stays in skipped, never invented):')
        for p in problems:
            print('  - ' + p)
    if not args.apply:
        print('--check only: nothing written.')
        return 0 if not problems else 1

    # --apply: verify the pilot's 4 moves are untouched, then write.
    log_lines = []
    log_lines.append('# DW kit-pack move map log')
    log_lines.append('')
    log_lines.append('Mapped 2026-11-08 (branch `dw-followups`) by `tools/anim/dw_map_kit_moves.py` '
                     'from the measured moveset library — never invented. One `moves` entry per '
                     'packed clip with a library move, keyed by the library move id minus `dw:`; '
                     '`input` null (no measured DW input), `active_frames` null (no hit timing in '
                     'the decode), `verified` false (not yet watched playing).')
    log_lines.append('')
    log_lines.append('## Sources (SHA-256)')
    log_lines.append('')
    log_lines.append(f'- moveset library: `game/data/moveset-library/banks/dw.json` sha256 `{sha256(bank_path)}`')
    if os.path.exists(curves_path):
        log_lines.append(f'- curves (kit cross-check): `teardown/tekken5/dw-motion-curves.json` sha256 `{sha256(curves_path)}`')
    for fname in packs:
        log_lines.append(f'- pack before mapping: `{fname}` sha256 `{sha256(os.path.join(packs_dir, fname))}`')
    log_lines.append('')
    for fname in packs:
        pack, new_moves = packs[fname]
        # Existing moves must be byte-identical after the run: only add, never rewrite.
        before_moves = json.dumps(pack['moves'], sort_keys=True)
        for key, m in new_moves.items():
            pack['moves'][key] = m
        assert json.dumps({k: pack['moves'][k] for k in json.loads(before_moves)}, sort_keys=True) == before_moves
        pack['moves'] = dict(sorted(pack['moves'].items()))
        moved = {m['clip'] for m in pack['moves'].values()}
        pack['skipped'] = [{'clip': c, 'reason': SKIPPED_REASON}
                           for c in sorted(pack['clips']) if c not in moved]
        with open(os.path.join(packs_dir, fname), 'w') as f:
            json.dump(pack, f, indent=1)
            f.write('\n')
        log_lines.append(f'## {fname} — {len(pack["clips"])} clips, {len(pack["moves"])} moves, '
                         f'{len(pack["skipped"])} skipped')
        log_lines.append('')
        log_lines.append('| move key | clip | library move | type | frames | gloss |')
        log_lines.append('|---|---|---|---|---|---|')
        for key in sorted(pack['moves']):
            m = pack['moves'][key]
            lib = by_clip.get(m['clip'])
            if lib is None:
                # Pilot move with no library move (beam 'surge' only).
                log_lines.append(f'| `{key}` | `{m["clip"]}` | — (pilot move, no library entry) | — | — | pilot-mapped, kept as-is |')
                continue
            log_lines.append(f'| `{key}` | `{m["clip"]}` | `{lib["id"]}` | {lib["type"]} | '
                             f'{lib["frames"]["total"]} | {lib["name"].split(" — ", 1)[-1]} |')
        log_lines.append('')
        if pack['skipped']:
            log_lines.append('Unmapped (stays in `skipped`, never invented):')
            log_lines.append('')
            for s in pack['skipped']:
                log_lines.append(f'- `{s["clip"]}`: {s["reason"]}')
            log_lines.append('')
    # Library moves whose clip was never baked: nothing to bind them to.
    packed_clips = set()
    for fname in packs:
        packed_clips.update(packs[fname][0]['clips'])
    unbaked = sorted(set(by_clip) - packed_clips)
    log_lines.append('## Library moves with no baked clip (unmapped — nothing to bind)')
    if len(packs) < len(PACK_FILES):
        log_lines.append(f'(this run covered only: {", ".join(sorted(packs))} — the full list is in the repo\'s DW-MOVE-MAP-LOG.md)')
    log_lines.append('')
    log_lines.append('| library move | clip | type | reason not baked |')
    log_lines.append('|---|---|---|---|')
    curves = load_json(curves_path) if os.path.exists(curves_path) else {'clips': []}
    by_src = {c['source_file']: c for c in curves.get('clips', [])}
    for clip in unbaked:
        lib = by_clip[clip]
        src = 'gym_' + clip + '.dat'
        entry = by_src.get(src, {})
        bones = entry.get('bones')
        if bones is None:
            reason = 'no data in TK5DATA2 (list reference only)' if 'ozhe_1ckj66a' in clip else 'not in the decoded curves'
        elif bones == 4:
            reason = '4-bone appendage part-clip (tail/teil1), not a full-body skeleton'
        elif bones == 12:
            reason = '12-bone wings/feathers appendage motion, not fighter motion'
        elif bones == 27:
            reason = '27-bone single dropped from the pantera pack by the trigger swap (ozhe_power replaces dwup00)'
        else:
            reason = f'{bones}-bone skeleton, not bakeable with the 35/27-bone FK model'
        log_lines.append(f'| `{lib["id"]}` | `{clip}` | {lib["type"]} | {reason} |')
    log_lines.append('')
    log_lines.append('## What is NOT mapped')
    log_lines.append('')
    log_lines.append('- Inputs, damage, hitboxes: the library carries none of these for DW moves '
                     '(all null) — the game times DW moves on the moveset\'s own S/A/R. '
                     'Mapping a clip to a move does NOT claim an input for it.')
    log_lines.append('- The 24 ikt5 35-bone clips: decoded, but no library entry, so the '
                     'bank-keyed bake path never baked them. They need library entries first, '
                     'not a new FK model.')
    log_lines.append('- The 33 non-35/27 clips: not bakeable with the current FK model '
                     '(11× 4-bone, 15× 78-bone 1-frame init poses, 1× 96-bone devil init object, '
                     '2× 111-bone boss init objects, 4× 12-bone wings) — counted from '
                     '`dw_measurements.json`.')
    log_lines.append('')
    with open(os.path.join(packs_dir, 'DW-MOVE-MAP-LOG.md'), 'w') as f:
        f.write('\n'.join(log_lines))
    print(f'Wrote {len(packs)} pack(s) + DW-MOVE-MAP-LOG.md in {packs_dir}')
    if problems:
        print(f'NOTE: {len(problems)} clip(s) stayed UNMAPPED (see above); skipped lists keep them.')
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
