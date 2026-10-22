# Decision log — Tekken 3 pull scope (user 2026-10-22 ~17:30 CDT)

Worker 63. Filed under the teardown priorities per the user's instruction:
docs/decisions/ 2026-10-22 entry + reference from the owner-directives.md
teardown section.

## Owner verbatim (2026-10-22 ~17:30 CDT)

"We won't need Tekken 3 models — too much to decode for bad low-poly quality. But everything else — the moves, the arenas, the menus — from all the other Tekken games, get the models from all those."

## The rule

- **Tekken 3: pull everything EXCEPT character models.** Moves, movesets, arenas/stages, menus, UI, systems, audio — yes. Character models — skip (too much decode effort for bad low-poly quality).
- **All other Tekken games (T5, T6, TTT2, T7, T8): pull everything INCLUDING character models.**

## Notes

- This is a scope carve-out inside the standing 100% Tekken coverage goal (INTEGRATION LAW) — the goal is still every game, every system, backend to frontend; Tekken 3's character models are the single excluded asset class.
- Gon's Tekken 3 moveset for Dorowani stays in scope (moves, not models) — Dorowani's model is a Tripo pull per the display order law.
- Standing reference: `docs/owner-directives.md` → "Tekken 3 scope" bullet (2026-10-22 section, teardown area). Also referenced from `AGENTS.md` (INTEGRATION LAW section).
