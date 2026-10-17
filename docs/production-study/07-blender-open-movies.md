# Blender Open Movies — Production File Study

**Source:** Big Buck Bunny (Project Peach, 2008) production files, CC-BY licensed,
pulled from archive.org (`project-peach`) for study. ~147MB: 5 character .blends,
14 textures, 5 constraint scripts. Full study notes:
`~/workspace/game-leaks-working/blender-open-movies/STUDY-NOTES.md`.

**Skipped (documented honestly):** Sintel .blends (login-gated/torrent-only),
Tears of Steel .blends (DVD-ROM-only, no public mirror), full BBB `blender.zip`
(830MB — disk budget). If disk frees up, `blender.zip` is the next pull.

## What the Pros' Character Files Actually Contain

`rabbit.blend` (the hero character) inspected live:
- **68 objects. TWO armatures:** `RabbitRig` (287 bones, body) + `RabbitFaceRig`
  (99 bones, face) — body and face rigs are SEPARATE
- **Meshes:** main body (4,138 verts), separate eye meshes, `RabbitDef` (238
  verts — low-poly deform/collision PROXY), IK/FK switch controls
- **32 Actions** (animation clips): full-body moves + `COR_*` corrective actions
  (driven by pose, 7–11 frames) + face set + finger set
- **~30 `WIDGT_*` meshes:** custom bone-shape widgets (animator control handles)
- **Custom Python constraints:** foot-roll, pivot-change, volume-preserve
  (0.9–2.2KB scripts)
- **8 materials**, texture naming `<char>_<part>_<map>.png` (`_col`, `_nor`,
  `_spec`, `_alpha`)

## Naming Conventions (the pro pattern)

- Armatures: `<CharName>Rig` + `<CharName>FaceRig`
- Bilateral bones: `.L` / `.R` suffixes
- Corrective actions: `COR_` prefix
- Materials: `<char>_<part>`; Textures: `<char>_<part>_<map>.png`
- Scenes: `NN_sequence/NN.blend` with `00_shared.blend` per sequence

## Production Tree Structure

Assets grouped by DEPARTMENT: `chars/`, `sets/`, `props/`, `envs/`, `mattes/`.
Shots in `scenes/NN_sequence/NN.blend`. Character libraries LINKED into shots,
never duplicated. Textures in sibling `textures/` dirs, referenced by RELATIVE
path. Full render-farm `scripts/` pipeline (batching, EXR validation, dailies).

## What Maps to the Western Heart Character Pipeline

| BBB pattern | Western Heart application |
|---|---|
| One self-contained .blend per character | One asset folder per fighter; roster files LINK, never duplicate |
| Body rig / face rig split | Gameplay skeleton (export to engine) vs cinematic skeleton (intros/taunts/win poses) — keep separate |
| 32 named Actions | Animation state machine entries (idle, walk, jab, special) |
| `COR_*` corrective actions | Additive corrective layers (shoulder/hip fixes on punch poses) |
| `RabbitDef` deform proxy (238 verts) | Hitbox/hurtbox proxy mesh — gameplay skeleton binds to the proxy, hi-res mesh is display-only |
| `pyconstraints/` (foot-roll, pivot-change) | Control-rig logic: grounded stance, turnaround handling |
| IK/FK switch meshes | Procedural vs keyframed limb control |
| Relative-path textures | Repo works on any machine — no absolute paths, ever |
| Department dirs + linked libraries | `assets/characters/[code]/` per fighter, stages link fighters in |

## Key Takeaway

The 2008 Blender Institute ran the same character pipeline our 7-stage Western
Heart pipeline describes — self-contained character libraries, split rigs,
named animation clips, proxy meshes, scripted constraints, relative paths.
The tools changed (Blender 2.47 → UE/Godot); the STRUCTURE didn't. This
validates the pipeline in `06-western-heart-character-pipeline.md`.
