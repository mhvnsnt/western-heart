#!/usr/bin/env python3
"""tools/deploy/cook_assets.py: deploy-time "cook" of GLBs for the web build.

docs/tech/ASSET-PIPELINE-2026.md has the why and the sources. In short,
studios keep source assets lossless in the repo and ship a cooked,
GPU-friendly copy. Here that means:

  original  game/assets/models/x.glb   (unchanged, still deployed)
  cooked    game/assets/models/x.web.glb  meshopt geometry + KTX2/Basis textures
  index     cooked-manifest.json        {"entries": {"<orig path>": {"cooked": ..., ...}}}

game/js/asset-codecs.js swaps to the cooked file when the manifest lists it.

Safety: a cooked file is only used if it keeps every node name, every
animation and every skin's joint count from the original, and is at least
10% smaller. Otherwise the original is used. Results are cached by the
original blob's git SHA in ~/.cache/wh-cook, so a re-deploy only cooks new
or changed models.

Tool: gltfpack (zeux/meshoptimizer, MIT). Flags (see doc §3):
  -cc   EXT_meshopt_compression (higher compression mode)
  -tc   textures -> KTX2 with Basis Universal supercompression (ETC1S for color)
  -tu normal  UASTC for normal maps (ETC1S block artifacts are visible in lighting)
  -noq  no attribute quantization: float vertex data, identical scene graph
  -kn -km -ke -kv  keep named nodes, materials, extras, and vertex attributes
  -ac   keep constant animation tracks
  -af 0 do not resample animations (Tekken-rate keys preserved)
"""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

FLAGS = ["-cc", "-tc", "-tu", "normal", "-noq", "-kn", "-km", "-ke", "-kv", "-ac", "-af", "0"]
# cache key includes the flags, so changing them re-cooks everything
CACHE = os.path.join(os.path.expanduser("~/.cache/wh-cook"), hashlib.sha1(" ".join(FLAGS).encode()).hexdigest()[:10])


def gltfpack_bin():
    for c in (os.environ.get("GLTFPACK"), shutil.which("gltfpack"),
              os.path.join(os.path.dirname(__file__), "..", "procgen", "gltf-delivery", "bin", "gltfpack")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    sys.exit("gltfpack not found: download gltfpack-ubuntu.zip from github.com/zeux/meshoptimizer releases "
             "(or set GLTFPACK=/path)")


def glb_json(data):
    if data[:4] != b"glTF":
        raise ValueError("not a GLB")
    n = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + n])


def repair(data):
    """Some exports declare buffers[0].byteLength larger than the BIN chunk
    (three.js tolerates it, gltfpack refuses). Clamp it; nothing else changes."""
    jl = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + jl])
    o = 20 + jl
    if o + 8 > len(data) or not j.get("buffers"):
        return data
    bl = struct.unpack("<I", data[o:o + 4])[0]
    b0 = j["buffers"][0]
    if "uri" in b0 or b0.get("byteLength", 0) <= bl:
        return data
    b0["byteLength"] = bl
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + data[o:]
    return b"glTF" + struct.pack("<II", 2, 12 + len(body)) + body


def signature(j):
    return ({n.get("name") for n in j.get("nodes", []) if n.get("name")},
            len(j.get("animations", [])),
            [len(s.get("joints", [])) for s in j.get("skins", [])])


def git_blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def cook_one(path, data, blob):
    """-> dict(meta) and cooked bytes (or None)."""
    os.makedirs(CACHE, exist_ok=True)
    meta_p = os.path.join(CACHE, blob + ".json")
    out_p = os.path.join(CACHE, blob + ".web.glb")
    if os.path.exists(meta_p):
        meta = json.load(open(meta_p))
        if not meta.get("ok") or os.path.exists(out_p):
            return meta, (open(out_p, "rb").read() if meta.get("ok") else None)
    meta = {"in_bytes": len(data), "ok": False}
    try:
        src = repair(data)
        sig_in = signature(glb_json(src))
        with tempfile.TemporaryDirectory() as td:
            i, o = os.path.join(td, "in.glb"), os.path.join(td, "out.glb")
            open(i, "wb").write(src)
            r = subprocess.run([gltfpack_bin(), "-i", i, "-o", o, *FLAGS], capture_output=True, text=True, timeout=900)
            if r.returncode or not os.path.exists(o):
                meta["reason"] = "gltfpack: " + (r.stderr or r.stdout).strip()[-300:]
            else:
                out = open(o, "rb").read()
                sig_out = signature(glb_json(out))
                meta["out_bytes"] = len(out)
                if not sig_in[0] <= sig_out[0]:
                    meta["reason"] = f"lost {len(sig_in[0] - sig_out[0])} node names"
                elif sig_in[1:] != sig_out[1:]:
                    meta["reason"] = f"animation/skin mismatch {sig_in[1:]} -> {sig_out[1:]}"
                elif len(out) > 0.9 * len(data):
                    meta["reason"] = "under 10% smaller"
                else:
                    meta["ok"] = True
                    open(out_p, "wb").write(out)
    except Exception as e:  # never break a deploy over one model
        meta["reason"] = f"{type(e).__name__}: {e}"[:300]
    json.dump(meta, open(meta_p, "w"))
    return meta, (open(out_p, "rb").read() if meta["ok"] else None)


def cooked_name(path):
    return path[:-4] + ".web.glb"


def cook_all(items, read, jobs=4):
    """items: [(path, blob_sha)]; read(path, blob) -> bytes.
    Returns (manifest_entries, {cooked_path: bytes})."""
    entries, outputs = {}, {}

    def work(it):
        path, blob = it
        data = read(path, blob)
        return path, cook_one(path, data, blob)

    with cf.ThreadPoolExecutor(jobs) as ex:
        for n, (path, (meta, out)) in enumerate(ex.map(work, items), 1):
            if out is not None:
                cp = cooked_name(path)
                entries[path] = {"cooked": cp, "bytes": meta["in_bytes"], "cooked_bytes": len(out)}
                outputs[cp] = out
            else:
                entries[path] = {"cooked": None, "bytes": meta["in_bytes"], "reason": meta.get("reason")}
            print(f"  cook {n}/{len(items)} {path}: "
                  + (f"{meta['in_bytes']/1e6:.1f} -> {len(out)/1e6:.1f} MB" if out else f"kept original ({meta.get('reason')})"),
                  flush=True)
    return entries, outputs


def manifest(entries, ref_sha):
    tot = sum(e["bytes"] for e in entries.values())
    cooked = sum(e.get("cooked_bytes", e["bytes"]) for e in entries.values())
    return {"format": "wh-cooked/1", "tool": "tools/deploy/cook_assets.py", "commit": ref_sha,
            "gltfpack_flags": FLAGS, "models": len(entries),
            "cooked_models": sum(1 for e in entries.values() if e["cooked"]),
            "bytes_original": tot, "bytes_served": cooked, "entries": entries}


if __name__ == "__main__":
    # Ad-hoc: cook_assets.py IN.glb [IN2.glb ...] -> prints result, writes *.web.glb beside.
    for p in sys.argv[1:]:
        d = open(p, "rb").read()
        meta, out = cook_one(p, d, git_blob_sha(d))
        if out:
            open(cooked_name(p), "wb").write(out)
        print(p, meta)
