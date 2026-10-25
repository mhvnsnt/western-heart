"""
SMPL (SCRIPT action space) -> WH fighter skeleton retarget interface.

SCRIPT's action a_t in R^69 is documented as "target joint angles for a
PD controller" (paper Sec 3.1). 69 = 23 SMPL joints x 3 axis-angle values
(root handled via the state stream's root height).

IMPORTANT — ordering assumption: the paper does not publish the exact
69-dim joint ordering. This module assumes the standard SMPL joint order
(joints 1..23, root excluded), flagged by LAYOUT_CONFIRMED = False.
The day the code drops, confirm against their env and flip the flag;
every function validates the flag and warns loudly until then.

Keyframe baking here uses the ACTION stream (axis-angles -> quaternions).
The state stream (6D rotations) is the preferred source for the real
pipeline — see README.md "when code drops" for the state-layout mapping task.

CPU-only, numpy.
"""

from __future__ import annotations

import json
import math
import warnings
from typing import Dict, List, Tuple

import numpy as np

from script_contract import ContractError, ScriptTrajectory

# Standard SMPL joint order (Loper et al. 2015). Joints 1..23 map to the
# 69 action dims in order; joint 0 (pelvis/root) comes from the state stream.
SMPL_JOINTS = [
    "pelvis",       # 0  (root — NOT in action vector)
    "l_hip",        # 1
    "r_hip",        # 2
    "spine1",       # 3
    "l_knee",       # 4
    "r_knee",       # 5
    "spine2",       # 6
    "l_ankle",      # 7
    "r_ankle",      # 8
    "spine3",       # 9
    "l_foot",       # 10
    "r_foot",       # 11
    "neck",         # 12
    "l_collar",     # 13
    "r_collar",     # 14
    "head",         # 15
    "l_shoulder",   # 16
    "r_shoulder",   # 17
    "l_elbow",      # 18
    "r_elbow",      # 19
    "l_wrist",      # 20
    "r_wrist",      # 21
    "l_hand",       # 22
    "r_hand",       # 23
]
ACTION_JOINTS = SMPL_JOINTS[1:]  # 23 joints -> 69 dims

LAYOUT_CONFIRMED = False  # flip when verified against released SCRIPT code
LAYOUT_SOURCE = (
    "assumed standard SMPL joint order from paper text "
    "(arXiv:2605.22894 Sec 3.1: 69-dim PD target joint angles); "
    "NOT yet confirmed against released code"
)

WH_FPS = 60  # game frame rate; SCRIPT training rollouts are ~30fps


def _check_layout():
    if not LAYOUT_CONFIRMED:
        warnings.warn(
            "SMPL 69-dim joint ordering is ASSUMED, not confirmed: "
            + LAYOUT_SOURCE,
            stacklevel=3,
        )


def axis_angle_to_quat(aa: np.ndarray) -> np.ndarray:
    """Axis-angle (..., 3) -> quaternion (..., 4) in (x, y, z, w) order."""
    aa = np.asarray(aa, dtype=np.float64)
    angle = np.linalg.norm(aa, axis=-1, keepdims=True)
    # stable division for near-zero angles
    axis = np.divide(aa, angle, out=np.zeros_like(aa), where=angle > 1e-8)
    half = angle / 2.0
    s = np.sin(half)
    quat = np.concatenate([axis * s, np.cos(half)], axis=-1)
    # normalize for safety
    n = np.linalg.norm(quat, axis=-1, keepdims=True)
    return np.divide(quat, n, out=quat, where=n > 1e-12)


def load_bone_map(path: str) -> Dict[str, str]:
    """Load {smpl_joint_name: wh_bone_name} JSON.

    Same convention as tools/mocap/ bone maps: SMPL-side keys use the
    SMPL_JOINTS names above; values are WH skeleton bone names.
    """
    with open(path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    if not isinstance(mapping, dict):
        raise ContractError(f"bone map {path} must be a JSON object")
    unknown = [k for k in mapping if k not in SMPL_JOINTS]
    if unknown:
        raise ContractError(f"bone map {path} has unknown SMPL joints: {unknown}")
    return mapping


def default_bone_map() -> Dict[str, str]:
    """Identity-ish default: SMPL joint name -> same WH bone name.

    The real map is authored per fighter in the retarget pilot (Phase 2);
    this default keeps the plumbing testable.
    """
    _check_layout()
    return {j: j for j in SMPL_JOINTS}


def trajectory_to_keyframes(
    traj: ScriptTrajectory,
    bone_map: Dict[str, str] | None = None,
    target_fps: int = WH_FPS,
) -> Dict[str, List[Tuple[float, Tuple[float, float, float, float]]]]:
    """Bake a SCRIPT trajectory into WH keyframes.

    Returns {wh_bone: [(time_s, (x, y, z, w)), ...]} at target_fps,
    resampled linearly in axis-angle space from traj.fps. Root height
    comes from states[:, 0]; root translation beyond height is zero
    (fighting-game root motion is authored separately — see README).

    Prototype note: linear axis-angle resampling is fine for plumbing;
    the real pipeline should slerp quaternions (marked in README).
    """
    _check_layout()
    traj.validate()
    bone_map = bone_map or default_bone_map()

    src_fps = float(traj.fps)
    n_src = traj.horizon
    duration = n_src / src_fps
    n_dst = max(2, int(round(duration * target_fps)) + 1)
    dst_t = np.linspace(0.0, duration, n_dst)
    src_t = np.linspace(0.0, duration, n_src)

    keyframes: Dict[str, List[Tuple[float, Tuple[float, float, float, float]]]] = {}
    for idx, smpl_joint in enumerate(ACTION_JOINTS):
        wh_bone = bone_map.get(smpl_joint)
        if not wh_bone:
            continue  # joint not mapped for this fighter — skipped, not faked
        aa_src = traj.actions[:, idx * 3 : idx * 3 + 3]  # (H, 3)
        aa_dst = np.stack(
            [np.interp(dst_t, src_t, aa_src[:, k]) for k in range(3)], axis=1
        )
        quats = axis_angle_to_quat(aa_dst)
        keyframes[wh_bone] = [
            (float(t), (float(q[0]), float(q[1]), float(q[2]), float(q[3])))
            for t, q in zip(dst_t, quats)
        ]

    # root height track (from state stream) for the anchoring step
    root_h_src = traj.states[:, 0]
    root_h_dst = np.interp(dst_t, src_t, root_h_src)
    keyframes["__root_height__"] = [
        (float(t), (0.0, 0.0, 0.0, float(h))) for t, h in zip(dst_t, root_h_dst)
    ]
    return keyframes


def keyframes_to_wh_anim_dict(
    keyframes: Dict[str, List[Tuple[float, Tuple[float, float, float, float]]]],
    clip_name: str,
    anim_set: str = "SHOW",
) -> Dict:
    """Wrap baked keyframes in the wh-anim/1 clip envelope.

    Default set is SHOW (show-animation lock: generated moves never enter
    FIGHT without explicit owner approval).
    """
    if anim_set not in ("FIGHT", "SHOW"):
        raise ContractError(f"anim_set must be FIGHT or SHOW, got {anim_set!r}")
    bones = {b: kfs for b, kfs in keyframes.items() if not b.startswith("__")}
    return {
        "format": "wh-anim/1",
        "name": clip_name,
        "set": anim_set,
        "fps": WH_FPS,
        "bones": {
            bone: [
                {"t": t, "q": [q[0], q[1], q[2], q[3]]} for t, q in kfs
            ]
            for bone, kfs in bones.items()
        },
        "root_height": [
            {"t": t, "h": q[3]} for t, q in keyframes.get("__root_height__", [])
        ],
        "source": "script-adapter (synthetic contract prototype)",
        "layout_confirmed": LAYOUT_CONFIRMED,
    }
