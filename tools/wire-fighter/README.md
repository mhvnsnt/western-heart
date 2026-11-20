# tools/wire-fighter — fighter game-wiring generator

Bottleneck #4 (2026-10-19 roster audit): game wiring was manual — 3 JS
files hand-edited per fighter. `wire-fighter.py` generates all three edits
from one command.

## Quick start

```bash
# preview first
python3 tools/wire-fighter/wire-fighter.py \
  --id cain-elias --model ../roster/cain-elias/attires/attire1/model.glb \
  --moveset bryan --name "CAIN ELIAS" --title "The Deadman" \
  --base "Undertaker" --suit 0x1a1a2a --trim 0x8a2be2 \
  --style "Power" --archetype "Grappler" --dry-run

# write (creates .bak backups)
python3 tools/wire-fighter/wire-fighter.py \
  --id cain-elias --model ../roster/cain-elias/attires/attire1/model.glb \
  --moveset bryan --name "CAIN ELIAS" --title "The Deadman" \
  --base "Undertaker" --suit 0x1a1a2a --trim 0x8a2be2 \
  --style "Power" --archetype "Grappler"
```

## What it edits (idempotent)

| File | Edit |
|------|------|
| `game/js/assets.js` | `MODEL_URLS['<id>'] = '<model path>'` |
| `game/js/fighter.js` | `MOVESET_MAP['<id>'] = '<moveset>'` |
| `game/js/roster-full.js` | `FULL_ROSTER` entry `{ id, name, title, base, moveset, model, tintStrength, colors, style, archetype }` |

- `--moveset` must be a family already in `MOVESET_MAP`
  (`king`, `demonio`, `heihachi`, `xiaoyu`, `bryan`, `gunjack`, `yoshimitsu`).
- Model path is stored verbatim, relative to `game/js/` (existing convention).
- The script verifies the model file exists before writing anything.
- Existing ids are refused unless `--force` (which rewrites in place).
- `node --check` validates every edited file; `.bak` backups are kept.

## Full pipeline for a new fighter

```bash
# 1. rig it
python3 tools/auto_rig/auto_rig.py --in tripo.glb --out game/assets/models/cain-elias.glb --backend blender-heat
# 2. texture it (optional)
#    ... tools/texture-pipe/ ...
# 3. animate it (optional)
#    ... tools/anim-retarget/ ...
# 4. wire it
python3 tools/wire-fighter/wire-fighter.py --id cain-elias --model assets/models/cain-elias.glb \
  --moveset bryan --name "CAIN ELIAS" --title "The Deadman" --base "Undertaker"
# 5. validate + commit on a branch, open a PR
python3 tools/auto_rig/validate.py --in game/assets/models/cain-elias.glb
```
