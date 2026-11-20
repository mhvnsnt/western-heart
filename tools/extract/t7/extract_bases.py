#!/usr/bin/env python3
"""Extract Tekken 7 base-character rig kits (skeleton + Namco-weighted
skeletal meshes) straight from the release-held paks — no local pak staging.

Pipeline (GRE-proven, tools/extract/t7/extract_pak.sh):
  pak_index.Pak over release_range.ReleaseFile
    -> pull each kit .uasset/.uexp by HTTP range
    -> t7_decrypt.fix (per-asset AES fix, community key)
    -> umodel -game=tekken7 -export -gltf -notex
    -> pygltflib gltf->glb + verification (skin joints, WEIGHTS_0, bone names)

A T7 fighter is an assembly: Face (<code>_fac) + Upper (<code>_bdu_1p) +
Lower (<code>_bdl_1p) + Hair (<code>_har_1p / <code>_fah_1p) + Extra
(<code>_exp_1p), all skinned to the shared base skeleton
(Character/Common/Skeleton/SKT_CH_base_Skeleton). Kit membership per base
is declared in t7_bases.json; pak locations in t7_sources.json.

Usage:
  extract_bases.py --only kin [--only jul ...] --workdir W --outdir O \
      --umodel /path/to/umodel [--sources t7_sources.json] [--bases t7_bases.json]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pak_index import Pak                      # noqa: E402
from release_range import GitHubReleaseParts, ReleaseFile, get_token  # noqa: E402
import urllib.request                          # noqa: E402

try:
    from t7_decrypt import fix as asset_fix    # in-repo sibling
except ImportError:                            # scratch layout fallback
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ref"))
    from t7_decrypt import fix as asset_fix    # noqa: E402


def release_parts(backend, prefix):
    """(name, size) list for one pak's parts on a release, in order."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{backend.repo}/releases/{backend.release_id}"
        f"/assets?per_page=100", headers={
            "Authorization": f"Bearer {backend.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "wh-t7-extract/1.0"})
    sizes = {}
    page = 1
    while True:
        r = urllib.request.Request(
            f"https://api.github.com/repos/{backend.repo}/releases/{backend.release_id}"
            f"/assets?per_page=100&page={page}", headers={
                "Authorization": f"Bearer {backend.token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "wh-t7-extract/1.0"})
        with urllib.request.urlopen(r, timeout=60) as resp:
            assets = json.loads(resp.read().decode())
        if not assets:
            break
        for a in assets:
            sizes[a["name"]] = a["size"]
        if len(assets) < 100:
            break
        page += 1
    parts = sorted((n, s) for n, s in sizes.items() if n.startswith(prefix))
    if not parts:
        raise SystemExit(f"no parts with prefix {prefix} on {backend.repo} release")
    return parts


def open_pak(sources, pak_key):
    spec = sources["paks"][pak_key]
    src = spec["read_from"]
    backend = GitHubReleaseParts(src["repo"], src["release"], token=get_token())
    parts = release_parts(backend, spec["part_prefix"])
    rf = ReleaseFile(backend, parts)
    if rf.size != spec["size"]:
        raise SystemExit(f"{pak_key}: virtual size {rf.size} != manifest {spec['size']}")
    return Pak(rf), spec


class PakView:
    """Canonical game paths for a Pak. pakchunk0 stores names in full
    (TekkenGame/Content/...) under mount '../../../', while pakchunk1_P
    mounts at '../../../TekkenGame/Content/' and stores names relative to
    it. Canonical name = mount (sans ../) + stored name."""

    def __init__(self, pak):
        self.pak = pak
        m = pak.mount
        while m.startswith("../"):
            m = m[3:]
        self.canon = {}
        for raw in pak.by_name:
            c = raw if (not m or raw.startswith(m)) else m + raw
            self.canon[c] = raw

    def __contains__(self, canon_name):
        return canon_name in self.canon

    def entry(self, canon_name):
        return self.pak.by_name[self.canon[canon_name]]


def kit_entries(view, code, patterns):
    """Map slot -> [canonical entry names] for one base's default kit.

    Matching is by (part directory, mesh stem), case-insensitive, ignoring
    the item-folder segment: the game is not consistent — Steve's face sits
    at ste/Face/Meshes/SK_CH_ste_fac.uasset (no item folder) and Lili's
    lower is spelled SK_CH_lil_bdl_1P (capital P). Split meshes are the
    main stem plus a single-letter suffix (_A, _B, ...)."""
    root = f"TekkenGame/Content/Character/Item/Meshes/{code}/"
    out = {}
    for slot, pats in patterns.items():
        names = []
        for pat in pats:
            p = pat.format(code=code)
            part_dir, item = p.split("/")[0], p.split("/")[-1]
            want = f"sk_ch_{item}"
            for name in view.canon:
                if not name.startswith(root) or not name.endswith(".uasset"):
                    continue
                rel = name[len(root):].split("/")
                if len(rel) < 3 or rel[0] != part_dir or rel[-2] != "Meshes":
                    continue
                stem = rel[-1][:-len(".uasset")].lower()
                if stem == want or (stem.startswith(want + "_")
                                    and len(stem) == len(want) + 2
                                    and stem[-1].isalpha()):
                    names.append(name)
        if names:
            out[slot] = sorted(set(names))
    # Head slot: explicit <code>_hed_1p if present, else the single hed item.
    hed = [n for n in view.canon
           if n.startswith(root + "Head/") and "/Meshes/SK_CH_" in n
           and n.endswith(".uasset") and n.count("/") == root.count("/") + 3]
    hed1p = [n for n in hed if "_hed_1p" in n]
    if hed1p:
        out["head"] = sorted(hed1p)
    elif len(hed) == 1:
        out["head"] = hed
    return out


def extract_entry(view, name, workroot):
    """Pull one entry (+ .uexp companion) into workroot/<canonical name>."""
    facts = {"pak_path": name}
    for suffix in ("", ".uexp"):
        ename = name if suffix == "" else name[:-len(".uasset")] + ".uexp"
        if ename not in view:
            if suffix == "":
                raise KeyError(name)
            facts["uexp"] = None
            continue
        e = view.entry(ename)
        data = view.pak.extract(e)
        dest = os.path.join(workroot, ename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        key = "uasset" if suffix == "" else "uexp"
        facts[key] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                      "pak_entry_sha1": e.get("sha1")}
    return facts


def umodel_export(umodel, workroot, rel_uasset, outdir):
    """Export ONE asset into a FRESH out dir; return its own .gltf only.
    (umodel mirrors the package path under -out; matching by exact stem in a
    clean dir prevents cross-asset mixups.)"""
    import shutil
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)
    p = subprocess.run([umodel, "-game=tekken7", "-path=.", "-export", "-gltf",
                        "-notex", f"-out={outdir}", rel_uasset],
                       cwd=workroot, capture_output=True, text=True, timeout=600)
    stem = os.path.splitext(os.path.basename(rel_uasset))[0]
    gltfs = []
    for dp, _, fs in os.walk(outdir):
        for f in fs:
            if f == stem + ".gltf":
                gltfs.append(os.path.join(dp, f))
    return p.returncode, p.stdout[-2000:], gltfs


def glb_convert_and_verify(gltf_path, glb_path):
    from pygltflib import GLTF2
    g = GLTF2().load(gltf_path)
    joints = 0
    bone_names = []
    weights = False
    if g.skins:
        skin = max(g.skins, key=lambda s: len(s.joints))
        joints = len(skin.joints)
        bone_names = [g.nodes[j].name for j in skin.joints]
    verts = 0
    for mesh in g.meshes or []:
        for prim in mesh.primitives:
            if prim.attributes.WEIGHTS_0 is not None:
                weights = True
            if prim.attributes.POSITION is not None:
                verts += g.accessors[prim.attributes.POSITION].count
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    g.convert_buffers("binary_blob")
    g.save_binary(glb_path)
    return {"joints": joints, "weights": weights, "bone_names": bone_names,
            "vertices": verts, "glb_bytes": os.path.getsize(glb_path)}


SKELETON_ENTRIES = [
    "TekkenGame/Content/Character/Common/Skeleton/SKT_CH_base_Skeleton.uasset",
    "TekkenGame/Content/Character/Common/Skeleton/AB_CH_base_Skeleton.uasset",
]


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--sources", default=os.path.join(here, "t7_sources.json"))
    ap.add_argument("--bases", default=os.path.join(here, "t7_bases.json"))
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--umodel", required=True)
    a = ap.parse_args()
    # umodel resolves -out against its own cwd quirks; absolute paths only.
    a.workdir = os.path.abspath(a.workdir)
    a.outdir = os.path.abspath(a.outdir)
    a.umodel = os.path.abspath(a.umodel)

    sources = json.load(open(a.sources))
    bases_doc = json.load(open(a.bases))
    patterns = bases_doc["kit_patterns"]
    wanted = [b for b in bases_doc["bases"] if not a.only or b["code"] in a.only]
    if not wanted:
        raise SystemExit("no bases selected")

    paks = {}
    # Resume support: seed from an existing manifest; assets already recorded
    # with a GLB on disk are skipped (their records are carried over).
    top = {"sources": {}, "bases": {}}
    man_path = os.path.join(a.outdir, "extraction-manifest.json")
    if os.path.exists(man_path):
        top = json.load(open(man_path))

    def cached(code, slot, name):
        recs = top.get("bases", {}).get(code, {}).get("slots", {}).get(slot, [])
        stem = os.path.splitext(os.path.basename(name))[0]
        for r in recs:
            if r.get("pak_path") == name and r.get("glb"):
                p = os.path.join(a.outdir, code, slot, stem + ".glb")
                if os.path.exists(p):
                    return True
        return False
    # shared skeleton first (from pakchunk0)
    pak0, spec0 = open_pak(sources, "pakchunk0")
    view0 = PakView(pak0)
    paks["pakchunk0"] = (pak0, spec0, view0)
    shared_dir = os.path.join(a.outdir, "_shared")
    shared = {"pak": "pakchunk0", "assets": []}
    swork = os.path.join(a.workdir, "pakchunk0")
    for name in SKELETON_ENTRIES:
        if name not in view0:
            shared["assets"].append({"pak_path": name, "missing": True})
            continue
        facts = extract_entry(view0, name, swork)
        fixres = asset_fix(os.path.join(swork, name))
        facts["decrypt_fix"] = fixres
        s_stem = os.path.splitext(os.path.basename(name))[0]
        rc, log, gltfs = umodel_export(a.umodel, swork, name,
                                       os.path.join(a.workdir, f"umodel_shared_{s_stem}"))
        facts["umodel_rc"] = rc
        for gt in gltfs:
            stem = os.path.splitext(os.path.basename(gt))[0]
            facts["glb"] = glb_convert_and_verify(
                gt, os.path.join(shared_dir, stem + ".glb"))
        if not gltfs:
            # umodel exports 0 objects for a standalone Skeleton asset; the
            # skeleton ships embedded in every skeletal mesh GLB instead.
            # Commit the raw extracted asset so the repo holds it directly.
            import shutil
            raw_dest = os.path.join(shared_dir, "raw", os.path.basename(name))
            os.makedirs(os.path.dirname(raw_dest), exist_ok=True)
            shutil.copyfile(os.path.join(swork, name), raw_dest)
            facts["raw_asset"] = os.path.relpath(raw_dest, a.outdir)
            facts["note"] = ("umodel glTF export of a standalone Skeleton asset "
                             "yields 0 objects; skeleton is embedded in every "
                             "per-base skeletal-mesh GLB (see bone_names there).")
        shared["assets"].append(facts)
    top["shared_skeleton"] = shared

    for b in wanted:
        code = b["code"]
        pak_key = b["pak"]
        if pak_key not in paks:
            _p, _s = open_pak(sources, pak_key)
            paks[pak_key] = (_p, _s, PakView(_p))
        pak, spec, view = paks[pak_key]
        top["sources"][pak_key] = {"file": spec["file"], "sha256": spec["sha256"],
                                   "read_from": spec["read_from"],
                                   "index_entries": len(pak.entries),
                                   "pak_version": pak.footer["version"]}
        work = os.path.join(a.workdir, pak_key)
        if pak_key != "pakchunk0":
            # umodel resolves the shared skeleton inside the export root:
            # seed this pak's workroot with it (from this pak if it carries
            # a copy, else the byte-identical pakchunk0 extraction).
            import shutil
            for sname in SKELETON_ENTRIES:
                dest = os.path.join(work, sname)
                if os.path.exists(dest):
                    continue
                if sname in view:
                    extract_entry(view, sname, work)
                elif os.path.exists(os.path.join(swork, sname)):
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copyfile(os.path.join(swork, sname), dest)
        kit = kit_entries(view, code, patterns)
        # per-character skeleton asset if the game ships one
        skt = f"TekkenGame/Content/Character/Item/Meshes/{code}/Meshes/SKT_CH_{code}.uasset"
        base_rec = {"name": b["name"], "code": code, "roster_code": b["roster_code"],
                    "wh_fighter": b["wh_fighter"], "pak": pak_key, "slots": {}}
        jobs = [(slot, name) for slot, names in kit.items() for name in names]
        if skt in view:
            jobs.append(("skeleton", skt))
        old_slots = top.get("bases", {}).get(code, {}).get("slots", {})
        for slot, name in jobs:
            if cached(code, slot, name):
                print(f"{code}/{slot}: {os.path.basename(name)} cached, skip", flush=True)
                old = [r for r in old_slots.get(slot, []) if r.get("pak_path") == name]
                base_rec["slots"].setdefault(slot, []).extend(old)
                continue
            rec = extract_entry(view, name, work)
            rec["decrypt_fix"] = asset_fix(os.path.join(work, name))
            stem0 = os.path.splitext(os.path.basename(name))[0]
            uout = os.path.join(a.workdir, f"umodel_{code}_{stem0}")
            rc, log, gltfs = umodel_export(a.umodel, work, name, uout)
            rec["umodel_rc"] = rc
            if gltfs:
                stem = os.path.splitext(os.path.basename(name))[0]
                rec["glb"] = glb_convert_and_verify(
                    gltfs[0], os.path.join(a.outdir, code, slot, stem + ".glb"))
            else:
                rec["umodel_log_tail"] = log
            base_rec["slots"].setdefault(slot, []).append(rec)
            print(f"{code}/{slot}: {os.path.basename(name)} rc={rc} "
                  f"joints={rec.get('glb', {}).get('joints')} "
                  f"weights={rec.get('glb', {}).get('weights')}", flush=True)
        merged = dict(old_slots)
        merged.update(base_rec["slots"])
        base_rec["slots"] = merged
        top["bases"][code] = base_rec

    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "extraction-manifest.json"), "w") as f:
        json.dump(top, f, indent=1)
    print("manifest ->", os.path.join(a.outdir, "extraction-manifest.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
