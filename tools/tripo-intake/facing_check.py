#!/usr/bin/env python3
"""tools/tripo-intake/facing_check.py — automatic facing determination for unrigged Tripo statics.

Reads a DECODED (meshopt-free) GLB and decides which way the mesh faces
(+X / -X / +Z / -Z in glTF axes) from TWO independent geometry cues:

  cue1 — the gamerig computation: tools/auto_rig/backends/gamerig_backend.py
         normalize_and_face() estimates facing from the foot band (bottom 8%
         of height) vs the shin band (18-30%) horizontal centroids. The same
         math, re-implemented here in plain numpy so it runs without Blender.
         Known failure: it can land well off-axis (-74 deg instead of -90 on
         the demonio-a1 Tripo pull, 2026-10-20); used raw, that put the
         metarig's arms outside the mesh's arms and bone heat failed for every
         vertex. This script SNAPS the raw yaw to the nearest cardinal axis
         and REFUSES when the residual is large instead of trusting the raw
         angle.

  cue2 — the runtime computation: game/js/assets.js feetFacingCue(), the
         lowest-5% band's toe-vs-heel extent asymmetry near each ankle
         (|score| >= 0.05, the threshold that misread no model in the 52-model
         rest-render check, 2026-10-20). Run here on both the Z and X axes
         (the game only needs Z); the dominant axis wins. Ankle positions come
         from the shin band above each foot (no bones exist on a static).

CONFIDENCE GATE — all must hold, else verdict REFUSE (exit 2). Never guess:
  1. cue1's snapped axis == cue2's dominant axis (sign included)
  2. |cue1 raw yaw - snapped axis| <= --residual-deg (default 15)
  3. cue1 toe-offset magnitude >= --min-mag-frac of height (default 0.015)
  4. >= --min-band-verts verts in each band (default 500)

Usage:
    python3 facing_check.py --in DECODED.glb [--json-out facing_report.json]
                            [--residual-deg 15] [--quiet]

Exit 0: CONFIDENT (axis printed + in the JSON report).
Exit 2: REFUSE — flag for human review (a human views rest renders, then
        re-runs the intake with --facing <axis> as a manual override).

Aligns with the repo's facing truth source: game/assets/models/model-facing.json
(hand-verified rest renders) remains authoritative for WIRED models; this
script is the automatic gate for NEW, never-before-seen statics. Its ledger
(tools/tripo-intake/ledger.json, keyed by sha256) is consulted first when
--ledger is given so a re-intake of the same bytes decides identically.
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "anim"))
from t3_bank_skeleton import read_glb, accessor  # noqa: E402

AXES = {"+X": 0.0, "+Z": 90.0, "-X": 180.0, "-Z": -90.0}  # yaw deg = atan2(z, x)


def ang_diff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def world_verts(j, blob):
    """All POSITION verts in world space (node transforms applied)."""
    N = j.get("nodes", [])
    par = {c: i for i, nd in enumerate(N) for c in nd.get("children", [])}

    def local(i):
        nd = N[i]
        if "matrix" in nd:
            return np.array(nd["matrix"], float).reshape(4, 4).T
        m = np.eye(4)
        t = nd.get("translation")
        if t:
            m[:3, 3] = t
        q = nd.get("rotation")
        if q and q != [0, 0, 0, 1]:
            x, y, z, w = q
            m[:3, :3] = np.array([
                [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        s = nd.get("scale")
        if s:
            m[:3, :3] *= np.array(s, float)
        return m

    world = {}

    def w(i):
        if i in world:
            return world[i]
        m = local(i)
        if i in par:
            m = w(par[i]) @ m
        world[i] = m
        return m

    out = []
    for mi, mesh in enumerate(j.get("meshes", [])):
        for pr in mesh.get("primitives", []):
            at = pr.get("attributes", {})
            if "POSITION" not in at:
                continue
            pos = accessor(j, blob, at["POSITION"]).astype(float)
            node = pr.get("node", mesh.get("node", 0))
            # find owning node: search nodes referencing this mesh
            owner = next((i for i, nd in enumerate(N)
                          if nd.get("mesh") == mi), 0)
            M = w(owner)
            homo = np.concatenate([pos, np.ones((len(pos), 1))], axis=1)
            out.append((homo @ M.T)[:, :3])
    if not out:
        raise RuntimeError("no POSITION vertices found")
    return np.concatenate(out)


def cue1(x, y, z):
    """gamerig foot-vs-shin cue. -> (raw_yaw_deg, snapped, residual_deg, mag_frac, n_foot, n_shin)."""
    y0, y1 = y.min(), y.max()
    h = y1 - y0
    foot = y < y0 + 0.08 * h
    shin = (y > y0 + 0.18 * h) & (y < y0 + 0.30 * h)
    n_foot, n_shin = int(foot.sum()), int(shin.sum())
    if n_foot == 0 or n_shin == 0:
        return None
    f = np.array([x[foot].mean() - x[shin].mean(),
                  z[foot].mean() - z[shin].mean()])
    mag = float(np.linalg.norm(f))
    raw_yaw = math.degrees(math.atan2(f[1], f[0]))
    snapped = min(AXES, key=lambda a: ang_diff(raw_yaw, AXES[a]))
    residual = ang_diff(raw_yaw, AXES[snapped])
    return raw_yaw, snapped, residual, mag / h, n_foot, n_shin


def cue2(x, y, z):
    """assets.js feetFacingCue cue on both axes. -> (scores, dominant_axis_or_None)."""
    y0, y1 = y.min(), y.max()
    h = y1 - y0
    low = y < y0 + 0.05 * h
    out = {}
    for ax, perp in (("z", "x"), ("x", "z")):
        A = z if ax == "z" else x
        P = x if perp == "x" else z
        pl, ph = P[low], A[low]
        if len(pl) < 20:
            out[ax] = (0.0, 0)
            continue
        med = np.median(pl)
        score = 0.0
        for side in (pl > med, pl <= med):
            a_perp = float(np.median(pl[side]))
            near = (np.abs(pl - a_perp) < 0.06 * h) & side
            ank = A[(y > y0 + 0.09 * h) & (y < y0 + 0.20 * h) &
                    (np.abs(P - a_perp) < 0.06 * h)]
            if len(ank) < 10 or int(near.sum()) < 10:
                continue
            a_ax = float(np.median(ank))
            c = ph[near]
            lo, hi = np.percentile(c, 1), np.percentile(c, 99)
            score += ((hi - a_ax) - (a_ax - lo)) / h
        sign = 1 if score >= 0.05 else (-1 if score <= -0.05 else 0)
        out[ax] = (float(score), sign)
    cands = [(ax, s, sg) for ax, (s, sg) in out.items() if sg != 0]
    if not cands:
        return out, None
    ax, _s, sg = max(cands, key=lambda t: abs(t[1]))
    return out, ("+" if sg > 0 else "-") + ax.upper()


def decide(verts, residual_deg=15.0, min_mag_frac=0.015, min_band_verts=500):
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    h = float(y.max() - y.min())
    c1 = cue1(x, y, z)
    scores, dom = cue2(x, y, z)
    rep = {"height_m": round(h, 4),
           "cue1": None,
           "cue2": {a: {"score": round(s, 4), "sign": sg} for a, (s, sg) in scores.items()},
           "cue2_axis": dom,
           "gate": {"residual_deg_max": residual_deg, "min_mag_frac": min_mag_frac,
                    "min_band_verts": min_band_verts},
           "verdict": "REFUSE", "reasons": []}
    if c1 is None:
        rep["reasons"].append("cue1: empty foot or shin band")
        return rep
    raw_yaw, snapped, residual, mag_frac, n_foot, n_shin = c1
    rep["cue1"] = {"raw_yaw_deg": round(raw_yaw, 2), "snapped": snapped,
                   "residual_deg": round(residual, 2), "mag_frac": round(mag_frac, 4),
                   "n_foot": n_foot, "n_shin": n_shin}
    ok = True
    if dom is None:
        ok = False
        rep["reasons"].append("cue2: no confident axis (|score| < 0.05 on both axes)")
    elif dom != snapped:
        ok = False
        rep["reasons"].append(f"cues disagree: cue1={snapped} cue2={dom}")
    if residual > residual_deg:
        ok = False
        rep["reasons"].append(f"residual {residual:.1f}deg > {residual_deg}deg (off-axis mesh?)")
    if mag_frac < min_mag_frac:
        ok = False
        rep["reasons"].append(f"toe offset {mag_frac:.4f} of height < {min_mag_frac} (noise level)")
    if n_foot < min_band_verts or n_shin < min_band_verts:
        ok = False
        rep["reasons"].append(f"thin bands: foot={n_foot} shin={n_shin} (< {min_band_verts})")
    if ok:
        rep["verdict"] = "CONFIDENT"
        rep["axis"] = snapped
    return rep


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="DECODED glb (meshopt-free)")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--ledger", default=None, help="tools/tripo-intake/ledger.json for sha256 lookup")
    ap.add_argument("--residual-deg", type=float, default=15.0)
    ap.add_argument("--min-mag-frac", type=float, default=0.015)
    ap.add_argument("--min-band-verts", type=int, default=500)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    digest = sha256_of(a.inp)
    if a.ledger and os.path.exists(a.ledger):
        try:
            led = json.load(open(a.ledger))
            if digest in led:
                e = led[digest]
                rep = {"verdict": e.get("verdict", "REFUSE"), "axis": e.get("facing"),
                       "source": "ledger", "sha256": digest,
                       "note": "identical bytes decided before; refusing to re-decide"}
                if not a.quiet:
                    print(json.dumps(rep, indent=1))
                if a.json_out:
                    json.dump(rep, open(a.json_out, "w"), indent=1)
                sys.exit(0 if rep["verdict"] == "CONFIDENT" else 2)
        except (json.JSONDecodeError, OSError):
            pass

    j, blob = read_glb(__import__("pathlib").Path(a.inp))
    verts = world_verts(j, blob)
    rep = decide(verts, a.residual_deg, a.min_mag_frac, a.min_band_verts)
    rep["sha256"] = digest
    rep["input"] = a.inp
    rep["source"] = "geometry cues (cue1=gamerig foot-vs-shin, cue2=assets.js feetFacingCue)"
    if not a.quiet:
        print(json.dumps(rep, indent=1))
    if a.json_out:
        json.dump(rep, open(a.json_out, "w"), indent=1)
    sys.exit(0 if rep["verdict"] == "CONFIDENT" else 2)


if __name__ == "__main__":
    main()
