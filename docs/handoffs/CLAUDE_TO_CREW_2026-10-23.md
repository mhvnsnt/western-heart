# Claude → crew handoff (2026-10-23): what broke, why, and how to do it right

Owner order (2026-10-23): write down what the other agents broke so they can work smarter, and stop the
"fast and lazy on purpose" habit. Every item below is a real breakage on main, with the commit and the fix. Read it
before your next PR. The rule that ties them together is the last section: **done means played, not pushed.**

## 1. Select screen crashed on every mode start: markup removed under live JS

- **What:** `33bff4dee` (worker 55, PR #676, "rebase menu fix") swapped the select-pane markup in `game/index.html`
  for a T8 `.pane-facts` row and dropped `.pane-title` and `.pane-style`. `game/js/select-screen.js renderPlate()`
  still writes `els.title.textContent` / `els.style.textContent`. Every `startMode()` threw
  `Cannot set properties of null (setting 'textContent')`. Nobody could reach a fight from the menus on main.
- **Fixed:** PR #795 puts both divs back beside `.pane-facts`.
- **Do it right:** before you remove or rename an id/class in HTML, `grep -rn` it in `game/js/`. Every selector the
  JS reads must still exist, or the JS must change in the same commit. Then run the fight harness (section 6).

## 2. Unit test red on main: wiring without updating the guard table

- **What:** `3148e6afd` (Wave 2 batch A2) wired `vainabel-attire1` as Vain Abel's default, but did not add it to
  `OWNERSHIP` in `game/tests/model-key-guard.test.mjs`. `node --test game/tests/*.test.mjs` has failed on main since then
  (`vainabel: player/select path resolves 'vainabel-attire1' (not their own)`).
- **Why it slipped:** the `game-unit-tests` CI job runs `test/*.test.mjs` only. Nothing runs `game/tests/`.
- **Do it right:** run `node --test game/tests/*.test.mjs` before every PR that touches `game/` or `roster/`. When you
  wire a fighter's own model, update the OWNERSHIP table in the same commit. (Claude is adding `game/tests` to CI.)

## 3. Statues and invisible fighters: unskinned statics wired as playable keys

- **What:** Tripo pulls are wired straight to `model.glb` (0 skins), with "rig queued" in the WORKLOG (SmutBase wave 6,
  Ryusan/Tobi; earlier King Tyrant A1–4, Star A1–3, Burger A2–7, Kronos A3, Vain Abel A2–4, Cain Elias A1–2, ...).
  A 0-skin GLB cannot animate. In a fight that fighter stands frozen or does not render
  (`createInstance: ZERO skinned meshes`).
- **Do it right:** owner standing rule (roster/TRIPO-REGISTRY.md step 3): **rig on intake.** Run
  `tools/auto_rig/rig_tripo_static.py --facing <axis>` and wire the rigged file. If you cannot rig it in the same
  PR, do not point a fighter's default slot at the static; record it as pending.

## 4. Nineteen fighters sideways: rigging without checking which way the mesh faces

- **What:** the 2026-10-21 k-NN batch rigs (`model-rigged.glb`, 49 joints) assumed every mesh faces +Z. Tripo
  pulls face **+X**. The skeleton sat across the body: those fighters stood in profile and their stance shredded
  (skull, kronos, saku-ra, phantom, purple-rain, waterfall, thor, sam-ur-a1, doc-frank A2/A4, demonio-human, burger,
  charger, ...).
- **Fixed so far:** PR #795 re-rigs and wires 10 of them (`model-rerig.glb`, old files kept). The rest are queued.
- **Do it right:** read the facing from renders, never assume it. Render the static from +Z, +X, −Z and −X and see
  where the face is (or use `tools/tripo-intake/facing_check.py` when it says CONFIDENT). Pass `--facing`. Then
  check the game's own instance with `node tools/proof-harness/rig_sheet.mjs OUT <key>`: the face must show from the
  +Z camera, and the T3 stance must hold together. Look at the PNGs yourself.

## 5. Earlier breakages from the same habits (all fixed by Claude, 2026-10-22)

| commit | what broke | habit |
|---|---|---|
| `6255a6e22` (PR #579) | stale full-file copies wiped 427 lines of assets.js, 113 of main.js, 316 of WORKLOG.md | copied whole files from an old base instead of a surgical edit on fresh main |
| `3942b8584` | deleted Zen's whole `MODEL_URLS` block; Zen could not load | did not read the deletion list |
| `4ab3aa206` | `charData` out of scope in `fighter.js _build()`; ReferenceError, **no fight could start** | never started a fight after the change |
| `c31b667d9` | duplicate `id="screen-stage"`; `show()` crashed on every mode start | never started a mode after the change |

## 6. The working standard (no more "fast and lazy on purpose")

Speed that breaks main costs the owner more time than it saves. Working fast and lazy on purpose is banned on this
repo. Before you call anything done:

1. **Sync** to the latest `origin/main` before you start and again before you commit (AGENTS.md).
2. **Surgical edits only.** Change the lines you mean to change. Never paste a whole file from an older copy.
3. **Read your own diff.** Every deleted line and every removed selector, key or id must be one you meant to
   remove. `git diff --stat` and the deletion list come before `git commit`.
4. **Run the checks:** `node --test game/tests/*.test.mjs` plus the `test/` suite.
5. **Play it:** serve the repo (`python3 -m http.server 8765`), then
   `node tools/proof-harness/fight.mjs OUT pantera <your fighter> demo=1 4 900`. The log must reach
   `"round":"fight"` with no `[pageerror]`. Open the PNG frames and look at them. Pantera is the canary.
6. **Proof in the PR:** the frames or sheets you actually viewed, and the test output. "Should work" is not proof.
7. **Say what you didn't do.** A shortcut, a skipped step or a known issue goes in the PR body, not under the rug.

## 7. More from 2026-10-23 (SmutBase, banks, loader)

| what | where | do it right |
|---|---|---|
| SmutBase rigs built "facing −Z" on the belief that "the game assumes every model rests facing −Z" | `docs/research/SMUTBASE6-RIGGING-REPORT-2026-10-23.md`, `8c4fef1b3` | The game convention is **+Z** (`game/assets/models/model-facing.json` note). A `-Z` entry turns the model 180°. Check with `rig_sheet.mjs`: the face must show from the +Z camera. |
| Ryusan / Tobi rigs wired after "rig validation" although they tear apart in the T3 stance | main's assets.js comments, PR #781 | "Validated" means the in-game stance render was viewed (`tools/proof-harness/rig_sheet.mjs OUT key`). Re-rigged from upright statics: `tools/auto_rig/reorient_static.py` then `rig_tripo_static.py --facing +Z`. |
| Menajerii's mesh carried a 4.23 m floor plane, skinned into the model | `roster/vixen/attires/attire1/model-rigged.glb` mesh "Plane" | List the meshes before rigging; drop props/floors (`gltf-transform` node dispose + prune). |
| `-attire1` keys pointed back at the unskinned statics while the main key used the rig | assets.js | Every key a fighter can select must point at a skinned file. |
| Megami, Menajerii, Ryusan, Tobi had movesets + models but **no roster entry** — not selectable (FIXED by the crew 2026-10-23) | `game/js/roster-full.js` | A fighter is not "wired" until `FULL_ROSTER` has the entry; then start a fight with them. |
| New movesets with no `anim_bank` and a base whose bank was never decoded → 0 T3 clips, frozen in fights | chatur/pond/megami/menajerii/ryusan/tobi | Check `t3: <n>` in the fight harness log (`fight.mjs`). Ogre, Kuma, Gon, Law, Forest Law banks now exist (`tools/anim/t3_bake_bank.py`); Raven/Jun/Lucky Chloe still have none — say so, don't ship a frozen fighter silently. |
| `index.json` stale vs the moveset files (6 fighters missing, counts wrong) | `game/assets/movesets/index.json` | Regenerate it with the tool that edits movesets (`merge_sources.py` does) in the same PR. |
| Loader joined a download it had just aborted → fights with a still-warming fighter failed (`AbortError`) | `game/js/assets.js loadModels` (`6255a6e22`) | Abort + reuse is a race: test the user path while the background lane is busy (start a fight right after boot). |
| Phone main menu (live, 390x844, touch): the "TAP TO ENABLE SOUND" pill sits on top of DAILY CHALLENGES (elementFromPoint hits the pill, not the button); the WESTERN HEART logo overlaps the top of the STORY card; the soul-urge dots crowd the header | `node tools/proof-harness/menu_tap.mjs <url> <outdir>`; live gh-pages d24dcdd0b | Test every menu on a phone viewport with touch before merging: each button must be the top element at its own centre. |
