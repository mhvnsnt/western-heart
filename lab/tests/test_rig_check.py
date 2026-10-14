"""Automated rig check (run: python3 lab/tests/test_rig_check.py). Fails if any Lab fighter GLB has
bones/weights/mesh/animation disagreement, exploded vertices, or feet off the floor."""
import glob, sys, unittest
from pathlib import Path
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import rig_check

class RigCheck(unittest.TestCase):
    def test_lab_fighters(self):
        files = sorted(glob.glob(str(LAB / "game/assets/t3_*.glb")))
        files = [f for f in files if "stage" not in f]
        self.assertTrue(files, "no Lab fighter GLBs found")
        for f in files:
            r = rig_check.check(f)
            self.assertTrue(r["pass"], f"{f}: {r['errors'][:5]}")
            self.assertLessEqual(r["stats"]["max_edge_stretch"], 1.01, "rigid T3 parts must not stretch")

    def test_detects_broken_rig(self):
        """The checker must catch a known-bad rig (Mixamo cm-scale Idle on a metre rig)."""
        bad = LAB.parent / "game/assets/models/pantera.glb"
        if not bad.exists(): self.skipTest("pantera.glb absent")
        r = rig_check.check(bad)
        self.assertFalse(r["pass"])
        self.assertTrue(any("exploded" in e or "floor" in e for e in r["errors"]))

    def test_importer_reproducible(self):
        import subprocess, tempfile, hashlib
        repo = LAB.parent; out = Path(tempfile.mkdtemp()) / "k.glb"
        subprocess.check_call([sys.executable, str(LAB / "tools/t3_to_gltf.py"), "fighter",
            str(repo / "teardown/tekken3/models/king95/king95.kmd"), str(repo / "teardown/tekken3/renders/pose-check/king_stance75.obj"), str(out)], stdout=subprocess.DEVNULL)
        r = rig_check.check(out); self.assertTrue(r["pass"], r["errors"][:5])

if __name__ == "__main__":
    unittest.main(verbosity=2)
