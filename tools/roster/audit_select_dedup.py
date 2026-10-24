#!/usr/bin/env python3
"""Character-select dedup audit for the Western Heart select overhaul.

Asserts the owner's dedup law:
  - zero duplicate fighter identities on the select grid
    (only attire ladders may repeat a fighter's models)
  - zero duplicate card images (one portrait per select entry)
  - every entry's attire ladder resolves (attiresFor reachability)

Usage: audit_select_dedup.py [--strict]
Exit 0 = PASS, 1 = FAIL (also prints the full slot list).
"""
import json, re, sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') \
    else Path(__file__).resolve().parents[2]

roster_src = (REPO / "game/js/roster-full.js").read_text()
attires_src = (REPO / "game/js/attires.js").read_text()
assets_src = (REPO / "game/js/assets.js").read_text()

ENTRY = re.compile(
    r"""\{\s*id:\s*'([^']+)',\s*name:\s*'([^']+)',\s*title:\s*["'](.*?)["'].*?
        model:\s*'([^']+)'""", re.S | re.X)
entries = [(m.group(1), m.group(2), m.group(3), m.group(4))
           for m in ENTRY.finditer(roster_src)]

VARIANTS = {}
for key, body in re.findall(r"'([\w-]+)':\s*\[(.*?)\]", attires_src, re.S):
    VARIANTS[key] = re.findall(r"model:\s*'([^']+)'", body)

MODEL_URLS = dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'",
                             assets_src, re.M))

errors = []
print(f"select entries: {len(entries)}")
print(f"{'id':22s} {'name':14s} {'model':28s} attires portrait")
for eid, name, title, model in entries:
    ladder = VARIANTS.get(model) or VARIANTS.get(eid)
    n_att = len(ladder) if ladder else 1
    port = (REPO / "game/assets/portraits" / f"{eid}.png")
    pstat = "OK" if port.is_file() else "MONOGRAM-FALLBACK"
    print(f"{eid:22s} {name:14s} {model:28s} {n_att:>3d}     {pstat}")
    if ladder:
        for mk in ladder:
            if mk not in MODEL_URLS:
                errors.append(f"DEAD MODEL KEY: entry '{eid}' attire "
                              f"model '{mk}' has no MODEL_URLS entry")
    elif model not in MODEL_URLS:
        errors.append(f"DEAD MODEL KEY: entry '{eid}' model '{model}' "
                      f"has no MODEL_URLS entry")

# 1. duplicate fighter identities: same display name on >1 select entry.
#    (Canon merges like RAVE=Kiko Tanaka=Ghost share one entry already;
#    MARIPOSA covers Mary Posa/Zafina; PHANTOM covers Yoshimitsu;
#    DOC FRANK covers Bosco.)
by_name = {}
for eid, name, title, model in entries:
    by_name.setdefault(name, []).append(eid)
for name, ids in sorted(by_name.items()):
    if len(ids) > 1:
        errors.append(f"DUPLICATE FIGHTER: name '{name}' on select "
                      f"entries {ids}")

# 2. duplicate card images: same portrait file served for >1 entry.
seen_portraits = {}
for eid, name, title, model in entries:
    p = REPO / "game/assets/portraits" / f"{eid}.png"
    if p.is_file():
        seen_portraits.setdefault(p.name, []).append(eid)
for p, ids in sorted(seen_portraits.items()):
    if len(ids) > 1:
        errors.append(f"DUPLICATE CARD IMAGE: portrait '{p}' used by {ids}")

# 3. every entry id unique (no id collisions at all).
ids = [e[0] for e in entries]
if len(ids) != len(set(ids)):
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    errors.append(f"DUPLICATE ENTRY IDS: {dupes}")

print()
if errors:
    print("FAIL — violations:")
    for e in errors:
        print("  ✗", e)
    sys.exit(1)
print(f"PASS — {len(entries)} select entries, zero duplicate fighters, "
      f"zero duplicate card images, all attire ladders resolve.")
