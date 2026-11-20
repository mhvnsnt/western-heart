#!/usr/bin/env python3
"""pipeline.py - universal rig-repair orchestrator.

One command per model; batch via xargs -P (one Blender process per model
per stage = crash isolation).

  python3 pipeline.py --in MODEL.glb --outdir OUTDIR --tag TAG
      [--transfer-src CANONICAL.glb] [--reskin {shd,heat,none}]
      [--from-stage STAGE] [--skip-proof]

Stages (each writes a VERSIONED file + JSON report; inputs never touched):
  detect    rig_repair.py detect (multi-mesh, meshopt/multi-buffer safe)
  transfer  rig_repair.py transfer --limb-separate (only if --transfer-src)
  refit     refit.py (Blender volume-mode skeleton refit, IBMs recomputed)
  reskin    reskin.py (shd) | reskin_heat.py | none [default: none --
            keep transfer weights; re-skin only when weights are missing]
  separate  separate.py (topology limb/body separation, numpy)
  armpit    armpit.py (de-bleed + sharpen + torso-side, numpy)
  weldcap   weldcap.py (Blender recalc + hard assert zero open edges)
  gate      rig_check.py (p99.9 stretch vs 2.5, ground, hinge)
  proof     proof.py (Blender stress-pose renders, own-eyes verification)

Batch:
  ls models/*.glb | xargs -P 4 -I{} python3 pipeline/pipeline.py \
      --in {} --outdir out --tag $(basename {} .glb)
"""
import argparse, json, os, subprocess, sys, hashlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.path.expanduser("~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")
BFLAGS = ["--background", "--factory-startup", "--disable-autoexec",
          "--python-exit-code", "1"]

STAGES = ["detect", "transfer", "refit", "reskin", "separate", "armpit",
          "weldcap", "gate", "proof"]

def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def run(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    if r.returncode != 0:
        print(r.stdout[-3000:], file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        raise RuntimeError(f"stage failed: {' '.join(cmd[:6])}... (rc={r.returncode})")
    return r

def blender(script, args):
    # one process per stage; crash isolation (NO-SHORTCUTS: never reuse a
    # Blender process across models). PYTHONPATH is stripped from the child
    # env (equivalent to env -u PYTHONPATH).
    e = dict(os.environ); e.pop("PYTHONPATH", None); e["XDG_RUNTIME_DIR"] = "/tmp"
    cmd = [BLENDER] + BFLAGS + ["--python", os.path.join(HERE, script), "--"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    if r.returncode != 0:
        print(r.stdout[-3000:], file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        raise RuntimeError(f"blender stage {script} failed (rc={r.returncode})")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--transfer-src", default=None)
    ap.add_argument("--reskin", choices=["shd", "heat", "none"], default="none")
    ap.add_argument("--from-stage", default="detect", choices=STAGES)
    ap.add_argument("--skip-proof", action="store_true")
    ap.add_argument("--clips", default=os.path.join(HERE, "clips", "standard"))
    ap.add_argument("--facing", default="+X")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    cur = os.path.abspath(a.inp)
    manifest = {"tag": a.tag, "input": cur, "input_sha256": sha256(cur), "stages": {}}
    start = STAGES.index(a.from_stage)

    def stage_out(name):
        return os.path.join(a.outdir, f"{a.tag}_{name}.glb")

    def note(name, out, rep):
        manifest["stages"][name] = {"out": out, "report": rep,
                                    "sha256": sha256(out) if out and os.path.exists(out) else None}

    # ---- detect ----
    if start <= 0:
        rep = os.path.join(a.outdir, f"{a.tag}_detect.json")
        run([sys.executable, os.path.join(HERE, "rig_repair.py"), "detect",
             cur, "--json", rep])
        note("detect", None, rep)

    # ---- transfer (optional) ----
    if start <= 1 and a.transfer_src:
        out = stage_out("transfer")
        rep = os.path.join(a.outdir, f"{a.tag}_transfer.json")
        run([sys.executable, os.path.join(HERE, "rig_repair.py"), "transfer",
             "--src", a.transfer_src, "--tgt", cur, "--out", out,
             "--limb-separate", "--json", rep])
        cur = out; note("transfer", out, rep)
    elif start <= 1:
        manifest["stages"]["transfer"] = {"skipped": "no --transfer-src"}

    # ---- refit (Blender) ----
    if start <= 2:
        out = stage_out("refit")
        rep = os.path.join(a.outdir, f"{a.tag}_refit.json")
        blender("refit.py", ["--in", cur, "--out", out, "--report", rep,
                             "--rays", "6", "--clamp", "0.10"])
        cur = out; note("refit", out, rep)

    # ---- reskin (Blender, conditional) ----
    if start <= 3 and a.reskin != "none":
        out = stage_out("reskin")
        rep = os.path.join(a.outdir, f"{a.tag}_reskin.json")
        script = "reskin.py" if a.reskin == "shd" else "reskin_heat.py"
        blender(script, ["--in", cur, "--out", out, "--report", rep])
        cur = out; note("reskin", out, rep)
    elif start <= 3:
        manifest["stages"]["reskin"] = {"skipped": "reskin=none (keep transfer weights)"}

    # ---- separate (numpy) ----
    if start <= 4:
        out = stage_out("separate")
        rep = os.path.join(a.outdir, f"{a.tag}_separate.json")
        run([sys.executable, os.path.join(HERE, "separate.py"),
             "--in", cur, "--out", out, "--report", rep])
        cur = out; note("separate", out, rep)

    # ---- armpit (numpy) ----
    if start <= 5:
        out = stage_out("armpit")
        rep = os.path.join(a.outdir, f"{a.tag}_armpit.json")
        run([sys.executable, os.path.join(HERE, "armpit.py"),
             "--in", cur, "--out", out, "--report", rep, "--force"])
        cur = out; note("armpit", out, rep)

    # ---- weldcap (Blender) ----
    if start <= 6:
        out = stage_out("weldcap")
        rep = os.path.join(a.outdir, f"{a.tag}_weldcap.json")
        blender("weldcap.py", ["--in", cur, "--out", out, "--report", rep])
        cur = out; note("weldcap", out, rep)

    # ---- gate ----
    if start <= 7:
        rep = os.path.join(a.outdir, f"{a.tag}_gate.json")
        # rc=1 with a written JSON = verdict FAIL (valid outcome, not a crash)
        try:
            run([sys.executable, os.path.join(HERE, "rigcheck", "rig_check.py"),
                 cur, "--clips", a.clips, "--facing", a.facing,
                 "--json", rep, "--quiet"])
        except RuntimeError as ex:
            if not (os.path.exists(rep) and "rc=1" in str(ex)):
                raise
            print("gate: verdict FAIL (rc=1, JSON written)")
        g = json.load(open(rep))
        manifest["stages"]["gate"] = {"report": rep, "verdict": g.get("verdict")}
        print("gate verdict:", g.get("verdict"))
        for c in g.get("clips", []):
            print(f"  {c['clip']:10} p99.9={c.get('stretch_p999_max')}")

    # ---- proof (Blender) ----
    if start <= 8 and not a.skip_proof:
        pdir = os.path.join(a.outdir, f"{a.tag}_proof")
        blender("proof.py", ["--in", cur, "--outdir", pdir,
                             "--tag", a.tag, "--res", "640"])
        manifest["stages"]["proof"] = {"outdir": pdir}
        print("proof renders in", pdir, "-- OPEN EVERY ONE YOURSELF")

    manifest["final"] = cur
    mf = os.path.join(a.outdir, f"{a.tag}_manifest.json")
    json.dump(manifest, open(mf, "w"), indent=1)
    print("manifest:", mf)
    print("final:", cur, sha256(cur)[:16])

if __name__ == "__main__":
    main()
