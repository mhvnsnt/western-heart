#!/usr/bin/env python3
"""Additive union merge for Western Heart movesets — v2 (canonical-input identity).

Unions every historical version of game/assets/movesets/{fighter}.json
(548 unique versions across 60 commits, all refs) over the current main file.

Identity model (grounded in the files themselves):
- A move's identity is its canonical input: entry.input when the entry
  declares one, else its storage key (whitespace-normalized; spaces around
  ',' and '+' provably break the runtime parser in game/js/movesets.js).
  Storage keys in seed files are often bare indexes ('5' -> input 'f+1')
  or rekeys ('1_r48'); the declared input is the move.
- Current main is the base, preserved verbatim: no existing move, string,
  or special is edited, rekeyed, or removed. Additions only.
- A historical move whose canonical input is absent from main (neither as
  a key nor as any entry's declared input) is added under key = canonical
  input, payload verbatim from its richest historical version.
  If several distinct payloads share one canonical input (different bank
  rows), extras are kept under '<input>_r<row>' — the repo's own rekey
  convention (cluster merges / PR #357 forward-merge precedent).
- Strings/specials union by input; main wins contested inputs; a
  historical special with a contested input but different payload is
  appended with `forward_merge_alt_of` (PR #357 precedent).
- Files with no additions are not written at all.

Usage: build_merge.py <versions_dir> <index.json> <main_files.json> <out_dir> <report.json>
"""
import json, os, re, sys, collections

def ws_norm(s):
    if not isinstance(s, str):
        return s
    s = s.strip()
    s = re.sub(r'\s*,\s*', ',', s)
    s = re.sub(r'\s*\+\s*', '+', s)
    return s

def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)

ERA_PREFIXES = [('t8', 6), ('wh', 6), ('t7', 5), ('ttt2', 4), ('t6', 3),
                ('doa', 3), ('ur', 3), ('nomercy', 3), ('vf', 3), ('sf', 3),
                ('t5', 2), ('t3', 1)]
ERA_NAMES = {6: 'T8/WH-newest', 5: 'T7', 4: 'TTT2', 3: 'T6/other-teardown',
             2: 'T5/unknown', 1: 'T3', 0: 'unprovenanced'}

def era_rank(entry):
    """Newest-era rank of a move entry from its own provenance fields.
    Owner standard 2026-10-20: prefer the richest, newest-era expression
    (T6/T7/T8 + other teardowns); T3 is the fallback, never the target."""
    if not isinstance(entry, dict):
        return 0
    best = 0
    for k, v in entry.items():
        for pre, rank in ERA_PREFIXES:
            if k == f'{pre}_source' or k.startswith(f'{pre}_') or k == f'{pre}_input':
                best = max(best, rank)
        if k == 'anim_ref' and isinstance(v, str) and ':' in v:
            src = v.split(':', 1)[0]
            for pre, rank in ERA_PREFIXES:
                if src == pre:
                    best = max(best, rank)
    return best

def move_ci(key, entry):
    if isinstance(entry, dict) and entry.get('input'):
        return ws_norm(entry['input'])
    return ws_norm(key)

def main():
    versions_dir, index_path, main_path, out_dir, report_path = sys.argv[1:6]
    idx = json.load(open(index_path))
    main_files = json.load(open(main_path))
    os.makedirs(out_dir, exist_ok=True)
    report = {'fighters': {}, 'totals': collections.Counter()}

    for path, blobs in sorted(idx.items()):
        if path not in main_files:
            continue
        fid = os.path.basename(path)[:-5]
        base = json.load(open(os.path.join(versions_dir, fid, main_files[path] + '.json')))
        base_moves = base.get('moves') or {}
        covered = set()
        for k, v in base_moves.items():
            covered.add(ws_norm(k)); covered.add(move_ci(k, v))
        base_str_inputs = {ws_norm(s['input']) for s in base.get('strings') or []
                           if isinstance(s, dict) and s.get('input')}
        base_spc = base.get('specials') or []
        base_spc_inputs = {ws_norm(s['input']) for s in base_spc
                           if isinstance(s, dict) and s.get('input')}
        base_spc_by_input = collections.defaultdict(list)
        for s in base_spc:
            if isinstance(s, dict) and s.get('input'):
                base_spc_by_input[ws_norm(s['input'])].append(s)

        cand = {}          # ci -> list of (score, last, payload)
        cand_str = {}
        cand_spc = {}
        versions_seen = 0
        for blob, (first, last) in blobs.items():
            vpath = os.path.join(versions_dir, fid, blob + '.json')
            if not os.path.exists(vpath):
                continue
            versions_seen += 1
            d = json.load(open(vpath))
            mv = d.get('moves')
            if isinstance(mv, dict):
                for k, v in mv.items():
                    ci = move_ci(k, v)
                    if ci in covered:
                        continue
                    score = len(v) if isinstance(v, dict) else 0
                    cand.setdefault(ci, []).append((score, last, v))
            for s in d.get('strings') or []:
                if isinstance(s, dict) and s.get('input'):
                    nk = ws_norm(s['input'])
                    if nk not in base_str_inputs and nk not in cand_str:
                        cand_str[nk] = s
            for s in d.get('specials') or []:
                if isinstance(s, dict) and s.get('input'):
                    nk = ws_norm(s['input'])
                    if nk not in cand_spc:
                        cand_spc[nk] = s

        added_keys = []
        merged = json.loads(json.dumps(base))
        if cand:
            mv = merged.setdefault('moves', {})
            used = set(mv.keys())
            for ci in sorted(cand):
                payloads = sorted(cand[ci], key=lambda t: (era_rank(t[2]),
                                  bool(isinstance(t[2], dict) and t[2].get('name')),
                                  t[0], t[1]), reverse=True)
                best = payloads[0][2]
                mv[ci] = best; used.add(ci); added_keys.append(ci)
                seen = {canon(best)}
                for _, _, extra in payloads[1:]:
                    if canon(extra) in seen or not isinstance(extra, dict):
                        continue
                    seen.add(canon(extra))
                    row = None
                    for f in ('t3_row', 'ttt2_row', 't6_row', 'doa_row'):
                        if isinstance(extra.get(f), int):
                            row = extra[f]; break
                    rk = f'{ci}_r{row}' if row is not None else None
                    if rk and rk not in used and rk not in covered:
                        mv[rk] = extra; used.add(rk); added_keys.append(rk)
        added_str = 0
        if cand_str:
            lst = merged.setdefault('strings', [])
            for nk in sorted(cand_str):
                lst.append(cand_str[nk]); added_str += 1
        added_spc = 0; alt_spc = 0
        if cand_spc:
            lst = merged.setdefault('specials', [])
            existing = {canon(s) for s in lst}
            for nk in sorted(cand_spc):
                s = cand_spc[nk]
                if nk in base_spc_inputs:
                    if canon(s) not in existing and not any(
                            canon(x) == canon(s) for x in base_spc_by_input.get(nk, [])):
                        alt = dict(s); alt['forward_merge_alt_of'] = s['input']
                        if canon(alt) not in existing:
                            lst.append(alt); existing.add(canon(alt)); alt_spc += 1
                else:
                    lst.append(s); existing.add(canon(s)); added_spc += 1

        total_added = len(added_keys) + added_str + added_spc + alt_spc
        report['fighters'][fid] = {'versions': versions_seen, 'moves_added': len(added_keys),
                                   'strings_added': added_str, 'specials_added': added_spc,
                                   'specials_alt': alt_spc, 'added_move_keys': added_keys}
        # Era census of the fighter's final set (owner standard 2026-10-20:
        # newest-era expression preferred, T3 = fallback only).
        census = collections.Counter(era_rank(e) for e in merged['moves'].values())
        era_note = ('final set era census: ' + ', '.join(
            f'{ERA_NAMES[k]}={v}' for k, v in sorted(census.items(), reverse=True))
            + '; additions selected newest-era first (T8/T7/TTT2/T6+other teardowns), '
              'T3 payloads used only where no newer expression exists; union-first, no-loss absolute')
        report['fighters'][fid]['era_census'] = {ERA_NAMES[k]: v for k, v in sorted(census.items(), reverse=True)}
        report['fighters'][fid]['era_dominant'] = ERA_NAMES[census.most_common(1)[0][0]] if census else None
        report['fighters'][fid]['era_t3_only'] = set(census) <= {0, 1}
        report['fighters'][fid]['era_note'] = era_note
        if total_added == 0:
            continue
        merged['union_merge'] = {
            'date': '2026-10-20',
            'method': 'additive union of all historical versions of this file '
                      '(548 versions / 60 commits / all refs) over current main; '
                      'identity = canonical input (entry.input, else key); main '
                      'preserved verbatim, main wins contested inputs (PR #357 precedent)',
            'versions_considered': versions_seen,
            'moves_added': len(added_keys),
            'strings_added': added_str,
            'specials_added': added_spc,
            'specials_alt_appended': alt_spc,
            'added_move_keys': added_keys,
        }
        merged['union_merge']['era_note'] = era_note
        open(os.path.join(out_dir, fid + '.json'), 'w').write(
            json.dumps(merged, indent=2, ensure_ascii=False) + '\n')
        t = report['totals']
        t['moves_added'] += len(added_keys); t['strings_added'] += added_str
        t['specials_added'] += added_spc; t['specials_alt'] += alt_spc
        t['files_changed'] += 1

    report['totals'] = dict(report['totals'])
    json.dump(report, open(report_path, 'w'), indent=1)
    print(json.dumps(report['totals'], indent=1))

if __name__ == '__main__':
    main()
