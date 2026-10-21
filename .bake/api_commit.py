import base64, json, subprocess, sys
from pathlib import Path

REPO = 'mhvnsnt/western-heart'
BASE_TREE = 'd9d486f073e1d282a668da0e4de451df0e6d7f2b'
BASE_COMMIT = 'ed0f717860cc925adf8f98580e769376b01580a4'
FILES = [
 'game/js/fighter.js', 'docs/anim/PROCEDURAL_AUDIT.md', 'docs/anim/BANK-TABLE-2026-10-20.md',
 'lab/tools/t3_motion_bake.py', 'tools/anim/t3_row_bake.py', 'tools/anim/t3_bake_packs.py',
 'game/assets/anim/t3/paul/rows.pack.json', 'game/assets/anim/t3/lei/rows.pack.json',
 'game/assets/anim/t3/nina/rows.pack.json', 'game/assets/anim/t3/hwoarang/rows.pack.json',
 'game/assets/anim/t3/eddy/rows.pack.json', 'game/assets/anim/t3/julia/rows.pack.json',
 'game/assets/anim/t3/anna/rows.pack.json', 'game/assets/anim/t3/bosconovitch/rows.pack.json',
 'game/assets/anim/t3/armorking/rows.pack.json',
 'lab/game/assets/t3_paul.glb', 'lab/game/assets/t3_lei.glb', 'lab/game/assets/t3_nina.glb',
 'lab/game/assets/t3_hwoarang.glb', 'lab/game/assets/t3_eddy.glb', 'lab/game/assets/t3_julia.glb',
 'lab/game/assets/t3_anna.glb', 'lab/game/assets/t3_bosconovitch.glb', 'lab/game/assets/t3_armorking.glb',
 'teardown/tekken3/models/paul/paul.kmd', 'teardown/tekken3/models/lei/lei.kmd',
 'teardown/tekken3/models/nina/nina.kmd', 'teardown/tekken3/models/hwoarang/hwoarang.kmd',
 'teardown/tekken3/models/eddy/eddy.kmd', 'teardown/tekken3/models/julia/julia.kmd',
 'teardown/tekken3/models/anna/anna.kmd', 'teardown/tekken3/models/bosconovitch/bosconovitch.kmd',
 'teardown/tekken3/renders/pose-check/paul_stance75.obj', 'teardown/tekken3/renders/pose-check/lei_stance75.obj',
 'teardown/tekken3/renders/pose-check/nina_stance75.obj', 'teardown/tekken3/renders/pose-check/hwoarang_stance75.obj',
 'teardown/tekken3/renders/pose-check/eddy_stance75.obj', 'teardown/tekken3/renders/pose-check/julia_stance75.obj',
 'teardown/tekken3/renders/pose-check/anna_stance75.obj', 'teardown/tekken3/renders/pose-check/bosconovitch_stance75.obj',
 'docs/anim/proof-bank-wiring-20261020/docfrank/console.log',
 'docs/anim/proof-bank-wiring-20261020/yukihyo/console.log',
 'docs/anim/proof-bank-wiring-20261020/awapop/console.log',
 'docs/anim/proof-bank-wiring-20261020/tou/console.log',
 'docs/anim/proof-bank-wiring-20261020/kingtyrant/console.log',
]
STATE = Path('.bake/api_commit_state.json')
state = json.loads(STATE.read_text()) if STATE.exists() else {}

def gh(endpoint, payload, method='POST'):
    p = subprocess.run(['gh', 'api', f'repos/{REPO}/{endpoint}', '-X', method, '--input', '-'],
                       input=json.dumps(payload).encode(), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f'{endpoint}: {p.stderr.decode()[:300]}')
    return json.loads(p.stdout)

for f in FILES:
    if f in state:
        continue
    data = Path(f).read_bytes()
    r = gh('git/blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
    state[f] = r['sha']
    STATE.write_text(json.dumps(state))
    print(f'blob {len(state)}/{len(FILES)} {f} -> {r["sha"][:8]}', flush=True)

tree_entries = [{'path': f, 'mode': '100644', 'type': 'blob', 'sha': state[f]} for f in FILES]
r = gh('git/trees', {'base_tree': BASE_TREE, 'tree': tree_entries})
tree_sha = r['sha']
print('tree ->', tree_sha, flush=True)

msg = ("Anim banks: every fighter on their own base's clips \u2014 remainder-bank row packs + per-fighter bank bindings\n\n"
 "Owner order 2026-10-20: Blanka clips for CHARGER, Zangief for KRONOS, Vega for KORESHI, Iori for DEATHFANG, "
 "Wolf for NIGHTWOLF, Bryan for SKULL, Jack for SAM-UR-A1, Bosconovitch for DOC FRANK, Alisa for CAPE JONES, "
 "Steve for ZUI, King for PANTERA, Armor King for YUKIHYO, Bob for BURGER, and so on.\n\n"
 "- rows.pack.json for all 9 remainder banks (PR #405 landed their action clips): bosconovitch FULL move-index "
 "bake (647 rows), armorking with the 176 king-referenced rows, paul/lei/nina/hwoarang/eddy/julia/anna "
 "referenced-rows packs (full-index bake = tools/anim/t3_bake_packs.py, added here; bake maps extended additively).\n"
 "- fighter.js FIGHTER_BANK: awapop->nina, torch->anna, kingtyrant->eddy, kai->eddy, tou->paul, byou->lei, "
 "gyou->hwoarang, zen->julia, rave->lei, yukihyo->armorking, nightwolf->julia (CANON base; owner-named Wolf/VF "
 "is a proven gap, flagged). _moveRowAction king/armorking family rule.\n"
 "- Teardown inputs: KMDs + stance OBJs for 8 characters missing from main + plain t3_<char>.glb bake rigs.\n"
 "- docs/anim/BANK-TABLE-2026-10-20.md (full roster table + era + GAP register; SF PAC decode = CHARGER case #1) "
 "+ PROCEDURAL_AUDIT s5 entries + in-engine proof logs. Zero deletions.")
r = gh('git/commits', {'message': msg, 'tree': tree_sha, 'parents': [BASE_COMMIT]})
commit_sha = r['sha']
print('commit ->', commit_sha, flush=True)
r = gh('git/refs', {'ref': 'refs/heads/feat/anim-bank-wiring-20261020', 'sha': commit_sha})
print('branch ->', r['ref'], commit_sha, flush=True)
