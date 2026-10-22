# Soulcalibur II (Xbox) — Phase 17 State: Placed-Set Re-decode + SCII Closeout

Lane: TEARDOWN COMPLETION SWEEP, Phase 17 (FINAL SCII lane).
Stacked on PR #571 (`scii-phase16-redecode-fixed-reader` @ 1c02ab54).
Branch: `scii-phase17-placed-closeout`. Workdir:
`~/workspace/scii-work/p13/` (sparse clone `wh/` + `work/`).
Banned file NOT touched: `~/workspace/scii-work/p2/v982_idx47.bin`.

## Background (phases 15–16, verified — not re-derived)

The fixed reader (`tools/build_skinned.py`, phase-4 "+8 shift"
deleted + finite assertions) restored the trailer-span rigid parts
the old reader dropped. Phase 16 re-decoded `models-skinned/` +
`models-textured/` + all 80 variants with it: gates passed, +190
base parts, +597 variant parts, the 255-census reconciled exactly,
Nightmare's thigh gap closed (his "sheets" are plate armor).

## Jobs

1. PLACED SET RE-DECODE: rebuild the 22 `models/` placed GLBs
   (phase 3, PR #31 lineage: bind matrix = file 4×4, translation
   ×0.1; world stream reproduced max error 3.1e-07) with the FIXED
   reader through the placement path. They were built with the
   pre-fix reader family, so their trailer-span rigid parts were
   dropped the same way. Gates per file: (a) every part in the OLD
   placed GLB present in the NEW with identical post-placement
   POSITION data (world/placed space); (b) recovered trailer-span
   parts counted per fighter + totaled, reconciled against the
   phase-16 base sets' rigid recoveries per fighter; (c) all
   normals finite; (d) node/skin structure unchanged in kind
   (placed GLBs are rigid — no skins). Renders VIEWED: Nightmare
   placed (front) + Mitsurugi placed + the fighter with the
   largest recovery. In-place GLB replacement on this branch is
   the purpose of the phase.
2. SCII CLOSEOUT: `SCII-FINAL-STATE.md` written to be read
   standalone (100% shipped set / capture-gated / closed-unproven /
   owner-pending / known artifacts / full PR stack list).
3. WIRING-INVENTORY final section (phase-17): placed set fixed
   (counts), closeout doc pointer, sweep-status line for SCII =
   teardown-side COMPLETE. `CANON-CONVERSION.md` untouched.

## NOT this lane's jobs (recorded in the closeout only)

Motion (xemu capture, GRE PR #40 — parent lane), canon assignment
(OWNER), rec80 draw-time binding (dynamic), mmx waveform codec
(CRI middleware, statically closed), the idx632 (Cassandra)
≤4e-09 truncation-tail weight artifact (known, characterized in
PHASE16-STATE).

## Placement-path finding (lane start, verified from bytes)

The phase-3 placed build has no separate script in the repo; its
geometry logic is the one carried inside `tools/build_skinned.py`
("Rigid parts included placed (as phase-4 _placed)"). Verified
empirically at lane start across all 22 files: **every one of the
891 old placed meshes is byte-identical (POSITION / NORMAL /
TEXCOORD_0 / COLOR_0 / index bytes) to the mesh of the same name
in the NEW fixed-reader skinned GLB** — type-4 (skinned) parts use
the shared dst world/bind stream (already placed), rigid parts
use their per-part stream transformed by the node world matrix.
So the placed rebuild is the same geometry code with the fixed
(+0) rigid read, minus skinning: a new repo tool
`tools/build_placed.py` implements exactly that path (bundle →
placed GLB, no skins, one node per mesh).

## Status log

- 2026-10-22 ~06:12 CDT — lane start. Branch created from
  1c02ab54 (PR #571 head); this state doc is the first commit;
  PR opened immediately after (stacked on #571).

## Clears log

- (none yet)
