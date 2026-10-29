"""Compact, integration-ready move table from a TekkenMovesetExtractor-format (T8) JSON.
Usage: python3 summarize.py <in.json[.gz]> <out.summary.json>"""
import json,sys,gzip
p=sys.argv[1]; d=json.load((gzip.open if p.endswith('.gz') else open)(p,'rt'))
keys=['name','anim_name','hitlevel','anim_max_len','first_active_frame','last_active_frame','airborne_start','airborne_end','transition','cancel_idx','hit_condition_idx','hitbox_location']
moves=[{'idx':i,**{k:m.get(k) for k in keys}} for i,m in enumerate(d['moves'])]
out={'source':'Kaiutzi21/Tekken8Movesets (CC BY-NC 4.0)','character':d['character_name'],'tekken_character_name':d['tekken_character_name'],'export_version':d['export_version'],'counts':{k:len(v) for k,v in d.items() if isinstance(v,list)},'throws':len(d.get('throws',[])),'moves':moves}
json.dump(out,open(sys.argv[2],'w'),separators=(',',':'))
print(sys.argv[2],len(moves))
