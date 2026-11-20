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


## ADDENDUM 2026-11-08 (evening) — browser proof landed + v4 offset attribution

Visual proof (Playwright + headless Chromium on this VM; three.js, the game's own
engine path) is committed under `customization/proof/hair-wiring-2026-11-08/`:

- `flora-shipped-bind.png` — the Flora GLB **as shipped on main** (PR #1677),
  rendered standalone: dark, textured, natural hang; bind verified two ways
  (in-engine render + numeric check: world @ inverseBindMatrix = identity for
  head/neck/chest joints; skinned == raw bind positions across all 9 prims).
- `flora-phys-lag.png` / `flora-phys-wind.png` — the shipped `hair-spring.js`
  driving Flora's own rig: frame after a 0.55 rad head snap (4 steps) shows
  inertia lag; after wind +X for 45 steps the mass streams sideways. 10 spring
  chains discovered on Flora's rig.
- `ltn-onbody-closeup.png` — a registered Tekken 7 hair (ltn) worn on the
  Megami body in the same harness, textured from its shipped WebP PBR set.

**Attribution note (stage law):** when Flora is rendered alongside the v4 body
GLB (`parvati-basefixed-glb-v4.glb`), the PAIR looks offset — measurement shows
the defect is in the **v4 body build, not the hair**: the body's skinned mesh
sits ~0.33 m below its own skeleton (its deform `head` bone reads Y 1.629 while
the mesh's bounds top out at ~1.41), so any bone-true part reads as floating
next to it. Flora alone is exact. The v4 basefix is the fidelity lane's
artifact (same defect family as the open Megami live-proof issue); fixing the
body build is theirs — no part registered by this lane carries the offset.

**Next work assigned to this lane (owner verdicts 2026-11-08 ~20:20 CST):**
Angel Fernandez hairstyles for Megami — (1) curly AFRO is the owner's
preferred style and its reference has now been received (owner-supplied
screenshots of Angel's public posts, in `~/workspace/user/files/`); (2) the
straight style gets a full strand-grade opaque rebuild (v1 cards rejected as
unrealistic), same evidenced design (centre part, blonde front-left streak,
toggleable headband). Both register here with spring-bone physics when built.
Flora stays Megami's main default hairstyle; the Angel styles are additional
options.

## Addendum 3 — Angel Afro registered (2026-11-08, owner priority)

Owner supplied 5 reference screenshots of Angel Fernandez's public posts (Threads
@the67latina / X / Facebook "Tallest Latin Model") and ordered the afro built as the
priority Angel style for Megami ("the afro will look better"). Built strand-grade on
the Parvati commission rig: Flora's real scalp cap (inner layer) + an ellipsoid volume
shell cut to the bone-space hairline (face opening) + 1,700 opaque helix-curl clump
meshes; silhouette and density governed by the references (rounded dome ~2x head width,
ears covered, sides descend to the jaw, back to the nape, no part, tight curl,
near-black). 6 spring-bone chains (hairFront/hairBack/hairLeft/hairRight/hairTop/
hairTopB) parented to `head`; stiff physics profile via the generic hair-spring driver
(dense curl mass barely sways). Registered as a selectable Megami hair OPTION — Flora
remains her main default hairstyle.
Proof: customization/proof/hair-wiring-2026-11-08/afro-onbody-front.png,
afro-onbody-34.png, afro-solo-back.png (harness applies the labeled compensation for
the known v4-body mesh-vs-skeleton offset; see PR #1679 addendum).
Source evidence: customization/parts/megami-hair/megami-hair-angel-afro/evidence/.
Build script: build_afro.py in the part folder.
Known polish items (not blockers): crown coverage shows dome patches under flat
harness lighting; shell rim edge visible from low angles. Angel straight rebuild
(strand-grade, replacing the PR #1678 v1 card veil) still owed.

## Addendum 4 — Angel Straight REBUILT strand-grade + registered (2026-11-08)

The Pilot 2 v1 straight style (PR #1678) rendered as a translucent card veil; the
owner rejected it ("the hair there looks terrible and unrealistic") and ordered a
strand-grade rebuild. Rebuilt from Flora's real DAZ strand geometry on the Parvati
commission rig (the same system that renders solid as Megami's default hair):
fringe sections removed, waves relaxed, length graded to the evidenced design
(front collarbone / back shoulder blades), centre part kept, near-black sections
authored from Flora's own texture with a darkening factor, the wide blonde streak
kept as its own material section at front-left (baked blonde texture variant),
and Pilot 2's own headband mesh repositioned onto the hairline as a separate
toggleable mesh skinned to `head`. Colours finished at the glTF level
(postprocess_glb.py in the part folder). Bound to Flora's chain set — the shipped
hair-spring driver discovers 10 chains. Registered as a selectable Megami hair
OPTION; Flora remains her main default.
Proof: customization/proof/hair-wiring-2026-11-08/straight-onbody-front.png,
straight-onbody-34.png, straight-solo-back.png (harness compensates the known
v4-body mesh-vs-skeleton offset, labeled in PR #1679's addendum; the dark bun at
the hairline in harness shots is the v4 body's own base hair, hidden in game when
a hair part is equipped).


## Addendum 5 — FIX PASS: afro density/colour + straight cap/headband (2026-11-08)

Parent own-eyes review REJECTED the #1687/#1688 proofs: afro grey and see-through
(smooth dome patches through the curl mass), afro proofs shot on the wrong (white)
stage, the body's own base hair showing inside the afro, pale/white eyes in the
hair proofs, and the straight headband sitting across the forehead like a slab.
This pass fixes all five. Flora remains Megami's main default hair; afro and
straight remain selectable options.

AFRO — root causes established by measurement:
1. GREY WASH: the shipped AngelAfroMat carried KHR_materials_sheen with
   sheenColorFactor [1,1,1] at full strength over thin curl tubes. The rebuilt
   materials carry NO sheen anywhere: curls (0.010, 0.008, 0.006) roughness 0.9;
   dome/cap backing (0.004, 0.004, 0.004) roughness 1.0.
2. SEE-THROUGH PANEL: a "pull-in" deform in the build scaled the front band's
   x/y by 0.55 toward the skull, putting the whole front clump screen BEHIND the
   forehead plane (joined-mesh front extent |y| max 0.146 vs envelope 0.170;
   forehead surface at -0.095..-0.098) — her crown poked through the recessed
   screen as a smooth warm trapezoid (material-ID render confirmed the panel is
   body skin, not dome or curl). The deform is REMOVED: roots sit on the raw
   envelope ~6 cm in front of the forehead, and the sight corridor is tiled by
   layered passes — main 2,100 + frizz 800 + front wall fill 900 + dome-band
   apron 800 + hairline fringe 500 + scalp-cap fill 850 + hairline seal 350 =
   6,300 corkscrew clumps on the registered 6 spring chains (stiff profile).
   The envelope's bottom edge follows the MEASURED Flora hairline at the front
   (set 8 mm below it, natural range) and descends to jaw/nape at sides/back;
   ears covered.
3. STAGE: all fix proofs re-shot on the dark standard stage (#14121c,
   v4 skin-standard lighting), matching every other Megami proof.
4. BASE HAIR HIDDEN (harness + game-side rule): GLTFLoader sanitizes the v4
   body's node name `Hair.001` to `Hair001`; the original hide list used the
   dotted spelling and never matched. Hide by name on ANY object type, both
   spellings. GAME-SIDE COMPOSITION: when a hair part is equipped, hide the
   body's own hair the same way — for the v4 body GLB the group `Hair001`
   (meshes 25_Material40_1_0_0 / 25_Material40_1_0_1) plus the `Full` strand
   mesh where applicable; the combined hero shot hides the Pilot 2 v2 GLB's
   bundled Hair.001 identically.
5. EYES: the Angel-brown eye part (customization/eye-library/
   eye-brown-angel-daz.png) is applied to Irises-2 in the harness
   (radial-remap, RepeatWrapping, flipY=false, SRGB) — no more pale eyes.

Afro verdict (own-eyes on the shipped GLB): dense, black, opaque from front,
3/4, back and top; ~2x head width; back matches the v1 back-view colour target.
SIZE NOTE: density costs geometry — the GLB is now 81,320,784 B / 1,670,136 tris
(was 22,441,832 B / 456,624); registry/index/catalog updated in place (part
counts unchanged: registry 1,192 / suite 7,744 / create-fighter 8,002). Serving
this part through the 25 MiB Pages path needs the same treatment as other
oversize models; the part file itself is correct.

STRAIGHT — cap darkened (AngelCap base factor [0.07, 0.065, 0.06] ->
[0.012, 0.011, 0.010], roughness 1.0) so the sleek top reads as black hair, not
a grey dome; headband repositioned in geometry: base fit + lift (bottom edge ON
the measured hairline, z 1.715) + tip back -8 deg to follow the forehead curve +
hug pass (radial scale 0.96 about the head axis, -0.015 drop, -5 deg tuck);
final band bounds x +/-0.084, y -0.113..-0.029, z 1.704..1.762 (front surface
~5 mm proud of the cap). RESIDUAL, stated plainly: in the three.js proof
renderer the band — a 100%-`head`-weighted accessory mesh — still renders
displaced forward off the cap (visor artifact), although its GLB geometry,
skin indices and weights verify correct (all 74 verts -> joint `head`,
weight 1.0; inverse-bind-matrix recompute changed nothing). Same
mesh-vs-skeleton bind family as the v4 body's -0.33 offset — the fidelity
lane's territory. Per the fix brief's sanctioned fallback, the shipped
straight proofs are shot with the band toggled OFF, plus one labeled band-ON
close proof showing the residual displacement. The band remains a toggleable
sub-part (node `AngelHeadband`).

Harness compensation (unchanged, labeled): proof shots place the hair root at
y -0.33, compensating the known v4-body mesh-vs-skeleton offset; the body fix
belongs to the fidelity lane, not this pass.

Proofs: customization/proof/hair-wiring-2026-11-08/afro-onbody-front-v2-20261108.png,
afro-onbody-34-v2-20261108.png, afro-onbody-back-v2-20261108.png,
afro-onbody-top-v2-20261108.png, afro-closeup-curl-v2-20261108.png,
straight-onbody-front-v2-20261108.png, straight-onbody-34-v2-20261108.png,
straight-onbody-close-v2-20261108.png,
straight-headband-bandon-close-v2-20261108.png.
