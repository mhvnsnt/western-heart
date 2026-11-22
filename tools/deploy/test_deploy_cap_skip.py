"""Unit tests for the over-cap update skip in tools/deploy/deploy_api.py (2026-11-22).

Run: python3 -m unittest tools/deploy/test_deploy_cap_skip.py   (from the repo root; no network)

The case is the real one: game/data/moveset-library/index.json grew from 2,231 B to 60,249,618 B on main
(f58ef35d) and the github.io shell deploy refused every merge since ("new tree over the 1 GiB cap",
live 1,052,268,267 B, projected 1,112,563,527 B).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deploy_api as D  # noqa: E402


class CapSkip(unittest.TestCase):
    def test_real_case_index_stays_live_and_code_ships(self):
        idx = "game/data/moveset-library/index.json"
        upd = [idx, "game/js/fighter.js", "game/js/stagebreaks.js"]
        live = {idx: 2231, "game/js/fighter.js": 319896, "game/js/stagebreaks.js": 22491}
        main = {idx: 60249618, "game/js/fighter.js": 322416, "game/js/stagebreaks.js": 28571}
        projected = 1_112_563_527
        kept, skipped, after = D.skip_over_cap_updates(upd, live, main, projected)
        self.assertEqual(skipped, [idx])
        self.assertEqual(kept, ["game/js/fighter.js", "game/js/stagebreaks.js"])
        self.assertEqual(after, projected - (60249618 - 2231))
        self.assertLessEqual(after, D.CAP)

    def test_under_cap_nothing_skipped(self):
        upd = ["game/data/moveset-library/index.json"]
        kept, skipped, after = D.skip_over_cap_updates(upd, {upd[0]: 1}, {upd[0]: 2}, D.CAP - 10)
        self.assertEqual((kept, skipped, after), (upd, [], D.CAP - 10))

    def test_never_skips_outside_the_editor_data(self):
        upd = ["game/js/huge.js", "game/assets/movesets/pantera.json"]
        live = {upd[0]: 1, upd[1]: 1}
        main = {upd[0]: 500_000_000, upd[1]: 500_000_000}
        kept, skipped, after = D.skip_over_cap_updates(upd, live, main, D.CAP + 1_000)
        self.assertEqual(skipped, [], "code and fight data are never left stale")
        self.assertEqual(kept, upd)
        self.assertGreater(after, D.CAP, "the deploy still refuses when only non-skippable files are over")

    def test_biggest_growth_first_and_stops_once_under(self):
        a, b = "game/data/moveset-library/banks/a.json", "game/data/moveset-library/banks/b.json"
        live = {a: 10, b: 10}
        main = {a: 1_000, b: 5_000}
        kept, skipped, after = D.skip_over_cap_updates([a, b], live, main, D.CAP + 3_000)
        self.assertEqual(skipped, [b], "the 4,990 B grower alone brings it under; the smaller one still ships")
        self.assertEqual(kept, [a])
        self.assertLessEqual(after, D.CAP)


if __name__ == "__main__":
    unittest.main()
