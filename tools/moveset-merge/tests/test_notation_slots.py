"""Notation twin + slot reading (2026-11-01).

Run: python3 -m unittest discover -s tools/moveset-merge/tests -v

notation.canon must agree with the game's canonNotation (game/js/movesets.js) on what the merge tool slots:
'WR 4' is while-running 4, a twice-escaped just-frame ('1,2,&amp;#58;4') is '1,2:4', and a tilde input ('3~4')
is its own input, never a source tag. tools/moveset-merge/repair_slots.py re-points the slots the old reading
hijacked; test/moveset-slot-hijack.test.mjs guards the data with the game's own canonNotation.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import merge_sources as MS  # noqa: E402
import notation as N  # noqa: E402
import repair_slots as R  # noqa: E402


class CanonTwin(unittest.TestCase):
    CASES = {  # raw -> game/js/movesets.js canonNotation (node, 2026-11-01)
        "WR 4": "WR.4", "WR.4": "WR.4", "wr 4": "WR.4", "WR+4": "WR.4",
        "3~4": "3~4", "4~3": "4~3", "3~3": "3~3", "3~3:4": "3~3:4",
        "1,2,&amp;#58;4": "1,2:4", "4,4,&amp;#58;4": "4,4:4", "1,2,:4": "1,2:4",
        "FC 1": "FC.1", "WS 4": "WS.4", "1, 2": "1,2", "d/f+1, 3": "d/f+1,3", "f,F+2": "f,F+2",
    }

    def test_cases(self):
        for raw, want in self.CASES.items():
            self.assertEqual(N.canon(raw)[0], want, raw)


class NotationOf(unittest.TestCase):
    def test_source_tags_strip_inputs_do_not(self):
        for key, inp, want in [("3~4", "3~4", "3~4"), ("4~3", "4~3", "4~3"), ("3~3~t7.lee", "3~3", "3~3"),
                               ("d/f+1~t7.lei", "d/f+1", "d/f+1"), ("4~t7.jin.2", "4", "4"), ("3~donor.byou", "3", "3"),
                               ("SCR 3,3,4~D", "SCR 3,3,4~D", "SCR.3,3,4~D"), ("f+3__main", "f+3", "f+3"),
                               ("1_t8", "1", "1"), ("1+3_c36", "1+3", "1+3"), ("WR 4", "WR 4", "WR.4")]:
            self.assertEqual(MS.notation_of(key, {"input": inp}), want, key)

    def test_unparsed_string_is_not_its_first_hit(self):
        m = {"input": "(3),4,4)", "input_slots": ["(3)", "(3),4", "(3),4,4)"]}
        self.assertNotEqual(MS.notation_of("(3),4,4)", m), "3")
        m = {"input": "1,2,&amp;#58;4", "input_slots": ["1", "1,2", "1,2,&amp;#58;4"]}
        self.assertEqual(MS.notation_of("1,2,&amp;#58;4", m), "1,2:4")

    def test_legacy_reading_reproduces_the_hijacks(self):
        self.assertEqual(R.legacy_notation_of("3~4", {"input": "3~4"}), "3")
        self.assertEqual(R.legacy_notation_of("WR 4", {"input": "WR 4", "input_slots": ["WR 4"]}), "4")
        self.assertEqual(R.legacy_notation_of("1,2,&amp;#58;4", {"input": "1,2,&amp;#58;4", "input_slots": ["1", "1,2"]}), "1")


class Repair(unittest.TestCase):
    def test_plan_and_rewrite(self):
        cur = {"tekken_base": "Lee", "specials": [],
               "moves": {"1,2,&amp;#58;4": {"input": "1,2,&amp;#58;4", "input_slots": ["1", "1,2", "1,2,&amp;#58;4"]},
                         "1~t8.lee": {"input": "1", "t8_source": "lee"},
                         "BT.1": {"input": "BT.1"}},
               "slots": {"1": "1,2,&amp;#58;4", "BT.2": "BT.1"}}
        rows = R.plan("purplerain", cur, {})
        self.assertEqual(rows, [("1", "1,2,&amp;#58;4", "1~t8.lee")])  # the BT.2 alias is not the old reading's
        text = json.dumps(cur, indent=2)
        after = json.loads(R.rewrite(text, {"1": ("1,2,&amp;#58;4", "1~t8.lee")}))
        self.assertEqual(after["slots"], {"1": "1~t8.lee", "BT.2": "BT.1"})
        self.assertEqual(after["moves"], cur["moves"])

    def test_repo_movesets_need_no_repair(self):
        r = subprocess.run([sys.executable, str(HERE / "repair_slots.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])


if __name__ == "__main__":
    unittest.main()
