# Create-a-Fighter Template Plan: replacing the Mixamo base

**Date:** 2026-10-24. **Type:** read-only survey and build plan. No code, asset or menu was changed to write it.
**Repo state read:** `main` working tree at `855bd4616`, open PRs as of 2026-10-24 ~10:00 UTC.
**Lane owner of the creation suite:** Repo Co Dev (`docs/RULES_NO_GUESSING.md` rule 8). The ui_sources CI gate belongs to MoneyManBusch (`AGENTS.md`). This plan does not build either one.

## 0. The ask and the laws that apply

Owner, verbatim: *"you guys never replaced mixamo shoulder [the Mixamo base body] with a actual create a fighter template fully morph able and changeable or used the Tekken and WWE Creation suite files or setup"*.

Earlier owner wording on the same point (`docs/creation-suite/OWNER-DIRECTIVE-2026-10-22.md`): *"instead of Mixamo soldier it should be like different variations of the Def Jam creation templates, Tekken customization and creation templates, WWE game file templates for character creation and customization, like their default and template models that they build on, and then the option to actually use pieces and parts from the characters that are in game or to edit them"*.

Laws this plan follows:
- **No guessing or procedural work when real data exists** (`docs/RULES_NO_GUESSING.md` rules 1–4). If something is missing, this plan says MISSING and names the unblock.
- **Data priority T5/T6/T7/T8/TTT2 first.** T3 is the logged last resort (`AGENTS.md`, instruction gate of 2026-10-23 2:19 PM CT).
- **No hand-made menus.** Every creation or customization screen comes from teardown files, and every UI change cites its source in `game/ui_sources.json`, the PR and the WORKLOG (`AGENTS.md`, laws of 2026-10-23 2:21 PM CT and t123u).
- `packages/creation-suite` UI is **NON-COMPLIANT pending a teardown-sourced rebuild. Do not delete it.**
- Bandai Namco and 2K assets stay in the private repo `mhvnsnt/game-reverse-engineering`. They load only behind `globalThis.__WH_PRIVATE_ASSETS` (`docs/tech/T7-STEAM-EXTRACTION.md`, "Where the assets live"). This public doc records only paths, names and counts.

---

## 1. What the base body is today

There are three creation front-ends and three different bases. **The game itself still uses the Mixamo soldier.**

| Where | Base it loads | How the body is "shaped" | Evidence |
|---|---|---|---|
| **In game:** a created fighter in a match | `customization/create-fighter/assets/Soldier.glb` | `game/js/custom-fighter.js` `BODY_TYPES` maps a No Mercy body-type *name* to an `{h, w}` pair. `game/js/fighter.js` scales the whole root by `(w, h, w)`. `game/js/assets.js` lerps every material colour 30% toward the skin tone. Moveset is hard-wired to `'jin'`. Parts are attached at bone sockets by `game/js/customization-consumer.js`. | `game/js/assets.js` `MODEL_URLS.custom` (line ~339). `custom-fighter.js` lines 9–18 and 47 ("Uses Soldier.glb base model") and 68. `fighter.js` lines ~405–411. The colorize block in `assets.js` is at line ~1375. |
| **Flagship suite** `customization/creation-suite-ui/` | `Soldier.glb` again (`BLANK_GLB`, the blank fighter's `baseGlb`) | Same localStorage record (`wh_creation_suite_v1`) that the game reads | `customization/creation-suite-ui/js/suite.js` lines 60, 77, 98 |
| **Legacy create-fighter** `customization/create-fighter/` | One of 9 MB-Lab bakes in `customization/templates/meshes/*.glb`, picked on the template-select screen | Each template is a separate static bake. MB-Lab morph values are baked in at build time (`body-templates.json` → `mb_lab.morphs`). | `customization/create-fighter/js/creation-flow.js`, `customization/templates/README.md` |
| **Package suite** `packages/creation-suite` (ui/, ui2/) | Roster fighters' own GLBs (ui2 list: pantera, demonio, diablo, slice, zui, phantom, skull, saku-ra) | `src/body.js` builds **procedural** `cs_<region>` morph targets: ellipsoid falloff along the normals, 1.0 = 60% of the region radius. Bone scaling covers height, limbs, shoulders and head. `src/dna.js` defines 15 sliders. | `packages/creation-suite/src/body.js` header comment. `src/dna.js` `SLIDERS` and `BODY_TYPES` |

Measured with a GLB JSON parse (no Blender) during this survey:

| File | Skins / joints | Skeleton naming | Morph targets | Notes |
|---|---|---|---|---|
| `customization/create-fighter/assets/Soldier.glb` (2,160,468 B) | 2 skins, 49 joints | `mixamorig:Hips … RightToeBase` (Mixamo-49) | **0** | 7,434 verts, 4 clips. This is the "Mixamo soldier". |
| `customization/templates/meshes/technician.glb` (9,087,004 B) and the 8 siblings | 1 skin, 71 joints | MB-Lab names (`root, pelvis, thigh_R, … breast_L`) | **0** | 38,754 verts. Static bake, AGPL-3.0 (MB-Lab database) |

Conflict to fix: WORKLOG.md (2026-10-22, "Mixamo soldier DEAD as a default") says `creation-suite-ui/js/suite.js` was switched to `templates/meshes/technician.glb`. **Main still points it at `Soldier.glb`**, and `game/js/assets.js` `MODEL_URLS.custom` was never changed. So the soldier is still the in-game created-fighter body.

Other compliance notes on the current base. These are flags only; nothing gets deleted.
- `custom-fighter.js` `BODY_TYPES` numbers (`'Rikishi': {h:1.02, w:1.42}`, `'King Frame'`, `'Ganryu Frame'` …) have no cited source. The names are No Mercy's, but the numbers are not data.
- `packages/creation-suite/src/body.js` region morphs and `src/dna.js` sliders are procedurally generated shapes. Under `RULES_NO_GUESSING.md` rule 1 they must not be extended once real morph data lands. Keep them as the fallback the code already treats them as ("authored morph targets with the same slider names … are used instead when the model has them").

---

## 2. Inventory: every creation and customization source

Counts come from `git ls-files` plus file sizes on disk. The private T7 rows come from the manifest committed on draft PR #863 (`teardown/tekken7-steam/pakchunk0/manifest.json`, read via the GitHub API at `refs/pull/863/head`). The private repo itself was **not readable from this session** (access denied), so treat those rows as "per manifest".

### 2.1 Tekken (priority sources)

| Source | Path | Files / size | Contents for creation | State |
|---|---|---|---|---|
| **T7 Steam extraction (private)** | `game-reverse-engineering` PR #51 → `teardown/tekken7-steam/pakchunk0/` (`manifest.json` mirrored on draft PR #863, which must not be merged) | **200 skeletal-mesh GLBs** across 38 character codes, plus 622 textures | Base 1P costume parts by slot token: `har` 60, `fac`/`face` 42, `bdu` 36, `bdl` 36, `hed` 8, `exp` 7, `hef` 5, `fah` 4, `bdf` 1. Joint counts run 207–305 (42 meshes have 207), plus one 2-joint drop item. Textures include **generic skin sets** `Character/Common/shader/Texture/skin/male/T_CH_male_{body,arm,hand,leg,foot,neck,head}_{D,S,N}` and `skin/female/…`, plus per-character skin. UI flash: CharacterSelect, Makuai, StageSelect, MainMenu, HUD_Gauge, Result. 15 meshes failed in UModel (`docs/tech/T7-STEAM-EXTRACTION.md`). | Held privately. **`Character/Common` was unpacked but no meshes were exported from it.** The export loop in `tools/extract/t7/extract_pak.sh` covers only `Character/Item/Meshes/*/*/*/Meshes/SK_CH_*.uasset`. No `cmn` (generic) meshes in this pak. |
| T7 tkdata (private) | same PR #51 → `teardown/tekken7-steam/tkdata/` | 1,087 files | `mothead/bin/<code>mot.bin` (full movesets), `list/` customize tables: `customize_item_data` (23,548 items), `customize_palette_color` (144), `customize_color_rules`, `customize_chara_list`, `customize_preset_table`; `SW_UI_*.bin` | Held privately. Parser: `tools/extract/t7/t7_customize.py` |
| T7 customize structure (public, derived) | `packages/creation-suite/src/t7layout.js`, `test/t7layout.test.js` | 2 files | Slot codes 1–15, 17, 18 (suntan / skin tone), 19 (mirror) with record counts, `T7_REGION_TABS`, `T7_FLOW`, 3 colour layers, 12×12 palette | In repo |
| T7 slot schema | `customization/parts/tekken/` | 9 files, 0.8 MB | `tekken7-slot-catalog.json`: 16 slots, slot-group IDs −236…−254, 21-field item CSV spec, conflict rules, colour slots 0–5, PlayerCus scope, T8 additions note. Also `tekken6-slot-catalog.json`, `ttt2-slot-catalog.json`, `tekken6-item-names.json` (9,440 names) | In repo (schema, from TKDataPatcher docs) |
| T7 parts catalog | `customization/parts/tekken7/` | 9 files, 2.2 MB | `CATALOG.json` with **1 real part**: `skull-mask.glb` (836,264 B, generic `cmn_hef_skull`, Dragunov-fitted variant from the TR205 arcade tree), 80 CI/CCI records, `suite_slot_mapping` | In repo |
| T7 teardown | `teardown/tekken7/` | 172 files, 81.9 MB | King FBX + 57 textures + `pantera_rigged.glb`. `tools/umodel_linux`. `tekkenmods-docs/` (58 files: extraction, TKDataPatcher, T8/TTT2 overview pages). `rigging-reference/tekken7-hand-arm.md` (the shared `SKT_CH_base_Skeleton` and finger chains). `T7-STEAM-EXTRACTION.md`. `ui/UI-EXTRACTION-STATUS.md` | **No base body and no customize parts.** `ui/UI-EXTRACTION-STATUS.md` still says "BLOCKED, never acquired", which is stale since the 2026-10-23 Steam pull. |
| T7 skeleton reference | `tools/retarget/tekken_skeleton_base.json`, `tools/retarget/tekken-bonemap.json` | 2 files | 60 core bones of the shared T7 base skeleton, from community dumps (Ludenous1 `SK_CH_kin`/`SK_CH_jin`, identical topology). Maps `tekken7_to_wh_canonical` and `tekken7_to_mixamo49` | In repo |
| T7 UI rules | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` | 1 file | Measured sizes and colours for select, stage, result and main menu | **No customize-screen rows** |
| T7 community | `teardown/community/tekken7/` | 143 files | Frame-data CSVs only | No creation content |
| T5 | `customization/parts/tekken5/` (32 files, 3.9 MB) + `teardown/tekken5/` (11 files) | — | 80 whole-costume `FULL_BODY` GLBs (release `tekken5-costume-glbs-v1`, static; per-file verts/tris in `GLB-MANIFEST.json`), a low-poly body per pack, surveys, tools, proof renders | No per-slot parts, no rig data in the manifest, no morphs. ctype-5 VIF 0x82 and TK5DATA0 are named gaps. |
| T6 (PSP) | `customization/parts/tekken6/` (7 files, 1.8 MB) + `teardown/tekken6/` (112 files) | — | `item-definitions.json` (768 tables, 9,440 names validated). **Definition array NOT located.** `CATALOG.json` has 0 parts. 2,546 mesh containers sit behind a custom-DEFLATE (open PR #446 claims the cipher is solved). The EBOOT shows `CUSTOMIZEPACK%d_%d`, `HAIRCUSTOMIZEPACK%d` and `DEFAULTPACK%d`. | Names and structure only |
| TTT2 (X360) | `teardown/tekken-tag-tournament-2/` (33 files) + `teardown/ttt2-customization-research.md` | — | GOD/XDVDFS tooling and archive map. Item models expected as `.nud`/`.nut` | No item records or meshes. Open PR #968 (take-2 carve) |
| T8 | `teardown/tekken8/` | 7 files, 113.6 MB | 2 character model archives, select-screen refs | No customization data. **TEKKEN 8 is not owned on Steam** (`docs/tech/STEAM-LIBRARY.md`) |

### 2.2 WWE and other games

| Source | Path | Files / size | Contents | State |
|---|---|---|---|---|
| WWE 2K CAW research | `customization/wwe2k-caw/` | 9 files | `CAW-STRUCTURE-2026-10-19.md` (the 8 editors, CAW load pipeline: "read base body template (slot 256/257 morph target set) → apply morph slider values"). `CAW-SUITE-BREAKDOWN.md`. `PULL-PLAN.md` (targets `pac/edit/bbtemplate.pac` "male/female base bodies + morph targets", `default.pac`, `edit.pac`, `pac/edit/ch/`, `pac/edit/body/`). `moveset-library-2k19.txt` (5,581 move names from 2K19 `pac/root/createmode*.pac`) | **No `pac/edit` file held anywhere.** `bbtemplate.pac` contents come from community docs and are unverified. |
| WWE 2K research docs | `docs/research/WWE2K-CREATION-SUITE-TARGETS-2026-10-23.md`, `docs/research/WWE-CAW-EXTRACTION-STATUS.md`, `docs/research/RE-WWE2K22-PLAN-2026-10-23.md`, `teardown/wwe-2k/` (6 docs), `teardown/wwe2k19|wwe2k20|wwe2k22/README.md` | — | Depots, file targets, tool status. 2K22 `.pac` chunk codec and rig format **not publicly documented** | Owned on Steam: **2K19, 2K20, 2K22** (`docs/tech/STEAM-LIBRARY.md`, which lists 2K25 as not owned on Steam despite the owner's verbal "own every 2K") |
| WWE 2K22 format research | open **PR #881** → `docs/research/WWE2K22-CREATION-SUITE-2026-10-23.md` | 1 doc | Persona → weight class/archetype → Face (Template / Parts / **Face Deformation** sliders / Photo) → Body (Body Type, Skin, Veins, Hair, Tattoos) → Attire layers. `pac\edit\ch` = CAW parts. Rig/anim format: "No public knowledge, awaits pull" | Docs only |
| WWF No Mercy | `customization/parts/no-mercy/` (1,292 files, 3.9 MB) + `teardown/wwf-no-mercy/` (18,567 files) | — | `CATALOG.json` 682 parts: **220 body segment meshes** (per body type, e.g. "(Skinny) Chest Front", 17 verts), 194 faces, 233 skins, 34 accessories. 303 GLBs, static and unskinned. Menu doc `re-docs/docs/ui/menus/edit-a-superstar.md`: 14M+9F body types, 8 skin tones, 7M+3F heads | Real CAW body-type set, low-poly segments, not a modern template |
| WWE WrestleMania XIX | `customization/parts/wmxix/` (2,692 files, 53 MB) + `parts-converted/wmxix-textures/` (1,477 PNG) + `teardown/wmxix/` (1,568) + `teardown/wwe-wrestlemania-xix/` (160) | — | 1,470 `.tex`, 1,200 `.ymg`, 8 `.ycg` CAW edit_data. YOBJ/YANM docs, wrestler-000 solved | `.ymg` decode blocked. The FIGURE 12-region sliders are known only from a GameFAQs FAQ; no slider data has been decoded |
| Def Jam: Fight for NY | `teardown/def-jam-fight-for-ny/` (271 files, 30 MB) + `customization/parts-converted/defjam/` (3,402 files, 122 MB) | — | 78 `V2IP` base models (`.o` rig + `.ssh` SHPS mesh). `FIGHTER.XML` with 142 entries including a `bodysize` field. ~1,900 `V2CP` CAW parts including `V2CP_D_A..F` defaults. 1,218 GLBs with **POINTS topology, vertex order unproven** | SHPS mesh decode open. Not usable as a body yet |
| Fire Pro / Nioh / Wrestling Empire / MK / FO3 | `teardown/firepro/README.md`, open PR #879; `teardown/nioh/README.md`, `docs/research/NIOH2-SYSTEMS-2026-10-23.md`, open PR #882; `teardown/wrestling-empire/README.md`, open PR #884; `docs/research/MK-*.md`, open PR #940 (Kreate-A-Fighter); `docs/research/FO3-CREATION-2026-10-23.md` | docs | Creation UX and taxonomy research. FPW decompiled privately (`game-reverse-engineering#53`, per `docs/tech/GAME-SOURCE-QUEUE.md`). FO3 records "no body-shape sliders at creation" | No body meshes or morph data |

### 2.3 Open-source parametric and suite code

| Source | Path | Contents | State |
|---|---|---|---|
| MB-Lab templates | `customization/templates/` (14 files, 76.9 MB) | 9 baked bodies (3 Heavyweight / 3 Cruiserweight / 3 Women's) named after No Mercy body types. `face-presets.json`, `skin-tones.json`, `face-parts.json` | Static, **0 morph targets**, 71-joint MB-Lab skeleton, AGPL-3.0 |
| MPFB2 morph map | `customization/body-morphs/MANIFEST.json`, `apply_mpfb_morphs.py`; fetch script `tools/mpfb2/fetch-mpfb2.sh` | 13 body dials (height, bulk, muscle, fat, shoulders, belly, limbs, chest, waist, hips, neck, hands, feet) and 12 face dials → MPFB2 target files. Targets are CC0, code is GPL-3.0 | **No MPFB checkout in repo.** No GLB in repo carries `MPFB_*` shape keys. **Defect:** `apply_mpfb_morphs.py` builds its KD-tree from the *target* mesh and queries it with the same target verts, so `nearest[i] == i`. MPFB deltas are applied by coincident vertex index, not by surface correspondence. It must not be used until fixed. |
| GNM face | `customization/face-morphs/MANIFEST.json`, `tools/gnm/` | 20 semantic expression params and presets (Apache-2.0) | Expressions, not body shape |
| Suite package | `packages/creation-suite/` (78 files) | `src/`: `body.js` (procedural morphs), `dna.js`, `rigswap.js` (re-bind parts to the live rig by bone name, refuses below 90% coverage), `slotmap.js` (Tekken slot spine), `t7layout.js`, `t7material.js`, `catalogs.js`, `parts.js`, `attire.js`, `layering.js`, `morphs.js`, `facemorphs.js`. Hand-built UIs in `ui/` and `ui2/` | UI is NON-COMPLIANT (README banner) |
| Flagship + legacy suites | `customization/creation-suite-ui/` (18 files), `customization/create-fighter/` (27 files) | Hand-built menus. `menu-data.js` trees tagged with guide sources | Hand-built, outside `game/ui_sources.json` |
| Other part libraries | `customization/parts/hair` (49), `accessories` (13), `kaykit-adventurers` (31), `customization/decal-library` (79), `eye-library` (5) | CC0 and WH parts | Usable as attachments |
| Extract tools | `tools/extract/t7/` (`extract_pak.sh`, `t7_decrypt.py`, `t7_tkdata.py`, `t7_customize.py`, `t7_motbin_to_json.py`, `convert.py`), `tools/t7-extract/`, `tools/depot-pull/` (T7 filelists), `tools/retarget/`, `tools/auto_rig/`, `customization/tools/` (converters for No Mercy, Def Jam, WMXIX) | — | In repo |

---

## 3. Which source body and rig to use

**Decision: a Tekken 7 base body on the shared T7 skeleton (`SKT_CH_base_Skeleton`).** Build it from the owner's own Steam extraction.

Why T7:
1. It is top data priority (T7 is in the T5/6/7/8/TTT2 set), and it is the only priority game where real skinned body parts are actually held: 200 SK GLBs.
2. Every T7 fighter, and every T7 customization item, binds to **one shared skeleton**. Topology is identical across characters; only proportions differ (`tools/retarget/README.md`, `tools/retarget/tekken_skeleton_base.json` source note, `teardown/tekken7/rigging-reference/tekken7-hand-arm.md`). A template on that skeleton therefore takes T7 parts natively. Swapping is already proven privately: "Lee assembled from bdl + bdu + fac + har (92–100% coverage), then Paul's upper body (97%) swapped onto Lee" (`docs/tech/CREATION-SUITE.md` §1).
3. T7 animations from the private `mothead/bin/<code>mot.bin` banks bind to that skeleton without a cross-rig retarget. That is the data-priority path; T3 banks become the logged fallback.

What T7 does **not** give us:
- A single neutral "create-a-fighter" body mesh has not been located. The pakchunk0 export holds per-character 1P costume parts only. However, the generic `skin/male/*` and `skin/female/*` texture sets in `Character/Common` show that a shared generic body skin layout exists. **MISSING:** any `SK_*` or `SKT_*` asset under `TekkenGame/Content/Character/Common/`. It was unpacked but never exported. The unblock is step B2.
- Generic (`cmn`) items. None are in pakchunk0. The skull mask came from the TR205 arcade tree, where each generic item ships as **per-character fitted variants** (43 `SK_CH_<code>_hef_skull` meshes). That is how T7 fits one item to different bodies, and it shapes the morph design in §4.

Fallbacks, in order, if B1–B3 fail. Each is real data, not invented:
1. Assemble a T7 base from one character's 1P parts (`bdu` + `bdl` + `fac` + `har`), choosing the parts the probe in B1 shows are bare-skin regions on the generic `T_CH_male_*` or `T_CH_female_*` materials.
2. WWE 2K19/2K22 default CAW bodies (slots 256 male / 257 female per `customization/wwe2k-caw/PULL-PLAN.md`). This needs the pull and `.pac` decode.
3. The MB-Lab bakes already in `customization/templates/meshes/`. They are not Tekken or WWE, are AGPL, and use the wrong skeleton, so this is the last resort and must be reported as such.

The Mixamo `Soldier.glb` is not a candidate.

---

## 4. Body-shape morphs: where real ones exist

**Plainly: no real body-shape blendshapes exist anywhere in this repo today.** Every body GLB inspected has 0 morph targets: `Soldier.glb`, all 9 MB-Lab templates, the No Mercy parts and the T7 skull mask. T7's customize data has **no body-shape slider table**. The five customize tables `t7_customize.py` parses are items, palette, colour rules, character list and presets. The only body-wide codes are 18 (`suntan` = skin tone, 44 records) and 19 (`mirror`, 52 records) (`packages/creation-suite/src/t7layout.js`). Whether T7 SK meshes carry UE morph targets at all (for example facial) is **unverified**. B1 checks it.

So the template gets its shape variety from these sources, in this order. No slider is invented here. Each option names where its slider list comes from.

| # | Option | What is real | Slider list source | Status |
|---|---|---|---|---|
| M1 | **WWE 2K CAW body morph targets** (owner-named source) | `pac/edit/bbtemplate.pac`: "male/female base bodies + morph targets" (2K19, community-documented). 2K22 has a Body Type select plus Face Deformation sliders (PR #881 §2.2–2.3) | The morph names in the pulled `bbtemplate.pac` itself. Until then the list is **MISSING**, and the 2K19 breakdown's names (height, weight, muscle definition, shoulder width, chest, waist, arms, legs: `CAW-SUITE-BREAKDOWN.md`) are a checklist, not data | **Needs pull + RE.** Owned on Steam (2K19 / 2K20 / 2K22). 2K19 has mature `.pac` tools (PAC Editor / rePac / Genesis). The 2K22 chunk codec is undocumented (likely Oodle per SteamDB). Puller per `docs/tech/STEAM-LIBRARY.md`: Muse for 2K22/2K20, Grok for 2K19. |
| M2 | **T7 per-character body frames** (Tekken's own way to vary bodies) | 38 characters' real bodies on one topology. Generic items ship as per-character fitted variants | Discrete "frame" pick = the extracted character codes. No interpolation | **Available privately now.** Gives real body variety with zero morphs. Parts must use the variant fitted to the chosen frame when one exists (rigswap coverage check). |
| M3 | Real proportion ranges from T7 skeletons | Per-character `SKT` rest poses (e.g. `SK_CH_kin` vs `SK_CH_jin` in `tekken_skeleton_base.json`'s source) | Bone-length deltas between real characters | **Derived.** Blending between two real rest poses is interpolation, so it needs owner OK before shipping. |
| M4 | No Mercy body types as presets | 14M + 9F body types, 220 segment meshes | `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md` | Real names and segment geometry. Proportion ratios can be **measured** from the segment meshes, but that measurement hasn't been done. |
| M5 | Open-source morphable body: **MPFB2** (CC0 targets and base mesh, GPL-3 code) | Artist-made MakeHuman targets. The dial→target map already exists in `customization/body-morphs/MANIFEST.json` | That MANIFEST, mapped to MPFB target files | Not Tekken or WWE data, so owner approval is needed. Two safe uses: (a) as the template mesh itself, where targets apply by native vertex index; or (b) transferred onto the T7 body only after `apply_mpfb_morphs.py` is fixed to map through MPFB `base.obj` positions with alignment. Today's script is broken (§2.3). |
| M6 | MB-Lab | Real morph database (AGPL) | `mb_lab.morphs` in `body-templates.json` | Bakes only. No live shape keys, wrong skeleton. Keep as fallback. |

Recommendation: ship **M2 now**: frame choice from real T7 bodies plus the T7 part swap. Pull **M1** as the real slider source. Treat **M5** as an owner decision, not a default. Face shape follows the same rule: WWE 2K22 Face Deformation and Face Template (M1) first, GNM (`customization/face-morphs`) only as a labelled non-Tekken/WWE fallback.

The existing procedural `cs_<region>` morphs (`packages/creation-suite/src/body.js`) stay as they are. They are not extended and not used for new art (`RULES_NO_GUESSING.md` rule 5).

---

## 5. Part-slot system, mapped from Tekken customization

The spine already exists in code: `packages/creation-suite/src/slotmap.js` `SPINE` and `t7layout.js` `T7_SLOTS`. Record counts below are from `customize_item_data.bin`. Conflicts are from `customization/parts/tekken/tekken7-slot-catalog.json`.

| Owner's group | T7 slot (code, mesh token, records) | Conflicts (T7) | Other-game source for gaps |
|---|---|---|---|
| **Head** | HEAD (1, `hed`, 1,260) · HAIR (2, `har`, 883) · FULL_HEAD (3, `hef`, 514) · HAIR_ACC (4, `oph`, 2,200) · GLA (5, `gla`, 1,660) · FACE (6, `fac`, 58) · FACE_HAIR (7, `fah`, 85) · MAKE_UP (8, `fam`, 459, texture class) | FULL_HEAD ↔ HEAD / HAIR / FACE / HAIR_ACC / GLA / FACE_HAIR | T6 hair categories `Hair - Back` / `Hair - Front (Right)` (NTXL strings, `teardown/tekken6-customization-research.md` §3) |
| **Upper** | UPPER (9, `bdu`, 2,103) · FULL_BODY (10, `bdf`, 311) | FULL_BODY ↔ UPPER / LOWER | T6 Upper Inner/Outer (`SPINE` 9a/9b) |
| **Lower** | LOWER (11, `bdl`, 1,150) | LOWER ↔ FULL_BODY | — |
| **Hands** | *No T7 slot.* Hands ship inside the 1P body parts (to verify in B1) | — | T6 Hands slot (`SPINE` `hands`, `t7: 'H'`). T6 meshes are not decoded |
| **Feet** | *No T7 slot* | — | T8 footwear slot (`tekken7-slot-catalog.json` → `tekken8_additions`; T8 not owned). T6 Feet (`SPINE` `feet`). WWE 2K22 Boots/Shoes (PR #881) |
| **Accessories** | UPPER_ACC (12, `opu`, 4,984) · LOWER_ACC (13, `opl`, 1,487) · EXTRA (14, `exp`, 10) | — | T8 "2 accessory slots" (`tekken7-slot-catalog.json` → `tekken8_additions`) |
| Effects (not body) | EFFECT (15, `unique`, 3,534) · AURA (17, `aura`, 2,652) | — | — |
| Body-wide | SKIN TONE (18, `suntan`, 44) · MIRROR (19, `mirror`, 52) | — | WWE 2K22 Skin Colour |

Colour: up to 5 colour slots per item (schema), 3 layers base/sub/trim on a 144-swatch 12×12 palette with brightness clamps from `customize_color_rules` (`t7layout.js`). Scope: `PlayerCusID` 0 = generic, 1/2 = character (schema).

Swap mechanics: T7-style re-bind by bone name (`rigswap.js`), not socket attach, whenever the part is on the T7 skeleton. Socket attach (`parts.js` / `attire.js`) stays for non-T7 parts. The in-game consumer (`game/js/customization-consumer.js`) currently socket-attaches only, so it needs a rigswap path (step B6).

---

## 6. Mapping the template rig to the game's canonical skeleton

The game's animation contract (`game/js/t3anims.js`):
- `T3_BONES` (22): `Root, Hips, Spine, Chest, Neck, Head, Left/RightShoulder, Left/RightArm, Left/RightForeArm, Left/RightHand, Left/RightUpLeg, Left/RightLeg, Left/RightFoot, Left/RightToeBase`.
- Banks were baked on the **WH-Canonical-22** identity-rest rig (`lab/skeleton/canonical_skeleton.json`). Each bank ships a `wh-anim-skel/1` `skeleton.json` (e.g. `game/assets/anim/t3/jin/skeleton.json`, 18 joints, root `Root`, faces +Z, character left = +X).
- `retargetT3Clips()` converts bank clips into each rig's own bone names and rest frame. On Mixamo-style rigs, `Chest` lands on `Spine2`.

T7 → canonical. All of this already exists in the repo:

| T7 (`SKT_CH_base_Skeleton`) | Game canonical | Where it is defined |
|---|---|---|
| `Base` | `Root` | `tools/retarget/tekken-bonemap.json` `tekken7_to_wh_canonical` |
| `Hip` | `Hips` | same; runtime `game/js/assets.js` `SLICE_T3_BONE_REMAP` |
| `Spine1` | `Spine` | same |
| `Spine2` | `Chest` | same |
| `Neck`, `Head` | `Neck`, `Head` | already T3-named |
| `L_/R_Shoulder`, `_Arm`, `_ForeArm`, `_Hand` | `Left/Right…` | same |
| `L_/R_UpLeg`, `_Leg`, `_Foot`, `_Toe` | `Left/Right{UpLeg,Leg,Foot,ToeBase}` | same |
| finger chains `L_Thumb1…R_Pinky3` | Mixamo finger names | `tekken-bonemap.json` `tekken7_to_mixamo49` |

The runtime conversion is already written for T7 rigs (`assets.js`, the `T7_RIG_URLS` / `PRIVATE_T7_RIGS` path):
- It reparents `Spine1` under `Hip`. T7's spine is a **sibling** of `Hip` under `BASE`.
- It normalises `MODEL_00`/`BASE` to the canonical root-chain rotation `(-0.7071, 0, 0, 0.7071)`.
- It sets canonical bind locals and recomputes inverse bind matrices.

**Known blocker:** the private Burger re-rig onto Bob's T7 skeleton (232 bones) holds its bind pose but **"in-fight pose collapses (T7->T3 remap/bind-frame issue)"** (`docs/tech/ROSTER-MODEL-AUDIT.md`). The template must clear that same remap before it can be the live `custom` model. Step B5 owns it.

Preferred animation source for the template: T7 motbin (private `tkdata/mothead/bin/*mot.bin` → `tools/extract/t7/t7_motbin_to_json.py`) plays on the T7 skeleton natively. T3 banks are the logged fallback through `retargetT3Clips`, and each use is logged in `docs/anim/PROCEDURAL_AUDIT.md`.

---

## 7. UI layout source for the creation screen

Rule: no hand-made layout. What exists versus what is missing:

| Need | Teardown source | State |
|---|---|---|
| Menu flow and tab structure | T7 customize tables → `t7layout.js` `T7_FLOW` (fighter → attire → region → slot → item → colour → pattern → equip) and `T7_REGION_TABS` (Head / Upper Body / Lower Body / Body / Effects) | **In repo** (data-derived from `customize_item_data.bin` by `tools/extract/t7/t7_customize.py`). Usable as the cited source for structure |
| Slot titles, group order, conflicts, colour slots | `customization/parts/tekken/tekken7-slot-catalog.json` (TKDataPatcher docs in `teardown/tekken7/tekkenmods-docs/files/en/Tekken_7/TKDataPatcher/index.md`) | In repo |
| Palette grid | `customize_palette_color.bin` (144 swatches, private) | Private, parsed |
| Customize-screen art and layout (panels, cursor, item grid, colour picker) | T7 `UI_common/flash/` Scaleform movie for the customize mode | **MISSING.** pakchunk0's UI flash folders are only `SW_UI_CharacterSelect`, `Makuai`, `StageSelect`, `MainMenu`, `HUD_Gauge` and `Result_*`. `Rep_PL_CUS_PANEL_L/R` and `Rep_PL_CUS_CMT_L/R` are player-customization panels on the select/VS screens, **not** the customize editor. The extractor also exported textures only, not the GFx/SWF movie that carries positions. Unblock: B7. |
| Preset bodies | `customize_preset_table_cs_s3.bin` preset names (private, parsed by `presets()`) | Private, names only |
| WWE CAW editor hierarchy | 2K19 `pac/root/createmode*.pac` editor labels (`CAW-STRUCTURE-2026-10-19.md` marks them EXTRACTED). The repo holds only the move-name list | **Editor-label table MISSING from the repo.** Re-export from the same pac into a public label list (names only). `menu-data.js` WWE trees cite player guides, which are not teardown files |
| T8 presentation (owner-stated 25/75 drawer + viewport) | Owner text in `docs/creation-suite/OWNER-DIRECTIVE-2026-10-22.md` and `teardown/tekken8/ui/CHARACTER-SELECT.md` (select only) | T8 not owned. No customize refs held |
| Manifest entry | `game/ui_sources.json` | **No creation or customize screen is listed.** Separately, the gate's `UI_GLOBS` in `tools/ui-sources/check.py` match `packages/creation-suite/*.html` but **not** `packages/creation-suite/ui/*.js`, `ui2/*.js`, `src/menu.js`, `customization/creation-suite-ui/**` or `customization/create-fighter/**`. Reported for MoneyManBusch; this plan does not build a duplicate gate. |

---

## 8. Build steps

Legend: **[REPO]** possible from this repo now · **[PRIVATE]** needs `game-reverse-engineering` access (held data, no pull) · **[PULL]** needs a game-file pull · **[OWNER]** needs an owner decision. Per `CLAUDE.md`, every script below goes under `tools/` in the same PR, each step is its own PR, and the work is pushed as it goes.

**B1. T7 template probe [PRIVATE] — recommended first build step.**
- New tool: `tools/creation/t7_template_probe.py`. It is read-only, prints JSON, and needs no Blender.
- Inputs: the private `teardown/tekken7-steam/pakchunk0/manifest.json` and every GLB it lists under `models/Character/Item/Meshes/<code>/{Upper,Lower,Face,Hair,Head,Full_Body}/…/SK_CH_*.glb`. Example first targets, exact paths from the manifest:
  - `lee/Upper/lee_bdu_1p/Meshes/SK_CH_lee_bdu_1p.glb`, `lee/Lower/lee_bdl_1p/Meshes/SK_CH_lee_bdl_1p.glb`, `lee/Face/lee_fac/Meshes/SK_CH_lee_fac.glb` and `lee/Hair/lee_har_1p/Meshes/SK_CH_lee_har_1p.glb` (the privately proven assembly);
  - `bob/Upper/bob_bdu_1p/…/SK_CH_bob_bdu_1p.glb` and `bob/Lower/bob_bdl_1p/…/SK_CH_bob_bdl_1p.glb` (heavy frame; Burger is Bob-sized per PR #973);
  - `nin/…/SK_CH_nin_{bdu,bdl}_1p.glb` and `asa/…/SK_CH_asa_{bdu,bdl}_1P.glb` (female frames).
- Per GLB it reports: joint names against `tools/retarget/tekken_skeleton_base.json`, **morph-target count and names**, materials and which use `T_CH_male_*` / `T_CH_female_*` generic skin, bounding box, and hand and foot coverage.
- Output: `docs/creation/T7-TEMPLATE-PROBE.md` (names and counts only).
- This answers three things: are there any real T7 morph targets, which parts are bare generic-skin bodies, and is the skeleton consistent.

**B2. Export `Character/Common` bodies and skeleton [PULL, one pak].** Re-run `tools/extract/t7/extract_pak.sh pakchunk0-WindowsNoEditor.pak <work> <dest>` with the UModel loop widened to `TekkenGame/Content/Character/Common/**/SK_*.uasset` and `SKT_*.uasset`. The `-i 'TekkenGame/Content/Character/Common/**'` unpack filter is already there; only the export loop is missing them. Exact asset names are not known; list them with `repak list` first and do not guess. Output goes to the private repo. Disk rules: `tools/depot-pull/DISK-RULES.md` (pak ~20.1 GB, deleted after).

**B3. Assemble template v0 [PRIVATE].**
- From B1/B2 results, build one male and one female base on the T7 skeleton with `packages/creation-suite/src/rigswap.js`. Use a generic `Character/Common` body if B2 finds one; otherwise use the bare-skin 1P parts B1 selects.
- Store them privately as `templates/t7/<frame>/template.glb`.
- Public side: add `customization/templates/t7-templates.json` (ids, frame code, private path, `private: true`, sources). It follows `body-templates.json`'s data-driven schema and mirrors the `PRIVATE_T7_RIGS` pattern.

**B4. Frame selection (M2) [PRIVATE].** Add the other extracted character bodies as frames in `t7-templates.json`. Each frame's parts resolve to that character's fitted variant where one exists. Otherwise run the rigswap coverage check (refuse below 90%) and fall back to socket attach.

**B5. Fix the T7 → T3 runtime remap [REPO + PRIVATE proof].**
- Reproduce the Burger collapse (`docs/tech/ROSTER-MODEL-AUDIT.md`) on template v0.
- Fix the conversion in `game/js/assets.js` (the `SLICE_T3_BONE_REMAP` / `T7_RIG_URLS` path).
- Prove it with `tools/proof-harness/fight.mjs` reaching `"round":"fight"` with no `[pageerror]` under `__WH_PRIVATE_ASSETS`, frames viewed (`AGENTS.md` NO FAST-AND-LAZY LAW).
- Coordinate with other agents editing `game/js` first.

**B6. Wire the template as the created-fighter body [REPO].**
- Make `MODEL_URLS.custom` resolve to the template when `__WH_PRIVATE_ASSETS` is set, the same way as `PRIVATE_T7_RIGS`.
- Public build: keep the current URL until the owner decides what the public fallback is (§9 Q2). Do not silently swap in MB-Lab.
- Replace the `BODY_TYPES` `{h, w}` root scale in `custom-fighter.js` with the saved frame id.
- Add a rigswap path to `customization-consumer.js` for T7-skeleton parts.

**B7. Customize-screen UI source [PULL].**
- Find the customize-mode Scaleform movie in the remaining paks (`pakchunk0_P`, `pakchunk1`, `pakchunk1_P`, per `docs/tech/T7-STEAM-EXTRACTION.md` "Not yet extracted"). Search `UI_common/flash/` names for customize. Export the movie (GFx), not just its textures.
- Record measured rules in `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (sizes and colours, no Namco pixels).
- Add a `screen-create` entry to `game/ui_sources.json` citing those files plus `t7layout.js`'s tables.
- Only then rebuild the creation UI. The existing UIs stay until the rebuild replaces them in a reviewed PR.

**B8. Real body and face morphs (M1) [PULL + RE].**
- Pull WWE 2K19 `pac/edit/` (`bbtemplate.pac`, `default.pac`, `edit.pac`, `ch/`, `body/`) and/or the 2K22 equivalents (`pac\edit\ch`) to the private store. Use the depots in `docs/research/WWE2K-CREATION-SUITE-TARGETS-2026-10-23.md` and PR #881 §1.
- Decode the morph target set. The slider list then comes from the file.
- Transfer onto the T7 template by surface correspondence and record the method. Or offer WWE default bodies (slots 256/257) as a second template family on their own rig, mapped like §6.
- Log every source per `RULES_NO_GUESSING.md` rule 3.

**B9. Fix or retire `apply_mpfb_morphs.py` [REPO, only if the owner picks M5].**
- Map target verts → MPFB `base.obj` verts after alignment and scale. Today the KD-tree is built on the target mesh itself.
- Add a test with a known MPFB target. Ship nothing from M5 without owner approval.

**B10. Housekeeping [REPO].**
- Mark `teardown/tekken7/ui/UI-EXTRACTION-STATUS.md` as superseded by the 2026-10-23 Steam pull.
- Correct the WORKLOG claim about `suite.js` (§1).
- Log the procedural `body.js` / `dna.js` morphs and the `BODY_TYPES` numbers in `docs/anim/PROCEDURAL_AUDIT.md`-style as flagged, not deleted.

### What is in the repo now versus what needs pulling

| Item | In public repo | In private repo (held) | Needs pull / RE |
|---|---|---|---|
| T7 slot schema, slot codes, flow, palette size | ✅ | raw tables ✅ | — |
| T7 skeleton names and map to canonical | ✅ (60-bone community ref + bonemap) | full SK joints ✅ | `SKT_CH_base_Skeleton` asset itself (B2) |
| T7 body parts (1P bdu / bdl / fac / har, 38 chars) | ❌ (by design) | ✅ 200 GLBs | — |
| T7 generic body in `Character/Common` | ❌ | ❌ (not exported) | **B2** |
| T7 generic `cmn` items | 1 (skull mask) | ❌ | other paks / TR205 tree |
| T7 morph targets | ❌ | unknown → **B1** | — |
| T7 customize-screen layout | ❌ | ❌ | **B7** |
| T7 animations on T7 skeleton | ❌ | motbin ✅ | conversion (`t7_motbin_to_json.py` exists) |
| WWE body / face morph targets, default CAW bodies | ❌ | ❌ | **B8** |
| WWE CAW editor labels | ❌ | ? (2K19 createmode pac was read once) | re-export labels |
| T5 / T6 / TTT2 slot parts | T5 whole costumes only | — | T6 mesh decode, TTT2 archive |

---

## 9. Missing (reported, not faked) and owner questions

MISSING:
1. A neutral T7 base-body mesh. Not exported (B2).
2. Any real body-shape morph target (T7 has no body-slider table; WWE not pulled) (B1, B8).
3. The T7 customize-screen layout files (B7).
4. A WWE CAW editor-label table in the repo.
5. A working T7 → T3 in-fight remap on a full T7 body (B5).
6. Hands and feet as separate slots in any held Tekken data.

Owner questions:
- **Q1.** May shape variety ship first as T7 frame choice (M2), with sliders arriving only when WWE morph data is decoded (M1)? Or are MPFB2 CC0 morphs (M5) acceptable as an interim, labelled non-Tekken/WWE?
- **Q2.** In the public build, with T7 assets private, what should a created fighter use? Options: keep the soldier until approved, use an MB-Lab template (AGPL), or a WWE CAW default once pulled.
- **Q3.** Which character bodies are allowed as frames? The private extraction holds 38 codes.

---

## 10. Crew work in flight (open PRs touching creation and customization, 2026-10-24)

| PR | Title | Relevance |
|---|---|---|
| #881 | docs: WWE 2K22 creation-suite / animation / rig format research | WWE morph and parts source map; says 2K22 rig format needs the pull |
| #710 | worker65: WWE CAW drives the creation suite (menu logic) | Adds WWE / SC / Def Jam / No Mercy / WMXIX trees to the hand-built `menu-data.js`. Guide-sourced, so it would need teardown sources under the no-hand-made-menus law |
| #709 | Clothing remove/change system + labeling standard (worker 64) | Per-mesh visibility layers; touches `packages/creation-suite/ui/*` and `game/js/assets.js` |
| #711 | In-suite hand-tooling with headless Blender backend | Suite tooling |
| #712 | Worker 61: owner-repo mining (customization parts) | AshLane parts into `create-fighter/data/PARTS-INDEX.json` |
| #940 | MK Armageddon Kreate-A-Fighter research | KAF taxonomy (docs) |
| #879 / #882 / #884 | Fire Pro / Nioh / Wrestling Empire research | Creation research (docs) |
| #973 | Canon sizing: per-version height+girth, Burger Bob-sized | Height and girth scaling; must not fight frame choice |
| #863 (draft) | T7 Steam extraction #1 (public copy) | **Abandoned, must not be merged.** Its `manifest.json` is the listing this plan cites |
| #849 | cyborgx 52-bone rig + T8 extraction tools | T8 tooling (T8 not owned) |
| #826 | T7 character select rebuild | Teardown-sourced UI precedent (`ui_sources.json` screen-select) |
| #718 | T5/T6/TTT2/T7 teardown completion report (MERGE FREEZE) | Status |
| #446 | Tekken 6 PSP SOLVED (sector cipher) | Could unblock T6 hands/feet/hair meshes |
| #968 | TTT2 take-2 surgical carve + XDVDFS listing | TTT2 item data path |

Other plans found:
- `docs/decisions/2026-10-22-creation-suite-teardown-blueprint.md`, on PR #710 only: "template select (WWE base bodies, never Mixamo)".
- `docs/tech/CREATION-SUITE.md`: T7 structure, rigswap, private catalog.
- `WORKLOG.md` 2026-10-22 "Mixamo soldier killed" (contradicted by main, §1).
- `AGENTS.md` / `docs/handoffs/MUSE_CONTINUE_WESTERN_HEART.md`: the CI gate is owned by MoneyManBusch. The live gate is `.github/workflows/ui-sources.yml`.

---

## 11. Sources read for this plan

`AGENTS.md`, `CLAUDE.md`, `docs/RULES_NO_GUESSING.md`, `docs/creation-suite/OWNER-DIRECTIVE-2026-10-22.md`, `docs/tech/T7-STEAM-EXTRACTION.md`, `docs/tech/CREATION-SUITE.md`, `docs/tech/ROSTER-MODEL-AUDIT.md`, `docs/tech/STEAM-LIBRARY.md`, `docs/tech/GAME-SOURCE-QUEUE.md`, `docs/tech/T78-FULL-INTEGRATION.md`, `docs/research/T7-EXTRACTION-PIPELINE-2026-10-23.md`, `docs/research/WWE2K-CREATION-SUITE-TARGETS-2026-10-23.md`, `docs/research/WWE-CAW-EXTRACTION-STATUS.md`, `docs/research/CREATION-TOOLCHAIN-MBLAB-GNM-MPFB2.md`, `docs/research/SKELETON-VARIANTS-2026-10-23.md`, `docs/research/FO3-CREATION-2026-10-23.md`, `docs/research/NIOH2-SYSTEMS-2026-10-23.md`, `docs/creation-suite-ui-v2-survey/tekken-frontend-inventory.md`, `customization/parts/{tekken,tekken5,tekken6,tekken7,no-mercy}/*`, `customization/templates/*`, `customization/body-morphs/*`, `customization/face-morphs/MANIFEST.json`, `customization/wwe2k-caw/*`, `customization/DEFJAM-CAW-WIRING.md`, `teardown/tekken7/**` (docs), `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md`, `teardown/{ttt2,tekken6}-customization-research.md`, `teardown/{tekken5,tekken-tag-tournament-2}/ui/UI-EXTRACTION-STATUS.md`, `teardown/wwe-2k/WWE2K-PULL-STATUS.md`, `teardown/wwe2k19|22/README.md`, `teardown/def-jam-fight-for-ny/TEARDOWN.md`, `tools/extract/t7/*`, `tools/retarget/{README.md,tekken-bonemap.json,tekken_skeleton_base.json}`, `tools/ui-sources/check.py`, `game/ui_sources.json`, `game/js/{custom-fighter,assets,fighter,t3anims,customization-consumer}.js`, `packages/creation-suite/{README.md,src/*.js}`, `customization/creation-suite-ui/js/suite.js`, `customization/create-fighter/{README.md,js/*.js}`, `lab/skeleton/canonical_skeleton.json`, `game/assets/anim/t3/jin/skeleton.json`, open PRs #863 (manifest), #881, #710, #709, #712, #940, #879, #973 (via the GitHub API).
