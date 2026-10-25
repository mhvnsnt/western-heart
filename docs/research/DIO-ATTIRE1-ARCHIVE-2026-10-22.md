# DIO — Attire 1 archive + transformation archive + moveset spec (2026-10-22)

Crew support lane for DIO. The user is making Dio themselves — this archive
and spec support their work; they do not replace it. No canon is invented
here beyond the user's own words.

## Character description (user's words)

- **DIO** — Shuten-dōji (酒呑童子) inspired Oni. The Oni King of Mount Ōe.
- Massive, muscular demon with wild hair, horns, fierce face, fangs,
  claw-like nails.
- Jade/green skin.
- Levitating tattered wind-blown clothing.
- Godly demonic power vibe.

## Moveset spec (user's words)

1. **Takes over AKUMA's slot completely** — all of Akuma's moves, stance,
   animations, everything. Akuma is Dio's claimed moveset source.
   - Recorded in the claimed map: `docs/movesets/SOURCE-MERGE-2026-10-21.json`
     (`fighters/dio`, tekken_base "Akuma") and `docs/MOVESET-COVERAGE.md`
     (`dio | Akuma | 104 moves | FULL-BANKED`).
2. **PLUS elemental god powers**: controls lightning, water, air, fire,
   thunder. Different elemental attack types. "The all powerful demon" — a
   god of elements.

## Attire 1 archive provenance

- File: `roster/dio/attires/attire1/source/dio-a1-fantasy-demon.glb`
- Source: Tripo3D — "fantasy demon 3d model"
  (https://studio.tripo3d.ai/3d-model/14943921-4f3f-4736-bf02-61d91726872e)
- Size: 21,600,980 bytes (md5 `5278f20cb5bcea2906271664bba314a9`,
  sha256 `9b10d24635c8ed46e68ad724c04d77235fb2549d0c53263a9fbc4616f87905d0`)
- glTF magic verified in the Tripo staging manifest.
- Immutable-original annotated tag: `dio-a1-original`
  ("Restore point: these bytes never change").
- Archive-only: unrigged static, NOT wired into MODEL_URLS.
- Pattern follows the Dorowani Attire 1 archive (PR #603).

## Transformation archive — "Million Eyes Demon" (user's words, 2026-10-22)

- **Form:** Red-skinned demon, million eyes, horns all over body.
  Red Super Saiyan-type aura with electricity and energy/ki around him.
- File: `roster/dio/transformation/source/dio-transformation-million-eyes.glb`
- Source: Tripo3D — "demon creature 3d model"
  (https://studio.tripo3d.ai/3d-model/bdd9e4ef-1c8f-4be2-ac20-5b47ad02bcc5)
- Size: 23,422,084 bytes (md5 `1a4bb9a09bccde42d1bd80b65e8ed134`,
  sha256 `19ca8111fad6109abbe53c78742600559aaadfbecf4d6ea5233f06369a8bb432`)
- glTF magic verified in the Tripo staging manifest.
- Immutable-original annotated tag: `dio-transformation-original`
  ("Restore point: these bytes never change").
- Archive-only: unrigged static, NOT wired into MODEL_URLS.

## Transformation-sequence requirement (user's words — future rig/anim work)

The user wants the visual transformation sequence/form like all other
character transformations — the in-game transformation animation/VFX when
he transforms. The VFX/animation layer is future rig/anim work. What is
needed (recorded, not built):

1. **Transformation trigger** — the in-game moment/condition that starts
   Dio's transformation (same trigger system other character transformations
   use).
2. **Aura/electricity/ki VFX** — red Super Saiyan-type aura with electricity
   and energy/ki around him. This is the VFX target for the sequence.
3. **Form swap** — base Dio form swaps to the "Million Eyes Demon" form
   (red skin, million eyes, horns all over body) as the sequence resolves.

Nothing in this section is implemented by this archive; it is recorded so
the rig/anim lane picks it up with the user's VFX target intact.
