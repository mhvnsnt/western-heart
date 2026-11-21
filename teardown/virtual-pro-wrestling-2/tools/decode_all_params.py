import json, os, collections
from vpw2_moveset import MOVESET_DIR, RAW_DIR
from vpw2_params import unpack_params
from vpw2_params_decode import decode_params, style_from_params
man=json.loads((MOVESET_DIR/'params_moveset_manifest.json').read_text())
dec=json.load(open('decoded_movesets.json'))
style={w['wrestler_id4']:w['style'] for w in dec['wrestlers']}
roster=json.loads((MOVESET_DIR.parent/'roster'/'roster.json').read_text())
by_id4={w['id4']:w for w in roster['wrestlers']}
out={"source":"VPW2 params decoder (ROM 0x80006608, 50-case switch)","wrestlers":[]}
ranges=[collections.Counter() for _ in range(50)]
bad=0
for p in man['pairs']:
    if p['kind']!='params': continue
    data=(RAW_DIR/f"{p['file_id']}.bin").read_bytes()
    temp,raw=unpack_params(data)
    params=decode_params(temp)
    s=style_from_params(params)
    if s!=style[p['wrestler_id4']]:
        bad+=1; print("STYLE MISMATCH", p['wrestler_id4'], s, style[p['wrestler_id4']])
    for i,v in enumerate(params): ranges[i][v]+=1
    w=by_id4.get(p['wrestler_id4'],{})
    out['wrestlers'].append({
        "wrestler_id4":p['wrestler_id4'],"name":w.get('name'),
        "slot":w.get('slot'),"params_file_id":p['file_id'],
        "style":s,"params":params,
        "raw_fields":raw,
        "temp_hex":temp.hex(),
    })
json.dump(out,open('decoded_params.json','w'),indent=1,ensure_ascii=False)
print(f"style check: {98-bad}/98 match moveset style")
print("param value ranges (distinct values):")
for i,c in enumerate(ranges):
    vals=sorted(c)
    print(f"  p{i:2d}: distinct {len(vals):2d} min {vals[0]:5d} max {vals[-1]:5d}  {vals[:12]}{'...' if len(vals)>12 else ''}")
