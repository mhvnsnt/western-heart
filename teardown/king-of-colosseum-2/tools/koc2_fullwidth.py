#!/usr/bin/env python3
"""koc2_fullwidth.py — convert ASCII translations to full-width Latin.

WHY: the KoC2 font is a JIS X 0208 full-width font. It renders
full-width Latin (proven by the original data: S.T.F is stored as
full-width Ｓ・Ｔ・Ｆ, and 1,290 of 4,021 original 02010 strings use
full-width alphanumerics) but NOT half-width ASCII — our half-width
translations rendered as BLANK on the wrestler-select screen
(boot test 2026-11-20; control with the original ISO shows Japanese
names fine). See WORKLOG.md "BLANK NAMES — FONT FINDING".

RULES (all derived from the original data's proven inventory):
- ALL UPPERCASE: the original data proves all 26 full-width capitals
  (Ａ-Ｚ) and all 10 digits (０-９), but only 15/26 lowercase letters
  (b c d f h j m q u x z never appear) — lowercase is NOT safe.
- Space -> U+3000 ideographic space (the original uses it between
  family and given names).
- Proven punctuation kept as full-width: ( ) & ! + - . = ~
- Unproven punctuation mapped: ' dropped, " dropped, , : / -> space,
  ? -> ！. Semicolon dropped.
- Initials: single capital + "." + single capital -> ・ (U+30FB,
  katakana middle dot, the game's own style for S.T.F).
- Everything else ASCII -> full-width equivalent (U+FF01-FF5E).

to_fullwidth() returns the converted string. validate() reports any
character outside the proven set (should be none after conversion).
The builders call to_fullwidth() just before Shift-JIS encoding, so
the translation JSONs stay readable ASCII.

KoC2 English lane, 2026-11-20.
"""
import re

# Characters proven present in the game's font by the original data
# (02010 + 02008 + 01999 inventories, 2026-11-20).
PROVEN_PUNCT = set("　！＆（）＋－．＝～・")

_INITIALS = re.compile(r"(?<=[A-Z])\.(?=[A-Z])")

# ASCII punctuation -> full-width (proven) or mapped.
_PUNCT_MAP = {
    "(": "（", ")": "）", "&": "＆", "!": "！", "+": "＋",
    "-": "－", ".": "．", "=": "＝", "~": "～",
    "'": "", '"': "", ",": " ", ":": " ", "/": " ", ";": "",
    "?": "！",
}


def to_fullwidth(text: str) -> str:
    """Convert an ASCII translation string to full-width uppercase."""
    if not text:
        return text
    s = text.upper()
    # Initials first: S.T.F. -> S・T・F (before the '.' rule).
    s = _INITIALS.sub("・", s)
    out = []
    for ch in s:
        o = ord(ch)
        if ch == " ":
            out.append("\u3000")
        elif "A" <= ch <= "Z" or "0" <= ch <= "9":
            out.append(chr(o + 0xFEE0))
        elif ch in _PUNCT_MAP:
            out.append(_PUNCT_MAP[ch])
        elif 0x21 <= o <= 0x7E:
            # Any other ASCII printable -> full-width equivalent.
            out.append(chr(o + 0xFEE0))
        else:
            # Non-ASCII passed through unchanged (should not happen;
            # translations are ASCII-only by rule).
            out.append(ch)
    return "".join(out)


def validate(text: str) -> list:
    """Return characters in `text` outside the proven-safe set."""
    bad = []
    for ch in text:
        if ch in PROVEN_PUNCT:
            continue
        if "\uff21" <= ch <= "\uff3a":  # full-width A-Z
            continue
        if "\uff10" <= ch <= "\uff19":  # full-width 0-9
            continue
        bad.append(ch)
    return sorted(set(bad))


if __name__ == "__main__":
    tests = [
        "Tatsumi Fujinami",
        "Dragon Sleeper",
        "S.T.F.",
        "Demon World's Rampaging Criminal",
        "Blue-Eyed Fighting Spirit",
        "Vert. Drop Reverse Brainbuster",
        "Hirai Jr.",
        "(M Dragon Ver)",
        "Northern Lights Suplex Hold",
    ]
    for t in tests:
        fw = to_fullwidth(t)
        print(f"{t!r:45} -> {fw!r}  bad={validate(fw)}")
