#!/usr/bin/env python3
"""Bake AKI (WWF No Mercy) clips into a WH bank rows.pack.json — with a quality gate.

Pipeline (all existing, proven WH tooling; no new math):
  teardown/wwf-no-mercy/aki_to_tekken3_v3.py   AKI .npy -> 49ch T3 pose vectors
  teardown/tekken3/tools/local/usa_tables.py   pose_to_slot_rotations (bit-exact
                                               PoseBuildMatrices port)
  teardown/tekken3/tools/local/pose_assemble.py FK over the King KMD part hierarchy
                                               (same code path as PA.assemble, fed
                                               explicit pose vectors instead of a
                                               divmot stream)
  lab/tools/t3_motion_bake.py                  T3Space.frame_globals (Kabsch per part)
                                               + TargetRig retarget onto the bank rig
  tools/anim/t3_row_bake.py                    wh-anim-pack/1 writing format (mirrored)

QUALITY GATE (the reason this tool exists): a baked row is written ONLY if it
passes BOTH checks, each calibrated on the bank's existing REAL T3 rows
(king pack, 176 rows, measured 2026-10-21):
  1. step gate — worst-bone mean per-frame rotation step <= the worst such
     value in the real rows (60.6 deg). Kills the IK-whip jitter.
  2. height gate — the row's peak root height (ry) must reach >= 0.70 m.
     Every named Rock move/taunt starts from standing (real standing rows
     peak at ~0.96 m); a bake whose hips never rise above 0.70 m is a
     collapsed pose, however smooth. This gate exists because the four
     taunt clips PASSED the step gate (32-60 deg) while rendering as a
     crumpled floor-level skeleton (peak ry 0.52-0.53 m, own-eyes stick
     render vs real row 281 — see docs/anim/AKI-BAKE-ROCK-2026-10-21.md).
AKI v3 poses drive T3's FK Euler joints, but T3 arm/leg segments are
IK-driven (PoseBuildMatrices overwrites slots 4,5,8,9,12,13,15,16 from the
IK target channels, which AKI FK data does not yet feed) — so today every
AKI clip fails at least one gate and NOTHING is written. The gate keeps
unplayable motion out of the game; when the AKI FK -> T3 IK step lands
(the open item named in AKI-TEKKEN3-RETARGET.md v1 scope limits), the same tool writes the rows unchanged.

Usage:
  python3 tools/anim/aki_row_bake.py              # verify all CornerStone Rock clips
  python3 tools/anim/aki_row_bake.py --write      # write gate-passing rows into the pack
"""
import argparse, base64, hashlib, json, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "lab/tools"))
sys.path.insert(0, str(REPO / "teardown/tekken3/tools/local"))
import t3_motion_bake as TB  # noqa: E402
import pose_assemble as PA  # noqa: E402
import usa_tables  # noqa: E402

BANK_DIR = REPO / "game/assets/anim/t3/king_on_pantera_leoman"
POSE_DIR = REPO / "teardown/wwf-no-mercy/aki-rock-v3"
TARGET_GLB = "lab/game/assets/pantera_leoman.glb"


def b64_i16(a):
    return base64.b64encode(np.ascontiguousarray(a, dtype="<i2").tobytes()).decode()


def b64_i16_decode(s):
    return np.frombuffer(base64.b64decode(s), dtype="<i2").astype(float)


def pack_baseline(pack):
    """Worst-bone mean per-frame step (deg) across the pack's existing rows."""
    from scipy.spatial.transform import Rotation as Rr
    nb = len(pack["bones"])
    worst = 0.0
    for rec in pack["rows"].values():
        n = rec["n"]
        q = b64_i16_decode(rec["q"]).reshape(n, nb, 4) / 32767.0
        for bi in range(nb):
            rots = Rr.from_quat(q[:, bi, :])
            mag = np.degrees((rots[:-1].inv() * rots[1:]).magnitude())
            if len(mag):
                worst = max(worst, float(mag.mean()))
    return worst


def clip_stats(tracks, names):
    from scipy.spatial.transform import Rotation as Rr
    stats = {}
    for name in names:
        qs = np.array(tracks[name][0])
        if len(qs) < 2:
            stats[name] = 0.0
            continue
        rots = Rr.from_quat(qs)
        mag = np.degrees((rots[:-1].inv() * rots[1:]).magnitude())
        stats[name] = float(mag.mean())
    return stats


class KingFK:
    """pose_assemble FK with explicit pose vectors (PA.assemble minus the divmot read)."""

    def __init__(self):
        self.kmd_path = TB.T3 / TB.BANKS["king"][0]
        self.model = PA.kmd.parse(self.kmd_path.read_bytes())
        self.stab = usa_tables.load_tables(usa_tables.EXE_PATH)
        self.part_parent, self.part_offset = [], []
        for k in range(18):
            row = self.model.rows[PA.PART_ROW[k]]
            x, y, z = row.offset
            self.part_parent.append(row.parent)
            self.part_offset.append((x, y, -z))
        self.slot_of_part = PA.PART_SLOT[:18]
        self.slot_parent = {}
        for k, s in enumerate(self.slot_of_part):
            p = self.part_parent[k]
            self.slot_parent[s] = self.slot_of_part[p] if p >= 0 else -1

    def posed_parts(self, pose_vec):
        slot_rots = usa_tables.pose_to_slot_rotations([int(x) for x in pose_vec], self.stab)
        local = {}
        for k, s in enumerate(self.slot_of_part):
            r = slot_rots[s]
            rf = [[r[3 * i + j] / 4096.0 for j in range(3)] for i in range(3)]
            tx, ty, tz = self.part_offset[k]
            local[s] = [rf[0] + [tx], rf[1] + [ty], rf[2] + [tz], [0, 0, 0, 1]]
        root = [[1, 0, 0, pose_vec[0]], [0, 1, 0, pose_vec[1]],
                [0, 0, 1, pose_vec[2]], [0, 0, 0, 1]]
        world = {}

        def get_world(s):
            if s in world:
                return world[s]
            p = self.slot_parent[s]
            base = root if p < 0 else get_world(p)
            world[s] = PA.mat_mul(base, local[s])
            return world[s]

        parts = {}
        for k in range(18):
            s = self.slot_of_part[k]
            w = get_world(s)
            row = self.model.rows[PA.PART_ROW[k]]
            if row.verts is None:
                continue
            parts[k] = np.array([PA.mat_vec(w, v) for v in row.verts.coords])
        return parts


def bake_clip(pose_json, fk, space, rig):
    data = json.load(open(pose_json))
    frames = [space.frame_globals(fk.posed_parts(pv)) for pv in data["poses"]]
    tracks, root_t = TB.retarget(rig, space, {"frames": frames, "fps": 30.0})
    return data, tracks, root_t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write gate-passing rows into rows.pack.json")
    ap.add_argument("--report", default="", help="write the JSON bake report here")
    a = ap.parse_args()

    pack_path = BANK_DIR / "rows.pack.json"
    pack = json.load(open(pack_path))
    baseline = pack_baseline(pack)
    print(f"gate: worst-bone mean step <= {baseline:.1f} deg (max over the pack's {len(pack['rows'])} real rows)")

    fk = KingFK()
    space = TB.T3Space(TB.T3 / TB.BANKS["king"][0], TB.T3 / TB.BANKS["king"][2])
    rig = TB.TargetRig(REPO / TARGET_GLB)

    HEIGHT_GATE = 0.70  # m; standing-start clips must peak at/above this root height
    report = {"gate_worst_bone_mean_step_deg": round(baseline, 2), "gate_peak_root_height_m": HEIGHT_GATE, "clips": {}}
    wrote = []
    for pose_json in sorted(POSE_DIR.glob("*.json")):
        data, tracks, root_t = bake_clip(pose_json, fk, space, rig)
        stats = clip_stats(tracks, rig.names)
        worst_bone = max(stats, key=stats.get)
        peak_ry = float(np.max(np.array(root_t)[:, 1]))
        step_ok = stats[worst_bone] <= baseline
        height_ok = peak_ry >= HEIGHT_GATE
        passed = step_ok and height_ok
        key = data["mat_kings_id"].lower().replace("-", "")  # MK-1240 -> mk1240
        report["clips"][key] = {
            "source_file": data["source_file"], "frames": data["source_frames"],
            "worst_bone": worst_bone, "worst_bone_mean_step_deg": round(stats[worst_bone], 1),
            "peak_root_height_m": round(peak_ry, 2),
            "gate": "PASS" if passed else "FAIL",
            "gate_detail": f"step {'ok' if step_ok else 'FAIL'}, height {'ok' if height_ok else 'FAIL'}",
        }
        print(f"{key}: {data['source_frames']}f worst {worst_bone} {stats[worst_bone]:.1f} deg/frame, peak ry {peak_ry:.2f} m -> {'PASS' if passed else 'FAIL'}")
        if passed and a.write:
            n = len(root_t)
            q = np.array([tracks[b][0] for b in rig.names], float).transpose(1, 0, 2)
            q *= np.where(q[..., 3:4] < 0, -1.0, 1.0)
            rtv = np.array(root_t, float)
            pack["rows"][key] = {
                "slot": None, "move_row": key, "stream_frames": data["source_frames"], "n": n,
                "used_by": ["ryuji-rock"], "source": "WWF No Mercy (AKI) via aki_to_tekken3_v3 + aki_row_bake",
                "q": b64_i16(np.round(np.clip(q, -1, 1) * 32767)),
                "rx": b64_i16(np.round(rtv[:, 0] * 1000)), "ry": b64_i16(np.round(rtv[:, 1] * 1000)),
                "rz": b64_i16(np.round(rtv[:, 2] * 1000)),
            }
            wrote.append(key)
    if a.write and wrote:
        json.dump(pack, open(pack_path, "w"), separators=(",", ":"))
        print(f"wrote rows: {wrote}")
    elif a.write:
        print("no clips passed the gate — pack untouched")
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
