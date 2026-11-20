"""Shared Tekken 3 helpers for the Lab importer (reads the owner's own teardown data)."""
import sys, json
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
T3 = REPO / "teardown/tekken3"
sys.path.insert(0, str(T3 / "tools/local"))
import kmd_parse  # noqa: E402

PART_ROW = [0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24]
NPARTS = 18

def load_obj_parts(path):
    parts, cur = {}, None
    for line in open(path):
        if line.startswith("o "):
            cur = int(line.split()[1].split("_")[1]); parts[cur] = []
        elif line.startswith("v ") and cur is not None:
            parts[cur].append([float(x) for x in line.split()[1:4]])
    return {k: np.array(v) for k, v in parts.items()}

def kabsch(A, B):
    """Rigid R,t with B ~= R A + t. Returns R, t, rms."""
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    t = cb - R @ ca
    rms = float(np.sqrt(((A @ R.T + t - B) ** 2).sum(1).mean()))
    return R, t, rms
