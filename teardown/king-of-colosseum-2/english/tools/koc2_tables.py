#!/usr/bin/env python3
"""koc2_tables.py — parse King of Colosseum II's plain-text data tables.

KC2FIRE.000 ships several data files as human-readable text (found
2026-11-19). This tool parses the three non-ACW kinds into JSON:

  file 02031 — AFS FILE ID HEADER (388,097 bytes): a C header the
      developers left in the game data:
        /* '..\\kc2fire\\data\\kc2fire.afs' FILE ID Header */
        #define K06_ADX (0) /* k06.adx */
      One #define per AFS file (9,003), mapping the game's symbol
      (K06_ADX) to the AFS file id (0) and filename (k06.adx).
      Confirms the AFS index order and gives every audio clip its
      in-code name. The commentary codes in file 02030 (a1, b1644,
      ...) line up with these ids (a0001.adx = id 20, ...).
  files 02893-02900 — THRESHOLD TABLES (8 files): rows of
      "value<TAB>score" in blocks, e.g. 2000->90, 1900->85, ...
      1000->50, then 7000->90 ... 4000->50, 15000->90 ... 8000->50,
      60000->90 ... 30000->50. The blocks look like venue scales
      (small hall to Tokyo Dome at 60,000) mapping a raw number
      (attendance) to a score 50-90 — very likely the Audience
      Ranking / Match Maker attendance scoring. The 8 files differ
      in which blocks they include (mode/difficulty variants?).
      Labelled "threshold_tables" with the venue-scale reading
      marked as interpretation, not fact.
  files 02401-02402 — GRADE GRIDS (2 files): 5x5 blocks of letter
      grades (D, C, B, BC, CD, BCD) separated by blank lines.
      Unidentified: possibly a move/rank grade matrix. Kept verbatim
      as grids; no interpretation is asserted.

Usage:
  koc2_tables.py <kc2fire000-dir> <outdir>
  Writes afs-ids.json, threshold-tables.json, grade-grids.json.

Lane E (KoC2), 2026-11-19.
"""
import json
import re
import sys
from pathlib import Path

AFS_HEADER = "file02031.bin"
GRADE_FILES = ["file02401.bin", "file02402.bin"]
THRESHOLD_FILES = [f"file0289{i}.bin" for i in range(3, 10)] + ["file02900.bin"]

DEFINE_RE = re.compile(r"#define\s+(\w+)\s+\((\d+)\)\s*/\*\s*(\S+)\s*\*/")


def parse_afs_header(text: str):
    entries = []
    for m in DEFINE_RE.finditer(text):
        entries.append({"symbol": m.group(1), "id": int(m.group(2)),
                        "file": m.group(3)})
    return {"source": "KC2FIRE.000 file 02031",
            "note": "C header left in the game data; maps AFS file ids to symbols",
            "count": len(entries), "entries": entries}


def parse_thresholds(text: str):
    # Rows are "value<TAB>score" with no blank-line separators; a new
    # block starts whenever the score resets to 90. Each block is 8
    # rows: scores 90, 85, 80, 75, 70, 65, 60, 50.
    blocks = []
    block = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            value, score = int(parts[0]), int(parts[1])
            if score == 90 and block:
                blocks.append(block)
                block = []
            block.append([value, score])
    if block:
        blocks.append(block)
    return blocks


def parse_grades(text: str):
    # Grids are 5 rows of 5 tab-separated grades, with no blank-line
    # separators; split every 5 rows.
    rows = [ln.split("\t") for ln in text.splitlines() if ln.strip()]
    return [rows[i:i + 5] for i in range(0, len(rows), 5)]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, outdir = Path(argv[1]), Path(argv[2])
    outdir.mkdir(parents=True, exist_ok=True)

    afs = parse_afs_header((src / AFS_HEADER).read_text(errors="replace"))
    (outdir / "afs-ids.json").write_text(
        json.dumps(afs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"afs-ids.json: {afs['count']} entries")

    thresholds = {}
    for fn in THRESHOLD_FILES:
        p = src / fn
        if p.exists():
            thresholds[fn] = parse_thresholds(p.read_text(errors="replace"))
    (outdir / "threshold-tables.json").write_text(
        json.dumps({"source": "KC2FIRE.000 files 02893-02900",
                    "note": "value -> score (50-90) blocks; blocks look like "
                            "venue scales (2k / 7k / 15k / 60k seats); "
                            "attendance-to-audience-score reading is "
                            "interpretation, not verified fact",
                    "files": thresholds},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"threshold-tables.json: {len(thresholds)} files, "
          f"{sum(len(v) for v in thresholds.values())} blocks")

    grades = {}
    for fn in GRADE_FILES:
        p = src / fn
        if p.exists():
            grades[fn] = parse_grades(p.read_text(errors="replace"))
    (outdir / "grade-grids.json").write_text(
        json.dumps({"source": "KC2FIRE.000 files 02401-02402",
                    "note": "5x5 letter-grade grids; purpose unidentified",
                    "files": grades},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"grade-grids.json: {len(grades)} files, "
          f"{sum(len(v) for v in grades.values())} grids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
