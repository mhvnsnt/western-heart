# DECISION LOG — 2026-10-22 — Clothing remove/change system + labeling standard

## Context
Owner directives (2026-10-22): (1) clothing remove/change in the creation
suite AND in game while playing/previewing; (2) a labeling standard for every
clothing part and accessory across all characters going forward, retroactive
cleanup starting with Parvati; (3) hair, hats, accessories as separate
interchangeable parts (hair = first-class library item); (4) Tsuyu's missing
frog hat — "Tsuyu without her frog hat isn't Tsuyu. Get it on her."

## Decisions

1. **Runtime visibility toggles, not bake removal.** The suite's existing
   `hide_meshes` is bake-time (permanent output GLB). The owner wants live
   remove/change in game, so the system toggles `mesh.visible` on live
   instances. Bake stays untouched.
2. **Explicit mesh-name lists, never substring matching.** `Bra` must not
   match `Bra (2)`. Each layer owns an exact list of raw GLB mesh names
   (case-insensitive exact match).
3. **Config key = MODEL_URLS model key.** Each attire is already a model key
   in this game, so one config (`game/data/clothing-layers.json`) serves the
   suite, the fight, previews, and harnesses with no translation layer.
4. **Hook point: `assets.createInstance`.** The single choke point for every
   fighter model instance. Guarded + fire-and-forget so a missing/broken
   config can never break a fight.
5. **Persistence: `wh_clothing_v1`** (hidden-set per model key), mirrored into
   the suite profile as additive `clothing_layers.hidden` so the choice
   travels with the attire record.
6. **Label format `<category>_<item>_<variant>`**, 11 categories, hair
   separate from headwear. Raw source names (incl. typos like `Gaunlet`) stay
   quarantined in the config's `meshes` lists. Full standard:
   `docs/CLOTHING-ACCESSORY-LABELING-STANDARD.md`.
7. **Suite UI nests in the ATTIRE tab** (integration law); in-game UI nests
   in the pause menu. No parallel systems, no new screens.
8. **Tsuyu frog hat: missing from the source, crew-modeled as a separate
   library part** (`headwear_frog-hat_01`), attached for the re-render, not
   baked into her model. Tsuyu's hair was verified present — no action.
9. **Unidentified source meshes get `review: true`**, never silent guesses
   (Parvati's `Stripe`, `Full`, `Triangle`).

## Consequences
- Intake is not complete until the label map is filed (§6 of the standard).
- Mix-and-match across characters is prepared but not yet wired (library phase).
- The procedural frog hat is a placeholder the owner can art-direct/replace.
