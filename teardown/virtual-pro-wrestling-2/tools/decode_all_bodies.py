import json, os
from vpw2_moveset import MOVESET_DIR
from vpw2_bodyparts import body_models, head_triple, SLOT_LABELS
E=MOVESET_DIR.parent
roster=json.loads((E/'roster'/'roster.json').read_text())
cost=json.loads((E/'roster'/'costumes.json').read_text())
cost_by_idx={x['costume_index']:x for x in cost['costumes']}
man=json.loads((E/'models'/'manifest.json').read_text())
on_disk={int(x['file_id'],16) for x in man['models']}
out={"source":"VPW2 body-part selection table (ROM 0x435AC + pointer table 0x438D0); head grid 0x15D5",
     "slot_labels":SLOT_LABELS,
     "note":"base body (no-attire) per costume slot 0; attire-variant geometry (groups 6+) still open",
     "wrestlers":[]}
missing=0; total=0
for w in roster['wrestlers']:
    cs=cost_by_idx.get(w['appearance_index'])
    if cs is None:
        print("no costume for", w['id4']); continue
    bt=cs['body_type']
    body=body_models(bt)
    face,neck,head=head_triple(bt, cs['head_shape'], cs['hair_type'])
    ids=list(body)+[face,neck,head]
    total+=len(ids)
    miss=[f'{i:04x}' for i in ids if i not in on_disk]
    missing+=len(miss)
    out['wrestlers'].append({
        "wrestler_id4":w['id4'],"name":w['name'],"slot":w['slot'],
        "appearance_index":w['appearance_index'],
        "body_type":bt,"body_type_name":cs['body_type_name'],
        "head_shape":cs['head_shape'],"hair_type":cs['hair_type'],
        "body_group_base":f"{body[0]:04x}",
        "body_models":{SLOT_LABELS[i]:f"{f:04x}" for i,f in enumerate(body)},
        "face_fid":f"{face:04x}","neck_fid":f"{neck:04x}","head_fid":f"{head:04x}",
        "missing_files":miss,
    })
json.dump(out,open('decoded_bodies.json','w'),indent=1,ensure_ascii=False)
print(f"wrote decoded_bodies.json: {len(out['wrestlers'])} wrestlers, {missing}/{total} model files missing from manifest")
# verify head triples against hidden25 (23 entries)
h=json.load(open(E/'roster'/'hidden25.json'))
by={w['wrestler_id4']:w for w in out['wrestlers']}
bad=0
for hw in h['wrestlers']:
    if 'head_models' not in hw: continue
    b=by[hw['vpw2_id4']]
    if b['face_fid'].upper()!=hw['head_models']['face_fid']:
        bad+=1; print("HEAD MISMATCH", hw['real_name'], b['face_fid'], hw['head_models']['face_fid'])
print(f"hidden25 head check: {23-bad}/23 match")
