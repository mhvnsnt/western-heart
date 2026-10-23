# DOA4 — FINAL STATE (phase 13 closeout, 2026-10-22)

The honest final accounting for Dead or Alive 4 (Xbox 360) after
thirteen teardown phases. Standalone: every claim names its proof
document. Staged content lives under `teardown/dead-or-alive-4/`;
NOTHING DOA4 is registered in the game roster — canon is an owner
decision (Q1–Q6, §4).

## §1 At 100% — extracted, decoded, assembled, proven

- **ISO / XDVDFS: 100%.** Release `doa4-iso-v1` (30 parts,
  7,834,892,288 B) re-verified part-by-part against the store's
  sha256 digests (phase 13 landed parts 01–04+ byte-verified into
  a sparse assembly; log in `phase13/PHASE13-STATE.md`). The full
  filesystem is censused: 62 entries (`phase13/
  xdvdfs_tree_full.json`) — 11 root files + dic/ (3) + SOUND/ (26)
  + movie/ (19). Partition layout corrected this phase: standard
  XGD2, base 0x0FD90000, magic at 0x0FDA0000 (the phase-1
  "0x390000" note was wrong; its extraction results stand).
  XDVDFS extraction from the assembled ISO proven against the
  independent mirror store (avt.afs: head / filename-block /
  mid-body spans byte-identical; cmn.afs extracted whole).
- **Standard AFS (cmn/snd/spr/avt): 100%.** 961 files extracted
  (phase 1); filename blocks fully censused (phase 13: cmn 7,
  snd 201, avt 700 named entries; spr 53 entries by size).
- **Custom volumes (chrone/chrtwo/chrthree/mot/stg): data 100%
  plaintext.** The 2026-10-17 "encryption" was a table-layer
  mirage (phase 7): file data was never encrypted; packages are
  index-addressed and carved by structure.
- **Character packages: 148/148.** chrone 30 + chrtwo 68 +
  chrthree 50 (+25 TX2D-only sub-packages accounted) — every
  package's directory parsed and inventoried (phase 6).
- **Assembly + skinning: 100%.** 148 skinned GLBs / 8,241 meshes
  (release `doa4-phase6-models-20261021`, manifest with sha256 in
  git); bind reproduction error 0.000000 (phase 6).
- **TX2D texture decode: 100%.** Format solved (X360 fetch
  constants, tiling, DXT1/DXT5/8888); per-package census of ~6,000
  TX2D records (phase 13 L1 census, all 148 packages).
- **Heads: attach rule 100%, composites 23/31 distinct.** Heads
  are separate chrtwo packages (04–45, 31 distinct); attach is by
  Hie node identity (phase 10), reseated per-head by skin-weight
  origin class (phase 11), every composite VIEWED seated.
- **Identification viewing: 148/148 packages viewed** (phases
  8–12: chrone, chrtwo bodies + all 31 distinct heads, chrthree
  50/50). Tentative family groupings recorded; **certain
  character names: 0** — identification is content-tentative by
  design until the owner rules (Q1–Q6).
- **XEX: decrypted PE, loader/filesystem families mapped**
  (phases 11–12: file table, AFS descriptor registry, anm loader
  state machine, stream object + 0x20 stride, tag-translator
  family fully read raw).

## §2 Terminal — dynamic-only (statically exhausted, proven)

- **Texture→material binding: DYNAMIC-ONLY** (phase 12 terminal
  verdict; the draw-path hunt closed empty: the TX2D descriptor
  type is materialized nowhere in .text). Exactly 3 static
  assignments are proven (chrone pkg00: decl1→tex30,
  decl12→tex40, decl30→tex40); the rest are decided by the engine
  at runtime.
- **ANM animation: definition layer FOUND, decode pending**
  (phase 13, `phase13/ANM-DEFINITION-2.md` — which supersedes
  this lane's own same-day exhaustion draft, withdrawn in
  `phase13/ANM-DEFINITION.md`). The ISO's anm.afs is a standard
  AFS container holding all 26 definition files
  (anm_version.bin + 24 per-fighter `.bin` + anime_cm.bin) —
  extracted, released (`doa4-anime-definition-20261022`),
  manifest in git, container round-trip byte-exact. The files
  carry 34-u32 section headers + curve/index sections per
  fighter and a 16 B-record common table (anime_cm). **Clips
  shipped: none yet** — the section-semantics decode is the
  named next lane (steps in ANM-DEFINITION-2 §3). Also recorded:
  the 2,949,120 B file phases 7–12 studied as "anm.afs"
  (27,392 × 16 B records) is a DIFFERENT file from an earlier
  source image, mislabeled in phase 1 and propagated by the
  mirrors; its censuses stand under that corrected identity.
- **The 8 unpaired heads (05, 06, 23, 24, 26, 27, 28, 32): stay
  unpaired.** Skin-bind Δ exhausted them (phase 12: no Δ=0.000
  against any of 148 bodies; six are origin-bound and carry no
  signal by construction). Phase 13 tested the two remaining
  evidence classes — TX2D record identity and slot-grid adjacency
  (`phase13/HEAD-EVIDENCE.md`): L1/DESC tiers carry no signal;
  the L2 payload tier fires strongly on some proven pairs
  (13–15 shared payloads, unique family) and returns 0–2
  against every family for all 8 unpaired heads; slot-grid
  adjacency nominates families at best and is contradicted for
  26/28. No pairing was forced; the proof bar (unique +
  quantitative) was not met by construction-paper evidence in
  any phase.

## §3 Data assets staged (where things live)

- Models: release `doa4-phase6-models-20261021` (split zips) +
  `phase6/` inventories + per-GLB sha256 manifest in git;
  chrone-pkg00 skinned + textured GLBs in git.
- Textures: chrone-pkg00's 42 TX2D decoded to PNG in git
  (`textures/chrone-pkg00/`); TX2D censuses in `phase13/`.
- Movesets: Bass full movelist + 6 core fighters' lists staged
  (`movesets/`); the XEX's ~206 `D:\bin\*.mot` names are logical
  registry entries — mot.afs (75,393,024 B of float data from byte
  0) is their index-addressed backing store, undecoded as
  per-move data for the same reason as ANM (§2).
- Stages: stg.afs 27 packages parsed (phase 3), not batched to
  GLB — out of the fighter scope of phases 6–13.
- Audio/video: snd.afs banks + SOUND/ streams + movie/ .sfd FMVs
  extracted/censused, not processed further (out of scope).

## §4 Owner-pending (unchanged, canon Q1–Q6)

`CANON-QUESTIONS.md` stands verbatim: Q1 entry mode (guests /
reskins / new canon), Q2 which fighters, Q3 names + rename log,
Q4 moveset treatment, Q5 stages, Q6 order of work. Also pending:
0 certain package→character names (identification stays
tentative-grade until Q1/Q2 aim it). No DOA4 content moves from
`teardown/` staging into `game/` before these are answered.

## §5 What a future lane could still do (named, not promised)

1. **ANM definition decode** (the live route, steps named in
   `phase13/ANM-DEFINITION-2.md` §3): fighter header section
   tables → anime_cm record table → clip framing → gate-2 posed
   render. The data is extracted and released; this is now a
   format decode, not a hunt.
2. **Dynamic binding analysis**: run the game (Xenia) and
   observe the renderer's runtime texture resolution — the only
   route left for binding beyond the 3 proven assignments.
3. **Stage batch**: phase-6-style skinned GLB pass for stg.afs's
   27 packages.
4. **mot.afs stream decode**: its entry structure is
   index-addressed like the chr volumes; the .bin definitions
   (item 1) may name its framing.

*End of the DOA4 teardown sweep. Thirteen phases: extraction,
decryption-myth, assembly, skinning, textures, heads, identity —
closed. Animation and binding — closed as dynamic-only, with the
proofs. Canon — the owner's.*

## Phase-14 addendum (2026-10-22, PR #574) — pointer, additive only

Phase 14 (`teardown/dead-or-alive-4/phase14/`) resumed and
closed the two items §5 named: (1) the ISO assembly completed
30/30 with a whole-ISO sha256 on record and the local assembly
cleared per the one-store rule (`phase14/PHASE14-STATE.md`);
(2) the ANM definition decode (§5 item 1) landed: the fighter
.bin header is a proven 32-pointer section table, w21 is a
1024-entry clip command table, mot.afs is a standard AFS with
197 named .mot entries (comon.mot in cmn.afs), the parser
round-trips all 24 definition files byte-exact (gate 1), and
gate 2 (posed clips) stands as an exact residual — the
keyframe/.mot stream grammar is the remaining decode
(`phase14/ANM-DECODE.md`). A mirror-vs-ISO provenance pass
quantified the pressing correction: the mirror's anm.afs is
DIFFERENT (same size, 9.83% identical); chr* verdicts in
`phase14/PROVENANCE.md`. Canon Q1–Q6 remain OWNER-pending;
nothing else in this document changes.

## Phase-15 addendum (2026-10-22, PR #597) — pointer, additive only

Phase 15 (`teardown/dead-or-alive-4/phase15/`) closed the
provenance question the phase-14 addendum left quantified but
open: the mirror chr streams are an earlier build's package
layout, not a permuted retail copy — containment is regional
(189 of 389 entries byte-contiguous; union coverage
29.8/51.2/48.3 %), and 70 of the 148 library packages now carry
proven filename-grade identities (78 unassigned, honestly).
One phase-8 identification is REFUTED (chrone-pkg29 is tin02,
not an accessory package); the Kokoro / katana-ninja / pkg10
tentatives stand UNRESOLVED. The .mot stream layer is censused
and released (`doa4-mot-20261022`): gate 2's remaining blocker
is now exactly the .mot packed-encoding expansion grammar plus
the loader-side w21 token→record expansion trace in the real
XEX (the .mot loader mechanism itself is proven). Detail:
`phase15/CONTAINMENT-AUDIT.md`, `phase15/MOT-CENSUS.md`,
`phase15/XEX-HUNT.md`, `phase15/PHASE15-STATE.md`. Canon Q1–Q6
remain OWNER-pending; nothing else in this document changes.

## Phase-16 addendum (2026-10-22, PR #697) — pointer, additive only

Phase 16 (`teardown/dead-or-alive-4/phase16/`) attacked phase
15's two named blockers and closed its two disclosed
deviations. The .mot grammar is proven at the record layer
with the framing direction corrected (44 sub-blocks followed
by a 44-entry descriptor of absolute channel offsets; exact
tiling across 530 t_* records and all fighter files), and the
payload's exact residual is named: a stateful per-item length
rule (the simple tag→length rule is falsified by constraint
propagation; no clip assembled, gate G4 stays open). The w21
trace evidences the runtime-record layer at field level
(initializer 0x82406E48, validator 0x824091F0, translator
0x823F6FA0) and names its exact frontier: the file-side
writer from the .bin w21 table to the 0x9C records. The
containment scatter-pass is complete: all 147 probe-grade
rows resolved (118 with byte-exact piece maps, 29 proven
absent), jan02.tpr's absence overturned
(scattered_cross_volume), union coverage chrtwo 52.0069% /
chrthree 50.6650%. Detail: `phase16/MOT-GRAMMAR.md`,
`phase16/W21-TRACE.md`, `phase16/CONTAINMENT-AUDIT-2.md`,
`phase16/containment-map-2.json`, `phase16/PHASE16-STATE.md`.
Canon Q1–Q6 remain OWNER-pending; nothing else in this
document changes.

## Phase 17 addendum (2026-10-22, PR #737) — pointer only
Faithful Ghidra project built (phase-16 import blocker
root-caused to the MZ loader; project at true base 0x82000000,
.pdata-seeded, stored in release
`doa4-ghidra-phase17-20261022`). G4's two items were attacked
with the project + full-sweep data-flow + stateful constraint
propagation: the file-side writer's frontier advanced to
pinned arena bases/pointer globals with the exact missing
link stated (`phase17/W21-TRACE-2.md`), and the .mot length
rule's word-aligned rule classes were exhausted with
falsification counts (`phase17/MOT-STATEFUL.md`). Neither
item is proven; G4 stays OPEN on the same two items, with a
one-session dynamic closure spec'd in
`phase17/XENIA-TRACE-SPEC.md`. Detail:
`phase17/GHIDRA-PROJECT.md`, `phase17/PHASE17-STATE.md`.
Nothing else in this document changes.
