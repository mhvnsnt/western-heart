#!/usr/bin/env python3
"""Build the KoC2 hybrid JP/EN ISO (M3, Mars's language-toggle build).

The hybrid carries BOTH languages in one disc image:

  * KC2FIRE.000 is the hybrid pack (tools/hybrid_pack.py): the Japanese
    originals at their own indices, plus English mirrors of the 392 affected
    groups appended after the last group (604 mirror entries).
  * The ELF is kactusken's English ELF (ASCII font patch + Dojo quotes)
    plus the toggle hook (tools/toggle_patch.py): three hook sites redirect
    pack loads to the English mirrors when the flag word is 1 (English,
    the default) and leave them alone when it is 0 (Japanese).
  * The 379 ELF string slots (elf.txt) live in the executable, so no pack
    hook can reach them: the flip script (tools/koc2_lang_toggle.py) rewrites
    them in the ISO file together with the flag byte. This builder records
    everything the flip script needs in toggle_data.json (flag ISO offset,
    per-slot JP/EN bytes, Dojo token bytes).

Base image: the v0.2 REFERENCE ISO (the author's released, in-game-verified
build), not our rebuild. The clean ISO is read only for the Japanese bytes
of the ELF string slots.

Usage:
  build_hybrid.py [--out NAME] [--data toggle_data.json]
"""
import base64
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
M3 = HERE.parent
REPO = M3 / 'sources' / 'kactusken' / 'repo'
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(HERE))

import disc  # noqa: E402
import elf as elfmod  # noqa: E402
import pak  # noqa: E402
import toggle_patch  # noqa: E402

EN_ISO = M3 / 'sources' / 'kactusken' / 'v02ref' / 'kactusken-v0.2-english.iso'
CLEAN_ISO = Path('/home/hatch/workspace/grok-declined-items/lane-koc2/extract'
                 '/King of Colosseum II (Japan).iso')
HYBRID_PACK = M3 / 'work' / 'KC2FIRE-hybrid.000'
HYBRID_INFO = M3 / 'work' / 'hybrid-info.json'
ELF_TXT = REPO / 'translation' / 'text' / 'elf.txt'
OUT = M3 / 'work' / 'King of Colosseum II (Hybrid JP-EN).iso'
DATA_OUT = M3 / 'work' / 'toggle_data.json'

PADDING_DONORS = ['/DATA/GOOD.BYE', '/DATA/HELLO.FOR']
SHIFT_INTO = ['/DATA/LAST.DAY']
ELF_PATH = '/SLPM_656.02'
PACK_PATH = '/DATA/KC2FIRE.000'
# Dojo yellow-quote token tables (build.py TEXT_DATA_PATCHES): JP bytes -> EN bytes
DOJO_TOKENS = [(0x3abdb0, b'\x81\x75', b'\x81\x67'), (0x3abe00, b'\x81\x76', b'\x81\x68')]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_elf(iso_path):
    with open(iso_path, 'rb') as f:
        d = disc.Disc(f)
        return bytes(d.read_file(d.find(ELF_PATH)))


def parse_elf_slots(path):
    """[(file offset, slot size)] from translation/text/elf.txt."""
    slots = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        m = re.match(r'@\s*([0-9a-fA-F]+)\s+slot=(\d+)', line)
        if m:
            slots.append((int(m.group(1), 16), int(m.group(2))))
    return slots


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = OUT
    data_out = DATA_OUT
    if '--out' in argv:
        out = Path(argv[argv.index('--out') + 1])
    if '--data' in argv:
        data_out = Path(argv[argv.index('--data') + 1])

    info = json.loads(HYBRID_INFO.read_text())
    affected, mirror_base = info['affected'], info['mirror_base']
    print(f'hybrid pack: {len(affected)} affected entries, mirror base {mirror_base}')

    hybrid_pack = HYBRID_PACK.read_bytes()
    errors = pak.layout_errors(hybrid_pack)
    if errors:
        sys.exit('hybrid pack breaks the layout rules:\n  ' + '\n  '.join(errors[:10]))
    print(f'hybrid pack OK: {len(hybrid_pack)} bytes, layout clean')

    if not EN_ISO.exists():
        sys.exit(f'v0.2 reference ISO missing: {EN_ISO}')
    print(f'copying v0.2 reference ISO -> {out.name} ...')
    shutil.copyfile(EN_ISO, out)

    clean_elf = read_elf(CLEAN_ISO)
    print(f'clean ELF: {len(clean_elf)} bytes')

    with open(out, 'r+b') as f:
        d = disc.Disc(f, writable=True)
        en_elf = bytearray(d.read_file(d.find(ELF_PATH)))
        e = elfmod.Elf(bytes(en_elf))
        print(f'EN ELF: {len(en_elf)} bytes, entry {e.entry:#x}')

        # --- verify the toggle sites against the EN ELF, then patch it ---
        for addr, (w0, w1) in toggle_patch.ORIGINAL.items():
            off = e.offset(addr)
            cur = bytes(en_elf[off:off + 8])
            if cur != __import__('struct').pack('<II', w0, w1):
                sys.exit(f'EN ELF: unexpected code at hook site 0x{addr:x} - not the v0.2 ELF?')
        cave_off = e.offset(toggle_patch.CAVE)
        cave_cur = bytes(en_elf[cave_off:cave_off + toggle_patch.CAVE_SIZE])
        if hashlib.sha1(cave_cur).hexdigest() != toggle_patch.CAVE_SHA1:
            sys.exit('EN ELF: toggle cave bytes differ from the original - not the v0.2 ELF?')
        print('hook sites + cave verified against the EN ELF')

        blob, syms = toggle_patch.build(affected, mirror_base)
        en_elf[cave_off:cave_off + len(blob)] = blob
        for addr, new in toggle_patch.hooks(syms).items():
            off = e.offset(addr)
            en_elf[off:off + 8] = new
        print(f'toggle cave written: {len(blob)}/{toggle_patch.CAVE_SIZE} bytes, '
              f'FLAG at 0x{syms["FLAG"]:x} (default 1 = English), TABLE at 0x{syms["TABLE"]:x}')

        # --- write both files back (pack first: it needs relocation) ---
        def fits(name, data):
            return (len(data) + disc.SECTOR - 1) // disc.SECTOR <= d.allocated_sectors(d.find(name))
        for name, data in sorted([(PACK_PATH, hybrid_pack), (ELF_PATH, bytes(en_elf))],
                                 key=lambda nd: fits(nd[0], nd[1])):
            d.write_file(d.find(name), data, relocate=True,
                         donors=PADDING_DONORS, shift_into=SHIFT_INTO)
            print(f'patched {name}')

        # --- final layout, for toggle_data.json ---
        elf_entry = d.find(ELF_PATH)
        pack_entry = d.find(PACK_PATH)
        flag_off = e.offset(syms['FLAG'])
        problems = d.check()
        print('disc check:', '\n'.join(problems) if problems else 'ISO9660 and UDF agree')
        if problems and problems[0] != 'no UDF file system (ISO9660 only)':
            sys.exit('disc check failed - not writing toggle data')

    # --- toggle data: flag offset + per-slot JP/EN bytes + Dojo tokens ---
    slots = parse_elf_slots(ELF_TXT)
    print(f'elf.txt: {len(slots)} string slots')
    slot_data = []
    for off, size in slots:
        jp, en = clean_elf[off:off + size], bytes(en_elf[off:off + size])
        if len(jp) != size or len(en) != size:
            sys.exit(f'elf slot @{off:x} slot={size} runs past the end of an ELF')
        slot_data.append({'offset': off, 'slot': size,
                          'jp': base64.b64encode(jp).decode(),
                          'en': base64.b64encode(en).decode()})
    dojo = []
    for addr, jp_want, en_want in DOJO_TOKENS:
        off = e.offset(addr)
        jp, en = clean_elf[off:off + 2], bytes(en_elf[off:off + 2])
        if jp != jp_want or en != en_want:
            sys.exit(f'Dojo token @{addr:#x}: got JP {jp.hex()} EN {en.hex()}, '
                     f'expected JP {jp_want.hex()} EN {en_want.hex()}')
        dojo.append({'addr': addr, 'offset': off,
                     'jp': base64.b64encode(jp).decode(),
                     'en': base64.b64encode(en).decode()})

    data = {
        'hybrid_iso': out.name,
        'hybrid_sha256': sha256_file(out),
        'en_source': EN_ISO.name,
        'en_source_sha256': '8184f07ac7559d1e1f5fd3695e7a308ded33688281a32433028fed3f41c5327d',
        'flag': {'iso_offset': elf_entry.lba * disc.SECTOR + flag_off,
                 'elf_lba': elf_entry.lba, 'elf_file_offset': flag_off,
                 'default': 1, 'values': {'en': 1, 'jp': 0}},
        'hook_check': {'elf_file_offset': e.offset(toggle_patch.LOAD_SITE),
                       'bytes_b64': base64.b64encode(
                           toggle_patch.hooks(syms)[toggle_patch.LOAD_SITE]).decode()},
        'elf': {'lba': elf_entry.lba, 'size': elf_entry.size},
        'pack000': {'lba': pack_entry.lba, 'size': pack_entry.size,
                    'entries': 7519 + len(affected), 'mirror_base': mirror_base},
        'slots': slot_data,
        'dojo_tokens': dojo,
    }
    data_out.write_text(json.dumps(data, indent=1))
    print(f'wrote {data_out} ({len(slot_data)} slots, {len(dojo)} Dojo tokens)')
    print(f'done: {out} ({out.stat().st_size} bytes)')
    print(f'  SHA-256 {data["hybrid_sha256"]}')
    print(f'  ELF LBA {elf_entry.lba}, .000 LBA {pack_entry.lba}, '
          f'flag ISO offset {data["flag"]["iso_offset"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
