# Owner-Repo Asset Inventory — Animations, Customization Parts, Select-Screen Assets

**Date:** 2026-10-22
**Worker:** 61
**Scope:** everything reusable for Western Heart's animation bank, creation suite, and character-select building, mined from the owner's three repos. (OSS fighting-game engines are cataloged separately in `2026-10-22-oss-fighting-games-in-owner-repos.md`. Renders excluded — worker 46's lane, PR #702.)

## A. Animations

### A1. Owner motion bank — `brutalfistgrokversiontenpointfive/public/motion/` (75 clips, ~7 MB JSON)
Mixamo-convention (52 bones) FBX→JSON conversions. Index: `public/motion/index.json` (`{file, bytes, dur, keys, bones, src}`). Combat map: `public/motion/combat_clip_map.json` (140 moves → 91 clips, limb/trajectory/height/style scored). Registry: `animation_bridge/SOURCE_REGISTRY.json` (19 semantic states: idle, walk_forward/back, strafe, attack_1/2, block, hit_reaction, knockdown, getup, grapple, crouch, run, dash_forward, backdash, victory, defeat, taunt).
**Clip families:** BOXING ×6, BOX_IDLE, COMBO_PUNCH, BODY_JAB_CROSS, CAPOEIRA + GINGA ×3 + ESQUIVA, HURRICANE_KICK, TIGER_FEINT_KICK, ILLEGAL_ELBOW_PUNCH ×2, ILLEGAL_KNEE, CHOKESLAM, DDT, GERMANSUPLEX, SUPLEX, DOUBLE_LEG_TAKEDOWN___VICTIM, DROP_KICK, hit reactions ×5, GUARD_HIGH/LOW, STANCE_BLADED/CROUCH/WIDE, TAUNT ×4, locomotion (IDLE, walks, runs, crouch walks, DWARF_WALK, DRUNK_IDLE/RUN/WALK, BIG_JUMP, CROSS_JUMPS), KIP_UP, CORKSCREW_KIP_UP, knockdowns (FALLING_FLAT_IMPACT, FALLING_FORWARD_DEATH, DYING_BACKWARDS), DEFEAT, BREAKDANCE_READY.
**Gap coverage vs teardowns:** wrestling grapples (suplex family, chokeslam, DDT, double-leg), capoeira ginga/esquiva flow, drunken style, breakdance — none of these exist in the No Mercy/WMXIX/Tekken teardown sets.
**Wired this PR:** full clip set → `moveset-library/animations/owner-motion-bank/` + `OWNER-MOTION-BANK.json` index + combat move→clip map, nested under the existing animation-bank structure.

### A2. Quaternius UAL — CC0, 86 clips (`AshLane-prototype/public/motion/ual/`)
UAL1_Standard.glb (7.4 MB): 43 clips — locomotion, barehand combat, reactions. UAL2_Standard.glb (7.9 MB): 43 clips — melee/weapon combat. Godot glTF+bin mirrors. 65-joint Quaternius rig; no retarget needed on Quaternius bodies; owner's `retargetUal()` maps to the 58-joint Mixamo skeleton.
**Wired this PR:** `moveset-library/animations/UAL-CC0.json` source entry (license, files, clip counts, rig/retarget notes, fetch URLs). GLBs stay in AshLane-prototype; entries carry `raw.githubusercontent.com` URLs so the runtime/retarget pipeline can fetch at build time. Full clip-name enumeration deferred to build time (parse GLB JSON chunk).

### A3. BANNON native animations — `brutalfistgrokversion/native/`
`animations/idle.x`, `running.x`, `walkFast.x` (DirectX) + `source/idle.glb`, `running.glb`, `walking.glb` + `BANNON_rigged.glb` (4.2 MB). Owner's own character — clean IP.
**Use:** reference locomotion for the BANNON-universe fighters; the `.x`→GLB path documents the DirectX conversion pipeline. Cataloged, not copied (small, but redundant with A1's locomotion coverage).

### A4. Retarget/registry code (reference, cataloged)
- `brutalfistgrokversiontenpointfive/src/engine/retarget/AnimationRetargeter.ts` (33.7 KB), `AnimationController.ts`, `AnimationStateMap.ts`, `FighterMotionBank.ts`, `MixamoFightingMotionBank.ts`, `animation_bridge/retarget.ts` — owner's retarget stack.
- `AshLane-prototype/src/game3d/universal-retarget.ts` (18 KB), `motion-bank.ts` (15 KB, bone-family maps: KayKit/Rigify/Mixamo/colon-Mixamo/UE), `rig-pipeline.ts` (23.8 KB).
- **Use:** patterns for WH's retarget pipeline (bone-family detection, UAL→Mixamo joint mapping). Not copied — WH has its own retarget lane; these are cited as proven patterns.

## B. Character customization parts

### B1. AshLane parts library — `AshLane-prototype/public/models/` (~40 parts, ~8 MB)
| Slot | Files | Notes |
|---|---|---|
| footwear | sneaker_high/low L/R, theory_boot L/R, wrestling_boot L/R + manifest | L/R pairs, small GLBs (27–54 KB) |
| gloves | boxing, mma, opera_theory, street L/R + manifest | 15–40 KB |
| masks | bandana ×3, hollow_superdragon, luchador ×3 (azul/crimson/sombra) + manifest + FIT_NOTES | lucha masks ~570 KB |
| hair | echo_long_green, hollow_long_black, static_blond_beard, theory_locs_beads/pinned + manifest + FIT_NOTES | quaternius-derived, CC0, recolored |
| hoods | purple_robe ×2 + manifest + FIT_NOTES | ~406 KB |
| wristbands | pad, sweatband, wrap L/R + manifest | 4–20 KB |
| accessories | 4 rigged chains (gold_ashlane, wizard_gang, diamond_ice, bannon_piece) + manifest | skinned to Neck/Spine2, manifest `attach` (bone/pos/rot/scale) |

Manifests carry attach specs (`attachBone`, offsets, scale, per-slot tuning notes). The customizer UI (`src/components/customizer-panel.tsx`, 22.6 KB) defines the slot model: hair, facialHair, mask, hood, chain, gloves, wristbands, shoes + sections Fighter/Attire/Eyes/Body/Hair/Facial hair/Accessories/Face paint/Save, with live 3D preview and per-fighter persistence.
**Wired this PR:** all parts + manifests → `customization/parts/ashlane/`; entries appended to `customization/parts/PARTS-INDEX.json` (`source_game: "ashlane"`); `sources` gains `"ashlane"`. Slot names follow the existing suite slot vocabulary.

### B2. Quaternius modular parts — CC0 (`AshLane-prototype/public/models/cast/quaternius/`)
9 parts: Hair_Buns/Buzzed/BuzzedFemale/Long/SimpleParted, Hair_Beard, Eyebrows_Female/Regular. Same 65-joint skeleton in every part GLB → attach by bone-name rebind, no retargeting (`quaternius.ts: attachPart`). `tintSkin()` for skin-tone variants.
**Use:** creation-suite hair/beard/brow options + the attach pattern. Parts cataloged here; the attach-by-rebind pattern is cited for the suite's part-attachment work (no parallel system — it nests in the existing parts pipeline).

### B3. Face-paint system — `AshLane-prototype/src/game3d/customization/facepaint/` (11 files)
Regions, patterns, presets, profiles, picker, painter, decal, adapter. Facepaint texture dir: `public/textures/facepaint/` (incl. skull-nose.png).
**Use:** creation-suite face-paint section. Cataloged with a pointer; wiring the full layer-stack UI is a follow-up once the suite's Tekken-style menu map has its face-paint submenu slot.

### B4. Eye colors / morphs / persistence — `AshLane-prototype/src/game3d/customization/customizer/`
`eye-colors.ts`, `morphs.ts`, `persistence.ts` (per-fighter build save/load), `preview.ts` (live 3D preview host), `types.ts` (CustomBuild/AccessorySlotId).
**Use:** the CustomBuild save/load shape and live-preview-host pattern for the creation suite. Cataloged as proven patterns.

## C. Character-select screen assets

### C1. Deterministic SVG portraits — `AshLane-prototype/src/game3d/fighter-portraits.tsx` (8.5 KB)
Seeded PRNG (FNV-1a + mulberry32) → geometric street-art/wheatpaste portraits. Same fighter id always generates the same portrait; zero external assets; skin tones, hair styles/colors, beard, scars/tattoos, angry brows, headband accessories; faction-tinted halftone backgrounds.
**Wired this PR:** ported to vanilla JS as `game/js/fighter-portraits.js`, nested inside the existing select screen (`game/js/select-screen.js`) as the procedural portrait layer — placeholder/personality portraits until the portrait-pose pipeline produces real renders. No new menu, no parallel system.

### C2. Customizer panel UI structure (reference)
`src/components/customizer-panel.tsx` + `src/game3d/menu-backdrop.tsx`, `menu-icons.tsx`, `menu-theme.css`, `menu-sfx.ts` — the in-menu (not disconnected tool) customizer pattern: every control applies to the live model immediately.
**Use:** interaction pattern for the creation suite's Tekken-style flow (live preview, in-menu, immediate apply). Cataloged.

### C3. Select-screen-adjacent art (not pulled)
Screenshots in AshLane (`screenshots/*fighters*.png`, `new-menu-fighters.png`) are dev screenshots, not assets. BANNON `selectionPreview0.png`/`fightPreview.png`/`portrait.png` are single-character previews — cataloged for the portrait-pose pipeline's reference set.

## D. Explicitly NOT pulled (and why)
- **Renders/portraits** — worker 46's lane (PR #702 merged).
- **Full character GLBs** (28 AshLane/BrutalFist cast models) — the user reviews canon first; models stay in the source repos per #702's precedent ("large GLBs stay in the source repos").
- **SOMBRA_NEGRA_rigged.glb** (25 MB) — same reason.
- **Schwarzerblitz/NightSky engines** — reference/survey only, never bytes into WH without worker 62's survey + a dedicated wiring task.
- **YokosukaJS sprites** — explicitly unlicensed rips; only the MIT code portions are ever reusable.
- **KayKit/Kenney env/weapon/prop packs** — cataloged for arena/stage work; pulling is the arena lane's call.

## E. License summary for everything wired this PR
- Owner motion bank: owner's own conversions, registry-marked `owner-granted`; provenance note kept in `OWNER-MOTION-BANK.json`.
- AshLane parts: owner's own assemblies (quaternius-derived hair marked CC0 in manifests; chain/mask/lucha pieces are owner-made).
- UAL: CC0 — `LICENSE.txt` terms preserved in `UAL-CC0.json`; GLBs not copied, fetched at build time.
- Portraits module: owner's own code, ported with provenance header.
