#!/usr/bin/env python3
"""W6 probe: do menu.mpq per-wrestler profile blocks pair special-move
NAMES with motion IDs? Dump the bytes around several specials' offsets
(Rock Bottom @ 0x5b6ef etc.) and look for numeric IDs nearby."""
import sys, struct, json

MPQ = '/data/wmxix/extracted/menu/menu.mpq'


def u16(b, o):
    return struct.unpack('>H', b[o:o + 2])[0]


def u32(b, o):
    return struct.unpack('>I', b[o:o + 4])[0]


def main():
    d = open(MPQ, 'rb').read()
    print('menu.mpq size:', len(d))
    # Rock Bottom at 0x5b6ef per the specials JSON; dump context
    for off, name in ((0x5b6ef, 'Rock Bottom'),
                      (0x5b52b, 'profile-block start')):
        print(f'--- {name} @ 0x{off:x} ---')
        print('  text:', d[off:off + 64])
        print('  64B before:', d[off - 64:off].hex())
        print('  32B after name end:',
              d[off + len(name):off + len(name) + 32].hex())
    # Scan the whole profile region for the structure: find all offsets
    # where a special name occurs, print the 16 bytes before each.
    specials = json.load(open(
        '/data/wmxix/tools-src/docs/wmXix-specials-99.json')) \
        if False else None
    # (specials JSON is local; hardcode the three Rock entries' offsets
    # from the survey: Rock Bottom 0x5b6ef; find the others by search)
    region = d[0x5b52b:0x62500]
    for name in (b'Rock Bottom', b"People's Elbow",
                 b"People's Spine Buster", b'Stone Cold Stunner',
                 b'Pedigree', b'Chokeslam'):
        o = region.find(name)
        while o != -1:
            abs_o = 0x5b52b + o
            print(f'{name.decode()} @ 0x{abs_o:x} '
                  f'before16={d[abs_o - 16:abs_o].hex()} '
                  f'after8={d[abs_o + len(name):abs_o + len(name) + 8].hex()}')
            o = region.find(name, o + 1)


if __name__ == '__main__':
    main()
