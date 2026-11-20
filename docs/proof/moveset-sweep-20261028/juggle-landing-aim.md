# Juggle follow-ups: landing-aimed check and launcher airtime (2026-10-29)

Sweep change (test/e2e/moveset-sweep.page.js):
- reset() restores any broken stage floor first; before this, a floor-breaking launcher dropped later rows to y=-6 and produced fake juggle passes.
- The juggle follow-up aims at the victim's predicted ballistic landing x, and a hit counts only if the victim was airborne when its HP dropped.

Engine fix (game/js/fighter.js): a non-grab launcher now keeps the victim in the air for the move's remaining frames plus its T8 on_hit advantage (the "+34a" form, default 30f), peaking at 1.2 m. Before, the pop landed in about 18f while the attacker needed about 21f to recover, so no launcher could be followed up.

Measured (jin_soul d/f+2, T8 +34a): attacker actionable at frame 23, victim lands at frame 54.

| fighter | rows pass before -> after | juggles (stage-reset baseline) -> now | row regressions |
|---|---|---|---|
| jin_soul | 785 -> 785 | 0/193 -> 71/197 | 0 |
| pantera | 696 -> 696 | 0/34 -> 13/34 | 0 |
| ryuji | 135 -> 135 | 0/14 -> 3/14 | 0 |
| ryuji-rock | 136 -> 136 | 0/14 -> 3/14 | 0 |

Per-launcher results: sweep-jin_soul-juggle.json, sweep-pantera-juggle.json, sweep-ryuji-juggle.json, sweep-ryuji-rock-juggle.json in this folder.
