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
  PR opened immediately after (stacked on #571) as PR #573.
- 2026-10-22 — JOB 1 DONE: all 22 placed GLBs rebuilt with
  `tools/build_placed.py` (new repo tool, the placement path with
  the fixed +0 rigid read) from the 22 base bundles already on
  disk in `p13/work/bundles` (phase-13 fetches, header-verified
  then; VMX magic asserted per build). All gates pass per file
  (table below); in-tree replacement committed as the JOB 1
  commit. JOB 1 renders DONE + viewed (below).
- 2026-10-22 — JOB 2 DONE: `SCII-FINAL-STATE.md` written
  standalone (100% set / capture-gated / closed-unproven /
  owner-pending / known artifacts / full PR stack).
- 2026-10-22 — JOB 3 DONE: `WIRING-INVENTORY.md` phase-17 final
  section (placed set fixed + closeout pointer + sweep-status
  line: SCII = teardown-side COMPLETE). `CANON-CONVERSION.md`
  untouched.

## JOB 1 — placed set re-decode (DONE, all gates pass)

Gate method: old placed GLBs snapshotted before replacement
(per-mesh accessor counts + SHA-256 of POSITION/NORMAL/
TEXCOORD_0/COLOR_0/index bytes, skin count, normals-finite scan).
New GLBs must contain every old mesh with identical counts and —
stricter than the task gate (a), which allowed ≤1e-05 in placed
coordinates — identical accessor BYTES; normals finite
everywhere; structure unchanged in kind. The tolerance actually
needed was **zero**: byte equality held for all 891 old parts in
all 22 files (the placement transform is deterministic and the
fixed reader changes only which rigid parts are included, never
their bytes). Gate (d) actual structure, old and new alike:
**rigid GLB — 0 skins, 0 images, one scene node per mesh
(node count == mesh count), meshes named `g{gi}p{ii}` for
type-4 parts (shared dst-stream attributes) and `g{gi}p{ii}_r`
for rigid parts.** Only the generator string changed
(`scii-phase4-decoder-v2` → `scii-phase17-placed-fixed-reader`).

| Entry | Fighter | Old parts | New parts | Recovered | = phase-16 base recovery | Gate |
|---|---|---|---|---|---|---|
| 47 | Mitsurugi | 39 | 51 | +12 | +12 ✓ | PASS |
| 86 | Seong Mi-na | 55 | 63 | +8 | +8 ✓ | PASS |
| 125 | Taki | 41 | 49 | +8 | +8 ✓ | PASS |
| 164 | Maxi | 32 | 36 | +4 | +4 ✓ | PASS |
| 203 | Voldo | 34 | 36 | +2 | +2 ✓ | PASS |
| 242 | Sophitia | 33 | 37 | +4 | +4 ✓ | PASS |
| 281 | Ivy | 46 | 59 | +13 | +13 ✓ | PASS |
| 320 | Kilik | 30 | 32 | +2 | +2 ✓ | PASS |
| 359 | Xianghua | 22 | 24 | +2 | +2 ✓ | PASS |
| 398 | Yoshimitsu | 83 | 102 | +19 | +19 ✓ | PASS |
| 437 | Nightmare | 56 | 86 | +30 | +30 ✓ | PASS |
| 476 | Astaroth | 25 | 34 | +9 | +9 ✓ | PASS |
| 515 | Cervantes | 49 | 62 | +13 | +13 ✓ | PASS |
| 554 | Raphael | 39 | 41 | +2 | +2 ✓ | PASS |
| 593 | Talim | 36 | 38 | +2 | +2 ✓ | PASS |
| 632 | Cassandra | 40 | 42 | +2 | +2 ✓ | PASS |
| 671 | Necrid | 17 | 24 | +7 | +7 ✓ | PASS |
| 710 | Yun-seong | 33 | 40 | +7 | +7 ✓ | PASS |
| 827 | UNIDENTIFIED (1e) | 28 | 37 | +9 | +9 ✓ | PASS |
| 866 | UNIDENTIFIED (1f) | 24 | 28 | +4 | +4 ✓ | PASS |
| 905 | UNIDENTIFIED (20) | 54 | 79 | +25 | +25 ✓ | PASS |
| 944 | Spawn | 75 | 81 | +6 | +6 ✓ | PASS |
| **total** | **22 fighters** | **891** | **1,081** | **+190** | **+190 ✓** | |

**Reconciliation (gate b): EXACT, zero differences to explain.**
The placed set derives from the same 22 bundles as phase 16's
base sets, and the placement path's part selection is the same
part list (type-4 parts via the dst stream + all rigid parts),
so the trailer-span recovery per fighter is identical to the
base sets' rigid recovery for every fighter. The placed total
(1,081) equals the skinned/textured base total exactly. Largest
recovery: Nightmare (+30); second: idx905 (+25).

## JOB 1 renders (DONE, all viewed by this lane)

Proof renders in `phase17-proof/` (Blender/Cycles fronts of the
PLACED GLBs, old-vs-new; placed GLBs are untextured, rendered in
the standard gray material):

- `nightmare-placed-old-vs-new-front.png` — **Nightmare placed
  verdict: his armor is COMPLETE in placed form.** Old: bare
  head (no helmet), hollow cuirass, shorts ending in an empty
  gap with the greaves floating detached below. New: horned
  helmet with face guard, complete layered cuirass, faulds,
  spiked hip plates, and solid armored thighs joining hip to
  knee — the thigh gap is closed in the placed set too.
- `mitsurugi-placed-old-vs-new-front.png` — old: shoulder
  guards reduced to thin shards, hip scabbards thin ribbons.
  New: full layered sode shoulder guards and complete boxy
  scabbards at both hips.
- `unidentified-20-placed-old-vs-new-front.png` (idx905, the
  largest recovery after Nightmare) — old: left arm in detached
  floating segments, thighs hollow above the knee guards. New:
  arm fully connected (pauldron + segments), cuisses in place
  hip-to-knee, hip side plates added.

## Clears log

- No bundles were fetched this phase (the 22 base bundles were
  already on disk from phase 13 and remain that lane's set; they
  are not cleared here). Lane scratch (`p13/work/p17/out/`
  rebuilt GLBs + gate reports + the old-GLB snapshot in
  `p13/work/p17/oldglb/`) is superseded by the committed tree
  files + this doc's gate table; the scratch dir itself is
  outside git. Banned file untouched.
