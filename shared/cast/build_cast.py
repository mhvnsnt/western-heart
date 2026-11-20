#!/usr/bin/env python3
"""Build shared/cast/cast.json: every rigged western-heart fighter -> Cape Jones cast entry.
References models by repo path only (never copies or edits them).
Run from western-heart repo root:  python3 shared/cast/build_cast.py
Sources: `git ls-files` (roster/*/attires/*/model-rigged.glb, game/assets/models/*.glb),
game/assets/models/model-facing.json (facing), game/ui-wh/roster_canon.json (names)."""
import json, subprocess, re, collections
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
facing = json.load(open("game/assets/models/model-facing.json"))["models"]
try:
    canon = {k.lower().replace(" ", "-"): k for k in json.load(open("game/ui-wh/roster_canon.json"))}
except Exception:
    canon = {}
fs = set(files)
chars = collections.OrderedDict()
for f in sorted(files):
    m = re.match(r"^roster/([^/]+)/attires/([^/]+)/model-rigged\.glb$", f)
    if m:
        cid, att = m.groups()
        chars.setdefault(cid, {"rigged_attires": {}})["rigged_attires"][att] = f
for cid in list(chars) + ["cape-jones"]:
    e = chars.setdefault(cid, {"rigged_attires": {}})
    g = f"game/assets/models/{cid}.glb"
    e["game_model"] = g if g in fs else None
    e["canon_doc"] = f"roster/{cid}/CANON.md" if f"roster/{cid}/CANON.md" in fs else None
    e["display_name"] = canon.get(cid, cid.upper())
    e["facing_rest"] = facing.get(cid, "unlisted (+Z fallback per model-facing.json note)")
    e["rotate_y_deg_on_import"] = 180 if facing.get(cid) == "-Z" else 0
    e["rig"] = "wh-52-bone auto-rig (template skeleton faces -Z; trust facing_rest, not bone names)" if e["rigged_attires"] else "game model skeleton"
    e["fight_moveset"] = {"owner": "western-heart", "rule": "READ-ONLY for the show; never retime/overwrite"}
    e["show_anims_dir"] = f"anims/show/{cid}/"
    e["cape_jones_role"] = "Cape Jones (host/protagonist)" if cid == "cape-jones" else "cast member - Immortal Qombat fighter met through the TV portal"
out = {"format": "wh-cast/1",
       "note": "Canonical in mhvnsnt/western-heart shared/cast/cast.json; mirrored to mhvnsnt/cape-jones via its shared/cast/sync_cast.sh. Paths are relative to western-heart root.",
       "generator": "shared/cast/build_cast.py", "count": len(chars), "cast": chars}
json.dump(out, open("shared/cast/cast.json", "w"), indent=1, sort_keys=False)
print("cast entries:", len(chars))
