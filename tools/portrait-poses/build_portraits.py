#!/usr/bin/env python3
"""tools/portrait-poses/build_portraits.py — resolve fighter->model, decode, render all portraits.

Fighter's portrait model = the model the select screen shows by default
(game/js/attires.js selectedAttireModel: first ATTIRE_VARIANTS entry for the
fighter's model key, else the fighter's own model key), resolved through
game/js/assets.js MODEL_URLS.

    python3 tools/portrait-poses/build_portraits.py [--only id1,id2] [--outdir game/assets/portraits]

Env: WH_BLENDER (default ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender),
NODE_PATH (gltf node_modules for the meshopt decode).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CODEC = os.path.join(REPO, "tools", "anim", "gltf_codec.mjs")


def parse_roster():
    text = open(os.path.join(REPO, "game/js/roster-full.js")).read()
    out = []
    for block in re.findall(r"\{ id: '[^']+',.*?\},", text, re.S):
        fid = re.search(r"id: '([^']+)'", block).group(1)
        m = re.search(r"model: '([^']+)'", block)
        out.append((fid, m.group(1) if m else None))
    return out


def parse_attire_variants():
    text = open(os.path.join(REPO, "game/js/attires.js")).read()
    variants = {}
    for m in re.finditer(r"'([^']+)': \[(.*?)\],\n", text, re.S):
        key, body = m.group(1), m.group(2)
        models = re.findall(r"model: '([^']+)'", body)
        if models:
            variants[key] = models
    return variants


def parse_model_urls():
    text = open(os.path.join(REPO, "game/js/assets.js")).read()
    urls = dict(re.findall(r"""['"]?([A-Za-z0-9_.\-]+)['"]?\s*:\s*'([^']+\.glb)'""", text))
    return urls


def resolve_glb(rel):
    # MODEL_URLS paths are relative to game/ (the served root): '../roster/x' -> repo root
    return os.path.normpath(os.path.join(REPO, "game", rel))


def default_model_key(fid, fmodel, variants):
    lst = variants.get(fmodel) or variants.get(fid)
    if lst:
        return lst[0]
    return fmodel


def make_codec(work):
    # ES modules ignore NODE_PATH: run a copy of the codec beside a node_modules link.
    cdir = os.path.join(work, "codec")
    os.makedirs(cdir, exist_ok=True)
    npath = os.environ.get("NODE_PATH", os.path.expanduser("~/workspace/tools/gltf/node_modules"))
    link = os.path.join(cdir, "node_modules")
    if not os.path.isdir(link):
        os.symlink(npath.split(os.pathsep)[0], link)
    return shutil.copy(CODEC, os.path.join(cdir, "gltf_codec.mjs"))


def needs_decode(path):
    with open(path, "rb") as f:
        data = f.read(200000)
    return b"meshopt" in data or b"EXT_meshopt_compression" in data


def decode(codec, src, dst):
    r = subprocess.run(["node", codec, "decode", src, dst],
                       capture_output=True, text=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--outdir", default=os.path.join(REPO, "game/assets/portraits"))
    ap.add_argument("--manifest-only", action="store_true")
    a = ap.parse_args()

    poses = json.load(open(os.path.join(HERE, "poses.json")))["poses"]
    entries = parse_roster()
    variants = parse_attire_variants()
    urls = parse_model_urls()

    only = set(a.only.split(",")) if a.only else None
    os.makedirs(os.path.join(REPO, ".portrait-work"), exist_ok=True)
    work = tempfile.mkdtemp(prefix="wh-portraits-", dir=os.path.join(REPO, ".portrait-work"))
    codec = make_codec(work)
    manifest = []
    missing = []
    for fid, fmodel in entries:
        if fid not in poses:
            print(f"no pose defined for {fid}; skipping")
            continue
        if only and fid not in only:
            continue
        key = default_model_key(fid, fmodel, variants)
        rel = urls.get(key)
        if not rel:
            missing.append((fid, key)); continue
        glb = resolve_glb(rel)
        if not os.path.isfile(glb):
            missing.append((fid, glb)); continue
        dec = os.path.join(work, fid + ".glb")
        if needs_decode(glb):
            r = decode(codec, glb, dec)
            if r.returncode != 0:
                print(f"decode failed for {fid}: {r.stderr[-500:]}")
                missing.append((fid, glb)); continue
        else:
            shutil.copy(glb, dec)
        manifest.append({"id": fid, "model": dec, "preset": poses[fid]["preset"]})
    seen = {e["id"] for e in manifest}
    # bonus portraits (not in select roster but shipped as portraits)
    for fid in ("blanka",):
        if fid in seen:
            continue
        if fid not in poses or (only and fid not in only):
            continue
        key = {"blanka": "blanka", "baek-master-white": "baek-master-white",
               "waterfall": "waterfall"}[fid]
        rel = urls.get(key)
        if not rel:
            missing.append((fid, key)); continue
        glb = resolve_glb(rel)
        if not os.path.isfile(glb):
            missing.append((fid, glb)); continue
        dec = os.path.join(work, fid + ".glb")
        if needs_decode(glb):
            r = decode(codec, glb, dec)
            if r.returncode != 0:
                missing.append((fid, glb)); continue
        else:
            shutil.copy(glb, dec)
        manifest.append({"id": fid, "model": dec, "preset": poses[fid]["preset"]})

    man_path = os.path.join(work, "manifest.json")
    json.dump(manifest, open(man_path, "w"))
    print(f"manifest: {len(manifest)} fighters -> {man_path}")
    for fid, what in missing:
        print(f"MISSING model for {fid}: {what}")
    if a.manifest_only:
        print(work)
        return

    blender = os.environ.get("WH_BLENDER") or os.path.expanduser(
        "~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")
    cmd = ["xvfb-run", "-a", "env", "-u", "PYTHONPATH",
           "XDG_RUNTIME_DIR=/tmp", blender, "-b", "--factory-startup",
           "--python", os.path.join(HERE, "render_portraits.py"), "--",
           "--manifest", man_path, "--presets", os.path.join(HERE, "presets.json"),
           "--outdir", a.outdir]
    if a.only:
        cmd += ["--only", a.only]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-4000:])
    print(r.stderr[-2000:], file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
