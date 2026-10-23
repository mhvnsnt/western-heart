#!/usr/bin/env python3
"""No-loss guard for the Western Heart moveset union merge.

Independently verifies a merged moveset set against (a) current main and
(b) the union of all historical versions. This is the owner's hard guard:
if any fighter loses a move, string, special, or working input, the guard
fails and the merge must not land.

Checks per fighter file on main:
 1. Merged file parses; fighter field matches filename.
 2. BASE PRESERVATION — every main move (by key, deep-equal payload), every
    main string and special (multiset, canonical JSON) is still present.
 3. UNION COVERAGE (moves) — every historical move's canonical input
    (entry.input, else key; whitespace-normalized) is present in the merged
    file as a key or as some entry's canonical input. Historical storage
    keys that are mere row indexes (seed files keyed '5', '11', ... with the
    real input declared in entry.input) are reported as informational counts,
    not failures: the move is covered when its canonical input is present.
 4. UNION COVERAGE (strings/specials) — every historical input is present.
 5. NO FABRICATION — every merged move key absent from main traces back to
    a historical version (same canonical input or same key).

Usage: guard.py <versions_dir> <index.json> <main_files.json> <merged_dir>
Merged files are read from <merged_dir> when present there, else the main
version is used (file untouched by the merge). Exit 1 on any failure.
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

def move_ci(key, entry):
    if isinstance(entry, dict) and entry.get('input'):
        return ws_norm(entry['input'])
    return ws_norm(key)

def main():
    versions_dir, index_path, main_path, merged_dir = sys.argv[1:5]
    idx = json.load(open(index_path))
    main_files = json.load(open(main_path))
    failures = []
    rows = []
    for path, blobs in sorted(idx.items()):
        if path not in main_files:
            continue
        fid = os.path.basename(path)[:-5]
        base = json.load(open(os.path.join(versions_dir, fid, main_files[path] + '.json')))
        mpath = os.path.join(merged_dir, fid + '.json')
        merged = json.load(open(mpath)) if os.path.exists(mpath) else base
        errs = []
        if merged.get('fighter') != fid:
            errs.append(f"fighter field {merged.get('fighter')!r} != {fid!r}")
        bm, mm = base.get('moves') or {}, merged.get('moves') or {}
        for k, v in bm.items():
            if k not in mm:
                errs.append(f'base move key lost: {k}')
            elif canon(mm[k]) != canon(v):
                errs.append(f'base move payload changed: {k}')
        for cat in ('strings', 'specials'):
            bcount = collections.Counter(canon(x) for x in base.get(cat) or [])
            mcount = collections.Counter(canon(x) for x in merged.get(cat) or [])
            for item, n in bcount.items():
                if mcount[item] < n:
                    errs.append(f'base {cat[:-1]} lost: {item[:80]}')
        merged_cis = set()
        for k, v in mm.items():
            merged_cis.add(ws_norm(k)); merged_cis.add(move_ci(k, v))
        merged_str = {ws_norm(s['input']) for s in merged.get('strings') or []
                      if isinstance(s, dict) and s.get('input')}
        merged_spc = {ws_norm(s['input']) for s in merged.get('specials') or []
                      if isinstance(s, dict) and s.get('input')}
        hist_cis, hist_str, hist_spc = set(), set(), set()
        storage_only_keys = set()
        for blob in blobs:
            d = json.load(open(os.path.join(versions_dir, fid, blob + '.json')))
            mv = d.get('moves')
            if isinstance(mv, dict):
                for k, v in mv.items():
                    hist_cis.add(move_ci(k, v))
                    if ws_norm(k) not in merged_cis:
                        storage_only_keys.add(ws_norm(k))
            elif isinstance(mv, list):
                for s in mv:
                    if isinstance(s, str):
                        hist_cis.add(ws_norm(s))
            for s in d.get('strings') or []:
                if isinstance(s, dict) and s.get('input'):
                    hist_str.add(ws_norm(s['input']))
            for s in d.get('specials') or []:
                if isinstance(s, dict) and s.get('input'):
                    hist_spc.add(ws_norm(s['input']))
        for ci in sorted(hist_cis - merged_cis):
            errs.append(f'union move input not covered: {ci}')
        for i in sorted(hist_str - merged_str):
            errs.append(f'union string input not covered: {i}')
        for i in sorted(hist_spc - merged_spc):
            errs.append(f'union special input not covered: {i}')
        base_keys = set(bm)
        for k in mm:
            if k not in base_keys and ws_norm(k) not in hist_cis and move_ci(k, mm[k]) not in hist_cis:
                errs.append(f'fabricated move key (no historical source): {k}')
        rows.append((fid, len(bm), len(mm), 'FAIL' if errs else 'PASS'))
        if storage_only_keys:
            rows[-1] = (fid, len(bm), len(mm), rows[-1][3] +
                        f' (info: {len(storage_only_keys)} historical storage keys covered by canonical input, e.g. {sorted(storage_only_keys)[:4]})')
        for e in errs:
            failures.append(f'{fid}: {e}')
    w = max(len(r[0]) for r in rows)
    for fid, b, m, st in rows:
        print(f'{fid:<{w}}  moves {b:>4} -> {m:>4}  {st}')
    print(f'\n{sum(1 for r in rows if r[3].startswith("PASS"))}/{len(rows)} fighters PASS')
    if failures:
        print(f'\n{len(failures)} GUARD FAILURES:')
        for f in failures[:60]:
            print(' -', f)
        sys.exit(1)
    print('GUARD: PASS — no move, string, special, or working input lost vs union of all versions + current main.')

if __name__ == '__main__':
    main()
