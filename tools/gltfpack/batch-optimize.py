#!/usr/bin/env python3
"""batch-optimize.py — repeatable gltfpack batch for Western Heart.

Discovers game GLBs, validates each one, and optimizes it with the
pinned flag policy (see run_gltfpack_job.py). Outputs NEVER overwrite
inputs: optimized files land under --out-dir mirroring the input
tree, and a manifest JSON records every input/output size, flag set
and status, so a PR's before/after numbers are checkable.

  python3 tools/gltfpack/batch-optimize.py --root . --out-dir /tmp/wh-opt
  python3 tools/gltfpack/batch-optimize.py --root . --dry-run --manifest out.json
  python3 tools/gltfpack/batch-optimize.py --root . --tc --simplify-allow tools/gltfpack/simplify-allow.json

Discovery (default): game/assets/models/*.glb + game/assets/stages/**/*.glb.
  --include-roster adds roster/*/attires/*/model*.glb (opt-in: large).
Validation (always, even --dry-run): GLB header magic/version, JSON
chunk parse, buffer byteLength vs BIN chunk, every bufferView range
inside its buffer. A file that fails validation is recorded with
status "invalid" and SKIPPED. A file that passes validation but
fails inside gltfpack is recorded "failed" and also fails the batch
— that is the burger-fixed.glb class ("buffer too short" inside
gltfpack despite a consistent outer header, which this validator
correctly does NOT claim to catch): either way the batch surfaces
the file and ships nothing for it.
Flag selection per asset (measured, 2026-10-24):
  skinned (skins[] present) -> -cc -kn (bone names load-bearing)
  unskinned stage/prop       -> -cc, no -kn (-kn cost Jungle Outpost
                                +30%: 219,160 -> 284,540 bytes)
  -tc only with --tc, per asset, WITH measurement (it grew one
      textured model +7%; Basis transcoder wiring is a prerequisite
      before any -tc asset ships — see README).
  -si only for assets listed in --simplify-allow (JSON: {relpath: ratio}),
      never for a skinned fighter unless that asset is explicitly listed
      AND the allow entry sets "approved": true (owner eye-check).
Exit codes: 0 = all valid assets optimized (or dry-run clean);
1 = any asset invalid, any gltfpack run failed, or the binary is
missing in non-dry-run mode.
"""
import argparse
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMPONENT_SIZES = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TYPE_COUNTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4,
               "MAT3": 9, "MAT4": 16}


def validate_glb(path):
    """Return (ok, error, info). info: {skinned, json} on success."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        return False, f"unreadable: {e}", {}
    if len(data) < 20 or data[0:4] != b"glTF":
        return False, "bad magic (not a GLB)", {}
    _magic, _ver, total = struct.unpack("<III", data[:12])
    if total != len(data):
        return False, f"header length {total} != file size {len(data)}", {}
    jlen, jtype = struct.unpack("<II", data[12:20])
    if jtype != 0x4E4F534A or 20 + jlen > len(data):
        return False, "JSON chunk header out of range", {}
    try:
        doc = json.loads(data[20:20 + jlen])
    except ValueError as e:
        return False, f"JSON chunk unparseable: {e}", {}
    buffers = doc.get("buffers", [])
    if not buffers:
        return False, "no buffers", {}
    blen = buffers[0].get("byteLength", 0)
    boff = 20 + jlen
    if len(data) >= boff + 8:
        clen, ctype = struct.unpack("<II", data[boff:boff + 8])
        if ctype == 0x004E4942 and clen != blen:
            return False, f"BIN chunk {clen} != buffer byteLength {blen}", {}
    for i, bv in enumerate(doc.get("bufferViews", [])):
        # Meshopt views: byteLength is the DECODED size, not stored
        # bytes — the stored extent is the extension's byteLength.
        # (Caught by end-to-end test: a valid -cc output was flagged
        # as overrunning by 161,000 bytes before this carve-out.)
        ext = (bv.get("extensions") or {}).get("EXT_meshopt_compression")
        if ext is not None:
            end = ext.get("byteOffset", 0) + ext.get("byteLength", 0)
            if end > blen:
                return False, f"meshopt bufferView {i} overruns buffer by {end - blen}", {}
            continue
        end = bv.get("byteOffset", 0) + bv.get("byteLength", 0)
        if end > blen:
            return False, f"bufferView {i} overruns buffer by {end - blen}", {}
    return True, "", {"skinned": bool(doc.get("skins")), "json": doc}


def flags_for(skinned, tc=False, simplify=None):
    flags = ["-cc"]
    if skinned:
        flags.append("-kn")
    if tc:
        flags.append("-tc")
    if simplify is not None:
        flags += ["-si", str(simplify)]
    return flags


def discover(root, include_roster):
    found = []
    for base in ("game/assets/models", "game/assets/stages"):
        d = os.path.join(root, base)
        for dirpath, _dirs, files in os.walk(d):
            for f in sorted(files):
                if f.endswith(".glb"):
                    found.append(os.path.relpath(os.path.join(dirpath, f), root))
    if include_roster:
        d = os.path.join(root, "roster")
        for dirpath, _dirs, files in os.walk(d):
            if "attires" not in dirpath:
                continue
            for f in sorted(files):
                if f.startswith("model") and f.endswith(".glb"):
                    found.append(os.path.relpath(os.path.join(dirpath, f), root))
    return sorted(set(found))


def find_bin(explicit):
    if explicit and os.path.isfile(explicit):
        return explicit
    vendor = os.path.join(HERE, "vendor", "gltfpack")
    if os.path.isfile(vendor):
        return vendor
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, "gltfpack")
        if os.path.isfile(p):
            return p
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default="wh-opt-out")
    ap.add_argument("--manifest", default="")
    ap.add_argument("--bin", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tc", action="store_true")
    ap.add_argument("--include-roster", action="store_true")
    ap.add_argument("--simplify-allow", default="")
    ap.add_argument("--only", default="", help="substring filter on relpath")
    a = ap.parse_args(argv)

    allow = {}
    if a.simplify_allow:
        with open(a.simplify_allow) as fh:
            allow = json.load(fh)
    binary = None if a.dry_run else find_bin(a.bin)
    if not a.dry_run and not binary:
        print("gltfpack binary not found. Run: bash tools/gltfpack/fetch-gltfpack.sh",
              file=sys.stderr)
        return 1

    manifest = {"assets": [], "flags_policy": "cc always; kn skinned-only; tc opt-in; si allow-list only"}
    failed = False
    for rel in discover(a.root, a.include_roster):
        if a.only and a.only not in rel:
            continue
        src = os.path.join(a.root, rel)
        entry = {"input": rel, "inBytes": os.path.getsize(src)}
        ok, err, info = validate_glb(src)
        if not ok:
            entry.update({"status": "invalid", "error": err})
            manifest["assets"].append(entry)
            print(f"SKIP invalid {rel}: {err}")
            failed = True
            continue
        entry["skinned"] = info["skinned"]
        simplify = None
        if rel in allow:
            spec = allow[rel]
            ratio = spec["ratio"] if isinstance(spec, dict) else spec
            approved = True if not isinstance(spec, dict) else bool(spec.get("approved"))
            if info["skinned"] and not approved:
                entry.update({"status": "refused",
                              "error": "simplification of a skinned fighter needs approved=true"})
                manifest["assets"].append(entry)
                print(f"REFUSE simplify {rel}: skinned, not approved")
                failed = True
                continue
            simplify = ratio
        entry["flags"] = flags_for(info["skinned"], tc=a.tc, simplify=simplify)
        entry["tc"] = bool(a.tc)
        entry["simplified"] = simplify is not None
        out = os.path.join(a.out_dir, rel)
        entry["output"] = os.path.relpath(out, a.root) if not os.path.isabs(a.out_dir) else out
        if a.dry_run:
            entry["status"] = "planned"
            manifest["assets"].append(entry)
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        r = subprocess.run([binary, "-i", os.path.abspath(src), "-o", os.path.abspath(out)]
                           + entry["flags"], capture_output=True, text=True)
        if r.returncode != 0:
            entry.update({"status": "failed",
                          "error": (r.stderr or r.stdout or "")[-500:]})
            manifest["assets"].append(entry)
            print(f"FAIL {rel}: {entry['error']}")
            failed = True
            continue
        entry["outBytes"] = os.path.getsize(out)
        entry["ratio"] = round(entry["outBytes"] / entry["inBytes"], 4) if entry["inBytes"] else None
        entry["status"] = "ok"
        manifest["assets"].append(entry)
        print(f"OK {rel}: {entry['inBytes']} -> {entry['outBytes']} "
              f"({entry['flags'] and ' '.join(entry['flags'])})")
    if a.manifest:
        with open(a.manifest, "w") as fh:
            json.dump(manifest, fh, indent=2)
    ok_n = sum(1 for e in manifest["assets"] if e["status"] in ("ok", "planned"))
    print(f"{ok_n}/{len(manifest['assets'])} assets ok/planned; "
          f"{sum(1 for e in manifest['assets'] if e['status'] not in ('ok', 'planned'))} failed/skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
