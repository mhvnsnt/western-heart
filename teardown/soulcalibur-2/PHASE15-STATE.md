# Soulcalibur II (Xbox) — Phase 15 State: Ivy Solver Residual + idx789 + Probes

Lane: TEARDOWN COMPLETION SWEEP, Phase 15. Stacked on PR #519
(`scii-phase14-stages-costumes-av` @ 5c7b5d1d, OPEN). Branch:
`scii-phase15-ivy-probes`. Workdir: `~/workspace/scii-work/p13/`
(sparse clone `wh/` + `work/`). Banned file NOT touched:
`~/workspace/scii-work/p2/v982_idx47.bin`.

## Jobs
1. IVY SOLVER RESIDUAL (idx283 + idx291): diagnose non-finite normals in
   build_skinned, prove mechanism from bytes, fix solver (tools-side
   guard, never source data), regenerate both GLBs with full gates +
   viewed renders.
2. idx789 RIGID BUNDLE: identify class from structure, assemble via
   rigid path + VXT textures, viewed render; or byte-evidence verdict.
3. REC80 RUNTIME ROLE: XBE material-consumer read near FUN_00025300;
   verdict with texture-stage/sampler proof.
4. TYPE-0XC VIA FUN_00033fb0: decompile, section↔type mapping, payload
   format from loader behavior; decode one section if a standard
   decoder covers it.
5. CENSUS + INVENTORY: CENSUS-PHASE13.md variants 83/83;
   WIRING-INVENTORY.md phase-15 section. CANON-CONVERSION.md untouched.

## Status log
- 2026-10-22 ~03:45 CDT — lane start. Branch created from 5c7b5d1d;
  this state doc is the first commit; PR opened immediately after
  (stacked on #519).
- Disk ~87-88% at start; scratch kept in p13/work, fetched bundles
  cleared after their job lands (clears logged here).

## Clears log
- (none yet)
