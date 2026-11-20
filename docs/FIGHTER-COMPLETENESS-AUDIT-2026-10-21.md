# FIGHTER COMPLETENESS AUDIT — 2026-10-21

Owner order 2026-10-21 ~08:09 CDT: get all the moves set up and all the animations set up to each
character they belong to; get it so he can customize the fighters and SEE them — customized — in
the fights. Acceptance (owner 2026-10-20 20:57): (1) a real fight works between all fighters
(movesets + animations), (2) the customization suite works.

## Method — the audit EXECUTED the game's real resolution chains (no eyeballing)

- **Model (player path):** `attires.js selectedAttireModel()` = ATTIRE_VARIANTS[model]||[id], first entry
  (or persisted pick); **(enemy path):** raw roster `model:` field. Both keys -> `MODEL_URLS` in
  `assets.js` (with the ATTIRE_CUSTOMIZATIONS override layer applied exactly as assets.js applies it),
  then the target file's existence verified on live main via the GitHub API (50/50 unique paths exist).
  Same chain as `game/tests/model-key-guard.test.mjs`.
- **Moveset:** the Fighter keys its moveset by ROSTER ID (`fighter.js:286 this._movesetId = charData.id`),
  loaded by `movesets.js loadFighterMovesets()` — which only loads ids listed in `MOVESET_IDS`. A file
  that exists but is not in `MOVESET_IDS` is NEVER loaded; the fighter silently falls back to the legacy
  T3 aggregate (7 sources) via `MOVESET_MAP` in fighter.js, or to nothing when no aggregate entry exists.
  The roster `moveset:` display field does NOT drive combat loading.
- **Animation bank:** `fighter.js bankIdFor(char.id, movesetId)` executed faithfully: FIGHTER_BANK override
  map (11 fighters, PR #425) -> per-fighter moveset JSON `t3_source` -> `SOURCE_TO_BANK` (t3anims.js) ->
  `MOVESET_MAP` fallback. `null` = no decoded bank for the source (by design: embedded locomotion +
  procedural combat, never another character's clips). NOTE: absence from the FIGHTER_BANK override map
  is NOT a gap by itself — most fighters resolve their bank through their moveset's t3_source.
- **Attires:** ATTIRE_VARIANTS lists vs the 68 `roster/*/attires/*/model.glb` files on main.
- **Transforms:** roster `forms`/`transform` targets executed against MODEL_URLS — `fighter.js`
  `_doTransform` calls `assets.createInstance(t.target)` and swallows failures in a catch, so a missing
  key = a transform that silently never happens.

## Headline result

- All **58** FULL_ROSTER fighters resolve a model on BOTH paths; every resolved file exists on main.
- Animation banks resolve for **56/58** (exceptions: doc-frank-frankenstein, ryuji — both owned by other lanes, below).
- Real defects found: **1 broken transformation chain** (Burger), **3 movesets present-but-never-loaded or
  missing** closable from repo data (kronos-attire2, demonio-human, charger-attire2), **3 fighters with
  canon attires unreachable** in the picker (Diablo A2, Kronos A2/A3, Awa Pop A2), plus per-lane items below.
- The five "missing base movesets" from earlier summaries (josie/shaheen/miguel/negan/akuma files) are NOT
  gaps: per-fighter files (waterfall 146, scimitar 229, bruno 315, negativo 270, dio 265 moves) exist, are
  loaded, and carry their provenance honestly. `gunjack.json` (15 moves) is loaded by NO roster fighter
  (combat keys by roster id; samura1 fights on his own 342-move samura1.json, bank gunjack). The 24-byte
  `sam-ur-a1.json` stub is referenced by nothing and is not in MOVESET_IDS (it cannot poison the loader).

## Gap table — every fighter with a gap, a note, or another lane's ownership

| Fighter | Model | Moveset | Bank | Gap / note | Owner of the fix |
|---|---|---|---|---|---|
| byou | steve-fox ✓ | byou.json 157 ✓ | lei | **CANON (owner 2026-10-21): Byou's vessel is ZUI** (base body Steve Fox — the roster model `steve-fox` IS Zui's declared base body, so the current wiring is consistent), NOT Kevin. Moveset base is Lei Wulong (nine-souls appendix); bank lei. This lane grep-verified game/js + all 96 moveset files: **no Kevin-linked and no Rave-linked Byou wiring exists on main** — the superseded placements the owner referenced are not present in code; nothing to flag as a live conflict. (fighter.js's bank comment calls Lei his "vessel base" — wording only; the binding matches his moveset base.) | — (verified consistent) |
| zen | steve-fox (interim body) ✓ | zen.json 148 ✓ | **julia — INTERIM** | **CANON (owner 2026-10-21): Zen is UNVESSELED** (refused the trial). His Tekken base was Julia (Julia became Nightwolf). End-state = his OWN spirit-body model (owner-supplied Tripo, PENDING — named gap) + a stand version of himself (Susanoo x JoJo Stand x Shaman King Over Soul). The #425 zen->julia bank binding stays INTERIM, not canon-final. Roster `base:` display string still reads "Heihachi" — flagged for the owner's canon pass, not edited here. | Owner (Tripo supply) / canon pass |
| gyou | pantera (declared vessel base) ✓ | gyou.json 149 ✓ | hwoarang | Spirit-form GLB + key `gyou-spirit` exist but no transform/forms wiring reaches them. Spirit/stand forms are a design mechanic (see Zen), not a wiring slip. | Owner design (stands) |
| pantera | pantera ✓ | pantera.json 370 ✓ | king | Picker offers only Attire 1 + Attire 2 Leo Man. **Leopard King (canon Attire 6) GLB at roster/pantera/attires/leopard-king/model.glb has NO MODEL_URLS key**; key `pantera_alt1` exists but is in no variant list; Slot 3 snow-leopard reskin is owner-view-gated (owner decisions 2026-10-17). Flagged, not wired — slot order/defaults are owner-ruled for this fighter. | Owner canon pass |
| diablo | diablo ✓ | diablo.json 288 ✓ | heihachi | **Attire 2 "Devil God" unreachable**: key `diablo-attire2` + GLB exist, but ATTIRE_VARIANTS has no diablo entry, so the picker only ever offers Attire 1. Closable: variant list. | THIS LANE |
| samura1 | sam-ur-a1 ✓ | samura1.json 342 ✓ | gunjack | Model resolves but is UNRIGGED (single tripo_node, no skin). Rigging owned elsewhere. | Pose-isolation lane (PR #393) |
| zui | zui-attire1 ✓ | zui.json 482 ✓ (his own full set — the roster `moveset: demonio` field is display-only; combat keys by id) | jin (t3_source) | No gap. Earlier "unbound" readings confused the FIGHTER_BANK override map with bank resolution. | — |
| kinpo | kinpo ✓ | kinpo.json 285 ✓ | jin (t3_source) | Picker: BASE + "T8" (assets/models/kinpo-t8.glb, 5.3MB). roster/kinpo/attires/attire2/model.glb (18.4MB, key `kinpo-attire2`) is in no variant list — whether it duplicates the T8 build at a different compression is unverified. A1 is under an active owner-reported mesh-repair lane; not touched here. | Kinpo A1 repair lane (active) |
| kingtyrant | king-tyrant ✓ | kingtyrant.json 286 ✓ | eddy | Four attire GLBs under roster/king-tyrant/attires/ (1-4, ~19MB each) + key `king-tyrant_alt1` (0.75MB) exist; no ATTIRE_VARIANTS entry and no ATTIRE-SLOTS.md canon labels on file — slot mapping would be guesswork. Needs canon labels before wiring. | Owner canon pass |
| burger | burger (A1 Demon) | burger.json 264 ✓ + form sets exist & loaded | bryan | **TRANSFORM CHAIN BROKEN**: form targets `burger-speed-demon` / `burger-the-mouth` / `burger-demon` are not MODEL_URLS keys; `_doTransform` catch swallows the failure, he can never transform. Canon mapping (roster/burger/ATTIRE-SLOTS.md): Speed Demon = Attire 6, The Mouth = Attire 7, Demon = Attire 1. | THIS LANE (alias keys in MODEL_URLS) |
| awapop | awa-pop ✓ | awapop.json 340 ✓ | nina | **Attire 2 unreachable**: GLB at roster/awa-pop/attires/attire2/model.glb (owner-confirmed Awa Pop Attire 2, ATTIRE-SLOTS.md) has NO MODEL_URLS key and no variant list. Closable: key + variant list. | THIS LANE |
| nightwolf | nightwolf ✓ | nightwolf.json 135 ✓ | julia | Canon interim CONFIRMED: owner order names Wolf Hawkfield (VF) clips, but no VF motion data exists in any teardown store; Julia is his canon Tekken base and her bank is bound. Leave. | — (canon interim) |
| star | star ✓ (Attire 4 "Classic", untextured clay — documented interim) | star.json 282 ✓ | xiaoyu | Canon Attire 1 "Red Latex" (DEFAULT per ATTIRE-SLOTS.md), Attire 2 "After Dark", Attire 3 "Capoeira Gold" GLBs exist but are UNRIGGED statics; the doc itself gates the playable swap on the auto-rig pass. Not wired here on purpose — an unrigged static in a fight is worse than the clay default. | Auto-rig lane (gate) |
| negativo | n3g4tiv0 ✓ | negativo.json 270 ✓ | bryan | Model textures render pink — pixel-identical MD5 proof says the pink is baked into the only held textures; needs a real Tekken 7 extraction for clean textures. Moveset/bank are fine. | T7 extraction (parked, owner 2026-10-21) |
| docfrank | doc-frank / doc-frank-machine-shop ✓ | docfrank.json 114 ✓ | bosconovitch | Family under active rework (owner 2026-10-21): all 7 Tripo attires on the main entry + Option A bind fix. NOT touched by this lane. | Doc Frank lane (parent-dispatched) |
| demonio-human | demonio-human ✓ | **demonio-human.json (102 moves) exists but is NOT in MOVESET_IDS — never loaded** (Demonio's human form + the standalone roster entry fall back to the jin aggregate) | jin (via aggregate) | Closable: add id to MOVESET_IDS. | THIS LANE |
| doc-frank-wowomomo | ✓ | doc-frank-wowomomo.json (101) exists but NOT in MOVESET_IDS — never loaded | gunjack (aggregate) | Doc Frank family — see docfrank row. | Doc Frank lane |
| doc-frank-hood | ✓ | doc-frank-hood.json (101) exists but NOT in MOVESET_IDS — never loaded | gunjack (aggregate) | Doc Frank family — see docfrank row. | Doc Frank lane |
| doc-frank-frankenstein | ✓ | **NO moveset file, NOT in MOVESET_IDS, NO MOVESET_MAP fallback — no frame data at all** | **null** | Doc Frank family — see docfrank row. | Doc Frank lane |
| doc-frank-machine-shop | ✓ | doc-frank-machine-shop.json 147 ✓ loaded | gunjack (t3_source) | Doc Frank family — see docfrank row. | Doc Frank lane |
| charger | charger ✓ | charger.json 199 ✓ | bryan (t3_source) | His OWN Blanka-derived animation set is a named gap: Street Fighter EX PAC decode. Check-only for this lane. | Teardown sweep (SF EX, queued) |
| charger-attire2 | charger-attire2 ✓ | **NO moveset file**; roster entry declares `moveset: charger` but combat keys by id, so he fights on the bryan aggregate, not Charger's own 199-move set | bryan (aggregate) | Closable: per-id file from charger.json (repo pattern, cf. kronos-attire2.json) + MOVESET_IDS entry. | THIS LANE |
| kronos | kronos ✓ | kronos.json 257 ✓ | king | **Attires 2 "Timberwolf" + 3 "TimberWolf Fully Suited" unreachable**: keys + GLBs exist (ATTIRE-SLOTS.md marks them wired), no ATTIRE_VARIANTS entry. Closable: variant list. | THIS LANE |
| kronos-attire2 | kronos-attire2 ✓ | **kronos-attire2.json (142 moves) exists but is NOT in MOVESET_IDS — never loaded**; fights on the legacy king aggregate instead of his own set | king (via aggregate) | Closable: add id to MOVESET_IDS. | THIS LANE |
| ryuji | steve-fox (fallback rider) | ryuji.json (103) exists but NOT in MOVESET_IDS — never loaded; no MOVESET_MAP entry | **null** | Stale pre-rename entry; the character's live build is ryuji-rock (CornerStone). Flagged for retirement/re-point at the CornerStone merge — rewiring the stale entry here would collide with that lane. | CornerStone lane |
| ryuji-rock | ryuji-rock (branch-only model, pending) | ryuji-rock.json = 24 moves on main | king | Full 129-move set + CornerStone model live on the CornerStone branches; merge in flight (RAM-gated). | CornerStone lane |

## Verified complete (no gap): the remaining fighters

Model resolves on both paths to an existing file; own per-fighter moveset file present, in
MOVESET_IDS, and full (move counts from the executed audit); bank resolves as shown.

| Fighter | Moves | Bank | Attire variants |
|---|---|---|---|
| rin | 149 | jin | 0 |
| tou | 143 | paul | 2 |
| sha | 303 | xiaoyu | 0 |
| kai | 146 | eddy | 2 |
| jin_soul | 123 | yoshimitsu | 0 |
| retsu | 111 | bryan | 2 |
| demonio | 270 | jin | 5 |
| phantom | 432 | yoshimitsu | 2 |
| skull | 275 | bryan | 0 |
| sakura | 306 | xiaoyu | 2 |
| waterfall | 146 | jin | 0 |
| scimitar | 229 | jin | 0 |
| purplerain | 298 | jin | 2 |
| dio | 265 | heihachi | 0 |
| cyborgx | 334 | gunjack | 0 |
| michiko | 332 | jin | 0 |
| torch | 307 | anna | 0 |
| bruno | 315 | bryan | 0 |
| thor | 244 | bryan | 2 |
| yukihyo | 342 | armorking | 0 |
| slice | 331 | bryan | 0 |
| demonio-bloodline-ember | 147 | jin | 0 |
| demonio-winged | 175 | jin | 0 |
| baek-master-white | 113 | bryan | 2 |
| mariposa-monarch | 351 | xiaoyu | 0 |
| dxmmii-patchwork | 150 | jin | 0 |
| zangief | 217 | king | 0 |
| vega | 207 | xiaoyu | 0 |
| iori | 196 | heihachi | 0 |
| armor-king | 125 | armorking | 0 |
| deathfang | 122 | heihachi | 0 |
| koreshi | 329 | heihachi | 0 |

## Staged fighters (movesets wired, not in FULL_ROSTER)

`MOVESET_IDS` carries 79 ids; the ids not in FULL_ROSTER are staged sets (DOA/VF federation,
intake wave, custom fighters) whose roster entries/models land with their own lanes
(DOA4 models: teardown-sweep PRs in flight). They are not playable-roster gaps.

## The consumer gap (customization in fights)

- `game/js/custom-fighter.js` loads suite profiles for CAW fighters but applies NO registry parts;
  nothing in `game/js` consumes a fighter's customization profile in the fight scene.
- The suite side is complete: `packages/creation-suite/src/catalogs.js` (`loadCatalog` / `mergeCatalogs` /
  `resolveProfileParts`) and `parts.js` (`applyPart` — texture swap or bone-socket mesh attach via
  `attire.js attach()`) implement the whole consumer contract against the customization.json v1 profile
  shape `{ parts: { <suite_slot>: { part_id, glb?, placement? } } }`.
- Per-game catalogs now live at `customization/parts/<game>/CATALOG.json` (No Mercy: real parts, PR #401;
  Tekken 7: `parts: []` — zero T7 part meshes exist in any holding, survey PR #437; the legacy Tekken
  program T5/T6/TTT2 is the active parts source per owner order 2026-10-21, gap-closure lane W7).
- Wiring delivered by this lane: an additive consumer that, after a fighter's model loads, resolves the
  fighter's in-repo profile (`customization/profiles/<fighter>.json`, customization.json v1) against the
  merged catalogs and applies each part at its bone socket — no changes to bind/retarget/fighter-loading
  code; a missing profile or catalog leaves the fight untouched.


## Addendum — fixes landed + consumer wiring (2026-10-21, this lane)

**PR #444 (MERGED):** the closable audit fixes — MOVESET_IDS now loads kronos-attire2's,
demonio-human's, and charger-attire2's own movesets (+ new `charger-attire2.json`);
Burger's transformation keys registered on their canon attire files (speed-demon =
Attire 6, the-mouth = Attire 7, demon = Attire 1); attire ladders added for Diablo
(A2 Devil God), Kronos (A2/A3), Awa Pop (A2, + its MODEL_URLS key). Regression guard:
`game/tests/fighter-completeness.test.mjs`.

**Consumer wiring (this lane's follow-up PR):** `game/js/customization-consumer.js` +
a two-line hook in `game.js startMatch`. After a fighter's model is built, the
fighter's suite profile (localStorage `wh_creation_suite_v1` record the suite UI
saves, or `customization/profiles/<fighter-id>.json`) is resolved through the suite's
own `catalogs.js`/`parts.js` and each part attaches at its bone socket on the
fighting model — mesh parts, texture layers, and item-color tints. The UI-built
Pantera proof profile is committed at `customization/profiles/pantera.json`.
Proof harness: `game/customization-harness.html` (boots a real match through the
game's own path). The UI v2 lane's live viewport shares this exact attach path
(parts.js/attire.js + the consumer's exported placement normalization) — no fork.

**Zen update (owner 2026-10-21 ~10:41 CDT):** Zen's own-model line above is now
RESOLVED-BY-OWNER-TRIPO — the owner delivered the spirit-body Tripo
(8c46e379-a51c-4741-b4a3-2132ca89078f) and the zen-spirit-body lane wires it as
roster/zen Attire 1 default. His bank stays Julia (canon Tekken base, INTERIM as a
final-form statement per the unvesseled ruling); Zen remains UNVESSELED.

**Known v1 boundaries of the consumer (honest):** parts do not yet follow a
mid-match transformation (they stay on the model they were attached to — re-applying
needs a hook inside fighter.js's transform path, flagged for a follow-up lane, not
hacked around); body morphs/body-type/skin-tone from a profile stay with the CAW
loader and the bake engine — the consumer applies parts, part tints, and texture
layers only, and never re-tints a roster fighter's own textured model.

**Consumer fit fixes found by the proof (same PR):** two real defects surfaced
only when a converted part was actually worn. (1) Parts are now wrapped in a
group centred on their bounding box instead of translating geometry — converted
parts carry baked node rotations, which swung geometry-translated parts off the
socket (the test plate sat a full quadrant off the Spine2 bone; centred wrap:
bbox exactly on the bone). (2) Attached part materials are forced double-sided
in the consumer's layer — several No Mercy shells are wound inward and vanish
single-sided from most angles (proven with/without in the viewer). Per-fighter
surface fit (how far a piece sits proud of a given body) remains profile data,
authored per fighter — the committed Pantera profile carries its tuned offset.

**Proof-environment note (honest):** frame capture of the full fight page was
blocked by the shared VM's load (2 cores at load 14–30 under sibling lanes'
Ghidra/Blender/pack-objects work; the software-GL renderer repeatedly starved
before presenting a frame across a dozen attempts, including a deterministic
harness clock and canvas-readback captures). The in-fight evidence committed is
the real match's console record (consumer STATE + live match STATE with banks
and parts); the visual frame of the customized fighter comes from the same
consumer code path in `game/customization-viewer.html`, viewed by the lane
before filing. A clean-load rerun of `game/customization-harness.html` is the
only remaining proof upgrade, and it is a rerun, not new work.
