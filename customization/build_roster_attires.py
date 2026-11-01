#!/usr/bin/env python3
"""build_roster_attires.py — scan roster/*/attires/** for GLBs and emit
customization/creation-suite-ui/data/roster-attires.json.

One entry per (fighter, attire directory):
  { fighter, fighter_name, attire_id, attire_name, dir, glb, variants[],
    slots_md, customization_json }
Primary GLB preference: *-rigged.glb > model.glb > first GLB (sorted).
Display names come from the fighter's ATTIRE-SLOTS.md where a slot line
mentions the attire; otherwise the directory name is humanized.

NAMES LAW (2026-11-01, AGENTS.md): a roster folder is often named after the source-game model it holds
(roster/armor-king, roster/lili, roster/zafina ...). The suite shows the WH fighter that uses the folder in the
game (display_name, from game/js/assets.js MODEL_URLS + game/data/roster_map.json); a folder no WH fighter uses
yet is "unassigned" and is shown as an unassigned base body, never under the source name. The primary GLB of an
attire is the one the game itself loads for it (MODEL_URLS) when there is one.
Run from anywhere:  python3 customization/build_roster_attires.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROSTER = ROOT / "roster"
OUT = ROOT / "customization" / "creation-suite-ui" / "data" / "roster-attires.json"
ASSETS_JS = ROOT / "game" / "js" / "assets.js"
ROSTER_MAP = ROOT / "game" / "data" / "roster_map.json"
DENYLIST = ROOT / "tools" / "canon" / "denylist.json"   # source-game names (the canon-names CI gate's list)


ROSTER_FULL = ROOT / "game" / "js" / "roster-full.js"


# WH characters that have a roster folder but are not on the game roster yet (owner canon; not source-game names)
WH_CANON_PENDING = {"THEORY", "TORCH", "SCIMITAR"}
FOLDER_NAMES = ROOT / "tools" / "canon" / "roster-folder-wh-names.json"   # owner-confirmed folder -> WH name


def roster_bases():
    """roster-full.js { id, name, base }: the source character each WH fighter is built on (base: 'Kuma' -> GASHADOKURO).
    Returns normalized base part -> WH name ('Zangief + Golem' gives both 'zangief' and 'golem')."""
    try:
        txt = ROSTER_FULL.read_text(errors="ignore")
    except OSError:
        return {}
    out = {}
    for m in re.finditer(r"\{\s*id:\s*'[^']+',\s*name:\s*'([^']+)'[^}]*?\bbase:\s*'([^']+)'", txt):
        name, base = m.group(1), m.group(2)
        for part in re.split(r"\s*[+/,&]\s*", base):
            key = re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-")
            if key:
                out.setdefault(key, name)
                out.setdefault(key.split("-")[0], name)   # 'iori-yagami' also answers 'iori'
    return out


def folder_wh_names():
    try:
        d = json.loads(FOLDER_NAMES.read_text())
    except (OSError, ValueError):
        return {}
    return {**d.get("derived_from_game_models", {}), **d.get("owner_confirmed", {})}


def wh_roster_names():
    """Every WH fighter display name in the game's roster (roster-full.js name: '...')."""
    try:
        txt = ROSTER_FULL.read_text(errors="ignore")
    except OSError:
        return set()
    return {m.group(1).upper() for m in re.finditer(r"\bname:\s*'([^']+)'", txt)}


def source_named(label: str) -> bool:
    try:
        terms = json.loads(DENYLIST.read_text()).get("terms", [])
    except (OSError, ValueError):
        terms = []
    return any(re.search(r"\b" + re.escape(t) + r"\b", label, re.I) for t in terms)


def game_model_index():
    """MODEL_URLS: model id -> repo path; folder -> model ids; model id -> WH fighter name."""
    urls = {}
    for m in re.finditer(r"'([A-Za-z0-9_-]+)'\s*:\s*'\.\./(roster/[^']+\.glb)'", ASSETS_JS.read_text(errors="ignore")):
        urls.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*'\.\./(roster/[^']+\.glb)'", ASSETS_JS.read_text(errors="ignore"), re.M):
        urls.setdefault(m.group(1), m.group(2))
    by_folder = {}
    for mid, path in urls.items():
        by_folder.setdefault(path.split("/")[1], set()).add(mid)
    names = {}
    try:
        for f in json.loads(ROSTER_MAP.read_text()).get("fighters", []):
            ids = {f.get("id")} | {a.get("model") for a in f.get("attires", []) if a.get("model")}
            for mid in ids:
                if mid and mid not in names:
                    names[mid] = f.get("name")
    except (OSError, ValueError):
        pass
    return urls, by_folder, names


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
    urls, by_folder, wh_names = game_model_index()
    roster_names = wh_roster_names()
    folder_names = folder_wh_names()
    bases = roster_bases()
    unassigned_n = 0
    game_paths = set(urls.values())
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
            used = [g for g in glbs if g.relative_to(ROOT).as_posix() in game_paths]
            primary = pick_primary(used) if used else pick_primary(glbs)
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
            ids = by_folder.get(fdir.name, set())
            wh = sorted({wh_names[i] for i in ids if wh_names.get(i)})
            if not wh:   # the WH fighter built on this source model (roster-full.js base: 'Kuma' -> GASHADOKURO)
                b = bases.get(fdir.name) or bases.get(fdir.name.split("-")[0])
                if b:
                    wh = [b]
            if fdir.name in folder_names:
                wh = [folder_names[fdir.name]]   # the owner's word wins
            own = humanize(fdir.name).upper()
            if not wh and (own in roster_names or own in WH_CANON_PENDING) and not source_named(own):
                wh = [own]          # a WH fighter whose folder the roster map does not list yet (GYOU, THEORY ...)
            if not wh:
                unassigned_n += 1
            fighters.append({
                "fighter": fdir.name,
                "fighter_name": humanize(fdir.name),
                # the WH fighter using this folder; else the folder's own name unless it is a source-game name
                "display_name": wh[0] if wh else f"UNASSIGNED BODY {unassigned_n}",
                "unassigned": not wh,
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
