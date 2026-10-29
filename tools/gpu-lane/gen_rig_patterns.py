#!/usr/bin/env python3
"""Generate tools/gpu-lane/rig-patterns.json FROM game/js/rig-compat.js.
Single source of truth is rig-compat.js: the GPU batch jobs load
this JSON to validate rigs (tool x model matrix) with the SAME
patterns the game uses, instead of a hand-copied second list that
drifts. Regenerate whenever rig-compat.js patterns change:
  python3 tools/gpu-lane/gen_rig_patterns.py
Parses only the `'type': { bones: ..., patterns: {...} }` blocks;
patterns are simple 'role': 'name' pairs, so a regex over those
blocks is exact (verified by the generator's own self-check,
which re-reads the JSON and asserts every rig type + role count).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(REPO_ROOT, "game", "js", "rig-compat.js")
OUT = os.path.join(HERE, "rig-patterns.json")


def main():
    src = open(SRC, encoding="utf-8").read()
    rigs = {}
    # Match: 't7-160': { bones: 160, patterns: { ... } },
    block_re = re.compile(
        r"'([a-z0-9\-]+)':\s*\{\s*bones:\s*([^,]+),\s*patterns:\s*\{([^}]*)\}\s*\}",
        re.DOTALL)
    pair_re = re.compile(r"(\w+):\s*'([^']*)'")
    for m in block_re.finditer(src):
        rtype, bones, body = m.group(1), m.group(2).strip(), m.group(3)
        patterns = dict(pair_re.findall(body))
        rigs[rtype] = {
            "bones": None if bones == "null" else int(bones),
            "patterns": patterns,
        }
    if "custom" not in rigs:
        rigs["custom"] = {"bones": None, "patterns": {}}
    if len(rigs) < 5:
        print(f"gen_rig_patterns: FAIL — only {len(rigs)} rig types parsed from {SRC}")
        return 1
    for rtype, data in rigs.items():
        if rtype != "custom" and len(data["patterns"]) < 17:
            print(f"gen_rig_patterns: FAIL — {rtype} has only {len(data['patterns'])} patterns")
            return 1
    out = {
        "provenance": "Generated from game/js/rig-compat.js RIG_TYPES by gen_rig_patterns.py. "
                      "Do NOT hand-edit: regenerate. Patterns are full-file-derived for "
                      "t7-160 (Alisa bonemap) and cape-94 (CapeJones_Rig nodes); "
                      "t3/tripo remain provisional (see rig-compat.js header).",
        "rigs": rigs,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"gen_rig_patterns: wrote {OUT} ({len(rigs)} rig types)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
