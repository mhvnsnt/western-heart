# MARIPOSA — Attire Slots (owner 2026-10-18; slot order updated owner 2026-10-19)

Canonical slot map. Mariposa is ONE character (owner 2026-10-18): her Tripo 3D
butterfly model (made based on Zafina) replaced Zafina's in-game model as her
default; the old Zafina in-game models are her later attires. Never split into
two characters.

Ordering follows the Tripo Attachment Registry law (owner 2026-10-18): Tripo 3D
models are the main/default attires; older in-game attires slot in after.
(Pantera is the exception.) Per owner 2026-10-18 ~21:57 CDT: the more custom
Tripo-based attires get built, the further back the Tekken reskins get pushed.

**Owner decision 2026-10-19:** Butterfly Default IS her Slot 1 default —
owner: "if it was her first winged and eyes on wing tripo model then yes that
should be her default." Tripo moves to Slot 2. This is an owner exception to
the Tripo-default law (cf. Pantera Attire 1): the Butterfly Default is a
pipeline-built Tekken-wire custom (PR #282), not a Tripo pull.

## Slots — current (owner 2026-10-19)

| Slot | Display name | Status | Contents |
|------|--------------|--------|----------|
| 1 | **Mariposa — Butterfly Default** (default) | ✅ wired | Pipeline-built Tekken-wire custom (PR #282): dark butterfly silhouette, wing eyeshadow, plum lips, yellow tiger eyes, MPFB2 body morph. `roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb`. Renders: `docs/tpose-refs/mariposa-butterfly-default/`. Owner-designated Slot 1 default 2026-10-19 (owner exception to the Tripo-default law). |
| 2 | **Mariposa — Tripo** | ✅ have | Her proprietary Tripo 3D butterfly model (made based on Zafina; Tripo pull 2026-10-17). `game/assets/models/mariposa.glb`. Was the Slot 1 default 2026-10-18; moved to Slot 2 per owner 2026-10-19. |
| 3 | **Mariposa — Monarch** | 🔒 LOCKED (owner-approved 2026-10-18) | Monarch-orange butterfly wing colorway, black veins, wing eye-spots preserved. PR #271. Renders: `docs/tpose-refs/mariposa-monarch/`. Was Slot 2; now Slot 3. |
| 4 | **Mariposa — Blue Morpho** | 🛠️ in build | Iridescent blue morpho butterfly colorway, black borders. Texture-only on the Tripo model. Slot locks when the owner reviews the render. Was Slot 3; now Slot 4. |
| 5 | **Mariposa — Luna Moth** | 🛠️ in build | Pale luna-moth green colorway, warm brown borders. Texture-only on the Tripo model. Slot locks when the owner reviews the render. Was Slot 4; now Slot 5. |
| 6+ | Zafina in-game models | 📦 have (not wired) | Her Tekken in-game attires ladder behind ALL custom attires: Golden Pharaoh (PR #262), original T6 outfit, etc. See `roster/zafina/attires/`. Was 5+; now 6+. |

## Slots — superseded (2026-10-18 canon, kept for history)

| Slot | Display name | Status | Contents |
|------|--------------|--------|----------|
| 1 | **Mariposa — Tripo** (default) | ✅ wired | Her proprietary Tripo 3D butterfly model (made based on Zafina). Main/default attire per registry law. |
| 2 | **Mariposa — Monarch** | 🔒 LOCKED (owner-approved 2026-10-18) | Monarch-orange butterfly wing colorway, black veins, wing eye-spots preserved. PR #271. Renders: `docs/tpose-refs/mariposa-monarch/`. |
| 3 | **Mariposa — Blue Morpho** | 🛠️ in build | Iridescent blue morpho butterfly colorway, black borders. Texture-only on the Tripo model. Slot locks when the owner reviews the render. |
| 4 | **Mariposa — Luna Moth** | 🛠️ in build | Pale luna-moth green colorway, warm brown borders. Texture-only on the Tripo model. Slot locks when the owner reviews the render. |
| 5+ | Zafina in-game models | 📦 have (not wired) | Her Tekken in-game attires ladder behind ALL custom attires: Golden Pharaoh (PR #262), original T6 outfit, etc. See `roster/zafina/attires/`. |

## Slot-ordering law

- Slot 1: Butterfly Default — owner-designated default (2026-10-19). Owner
  exception to the Tripo-default law (like Pantera's Attire 1): this one is a
  pipeline-built Tekken-wire custom, not a Tripo pull.
- Slot 2: her Tripo 3D butterfly model (`game/assets/models/mariposa.glb`).
- Slot 3: Monarch — owner-locked.
- Slots 4–5: new custom Tripo-based colorways (Blue Morpho, Luna Moth — in build).
- Slot 6+: the Tekken reskins (Golden Pharaoh etc.).
- The owner does the creative customization himself; slots are wired clean.

## Options wired

- Eyes: `customization/parts/zafina-eyes/` (original dark brown saved) +
  universal `customization/eye-library/` (yellow tiger "I like" variant).
- Monarch reskin library: `customization/decal-library/mariposa/` (from PR #271).

## History

- 2026-10-18: Tripo Mariposa attached as default (Attire 1).
- 2026-10-18: Monarch reskin owner-approved as Attire 2 (PR #271, merged).
- 2026-10-18: Blue Morpho + Luna Moth colorways enter the build queue (slots 3/4 provisional).
- 2026-10-18: Canon merged — the two MARIPOSA entries were never two characters.
- 2026-10-19: Owner decision — Butterfly Default IS her Slot 1 default ("if it
  was her first winged and eyes on wing tripo model then yes that should be her
  default"). New order: 1 Butterfly Default, 2 Tripo, 3 Monarch, 4 Blue Morpho,
  5 Luna Moth, 6+ Tekken-wire. Honest note: the Butterfly Default is
  pipeline-built Tekken-wire (PR #282 — "Tripo generation NOT available"),
  not a Tripo pull; the actual Tripo model is `game/assets/models/mariposa.glb`
  (Tripo pull 2026-10-17). Recorded as an owner exception to the Tripo-default
  law, cf. Pantera Attire 1.
