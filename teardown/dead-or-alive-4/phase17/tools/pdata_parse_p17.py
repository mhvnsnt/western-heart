#!/usr/bin/env python3
"""DOA4 phase 17: parse the XEX PE .pdata function table.

Xbox 360 .pdata entries are 8 bytes: u32 BE begin VA (absolute,
base 0x82000000 already applied) + u32 BE packed word whose
bits 8..27 hold the function length in instructions
(end = begin + 4 * count) and whose low byte carries flags.
Validated: 15,054 entries, begins strictly increasing, every
phase-16 proven VA falls inside exactly one entry.
Output: CSV of begin,end (hex) + summary.
"""
import struct, sys

def parse(pe_path):
    d = open(pe_path, 'rb').read()
    PD_OFF, PD_VSZ = 0x2B4000, 0x1D670  # from the PE section table
    funcs = []
    for i in range(0, PD_VSZ // 8 * 8, 8):
        b, w = struct.unpack_from('>II', d, PD_OFF + i)
        funcs.append((b, b + 4 * ((w >> 8) & 0xFFFFF)))
    return funcs

if __name__ == '__main__':
    funcs = parse(sys.argv[1])
    for b, e in funcs:
        print(f'{b:x},{e:x}')
    print(f'# {len(funcs)} functions', file=sys.stderr)
