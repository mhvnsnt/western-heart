# Megami texture pipeline — 1024px payload cap (SmutBase 6 fidelity, Megami lane).
# Same as-run note as build_payloads.py: game payloads capped from the v2
# manifest/dirs named below; the master's from the v1 pair. Only paths differ.
"""Produce 1024px-capped variants of the full-res payloads (the shipped
conversion's established in-game texture class). Channel-independent
resize (no alpha premultiplication). Payloads already <=1024 pass through
byte-identical. Output: work/graft-imgs-v2-1024/ + payload-manifest-1024.json
"""
import json, os, hashlib
import numpy as np
from PIL import Image

ROOT = os.path.expanduser("~/workspace/_smutbase6-megami-20261105")
OUTDIR = os.path.join(ROOT, "work/graft-imgs-v2-1024")
os.makedirs(OUTDIR, exist_ok=True)
CAP = 1024
man = json.load(open(os.path.join(ROOT, "scratch/v2-payload-manifest.json")))

def resize_rgba(im, maxdim):
    w, h = im.size
    s = maxdim / max(w, h)
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    chans = []
    for ch in range(4):
        c = im.getchannel(ch).resize((nw, nh), Image.LANCZOS)
        chans.append(c)
    out = Image.merge("RGBA", chans)
    return out

newman = []
for e in man:
    out = os.path.join(OUTDIR, f"{e['index']}.bin")
    im = Image.open(e["file"])
    w, h = im.size
    if max(w, h) <= CAP:
        data = open(e["file"], "rb").read()
        open(out, "wb").write(data)
        rule = e["rule"] + "|cap:passthrough"
    else:
        im = im.convert("RGBA")
        im = resize_rgba(im, CAP)
        if e["mime"] == "image/jpeg":
            im.convert("RGB").save(out, format="JPEG", quality=90)
        elif e["mime"] == "image/webp":
            im.save(out, format="WEBP", quality=95, method=6)
        else:
            im.save(out, format="PNG")
        data = open(out, "rb").read()
        rule = e["rule"] + f"|cap:1024({w}x{h})"
    newman.append({"index": e["index"], "name": e["name"], "mime": e["mime"],
                   "rule": rule, "bytes": len(data),
                   "sha256": hashlib.sha256(data).hexdigest(), "file": out})
    print(e["index"], e["name"], f"{w}x{h}", rule, len(data))
json.dump(newman, open(os.path.join(ROOT, "scratch/v2-payload-manifest-1024.json"), "w"), indent=1)
print("CAP_DONE", len(newman))
