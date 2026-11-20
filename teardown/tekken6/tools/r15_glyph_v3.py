#!/usr/bin/env python3
"""Round 15: regenerate the 18 moveset JSONs as additive v3 files with the
COMPLETED glyph map (round15-evidence/JOB1-GLYPH-TAIL.md).

Map additions over round 14: E006=u; the hold-direction ring E008-E00F
(D/B, D, D/F, B, F, U/B[unused in corpus], U, U/F) mirroring the tap ring
E000-E007 in ring order (E00C revised from round 14's contextual label to
its glyph identity F); buttons E01A=2+3, E01D=1+4, E01F=1+2+4,
E021=1+3+4, E022=2+3+4, E023=1+2+3+4 (the button block E015-E023 is
exactly the 15 non-empty subsets of {1,2,3,4}, enumerated by highest
button then combination order).

Decode rendering (same fusion rule as round 14's v2): a direction glyph
immediately followed by a button glyph fuses with '+'; everything else
is comma-separated. E00C renders 'F' after E004 (the f,F dash) and '~F'
elsewhere (the slide/hold transition, round 14's '~f' case).
v2 files are read, never written; all non-notation fields are carried
byte-identical (verified by the caller).
"""
import json, glob, os, sys

GLYPH_MAP = {
    'U+E000': 'd/b', 'U+E001': 'd', 'U+E002': 'd/f', 'U+E003': 'b',
    'U+E004': 'f', 'U+E005': 'u/b', 'U+E006': 'u', 'U+E007': 'u/f',
    'U+E008': 'D/B', 'U+E009': 'D', 'U+E00A': 'D/F', 'U+E00B': 'B',
    'U+E00C': 'F', 'U+E00D': 'U/B', 'U+E00E': 'U', 'U+E00F': 'U/F',
    'U+E015': '1', 'U+E016': '2', 'U+E017': '1+2', 'U+E018': '3',
    'U+E019': '1+3', 'U+E01A': '2+3', 'U+E01B': '1+2+3', 'U+E01C': '4',
    'U+E01D': '1+4', 'U+E01E': '2+4', 'U+E01F': '1+2+4',
    'U+E020': '3+4', 'U+E021': '1+3+4', 'U+E022': '2+3+4',
    'U+E023': '1+2+3+4',
}
DIRECTIONS = {f'U+E{i:03X}' for i in range(0x000, 0x010)}

def decode(glyphs):
    toks = []
    for i, g in enumerate(glyphs):
        if g == 'U+E00C' and not (i > 0 and glyphs[i-1] == 'U+E004'):
            toks.append('~F')
        else:
            toks.append(GLYPH_MAP[g])
    out = []
    for i, g in enumerate(glyphs):
        if i and glyphs[i-1] in DIRECTIONS and g not in DIRECTIONS:
            out.append('+')
        elif i:
            out.append(',')
        out.append(toks[i])
    return ''.join(out)

def main(src_glob,):
    files = sorted(glob.glob(src_glob))
    assert len(files) == 18, files
    tot = withnot = complete = 0
    for f in files:
        d = json.load(open(f))
        assert 'round14_notation' in d
        d['round15_notation'] = {
            'source': 'game-font PUA glyphs (U+E000-U+E023) in per-move name records',
            'glyph_map': GLYPH_MAP,
            'special': {
                'U+E00C': 'hold-form of f: rendered "F" when following U+E004 (the f,F dash), "~F" otherwise (slide/hold transition)',
                'U+E00D': 'U/B (hold u/b) by ring position; never occurs in the 18 files\' records (0 occurrences in the v2 census)',
            },
            'unproven_codepoints': 'none - the map is complete over every codepoint occurring in the corpus',
            'evidence': 'tools/round15-evidence/JOB1-GLYPH-TAIL.md (supersedes the round-14 tail in tools/round14-evidence/JOB3-GLYPH-MAP.md)',
        }
        del d['round14_notation']
        for m in d['moves']:
            tot += 1
            g = m.get('command_glyphs') or []
            if g:
                withnot += 1
                assert all(x in GLYPH_MAP for x in g), (f, m['name'], g)
                m['command_decoded'] = decode(g)
                m['command_complete'] = True
                complete += 1
        out = f.replace('-moveset-v2.json', '-moveset-v3.json')
        with open(out, 'w') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
        print('wrote', out)
    print(f'moves {tot}, with notation {withnot}, fully decoded {complete}')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'teardown/tekken6/movesets/*-moveset-v2.json')
