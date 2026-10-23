#!/usr/bin/env python3
"""DOA4 phase 13 Job 3(a): L2 census RESUME — the decision set only
(42 head packages + 43 proven-family bodies), writing the merged
JSON after EVERY package (the full-census run died at 131/148 with
its results in memory only; this pass is the resilient artifact).
Output: scratch p13/texrecord_census.json (analyzer-compatible).
"""
import importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location(
    'census', '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase13/tools/texrecord_census_p13.py')
census = importlib.util.module_from_spec(spec)
sys.argv = ['census']  # avoid --l1-only
spec.loader.exec_module.__self__ if False else None
import types
# load module without running main
src = open('/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase13/tools/texrecord_census_p13.py').read()
mod = types.ModuleType('census')
mod.__dict__['__name__'] = 'census_lib'
exec(compile(src.replace("if __name__ == '__main__':", "if False:"), 'census', 'exec'), mod.__dict__)

SCR = '/home/hatch/workspace/_doa4p2-scratch/p13/'
OUT = SCR + 'texrecord_census.json'
HEADS = ['chrtwo-pkg%02d' % i for i in range(4, 46)]
FAM_BODIES = (['chrone-pkg%02d' % i for i in range(0, 6)]
              + ['chrone-pkg10', 'chrone-pkg13', 'chrtwo-pkg46', 'chrtwo-pkg49', 'chrthree-pkg01']
              + ['chrone-pkg17', 'chrone-pkg18', 'chrone-pkg20', 'chrone-pkg21', 'chrone-pkg22', 'chrthree-pkg18', 'chrthree-pkg19']
              + ['chrtwo-pkg%02d' % i for i in range(50, 56)] + ['chrthree-pkg%02d' % i for i in range(2, 8)]
              + ['chrone-pkg14', 'chrone-pkg15', 'chrone-pkg16']
              + ['chrone-pkg%02d' % i for i in range(6, 10)] + ['chrtwo-pkg00']
              + ['chrthree-pkg%02d' % i for i in range(29, 32)])
WANT = HEADS + FAM_BODIES

out = json.load(open(OUT)) if os.path.exists(OUT) else {}
for pkg in WANT:
    if pkg in out and all(t.get('l2') for t in out[pkg].get('tex', [])):
        print(pkg, 'cached', flush=True); continue
    afs = pkg.split('-')[0]
    xp = None
    for line in open(mod.INV % afs):
        r = line.split(',')
        if r[0] == pkg:
            xp = int(r[1], 16); break
    out[pkg] = mod.census_pkg(afs, xp)
    json.dump(out, open(OUT, 'w'), indent=1)
    print(pkg, 'tex', len(out[pkg].get('tex', [])),
          'l2', sum(1 for t in out[pkg].get('tex', []) if t.get('l2')), flush=True)
print('DONE', len(out))
