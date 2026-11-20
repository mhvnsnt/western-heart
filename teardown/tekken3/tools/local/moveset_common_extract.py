#!/usr/bin/env python3
"""Extract the Tekken 3 COMMON bank (divmot99) — the shared move bank every
character bank references through `common:N` move-index entries — plus the
shared branch-block table that `<common>` CALL records splice in.

Provenance chain (all inputs in-repo):
  teardown/tekken3/disc/files/TEKKEN3/TEKKEN3.BNS  (disc archive)
  teardown/tekken3/bns-table.pkl                   (record index: id, sector, size)
  teardown/tekken3/disc/files/TEKKEN3/SLUS_004.02  (USA EXE: sequence tables
                                                    + the branch-block table)

divmot99 is BNS record 279 (sector 15104, 240468 bytes;
docs/BNS-ORGANIZATION-PATTERN.md motion table). Its SHA-256 must equal
n0madic's original-disc index value (asserted below). The bank is parsed with
the same extractor family as the 20 character banks
(tools/local/moveset_extract.py + the Tekken3Remake `motion` module).
Control: divmot03 (King, BNS record 283) is re-extracted and must reproduce
the shipped moveset_king.json moves + move_index exactly.

Engine semantics (verified against the Tekken3Remake engine port,
fight_sim.py BranchFind 0x8002E078 / MoveBranchStep 0x8002DC3C):
- A branch record with command 0xC00C ("<common>") is a CALL: the branch list
  spliced in is `entry` records from the EXE branch-block table at VA
  0x80017C78 (SLUS_004.02 file offset 0x8478), starting at record
  `target_slot`, followed by a RETURN (0xC00D) record.
- A matched branch's target move is move_lookup(slot): the slot resolves
  through the ACTIVE character bank's move_index (int = local row,
  0x3FFFFFFF = none, >= 0x40000000 = common row value - 0x40000000).
- divmot99 itself has NO move-index section (section 2 size is 0); branch
  targets inside common rows and EXE blocks resolve the same way, through
  the active character's index.

Output (teardown/tekken3/movesets/): moveset_common.json + moveset_common.csv
in the same schema as the 20 character-bank artifacts, with two additive
top-level keys: branch_blocks (the EXE table blocks, keyed by start record)
and move_index_note. move_index is [] (no such section exists in divmot99).
"""
from __future__ import annotations

import csv
import hashlib
import json
import pickle
import struct
import sys
from pathlib import Path

LOCAL = Path(__file__).resolve().parent
RESEARCH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(LOCAL))
sys.path.insert(0, str(RESEARCH))
import motion  # noqa: E402
import moveset_extract as mx  # noqa: E402

T3 = LOCAL.parents[1]  # teardown/tekken3
BNS_REC_COMMON = 279
BNS_REC_KING = 283
SHA_DIVMOT99 = "2a8c754adf1f222fbac64bb9775cfdec106ce017f12e45803ec572baa6ffd241"
SHA_DIVMOT03 = "8ae24919a89ac81adc6d34f1ef35cbb3ccafd19c55dafe820c923bbd638da899"
BLOCK_TABLE_VA = 0x80017C78
EXE_BASE, EXE_HEADER = 0x80010000, 0x800


def slice_bns(bns: bytes, table: list, rec_id: int) -> bytes:
    rid, sector, size = next(r for r in table if r[0] == rec_id)
    return bns[sector * 2048: sector * 2048 + size]


def read_record(exe: bytes, seqs, p: int) -> dict:
    cmd = struct.unpack_from("<H", exe, p)[0]
    return {"command": mx.command_text(cmd, seqs), "command_hex": f"{cmd:#06x}",
            "restriction": exe[p + 2], "condition": exe[p + 3],
            "condition_param": struct.unpack_from("<H", exe, p + 4)[0],
            "target_slot": struct.unpack_from("<H", exe, p + 6)[0],
            "flags": exe[p + 8], "first": exe[p + 9], "last": exe[p + 10],
            "entry": exe[p + 11]}


def main() -> int:
    bns = (T3 / "disc/files/TEKKEN3/TEKKEN3.BNS").read_bytes()
    exe = (T3 / "disc/files/TEKKEN3/SLUS_004.02").read_bytes()
    table = pickle.loads((T3 / "bns-table.pkl").read_bytes())
    seqs = mx.load_seq_tables(exe)

    common_data = slice_bns(bns, table, BNS_REC_COMMON)
    assert hashlib.sha256(common_data).hexdigest() == SHA_DIVMOT99, "divmot99 sha mismatch"
    king_data = slice_bns(bns, table, BNS_REC_KING)
    assert hashlib.sha256(king_data).hexdigest() == SHA_DIVMOT03, "divmot03 sha mismatch"
    tmp = Path("/tmp/_t3common_check")
    tmp.mkdir(exist_ok=True)
    (tmp / "divmot99_common.bin").write_bytes(common_data)
    (tmp / "divmot03_king.bin").write_bytes(king_data)

    common = motion.parse_bank(common_data)
    print(f"common bank: {common.move_count} moves (type {common.type_code})")

    def conv(ms: dict) -> dict:
        js = dict(ms)
        js["move_index"] = [r if r < 0x40000000 else f"common:{r - 0x40000000}"
                            for r in ms["move_index"]]
        return js

    # control: king re-extraction must equal the shipped artifact
    king_js = conv(mx.extract_bank(tmp / "divmot03_king.bin", exe, seqs, common, common_data))
    shipped = json.loads((T3 / "movesets/moveset_king.json").read_text())
    assert king_js["moves"] == shipped["moves"] and king_js["move_index"] == shipped["move_index"], \
        "control failed: king re-extraction != shipped moveset_king.json"
    print("control: king re-extraction == shipped moveset_king.json (moves + move_index)")

    cms = mx.extract_bank(tmp / "divmot99_common.bin", exe, seqs, common, common_data)
    total = sum(len(m["branches"]) for m in cms["moves"])
    sec0 = (common.bounds[1] - common.bounds[0]) // 12
    assert total == sec0, f"branch records {total} != section-0 records {sec0}"
    print(f"common rows account for all {sec0} section-0 branch records")

    # CALL census across every shipped bank + the common bank itself
    callentry: dict[int, set] = {}
    def scan(moves):
        for m in moves:
            for b in m["branches"]:
                if b.get("command") == "<common>":
                    callentry.setdefault(b["target_slot"], set()).add(b.get("entry"))
    banks_dir = T3 / "movesets"
    for p in sorted(banks_dir.glob("moveset_*.json")):
        if p.name != "moveset_common.json":
            scan(json.loads(p.read_text())["moves"])
    scan(cms["moves"])
    print(f"CALL blocks referenced: {len(callentry)}")

    base = BLOCK_TABLE_VA - EXE_BASE + EXE_HEADER
    blocks = {}
    for idx in sorted(callentry):
        lens = callentry[idx]
        assert len(lens) == 1, f"block {idx}: inconsistent entry bytes {lens}"
        n = next(iter(lens))
        recs = [read_record(exe, seqs, base + 12 * (idx + k)) for k in range(n)]
        term = struct.unpack_from("<H", exe, base + 12 * (idx + n))[0]
        assert term == 0xC00D, f"block {idx}: no RETURN after {n} records"
        assert all(r["command"] != "<common>" for r in recs), f"block {idx}: nested CALL"
        blocks[str(idx)] = recs
    print(f"blocks extracted from EXE table: {len(blocks)} (RETURN-verified, no nested CALLs)")

    out = {"bank": "divmot99_common.bin", "bank_type": 99,
           "move_count": cms["move_count"], "moves": cms["moves"], "move_index": [],
           "move_index_note": ("divmot99 has no move-index section (section 2 size 0). "
                               "Branch targets in common rows and in branch_blocks resolve "
                               "through the ACTIVE character bank's move_index "
                               "(engine: MoveBranchStep -> move_lookup via the fighter's bank)."),
           "branch_blocks": blocks,
           "branch_blocks_note": ("Shared branch lists spliced in by <common> CALL records "
                                  "(cmd 0xC00C). Stored in the game EXE at VA 0x80017C78 "
                                  "(SLUS_004.02 file offset 0x8478); block = entry-count "
                                  "records followed by a RETURN (0xC00D) record. "
                                  "Key = start record index in that table.")}
    (banks_dir / "moveset_common.json").write_text(json.dumps(out, indent=1))
    with open(banks_dir / "moveset_common.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=mx.CSV_FIELDS)
        w.writeheader()
        for m in cms["moves"]:
            inputs = "; ".join(
                f"{br['command']}->{br['target_slot']}[{br['first']}-{br['last']}]"
                for br in m["branches"] if br.get("command") not in ("<end>", None))
            w.writerow({k: m.get(k) for k in mx.CSV_FIELDS
                        if k not in ("n_branches", "n_events", "inputs")} | {
                "n_branches": len([b for b in m["branches"] if b.get("command") not in ("<end>", None)]),
                "n_events": len(m["events"]), "inputs": inputs})
    print("wrote moveset_common.json + moveset_common.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
