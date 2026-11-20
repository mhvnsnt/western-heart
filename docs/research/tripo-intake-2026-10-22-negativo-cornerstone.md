# Tripo intake note 2026-10-22 — Negativo A1/A2 + CornerStone A1 (worker 67)

Archive batch per owner 2026-10-22 ~18:14 CDT. Dorowani #603 pattern.

## Models archived (byte-verified against tripo-staging originals)

| # | Character / attire | Tripo project | UUID | Bytes | sha256 | Tag |
|---|---|---|---|---|---|---|
| 1 | Negativo A1 (Futuristic Superhero) | futuristic superhero 3d model | `7853a4d6-0a22-45e8-943b-a0afe3ec5c34` | 23,252,660 | `822c64a6f50da0ba43c76d094996a58fb78e92dae94d747bbd01a7fedf67643f` | `negativo-a1-original` |
| 2 | Negativo A2 — before the trials (Sci-Fi Armored Suit) | sci-fi armored suit 3d model | `2a13dd2b-7233-4d50-b02d-982bc9c60f16` | 27,085,484 | `6750d38f340b7cbadd571d5fe04b7bb507c88d9d712bdeca15311b1a843942ab` | `negativo-a2-original` |
| 3 | CornerStone A1 (Tattooed Man) → `roster/ryuji-rock/` | tattooed man 3d model | `20c1fd2e-40d0-4500-9be6-50f6494ab5e1` | 18,872,720 | `658848674696b6c4e47c55f773d2c55e07359595e51e57ce273704dc4871049d` | `ryuji-rock-a1-original` |

Share URLs: `https://studio.tripo3d.ai/3d-model/<uuid>` (see each `source/manifest.json`).

## Model inspection notes

- All three are **unrigged statics**: 1 merged mesh, 0 skins, 0 animations, single
  material, gltfpack 1.2. They archive as immutable originals only — NOT wired into
  `MODEL_URLS` (an unrigged static renders invisible: ZERO skinned meshes).
- Negativo A1's Tripo original has no separate eye meshes (single material). The
  eye-glow feature targets the in-game `n3g4tiv0.glb`, which has a dedicated eye
  material `ModelEyes_Material028` (27 materials total).
- CornerStone's model lands the long-pending `roster/ryuji-rock/attires/attire1/`
  slot (README: "MODEL STATUS: PENDING — no model pulled yet"). Internal id stays
  `ryuji-rock`; WH display name is CornerStone.

## Eye glow spec (owner 2026-10-22 ~18:16 CDT)

- Attire 1: glowing **RED** eyes (`0xff2222`)
- Attire 2 (before the trials): glowing **WHITE** eyes (`0xffffff`)
- Per-attire emissive config in `game/js/attires.js` `'negativo'` ladder; renderer
  hook in `game/js/assets.js` `createInstance`. Details: `roster/negativo/README.md`.

## Standing directive (owner 2026-10-22, logged for the pipeline)

"For ALL future Tripo pulls — AUTO-ARCHIVE to the repo. Don't ask, just wire them
up every time." Logged in `tools/tripo-intake/README.md` ("Archive (automatic)"
section). Worker 61 (intake inventory) owns folding it into `intake.py`.
