> Before touching any model, rig, or animation: read ASSET-PIPELINE.md. Prove with renders you looked at.

# AGENTS.md

> **PIPELINE LAW (2026-11-05):** read `docs/PIPELINE-LAW.md` before OpenKumite / FightingEngine / moveset-template / Pantera / first-play camera-debris work. FE source private until 2026-12-25 — do not hunt leaks. Tag Battle demo chars and WWE superstar names never go on the WH roster. Pantera = exact King T7 via template `t7-grappler-jaguar-mask`.


# ANTI-CLOBBER LAWS (owner 2026-10-17 — the DXMMII 54k-file wipe)

On 2026-10-17, commit cd3bf38 ("DXMMII limb system", PR mhvnsnt/western-heart#221) deleted 54,456 files against 105 additions. The commit message said nothing about deletions. Nobody read the deletion list before merging. The repo was 99.996% gone. These laws exist so that never happens again. Every agent, every repo, every commit, every merge.

1. DELETION CHECK — before every commit, read `git status` and the diff stat. Every deleted file in the diff must be something your task intended to delete. A deleted file your task did not delete on purpose means STOP: do not commit, do not push, report what you found. The working tree is wrong, not the task.

2. OWN THE TREE — never `git add -A` or `git commit -a` in a working tree you did not fully populate yourself. Before committing, verify the tree is complete: file counts match the remote branch you branched from (your task's own additions and changes aside). A tree missing files you didn't delete is damaged — don't sweep it into history.

3. CIRCUIT BREAKER — if a commit would delete more than a handful of files outside your task's scope, STOP and report instead of committing. A big deletion count is a hard stop, not a warning to scroll past. Committing unexplained deletions "and letting someone else figure it out" is the failure.

4. SAY THE DELETIONS — the commit message names every deletion. One deleted file gets one line; many deleted files get a count plus what category went. A commit whose message and diff disagree is a hard failure — don't push it.

5. MERGE GATE — the merger reads the PR's deletion list against the task description before merging. Unexplained deletions block the merge. "CI is green" does not excuse a deletion list the task never asked for. A red, conflicting, or lossy PR stays open with a comment naming the blocker.

(Co-authored with Aider and Copilot per the ALL-AGENTS-WORKFLOW LAW. Cline's seat stays open — its free-tier API was down during drafting.)

Read by Codex-style and other coding agents automatically.

---

## INTEGRATION LAW (owner 2026-10-22 — permanent)

Everything pulled into the game wires INTO the Tekken menu/system structure as submenus and subsystems — never bolted-on random menus, never extra systems piled on top, never parallel systems competing with Tekken's structure. Tekken is the architectural authority for layout, menus, flow, everything; new work follows the Tekken teardown files' direction. End goal: 100% Tekken coverage — every game, every system, backend to frontend. Full law: `docs/owner-directives.md` (INTEGRATION LAW section). Tekken 3 carve-out: pull everything EXCEPT character models (T5/T6/TTT2/T7/T8 include models) — `docs/decisions/2026-10-22-tekken3-scope.md`.

## Owner's Agent Working Standard (mandatory, all agents)

Full standard: https://github.com/mhvnsnt/money-machine-hq/blob/main/docs/AGENTS.md. Read it before working here. The short version:

1. Do exactly what was asked. Ask when it's ambiguous. Never quietly swap in a cheaper or placeholder approach; call it out.
2. No faked progress. No "done/PASS/verified" without proof (PR link, test output, frames/screenshots you actually viewed).
3. Feature branch + PR for everything. **Never push WIP to `main`.** Merge only if it merges cleanly, CI passes, and it deletes/breaks nothing on main; otherwise leave the PR open.
4. Run gitleaks before every push. No secrets or personal info.
5. Build on existing work; don't redo or overwrite it. Finish before going wide.
6. Report failures first and honestly.
7. Owner's interests first: his money, his time, no advertising of unfinished games.
8. No copyrighted/leaked game files or third-party logos in public repos or Pages.
9. **Edit in place:** a fix or edit means opening the SAME existing project/file and changing it, with a git commit per change. Never regenerate from scratch unless asked. Keep one canonical project per work item at a documented path, with editable sources (EDLs, timelines, scripts, asset lists) next to renders.
10. **Log your workflow** in `WORKLOG.md` or `docs/workflows/`: what you did, the tools and settings, and the file paths.
11. Media deliverables follow Producerbot's `media-proof-standard` skill (check frames actually viewed; UNKNOWN is never PASS).

Self-check before saying "done": asked-scope met · shortcuts disclosed · proof attached · on a branch/PR · CI green · gitleaks clean · nothing copyrighted made public.

## No guessing (owner law)

**Read [docs/RULES_NO_GUESSING.md](docs/RULES_NO_GUESSING.md) before any animation, pose, model or data work.** Never hand-make, procedurally generate or guess when teardown/owned data exists; search the teardowns, decoded files and all repos first; log every source; report missing sources instead of faking; prove real bytes. Current audit: [docs/anim/PROCEDURAL_AUDIT.md](docs/anim/PROCEDURAL_AUDIT.md).

## Muse training pack
Muse/Ashes and every agent: read the [Muse training pack](https://github.com/mhvnsnt/money-machine-hq/tree/main/docs/muse-training-pack) (instructions, pre-flight checklist, real before/after examples, right-way videos) before every job.


## Sale status (owner rule, Oct 14, 2026)

No game is on a commercial or sale track until the owner explicitly says "I'm going to sell this," even if earlier docs say it is being made to sell. Until then, agents must not withhold, water down, or refuse requested work because it might affect publishing or sale readiness. Sale-readiness rework (rescanning or replacing third-party-derived content) happens only after the owner declares a sale.

## No-data-loss rules (MANDATORY)
Read and follow [`docs/NO-DATA-LOSS-RULES.md`](docs/NO-DATA-LOSS-RULES.md) (canonical: mhvnsnt/agent-ops). No force-push, no rebase/amend of pushed work, no history rewrite, no branch/asset deletion without backup + owner approval, PRs only, empty D-filter + gitleaks + green CI before merge, push incrementally, keep WORKLOG, back up and sha256-verify before disk cleanup, never touch other agents' or Muse's work.


## MERGE-IT-YOURSELF LAW (owner 2026-10-15)
"Stop leaving things open for me to merge... I don't like to manually handle PRs."
When a PR satisfies ALL merge conditions (GitHub says MERGEABLE, CI green, no-deletion guard clean, gitleaks clean, build passes), MERGE IT — do not leave it open for the owner. He does not want to manually handle PRs.
The merge must be CLEAN and NON-DESTRUCTIVE: merge commits, never rebase/squash/force-push; resolve conflicts by keeping both sides' work — nothing lost, nothing clobbered, nothing destroyed on either side. Verify the merged result still builds and passes tests before calling it done.
A PR that is red, conflicting, or would lose work stays OPEN with a comment naming the blocker — but the default for a clean, green PR is MERGE, never "leave it for the owner."
Carve-outs (standing owner decisions, not overridden): never merge a DRAFT PR; never merge a PR the owner explicitly excluded.

## NO FAST-AND-LAZY LAW (owner 2026-10-23)
"Fast and lazy on purpose" is banned. Speed that breaks main costs the owner more than it saves. Done means PLAYED, not pushed: sync to latest main, surgical edits only, read your own diff and deletion list, run `node --test game/tests/*.test.mjs`, start a real fight with `tools/proof-harness/fight.mjs` (must reach `"round":"fight"` with no `[pageerror]`; look at the frames), and put the proof you viewed in the PR. Never wire an unskinned static as a fighter's playable slot: rig on intake with `--facing` read from renders. Real breakages and the right way: [docs/handoffs/CLAUDE_TO_CREW_2026-10-23.md](docs/handoffs/CLAUDE_TO_CREW_2026-10-23.md).


## INSTRUCTION GATE: Owner law, data source priority (Oct 23, 2026, 2:19 PM CT)

> **Western Heart data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use must be logged with the reason no T5/6/7/8/TTT2 source was available.**

- Search T5/T6/T7/T8/TTT2 teardowns first. Use T3 only when none of them has the data, and log the T3 use (file, clip, reason) in `docs/anim/PROCEDURAL_AUDIT.md`.

## OWNER LAW — no hand-made menus (Oct 23, 2026, 2:21 PM CT)
> **NO hand-made menus. Every Western Heart menu, character select and customization screen, including the creation suite in `packages/creation-suite`, must be built from the actual Tekken teardown files (T5/T6/T7/T8/TTT2) and other game teardowns, and every UI change must cite its teardown source in the PR and WORKLOG.**
- CI gate is being landed by MoneyManBusch; don't build a duplicate.
- The existing hand-built creation suite UI in `packages/creation-suite` is NON-COMPLIANT, pending a teardown-sourced rebuild. Do NOT delete it.
- See `docs/RULES_NO_GUESSING.md` and `docs/HOW-TO-CONTINUE.md`.

## OWNER LAW — work order: finish whole playable fighters, short jobs first (owner 2026-10-31)

> "the ones that are T-pose and they have a simpler moveset that don't have extra added canon moves that just take their moves straight from the Tekken character or DOA character or KOF character or ... VF5 character or Urban Reign character straight from them ... those are the ones to go ahead and knock out first ... then do the long jobs later"
> "step by step getting each playable thing done that the player would experience at a time so when I go play the deployable build it feels actually more complete than if we were doing a bunch of unrelated mechanics and unwired things at a time"
> "if he starts taking too long you can get to a point where you can checkpoint where you can push it and merge it and then pause on him and then work on the ones that can get done more efficiently"

1. **Short jobs first.** A fighter is a short job when its model is in a T-pose AND its moveset comes straight from ONE source character (Tekken, DOA, KOF, VF5, Urban Reign, ...) with no extra canon moves. Examples: Pantera (King), Purple Rain (Lee), Negativo (Negan).
2. **Long jobs later.** These are long jobs: A-pose models (the skeleton must be fitted to the pose before weighting), size/form transformations, and canon extra moves or mixed movesets. Examples: Burger (Bob + Kusaregedo moves per form + many forms, A-pose model) and Deathfang (Iori + werewolf moves).
3. **Finish one fighter to playable before starting the next.** For each one, cover the model/rig (no stretched skin, no cone face, faces the right way), stance, moves, animations, inputs, and the live deploy. Every step must be something the player sees in the deployed build. Don't ship unrelated mechanics or unwired pieces.
4. **Checkpoint long jobs.** When a long job runs long, push and merge a clean checkpoint, write where it stands in the handoff, then switch to a short job. Return to the long job later.
5. **Log the sequence.** Keep the per-fighter job order and status in `docs/handoff/` (current: `HANDOFF-CLAUDE-2026-10-31.md`, "Work order").

## OWNER LAW — build it like the real game, play it like the player (owner 2026-10-31)

> "use the real game code to understand how to set stuff up and use the real game code to actually set a good template base and then build all the other stuff on top of it ... not like how the games that were inspired by its code would do it ... y'all start doing s*** like guessing not like an actual video game would do it and not like a user would enjoy ... you don't even try and play the game like the player or the user that's going to be enjoying the game so y'all don't even be making the interface user friendly"
> (about the FREE CAMERA button) "that's always covering up stuff ... the main menu and the character select menu and in the fight in the arena select ... should only be there where it's appropriate or in the settings menu"

1. **Real game code is the template.** Before building a screen, menu, camera, HUD element, input or system, find how the source games do it (Tekken 7/8/TTT2 teardowns in GRE, the vendored game code, teardown docs) and build on that structure. No invented flows, no guessed layouts (see also the ui_sources gate and RULES_NO_GUESSING).
2. **Nothing free-floats over menus or the HUD.** Dev/extra tools (free camera, photo, debug, editors) live where real fighting games put them: behind PAUSE, in OPTIONS, or in a dedicated mode. A fixed overlay button that shows on every screen is a bug. Example fix: FREE CAMERA moved into the fight's pause menu (game/js/menus.js, free-camera.js, test/free-camera-placement.test.mjs).
3. **Play it like the player before you call it done.** Open the build at phone size, go menu -> select -> stage -> fight -> pause -> results, and look at what you changed up close (tools/anim/t7_closeup_probe.mjs for fighters). If you would not enjoy it as a player, it is not done.
4. **See what the owner sees.** Describe visual problems by their real cause (skin weights, bone weights, bind pose, facing, retarget), not as "hard to make out". Judge rigs from close-ups, never from a distant fight camera.

## OWNER LAW — rigs fit the body, tools land in the repo (owner 2026-10-31 / 11-01, Negativo re-rig)

> "you got to get that cone face fixed fixed universally" / "make sure all those tools like the heat mapping and everything ... is getting put into the repo don't just use it and keep it to yourself and hold it hostage put everything in document everything into the repo"

1. **Fit the skeleton to the body's landmarks, never to the mesh's total height.** Hair, hats, horns and crests make a mesh taller than its body; a height-scaled template then puts the chest bones in the face (cone face), the arms above the arms (crushed arms) and the hip joints in the belly. Use `tools/auto_rig/refit_rig.py` (T-pose models): arms, armpits, wrists, crotch, knees, throat and chin are measured on the mesh.
2. **Never hard-cut skin weights to 4 bones.** Neighbouring vertices then keep different 4th bones and tear on every move. Use the continuous limit (`seam_safe_smooth.top4`, `smooth_weights.limit4`).
3. **UV-seam copies of a vertex must carry identical weights**, or the seam cracks open in motion (no stretch metric sees it). Check with `tools/auto_rig/rig_inspect.py seams`.
4. **Hair and anything resting on the shoulders fades onto the Head bone geodesically** (`tools/auto_rig/head_territory.py`); a hard head region tears it.
5. **A replacement model keeps the replaced model's height**: the game renders a GLB at its own size (`bodyScale` defaults to 1). `heat_rebind.py --height`.
6. **Judge a rig in motion**: `tools/anim/t7_attack_probe.mjs` freezes real moves at their active frames (front + side) with `NO_REMOTE=1`, because the live game loads models from B2 first; a model fix is live only after the B2 copy is replaced.
7. **Every tool, probe and diagnostic used to fix the game is committed under `tools/`** (with its findings in the tool's docstring / README and the handoff doc) in the same PR as the fix. Nothing used once and thrown away.

## OWNER LAW — no source-game character names; fighters by their Western Heart names (owner 2026-11-01)

> "Bryan Fury should not appear in our game ... you got to stop calling them the names of their models from the Tekken games ... log that into the repo and the agents MD so everyone stops getting confused" / "there is a j i n character, Jin, he's one of the nine Soul Spirit characters, he's just not Jin Kazama"

1. No Tekken / teardown character name anywhere a player can see it (menus, select, roster, HUD, move names, bios, banter).
2. Our fighters are called by their Western Heart names only: never "Bryan" for Skull, "Lee" for Purple Rain, "King" for Pantera, in UI, docs, PRs, commits or chat. Name a source character ONLY when the topic is getting its data over (extraction / conversion); recorded provenance cites the source DATA (`brymot.json`, T7 code `bry`), never as the fighter's identity.
3. A teardown model is a placeholder to build on until it is completely re-skinned and recreated through our customization / creation suites so it no longer looks like the source character (why almost every fighter has a GLB replacement model).
4. JIN is one of the nine Soul Spirit characters (`jin_soul`), NOT Jin Kazama. Jin Kazama does not exist in Western Heart; the fighter built on his data is DEMONIO. Never call Demonio "Jin".

Full rule: `docs/rules/NO-SOURCE-CHARACTER-NAMES.md`.

## NO-SPARSE-COMMIT LAW (owner 2026-10-23 — the cape-jones #219 main wipe)

On 2026-10-23, cape-jones PR #219 wiped main: the merge was built from a sparse/partial checkout, so the commit carried only the partial tree and main lost everything outside it.

1. NEVER commit or push from a sparse/partial checkout. A partial working tree committed as a full tree is a wipe.
2. Before ANY commit from a non-full clone, verify the working tree against the branch's real tree: diff the root listing, or compare tree SHAs. If they don't match, stop — do not commit.
3. Default recovery path for a bad merge: revert the merge commit (`-m 1`) and re-add the branch's real payload. Never "fix forward" on top of a wiped tree.
4. When in doubt, build the commit via the Git Data API from verified tree SHAs — never from a working tree you haven't verified.
5. GOTCHA: `gh`'s `-f content=@file` does NOT expand `@file` for the blobs API — base64 the content explicitly.

## OWNER LAW: ui_sources gate (t123u, Oct 23 2026)
> **Every menu screen must list the exact Tekken/teardown file it came from. Any menu change without that source is blocked from merging, whichever agent made it.**
- The manifest is `game/ui_sources.json`. Each `<section id="screen-*">` gets `{status, sources[], files[]}`. A source is a `teardown/...` path in this repo or `gre:<path>` in game-reverse-engineering.
- The gate is `.github/workflows/ui-sources.yml`, which runs `tools/ui-sources/check.py BASE HEAD`. It FAILS when a new screen, changed `<section>` markup, or a changed UI file (index.html, game/*.css, *menu*/*-screen*/*-ui*/ui-* js, game/ui/**, creation-suite UI) has no existing teardown source. It also fails when a changed UI file isn't listed under some screen's `files`.
- `legacy-unsourced` marks the pre-law hand-made screens. They are grandfathered only while untouched. To change one, first rebuild it from a teardown source and cite that source.
- Make this check **required** in branch protection (owner setting).

## Never strand work locally — push early, push often (owner rule, 2026-10-23)
Applies to Muse, Claude, Grok and every agent. Usage limits and crashes have left finished work
(e.g. a 16-rig batch) stuck on one agent's disk. So: commit + push every finished piece immediately;
commit any script/tool used to generate assets under `tools/`; open the PR right after the first
commit; follow the merge rules (clean merge, every check green via the Actions runs API, no
deletions, nothing frozen, no batch merges). On resume, first push anything left over, then
reconcile with other agents' branches via agent-ops `CLAIMS.md`. Claude Code also has an automatic
safety net: `.claude/settings.json` hooks → `tools/agent/autosave.sh` (see `CLAUDE.md`). Other agents
may run it by hand: `bash tools/agent/autosave.sh manual`. `wip(autosave)` commits are allowed.

## Owner rules — 2026-10-23 (disk offload + merge rule) — Repo Co Dev

**(a) Disk offload.** Once local work is verified 100% pushed (0 dirty, 0 untracked, 0 stash, every local branch on the remote at the same or a later SHA, submodules included) or stored in box-storage, clear it off the box disk as you go, and log each removal (path, repo, HEAD SHA, date) in agent-ops `BOX-OFFLOAD-LOG.md`. If any check fails or ownership is unclear, keep it on disk and list it.

**(b) Merge rule.** Merge only when GitHub shows the PR as MERGEABLE/CLEAN, every check is verified green through the Actions runs API (a timeout, 403 or unreadable result counts as a FAIL), `git diff --diff-filter=D --name-only origin/main...HEAD` is empty, and the PR is not freeze-marked. No batch merges: one PR at a time. Claim the work in agent-ops `CLAIMS.md` first. Never force-push or rebase pushed work. If any check is unverifiable, leave the PR open.

## Team workflow — Tekken data sources
Where the Tekken 7/8 data comes from and how any agent pulls it (T8 movesets, T7 frame data, owner's Steam T7 files, HUD/announcer): `docs/team/TEKKEN-DATA-SOURCES.md`.


## COMPLETE WIRING LAW (owner 2026-10-23 — permanent)

Everything pulled from Tekken and every other game must be 100% wired in without the owner naming each system; agents audit and fix it themselves, claim rows on #866, and push at least every system / ~30 min. Full law: `docs/rules/COMPLETE-WIRING-LAW.md`. Inventory: `docs/tech/SYSTEMS-COVERAGE.md`.


## Main protection law (2026-10-23, after PR #498)
main is branch-protected with required checks (pr-safety-guard, clobber-guard, deletion-guard, no-deletion-guard, instruction-gate), admins included. Never merge with pending or red checks, never resolve merges in a sparse checkout, never self-apply `owner-approved-deletion` / `owner-approved-stale`. Full rules: `docs/rules/MAIN-PROTECTION.md`.
## Handoff playbook (2026-10-23)
All agents (Claude Code, Muse, others): follow [docs/handoff/HOW-TO-WORK-LIKE-GROK.md](docs/handoff/HOW-TO-WORK-LIKE-GROK.md) and the lane table in [docs/handoff/HANDOFF-2026-10-23.md](docs/handoff/HANDOFF-2026-10-23.md).

## Team workflow — Tekken data sources
Where the Tekken 7/8 data comes from and how any agent pulls it (T8 movesets, T7 frame data, owner's Steam T7 files, HUD/announcer): `docs/team/TEKKEN-DATA-SOURCES.md`.


## COMPLETE WIRING LAW (owner 2026-10-23 — permanent)

Everything pulled from Tekken and every other game must be 100% wired in without the owner naming each system; agents audit and fix it themselves, claim rows on #866, and push at least every system / ~30 min. Full law: `docs/rules/COMPLETE-WIRING-LAW.md`. Inventory: `docs/tech/SYSTEMS-COVERAGE.md`.


## Main protection law (2026-10-23, after PR #498)
main is branch-protected with required checks (pr-safety-guard, clobber-guard, deletion-guard, no-deletion-guard, instruction-gate), admins included. Never merge with pending or red checks, never resolve merges in a sparse checkout, never self-apply `owner-approved-deletion` / `owner-approved-stale`. Full rules: `docs/rules/MAIN-PROTECTION.md`.

## Team workflow (multi-agent, t141u)
- Rules + lanes: `docs/AGENT-TEAM-PROTOCOL.md`
- Backlog any agent can pull (claim by setting owner + branch): `docs/team/TASKBOARD.md`
- Hitting a limit / resuming / reconciling parallel branches: `docs/team/HANDOFF.md`
- Free tools + CI/hosting to keep work going 24/7 at $0: `docs/team/FREE-RESOURCES.md`

## SELF-IMPROVE KIT — WIRED IN (2026-11-16, owner order WIRE-IT-EVERYWHERE)

The see-better / think-better / work-better kit's canonical home is mhvnsnt/physics-playground-pwa, `docs/build-a-bitch/tools/self-improve/` (visual QA, source verification, lane-ops guards, reference library). This repo uses the same methods and the same kit — appended additively 2026-11-16, nothing above was rewritten or deleted. Do not fork the kit into this repo; improvements land in the canonical home and this repo points at it.

## SELF-IMPROVE METHODS (2026-11-16 — method rules under the HIGHEST-STANDARD BAR order, not owner-word laws; the tools live in mhvnsnt/physics-playground-pwa, docs/build-a-bitch/tools/self-improve/ (canonical in-repo home; working mirror at ~/workspace/agent-ops/self-improve/))
These fix the exact failure modes the owner named on 2026-11-16 ("running me in circles"): search-only research, lanes re-briefed from the top, process reported instead of proof, lists instead of wired work. The scripts are the enforcement; the rules are the requirement.

### EVIDENCE-LABEL LAW
Every research source carries exactly one label, in those words:
- **FETCH-VERIFIED** — bytes were fetched in this run (or `git ls-remote` answered). Size + sha256 recorded in the verify log.
- **SEARCH-VERIFIED** — page text was seen, but no artifact bytes were pulled. Never ranked as pullable, never presented as "we have it."
- **UNVERIFIED** — fetch failed. The exact error is recorded. Never enters a ranked list.
- **BROWSER-GATED** — needs a live-browser check (login, JS, download button). Goes on BROWSER-QUEUE.md, never left "unverified" forever.
A source enters a ranked list ONLY as FETCH-VERIFIED with a licence verdict present. No verdict → NOT-RANKABLE. The tool is `research-verify/verify_sources.py` — a lane that ranks a source without running it (or without the verify log) has not verified it.

### VERIFY-LATER-QUEUE LAW
A 429, 5xx, timeout, or DNS failure is recorded as RETRY-LATER with the exact error and queued in `verify-queue.jsonl` — then re-run with `--retry-queue` after a pause. "Re-fetch later" written in a report with no queue file and no retry is not a plan, it is a dropped source. Search-verified is the ceiling for a queued source until the retry lands.

### BROWSER-QUEUE LAW
When a check needs the live browser (Mixamo downloads, login-gated pages, JS-only buttons), the lane writes the exact URL + what must be confirmed into the workdir's `BROWSER-QUEUE.md` and flags it to the parent in its report. The parent runs browser checks; the lane never claims the site is down from a fetch error alone, and never leaves the item UNVERIFIED forever.

### RESUME-BRIEF METHOD
A successor lane is briefed from the checkpoint, never from the top. The writer of a resume brief MUST: (1) quote the checkpoint's exact next step verbatim; (2) count the disk state themselves (file/frame/cache counts — never the dead lane's numbers); (3) list what is DONE and forbidden to redo. Template: `lane-ops/resume_brief.md`. If the checkpoint is missing or stale, the first step is re-establishing it from disk — not re-briefing the whole task.

### VISUAL-QA-BEFORE-CLAIM LAW
No visual claim ("matches source," "fixed," "identical," "changed") without a deterministic check run first:
- Pair claims (before/after, orig/served): `visual-qa/pair_compare.py` with `--expect same|different` — SSIM + pixel-diff + heatmap. The machine gathers the numbers; the agent's eyes judge the same frames. A lane's numbers alone never pass a visual gate (the identity audit proved "loaded OK" ships broken models).
- Frame-set claims (capture complete, film assembled): `visual-qa/frame_set_gate.py` — contiguity (a count alone is NOT proof; ffmpeg stops silently at the first gap), zero-byte/truncation + PIL decode, frozen sha-identity vs manifest, full-decode + frame count of the assembled mp4.
- Own-eyes still required on the checked frames. The scripts make the check cheap; they do not replace looking.

### NO-LISTS-WITHOUT-PULLS LAW
A research deliverable is pull attempts + artifacts (or honest failure records with exact errors), not a list of names. A source the lane never attempted to fetch is UNVERIFIED and unranked. A finding without a pull-in (or a recorded, retried failure) is incomplete work — the RESEARCH-TO-REPO LAW already says so; this is the method that enforces it.

### ADDENDA-MAILBOX RULE
A coordinator holds late owner addenda in a mailbox file in its workdir and folds them in at synthesis. Never send follow-up instructions to a lane that already completed — the send fails and the angle gets lost. If a completed lane's report lacks the new angle, spawn a follow-up lane for that angle only, or fold it into the synthesis with the gap named.

### PRE-DELIVERY CHECKLIST LAW (round 2, 2026-11-16)
Nothing reaches the owner without a delivery checklist. The tool is
`visual-qa/pre_delivery_checklist.py`: it hashes the deliverable, runs the
applicable kit checks (colour/light, pose, face, video probe, pair vs
source, reference compare), and REQUIRES `--seen "..."` — the agent's
own-eyes attestation of what they actually looked at and saw. No `--seen`
=> DELIVERY-READY NO, nothing is stamped. The checklist cannot verify the
agent's eyes — but it makes skipping the look a VISIBLE omission, and a
delivery without one is an incomplete delivery. Intentional frozen holds
in a film are attested with `--allow-frozen "reason"` (frozen-runs-only
→ WARN); black/blown frames can never be attested away.

### REFERENCE-METHOD LAW (owner 2026-11-16 ~09:45–09:47 EST)
The way to learn what's good is the top of the field, worked down the list
from the top. The library lives in mhvnsnt/physics-playground-pwa, `docs/build-a-bitch/tools/self-improve/reference/` (manifest.json:
title, source, licence, why it's the top of its field, sha256 — FETCH-VERIFIED
only; BROWSER-GATED items go on BROWSER-QUEUE.md, never faked). Every visual
deliverable is compared against the top reference for its field with
`visual-qa/reference_compare.py` — side-by-side sheet + BELOW / MEETS /
ABOVE bands. The reference is the FLOOR, not the ceiling: MEETS is industry
standard reached, ABOVE is better than the top, BELOW is fix-before-delivery.
The side-by-side sheet is shown to the owner every turn so he can approve —
TWO PAIRS OF EYES. A number alone is never the verdict.

### REPO-PREFLIGHT + RUN-GUARDED
Before any lane cuts a branch: `lane-ops/repo_preflight.sh` (clean tree, base branch present, fetch fresh). A dirty or stale clone is a hard stop — cut from a fresh clone or via the API instead. Long-lived runners (capture loops, watchers, servers) always launch under `lane-ops/run_guarded.sh` (flock) — a VM-restart relaunch can never start a second copy (the duplicate-runner race from Life Cut v2.2, twice).

## PRESENT-REFERENCES-EVERY-TURN RULE (owner 2026-11-16 ~09:47 EST)
Show him the best references when found — EVERY turn we work, no exceptions. Show the references + things found so HE CAN APPROVE them. Then compare them to our work — TWO PAIRS OF EYES. Side-by-side OR one individually then the next — either way works, as long as he sees both and judges. Presenting new information every turn is not optional and not something a lane does for me — it is my job in the reply itself.

## Sourcing rule (Mars, 2026-11-19)

If it isn't accessible on Steam, go find it anywhere else — archive.org, modding communities, wherever it can be gotten from. Don't ask, don't wait. (Mars owns a lot of games on Xbox and there's no way to get those files off an Xbox, so alternate sourcing is the path for all of them.)

"I own like hundreds of games on Xbox and anytime I mention certain games you just have to go get them because I own so many games that are like on disc and on Xbox and there's no way to actually get them to you but you have to go use the games in the commercial files and the actual source anyway."

## COMMUNITY-CRACKED RULE (owner 2026-11-20 ~22:13, extended 2026-11-21)

> "Fully already-decomped/recomped/decrypted/extracted community work FIRST, always — pull it in and wire it up 100% instead of decoding from scratch."

Before any decoding, decrypting, decompiling, or extracting from scratch, check what the community has already cracked — decompilations, recompilations, decrypted dumps, extracted files, fan tools and docs, modding-community releases. If the already-cracked version exists, pull it in and wire it up 100%. That is the work, not a shortcut.

Extension (owner 2026-11-21):

> "For ANY encrypted file, find where it is already decrypted and pull that in."

## LICENSE RULE (owner 2026-11-21 ~09:37)

> "I don't care about licenses, bro. Get it anyway. I don't care if it can be licensed or not."

Licensing status never blocks pulling something in — get it anyway. This supersedes the PR #217 note that Euphoria/Endorphin can't be licensed.
