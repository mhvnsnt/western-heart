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
CHANGE_KINDS = ("part_transform", "hitfeel_tune", "ui_screen_define")
FEEL_KEYS = ("hitstop", "shake", "knockback", "launch")

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
    if fighter == "ui":
        kinds = {c.get("kind") for c in patch.get("changes", []) if isinstance(c, dict)}
        if kinds - {"ui_screen_define"}:
            fail("'fighter' 'ui' is only valid for ui_screen_define patches")
    elif fighter not in load_roster_ids(repo):
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
        kind = c.get("kind")
        if kind not in CHANGE_KINDS:
            fail(f"{where}: bad 'kind' {kind!r} "
                 f"(expected one of {list(CHANGE_KINDS)})")
        if kind == "hitfeel_tune":
            tune = {}
            for k in FEEL_KEYS:
                v = c.get(k, 1.0)
                if not _is_finite_number(v) or not (0 <= v <= 4):
                    fail(f"{where}: '{k}' must be a finite number in [0, 4] "
                         f"(multiplier on the wired value)")
                tune[k] = float(v)
            note = c.get("note", "")
            if not isinstance(note, str):
                fail(f"{where}: 'note' must be a string")
            if all(v == 1.0 for v in tune.values()):
                fail(f"{where}: hitfeel_tune changes nothing "
                     f"(all multipliers are 1.0)")
            norm.append({"kind": kind, **tune, "note": note})
            continue
        if kind == "ui_screen_define":
            scr = c.get("screen")
            serrs = _validate_screen(scr, where)
            if serrs:
                fail(f"{where}: invalid screen definition: " + "; ".join(serrs))
            note = c.get("note", "")
            if not isinstance(note, str):
                fail(f"{where}: 'note' must be a string")
            norm.append({"kind": kind, "screen": scr, "note": note})
            continue
        group = c.get("group")
        if group not in PART_GROUPS:
            fail(f"{where}: bad 'group' {group!r} "
                 f"(expected one of {list(PART_GROUPS)})")
        if group in seen:
            fail(f"{where}: duplicate group {group!r} — one entry per group")
        seen.add(group)  # part_transform only; hitfeel_tune continued above
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


SCREEN_ELEMENT_TYPES = ("label", "button", "panel", "image", "card-grid")


def _validate_screen(def_, where):
    errs = []
    if not isinstance(def_, dict):
        return ["screen definition must be an object"]
    if def_.get("format") != "wh-ui-screen":
        errs.append(f"bad screen format: {def_.get('format')!r}")
    if def_.get("version") != 1:
        errs.append(f"unsupported screen version: {def_.get('version')!r}")
    sid = def_.get("id")
    if not isinstance(sid, str) or not sid or not all(
            ch.isalnum() or ch in "-_" for ch in sid):
        errs.append("screen id must be a non-empty [a-z0-9-_] string")
    canvas = def_.get("canvas") or {}
    if not _is_finite_number(canvas.get("w")) or not _is_finite_number(canvas.get("h")):
        errs.append("bad screen canvas")
    seen = set()
    for i, e in enumerate(def_.get("elements") or []):
        w = f"{where}.elements[{i}]"
        if not isinstance(e, dict):
            errs.append(f"{w} must be an object"); continue
        if e.get("type") not in SCREEN_ELEMENT_TYPES:
            errs.append(f"{w}: bad type {e.get('type')!r}"); continue
        eid = e.get("id")
        if not isinstance(eid, str) or not eid:
            errs.append(f"{w}: missing id")
        elif eid in seen:
            errs.append(f"{w}: duplicate id {eid!r}")
        else:
            seen.add(eid)
        for k in ("x", "y", "w", "h"):
            if not _is_finite_number(e.get(k)):
                errs.append(f"{w}: bad {k}")
        if _is_finite_number(e.get("w")) and _is_finite_number(e.get("h")) and \
                (e["w"] <= 0 or e["h"] <= 0):
            errs.append(f"{w}: w/h must be positive")
    return errs


def _now_z():
    return datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec="seconds").replace("+00:00", "Z")


def apply_patch(norm, repo):
    """Merge a validated patch into the staged kit / hit-feel file + applied record."""
    fighter = norm["fighter"]
    kit_id = norm["kit_id"] or f"{fighter}-manual"
    part_changes = [c for c in norm["changes"] if c["kind"] == "part_transform"]
    feel_changes = [c for c in norm["changes"] if c["kind"] == "hitfeel_tune"]
    screen_changes = [c for c in norm["changes"] if c["kind"] == "ui_screen_define"]
    written = []
    if part_changes:
        written.extend(_apply_part_transform(norm, part_changes, repo, fighter, kit_id))
    if feel_changes:
        written.extend(_apply_hitfeel(norm, feel_changes, repo, fighter))
    if screen_changes:
        written.extend(_apply_screen(norm, screen_changes, repo))
    return written


def _applied_record(repo, fighter, name, norm):
    digest = hashlib.sha256(
        json.dumps(norm, sort_keys=True).encode()).hexdigest()[:12]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    applied_dir = os.path.join(repo, "customization", "tweak-kits",
                               fighter, "applied")
    os.makedirs(applied_dir, exist_ok=True)
    applied_path = os.path.join(applied_dir, f"{name}-{ts}-{digest}.applied.json")
    with open(applied_path, "w", encoding="utf-8") as f:
        json.dump({
            "format": "wh-tweak-patch-applied", "version": 1,
            "kit_id": norm["kit_id"], "fighter": fighter,
            "patch_sha256_12": digest,
            "validation": "pass",
            "applied_at": ts,
            "patch": norm,
        }, f, indent=2)
        f.write("\n")
    return applied_path


def _apply_part_transform(norm, part_changes, repo, fighter, kit_id):
    kp = kit_path(repo, kit_id)
    if os.path.isfile(kp):
        with open(kp, encoding="utf-8") as f:
            kit = json.load(f)
    else:
        kit = {
            "format": "wh-tweak-kit", "version": 0, "id": kit_id,
            "fighter": fighter, "attire": norm["attire"], "status": "staged",
            "notes": f"auto-created from user patch (kit_id omitted)",
            "flagged_parts": sorted({c["group"] for c in part_changes}),
            "part_map": {}, "adjustments": {}, "history": [],
        }
    adj = kit.setdefault("adjustments", {})
    for c in part_changes:
        adj[c["group"]] = {
            "rotation_deg": c["rotation_deg"], "flip": c["flip"],
            "offset": c["offset"], "scale": c["scale"],
            "note": c["note"], "from_patch": True,
        }
    kit["version"] = int(kit.get("version", 0)) + 1
    kit.setdefault("history", []).append({
        "at": _now_z(),
        "action": "tweak-patch-applied",
        "groups": [c["group"] for c in part_changes],
        "exported_at": norm["exported_at"],
        "exported_by": norm["exported_by"],
    })
    os.makedirs(os.path.dirname(kp), exist_ok=True)
    with open(kp, "w", encoding="utf-8") as f:
        json.dump(kit, f, indent=2)
        f.write("\n")
    applied_path = _applied_record(repo, fighter, kit_id, norm)
    return [(kp, applied_path)]


def _apply_hitfeel(norm, feel_changes, repo, fighter):
    """Write the user's feel deltas to customization/hit-feel/<fighter>.json."""
    fp = os.path.join(repo, "customization", "hit-feel", fighter + ".json")
    if os.path.isfile(fp):
        with open(fp, encoding="utf-8") as f:
            doc = json.load(f)
    else:
        doc = {"format": "wh-hitfeel", "version": 1, "fighter": fighter,
               "multipliers": {}, "history": []}
    # last change wins per patch; multipliers are absolute (1.0 = wired value)
    merged = dict(doc.get("multipliers", {}))
    for c in feel_changes:
        for k in FEEL_KEYS:
            merged[k] = c[k]
    doc["multipliers"] = merged
    doc["version"] = int(doc.get("version", 0)) + 1
    doc.setdefault("history", []).append({
        "at": _now_z(),
        "action": "hitfeel-tune-applied",
        "multipliers": merged,
        "exported_at": norm["exported_at"],
        "exported_by": norm["exported_by"],
    })
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    applied_path = _applied_record(repo, fighter, f"{fighter}-hitfeel", norm)
    return [(fp, applied_path)]


def _apply_screen(norm, screen_changes, repo):
    """Write workshop screen definitions to customization/ui-screens/."""
    written = []
    for c in screen_changes:
        scr = dict(c["screen"])
        sid = scr["id"]
        sp = os.path.join(repo, "customization", "ui-screens", sid + ".json")
        scr["version"] = 1
        hist = scr.get("history", [])
        hist.append({
            "at": _now_z(),
            "action": "ui-screen-applied",
            "exported_at": norm["exported_at"],
            "exported_by": norm["exported_by"],
        })
        scr["history"] = hist
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(scr, f, indent=2)
            f.write("\n")
        applied_path = _applied_record(repo, "ui", sid, norm)
        written.append((sp, applied_path))
    return written


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

    kinds = {}
    for c in norm["changes"]:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    desc = ", ".join(f"{k}x{v}" for k, v in kinds.items())
    print(f"PATCH VALID: fighter={norm['fighter']} kit={norm['kit_id']} "
          f"changes={len(norm['changes'])} ({desc})")
    if args.check:
        return 0

    written = apply_patch(norm, repo)
    for target_p, applied_p in written:
        print(f"APPLIED: {os.path.relpath(target_p, repo)}")
        print(f"RECORD:  {os.path.relpath(applied_p, repo)}")

    if args.pr:
        branch = args.branch or \
            f"tweak-patch/{norm['fighter']}/{norm['kit_id'] or 'manual'}"
        cmd = [sys.executable, GH_PUSH, "--branch", branch, "--base", "main"]
        for target_p, applied_p in written:
            cmd += ["--add", os.path.relpath(target_p, repo),
                    "--add", os.path.relpath(applied_p, repo)]
        cmd += ["--title", f"tweak-patch: {norm['fighter']} "
                           f"{norm['kit_id'] or 'manual'} ({desc})",
                "--body", f"User-exported tweak patch applied via "
                          f"tools/customization/import_tweak_patch.py\n\n"
                          f"Fighter: {norm['fighter']}\n"
                          f"Kit: {norm['kit_id']}\n"
                          f"Changes: {desc}\n"
                          f"Exported: {norm['exported_at']} by {norm['exported_by']}\n"]
        print("pushing:", " ".join(cmd))
        r = subprocess.run(cmd, cwd=repo)
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
