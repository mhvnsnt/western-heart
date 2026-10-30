#!/usr/bin/env python3
"""Join a T7 motbin JSON (tools/extract/t7/t7_motbin_to_json.py output) with the
character's <code>rotsm.arc animation bank, so every move resolves to the real
T7 clip it plays.

Bank rule (validated on King, see docs/BUILD-LOG.md):
  anim_id & 0xC000 == 0x4000 -> <code>rotsm.arc, first MOTA block, index anim_id & 0x3FFF
  anim_id & 0xC000 == 0x8000 -> shared common bank (not in the extracted data; gap)
  anim_id & 0xC000 == 0x0000 -> per-character inline/story bank (gap)

usage: t7_clipmap.py <code>mot.json <code>rotsm.arc out.json
Exits non-zero if any 0x4000-bank move fails to decode.
"""
import json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import Anim64, mota_anims

BANKS = {0x4000: 'rotsm', 0x8000: 'common', 0x0000: 'inline'}


def clipmap(motjson, arc):
    mv = json.load(open(motjson))['moves']
    d = open(arc, 'rb').read()
    m0 = re.search(b'MOTA', d).start()
    offs = mota_anims(d, m0)
    rows, err = [], 0
    for m in mv:
        aid = m['anim_id']
        bank = BANKS.get(aid & 0xC000, 'other')
        r = {'move': m['name'], 'anim': m['anim'], 'bank': bank,
             'clip': aid & 0x3FFF, 'damage': m['damage'], 'active': m['active_frames']}
        if bank == 'rotsm':
            i = aid & 0x3FFF
            try:
                o = m0 + offs[i]
                t = d[o + 1]
                if t == 0x64:
                    a = Anim64(d, o)  # full decode validated by t7_anim64 validate
                    r.update(fmt='0x64', frames=a.length)
                elif t == 0xC8:
                    r.update(fmt='0xC8', frames=struct.unpack_from('>I', d, o + 4)[0])
                else:
                    raise ValueError('type %#x' % t)
            except Exception as e:  # noqa: BLE001
                r['error'] = str(e); err += 1
        rows.append(r)
    atk = [r for r in rows if r['damage']]
    summ = {b: {'moves': sum(r['bank'] == b for r in rows),
                'attacks': sum(r['bank'] == b for r in atk)} for b in set(r['bank'] for r in rows)}
    return {'schema': 'wh-t7-clipmap/1', 'motbin': os.path.basename(motjson),
            'arc': os.path.basename(arc), 'clips_in_bank': len(offs),
            'summary': summ, 'decode_errors': err, 'moves': rows}, err


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    out, err = clipmap(sys.argv[1], sys.argv[2])
    json.dump(out, open(sys.argv[3], 'w'), indent=1)
    print(json.dumps(out['summary']), 'decode_errors', err)
    sys.exit(1 if err else 0)
