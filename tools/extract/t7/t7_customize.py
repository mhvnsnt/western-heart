#!/usr/bin/env python3
"""Tekken 7 customization tables -> JSON (Creation Suite structure source).

Input: the tkdata `list/` folder unpacked by t7_tkdata.py from the owner's
own Steam copy. Output goes to the PRIVATE repo (mhvnsnt/game-reverse-
engineering, tekken7/customization/) because it is Bandai Namco game data;
this public repo keeps only this parser and the derived slot STRUCTURE.

All tables share one container: u64 string_table_offset, u64 record_count,
fixed-size records, then a NUL-terminated string table. Record size is
(string_table_offset - 16) / record_count, which is how each layout below
was derived (no hand-written values):

  customize_item_data.bin   64 B  +0 u32 item_no | +8 u64 mesh str | +0x11 u8 slot code
                                  +0x18 u64 text key | +0x20 u8 group | +0x28 5 x u8 flags
                                  +0x38 u64 aux str
  customize_palette_color   3 B   RGB888 swatches (the in-game colour grid)
  customize_color_rules    24 B   +0 u32 key | +8 u8 kind | +0xc f32 lo | +0x10 f32 hi | +0x14 u16 mask
  customize_chara_list     24 B   +0 u8 index | +1 u8 flag | +8 u64 code | +0x10 u64 name
  customize_preset_table   408 B  +0 u64 preset name (rest kept as hex)

Slot-code names come from the mesh-name token each code carries in the
data (code 9 -> 2,103 `*_bdu_*` meshes = upper body, etc.); see
packages/creation-suite/src/t7layout.js for the table.

usage: t7_customize.py <tkdata/list dir> <out dir> [<pakchunk0 models dir>]
"""
import collections, json, os, re, struct, sys

def table(path):
    b = open(path, 'rb').read()
    st, n = struct.unpack_from('<QQ', b, 0)
    size = (st - 16) // n if n else 0
    def s(o):
        if o < st or o >= len(b): return None
        return b[o:b.index(b'\0', o)].decode('utf-8', 'replace')
    return b, n, size, s

def items(d):
    b, n, size, s = table(os.path.join(d, 'customize_item_data.bin'))
    assert size == 64, size
    out = []
    for i in range(n):
        o = 16 + 64 * i
        out.append(dict(
            item_no=struct.unpack_from('<I', b, o)[0],
            mesh=s(struct.unpack_from('<Q', b, o + 8)[0]),
            slot_code=b[o + 0x11],
            text_key=s(struct.unpack_from('<Q', b, o + 0x18)[0]),
            group=b[o + 0x20], flags=list(b[o + 0x28:o + 0x2d]),
            aux=s(struct.unpack_from('<Q', b, o + 0x38)[0])))
    return out

def palette(d):
    b, n, size, s = table(os.path.join(d, 'customize_palette_color.bin'))
    return ['#%02x%02x%02x' % tuple(b[16 + 3 * i:19 + 3 * i]) for i in range(n)]

def color_rules(d):
    b, n, size, s = table(os.path.join(d, 'customize_color_rules.bin'))
    out = []
    for i in range(n):
        o = 16 + size * i
        out.append(dict(key=struct.unpack_from('<I', b, o)[0], kind=b[o + 8],
                        lo=round(struct.unpack_from('<f', b, o + 12)[0], 4),
                        hi=round(struct.unpack_from('<f', b, o + 16)[0], 4),
                        mask=struct.unpack_from('<H', b, o + 20)[0]))
    return out

def chara_list(d):
    b, n, size, s = table(os.path.join(d, 'customize_chara_list.bin'))
    return [dict(index=b[16 + size * i], flag=b[17 + size * i],
                 code=s(struct.unpack_from('<Q', b, 24 + size * i)[0]),
                 name=s(struct.unpack_from('<Q', b, 32 + size * i)[0])) for i in range(n)]

def presets(d):
    p = os.path.join(d, 'customize_preset_table_cs_s3.bin')
    if not os.path.exists(p): return []
    b, n, size, s = table(p)
    return [s(struct.unpack_from('<Q', b, 16 + size * i)[0]) for i in range(n)]

TOKEN = re.compile(r'^(?:SK_CH_)?([a-z0-9]{3})_([a-z]+)', re.I)

def part_catalog(models_dir, slot_by_token):
    """Rigged base-costume parts (SK_CH_<chr>_<token>...glb) -> registry-entry catalog.
    `glb` is the path a PRIVATE build copies them to (game/assets/private/t7/...)."""
    parts = []
    for root, _, files in os.walk(models_dir):
        for f in sorted(files):
            if not f.endswith('.glb'): continue
            m = TOKEN.match(f)
            if not m: continue
            chr_, tok = m.group(1).lower(), m.group(2).lower()
            tok = {'face': 'fac'}.get(tok, tok)
            code = slot_by_token.get(tok)
            rel = os.path.relpath(os.path.join(root, f), models_dir)
            parts.append(dict(
                id=f't7:{f[:-4]}', name=f[:-4], source_game='tekken7', char_id=chr_,
                slot=tok, t7_slot_code=code, part_class='mesh_part', rig_swap=True,
                file=f'game/assets/private/t7/{rel}', glb=f'game/assets/private/t7/{rel}',
                conversion=dict(status='converted', tool='tools/extract/t7/convert.py'),
                private=True))
    return parts

def main():
    d, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    it = items(d)
    hist = collections.defaultdict(collections.Counter)
    for x in it:
        m = TOKEN.match(x['mesh'] or '')
        hist[x['slot_code']][m.group(2).lower() if m else '?'] += 1
    slots = {c: dict(count=sum(h.values()), tokens=dict(h.most_common(6))) for c, h in sorted(hist.items())}
    slot_by_token = {}
    for c, h in hist.items():
        for tok, k in h.items():
            if tok != '?' and k >= 10 and tok not in slot_by_token: slot_by_token[tok] = c
    per_char = collections.Counter((TOKEN.match(x['mesh'] or '') or [None, '?'])[1].lower() for x in it)
    summary = dict(source='Tekken 7 (Steam app 389730) tkdata list/', items=len(it), slots=slots,
                   slot_by_token=slot_by_token, items_per_character=dict(per_char.most_common()))
    w = lambda name, obj: json.dump(obj, open(os.path.join(out, name), 'w'), ensure_ascii=False, indent=1)
    w('items.json', it); w('palette.json', palette(d)); w('color_rules.json', color_rules(d))
    w('chara_list.json', chara_list(d)); w('presets.json', presets(d)); w('summary.json', summary)
    if len(sys.argv) > 3:
        parts = part_catalog(sys.argv[3], slot_by_token)
        w('CATALOG.json', dict(_meta=dict(catalog='Tekken 7 rigged base-costume parts (PRIVATE build only)',
                                         count=len(parts), consumer='packages/creation-suite/src/catalogs.js'),
                               parts=parts))
    print(json.dumps({k: summary[k] for k in ('items', 'slot_by_token')}))

if __name__ == '__main__':
    main()
