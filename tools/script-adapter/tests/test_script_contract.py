"""Contract tests for tools/script-adapter/.

Run:  python3 tools/script-adapter/tests/test_script_contract.py
  or: python3 -m pytest tools/script-adapter/tests/ -q

All data is synthetic. These tests prove the plumbing
(contract -> prompt -> client -> retarget -> keyframes), not the AI.
"""

import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from script_contract import (  # noqa: E402
    ACTION_DIM,
    STATE_DIM,
    ContractError,
    ScriptAction,
    ScriptState,
    ScriptTrajectory,
    TextConditioning,
    make_synthetic_trajectory,
)
from prompt_builder import (  # noqa: E402
    build_script_prompt,
    canon_filter,
    style_hints_for,
)
from smpl_to_wh import (  # noqa: E402
    ACTION_JOINTS,
    axis_angle_to_quat,
    default_bone_map,
    keyframes_to_wh_anim_dict,
    trajectory_to_keyframes,
)
from client import ScriptClient, StubScriptServer  # noqa: E402

PASS = []
FAIL = []


def check(name, fn):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # layout assumption warning is expected
            fn()
        PASS.append(name)
        print(f"  PASS {name}")
    except Exception as e:  # noqa: BLE001
        FAIL.append((name, e))
        print(f"  FAIL {name}: {e}")


def expect_raises(fn, exc=ContractError):
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


# --- contract shapes -------------------------------------------------------
def t_state_ok():
    ScriptState(np.zeros(STATE_DIM)).validate()


def t_state_bad_dim():
    expect_raises(lambda: ScriptState(np.zeros(100)).validate())


def t_state_nan():
    v = np.zeros(STATE_DIM)
    v[5] = np.nan
    expect_raises(lambda: ScriptState(v).validate())


def t_action_ok():
    ScriptAction(np.zeros(ACTION_DIM)).validate()


def t_action_bad_dim():
    expect_raises(lambda: ScriptAction(np.zeros(10)).validate())


def t_text_cond_ok():
    TextConditioning(np.zeros(512), np.zeros((8, 512))).validate()


def t_text_cond_bad():
    expect_raises(lambda: TextConditioning(np.zeros(256), np.zeros((8, 512))).validate())


def t_traj_synthetic():
    traj = make_synthetic_trajectory(horizon=16, seed=7)
    assert traj.horizon == 16
    assert abs(traj.duration_s - 16 / 30) < 1e-9


def t_traj_mismatch():
    expect_raises(
        lambda: ScriptTrajectory(
            states=np.zeros((16, STATE_DIM)), actions=np.zeros((8, ACTION_DIM))
        ).validate()
    )


# --- prompt builder ---------------------------------------------------------
def t_prompt_ok():
    job = build_script_prompt("fast jab-cross", "king", archetype="strike",
                              duration_s=2.0, seed=1)
    assert "jab-cross" in job.prompt
    assert "lucha-libre wrestling" in job.prompt
    assert job.constraints["require_foot_contact"] is True


def t_prompt_unmapped_source():
    expect_raises(lambda: build_script_prompt("jab", "no-such-fighter"))


def t_prompt_rejects_minor():
    expect_raises(lambda: canon_filter("a child throws a punch"))


def t_prompt_rejects_sexual():
    expect_raises(lambda: canon_filter("sexy victory pose, nude"))


def t_prompt_rejects_famous():
    expect_raises(lambda: canon_filter("punch like mike tyson"))


def t_style_hints_table():
    hints = style_hints_for("hwoarang")
    assert "taekwondo kick chains" in hints


# --- retarget ----------------------------------------------------------------
def t_quat_identity():
    q = axis_angle_to_quat(np.zeros((4, 3)))
    assert q.shape == (4, 4)
    assert np.allclose(q[:, 3], 1.0)  # w = 1 for zero rotation


def t_quat_90deg():
    q = axis_angle_to_quat(np.array([[0.0, 0.0, np.pi / 2]]))
    assert abs(q[0, 2] - np.sin(np.pi / 4)) < 1e-9
    assert abs(q[0, 3] - np.cos(np.pi / 4)) < 1e-9
    assert abs(np.linalg.norm(q[0]) - 1.0) < 1e-9


def t_bone_map_default():
    m = default_bone_map()
    assert len(m) == 24 and m["l_elbow"] == "l_elbow"


def t_keyframes_bake():
    traj = make_synthetic_trajectory(horizon=30, seed=3)  # 1s at 30fps
    kfs = trajectory_to_keyframes(traj, target_fps=60)
    # 23 action joints mapped + root height track
    assert len([k for k in kfs if not k.startswith("__")]) == len(ACTION_JOINTS)
    elbow = kfs["l_elbow"]
    assert len(elbow) == 61  # 1s @ 60fps + endpoint
    assert abs(elbow[0][0] - 0.0) < 1e-9 and abs(elbow[-1][0] - 1.0) < 1e-6
    for _, q in elbow:
        assert abs(sum(c * c for c in q) - 1.0) < 1e-6  # unit quats


def t_keyframes_unmapped_joint_skipped():
    traj = make_synthetic_trajectory(horizon=8, seed=3)
    kfs = trajectory_to_keyframes(traj, bone_map={"l_elbow": "l_elbow"})
    bones = [k for k in kfs if not k.startswith("__")]
    assert bones == ["l_elbow"]


def t_clip_envelope_defaults_show():
    traj = make_synthetic_trajectory(horizon=8, seed=3)
    kfs = trajectory_to_keyframes(traj)
    clip = keyframes_to_wh_anim_dict(kfs, "test-jab")
    assert clip["format"] == "wh-anim/1"
    assert clip["set"] == "SHOW"  # show-animation lock: never FIGHT by default
    assert clip["fps"] == 60


# --- client / stub round trip -------------------------------------------------
def t_client_round_trip():
    job = build_script_prompt("spinning backfist", "law", duration_s=1.0, seed=42)
    with StubScriptServer() as server:
        client = ScriptClient(server.url)
        traj = client.generate_trajectory(job, timeout_s=10)
        assert traj.horizon == 30  # 1s @ 30fps
        assert traj.prompt == job.prompt
        assert traj.seed == 42
        # full path: trajectory -> keyframes -> clip
        kfs = trajectory_to_keyframes(traj)
        clip = keyframes_to_wh_anim_dict(kfs, "spinning-backfist")
        assert clip["set"] == "SHOW"


def main():
    print("script-adapter contract tests (synthetic data)")
    for name, fn in sorted(
        [(k, v) for k, v in globals().items() if k.startswith("t_")],
        key=lambda kv: kv[0],
    ):
        check(name, fn)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
