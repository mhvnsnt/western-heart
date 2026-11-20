# Creation Suite — T5/T6 Customization System Data (Lane 6, 2026-10-24)

System data + canon framing ONLY. The UI lane owns the menus;
the parts lane owns meshes; this doc + `game/js/customization-t56.js`
own the slot taxonomy, the conflict rules, and the validation
contract the suite and the in-fight consumer share. No Tekken
names in-game; Tekken labels appear here as source labels only.

## The model: 24 slots in two eras

`T56_SLOTS` in `game/js/customization-t56.js`. Every slot:
`{ id, label, era, group, conflicts[], canon }`.

### Era t5 — T5's four categories (community-documented structure)
T5 (2004) sold items in four categories — head, face, upper
body, lower body — plus colour zones and full costumes, bought
with fight money ("G") earned in play (GameSpy T5 preview;
FunTrivia T5 quiz: "four types of items: head, face, upper
body, lower body"). T5 counts (~five items per category per
character) are T5's, not WH's; the categories are the
structure pulled.

| Slot | Group | Canon |
|---|---|---|
| head, face, upper-body, lower-body | head / face / body | face = CANON-ANCHORED; rest = SYSTEM |
| colours | colour | SYSTEM |
| costume (full costume) | body | SYSTEM (conflicts with all component slots) |

### Era t6 — T6 expansion, now full-file grounded
Two independent sources agree on the expansion shape:
- T6 item lists (e.g. Julia Chang T6 items: cowgirl hat /
  gloves / top, face paints, suspenders, holsters, tribal
  tops) — community lists.
- FULL FILE: `teardown/tekken6-customization-research.md`
  (2026-10-16) — decrypted T6 PSP EBOOT item-name tables
  (10,495 records) + NTXL string tables. Confirmed: the hair
  split (Hair - Back, Hair - Front (Right)), Face - Other,
  and item names including Ki / Aura / Effect / Comic Effect
  / SP Rage variants.

| Slot | Group | Canon | Note |
|---|---|---|---|
| hairstyle | head | SYSTEM | Combined slot; conflicts with hair-back / hair-front / full-head |
| hair-back, hair-front | head | SYSTEM | T6 PSP split form; coexist with each other, conflict with hairstyle + full-head |
| full-head | head | SYSTEM | Conflicts with head / hairstyle / hair-accessory |
| hair-accessory | head | SYSTEM | |
| glasses | face | SYSTEM | |
| facial-hair | face | CANON-ANCHORED | Part of the face the Reincarnation assembles |
| face-paint | face | CANON-ANCHORED | Face Paint / Make-up |
| face-other | face | SYSTEM | T6 PSP NTXL category |
| full-body | body | SYSTEM | Conflicts with upper-body / lower-body / upper-accessory / lower-accessory |
| upper-accessory, lower-accessory, extra | body | SYSTEM | |
| eyes, nose, mouth | face | CANON-ANCHORED | Reincarnation sub-slots of `face` (refine it, do not conflict with it) |
| effects, aura | layer | SYSTEM | T6 PSP items (Ki / Aura / Effect names in the decrypted tables) — NOT later-Tekken-only. Layer slots, no conflicts |

Later-Tekken slot table (T7, TekkenMods TKDataPatcher docs:
HEAD, HAIR, FULL_HEAD, HAIR_ACC, GLA, FACE, FACE_HAIR,
MAKE_UP, UPPER, FULL_BODY, LOWER, UPPER_ACC, LOWER_ACC,
EXTRA, Effects, Aura) was used as a COMPLETENESS cross-check
for this taxonomy, not as an era claim.

## Canon framing (split honestly)

- CANON-ANCHORED (face slots only): the Reincarnation gives
  a soul "three pairs of eyes, three noses, three mouths"
  and "the face is not cosmetic. Sharper eyes, faster hands.
  A heavier nose, heavier hits" (CANON.md L48–50, L1342).
  "The Reincarnation is the only character creator the
  Western Heart has ever needed" (CANON.md L1342). Face
  slots ARE that creator, in suite form.
- SYSTEM (everything else): trial attire and suite
  mechanics. No canon location, being, or backstory is
  claimed for a jacket, a hat, or an aura. In particular
  the Trader's marketplace is NOT cited as a clothing
  shop: canon says the Trader buys and sells elemental
  forces (CANON.md L477–481), never clothes.
- DO NOT CONFLATE: T6 PSP "SP Rage" effect-item names
  are cosmetics in an item table, not the Rage combat
  system (which still NEEDS NAME — see the
  proprietary-names audit).

## Consumer wiring (already waiting for this)

`game/js/customization-consumer.js` (header, 2026-10-21)
resolves suite profiles by slot key against merged catalogs
and states: "Tekken 5/6 catalogs are picked up automatically
when the gap-closure lane lands them." This module IS that
landing: profile `parts` keys MUST be slot ids from
`T56_SLOTS`. Catalog entries (meshes) arrive from the parts
lane keyed by the same ids; this module carries no meshes.
`validateCustomization(parts)` returns `{ ok, unknown[],
conflicts[] }` — unknown ids are reported, never silently
dropped; symmetric conflict pairs are de-duplicated.

## What the UI lane still owns / gaps

- Menus, pickers, previews, pricing/economy (T5's "G" is
  structure reference, not a WH currency decision — the
  owner has not locked a WH customization currency).
- Meshes per slot (parts lane) and per-fighter eligibility.
- NTXL full-category enumeration (120 tables; the research
  doc confirms the category list spans multiple tables and
  is not fully enumerated) and the item definition struct
  (`sbcustomize_item_t` array — still locked, teardown
  lane). If enumeration adds categories, they land as new
  `T56_SLOTS` entries in a follow-up PR, not by editing
  this doc alone.
- Body morphs / body type / skin tone stay with the CAW
  loader + bake engine per the consumer's scope boundary
  (v1: parts + tints + textures live; morphs do not).
