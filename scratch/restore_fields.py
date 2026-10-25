import json, sys, collections
FIGHTERS = ['burger','demonio','diablo','kinpo','pantera','phantom','scimitar','skull']
tot = collections.Counter(); diffs = 0; ex = []
for f in FIGHTERS:
    d = json.load(open(f'game/assets/movesets/{f}.json'))
    q = d.get('t8_quarantine_20261024', {})
    qm = q.get('moves', q) if isinstance(q, dict) else {}
    for k, qv in qm.items():
        if not isinstance(qv, dict): continue
        mv = d['moves'].get(k)
        if mv is None: tot['not_restored'] += 1; continue
        for fld, val in qv.items():
            if fld not in mv: tot['missing:' + fld] += 1; diffs += 1; (len(ex) < 6 and ex.append((f, k, fld)))
            elif mv[fld] != val and fld not in ('anim_t3',): tot['changed:' + fld] += 1
print(dict(tot.most_common(30))); print('examples', ex)
