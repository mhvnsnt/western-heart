#!/usr/bin/env python3
"""Validate T7 extraction outputs — TRACK 1 (2026-10-23).

Runs WITHOUT game files. Two modes:

  --check-tools [TOOLS_DIR]  verify vendored tool dirs + print SHAs
  --check-output OUT          verify the extracted tree + moveset JSON schema

Exit 0 = green, 1 = problems found (file-by-file report).
"""

import argparse
import json
import os
import subprocess
import sys

EXPECTED_OUTPUT_DIRS = [
    "paks_unpacked", "movesets", "anim_bin", "meshes",
    "textures", "audio", "ui", "stages",
]

VENDOR_TOOLS = [
    "TKMovesets", "TekkenMovesetExtractor", "UEViewer",
    "BlenderTekkenAnimationImporter", "Tekken-7-Extracting-Packing-Tools",
]

# Must match existing game/assets/movesets/*.json (e.g. buffalo-bill.json).
MOVESET_REQUIRED_TOP = ["fighter", "display", "moves"]
MOVESET_REQUIRED_MOVE = [
    "name", "input", "startup", "active", "recovery", "damage",
    "limb", "heavy", "knock", "soulGain", "anim_ref", "input_slots",
    "move_class",
]


def check_tools(tools_dir):
    print("== check-tools: %s ==" % tools_dir)
    code = 0
    for name in VENDOR_TOOLS:
        p = os.path.join(tools_dir, name)
        if not os.path.isdir(p):
            print("FAIL: missing tool dir: %s" % p)
            code = 1
            continue
        try:
            sha = subprocess.run(
                ["git", "-C", p, "log", "-1", "--format=%H %ad", "--date=short"],
                capture_output=True, text=True, timeout=15).stdout.strip()
        except Exception:
            sha = "(no git metadata)"
        print("OK: %-38s %s" % (name, sha))
    return code


def validate_moveset_json(path):
    """Return list of problems (empty = valid)."""
    problems = []
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        return ["%s: not valid JSON: %s" % (path, e)]
    for k in MOVESET_REQUIRED_TOP:
        if k not in d:
            problems.append("%s: missing top-level key %r" % (path, k))
    moves = d.get("moves")
    if not isinstance(moves, dict) or not moves:
        problems.append("%s: 'moves' must be a non-empty object" % path)
        return problems
    for inp, m in moves.items():
        if not isinstance(m, dict):
            problems.append("%s: move %r not an object" % (path, inp))
            continue
        for k in MOVESET_REQUIRED_MOVE:
            if k not in m:
                problems.append("%s: move %r missing key %r" % (path, inp, k))
        ref = m.get("anim_ref", "")
        if ref and not ref.startswith(("t7:", "t3:", "t7chicken:", "t8:")):
            problems.append("%s: move %r anim_ref has unexpected prefix: %r"
                            % (path, inp, ref))
    return problems


def check_output(out_dir):
    print("== check-output: %s ==" % out_dir)
    code = 0
    if not os.path.isdir(out_dir):
        print("FAIL: output dir missing: %s" % out_dir)
        return 1
    for sub in EXPECTED_OUTPUT_DIRS:
        p = os.path.join(out_dir, sub)
        if os.path.isdir(p):
            n = len(os.listdir(p))
            print("OK: %-14s (%d entries)" % (sub + "/", n))
        else:
            print("WARN: missing expected dir: %s" % p)

    # .tkmoveset presence (produced by interactive Stage 2)
    ms = os.path.join(out_dir, "movesets")
    if os.path.isdir(ms):
        tk = [f for f in os.listdir(ms) if f.endswith(".tkmoveset")]
        print("  .tkmoveset files staged: %d" % len(tk))

    # Validate any game-ready moveset JSONs dropped next to the tree.
    problems = []
    for root, _dirs, files in os.walk(out_dir):
        for f in files:
            if f.endswith(".json") and "moveset" in root.lower().replace("\\", "/"):
                problems += validate_moveset_json(os.path.join(root, f))
    # Also validate a repo game/assets/movesets dir if pointed at one.
    if problems:
        print("FAIL: moveset JSON problems:")
        for p in problems[:50]:
            print("  - " + p)
        if len(problems) > 50:
            print("  ... and %d more" % (len(problems) - 50))
        code = 1
    else:
        print("OK: moveset JSON schema: no problems found")
    return code


def main(argv):
    ap = argparse.ArgumentParser(description="Validate T7 extraction outputs")
    ap.add_argument("--check-tools", action="store_true")
    ap.add_argument("--check-output", metavar="OUT")
    ap.add_argument("--tools-dir", default="tools-vendor/t7-pipeline")
    args = ap.parse_args(argv)
    if not args.check_tools and not args.check_output:
        ap.error("pass --check-tools and/or --check-output OUT")
    code = 0
    if args.check_tools:
        code |= check_tools(args.tools_dir)
    if args.check_output:
        code |= check_output(args.check_output)
    print("VALIDATE: " + ("GREEN" if code == 0 else "RED"))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
