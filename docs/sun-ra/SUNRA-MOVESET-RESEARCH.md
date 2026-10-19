# SUN RĀ — Moveset Research (owner 2026-10-18 ~20:32 CDT)

## 1. Does the Tekken 7 Pac-Man model come with moves/animations?

**NO — verified against the actual files, not assumed.** The rip at
`~/workspace/_sunra-scratch/Pac-Man (Tekken 7) Model Rip/Pac-Man.dae`:
- 24 skinned geometries, 109 joints, **0 animation clips** in `library_animations`
  (parsed the DAE XML directly).
- The 8 "Mouth_A…H" meshes are static mouth-shape morph targets, not animation.
- Pac-Man in Tekken 7 was a stage cameo (Pac-Pixels stage), not a playable fighter —
  he never had a fighting moveset to extract.

## 2. Do the Sketchfab Pac-Man or Tripo GLB have animations?

- **Tripo GLB (cf2dee24):** Tripo 3D models ship as static triangle soup — no rig,
  no animations. The owner's proprietary Sun Rā model will need rigging before
  any animation. (GLB pull itself needs his Tripo studio session — browser lane.)
- **Sketchfab Pac-Man:** fallback only; Sketchfab rips are fan uploads of the same
  T7 model — same zero-animation situation. Not worth a separate pull unless the
  T7 rip is lost. Requires browser lane; not attempted.

## 3. Donor movesets from fighting-game characters of similar size/shape

**Honest finding: no small/spherical-character moveset exists in our teardowns.**
- Gon (T3's small dinosaur) — never pulled. Kuma/Roger/Jack (large, not spherical) —
  not in our teardowns. Mokujin — not available.
- T6 PSP: 0 Tekken models. TTT2: extraction blocked on disk. Urban Reign: PPKs need
  binary RE. VF5: Brad Burns cracked (156 files, model format needs RE).
- Closest usable banks: No Mercy ~1,354 clips (humanoid wrestlers), T3 31 King clips,
  DOA4 Bass movelist (real data, PR #218), CMU mocap 16 clips.

**Key structural fact:** the T7 Pac-Man rig IS humanoid-ish — arms (shoulder/elbow/
wrist + thumb/index/middle fingers), legs (thigh/knee/shin/foot), plus a rich face
rig (face_A–H mouth joints, eye A–D, eyebrow A–E, nose). 109 joints total. So
humanoid donor animations retarget onto him — the "spherical" problem is only
visual (round body), not skeletal.

## 4. Recommended path (owner decides)

**Build Sun Rā's moveset from the merged moveset library** (`game/assets/movesets/`,
PR #252 merged, schema v2) adapted to his rig — tap-to-assign in the moveset
editor, Tekken inputs, Tekken playstyle per his moveset law. Wrestling moves are
welcome in the library but all rewired to Tekken inputs.

Boss-specific design (fits his canon — "Not a fighter. A realm."):
- Base kit: heavy grappler/striker kit (Bass/Vain Abel real-data template works —
  big body, soul-crushing throws fit the soul-eater).
- Boss specials: arena-scale attacks (soul-drain AoE, wrong-fire breath from the
  open jagged mouth, ground-slam shockwave). These are new builds, not donor clips.
- Talking animation: open mouth + jagged teeth (already in the Tripo model) —
  jaw morph driven by dialogue, eyes NEVER blink (the curse).

## Status of this lane

- Pac-Man T7 base GLB built: `~/workspace/_sunra-scratch/sun-ra-full.glb` (881KB,
  9 parts, embedded textures) — wired as his base per the NO-GATE law.
- Skeleton documented: 109 joints, humanoid-ish + face morph rig.
- Tripo GLB pull: needs his Tripo studio session (browser lane) — cannot pull
  as a background agent.
- Canon: new entries drafted (Curse of the Stare, Bleeding Eyes, Mouth Blood).
- Video: renders after Tripo GLB lands and rig transfer is done.
