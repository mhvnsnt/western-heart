# PROOF — Alisa intake + Immortal Qombat corrections (2026-11-05)

Owner stack: t91u (Alisa into both repos) / t92u (Jungle Outpost map) / t93u (Cape not Zen).

## t91u — Alisa files
### FOUND (real motion SOURCE)
- GRE ASA pack (Alisa T7 mothead): asamot.bin/json, asarotsm.arc, asa.mvl/nhb/vbn
  → landed under `game/assets/anim/t7/alisa-source/` in western-heart and
  `fight/alisa-source/` in cape-jones (see INDEX.md + SHA256SUMS).
- Frame data: `docs/t7t8-reference/frame-data-t8-full/alisa.json`
- Binding: `game/data/cape-alisa-binding.json` (188 moves; anim_source still
  PENDING bake — sources now present)
- FIGHT guard clip already in WH: `game/assets/anim/oss/cyborgx/stance.glb`
  (CMU boxing; owner-approved). Copied into cape-jones as
  `fight/guard_stance/stance.glb`.

### NOT FOUND as playable baked clips
- No `game/assets/anim/t3/alisa/` or `t7/alisa/` wh-anim bank anywhere
- No Alisa GLB/FBX/BVH clip banks outside GRE mothead SOURCE
- Drive search "Alisa"/"ALS"/"Tekken": T3 zip + T6 teardown parts only (no Alisa motion)
- TeraBox manifest: T7 full game listed CANDIDATE/blocked, no Alisa extract listed
- Local clones checked: wh-moves, wh-studio, whpr, wt-main, wt-sweep2, wt-rm,
  wt-matrix10, wh-rma, cjh, gre-*, /tmp/wh-src, cape-proof, agent store

## t92u — Jungle Outpost (stg02)
- Script Scene 6 + §8 item 2: Jungle Outpost, T7 extraction, owner-picked 2026-10-24
- Stage table: stg02 = Jungle Outpost (stg26 = Jungle Outpost 2)
- gltfpack docs REFERENCE a historical 1,669,744-byte Jungle Outpost GLB
  optimization — file itself NOT present in western-heart `game/assets/stages/`,
  GRE, cape-jones, Drive, TeraBox manifest, or local clones
- Only T7 arena binary on disk: `teardown/tekken7/arenas/mishima-dojo_2024-map.rar`
- Gap audit: T7 stage geometry blocked on full-game acquisition

## t93u — Cape vs Zen
- v1 cut second half was Zen vs Pantera (PROOF-immortal-qombat-wh-v1). Corrected.
- Cape 3D show fight rig: `cape-jones` `3d-assets/cape-jones-rig/cape_jones_rigged_w5r*.blend`
  (do not touch sitting lib). Not used in v1.
- Guard pose owner meant: WH `oss/cyborgx/stance.glb` (FIGHT). Now mirrored into cape-jones.

## v2 fight proof
**NOT PRODUCED.** Would require inventing Jungle Outpost geometry and/or
faking Alisa poses from unbaked mothead. Per owner rules: no invent.
Leftovers blocking v2:
1. Bake ASA → playable Alisa FIGHT bank (needs blender + unicorn + common.arc + shipping exe)
2. Jungle Outpost stg02 geom (needs T7 stage extract or owner-supplied GLB)
3. Wire Cape show/fight rig (W5r) or cape-jones.glb with Alisa bank + purple-tights Pantera P1
4. One continuous Cape-vs-Pantera fight ending on Pantera chain-grapple win

## Pantera skin note
Script wants black panther + purple tights = T7King P1 / `pantera.glb` Slot 3.
v1 footage read gold/maned (Leo man / wrong attire). Prefer
`game/assets/models/pantera.glb` / classic P1, not leopard-king/leo man.
