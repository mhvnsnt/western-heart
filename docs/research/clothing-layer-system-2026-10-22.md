# RESEARCH — Clothing remove/change system (worker 64, 2026-10-22)

Owner directive (2026-10-22): "Make it able to remove and change their clothes
in the character creation suite and in game when I play it and preview it."

## What exists today

- **Creation Suite bake schema** (`customization/CUSTOMIZATION-JSON-SCHEMA.md`,
  v1 + round-2 additions): per-attire `customization.json` with `parts`
  (catalog mesh parts), `textures`, `colors`, `region_swaps` (Tekken-style
  region cut/graft), and `hide_meshes` — a bake-time base-mesh removal list
  (substring patterns; the "hide base hair" toggle writes `["hair"]`).
  `hide_meshes` is **bake-time only** (it drops meshes from the baked output
  GLB permanently) — it is not a runtime toggle and cannot do what the owner
  asked (remove/change clothes live, in game).
- **Suite UI** (`packages/creation-suite/ui/`): `profile.js` (pure state;
  `toCustomizationJson` / `toSuiteRecord` / `fromSuiteRecord`), `suite.js`
  (DOM; ATTIRE tab = Tekken 16-slot spine, PIECES tab = region swaps).
  The ATTIRE tab's slot spine equips *catalog parts from other sources* —
  there is no surface for toggling the base model's OWN clothing meshes.
- **Game runtime**: `game/js/assets.js` `createInstance(fighterId)` is the
  single choke point that clones every fighter's GLB scene. It sets
  `o.visible = true` on all meshes. `game/js/customization-consumer.js`
  `applyFighterProfile(fighter)` applies suite profiles to in-fight models.
  `game/js/attires.js` (attire picker) persists per-fighter attire choice in
  `wh_attires_v1`. The pause menu (`game/js/menus.js`) has RESUME / OPTIONS /
  QUIT — no clothing surface.
- **Confirmed technical foundation**: clothing meshes are separate modeled
  geometry (Tsuyu: `OBsuit`, `OBboots`, `OBgloves`, belt/mask/goggles, `OBHair`
  vs body `OBtsuyu`; Parvati: `Body Suit`, `Bra`, `Bra (2)`, `Bottom`, `Belt`,
  `Choker`, `Gaunlet`, `Glove L/R`, `Goggles`, `Hair`, `Heels`, `Pantie`,
  `Shoes`, `Stocking`, …). Undress = hide meshes. No painted-on clothing to
  repaint on these two.

## Design chosen

1. **Runtime per-mesh visibility engine** (`game/js/clothing-layers.js`):
   layers are matched by explicit raw-mesh-name lists (never substrings —
   `Bra` must not catch `Bra (2)`); toggling sets `mesh.visible` on the live
   instance. Hooked into `assets.createInstance` so saved choices apply to
   every fight, preview, and harness automatically.
2. **Data-driven config** (`game/data/clothing-layers.json`): model key →
   layers. Key = MODEL_URLS model key (each attire IS a model key in this
   game), so the same file serves the suite, the fight, and previews.
3. **Persistence** `wh_clothing_v1`: `{ modelKey: { label: true } }` hidden-set
   per attire. The suite profile ALSO carries `clothing_layers.hidden` in
   `customization.json` v1 (additive key) so the choice travels with the
   attire record.
4. **Suite UI**: a CLOTHING LAYERS section nested at the top of the ATTIRE tab
   (per the integration law — inside the Tekken flow, not a parallel system),
   listing the current attire's layers with clean labels, category badges, and
   toggle switches. Toggles write to profile state and persist via the
   existing save path.
5. **In-game**: a CLOTHING button on the pause menu opens a sheet with P1/P2
   layer lists; toggles apply live to the fight instances AND persist.
6. **Naming convention** (`docs/CLOTHING-ACCESSORY-LABELING-STANDARD.md`):
   `<category>_<item>_<variant>`; 11 categories (hair is first-class,
   separate from headwear, per the owner's architectural point).

## Tekken integration-law check

- The suite surface nests inside the ATTIRE tab's existing Tekken slot-spine
  flow (new section, same sheet, same save path) — no parallel system.
- The in-game surface nests inside the existing pause dialog — no new screen.
- The bake schema is extended additively (`clothing_layers`); v1 still parses.
- The wiring map (`customization/CREATION-SUITE-UI-WIRING.md`) gets a new row
  per its rule 2.

## Tsuyu frog hat — investigation result

1. In the source model but not exported? **No.** Full object-name scan of
   `Tsuyu Asui IK.blend` (37 objects): suit, boots, gloves, belt, mask,
   goggles, hair, body, face/mouth templates, rig + widgets — no hat object.
2. A separate accessory mesh needing attach? **No** — it doesn't exist.
3. Missing entirely? **Yes.** The crew modeled one as a separate library
   part (`customization/parts/headwear/frog-hat/`, label
   `headwear_frog-hat_01`) and it is attached in the re-render + registered
   in her clothing config.

Tsuyu's HAIR: the user suspected it missing too — it is **present**
(`OBHair`, visible in the PR #634 render). No fix needed; it is registered
as the first-class hair library item `hair_bob_01`.

## Open / deferred

- Tsuyu and Parvati have no in-repo GLBs yet (intake staged in workspace;
  only `roster/<x>/intake/` exists on main). Their clothing configs are
  written against the verified source mesh names so they light up the moment
  their models land; the engine no-ops cleanly until then.
- The procedural frog hat is a crew placeholder — the owner art-directs hats
  like any other part; it ships as a swappable library item, not baked in.
- Mix-and-match ACROSS characters (wear Parvati's choker on Tsuyu) is
  architecturally prepared (labels are cross-character; the library path is
  reserved) but not wired — that's the library-phase follow-up.
