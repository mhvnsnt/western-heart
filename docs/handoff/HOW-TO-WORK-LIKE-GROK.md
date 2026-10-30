# How to work like Grok Bot — playbook for Claude Code, Muse and every agent

The owner (Marquis) is not a coder and doesn't want manual steps. He judges work by **what he can see and test**. Follow every step below, every pass.

## 1. Proof every time
1. After each fix, capture **before and after** screenshots or a short clip at **390x844 portrait** and **844x390 landscape**.
2. Commit them under `docs/proof/<lane>/` (e.g. `docs/proof/select/negativo-after-390x844.png`).
3. **Open the render and look at it** before claiming anything (T-pose? cut-off? wrong model? black texture?). Media-proof standard: open it, check it, then claim it.
4. Link the proof in the PR body **and** in your reply to the owner.
5. Never say "works", "fixed" or "live" without visible proof. If you couldn't verify, say so.

## 2. Talk to the owner
- Plain, short, non-technical. Lead with **what changed** and **what he can test**, then the live link: https://mhvnsnt.github.io/western-heart/
- No jargon walls, no code dumps. One honest caveat line if something is blocked.
- Don't ask him to do steps you can do yourself.

## 3. Push often, never clobber
- Push after **every pass or every 30 minutes**, whichever first.
- **One job = one branch.** Never commit onto another agent's branch without merging it in cleanly; never overwrite work.
- Before a long job, push a backup branch: `backup/<name>-<yyyymmdd>`.
- Use `git worktree add /tmp/<name> -b <branch> origin/main` from `/workspace/western-heart`, not full clones (disk is tight).

## 4. Merge recipe (exact)
1. `git fetch origin && git merge origin/main` — **never rebase**. No force-push, amend, `reset --hard`, or deleting files.
2. `gitleaks detect --no-git --source <worktree> --no-banner` (there is no `-q`). Must be clean.
3. `git diff --name-only --diff-filter=D origin/main...HEAD` **must be empty**.
4. Commit as `mhvnsnt <197314870+mhvnsnt@users.noreply.github.com>`.
5. Open the PR with the instruction-gate template. **"Method actually used" must match "Method the owner specified" word for word.**
6. Merge only when the merge is clean and **every** Actions run is green (check via the Actions runs API, not just the PR badge).
7. Redeploy: `python3 tools/deploy/build_pages.py --onto` and **open the live game** to check it.
8. Never merge an old branch that is far behind main (that is how #498 deleted 4,225 files).

## 5. Find problems yourself
- Every pass, playtest the live game at **both** sizes: select screen, a fight, movement/stick, dash, block, grabs, combos, walls, camera, health bars, round flow.
- Run `tools/select-audit/run_all.sh` (on `grok/select-hero-ladder` / main once merged).
- Don't wait for the owner to report bugs. Log every finding in `docs/qa/PLAYTEST-<date>.md`, fix it or hand it to the right lane.

## 6. Complete-wiring law
- `docs/rules/COMPLETE-WIRING-LAW.md` + `tools/coverage/systems-coverage.json` (PR #958). Everything from Tekken (contact, hitboxes, hit reactions, grabs, throws, walls, rage…) and the other games is wired 100% **without the owner naming each part**. Coverage may never go down.

## 7. Use the real games as the template
- Fighting: **T8, then T7, then TTT2/T6** (T6 PSP ISO on release `tekken6-psp-v1`, play it in PPSSPP). T3 = logged last resort.
- Menus & creation: **WWE 2K19, Fire Pro, Wrestling Empire**, Tekken customization, SvR 2010/2011 Create-a-Finisher.
- Raw Tekken/WWE assets and Tekken-derived rigs go **only** in private `game-reverse-engineering`, loaded via `__WH_PRIVATE_ASSETS`. Canon names via `tools/canon`.

## 8. Canon rules
- Spirit Actions: English `魂 ACTION`, Japanese `魂アクション`. **Never "Heat Action".**
- **KESSHOU** (finisher), **Nine-Soul Release 九魂解放** ("SOUL RELEASE READY", never "Climax"), **Reihou 霊放** (purges rage), **Trial's Seal 試練の封** (verdict seal, not death) are separate systems, each with 3–4 variants per fighter (5–6+ for stronger canon fighters, per transformation).
- Owner's own model = **attire 1** (only exception: Pantera). Negativo shows his tribal model.
- Canon sizing for every fighter/transformation (Burger default = Bob-sized). `docs/roster/CANON-SIZING.md`.
- Full move lists (Tekken base + canon adds) must be inputtable, comboable and make contact.
- Select: unique pose each, no T-poses, Pantera card is the bar, **Buffalo Bill's pose is locked**.
- Never change arena sky, colors or lighting. Never cut models.
- Naming: **Creation Suite** (main menu), with the **Stance Editor** inside it.

## 9. Disk
- Keep **≥ 8 GB free** (`df -h /`). Use `/workspace/tools/agent/backup_and_clear.sh` and `/workspace/tools/agent/safe_delete.sh` only.
- Never delete unpushed work: push, verify on GitHub, then clear.

## 10. Secrets
Never print or commit `STEAM_PASSWORD`, `STEAM_GUARD_CODE`, `JULES_API_KEY`, `BANNON_SOURCE_TOKEN` or token files.

## 11. Coordination
Current lanes: `docs/handoff/HANDOFF-2026-10-23.md`. Post progress on issue #866.
