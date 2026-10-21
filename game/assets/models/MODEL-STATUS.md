# Western Heart — Fighter Model Status (Lane 2)

Date: 2026-10-17. Gate = the game's own loader path (`game/js/assets.js`):
valid glTF, ≥1 skinned mesh, Mixamo-style bones (Hips/Spine1/Spine2/Head/
hands/feet), sane world scale (~1.5–2.2 m). Verified with
`workspace/lane2-work/lane2-verify.mjs` (three.js GLTFLoader + meshopt)
and Blender bbox checks — own eyes on the numbers, no worker claims.

## PASS — playable now (6)

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

## FAIL — unrigged miniatures (~2.5 cm, 0 skinned meshes, 0 bones)

Wiring any of these would REGRESS the game (invisible/static fighters;
fighter.js crashes on missing Hips). They are concept sculpts or bad
exports, NOT playable models. Each needs: ×100 scale fix + auto-rig onto
the WH/Mixamo skeleton (tools/rig_repair pipeline) before wiring.

awa-pop, baek, jin-body, kai-body, king-tyrant(+_alt1), kinpo(+_alt1),
lili, n3g4tiv0, nightwolf, pantera_alt1, pantera-body, phantom,
purple-rain, rave, retsu-body, saku-ra(+_alt1), sam-ur-a1(+_body),
skull, thor, waterfall, dxmmii

Affected roster fighters (stay on base fallback until re-rigged):
PHANTOM, SKULL, SAM-UR-A1, SAKU RA, KINPO, WATERFALL, KING TYRANT,
AWA POP, PURPLE RAIN, NIGHTWOLF, CYBORG X (cyborg-x.glb is ValveBiped —
see below), N3GΔTIV0, THOR, DOC FRANK (doc-frank.glb is T7-native —
see below).

## FAIL — rigged but foreign skeleton (needs retarget, not a rename)

| Model | Skeleton | Bones | Height |
|---|---|---|---|
| cyborg-x.glb | ValveBiped (SFM) | 160 | 1.49 m |
| diablo.glb | custom (_Pelvis/_Spine_1/…) | 32 | 2.00 m |
| doc-frank.glb | T7-native (root_hips/spine_lower/…) | 178 | 1.79 m |
| zafina.glb | T7-native | 246 | 1.93 m |
| kinpo-t8.glb | T8-native (SFM) | 244 | 1.12 m |
| phantom-t8.glb | T8-native | 311 | 2.02 m |

## FAIL — Tripo statics (~1 m, 1 mesh, 0 bones, meshopt)

cape-jones.glb (0.93 m), kiko-tanaka.glb (0.98 m),
kiko-tanaka_alt1.glb, purple-rain-main.glb (0.98 m), mariposa.glb (0.86 m).
Loadable now (meshopt wired) but unrigged — auto-rig before wiring.
cape-jones = Cyborg X Attire 1 per canon.

## Re-pulled 2026-10-18 — all parse clean now (earlier errors were
truncated downloads). Final classification: saku-ra-main.glb = Tripo
static (0.98 m, unrigged, meshopt); sha-body / zen-body / zui_alt1 /
zui_alt2 = unrigged miniatures (2.5 cm). Same auto-rig path as above.

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
