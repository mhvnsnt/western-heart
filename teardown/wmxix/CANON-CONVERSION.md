# WMXIX — CANON CONVERSION (mat-legends)

**Game:** WWE WrestleMania XIX (GameCube) → WH universe **`mat-legends`** (root `RENAME-MAP.md` universe table: "Legends of the mat")
**Scope:** both teardown folders — `teardown/wmxix/` (assets, canonical for asset data) and `teardown/wwe-wrestlemania-xix/` (research, canonical for format/solver truth). Reconciliation evidence: `teardown/wmxix/WIRING-INVENTORY.md`.
**Lane:** Full Wiring + Canon Conversion, WMXIX sub-lane, 2026-10-20. This file is the per-game source of truth; root `CANON.md`/`RENAME-MAP.md` carry delimited summaries only.
**Rule applied throughout:** conversion is ADDITIVE. No teardown file was renamed, moved, or deleted by this lane. Physical folder renames remain PLANNED and gated (see `teardown/wmxix/docs/RENAME-ENTRIES-WMXIX.md`: watchdog lane + owner name assignment). Canon names are applied at the registry/data layer the game and library actually read.

## 1. Universe-level conversion

| Source identity | WH canon | Where applied |
|---|---|---|
| WWE WrestleMania XIX | `mat-legends` universe | `moveset-library/animations/WMXIX-CLIP-INDEX.json`, `moveset-library/movesets/WMXIX-MOVES.json`, `game/assets/stages/mat-legends/stages.json`, `customization/mat-legends-caw.json`, root `CANON.md` + `RENAME-MAP.md` appended sections |

## 2. Animation / moveset conversion (federation rule)

All 170 YANM clips keep their decoded data untouched. Conversion applied at the library layer:

| Conversion | Detail |
|---|---|
| Canon clip IDs | `ML-<CLIP>` (e.g. `ML-A000-0A`) assigned to all 170 clips in `moveset-library/animations/WMXIX-CLIP-INDEX.json` (bank a x35, b x24, c x105, d x6) |
| Move entries | 169 entries `WMXIX-001`..`WMXIX-169` in `moveset-library/movesets/WMXIX-MOVES.json`, MOVE-DATABASE schema, `anim_ref` → the real clip JSON |
| Tekken-style inputs (federation rule) | Grapple slot family mapped to Tekken throw inputs: front weak = `1+3`, front strong = `2+4`, back weak = `1+3` behind, back strong = `2+4` behind, front finisher = `f,f+1+3`, back finisher = `f,f+2+4` (notation per `game/js/movesets.js` header). No wrestling-native input scheme was carried into the library. |
| Excluded | `c138_0a` — 72-byte stub, wrong magic, no track directory (`TEARDOWN.md` section 5). Registered in the clip index with its decode status; no move entry created. |
| NOT converted (flagged) | Per-clip move names. Per-clip hash-set → move-category mapping is an OPEN decode item (`TEARDOWN.md` section 5); move entries carry provisional registry labels explicitly marked `name_status: provisional — NOT a canon move name`. No names were invented. Slot eligibility is registered at the grapple-family level; exact per-move slot assignment awaits the semantics decode. |

Retarget path (unchanged, research-canonical): `teardown/wwe-wrestlemania-xix/docs/yanm_to_tekken3_v2.json` (+ v1), `aki_to_tekken3_v1.json`, tools `yanm_to_tekken3_v2.py` / `aki_to_tekken3.py`. YMG bone coords Y-Z-X (perm 1,0,2). Light proprietary pass on animations = the canon ID + input-structure layer above; clip key data was NOT numerically altered (staging law: additions over alterations).

## 3. Arena → stage conversion

Source of truth for mappings: `teardown/wmxix/ARENA-UNIVERSE-MAP.md` (authored WH canon, pre-existing). This lane wired the mappings into game data at `game/assets/stages/mat-legends/stages.json`:

| WMXIX source | WH canon stage | Status in stages.json |
|---|---|---|
| Arena `00` (primary show) | HELIX PALACE (`helix-palace`) | registered, geometry point-cloud |
| Arena `01` (secondary show) | OCTAGONAL SHRINE PAR-FANG (`octagonal-shrine`) | registered, geometry point-cloud |
| Arena `02` (PPV) | PHANTOM MARKETPLACE (`phantom-marketplace`) | registered, geometry point-cloud |
| `bg/cage/hell.pac` | THE DRILL WOUND (Stage 7, secret) | registered, .pac not decoded |
| `bg/cage/cage.pac` | Octagonal Shrine Par-Fang alt / Wrestling Mode cage | registered, .pac not decoded |
| Backstage sets `bs/0_*`, `1_*`, `2_*` | Helix Palace interior rooms / Wrestling Mode pre-fight areas | registered, geometry point-cloud |
| Backstage set `bs/5_*` | UNASSIGNED — pending geometry review | registered, no canon name invented |
| `kaijo_x8` | UNASSIGNED — pending geometry review | registered, no canon name invented |
| Revenge packages A/C/F/H/P/S/T (35) | Open Land Stages by type (Plains of Chi-U / Tree of Life / Palace of Dreaming) | registered as a set; exact slot→location mapping open in the source doc itself |
| `ring.obj` | Wrestling Mode ring / canon-land ring dressing | registered |

Note: the 8 canon lands in `game/js/stages.js` are procedural stages carrying these canon names today; no WMXIX geometry feeds them yet (face reconstruction open — see inventory). Branding strip/re-soul treatment per `ARENA-UNIVERSE-MAP.md` Part 2 applies when geometry lands.

## 4. Wrestler character conversion — FLAGGED, none executed

`teardown/wwe-wrestlemania-xix/WRESTLER-IDENTITY-MAP.md` is explicit: slot→identity assignment is the owner's, WH names are PENDING, "Never invent WH names." Only slot 000 carries a confirmed source identity in-repo. Per the federation rule the models themselves belong to mhvnsnt/wrestling-game and mhvnsnt/wrestlemania-xix-mod (ACCOUNTED-ELSEWHERE in the inventory). **This lane converted zero character identities and invented zero names.** Blocker type: owner canon decision.

## 5. CAW (create-a-wrestler) conversion

The XIX CAW part library (2,690 files, cataloged in `teardown/wmxix/caw-parts/CATALOG.md` + `files.tsv`) is registered for the Creation Suite at `customization/mat-legends-caw.json` under the mat-legends universe, by category (Man 670, Woman 543, Face 351, Upper_Body 218, Face_op 208, Gears 149, Lower_Body 142, Shoes 84, Hair 70, Wrist 60, Gloves 50, common 50, 64gara 41, Knee 24, Elbow 22). Part files are not duplicated into the repo (they live on the ISO/release side); the catalog is the wiring point. No part was renamed (part-level WH naming awaits the same owner assignment as section 4).

## 6. Mode conversion — Revenge Mode

XIX's Revenge Mode (out-of-ring mission/traversal fighting; reference: `teardown/wwe-wrestlemania-xix/REVENGE-MODE-ARENAS.md`) has no WH canon mode name in `CANON.md`/`ROSTER.md` and no implementation in `game/js/modes.js`. This lane did NOT invent a canon name and did NOT wire a mode (engine code is another lane's). The traversal stage data it would consume IS registered (`stages.json` backstage/open entries, `type: backstage_traversal` / `open_traversal`). FLAGGED to coordinator as an engine + canon decision item.

## 7. Per-character isolation statement

This lane touched NO character skeleton, rig, animation file, or shared retarget/pose code. All work is new registry/data files keyed by clip/stage/part IDs. WMXIX clips run on the shared Yukes 70-bone research skeleton only inside the teardown/research layer; nothing was attached to any WH fighter, so no character's stance/pose/animations could change. No add-ons (extra arms, jiggle, wings, extra hands/wrists) exist in the WMXIX material wired here. Deliberate parallels sharing: NONE introduced. The only shared structures are the pre-existing library schemas (`MOVE-DATABASE` entry format, `MOVE-SLOTS` grapple family) which the new files follow without modifying.
