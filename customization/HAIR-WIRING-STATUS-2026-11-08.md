# Hair + Customization Wiring — Status (2026-11-08)

Owner orders (2026-11-08): (1) ALL hair from ALL held game files usable and
swappable in the Creation Suite, organized the source games' way (Tekken
pieces/styles, WWE styles), from the actual game files, industry standard.
(2) Hair rigged and ALIVE: physics — gravity, wind, inertia — in game.
(3) Scope expansion: EVERY clothing item / outfit piece / accessory / item
from ALL held games saved INDIVIDUALLY as customization options for ALL
models, same treatment.

## Landed

### Spring-bone hair physics engine — `game/js/hair-spring.js`
Generic, data-driven spring-bone solver (the VRM/UE spring-bone
formulation the source games' physics assets use): per hair bone a verlet
particle at its tip; gravity + wind + inertia; stiffness spring toward the
animated pose; distance constraint to the parent joint; sphere colliders
(head by default); LOD sleep; substeps. Discovery is data-driven — bones
descending from a head bone whose names match the source conventions
(T7 `SWG_`/`Hair_OPT`, DAZ section bones, SmutBase chains) or that the
hair mesh actually weights; face bones blocklisted; the carrier head/neck
bones themselves are never simulated. Rigid hair (source games weight
some styles to the head only) correctly gets NO system and follows the
head.
Wiring: `fighter-depth.js` attaches one system per fighter at match start
and steps all systems per frame (flag `hairPhysics`); `customization-
consumer.js` attaches a system to every hair part it equips (entry
`physics` block tunes stiffness/drag/gravity/wind), stored on
`model.userData.whHairSprings`.
Verification: `game/js/hair-spring.test.mjs` (node --test, repo-vendored
three) proves chain discovery, gravity hang below the rigid-follow tip,
wind displacement, carrier-bone safety, the rigid-null case, and the
WHSpringBones boundary — 5/5 passing at landing.
Division of labour: the pre-existing `game/js/springbones.js`
(WHSpringBones, live via integration.js) keeps driving secondary motion
on WH-authored rigs (Wiggle-2-baked jiggle chains: breast/butt/belly/
cloth + authored hair_jiggle/ponytail chains). hair-spring.js drives
IMPORTED game hair only and never claims a jiggle/ponytail bone, so the
two systems never write the same bone.

### Tekken 7 hair — 33 items (PR: Tekken 7 hair)
31 HAIR (slotId 2) + 2 FACE_HAIR (slotId 7) from the held GRE Steam
teardown (`tekken7-steam/pakchunk0`), T7-native organization: 62 GLBs
(multi-part items keep every component piece — Asuka's 10-part system
included) + 33 held texture maps, registered in the tekken7 CATALOG
(34 parts), PARTS-REGISTRY (1,183), suite catalog (7,735) and
create-fighter index (7,993). Per-item swing-bone/chain counts measured
from the files (Lili 58 bones/16 chains, bs7 66/16, frv 48/12, Eliza
34/9, Xiaoyu 30/5 …).

### Megami (Parvati) — Flora + default attire pieces (PR: Megami)
Flora Hair built from her source blend's `Hair` object (the owner's pick;
dark 20WFFloraHair diffuse): game GLB with the rig pruned to its 23-joint
subset — neck/head + the 19 Flora hair bones in 10 chains — physics-ready
by the same discovery rules. Registered as Megami's MAIN DEFAULT
hairstyle. The five Roses & Bows / Sugar / gauntlet pieces of her owner-
picked default attire were exported individually from the fixed blend
(pantie, garter belt, stockings, choker, black-panel gauntlets) and
registered as individual parts; her suite profile composes them + Flora.

## Exact gaps (logged, never fabricated)

- **T7 textures partial:** GRE extraction holds 33 hair maps total; some
  items hold only a normal/specular map, Lili holds none. Entries list
  exactly what is held. Completion = a GRE texture-extraction pass.
- **T7 CCI color slots:** per-item records not yet extracted → null.
- **Unresolved character codes:** arb, bs7, dnc, frv, ltn, mut kept as
  codes (no held doc names them; never guessed).
- **T7 remaining item slots** (UPPER 38, LOWER 36, FACE 43, HEAD 9,
  FULL_HEAD 5, EXTRA 4, FULL_BODY 1 converted GLBs in the same held
  tree): registration follows this same pattern in the next PRs of this
  lane — not yet landed.
- **Tekken 6:** meshes decode-blocked (DATA401 DEFLATE defect);
  ~2,546 item containers + ~595 hair-name records unclassified.
- **WMXIX:** 153 hair meshes in raw .ymg — registered name-only
  (geometryPending) by earlier lanes; conversion outstanding.
- **WWE 2K19:** YOBJ hair unconverted (2 CAW hair bins extracted only).
- **TTT2:** schema/banks only. **T8:** not owned (archive.org item is a
  single unverifiable 11.7 GB RAR — FOUND-UNVERIFIED).
- **Def Jam:** 1,218 converted GLBs carry POINTS topology — mesh
  conversion pass outstanding before item registration.
- **DOA4:** 272 costume GLBs already in the suite catalog as full-body
  entries; per-item split happens only where the source game splits.
- **Megami composed attire GLB** (body + pieces + Flora as one
  model-rigged.glb for attire slot A2): the full-blend Blender export
  OOMs on this 8 GB VM (474 shape keys; two attempts killed). Pieces +
  Flora + profile composition landed instead; the single-GLB attire
  export remains open for a quiet-VM window or a GLB-surgery merge.
- **Angel Fernandez hairstyles for Megami** (Pilot 2 lane building):
  registry + physics wiring in this lane when their assets land in the
  repo; not landed yet at this writing.
- In-browser visual proof of swaps/physics: the VM's headless Chromium
  was wiped with the old lanes' caches, so the SwiftShader harness could
  not run in this lane; proof at landing is the solver's node test-suite
  (4/4) plus in-repo harness-readiness. Browser proof still owed. (The Flora GLB's skinning was verified byte-exact at bind in its place: skinned == raw positions, max delta 0.0.)
