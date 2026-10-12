#!/usr/bin/env python3
"""No Mercy ROM structural analysis — reproducible teardown tooling.
ROM: WWF No Mercy (USA) (Rev-A).z64, 32MB, big-endian (.z64).

Findings documented in ../docs/CHARACTER-DATA.md and ../docs/NOMERCY-TEARDOWN.md.
Usage: python3 analyze_nomercy.py [--dump-ids] [--dump-seg]
"""
import json, os, struct, sys

ROM = os.path.join(os.path.dirname(__file__), "..", "WWF No Mercy (USA) (Rev-A).z64")

def load():
    with open(ROM, "rb") as f:
        return f.read()

# --- Table A: wrestler display-name / internal-ID table @ 0x168D930 ---
WRESTLER_TABLE = 0x168D930
def parse_wrestler_table(d):
    base = WRESTLER_TABLE
    assert d[base:base+2] == b"\x00\x00", "pad bytes changed"
    count = d[base+2]
    i = base + 3
    recs = []
    for _ in range(count):
        wid = d[i]
        j = d.find(b"\x00", i + 1)
        name = d[i+1:j].decode("ascii")
        recs.append({"id": wid, "name": name, "table_offset": f"0x{i:08X}"})
        i = j + 1
    return recs, i

# --- 0x13E000 data segment: FF-separated mixed tables ---
SEG_START, SEG_END = 0x13E000, 0x142000
def parse_segment(d):
    seg = d[SEG_START:SEG_END]
    recs = []
    i = 0
    while i < len(seg):
        if seg[i:i+4] == b"\xff\xff\xff\xff":
            i += 4
            continue
        j = i
        while j < len(seg) and seg[j:j+4] != b"\xff\xff\xff\xff":
            j += 4
        payload = seg[i:j]
        recs.append({"offset": SEG_START+i, "len": len(payload),
                     "u32_head": [f"0x{v:08X}" for v in
                                  struct.unpack(f">{min(len(payload)//4,8)}I", payload[:32])]})
        i = j
    return recs

def classify(rec):
    """Heuristic classification of a segment record."""
    head = rec["u32_head"]
    if not head:
        return "empty"
    vals = [int(h, 16) for h in head]
    if all(v < 0x100 for v in vals):
        return "u32 small-int list (move/attr IDs)"
    if all(0x80000000 <= v < 0x80800000 for v in vals[:4]):
        return "RAM pointer table (0x80xxxxxx, KSEG0)"
    floats = []
    for h in head[:4]:
        try:
            floats.append(struct.unpack(">f", struct.pack(">I", int(h,16)))[0])
        except Exception:
            pass
    if all(abs(f) < 10000 and f == f for f in floats):
        return "float table (positions/anim keys?)"
    return "mixed/binary"

def main():
    d = load()
    print(f"ROM size: {len(d)} bytes, CRC32: {__import__('zlib').crc32(d) & 0xFFFFFFFF:08X}")
    if "--dump-ids" in sys.argv or len(sys.argv) == 1:
        recs, end = parse_wrestler_table(d)
        print(f"\nwrestler table: {len(recs)} entries, ends 0x{end:08X}")
        for r in recs:
            print(f"  id={r['id']:3d}  {r['name']}")
        out = os.path.join(os.path.dirname(__file__), "..", "docs", "wrestler-id-table.json")
        json.dump(recs, open(out, "w"), indent=1)
        print("saved", out)
    if "--dump-seg" in sys.argv or len(sys.argv) == 1:
        print("\n0x13E000 segment records:")
        for rec in parse_segment(d):
            print(f"  0x{rec['offset']:08X} len={rec['len']:6d}  {classify(rec)}")

if __name__ == "__main__":
    main()
