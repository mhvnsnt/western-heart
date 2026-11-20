# NEGATIVO (N3GΔTIV0) — Galactic Bounty Hunter

Western Heart fighter. Base: Negan (Tekken). Moveset: bryan (`game/assets/movesets/negativo.json`).
Roster entry: `game/js/roster-full.js` (`id: 'negativo'`, model `'n3g4tiv0'`).

## Attire sources (immutable originals)

| Attire | Source file | Tripo UUID | sha256 |
|---|---|---|---|
| 1 — Futuristic Superhero | `attires/attire1/source/negativo-a1-futuristic-superhero.glb` | `7853a4d6-0a22-45e8-943b-a0afe3ec5c34` | `822c64a6…f67643f` |
| 2 — Sci-Fi Armored Suit (before the trials) | `attires/attire2/source/negativo-a2-sci-fi-armored-suit.glb` | `2a13dd2b-7233-4d50-b02d-982bc9c60f16` | `6750d38f…83942ab` |

Each `source/` dir holds the user-provided Tripo original + `manifest.json`, tagged
immutable (`negativo-a1-original`, `negativo-a2-original` — "Restore point: these
bytes never change"). Rig/playable copies derive from these bytes, never replace them.
Both Tripo originals are unrigged statics (0 skins) — the rig crew produces playable
copies; nothing in `source/` is wired into `MODEL_URLS`.

## Eye glow (owner 2026-10-22)

Negativo's eyes glow. **Per-attire emissive color, data-driven in the attire config**
(`game/js/attires.js` `'negativo'` ladder — each slot carries its own `eyeGlow`):

- **Attire 1: glowing RED eyes** — `eyeGlow: { color: 0xff2222, intensity: 2.4 }`
- **Attire 2 (before the trials): glowing WHITE eyes** — `eyeGlow: { color: 0xffffff, intensity: 2.4 }`

The renderer (`game/js/assets.js` `createInstance`) applies the slot's `eyeGlow` to the
meshes whose material/mesh name is in the slot's `eyeGlow.materials` list, identified
from the model: the in-game `n3g4tiv0.glb` carries a dedicated eye material
`ModelEyes_Material028`. The archived Tripo originals are single merged meshes with no
separate eye material, so the glow is a no-op there until the rig crew separates eye
meshes (then the same config applies).

Attire 2's slot is `pending: true` until its rigged model lands — the white-eye config
is wired and waiting; the picker hides pending slots so nothing unplayable is selectable.
