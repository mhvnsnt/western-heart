# SUN RĀ — THE STARING SKY (boss stage)

Kevin's home base. He takes Baek's roster slot and can fight on any stage —
but THIS is home.

## The three inspirations (owner 2026-10-18: "do the research")

### 1. GOD MOLECULE — `docs/GOD-MOLECULE-UNIFIED-BIBLE.md` (God-Molecule-Show-Studio)

- **Four-land taxonomy** (each land locks element + music + soul-force):
  - **Life** = Wood · organic/techno-house textures · growth-duty
  - **Time** = Fire · driving percussion · urgency-duty
  - **Desire** = Metal · sharp synthetic textures · appetite-duty
  - **Dreaming** = Water · fluid ambient textures · memory-duty
  - **Central Mountain** = the trickster hub — **Kevin's territory**: barter-only,
    published-but-absurd exchange rates, no money, every trade has a catch.
  - The arena floor is zoned by the four lands; the center disc is Central
    Mountain with barter glyphs.
- **Mars**: cobalt/electric-blue skin, indigo dreads, solid glowing white eyes.
  The forehead symbol is a **living portal/organ** — it dilates and the dreads
  lift before transit. In the stage, the portal pre-pulses 1.2s before every
  reality shift (Tong-Nou organ reaction), then the shift fires.
- **Reality transitions**: datamosh-style effect bridges + **continuous music** —
  "the cut carries the story" (never bridge with dialogue). The stage runs a
  datamosh shift every ~24–32s: glitch slices, planet smear, portal shockwave,
  floor-texture scroll.
- **Sun Rā canon** (owner): eyes NEVER blink (cursed to stare and watch forever —
  that is why he makes the souls fight); eyes BLEED; blood at the corner of the
  mouth, from the eternal staring, from being the sun, from EATING THE SOULS.
  The stage carries twin bleeding-eye glows under Mars's gaze.
- `music` field on the stage def (`{ land: 'dreaming', palette: 'fluid ambient
  textures', continuous: true }`) is data for audio.js — per-land palette
  wiring is a follow-up.

### 2. TONG-NOU / EASTERN MIND (Osamu Sato)

- Surrealist fever-dream art direction; **living-island heads** (Mars IS the
  island — the stage is built in his sky); reality-shift mechanics;
  death-as-transition. Eastern Mind is ~50% of the Western Heart bible —
  incorporation is a nod, never literal.
- The stage's sky is the void between Macro ↔ Microcosm: starfield, molecular
  grain, planets as the cosmic rung of the scale stack.

### 3. MALAKOR (TikTok — owner: "malakor from TikTok inspired")

- **@obruxomalakor** (🜏 𝕸𝖆𝖑𝖆𝖐𝖔𝖗 🜏) — researched 2026-10-19. Profile: 412
  followers / 754 following / 231 likes / 19 videos. Bio (PT): "🔮 Livros de
  magia, ocultismo e mistérios 📚 Explore conhecimentos fascinantes. ✨ Compre
  agora seu livro e mergulhe nesse universo! AVEH Belzebub Ethan🔱"
  → the vibe is **occult grimoire / mystery**: arcane sigils, ritual rings,
  infernal iconography. The arena carries twin Malakor sigil rings (runic
  circles) around the platform, in dried-blood red.
- Honest flag: TikTok video *content* could not be watched from this lane (no
  live browser on subagents) — the direction is taken from the profile bio,
  stats, and name/iconography. A browser lane can spot-check the 19 videos and
  refine the sigil work; the current design stands on the documented aesthetic.

## The 9 planets

Real relative diameters (NASA fact sheets, km) — the owner locked the 9th as
**Pluto** (his own call, not an original 9th):

| Planet | Diameter (km) | Texture source |
|---|---|---|
| Mercury | 4879 | Solar System Scope 2k (NASA MESSENGER-derived) |
| Venus | 12104 | threex.planets (NASA Magellan-derived) |
| Earth | 12756 | threex.planets 1k (NASA Blue Marble-derived) |
| Mars | 6792 | threex.planets 1k (NASA Viking/MGS-derived) |
| Jupiter | 142984 | threex.planets (NASA Cassini-derived) |
| Saturn | 120536 | threex.planets (NASA Cassini-derived) + ring texture |
| Uranus | 51118 | threex.planets (NASA Voyager 2-derived) |
| Neptune | 49528 | threex.planets (NASA Voyager 2-derived) |
| Pluto | 2376 | threex.planets 1k (NASA New Horizons-derived) |

All textures are cylindrical equirectangular maps derived from NASA/USGS
public-domain mission data — no license risk. Scale anchor: Jupiter radius =
2.2 game units; every other planet is `radius = (diameter/2) × (2.2/71492)`.
Orbits are inclined (each planet's orbit plane tilted ±3–9°) and periods are
scaled for visual effect (44–200s), inner planets faster.

## Mars sky prop

- `mars-sky.glb` — decimated from the owner's Tripo pull
  (`spiky_sun_creature_3d_model.glb`, "spiky sun creature" by marz6kdabest,
  13MB / 1M verts, meshopt-compressed) via `gltf-transform simplify --ratio
  0.05`. Full-res original stays in `~/workspace/tripo-downloads/`.
- Floats at (0, 24, −46), slow yaw + bob. If the GLB fails to load, the stage
  still builds — portal, bleeding-eye glows, and planets carry the sky.

## Arena

- Floor: `buildBase` dark platform + fever-dream zone disc (canvas texture:
  four-land quadrant washes, Central Mountain barter hub, Malakor sigil rings).
- Zone totems for **wizards** (Life/crystal), **thugs** (Time/monolith),
  **goblins** (Desire/spire), **knights** (Dreaming/blade) — emissive
  procedural geometry with rotating rune halos.
- Backdrop ridge: **real Tekken 3 panorama geometry**
  (`game/assets/stages/t3/stg_n_panorama.obj` + atlas), tinted into the
  fever-dream palette. Falls back to the sky gradient if the fetch fails.

## Wire-in

- `game/js/stages.js`: `STAGES.push({... id: 'sunra' ...})`, builder `sunra`,
  new tier `BOSS STAGES` in `STAGE_TIERS`, `GLTFLoader` import.
- Select it in the stage test harness: `await window.__test.jump('sunra')`.

## Honest flags

- Planets are visual-period (not real orbital periods) — real periods would be
  invisible at game scale.
- The `music` def field is data-only until audio.js consumes per-land palettes.
- Mars's eyes are a glow approximation on the static Tripo head (closed-eye
  sculpt) — the "never blinks / bleeding" canon reads through the twin red
  glows + portal pulse.
- Malakor video content not directly watched (see §3) — sigil direction from
  profile research; open to refinement.
