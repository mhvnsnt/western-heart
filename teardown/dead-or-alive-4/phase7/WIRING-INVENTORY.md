# DOA4 Wiring Inventory — Phase 7 (2026-10-21)

Status key: **STAGED** = game-format asset exists in `teardown/`
(not in `game/` — no roster registration this phase; canon is an
owner decision, see `CANON-QUESTIONS.md`). **PARTIAL** = exists with
documented gaps. **NONE** = does not exist yet.

Per-package detail lives in the phase-6 inventories
(`phase6/inventory-chrone.csv`, `phase6/inventory-chrtwo.csv`,
`phase6/inventory-chrthree.csv` — 148 rows) and the phase-6
manifest (`models/phase6-manifest.json` — per-GLB sha256 + size +
release asset). This doc is the per-container roll-up.

| Container | Packages | Skinned GLB | Textures | Clips | Notes |
|---|---|---|---|---|---|
| chrone.afs | 30/30 | STAGED — release `doa4-phase6-models-20261021` (split zips), manifest in git | PARTIAL — pkg00 only: 42 TX2D decoded to PNG (`textures/chrone-pkg00/`), 3 evidence-only material assignments in `models/chrone-pkg00-textured.glb`; other packages untextured (binding gap, `phase7/BINDING-HUNT.md`) | NONE | pkg00 additionally in git as skinned + textured GLB with viewed proof renders |
| chrtwo.afs | 68/68 | STAGED — same release + manifest | NONE decoded (TX2D format solved phase 6; per-package decode not run) | NONE | 17 oversized packages rebuilt with wide windows in phase 6 |
| chrthree.afs | 50/50 full + 25 TX2D-only sub-packages | STAGED — same release + manifest (50 full) | NONE decoded; the 25 sub-packages are texture bundles (XPR2 + TX2D only, verified again phase 7) | NONE | G2 closed by accounting in phase 6 (75/75) |
| mot.afs | 11 packages (old triangulated set) | PARTIAL — mot packages were assembled as model packages in phases 3–6, not as motion data | NONE | NONE — no clip-format parse exists; mot head is plaintext floats (phase 7), so clips are gated on format work, not on any cipher | see `PHASE7-FINDINGS-2026-10-21.md` §3 |
| anm.afs | 1 file, region-mapped phase 7 | n/a | n/a | NONE — updated phase 11: the XEX loader is now FOUND (true-base constant scan; `anm%d.afs` materialized @ 0x8243D650; async state machine, stream object 0x82C3A3D0, cursor stride 0x20) but the 16B-record bit layout + record→stream mapping are still unknown, so no parser and no clips. Exact residual: `phase11/ANM-READER3.md` | region map in phase-7 findings §2; loader family in phase11 |
| stg.afs | 27 packages parsed phase 3 (stg pkg00 graph in git) | PARTIAL — no phase-6-style batch for stages | NONE | n/a (stages) | stage wiring is out of scope for the fighter roster question |

Other staged assets in `teardown/dead-or-alive-4/`:

- 165 triangulated pool GLBs (`models/triangulated/`, PR #386
  import-repaired) — superseded by the phase-6 skinned batch for
  chr*, kept as the decode-provenance record.
- Assembly graphs for all 148 chr packages (`assembly-graphs/`).
- Movesets: `movesets/bass-armstrong/BASS-MOVELIST.md` + the 6
  core fighter move lists noted in
  `DOA4-CONTINUATION-2026-10-19.md` (16–26 moves each; FULL MOVESET
  LAW wants 100+/fighter — flagged, not satisfied).
- Fighter identity of packages: **UNRESOLVED.** Packages are known
  only as chrone/chrtwo/chrthree indices. There is no TOC with
  filenames to recover (§1.2 of the phase-7 findings — no TOC
  exists), so package→character identification must come from
  content (model appearance/moveset matching), not from metadata.
  This is an input to the owner's canon decision.

Wiring blockers, in dependency order:

1. Package→character identification (content-based pass, not yet run).
2. Material→texture binding beyond pkg00's 3 proven assignments
   (`phase7/BINDING-HUNT.md` — hunt run, not found in XEX strings,
   package records, or sub-package directories).
3. Animation clips (anm head/index format + mot/anm stream format).
4. Owner canon decision (`CANON-QUESTIONS.md`) — gates any move
   from `teardown/` staging into `game/`.

## Phase 11 update (2026-10-22, PR #525)

- **Composites: 23 distinct body+head pairings** (phase 10 built 20;
  phase 11 reseated all 7 floaters + the marginal at measured
  neck-junction anchors — all VIEWED seated — and extended with
  pkg10, plus two pairings newly PROVEN by dominant-joint skin bind:
  pkg22 → 0.477 family, pkg31 → group-C family). 8 distinct heads
  remain unpaired (05, 06, 23, 24, 26, 27, 28, 32 — no proof
  available). Detail: `phase11/HEAD-ORIGIN-RESEAT.md`.
- **Clips: still NONE.** The anm loader family is identified in the
  XEX (phase 11 Job 1), narrowing the blocker to the record-consumer
  functions (0x829FD490, 0x8295F7D0) + the per-fighter `D:\bin\*.bin`
  files — see the anm.afs row above.
- **Binding: unchanged.** Phase 11's scan exposed the file system,
  not material setup; proven assignments stay exactly 3
  (`phase11/ANM-READER3.md` §4 negative).
- **ID coverage:** chrone COMPLETE; chrtwo bodies COMPLETE (26/26
  viewed) and all 31 distinct chrtwo heads rendered + viewed;
  chrthree 0/50 bodies viewed — chrthree "pkg50" does not exist as a
  model package (indices 50+ are the TX2D-only sub-packages, per the
  chrthree.afs row). Certain character names: still 0; tentatives
  unchanged. Detail: `phase11/ID-TABLE.md`.

## Phase 12 update (2026-10-22, PR #559)

- **Composites: 23 distinct body+head pairings — UNCHANGED.** The 8
  unpaired heads (05, 06, 23, 24, 26, 27, 28, 32) were tested against
  all 50 chrthree bodies with the proven dominant-joint skin-bind Δ
  method: no pairing reaches the Δ = 0.000 bar (pkg26 min Δ = 0.0646,
  pkg28 min Δ = 0.0962; the six origin-bound heads carry no signal).
  The head census is now tested against the COMPLETE body census.
  Detail: `phase12/ID-TABLE-CHRTHREE.md`.
- **Clips: still NONE.** Phase 12 read all 13 jump-table case bodies
  of the anm tag translator raw and completed the ring-writer census
  (tags 5/6/7/8 only): the family is a (tag, key, value) command
  layer — the anm 16B-record consumer is NOT in it, and that named
  route is exhausted with a proven negative. The only remaining
  named route is the per-fighter `.bin` / `anime_cm.bin` definition
  layer from the ISO (not pulled; recorded as the standing next
  step). Detail: `phase12/ANM-READER5.md` (which also proves the
  −0xE800 frame correction for all phase-11 .text VAs).
- **Binding: DYNAMIC-ONLY (terminal verdict).** The phase-12
  draw-path hunt closed empty (TX2D descriptor type 0x30001 is
  materialized nowhere in .text; the XPR2 registry family takes no
  per-decl/per-item index). No static decl→texture table exists in
  the XEX or package records; the 3 proven assignments stand as the
  only static facts. Wiring blocker #2 is closed as dynamic-only.
  Detail: `phase12/BINDING-DRAWPATH.md`.
- **ID coverage: chrone COMPLETE; chrtwo COMPLETE; chrthree COMPLETE
  (50/50 viewed this phase + phase 11).** All 148 phase-6 packages
  have been viewed at least once. Certain names still 0; tentatives
  unchanged; new tentative groups: chrthree 22–28 (armored ×7),
  chrthree 39/41/42/43 (cat-ear). Detail:
  `phase12/ID-TABLE-CHRTHREE.md`.

## Phase 13 update (2026-10-22, PR #569) — FINAL

- **Composites: 23 distinct body+head pairings — FINAL.**
  Phase 13 tested the last two evidence classes for the 8
  unpaired heads (05, 06, 23, 24, 26, 27, 28, 32): TX2D
  texture-record identity (L1 layout census of all 148 packages +
  L2 payload-hash matrix) and slot-grid adjacency. Neither met
  the unique + quantitative proof bar; the heads stay unpaired
  with the matrices landed as evidence. Detail:
  `phase13/HEAD-EVIDENCE.md`.
- **Clips: still NONE — but the route is now OPEN.** The ISO's
  anm.afs is a standard AFS container holding all 26 animation
  definition files (anm_version.bin + 24 per-fighter `.bin` +
  anime_cm.bin), extracted this phase from XDVDFS sector 416009
  and released as `doa4-anime-definition-20261022` (manifest:
  `phase13/definition-manifest.json`; census + decode steps:
  `phase13/ANM-DEFINITION-2.md`). The section-semantics decode
  to clips is the named next lane. CORRECTION OF RECORD: the
  2,949,120 B file phases 7–12 called "anm.afs" is a different
  file from an earlier source image (mislabeled in phase 1);
  the phase-12 "only remaining route" framing and this phase's
  own withdrawn exhaustion draft both trace to that mislabel.
- **Binding: DYNAMIC-ONLY (terminal, unchanged).** 3 proven
  assignments stand.
- **ID coverage: COMPLETE (148/148 viewed).** Certain names 0;
  canon Q1–Q6 OWNER-pending. Closeout: `phase13/
  DOA4-FINAL-STATE.md`.

## Phase 14 update (2026-10-22, PR #574) — ISO closed; ANM definition layer decoded to gate 1; provenance

- **ISO: CLOSED (pending final hash line).** The phase-13 sparse
  assembly resumed at 10/30, part_10's in-flight download was
  left to finish on its own (never killed/duplicated), and the
  remaining parts landed one at a time under the assembler's
  verify→write→delete discipline. Whole-ISO sha256 + the clear
  log: `phase14/PHASE14-STATE.md`.
- **ANM: definition layer DECODED to gate 1.** The fighter .bin
  header is a 32-pointer section table (tiles every file
  exactly, 24/24); w21 is a 1024-entry clip command table;
  mot.afs is a standard AFS with 197 named .mot entries
  (comon.mot lives in cmn.afs; rtm's plain/c_ slots are
  byte-identical kasumi copies). Parser
  `phase14/tools/anm_parse_p14.py` round-trips all 24 files
  byte-exact (GATE 1 PASS). Clips: NONE yet — the keyframe
  grammar (B-stream records + .mot stream grammar + joint
  order) is the exact residual in `phase14/ANM-DECODE.md`;
  no guessed posing. Extracts (mot.afs + default.xex whole)
  released as `doa4-iso-extracts-20261022`.
- **Provenance (mirror vs ISO): anm DIFFERENT** (same size,
  first diff byte 0, 9.83% identical — the phases 7–12 file
  was a different pressing's, quantified). chrone/chrtwo/
  chrthree: (pending — `phase14/PROVENANCE.md`).
- **Composites 23/31 FINAL, binding DYNAMIC-ONLY, ID complete,
  canon Q1–Q6 OWNER-pending: all unchanged.**
