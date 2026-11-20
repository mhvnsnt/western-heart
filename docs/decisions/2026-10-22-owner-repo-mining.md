# Decision Log — Owner-Repo Mining (Worker 61)

**Date:** 2026-10-22

## Context
Owner directive (2026-10-22): mine the owner's own repos (brutalfistgrokversiontenpointfive, AshLane-prototype, brutalfistgrokversion) for reusable animations, character-customization parts, and character-select assets, and wire them into Western Heart. Correction same day: specifically catalog OSS fighting-game content already collected in those repos as the FIRST step for worker 62's public OSS survey. Standing INTEGRATION LAW (2026-10-22, permanent): everything pulled wires INTO Tekken's menu/system structure as submenus/subsystems — never bolted-on parallel menus/systems.

## Decisions

1. **OSS inventory is a research doc, not code.** The Schwarzerblitz/NightSky/YokosukaJS finds are engine/reference-level; the correct first step is the catalog (`docs/research/2026-10-22-oss-fighting-games-in-owner-repos.md`) with per-find usability notes, which worker 62 consumes before any external pull. No engine bytes enter WH this round.

2. **Wire the owner's motion bank as a new source inside the existing animation bank** (`moveset-library/animations/owner-motion-bank/` + `OWNER-MOTION-BANK.json`), not as a parallel bank. The combat move→clip map (140 moves, limb/trajectory scored) plugs into the library's existing `anim_ref` model. Per INTEGRATION LAW: submenus/subsystems of the Tekken teardown direction, never a competing system.

3. **UAL (Quaternius, CC0) wired as a source entry with fetch URLs, GLBs not copied.** 15 MB of binary stays in AshLane-prototype; `UAL-CC0.json` carries license, clip counts, rig/retarget notes, and raw URLs so the retarget pipeline enumerates clips at build time. Rationale: binary already lives in a public owner repo; duplicating it into WH buys nothing until the pipeline consumes it.

4. **AshLane parts copied into `customization/parts/ashlane/`.** Unlike UAL, these are small (~8 MB total), slot-addressed by manifests, and the creation suite consumes them by file path — copying is the robust wiring (no cross-repo runtime fetches). PARTS-INDEX.json gains `ashlane` as a source with the existing entry schema.

5. **Portraits: port the deterministic SVG generator, don't pull images.** `fighter-portraits.tsx` → vanilla-JS `game/js/fighter-portraits.js`, nested in the existing select screen as the procedural portrait layer. No renders (worker 46's lane), no new menu.

6. **Schwarzerblitz input buffer NOT wired this round.** Input work is owner-deferred until after menus; the buffer is cataloged as the drop-in motion-command detector for that lane. Wiring it now would create a parallel input path — exactly what the INTEGRATION LAW forbids.

7. **YokosukaJS cataloged for the Heart and Mind Within lane.** The MIT beat-em-up state machine is the scaffold for the locked per-character beat-em-up story mode; wiring it now, ahead of that lane's design, would bolt on a system. Pointer left in the research doc.

8. **Character GLBs stay in the source repos** (28 cast models + SOMBRA_NEGRA). Canon decisions come from the owner after render review (per #702's precedent); models move only when a fighter's canon locks.

## Open questions for the owner
- None blocking. Follow-up wiring candidates (face-paint layer stack, CustomBuild persistence shape, KayKit/Kenney arena props) are cataloged and ready when their lanes open.
