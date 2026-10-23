# HANDOFF — Cape Jones x Western Heart (Grok Bot, 2026-10-23)

Same file in `mhvnsnt/western-heart` and `mhvnsnt/cape-jones` at `docs/HANDOFF-CAPE-JONES-X-WESTERN-HEART.md`.

## What this is
Owner (2026-10-23): tie the Cape Jones 3D show and western-heart ("Immortal Qombat") together in full. Cape's house/room/neighborhood = a WH stage AND the show's setting; in both canons Cape plays the game at home and flies in through the TV; every rigged WH fighter joins the show as cast with show animations (idle/talk/walk/sit/reactions/gestures), **without touching their fight movesets**; those show anims feed WH cutscenes, story, pre-fight and heart-and-mind scenes. cape-jones is the 3D video test ground for WH.

## Files (all NEW, additive, nothing deleted)
western-heart (canonical):
- `shared/cast/build_cast.py` → `shared/cast/cast.json` (34 entries: 33 rigged roster fighters + cape-jones; GLB paths, facing from `game/assets/models/model-facing.json`, rotate-on-import, rig note). References models by path, never copies them.
- `anims/show/INDEX.json`, `anims/show/CLIP-INDEX.json`, `anims/show/README.md`
- `stages/cape-house/STAGE-SPEC.md`
- `docs/story/TV-PORTAL.md`
cape-jones (test ground):
- `shared/cast/cast.json` (mirror) + `shared/cast/sync_cast.sh`
- `shared/cast/render_cast_in_room.py` (proof render; never saves the .blend)
- `shared/cast/proof/pantera_in_cape_room_scene_cam.png`, `..._close.png`, `..._castinfo.txt`
- `docs/story/TV-PORTAL.md` (copy)

## Exact commands
```bash
# rebuild cast (in western-heart root)
python3 shared/cast/build_cast.py
# mirror into cape-jones (in cape-jones root; needs gh auth)
bash shared/cast/sync_cast.sh
# proof render (cape-jones root; Blender 4.2 portable at /home/box/offload/blender/blender-4.2.3-linux-x64/blender)
blender -b 3d-assets/living_room.blend -P shared/cast/render_cast_in_room.py -- <path/to/model-rigged.glb> <rotate_y_deg from cast.json> shared/cast/proof/<name> '[1.2,0.9,0]'
```
Facing: glTF +Z forward imports facing Blender -Y = toward MainCam (0,-4.6,1.7). For `-Z` models pass 180.

## Proof (what the frames show — and don't)
- `pantera_in_cape_room_scene_cam.png` (show MainCam) and `_close.png`: Pantera (leopard-king, model-rigged.glb) standing on the floor of Cape's living room, front-facing, scaled to 1.8 m, Cycles CPU 48 spp, 1280x720. Viewed by Grok Bot.
- REST POSE ONLY. No show animation is baked or retargeted yet. The GLB's stray unparented `Icosphere` helper is hidden in this render only (GLB not edited) — worth cleaning in WH by its owner.

## Log (CT)
- 13:46 start; `df -h /` = 38 G free of 128 G.
- 13:47 claim → mhvnsnt/agent-ops#48.
- 13:48 cast.json built (34). 13:49–13:54 proof render x4 (fixes: evaluated-mesh bbox, hide GLB strays, wider close cam). Frames viewed.
- 13:55 docs + PRs.

## Next steps (pending, in order)
1. Retarget CMU slots (`anims/show/INDEX.json`) onto the 52-bone WH rig → `anims/show/<char>/<slot>.glb` + `SOURCES.md`; render a moving proof clip in cape-jones and view it.
2. Export the living room to `stages/cape-house/living-room.glb` and add a stage-select entry (separate claimed PR; `game/` files are other agents').
3. Bedroom / exterior / street: no 3D yet — fill from teardown stage kits or existing repo assets (owner rule: no hand-tooling).
4. Bake portal scenes `portal_01..03` and wire into WH story mode.

## Owner decisions needed
- Which fighter greets Cape first (proof uses Pantera). Is Cape playable in WH?
- OK to place characters in the canon living room (SCENE-CANON says recliner stays empty until the light-flicker gag)? Proofs never save the .blend.

## How Grok Bot works (copy this)
1. CHECK first: `df -h`, read agent-ops CLAIMS/TAG-TEAM/NO-DATA-LOSS-RULES/ANTI-CLOBBER-LAW + repo AGENTS/WORKLOG/HOW-TO-CONTINUE.
2. CLAIM in agent-ops `CLAIMS.md` (own PR) naming exact paths; stay out of others' files (Claude/Muse own `game/`, `lab/`, rigs).
3. Fresh clone in a unique dir (`/tmp/<agent>-<task>/`, `--filter=blob:none` + sparse for western-heart, 65k files). Never commit from a tree you didn't populate.
4. Feature branch, NEW files only, `git add <explicit paths>` (never `-A`). Commit as `git -c user.name=mhvnsnt -c user.email=197314870+mhvnsnt@users.noreply.github.com`.
5. Before push: `git diff --cached --diff-filter=D --name-only` must be empty; gitleaks (or secret grep) clean. Push each piece as it's done; open PR with the instruction-gate template filled (verbatim owner quote, method, deviations, proof paths).
6. Merge only: MERGEABLE+CLEAN, every latest Actions run success via `gh api repos/<r>/actions/runs?head_sha=<sha>` (unreadable/403 = fail), zero deletions. Otherwise leave open with a comment. Never force-push, rebase pushed work, or delete branches.
7. Look at every render yourself before reporting; say exactly what the pixels show.
