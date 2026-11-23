#!/usr/bin/env python3
"""koc2_abbrev_02010.py — shorten 02010 translations to fit the raw slot.

Why: the game's 02010 loader reads the file RAW (it does not
decompress — boot Test C, 2026-11-20: a compressed 02010 shows
garbage/blank values on the Appearance screen). So 02010 must be
stored raw, and the raw file must fit its original stored slot
(198,656 bytes) because the archive is fully packed and shifting
other files breaks the game (boot Tests A/B/D, 2026-11-20).

The full-width English table is 143,485 bytes; the slot allows
~69,768. Two-pass fit:
  Pass 1: per-string cap at the ORIGINAL string's byte length
      (full-width = 2 bytes/char in cp932), word-boundary
      truncation. This fits easily but wastes budget on word
      boundaries (~52,767 bytes used).
  Pass 2 (restore): spend the spare budget by restoring truncated
      strings word-by-word, highest-priority categories first
      (costume parts, then names, styles, nicknames, music,
      entrance, staff/titles, narration last). No string is
      restored past 30 chars (the Appearance UI column fits ~15
      full-width chars; 30 is a safe display cap).
Tape variants ('(Hairy)', '(Finger Tape)', ...) distinguish parts
that are otherwise identical, so they are rewritten to short codes
(' H', ' F', ' B', ' HF', ' HB') instead of being stripped or
truncated away.

Usage (imported by koc2_strings_build.py):
  shorten_all(translations, segments) -> dict phys->shortened text
  shorten(text, orig_bytes) -> str   (pass 1 only, for one string)

Run standalone to report the fit + worst remaining truncations:
  koc2_abbrev_02010.py
"""
import json
import re
import struct
import sys
from pathlib import Path

BUDGET = 69568  # string-table bytes (69,768 slot minus 200 safety)
DISPLAY_CAP = 30  # max chars after restore (UI width safety)

# Tape/hair variant parentheticals -> short distinguishing codes.
TAPE_CODES = [
    ("(Hairy & Back-of-Hand Tape)", "HB"),
    ("(Hairy & Finger Tape)", "HF"),
    ("(Back-of-Hand Tape)", "B"),
    ("(Finger Tape)", "F"),
    ("(Hairy)", "H"),
]

# Restore priority by category id (lower = restore first).
CAT_PRIORITY = {
    6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,  # costume
    0: 1, 15: 1,  # wrestler names
    1: 2, 2: 2, 3: 2, 4: 2, 5: 2,  # styles/types
    22: 3,  # nicknames
    23: 4,  # music
    17: 5, 21: 5,  # entrance
    16: 6, 18: 6, 19: 6, 20: 6,  # staff/titles/booleans
    24: 7,  # narration last
}


def rewrite_tape(text: str) -> str:
    for paren, code in TAPE_CODES:
        if text.endswith(" " + paren):
            return text[: -len(paren) - 1] + " " + code
        if text.endswith(paren):
            return text[: -len(paren)] + code
    return text


def truncate_words(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 0:
        raise ValueError(f"no room for {text!r}")
    out = ""
    for w in text.split(" "):
        cand = w if not out else out + " " + w
        if len(cand) <= max_chars:
            out = cand
        else:
            break
    return out if out else text[:max_chars]


def shorten(text: str, orig_bytes: int) -> str:
    """Pass 1: tape-code rewrite + word-boundary truncation to the
    original string's byte length (full-width = 2 bytes/char)."""
    return truncate_words(rewrite_tape(text), orig_bytes // 2)


def logical_to_physical(logical: int) -> int:
    if logical < 581:
        return logical
    if logical < 1353:
        return logical + 1
    return logical + 2


def phys_to_category(root: Path) -> dict:
    d = json.loads((root / "data" / "koc2-strings.json").read_text())
    out = {}
    for c in d["categories"]:
        for k in range(c["count"]):
            out[logical_to_physical(c["first_string"] + k)] = c["id"]
    return out


def shorten_all(translations: dict, segments: list,
                budget: int = BUDGET) -> dict:
    """Two-pass fit. segments is the list of ORIGINAL segment bytes
    (physical order). Returns {phys_str: shortened ASCII text} for
    every translated segment."""
    root = Path(__file__).resolve().parent.parent
    cat_of = phys_to_category(root)
    # Pass 1: per-string cap.
    full = {}   # phys -> tape-rewritten full text
    short = {}  # phys -> truncated text
    total = 0
    for phys, seg in enumerate(segments):
        key = str(phys)
        if key not in translations:
            total += len(seg) + 1
            continue
        f = rewrite_tape(translations[key])
        s = truncate_words(f, len(seg) // 2)
        full[phys] = f
        short[phys] = s
        total += len(s) * 2 + 1
    # Pass 2: restore by priority, word by word, while budget allows.
    capped = [p for p in full if len(short[p]) < min(len(full[p]),
                                                     DISPLAY_CAP)]
    capped.sort(key=lambda p: (CAT_PRIORITY.get(cat_of.get(p, 99), 99),
                               -(min(len(full[p]), DISPLAY_CAP)
                                 - len(short[p]))))
    for p in capped:
        target = min(len(full[p]), DISPLAY_CAP)
        words = full[p].split(" ")
        cur = short[p]
        # Extend word by word while it fits budget and display cap.
        while len(cur) < target:
            # Find the next word after cur.
            rest = full[p][len(cur):].lstrip(" ")
            if not rest:
                break
            nxt = rest.split(" ", 1)[0]
            cand = (cur + " " + nxt) if cur else nxt
            if len(cand) > target:
                break
            if total + (len(cand) - len(cur)) * 2 > budget:
                break
            total += (len(cand) - len(cur)) * 2
            cur = cand
        short[p] = cur
    if total > budget:
        raise ValueError(f"shortened table {total} > budget {budget}")
    print(f"02010 abbrev: table {total} bytes (budget {budget}), "
          f"{len(capped)} strings capped then restored")
    return {str(p): s for p, s in short.items()}


def main():
    root = Path(__file__).resolve().parent.parent
    t = json.loads((root / "work" / "translations-02010.json").read_text())
    raw = (root / ".." / "grok-declined-items" / "lane-koc2" / "extract"
           / "kc2fire000" / "file02010.bin").resolve().read_bytes()
    n_cat, n_str, str_bytes = struct.unpack_from("<III", raw, 0)
    base = len(raw) - str_bytes
    segs = []
    i = base
    while i < len(raw):
        j = raw.find(b"\x00", i)
        segs.append(raw[i:j])
        i = j + 1
    out = shorten_all(t, segs)
    # Report worst remaining truncations.
    worst = []
    for k, s in out.items():
        f = rewrite_tape(t[k])
        if len(s) < len(f):
            worst.append((len(f) - len(s), int(k), f, s))
    worst.sort(reverse=True)
    print(f"still truncated: {len(worst)} strings")
    for lost, phys, f, s in worst[:20]:
        print(f"  -{lost:2d} [phys {phys}] {f!r} -> {s!r}")


if __name__ == "__main__":
    main()
