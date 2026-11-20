#!/usr/bin/env python3
"""
wire-fighter.py — generate game wiring for a new fighter.

Bottleneck #4 in the 2026-10-19 roster audit: game wiring is manual —
3 JS files hand-edited per fighter. This generator does it from one
command:

    python3 tools/wire-fighter/wire-fighter.py \\
        --id thor-attire3 --model ../roster/thor/attires/attire3/model.glb \\
        --moveset bryan --name THOR --title "Thunder God" --base "Jack" \\
        --suit 0x2a3a5a --trim 0xffcc00 --style "Power" --archetype "Grappler"

It updates (idempotent — existing ids are skipped, never duplicated):
  1. game/js/assets.js      -> MODEL_URLS['<id>'] = '<model>'
  2. game/js/fighter.js     -> MOVESET_MAP['<id>'] = '<moveset>'
  3. game/js/roster-full.js -> FULL_ROSTER entry { id, name, title, base,
                               moveset, model, tintStrength, colors, style,
                               archetype }

Model path is stored as given (relative to game/js/, matching the existing
convention: 'assets/models/x.glb' or '../roster/<f>/attires/<a>/model.glb').

Safety:
  --dry-run prints the diff without writing.
  Every write keeps a .bak next to the file.
  Refuses unknown moveset families (must exist in fighter.js MOVESET_MAP).
  Verifies the model file exists (relative to repo root or game/).
  node --check validates each edited file (when node is available).
"""
import argparse, os, re, shutil, subprocess, sys

REPO = os.environ.get("WH_REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
ASSETS_JS = os.path.join(REPO, "game", "js", "assets.js")
FIGHTER_JS = os.path.join(REPO, "game", "js", "fighter.js")
ROSTER_JS = os.path.join(REPO, "game", "js", "roster-full.js")

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

def parse_args():
    p = argparse.ArgumentParser(description="wire a fighter into game/js")
    p.add_argument("--id", required=True, help="fighter id (lowercase, dashes)")
    p.add_argument("--model", required=True, help="model path as stored in MODEL_URLS")
    p.add_argument("--moveset", required=True, help="moveset family (must exist in MOVESET_MAP)")
    p.add_argument("--name", default=None, help="display name (default: ID uppercased)")
    p.add_argument("--title", default="New Fighter")
    p.add_argument("--base", default="Original", help="Tekken base character")
    p.add_argument("--suit", default="0x3a3a4a", help="suit color hex, e.g. 0x1a3a6b")
    p.add_argument("--trim", default="0xcccccc", help="trim color hex")
    p.add_argument("--style", default="Mishima Karate")
    p.add_argument("--archetype", default="Balanced")
    p.add_argument("--tint", type=float, default=0.25)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="allow re-wiring an id that already exists (updates in place)")
    return p.parse_args()

def read(path):
    with open(path) as f:
        return f.read()

def write(path, text):
    shutil.copy2(path, path + ".bak")
    with open(path, "w") as f:
        f.write(text)

def moveset_families(fighter_js):
    m = re.search(r"const MOVESET_MAP = \{(.*?)\n\};", fighter_js, re.S)
    fams = set(re.findall(r":\s*'([a-z0-9_]+)'", m.group(1)))
    fams |= set(re.findall(r"^\s*([a-z0-9_]+)\s*:", m.group(1), re.M))
    return fams

def model_exists(model_path):
    # model paths in MODEL_URLS are relative to game/js/
    cands = [os.path.join(REPO, "game", "js", model_path),
             os.path.join(REPO, "game", model_path),
             os.path.join(REPO, model_path)]
    return any(os.path.exists(c) for c in cands)

def main():
    a = parse_args()
    if not ID_RE.match(a.id):
        raise SystemExit(f"bad id '{a.id}' (use lowercase letters, digits, dashes)")
    if not model_exists(a.model):
        raise SystemExit(f"model not found: {a.model} (checked game/js/, game/, repo root)")

    assets = read(ASSETS_JS)
    fighter = read(FIGHTER_JS)
    roster = read(ROSTER_JS)

    fams = moveset_families(fighter)
    if a.moveset not in fams:
        raise SystemExit(f"unknown moveset '{a.moveset}'. Known: {sorted(fams)}")

    exists = {
        "assets.js": re.search(rf"^\s*['\"]?{re.escape(a.id)}['\"]?\s*:", assets, re.M),
        "fighter.js": re.search(rf"^\s*['\"]?{re.escape(a.id)}['\"]?\s*:", fighter, re.M),
        "roster-full.js": re.search(rf"id:\s*'{re.escape(a.id)}'", roster),
    }
    if any(exists.values()) and not a.force:
        raise SystemExit(f"id '{a.id}' already wired in "
                         f"{[k for k, v in exists.items() if v]} — use --force to update")

    name = a.name or a.id.upper().replace("-", " ").replace("_", " ")

    # 1. assets.js — MODEL_URLS (anchored on the dict's own block)
    new_assets = re.sub(
        rf"(^\s*['\"]?{re.escape(a.id)}['\"]?\s*:\s*'[^']*',?\n)",
        "", assets, flags=re.M) if a.force else assets
    if not re.search(rf"^\s*['\"]?{re.escape(a.id)}['\"]?\s*:", new_assets, re.M):
        mu = re.search(r"const MODEL_URLS = \{(.*?)\n\};", new_assets, re.S)
        if not mu:
            raise SystemExit("MODEL_URLS block not found in assets.js")
        block_new = mu.group(1) + f"\n  '{a.id}': '{a.model}',"
        new_assets = (new_assets[:mu.start(1)] + block_new +
                      new_assets[mu.end(1):])

    # 2. fighter.js — MOVESET_MAP (anchored on the MAP's own block, not MOVES)
    new_fighter = re.sub(
        rf"(^\s*['\"]?{re.escape(a.id)}['\"]?\s*:\s*'[a-z0-9_]+',?\n)",
        "", fighter, flags=re.M) if a.force else fighter
    if not re.search(rf"^\s*['\"]?{re.escape(a.id)}['\"]?\s*:", new_fighter, re.M):
        mm = re.search(r"const MOVESET_MAP = \{(.*?)\n\};", new_fighter, re.S)
        if not mm:
            raise SystemExit("MOVESET_MAP block not found in fighter.js")
        block_new = mm.group(1) + f"\n  '{a.id}': '{a.moveset}',"
        new_fighter = (new_fighter[:mm.start(1)] + block_new +
                       new_fighter[mm.end(1):])

    # 3. roster-full.js — FULL_ROSTER entry before the closing ];
    new_roster = re.sub(
        rf"(^  \{{ id: '{re.escape(a.id)}'.*?\n\}},?\n)",
        "", roster, flags=re.M | re.S) if a.force else roster
    if not re.search(rf"id:\s*'{re.escape(a.id)}'", new_roster):
        entry = (
            f"  {{ id: '{a.id}', name: '{name}', title: '{a.title}', base: '{a.base}', "
            f"moveset: '{a.moveset}', model: '{a.id}', tintStrength: {a.tint},\n"
            f"    colors: {{ suit: {a.suit}, trim: {a.trim} }}, style: '{a.style}', "
            f"archetype: '{a.archetype}' }},\n"
        )
        mr = re.search(r"^(\];)\s*$", new_roster, re.M)
        if not mr:
            raise SystemExit("FULL_ROSTER closing ]; not found in roster-full.js")
        new_roster = new_roster[:mr.start()] + entry + new_roster[mr.start():]

    # sanity: edited files must still parse as JS
    if not a.dry_run and shutil.which("node"):
        for label, path, new in [("assets.js", ASSETS_JS, new_assets),
                                 ("fighter.js", FIGHTER_JS, new_fighter),
                                 ("roster-full.js", ROSTER_JS, new_roster)]:
            tmp = path + ".check.js"
            with open(tmp, "w") as f:
                f.write(new)
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            os.remove(tmp)
            if r.returncode != 0:
                raise SystemExit(f"JS syntax broken after editing {label}:\n"
                                 f"{r.stderr}\nAborting, nothing written.")

    if a.dry_run:
        import difflib
        for label, old, new in [("game/js/assets.js", assets, new_assets),
                                ("game/js/fighter.js", fighter, new_fighter),
                                ("game/js/roster-full.js", roster, new_roster)]:
            diff = "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                                fromfile=label, tofile=label + " (new)"))
            print(diff or f"# no change: {label}")
        return

    write(ASSETS_JS, new_assets)
    write(FIGHTER_JS, new_fighter)
    write(ROSTER_JS, new_roster)
    print(f"wired '{a.id}':")
    print(f"  assets.js      MODEL_URLS['{a.id}'] = '{a.model}'")
    print(f"  fighter.js     MOVESET_MAP['{a.id}'] = '{a.moveset}'")
    print(f"  roster-full.js FULL_ROSTER entry (name={name})")
    print("  backups: *.bak next to each file")

if __name__ == "__main__":
    main()
