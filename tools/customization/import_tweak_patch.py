#!/usr/bin/env python3
"""Validate and apply a suite-exported tweak patch (wh-tweak-patch).

The coordinator's apply script for the customization-suite round trip:
  1. User tweaks a fighter live in the suite and hits EXPORT -> downloads
     a small JSON patch (see customization/TWEAK-PATCH-SPEC.md).
  2. User sends the file back in chat.
  3. Coordinator runs THIS script on the file. It VALIDATES strictly
     (rejects malformed patches with a clear error and changes NOTHING),
     then applies it to the staged tweak kit in the repo:
       - merges each change into the kit's `adjustments` (patch wins per group)
       - bumps the kit version and appends a history entry
       - writes a canonical applied record under
         customization/tweak-kits/<fighter>/applied/

Usage:
  import_tweak_patch.py <patch.json> [--repo DIR] [--check] [--pr]

  --check   validate only, change nothing (exit 0 = valid)
  --pr      after applying, push via gh_push.py and open a PR
            (needs --branch name, defaults to tweak-patch/<fighter>/<kit>)

Anti-corruption rules: every rejection is a hard error with the reason;
a patch with ANY invalid field is rejected whole. No silent fixes.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

FORMAT = "wh-tweak-patch"
SUPPORTED_VERSIONS = (1,)
PART_GROUPS = ("head", "torso", "upper_arms", "forearms",
               "hands", "thighs", "shins", "feet")
CHANGE_KINDS = ("part_transform",)

GH_PUSH = os.environ.get("WH_GH_PUSH", os.path.expanduser("~/workspace/fix2/gh_push.py"))


class PatchError(Exception):
    pass


def fail(msg):
    raise PatchError(msg)


def _is_finite_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and \
        abs(x) != float("inf") and x == x  # NaN != NaN


def load_roster_ids(repo):
    """Roster ids from game/js/roster-full.js and customization/profiles/."""
    ids = set()
    roster_js = os.path.join(repo, "game", "js", "roster-full.js")
    if os.path.isfile(roster_js):
        with open(roster_js, encoding="utf-8", errors="replace") as f:
            ids.update(re.findall(r"""\bid\s*:\s*['"]([^'"]+)['"]""", f.read()))
    prof_dir = os.path.join(repo, "customization", "profiles")
    if os.path.isdir(prof_dir):
        for fn in os.listdir(prof_dir):
            if fn.endswith(".json"):
                ids.add(fn[:-5])
    return ids


def kit_path(repo, kit_id):
    return os.path.join(repo, "customization", "tweak-kits", kit_id + ".json")


def validate(patch, repo):
    """Return a normalized patch dict, or raise PatchError with a clear reason."""
    if not isinstance(patch, dict):
        fail("patch root must be a JSON object")
    if patch.get("format") != FORMAT:
        fail(f"bad 'format': expected {FORMAT!r}, got {patch.get('format')!r}")
    if patch.get("version") not in SUPPORTED_VERSIONS:
        fail(f"unsupported 'version': {patch.get('version')!r} "
             f"(this importer supports {list(SUPPORTED_VERSIONS)})")

    fighter = patch.get("fighter")
    if not isinstance(fighter, str) or not fighter:
        fail("'fighter' must be a non-empty string (roster id)")
    if fighter not in load_roster_ids(repo):
        fail(f"unknown 'fighter' {fighter!r}: no such roster id in "
             f"game/js/roster-full.js or customization/profiles/")

    kit_id = patch.get("kit_id")
    if kit_id is not None:
        if not isinstance(kit_id, str) or not kit_id:
            fail("'kit_id' must be a non-empty string or omitted/null")
        kp = kit_path(repo, kit_id)
        if not os.path.isfile(kp):
            fail(f"unknown 'kit_id' {kit_id!r}: no staged kit at "
                 f"customization/tweak-kits/{kit_id}.json")
        try:
            with open(kp, encoding="utf-8") as f:
                kit = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            fail(f"staged kit {kit_id!r} is unreadable: {e}")
        if kit.get("format") != "wh-tweak-kit":
            fail(f"staged kit {kit_id!r} has bad format {kit.get('format')!r}")
        if kit.get("fighter") != fighter:
            fail(f"patch fighter {fighter!r} does not match kit {kit_id!r} "
                 f"fighter {kit.get('fighter')!r}")

    attire = patch.get("attire", "default")
    if not isinstance(attire, str) or not attire:
        fail("'attire' must be a non-empty string")

    changes = patch.get("changes")
    if not isinstance(changes, list) or not changes:
        fail("'changes' must be a non-empty array")
    seen = set()
    norm = []
    for i, c in enumerate(changes):
        where = f"changes[{i}]"
        if not isinstance(c, dict):
            fail(f"{where} must be an object")
        if c.get("kind") not in CHANGE_KINDS:
            fail(f"{where}: bad 'kind' {c.get('kind')!r} "
                 f"(expected one of {list(CHANGE_KINDS)})")
        group = c.get("group")
        if group not in PART_GROUPS:
            fail(f"{where}: bad 'group' {group!r} "
                 f"(expected one of {list(PART_GROUPS)})")
        if group in seen:
            fail(f"{where}: duplicate group {group!r} — one entry per group")
        seen.add(group)
        rot = c.get("rotation_deg")
        if not isinstance(rot, list) or len(rot) != 3 or \
                not all(_is_finite_number(v) for v in rot):
            fail(f"{where}: 'rotation_deg' must be 3 finite numbers")
        if any(abs(v) > 360 for v in rot):
            fail(f"{where}: 'rotation_deg' values must be within [-360, 360]")
        flip = c.get("flip", [False, False, False])
        if not isinstance(flip, list) or len(flip) != 3 or \
                not all(isinstance(v, bool) for v in flip):
            fail(f"{where}: 'flip' must be 3 booleans")
        off = c.get("offset", [0, 0, 0])
        if not isinstance(off, list) or len(off) != 3 or \
                not all(_is_finite_number(v) for v in off):
            fail(f"{where}: 'offset' must be 3 finite numbers")
        if any(abs(v) > 5 for v in off):
            fail(f"{where}: 'offset' values must be within [-5, 5] model units")
        scale = c.get("scale", 1.0)
        if not _is_finite_number(scale) or not (0.1 <= scale <= 10):
            fail(f"{where}: 'scale' must be a finite number in [0.1, 10]")
        note = c.get("note", "")
        if not isinstance(note, str):
            fail(f"{where}: 'note' must be a string")
        norm.append({
            "kind": "part_transform", "group": group,
            "rotation_deg": [float(v) for v in rot],
            "flip": list(flip), "offset": [float(v) for v in off],
            "scale": float(scale), "note": note,
        })
    return {
        "format": FORMAT, "version": patch["version"],
        "kit_id": kit_id, "fighter": fighter, "attire": attire,
        "exported_at": patch.get("exported_at"),
        "exported_by": patch.get("exported_by"),
        "suite_build": patch.get("suite_build"),
        "notes": patch.get("notes", "") if isinstance(patch.get("notes", ""), str) else "",
        "changes": norm,
    }


def apply_patch(norm, repo):
    """Merge a validated patch into the staged kit + applied record."""
    fighter = norm["fighter"]
    kit_id = norm["kit_id"] or f"{fighter}-manual"
    kp = kit_path(repo, kit_id)
    if os.path.isfile(kp):
        with open(kp, encoding="utf-8") as f:
            kit = json.load(f)
    else:
        kit = {
            "format": "wh-tweak-kit", "version": 0, "id": kit_id,
            "fighter": fighter, "attire": norm["attire"], "status": "staged",
            "notes": f"auto-created from user patch (kit_id omitted)",
            "flagged_parts": sorted({c["group"] for c in norm["changes"]}),
            "part_map": {}, "adjustments": {}, "history": [],
        }
    adj = kit.setdefault("adjustments", {})
    for c in norm["changes"]:
        adj[c["group"]] = {
            "rotation_deg": c["rotation_deg"], "flip": c["flip"],
            "offset": c["offset"], "scale": c["scale"],
            "note": c["note"], "from_patch": True,
        }
    kit["version"] = int(kit.get("version", 0)) + 1
    kit.setdefault("history", []).append({
        "at": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds").replace("+00:00", "Z"),
        "action": "tweak-patch-applied",
        "groups": [c["group"] for c in norm["changes"]],
        "exported_at": norm["exported_at"],
        "exported_by": norm["exported_by"],
    })
    os.makedirs(os.path.dirname(kp), exist_ok=True)
    with open(kp, "w", encoding="utf-8") as f:
        json.dump(kit, f, indent=2)
        f.write("\n")

    digest = hashlib.sha256(
        json.dumps(norm, sort_keys=True).encode()).hexdigest()[:12]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    applied_dir = os.path.join(repo, "customization", "tweak-kits",
                               fighter, "applied")
    os.makedirs(applied_dir, exist_ok=True)
    applied_path = os.path.join(applied_dir, f"{kit_id}-{ts}-{digest}.applied.json")
    with open(applied_path, "w", encoding="utf-8") as f:
        json.dump({
            "format": "wh-tweak-patch-applied", "version": 1,
            "kit_id": kit_id, "fighter": fighter,
            "patch_sha256_12": digest,
            "validation": "pass",
            "applied_at": ts,
            "patch": norm,
        }, f, indent=2)
        f.write("\n")
    return kp, applied_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate + apply a tweak patch.")
    ap.add_argument("patch", help="exported JSON patch file")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--check", action="store_true",
                    help="validate only, write nothing")
    ap.add_argument("--pr", action="store_true",
                    help="push the change and open a PR via gh_push.py")
    ap.add_argument("--branch", default=None, help="branch name for --pr")
    args = ap.parse_args(argv)
    repo = os.path.abspath(args.repo)

    try:
        with open(args.patch, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: patch file not found: {args.patch}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"ERROR: patch is not valid JSON: {e}", file=sys.stderr)
        return 2

    try:
        norm = validate(raw, repo)
    except PatchError as e:
        print(f"PATCH REJECTED: {e}", file=sys.stderr)
        return 1

    n = len(norm["changes"])
    groups = ", ".join(c["group"] for c in norm["changes"])
    print(f"PATCH VALID: fighter={norm['fighter']} kit={norm['kit_id']} "
          f"changes={n} ({groups})")
    if args.check:
        return 0

    kit_p, applied_p = apply_patch(norm, repo)
    print(f"APPLIED: kit -> {os.path.relpath(kit_p, repo)}")
    print(f"RECORD:  {os.path.relpath(applied_p, repo)}")

    if args.pr:
        branch = args.branch or \
            f"tweak-patch/{norm['fighter']}/{norm['kit_id'] or 'manual'}"
        rel_kit = os.path.relpath(kit_p, repo)
        rel_applied = os.path.relpath(applied_p, repo)
        cmd = [sys.executable, GH_PUSH, "--branch", branch, "--base", "main",
               "--add", rel_kit, "--add", rel_applied,
               "--title", f"tweak-patch: {norm['fighter']} "
                          f"{norm['kit_id'] or 'manual'} ({groups})",
               "--body", f"User-exported tweak patch applied via "
                         f"tools/customization/import_tweak_patch.py\n\n"
                         f"Fighter: {norm['fighter']}\n"
                         f"Kit: {norm['kit_id']}\n"
                         f"Groups: {groups}\n"
                         f"Exported: {norm['exported_at']} by {norm['exported_by']}\n"]
        print("pushing:", " ".join(cmd))
        r = subprocess.run(cmd, cwd=repo)
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
