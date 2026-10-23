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

- **ISO: CLOSED.** The phase-13 sparse assembly resumed at
  10/30, part_10's in-flight download was left to finish on
  its own (never killed/duplicated), and the remaining parts
  landed one at a time under the assembler's
  verify→write→delete discipline (proxy-killed attempts
  relaunched by the phase-14 supervisor; no part written
  without its digest matching). **30/30 verified: size
  exactly 7,834,892,288 B, whole-ISO sha256
  `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa`.**
  Local assembly cleared after verification (one-store
  rule); detail + clear log: `phase14/ISO-CLOSEOUT.md` +
  `phase14/PHASE14-STATE.md`.
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
- **Provenance (mirror vs ISO): ALL FOUR DIFFERENT** — anm
  9.8271% identical, chrone 4.2795%, chrtwo 4.6732%,
  chrthree 4.4639% (all same-size, all differing from byte
  0; ISO side all standard AFS containers with 26/73/128/
  188 entries, mirror side all raw streams). The mirror is
  a different pressing's/raw-layout source throughout;
  chrone containment found the retail payloads present in
  the mirror at permuted offsets, so the phase 6–12 models
  stand on the same payload bytes — but no mirror AFS file
  IS the retail file. Detail: `phase14/PROVENANCE.md`.
- **Composites 23/31 FINAL, binding DYNAMIC-ONLY, ID complete,
  canon Q1–Q6 OWNER-pending: all unchanged.**

## Phase 15 update (2026-10-22, PR #597) — containment audited; packages named; .mot census; XEX consumer hunt

- **Containment: DECIDED.** The ISO was re-assembled a second
  time under verify-before-write discipline (whole-ISO sha256
  `4423cd5c…` re-verified) and every named entry of
  chrone/chrtwo/chrthree (73/128/188) was located against its
  mirror stream. Verdict: the mirror streams are an EARLIER
  BUILD's package layout (30/68/75 XPR2 bundles), NOT a permuted
  copy of the retail containers. Containment is regional: 189
  entries byte-contiguous (incl. the chrone retail tail block
  zac00–tin01), the rest re-authored between builds — `.cat`
  texture data survives at 61–88%, `.tpr` model data at 0–25%
  (chrone scatter). Union coverage: chrone 29.7553%, chrtwo
  51.1871%, chrthree 48.2684%. Detail + machine map:
  `phase15/CONTAINMENT-AUDIT.md`, `phase15/containment-map.json`.
- **Identity: 70/148 packages NAME-GRADE.** XPR2 directory
  fingerprints + assembly-graph keys assign proven entry names
  to 70 packages (chrone pkg23–29; chrtwo pkg46–67; chrthree
  pkg09–49); 78 stay honestly unassigned (re-authored regions).
  Corrections: phase-8's chrone-pkg29 "non-character accessory"
  is REFUTED (it is tin02); the cord-loop family is Zack
  (zac00/01/02/04); the armored 7-package group is spa00–06; the
  cat-ear group is kor02/03/05/06/07. Kokoro (pkg02), the
  katana-ninja group (pkg06–09), and pkg10 tentatives are
  UNRESOLVED by filename evidence — stated plainly in
  `phase15/ID-CORRECTIONS.md` + `phase15/PACKAGE-NAME-MAP.md`.
- **.mot streams: CENSUSED + RELEASED.** All 197 mot.afs entries
  extracted from the verified ISO, per-file sha256 manifest in
  git (`phase15/mot-entries-manifest.json`), released as
  `doa4-mot-20261022`. Fighter .mot grammar is evidenced to the
  record layer: offset table A (1000/1004/400 entries by class),
  a 44-entry record descriptor before each record, packed
  (non-f32) payload encoding. Cross-reference PROVES the .bin
  w21 clip table and the .mot record table are different index
  spaces (1024/584 vs 1000/376 for zack) — no slot mapping
  exists to claim. First clip NOT assembled; the residual is
  the packed-encoding expansion grammar. Detail:
  `phase15/MOT-CENSUS.md`.
- **XEX consumer: HUNTED (one bounded pass).** The real
  default.xex's .mot registry is a 196-record × 0x6C table
  (name char* at +0x18); the loader opens the .mot by runtime
  index → record → name (mechanism PROVEN). The 0x22xx token
  namespace is consumed on RUNTIME records (type byte +0x37,
  u16 id +0x30) at 15 evidenced dispatch/classifier sites; the
  bulk of the grammar is table-driven, so per-opcode w21
  semantics remain unproven — exact negative + named next step
  (trace the loader-side expansion from VA 0x823FA430) in
  `phase15/XEX-HUNT.md`.
- **Gates after phase 15:** G1 decrypt CLOSED (phase 14); G2
  extract-account CLOSED for chr/mot/cmn (this audit); G3
  format decode — packages named 70/148, .mot at record layer;
  G4 movesets-anim OPEN (expansion grammar is the blocker);
  G5 tooling — 13 phase-15 tools in `phase15/tools/`; G6
  in-game wiring UNCHANGED (no new wiring this phase).

## Phase 16 (2026-10-22, PR #697) — .mot grammar + w21 trace + containment completion

- **.mot grammar: RECORD LAYER PROVEN, payload residual named.**
  The phase-15 record framing is corrected and unified
  (`phase16/MOT-GRAMMAR.md`): a record = 44 sub-blocks FOLLOWED
  BY a 44-entry descriptor of u32 BE ABSOLUTE sub-block offsets
  in channel order; table A (fighter files) and the t_* (id,
  offset) index both point at DESCRIPTOR START. The fighter
  default record's span is the per-fighter shared front block.
  Tiling is exact everywhere: zack 376 records, m_zack 26,
  c_zack 2, all 124 t_* files = 530 records / 23,320
  sub-blocks. Cross-class proof: c_zack@32192 is byte-identical
  to zack@1151992 (44/44 channels); m_zack's records are
  disjoint longer motions (non-constant per-channel size
  ratios), so no different-encoding same-motion pair exists in
  the triple. Payload: an item cadence is evidenced (51.65%
  exact tile under the best simple tag rule) but the tag→length
  rule is FALSIFIED as a pure function of the tag by
  constraint propagation — the per-item length rule is
  stateful/contextual; delta-stream decodings refuted against
  shuffled controls; an 8-byte constant-channel form is
  identified. First clip NOT assembled.
- **w21 expansion trace: runtime-record layer EVIDENCED,
  file-side writer is the exact frontier** (`phase16/W21-TRACE.md`).
  Archive-open layer: open helper VA 0x8238ED10 (27 bl sites);
  per-fighter loader cluster 0x823918E8–0x82391B2C (its
  +0x54/+0x70 loads read the loader STRUCT, not a .bin
  buffer). Record initializer VA 0x82406E48 (strides
  0x44/0x9C/0x34; the 0x34 record's fields incl. u32 id at
  +0x30); validator VA 0x824091F0 (field bands
  [0x15,0x1C]/[0x1D,0x24]/[0x25,0x2C], ids 0x10A–0x10C /
  0x139–0x147, returns class 1–7 — phase 15's 0x2C compare
  candidates are this validator's band edge, NEGATIVE as a
  descriptor walk); per-player token decode ~0x823F6D2C over
  0x9C records (token u16s at +0x00/+0x02); translator
  0x823F6FA0 packing +0x36/+0x37/+0x32/+0x44/+0x4F/+0x54/+0x55
  from the 0x9C and 0x250 record generations. Classifier
  0x82408290 has ZERO direct bl callers (indirect dispatch).
  The function that reads a .bin buffer's w21 table and writes
  the 0x9C records was NOT isolated (named next step:
  data-flow hunt from the 0x9C array base; a Ghidra cross-check
  is blocked by the reconstructed PE importing at base 0 —
  logged in the trace). No offline expander is claimed.
- **Containment: scatter-pass COMPLETE**
  (`phase16/CONTAINMENT-AUDIT-2.md`, map:
  `phase16/containment-map-2.json`). All 147 probe-grade
  rows from phase 15 resolved by exhaustive multi-resolution
  scatter (16 KiB → 256 B, byte-exact verified) against the
  digest-verified mirror streams and the whole-ISO-verified
  re-assembly (sha256 4423cd5c…04aa): 104
  piecewise_unresolved → scattered, 14 absent_windows →
  scattered, 29 absent_windows → absent_proven (all chrthree
  .cat), 6 chrthree .cat files fully_scattered at 100%.
  jan02.tpr's phase-15 absence is OVERTURNED:
  scattered_cross_volume (chrone 0.7285%, chrtwo 4.9039%,
  chrthree 0.7729%). Union coverage: chrtwo 51.1871% →
  52.0069%, chrthree 48.2684% → 50.6650%.
- **Gates after phase 16:** G1 decrypt CLOSED; G2
  extract-account CLOSED; G3 format decode — .mot record
  grammar proven (payload item-length rule open), containment
  at reconstruction grade for all 389 chr entries; G4
  movesets-anim OPEN — the blockers are now exactly two named
  items: (1) the stateful .mot per-item length rule, (2) the
  XEX file-side writer (.bin w21 table → 0x9C runtime
  records); G5 tooling — 14 phase-16 tools in
  `phase16/tools/`; G6 in-game wiring UNCHANGED.

## Phase 17 (2026-10-22, PR #737) — faithful Ghidra project + data-flow attack on the last two G4 items
- **Faithful Ghidra project: BUILT** (`phase17/GHIDRA-PROJECT.md`). Phase 16's base-0 import blocker root-caused: Ghidra's MZ loader claims `default_pe.bin` (x86:LE:16 Real Mode import, ram space ending 0x10FFEF). Forcing `-loader PeLoader -processor PowerPC:BE:32:default` + an image-base shift to the true XEX base 0x82000000 (pre-analysis) places every section at its true VA. The .pdata function table is parsed (15,054 functions, `phase17/tools/pdata_parse_p17.py`) and seeded (23,832 functions in the saved project). Project DB stored in release `doa4-ghidra-phase17-20261022` (tar sha256 376b56ebb6e866d1e7f7dc0b009d11ff267941d09dae1b2b66f5349ad0abcccf); rebuild script at `phase17/tools/build_ghidra_project_p17.sh`.
- **Registry xrefs: PROVEN.** The .mot registry table @ 0x82C69A70 is used by the proven loader code at instruction level (0x82391AD4 helper 0x8238AC90 index → ×0x6C → + 0x82C69A88 = &registry[idx].name → open helper 0x8238ED10); registry strings carry DATA xrefs from the registry fields themselves (janlee.mot string from 0x82C69A88; zack.bin string from the .bin registry at 0x82C6B38C). Target functions decompile at correct VAs (12 decompiles in `phase17/data/decompile/`); the token decode FUN_823F6CE8 decompile independently re-confirms phase 16's field-level read.
- **Item 2 (file-side writer): FRONTIER ADVANCED, not isolated** (`phase17/W21-TRACE-2.md`). The 0x9C arena bases are PROVEN from the initializer's constants (token records 0x83020188; 0x34-id records 0x830A7C20; 0x44 copy arrays 0x830A7DBC/0x830A7DC0; tables 0x83022D10/0x830A6B58/0x830A7AC0). Token decode reads records via pointer globals 0x83099E04/0x83099BA8 (only stores: the reset at 0x823F6170, both := 0x83099BB8); FUN_824000B0 is a proven runtime-side arena writer. Two static writer signatures were exhausted over the full .text sweep (61 lwz+0x54→indexed sites; 19 mulli-0x9C + sth+0/+2 functions — none derefs a .bin buffer). Exact missing link stated in the trace; no offline expander claimed.
- **Item 1 (.mot stateful length rule): RESIDUAL, classes exhausted** (`phase17/MOT-STATEFUL.md`). Stateful constraint propagation over the zack triple (17,688 sub-blocks) falsifies every word-aligned functional class tested: pure tag (17,601 dead), (tag, prev tag) (17,479), (tag, index mod 2/3/4) (17,601/16,102/17,602), (tag, first u16) (15,652), (tag, channel) (17,601). First-u16-as-count refuted; no interleaved control stream at u16/byte granularity. No expander, no curves, no clip — the rule's state is not in the sub-block bytes' local features. Dynamic closure spec'd in `phase17/XENIA-TRACE-SPEC.md` (one session closes both items: registry watchpoint + buffer dumps for item 1; 0x9C-arena write watchpoint W3 for item 2).
- **Gates after phase 17:** G1 CLOSED; G2 CLOSED; G3 unchanged (record layer + 70/148 named); **G4 OPEN — remainder is still the same two items, now with their static attack surface exhausted and a one-session dynamic spec for both**; G5 tooling — phase-17 tools in `phase17/tools/` (build script, 3 Ghidra scripts, pdata parser, mot parser, stateful propagator); G6 in-game wiring UNCHANGED.
