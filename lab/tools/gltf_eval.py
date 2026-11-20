"""Tiny glTF/GLB reader + CPU skinning evaluator (numpy). Used by rig_check and previews."""
import json, struct
import numpy as np
CT = {5126: np.float32, 5123: np.uint16, 5121: np.uint8, 5125: np.uint32, 5122: np.int16, 5120: np.int8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

def qmat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def slerp(a, b, t):
    a = np.asarray(a, float); b = np.asarray(b, float); d = np.dot(a, b)
    if d < 0: b, d = -b, -d
    if d > 0.9995: r = a + t * (b - a); return r / np.linalg.norm(r)
    th = np.arccos(d); return (np.sin((1 - t) * th) * a + np.sin(t * th) * b) / np.sin(th)

class Gltf:
    def __init__(self, path):
        b = open(path, "rb").read()
        assert b[:4] == b"glTF", "not a GLB"
        l = struct.unpack("<I", b[12:16])[0]; self.j = json.loads(b[20:20 + l])
        o = 20 + l; self.bin = b[o + 8:o + 8 + struct.unpack("<I", b[o:o + 4])[0]] if o < len(b) else b""
        self.nodes = self.j.get("nodes", [])
        self.bind_mesh_world = True

    def acc(self, i):
        a = self.j["accessors"][i]; v = self.j["bufferViews"][a["bufferView"]]
        dt = CT[a["componentType"]]; n = NC[a["type"]]
        off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = v.get("byteStride")
        isz = np.dtype(dt).itemsize * n
        if stride and stride != isz:
            raw = np.frombuffer(self.bin, np.uint8, a["count"] * stride, off).reshape(a["count"], stride)[:, :isz]
            arr = np.frombuffer(raw.tobytes(), dt).reshape(a["count"], n)
        else:
            arr = np.frombuffer(self.bin, dt, a["count"] * n, off).reshape(a["count"], n)
        if a.get("normalized") and dt != np.float32: arr = arr.astype(np.float32) / np.iinfo(dt).max
        return arr

    def local(self, i, over=None):
        nd = self.nodes[i]; o = (over or {}).get(i, {})
        if "matrix" in nd and not o: return np.array(nd["matrix"]).reshape(4, 4).T
        m = np.eye(4)
        t = o.get("translation", nd.get("translation", [0, 0, 0])); r = o.get("rotation", nd.get("rotation", [0, 0, 0, 1])); s = o.get("scale", nd.get("scale", [1, 1, 1]))
        m[:3, :3] = qmat(r) * np.asarray(s); m[:3, 3] = t; return m

    def world(self, over=None):
        par = {}
        for i, nd in enumerate(self.nodes):
            for c in nd.get("children", []): par[c] = i
        W = {}
        def w(i):
            if i not in W: W[i] = (w(par[i]) if i in par else np.eye(4)) @ self.local(i, over)
            return W[i]
        for i in range(len(self.nodes)): w(i)
        return W

    def sample(self, anim, t):
        over = {}
        a = self.j["animations"][anim]
        for ch in a["channels"]:
            s = a["samplers"][ch["sampler"]]; tm = self.acc(s["input"])[:, 0]; val = self.acc(s["output"])
            if s.get("interpolation") == "CUBICSPLINE": val = val[1::3]
            k = int(np.searchsorted(tm, t, side="right") - 1); k = max(0, min(k, len(tm) - 1)); k2 = min(k + 1, len(tm) - 1)
            f = 0.0 if k2 == k else float(np.clip((t - tm[k]) / (tm[k2] - tm[k]), 0, 1))
            path = ch["target"]["path"]
            if path == "weights": continue
            v = slerp(val[k], val[k2], f) if path == "rotation" else (1 - f) * val[k] + f * val[k2]
            over.setdefault(ch["target"]["node"], {})[path] = list(v)
        return over

    def anim_len(self, anim):
        a = self.j["animations"][anim]
        return max(float(self.acc(s["input"]).max()) for s in a["samplers"])

    def skinned_meshes(self):
        out = []
        for ni, nd in enumerate(self.nodes):
            if "mesh" in nd and "skin" in nd:
                for pr in self.j["meshes"][nd["mesh"]]["primitives"]:
                    at = pr["attributes"]
                    if "JOINTS_0" not in at: continue
                    out.append(dict(node=ni, skin=nd["skin"], pos=self.acc(at["POSITION"]).astype(float), joints=self.acc(at["JOINTS_0"]).astype(int),
                                    weights=self.acc(at["WEIGHTS_0"]).astype(float), idx=self.acc(pr["indices"])[:, 0].astype(int) if "indices" in pr else None))
        return out

    def skin_pose(self, m, over=None):
        sk = self.j["skins"][m["skin"]]; W = self.world(over)
        ibm = self.acc(sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1) if "inverseBindMatrices" in sk else np.array([np.eye(4)] * len(sk["joints"]))
        J = np.array([W[j] @ ibm[k] for k, j in enumerate(sk["joints"])])
        # three.js / Godot convention: the skinned mesh node's world matrix is the bind matrix
        p = np.concatenate([m["pos"], np.ones((len(m["pos"]), 1))], 1) @ W[m["node"]].T if self.bind_mesh_world else np.concatenate([m["pos"], np.ones((len(m["pos"]), 1))], 1)
        out = np.zeros((len(p), 3))
        for c in range(4):
            out += m["weights"][:, c:c + 1] * np.einsum("nij,nj->ni", J[m["joints"][:, c]], p)[:, :3]
        return out
