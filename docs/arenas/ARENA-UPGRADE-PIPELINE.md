# ARENA UPGRADE PIPELINE — from prototype blockout to real arena

**Owner directive (2026-10-22):** "FIRST: save every current arena EXACTLY as it is right
now — these become 'arena drafts,' a revertible baseline. THEN: upgrade them from the
prototype 3JS look to real arenas. Document the pipeline (concept → blockout → detail
pass → lighting → polish)."

**Expanded direction (2026-10-22):** keep the arena IDEAS and NAMES — especially the
proprietary universe ones. The concepts stay; the VISUALS go from "blocky minecraft
roblox 3JS prototype" to real arenas. Source every upgrade from **teardown files, NOT
hand-tooling**. The Pink Narwhal SmutBase map (strip-club interior) is confirmed as the
arena base for club/DJ/music-themed arenas — it is the first teardown-sourced upgrade.

This doc is written so the owner can follow along and art-direct every arena at every
stage. Each stage ends with a **HANDOFF** — the exact thing the owner looks at and the
exact decision they make before the next stage starts.

---

## 0. The law above the pipeline

1. **Concepts are locked, visuals are not.** Arena names, canon, descriptions, and
   associated fighters never change in this pipeline. Only the geometry/materials/
   lighting get upgraded.
2. **Teardown-first, never hand-tool.** Every piece of detail geometry comes from a
   teardown source (`teardown/`, SmutBase pulls, the asset catalog). Procedural
   placeholders are allowed ONLY as blockout/fallback, never as the final look.
3. **Drafts are sacred.** `arenas/drafts/` holds every arena exactly as it was before
   its upgrade — code, assets, and a hash manifest. Any stage can be reverted
   independently. (See `arenas/drafts/2026-10-22/MANIFEST.md`.)
4. **Surgical edits, green merges.** Arena upgrades land as PRs that touch only that
   arena's builder/assets. Never rewrite `stages.js` wholesale.

## 1. The six stages

### Stage 1 — CONCEPT / LOCK ✅ (already done for the whole roster)
What it is: the arena's identity — name, universe, element, description, home
fighters, mood. This is the part the owner already loves.
Where it lives: the `STAGES` registry in `game/js/stages.js`, plus
`prototype/stages/*.json` (the original concept docs).
**HANDOFF 1:** owner confirms the concept still stands (names/descriptions/attribution).
No geometry exists yet. Output: a locked concept line in the tracking table (§3).

### Stage 2 — BLOCKOUT ✅ (already done — the current arenas ARE the blockouts)
What it is: the current procedural arenas, exactly as playtested. Boxes, cylinders,
and placeholder pods are *correct* here — a blockout's job is scale, sightlines,
wall distances, spawn points, and camera framing, not beauty. Tekken's own arenas
start exactly this way (greybox).
What we keep from it: `dims` (width/depth/wallDistance), `spawns`, camera params
(`camDist`, `camAngle`, `camPos`/`camTgt`), and the `lighting` palette seed.
**HANDOFF 2:** owner playtests the blockout and approves *layout and feel* —
"the fight feels right here" — before any detail work starts. Output: the draft
snapshot in `arenas/drafts/` (this IS the approved blockout, revertible forever).

### Stage 3 — DETAIL PASS (geometry from teardown files)
What it is: the procedural placeholder geometry is replaced/overlaid with real
teardown-sourced geometry, converted to web-ready GLB/OBJ:
- Tekken 3 panoramas → `game/assets/stages/t3/` (already done — the T3 retro tier
  is the reference implementation of this stage).
- WWF No Mercy N64 arenas → `game/assets/stages/no-mercy/` (already done —
  `tools/stage-arena-pull/convert_nomercy.py` is the reference converter).
- Tekken 7 / Eastern Mind bitmaps → panorama cylinders (already done for 5 canon
  lands via `def.pano`).
- SmutBase/community maps (e.g. **Pink Narwhal** club interior) → `.blend` →
  Blender headless export → GLB → `game/assets/stages/<arena>/`.
- WWE/WMXIX/Def Jam venues → per `teardown/` extraction status.

The builder pattern (see `buildNoMercy` in `stages.js`): load the GLB, enable
vertex colors + shadows, then re-add ONLY the small procedural furniture the
teardown source can't provide (ropes, cage walls, canon accent lights). The
procedural blockout geometry stays in the builder as the **fallback** if the GLB
fails to load — the arena never renders empty.
Perf rule: keep the GLB under ~25 MB (gltf-transform + meshoptimizer via
`tools/setup/setup_toolchain.sh`); mobile (SwiftShader) must hold 30 fps.
**HANDOFF 3:** owner reviews untextured/greybox screenshots — "does this place
read as <concept>?" Geometry changes only, no material opinions yet.

### Stage 4 — MATERIAL / TEXTURE PASS
What it is: flat colors become real surfaces — teardown texture atlases
(`docs/arenas/t3-texture-pipeline/` is the reference), vertex colors, PBR
roughness/metalness, emissive signage. No new geometry.
**HANDOFF 4:** owner reviews look-dev stills — "do the materials feel right?"
(e.g. Helix Palace: everything reflects; Shrine: cold stone vs warm lanterns).

### Stage 5 — LIGHTING PASS
What it is: the arena's `lighting` block in `stages.js` gets tuned against the
real geometry — sky gradient, fog, hemi/sun/rim/fill, shadow camera bounds,
canon accent lights (lantern flicker, desire-room pods, eyeball glow). The
blockout's palette seed (§Stage 2) is the starting point, not the finish.
**HANDOFF 5:** owner reviews lit day/one screenshots + a 5-second motion clip —
"does the mood match the concept?" This is the last big art call.

### Stage 6 — POLISH / FINAL
What it is: particles/animated accents (already in the builders: leaves, embers,
motes, dust), select-screen thumbnail (`game/assets/stages/thumbs/<id>.png` via
`tools/stage-arena-pull/render_gallery.py`), menu-load budget check (the owner's
menu-speed directive), and the final playtest.
**HANDOFF 6:** owner playtests the finished arena and signs off — or sends it
back to a specific earlier stage with notes. Output: the arena is marked FINAL
in the tracking table.

## 2. How a real team does it (the 60-second version for the owner)

Naughty Dog / Tekken Project / AKI all run the same loop: **concept art →
greybox/blockout (designers playtest scale and sightlines) → environment art
replaces greybox with real geometry → materials → lighting → VFX/polish.**
Nobody sculpts final art first — the blockout exists so the *fight* is proven
before the *beauty* is expensive. Our pipeline mirrors that: your playtests at
Handoff 2 (blockout) and Handoff 6 (final) are the same gates a studio's
design director sits in. The difference: our "environment art" comes from
teardown extraction instead of a 40-person art team, and every gate produces a
screenshot you approve on your phone.

## 3. Tracking table

| Arena | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Teardown source |
|---|---|---|---|---|---|---|---|
| shrine (SHRINE OF THE BLADE) | ✅ | ✅ draft | — | — | — | — | eastern-mind bitmaps (pano pending) |
| tong-nou (TONG-NOU) | ✅ | ✅ draft | — | — | — | — | eastern-mind bitmaps (pano pending) |
| tree-of-life (TREE OF LIFE) | ✅ | ✅ draft | — | — | — | — | eastern-mind pano ✅ |
| plains-of-chi-u (PLAINS OF CHI-U) | ✅ | ✅ draft | — | — | — | — | eastern-mind pano ✅ |
| octagonal-shrine (OCTAGONAL SHRINE PAR-FANG) | ✅ | ✅ draft | — | — | — | — | eastern-mind pano ✅ |
| **helix-palace (HELIX PALACE)** | ✅ | ✅ draft | 🔨 **PILOT — Pink Narwhal GLB** | — | — | — | **SmutBase Pink Narwhal (club interior)** |
| palace-of-dreaming (PALACE OF DREAMING) | ✅ | ✅ draft | — | — | — | — | eastern-mind pano ✅ |
| phantom-marketplace (PHANTOM MARKETPLACE) | ✅ | ✅ draft | — | — | — | — | eastern-mind pano ✅ |
| sunra (SUN RĀ — THE STARING SKY) | ✅ | ✅ draft | — | — | — | — | eastern-mind / canon art |
| t3-* (15 TEKKEN RETRO) | ✅ | ✅ draft | ✅ geometry+textures | ✅ | — | — | tekken3 TMD + texture ARCs |
| nm-* (17 WWF NO MERCY) | ✅ | ✅ draft | ✅ GLB | ✅ vertex colors | — | — | wwf-no-mercy ROM |

Legend: ✅ done · 🔨 in progress (this PR) · — not started.
Stages 1–2 are ✅ for every arena because the drafts *are* the approved blockouts.

## 4. Worked example — PILOT: HELIX PALACE × PINK NARWHAL

Why this arena: Helix Palace ("Land of Desire — five glowing rooms: Greed,
Appetite, Immortality, Sexual Desire, Destruction — everything reflects") is the
canon club/DJ space, and its current builder is the most prototype-looking of
the canon eight (24 flat boxes + 5 glowing spheres). The Pink Narwhal map is a
real club interior — stage, bar, booths, dance floor — i.e. a teardown-sourced
detail pass that lands directly on the concept.

- **Stage 1 (concept):** unchanged — HELIX PALACE, Yui-wang, Metal, "Land of
  Desire… Everything reflects." Home fighter: purple-rain.
- **Stage 2 (blockout):** the current procedural builder, saved verbatim to
  `arenas/drafts/2026-10-22/`. Kept: dims, spawns, camera, lighting palette.
- **Stage 3 (detail):** Pink Narwhal `.blend` → headless Blender export →
  `game/assets/stages/pink-narwhal/pink-narwhal.glb` (fighting surface at y=0,
  club scaled to the 16.8-wide arena). `buildHelix` loads the GLB like
  `buildNoMercy` does; the five desire-room pods are kept as canon accent
  lights repositioned into the club's five zones; the procedural spiral walls
  remain as the no-GLB fallback.
- **Stage 4 (materials):** the .blend's club materials (neon, chrome, leather)
  ride through the GLB export; emissive signage tuned to the five room colors.
- **Stage 5 (lighting):** helix lighting block retuned — magenta/cyan club rig
  against the existing palette; shadow camera fitted to the interior.
- **Stage 6 (polish):** thumbnail re-rendered, before/after screenshots in the
  PR, owner playtest = Handoff 6.

**HANDOFF (owner):** after this PR, play Helix Palace and decide: (a) the club
direction is right → we roll the pipeline to the next arena; (b) adjust — tell
us which stage to send it back to (geometry? materials? lighting?).

## 5. Reverting

Every arena's pre-upgrade state lives in `arenas/drafts/<date>/` with a
`manifest.json` of SHA-256 hashes. To revert one arena: copy its draft files
back over `game/js/stages.js`'s builder (or check out the draft commit) — the
manifest proves the restore is byte-identical. Whole-pipeline revert = the
draft commit itself.
