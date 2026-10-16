# Handoff — Model Render Status

**Read this + [MODEL_CENSUS_AND_BLOCKERS.md](MODEL_CENSUS_AND_BLOCKERS.md) before continuing T-pose work.**

## What is done
- T-pose standard locked: camera on −X, scale ×100, centered, gray bg. See `docs/TPOSE_RENDER_STANDARD.md`.
- Mariposa (Zafina) confirmed: −90° Z + downward shift.
- Several PR #170 models rendered front-facing with camera-on-−X.
- Census of every set (ready / extracted-but-Source / packed / fully blocked) written to `docs/MODEL_CENSUS_AND_BLOCKERS.md`.

## What is blocked (do not guess)
- **VF5 (19):** `.farc` needs Windows tool.
- **Urban Reign (72):** geometry not decoded; ISO on GitHub release.
- **Soulcalibur 2:** only movesets, no 3D models.
- **TTT2:** release exists, not extracted (disk).
- **Tekken 6:** file map cracked, models locked.
- **T7 archives:** many still packed; no unrar/7z on this box. Extracted ones are often Source `.mdl` and need conversion.
- **T3 donors:** some render exploded — armature/scale issue.

## Next for whoever continues
1. Extract remaining archives (need unrar/p7zip or do it elsewhere).
2. Convert Source `.mdl` → FBX/GLB.
3. Fix or re-export exploding T3 models.
4. Keep rendering every new GLB with the camera-on-−X standard.
5. Update the census as blockers clear.

## Rules
- Feature branch + PR only. Never push WIP to main.
- No procedural generation when teardown data exists.
- Binary PNGs stay local until a binary push path exists.
