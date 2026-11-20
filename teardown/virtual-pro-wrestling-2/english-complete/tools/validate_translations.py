#!/usr/bin/env python3
"""validate_translations.py — check every translations/<hexid>.json:
  - JSON parses; every key is a valid index in the Beta 3 file
  - no Japanese / non-ASCII chars except U+3000 (ideographic space)
  - every line <= MAX_LINE visible chars (control codes @X / $N don't count)
  - @-codes are all known codes (@B etc. are state setters, not
    brackets — Beta 3's own strings routinely end without @D)
  - $N button codes and %N placeholders match the original string's set
  - the translation differs from the Beta 3 string (else why list it)
Usage: python3 tools/validate_translations.py [hexid ...]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from akitext_py import parse as akitext_parse

MAX_LINE = 55  # Japanese originals run ~30 full-width chars (~60 half-width); Beta 3's own 0008[14] hits 48
CODE_RE = re.compile(r'@[A-Za-z]')
DOLLAR_RE = re.compile(r'\$[0-9a-fA-F]')
PCT_RE = re.compile(r'%[0-9A-Fa-f]+')
KNOWN_AT_CODES = {'@G', '@D', '@B', '@Y', '@R', '@O', '@h', '@H',
                    '@a', '@E', '@g', '@y', '@r'}


def visible_len(line):
    line = CODE_RE.sub('', line)
    # $N glyphs render as one button icon each
    line = DOLLAR_RE.sub('#', line)
    return len(line)


def check_file(hexid):
    path = os.path.join(ROOT, 'translations', hexid + '.json')
    if not os.path.exists(path):
        print(f'{hexid}: no translation file')
        return 0
    table = json.load(open(path, encoding='utf-8'))
    blob = open(os.path.join(ROOT, 'work', 'beta3-%s.bin' % hexid), 'rb').read()
    orig, _ = akitext_parse(blob)
    errors = 0
    for key, text in sorted(table.items(), key=lambda kv: int(kv[0])):
        idx = int(key)
        tag = f'{hexid}[{idx}]'
        if idx < 0 or idx >= len(orig):
            print(f'{tag}: index out of range (file has {len(orig)} entries)')
            errors += 1
            continue
        o = orig[idx]
        o_text = o.decode('shift_jis', errors='replace') if o is not None else None
        if o_text is not None and text == o_text:
            print(f'{tag}: translation identical to Beta 3 string')
            errors += 1
        # non-ASCII check
        for ch in text:
            if ord(ch) > 0x7F and ord(ch) != 0x3000:
                print(f'{tag}: non-ASCII char U+{ord(ch):04X} {ch!r}')
                errors += 1
                break
        # line lengths
        for ln, line in enumerate(text.split('\n')):
            vl = visible_len(line)
            if vl > MAX_LINE:
                print(f'{tag} line {ln}: {vl} visible chars (max {MAX_LINE}): {line!r}')
                errors += 1
        # @-codes: only known codes (@B etc. are state setters, not
        # brackets — Beta 3's own strings routinely end without @D
        # and use multiple opens, so no balance check)
        for code in CODE_RE.findall(text):
            if code not in KNOWN_AT_CODES:
                print(f'{tag}: unknown @ code {code}')
                errors += 1
        # $ codes and % placeholders must match the original's
        if o_text is not None:
            if sorted(DOLLAR_RE.findall(text)) != sorted(DOLLAR_RE.findall(o_text)):
                print(f'{tag}: $ codes differ: {sorted(DOLLAR_RE.findall(text))} vs orig {sorted(DOLLAR_RE.findall(o_text))}')
                errors += 1
            if sorted(PCT_RE.findall(text)) != sorted(PCT_RE.findall(o_text)):
                print(f'{tag}: % placeholders differ: {sorted(PCT_RE.findall(text))} vs orig {sorted(PCT_RE.findall(o_text))}')
                errors += 1
    print(f'{hexid}: {len(table)} entries, {errors} errors')
    return errors


def main():
    hexids = sys.argv[1:] or sorted(
        f[:-5] for f in os.listdir(os.path.join(ROOT, 'translations'))
        if f.endswith('.json'))
    total = sum(check_file(h) for h in hexids)
    print(f'TOTAL: {total} errors')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
