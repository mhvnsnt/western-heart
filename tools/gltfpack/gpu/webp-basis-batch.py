#!/usr/bin/env python3
"""webp-basis-batch.py — WebP / Basis texture batch (Lane 5 GPU job).

Two conversions, one rule each, both measured per asset:
  WebP (PIL): convert discovered PNGs to WebP at --quality.
      SHIP ONLY IF SMALLER. Measured 2026-10-24: tree-of-life pano
      (580x183 palette PNG, 39,344 bytes) GREW to 45,028 bytes as
      WebP q90 (+14%). A conversion that grows is recorded
      "grew" and its output is DELETED, never shipped.
  Basis/KTX2 (gltfpack -tc): run on COPIES of GLBs that carry
      textures, per asset, WITH measurement. SHIP ONLY IF SMALLER
      (same rule — one textured model grew +7% under -tc). A -tc
      output additionally needs the three.js Basis transcoder (WASM)
      wired before it ships; this script measures, it does not wire
      the transcoder and does not claim otherwise.

WebP conversion is CPU-bound (PIL) and is labelled CPU-bound in the
manifest — it runs INSIDE the GPU job session (same machine, same
queue, same manifest) so the texture batch is one measured job, not
a separate CPU-only lane. gltfpack -tc is likewise run on the GPU
machine as part of this batch.

Usage:
  python3 webp-basis-batch.py --root . --out-dir wh-tex-out --gltfpack-bin <bin>
  python3 webp-basis-batch.py --root . --out-dir wh-tex-out --webp-only
  python3 webp-basis-batch.py --root . --out-dir wh-tex-out --tc-only --only arena_raw

Discovery: PNGs under game/assets/stages + game/assets/portraits;
GLBs under game/assets/models + game/assets/stages (same discovery
as batch-optimize.py, minus roster unless --include-roster).
Manifest JSON records every input, output-or-grew status, sizes,
and wall seconds. Exit 0 = batch complete (grew entries are not
failures — they are the measurement doing its job); 1 = a
conversion crashed.
"""
import argparse
import json
import os
import subprocess
import sys
import time


def _walk(root, base, exts):
    found = []
    d = os.path.join(root, base)
    for dirpath, _dirs, files in os.walk(d):
        for f in sorted(files):
            if any(f.lower().endswith(e) for e in exts):
                found.append(os.path.relpath(os.path.join(dirpath, f), root))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default="wh-tex-out")
    ap.add_argument("--quality", type=int, default=90)
    ap.add_argument("--webp-only", action="store_true")
    ap.add_argument("--tc-only", action="store_true")
    ap.add_argument("--include-roster", action="store_true")
    ap.add_argument("--gltfpack-bin", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--manifest", default="")
    a = ap.parse_args(argv)

    manifest = {"webp_quality": a.quality, "assets": []}
    crashed = False

    if not a.tc_only:
        try:
            from PIL import Image
        except ImportError:
            print("Pillow not installed: pip install pillow", file=sys.stderr)
            return 1
        pngs = []
        for base in ("game/assets/stages", "game/assets/portraits"):
            pngs += _walk(a.root, base, (".png",))
        for rel in sorted(set(pngs)):
            if a.only and a.only not in rel:
                continue
            src = os.path.join(a.root, rel)
            out = os.path.join(a.out_dir, rel.rsplit(".", 1)[0] + ".webp")
            entry = {"input": rel, "kind": "webp (CPU-bound, in GPU job)",
                     "inBytes": os.path.getsize(src)}
            t0 = time.monotonic()
            try:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with Image.open(src) as im:
                    im.convert("RGBA" if im.mode in ("P", "PA") else im.mode).save(
                        out, "WEBP", quality=a.quality)
                entry["outBytes"] = os.path.getsize(out)
                entry["wall_s"] = round(time.monotonic() - t0, 3)
                if entry["outBytes"] >= entry["inBytes"]:
                    entry["status"] = "grew"
                    os.unlink(out)
                    entry["output"] = None
                else:
                    entry["status"] = "ok"
                    entry["output"] = os.path.relpath(out, a.root)
            except Exception as e:  # noqa: BLE001 — per-asset crash must not kill the batch
                entry.update({"status": "crashed", "error": str(e)[:300]})
                crashed = True
            manifest["assets"].append(entry)
            print(f"WEBP {rel}: {entry['status']} "
                  f"{entry['inBytes']} -> {entry.get('outBytes')}")

    if not a.webp_only:
        binary = a.gltfpack_bin
        if not binary:
            for cand in (os.path.join(os.path.dirname(__file__), "..", "vendor", "gltfpack"),
                         "gltfpack"):
                if os.path.isfile(cand):
                    binary = cand
                    break
        if not binary or not os.path.isfile(binary):
            print("gltfpack binary not found: run tools/gltfpack/fetch-gltfpack.sh "
                  "or pass --gltfpack-bin", file=sys.stderr)
            return 1
        glbs = []
        for base in ("game/assets/models", "game/assets/stages"):
            glbs += _walk(a.root, base, (".glb",))
        if a.include_roster:
            glbs += _walk(a.root, "roster", (".glb",))
        for rel in sorted(set(glbs)):
            if a.only and a.only not in rel:
                continue
            src = os.path.join(a.root, rel)
            out = os.path.join(a.out_dir, rel.rsplit(".", 1)[0] + "-tc.glb")
            entry = {"input": rel, "kind": "gltfpack -tc (measured, transcoder required to ship)",
                     "inBytes": os.path.getsize(src)}
            t0 = time.monotonic()
            os.makedirs(os.path.dirname(out), exist_ok=True)
            r = subprocess.run([binary, "-i", os.path.abspath(src), "-o", os.path.abspath(out),
                                "-cc", "-tc"], capture_output=True, text=True)
            entry["wall_s"] = round(time.monotonic() - t0, 3)
            if r.returncode != 0:
                entry.update({"status": "failed",
                              "error": (r.stderr or r.stdout or "")[-300:]})
                crashed = True
            else:
                entry["outBytes"] = os.path.getsize(out)
                if entry["outBytes"] >= entry["inBytes"]:
                    entry["status"] = "grew"
                    os.unlink(out)
                    entry["output"] = None
                else:
                    entry["status"] = "ok"
                    entry["output"] = os.path.relpath(out, a.root)
            manifest["assets"].append(entry)
            print(f"TC {rel}: {entry['status']} "
                  f"{entry['inBytes']} -> {entry.get('outBytes')}")

    if a.manifest:
        with open(a.manifest, "w") as fh:
            json.dump(manifest, fh, indent=2)
    ok_n = sum(1 for e in manifest["assets"] if e["status"] == "ok")
    grew_n = sum(1 for e in manifest["assets"] if e["status"] == "grew")
    print(f"{ok_n} shipped-candidates, {grew_n} grew-and-discarded, "
          f"{len(manifest['assets'])} total")
    return 1 if crashed else 0


if __name__ == "__main__":
    raise SystemExit(main())
