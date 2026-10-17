# Producerbot workflow: how to continue exactly as Producerbot works

Written 2026-10-14 so Muse and every other agent can pick up the owner's (mhvnsnt) work with no guessing. Repo-specific notes are at the bottom. When something here conflicts with an owner message, the owner wins: write the new rule here in the same PR.

## 0. Start of every task
1. Read this file, `AGENTS.md`, `CANON.md` (games), and the agent-ops board: `mhvnsnt/agent-ops` → `TAG-TEAM.md` (who is on what) and `CLAIMS.md`.
2. **Claim first.** Add one line to `CLAIMS.md` (`<agent> | <repo> | <task> | <date>`) on a branch and open a PR with gh. Don't start work someone else claimed. Current owners: creation suite + teardown importers = Repo Co Dev; physics + physics test env = the physics agent; T-pose renders = Muse.
3. Pull main before you touch shared files (`git fetch origin main && git rebase origin/main`). Another job may be editing the same folder: work only in your files, resolve conflicts by keeping both sides.

## 1. Clones and disk (box is shared and often near full)
```
df -h /                                                     # check first; stop if < 3 GB free
git clone --filter=blob:none --depth 1 https://github.com/mhvnsnt/<repo> <dir>      # shallow, blobless
git clone --filter=blob:none --sparse https://github.com/mhvnsnt/<repo> <dir> && cd <dir> && git sparse-checkout set <paths...>
```
- Clone into `/workspace/<task>/`, not into another agent's folder.
- **Back up before delete. Never delete anything that is not verified saved.** For a clone:
  `git status --porcelain | wc -l` must be 0, `git log --branches --not --remotes --oneline | wc -l` must be 0, and every branch must show in `git ls-remote origin`. Stashes → push as `backup/box-<date>-<name>` branches. Uncommitted → commit to a `backup/...` branch, never main.
- Big untracked/ignored files → private `mhvnsnt/box-storage` as Release assets: `sha256sum f > f.sha256; gh release upload <tag> f f.sha256 -R mhvnsnt/box-storage`, then download it back and compare SHA-256 before deleting the local copy.
- Log every move with links in agent-ops `BOX-OFFLOAD-LOG.md`. Keep anything an agent is using right now.
- Ports: 8765 and 8791 are often taken by others. Pick a high free port (`python3 -m http.server 18437 -b 127.0.0.1 -d game`).

## 2. Git, PRs, merging
- **PRs only through the gh CLI from the box**, never the connector "create PR" form (the owner refuses to submit forms):
  `git push -u origin <branch> && gh pr create -R mhvnsnt/<repo> --head <branch> --title "..." --body "..."`
- Branch names `grok/<repo-short>-<topic>`. Small PRs, one piece each. Push each piece as soon as it's done (incremental pushes), never sit on local work.
- **Merge rule (owner, Oct 14 2026):** a PR merges into main only if it merges cleanly, its tests/CI pass, and it deletes or breaks nothing on main. Otherwise it stays open. Repos with `.github/workflows/pr-clean-merge.yml` (money-machine-hq, God Molecule, TRIPPEDD, Bannon) auto-merge when green; it fails any PR that deletes a file on main, and it never auto-merges PRs touching `.github/workflows` (owner merges those).
- Check before merging: `gh pr checks <n> -R mhvnsnt/<repo>` and `gh pr view <n> --json mergeable,mergeStateStatus`. If checks are invisible or failing on main too, say so and leave the PR open.
- Commit identity on the box: `git config user.name "Producerbot (Grok Bot)"; git config user.email mhvnsnt@users.noreply.github.com`.

## 3. Media proof standard (never claim without proof)
Full gate list: `/home/box/agent-data/workflows/media-proof-standard/SKILL.md`. Short form:
- Reopen the bytes you wrote (PIL `verify`, `ffprobe`, full `ffmpeg -f null` decode, GLB load).
- Open the frames/PNGs yourself with an image reader and look: subject present, no blank frames, text spelled right.
- SHA-256 every deliverable (`sha256sum`) into a manifest (parts.json / SHA256SUMS / PROVENANCE.md).
- Edits to owner art/models: before/after of the same frame, side by side.
- **No AI faces.** Characters are rendered from the owner's own models or real imports. AI only for non-character plates, labelled AI_PLATE.
- Unknown origin = **"parts unknown"**. Never invent canon. Card text comes from CANON.md through a script.
- **Version, never overwrite**: `_v2`, `_a1wip`, `base_v1`. Originals and teardown files are never edited.
- Never say "rescanned" for a recolor. Say what was actually done.
- You can't hear audio: say so and ask the owner to listen.

## 4. How the Western Heart UI screens were built (`game/ui-wh/`, PR #121, #123)
1. **Layouts mapped from teardowns**, rebuilt not copied: title = TTT2/T6; main menu = Urban Reign/TTT2 list with JP sub-label; mode select = Def Jam/WWE cards; character select = T6/TTT2 (P1 left, P2 right, grid middle, timer); VS = Def Jam/WWE diagonal; HUD = T6 bars + Nine-Soul meter; pause = Urban Reign/Tekken; results = WWE/Def Jam. Table in `game/ui-wh/README.md`.
2. **Wallpaper transform**: `python3 game/ui-wh/tools/make_wallpaper.py` derives `art/wallpaper_wh.png` from the owner's `game/assets/ui/title-bg.png`: 16:9 crop dropping the logo band → heavy blur (source characters become light) → indigo/crimson/gold duotone + crimson sun → Pantera rendered from his GLB as hero → Western Heart Japanese text. Source file untouched.
3. **Portraits from GLBs in Godot** (no AI): `xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_ui_portraits.gd -- $(pwd)/game/ui-wh/portraits`. Any GLB + recipe: `lab/game/tools/render_card.gd` (see §5).
4. **Playwright capture + self-review loop**: serve `game/`, then `PW_CHROMIUM=/usr/bin/google-chrome WH_PORT=<port> node game/ui-wh/tools/capture.mjs docs/qa/ui-wh` (needs a playwright install; on the box `ln -s /tmp/gb-pw/node_modules node_modules` temporarily, remove before commit). It fails on any page error / 404 / wrong active screen / broken keyboard flow. Then open every PNG, fix what looks wrong, capture again. Repeat until it passes AND looks right.

## 5. Roster cards and showcases (`docs/roster/ROSTER_CARDS.md`, PR #125)
```
python3 game/ui-wh/tools/canon_to_roster.py          # CANON.md -> game/ui-wh/roster_canon.json (never hand-edit)
# real render only if a model fits the canon description; else MODEL PENDING silhouette + full canon text
xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_card.gd -- $PWD/<glb> /tmp/<id> $PWD/docs/roster/<id>/kitbash_v1.json 20
WH_PORT=<port> PW_CHROMIUM=/usr/bin/google-chrome node game/ui-wh/tools/capture_cards.mjs docs/qa/roster-cards
```
- Lock state is data: `roster.js` `isUnlocked()`; Pantera only by default; `?unlock=all` only for promo captures.
- Card = render, name, kanji, soul, tier line, quote, Tekken body, element, ORIGIN parts unknown, signature. Flag on the art: ATTIRE 1 / WIP KITBASH / MODEL PENDING.
- **Kitbash** (owner t48u): re-dress existing models with parts from every teardown (TTT2/T6, Def Jam, Urban Reign, WWE) on versioned copies; log every part in `docs/roster/<id>/parts.json` with source, SHA-256, third_party, pre-sale action. Worked example: `docs/roster/zui/` (base T7 Steve Fox import → hide hair, robe recolour, indigo pants, sake gourd, beads, sash → before/after + SHA-256). Honest gap: no extracted head/hair meshes from TTT2/Def Jam/Urban Reign/WWE are on main yet.
- Showcase = select (default + unlock all) + every card + promo strip (`cards.html#strip?ids=...`). Look at every PNG before reporting.

## 6. Height / scale system (PR #120)
`lab/game/data/characters/heights.json` (cm per fighter) → `lab/game/scripts/height_scale.gd` scales each fighter at fight load; HUD shows height; tests `lab/game/tests/test_height_scale.gd` (46 pass). Tekken 6/TTT2 publish no heights; values borrowed from Tekken 7/8 profiles need owner OK (rule check holds it).

## 7. T-pose and model co-author pipeline
T-pose standard: `docs/tpose-refs/MUSE_TPOSE_SPEC.md` (one-to-one T-pose, pure white, fingertips in frame, flat light, every attire). Flow: T-pose image → Tripo 3D → rig (Tripo/Mixamo) → `python3 tools/import_model.py <glb> --character <id> --attire <a> --render` (rig map, Tekken segments, P1 retarget map, rig gates, register; `docs/MODEL_IMPORT_AUTORIG.md`) → co-author in Blender / creation suite (`docs/CREATE_A_FIGHTER_SPEC.md`, Repo Co Dev) → move-set (`docs/MOVESET_EDITOR_SPEC.md`). Drive links: AGENT_IMPORT_RUNBOOK in CREATE_A_FIGHTER_SPEC.md. Secondary/jiggle bone names for the physics sandbox: MODEL_IMPORT_AUTORIG.md.

## 8. Entrance videos
Exact method: `money-machine-hq/docs/production-bible/ENTRANCE_VIDEO_METHOD.md` (also in Bannon, God Molecule, TRIPPEDD): rig repair, animation, ring + lights, name plate and cards, beat-grid edit (every cut on the beat grid), music, post commands, vertical cut. Owner's spelling rules apply (e.g. "STICK UP", no hyphen).

## 9. Teardown → proprietary rule
Build on top, never destroy. Teardown files stay byte-identical; everything new is a derived, versioned file. Transform into the Eastern Mind · Western Heart universe (names, souls, kanji, colours, parts) until it reads as ours. Track every remaining third-party piece (`third_party: true` + pre-sale action in parts.json / move slots) so it can be replaced before any sale. Tell the owner plainly what is still third-party.

## 10. Honesty rules
- Report failures, blocks and gaps in the same message as the wins.
- Never say done, fixed, merged or "looks better" without the proof from §3 and a link.
- Never claim to have watched/listened. Never invent canon, faces or data.
- Prefer a smaller true result over a bigger claimed one.

## 11. Universal rig-repair pipeline (`tools/rig_repair/`, PRs #164–#168)
Owner order: a PERMANENT automatic pipeline that fixes every character rig defect (skin stretching esp. armpit-to-pec-to-bicep, holes, floating chunks, ghost hands, skeleton misfit) and runs every model in every game through it. Method ported from Bannon PR #77, skeleton-refit step invented here (no free tool refits an EXISTING skeleton in place).
- One command: `python3 tools/rig_repair/pipeline.py --in MODEL.glb --outdir out --tag <name>`; batch: `ls models/*.glb | xargs -P 4 -I{} python3 tools/rig_repair/pipeline.py --in {} --outdir out --tag $(basename {} .glb)`. Every stage writes a VERSIONED file + JSON report; inputs are NEVER touched.
- Stages: detect (multi-mesh, meshopt decode, pure Python) → transfer `--limb-separate` (de-hardcoded) → **refit** (volume-mode skeleton refit, headless Blender, clamp 0.10 m, inverse bind matrices recomputed so existing clips play unchanged) → reskin (CONDITIONAL, default none — measured worse than transfer weights) → separate (dominant bone >0.20 m away → reassign to correct body region) → armpit (de-bleed 0.14 m, sharpen p=1.6, torso-side) → weldcap (HARD ASSERT: zero open edges, non-manifold not increased — fails loudly) → gate (`rigcheck/rig_check.py`, 6 standard clips, p99.9 edge stretch ≤ 2.5) → proof (stress-pose renders, open every render yourself).
- Measured (Stick-Up v1, decimated): 27.7–44.7 → 10.7–15.1 p99.9. The 2.5 threshold is aspirational for LBS without corrective shapes; the pipeline drives it ~3× down. Full table + lessons in `tools/rig_repair/PR{1,2,3,4}_NOTES.md`; full method in `docs/handoffs/RIG_REPAIR_METHOD.md`; per-call decisions in `docs/handoffs/STICKUP_V2_DECISION_LOG.md`.
- Merge order: #164 → #165 → #166 → #168 (parallel branches; one README.md conflict on #165, resolve for #165's newer README).
- Run the gate before claiming any model "repaired": exit 0 = PASS, 1 = FAIL. Media proof standard applies to proof renders.

## Repo notes
- **western-heart**: menus `game/ui-wh/`, Godot lab `lab/game/`, canon `CANON.md`, cards `docs/roster/`, captures `docs/qa/`. No pr-clean-merge workflow yet: check `gh pr checks` and merge by hand only when green and clean.
