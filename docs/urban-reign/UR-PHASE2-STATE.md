# UR Phase 2 STATE
workdir: ~/workspace/ur-phase2-work/ (STATE + scratch)
branch: ur-phase2-motion (PR #442, stacked on ur-sweep1-wiring / PR #434)
report: docs/urban-reign/UR-PHASE2-REPORT.md (this repo)

## Format status — COMPLETE
- .gyu bank layout PROVEN; track types 8/12/13/14 all decoded.
- Validation: 56,844 tracks across all general banks + all 31 pmot +
  10 tmot packs decode with 0 failures.
- Motion bone 0 = root position track; bones 1..20 = Euler rotations.
- Mapping: motion bone b -> GLB node index b (H-index, documented in
  every artifact); composition = local delta (L = Lbind · R_euler),
  root delta on node 12, scale 0.4034 (pose-evaluator position path).
- char001 proof: baked frames 0/24/47/70 VIEWED — coherent authored
  fighting motion; embedded-GLB sample reproduces bake at 1.8e-07.
  Open: true game node graph (phase-1 open item too); one rigid
  accessory piece swings wide in pmot001 m0 f47-70.

## Jobs
1. gyu conversion: DONE (decoder + embedder + batch + general bank
   packed). 31 pmot chars native-embedded; 41 proxy (no pmot bank).
   Movelist NAME mapping still open (pmotID correlation) — moves
   stay engine-base, labeled as such per fighter.
2. textures: NOT cracked. Tail = interleaved VIF/GIF stream; next
   step = VIF/GIF stream walker -> virtual GS memory -> deswizzle
   from stream-declared TEX0. #306 state stands.
3. polish: not started (conditional on 1-2; char064 s16 group +
   11 accessory pieces remain open).
