#!/bin/bash
# usage: run_batch.sh START COUNT
set -e
cd /var/tmp/w7e
python3 ~/workspace/_w7e-stage/tools/fetch_convert.py "$1" "$2"
if [ -s /var/tmp/w7e/jobs.json ] && [ "$(python3 -c "import json;print(len(json.load(open('/var/tmp/w7e/jobs.json'))))")" != "0" ]; then
  xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender -b --python ~/workspace/_w7e-stage/tools/blender_batch.py -- /var/tmp/w7e/jobs.json 2>&1 | grep -E "BATCHDONE|BATCHFAIL" || true
fi
python3 - << 'PY'
import json, os, hashlib, shutil, sys
sys.path.insert(0, '/home/hatch/workspace/_w7e-stage/tools')
from validate_glb import validate
man = json.load(open('/var/tmp/w7e/manifest.json'))
jobs = json.load(open('/var/tmp/w7e/jobs.json'))
for job in jobs:
    idx = job['idx']; key = str(idx); glb = job['glb']
    if os.path.exists(glb):
        try:
            v = validate(glb)
            partial = bool(man[key].get('missing_tex_indices'))
            if partial:
                assert v['meshes'] >= 1 and v['tris'] > 0, v
            else:
                assert v['meshes'] >= 1 and v['images'] >= 1 and v['materials_textured'] == v['materials'], v
            dest = f'/home/hatch/workspace/_w7e-stage/glb/pack{idx:04d}-costume.glb'
            shutil.move(glb, dest)
            man[key].update({'stage': 'glb_ok_partial' if partial else 'glb_ok', 'glb': v, 'glb_sha256': hashlib.sha256(open(dest,'rb').read()).hexdigest(), 'glb_file': dest})
            print('GLBOK', idx, v)
        except Exception as e:
            man[key].update({'stage': 'glb_invalid', 'error': repr(e)}); print('GLBINVALID', idx, e)
    else:
        man[key].update({'stage': 'glb_missing'}); print('GLBMISSING', idx)
    json.dump(man, open('/var/tmp/w7e/manifest.json', 'w'), indent=1)
    shutil.rmtree(os.path.dirname(job['obj']), ignore_errors=True)
print('done batch; total glb_ok =', sum(1 for v in man.values() if v.get('stage') in ('glb_ok','glb_ok_partial')))
PY
