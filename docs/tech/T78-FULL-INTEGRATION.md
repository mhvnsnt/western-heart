# T7/T8 Full Integration Tracker (stages · front-end · back-end)

Owner law (pt137u, Oct 23 2026): "the stages the menus everything the front end back in everything from the … Tekken 7 and 8 files and everything from any other game that we need".
Scope of this tracker: stages, all front-end menus **except character select** (separate executor), and back-end
systems. Movesets/AI/touch buttons, character select, Cape/Alisa + T8 extraction tooling, rig isolation (#825) and the
asset pipeline are tracked by their own owners — see agent-ops `CLAIMS.md`.

## 1. Inventory — what T7/T8 data actually exists (verified Oct 23 2026, 4:05 PM CT)

| Source | Where | What it holds | Usable for |
|---|---|---|---|
| T8 frame data | `docs/t7t8-reference/frame-data-t8-full/` (41 files) | startup/on-block/on-hit/CH per move | hit/guard/CH tables, punish windows |
| T7 frame data | `docs/t7t8-reference/frame-data-t7/` (48 files) | same, T7 | fallback for hit system |
| T7/T8 stage facts | `docs/t7t8-reference/stages.md` | T8 stage list + layout archetypes (infinite / walls / wall-break→balcony / floor-break tiers) | stage layout logic only — **no geometry** |
| T8 models | `teardown/tekken8/models/` (Asuka SFM .rar, Yoshimitsu .7z, ~108 MB, box only) | character meshes | fighters (other executor) |
| T7 King/Pantera | `teardown/tekken7/king/` (72+18 files) | King meshes/anims | fighters (other executor) |
| T7 stage | `teardown/tekken7/arenas/mishima-dojo_2024-map.rar` (40 MB, box only, not yet extracted — no unrar on box) | one fan-ported Mishima Dojo map | **only T7 stage geometry candidate on hand** |
| T7 tools | `teardown/tekken7/tools/umodel_linux`, `tekkenmods-docs/` | UE4 pak/asset extraction | stage/UI extraction once paks exist |
| T8 extraction tooling | `tools/extract/t8/` | **not on main yet** (Cape executor's PR pending) | reuse when merged |

**Blocker (unchanged since `teardown/TEKKEN-ARENA-STATUS.md`):** the full T7 (~47 GB) and T8 game paks have never been
acquired, so no T7/T8 stage geometry/textures/skyboxes, UI textures/layouts (UMG widgets) or audio banks exist anywhere
on the box or in the repo. See `teardown/TEKKEN78-ACQUISITION-PLAN.md` — the purchase/download is an owner step.
Until then the only lawful sources are: frame data + stage facts above, the T7 Mishima Dojo map, and other teardowns
(Eastern Mind panoramas, T3/T6/TTT2, DOA4, VF5, Urban Reign, WWE) already in `teardown/`.

## 2. Percent done per area (honest, from T7/T8 data specifically)

| Area | T7/T8-sourced % | Current source | Next step |
|---|---|---|---|
| Stage geometry | 0% | T3 panoramas + Eastern Mind panos + procedural builders | extract Mishima Dojo rar (needs unrar); real T8 stages need paks |
| Stage textures / skyboxes | 0% | Eastern Mind bitmaps, procedural gradients | same |
| Stage lighting | ~10% | per-stage rig (exposure/bloom tuned, not T8 values) | match T8 grade once pak lighting exists |
| Walls / floor breaks | ~15% | `stagebreaks.js`; archetypes from `stages.md` | map each WH stage to a T8 archetype in data |
| Stage select | ~10% | gated by `ui_sources` (#834) | rebuild from T8 layout ref once UI paks exist |
| Title / main / mode select | ~10% | T7 menu refs (#841 versus setup from T7 GAME OPTION) | cite T8 ref per screen |
| Versus / loading | ~5% | load bar owned by moveset/loading executor | T8 VS splash layout |
| Options / pause / results | ~5% | hand-built legacy | rebuild per T8 refs, cite in `ui_sources` |
| In-fight HUD (health/heat/rage/timer/rounds) | ~10% | `rage.js` + HUD; touch HEAT/RAGE in #842 | T8 HUD layout + heat gauge |
| Game flow / round logic | ~40% | T-series rules (rounds, timer, KO) already in `game.js` | verify vs T8 (3 rounds, 60s/round default) |
| Camera | ~20% | `camdirector.js` | T8 wall/heat-smash camera beats |
| Hit / guard / counter-hit | ~35% | `hitdetect.js` + frame-data tables | load T8 frame-data-full per source character |
| Throws | ~20% | per-moveset throws | T8 break (1/2) windows from frame data |
| Heat / rage | ~25% | `rage.js` | T8 heat burst/engager/smash rules |
| Sound / announcer hooks | ~5% | `audio.js`, `voice.js` (no T7/T8 banks) | needs paks |

## 3. Done in this pass
- Tree of Life white sky band fixed (`game/js/stages.js`, `panoCropTop` + backdrop tint). Cause: the Eastern Mind
  source bitmap's top rows are near-white cloud (rows 0–9 average >210/255) which blew out under exposure 1.5 + bloom.
  Proof: `proof/t78/tree-of-life-sky-before-after-390px.png`, `proof/t78/tree-of-life-after-390px.png` (390×844 @2x).

## 4. Rules for anyone continuing
Teardown-only sources; T3 only as a logged last resort; every menu change cites `game/ui_sources.json`; branch + PR
with full template; gitleaks before push; no deletions/force-push; merge only when every check is verified green.

## Mishima Dojo
- Source: `teardown/tekken7/arenas/mishima-dojo_2024-map.rar` → `Mishima_Dojo_Final_2_17_24.blend` (community Blender port of T7 stage s0; original posting URL/author not recorded, so it's still TODO). Extracted with 7-Zip 24.09 (`7zz`, github.com/ip7z/7zip).
- Converter: `tools/stage-arena-pull/convert_mishima_dojo.py`. 478 meshes / 1.9M tris → ~5.5 MB GLB. No textures (the .rar shipped none).
- License: Bandai Namco geometry. **Not committed here and not on the public Pages site.** The GLB lives in private `mhvnsnt/game-reverse-engineering` (PR #50, `tekken7/stages/mishima-dojo/`). The stage entry in `stages.js` registers only when `globalThis.__WH_PRIVATE_ASSETS` is set. The generic `t7glb` builder is public.
- Proof (private repo): `mishima-dojo-390px.png`, the 390px fight camera.

## Community-rip source track
Publicly posted community rips (The Models Resource, The Textures/Spriters Resource, DeviantArt, Sketchfab, modding forums) are allowed as an input track. No pirated game downloads. Log every source URL and the uploader here, store pulls in private repos, and pull in small batches.
