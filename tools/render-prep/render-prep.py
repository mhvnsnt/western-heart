#!/usr/bin/env python3
"""
================================================================================
 render-prep — THE MANDATORY PRE-STEP FOR EVERY BLENDER RENDER OF A GLB.
================================================================================
Owner law context (2026-10-19 incidents):
  * Blender 4.0.2 on this VM OOM-kills rendering raw Tripo GLBs
    (20 MB+, ~1M verts, 4096px textures). Cain (58 MB decoded),
    Doc Frank (1.38M verts), Star (1M verts) all died.
  * A shipped Mariposa texture JPEG was truncated/corrupt, rendered
    white, and nobody knew until a human looked at the render.
  * GLBs with garbage vertex bounds (+/-3.4e38 float-max junk) shipped
    in a PR and were only caught downstream.

render-prep fixes all three BEFORE Blender ever sees the file:

  validate  — deep-check a GLB and fail LOUDLY on:
              * broken container / JSON / buffer structure
                (glTF-Validator-equivalent structural checks, pure Python)
              * ANY embedded texture that does not fully decode
                (truncated JPEG/PNG is caught by name, before render)
              * NaN / Inf / float-max-garbage vertex positions
                (declared accessor min/max AND, when the data is not
                meshopt/draco compressed, the actual vertex bytes)
              * meshopt/draco compression Blender cannot import raw

  prep      — produce a RENDER-SAFE COPY (original is never touched):
              1. validate input
              2. decode meshopt/draco via @gltf-transform/cli (if present)
              3. deep-validate the decoded geometry bytes
              4. decimate to a vertex budget via gltfpack (meshoptimizer)
                 (fallback: @gltf-transform/cli simplify)
              5. downscale oversized textures in pure Python (Pillow)
              6. deep-validate the final output; refuse to ship a bad copy

Usage:
  python3 render-prep.py validate model.glb [--json report.json]
  python3 render-prep.py prep model.glb -o model.render.glb \
      [--max-verts 250000] [--max-texture 2048] [--json report.json]
  python3 render-prep.py check-env

Exit codes: 0 = OK, 2 = validation failed, 3 = prep/tooling failed.

Deps: Python 3.10+, numpy, Pillow. Optional external tools (auto-detected):
  gltfpack (npm i -g gltfpack) and/or @gltf-transform/cli
  (npm i -g @gltf-transform/cli). Blender is NEVER invoked by this tool.
================================================================================
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile

import numpy as np

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

GLB_MAGIC = b"glTF"
CHUNK_JSON = b"JSON"
CHUNK_BIN = b"BIN\x00"

COMPONENT_DTYPES = {
    5120: np.int8, 5121: np.uint8, 5122: np.int16,
    5123: np.uint16, 5125: np.uint32, 5126: np.float32,
}
TYPE_COMPONENTS = {
    "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
    "MAT2": 4, "MAT3": 9, "MAT4": 16,
}
# |coordinate| above this is not a character model, it's garbage.
DEFAULT_MAX_COORD = 1.0e5
# float32 max is ~3.4028235e38; anything near it is the classic
# uninitialized-bounds garbage signature we shipped once.
GARBAGE_ABS = 3.0e38

JPEG_MAGIC = b"\xff\xd8"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
KTX2_MAGIC = b"\xabKTX 20\xbb\r\n\x1a\n"


class PrepError(Exception):
    """Fatal prep/tooling problem (exit 3)."""


def _is_meshopt_bv(bv: dict) -> bool:
    return "extensions" in bv and "EXT_meshopt_compression" in bv["extensions"]


# --------------------------------------------------------------------------
# GLB container
# --------------------------------------------------------------------------

class GLB:
    """Minimal GLB reader/writer (stdlib only)."""

    def __init__(self, data: bytes):
        self.data = data
        self.json: dict = {}
        self.bin: bytes = b""
        self.issues: list[str] = []  # container-level problems
        self._parse()

    def _parse(self):
        d = self.data
        if len(d) < 12:
            self.issues.append("file shorter than GLB header (12 bytes)")
            return
        if d[0:4] != GLB_MAGIC:
            self.issues.append("bad magic: not a GLB file")
            return
        version, length = struct.unpack_from("<II", d, 4)
        if version != 2:
            self.issues.append(f"GLB version {version}, expected 2")
        if length != len(d):
            self.issues.append(
                f"header length {length} != actual file size {len(d)} "
                "(truncated or padded file)")
        off = 12
        chunk_no = 0
        while off + 8 <= len(d):
            clen, ctype = struct.unpack_from("<I4s", d, off)
            body = d[off + 8: off + 8 + clen]
            if len(body) < clen:
                self.issues.append(f"chunk {chunk_no} truncated: "
                                   f"declared {clen} bytes, {len(body)} present")
                break
            if chunk_no == 0 and ctype != CHUNK_JSON:
                self.issues.append("first chunk is not JSON")
            if ctype == CHUNK_JSON:
                try:
                    self.json = json.loads(body.decode("utf-8"))
                except Exception as e:  # noqa: BLE001
                    self.issues.append(f"JSON chunk does not parse: {e}")
            elif ctype == CHUNK_BIN:
                self.bin = body
            off += 8 + clen
            chunk_no += 1
        if not self.json:
            self.issues.append("no parseable JSON chunk")

    # -- buffer helpers ----------------------------------------------------
    def buffer_view_bytes(self, bv_index: int) -> bytes | None:
        bv = self.json.get("bufferViews", [])[bv_index]
        start = bv.get("byteOffset", 0)
        return self.bin[start: start + bv["byteLength"]]

    def accessor_array(self, acc_index: int) -> np.ndarray | None:
        """Return accessor data as ndarray (count, ncomp), or None if the
        underlying bufferView is codec-compressed (meshopt)."""
        acc = self.json["accessors"][acc_index]
        bv_index = acc.get("bufferView")
        if bv_index is None:
            return None
        bv = self.json["bufferViews"][bv_index]
        if _is_meshopt_bv(bv):
            return None
        dtype = COMPONENT_DTYPES.get(acc["componentType"])
        ncomp = TYPE_COMPONENTS.get(acc["type"])
        if dtype is None or ncomp is None:
            return None
        count = acc["count"]
        elem = np.dtype(dtype).itemsize * ncomp
        stride = bv.get("byteStride", elem)
        start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        raw = np.ndarray(
            shape=(count, ncomp), dtype=dtype, buffer=self.bin,
            offset=start, strides=(stride, np.dtype(dtype).itemsize))
        return np.array(raw)  # copy out of the bytes buffer

    def to_bytes(self) -> bytes:
        js = json.dumps(self.json, separators=(",", ":")).encode("utf-8")
        js += b" " * ((4 - len(js) % 4) % 4)
        binp = self.bin + b"\x00" * ((4 - len(self.bin) % 4) % 4)
        total = 12 + 8 + len(js) + 8 + len(binp)
        out = [GLB_MAGIC, struct.pack("<II", 2, total),
               struct.pack("<I4s", len(js), CHUNK_JSON), js,
               struct.pack("<I4s", len(binp), CHUNK_BIN), binp]
        return b"".join(out)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

class Report:
    def __init__(self, path: str):
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict = {}
        self.textures: list[dict] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {"path": self.path, "ok": self.ok,
                "errors": self.errors, "warnings": self.warnings,
                "stats": self.stats, "textures": self.textures}


def _check_structure(g: GLB, rep: Report):
    """glTF-Validator-equivalent structural checks (the subset that has
    actually bitten us, plus reference/bounds integrity)."""
    js = g.json
    for issue in g.issues:
        rep.errors.append(f"container: {issue}")
    if not js:
        return
    buffers = js.get("buffers", [])
    bvs = js.get("bufferViews", [])
    accs = js.get("accessors", [])
    if buffers:
        declared = buffers[0].get("byteLength", 0)
        if declared > len(g.bin):
            rep.errors.append(
                f"buffers[0].byteLength {declared} > BIN chunk {len(g.bin)} "
                "(file truncated?)")
    for i, bv in enumerate(bvs):
        # meshopt bufferViews declare the DECOMPRESSED layout; their
        # byteLength legitimately exceeds the compressed buffer size.
        if _is_meshopt_bv(bv):
            continue
        end = bv.get("byteOffset", 0) + bv.get("byteLength", 0)
        limit = buffers[0].get("byteLength", len(g.bin)) if buffers else len(g.bin)
        if end > limit:
            rep.errors.append(f"bufferView[{i}] overruns buffer: end {end} > {limit}")
    for i, acc in enumerate(accs):
        if "bufferView" not in acc:
            continue
        bv = bvs[acc["bufferView"]]
        if _is_meshopt_bv(bv):
            continue  # compressed: verified against decoded bytes during prep
        dtype = COMPONENT_DTYPES.get(acc["componentType"])
        ncomp = TYPE_COMPONENTS.get(acc["type"])
        if dtype is None or ncomp is None:
            rep.errors.append(f"accessor[{i}]: unknown componentType/type")
            continue
        elem = np.dtype(dtype).itemsize * ncomp
        stride = bv.get("byteStride", elem)
        need = acc.get("byteOffset", 0) + stride * (acc["count"] - 1) + elem \
            if acc["count"] else 0
        if need > bv["byteLength"]:
            rep.errors.append(
                f"accessor[{i}] overruns bufferView[{acc['bufferView']}]: "
                f"needs {need} > {bv['byteLength']}")
    # reference integrity for the arrays renders actually traverse
    n_meshes = len(js.get("meshes", []))
    for ni, node in enumerate(js.get("nodes", [])):
        if "mesh" in node and not (0 <= node["mesh"] < n_meshes):
            rep.errors.append(f"node[{ni}].mesh index {node['mesh']} out of range")
    for ii, img in enumerate(js.get("images", [])):
        if "bufferView" in img and not (0 <= img["bufferView"] < len(bvs)):
            rep.errors.append(f"image[{ii}].bufferView out of range")
    for ti, tex in enumerate(js.get("textures", [])):
        if "source" in tex and not (0 <= tex["source"] < len(js.get("images", []))):
            rep.errors.append(f"texture[{ti}].source out of range")
    rep.stats["meshes"] = n_meshes
    rep.stats["textures_declared"] = len(js.get("textures", []))


def _check_textures(g: GLB, rep: Report):
    """Every embedded texture must FULLY decode. This is the Mariposa gate:
    a truncated JPEG renders white in Blender and must die here, by name."""
    try:
        from PIL import Image
    except ImportError:
        rep.errors.append("Pillow not installed — cannot verify textures "
                            "(pip install pillow). Refusing to pass blind.")
        return
    total_bytes = 0
    max_dim = 0
    for i, img in enumerate(g.json.get("images", [])):
        entry = {"index": i, "name": img.get("name", f"image[{i}]"),
                 "mime": img.get("mimeType", "?")}
        rep.textures.append(entry)
        if "bufferView" not in img:
            entry["status"] = "external-uri (not verified)"
            rep.warnings.append(f"image[{i}] '{entry['name']}': external URI, "
                                "embedded-texture check skipped")
            continue
        raw = g.buffer_view_bytes(img["bufferView"])
        entry["bytes"] = len(raw)
        total_bytes += len(raw)
        mime = img.get("mimeType", "")
        if mime == "image/jpeg" and not raw.startswith(JPEG_MAGIC):
            rep.errors.append(f"image[{i}] '{entry['name']}': declared JPEG "
                              "but missing FFD8 magic — corrupt")
            entry["status"] = "FAIL bad-magic"
            continue
        if mime == "image/png" and not raw.startswith(PNG_MAGIC):
            rep.errors.append(f"image[{i}] '{entry['name']}': declared PNG "
                              "but missing PNG magic — corrupt")
            entry["status"] = "FAIL bad-magic"
            continue
        if mime == "image/ktx2" or raw.startswith(KTX2_MAGIC):
            entry["status"] = "ktx2 (container noted; not pixel-decoded)"
            rep.warnings.append(f"image[{i}] '{entry['name']}': KTX2 texture; "
                                "Blender import of KTX2 is unreliable")
            continue
        # structural tails (cheap truncation tripwires)
        if mime == "image/jpeg" and b"\xff\xd9" not in raw[-4096:]:
            rep.errors.append(f"image[{i}] '{entry['name']}': JPEG missing EOI "
                              "marker (FFD9) — TRUNCATED texture")
            entry["status"] = "FAIL truncated-jpeg"
            continue
        if mime == "image/png" and b"IEND" not in raw[-32:]:
            rep.errors.append(f"image[{i}] '{entry['name']}': PNG missing IEND "
                              "chunk — TRUNCATED texture")
            entry["status"] = "FAIL truncated-png"
            continue
        # the real gate: full decode of every scanline/chunk
        try:
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                entry["size"] = list(im.size)
                max_dim = max(max_dim, im.size[0], im.size[1])
                entry["status"] = "ok"
        except Exception as e:  # noqa: BLE001 — any decode failure is THE failure
            rep.errors.append(
                f"image[{i}] '{entry['name']}' ({mime}, {len(raw)} bytes): "
                f"TEXTURE DOES NOT DECODE: {type(e).__name__}: {e}")
            entry["status"] = f"FAIL decode: {e}"
    rep.stats["texture_bytes"] = total_bytes
    rep.stats["texture_max_dim"] = max_dim


def _check_positions(g: GLB, rep: Report, max_coord: float, deep: bool):
    """Vertex sanity: declared min/max on every POSITION accessor, plus a
    full byte-level NaN/garbage scan when data is uncompressed (deep)."""
    js = g.json
    total_verts = 0
    total_tris = 0
    scanned = 0
    for mi, mesh in enumerate(js.get("meshes", [])):
        for pi, prim in enumerate(mesh.get("primitives", [])):
            attrs = prim.get("attributes", {})
            if "POSITION" not in attrs:
                continue
            ai = attrs["POSITION"]
            acc = js["accessors"][ai]
            total_verts += acc["count"]
            if "indices" in prim:
                total_tris += js["accessors"][prim["indices"]]["count"] // 3
            else:
                total_tris += acc["count"] // 3
            where = f"mesh[{mi}].primitives[{pi}] POSITION accessor[{ai}]"
            mn, mx = acc.get("min"), acc.get("max")
            if mn is None or mx is None:
                rep.errors.append(f"{where}: missing min/max "
                                  "(glTF requires them for POSITION)")
                continue
            flat = list(mn) + list(mx)
            if any(not math.isfinite(v) for v in flat):
                rep.errors.append(f"{where}: non-finite min/max {mn}..{mx}")
                continue
            worst = max(abs(v) for v in flat)
            if worst >= GARBAGE_ABS:
                rep.errors.append(
                    f"{where}: GARBAGE vertex bounds min={mn} max={mx} "
                    "(float-max junk — the PR #317 failure signature)")
                continue
            if worst > max_coord:
                rep.errors.append(
                    f"{where}: vertex bounds reach {worst:.3g} > "
                    f"--max-coord {max_coord:.3g} — implausible for a model")
                continue
            if deep:
                arr = g.accessor_array(ai)
                if arr is None:
                    continue  # compressed; caller re-checks after decode
                scanned += acc["count"]
                with np.errstate(invalid="ignore"):
                    f = arr.astype(np.float64)
                n_nan = int(np.isnan(f).sum())
                n_inf = int(np.isinf(f).sum())
                if n_nan or n_inf:
                    rep.errors.append(
                        f"{where}: {n_nan} NaN and {n_inf} Inf coordinate "
                        "values in the actual vertex bytes")
                    continue
                peak = float(np.abs(f).max()) if f.size else 0.0
                if peak >= GARBAGE_ABS:
                    rep.errors.append(
                        f"{where}: actual vertex bytes contain garbage "
                        f"(|v| up to {peak:.3g}) despite sane declared bounds")
                    continue
                real_mn = f.min(axis=0)
                real_mx = f.max(axis=0)
                tol = 1e-3 * max(1.0, float(np.abs(real_mx).max()))
                if (np.abs(real_mn - np.array(mn[:3])) > tol).any() or \
                   (np.abs(real_mx - np.array(mx[:3])) > tol).any():
                    rep.warnings.append(
                        f"{where}: declared min/max {mn}..{mx} disagree with "
                        f"actual data {real_mn.tolist()}..{real_mx.tolist()}")
    rep.stats["vertices"] = total_verts
    rep.stats["triangles"] = total_tris
    rep.stats["positions_scanned"] = scanned


def _check_compression(g: GLB, rep: Report):
    used = set(g.json.get("extensionsUsed", []))
    rep.stats["extensions_used"] = sorted(used)
    blockers = []
    if "EXT_meshopt_compression" in used:
        blockers.append("EXT_meshopt_compression")
    if "KHR_draco_mesh_compression" in used:
        blockers.append("KHR_draco_mesh_compression")
    rep.stats["blender_blockers"] = blockers
    if blockers:
        rep.warnings.append(
            "geometry is codec-compressed (" + ", ".join(blockers) + ") — "
            "Blender cannot import this raw; render-prep prep will decode it, "
            "a bare Blender import will fail or OOM-thrash")


def validate_bytes(data: bytes, path: str, max_coord: float = DEFAULT_MAX_COORD,
                   deep: bool = True) -> Report:
    rep = Report(path)
    rep.stats["file_bytes"] = len(data)
    g = GLB(data)
    if g.json:
        _check_structure(g, rep)
        _check_compression(g, rep)
        _check_textures(g, rep)
        _check_positions(g, rep, max_coord, deep)
    else:
        for issue in g.issues:
            rep.errors.append(f"container: {issue}")
    return rep


def validate_file(path: str, max_coord: float = DEFAULT_MAX_COORD,
                  deep: bool = True) -> Report:
    with open(path, "rb") as f:
        return validate_bytes(f.read(), path, max_coord, deep)


# --------------------------------------------------------------------------
# External tool discovery
# --------------------------------------------------------------------------

def find_tool(name: str) -> str | None:
    p = shutil.which(name)
    if p:
        return p
    # user-global npm prefix + workspace-local node installs (this VM keeps
    # @gltf-transform/cli under ~/workspace/node_modules/.bin)
    for cand in (os.path.expanduser("~/.npm-global/bin/" + name),
                 os.path.expanduser("~/workspace/node_modules/.bin/" + name),
                 os.path.expanduser("~/.local/bin/" + name)):
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def run(cmd: list[str], what: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if proc.returncode != 0:
        raise PrepError(f"{what} failed (exit {proc.returncode}):\n"
                        f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return proc


# --------------------------------------------------------------------------
# Prep steps
# --------------------------------------------------------------------------

def decode_compressed(src: str, dst: str):
    """Meshopt/Draco -> plain GLB via @gltf-transform/cli copy (its reader
    decodes codecs; writing without re-applying them yields plain data)."""
    gt = find_tool("gltf-transform")
    if not gt:
        raise PrepError(
            "input is codec-compressed and @gltf-transform/cli was not found. "
            "Install: npm i -g @gltf-transform/cli  (or npm i in ~/workspace).")
    run([gt, "copy", src, dst], "gltf-transform copy (codec decode)")


def decimate(src: str, dst: str, ratio: float):
    """Simplify via gltfpack (-si is an index-count ratio); fall back to
    gltf-transform simplify. Returns the method used."""
    gp = find_tool("gltfpack")
    if gp:
        run([gp, "-i", src, "-o", dst, "-si", f"{ratio:.4f}"],
            "gltfpack simplify")
        return "gltfpack -si"
    gt = find_tool("gltf-transform")
    if gt:
        run([gt, "simplify", src, dst, "--ratio", f"{ratio:.4f}",
             "--error", "0.01"], "gltf-transform simplify")
        return "gltf-transform simplify"
    raise PrepError(
        "no decimator found. Install one: npm i -g gltfpack  "
        "(preferred, meshoptimizer) or npm i -g @gltf-transform/cli")


def downscale_textures(glb_path: str, max_dim: int) -> int:
    """Rewrite the GLB at glb_path in place (it's OUR copy): any embedded
    JPEG/PNG larger than max_dim is resized (aspect kept) and re-encoded.
    Rebuilds the BIN chunk bufferView-by-bufferView. Returns resize count."""
    from PIL import Image
    with open(glb_path, "rb") as f:
        g = GLB(f.read())
    js = g.json
    bvs = js.get("bufferViews", [])
    replacements: dict[int, bytes] = {}
    n_resized = 0
    for img in js.get("images", []):
        if "bufferView" not in img:
            continue
        mime = img.get("mimeType", "")
        if mime not in ("image/jpeg", "image/png"):
            continue
        raw = g.buffer_view_bytes(img["bufferView"])
        with Image.open(io.BytesIO(raw)) as im:
            if max(im.size) <= max_dim:
                continue
            scale = max_dim / max(im.size)
            new_size = (max(1, round(im.size[0] * scale)),
                        max(1, round(im.size[1] * scale)))
            im2 = im.convert("RGB") if mime == "image/jpeg" else im
            im2 = im2.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            if mime == "image/jpeg":
                im2.save(buf, "JPEG", quality=92)
            else:
                im2.save(buf, "PNG", optimize=True)
            replacements[img["bufferView"]] = buf.getvalue()
            n_resized += 1
    if not replacements:
        return 0
    new_bin = bytearray()
    for i, bv in enumerate(bvs):
        while len(new_bin) % 4:
            new_bin += b"\x00"
        data = replacements.get(i)
        if data is None:
            data = g.buffer_view_bytes(i)
        bv["byteOffset"] = len(new_bin)
        bv["byteLength"] = len(data)
        new_bin += data
    js["buffers"][0]["byteLength"] = len(new_bin)
    g.bin = bytes(new_bin)
    with open(glb_path, "wb") as f:
        f.write(g.to_bytes())
    return n_resized


def prep(src: str, dst: str, max_verts: int, max_texture: int,
         max_coord: float, scratch: str | None = None) -> dict:
    """Full pipeline. Writes dst + returns a log dict. Never touches src."""
    log: dict = {"input": src, "output": dst, "steps": []}
    if os.path.abspath(src) == os.path.abspath(dst):
        raise PrepError("output must differ from input — originals are sacred")
    rep0 = validate_file(src, max_coord)
    log["input_report"] = rep0.to_dict()
    if not rep0.ok:
        raise PrepError("input FAILED validation — refusing to prep:\n  "
                        + "\n  ".join(rep0.errors))
    log["steps"].append(f"validated input: {rep0.stats.get('vertices')} verts, "
                         f"{rep0.stats.get('triangles')} tris, "
                         f"texture max dim {rep0.stats.get('texture_max_dim')}")
    tmp = tempfile.mkdtemp(prefix="render-prep-", dir=scratch)
    try:
        work = os.path.join(tmp, "work.glb")
        shutil.copyfile(src, work)
        # 1) decode codecs if present
        if rep0.stats.get("blender_blockers"):
            decoded = os.path.join(tmp, "decoded.glb")
            decode_compressed(work, decoded)
            work = decoded
            log["steps"].append("decoded codec compression via gltf-transform")
        # 2) deep-validate actual geometry bytes now that they're readable
        rep1 = validate_file(work, max_coord, deep=True)
        if not rep1.ok:
            raise PrepError("decoded geometry FAILED deep validation:\n  "
                            + "\n  ".join(rep1.errors))
        verts = rep1.stats["vertices"]
        log["steps"].append(f"deep-validated geometry bytes: {verts} verts")
        # 3) decimate to budget (refine pass re-runs on the PRE-decimation
        #    file with a corrected ratio — never decimate a decimated mesh)
        if verts > max_verts:
            ratio = max_verts / verts
            out = os.path.join(tmp, "decimated.glb")
            method = decimate(work, out, ratio)
            rep2 = validate_file(out, max_coord, deep=False)
            got = rep2.stats.get("vertices", 0)
            log["steps"].append(f"decimated via {method} ratio {ratio:.3f}: "
                                f"{verts} -> {got} verts")
            if got > max_verts * 1.05 and got > 0:
                ratio2 = ratio * (max_verts / got) * 0.98
                out2 = os.path.join(tmp, "decimated2.glb")
                decimate(work, out2, ratio2)
                rep2 = validate_file(out2, max_coord, deep=False)
                log["steps"].append(
                    f"refine pass on original geometry, ratio {ratio2:.3f}: "
                    f"-> {rep2.stats.get('vertices')} verts")
                out = out2
            work = out
        # 4) texture downscale (pure Python, on our copy)
        n = downscale_textures(work, max_texture)
        log["steps"].append(f"downscaled {n} textures to <= {max_texture}px")
        # 5) final deep validation of exactly what Blender will eat
        repf = validate_file(work, max_coord, deep=True)
        log["output_report"] = repf.to_dict()
        if not repf.ok:
            raise PrepError("FINAL output FAILED validation — not shipping:\n  "
                            + "\n  ".join(repf.errors))
        if repf.stats.get("blender_blockers"):
            raise PrepError("final output still codec-compressed: "
                            + ", ".join(repf.stats["blender_blockers"]))
        shutil.copyfile(work, dst)
        log["steps"].append(f"wrote render-safe copy: {dst} "
                             f"({repf.stats['file_bytes']} bytes, "
                             f"{repf.stats['vertices']} verts, "
                             f"texture max dim {repf.stats['texture_max_dim']})")
        return log
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_report(rep: Report):
    s = rep.stats
    print(f"file: {rep.path} ({s.get('file_bytes', '?')} bytes)")
    print(f"  vertices={s.get('vertices')} triangles={s.get('triangles')} "
          f"textures={len(rep.textures)} texture_max_dim={s.get('texture_max_dim')} "
          f"extensions={s.get('extensions_used')}")
    for t in rep.textures:
        print(f"  texture[{t['index']}] {t['name']} {t['mime']} "
              f"{t.get('bytes', '?')}B -> {t['status']}")
    for w in rep.warnings:
        print(f"  WARNING: {w}")
    for e in rep.errors:
        print(f"  ERROR: {e}")
    print("  RESULT:", "OK — safe to render" if rep.ok else "FAIL — DO NOT RENDER")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="render-prep",
        description="Validate GLBs and produce render-safe copies for Blender.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="deep-check a GLB, fail loudly")
    pv.add_argument("input")
    pv.add_argument("--max-coord", type=float, default=DEFAULT_MAX_COORD)
    pv.add_argument("--json", dest="json_out")

    pp = sub.add_parser("prep", help="validate + build a render-safe copy")
    pp.add_argument("input")
    pp.add_argument("-o", "--output", required=True)
    pp.add_argument("--max-verts", type=int, default=250_000)
    pp.add_argument("--max-texture", type=int, default=2048)
    pp.add_argument("--max-coord", type=float, default=DEFAULT_MAX_COORD)
    pp.add_argument("--scratch", default=None,
                    help="scratch dir for intermediates (default: system temp)")
    pp.add_argument("--json", dest="json_out")

    sub.add_parser("check-env", help="report which external tools are visible")

    args = ap.parse_args(argv)

    if args.cmd == "check-env":
        for name in ("gltfpack", "gltf-transform", "blender"):
            print(f"{name}: {find_tool(name) or 'NOT FOUND'}")
        try:
            import PIL
            print(f"Pillow: {PIL.__version__}")
        except ImportError:
            print("Pillow: NOT INSTALLED (required)")
        print(f"numpy: {np.__version__}")
        return 0

    if args.cmd == "validate":
        rep = validate_file(args.input, args.max_coord)
        _print_report(rep)
        if args.json_out:
            with open(args.json_out, "w") as f:
                json.dump(rep.to_dict(), f, indent=2)
        return 0 if rep.ok else 2

    if args.cmd == "prep":
        try:
            log = prep(args.input, args.output, args.max_verts,
                       args.max_texture, args.max_coord, args.scratch)
        except PrepError as e:
            print(f"PREP FAILED: {e}", file=sys.stderr)
            return 3
        for step in log["steps"]:
            print(f"  [prep] {step}")
        if args.json_out:
            with open(args.json_out, "w") as f:
                json.dump(log, f, indent=2)
        print(f"OK: render-safe copy at {args.output}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
