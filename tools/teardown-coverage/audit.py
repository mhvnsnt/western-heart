#!/usr/bin/env python3
"""Teardown coverage audit (t121u / original 100%-integration task).
Read-only against a git ref (default origin/main); no checkout needed.
Writes docs/teardown-coverage/coverage.json + COVERAGE.md.

Per teardown file:
  source_game  - from teardown/<game>/ (TTT2/T6/T5/T7/T8 are priority sources; T3 is last resort)
  category     - anim | moveset | model | stage | ui | customization | audio | texture | tool | doc | other
  status       - integrated: path (or a parent dir) referenced from code/data (game/ lab/ tools/ test/ scripts/ .github/ customization/ packages/ roster/)
                 documented: referenced only from docs
                 unreferenced: referenced nowhere outside teardown/
Moveset section: per-move source_game across game/assets/movesets/*.json and the
share of reachable command slots per source (the T3 share the owner asked for).
"""
import json, re, subprocess, sys, collections, os
REF = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'docs/teardown-coverage'
def git(*a): return subprocess.run(['git', *a], capture_output=True, text=True, check=True).stdout
GAME = {'tekken3':'T3','tekken5':'T5','tekken6':'T6','tekken7':'T7','tekken8':'T8','tekken-tag-tournament-2':'TTT2',
 'dead-or-alive-4':'DOA4','dead-or-alive-6':'DOA6','def-jam-fight-for-ny':'DEFJAM_FFNY','wwf-no-mercy':'WWF_NO_MERCY',
 'wmxix':'WMXIX','wwe-wrestlemania-xix':'WMXIX','wwe-2k':'WWE2K','urban-reign':'URBAN_REIGN','soulcalibur-2':'SC2',
 'soulcalibur-6':'SC6','virtua-fighter-5':'VF5','vf5':'VF5','street-fighter-3d-games':'SF3D','street-fighter-ex-plus-alpha':'SFEX+A',
 'street-fighter-ex2-plus':'SFEX2+','street-fighter-ex3':'SFEX3','street-fighter-5':'SF5','eastern-mind':'EASTERN_MIND',
 'models':'MIXED','western-heart-design':'WH_DESIGN'}
PRIORITY = ['TTT2','T6','T5','T7','T8']
CODE = ('game/','lab/','tools/','test/','scripts/','.github/','customization/','packages/','roster/')
def category(p):
    l = p.lower(); e = os.path.splitext(l)[1]
    if e in ('.md','.txt','.pdf','.html') : return 'doc'
    if e in ('.py','.js','.mjs','.sh','.gd','.ts','.c','.h'): return 'tool'
    if re.search(r'anim|motion|mot\d|/mot|\.anm|\.tmd|\.fbx$|bvh|pose', l): return 'anim'
    if re.search(r'move|frame.?data|command|combo|string', l): return 'moveset'
    if re.search(r'stage|arena|level|ring', l): return 'stage'
    if re.search(r'menu|/ui/|hud|select|font|portrait|icon', l): return 'ui'
    if re.search(r'custom|attire|costume|item|part', l): return 'customization'
    if e in ('.wav','.ogg','.mp3','.adx','.vag','.at3') or 'audio' in l or 'sound' in l: return 'audio'
    if e in ('.png','.jpg','.tga','.dds','.tim','.bmp','.webp'): return 'texture'
    if e in ('.glb','.gltf','.obj','.dae','.tmd') or 'model' in l or 'mesh' in l: return 'model'
    return 'other'
tree = git('ls-tree','-r','--name-only',REF).split('\n')
td = [p for p in tree if p.startswith('teardown/') and p.count('/') >= 2]
# references: every teardown/... token in files outside teardown/, split by referrer kind
code_refs, doc_refs = set(), set()
out = git('grep','-oE',r'teardown/[A-Za-z0-9_./+-]+',REF,'--',':!teardown',':!*.glb',':!*.png',':!*.jpg',':!*.bin')
for line in out.split('\n'):
    if not line: continue
    sp = line.split(':', 2)
    if len(sp) < 3: continue
    _, f, tok = sp
    tok = tok.rstrip('.,)/') ; 
    (code_refs if f.startswith(CODE) and not f.endswith('.md') else doc_refs).add(tok)
def refd(p, refs):
    if p in refs: return True
    parts = p.split('/')
    for i in range(3, len(parts)):
        if '/'.join(parts[:i]) in refs: return True
    return False
files = []
for p in td:
    g = GAME.get(p.split('/')[1], p.split('/')[1].upper())
    st = 'integrated' if refd(p, code_refs) else ('documented' if refd(p, doc_refs) else 'unreferenced')
    files.append({'path': p, 'source_game': g, 'category': category(p), 'status': st})
# movesets
mv = collections.Counter(); reach = collections.Counter()
mfiles = [p for p in tree if p.startswith('game/assets/movesets/') and p.endswith('.json')]
def src(m):
    if m.get('source_game'): return m['source_game']
    ms = str(m.get('merge_source','')).lower()
    for k,v in (('ttt2','TTT2'),('t6','T6'),('t5','T5'),('t8','T8'),('t7','T7'),('t3','T3')):
        if ms.startswith(k): return v
    if 'ttt2_source' in m: return 'TTT2'
    if 't6_source' in m: return 'T6'
    if 't5_source' in m: return 'T5'
    if 't8_source' in m: return 'T8'
    if 't7_source' in m: return 'T7'
    if 't3_source' in m: return 'T3'
    return 'OTHER'
for p in mfiles:
    try: d = json.loads(git('show', f'{REF}:{p}'))
    except Exception: continue
    moves = d.get('moves') or {}
    if isinstance(moves, list): moves = {str(i): m for i, m in enumerate(moves)}
    for m in moves.values():
        if isinstance(m, dict): mv[src(m)] += 1
    for k in (d.get('slots') or {}).values():
        m = moves.get(k) if isinstance(k, str) else None
        if isinstance(m, dict): reach[src(m)] += 1
def pct(c, k): t = sum(c.values()); return round(100.0 * c[k] / t, 1) if t else 0.0
summary = {'ref': git('rev-parse', REF).strip(), 'teardown_files': len(files)}
by = lambda key: collections.Counter((f[key], f['status']) for f in files)
games = sorted({f['source_game'] for f in files})
summary['by_game'] = {g: {s: sum(1 for f in files if f['source_game']==g and f['status']==s) for s in ('integrated','documented','unreferenced')} for g in games}
for g, v in summary['by_game'].items(): v['total'] = sum(v.values()); v['integrated_pct'] = round(100.0*v['integrated']/v['total'],1)
summary['by_category'] = {c: {s: sum(1 for f in files if f['category']==c and f['status']==s) for s in ('integrated','documented','unreferenced')} for c in sorted({f['category'] for f in files})}
tot = collections.Counter(f['status'] for f in files)
summary['integrated_pct'] = round(100.0*tot['integrated']/len(files),1)
summary['status_totals'] = dict(tot)
summary['moveset_moves_by_source'] = dict(mv.most_common())
summary['moveset_reachable_slots_by_source'] = dict(reach.most_common())
summary['t3_share_moves_pct'] = pct(mv,'T3'); summary['t3_share_reachable_pct'] = pct(reach,'T3')
summary['priority_share_reachable_pct'] = round(sum(pct(reach,k) for k in PRIORITY),1)
os.makedirs(OUT, exist_ok=True)
json.dump({'summary': summary, 'files': files}, open(f'{OUT}/coverage.json','w'), separators=(',',':'))
L = ['# Teardown coverage', '', f'Generated by `tools/teardown-coverage/audit.py` against `{summary["ref"][:10]}`. Re-run: `python3 tools/teardown-coverage/audit.py origin/main docs/teardown-coverage`.', '',
 '**Status definitions.** integrated = the file or a parent dir is referenced from code/data (game, lab, tools, test, scripts, .github, customization, packages, roster). documented = only docs mention it. unreferenced = nothing outside teardown/ mentions it. A reference is evidence of consumption, not proof of correct use; in-game proof is tracked per batch.', '',
 f'**Overall: {summary["integrated_pct"]}% integrated** ({tot["integrated"]} / {len(files)} files; documented-only {tot["documented"]}, unreferenced {tot["unreferenced"]}).', '',
 '## By source game', '', '| source_game | files | integrated | documented | unreferenced | integrated % |', '|---|---|---|---|---|---|']
for g, v in sorted(summary['by_game'].items(), key=lambda x: -x[1]['total']):
    L.append(f'| {g}{" (priority)" if g in PRIORITY else ""}{" (last resort)" if g=="T3" else ""} | {v["total"]} | {v["integrated"]} | {v["documented"]} | {v["unreferenced"]} | {v["integrated_pct"]} |')
L += ['', '## By category', '', '| category | integrated | documented | unreferenced |', '|---|---|---|---|']
for c, v in summary['by_category'].items(): L.append(f'| {c} | {v["integrated"]} | {v["documented"]} | {v["unreferenced"]} |')
L += ['', '## Movesets: source_game of the move data', '', f'T3 share of move records: **{summary["t3_share_moves_pct"]}%**. T3 share of reachable command slots: **{summary["t3_share_reachable_pct"]}%**. Priority sources (TTT2/T6/T5/T7/T8) share of reachable slots: **{summary["priority_share_reachable_pct"]}%**.', '',
 '| source_game | move records | reachable slots |', '|---|---|---|']
for k in sorted(set(mv)|set(reach), key=lambda k: -reach[k]): L.append(f'| {k} | {mv[k]} | {reach[k]} |')
L += ['', 'Per-file detail (path, source_game, category, status) is in `coverage.json`.', '']
open(f'{OUT}/COVERAGE.md','w').write('\n'.join(L))
print(json.dumps({k: summary[k] for k in ('teardown_files','integrated_pct','status_totals','t3_share_moves_pct','t3_share_reachable_pct','priority_share_reachable_pct')}))
