#!/usr/bin/env python3
"""Which roster fighters have the owner's Tripo 3D models -> game/data/tripo-fighters.json.

Owner 2026-10-21: "it needs to actually show all the fighters that have tripo 3D models that I put
into the game first at the top like the first few rows ... it shouldn't be people like rin, byou
and such ... that don't have models in the top rows."

Evidence (no hand list):
  1. roster/TRIPO-REGISTRY.md rows marked ✅ (canonical registry, owner law: updated on every pull)
  2. the GLB files themselves: Tripo-generated glTF carries a 'tripo' marker in its JSON chunk
     (generator / node names). Checked for every model a fighter can wear: its model key and every
     ATTIRE_VARIANTS model (game/js/attires.js -> game/js/assets.js MODEL_URLS) plus
     roster/<folder>/attires/**/*.glb.
game/js/select-screen.js puts these fighters in the first rows. Re-run after any Tripo pull.
"""
import json, re, struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
roster_src = (REPO / "game/js/roster-full.js").read_text()
assets_src = (REPO / "game/js/assets.js").read_text()
attires_src = (REPO / "game/js/attires.js").read_text()

ENTRY = re.compile(r"\{\s*id:\s*'([^']+)',\s*name:\s*'([^']+)'[^}]*?model:\s*'([^']+)'", re.S)
URLS = dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", assets_src, re.M))
# ATTIRE_VARIANTS: 'key': [ { model: 'x' ...}, ... ]
VARIANTS = {}
for key, body in re.findall(r"'([\w-]+)':\s*\[(.*?)\]", attires_src, re.S):
    VARIANTS[key] = re.findall(r"model:\s*'([^']+)'", body)


def glb_is_tripo(p):
    try:
        with open(p, "rb") as f:
            h = f.read(20)
            if h[:4] != b"glTF":
                return False
            n = struct.unpack("<I", h[12:16])[0]
            return b"tripo" in f.read(n).lower()
    except OSError:
        return False


def url_path(key):
    u = URLS.get(key)
    if not u:
        return None
    return (REPO / "game" / u).resolve()


def folder_for(fid, name):
    cands = [fid, fid.replace("_", "-"), name.lower().replace(" ", "-"), re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")]
    for c in cands:
        if (REPO / "roster" / c).is_dir():
            return c
    return None


registry = set()
for line in (REPO / "roster/TRIPO-REGISTRY.md").read_text().splitlines():
    cells = [c.strip() for c in line.split("|")]
    if len(cells) > 3 and "✅" in cells[2]:
        for part in re.split(r"/|\(|=", cells[1]):
            part = re.sub(r"[^A-Z0-9 -]", "", part.upper()).strip()
            if part:
                registry.add(part)

out, evidence = [], {}
for fid, name, model in ENTRY.findall(roster_src):
    ev = []
    nm = re.sub(r"[^A-Z0-9 -]", "", name.upper()).strip()
    if nm in registry:
        ev.append("roster/TRIPO-REGISTRY.md ✅")
    keys = [model] + VARIANTS.get(model, []) + VARIANTS.get(fid, [])
    for k in dict.fromkeys(keys):
        p = url_path(k)
        if p and glb_is_tripo(p):
            ev.append(f"{p.relative_to(REPO)} (tripo marker)")
    fol = folder_for(fid, name)
    if fol:
        for p in sorted((REPO / "roster" / fol / "attires").glob("**/*.glb")):
            if glb_is_tripo(p):
                ev.append(f"{p.relative_to(REPO)} (tripo marker)")
    if ev:
        out.append(fid)
        evidence[fid] = sorted(set(ev))
doc = {"format": "wh-tripo-fighters/1", "tool": "tools/roster/tripo_fighters.py",
       "rule": "fighters with the owner's Tripo models show first on the select screen (owner 2026-10-21)",
       "ids": out, "evidence": evidence}
dst = REPO / "game/data/tripo-fighters.json"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(f"{len(out)} roster fighters with Tripo models -> {dst.relative_to(REPO)}")
print(", ".join(out))
