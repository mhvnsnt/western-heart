#!/usr/bin/env python3
"""Flip the language of a KoC2 hybrid JP/EN ISO (M3, Mars's language toggle).

The hybrid ISO carries both languages. Switching rewrites, in the ISO file:

  * the toggle flag (1 byte): 1 = English, 0 = Japanese. The pack-loader
    hook reads it on every load, so the flag decides whether an affected
    pack entry loads from its Japanese original or its English mirror.
  * the 379 ELF string slots (elf.txt): these live in the executable, so no
    pack hook can reach them - the flip writes the JP or EN bytes directly.
  * the 2 Dojo yellow-quote token tables (「 」 in Japanese, " " in English).

The ASCII font patch stays on in both modes (Japanese two-byte codes are
unaffected by it).

Usage:
  koc2_lang_toggle.py <hybrid.iso> en|jp [--data toggle_data.json]
  koc2_lang_toggle.py <hybrid.iso> status

The flip is instant (a few KB of writes). Quit the game first, flip, then
start the game again - the language applies from boot.
"""
import base64
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / 'work' / 'toggle_data.json'
SECTOR = 2048


def load_data(path):
    data = json.loads(Path(path).read_text())
    for slot in data['slots']:
        slot['jp_b'] = base64.b64decode(slot['jp'])
        slot['en_b'] = base64.b64decode(slot['en'])
    for tok in data['dojo_tokens']:
        tok['jp_b'] = base64.b64decode(tok['jp'])
        tok['en_b'] = base64.b64decode(tok['en'])
    return data


def check_hybrid(f, data):
    """Refuse to touch an ISO that is not our hybrid build."""
    hook = data['hook_check']
    f.seek(data['elf']['lba'] * SECTOR + hook['elf_file_offset'])
    cur = f.read(8)
    if cur != base64.b64decode(hook['bytes_b64']):
        sys.exit('not a hybrid ISO (toggle hook not found in the ELF) - refusing to write')


def read_flag(f, data):
    f.seek(data['flag']['iso_offset'])
    return f.read(1)[0]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2:
        print(__doc__)
        return 1
    iso, lang = Path(argv[0]), argv[1].lower()
    data_path = DEFAULT_DATA
    if '--data' in argv:
        data_path = Path(argv[argv.index('--data') + 1])
    data = load_data(data_path)

    if lang == 'status':
        with open(iso, 'rb') as f:
            check_hybrid(f, data)
            flag = read_flag(f, data)
        print(f'{iso.name}: {"ENGLISH" if flag else "JAPANESE"} (flag={flag})')
        return 0
    if lang not in ('en', 'jp'):
        sys.exit('language must be en or jp (or: status)')

    with open(iso, 'r+b') as f:
        check_hybrid(f, data)
        before = read_flag(f, data)
        # flag byte
        f.seek(data['flag']['iso_offset'])
        f.write(bytes([data['flag']['values'][lang]]))
        # ELF string slots
        elf_base = data['elf']['lba'] * SECTOR
        for slot in data['slots']:
            f.seek(elf_base + slot['offset'])
            f.write(slot['en_b'] if lang == 'en' else slot['jp_b'])
        # Dojo quote tokens
        for tok in data['dojo_tokens']:
            f.seek(elf_base + tok['offset'])
            f.write(tok['en_b'] if lang == 'en' else tok['jp_b'])
        f.flush()
        after = read_flag(f, data)
    print(f'{iso.name}: {"ENGLISH" if before else "JAPANESE"} -> '
          f'{"ENGLISH" if after else "JAPANESE"} '
          f'({len(data["slots"])} ELF slots + {len(data["dojo_tokens"])} Dojo tokens flipped)')
    print('Start the game again to play in the new language.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
