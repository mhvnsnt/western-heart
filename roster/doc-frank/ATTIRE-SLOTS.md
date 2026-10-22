# DOC FRANK — Attire Slots (owner 2026-10-19; ladder reorder 2026-10-21; owner override 2026-10-21 ~23:14 CDT)

## Ladder rule (owner override 2026-10-21 ~23:14 CDT, verbatim)

> "his 1, 2, 3, 4, 5 should be his Tripo models; the Tekken reskins go toward
> the back, not 1 or 2. Stop showing me the Tekken versions first — show the
> Tripo 3D models I made for him."

Doc Frank's **Tripo models lead picker slots 1–5+**; the **Tekken-based
models go toward the back** — never slot 1 or 2, never the default. This
supersedes the 2026-10-21 ~19:08 CDT ladder rule, which had put Attire 1's
pre-form old man (`doc-frank-a1`) at the forefront: its file lineage is the
PR #263 machine-shop texture reskin of the Bosconovitch base (a Tekken
reskin, not a Tripo model), so the owner moved it back with the other
Tekken-based models. The Dr. Bosconovitch base model and all
retextures/reskins ladder **BACK** behind every Tripo model.

## Character-select picker order (`ATTIRE_VARIANTS['docfrank']`, game/js/attires.js)

| Picker slot | Model key | Provenance |
|---|---|---|
| 1 | `doc-frank-big` — ATTIRE 1 · TRANSFORMED | **Tripo** 2c6cff79 (the default) |
| 2 | `doc-frank-wowomomo` — ATTIRE 2 · WOWOMOMO | **Tripo** |
| 3 | `doc-frank-wowomomo-big` — ATTIRE 2 · WOWOMOMO XL | **Tripo** |
| 4 | `doc-frank-hood` — ATTIRE 3 · HOOD SCIENTIST | **Tripo** f40c7cde |
| 5 | `doc-frank-hood-big` — ATTIRE 3 · HOOD XL | **Tripo** 253812d5 |
| 6 | `doc-frank-frankenstein` — ATTIRE 4 · FRANKENSTEIN'S CYBORG | **Tripo** 2bea6cac |
| 7 | `doc-frank-frankenstein-big` — ATTIRE 4 · FRANKENSTEIN XL | **Tripo** 690d28a2 |
| 8 | `doc-frank-a1` — ATTIRE 1 · OLD MAN | Tekken reskin lineage (PR #263), binds normalized in #465 |
| 9 | `doc-frank` — BOSCONOVITCH BASE | Tekken canon base |
| 10 | `doc-frank-machine-shop` — MACHINE SHOP | Tekken reskin (PR #263) |

Reorder only — every model stays reachable; nothing deleted. The main
`docfrank` roster entry's model is `doc-frank-big`, matching the picker
default. NOTE: with the Tripo bigger form as the default, TRANSFORM from
the default swaps big→big (no visual change); selecting the back-slot
old-man form and transforming still lands on the Tripo bigger form.

## Slots

| Slot | Display name | Provenance | Status | Contents |
|------|--------------|-----------|--------|----------|
| 1 | **Doc Frank — Old Man / Transformed** | Attire GLBs (pre-form GLB + **Tripo** transformed) | ✅ wired (transform mechanic live) | TWO-FORM attire: pre-transform old man (`attire1/pre-transform/model.glb`, key `doc-frank-a1` — Tekken reskin lineage, now a **back-slot** picker entry per the owner override) ↔ post-transform bigger form (`attire1/post-transform/model.glb`, key `doc-frank-big`, **Tripo** 2c6cff79, 2026-10-19 — **the default model for the main `docfrank` entry and the first picker entry**). Mid-match transform via KeyT / 💪 button — Roshi-style. Bigger = +40% power, −12% speed, +15% defense. |
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

- Picker slots 1–7 = Doc Frank's Tripo models, in attire order (owner
  override 2026-10-21: Tripo models lead, slots 1–5+). Slot 1 (the default)
  is Attire 1's Tripo bigger form; the old-man pre-form is the back-slot
  alternate every player can still pick and transform from.
- Tekken-based models (Attire 1 old-man pre-form, Bosconovitch base,
  Machine Shop reskin) always ladder behind every Tripo model — picker
  slots 8–10 here (doc slots 5–6).

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
- 2026-10-21 (~23:14 CDT): Owner override (verbatim): "his 1, 2, 3, 4, 5
  should be his Tripo models; the Tekken reskins go toward the back, not 1
  or 2. Stop showing me the Tekken versions first." The ~19:08 rule had put
  the old-man pre-form (a Tekken reskin by file lineage) at the forefront,
  so the user was still seeing a Tekken version first. Fix: all seven Tripo
  models lead the picker (slots 1–7), `doc-frank-a1` old man moves to the
  back with the Tekken base + Machine Shop reskin (slots 8–10); main
  `docfrank` entry model → `doc-frank-big` (matches the picker default).
  Reorder only — every model stays reachable.
