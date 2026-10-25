# Western Heart — Fighter Model Status (Lane 2)

Date: 2026-10-17. Gate = the game's own loader path (`game/js/assets.js`):
valid glTF, ≥1 skinned mesh, Mixamo-style bones (Hips/Spine1/Spine2/Head/
hands/feet), sane world scale (~1.5–2.2 m). Verified with
`workspace/lane2-work/lane2-verify.mjs` (three.js GLTFLoader + meshopt)
and Blender bbox checks — own eyes on the numbers, no worker claims.

## PASS — playable now (6 + 41 re-rigged 2026-10-18)

| Model | Skinned | Bones | Height | Notes |
|---|---|---|---|---|
| pantera.glb | 18 | 49 (Hips ✓) | 1.75 m | roster → PANTERA, TOU/KAI/RETSU/GYOU souls |
| steve-fox.glb | 18 | 49 (Hips ✓) | 1.75 m | roster → ZUI + RIN/BYOU/SHA/JIN/ZEN souls + 9 fallbacks |
| jin.glb | 21 | 50 (Hips ✓) | 1.75 m | (demonio moved to its own model) |
| demonio.glb | 18 | 49 (Hips ✓) | 1.75 m | **NEWLY WIRED** roster → DEMONIO (Idle/Run/TPose/Walk clips) |
| pantera_fixed.glb | 18 | 49 (Hips ✓) | 1.75 m | spare fixed Pantera |
| rin-body.glb | 18 | 49 (Hips ✓) | 1.75 m | RIN soul body |

`game/js/assets.js` now registers all per-fighter GLBs in MODEL_URLS
(load-on-demand; prefetch still warms only the 3 bases) and vendors
`game/vendor/addons/libs/meshopt_decoder.js` — Tripo meshopt-compressed
GLBs (cape-jones, thor, waterfall, …) previously could not load at all.

## PASS — Round-2 auto-rig wave, Lane B (2026-10-18)

All 41 previously-failing GLBs re-rigged and passing the playable gate
(valid glTF, ≥1 skinned mesh, Hips + Mixamo-style bones, 1.5–2.2 m).
Verified with `workspace/lane2-work/lane2-verify.mjs` + Blender T-pose
renders (own eyes on every model). Methods:

- **29 unrigged miniatures** — ×100 normalize to target height, facing
  rotated to −Z (pantera convention), then Blender bone-heat auto-rig onto
  the WH 49-bone skeleton (imported from pantera.glb). Heights: 1.75 m
  default; king-tyrant(+_alt1) 1.95 m, thor 1.90 m, dxmmii 1.80 m.
- **6 foreign skeletons** — JSON bone renames to canonical Mixamo-style
  names (no geometry change): cyborg-x (ValveBiped→canonical, 160 bones,
  rescaled 1.48→1.58 m), diablo (custom, 32 bones, 2.00 m), doc-frank
  (T7-native, 178 bones, 1.79 m), zafina (T7-native, 246 bones, 1.93 m),
  kinpo-t8 (T8-native, 244 bones, rescaled 1.12→1.56 m), phantom-t8
  (T8-native, 311 bones, 2.02 m). All keep their native skeletons; only
  names were canonicalized. diablo/doc-frank/zafina/kinpo-t8/phantom-t8
  have 2 spine bones (Spine1/Spine2) — the T3 "Spine" track won't bind on
  them, game doesn't require it.
- **6 Tripo statics** — numpy k-NN weight transfer from pantera's full
  skinned mesh set (bone heat fails on ~1M-vert meshes): cape-jones,
  kiko-tanaka(+_alt1), purple-rain-main, mariposa, saku-ra-main. 49 bones,
  1.75 m, geometry byte-identical to source.

`game/js/assets.js` MODEL_URLS gained 19 append-only entries for the newly
wired per-fighter variants (jin-body, kai-body, king-tyrant_alt1, kinpo-t8,
kinpo_alt1, phantom-t8, pantera_alt1, pantera-body, retsu-body, saku-ra_alt1,
saku-ra-main, sam-ur-a1-body, sha-body, zen-body, zui_alt1, zui_alt2,
kiko-tanaka, kiko-tanaka_alt1, purple-rain-main).

Known honest flags: saku-ra.glb / sha-body.glb are authored in a dynamic
idol pose (leg raised) — rigged in that pose, clips animate from it.
mariposa's wings follow the arm/shoulder bones (nearest-neighbor). The
Blender exports carry a harmless extra `neutral_bone` (50 vs 49 bones) on
some models — the game indexes bones by name and ignores it. Pantera rule
held: NO facial/mouth rig on any King-based model (pantera_alt1,
pantera-body) — the WH skeleton has no face bones at all.

| Model | Skinned | Bones | Height |
|---|---|---|---|
| awa-pop.glb | 31 | 49 | 1.75 m |
| baek.glb | 35 | 50 | 1.75 m |
| jin-body.glb | 32 | 49 | 1.75 m |
| kai-body.glb | 24 | 50 | 1.75 m |
| king-tyrant.glb | 24 | 50 | 1.95 m |
| king-tyrant_alt1.glb | 24 | 50 | 1.95 m |
| kinpo.glb | 16 | 50 | 1.75 m |
| kinpo_alt1.glb | 16 | 50 | 1.75 m |
| lili.glb | 42 | 50 | 1.75 m |
| n3g4tiv0.glb | 25 | 50 | 1.75 m |
| nightwolf.glb | 37 | 50 | 1.75 m |
| pantera_alt1.glb | 18 | 50 | 1.75 m |
| pantera-body.glb | 18 | 50 | 1.75 m |
| phantom.glb | 32 | 49 | 1.75 m |
| purple-rain.glb | 35 | 49 | 1.75 m |
| rave.glb | 28 | 50 | 1.75 m |
| retsu-body.glb | 27 | 49 | 1.75 m |
| saku-ra.glb | 32 | 50 | 1.75 m |
| saku-ra_alt1.glb | 31 | 50 | 1.75 m |
| sam-ur-a1.glb | 24 | 49 | 1.75 m |
| sam-ur-a1-body.glb | 24 | 49 | 1.75 m |
| skull.glb | 27 | 49 | 1.75 m |
| thor.glb | 25 | 49 | 1.90 m |
| waterfall.glb | 21 | 50 | 1.75 m |
| dxmmii.glb | 21 | 49 | 1.80 m |
| sha-body.glb | 32 | 50 | 1.75 m |
| zen-body.glb | 37 | 50 | 1.75 m |
| zui_alt1.glb | 18 | 50 | 1.75 m |
| zui_alt2.glb | 18 | 50 | 1.75 m |
| cyborg-x.glb | 52 | 160 | 1.58 m |
| diablo.glb | 1 | 32 | 2.00 m |
| doc-frank.glb | 25 | 178 | 1.79 m |
| zafina.glb | 38 | 246 | 1.93 m |
| kinpo-t8.glb | 15 | 244 | 1.56 m |
| phantom-t8.glb | 18 | 311 | 2.02 m |
| cape-jones.glb | 1 | 49 | 1.75 m |
| kiko-tanaka.glb | 1 | 49 | 1.75 m |
| kiko-tanaka_alt1.glb | 1 | 49 | 1.75 m |
| purple-rain-main.glb | 1 | 49 | 1.75 m |
| mariposa.glb | 1 | 49 | 1.75 m |
| saku-ra-main.glb | 1 | 49 | 1.75 m |

Roster note: these GLBs are loadable and playable; switching roster
fighters off the steve-fox/pantera fallbacks onto their own models is a
separate roster-lane decision. lili.glb / baek.glb stay UNASSIGNED —
Lili and Baek have NO Western Heart names. Never invent names for them.
cape-jones = Cyborg X Attire 1 per canon.

## No model in repo (unchanged from audit)

BURGER, SCIMITAR, MICHIKO, STAR, TORCH, DIO, BRUNO, YUKIHYŌ, SLICE
(no Bob/Shaheen/Katarina/Christie/Anna/Akuma/Miguel/Armor King/Dragunov
sources in any teardown dir — verified against the full 55k-file tree).
REALIZZT/KUTZ (no Brad Burns/Goh in VF5 teardown — aki/akixx only).
CHORDZ (no Lars source). SUN RĀ boss (no Pac-Man/sun source; needs
owner art direction — "the round, cute, evil sun" is an original build).
VAIN ABEL ELIAS — BLOCKED: mesh not extracted anywhere in repo.
`teardown/dead-or-alive-4/models/bass-armstrong/DOA5_Bass_Armstrong_Costume_1.zip`
is TEXTURES ONLY (43 PNGs, no obj/fbx). Per teardown/BASS-ARMSTRONG.md the
mesh waits on the DOA4 teardown lane (7.3GB ISO reassembly, running).
lili.glb / baek.glb — loadable statics, UNASSIGNED: Lili and Baek have
NO Western Heart names. Never invent names for them.

## Next (for this lane or gapfill-decode)

1. Re-pull the 3 corrupt GLBs; finish zui_alt1/alt2.
2. Run tools/rig_repair (auto-rig transfer) on the unrigged per-fighter
   statics, ×100 scale normalize to canon heights, export Mixamo-rigged
   GLBs, re-run this gate, then wire.
3. Convert Bass Armstrong zip → vain-abel.glb (T-pose, ~1.93 m).
4. Owner call: which foreign-skeleton models get retargeted vs re-rigged.
