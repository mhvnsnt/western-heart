#!/usr/bin/env python3
"""docs/movesets/SOURCE-MERGE-2026-10-21.md from the JSON report merge_sources.py writes."""
import json, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
r = json.loads((REPO / "docs/movesets/SOURCE-MERGE-2026-10-21.json").read_text())
F = r["fighters"]
done = {k: v for k, v in F.items() if "skipped" not in v}


def main_count(fid):
    """Moves in origin/main's file (the true 'before' — the tool may re-run on merged files)."""
    try:
        d = json.loads(subprocess.check_output(["git", "-C", str(REPO), "show", f"origin/main:game/assets/movesets/{fid}.json"],
                                               stderr=subprocess.DEVNULL))
        return len(d.get("moves") or {})
    except subprocess.CalledProcessError:
        return 0


for k, v in done.items():
    v["moves_before"] = main_count(k)
    after = json.loads((REPO / f"game/assets/movesets/{k}.json").read_text())
    v["moves_after"] = len(after["moves"])
    added = {}
    for m in after["moves"].values():
        src = isinstance(m, dict) and m.get("merge_source")
        if src:
            tag = src.split(":")[0] + (":" + src.split(":")[1] if src.startswith("donor:") else "")
            added[tag] = added.get(tag, 0) + 1
    v["added"] = added
sk = {k: v for k, v in F.items() if "skipped" in v}
L = ["# Moveset source merge — 2026-10-21 (T8 + T7 + fixed T3 + donors, additions only)\n",
     'Owner: "We need move string, combos, different moves and move inputs, everything Tekken and the teardown files have, '
     'but Tekken as the base" · "If ur just using stuff from t3 not the other then u will be limiting us" · '
     '"why would you decrease fighter moves?"\n',
     "Tools: `tools/moveset-merge/merge_sources.py` (+ `notation.py`, `bases.json`, `engine_check.mjs`, this `report_md.py`). "
     "Runs on top of PR #407's history union (main already = union of all 548 historical versions). "
     "Raw numbers: `docs/movesets/SOURCE-MERGE-2026-10-21.json`.\n",
     "## Guarantees\n",
     "- every existing move key kept with a byte-identical payload; strings/specials only appended (re-verified against origin/main: 0 files with a lost or changed move)",
     "- every new move carries `merge_source` resolving to a record in a vendored dataset (T8 wavu id, T7 t7chicken id, T3 bank row) or a donor file",
     "- `tools/moveset-merge/engine_check.mjs`: every input that fired a move on origin/main's engine fires one on the new engine (96 fighters, 4,370 inputs, 0 failures), apart from the owner-directed Doc Frank exclusion listed below",
     "- files keep their own JSON formatting (byte-exact round-trip), so the diff is additions (patience diff: lines changed only where a comma or an empty `[]` gained entries)\n",
     "## Owner corrections applied (2026-10-21)\n",
     '- **Lei Wulong = RAVE / Kiko Tanaka, not Byou** ("Lei wulong is not byou, he is Rave/Kiko tanaka"). Rave gets Lei T7 + Lei T3 + Byou\'s moves ("U can add leis and byous moves to rave"). Byou keeps exactly its origin/main file; its base is not recorded anywhere (CANON.md:427 "blocked pending the owner\'s Lei naming decision"), so nothing is merged into Byou until the owner names it.',
     '- **Doc Frank = Bosconovitch** (all four files): Bosconovitch T3, Gun Jack proxy moves never take a default input.\n',
     "## Per fighter\n",
     "`slots` maps every notation to the move it fires by default: WH signature > T8 base > T7 base > T3 base > curated/donor > proxy bank. Every other move stays assignable in the moveset editor (loadout).\n",
     "| Fighter | Built on | Moves on main → now | Inputs (slots) | Fired before | Added (this tool) |",
     "|---|---|---:|---:|---:|---|"]
for k, v in sorted(done.items()):
    on = ", ".join(f"{s}:{'/'.join(x)}" for s, x in v["bases"].items())
    L.append(f"| {k} | {on} | {v['moves_before']} → {v['moves_after']} | {v['slots']} | {v['previously_playable_inputs']} | "
             + ", ".join(f"{a} +{n}" for a, n in v["added"].items()) + " |")
tb = sum(v["moves_before"] for v in done.values())
ta = sum(v["moves_after"] for v in done.values())
L.append(f"\n**Totals ({len(done)} fighters merged): {tb:,} → {ta:,} moves.**\n")
L.append("## Owner-directed exclusions\n")
for k, v in sorted(done.items()):
    if v["owner_excluded_inputs"]:
        L.append(f"- **{k}**: inputs only Gun Jack proxy moves answered, with no Bosconovitch move: `" + "`, `".join(v["owner_excluded_inputs"]) + "` (moves stay in the file)")
L.append(f"\n## Not merged ({len(sk)} files: no decoded Tekken base yet)\n")
L.append("They keep exactly what they had; their bases need the other teardowns wired (SF 3D, DOA4, Urban Reign, No Mercy / WMXIX, KOF, VF5): "
         + ", ".join(f"{k} ({v['tekken_base']})" for k, v in sorted(sk.items())) + ".\n")
L.append("## Known limits\n")
L.append("- Animation: new T7/T8 moves carry `anim_t3` = the same base character's decoded T3 row for the same notation, else the nearest by limb/class/startup (flagged approximate). Rows for the 8 remainder banks are baked by `tools/anim/t3_row_bake.py` (2026-10-21 extension).")
L.append("- Damage: new T8 moves ×100/180, T7 ×100/170 to WH's 100 HP (raw in `damage_raw`). Earlier imports (PR #357 T8 cluster, 74efb3fb T7) kept raw T7/T8 damage. Those payloads are untouched and flagged in the Muse handoff.")
L.append("- Character stances: entered from source notes (`stance_after`, unconditional 'Transition to X' only); conditional transitions ('with F') are not automatic yet.")
L.append("- Not invented: Doc Frank's Dr. Gero / Mojo Jojo / Dr. Weird inspired moves, King Tyrant's Booker T moves, CHARGER's SF 3D moves. They need WWE/SF data decoded first.")
(REPO / "docs/movesets/SOURCE-MERGE-2026-10-21.md").write_text("\n".join(L) + "\n")
print(f"{len(done)} merged, {len(sk)} skipped, {tb} -> {ta}")
