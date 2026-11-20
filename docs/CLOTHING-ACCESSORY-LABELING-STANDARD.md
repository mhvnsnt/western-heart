# CLOTHING / ACCESSORY LABELING STANDARD

**Status:** owner directive 2026-10-22 (~17:34 CDT) — permanent standard for the
creation suite library. Every clothing piece and accessory on every character,
from intake onward, gets labeled under this convention.

**Why:** "Make sure all the different separate clothing parts and accessories
are labeled so it helps us arrange and organize how we switch and interchange
the parts. We'll have to do that for every character going in so it helps us
get our creation suite library set up."

## 1. The format

```
<category>_<item>_<variant>
```

- **category** — one of the taxonomy slots in §2 (always singular, lowercase).
- **item** — snake_case descriptor of what the piece IS
  (`bra`, `bodysuit`, `frog-hat`, `choker`, `goggles`, `bob`…).
  Hyphens allowed inside the descriptor for compound names
  (`frog-hat`, `glove-l`).
- **variant** — two digits, `_01` upward. Same garment, different cut/color =
  new variant, never a new name.

Examples: `top_bra_01`, `bottom_shorts_02`, `accessory_choker_01`,
`hair_bob_01`, `headwear_frog-hat_01`, `footwear_boots_01`.

**Never** ship raw source names to the user: not `Bra (2)`, not `Gaunlet`,
not `OBsuit`, not `GZM_whatever`. Raw names live only in the config's
`meshes` list so the engine keeps matching them.

## 2. Taxonomy (categories)

Hair is a first-class library item — separate from headwear (owner directive
2026-10-22: "hair, hats, and accessories as SEPARATE INTERCHANGEABLE PARTS").

| Category    | Covers                                                        |
|-------------|---------------------------------------------------------------|
| `hair`      | Hairstyles — wigs, bobs, ponytails, dreads. Swappable, never baked into the head mesh. |
| `headwear`  | Hats, caps, hoods, crowns, helmets. Sits ON/OVER hair.        |
| `facewear`  | Masks, goggles, glasses, visors.                             |
| `top`       | Shirts, bras, jackets, vests — torso coverage above the waist. |
| `bottom`    | Pants, shorts, skirts, briefs — waist down.                   |
| `fullbody`  | Bodysuits, dresses, robes, armor sets — one piece, torso + legs. |
| `underwear` | Panties, briefs, bras-as-underwear — the layer under the outfit. |
| `legwear`   | Stockings, socks, leggings, thigh-highs.                     |
| `gloves`    | Gloves, gauntlets, bracers, arm wraps.                       |
| `footwear`  | Boots, shoes, heels, sandals.                                |
| `accessory` | Belts, chokers, jewelry, chains, scarves, capes — everything else wearable. |

New categories need an owner sign-off — the list above is the contract the
suite UI filters on.

## 3. Rules

1. **One label per swappable piece.** A left/right pair shipped as two meshes
   gets two labels (`gloves_glove-l_01`, `gloves_glove-r_01`) so each side can
   toggle alone; a pair shipped as one mesh gets one label.
2. **Labels are stable.** Once a label ships in a config, it never changes —
   saved player choices (`wh_clothing_v1`) key on it. Rename = new variant.
3. **Raw names stay in the config.** `meshes: ["Bra (2)"]` keeps the engine
   matching even though the user only ever sees `top_bra_02`.
4. **Source typos are not propagated.** The label is spelled correctly
   (`gloves_gauntlet_01`); the raw typo (`Gaunlet`) stays quarantined in the
   config's `meshes` list with a note.
5. **`review: true` flag.** When a source mesh can't be identified from its
   name alone (`Stripe`, `Full`, `Triangle`), label it best-effort, set
   `"review": true`, and rename it properly once it's seen in the suite.
   Never silently guess.
6. **Left/right suffixes** are `-l` / `-r` inside the item descriptor.
7. **No bare numbers or parens** in labels — `(2)` becomes `_02`.

## 4. Where labels live

- **Runtime + game:** `game/data/clothing-layers.json` — model key → layers.
  The engine (`game/js/clothing-layers.js`) and every UI surface read this.
- **Creation suite library parts** (separate GLB parts like the frog hat):
  `customization/parts/<category>/<item>/` with a `README.md` that states the
  label. Example: `customization/parts/headwear/frog-hat/` → `headwear_frog-hat_01`.
- **Suite profile record:** `clothing_layers: { hidden: ["<label>", …] }` in
  `customization.json` v1 (additive) — persisted per attire.

## 5. Retroactive cleanups (done 2026-10-22)

- **Parvati** (SmutBase commission .blend, 90 objects): full map in
  `game/data/clothing-layers.json` under `parvati`. Raw → label examples:
  `Bra` → `top_bra_01`, `Bra (2)` → `top_bra_02`, `Gaunlet` [sic] →
  `gloves_gauntlet_01`, `Heels 3` → `footwear_heels_02`,
  `Pantie 3` → `underwear_pantie_02`, `Stocking`/`Stocking.001` →
  `legwear_stockings_01`. Unidentified meshes (`Stripe`, `Full`, `Triangle`)
  labeled best-effort with `"review": true`.
- **Tsuyu Asui** (SmutBase IK .blend, 37 objects): `OBsuit` →
  `fullbody_bodysuit_01`, `OBboots` → `footwear_boots_01`,
  `OBgloves` → `gloves_hero_01`, `OBBody_belt.dmx` → `accessory_belt_01`,
  `OBBody_mask.dmx` → `facewear_mask_01`, `OBBody_google.dmx` →
  `facewear_goggles_01`, `OBHair` → `hair_bob_01` (first-class hair item).
  Frog hat (`headwear_frog-hat_01`) added as a crew-modeled library part —
  it was missing from the source entirely.

## 6. Intake wiring (for the intake pipeline)

Every new character's intake MUST produce a label map before the model is
considered intake-complete:

1. Dump the source's mesh/object names (byte-scan the .blend or read the GLB).
2. Assign one `<category>_<item>_<variant>` label per clothing/accessory/hair
   mesh per this standard.
3. File the map in `game/data/clothing-layers.json` under the character's
   model key, with `source_mesh_names` preserved.
4. Flag anything unidentifiable with `"review": true` — do not guess silently.
5. Register detachable library parts (hats, hair, accessories shipped as
   separate assets) under `customization/parts/<category>/<item>/` with the
   label in their README.

The intake queue doc (`docs/SMUTBASE-INTAKE-QUEUE.md`) points here; intake is
not done until the labels are.
