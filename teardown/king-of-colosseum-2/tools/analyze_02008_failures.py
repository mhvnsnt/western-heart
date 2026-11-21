#!/usr/bin/env python3
"""Analyze 02008 translation failures: find where the greedy segmenter
gets stuck, aggregated by frequency, so missing TERM entries can be added
in bulk. Prints only aggregates (no full dumps).
Usage: python3 tools/analyze_02008_failures.py
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import koc2_translate_02008 as T  # noqa: E402
import koc2_translate_02008_patch as P  # noqa: E402

# Apply the patch additions so analysis reflects the patched translator.
T.TERM.update(P.TERM_ADD)
T.WHOLE.update(P.WHOLE_ADD)
T.TERM.update(P.TERM_ADD2)
T.WHOLE.update(P.WHOLE_ADD2)
T.TERM.update(P.TERM_ADD3)
T.WHOLE.update(P.WHOLE_ADD3)

WORK = os.path.join(HERE, "..", "work")

# Replicate the greedy matcher but report the stuck position.
KEYS = sorted(set(T.TERM) | set(T.WHOLE), key=len, reverse=True)


def stuck_at(s):
    """Return index where greedy matching first fails, or None if OK."""
    i = 0
    while i < len(s):
        c = s[i]
        if ord(c) < 128 or c in T.ROMAN or c in T.GREEK or \
                c in "０１２３４５６７８９" or c in "－。":
            i += 1
            continue
        m = None
        for k in KEYS:
            if s.startswith(k, i):
                m = k
                break
        if m is None:
            return i
        i += len(m)
    return None


def pieces(ja):
    """Split like translate_move/translate_fragment do (arrows, waves,
    middle dots, parens content)."""
    out = []
    for part in re.split(r"[→～]", ja):
        for sub in part.split("・"):
            # strip parens but keep inner as its own piece
            for p in re.split(r"[（）]", sub):
                if p:
                    out.append(p)
    return out


def main():
    fails = []
    with open(os.path.join(WORK, "translation-failures-02008.txt"),
              encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            idx, ja = line.split("\t", 1)
            fails.append((int(idx), ja))
    stuck_sub = Counter()
    stuck_char = Counter()
    unstuck = 0
    for idx, ja in fails:
        hit = False
        for p in pieces(ja):
            pos = stuck_at(p)
            if pos is not None:
                stuck_sub[p[pos:pos + 8]] += 1
                stuck_char[p[pos]] += 1
                hit = True
                break
        if not hit:
            unstuck += 1
    print(f"failures: {len(fails)}, no-stuck-position found: {unstuck}")
    print("--- top stuck substrings (from stuck position, 8 chars) ---")
    for sub, n in stuck_sub.most_common(100):
        print(f"{n:5d}  {sub}")
    print("--- top stuck single chars ---")
    for ch, n in stuck_char.most_common(60):
        print(f"{n:5d}  {ch}  U+{ord(ch):04X}")


if __name__ == "__main__":
    main()
