#!/usr/bin/env python3
"""build_roster_attires.py — scan roster/*/attires/** for GLBs and emit
customization/creation-suite-ui/data/roster-attires.json.

One entry per (fighter, attire directory):
  { fighter, fighter_name, attire_id, attire_name, dir, glb, variants[],
    slots_md, customization_json }
Primary GLB preference: *-rigged.glb > model.glb > first GLB (sorted).
Display names come from the fighter's ATTIRE-SLOTS.md where a slot line
mentions the attire; otherwise the directory name is humanized.
Run from anywhere:  python3 customization/build_roster_attires.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "roster"
OUT = ROOT / "customization" / "creation-suite-ui" / "data" / "roster-attires.json"


def humanize(slug: str) -> str:
    return re.sub(r"[-_]+", " ", slug).strip().title()


def slots_names(md: Path):
    """Best-effort display names from ATTIRE-SLOTS.md: lines like
    '- **Attire 3** — "Master's White" ...' or '| 3 | **Name** |'."""
    names = []
    if not md or not md.exists():
        return names
    for line in md.read_text(errors="ignore").splitlines():
        m = re.search(r"(?:Attire|Slot)\s*\d+\s*(?:\(DEFAULT\))?\s*[—\-:|]*\s*\**\"?([^\"*|—]{3,60})", line)
        if m:
            t = m.group(1).strip(" -*")
            if t and not t.lower().startswith(("the ", "slot")):
                names.append(t)
    return names


def pick_primary(glbs):
    def rank(p: Path):
        n = p.name.lower()
        if n.endswith("-rigged.glb"):
            return 0
        if n == "model.glb":
            return 1
        if "rigged" in n:
            return 2
        return 3
    return sorted(glbs, key=lambda p: (rank(p), p.name))[0]


def main():
    fighters = []
    total_attires = 0
    for fdir in sorted(p for p in ROSTER.iterdir() if p.is_dir()):
        att_root = fdir / "attires"
        if not att_root.is_dir():
            continue
        md = fdir / "ATTIRE-SLOTS.md"
        if not md.exists() and (att_root / "ATTIRE-SLOTS.md").exists():
            md = att_root / "ATTIRE-SLOTS.md"
        names = slots_names(md if md.exists() else None)
        attires = []
        # attire dirs = immediate children of attires/ containing GLBs anywhere below
        for adir in sorted(p for p in att_root.iterdir() if p.is_dir()):
            glbs = sorted(adir.rglob("*.glb"))
            if not glbs:
                continue
            primary = pick_primary(glbs)
            idx = len(attires)
            attires.append({
                "attire_id": adir.name,
                "attire_name": names[idx] if idx < len(names) else humanize(adir.name),
                "dir": adir.relative_to(ROOT).as_posix(),
                "glb": primary.relative_to(ROOT).as_posix(),
                "variants": [g.relative_to(ROOT).as_posix() for g in glbs],
                "customization_json": (adir / "customization.json").relative_to(ROOT).as_posix()
                    if (adir / "customization.json").exists() else None,
            })
        if attires:
            total_attires += len(attires)
            fighters.append({
                "fighter": fdir.name,
                "fighter_name": humanize(fdir.name),
                "slots_md": md.relative_to(ROOT).as_posix() if md.exists() else None,
                "attires": attires,
            })
    data = {"version": 1, "app": "wh-creation-suite", "source": "build_roster_attires.py scan of roster/*/attires/**",
            "fighters": fighters}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"fighters={len(fighters)} attires={total_attires} -> {OUT.relative_to(ROOT)}")
    for f in fighters:
        print(f"  {f['fighter']}: {len(f['attires'])} attires")
    return 0


if __name__ == "__main__":
    sys.exit(main())
