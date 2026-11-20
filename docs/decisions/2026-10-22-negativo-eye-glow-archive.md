# Decision: Negativo eye glow — per-attire emissive eyes + Tripo archive batch (2026-10-22)

## Owner instruction (verbatim quotes)

1. (2026-10-22, archive batch expanded ~18:14 CDT) Fold three archives into one PR:
   NEGΔTIVO attire 1, NEGΔTIVO attire 2 (before the trials), CornerStone attire 1
   (internal ID stays `ryuji-rock`). Dorowani #603 pattern: immutable-original
   annotated tags for each, byte-verified, manifests.
2. (2026-10-22 ~18:16 CDT, eye glow spec) "Attire 1: glowing RED eyes (emissive
   red). Attire 2 (before the trials): glowing WHITE eyes (emissive white). Wire
   the correct emissive color per attire — per-attire emissive color config, not a
   global eye-glow setting. Data-driven in the attire config so each attire
   carries its own eye color."
3. (2026-10-22 ~18:14 CDT, STANDING DIRECTIVE) "For ALL future Tripo pulls —
   AUTO-ARCHIVE to the repo. Don't ask, just wire them up every time."

## What was decided

- **Eye glow is per-attire, data-driven in `game/js/attires.js`.** The `'negativo'`
  ladder's slots each carry their own `eyeGlow: { color, intensity, materials }`:
  Attire 1 red (`0xff2222`), Attire 2 white (`0xffffff`). No global eye-glow
  setting; nothing hardcoded in the renderer.
- **Eye mesh identification from the model.** The in-game `n3g4tiv0.glb` (Tekken
  Negan-based, 27 materials) carries a dedicated eye material
  `ModelEyes_Material028` — the slot config names it explicitly. The archived
  Tripo originals are single merged meshes with no separate eye material, so the
  glow is a safe no-op there until the rig crew separates eye meshes.
- **Renderer hook in `assets.js createInstance`** (5th param `eyeGlow`), applied
  after material clone + tint so the glow color always wins. Both render paths
  feed it: fight (`fighter.js` via `resolveFighterAttire` → `this.char.eyeGlow`)
  and preview (`select-screen.js` via `attireEyeGlow(c, modelId)`). The
  lighting-rig soul-tint skips materials with `emissiveIntensity > 0.05`, so the
  glow (2.4) is never washed out.
- **Attire 2's slot is `pending: true`.** Its Tripo original is archived but the
  rigged playable model hasn't landed; the white-eye config is wired and waiting.
  `selectableAttires()` hides pending slots from the picker, `selectedAttireModel`
  falls back to the first playable slot — nothing unplayable is selectable, and
  the model-key-guard tests stay green.
- **Archive follows Dorowani #603 exactly:** `roster/<fighter>/attires/attire<N>/`
  `source/<file>.glb` + `manifest.json` (adds sha256), annotated tags
  `negativo-a1-original`, `negativo-a2-original`, `ryuji-rock-a1-original`
  ("Restore point: these bytes never change"). Archived statics are NOT wired
  into `MODEL_URLS` (0 skins → invisible fighter; rig crew lands playable copies).
- **Standing directive logged** in `tools/tripo-intake/README.md` ("Archive
  (automatic)" section) for worker 61's intake inventory: every future Tripo pull
  auto-archives to `source/` + manifest + immutable tag, no asking.

## Files

- `roster/negativo/attires/attire1/source/` — `negativo-a1-futuristic-superhero.glb` (23,252,660 B, sha256 `822c64a6…f67643f`) + `manifest.json`
- `roster/negativo/attires/attire2/source/` — `negativo-a2-sci-fi-armored-suit.glb` (27,085,484 B, sha256 `6750d38f…83942ab`) + `manifest.json`
- `roster/ryuji-rock/attires/attire1/source/` — `ryuji-rock-a1-tattooed-man.glb` (18,872,720 B, sha256 `65884867…59595e51`) + `manifest.json`
- `roster/negativo/README.md` — character dir readme (eye glow spec, archive table)
- `game/js/attires.js` — `'negativo'` ladder, `attireEyeGlow()`, `selectableAttires()`, pending guard
- `game/js/assets.js` — `createInstance` eyeGlow param + emissive application
- `game/js/fighter.js`, `game/js/select-screen.js` — pass per-attire eyeGlow through
- `game/js/roster-full.js` — comment on negativo's entry
- `tools/tripo-intake/README.md` — auto-archive standing directive
