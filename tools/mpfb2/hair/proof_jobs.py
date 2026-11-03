import json
T=['super-heavyweight','powerhouse','showman','technician','highflyer','luchador','powerhouse-w','athletic-w','striker-w']
R='/workspace/work/renders'; J='/workspace/work/hairpipe'
fem=lambda t:t.endswith('-w')
jobs=[dict(template=t,parts=[],views=[{'name':'front','kind':'body','yaw':0},{'name':'34','kind':'body','yaw':35}],out_prefix=f'{R}/bodies/{t}',res=1024) for t in T]
json.dump(jobs,open(f'{J}/jobs_bodies.json','w'))
jobs=[]
for t in T:
    hair='mh-hair-long01' if fem(t) else 'mh-hair-short02'
    face=['mh-brows-001','mh-lashes-01']+([] if fem(t) else ['wh-beard-goatee'])
    for nm,m in [('heavy',{'b_weight+':1.0}),('lean-toned',{'b_weight-':1.0,'b_tone+':1.0}),('broad',{'b_shoulder_w+':1.0,'b_chest+':1.0,'b_neck+':1.0,'b_traps+':1.0})]:
        jobs.append(dict(template=t,parts=[hair]+face,morphs=m,views=[{'name':'front','kind':'body','yaw':0},{'name':'34','kind':'body','yaw':35}],out_prefix=f'{R}/morphs/{t}_{nm}',res=768))
    for nm,m in [('face-neutral',{}),('face-extreme',{'f_head_w+':1.0,'f_brow_h+':1.0,'b_head_size+':1.0,'f_square+':1.0})]:
        jobs.append(dict(template=t,parts=[hair]+face,morphs=m,views=[{'name':'front','kind':'head','yaw':0},{'name':'34','kind':'head','yaw':35}],out_prefix=f'{R}/morphs/{t}_{nm}',res=768))
json.dump(jobs,open(f'{J}/jobs_morphs.json','w'))
A=json.load(open(f'{J}/pipe/assets.json'))
LONG=('mh-hair-long01','mh-hair-bob01','mh-hair-bob02','mh-hair-braid01','mh-hair-ponytail01')
jobs=[]
for a in A:
    t='striker-w' if a['id'] in LONG else 'technician'
    kind='bust' if a['kind']=='hair' else 'head'
    jobs.append(dict(template=t,parts=[a['id']],views=[{'name':'front','kind':kind,'yaw':0},{'name':'34','kind':kind,'yaw':145 if a['kind']=='hair' else 35}],out_prefix=f'{R}/parts/{a["id"]}_{t}',res=640))
json.dump(jobs,open(f'{J}/jobs_parts.json','w'))
