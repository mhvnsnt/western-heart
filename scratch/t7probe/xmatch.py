import pickle, math, sys
P='/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe/'
C8, A = [], []
for n in ('kin.pkl', 'common.arc.pkl', 'kinmot.bin.pkl'):
    c, a = pickle.load(open(P+n, 'rb'))
    for x in c: x['src'] = n; C8.append(x)
    for x in a: x['src'] = n; A.append(x)
H = (35, 47, 56, 65)
def sig(fr):
    return [[abs(f[h]) for h in H] for f in fr], [f[4] for f in fr]
res = []
for c in C8:
    hc, yc = sig(c['fr'])
    if max(max(r) for r in hc) < 1e-6: continue
    for a in A:
        if len(a['fr']) != len(c['fr']): continue
        ha, ya = sig(a['fr'])
        e = math.sqrt(sum((x-y)**2 for r1, r2 in zip(hc, ha) for x, y in zip(r1, r2)) / (4*len(hc)))
        res.append((e, c['src'], c['M'], c['i'], a['src'], a['M'], a['i'], len(hc)))
res.sort()
for r in res[:25]: print('hinge-rms %.3f rad | C8 %s M%d#%d | 64 %s M%d#%d | len %d' % r)
pickle.dump(res[:200], open(P+'xmatch.pkl','wb'))
