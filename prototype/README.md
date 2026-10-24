# Western Heart — Prototype

**Status:** Foundation / design docs + code structure. Not a playable game yet.

## What This Is

The structural foundation for the Western Heart fighting game, built from:
- **Combat system design** — adapted from the tk fighting game (`assets/free-pull-1/tk-fighting-game/`)
- **Fighter data templates** — per-character stats, movesets, visual config
- **Stage templates** — Eastern Mind arena definitions

## Structure

```
prototype/
├── README.md          — this file
├── combat/
│   ├── COMBAT-DESIGN.md    — Nine-Soul Meter, Soul Surge, frame data format
│   └── moveset-template.json — blank moveset template for new fighters
├── fighters/
│   ├── FIGHTER-TEMPLATE.md — how to define a new fighter
│   └── pantera.json        — Pantera (example, fully specified)
└── stages/
    ├── STAGE-TEMPLATE.md   — how to define a new stage
    └── shrine.json         — Shrine stage (example, using ambientCG textures)
```

## How to Run (future)

The prototype targets **Godot 4** with web export (phone browser).

1. Open `western-heart/` in Godot 4.
2. Import fighter models from `teardown/models/`.
3. Load `prototype/fighters/pantera.json` as test fighter.
4. Run the combat scene.

**Not yet implemented:** Godot project files, scene trees, GDScript port of combat core.
See `docs/TK-COMBAT-ANALYSIS.md` for the port checklist.

## Design Pillars

1. **Tekken 7 = primary base.** Modern models, UE4 skeletons.
2. **Frame data is data.** All moves defined in JSON, not code.
3. **Nine-Soul Meter** replaces super meter. **Soul Surge** replaces super moves.
4. **IK-driven combat.** Punches/kicks adapt to each skeleton — no per-character attack animations needed.
5. **Mocap base layer.** Quaternius + CMU clips for locomotion and signature moves.

## Related Docs

- `docs/TK-COMBAT-ANALYSIS.md` — combat system deep-dive
- `docs/ANIMATION-PIPELINE.md` — retargeting plan
- `assets/free-pull-1/INVENTORY.md` — asset catalog
- `CANON.md` — world and character bible
- `ROSTER.md` — fighter roster
