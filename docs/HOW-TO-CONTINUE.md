# Western Heart — How to continue

Read first: `lab/README.md` (milestones), `docs/PLAYTEST-METHOD.md` (how to play/measure), `docs/QA-FINDINGS.md` (bugs), `docs/WORKLOG.md` (what happened, newest last). Claim in `mhvnsnt/agent-ops` CLAIMS.md before editing; Repo Co Dev owns `lab/game/scripts/*` engine work.

## Rules
- Branch + PR, commit as mhvnsnt, gitleaks before push, merge only when Actions are verified green. Never delete work; edit in place.
- After every change: rerun `godot --headless --path lab/game -s res://tests/qa_playtest.gd | grep '^QA|'` and `lab/game/tests/run_match_headless.sh`; paste the before/after `QA|` lines in the PR.
- Append to WORKLOG.md with a CT timestamp each time you stop.

## Next steps (in order)
1. Bug 1 grab row + throw state; Bug 2 startup mapping (check King T3 row for jab, should be i10).
2. Input buffer + string windows (Bug 3), then f,f dash / b,b backdash (Bug 4) — add scenarios already in the harness to confirm.
3. Launcher → juggle state (Bug 5).
4. Visual: King KMD seams/head (Bug 6), stage pano (Bug 8), separation (Bug 7).
5. Add harness scenarios for crouch/sidestep when implemented; extend comparison table.
6. Teardown inspirations: browser builds / chimera emulator hub are a separate track (PS2 titles barely run in browser); use reference footage + wiki frame data until then.

## No-data-loss rules (MANDATORY)
Read and follow [`docs/NO-DATA-LOSS-RULES.md`](NO-DATA-LOSS-RULES.md) (canonical: mhvnsnt/agent-ops). No force-push, no rebase/amend of pushed work, no history rewrite, no branch/asset deletion without backup + owner approval, PRs only, empty D-filter + gitleaks + green CI before merge, push incrementally, keep WORKLOG, back up and sha256-verify before disk cleanup, never touch other agents' or Muse's work.

## Owner laws (Oct 23, 2026)
- **2:19 PM CT, data sources:**
> **Western Heart data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use is logged with its reason.**
  Search T5/T6/T7/T8/TTT2 teardowns first; log every T3 use (file, clip, reason) in `docs/anim/PROCEDURAL_AUDIT.md` and WORKLOG. Next-step references to King's T3 rows above are fallback-only until a T5–TTT2 source replaces them.
- **2:21 PM CT, no hand-made menus:**
> **NO hand-made menus. Every Western Heart menu, character select and customization screen, including the creation suite in `packages/creation-suite`, must be built from the actual Tekken teardown files (T5/T6/T7/T8/TTT2) and other game teardowns, and every UI change must cite its teardown source in the PR and WORKLOG.**
  CI gate is MoneyManBusch's (no duplicate). Current hand-built creation suite UI is NON-COMPLIANT, pending teardown-sourced rebuild; do not delete it.
## Teardown-integration lane status (Grok Bot, 2026-10-23 15:45 CT)
- Merged: #812 input V2, #821 phone menu touch fix + menu-touch-e2e CI job, #830 select phone layout, #834 ui_sources gate (game/ui_sources.json + tools/ui-sources/check.py). All 14 screens are legacy-unsourced, and changing one now requires a teardown source.
- Open: #831 coverage audit (tools/teardown-coverage/audit.py REF OUT: 27.2% integrated, 31.7% docs-only, 41.0% unreferenced of 51234 files), #835 roster map (node tools/roster-map/build.mjs; 67 owner issues).
- BLOCKER for the menu rebuild and T3 replacement: neither repo has T5/T7/T8/TTT2 menu/UI or move extractions (T6 UI is 2 PSP icons, T6 moves are still being decrypted, and there are no ISOs on the box). Next: extract them (game-reverse-engineering tools such as tekken5/tools/vendor/tim2dump), then cite them in ui_sources.json and rebuild the screens, keeping the old ones as Legacy (off by default).
- The WORKLOG is a conflict hotspot. After each merge, re-merge main into the other open PRs (keep both sides, never force-push).

## Input resolver V2 (2026-10-23 14:15 CT)
Read docs/input/INPUT-RESOLVER-V2.md. Run `node test/input-determinism.test.mjs --report /tmp/r.json` after any moveset/input change; it must print PASS. Next: the 107 long-string cases, 34 duplicate-spelling conflicts, hold-button (`*`) input, DOA 2/4 slots from the DOA4 decode, port to AshLane + Brutal Fist.
