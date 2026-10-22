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
- 2026-10-22 ~04:40 CDT — p15 scratch bundles + intermediate GLBs
  cleared after all jobs landed in git (idx281/283/291/789 .bin,
  untextured GLBs, tex reports, diag scripts, renders dir; the
  textured GLBs + proof renders live in this PR). Ghidra hunt
  scripts/output kept in p15/ghidra (small). Banned file untouched.

## Status log (final)
- JOB 1 DONE: Ivy root cause = rigid reader +8 start shift on
  trailer-span parts (phase-4 heuristic) — color word landed in the
  normal-Y slot; white = NaN (fake "sheet" exclusion), grey =
  ~-3.4e38 -> FLT_MAX overflow at pack. Census proof: all 725 rigid
  parts / 25 bundles unit-normal at +0. Fix in tools/build_skinned.py
  (landed in-repo); idx283+idx291 regenerated: 41 meshes, 22 images,
  1 skin, res 1.176e-07, renders viewed. FINDING: all 102 previously
  shipped GLBs are missing trailer-span rigid parts (255 parts) —
  re-decode is a follow-on lane.
- JOB 2 DONE: idx789 = rigid-only golem (102 rigid parts, 6,823
  verts, 6 textures); tools/build_rigid.py; render viewed (rocky
  segments, cyan seams, rune orb torso). No identity assigned.
- JOB 3 DONE: rec80 secondary = created-and-held (FUN_00025080
  relocates +0x0c beside +0x08; FUN_00025300 creates/uploads every
  VXT record at load); no draw-time stage binding found in the
  functions read — visible-layer verdict not provable statically.
  Shipping rule unchanged.
- JOB 4 DONE: type = section index (FUN_00033fb0 core decompiled);
  type 0xc = section 12 = character sound, CRI `mmx` sound-bank
  container (XHDp sub-bank at +0x40; FUN_000ed4d0 -> FUN_000ed440
  registration); vgmstream rejects container + slices — codec
  closed, residual named.
- JOB 5 DONE: CENSUS-PHASE13.md 83/83 + phase-15 section;
  WIRING-INVENTORY.md phase-15 section; CANON-CONVERSION.md
  untouched.
