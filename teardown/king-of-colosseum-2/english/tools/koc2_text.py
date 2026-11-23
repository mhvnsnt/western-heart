#!/usr/bin/env python3
"""koc2_text.py — parse King of Colosseum II's music + commentary text files.

Two more text-bearing files from KC2FIRE.000 (found 2026-11-19):

  file 01454 — MUSIC TABLE (23,184 bytes): entrance-theme titles in
      fixed 48-byte (0x30) slots, Shift-JIS, NUL-padded. 483 slots;
      slot 0 is "なし" (none). Titles carry suffixes: (手) = hand-clap
      version, (Ｃ) = chorus version. Examples: DRAGON SUPLEX,
      nWoクラッシュ, MISSONBLOW, テンザン〜時空〜, 怒りの獣神,
      スパルタンＸ, MUTA, 爆勝宣言, パワーホール, THUNDER STORM.
  file 02030 — COMMENTARY SCRIPT (331,155 bytes): the play-by-play
      announcer's lines. The file starts with 20 ADX names (K06..K28,
      NE01..NE03 — the first files of KC2FIRE.AFS), one per CRLF line,
      followed by 8,984 commentary lines in Shift-JIS. Each line
      carries a code prefix (letters + number + optional variant
      letter) and a full-width underscore (＿) separator, e.g.
      "a1＿パンチを打ち込んでまいります" (throws a punch). The codes
      group lines by situation: a/b = general play-by-play, fc/kc/nc/
      oc = per-federation calls, VS = versus lines, *BGM = music cues.

Usage:
  koc2_text.py music <file01454.bin> [output.json]
  koc2_text.py commentary <file02030.bin> [output.json]
  Without an output path, JSON goes to stdout.

Lane E (KoC2), 2026-11-19.
"""
import json
import re
import sys
from pathlib import Path

SLOT = 48


def parse_music(data: bytes):
    titles = []
    for i in range(0, len(data) - SLOT + 1, SLOT):
        raw = data[i:i + SLOT].split(b"\x00", 1)[0]
        try:
            titles.append(raw.decode("shift_jis"))
        except UnicodeDecodeError:
            titles.append("<0x" + raw.hex() + ">")
    return {
        "source": "KC2FIRE.000 file 01454",
        "slot_bytes": SLOT,
        "slot_count": len(titles),
        "titles": titles,
    }


def parse_commentary(data: bytes):
    # The file starts with 20 ADX names (K06..K28, NE01..NE03 — the
    # first files of KC2FIRE.AFS), one per CRLF line, followed by the
    # commentary lines. Each line carries a code prefix (letters +
    # number + optional variant letter) and a full-width underscore
    # (＿) separator, e.g. "a1＿パンチを打ち込んでまいります".
    # The codes group lines by situation: a/b = general play-by-play,
    # fc/kc/nc/oc = per-federation calls, VS = versus lines,
    # *BGM = music cues. Lines are kept in file order with their code.
    text = data.decode("shift_jis", errors="replace")
    lines = text.split("\r\n")
    adx = []
    body = []
    for ln in lines:
        if not body and re.fullmatch(r"[A-Z]+\d+", ln or ""):
            adx.append(ln)
        else:
            body.append(ln)
    entries = []
    for ln in body:
        if not ln:
            continue
        m = re.match(r"^([A-Za-z]+\d+[a-z]?)＿(.*)$", ln)
        if m:
            entries.append({"code": m.group(1), "text": m.group(2)})
        else:
            entries.append({"code": "", "text": ln})
    return {
        "source": "KC2FIRE.000 file 02030",
        "adx_header": adx,
        "line_count": len(entries),
        "lines": entries,
    }


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    kind, path = argv[1], Path(argv[2])
    data = path.read_bytes()
    if kind == "music":
        result = parse_music(data)
    elif kind == "commentary":
        result = parse_commentary(data)
    else:
        print(f"unknown kind {kind!r}: use 'music' or 'commentary'",
              file=sys.stderr)
        return 2
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if len(argv) > 3:
        Path(argv[3]).write_text(text, encoding="utf-8")
        print(f"wrote {argv[3]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
