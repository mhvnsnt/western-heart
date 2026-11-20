#!/usr/bin/env python3
"""
tekken_hitprops.py — extract Tekken hit/move property data into WH movesets.

The user never dials knockback from zero: hit-feel NUMBERS come straight
from Tekken's files. This script converts t7chicken frame data
(docs/t7t8-reference/frame-data-t7/, TekkenBot-extracted, 47 chars /
11,137 moves) into WH moveset hit-property patches.

Per move it extracts:
  damage      — T7 damage (first hit of "21 [25]" strings)
  startup     — T7 startup frames ("speed") -> seconds @60fps
  active      — active frames where present
  on_block/hit/ch — frame advantage ("KND" = knockdown, "LNC" = launch)
  pushback    — T7 pushback units -> WH knock (knockback strength)
  hit_level   — high/mid/low
  crush       — high/low crush properties
  range, tracking — reach/tracking notes

Join key: notation. t7chicken "notation" ("1", "df+2", ...) matches WH
moveset "input" ("1", "2", ...). Moves with no notation match are left
untouched (reported).

When real TKMovesets2 (.tkmvst) extractions land (owner acquisition), the
Reactions/Pushback structs (knockback vectors, wall splat, screw values)
flow through tools/moveset-decode/tkm2_decode.py and this script gains a
--tkm2 mode. The JSON patch format is stable across both sources.

Usage:
  python3 tools/retarget/tekken_hitprops.py --fighter king \\
      --frame-data docs/t7t8-reference/frame-data-t7/king.json \\
      --moveset game/assets/movesets/king.json \\
      --out /tmp/king.hitprops.json [--apply]

  --apply writes the patched moveset back (default: write sidecar only).
  Batch: --all-fighters runs every fighter with a frame-data file.
"""
import argparse
import copy
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# WH fighter -> t7chicken label. Built from docs/t7t8-reference/wh_body_map.json
# (fighter -> Tekken body) + frame-data-t7/<label>.json files.
T7CHICKEN_DIR = os.path.join(REPO, "docs", "t7t8-reference", "frame-data-t7")
MOVESET_DIR = os.path.join(REPO, "game", "assets", "movesets")
HITPROPS_DIR = os.path.join(HERE, "hitprops")


def parse_damage(s):
    m = re.search(r"(\d+)", str(s or ""))
    return int(m.group(1)) if m else None


def parse_frames(s):
    m = re.search(r"(\d+)", str(s or ""))
    return int(m.group(1)) if m else None


def parse_pushback(s):
    try:
        return float(str(s).strip())
    except (ValueError, TypeError):
        return None


def norm_notation(n):
    """Normalize a notation string for join matching."""
    n = str(n or "").strip().lower()
    n = re.sub(r"\s+", "", n)
    n = n.replace("~", ",")
    return n


def extract_move_props(m):
    """Pull hit properties from one t7chicken move row."""
    props = {}
    dmg = parse_damage(m.get("damage"))
    if dmg is not None:
        props["t7_damage"] = dmg
    spd = parse_frames(m.get("speed"))
    if spd is not None:
        props["t7_startup_frames"] = spd
        props["startup"] = round(spd / 60.0, 4)
    act = parse_frames(m.get("active_frames"))
    if act is not None:
        props["t7_active_frames"] = act
        props["active"] = round(act / 60.0, 4)
    pb = parse_pushback(m.get("pushback"))
    if pb is not None:
        props["t7_pushback"] = pb
        # WH knock scale: calibrated so T7 pushback 1.0 ~= WH knock 2.2
        # (matches existing hand-tuned jab values in movesets).
        props["knock"] = round(pb * 2.2, 2)
    for k in ("on_block", "on_hit", "on_ch"):
        v = m.get(k)
        if v not in (None, "-", ""):
            props["t7_" + k] = str(v)
    for k in ("hit_level", "crush", "range", "tracking"):
        v = m.get(k)
        if v not in (None, "-", ""):
            props["t7_" + k] = str(v)
    props["t7_notation"] = m.get("notation")
    props["t7_id"] = m.get("id")
    return props


def load_frame_data(path):
    d = json.load(open(path))
    ml = d.get("movelist") if isinstance(d, dict) else d
    return ml or []


def build_notation_index(moves):
    idx = {}
    for m in moves:
        n = norm_notation(m.get("notation"))
        if n:
            idx.setdefault(n, []).append(m)
    return idx


def wire_fighter(fighter, frame_data_path, moveset_path, apply=False,
                 out_path=None, repo=REPO):
    t7moves = load_frame_data(frame_data_path)
    idx = build_notation_index(t7moves)
    ms = json.load(open(moveset_path))
    moves = ms.get("moves", {})
    patched, unmatched_inputs, multi = 0, [], []
    patch = {"fighter": fighter,
             "source": os.path.relpath(frame_data_path, repo),
             "moves": {}}
    for key, mv in moves.items():
        inp = norm_notation(mv.get("input", key))
        cands = idx.get(inp, [])
        if not cands:
            unmatched_inputs.append(mv.get("input", key))
            continue
        if len(cands) > 1:
            multi.append((mv.get("input", key), len(cands)))
        props = extract_move_props(cands[0])
        patch["moves"][key] = props
        patched += 1
        if apply:
            for pk, pv in props.items():
                if pk.startswith("t7_"):
                    mv.setdefault("t7", {})[pk[3:]] = pv
                else:
                    mv[pk] = pv
            mv.setdefault("t7", {})["wired"] = True
    result = {"fighter": fighter, "patched": patched,
              "total_moves": len(moves),
              "t7_rows": len(t7moves),
              "unmatched_inputs": unmatched_inputs,
              "multi_match": multi}
    if apply:
        with open(moveset_path, "w") as f:
            json.dump(ms, f, indent=2)
            f.write("\n")
    if out_path:
        with open(out_path, "w") as f:
            json.dump(patch, f, indent=2)
    return result


# T8 body name -> t7chicken label overrides (most are identical)
T7_LABEL_OVERRIDES = {
    "jack-8": "jack-7",
    "devil-jin": "deviljin",
    "lucky-chloe": "luckychloe",
    "master-raven": "masterraven",
    "shaheen": "shaheen",
}


def fighter_to_t7label(repo):
    """Map WH fighter -> t7chicken label via wh_body_map.json (T8 body name)."""
    mapping = {}
    try:
        wbm = json.load(open(os.path.join(
            repo, "docs", "t7t8-reference", "wh_body_map.json")))
        for fighter, info in wbm.get("fighters", {}).items():
            fd = info.get("frame_data") or ""
            m = re.search(r"frame-data/([a-z0-9_\-]+)\.json", fd)
            if m:
                body = m.group(1)
                label = T7_LABEL_OVERRIDES.get(body, body)
                t7path = os.path.join(repo, "docs", "t7t8-reference",
                                      "frame-data-t7", label + ".json")
                if os.path.exists(t7path):
                    mapping[fighter] = label
    except FileNotFoundError:
        pass
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fighter")
    ap.add_argument("--frame-data")
    ap.add_argument("--moveset")
    ap.add_argument("--out")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--all-fighters", action="store_true",
                    help="run every fighter with a frame-data file")
    ap.add_argument("--repo", default=REPO,
                    help="repo root (default: inferred from script location)")
    a = ap.parse_args()

    global T7CHICKEN_DIR, MOVESET_DIR
    T7CHICKEN_DIR = os.path.join(a.repo, "docs", "t7t8-reference",
                                 "frame-data-t7")
    MOVESET_DIR = os.path.join(a.repo, "game", "assets", "movesets")

    if a.all_fighters:
        mapping = fighter_to_t7label(a.repo)
        results = []
        for fighter, label in sorted(mapping.items()):
            fd = os.path.join(T7CHICKEN_DIR, label + ".json")
            ms = os.path.join(MOVESET_DIR, fighter + ".json")
            if not (os.path.exists(fd) and os.path.exists(ms)):
                continue
            out = os.path.join(HERE, "hitprops", fighter + ".hitprops.json")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            try:
                r = wire_fighter(fighter, fd, ms, apply=a.apply, out_path=out,
                                 repo=a.repo)
            except Exception as e:  # noqa: BLE001 — batch must survive
                r = {"fighter": fighter, "error": f"{type(e).__name__}: {e}"}
            results.append(r)
            print(f"{fighter}: patched {r.get('patched', 0)}/"
                  f"{r.get('total_moves', '?')} "
                  f"({r.get('error', 'ok')})")
        ok = sum(1 for r in results if "error" not in r)
        total_patched = sum(r.get("patched", 0) for r in results)
        print(f"\n{a.all_fighters and 'batch'}: {ok}/{len(results)} fighters, "
              f"{total_patched} moves wired")
        with open(os.path.join(HERE, "hitprops", "_batch.json"), "w") as f:
            json.dump(results, f, indent=2)
        return

    if not (a.fighter and a.frame_data and a.moveset):
        ap.error("--fighter, --frame-data and --moveset required (or --all-fighters)")
    r = wire_fighter(a.fighter, a.frame_data, a.moveset,
                     apply=a.apply, out_path=a.out)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
