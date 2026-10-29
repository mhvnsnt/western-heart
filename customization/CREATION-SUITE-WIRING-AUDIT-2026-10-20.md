# Creation Suite — Wiring Audit + Gap Map (2026-10-20)

**Owner order (2026-10-20, creation systems pass, re-issued ~19:44 CDT and
confirmed ~20:31 CDT):** pull together every character-creation/customization
system in our teardown files — Tekken, WWF No Mercy CAW, WrestleMania XIX CAW,
WWE 2K creation, Def Jam creation, plus any other torn-down game with a
creation system — at the highest industry standard we have, wired toward ONE
mobile, user-friendly suite with Tekken/WWE-style UI taken straight from the
teardowns' own files and layouts.

**Scope of this document:** audit + gap map only. It is the handoff the
building lanes work from. Building ownership today (checkpoint
`creation-suite-pass.json`, updated 2026-10-20 19:55 CDT): Worker A =
WMXIX inventory/conversion, Worker B = bake pipeline + schema + game
assets.js hook, Worker C run 4 = `creation-suite-ui` app/catalog/docs
(branch `feat/cs-ui-wiring-20261020`). This audit does not duplicate them;
where a piece below names one of those lanes, that lane owns it.

**Method:** every claim below was read directly from `mhvnsnt/western-heart`
main via the GitHub API on 2026-10-20 (file listings, raw file reads, and
full JSON parses of the three parts indexes and `PARTS-REGISTRY.json`).
Anything I could not verify first-hand is marked **[UNVERIFIED]** or
**[CLAIM]** with its source. Evidence discipline: a path or it didn't happen.

---

## 0. The headline numbers

| Catalog | Entries | Loaded by suite runtime? | Engine-ready geometry |
|---|---|---|---|
| `customization/PARTS-REGISTRY.json` (the canonical registry) | 1,148 parts | **Yes** — `packages/creation-suite/src/parts.js` `loadRegistry()` | 6 parts classified `mesh_part` |
| `customization/parts/PARTS-INDEX.json` | 3,398 parts | **No** — no code path found loads it | 303 `.obj`, 392 `.png`; 2,670 are GameCube `.tex`/`.ymg` binaries |
| `customization/parts/defjam/PARTS-INDEX.json` | 22,360 parts | **No** | 0 — all PS2 `.o`, files live in another repo |
| `customization/parts/tekken/PARTS-INDEX.json` | 26 parts | **No** | 0 separable parts — full-body FBX models |
| **Total indexed part records** | **25,784** | runtime sees **1,148 (4.5%)** | — |

Registry classification gap (parsed first-hand): of the 1,148 registry
parts, **1,120 have `kind: null`** and **1,111 have `part_class: null`**.
Only 28 parts carry a `kind` (eye 7, decal_logo 5, full_reskin 3, tights 2,
pants 2, top 2, hair 2, eye_lenses 1, mask 1, cowl 1, gauntlets 1) and only
37 carry a `part_class` (texture_part 31, mesh_part 6). The runtime's own
`PART_CLASSES` are `texture_part`/`mesh_part` — so ~97% of the registry is
invisible to class-based queries (`entriesForClass`) today.

---

## 1. Inventory by source system

### 1.1 The suite runtime + apps (Western Heart native)

- **Runtime:** `packages/creation-suite/src/` — 11 modules (`attire.js`,
  `body.js`, `dna.js`, `facemorphs.js`, `index.js`, `layering.js`,
  `menu.js`, `morphs.js`, `parts.js`, `regions.js`, `secondary.js`) plus
  `test/` and `proof/`. `parts.js` is the registry consumer: `loadRegistry`,
  `entriesForSlot`, `entriesForClass`, `entriesForLibrary`, `usableOn`
  (mesh parts fit any rig via bone sockets; texture parts need a
  `character_mappings` entry). It fetches **only** `PARTS-REGISTRY.json`.
- **Two UI apps exist.** `customization/creation-suite-ui/` is the flagship
  (the game's own code comment in `game/js/custom-fighter.js` calls it
  "the flagship Creation Suite"; `js/suite.js` 31,469B, `menu-data.js`,
  `viewer3d.js`; saves profile key `wh_creation_suite_v1`).
  `customization/create-fighter/` is the legacy app (saves
  `wh_create_fighter_v1`). Worker C run 4 owns the flagship app.
- **Game consumer:** `game/js/custom-fighter.js` (3,660B) reads saved
  profiles from localStorage (suite key first, legacy fallback), maps a
  `BODY_TYPES` preset table (duplicated from the legacy app — drift risk),
  and builds a roster fighter on a `Soldier.glb` base. **It applies no
  registry parts** — no `loadRegistry` call; `customization/mat-legends-caw.json`
  admits the same in its `_meta`: "it does not yet read this part catalog."
  The bake path that turns a profile into a dressed GLB is
  `customization/tools/apply_customization.py` (32,285B) under the
  `customization.json` v1 schema (`customization/CUSTOMIZATION-JSON-SCHEMA.md`)
  — Worker B's lane, including the `assets.js` game hook.
- **Suite docs already in repo:** `customization/SYSTEMS-WIRING.md` (the
  wiring map this audit supersedes in detail), `CHARACTER-CREATION.md`,
  `UNIFIED-UI-SPEC.md` (synthesized UI spec — see §3), `CUSTOMIZATION-LIBRARY-LAYOUT.md`,
  `CUSTOMIZATION-RESEARCH.md`, `CUSTOMIZATION-FILES-INDEX.json` (149KB file
  index; not deep-parsed in this audit).

### 1.2 WWF No Mercy (N64, AKI) — the most complete creation dataset

- **Teardown:** `teardown/wwf-no-mercy/` — `TEARDOWN.md`,
  `WIRING-INVENTORY.md`, `CANON-CONVERSION.md`, `CAW-SAVE-RECORD-STATUS.md`
  (the CAW save-record format work), models/textures/animations/recomp.
- **UI evidence (primary source):** `teardown/wwf-no-mercy/re-docs/docs/ui/menus/`
  — `edit-a-superstar.md` (**21,431 bytes**, the full Edit-a-Superstar flow),
  `main-menu.md` (7,618B), `superstar-select.md` (3,300B).
- **Parts on disk in the suite tree:** `customization/parts/no-mercy/`
  (`attire_parts/`, `body_parts/`, `face/`, `faces/`, `skins/`, `weapon/`,
  `manifest.json` 769,672B). `parts/PARTS-INDEX.json` carries **682 No Mercy
  parts** (of the index's slot counts: faces 348, skins 233, bodies 220 are
  dominated by No Mercy + WMXIX — see §1.3); across the whole index there are
  **303 `.obj` geometry files** (the No Mercy extractions) — OBJ is directly
  consumable/convertible with standard tooling, unlike the GameCube/PS2
  binaries below.
- **Registry exposure:** only **35** of the 682 indexed No Mercy parts appear
  in `PARTS-REGISTRY.json` (5.1%), as the `no-mercy` library pointing at
  `parts/PARTS-INDEX.json` for its manifest.
- **State:** extracted ✔, decoded (OBJ + textures) ✔, indexed ✔,
  **wired into the suite: NO** (no runtime loader for the index; 35/682 in
  the registry, unclassified like the rest).

### 1.3 WrestleMania XIX (GameCube, AKI/Yuke's) — biggest in-repo catalog, unconverted geometry

- **Teardown:** two trees — `teardown/wmxix/` (the working teardown:
  `TEARDOWN.md`, `WIRING-INVENTORY.md`, `caw-parts/`, `catalog_caw.py`,
  `decode_tpl.py`, `extract_yanm.py`, YANM cycle docs) and
  `teardown/wwe-wrestlemania-xix/` (assembly/skeleton solution docs).
- **CAW catalog:** `teardown/wmxix/caw-parts/CATALOG.md` + `files.tsv`
  (158,114B) catalog **2,690 part files**; `customization/mat-legends-caw.json`
  indexes them by category: Man 670, Woman 543, Face 351, Upper_Body 218,
  Face_op 208, Gears 149, Lower_Body 142, Shoes 84, Hair 70, Wrist 60,
  Gloves 50, common 50, 64gara 41, Knee 24, Elbow 22. Extensions: `.tex`
  1,470, `.ymg` 1,200, `.ycg` 8, `.ymm` 3, misc.
- **Format state (from `mat-legends-caw.json`, verified as written there):**
  YOBJ v00030001 ×754 + v00040001 ×175 + v00040002 ×32 + v00040003 ×31 =
  **992 parts carry real geometry** (same YOBJ family as the solved wrestler
  assembly, `assemble_wrestler_v2`); **202 DUMY placeholders carry no
  geometry**. Texture parts are GameCube TPL/`.tex` — `teardown/wmxix/decode_tpl.py`
  is validated (mean abs diff 4.2/255 vs artist source). The part *files*
  themselves live on the ISO/release side (54.3MB, streamed 2026-10-13) and
  are cataloged, not duplicated, per the index `_meta`.
- **Registry exposure:** 1,050 of 2,690 in `PARTS-REGISTRY.json` (39%) — every
  one an unconverted binary; a sampled registry entry's own `conversion`
  field reads: ".ymg GameCube binary — decode to GLB before in-engine use."
- **State:** extracted ✔, cataloged ✔, geometry format solved for wrestlers ✔,
  **part-level `.ymg`→GLB conversion: NOT LANDED.** Worker A owns this
  converter; per `creation-suite-pass.json` (19:55 CDT) A's
  `customization/parts-converted/CATALOG.json` is **absent on main** and A is
  "RUNNING but UNVERIFIED — check-in demanded." **[CLAIM — checkpoint]**
  First-hand check this audit: no `parts-converted/` directory exists under
  `customization/` or `customization/parts/` on main. ✔ (absence verified)

### 1.4 WWE 2K (2K14–2K19+) — documentation only, zero assets (by design boundary)

- **In-repo:** `customization/wwe2k-caw/` — 8 docs (`CAW-SUITE-BREAKDOWN.md`,
  `CAW-STRUCTURE-2026-10-19.md`, `COMBINED-CREATION-SUITE.md`,
  `MOVESET-LIBRARY-2026-10-19.md`, `PARTS-CATALOG.md`, `PULL-PLAN.md`,
  `TRANSFER-PLAN-2026-10-19.md`, `AUDIT-2026-10-19.md`) + `moveset-library-2k19.txt`
  (100,315B). `teardown/wwe-2k/` — `CATALOG.md`, `WWE2K14-DLC-CATALOG.md`,
  acquisition specs only.
- **`AUDIT-2026-10-19.md` states it plainly:** "Actual 2K18/2K19 game assets
  in western-heart: **ZERO. Nothing pulled.**" Commercial files are
  documented-but-not-pulled per standing law (no cracking/paywall bypass);
  acquiring them is an owner decision, not a lane decision.
- **What substitutes for 2K depth today:** CC0 pulls — KayKit Adventurers
  (14 parts, `customization/parts/kaykit-adventurers/`), Quaternius CC0 hair
  (8 pieces + eyebrows, `customization/parts/hair/`), chain accessories.
  The 2K *system design* (8 editors, layered attire, per-item color/material,
  logo placement) is fully documented in `CAW-SUITE-BREAKDOWN.md` and is UI
  evidence (§3), not data.
- **State:** researched ✔, **extracted: NO (never), wired: design-level only.**

### 1.5 Def Jam: Fight for NY (PS2, AKI/EA) — the largest creation dataset, cross-repo and unconverted

- **Index in WH:** `customization/parts/defjam/PARTS-INDEX.json` (6.9MB) —
  **22,360 parts**, all `source_game: defjam`, all PS2 `.o` format, slots:
  upper_body 14,430, lower_body 5,850, accessories 1,625, head 455.
  Index `format_note`: "PS2-native; requires conversion for web rendering."
- **The files are NOT in western-heart.** Every `file_path` points at
  `teardown/def-jam-fight-for-ny/models/caw-parts/…` with `"repo":
  "mhvnsnt/wrestling-game"`. First-hand checks this audit: that path
  **404s in western-heart**; the same path **exists in `mhvnsnt/wrestling-game`**
  (sampled: `V2CP_110_0001_A.o`, `_B.o`, `_C.o` present).
- **WH teardown side:** `teardown/def-jam-fight-for-ny/` — `TEARDOWN.md`
  (142 fighters/48 venues per PR #216), `EAGL-FORMAT-ANALYSIS.md` (the PS2
  EAGL container analysis — the format the `.o` parts use),
  `ISO-MANIFEST.md`, `surgical/`, `tools/`. The Def Jam ISO itself is still
  completing under the teardown sweep (was ~31.5% at last verified count) —
  but the CAW parts already exist in wrestling-game, so creation wiring does
  not have to wait on the ISO.
- **State:** indexed ✔ (in WH), files extracted ✔ (in wrestling-game),
  decoded ✘ (`.o`→web conversion does not exist), wired ✘ (nothing in WH
  references the index at runtime; the index isn't even in the registry's
  libraries).

### 1.6 Tekken (T3 / T6 / T7 / TTT2) — slot schema wired, no item data yet

- **Slot catalogs (data, in-repo):** `customization/parts/tekken/` —
  `tekken7-slot-catalog.json` (9,803B; T7's 16-slot schema, slot group IDs,
  21-field item CSV spec, asset prefixes, conflict rules, color system per
  `SYSTEMS-WIRING.md`), `tekken6-slot-catalog.json` (1,729B),
  `ttt2-slot-catalog.json` (1,761B), `MANIFEST.json`, small `PARTS-INDEX.json`.
  `SYSTEMS-WIRING.md` calls the T7 catalog "wired" — **[CLAIM, qualified]:**
  the file exists and is valid schema data, but this audit found **no
  runtime consumer** of the slot catalogs in `packages/creation-suite/src/`
  (`parts.js` reads only `PARTS-REGISTRY.json`). Schema-present ≠ wired.
- **Item data:** `customization/parts/tekken/PARTS-INDEX.json` = 26 entries,
  all full-body Tekken 7 FBX models (`slot: full_body`, paths in the
  game-reverse-engineering repo) — base bodies/references, **not separable
  customization items**. T7 item meshes (`.uasset`) not pulled (per
  `SYSTEMS-WIRING.md`, pending the T7 pull).
- **Tekken 6 PSP:** `teardown/tekken6/` present (TEARDOWN.md, decrypted
  bank, models/ui dirs); its extracted files are **unsearched for
  item/equipment tables** (`SYSTEMS-WIRING.md` names this as the next step;
  still true — no T6 item catalog exists anywhere in the repo). The teardown
  sweep's T6 lane (PR #388, CL repeat semantics) is RE work, not item-table
  extraction. Research docs: `teardown/tekken6-customization-research.md`,
  `teardown/ttt2-customization-research.md`.
- **Tekken 3:** teardown complete and movesets wired (PR #382), but T3 has
  no item-customization system to wire (palette/attire-era) — nothing owed.
- **State:** schema ✔, **items: none extracted, runtime consumption: none.**

### 1.7 DOA wardrobe (Dead or Alive 4/6) — named in the UI spec, thin data

- `UNIFIED-UI-SPEC.md` §5.3 mandates a WARDROBE tab on the DOA loadout model
  ("do NOT skip DOA"). Data side: `customization/parts/doa/` exists (contents
  not deep-audited here), `teardown/dead-or-alive-4/` + `dead-or-alive-6/`
  exist; DOA4's own teardown "complete" claim was proven false by the sweep's
  audit PR #381 and is back in progress. DOA costume data is therefore
  **partial and unverified** — flagged, not counted in the totals above.

### 1.8 Western Heart native libraries (eyes, decals, reskins, superhero, hair)

- **Eye library:** `customization/eye-library/` — `MANIFEST.json` + 3 texture
  PNGs (yellow-tiger = owner's universal "I like" variant, blue-snow-leopard,
  classic-original). The manifest's `character_mappings` (pantera, lili,
  zafina, mariposa, jin verified in the file head) are all **texture
  replacements** (`replaces_texture` per character material). Per-character
  eye texture variants also live at `customization/parts/{pantera,jin,lili,zafina,baek,doc-frank}-eyes/`.
- **Owner rule (2026-10-20, after the Deathfang eye rejection — see §3):**
  eyes must be **real placeable mesh parts** (eyeball + eyelashes +
  eyebrows), never texture decals. Against that rule, the entire current eye
  system is **legacy texture-only**. The only mesh-eye asset found in the
  repo: `customization/parts/superhero/spidergirl/spidergirl-eyes.glb`
  (3,596B). Eyebrow geometry exists inside the Quaternius CC0 hair set
  (`parts/hair/`, per `wwe2k-caw/AUDIT-2026-10-19.md`). The registry contains
  **no lash parts at all** and no brow parts as registry entries. Eye-parts
  build is assigned: Worker B (schema/bake treats eye parts as mesh parts) +
  Worker C run 4 (UI/catalog), directives delivered 2026-10-20 ~19:53 CDT
  per `creation-suite-pass.json`. Deathfang (human) is the named test case.
- **Decals:** `customization/decal-library/{baek,lili,mariposa,pantera,zafina}/`
  with per-character manifests + placements (pantera decal set: logo/tights/
  pants parameterized swaps). **Reskins:** `customization/reskin-library/{doc-frank,jin}/`.
  **Superhero pieces:** `customization/parts/superhero/` (batgirl, spaceghost,
  spidergirl dirs + MANIFEST) — original-geometry GLB pieces (mask/cowl/
  gauntlets/eye_lenses kinds in the registry). **Hair:** CC0 Quaternius set +
  toon dread ponytail. **KayKit:** 14 CC0 parts. All of these ARE in the
  registry (they are most of the 28 classified parts) and are the suite's
  only fully-wired part content today.

### 1.9 Body + face morphs

- **Body:** `customization/body-morphs/MANIFEST.json` maps suite sliders to
  MPFB2 (MakeHuman) targets — `face_shape_morphs` groups (eyes/face/mouth/
  nose with named MPFB target paths, e.g. `eyes/eye-scale-decr-incr` →
  `eye_size`) + macro morphs (height…); application via
  `customization/body-morphs/apply_mpfb_morphs.py` (KD-tree). The checkpoint
  records 13 body + 12 face slider mappings. The MPFB2 checkout itself lives
  **outside this repo** (`~/workspace/cape-jones/production/tools/mpfb2`,
  per `creation-suite-pass.json`) — a cross-repo dependency the suite build
  must keep visible. Runtime integration point: `packages/creation-suite/src/body.js` + `morphs.js`.
- **Face:** `customization/face-morphs/MANIFEST.json` (5,238B) + the GNM face
  rig at `customization/tools/gnm/` (per `SYSTEMS-WIRING.md`); runtime:
  `src/facemorphs.js` + `src/regions.js`.
- **State:** manifests + applier + runtime modules exist; **[UNVERIFIED]**
  end-to-end morph proof on a roster fighter inside the suite (Worker B's
  fixture self-proof covers the bake path; the Master White → Kevin
  differentiation is the creation pass's named first proof, Worker D,
  queued after B + C land).

### 1.10 Moveset creation

- **Data:** `moveset-library/` — `MOVESET-EDITOR-RESEARCH.md`,
  `UI-DESIGN-SPEC.md`, `MOVES-LIBRARY.md`; `moveset-library/movesets/`:
  `MOVE-DATABASE.json`, `MOVE-SLOTS.json`, `WMXIX-MOVES.json`,
  `mat-kings-move-database.json`, `pantera-moveset.json`. T7 frame data
  landed via PR #394 (`docs/t7t8-reference/frame-data-t7/*.json`). The other
  session's additive moveset-data merge (548 historical versions, no-loss
  guard) is paused at its session limit, auto-resuming 22:31 CDT — data
  lane, not this audit's.
- **Editor:** the tap-to-assign editor exists as research + UI design spec;
  a wired in-suite moveset editor (tap slot → scroll library → tap assign,
  live preview on the model) has **no lane heartbeat** in
  `creation-suite-pass.json` — flagged UNOWNED in the gap map (§2), pending
  the building chat's sequencing. Owner law is unambiguous (see §3).

### 1.11 Roster attire system (the other half of "creation")

- Fighters live at `roster/<fighter>/` with `attires/` subdirs (verified:
  `roster/pantera/` — IDENTITY.md, attires/, rigged GLB, reskin refs). The
  `customization.json` v1 contract (per `creation-suite-pass.json`
  schema_contract + `CUSTOMIZATION-JSON-SCHEMA.md`) places a per-attire
  `customization.json` in each attire folder: `{version, app, fighter,
  attire, base_glb, out_glb, body, morphs, parts{suite_slot:{part_id, glb,
  placement}}, textures[], colors}`. Options-stacking (§3) is implemented
  as: attires are separate folders/files, never overwritten.
- Attire provenance: PR #391 (open at audit time) is a 101-row
  attire-provenance marking sheet — the roster-side bookkeeping is being
  actively reconciled by another lane; not duplicated here.

---

## 2. Gap map — source system → suite need → concrete wiring step

| # | Source | What the unified suite still needs | Concrete wiring step | Owner / status |
|---|---|---|---|---|
| 1 | **No Mercy parts** (682 indexed, in-repo files, 303 OBJ across index) | Browsable, classified, engine-ready parts the runtime can enumerate | Generate a registry-format No Mercy catalog from `parts/PARTS-INDEX.json`; convert OBJ geometry to GLB; add a runtime catalog loader (registry + catalogs, one enumeration API) | **THIS AUDIT's Phase 1** (§4) — no lane found on it |
| 2 | **WMXIX `.ymg` geometry** (992 real-geometry parts) | GLB parts + converted catalog | `.ymg`→GLB converter (YOBJ family already solved for wrestler assembly) + `parts-converted/CATALOG.json` | Worker A — assigned; **unverified/stalled**: catalog absent on main (verified), check-in unanswered at 19:55 CDT |
| 3 | **WMXIX `.tex` textures** (1,470) | Decoded PNG texture parts | Batch-run the already-validated `teardown/wmxix/decode_tpl.py` over the catalog | Unassigned — pairs with #2; flagged for the building chat |
| 4 | **Def Jam CAW parts** (22,360, in `mhvnsnt/wrestling-game`) | Access from the WH build + a PS2 `.o` (EAGL) → GLB path | Decide the access pattern (cross-repo release vs mirror), then build the EAGL `.o` converter using `teardown/def-jam-fight-for-ny/EAGL-FORMAT-ANALYSIS.md` | **UNOWNED** — largest single dataset; nobody assigned in any checkpoint read |
| 5 | **Tekken 6 item tables** | A T6 item catalog in the T7 slot schema | Grep T6's extracted files for item/equipment tables (named as the next step in `SYSTEMS-WIRING.md`; still not done) | **UNOWNED** — the sweep's T6 lane is RE/decryption, not item extraction |
| 6 | **Tekken slot catalogs** (T6/T7/TTT2 JSON) | Runtime enforcement of slot conflicts + color channels | Load the slot catalogs in the suite runtime alongside the registry | Unassigned — small, well-bounded; flag for building chat |
| 7 | **Registry classification** (1,120/1,148 `kind: null`) | A registry the class/slot queries can actually see | Generated classification pass (index slot → kind/part_class mapping), per source, as catalogs — not hand edits | Partially Worker C (catalog/docs); Phase 1 classifies the No Mercy slice via its catalog (§4) |
| 8 | **Game-side application** | Created fighters wear their parts in matches | Bake (`apply_customization.py`) + `assets.js` hook + fixture self-proof | Worker B — running |
| 9 | **Eyes as real parts** | Eyeball + lashes + brows mesh parts with placement controls | New mesh part set (precedent: `spidergirl-eyes.glb`); schema/bake treats them as mesh parts; Deathfang = named test case | Workers B (schema/bake) + C run 4 (UI) — directives delivered 2026-10-20 ~19:53 CDT |
| 10 | **Moveset editor** | Tap-to-assign editor wired to the move database, live preview | Build per `moveset-library/UI-DESIGN-SPEC.md` against `MOVE-DATABASE.json`/`MOVE-SLOTS.json` | **UNOWNED** as UI; the data merge is the other session's lane (resumes 22:31 CDT) |
| 11 | **Morphs end-to-end** | Suite sliders visibly change a roster fighter via the bake | MPFB2 applier through Worker B's bake; Master White → Kevin differentiation as first proof | Worker B (bake) + Worker D (proof, queued after B + C) |
| 12 | **WWE 2K assets** | Nothing buildable without the commercial files | Owner acquisition call (documented-not-pulled boundary); 2K *design* is already extracted (§3) | **Owner decision** — not a lane gap |
| 13 | **DOA wardrobe** | Verified costume/loadout data for the WARDROBE tab | DOA4 teardown completion first (sweep; its "complete" claim was falsified by PR #381) | Sweep lane; `parts/doa/` not deep-audited here |
| 14 | **Def Jam ISO** | Full game extraction (modes/data beyond CAW parts) | Sweep lane continues the ISO pull | Not creation-blocking — CAW parts already sit in wrestling-game |

**Flagged claims (no path evidence found):**
- `SYSTEMS-WIRING.md` calls the Tekken 7 slot catalog "wired." The JSON
  exists; no runtime consumer was found. Status: **schema present, wiring
  not evidenced** (gap #6).
- Any claim that a WMXIX parts converter/catalog has landed: **false on
  main today** (gap #2; absence verified first-hand).
- `creation-suite-pass.json` reports `customization/parts/` = 3,883 files
  and `PARTS-INDEX.json` indexing 3,398 — the 3,398 figure is **verified**
  (parsed first-hand); the 3,883 file count is **[CLAIM — checkpoint]**,
  not independently recounted.
- DOA4 teardown "complete": **falsified** by PR #381 (see §1.7).

---

## 3. UI layout evidence — from the teardown files, not from memory

The suite's mobile UI must mirror these flows. Every item below names the
file it comes from. The synthesized target spec already in the repo is
`customization/UNIFIED-UI-SPEC.md` (full-screen preview + floating menus;
Fighter Select → Attire Slots → Customization Hub with BODY / ATTIRE /
WARDROBE / PROFILE tabs + MOVESET link → Save/Photo). The extraction
provenance is logged in `customization/creation-suite-ui/UI-EXTRACTION-LOG.md`,
which records per-game verbatim sources and one honest limit, quoted here
because the build lanes must respect it: the actual `.uasset` menu binaries
and pixel layouts are **not** in any teardown we hold — what is verbatim is
the **information architecture** (menu trees, category names, slot IDs, UI
group ordering, conflict rules, color systems, buy/equip flows, slider sets).

- **WWF No Mercy — the profile + edit flow.** `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`
  (21,431B) is the complete Edit-a-Superstar flow; `main-menu.md` (7,618B)
  and `superstar-select.md` (3,300B) give entry and selection. No Mercy
  contributes: the PROFILE page (spec §5.4 "No Mercy page 1"), the
  **4-slot attire system** (spec §4 — four saved attires per superstar, the
  original options-stacking), and the AKI part taxonomy the BODY tab follows.
- **WrestleMania XIX — the part-category taxonomy.** `teardown/wmxix/caw-parts/CATALOG.md`
  + `files.tsv` and `customization/mat-legends-caw.json` give the browsable
  category tree the suite's part browser mirrors: Man / Woman / Face /
  Upper_Body / Face_op / Gears / Lower_Body / Shoes / Hair / Wrist / Gloves /
  common / 64gara / Knee / Elbow. Edit-data specifics:
  `teardown/wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md` (2,276B —
  verified present; a compact data doc, not a full flow transcript).
- **WWE 2K — the editor depth model.** `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`
  §2 (read first-hand): Personal Info → Appearance (Head/Face morph sliders;
  Body type presets + morph sliders; **layered attire** with left/right
  independent arm/leg slots, per-item color channels, material editor, logo
  placement/scale/rotation; tattoos as a full-body placeable canvas) →
  Moveset. The full suite has 8 editors (Superstar, Entrance, Victory,
  Moveset, Championship, Arena, Show, Video, MITB) — Western Heart takes
  Superstar + Moveset + Victory depth, Tekken-style (below).
- **Tekken — the attire spine + transaction flow.** `customization/parts/tekken/tekken7-slot-catalog.json`
  per `UI-EXTRACTION-LOG.md` §1: **17 slots with their real UI titles**
  (HEAD/HAIR/FULL_HEAD/HAIR_ACC/GLA/FACE/FACE_HAIR/MAKE_UP/UPPER/FULL_BODY/
  LOWER/UPPER_ACC/LOWER_ACC/EXTRA/EFFECT/AURA), slot-group IDs (−236..−254 =
  the actual in-game UI group ordering), zone-conflict rules, 0–5 color-slot
  system, and T7's verified behavior: pick fighter → pick slot → category
  list, **buy/equip two-step, hover try-on, exit → photo mode**.
  Tekken 6 PSP subdivisions (extraction log §2, from the T6 teardown):
  Upper Inner/Outer sub-slots, separate Hands slot, separate Feet slot,
  Waist L/R — nested under the T7 spine where they add depth T7 merged away.

**Standing owner rules that bind the build (non-negotiable):**
1. **Moveset editor = tap a move slot → scroll the library → TAP to assign.**
   Never drag-and-drop (owner law 2026-10-18; restated in every lane brief).
   Same tap model for parts/attires.
2. **Options-stacking:** every variant is saved and swappable, never
   overwritten (No Mercy's 4 attires → WH's 10 customization slots on
   select; punch = outfit 1, kick = outfit 2).
3. **Intro/victory live INSIDE customization, Tekken-style** — the fighter
   walks in, says something, interacts, then fights. Not full wrestling
   entrances.
4. **Eyes are real placeable parts** (eyeball + eyelashes + eyebrows, with
   placement controls) — never texture decals. Owner, 2026-10-20, rejecting
   Deathfang's painted eye: "let it be a real eye not just a decal on his
   face from hand tooling." If placement help is needed, the owner places
   eyes himself in the suite — so placement controls must be genuinely
   usable, mobile-first.
5. **Mobile-first:** the owner works from his phone. Tap targets, contained
   scroll regions (the card strip scrolls inside its own box — the same
   rule as the character-select spec), no hover-only interactions (T7's
   hover try-on becomes tap-to-preview).

---

## 4. Wiring Phase 1 (this audit's lane, starting immediately)

**Decision: wire No Mercy first** (gap #1). Rationale, from the evidence
above: it has the most complete extracted creation data in the repo (682
indexed parts with in-repo files, OBJ geometry — the only large part set
already in a standard, convertible format), it is one of the two editor
models the owner explicitly demands (AKI CAW), and **no lane is building
it**: Worker A owns WMXIX conversion, Worker B owns bake/schema/game hook,
Worker C run 4 owns the flagship UI app, the moveset data merge belongs to
the paused session. Per the narrowed stand-down rule, the pieces below are
the ones with no active builder; the moment a heartbeat shows otherwise,
that piece stands down and gets reported.

**Phase 1 deliverables (additions-only PRs, checkpointed per step):**
1. `customization/tools/build_no_mercy_catalog.py` — deterministic
   generator: `parts/PARTS-INDEX.json` (source of truth) → No Mercy catalog
   in registry-entry shape (id, name, source slot → suite_slot, kind,
   part_class, file, format, conversion status).
2. `customization/parts/no-mercy/CATALOG.json` — all 682 No Mercy parts,
   classified (this also closes the No Mercy slice of gap #7 without
   hand-editing the shared registry).
3. OBJ→GLB conversion for the No Mercy geometry parts (committed converter
   script; GLBs beside the catalog) so the parts are engine-ready, with a
   conversion report (converted / skipped / why).
4. `packages/creation-suite/src/catalogs.js` — NEW runtime module: loads
   the registry plus named per-source catalogs and exposes one enumeration
   API (by slot / class / library / source, conversion status visible), so
   any UI — flagship or future — browses all wired catalogs, not just the
   registry's 4.5%. Plus a test under `packages/creation-suite/test/`
   proving enumeration counts against the real files.
5. Proof: a sample No Mercy part traced end-to-end — index entry → catalog
   entry → converted GLB → enumerated by the runtime test.

**Explicitly NOT in Phase 1 (other lanes / owner):** WMXIX conversion
(Worker A), the UI app itself (Worker C run 4), bake + game hook (Worker
B), eye parts (Workers B + C), moveset data merge (paused session),
Def Jam conversion (gap #4 — the natural Phase 2: biggest dataset, needs
the EAGL converter and a cross-repo access decision), WWE 2K assets
(owner acquisition call).

---

*Audit compiled 2026-10-20 by the creation-suite wiring audit lane.
Companion state: `creation-suite-pass.json` (building lanes) and
`creation-suite-wiring-audit.json` (this lane) under
`~/workspace/agent-ops/checkpoints/`.*
