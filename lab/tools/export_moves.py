#!/usr/bin/env python3
"""Copy the 7 existing Tekken 3 move files (game/assets/<name>_moves.json) into the Lab,
attaching the full extracted T3 move rows they reference (teardown/tekken3/movesets),
so the Godot move-table interpreter can read real frame data at runtime."""
import json
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "lab/game/data/moves"; OUT.mkdir(parents=True, exist_ok=True)
NAMES = ["king", "jin", "bryan", "heihachi", "xiaoyu", "yoshimitsu", "gunjack"]
KEEP = ["row", "stream_frames", "damage", "attack_class", "active_first", "active_last", "hit_freeze",
        "reaction", "close_reaction", "step_per_frame", "air_first", "air_last", "hold_frame", "state_word", "attack_word", "branches"]
for n in NAMES:
    summary = json.load(open(REPO / f"game/assets/{n}_moves.json"))
    full = json.load(open(REPO / f"teardown/tekken3/movesets/moveset_{n}.json"))
    rows = {m["row"]: m for m in full["moves"]}
    used = {}
    for slot in ("light", "medium", "heavy", "grab"):
        r = summary[slot]["t3_row"]; used[str(r)] = {k: rows[r].get(k) for k in KEEP}
    attacks = [{k: m.get(k) for k in KEEP if k != "branches"} for m in full["moves"] if (m.get("damage") or 0) > 0]
    json.dump({"fighter": n, "summary": summary, "rows": used, "attack_rows": attacks,
               "source": [f"game/assets/{n}_moves.json", f"teardown/tekken3/movesets/moveset_{n}.json"]},
              open(OUT / f"{n}.json", "w"), indent=1)
    print(n, {s: summary[s]["t3_row"] for s in ("light", "medium", "heavy", "grab")}, len(attacks), "attack rows")
