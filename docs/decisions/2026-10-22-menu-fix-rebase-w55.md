# 2026-10-22 — PR #676 menu-fix rebase resolution (worker 55)

## Context
PR #676 (`worker36/menu-fix`, worker 37) was built to fix the unplayable main menu (unstyled white text boxes, nothing tappable, overlapping text; user playtesting live). By rebase time, main had moved 30 commits (through #688), and the branch was `mergeable_state: dirty`.

## Investigation
- Worker 37's branch `game/index.html` contained literal `\"` and `\n` escape sequences in the `<head>` (verified with `cat -A` on the raw bytes). The three stylesheet `<link>` tags were malformed (`rel=\"stylesheet\"`), so NO stylesheets would load — the branch would have shipped the exact reported symptom.
- Meanwhile main had already merged the substantive fixes: #677 (mainmenu.css was never linked), #687 (data-mm event handlers wired — "fixes untappable menu"), plus LOADSPEED lazy loading, #688 stage-select→fight flow, PSX controls, colorblind CSS.
- The branch's `main.js`/`styles.css` were based on a stale main and destructively reverted: LOADSPEED imports, `stageIntro` screen, photo mode, `#screen-stage` select CSS, PSX control CSS, identity/wh-boot scripts.

## Decision
Rebase by keeping main's implementation (the T8 menu already delivers the owner's specified method) and porting only the branch's genuinely missing, non-conflicting hardening:
1. Inline critical-CSS fallback in `game/index.html` (correctly written).
2. Non-module fallback event binder in `game/index.html` (correctly written; `window.__whMenuBound` guard; toast, not alert).
3. `window.__whMenuBound = true` at EOF of `game/js/main.js` (EOF chosen because the first placement after the data-mm router conflicted in 3-way simulation — #688 changed the adjacent confirm-routing block; the file tail is unchanged base→main).
4. `.wh-main-menu`/`.wh-menu-btn`/`.screen-title`/`.wh-placeholder` CSS block in `game/styles.css` (main's coming-soon screens used these classes with no styles).

Rejected: the branch's wholesale T8-menu replacement (regression + the escape-mangling defect), its stale `main.js`/`styles.css` (would clobber LOADSPEED/stage-intro/PSX/identity), and its `.menu-content` override (main's is better).

## Verification
- Local `git merge-file` 3-way simulation (base `fab3e7d9`, ours = resolved, theirs = main `8af986e0`): all 3 files CLEAN; merged output byte-identical to intended files.
- `node --check` (ESM) on `game/js/main.js`: pass. HTML tag balance script: pass. CSS brace balance: pass.
- Instruction-gate: ran the repo's real `.github/scripts/instruction_gate.py::check()` locally against the rewritten PR body — passes. (Also revealed the old body's failure mode and fixed 9 proof-path issues.)
- CI on rebased head `8c13d1ad`: instruction-gate SUCCESS (run 39859322873); rig-guard success; clobber/deletion/no-deletion guards in progress at decision time.

## Status
Merge-ready; merge HELD per orchestrator MERGE FREEZE (2026-10-22 ~16:37 CDT, 20 min). Do not merge until all-clear. Merge via `git_merge.py` once `mergeable_state` is `clean` and all guards green.
