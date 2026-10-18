# Creation Suite — Tekken-Side Inventory

**Lane H · 2026-10-18 · branch `r2/creation-suite`**
Every creation/customization file the project already holds on the Tekken side,
verified against the working tree (not from memory). "Wired" = reachable from
the Create Fighter UI (`customization/create-fighter/`) or the game loader
(`game/js/custom-fighter.js`). Unwired items have a plan in §8.

## 1. Part libraries

| Library | Parts | Index | Location |
|---|---|---|---|
| WMXIX CAW (all categories) | 2,690 | `customization/parts/PARTS-INDEX.json` | `customization/parts/wmxix/` |
| No Mercy (bodies, faces, skins, weapons, attire) | 682 | same master index | `customization/parts/no-mercy/` |
| **Master total** | **3,372** | `customization/parts/PARTS-INDEX.json` | — |
| Def Jam FFNY CAW parts | 22,360 (indexed, NOT duplicated) | `customization/parts/defjam/PARTS-INDEX.json` | `teardown/def-jam-fight-for-ny/models/caw-parts/` |
| DOA wardrobe | 0 parts (docs only — see GAP.md) | `customization/parts/doa/manifest.json` (empty) | `customization/parts/doa/` |

### Master index by slot (3,372)

| Slot | Count | UI category |
|---|---|---|
| upper_body | 476 | Upper Body 🥋 |
| faces | 348 | Face 😐 |
| skins | 233 | Skins 🎨 |
| bodies | 220 | Body Parts 🦾 |
| hair | 156 | Hair 💇 |
| gears | 140 | Gears ⛓️ |
| lower_body | 120 | Lower Body 👖 |
| accessories | 94 | Accessories ⌚ |
| shoes | 50 | Shoes 🥾 |
| gloves | 48 | Gloves 🥊 |
| colors | 8 | (color channels) |
| attire | 1 | Full Body 👘 |
| textures | 1,478 | unsorted — see §7 gap 5 |

### Def Jam index by slot (22,360)

| Slot | Count | Maps to |
|---|---|---|
| upper_body | 14,430 | Upper Body 🥋 |
| lower_body | 5,850 | Lower Body 👖 |
| accessories | 1,625 | Accessories ⌚ |
| head | 455 | Hair/Face 💇😐 |

Part schema: `part_id` (`defjam:V2CP_110_0001_A.o`), `name`, `source_game`,
`slot`, `file_path` (`teardown/def-jam-fight-for-ny/models/caw-parts/...`),
`repo`. Category codes 110=head, 111=upper_body, 112=lower_body, 113=accessories.

## 2. Decal library — Pantera (the pattern every fighter follows)

`customization/decal-library/pantera/` — 6 entries on main (+1 pending in PR #249):

| Entry | Type | PNG |
|---|---|---|
| pantera-logo-white-scratches | logo (ORIGINAL thigh decal) | 186×390 |
| pantera-logo-red-scratches | logo variant | 186×390 |
| pantera-logo-snow-leopard | logo (owner art, currently applied) | 2048×2048 |
| tights-blue-snow-leopard | tights (logo baked in — current Attire 3) | 512×512 |
| tights-blue-clean | tights (neutral base for compositing) | 512×512 |
| pants-black-trunks | pants | 512×256 |

`MANIFEST.json` carries the canonical placement: pixel rect x=176,y=34,w=186,h=390
in 512×512 `King_PantsLower_D` (uv u=0.34375,v=0.06640625,w=0.36328125,h=0.76171875),
center_uv (0.525, 0.447), both thighs mirrored. Compositing recipe in
`how_to_swap` (pick logo → composite at canonical rect → re-embed as image 44).
**Options-stacking rule (owner 2026-10-18):** every variant is saved and swappable,
never overwritten.

## 3. Real T3 animation clips (intro/victory seed set)

`assets/anim/t3/king_on_pantera_leoman/` — 31 decoded wh-anim/1 JSONs, REAL T3
King motion (see `game/js/t3anims.js`, provenance in `docs/anim/PROCEDURAL_AUDIT.md`).
Bone names match the game's stripped Mixamo names (Hips, Spine, …) so clips bind
directly. Loaded by `loadT3Clips(THREE)` → `THREE.AnimationClip` per action.

| Use | Clips |
|---|---|
| VICTORY picker (4) | t3_win_rp, t3_win_lp, t3_win_rk, t3_win_lk |
| INTRO picker | t3_walk_fwd, t3_walk_fwd_b, t3_dash_fwd (walk-in / dash-in) |
| TAUNT picker | t3_stance, t3_stance_b, t3_stance_c |
| (gameplay, not picker) | light, medium, heavy, grab, block, hit, launch, ko, crouch, jumps, sidesteps, backdash |

## 4. Per-fighter Tekken movelists (moveset library seed)

`game/assets/movesets/*.json` — **45 fighters, 539 moves** (Lane F owns the files;
the Creation Suite READS them via the data contract below, never writes).

Move entry: `{ name, input, t3_source, t3_row, t3_command, startup, active,
recovery, damage, limb, heavy, knock, soulGain }`, keyed by **Tekken input
string**: `1` `2` `3` `4` (limbs), `1+3` `2+4` (throws), strings `1,2`,
motion inputs `qcf+2` `f,F+1` `d/b+3` `n,d,d/f,f+1`, etc.

**Data contract (creation-suite side):** `customization/create-fighter/data/`
holds a DERIVED index (built by `tools/build-tekken-library.py`, see §8) —
`{ move_id, move_name, input, damage, limb, source_fighter, t3_command,
preview_clip }`. Regenerate when Lane F's data grows. The editor never imports
`game/js/movesets.js` (avoids side effects); it reads the derived index.

## 5. Tekken customization docs (teardown side)

| Doc | What it gives the suite |
|---|---|
| `teardown/tekken3/tools/tekken3recompiled/Outfit-Slots.md` | T3 outfit-slot system (per-character costume slots) |
| `teardown/tekken6/TEARDOWN.md` | T6 4-slot layered system: Head / Upper / Lower / Other — items as separate meshes on bone sockets |
| `customization/CUSTOMIZATION-RESEARCH.md` | prior research rollup |
| `customization/UNIFIED-UI-SPEC.md` | prior UI spec (superseded by `docs/creation-suite/DESIGN.md`) |

T6 rule reused in the suite: **Full Body vs Upper/Lower conflict** — equipping a
full-body outfit unequips upper+lower (after Replace/Cancel confirm). Already in
`catalog.js` CONFLICTS; matches Tekken 8's "Entire Body outfits take up all item
slots apart from Accessory slots."

## 6. Limb system (DXMMII)

`tools/limb-system/dxmmii/` — 774-bone Rigify meta-rig, 39-part modular body,
5-state arm machine (`attached | retracting | hidden | growing | gyro-detached`),
socket positions from `dxrm_manifest.json`, Blender pipeline `scripts/01→04`,
`.blend` files, QC renders. The Create Fighter LIMBS tab reads/writes presets
into the fighter JSON (`limbs: { enabled, preset, presets, sockets, arm_state }`).

## 7. Create Fighter app (current state, v0.2)

`customization/create-fighter/` — standalone web app (importmap three.js,
vendored). Tabs: BODY · ATTIRE · WARDROBE · PROFILE · MOVESET · LIMBS.
Full-screen 3D preview, try-on, buy/equip with Fight Money, 4 No-Mercy attire
slots, 10 DOA wardrobe slots, presets, photo thumbnails, export/import JSON.
Saves to localStorage `wh_create_fighter_v1`; `game/js/custom-fighter.js`
converts it to a roster fighter (currently: hardcoded moveset `'jin'` — §8 gap).

Honest current limits: part geometry NOT wired (socket-proxy markers, never fake
meshes); move `anim_ref` mostly null (no live preview yet); Def Jam index not
browsable; no decal UI; no intro/victory picker; single save slot.

## 8. Wire-up plan (gaps → this branch)

1. **Derived Tekken move library** — `tools/build-tekken-library.py` reads the 45
   movelist JSONs (+ MOVE-DATABASE.json wrestling moves) → writes
   `customization/create-fighter/data/TEKKEN-LIBRARY.json` with `preview_clip`
   per move (T3 clip mapped by limb/input; null only when no clip fits).
2. **Live move preview** — tap a move in the library → its preview clip plays on
   the preview fighter (MDickie "tap once = preview" pattern); tap ASSIGN commits
   to the slot. Preview uses `preview3d.playClip()` (new) fed by `t3anims`
   `jsonToClip` logic vendored for the create-fighter page.
3. **PERFORMANCE tab** — INTRO / VICTORY / TAUNT pickers inside the Create Fighter
   flow (WWE 2K22 "Performance section" pattern), first set = the §3 T3 clips.
4. **Decal UI** — ATTIRE → Decals section driven by decal-library MANIFESTs
   (Pantera first; pattern repeats per fighter). Options stack, never overwrite.
5. **Def Jam browsing** — catalog merges the 22,360-part Def Jam index into the
   same category grids (indexed, not duplicated — disk ceiling).
6. **custom-fighter.js v0.3** — moveset slots → real moveset object (no more
   hardcoded `'jin'`); intro/victory/taunt → fighter object; multi-slot saves
   (`wh_create_fighter_slots`, backward-compatible read of `wh_create_fighter_v1`).
7. **DOA parts** — still extraction-blocked (GAP.md); UI shows the category with an
   honest "no parts extracted yet" state instead of hiding it.
