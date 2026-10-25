# DOC FRANK — Transformation Sequences (Personalized)

**Design law (owner 2026-10-19):** transformations are PERSONALIZED per
character — the visual sequence must reflect who the character IS.

**Who Doc Frank is:** A mad scientist (Bosconovitch/Gero/Mojo Jojo/Dr. Weird
mix). His transform is an EXPERIMENT — serum, device, or unstable science
going wrong (or right). The feeling: body horror, Hulk-style. NOT a clean
magical transformation. It should look like his body is being rewritten by
his own invention, painfully and gradually.

**Owner's spec (verbatim):** "it needs to be like Hulk like kind of like one
arm get big then the other arm get bigger like one leg get big at a time like
you know different parts of him like change size at a time like gradually
into the damn bigger form"

## Universal mechanics (all attires)

- **Trigger:** Player-initiated (KeyT / TRANSFORM button). NOT automatic.
- **Duration:** ~4.5 seconds total. The fighter is VULNERABLE during the
  sequence (can be hit, but gains super-armor on the final phase).
- **Method:** Procedural bone scaling on the RIGGED base model (not a model
  swap). The base model's skeleton scales body parts in sequence; at the
  climax, the mesh cross-fades to the bigger Tripo form.
- **VFX:** Green serum glow (veins), bubbling, steam, lab-equipment hum
  escalating to a roar. Screen shake on each growth pulse.

## Phase breakdown (Hulk-style gradual growth)

| Phase | Time | What happens | VFX/SFX |
|-------|------|--------------|---------|
| 0. **Activation** | 0.0–0.5s | He clutches his chest (or injects/activates a device). His back arches. | Serum glow starts in veins. Low hum. |
| 1. **Right arm** | 0.5–1.2s | Right arm SWELLS — bicep, forearm, fist grow 2x. Veins bulge. | Green glow pulses. Flesh-stretch SFX. Sleeve rips (if clothed). |
| 2. **Left arm** | 1.2–1.9s | Left arm SWELLS to match. He roars. | Same. Louder. |
| 3. **Right leg** | 1.9–2.6s | Right leg SWELLS — thigh, calf grow. He staggers, catches himself. | Ground cracks under foot. Deeper boom. |
| 4. **Left leg** | 2.6–3.3s | Left leg SWELLS. He's now hunched, massive limbs, small torso (Hulk silhouette). | Steam vents. |
| 5. **Torso** | 3.3–4.0s | Torso EXPANDS — chest, shoulders, neck swell to match limbs. The chest device (if any) glows blindingly. | Bright flash. Shockwave ring. |
| 6. **Stabilize** | 4.0–4.5s | He stands upright, cracks his neck, the bigger form settles. Cross-fade to the Tripo bigger mesh completes. | Aura flash. Power-up roar. Super-armor ON. |

## Per-attire flavor

### Attire 1 (Old man → bigger)
- **Flavor:** The serum experiment. He pulls a syringe/activator from his coat.
  The growth is painful — he screams through it. The old man's clothes RIP
  off (shirt shreds at Phase 5). Classic Hulk.
- **VFX:** Green serum veins, tattered coat strips.

### Attire 2 (Wowomomo → bigger)
- **Flavor:** The android/cyborg mix. More MECHANICAL — panels shift, hydraulics
  hiss, the dome FLUID SLOSHES violently. The brain pulses. It's less
  "flesh growing" and more "systems overclocking."
- **VFX:** The green dome fluid churns. Mechanical whir + flesh-stretch hybrid.
  The W emblem glows.

### Attire 3 (Hood scientist → bigger)
- **Flavor:** Mob-boss scientist. He adjusts his tie, smirks — then the growth
  hits. He tries to stay composed (straightens his jacket at Phase 1) but by
  Phase 3 he's roaring. The suit RIPS (jacket bursts at Phase 5, pants hold).
- **VFX:** Pinstripes tear. He keeps the glasses (they stretch or pop off at
  Phase 5 — comedic beat).

## Technical implementation

- Requires the RIGGED base model (tools/auto_rig). The procedural scaling
  drives bone scale channels: `upperarm.R`, `upperarm.L`, `thigh.R`,
  `thigh.L`, `spine`, `chest`.
- Each phase: lerp bone scale from 1.0 → target over the phase duration with
  an elastic ease (overshoot then settle — fleshy).
- At Phase 6, cross-fade opacity base → Tripo bigger mesh (0.3s).
- The `tryTransform()` in `game/js/fighter.js` becomes a TIMELINE, not an
  instant swap. (Current instant-swap is the placeholder.)

## Status
DESIGN ONLY. Implementation requires: rigged base models + procedural
animation system + VFX. This doc is the build order.
