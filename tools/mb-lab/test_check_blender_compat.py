#!/usr/bin/env python3
"""test_check_blender_compat.py — proof run for check_blender_compat.py.

    python3 tools/mb-lab/test_check_blender_compat.py

Pure Python. Uses a fake `blender` executable (a shell script that
prints a Blender version line) so no real Blender or MB-Lab vendor
checkout is needed:
  1. Version parsing accepts 4.0.2 / 4.2.3 / 5.2.3 lines.
  2. With no vendor dir, the verdict is "unverified: vendor missing"
     — never a pass, never a fail claim about the Blender version.
  3. With a fake vendor dir (__init__.py present) and Blender >= 4.0,
     the verdict is "candidate" — still NOT a compatibility claim.
  4. With Blender 3.6 and a vendor dir, the verdict is "incompatible".
  5. A non-executable blender path exits 2.
Exit non-zero on failure.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check_blender_compat.py")


def load():
    spec = importlib.util.spec_from_file_location("wh_check_compat", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fake_blender(td, version):
    path = os.path.join(td, "blender")
    with open(path, "w") as fh:
        fh.write(f"#!/bin/sh\necho 'Blender {version} LTS'\n")
    os.chmod(path, 0o755)
    return path


def main():
    mod = load()
    assert mod.parse_blender_version("Blender 4.0.2 LTS") == (4, 0, 2)
    assert mod.parse_blender_version("Blender 5.2.3 LTS") == (5, 2, 3)
    assert mod.parse_blender_version("Blender 4.2.3 LTS") == (4, 2, 3)
    with tempfile.TemporaryDirectory() as td:
        blender = fake_blender(td, "5.2.3")
        # No vendor dir at all.
        r = mod.check(blender, os.path.join(td, "no-vendor"))
        assert r["verdict"].startswith("unverified: vendor missing"), r
        assert r["blender_version"] == "5.2.3"
        # Fake vendor present, Blender >= 4.0 -> candidate, not a claim.
        vendor = os.path.join(td, "MB-Lab")
        os.makedirs(vendor)
        with open(os.path.join(vendor, "__init__.py"), "w") as fh:
            fh.write("# fake\n")
        r = mod.check(blender, vendor)
        assert r["verdict"].startswith("candidate:"), r
        assert "NOT claimed" in r["verdict"]
        # Blender 3.6 + vendor -> incompatible.
        sub = os.path.join(td, "sub")
        os.makedirs(sub)
        old_blender = os.path.join(sub, "blender")
        with open(old_blender, "w") as fh:
            fh.write("#!/bin/sh\necho 'Blender 3.6.0 LTS'\n")
        os.chmod(old_blender, 0o755)
        r = mod.check(old_blender, vendor)
        assert r["verdict"].startswith("incompatible:"), r
        # CLI: non-executable path exits 2.
        r = subprocess.run([sys.executable, CHECK, "--blender",
                            os.path.join(td, "missing")],
                           capture_output=True, text=True)
        assert r.returncode == 2, r.returncode
        # CLI: JSON output parses and carries the unverified verdict.
        r = subprocess.run([sys.executable, CHECK, "--blender", blender,
                            "--mblab-dir", os.path.join(td, "no-vendor"),
                            "--json"], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        out = json.loads(r.stdout)
        assert out["verdict"].startswith("unverified: vendor missing")
    print("PASS: check_blender_compat — version parse, unverified / "
          "candidate / incompatible verdicts, CLI exit codes verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
