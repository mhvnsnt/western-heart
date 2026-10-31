"""Which T7 moves play 0xC8 clips (bakeable now through tools/anim/t7_c8_stance_bake.py, the community 0xC8 path)
and which play 0x64 clips (waiting on the joint frame: docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md).
Read-only; reads the raw files from the private GRE checkout and copies nothing in.
usage: python3 tools/anim/t7_clip_formats.py <GRE>/teardown/tekken7-steam/tkdata/mothead <code> [--list-c8]
Bank rule (anim_id & 0xC000): 0x4000 -> mask/<code>rotsm.arc, 0x8000 -> mask/common.arc, 0x0000 -> bin/<code>mot.bin."""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import mota_anims

BANK = {0x4000: 'rotsm', 0x8000: 'common', 0x0000: 'motbin'}


def main():
    if len(sys.argv) < 3: raise SystemExit(__doc__)
    G, code = sys.argv[1].rstrip('/') + '/', sys.argv[2]
    paths = {0x4000: G + 'mask/%srotsm.arc' % code, 0x8000: G + 'mask/common.arc', 0x0000: G + 'bin/%smot.bin' % code}
    banks = {}

    def fmt(aid):
        sel = aid & 0xC000
        if sel not in paths: return '?'
        if sel not in banks:
            d = open(paths[sel], 'rb').read(); m0 = re.search(b'MOTA', d).start()
            banks[sel] = (d, m0, mota_anims(d, m0))
        d, m0, offs = banks[sel]; i = aid & 0x3FFF
        if i >= len(offs): return 'out-of-range'
        o = m0 + offs[i]; t = d[o + 1] if d[o] == 0 else d[o]
        return {0xC8: '0xC8', 0x64: '0x64'}.get(t, hex(t))

    moves = json.load(open(G + 'json/%smot.json' % code))['moves']
    count, clips = collections.Counter(), collections.defaultdict(list)
    for m in moves:
        f, bk = fmt(m['anim_id']), BANK.get(m['anim_id'] & 0xC000, '?')
        count[('attack' if m.get('damage') else 'other', bk, f)] += 1
        clips[(bk, m['anim_id'] & 0x3FFF, m['anim'], f)].append(m['name'])
    for k, v in sorted(count.items()): print('%-6s %-6s %-5s %5d moves' % (*k, v))
    uniq = collections.Counter((bk, f) for (bk, _, _, f) in clips)
    for k, v in sorted(uniq.items()): print('unique clips %-6s %-5s %5d' % (*k, v))
    if '--list-c8' in sys.argv:
        for (bk, i, anim, f), names in sorted(clips.items()):
            if f == '0xC8': print('0xC8 %-6s %4d %-34s %s' % (bk, i, anim, ', '.join(names[:6])))


if __name__ == '__main__':
    main()
