#!/usr/bin/env python3
"""Join a T7 motbin JSON (tools/extract/t7/t7_motbin_to_json.py output) with the
character's <code>rotsm.arc animation bank, so every move resolves to the real
T7 clip it plays.

Bank rule (validated on King, see docs/BUILD-LOG.md):
  anim_id & 0xC000 == 0x4000 -> <code>rotsm.arc, first MOTA block, index anim_id & 0x3FFF
  anim_id & 0xC000 == 0x8000 -> shared common bank, common.arc (held in the GRE
    tree at teardown/tekken7-steam/tkdata/mothead/mask/common.arc; first MOTA
    block, index anim_id & 0x3FFF — join tested on King, see
    docs/proof/t7-clipmap-king-common-20261030.md)
  anim_id & 0xC000 == 0x0000 -> per-character inline/story bank (gap)

usage: t7_clipmap.py <code>mot.json <code>rotsm.arc out.json [common.arc]
Exits non-zero if any 0x4000- or 0x8000-bank move fails to decode.
Without common.arc, 0x8000 rows are listed with their bank and clip index only.
"""
import json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import Anim64, mota_anims

BANKS = {0x4000: 'rotsm', 0x8000: 'common', 0x0000: 'inline'}


def _decode_row(d, m0, offs, i):
    o = m0 + offs[i]
    t = d[o + 1]
    if t == 0x64:
        a = Anim64(d, o)  # full decode validated by t7_anim64 validate
        return {'fmt': '0x64', 'frames': a.length}
    if t == 0xC8:
        return {'fmt': '0xC8', 'frames': struct.unpack_from('>I', d, o + 4)[0]}
    raise ValueError('type %#x' % t)


def clipmap(motjson, arc, common_arc=None):
    mv = json.load(open(motjson))['moves']
    d = open(arc, 'rb').read()
    m0 = re.search(b'MOTA', d).start()
    offs = mota_anims(d, m0)
    cd, cm0, coffs = None, None, None
    if common_arc:
        cd = open(common_arc, 'rb').read()
        cm0 = re.search(b'MOTA', cd).start()
        coffs = mota_anims(cd, cm0)
    rows, err = [], 0
    for m in mv:
        aid = m['anim_id']
        bank = BANKS.get(aid & 0xC000, 'other')
        r = {'move': m['name'], 'anim': m['anim'], 'bank': bank,
             'clip': aid & 0x3FFF, 'damage': m['damage'], 'active': m['active_frames']}
        if bank == 'rotsm':
            try:
                r.update(_decode_row(d, m0, offs, aid & 0x3FFF))
            except Exception as e:  # noqa: BLE001
                r['error'] = str(e); err += 1
        elif bank == 'common' and cd is not None:
            try:
                r.update(_decode_row(cd, cm0, coffs, aid & 0x3FFF))
            except Exception as e:  # noqa: BLE001
                r['error'] = str(e); err += 1
        rows.append(r)
    atk = [r for r in rows if r['damage']]
    summ = {b: {'moves': sum(r['bank'] == b for r in rows),
                'attacks': sum(r['bank'] == b for r in atk)} for b in set(r['bank'] for r in rows)}
    out = {'schema': 'wh-t7-clipmap/1', 'motbin': os.path.basename(motjson),
           'arc': os.path.basename(arc), 'clips_in_bank': len(offs),
           'summary': summ, 'decode_errors': err, 'moves': rows}
    if common_arc:
        out['common_arc'] = os.path.basename(common_arc)
        out['clips_in_common_bank'] = len(coffs)
    return out, err


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5):
        sys.exit(__doc__)
    out, err = clipmap(sys.argv[1], sys.argv[2],
                       sys.argv[4] if len(sys.argv) == 5 else None)
    json.dump(out, open(sys.argv[3], 'w'), indent=1)
    print(json.dumps(out['summary']), 'decode_errors', err)
    sys.exit(1 if err else 0)
