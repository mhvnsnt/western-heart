#!/usr/bin/env python3
"""Catalog all .yanm clips under given roots into a JSON summary."""
import glob, json, sys
from collections import Counter
import yanm

roots = sys.argv[1:-1] or ['unpack-moves']
out_path = sys.argv[-1]
files = []
for r in roots:
    files += glob.glob(f"{r}/**/*.yanm", recursive=True)
files.sort()
print(f"{len(files)} clips")
cat = {"clips": len(files), "by_bones": Counter(), "hashes": Counter(),
       "special_entries": 0, "bad_parts": 0, "entries": []}
for f in files:
    try:
        y = yanm.load(f)
    except Exception:
        continue
    cat["by_bones"][len(y.bones)] += 1
    bones = []
    for b in y.bones:
        cat["hashes"][f"{b['bone_hash']:08X}"] += 1
        if b.get("special"):
            cat["special_entries"] += 1
        if not b.get("part_a_ok", True) or not b.get("part_b_ok", True):
            cat["bad_parts"] += 1
        bones.append(b["bone"] or f"{b['bone_hash']:08X}")
    cat["entries"].append({"path": f, "bytes": len(y.data),
                           "bones": len(y.bones), "names": bones})
cat["by_bones"] = dict(sorted(cat["by_bones"].items()))
cat["hashes"] = dict(cat["hashes"].most_common())
with open(out_path, "w") as fh:
    json.dump(cat, fh, indent=1)
print(f"bone-count histogram: {cat['by_bones']}")
print(f"distinct hashes: {len(cat['hashes'])}, "
      f"special entries: {cat['special_entries']}, "
      f"bad parts: {cat['bad_parts']}")
print(f"wrote {out_path}")
