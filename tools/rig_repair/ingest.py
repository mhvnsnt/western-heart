#!/usr/bin/env python3
"""ingest.py - shared GLB reader for the universal rig-repair pipeline.

Fixes the Track-1 (2026-10-14) findings against PR #77's rig_repair.py:
  1. multi-buffer GLBs: reads each bufferView from its own buffer index
     (PR #77 read only the first BIN chunk -> "buffer is smaller than requested size").
  2. EXT_meshopt_compression: decoded in pure Python via the `meshopt` pip
     package (no node_modules vendoring; disk was at 95%).
  3. multi-mesh / multi-primitive: every primitive of every mesh is readable;
     silent single-primitive reads are gone (data-integrity bug in PR #77).
  4. KHR_draco_mesh_compression: no pure-Python decoder exists -> raises
     DracoError with a clear message; the pipeline routes those models through
     the Blender headless ingest fallback (decode via import/export).

Public API:
  doc = GLBDoc(path)            # parsed container
  doc.accessor(i) -> np.ndarray  # decoded accessor data, any buffer/encoding
  doc.primitives() -> iterator of (mesh_name, prim_index, attrs_dict, idx)
  decode_to_plain(path, out_path)  # meshopt/multi-buffer -> plain 1-buffer GLB
"""
import json, struct, os, sys
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

class DracoError(RuntimeError):
    pass

class GLBDoc:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            b = f.read()
        if b[:4] != b"glTF":
            raise ValueError(f"not a GLB: {path}")
        L = struct.unpack("<I", b[12:16])[0]
        self.json = json.loads(b[20:20 + L])
        o = 20 + L
        # BIN chunks (type 0x004E4942) in order; buffer i -> i-th BIN chunk
        self.bins = []
        while o + 8 <= len(b):
            cl, ct = struct.unpack("<II", b[o:o + 8])
            if ct == 0x004E4942:
                self.bins.append(b[o + 8:o + 8 + cl])
            o += 8 + cl

    # -- raw buffer bytes -------------------------------------------------
    def buffer_view_bytes(self, vi):
        bv = self.json["bufferViews"][vi]
        ext = bv.get("extensions", {})
        if "EXT_meshopt_compression" in ext:
            return self._decode_meshopt(bv, ext["EXT_meshopt_compression"])
        if "KHR_draco_mesh_compression" in ext:
            raise DracoError(
                f"{self.path}: KHR_draco_mesh_compression has no pure-Python decoder; "
                "route through the Blender headless ingest fallback")
        bi = bv.get("buffer", 0)
        if bi >= len(self.bins):
            # phantom fallback buffer (e.g. meshopt fallback:true with no chunk):
            # zero-length view of nothing
            return b""
        buf = self.bins[bi]
        off = bv.get("byteOffset", 0)
        return buf[off:off + bv["byteLength"]]

    def _decode_meshopt(self, bv, e, acc_count=None, acc_ctype=None):
        import meshopt
        bi = e.get("buffer", 0)
        if bi >= len(self.bins):
            raise ValueError(f"meshopt payload buffer {bi} has no BIN chunk in {self.path}")
        buf = self.bins[bi]
        off = e.get("byteOffset", 0)
        comp = buf[off:off + e["byteLength"]]
        count, stride = e["count"], e["byteStride"]
        mode = e.get("mode", "ATTRIBUTES")
        filt = e.get("filter", "NONE") or "NONE"
        if mode in ("TRIANGLES", "INDICES"):
            # gltfpack writes the extension count as the INDEX count for
            # TRIANGLES (verified on real files: accessor count == ext count);
            # trust the accessor count, never count*3.
            n = acc_count if acc_count is not None else count
            size = {5121: 1, 5122: 2, 5123: 2, 5125: 4}.get(acc_ctype, 4)
            if size == 1:
                size = 2  # meshopt index codec minimum destination is 16-bit
            idx = meshopt.decode_index_buffer(comp, n, size)
            return np.asarray(idx).tobytes()
        # ATTRIBUTES
        arr = meshopt.decode_vertex_buffer(comp, count, stride, filter=filt if filt != "NONE" else None)
        return np.asarray(arr).tobytes()

    # -- accessors ---------------------------------------------------------
    def accessor(self, i):
        j = self.json
        a = j["accessors"][i]
        bv = j["bufferViews"][a["bufferView"]]
        ext = bv.get("extensions", {})
        dt = np.dtype(CT[a["componentType"]])
        n = NC[a["type"]]
        if "EXT_meshopt_compression" in ext:
            e = ext["EXT_meshopt_compression"]
            data = self._decode_meshopt(bv, e, acc_count=a["count"], acc_ctype=a["componentType"])
            # decoded layout: count x byteStride (or tight for indices)
            if e.get("mode") in ("TRIANGLES", "INDICES"):
                idt = np.dtype(CT[a["componentType"]])
                arr = np.frombuffer(data, dtype=idt, count=a["count"] * n).reshape(a["count"], n)
                if a.get("normalized"):
                    arr = arr.astype(np.float32) / np.iinfo(idt).max
                return arr.copy()
            stride = e["byteStride"]
            raw = np.frombuffer(data, np.uint8, count=stride * a["count"])
            arr = np.lib.stride_tricks.as_strided(
                raw, (a["count"], dt.itemsize * n), (stride, 1)).copy().view(dt).reshape(a["count"], n)
        else:
            data = self.buffer_view_bytes(a["bufferView"])
            off = a.get("byteOffset", 0)
            stride = bv.get("byteStride", 0) or dt.itemsize * n
            raw = np.frombuffer(data, np.uint8,
                                count=stride * (a["count"] - 1) + dt.itemsize * n, offset=off)
            arr = np.lib.stride_tricks.as_strided(
                raw, (a["count"], dt.itemsize * n), (stride, 1)).copy().view(dt).reshape(a["count"], n)
        if a.get("normalized"):
            arr = arr.astype(np.float32) / np.iinfo(dt).max
        return arr

    # -- primitives (ALL of them) ------------------------------------------
    def primitives(self):
        """Yields (mesh_name, prim_index, attrs, indices) for every primitive
        of every mesh. attrs maps attribute name -> np.ndarray."""
        j = self.json
        for mi, m in enumerate(j.get("meshes", [])):
            for pi, pr in enumerate(m["primitives"]):
                attrs = {k: self.accessor(v) for k, v in pr["attributes"].items()}
                idx = self.accessor(pr["indices"]).reshape(-1).astype(np.int64)
                yield (m.get("name", f"mesh_{mi}"), pi, attrs, idx)

    def prim_count(self):
        return sum(len(m["primitives"]) for m in self.json.get("meshes", []))


def decode_to_plain(path, out_path):
    """Rewrite a GLB with meshopt/multi-buffer content as a plain single-buffer
    GLB (same JSON structure, decoded data). Used so downstream numpy stages and
    rig_check never need a decode path of their own."""
    doc = GLBDoc(path)
    j = json.loads(json.dumps(doc.json))
    blob = bytearray()
    new_bvs = []

    def add(data, target=None):
        while len(blob) % 4:
            blob.append(0)
        bv = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
        if target:
            bv["target"] = target
        blob.extend(bytes(data))
        new_bvs.append(bv)
        return len(new_bvs) - 1

    # decode every bufferView that has data; keep JSON shape otherwise
    bv_map = {}
    for vi, bv in enumerate(j["bufferViews"]):
        ext = bv.get("extensions", {})
        data = doc.buffer_view_bytes(vi)  # decoded if meshopt
        bv2 = dict(bv)
        bv2.pop("extensions", None)
        bv2["buffer"] = 0
        while len(blob) % 4:
            blob.append(0)
        bv2["byteOffset"] = len(blob)
        bv2["byteLength"] = len(data)
        blob.extend(data)
        new_bvs.append(bv2)
        bv_map[vi] = len(new_bvs) - 1
    j["bufferViews"] = new_bvs
    for a in j["accessors"]:
        a["bufferView"] = bv_map[a["bufferView"]]
    for im in j.get("images", []):
        if "bufferView" in im:
            im["bufferView"] = bv_map[im["bufferView"]]
    # meshopt is decoded now: drop it from extensionsUsed (output is plain)
    for k in ("extensionsUsed", "extensionsRequired"):
        vals = [e for e in j.get(k, []) if e != "EXT_meshopt_compression"]
        if vals:
            j[k] = vals
        else:
            j.pop(k, None)
    j["buffers"] = [{"byteLength": len(blob)}]
    jb = json.dumps(j, separators=(",", ":")).encode()
    jb += b" " * (-len(jb) % 4)
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 28 + len(jb) + len(blob)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)
    return out_path


if __name__ == "__main__":
    # quick self-test: decode a meshopt GLB and report primitives
    src, dst = sys.argv[1], sys.argv[2]
    decode_to_plain(src, dst)
    d = GLBDoc(dst)
    print("primitives:", d.prim_count(), "buffers:", len(d.json["buffers"]),
          "extUsed:", d.json.get("extensionsUsed"))
