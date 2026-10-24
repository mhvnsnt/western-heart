# DOC FRANK — Attire Slots (owner 2026-10-19; ladder reorder 2026-10-21)

## Ladder rule (owner 2026-10-21, restated for every character)

Doc Frank's **Tripo GLB attires are Attires 1–4 at the FOREFRONT**, and his
defaults resolve to Attire 1. The Dr. Bosconovitch base model attires and
all retextures/reskins ladder **BACK** behind them — never the forefront,
never the default. (This doc previously framed the ladder around the base
model and the machine-shop reskin; that inversion was the confusion the
owner corrected 2026-10-21 ~19:08 CDT.)

## Slots

| Slot | Display name | Provenance | Status | Contents |
|------|--------------|-----------|--------|----------|
| 1 | **Doc Frank — Old Man / Transformed** | Attire GLBs (pre-form GLB + **Tripo** transformed) | ✅ wired (transform mechanic live) | TWO-FORM attire: pre-transform old man (`attire1/pre-transform/model.glb`, key `doc-frank-a1` — **the default model for the main `docfrank` entry and the first picker entry**) ↔ post-transform bigger form (`attire1/post-transform/model.glb`, key `doc-frank-big`, **Tripo** 2c6cff79, 2026-10-19). Mid-match transform via KeyT / 💪 button — Roshi-style. Bigger = +40% power, −12% speed, +15% defense. |
| 2 | **Doc Frank — Wowomomo / Transformed** | **Tripo** | ✅ wired (transform mechanic live) | TWO-FORM attire: base (`attire2/base/model.glb`, key `doc-frank-wowomomo`, Tripo villain, glass dome helmet, W emblem) ↔ transformed (`attire2/transformed/model.glb`, key `doc-frank-wowomomo-big`, Tripo, bigger brain-dome). Canon: Dr gero meets mojo Jojo meets bosconovitch meets Dr wierd. |
| 3 | **Doc Frank — Hood Scientist / Transformed** | **Tripo** | ✅ wired (transform mechanic live) | TWO-FORM attire: base (`attire3/base/model.glb`, key `doc-frank-hood`, Tripo f40c7cde — elderly scientist in suit, club-night look) ↔ transformed (`attire3/transformed/model.glb`, key `doc-frank-hood-big`, Tripo — massive muscular form, jacket burst off Roshi-style). |
| 4 | **Doc Frank — Frankenstein's Cyborg / Transformed** | **Tripo** | ✅ wired (transform mechanic live) | TWO-FORM attire: base (`attire4/base/model.glb`, key `doc-frank-frankenstein`, Tripo 2bea6cac) ↔ transformed (`attire4/transformed/model.glb`, key `doc-frank-frankenstein-big`, Tripo 690d28a2). Mid-match transform via TRANSFORM button. |
| 5 | **Bosconovitch Base** | **Tekken base** | ✅ wired (ladder-back alternate) | The base model `game/assets/models/doc-frank.glb` (key `doc-frank`) — the Dr. Bosconovitch base attire. NOT a default; a ladder-back alternate, same as every other character's Tekken base. |
| 6 | **Machine Shop** | **Reskin / retexture** | ✅ wired (ladder-back alternate + own roster entry) | Texture reskin of the slot-5 base model — 5 embedded PNGs swapped, no rig or geometry changes (PR #263). Key `doc-frank-machine-shop` → `attires/machine-shop/doc-frank-machine-shop-rigged.glb`. NOT a Tripo model and NOT a default. |

## Provenance notes (read before naming any model's origin)

- Slot 1's pre-form GLB (`attire1/pre-transform/model.glb`) is byte-identical
  to `attires/machine-shop/doc-frank-machine-shop.glb` (sha256
  55e1f8578a78…): the PR #263 reskin file was adopted as Attire 1's old-man
  form. It is Attire 1's GLB by slot and by the owner's order — but its file
  lineage is the reskin, and the standalone Machine Shop attire (slot 6) is
  that same reskin presented on its own. Do not call slot 6 a Tripo model;
  do not present slot 5 or 6 as Doc Frank's forefront.
- Rig state (verified 2026-10-21 by GLB skin scan + PR #465 bind fix):
  rigged = slot 1 pre-form (178 joints, binds normalized in #465), slot 3
  base (73 joints, binds normalized in #465), slot 5 base (178 joints),
  slot 6 (178 joints). **Unrigged statics** (wired + selectable, cannot
  animate until a rigging lane does them): slot 1 transformed, slot 2 base
  + transformed, slot 3 transformed, slot 4 base + transformed.

## Slot-ordering law

- Slots 1–4 = Doc Frank's own Tripo GLB attires, forefront, in order.
  Slot 1 is the default attire (owner law 2026-10-18: slot 1 = Tripo
  default; the post-transform Tripo bigger form is the Tripo anchor of
  the slot and the old-man pre-form is the form every player starts the
  match in).
- Tekken base attires and reskins/retextures always ladder behind the
  Tripo attires (owner rule 2026-10-21) — slots 5–6 here.

## History

- 2026-10-19: Owner shared the bigger-form Tripo link in chat ("he can
  transform mid match... like master roshi from dbz"). Both forms wired as
  Attire 1 + generic transform mechanic implemented in `game/js/`.
- 2026-10-19: Attire 2 "Wowomomo" wired (base + transformed, both Tripo). Attire 3 "Hood scientist" wired (base + transformed, both Tripo). All attires transform mid-match.
- 2026-10-21: Ladder reorder (owner correction ~19:08 CDT). Before: picker
  slot 1 was the Bosconovitch base GLB ("BASE"), the main roster entry's
  model was the machine-shop reskin, and Attire 1's own pre-form GLB had
  no MODEL_URLS key at all. After: `doc-frank-a1` key added for Attire 1's
  pre-form, main entry + picker default resolve to Attire 1, Tripo pairs
  occupy picker slots 1–8, base + reskin ladder back at slots 9–10 of the
  picker (doc slots 5–6).
