# COMPLETE WIRING LAW (owner 2026-10-23, t218 — permanent, all agents)

Owner: "make sure everything's 100% wired up ... so I don't have to sit here and name every specific system and every part ... and then start doing that for all the other games too ... push all of your work so none of it gets held hostage when you hit your limit ... let all the other agents know."

## The rule
1. Everything pulled from Tekken (T3/T5/T6/TTT2/T7/T8) and from every other game in `mhvnsnt/game-reverse-engineering` must end up 100% wired into Western Heart where it fits. The owner does not name systems or parts. Agents audit, find the gaps, and fix them.
2. The inventory is `docs/tech/SYSTEMS-COVERAGE.md` (data: `tools/coverage/systems-coverage.json`). Every pulled system has a row. New pulls add a row in the same PR.
3. Claim a `not-wired` / `partial` row on issue #866 before working it. One PR per system. Don't duplicate a claimed lane.
4. Tekken + Western Heart is the base; other games are extensions inside the Tekken structure (INTEGRATION LAW). Canon names via `tools/canon`. Raw assets stay private and load via `__WH_PRIVATE_ASSETS`.
5. Coverage may only go up. CI `coverage-guard` fails if a row is removed or its status drops.

## Definition of "wired" (all four, per system)
- **Data loaded** — the game reads the pulled data (private pack or derived public table), not a placeholder.
- **Used in gameplay** — a player can trigger it in a real match/menu (e.g. a move fires from its input and makes contact; a hit plays its reaction).
- **Tested** — a `test/*.test.mjs` (run by game-checks) exercises it and would fail if unwired.
- **Visible proof** — screenshot/clip/test log at 390x844 and 844x390 under `proof/`, linked in the PR.

Anything short of all four is `partial`.

## Push-often rules (nothing held hostage by a usage limit)
- Commit and push at least after every system, or about every 30 minutes, whichever comes first. WIP commits on the feature branch are fine.
- Before any long job (extraction, batch re-rig, big refactor) push a backup branch `backup/<lane>-<date>` first.
- Open a draft PR early so work is visible; never leave work only on a box (see CLAUDE.md "Never strand work").
- Standing rules still apply: gitleaks before push, instruction-gate PR template, no force-push/rebase/amend/file deletion, merge only clean + all Actions green + `--diff-filter=D` empty.
