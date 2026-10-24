#!/usr/bin/env python3
"""tools/tripo-intake/intake.py — Tripo auto-intake: rig new Tripo statics ASAP to their character rig.

Owner directive (2026-10-21, verbatim): "As soon as a Tripo model comes in you
need to get it rigged automatically ASAP to the character rig that it goes to."

Drop a model in and run it:

    # new arrival: inbox/<fighter-roster-dir>/attire<N>.glb (+ optional attire<N>.json sidecar)
    cp new-tripo.glb tools/tripo-intake/inbox/kinpo/attire3.glb
    python3 tools/tripo-intake/intake.py --scan

    # one-shot (used for dry runs / explicit drops):
    python3 tools/tripo-intake/intake.py --in /tmp/new.glb --fighter kinpo --attire 3 \\
        --stage-root /tmp/stage --report-root /tmp/reports --dry-run

Pipeline per model (the original inbox file is never modified or deleted —
on completion it is MOVED to outbox/<fighter>/attire<N>/<timestamp>/):

  0. env check: WH_BLENDER (or ~/workspace/tools/blender/...), node,
     xvfb-run, node_modules (@gltf-transform + meshoptimizer), numpy.
  1. claim: <fighter> must be an existing roster/<dir> (never guessed);
     attire slot must not already hold a model-rigged.glb (never clobber);
     input must be an UNRIGGED static (0 skins -> refuse otherwise).
  2. sha256; ledger lookup (tools/tripo-intake/ledger.json): identical bytes
     decided before are re-decided identically, never re-guessed.
  3. decode (tools/anim/gltf_codec.mjs) for the facing estimate.
  4. facing via facing_check.py (two independent geometry cues + confidence
     gate). Low confidence -> REFUSE (exit 2 for the item): the model is
     archived to the outbox with FLAG-FACING-NEEDED.md and a human views rest
     renders, then re-runs with --facing <axis> as the manual override.
     The intake NEVER guesses facing: a wrong rotation bakes backwards skin
     weights (the demonio-a1 -74-vs-90deg case).
  5. rig via the PROVEN pipeline tools/auto_rig/rig_tripo_static.py
     (decode -> gamerig Blender rig -> smooth_weights -> validate + anim_check
     -> render_poses -> encode), with --facing <axis>.
  6. gates on rig_report.json: validate.py (the playable gate) must PASS or
     nothing stages; anim_check flags are recorded and must be explained by
     viewing the renders before wiring (even the shipped Zui A1 carries
     anim_check flags on the CMU stress clip).
  7. stage to <stage-root>/roster/<fighter>/attires/attire<N>/model-rigged.glb
     (default stage-root = repo root) + WIRING-CHECKLIST.md for the reviewer.
     Wiring game/js/* stays a REVIEWED step — the intake never edits game code.

Exit codes: 0 all items done; 2 any item REFUSED (facing/claim/clobber);
3 any item FAILED a gate or a pipeline step errored.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "ledger.json")
INBOX = os.path.join(HERE, "inbox")
OUTBOX = os.path.join(HERE, "outbox")


def tool_paths(repo_root):
    return {
        "rig": os.path.join(repo_root, "tools", "auto_rig", "rig_tripo_static.py"),
        "facing": os.path.join(HERE, "facing_check.py"),
        "codec": os.path.join(repo_root, "tools", "anim", "gltf_codec.mjs"),
    }

UTC = datetime.datetime.now(datetime.timezone.utc)
TODAY = UTC.strftime("%Y-%m-%d")
STAMP = UTC.strftime("%Y%m%d-%H%M%S")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def glb_json(path):
    import struct as _s
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"glTF":
        raise ValueError("not a GLB file")
    jlen = _s.unpack("<I", raw[12:16])[0]
    return json.loads(raw[20:20 + jlen])


def check_env(repo_root):
    problems = []
    tools = tool_paths(repo_root)
    blender = os.environ.get("WH_BLENDER") or os.path.expanduser(
        "~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")
    if not (os.path.isfile(blender) and os.access(blender, os.X_OK)):
        problems.append(f"Blender 4.0.2 not executable: {blender} "
                        "(set WH_BLENDER or run tools/setup/setup_toolchain.sh)")
    if not shutil.which("node"):
        problems.append("node not on PATH")
    if not shutil.which("xvfb-run"):
        problems.append("xvfb-run not on PATH (Blender needs it headless)")
    nm = None
    if os.environ.get("NODE_PATH"):
        for p in os.environ["NODE_PATH"].split(os.pathsep):
            if os.path.isdir(p):
                nm = p
                break
    if nm is None and os.path.isdir(os.path.join(DEFAULT_REPO, "tools", "anim", "node_modules")):
        nm = os.path.join(DEFAULT_REPO, "tools", "anim", "node_modules")
    if nm is None:
        problems.append("node_modules with @gltf-transform+meshoptimizer not found "
                        "(set NODE_PATH=$HOME/workspace/tools/gltf/node_modules)")
    try:
        import numpy  # noqa: F401
    except ImportError:
        problems.append("python numpy missing (pip install numpy scipy pygltflib)")
    for p in (tools["rig"], tools["facing"], tools["codec"]):
        if not os.path.isfile(p):
            problems.append(f"missing pipeline file: {p}")
    return problems, blender, nm


def codec_cmd(work, node_modules, codec_path):
    """node invocation for gltf_codec.mjs (ES modules ignore NODE_PATH, so run
    a copy beside a node_modules symlink — same trick rig_tripo_static.py uses)."""
    cdir = os.path.join(work, "codec")
    os.makedirs(cdir, exist_ok=True)
    link = os.path.join(cdir, "node_modules")
    if not os.path.islink(link):
        os.symlink(node_modules, link)
    dest = os.path.join(cdir, "gltf_codec.mjs")
    if not os.path.isfile(dest):
        shutil.copy(codec_path, dest)
    return ["node", dest]


def run(cmd, env=None):
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return r


def load_ledger():
    if os.path.exists(LEDGER):
        try:
            return json.load(open(LEDGER))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_ledger(led):
    led["_note"] = ("sha256 -> facing/gate decisions. Consulted before re-deciding; "
                    "identical bytes always decide identically.")
    json.dump(led, open(LEDGER, "w"), indent=1)


WIRING_TEMPLATE = """# WIRING CHECKLIST — {fighter} attire {attire} (Tripo auto-intake {stamp})

The model is RIGGED and staged. Wiring it into the game stays a REVIEWED step:
do not wire until the renders below have been VIEWED by a human.

## What the intake did
- input: {in_name} (sha256 `{in_sha}`) — original archived, never modified
- facing: **{facing}** ({facing_source}); report: `{facing_report}`
- rig: tools/auto_rig/rig_tripo_static.py -> `{out_rel}` (sha256 `{out_sha}`)
- gates: validate {validate_verdict}; anim_check {anim_verdict}
- proof dir: `{report_dir}` — VIEW the *poses*.png renders there before wiring
- RIG-NOTES: {rig_notes}

## Reviewer: wire it (all manual)
1. `game/js/assets.js` MODEL_URLS — add (keys MUST match FULL_ROSTER `model`
   ids in `game/js/roster-full.js`; verify, the names below are the convention):
   ```
   '{fighter}': '../roster/{fighter}/attires/attire{attire}/model-rigged.glb',
   '{fighter}-attire{attire}': '../roster/{fighter}/attires/attire{attire}/model-rigged.glb',
   ```
   Keep the old key's file as the ladder-back (never delete a wired model).
2. `game/js/roster-full.js` — confirm the fighter's `model` id; add the attire
   entry if this is a new slot (see `roster/{fighter}/ATTIRE-SLOTS.md`).
3. Moveset: confirm `game/assets/movesets/index.json` has the fighter's
   moveset id and `game/js/movesets.js` MOVESET_MAP covers it.
4. Facing: record the model in `game/assets/models/model-facing.json`
   (`+Z`/`-Z` mesh facing, read from a rest render) — the runtime's truth table.
5. `roster/{fighter}/ATTIRE-SLOTS.md` — document the new slot (Tripo UUID,
   sha256, render proof).
6. Run the node test suites + the proof harness fight for this fighter;
   VIEW the frames (UNKNOWN is never PASS).
7. Delete this file when wiring lands (it is per-attire bookkeeping, not docs).
"""


def process_item(src_glb, fighter, attire, args, env_info, tools, sidecar=None):
    """Returns (status, summary_dict). status in done/refused/failed."""
    blender, node_modules = env_info
    repo = args.repo_root
    stage_root = args.stage_root
    report_root = args.report_root
    item_id = f"{fighter}-attire{attire}"
    rep_dir = os.path.join(report_root, f"{item_id}-{STAMP}")
    os.makedirs(rep_dir, exist_ok=True)
    log = []

    def refuse(reason, flag_name="FLAG-FACING-NEEDED.md", extra=None):
        summary = {"item": item_id, "status": "refused", "reason": reason,
                   "input": src_glb, "report_dir": rep_dir, "log": log}
        if extra:
            summary.update(extra)
        if not args.dry_run:
            dest = os.path.join(OUTBOX, fighter, f"attire{attire}", STAMP)
            os.makedirs(dest, exist_ok=True)
            shutil.copy(src_glb, os.path.join(dest, os.path.basename(src_glb)))
            if sidecar:
                shutil.copy(sidecar, dest)
            with open(os.path.join(dest, flag_name), "w") as f:
                f.write(f"# {flag_name}\n\n{item_id} refused by tripo-intake {STAMP}:\n\n{reason}\n")
            for fn in os.listdir(rep_dir):
                shutil.copy(os.path.join(rep_dir, fn), dest)
            summary["outbox"] = dest
        json.dump(summary, open(os.path.join(rep_dir, "intake_summary.json"), "w"), indent=1)
        return "refused", summary

    # 1. claim: fighter dir must exist; slot must be free; input must be an unrigged static
    roster_dir = os.path.join(repo, "roster", fighter)
    if not os.path.isdir(roster_dir):
        return refuse(f"unknown fighter: roster/{fighter}/ does not exist — the fighter id is "
                      f"the roster directory name and is never guessed "
                      f"(see roster/ for valid ids)")
    slot_dir = os.path.join(stage_root, "roster", fighter, "attires", f"attire{attire}")
    if os.path.exists(os.path.join(slot_dir, "model-rigged.glb")):
        return refuse(f"would clobber: {slot_dir}/model-rigged.glb already exists — "
                      f"owner decides replacements, the intake never overwrites")
    try:
        gj = glb_json(src_glb)
    except Exception as e:
        return "failed", {"item": item_id, "status": "failed",
                          "reason": f"input is not a readable GLB: {e}", "report_dir": rep_dir}
    if gj.get("skins"):
        return refuse(f"input already has {len(gj['skins'])} skin(s) — the intake only "
                      f"processes UNRIGGED statics; wire the existing file instead")
    digest = sha256_of(src_glb)
    log.append(f"sha256 {digest}")

    # 2. work dir + decode for facing
    work = tempfile.mkdtemp(prefix=f"wh-intake-{item_id}-")
    try:
        work_in = os.path.join(work, "in.glb")
        shutil.copy(src_glb, work_in)
        cc = codec_cmd(work, node_modules, tools["codec"])
        r = run(cc + ["decode", work_in, os.path.join(work, "decoded.glb")])
        if r.returncode != 0:
            return "failed", {"item": item_id, "status": "failed",
                              "reason": f"gltf_codec decode failed: {r.stderr[-2000:]}",
                              "report_dir": rep_dir}

        # 3. facing
        facing_report = os.path.join(rep_dir, "facing_report.json")
        if args.facing:
            facing, facing_source = args.facing, "manual override --facing"
            json.dump({"verdict": "CONFIDENT", "axis": facing, "source": facing_source,
                       "sha256": digest, "note": "operator-supplied; operator viewed rest renders"},
                      open(facing_report, "w"), indent=1)
            log.append(f"facing override: {facing}")
        else:
            fc = [sys.executable, tools["facing"], "--in", os.path.join(work, "decoded.glb"),
                  "--json-out", facing_report, "--quiet"]
            if not args.dry_run:
                fc += ["--ledger", LEDGER]
            r = run(fc)
            try:
                frep = json.load(open(facing_report))
            except Exception:
                frep = {"verdict": "REFUSE", "reasons": ["facing_check produced no report"]}
            if r.returncode != 0 or frep.get("verdict") != "CONFIDENT":
                reasons = "; ".join(frep.get("reasons", ["facing_check refused"]))
                if not args.dry_run:
                    led = load_ledger()
                    led[digest] = {"fighter": fighter, "attire": attire, "verdict": "REFUSE",
                                   "reasons": frep.get("reasons"), "date": TODAY,
                                   "report": facing_report}
                    save_ledger(led)
                return refuse(f"facing confidence too low — REFUSING to rig (never guess). "
                              f"{reasons}. View rest renders, determine facing, re-run with "
                              f"--facing <+X|-X|+Z|-Z>.",
                              extra={"facing_report": frep})
            facing = frep["axis"]
            facing_source = frep.get("source", "geometry cues")
            log.append(f"facing {facing} ({facing_source}) residual "
                       f"{frep['cue1']['residual_deg']}deg")

        # 4. rig via the proven pipeline
        os.makedirs(slot_dir, exist_ok=True)
        out_glb = os.path.join(slot_dir, "model-rigged.glb")
        rig_cmd = [sys.executable, tools["rig"], "--in", work_in, "--out", out_glb,
                   "--report-dir", rep_dir, "--facing", facing, "--height", args.height]
        env = dict(os.environ)
        env["WH_BLENDER"] = blender
        if os.environ.get("NODE_PATH"):
            env["NODE_PATH"] = os.environ["NODE_PATH"]
        else:
            env["NODE_PATH"] = node_modules
        r = run(rig_cmd, env=env)
        rig_report_p = os.path.join(rep_dir, "rig_report.json")
        if r.returncode != 0 or not os.path.exists(rig_report_p):
            return "failed", {"item": item_id, "status": "failed",
                              "reason": f"rig_tripo_static.py failed (exit {r.returncode}): "
                                        f"{r.stderr[-2000:]}",
                              "report_dir": rep_dir, "log": log}

        # 5. gates on rig_report.json
        # validate.py is the HARD playable gate (valid glTF, skinned mesh,
        # canonical bones, height 1.5-2.2m): it must pass or nothing stages.
        # anim_check is the deformation stress gate: its flags are RECORDED
        # and must be explained by viewing the renders before wiring (even the
        # shipped Zui A1 carries anim_check flags on the CMU clip) — flags do
        # not block staging, silence about them would.
        rep = json.load(open(rig_report_p))
        v = rep.get("validate", {})
        checks = v.get("checks", {}) or {}
        anims = rep.get("anim_check", {}) or {}
        v_ok = bool(v.get("pass")) and all(checks.values()) and bool(checks)
        bad_v = [k for k, okv in checks.items() if not okv]
        anim_flags = [f"{n}: {an.get('failures')}" for n, an in anims.items()
                      if not an.get("pass")]
        if not v_ok:
            return "failed", {"item": item_id, "status": "failed",
                              "reason": f"validate.py playable gate FAILED: "
                                        f"pass={v.get('pass')} failed_checks={bad_v}",
                              "report_dir": rep_dir, "log": log,
                              "rig_report": rig_report_p}

        # 6. stage + wiring checklist
        out_sha = sha256_of(out_glb)
        out_rel = os.path.relpath(out_glb, repo) if out_glb.startswith(repo) else out_glb
        rig_notes_p = os.path.join(repo, "roster", fighter, "RIG-NOTES.md")
        rig_notes = (f"roster/{fighter}/RIG-NOTES.md EXISTS — reviewer must apply its "
                     f"per-fighter specs (jiggle sets, M-rated anatomy, etc.); the auto-rig "
                     f"does not implement them") if os.path.exists(rig_notes_p) else "none on file"
        checklist = WIRING_TEMPLATE.format(
            fighter=fighter, attire=attire, stamp=STAMP,
            in_name=os.path.basename(src_glb), in_sha=digest,
            facing=facing, facing_source=facing_source, facing_report=facing_report,
            out_rel=out_rel, out_sha=out_sha,
            validate_verdict="PASS",
            anim_verdict=("FLAGS — explain before wiring: " + "; ".join(anim_flags)
                          if anim_flags else "PASS"),
            report_dir=rep_dir, rig_notes=rig_notes)
        with open(os.path.join(slot_dir, "WIRING-CHECKLIST.md"), "w") as f:
            f.write(checklist)

        summary = {"item": item_id, "status": "done", "input": src_glb,
                   "input_sha256": digest, "fighter": fighter, "attire": attire,
                   "facing": facing, "facing_source": facing_source,
                   "output": out_glb, "output_sha256": out_sha,
                   "validate": "PASS", "anim_check_flags": anim_flags,
                   "report_dir": rep_dir, "log": log}

        # 7. finalize (skip inbox/outbox/ledger writes in dry-run)
        if not args.dry_run:
            dest = os.path.join(OUTBOX, fighter, f"attire{attire}", STAMP)
            os.makedirs(dest, exist_ok=True)
            shutil.move(src_glb, os.path.join(dest, os.path.basename(src_glb)))
            if sidecar and os.path.exists(sidecar):
                shutil.move(sidecar, dest)
            for fn in os.listdir(rep_dir):
                shutil.copy(os.path.join(rep_dir, fn), dest)
            summary["outbox"] = dest
            led = load_ledger()
            led[digest] = {"fighter": fighter, "attire": attire, "facing": facing,
                           "facing_source": facing_source, "verdict": "CONFIDENT",
                           "output": out_rel, "output_sha256": out_sha,
                           "date": TODAY, "report": rep_dir}
            save_ledger(led)
        json.dump(summary, open(os.path.join(rep_dir, "intake_summary.json"), "w"), indent=1)
        return "done", summary
    finally:
        shutil.rmtree(work, ignore_errors=True)


def scan_inbox():
    items = []
    if not os.path.isdir(INBOX):
        return items
    for fighter in sorted(os.listdir(INBOX)):
        fdir = os.path.join(INBOX, fighter)
        if not os.path.isdir(fdir):
            continue
        for glb in sorted(glob.glob(os.path.join(fdir, "attire*.glb"))):
            m = re.search(r"attire(\d+)\.glb$", glb)
            if not m:
                continue
            sidecar = os.path.join(fdir, f"attire{m.group(1)}.json")
            items.append((glb, fighter, int(m.group(1)),
                          sidecar if os.path.exists(sidecar) else None))
    return items


def main():
    ap = argparse.ArgumentParser(description="Tripo auto-intake: rig new statics ASAP.")
    ap.add_argument("--scan", action="store_true", help="process every inbox/<fighter>/attire<N>.glb")
    ap.add_argument("--in", dest="inp", default=None)
    ap.add_argument("--fighter", default=None, help="roster/<dir> name — never guessed")
    ap.add_argument("--attire", type=int, default=None)
    ap.add_argument("--facing", default=None, choices=["+X", "-X", "+Z", "-Z"],
                    help="manual override: skip the facing gate (operator viewed rest renders)")
    ap.add_argument("--height", default="1.8")
    ap.add_argument("--stage-root", default=None, help="default: repo root (dry-run: /tmp/...)")
    ap.add_argument("--report-root", default=None)
    ap.add_argument("--repo-root", default=DEFAULT_REPO)
    ap.add_argument("--dry-run", action="store_true",
                    help="full pipeline, but stage to --stage-root and skip inbox/outbox/ledger writes")
    args = ap.parse_args()
    repo = args.repo_root
    if not args.stage_root:
        args.stage_root = repo
    if not args.report_root:
        args.report_root = os.path.join(repo, "docs", "proof", f"muse-{TODAY}", "tripo-intake")

    tools = tool_paths(repo)
    problems, blender, node_modules = check_env(repo)
    if problems:
        sys.exit("intake env check FAILED:\n  - " + "\n  - ".join(problems))

    if args.scan:
        items = scan_inbox()
        if not items:
            print(f"inbox empty: {INBOX}/<fighter>/attire<N>.glb (+ optional attire<N>.json)")
            return 0
    else:
        if not (args.inp and args.fighter and args.attire):
            sys.exit("need --scan or all of --in --fighter --attire")
        items = [(args.inp, args.fighter, args.attire, None)]

    env_info = (blender, node_modules)
    results = []
    for src_glb, fighter, attire, sidecar in items:
        if not os.path.isfile(src_glb):
            results.append(("failed", {"item": f"{fighter}-attire{attire}",
                                       "status": "failed",
                                       "reason": f"input not found: {src_glb}"}))
            continue
        try:
            st, summary = process_item(src_glb, fighter, attire, args, env_info, tools, sidecar)
        except Exception as e:  # noqa: BLE001 — one bad item never kills the scan
            st, summary = "failed", {"item": f"{fighter}-attire{attire}", "status": "failed",
                                     "reason": f"unexpected: {e!r}"}
        results.append((st, summary))
        print(f"[{st.upper()}] {summary['item']}: {summary.get('reason', summary.get('output', ''))}")

    worst = {"done": 0, "refused": 2, "failed": 3}
    code = max(worst[st] for st, _ in results) if results else 0
    print(json.dumps({"results": [s for _, s in results]}, indent=1))
    sys.exit(code)


if __name__ == "__main__":
    main()
