import json, subprocess, sys
pre, post = sys.argv[1], sys.argv[2]
def ls(ref):
    out = subprocess.run(['git','ls-tree','--name-only',ref,'game/assets/movesets/'],capture_output=True,text=True).stdout.split()
    return [p for p in out if p.endswith('.json')]
def load(ref,p):
    r = subprocess.run(['git','show',f'{ref}:{p}'],capture_output=True)
    try: return json.loads(r.stdout)
    except Exception: return None
tot_lost = 0; rows=[]
for p in sorted(set(ls(pre))|set(ls(post))):
    a, b = load(pre,p), load(post,p)
    if not isinstance(a,dict) or not isinstance(b,dict) or 'moves' not in a: continue
    am, bm = a.get('moves',{}), (b.get('moves',{}) if b else {})
    lost = [k for k in am if k not in bm]
    dang = [n for n,k in (b.get('slots') or {}).items() if k not in bm]
    if lost or dang:
        rows.append((p.split('/')[-1], len(am), len(bm), len(lost), len(dang))); tot_lost += len(lost)
for r in rows: print('%-34s pre=%5d now=%5d lost=%4d dangling_slots=%4d' % r)
print('TOTAL lost move keys:', tot_lost, 'files:', len(rows))
