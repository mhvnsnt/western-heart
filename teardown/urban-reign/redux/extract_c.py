#!/usr/bin/env python3
"""Lane 2 extraction step C: per-fighter gap map + extract 100%-covered files.

For every one of the 25 fighters (23 roster + 6 stock-slot, overlap noted):
- model VMD + package PPK entry indices (from manifest roster / AFS names)
- parts-coverage + exact gap list (file-relative offsets, sizes)
- if 100%: extract real bytes to extracted/fighters/<Name>/{model.vmd,package.ppk} + sha256
- if <100%: NO file written; gaps recorded (bytes live only in Jay's source ISO)

Then parse each extracted file with the author's own roster-lib tools:
- VMD: toolnative.vmd_structure.parse_vmd (+ vmd_mesh.read_mesh counts)
- PPK: toolnative.ppk_index.ppk_entries (+ scan members for GYU banks)

Also: copies src!=dst analysis (where the output disc grew vs the source).
"""
import bisect, hashlib, json, struct, sys
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
FIGHTERS = ROOT / "extracted" / "fighters"
TOOLS = ROOT / "work" / "tools" / "vendor"
sys.path.insert(0, str(TOOLS / "roster-lib"))
sys.path.insert(0, str(TOOLS / "mod-manager"))
H = lambda b: hashlib.sha256(b).hexdigest()

manifest = json.loads((CORE / "manifest.json").read_text())
layout = manifest["layout"]
d0 = json.load(open(CORE / "dvd000_table.json"))
by_idx = {r["index"]: r for r in d0}
by_name = {r["name"]: r for r in d0}

parts = sorted((p["offset"], p["length"], CORE / "parts" / Path(p["entry"]).name)
               for p in manifest["parts"])
poff = [p[0] for p in parts]


def gaps_for(base_off, size):
    """Return list of (file_rel_start, length) NOT covered by parts."""
    gaps = []
    cur = 0
    a, b = base_off, base_off + size
    i = bisect.bisect_right(poff, a) - 1
    if i < 0:
        i = 0
    pos = a
    while i < len(parts) and parts[i][0] < b:
        pa, pl, _ = parts[i]
        lo, hi = max(pa, a), min(pa + pl, b)
        if lo < hi:
            if lo > pos:
                gaps.append((pos - a, lo - pos))
            pos = max(pos, hi)
        i += 1
    if pos < b:
        gaps.append((pos - a, b - pos))
    return gaps


def read_entry_bytes(row):
    base = layout["DVD000"]["offset"]
    a = base + row["offset"]
    buf = bytearray(row["size"])
    i = bisect.bisect_right(poff, a) - 1
    if i < 0:
        i = 0
    while i < len(parts) and parts[i][0] < a + row["size"]:
        pa, pl, pf = parts[i]
        lo, hi = max(pa, a), min(pa + pl, a + row["size"])
        if lo < hi:
            data = pf.read_bytes()
            buf[lo - a:hi - a] = data[lo - pa:hi - pa]
        i += 1
    return bytes(buf)


# ---- fighter list: 23 roster + 6 stock-slot (CID map from extract_portraits.CID) ----
fighters = {}
for r in manifest["roster"]:
    fighters[r["character"]] = dict(cid=r["cid"], model=r["model"], package=r["package"])
stock = {"Leon": 0, "King": 19, "Hwoarang": 41, "Bryan": 43, "Heihachi": 53, "CJ": 97}
for name, cid in stock.items():
    if name in fighters:
        continue
    pkg = by_name[f"afs/safe/ppk/char{cid+1:03d}.ppk"]
    # chrNN suffix is decimal cid+1, zero-padded to 2 (chr01..chr99; chr00/chrA0/chrA1 are the 99..101 specials)
    mdl = by_name[f"converter/design/test/chr{cid+1:02d}.vmd"]
    fighters[name] = dict(cid=cid, model=mdl["index"], package=pkg["index"], stock_slot=True)

TARGET25 = ["Asuka", "Bryan", "Jin", "Kazuya", "King", "Nina", "Paul", "Yoshimitsu", "Hwoarang",
            "Heihachi", "Devil Jin", "Reina", "Kunimitsu", "Bob", "Christie", "Armor Queen",
            "Cammy", "Leon", "CJ", "Kiryu", "Jeff", "Snake", "Renamon", "Vergence", "Ricardo"]
assert set(TARGET25) <= set(fighters), set(TARGET25) - set(fighters)
assert len(fighters) == 29, len(fighters)  # 23 roster + 6 stock

report = {}
for name in sorted(fighters):
    f = fighters[name]
    rec = dict(cid=f["cid"], stock_slot=f.get("stock_slot", False))
    for kind, idx in (("model", f["model"]), ("package", f["package"])):
        row = by_idx[idx]
        gaps = gaps_for(layout["DVD000"]["offset"] + row["offset"], row["size"])
        cov = 1.0 - sum(g for _, g in gaps) / row["size"] if row["size"] else 1.0
        e = dict(index=idx, name=row["name"], size=row["size"], coverage=round(cov, 4),
                 gap_bytes=sum(g for _, g in gaps), gap_count=len(gaps),
                 gaps=[[s, l] for s, l in gaps[:20]])
        if cov == 1.0 and row["size"] > 0:
            dest = FIGHTERS / name
            dest.mkdir(parents=True, exist_ok=True)
            data = read_entry_bytes(row)
            fn = "model.vmd" if kind == "model" else "package.ppk"
            (dest / fn).write_bytes(data)
            (dest / (fn + ".sha256")).write_text(H(data) + f"  {fn}\n")
            e["extracted"] = f"extracted/fighters/{name}/{fn}"
            e["sha256"] = H(data)
        else:
            e["extracted"] = None
        rec[kind] = e
    report[name] = rec
    m, p = rec["model"], rec["package"]
    print(f"{name:12s} cid={rec['cid']:3d} model cov={m['coverage']:.3f} gaps={m['gap_count']} ({m['gap_bytes']} B) {'EXTRACTED' if m.get('extracted') else ''} | "
          f"pkg cov={p['coverage']:.3f} gaps={p['gap_count']} ({p['gap_bytes']} B) {'EXTRACTED' if p.get('extracted') else ''}")

json.dump(report, open(CORE / "fighter_entries.json", "w"), indent=1)

# copies: where does src != dst (disc growth)?
copies = manifest["copies"]
shifted = [c for c in copies if c[0] != c[1]]
print(f"\ncopies: {len(copies)} total, {len(shifted)} with src!=dst")
for c in shifted[:10]:
    print("  copy src=%d dst=%d len=%d" % tuple(c))
json.dump({"shifted_copies": shifted}, open(CORE / "shifted_copies.json", "w"))
print("DONE step C")
