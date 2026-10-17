#!/usr/bin/env python3
"""Western Heart wire-up for Google GNM (Generative aNthropometric Model).

Connects GNM Head's parametric face model to the customization suite's BODY
tab (UNIFIED-UI-SPEC.md section 5.1: Head Shape / Face sliders).

What it does:
  1. fetch-weights  - download gnm_head.npz (v3.0) from Hugging Face
                      (gated: needs an HF account with access to google/gnm-3).
                      Skips download if a cached copy already exists.
  2. list-sliders   - print the named identity + expression slider dimensions
                      the suite's UI binds to.
  3. sample         - sample an identity (random or semantic-style preset) and
                      dump identity/expression parameter JSON.
  4. export-glb     - bake base head mesh + expression morph targets into a
                      GLB the web build loads directly; the BODY tab drives
                      mesh.morphTargetInfluences[i] per slider for live
                      re-morph (see WH-INTEGRATION.md).

The mesh math here uses GNM's documented linear shape model
(vertices = template + sum_i id[i]*identity_basis[i]
                    + sum_e ex[e]*expression_basis[e])
which is exactly the part the customization sliders modulate. Full joint
posing / pose-correctives live in upstream's gnm_numpy backend for offline
baking; they are intentionally out of the live-preview path.

Field layout follows upstream gnm/shape/gnm_numpy.py (attributes:
template_vertex_positions, vertex_identity_basis, expression_basis,
triangles, expression_names, identity_names, vertex_uvs).
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import urllib.request

import numpy as np

WEIGHTS_URL = "https://huggingface.co/google/gnm-3/resolve/main/v3_0/gnm_head.npz"
DEFAULT_CACHE = os.path.expanduser("~/.cache/wh-gnm/v3_0/gnm_head.npz")
UPSTREAM_COMMIT = "5cf11d785a38a83597e64ad0b6d15950bcd6b390"

REQUIRED_FIELDS = (
    "template_vertex_positions",
    "vertex_identity_basis",
    "expression_basis",
    "triangles",
)


# ---------------------------------------------------------------- weights

def fetch_weights(dest: str = DEFAULT_CACHE, token: str | None = None) -> str:
    """Download gnm_head.npz unless already cached. Returns local path."""
    if os.path.exists(dest):
        print(f"weights already cached: {dest} (skipping download)")
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"downloading {WEIGHTS_URL}\n  -> {dest}")
    print("NOTE: google/gnm-3 is a gated HF repo; set --token with an HF")
    print("token whose account has been granted access, or the server")
    print("returns 401 Unauthorized.")
    req = urllib.request.Request(WEIGHTS_URL)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    tmp = dest + ".part"
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length", 0))
            done = 0
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done/1e6:.1f} / {total/1e6:.1f} MB", end="",
                          flush=True)
        print()
    except Exception as e:  # noqa: BLE001 - report cleanly, keep partial file out
        if os.path.exists(tmp):
            os.remove(tmp)
        raise RuntimeError(f"weight download failed: {e}") from e
    os.rename(tmp, dest)
    print(f"saved: {dest}")
    return dest


# ---------------------------------------------------------------- model

class GNMHead:
    """Minimal dependency-free reader for the GNM Head .npz model."""

    def __init__(self, npz_path: str):
        data = np.load(npz_path, allow_pickle=False)
        missing = [k for k in REQUIRED_FIELDS if k not in data.files]
        if missing:
            raise ValueError(f"{npz_path} missing GNM fields: {missing}")
        self.template: np.ndarray = np.asarray(
            data["template_vertex_positions"], dtype=np.float32)
        self.identity_basis: np.ndarray = np.asarray(
            data["vertex_identity_basis"], dtype=np.float32)      # (I, V, 3)
        self.expression_basis: np.ndarray = np.asarray(
            data["expression_basis"], dtype=np.float32)           # (E, V, 3)
        self.triangles: np.ndarray = np.asarray(
            data["triangles"], dtype=np.int64)                    # (T, 3)
        self.identity_names = [str(n) for n in
                               data["identity_names"]] if "identity_names" \
            in data.files else [f"identity_{i}" for i in
                                range(self.identity_basis.shape[0])]
        self.expression_names = [str(n) for n in
                                 data["expression_names"]] if "expression_names" \
            in data.files else [f"expression_{e}" for e in
                                range(self.expression_basis.shape[0])]
        self.uvs: np.ndarray | None = (
            np.asarray(data["vertex_uvs"], dtype=np.float32)
            if "vertex_uvs" in data.files else None)

    @property
    def identity_dim(self) -> int:
        return self.identity_basis.shape[0]

    @property
    def expression_dim(self) -> int:
        return self.expression_basis.shape[0]

    @property
    def num_vertices(self) -> int:
        return self.template.shape[0]

    def generate(self, identity: np.ndarray,
                 expression: np.ndarray) -> np.ndarray:
        """Linear shape model: template + identity offsets + expression offsets."""
        identity = np.asarray(identity, dtype=np.float32).reshape(-1)
        expression = np.asarray(expression, dtype=np.float32).reshape(-1)
        assert identity.shape[0] == self.identity_dim, \
            f"identity dim {identity.shape[0]} != {self.identity_dim}"
        assert expression.shape[0] == self.expression_dim, \
            f"expression dim {expression.shape[0]} != {self.expression_dim}"
        verts = self.template.copy()
        verts += np.einsum("i,ivj->vj", identity, self.identity_basis)
        verts += np.einsum("e,evj->vj", expression, self.expression_basis)
        return verts

    def expression_target_delta(self, expr_index: int,
                                strength: float = 1.0) -> np.ndarray:
        """Vertex delta for one expression target (what a GLB morph target stores)."""
        return (self.expression_basis[expr_index] * strength).astype(np.float32)


def sample_identity(rng: np.random.Generator, dim: int,
                    scale: float = 1.0) -> np.ndarray:
    return (rng.standard_normal(dim) * scale).astype(np.float32)


# ---------------------------------------------------------------- export

def _vertex_normals(verts: np.ndarray, tris: np.ndarray) -> np.ndarray:
    n = np.zeros_like(verts)
    v0, v1, v2 = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    fn = np.cross(v1 - v0, v2 - v0)
    np.add.at(n, tris[:, 0], fn)
    np.add.at(n, tris[:, 1], fn)
    np.add.at(n, tris[:, 2], fn)
    mag = np.linalg.norm(n, axis=1, keepdims=True)
    return (n / np.maximum(mag, 1e-12)).astype(np.float32)


def _pad(data: bytes) -> bytes:
    return data + b"\x00" * ((-len(data)) % 4)


def export_glb(model: GNMHead, identity: np.ndarray,
               expression_names: list[str], out_path: str) -> None:
    """Write base head + expression morph targets as GLB 2.0.

    Morph target i stores the POSITION delta of expression i at strength 1.0;
    the web UI sets mesh.morphTargetInfluences[i] = slider value.
    Target names go in primitive.extras.targetNames (read by three.js
    via mesh.morphTargetDictionary after GLTFLoader parsing).
    """
    base = model.generate(identity, np.zeros(model.expression_dim,
                                             dtype=np.float32))
    normals = _vertex_normals(base, model.triangles)
    idx = model.triangles.astype(np.uint32).ravel()
    n_verts = model.num_vertices

    blob = bytearray()
    views = []   # (offset, length)
    accessors = []

    def push(arr: np.ndarray, comp: str, count: int, kind: str) -> int:
        off = len(blob)
        raw = _pad(arr.tobytes())
        blob.extend(raw)
        views.append({"buffer": 0, "byteOffset": off,
                      "byteLength": len(raw)})
        accessors.append({"bufferView": len(views) - 1,
                          "componentType": comp, "count": count,
                          "type": kind})
        return len(accessors) - 1

    pos_acc = push(base, 5126, n_verts, "VEC3")
    nrm_acc = push(normals, 5126, n_verts, "VEC3")
    prim: dict = {"attributes": {"POSITION": pos_acc, "NORMAL": nrm_acc},
                  "indices": 0, "material": 0}  # indices accessor set below
    if model.uvs is not None and model.uvs.shape[0] == n_verts:
        prim["attributes"]["TEXCOORD_0"] = push(model.uvs, 5126, n_verts,
                                               "VEC2")
    prim["indices"] = push(idx, 5125, idx.shape[0], "SCALAR")

    targets = []
    for name in expression_names:
        e = model.expression_names.index(name)
        delta = model.expression_target_delta(e)
        targets.append({"POSITION": push(delta, 5126, n_verts, "VEC3")})
    prim["targets"] = targets
    prim["extras"] = {"targetNames": list(expression_names)}

    gltf = {
        "asset": {"version": "2.0",
                  "generator": f"wh_gnm_wireup (GNM {UPSTREAM_COMMIT[:8]})"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [prim]}],
        "materials": [{"pbrMetallicRoughness": {
            "baseColorFactor": [0.82, 0.62, 0.52, 1.0],
            "metallicFactor": 0.0, "roughnessFactor": 0.65},
            "name": "wh_head_preview"}],
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    # glTF spec: JSON chunk padded with spaces (0x20), BIN chunk with zeros.
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode()
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    total = 12 + 8 + len(json_bytes) + 8 + len(blob)
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        f.write(json_bytes)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)
    print(f"wrote {out_path} "
          f"({n_verts} verts, {len(expression_names)} morph targets)")


def export_manifest(model: GNMHead, out_path: str) -> None:
    manifest = {
        "tool": "google/GNM",
        "upstream_commit": UPSTREAM_COMMIT,
        "variant": "head",
        "ui_binding": "UNIFIED-UI-SPEC.md section 5.1 (BODY tab)",
        "identity_sliders": [
            {"index": i, "name": n, "type": "identity",
             "ui": "Head Shape / Face", "range": [-3.0, 3.0], "default": 0.0}
            for i, n in enumerate(model.identity_names)
        ],
        "expression_sliders": [
            {"index": e, "name": n, "type": "expression",
             "ui": "Face (morph target)", "range": [0.0, 1.0], "default": 0.0}
            for e, n in enumerate(model.expression_names)
        ],
    }
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"wrote {out_path} "
          f"({len(model.identity_names)} identity + "
          f"{len(model.expression_names)} expression sliders)")


# ---------------------------------------------------------------- cli

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Western Heart GNM wire-up")
    ap.add_argument("--weights", default=DEFAULT_CACHE,
                    help="path to gnm_head.npz")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("fetch-weights", help="download gnm_head.npz (gated HF)")
    p.add_argument("--token", default=os.environ.get("HF_TOKEN"),
                   help="Hugging Face token (or set HF_TOKEN)")

    sub.add_parser("list-sliders", help="print named slider dimensions")

    p = sub.add_parser("sample", help="sample identity params to JSON")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--out", required=True)

    p = sub.add_parser("export-glb", help="bake head + morph targets to GLB")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--identity-json", default=None,
                   help="identity params JSON (overrides --seed)")
    p.add_argument("--expressions", default=None,
                   help="comma-separated expression names (default: all)")
    p.add_argument("--out", required=True, help="output .glb path")
    p.add_argument("--manifest-out", default=None,
                   help="also write slider manifest JSON here")

    args = ap.parse_args(argv)

    if args.cmd == "fetch-weights":
        fetch_weights(args.weights, args.token)
        return 0

    model = GNMHead(args.weights)
    print(f"loaded GNM Head: {model.num_vertices} verts, "
          f"{model.identity_dim} identity dims, "
          f"{model.expression_dim} expression dims")

    if args.cmd == "list-sliders":
        print("== identity (Head Shape / Face) ==")
        for i, n in enumerate(model.identity_names):
            print(f"  [{i}] {n}")
        print("== expression (morph targets) ==")
        for e, n in enumerate(model.expression_names):
            print(f"  [{e}] {n}")
        return 0

    if args.cmd == "sample":
        rng = np.random.default_rng(args.seed)
        ident = sample_identity(rng, model.identity_dim, args.scale)
        with open(args.out, "w") as f:
            json.dump({"identity": ident.tolist(),
                       "expression": [0.0] * model.expression_dim}, f)
        print(f"wrote {args.out}")
        return 0

    if args.cmd == "export-glb":
        if args.identity_json:
            ident = np.array(json.load(open(args.identity_json))["identity"],
                             dtype=np.float32)
        else:
            ident = sample_identity(np.random.default_rng(args.seed),
                                    model.identity_dim)
        expr_names = (args.expressions.split(",") if args.expressions
                      else list(model.expression_names))
        unknown = [n for n in expr_names if n not in model.expression_names]
        if unknown:
            print(f"unknown expressions: {unknown}", file=sys.stderr)
            return 2
        export_glb(model, ident, expr_names, args.out)
        if args.manifest_out:
            export_manifest(model, args.manifest_out)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
