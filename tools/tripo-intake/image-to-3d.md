# Tripo-intake: image→3D source path (worker 22, 2026-10-22)

The intake's primary path is Tripo statics → rig ASAP (owner directive
2026-10-21). This doc wires the **open-source image→3D generators** already
vendored in the repo as alternate sources feeding the SAME intake.

## The vendored generators

| Tool | Location | License | Role |
|---|---|---|---|
| Stable Fast 3D (Stability AI) | `tools/stable-fast-3d/` | see LICENSE.md | Quality image→3D: mesh + UV unwrap + material params |
| TripoSR (VAST-AI) | `tools/triposr/` | see LICENSE | Fast-iteration image→3D (TripoSR family) |

Both were vendored without WH wiring. This doc is the wiring.

## Flow

```
reference image (owner art / concept / photo)
        │  1. generate
        ▼
Stable Fast 3D  →  textured mesh (.obj/.glb + PBR-ish maps)
   --or--  TripoSR  →  fast draft mesh  (iterate, then SF3D for final)
        │  2. drop in the inbox like any Tripo static
        ▼
tools/tripo-intake/inbox/<fighter>/attire<N>.glb
        │  3. intake.py --scan  (facing gate → auto-rig → validate → stage)
        ▼
roster/<fighter>/attires/attire<N>/model-rigged.glb
```

## Which to use when

- **TripoSR first** when iterating on a look: seconds per mesh on a T4,
  good enough to check silhouette/proportions before committing GPU time.
- **Stable Fast 3D** for the keeper: UV-unwrapped + disentangled
  illumination/materials, drops straight into `tools/texture-pipe/`.
- **Owner's standing question** (2026-10-22, unanswered): TRELLIS.2
  (~24GB VRAM, primary pick) vs TripoSR (~6GB, interim) vs Hunyuan3D 2.1
  (quality alt) as the Tripo3D-level open-source generator. When the owner
  picks, the winner slots in at step 1 above — the intake side doesn't change.

## Run notes (Kaggle T4 / local GPU)

```bash
# Stable Fast 3D (needs torch + GPU; see tools/stable-fast-3d/requirements.txt)
python3 tools/stable-fast-3d/run.py --image ref.png --out /tmp/gen.glb
# TripoSR (lighter; see tools/triposr/run.py)
python3 tools/triposr/run.py --image ref.png --out /tmp/gen.glb
# then into the intake like any static:
cp /tmp/gen.glb tools/tripo-intake/inbox/<fighter>/attire<N>.glb
python3 tools/tripo-intake/intake.py --scan
```

Sidecar provenance (`attire<N>.json`) should note
`"source": "stable-fast-3d"` / `"triposr"` + the input image hash, so the
ledger distinguishes generated statics from Tripo pulls.

## Quality gate

Generated statics go through the SAME gates as Tripo pulls: the facing
check REFUSES rather than guesses, and `validate.py` must pass before
staging. A bad generate is re-rolled, never hand-fixed into the roster.
