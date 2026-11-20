# DEMONIO — Transformation Sequences (Personalized)

**Design law (owner 2026-10-19):** transformations are PERSONALIZED per
character — the visual sequence must reflect who the character IS.

**Who Demonio is:** A demonic possession (Devil Jin-style). The demon is
INSIDE him — on his chest, in his blood. The transform is the demon TAKING
OVER. The feeling: violent, supernatural, possession. NOT scientific. It
should look like something ancient and evil bursting out of a human shell.

**Tekken canon research (owner-provided):**
- Tekken 5: body surrounded by **purple haze** → **tattoos form on chest and
  arms** → **two black wings grow/burst from his back**
- Tekken 4: leans back, **lightning surrounds him**
- Tekken 5 ending: **muscles expand suddenly, bursting through gauntlets**,
  horns/wings grow longer, violent explosion, stands howling in the center
- Devil Within: **player-TRIGGERED** (L1+Triangle when Devil Gauge full) —
  NOT automatic

## Base → Winged (DEVIL ASCENSION) — Up transform

**Trigger:** Player-initiated (KeyT). NOT automatic (per Devil Within).
**Duration:** ~5.0 seconds. VULNERABLE until the wings burst (then super-armor).

| Phase | Time | What happens | VFX/SFX |
|-------|------|--------------|---------|
| 0. **The call** | 0.0–0.6s | He clutches his chest (where the demon face is). His head snaps back. | Purple haze wisps rise from his body. Low demonic rumble. |
| 1. **Haze** | 0.6–1.4s | **Purple haze** surrounds his entire body, thickening. He levitates slightly. | Dense purple fog. Lightning flickers INSIDE the haze (T4). |
| 2. **Markings** | 1.4–2.2s | **Tattoos/markings** form on his chest and arms — glowing purple lines that spread like veins. The demon face on his chest OPENS ITS EYES. | Glowing script. The chest-face animates. |
| 3. **Wings BURST** | 2.2–3.0s | He arches back, SCREAMS. **Two black wings BURST from his back** — flesh tears, wings unfold violently. Shockwave knocks back nearby. | Blood/feather burst. Wing-unfold SFX. Shockwave ring. SUPER-ARMOR ON. |
| 4. **Hands BURST** | 3.0–3.8s | **Demon bat hands BURST from his wrists/palms** — the extra 3-fingered hands tear through. He stares at them, flexes. | Flesh-tear SFX. The hands twitch, then obey. |
| 5. **Expansion** | 3.8–4.5s | **Muscles expand suddenly** — his frame grows, horns lengthen. He grows to the winged form's full size. | Violent pulse. Ground cracks. |
| 6. **Howl** | 4.5–5.0s | He stands in the center of dissipating haze, wings spread, **howling**. Cross-fade to the winged Tripo mesh completes. | Explosion of purple flame. Roar. Battle resumes. |

## Base → Human (DEPOWER) — Down transform (rare)

**Trigger:** Player-initiated (Down+KeyT). RARE — the demon LETS GO.
**Duration:** ~3.5 seconds. This is the REVERSE — quieter, almost sad.

| Phase | Time | What happens | VFX/SFX |
|-------|------|--------------|---------|
| 0. **Release** | 0.0–0.8s | He falls to one knee. The purple haze THINS. | Haze dissipates upward. |
| 1. **Recede** | 0.8–1.8s | The chest markings FADE. The demon face on his chest CLOSES ITS EYES. His claws retract. | Markings dim to scars. |
| 2. **Diminish** | 1.8–2.8s | He SHRINKS — muscles deflate, posture becomes human. He breathes hard. | Soft exhale. No shockwave. |
| 3. **Human** | 2.8–3.5s | He stands — just a man, possessed but contained. The demon face on his chest is dormant (a tattoo). Cross-fade to human mesh. | Quiet. He cracks his knuckles. |

**Design rationale:** The down-transform is NOT a power-up — it's a strategic
choice (smaller hitbox, faster, but weaker). The mood is "the storm passes."
This contrasts with the violent ascension.

## Winged → Base (REVERT) / Human → Base (REPOWER)

- **Revert (winged → base):** Wings FOLD and dissolve into haze (1.5s). Quick,
  tactical. No cinematic.
- **Repower (human → base):** The demon face OPENS ITS EYES, haze returns
  (2.0s). The demon reasserts control.

## Technical implementation

- **Haze:** GPU particle system (purple, additive). Density driven by phase.
- **Markings:** Decal/emissive mask on the base mesh, opacity 0→1 in Phase 2.
  (The Tripo base already has a demon face on the chest — enhance with glow.)
- **Wing burst:** The wings are SEPARATE meshes, scaled 0→full with a
  "tear" particle burst at the back. They don't grow — they EXPLODE out.
- **Hand burst:** Same — extra hand meshes scale 0→full with flesh-tear VFX
  at the wrists.
- **Muscle expansion:** Bone scaling (like Doc Frank) OR cross-fade to the
  bigger winged mesh.
- The `tryTransform(direction)` in `game/js/fighter.js` becomes a TIMELINE.
  (Current instant-swap is the placeholder.)

## Status
DESIGN ONLY. Implementation requires: rigged base, particle systems, the
wing/hand burst meshes, VFX. This doc is the build order.
