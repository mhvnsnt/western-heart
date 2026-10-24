"""Minimal dependency-free (numpy) GLB writer for the Lab importer."""
import json, struct
import numpy as np

class GLB:
    def __init__(self):
        self.j = {"asset": {"version": "2.0", "generator": "western-heart-lab t3_to_gltf"},
                  "scene": 0, "scenes": [{"nodes": []}], "nodes": [], "meshes": [],
                  "accessors": [], "bufferViews": [], "buffers": [], "materials": []}
        self.bin = bytearray()

    def _view(self, data, target=None):
        while len(self.bin) % 4: self.bin += b"\0"
        off = len(self.bin); self.bin += data
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target: v["target"] = target
        self.j["bufferViews"].append(v); return len(self.j["bufferViews"]) - 1

    def acc(self, arr, kind, target=None, minmax=False):
        arr = np.ascontiguousarray(arr)
        ct = {np.float32: 5126, np.uint16: 5123, np.uint8: 5121, np.uint32: 5125}[arr.dtype.type]
        bv = self._view(arr.tobytes(), target)
        a = {"bufferView": bv, "componentType": ct, "count": int(arr.shape[0]), "type": kind}
        if minmax:
            a["min"] = arr.min(0).tolist() if arr.ndim > 1 else [float(arr.min())]
            a["max"] = arr.max(0).tolist() if arr.ndim > 1 else [float(arr.max())]
        self.j["accessors"].append(a); return len(self.j["accessors"]) - 1

    def node(self, **kw):
        self.j["nodes"].append(kw); return len(self.j["nodes"]) - 1

    def save(self, path):
        self.j["buffers"] = [{"byteLength": len(self.bin)}]
        js = json.dumps(self.j, separators=(",", ":")).encode()
        while len(js) % 4: js += b" "
        b = bytes(self.bin)
        while len(b) % 4: b += b"\0"
        total = 12 + 8 + len(js) + 8 + len(b)
        with open(path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total))
            f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
            f.write(struct.pack("<II", len(b), 0x004E4942)); f.write(b)
