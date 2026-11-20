"""Contract tests for tools/photo-to-fighter/.

Run:  python3 tools/photo-to-fighter/tests/test_pipeline_contract.py
  or: python3 -m pytest tools/photo-to-fighter/tests/ -q

All backends are stubs with synthetic data. These tests prove the
orchestration, gates, and stage contracts — not the AI.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages import (  # noqa: E402
    GaiaHeadPass,
    GameMesh,
    IntakeSpec,
    PhotoFighter,
    RiggedFighter,
    SplatAvatar,
    StageError,
    TexturedFighter,
)
from likeness_policy import (  # noqa: E402
    build_intake_spec,
    log_likeness_record,
)
from pipeline import stub_pipeline  # noqa: E402

PASS = []
FAIL = []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"  PASS {name}")
    except Exception as e:  # noqa: BLE001
        FAIL.append((name, e))
        print(f"  FAIL {name}: {e}")


def expect_raises(fn, exc=StageError):
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def _good_record():
    return log_likeness_record(
        photo_path="crew/alice.png",
        face_source="own",
        subject_is_adult=True,
        consent_given=True,
        subject_age_years=34,
    )


def _good_spec(record=None):
    record = record or _good_record()
    return build_intake_spec("crew/alice.png", 2048, 2048, record)


# --- gates ------------------------------------------------------------------
def t_consent_gate_blocks():
    expect_raises(
        lambda: log_likeness_record(
            photo_path="x.png", face_source="own", subject_is_adult=True,
            consent_given=False,
        )
    )


def t_adult_gate_blocks_minor():
    expect_raises(
        lambda: log_likeness_record(
            photo_path="x.png", face_source="own", subject_is_adult=True,
            consent_given=True, subject_age_years=15,
        )
    )


def t_adult_gate_blocks_unconfirmed():
    expect_raises(
        lambda: log_likeness_record(
            photo_path="x.png", face_source="ai-generated",
            subject_is_adult=False, consent_given=False,
        )
    )


def t_famous_face_blocked():
    expect_raises(
        lambda: log_likeness_record(
            photo_path="x.png", face_source="own", subject_is_adult=True,
            consent_given=True, is_public_figure=True,
        )
    )


def t_claimed_identity_blocked():
    expect_raises(
        lambda: log_likeness_record(
            photo_path="x.png", face_source="own", subject_is_adult=True,
            consent_given=True, claimed_identity="Some Celebrity",
        )
    )


def t_ai_generated_face_ok():
    rec = log_likeness_record(
        photo_path="gen/face-001.png", face_source="ai-generated",
        subject_is_adult=True, consent_given=False,
    )
    assert rec.face_source == "ai-generated"


# --- stage contracts ----------------------------------------------------------
def t_intake_rejects_small_photo():
    rec = _good_record()
    expect_raises(lambda: build_intake_spec("x.png", 512, 512, rec))


def t_splat_rejects_non_apose():
    expect_raises(
        lambda: SplatAvatar(
            splat_count=100_000, a_pose=False,
            bounds_m=((0, 0, 0), (0.6, 1.8, 0.4)),
        ).validate()
    )


def t_mesh_rejects_non_watertight():
    expect_raises(
        lambda: GameMesh(
            vertex_count=20_000, triangle_count=40_000,
            watertight=False, method="sugar", height_m=1.8,
        ).validate()
    )


def t_mesh_rejects_unknown_method():
    expect_raises(
        lambda: GameMesh(
            vertex_count=20_000, triangle_count=40_000,
            watertight=True, method="magic", height_m=1.8,
        ).validate()
    )


def t_rig_rejects_bad_weights():
    import numpy as np
    from stages import REQUIRED_BONES
    w = np.ones((10, len(REQUIRED_BONES)))  # rows sum to n_bones, not 1
    expect_raises(
        lambda: RiggedFighter(bones=list(REQUIRED_BONES), skinning_weights=w).validate()
    )


def t_texture_rejects_incomplete_set():
    expect_raises(
        lambda: TexturedFighter(maps={"albedo": "a.png"}).validate()
    )


def t_fighter_rejects_default_slot():
    import numpy as np
    from stages import REQUIRED_BONES
    n = len(REQUIRED_BONES)
    w = np.ones((4, n)) / n
    rig = RiggedFighter(bones=list(REQUIRED_BONES), skinning_weights=w).validate()
    tex = TexturedFighter(
        maps={"albedo": "a", "normal": "n", "roughness": "r"}
    ).validate()
    expect_raises(
        lambda: PhotoFighter(
            fighter_id="f1", rig=rig, textures=tex, head_pass=None,
            likeness_record_id="likeness-x", attire_slot="default",
        ).validate()
    )


# --- pipeline -----------------------------------------------------------------
def t_pipeline_happy_path():
    pipe = stub_pipeline()
    fighter = pipe.run(_good_spec(), "photo-fighter-001")
    assert fighter.fighter_id == "photo-fighter-001"
    assert fighter.attire_slot == "user-1"
    assert fighter.head_pass is None


def t_pipeline_with_gaia_head():
    pipe = stub_pipeline(with_gaia_head=True)
    fighter = pipe.run(_good_spec(), "photo-fighter-002")
    assert fighter.head_pass is not None
    assert "neutral" in fighter.head_pass.expressions


def t_pipeline_rejects_unknown_record():
    pipe = stub_pipeline()
    spec = IntakeSpec(
        photo_path="x.png", width_px=2048, height_px=2048,
        subject_is_adult=True, consent_record_id="likeness-nonexistent",
        face_source="own",
    ).validate()
    expect_raises(lambda: pipe.run(spec, "f-bad"))


def main():
    print("photo-to-fighter contract tests (stub backends, synthetic data)")
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
