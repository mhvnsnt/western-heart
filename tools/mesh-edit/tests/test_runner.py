#!/usr/bin/env python3
"""tools/mesh-edit/tests/test_runner.py — unit tests, no Blender needed.

Covers: validate_job (pure), build_mesh_job guards (bad op / out==source /
missing source), and run_blender_job's WH_MESH_EDIT_REPORT parsing with a
fake Blender executable.

Run: python3 tools/mesh-edit/tests/test_runner.py
"""
import ast
import json
import os
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MED = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, MED)

from mesh_edit import validate_job  # noqa: E402

import importlib.util as _ilu  # dashed filename: load like run_job.py does
_spec = _ilu.spec_from_file_location(
    "wh_job_mesh_edit", os.path.join(MED, "run_mesh-edit_job.py"))
_runner = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_runner)
build_mesh_job, run_blender_job = _runner.build_mesh_job, _runner.run_blender_job

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (" — " + detail if detail and not cond else ""))


def good_job(tmp):
    src = os.path.join(tmp, "src.glb")
    open(src, "wb").write(b"glb")
    return {
        "job_id": "t1", "source_glb": src,
        "ops": [{"op": "mesh_list"}],
        "out_glb": os.path.join(tmp, "out.glb"),
        "out_report": os.path.join(tmp, "out.report.json"),
    }


def main():
    tmp = tempfile.mkdtemp(prefix="wh-meshedit-test-")

    # 1. validate_job: unknown op rejected
    errs = validate_job({"job_id": "x", "source_glb": "a", "ops": [{"op": "nope"}],
                         "out_glb": "b", "out_report": "c"})
    check("validate rejects unknown op", any("unknown op" in e for e in errs))

    # 2. validate_job: missing mesh on mesh_delete
    errs = validate_job({"job_id": "x", "source_glb": "a", "ops": [{"op": "mesh_delete"}],
                         "out_glb": "b", "out_report": "c"})
    check("validate requires mesh for mesh_delete", any("missing 'mesh'" in e for e in errs))

    # 3. validate_job: good job passes
    check("validate accepts good job", validate_job(good_job(tmp)) == [])

    # 4. build_mesh_job: out == source refused
    j = good_job(tmp)
    j["out_glb"] = j["source_glb"]
    try:
        build_mesh_job(j, tmp)
        check("build refuses out==source", False)
    except ValueError as e:
        check("build refuses out==source", "immutable" in str(e))

    # 5. build_mesh_job: missing source refused
    j = good_job(tmp)
    j["source_glb"] = os.path.join(tmp, "nope.glb")
    try:
        build_mesh_job(j, tmp)
        check("build refuses missing source", False)
    except ValueError as e:
        check("build refuses missing source", "not found" in str(e))

    # 6. build_mesh_job: good job writes job file
    j = good_job(tmp)
    job, job_path = build_mesh_job(j, tmp)
    check("build writes job file", os.path.isfile(job_path))
    with open(job_path) as fh:
        check("job file round-trips", json.load(fh)["job_id"] == "t1")

    # 7. run_blender_job with a fake Blender: parses WH_MESH_EDIT_REPORT
    fake = os.path.join(tmp, "fake_blender.sh")
    with open(fake, "w") as fh:
        fh.write("#!/usr/bin/env bash\n"
                 "JOB=\"\"; prev=\"\"\n"
                 "for a in \"$@\"; do if [ \"$prev\" = \"--job\" ]; then JOB=\"$a\"; fi; prev=\"$a\"; done\n"
                 "OUT=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))[\"out_report\"])' \"$JOB\")\n"
                 "ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))[\"job_id\"])' \"$JOB\")\n"
                 "mkdir -p \"$(dirname \"$OUT\")\"\n"
                 "echo '{\"job_id\":\"'$ID'\",\"ops_applied\":[],\"errors\":[],\"reweight_needed\":false}' > \"$OUT\"\n"
                 "echo \"WH_MESH_EDIT_REPORT {\\\"job_id\\\":\\\"$ID\\\",\\\"ok\\\":true,\\\"reweight_needed\\\":false,\\\"report\\\":\\\"$OUT\\\"}\"\n")
    os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
    os.environ["WH_BLENDER_BIN"] = fake
    logs = []
    report, _ = run_blender_job(job_path, logs.append, timeout_s=60)
    check("fake blender report parsed", report.get("ok") is True and report.get("job_id") == "t1",
          str(report)[:120])

    # 8. both scripts are syntactically valid Python
    for f in ("mesh_edit.py", "run_mesh-edit_job.py"):
        with open(os.path.join(MED, f), encoding="utf-8") as fh:
            try:
                ast.parse(fh.read())
                check("AST parse " + f, True)
            except SyntaxError as e:
                check("AST parse " + f, False, str(e))

    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
