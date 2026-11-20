#!/usr/bin/env python3
"""JP/EN language toggle for King of Colosseum II (M3, Mars's hybrid build).

The hybrid ISO carries BOTH languages in KC2FIRE.000: the Japanese originals
at their own indices, and English variants of the 392 affected groups appended
after the last group (see hybrid_pack.py). This patch hooks the game's pack
loader so that, when the language flag is EN, every load of an affected entry
is redirected to its English mirror. When the flag is JP, every load behaves
exactly as the original game.

Hook sites (all verified against the original ELF before patching):
  0x28b178  the pack loader (a0=pack, a1=dest, a2=index, a3=flag; 40+ callers)
  0x28b0a0  stored-size calc (a0=pack, a1=index) - external callers size
            buffers with it (incl. the roster loader 0x1164d0), so it must
            see the translated index too, or an English entry would overflow
            a Japanese-sized buffer
  0x28b0b8  unpacked-size calc (same shape, a3=1 variant)
0x28aff8 and 0x28b0d0 have no direct callers and need no hook.

The cave is 0x285464 (1,956 bytes): an unreferenced routine, verified safe by
tools/cave_check.py (no jal/j/branch/data-pointer/lui reference from outside
the region points into it; the words before it are `jr ra` + delay slot, so
nothing falls through into it). It holds the three hook stubs, the shared
translate routine, the flag word (1 = English, 0 = Japanese; default English)
and the table of affected original entry indices (u16, sorted). The mirror
index for table[i] is MIRROR_BASE + i (mirror entries are laid out in the
same order as the originals).

The flag is flipped by tools/koc2_lang_toggle.py, which also rewrites the
379 ELF string slots (elf.txt) in the ISO file, since those live in the
executable and no pack hook can reach them.

Usage:
  toggle_patch.py show                     the patch sites, cave layout, table size
  toggle_patch.py build <affected.json>    write the cave blob + hook bytes (for
                                           build_hybrid.py; normally imported)
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sources' / 'kactusken' / 'repo' / 'tools'))
import mips_asm  # noqa: E402

FILE = '/SLPM_656.02'
CAVE = 0x285464
CAVE_SIZE = 1956
# the cave's original bytes (an unreferenced routine) - SHA-1, checked by the build
CAVE_SHA1 = '758cd05c246385aa292e5ab0be5f83f7c5a8a9aa'

LOAD_SITE = 0x28b178
SIZE_A_SITE = 0x28b0a0
SIZE_B_SITE = 0x28b0b8
LOAD_BACK = 0x28b180
SIZE_A_BACK = 0x28b0a8
SIZE_B_BACK = 0x28b0c0
PACK_000 = 1  # pack index of KC2FIRE.000 (0=.MVS, 1=.000, 2=.001)

ORIGINAL = {
    LOAD_SITE: (0x27bdffc0, 0xffb00000),   # addiu sp,sp,-0x40 ; sd s0,(sp)
    SIZE_A_SITE: (0x27bdfff0, 0x0000382d),  # addiu sp,sp,-0x10 ; move a3,zero
    SIZE_B_SITE: (0x27bdfff0, 0x24070001),  # addiu sp,sp,-0x10 ; addiu a3,zero,1
}

SOURCE = '''
hook_load:
    addiu $sp, $sp, -0x40
    .word 0xffb00000
    addiu $sp, $sp, -8
    sw $ra, 0($sp)
    sw $a1, 4($sp)
    move $a1, $a2
    jal translate
    nop
    move $a2, $v0
    lw $a1, 4($sp)
    lw $ra, 0($sp)
    addiu $sp, $sp, 8
    j LOAD_BACK
    nop
hook_size_a:
    addiu $sp, $sp, -0x10
    move $a3, $zero
    addiu $sp, $sp, -8
    sw $ra, 0($sp)
    jal translate
    nop
    move $a1, $v0
    lw $ra, 0($sp)
    addiu $sp, $sp, 8
    j SIZE_A_BACK
    nop
hook_size_b:
    addiu $sp, $sp, -0x10
    addiu $a3, $zero, 1
    addiu $sp, $sp, -8
    sw $ra, 0($sp)
    jal translate
    nop
    move $a1, $v0
    lw $ra, 0($sp)
    addiu $sp, $sp, 8
    j SIZE_B_BACK
    nop
translate:
    move $v0, $a1
    addiu $t0, $zero, 1
    bne $a0, $t0, tr_done
    nop
    lui $t0, %hi(FLAG)
    lw $t1, %lo(FLAG)($t0)
    beqz $t1, tr_done
    nop
    lui $t2, %hi(TABLE)
    addiu $t2, $t2, %lo(TABLE)
    move $t3, $zero
    addiu $t4, $zero, COUNT
tr_loop:
    sll $t5, $t3, 1
    addu $t5, $t2, $t5
    lhu $t6, 0($t5)
    beq $t6, $a1, tr_found
    nop
    addiu $t3, $t3, 1
    sltu $t7, $t3, $t4
    bnez $t7, tr_loop
    nop
    j tr_done
    nop
tr_found:
    addiu $t0, $zero, MIRROR_BASE
    addu $v0, $t0, $t3
tr_done:
    jr $ra
    nop
FLAG:
    .word 1
TABLE:
'''


def build(affected, mirror_base):
    """(cave bytes, label addresses) - the routines, the flag, then the table."""
    affected = sorted(affected)
    if not affected:
        raise SystemExit('toggle_patch: no affected entries - nothing to translate')
    if max(affected) >= 0x10000 or mirror_base >= 0x10000 or len(affected) >= 0x8000:
        raise SystemExit('toggle_patch: table values do not fit u16')
    src = SOURCE + '\n'.join('    .half ' + ', '.join(f'0x{k:04x}' for k in affected[i:i + 8])
                             for i in range(0, len(affected), 8)) + '\n'
    blob, syms = mips_asm.assemble(src, CAVE, {
        'LOAD_BACK': LOAD_BACK, 'SIZE_A_BACK': SIZE_A_BACK, 'SIZE_B_BACK': SIZE_B_BACK,
        'COUNT': len(affected), 'MIRROR_BASE': mirror_base})
    if len(blob) > CAVE_SIZE:
        raise SystemExit(f'toggle_patch: cave needs {len(blob)} bytes, only {CAVE_SIZE}')
    return blob, syms


def hooks(syms):
    """The three hook sites: j <stub> + nop (each stub re-executes the two
    replaced instructions and jumps back to site+8)."""
    def j(target):
        return (2 << 26) | ((target >> 2) & 0x3ffffff)
    return {LOAD_SITE: struct.pack('<II', j(syms['hook_load']), 0),
            SIZE_A_SITE: struct.pack('<II', j(syms['hook_size_a']), 0),
            SIZE_B_SITE: struct.pack('<II', j(syms['hook_size_b']), 0)}


def patches(affected, mirror_base):
    """CODE_PATCHES-style entries (group, file, address, original, new,
    description); the cave's original is checked by CAVE_SHA1 (original None)."""
    blob, syms = build(affected, mirror_base)
    out = [('toggle', FILE, addr, struct.pack('<II', *ORIGINAL[addr]), new, None)
           for addr, new in hooks(syms).items()]
    out.append(('toggle', FILE, CAVE, None, blob,
                'JP/EN toggle: pack-loader remap hook + flag + table'))
    return out, syms


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == 'show':
        blob, syms = build([1441, 1442, 1999, 2008, 2010], 7519)
        print(f'cave 0x{CAVE:x}: {len(blob)}/{CAVE_SIZE} bytes (5-entry demo table)')
        for name in ('hook_load', 'hook_size_a', 'hook_size_b', 'translate', 'FLAG', 'TABLE'):
            print(f'  {name} at 0x{syms[name]:x}')
        for addr, new in hooks(syms).items():
            print(f'  hook 0x{addr:x}: {new.hex()}')
        return 0
    if argv[0] == 'build':
        affected = json.loads(Path(argv[1]).read_text())
        mirror_base = int(argv[2]) if len(argv) > 2 else 7519
        blob, syms = build(affected, mirror_base)
        Path('toggle-cave.bin').write_bytes(blob)
        print(f'cave 0x{CAVE:x}: {len(blob)}/{CAVE_SIZE} bytes, '
              f'{len(affected)} table entries, FLAG at 0x{syms["FLAG"]:x}, '
              f'TABLE at 0x{syms["TABLE"]:x}')
        return 0
    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main())
