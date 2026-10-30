"""Round 7 JOB 3: full verbatim decode of the 18 Tekken 6 PSP COM moveset
containers (decoded76 idx58-75, adler-exact clean plaintexts).
Per-character isolation: one JSON per fighter, named by the in-file
character string at offset 624 (round-6 HIGH-confidence evidence).
Verbatim only: header words, the 32-slot pointer table at 368 with
section spans, every ASCII string >=4 and UTF-8 Japanese run with its
file offset, per-move-name record hex (name offset -> next name offset),
MOTA chunk headers and the four 20B MOTA tail records as hex.
Tekken-input conversion is NAME-DERIVED ONLY (token substitution table
included in each file) and is logged as such; no command bytes are
claimed decoded beyond the verbatim record hex.
Inputs: ~/workspace/_t6r4-work/decoded76/ (retained workdir)."""
import struct, re, json, hashlib, os
SRC='/home/hatch/workspace/_t6r4-work/decoded76/'
OUT='/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/movesets/'
TOKENS={'Left Right':'LP RP','Left':'LP','Right':'RP','Kick':'RK','Punch':'LP'}
def tekken_input_from_name(name):
    # logged name-token conversion (NOT byte-decoded command data)
    s=name
    for k in ('Left Right','Left','Right'):
        s=s.replace(k, {'Left Right':'1,2','Left':'1','Right':'2'}[k])
    return s
def slug(s):
    return re.sub(r'[^A-Za-z0-9]+','-',s).strip('-').lower()
inv=json.load(open('/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools/round6-evidence/r6_com_inventory.json'))['com_files']
summary=[]
for f in inv:
    d=open(SRC+f['file'],'rb').read()
    assert hashlib.sha256(d).hexdigest()==f['sha256'], f['file']
    ver, magic, zero, count = struct.unpack_from('>I4sII', d, 0) if False else (struct.unpack_from('>I',d,0)[0], d[4:8], struct.unpack_from('<I',d,8)[0], struct.unpack_from('<I',d,12)[0])
    ptrs=[]
    for i in range(32):
        a,b=struct.unpack_from('<II', d, 368+i*8)
        ptrs.append({'slot':i,'word_a':a,'offset':b})
    live=[p for p in ptrs if p['offset']]
    offs=sorted(set(p['offset'] for p in live))
    for p in ptrs:
        nxt=[o for o in offs if o>p['offset']]
        p['section_len']=(nxt[0]-p['offset']) if nxt else (len(d)-p['offset'] if p['offset'] else 0)
    strs=[{'offset':m.start(),'text':m.group().decode('ascii')} for m in re.finditer(rb'[\x20-\x7e]{4,}', d)]
    jp=[{'offset':m.start(),'text':m.group().decode('utf-8')} for m in re.finditer(rb'(?:[\xe3][\x80-\xbf][\x80-\xbf]|[\xe4-\xe9][\x80-\xbf][\x80-\xbf]){2,}', d)]
    # move names: ASCII strings in the record region (>=624, before first large pointer target beyond the name table)
    # name region: from just after the build-date string to the first
    # structured (non-string-table) section = min offset among slots 2..31
    date_end = max([s['offset']+len(s['text']) for s in strs if 'JST' in s['text']], default=624)
    struct_offs=[ptrs[i]['offset'] for i in range(2,32) if ptrs[i]['offset']>624]
    name_region_end = min(struct_offs) if struct_offs else len(d)
    names=[s for s in strs if date_end<=s['offset']<name_region_end]
    names=[s for s in names if re.search(r'[A-Za-z]{3}', s['text'])]
    moves=[]
    for i,s in enumerate(names):
        end=names[i+1]['offset'] if i+1<len(names) else name_region_end
        rec=d[s['offset']:end]
        moves.append({'name':s['text'],'name_offset':s['offset'],'record_len':len(rec),
                      'record_hex':rec.hex(),'input_from_name':tekken_input_from_name(s['text'])})
    mota_offs=[m.start() for m in re.finditer(rb'MOTA', d)]
    mota=[]
    for o in mota_offs:
        chunk=d[o:o+64]
        mota.append({'offset':o,'header_hex':chunk.hex(),'words_le':list(struct.unpack_from('<8I',chunk,0)) if len(chunk)>=32 else list(struct.unpack_from('<5I',chunk,0))})
    tail=[{'offset':len(d)-80+i*20,'hex':d[len(d)-80+i*20:len(d)-60+i*20].hex()} for i in range(4)]
    doc={'source_game':'Tekken 6 (PSP)','format':'COM moveset container (round 6/7 decode)',
      'character':f['character_string'],'character_evidence':'in-file string at offset 624 of its own plaintext + author string + build timestamp (round 6, HIGH confidence)',
      'gzip_idx':f['idx'],'data401_entry':f['entry'],'file':f['file'],'size':len(d),'sha256':f['sha256'],
      'header':{'version_be_u32':ver,'magic':magic.decode('latin1').replace('\x00','\\0'),'word_at_8_le':zero,'count_word_at_12_le':count,
                'count_word_note':'per-file count 7-16 (sum 176); exact referent UNPROVEN (round 6) - not used as an asset census'},
      'pointer_table_at_368':ptrs,
      'name_region':{'start':624,'end':name_region_end,'note':'move-name record region: English move names first, then localized name/description variants (all byte-carried strings, verbatim with offsets); records span name offset -> next name offset'},
      'author_string':f['author_string'],
      'moves':moves,'move_count_from_name_strings':len(moves),
      'tekken_input_conversion':{'method':'name-token substitution ONLY (Left=1/LP, Right=2/RP, Left Right=1,2); logged conversion of the English move-name strings, NOT a decode of the binary command records - the verbatim record hex is the byte truth','tokens':{'Left':'1 (LP)','Right':'2 (RP)','Left Right':'1,2'}},
      'all_ascii_strings_ge4':strs,'utf8_japanese_runs':jp,
      'mota':{'offsets':mota_offs,'chunks':mota,'tail_records_20b':tail,'tail_note':'four 20B MOTA records end exactly at EOF in 18/18 files (round 6)'}}
    outname=f"t6psp-{slug(f['character_string'])}-moveset.json"
    json.dump(doc, open(OUT+outname,'w'), indent=1, ensure_ascii=False)
    summary.append({'character':f['character_string'],'file':outname,'moves':len(moves),'strings':len(strs),'mota':len(mota_offs),'count_word':count,'size':len(d)})
    print(outname, len(moves),'moves', len(strs),'strings')
json.dump(summary, open(OUT+'INDEX.json','w'), indent=1)
print("TOTAL moves:", sum(s['moves'] for s in summary))
