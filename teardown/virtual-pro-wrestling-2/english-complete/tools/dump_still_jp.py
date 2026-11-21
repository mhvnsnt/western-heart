#!/usr/bin/env python3
"""dump_still_jp.py — write the still-Japanese strings of each AkiText
file to work/still-jp/<hexid>.txt (index + Shift_JIS-decoded text), so
the translation pass can work file by file without pasting dumps into
chat. Also reports duplicate Japanese strings within a file (same JP
text at several indices — one translation covers all of them)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from akitext_py import parse as akitext_parse


def has_japanese(b):
    """True if the byte string contains Japanese characters (excluding
    U+3000 ideographic space, which Beta 3 uses as spacing in English)."""
    if b is None:
        return False
    try:
        s = b.decode('shift_jis')
    except UnicodeDecodeError:
        return True
    for ch in s:
        o = ord(ch)
        if o == 0x3000:
            continue
        if o > 0x2FFF or (0x3040 <= o <= 0x30FF) or \
                (0x4E00 <= o <= 0x9FFF) or (0xFF00 <= o <= 0xFFEF):
            return True
    return False


def decode(b):
    if b is None:
        return None
    try:
        return b.decode('shift_jis')
    except UnicodeDecodeError:
        return b.decode('shift_jis', errors='replace')


# Beta 3 replaced these three real move names with the "none OK"
# placeholder; translate from the CLEAN text instead.
RESTORE_FROM_CLEAN = {('0064', 415), ('0064', 416), ('0064', 417)}


def main():
    survey = json.load(open(os.path.join(ROOT, 'work', 'beta3-survey.json')))
    outdir = os.path.join(ROOT, 'work', 'still-jp')
    os.makedirs(outdir, exist_ok=True)
    for hexid, info in survey.items():
        blob = open(os.path.join(ROOT, 'work', 'beta3-%s.bin' % hexid), 'rb').read()
        strings, _deg = akitext_parse(blob)
        clean_blob = open(os.path.join(ROOT, 'work', 'clean-%s.bin' % hexid), 'rb').read()
        clean_strings, _cdeg = akitext_parse(clean_blob)
        # TRUE criterion: the Beta 3 string itself contains Japanese
        # (Beta 3 "translated" some files by only stripping newlines).
        still = [i for i, s in enumerate(strings) if has_japanese(s)]
        if not still:
            continue
        # duplicate analysis: group still-JP indices by identical JP text
        by_text = {}
        for i in still:
            src = clean_strings[i] if (hexid, i) in RESTORE_FROM_CLEAN else strings[i]
            by_text.setdefault(src, []).append(i)
        lines = []
        lines.append(f'# {hexid} {info["label"]}: {len(still)} still-Japanese '
                     f'({len(by_text)} unique texts)')
        lines.append('# format: [index] japanese text (duplicates listed once, '
                     'indices after =>)')
        lines.append('')
        for text, idxs in sorted(by_text.items(), key=lambda kv: kv[1][0]):
            tag = f'[{idxs[0]}]' if len(idxs) == 1 else \
                f'[{idxs[0]}] (also {", ".join(str(x) for x in idxs[1:])})'
            if (hexid, idxs[0]) in RESTORE_FROM_CLEAN:
                tag += ' [RESTORE: Beta 3 blanked this; translate from clean]'
            lines.append(f'{tag} {decode(text)}')
            lines.append('---')
        out = os.path.join(outdir, hexid + '.txt')
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'{hexid}: {len(still)} still-JP, {len(by_text)} unique -> {out}')


if __name__ == '__main__':
    main()
