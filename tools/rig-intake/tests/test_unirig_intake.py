"""Unit tests for tools/rig-intake/unirig_intake.py.

Covers the GPU-gating and pipeline-command logic. Real inference needs a
CUDA GPU + UniRig checkout and is NOT exercised here (see UNIRIG-SETUP.md).
"""
import importlib.util
import os
import pathlib
import sys

import pytest

MOD = pathlib.Path(__file__).resolve().parents[1] / "unirig_intake.py"
spec = importlib.util.spec_from_file_location("unirig_intake_under_test", str(MOD))
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)


def test_gpu_available_returns_bool():
    assert isinstance(ui.gpu_available(), bool)


def test_unirig_root_none_when_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("UNIRIG_ROOT", str(tmp_path / "nope"))
    monkeypatch.setenv("WH_UNIRIG_SKIP_DEFAULT", "1")
    assert ui.unirig_root() is None


def test_unirig_root_found_when_valid(monkeypatch, tmp_path):
    root = tmp_path / "UniRig"
    (root / "launch" / "inference").mkdir(parents=True)
    (root / "run.py").write_text("# stub")
    (root / "launch" / "inference" / "generate_skeleton.sh").write_text("# stub")
    monkeypatch.setenv("UNIRIG_ROOT", str(root))
    assert ui.unirig_root() == root


def test_build_pipeline_commands_three_stages(tmp_path):
    root = tmp_path / "UniRig"
    cmds = ui.build_pipeline_commands(root, "in.glb", "out.glb", tmp_path / "w", seed=7)
    assert [name for name, _ in cmds] == ["skeleton", "skin", "merge"]
    s1 = " ".join(cmds[0][1])
    assert "generate_skeleton.sh" in s1 and "--input in.glb" in s1 and "--seed 7" in s1
    s2 = " ".join(cmds[1][1])
    assert "generate_skin.sh" in s2 and "--data_name raw_data.npz" in s2
    s3 = " ".join(cmds[2][1])
    assert "merge.sh" in s3 and "--source" in s3 and "--target in.glb" in s3 and "--output out.glb" in s3
    # stage 2 consumes stage 1 output, stage 3 consumes stage 2 output
    assert cmds[1][1][cmds[1][1].index("--input") + 1].endswith("skeleton.fbx")
    assert cmds[2][1][cmds[2][1].index("--source") + 1].endswith("skin.fbx")


def test_maybe_autorig_none_when_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv("WH_UNIRIG", "0")
    src = tmp_path / "m.glb"
    src.write_bytes(b"GLB")
    assert ui.maybe_autorig(str(src), tmp_path / "w") is None


def test_maybe_autorig_none_without_checkout(monkeypatch, tmp_path):
    monkeypatch.setenv("WH_UNIRIG", "1")
    monkeypatch.setenv("UNIRIG_ROOT", str(tmp_path / "missing"))
    src = tmp_path / "m.glb"
    src.write_bytes(b"GLB")
    assert ui.maybe_autorig(str(src), tmp_path / "w") is None


def test_maybe_autorig_never_raises_on_bad_input(monkeypatch, tmp_path):
    monkeypatch.setenv("WH_UNIRIG", "1")
    assert ui.maybe_autorig("/does/not/exist.glb", tmp_path / "w") is None


def test_rig_model_rejects_unsupported_suffix(tmp_path):
    bad = tmp_path / "x.txt"
    bad.write_text("not a model")
    with pytest.raises(ValueError):
        ui.rig_model(bad, tmp_path / "o.glb")


def test_check_env_reports_dict():
    ok, report = ui.check_env(verbose=False)
    assert isinstance(ok, bool)
    assert set(report) >= {"wh_unirig_enabled", "unirig_root", "gpu_available", "ready"}


def test_cli_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as e:
        ui.main(["--help"])
    assert e.value.code == 0
