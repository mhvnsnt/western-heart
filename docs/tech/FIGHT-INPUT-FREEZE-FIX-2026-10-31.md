# Fight input freeze + stage-select kick — fix record (2026-10-31)

Owner symptoms on the live deployable build (source commit d27629c1):

- (a) 2026-10-31 08:37 CDT: "It's not loading into the fight still kicking me out to stage select after I already selected the stage."
- (b) 2026-10-31 ~09:13 CDT: "the button inputs is like struggling to reach the animations... it's making them freeze up and not do the moves. Like I can't do no combos or certain moves are just like freezing up not playing the animation when I press a button."

## Reproduction (locally served tree of main d27629c1 = the live deploy tree; Playwright, 360x640)

### Symptom (a) — fight load aborts and bounces to stage select

Run repro4-try1, Pantera vs Demonio, stage confirmed:

- roundState stuck at idle, running=false
- pageerror: BodyStreamBuffer was aborted
- console: [WH] fight load failed: AbortError: BodyStreamBuffer was aborted
- The game's own bounce signature followed: the stage confirm button re-enabled with the hint "Failed to load fighters: BodyStreamBuffer was aborted — tap CONFIRM to retry."

Mechanism: a fight's model list (the need array in startFight) contains both fighters' models plus every transformation-form target model. For Demonio that is attire1 model.glb 28,872,600 B + human model-rerig.glb 28,737,644 B + winged-devil model-rigged.glb 19,010,652 B = 76 MB fetched in parallel (plus Pantera's model). The model loader applied a 90 s TOTAL deadline per attempt: any single body that took longer than 90 s to arrive aborted, aborts were never retried, and one model's abort rejected the whole loadModels call — the fight bounced. On a phone connection sharing bandwidth across 76 MB of parallel models, the biggest model is exactly the one that crosses a total deadline. The timeout design and the parallel-forms preload both predate the 2026-10-29..31 delta; nothing in the range changed them.

### Symptom (b) — moves freeze: the animation never starts

Runs burger-try1 and probe2-d27629c1 (Burger vs Pantera):

- Control press 1 (healthy): plan {name "row:172", kind "notation"}, clip t3_bryan_row172@burger plays, phases startup → active → recovery → idle; at idle the current action is t7_burger_stance@burger — the T7 stance system binds and plays in-fight.
- String 3 then 4 (the string "3,4", Croque-Monsieur): console logs [WH-STEP-PLAN] burger 3,4: UNMAPPED steps [3, 3,4] — no bank row played, never donor fallback. The resolved plan is {kind: "step-plan", name: null}. NO animation action starts for the move; the mixer keeps the previous attack's action (t3_bryan_row63@burger) while the attack state machine runs the move's full frame data (startup 0.3 / active 0.017 / recovery 0.5, stateT advancing 0.042 → 0.742 across probes, phases progressing normally). The fighter visibly holds a finished pose for the move's whole 0.817 s — on the phone that reads as the input being ignored.
- The CPU Pantera fired a fully unmapped string in the same run — the path is not Burger-specific. Combos die first because string continuations are the most common unmapped step plans.
- A related observation (runs pantera-try1, pantera-try2): Pantera as P1 resolved plans correctly (her "1" → row:110) but her _t3current read null at idle and mid-attack even though her bank binds (console: "Fighter pantera: 22 real T3 actions from bank 'king' (retargeted onto pantera-leoman)") and her king pack is complete (36 files, byte-list identical to the live tree). Her T7 stance is rejected by the stance-fit check ("bank 'king' stance does not fit pantera's rig (Left shoulder swung 0.69 rad from bind) — falling back"), as is Burger's bryan stance (1.08 rad) in some runs, while in the probe2 run Burger's T7 stance did play. This stance-fit/current-action inconsistency is recorded here as an open thread for the stance lane; it is not one of the two mechanisms fixed by this PR.

## Bisect

Local git tree diff of game/js between main 05c5e851 (last owner-good era) and d27629c1 (deployed): the ONLY change is game/js/t3anims.js +27/−1 — the T7_STANCES table growing 1 → 16 entries (PRs #1368, #1371). fighter.js, step-plan-bank.js, combat-core.js, movesets.js and the moveset JSONs' code paths are byte-identical; the rest of the range is moveset JSON data (F6 throw repicks, provenance corrections) and docs/tools. The T7 stance delta is CLEARED for both symptoms by the reproduction evidence: the stance system binds and plays in-fight (symptom (b) control), and neither failure mechanism lives in t3anims.js — the loader timeout lives in assets.js and the null-plan presentation in fighter.js, both unchanged in range. (The GitHub compare API was not used for the bisect: its file list caps at 300 entries and misleads; the tree diff is authoritative.)

## The fix (this PR)

### game/js/assets.js — stall timeout + retry (symptom (a))

- The 90 s total deadline is replaced by a 45 s NO-BYTES stall watchdog: a per-attempt AbortController re-armed on every received chunk. A load still receiving bytes is alive however slow; only a load that receives nothing for 45 s is treated as hung and aborted.
- A failed attempt is retried once — including aborts — UNLESS the caller cancelled (ctrl.signal.aborted: preview-tap supersede and idle-warm preemption still fail fast, never retry). The old code rethrew every AbortError instantly, which is what turned one slow model into a bounced fight.
- Verified engaging in fixed-tree runs: "[WH] pantera load failed, retrying: no bytes received for 45000ms loading pantera".

### game/js/fighter.js — unmapped step plans present a real animation (symptom (b))

- New module helper genericBankAction(bank, clips, limb, grab): the bound bank's own generic action for the limb — grab for a throw, else the light/medium/heavy action whose strike profile matches the limb — the identical last-resort tier the main _attackClipPlan path already uses for moves with no specific clip. Generic actions are the bank's own decoded attack motions, never another move's row and never another bank's clip.
- In _attackClipPlan's step-plan branch, when the plan is unmapped (or its override bank/row is unavailable), the move now presents with that generic action (with hit-window timing built from the move's own frame data) instead of returning name: null. The step-plan contract stands — no bank ROW is ever substituted; the UNMAPPED console log stays, so the data gap is reported, not hidden.
- In the attack presentation branch, when no clip owns the attack, the previous attack's finished T3 action is released (_stopT3()) before the procedural fallback runs, so a clip-less move animates from a clean pose instead of the stale clip staying "current" for the move's whole duration.
- The newer REAL T7 MOVE tier on main (a row's own Tekken 7 clip resolving ahead of step plans) is untouched and still wins wherever a T7 clip exists; this fallback only covers moves that reach the step-plan branch without one.
- fighter.js in this PR is main + 61 lines, zero lines removed (verified by diff against main at the PR base).

## Named unmapped moves observed (data gaps — reported, not hidden)

- Burger "3,4" (Croque-Monsieur): both steps unmapped in burger.json string_step_plans (step "3" candidate row 65 is recorded SUSPENDED-DRIFT — never wired on stale data; step "3,4" unmapped). These need real step rows from the provenance/step-plan lanes; until then the move plays the bank's generic presentation above.
- Pantera: at least one full string fired by the CPU in probe2-d27629c1 was fully unmapped (the run's log line: [WH-CPU-STRING] pantera fired [1] (full string unmapped — legacy path)). Her string_step_plans coverage is the data lane's queue.

## Environment notes (verification conditions)

- Chromium on the lane VM cannot reach the live site (egress proxy TUNNEL failure), so all runs used a locally served tree, per the lane brief.
- The VM's stock python http.server repeatedly dropped large-file bodies mid-transfer (the same BodyStreamBuffer abort signature) and once stalled a 7.7 KB module body after logging 200, which left Game.start() waiting on its fighter-depth dynamic import with roundState at idle. Verification serving was moved to a node static server (28.9 MB file delivered in 1.15 s) to remove the server as a variable. Neither behavior exists on the real host (GitHub Pages).
- Headless swiftshader on this contended VM runs the game at a small fraction of real speed (a 0.5 s jab taking ~78 wall-s; full construction taking 10-20 wall-min). State/phase progression, not wall time, is the evidence standard in every run above.
- Fixed-tree verification and the post-republish acceptance run are recorded in the lane checkpoint (agent-ops checkpoints, fight-input-freeze-20261031) and summarized in the PR thread; the acceptance battery is the same harness: fight starts, every attack button produces its animation, strings chain, one full round to KO, console/pageerror log and a fight screenshot saved under the user's files.
