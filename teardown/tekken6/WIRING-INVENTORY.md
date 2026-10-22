# Tekken 6 PSP — Wiring Inventory (round 3, 2026-10-20)

Per the owner acceptance target (2026-10-20 ~20:57 CDT) and the wiring
standard in PR #397 (gates G1–G4). This is the honest state of T6
content on its way into the playable western-heart build.

## What's decrypted / decoded

| Layer | State | Evidence |
|---|---|---|
| PSP ISO | Byte-exact on release `tekken6-psp-v1` | sha256 `b5e52660…` (round-2 scoreboard) |
| DATA401 sector cipher | SOLVED with a round-5 correction: the cipher runs ONE call per 1024-byte block. The round-3 bulk was decrypted per-2048, corrupting every odd 1024-byte block of every file — `bulk_decrypted.bin` on disk is therefore WRONG past each file's first kilobyte and must be regenerated with `tools/bulk_decrypt.py` before any further use | `tools/ROUND5-STATUS.md` F12/F13, `tools/bulk_decrypt.py` |
| GZIP containers (76) | **76/76 byte-exact (size + adler32)** — round 5: bodies are plain zlib once decryption is correct; there is no custom gzip and no encode context | `tools/decode_all76.py`, `tools/round5-evidence/r5_inventory_summary.json` |
| COM containers (18, gzip idx 58–75, entries 709–735) | **18/18 decoded byte-exact.** Each plaintext is a COM container (`00 00 00 01 "COM\0"` + a count-like word 7–16, 176 total across the set); per-character assignment + inner mesh extraction is the next step (G4) | `tools/decode_all76.py` inventory |
| NDPP archive (entry 87, ~81 MB, 2,546 embedded GZIP) | Landed on main via PR #187; the round-3 embedded scan (94/2,720) ran on the corrupted bulk — a re-scan on the corrected bulk is now unblocked and owed | round-3 session-2 scan |
| GMO -> GLB pipeline | Proven on a sample GMO (round 2, PR #388: converted, re-imported, front-rendered, viewed) | PR #388 |

## What's wired into the playable build

**Nothing yet — deliberately.** No T6-derived fighter, moveset, or
animation is live in `game/`, because the only T6 content that exists
in decoded form today is (a) the 20 small byte-exact containers
(mostly 1,088-byte records and two small files — no character meshes)
and (b) NDPP data whose main containers (idx0 class) do not fully
decode. Wiring placeholder or partial content into the build would
violate the acceptance target's terms (real fights between his
fighters with working movesets — not placeholders).

Existing wiring precedents this lane will follow once the decode
lands: PR #379 (No Mercy wiring), PR #382 (Tekken 3 wiring), PR #385
(full-wiring audit), PR #397 (wiring standard + gates).

## What's left before T6 content is playable

1. **The decode (gate G1/G2) — DONE (round 5, PR #446).** The
   PPSSPP live trace + RAM diff found it: no encode context exists —
   our own sector-cipher driver used the wrong call granularity
   (per-2048 instead of per-1024), corrupting odd blocks. 76/76
   adler-exact; the game's loader byte-matches plain zlib in live
   traces. The 18 COM containers are decoded and inventoried; what
   remains is per-character inventory (below), not decoding.
2. **COM inventory per character (gate G4 completion).** From decoded
   COM data only; the "40 meshes / 18 COM files" figure is a roster-
   size estimate, not a measured count.
3. **Batch GMO->GLB (gate G3)** via the proven pipeline, one directory
   per character (per-character isolation: skeleton/animations/
   add-ons stay per-character), Blender import + front renders for
   samples, viewed before any claim.
4. **In-build wiring:** T6-derived fighters/movesets/animations into
   `roster/`, `moveset-library/`, and `game/` following the
   Tekken 3 / No Mercy precedents, with in-build verification
   evidence before any "playable" claim.

## Per-file status (76 DATA401 GZIP containers)

Full per-file scoreboard with first-failure evidence:
`tools/round3-evidence/scoreboard_strict.txt`.

- Byte-exact (76/76, round 5): ALL gzip idx 0–75 (size + adler32),
  via `tools/decode_all76.py` on the correctly decrypted regions.
  The round-3 scoreboard (20 pass / 56 fail) was an artifact of the
  corrupted round-3 bulk, not of the containers.
- COM set (18): gzip idx 58–75 — all decoded; each holds one COM
  container (count-like word 7–16 after the COM header).

## Round-6 update (2026-10-21, PR #479)

Evidence: `tools/round6-evidence/` (JOB1–JOB4 docs + JSON).

| Layer | State after round 6 |
|---|---|
| Regenerated bulk | **Verified clean**: 50.0% of 1024B blocks differ from the round-3 bulk, ALL odd, 0 even; 76/76 decode from the bulk file itself; 40/40 fresh-decrypt spot check. Round-3 bulk must never be used again |
| Embedded containers (entry-87 slice) | **CORRECTED: 5,470 found, 5,470/5,470 adler-exact** (was "94/2,720" on corrupt bytes; the "2,546" figure is also superseded). Decoded census of these is the next lane |
| NDPP census | **798 → 1,565 occurrences** on clean bytes. `ndpp_bounding_volumes.glb` (1,103 boxes) is **incomplete** pending clean re-extraction; NDPP-FORMAT's "no vertex arrays" negative is **withdrawn** (it scanned corrupt bytes) |
| `tekken6.bms` (G5) | **MET via equivalence proof**: binary unreachable from this VM (official site HTML challenge / timeout, recorded); line-by-line transliteration byte-identical (sha256) to `decode_all76.py` on idx0 + idx74 |
| COM set (18) | **Reclassified: per-character MOVESETS, not models.** 18/18 characters named by in-file string at offset 624 (HIGH confidence): LAW, KING, NINA, Lin_Xiaoyu, JIN, Kuma, HEIHACHI, LEE, MARDUK, ROGER, Wang, Asuka, BAEK_DOO_SAN, RAVEN, ARMOR_KING, Dragunov, EDDY, ZAFINA. Meshes 0, textures 0, MOTA animation refs 108 (36 substantive chunks + 72 tail records). The +12 count word (sum 176) has no proven table referent yet — not an asset census |
| GMO→GLB (G3) | **0 new GLBs**: no proven T6 meshes exist yet (0 literal `GMO\0` in the whole clean bulk; COM holds no meshes). Pipeline (PR #388) still-valid, proven on samples, awaiting real T6 geometry |
| Wired into the build | Still nothing T6-derived — no proven meshes/moveset-decode to wire yet. The 18 movesets are decoded and inventoried, which is the input the moveset wiring will consume |

### Left before T6 PSP true 100%
1. Census + decode the 5,470 embedded containers (classes, per-character assignment).
2. Clean-bulk NDPP re-scan (vertex/index hunt redo) + re-extract bounding volumes (complete set).
3. Pin the COM count word's referent (EBOOT COM-loader RE or body-record census reproducing 7–16/file) and decode the moveset record format fully (move records, MOTA chunk bodies).
4. Find the character geometry wherever it lives (embedded containers / NDPP redo are the candidate spaces) → then GMO/NDPP→GLB with viewed front renders.
5. Wire decoded fighters/movesets into the build per the engine steer; verify in-build.
6. Optional confirmation: run real QuickBMS binary on the JOB 2 test file when a binary is reachable.

## Round-7 update (2026-10-21, PR #489)

Evidence: `tools/round7-evidence/` (JOB1/JOB2/JOB3 docs + JSON).

| Layer | State after round 7 |
|---|---|
| Container directory | **SOLVED**: every non-COM container is a chunk-directory file — (count, header size) + (chunk_size, cumulative_end) pairs tiling the file to EOF. Type A 13 slots/112 B, type B 6 slots/64 B |
| Package classes (top-76) | 12 character packages (NDPP body + `BONE` 8,032 + NDPP head + name chunk + `BONE` 1,664), 16 stage/object packages (624 B transform NDPP + BE-headed slot9 float payload 61–218 KB = stage geometry stream), 29 NTPP texture packages, 2 tiny stubs |
| Embedded census (entry-87 slice) | **DONE: 5,470 containers classified** — 3,702 A-model / 1,432 B-texture / 336 dir-other, sha256 + slot maps in `r7_census.json`. NDPP occurrences 1,565/1,565 sane sizes. Most A-packages are items/parts/stage objects, not whole characters; per-character assignment of embedded packages NOT yet proven (blocker B3) |
| NDPP interior | Descriptors (2×64 B) + count word (3120 in idx00) + interleaved normal stream with ~48 B block headers PROVEN on clean bytes. **Vertex position/index encoding NOT cracked** — no float3 position arrays exist in NDPP sections (cell-map evidence). Blocker B1: EBOOT model-loader RE (Ghidra), scoped in the JOB1/2 doc (NTPP ctor xref 0x892fdf0; BONE template VA 0x08bdaab0; NDPP dispatched by slot, no magic in EBOOT) |
| COM movesets (JOB 3) | **DECODED 18/18**: per-fighter JSONs in `teardown/tekken6/movesets/` — verbatim pointer tables, 7,341 byte-carried name records with record hex, all strings, MOTA verbatim. Binary command encoding + count-word referent still unproven (named, not hidden) |
| GLBs (G3) | `models/ndpp_bounding_volumes_r7.glb` SUPERSEDES the incomplete round-2 GLB: **1,222 sections / 11,663 boxes** on clean bytes (was 357/1,103), renders viewed + original-comparison documented. Images: 0 (bounding volumes have no textures). **Character-mesh GLBs: 0 — blocked on B1, deliberately not faked** |
| NTPP textures | Classified + counted, interior NOT decoded → no bakeable texture images yet. Pairing evidence recorded: DATA401 entry-order interleaving of A/B packages |
| Wired into the build | Moveset JSONs landed in the teardown tree as the wiring input (game-side registration minimal per the 2026-10-21 engine steer; GLB + JSON are the deliverables). No T6 fighter is playable yet: no proven character mesh exists |

### Left before T6 PSP true 100% (round-7 blockers)
- B1: NDPP vertex/index layout via EBOOT model-loader RE (Ghidra) — unblocks character GLBs, texture baking, per-character mesh inventory.
- B2: NTPP interior decode (GIDX/CLUT/pixel format) → texture images for baking + stage textures.
- B3: Per-character assignment of the 3,702 embedded A-packages (DATA401 index-order + name-chunk analysis).
- B4: COM binary command-record encoding + count-word referent (EBOOT COM-loader RE); MOTA chunk bodies.
- B5: Stage slot9 float-stream layout (BE control words → geometry) → stage GLBs.
- B6: BONE record stride + full skeleton decode (counts proven: 146 body / 22 head / 110 EBOOT template).

## Round-8 update (2026-10-21, PR pending)

Evidence: `tools/round8-evidence/` (JOB1 docs + viewed negative render).

| Layer | State after round 8 |
|---|---|
| NDPP interior (B1) | **Unit model + vertex stride PROVEN**: unit = 20 B header + strip table (`0x01000000+offset`, `0x04040000+count`, offsets from unit-header start) + `(0x13, 0x0b)` marker + packed stream; `offset delta == count * 12` exact on all sampled records → stride 12 B. Descriptor re-read proven (`[y_center, z_center, f2, bbox...]`); round-7 "count word 3120" is a size-like field, not a count. **12-byte packing NOT proven**: candidate A (u16@6 bbox-affine) rendered as a point cloud and VIEWED — refuted (bbox-wall pile-up, `round8-evidence/renders/r8_cloud_idx00_body_candA.png`). No character GLB shipped; the remaining step is the loader's unpack in the model-class vtable methods (asm-scoped in the verdict doc) |
| Ghidra (EBOOT) | Pass 1 done: NTPP ctor `FUN_0892fdf0` + sibling `FUN_0892fc40` decompiled; NTPP template dumped from ELF (fields `0x110, 0x40, 0x80, 0x100050, 0x84030100, 0x80020`); second NTPP site tied to a `GIDX` string table; BONE template xrefs are memcpy defaults in character/entity ctors, not parsers; no `NDPP` string in ELF (slot dispatch, re-confirmed by raw scan) |
| BONE skeletons (B6) | **Array structure CRACKED**: parallel arrays, offset table `[64, 64+4N, 64+16N, 64+28N, ...]` verified exactly for N=110/146/22. Array roles + post-`64+28N` sections + skeleton assembly remain |
| NTPP textures (B2) | Seeded with the ELF template dump + GIDX tie-in; interior not decoded; nothing baked |
| Stage slot-9 (B5) | Seeded: BE offset table head mapped (entries stepping 0x20; `0x15a60` = payload-64 on idx24); layout not decoded; no stage GLB |
| GLBs (G3) / movesets (G4) / wiring (G6) | G3: no new GLB (0 proven character meshes — unchanged, deliberately not faked). G4: unchanged from round 7 (18/18 JSONs). G6: no game-side registration (no proven mesh to wire; GLB + JSON remain the deliverables per engine steer) |

### Left before T6 PSP true 100% (round-8 blockers)
- B1': Read the 12-byte vertex unpack from the model-class vtable methods (`FUN_0886fe88`'s class, vtable `0x08b918b8`) / shared chunk walker — one asm function between the proven unit model and the first character GLB.
- B2: NTPP interior decode from the dumped template fields (`0x84030100` pixel-format candidate) + GIDX/CLUT.
- B3: Per-character assignment of the 3,702 embedded A-packages (unchanged).
- B4: COM binary command-record encoding + count-word referent (unchanged; Job 5 not attempted).
- B5: Stage slot-9 BE layout decode from the mapped offset-table head.
- B6': BONE array roles (consumers' asm) + skeleton assembly for the 12 character packages.

## Round-9 update (2026-10-21, PR pending)

Evidence: `tools/round9-evidence/JOB1-UNPACK-CRACKED.md` +
viewed render `tools/round9-evidence/renders/r9_idx00_slot0_front.png`.
Decoder: `tools/r9_ndpp_decode.py`.

| Layer | State after round 9 |
|---|---|
| NDPP interior (B1′) | **CRACKED**: units are embedded GE display lists — header cmds 0x14/0x10/**0x12 VTYPE**, strip table = VADDR (0x01) + PRIM (0x04; type 4 strip / 3 list) command pairs, terminator 0x13/0x0B. VTYPE arg gives the full vertex layout (weights u8 sum=128, UV u8, normal s8, position s16; stride 12/14/16 by weight count 1/2–3/4–5). Position scale: world = raw × descriptor_ymax/32767, proven on 4 sections / 2 files |
| GLBs (G3) | **First proven character meshes shipped + batch done**: `models/idx00_slot0_r9.glb` (idx00 slot-0 = head section; 3,217 verts / 1,897 tris; GLB bbox matches descriptor bbox ≤0.03 on all axes; FRONT render VIEWED — coherent human head) plus all 24 NDPP sections of the 12 character packages as `models/idxNN_slot{0,10}_r9.glb`; idx01 slot-0 FRONT render VIEWED (second coherent face); idx00 slot-10 = T-pose full body (scatter VIEWED) |
| BONE skeletons (B6′) | **Roles PROVEN + skeletons shipped**: parents / local translations / Euler rotations / scales / 32 B name table (`tools/round9-evidence/JOB2-BONE-ROLES.md`). `models/idx00_skeleton_r9.glb` (110 bones) + `models/idx04_skeleton_r9.glb` (146 bones); bind-check vs meshes PASSED (overlay VIEWED). Vertex weights exist in the streams (u8, sum 128) but the per-unit bone palette is unproven → no skinned GLBs yet, stated not faked |
| NTPP textures (B2) | Interior MAPPED byte-exact (`tools/round9-evidence/JOB3-JOB4-STATUS.md`): section header fields confirmed against the ELF template, +16 = first GIDX block size, two GIDX blocks per section with format words `0x10400612/0x10400610`. Pixel format NOT decoded — no PNGs, no bake, no invented pairings |
| Stage slot-9 (B5) | Head map RE-VERIFIED on idx24 (BE table, `0x15a60` = payload−64); layout not decoded; no stage GLB |
| Movesets (G4) / wiring (G6) | G4 unchanged (18/18 JSONs). G6: first proven mesh now exists to wire (GLB above); game-side registration still per engine steer (GLB + JSON deliverables) |

### Left before T6 PSP true 100% (round-9 blockers)
- B1′: DONE (above). Remaining NDPP polish: unit header words 3–4 semantics (per-unit transform/bone binding), skinning bone-index mapping for skinned GLBs.
- B2: NTPP interior decode from the dumped template fields + GIDX/CLUT.
- B3: Per-character assignment of the 3,702 embedded A-packages (unchanged).
- B4: COM binary command-record encoding (unchanged).
- B5: Stage slot-9 BE layout decode from the mapped offset-table head.
- B6′: BONE array roles + skeleton assembly (in progress).

## Round-10 update (2026-10-22, PR #520)

Evidence: `tools/round10-evidence/JOB1-PALETTE-VERDICT.md`,
`tools/round10-evidence/JOB2-JOB4-BATCH-CENSUS.md`,
`tools/round10-evidence/JOB3-JOB5-STATUS.md`,
`tools/round10-evidence/r10_inventory.json`,
`tools/round10-evidence/r10_b3_census.json`.
Tool: `tools/r10_batch.py`.

| Layer | State after round 10 |
|---|---|
| Unit header words 3–4 | **PROVEN = GE USCALE (0x48) / VSCALE (0x49)**, imm24 float texture scales — NOT a bone palette (the round-9 candidate is refuted with the GE opcode table + value proof). Per-unit prefix blocks proven = bbox records (span + vertex count + 8-corner normalized bbox); a section-tail offset directory indexes them |
| Bone palette / skinning | **Not in the file data**: RAM ground truth shows the engine builds single-bone GE fragments (12×0x2B + 0x0B, stride 52 B) per frame and CALLs them in palette order — the palette is a runtime/code product. NO skinned GLBs shipped (no guessed skinning). Remaining routes enumerated in the Job-1 evidence (draw-code xref / live GE capture / moveset part data) |
| GLBs (G3) | Full-section batch CONFIRMED COMPLETE: character packages hold exactly slots 0+10 NDPP (12/12 packages enumerated; the 24 r9 GLBs are the full set). NEW: 24 skeleton GLBs — `models/idx{nn}_skeleton_r10.glb` (body, 110; idx04 = 146) + `models/idx{nn}_bone_slot12_r10.glb` (head, 22) for all 12 packages; overlay renders VIEWED (idx05 clean; idx00 discrepancy vs round-9 spot values flagged in the Job-2 doc). **G3 stays PARTIAL**: meshes unskinned + untextured until the palette and NTPP land — not marked full |
| NTPP textures (B2) | GIDX word PROVEN = chunk tag (0x1040) + serial (idx06: 0x121/0x122/0x123 sequential) — not a format word. Slot-4 payload mapped as a directory of 0x460 B items ((0x10, offset, size) records). Pixel decode attempted on idx02 block 1 (16 CLUT variants, swizzled + linear) — all noise, VIEWED and rejected. No PNGs, no bake, no textured GLBs |
| Census (B3) | Slice A-packages classified by slot pattern: 28 full-character / 3,002 boned part / 436 rigid NDPP part / 236 stage-object (+1,432 B-texture + 336 dir-other). Top-76 accounting closed (12 + 16 + 28 NTPP + 2 stubs + 18 COM = 76). Per-character ASSIGNMENT still unproven — packages stay unattributed beyond pattern |
| Stage slot-9 (B5) | Layout one level deeper: BE directory of 0x20 B records + 40 × (0x8a0, offset) page pairs tiling idx24's payload to EOF + an embedded NTPP section at +0x1c0; payload is a BE float stream (95% float-sane). Page record format not yet decoded → no stage GLB |

## Round-11 update (2026-10-22, PR #536)

Evidence: `tools/round11-evidence/JOB1-PALETTE-XREF.md`,
`tools/round11-evidence/JOB2-IDX00-SKELETON-VERDICT.md`,
`tools/round11-evidence/JOB3-NTPP-CLASS-VERDICT.md`,
`tools/round11-evidence/JOB4-B3-ASSIGNMENT.md`,
`tools/round11-evidence/JOB5-B5-PAGES-VERDICT.md`,
`tools/round11-evidence/r11_b3_assignment.json`,
`tools/round11-evidence/r11_skeleton_correction.json`.
Tool: `tools/r11_skeleton_fix.py`.

| Layer | State after round 11 |
|---|---|
| Bone palette / skinning | **Fragment BUILDER PROVEN in the EBOOT**: function at 0x08ad161c emits (obj, out, index) → 12× 0x2B + 0x0B (52 B) from a 48 B-stride pose-matrix array at obj->[0] — byte-exact vs the RAM fragments; the RAM pool holds exactly 110 fragments (one full 110-bone set). The per-unit bone-index rule lives in the emitter's caller, which has no jal/data xref (jalr/vtable-called) and was NOT identified — palette mapping stays ambiguous between unit-ordinal and per-part-index sources, stated exactly in the Job-1 doc. Route 3 (COM/census) negative; route 2 (live GE capture) feasibility note landed for the coordinator. **No skinned GLBs (proof gate unmet — not guessed). G3 stays PARTIAL** |
| Skeletons (idx00 discrepancy CLOSED) | Round-9 spot values PROVEN correct: bind joints compose T·R; BONE scales do NOT propagate into descendant translations (r10's TRS walk put idx00 ASHI_R at y=−9.7 vs mesh floor −0.7; fingers 30% past mesh span — overlay VIEWED). 24 CORRECTED skeleton GLBs `models/idx{nn}_*_r11.glb` shipped: glTF walk reproduces the proven bind pose to ≤0.02 units on all 24 (r10-shipped walks err up to 597.3 units). Prefer r11 GLBs for skeleton work |
| NTPP textures (B2) | The NTPP class (vtable 0x08b9c568; RTTI name record at 0x08b9c5b0) is FULLY READ: it is a texture placement/animation object (defaults +0x98=1, +0x9c=110.0f) with NO pixel path — no byte loops, swizzle, CLUT, or GE texture commands in any of its six functions. No code-derived pixel parameters exist → the one-item code-derived decode cannot run; no blind sweep substituted, no textured GLBs. Slot-4 items are embedded NTPP sections (entropy 5.51). Residual target named: datatextureroot load path / render-layer GE upload |
| Census (B3) | **Per-character assignment LANDED (confidence-labeled)**: bulk-order contiguity scored strong (A/B interleave exact 28/28; 21/28 segments near-identical kits; 12 top-76 + 28 slice anchors = 40 full-char packages). 28 anchor-proven / 5,206 contiguity-inferred / 236 unassigned (stage-pattern) in `r11_b3_assignment.json`. Inferred assignments live in the census evidence ONLY — no per-character model dirs touched. No fighter names claimed for segments |
| Stage slot-9 (B5) | Round-10 "95% BE-float-sane" CORRECTED: pages are 80.5% zero bytes (the sane reading was a denormal artifact). All float-stream / byte-image / GE-list geometry hypotheses REJECTED with viewed evidence. Pages = sparse byte-record arrays, measured 16 B / 32 B record period. No stage GLB; residual = per-record field decode across the 16 B grid |

## Round-12 update (2026-10-22, PR #550)

Evidence: `tools/round12-evidence/JOB1-REGISTRY-CALLER-VERDICT.md`,
`tools/round12-evidence/JOB2-DATATEXTUREROOT-VERDICT.md`,
`tools/round12-evidence/JOB3-B5-CENSUS.md`,
`tools/round12-evidence/JOB4-B3-ANOMALIES.md`,
`tools/round12-evidence/r12_b3_anomalies.json`,
`tools/round12-evidence/r12_b5_fieldmap.json`.
Supersede note: `models/SKELETON-SUPERSEDE.md`.

| Layer | State after round 12 |
|---|---|
| **Skeleton supersede (standing)** | **r11 skeleton GLBs SUPERSEDE r9/r10 skeleton GLBs** (TRS defect; walks err up to 597.3 units). All future skeleton work uses `models/idx{nn}_*_r11.glb` only. Superseded files stay on disk, labeled in `models/SKELETON-SUPERSEDE.md` |
| Bone palette / skinning | **Registry trace CLOSED; static hunt TERMINAL — palette = CAPTURE-ONLY.** The 0x08bcfdxx zone holds switch jump tables, default-filled arrays, two indirection cells (0x08bcfdc8→thunk 0x08ad1614, 0x08bcfde8→thunk 0x08ad160c; consumers read: a list for-each @0x08ad1490 + container code @0x08ad08f8) and the identity template @0x08bcfdf0 (consumer: node-builder @~0x08ad1850). NO entry references the emitter @0x08ad161c (exhaustive negative: no data word / jal / j / branch / lui-addiu pair / lui+lw / relocation addend anywhere in the EBOOT — same for the builder @0x08ad1890). The caller is the INLINED builder @0x08ad1890 in the emitter's object class: **index rule PROVEN = sequential identity** (fragment i ↔ pose-matrix i at obj->[0]; fragment pointers at obj+0x18[i]; count = byte @obj+0x41f ≤256; 48 B 3×4 stride when byte @obj+0x41d==0, else 64 B 4×4 stride path @0x08ad1b30; standalone emitters @0x08ad161c/@0x08ad1724 are the two paths' leaf twins). The obj+0x418 composition is read (out+0x24/+0x28 = VFPU composition of obj->[1] matrix with obj+0x418+3 vector; out+0x2c copied raw). Remaining unknown is ONLY the game-side per-unit selection (model class, vtable 0x08b918b8) — observable solely in a live GE capture. **No skinned GLBs (not guessed). G3 stays PARTIAL** |
| NTPP textures (B2) | **`tcb_datatextureroot_t` FULLY READ — also NO pixel path; static hunt CLOSED at the named residual.** No standalone class vtable/type_info for the root exists in this ELF; only `tcb_pointer_t<T>` smart-pointer instantiations (vtables 0x08b94028 datatextureroot-ptr / 0x08b94078 datamemoryroot-ptr / 0x08b940c8 sibling), whose COMPLETE method set (span 0x08893e80–0x08894080, disassembled) is ≤5-instruction ctor/dtor/reset thunks into base ctor 0x885f3e0 / allocator 0x887c640 — no load method, no GE commands, no pixel parameters. NTPP template consumers are exactly 3 xrefs (init @0x0892fc40 + siblings — factory/init only). The 0x08adefxx GE-word functions are a state cache, not upload. Residual chain (one hop named, then stopped per brief): archive loader → tk sprite/texture renderer (unread). No code-derived decode possible; no textured GLBs; textures-baked-in gate upheld by not baking |
| Census (B3) anomalies | **ALL FOUR RESOLVED/BOUNDED.** (a) 5 double segments: direct decoded-byte scan finds ZERO BONE sections outside slot starts (no hidden anchor — byte-level negative); segments = two kits under one anchor sharing an 18–29-part byte-identical common core (modal controls: 0 internal duplicates) — bounded as a second costume/form-class kit; NOT split. (b) Stub segment 26 = a compact reduced kit (29 containers: 1 anchor + 12 B-texture + 8 rigid + 4 boned + 2 stage + 2 other) under the 129-bone anchor. (c) Closing anchors SOLVED: BONE sizes 9,440/9,696 = **129- and 132-bone body skeletons** (N read at BONE +16; size formula 64+4N+12N+12N+X+32N+12N+pad verified exact on N=22/110/129/132/146); heads standard 22. (d) Segment 27's 42 stage containers = **34 distinct slot signatures** — a multi-stage object pool at the slice tail, not one stage; stays unassigned |
| Stage slot-9 (B5) | **GRID CORRECTED + RECORD CLASS DECODED.** Pages sit on the 448 B-head grid (40×2,208 tiling exactly to EOF); the rounds 10/11 table extraction was shifted +2,096 B (its 40th entry is a 0 terminator) and the "embedded NTPP @+0x1c0" is page 0's header. **Every page IS an embedded NTPP section**: records 0–5 are a byte-identical NTPP section header across all 40 (fields +16=0x890, +24=0x800 — the "0x800 constant" is this header field, 40/40, not a record field; a second BE 0x800 sits at in-page offset 2,148 in 37/40). Head directory record 3 agrees (0x28 pages × 0x8a0). Field census over the 5,240 payload records landed (entropy 1.4–2.7 bits/position, zero-dominated small-enum alphabets). Hypothesis verdicts: (id,offset,size) index REJECTED; fixed-point placements REJECTED; texture-reference reading SUPERSEDED (pages are the sections themselves; payload = GIDX-block record data). One payload render VIEWED (44×48): sparse streaks, no coherent image — no pixel claim. No stage GLB. B5 geometry question closed: geometry is not in these pages |

## Round-13 update (2026-10-22, PR #558)

Evidence: `tools/round13-evidence/JOB1-TK-RENDERER-VERDICT.md`,
`tools/round13-evidence/JOB2-STAGE-VERDICT.md`,
`tools/round13-evidence/JOB3-PARTS-BATCH.md`,
`tools/round13-evidence/JOB4-COM-B4-VERDICT.md`,
`tools/round13-evidence/r13_stage_inventory.json`,
`tools/round13-evidence/r13_stage_slice_manifest.json`,
`tools/round13-evidence/r13_parts_manifest.json`,
`tools/round13-evidence/r13_com_census.json`,
Capstone reads in `tools/round13-evidence/dis/`.

| Layer | State after round 13 |
|---|---|
| NTPP textures (B2) | **tk renderer READ — pixel contract PROVEN at the descriptor, section→descriptor factory is the residual.** The upload builders (texture bind @0x08acd030; CLUT @0x08acce14/0x08acce50) read a shared image descriptor: +0x08 u16 format word (low nibble = GE TPSM enum, bit 7 = swizzled), +0x0a u16 width, +0x0c u16 height, +0x28 pixel pointer; CLUT is a sibling pointer (obj+8) whose format is the descriptor's own format word. NO function in the NTPP-class → datatextureroot → tk-builder chain populates that descriptor from NTPP section bytes, so per-section (format, w, h, pixels, CLUT) values are NOT code-derived and were not guessed. **No textured GLBs. G3 texture portion NOT crossed** — textures-baked-in gate upheld by not baking. Residual (one hop, stopped): the archive-loader-side descriptor factory; alternative = live GE capture |
| Part GLBs (G3 mesh portion) | **3,039 proven part GLBs shipped in-tree**: `models/parts/seg{NN}/bulk{NNNN}_slot{K}_r13.glb` — all NDPP sections of the 3,438 A-slice part packages (3,002 boned + 436 rigid), 2,005,929 verts / 1,211,043 tris, per-segment organization with contiguity-INFERRED labeling preserved, nothing merged into the 12 proven character packages. 405 failures reported per package (400 = VTYPE color-format 7 `0x*33d` family, stride measured 20/24 B, layout hypothesis tested and NOT validated — not guessed; 4 no-position VTYPE; 1 truncated). Decode deterministic (two runs sha256-identical). Gate render VIEWED: seg00 bulk0086 coherent torso costume part |
| Stage geometry (G6 stage portion) | **NOT crossed — structural verdict: stage packages carry no NDPP geometry.** All 16 top-76 stage packages + 236 slice stage-pattern twins hold exactly one NDPP section: slot 0 (624 B), the proven transform node (decoder fails it identically, spurious tail unit VTYPE 0x11d, no vertex payload). The single decodable stage-class section (slice bulk 3640 slot 0) shipped: `stages/slice/unassigned/bulk3640_slot0_r13.glb` — gate render VIEWED: one flat 2×2 quad (ground-plane card), not an arena. Stage packages = placement (slot 0/11) + texture containers (slots 7/9 NTPP) + BE directory (slot 8) |
| COM command encoding (B4) | **Tail closed; encoding NOT proven; primary hypothesis FALSIFIED.** The 4×20B tail records are 72 byte-identical empty MOTA stub headers — placeholders, not commands. All 31 pointer-table slots classified across 18 files; no slot satisfies word_a == name count or len/stride == name count for any file — no fixed-stride name-indexed command list exists in the pointed sections. Input notation demonstrably lives in the per-move name records as game-font PUA glyphs (U+E000–U+E02x). Count-word sum "176": matches nothing in-file (r ≈ −0.1); bounded as an external structural count, never a moveset-size measure. Residuals named: font glyph→button map; high-entropy slots 25/26/30 compression probes |


## Round-14 update (2026-10-22)

Evidence: `tools/round14-evidence/JOB1-DESCRIPTOR-FACTORY-VERDICT.md`,
`tools/round14-evidence/JOB2-VTYPE7-VERDICT.md`,
`tools/round14-evidence/JOB3-GLYPH-MAP.md`,
`tools/round14-evidence/r14_gate_bulk1934.png`,
Capstone reads in `tools/round14-evidence/dis/`, decoder
`tools/r14_ndpp_decode.py` (round-9 lineage), state
`ROUND14-STATE.md`.

| Layer | State after round 14 |
|---|---|
| NTPP textures (B2) | **Descriptor factory: EXHAUSTIVE NEGATIVE — G3 texture portion still NOT crossed.** The shared descriptor (desc vtable 0x08bcfba0, embedded texobj at +0x10) is populated ONLY by parameterized ctors 0x08acd9a0/0x08acda10/0x08acda80 (a2→format +8, a3→width +0xa, t0→height +0xc) from caller-supplied scalars forwarded through vtable-dispatched texture/sprite library code; no EBOOT code derives them from NTPP section bytes. Scope: handler range + descriptor class + caller chains read in full; sh-triple write scan 0 hits EBOOT-wide; 31 sw-cluster write candidates triaged by disassembly (none section-fed); dispatch is registry-table only (no magic compares); serialized-descriptor scan 0 hits across 59 NTPP sections (incl. idx24 slot 9's 40). No textured GLBs — header guessing refused again. Residual: NTPP image params arrive from outside the section-parser path (same evidence class as round 12's capture-only palette verdict: live GE capture or an asset-database source outside the EBOOT) |
| Part GLBs (G3 mesh portion) | **COMPLETE: 3,444 / 3,444 part sections decoded.** VTYPE color-format 7 cracked (RGBA8888, 4 B, 4-aligned, GE order; stride aligned to 4): validation over the 400 failed packages — 10,648/10,648 units stride-exact, weights 111,386/111,386 sum 128, normals 58,453/58,453 unit, bbox containment 112,157/112,160. All 405 round-13 failures recovered (incl. the 4 KeyError-'pos' + 1 truncated — proven false GE-signature matches / pos-less units; bulk3745's "VTYPE 0x476bfd" is a false match inside a vertex stream) as `models/parts/seg{NN}/bulk{NNNN}_slot0_r14.glb`: 355,725 verts / 196,773 tris, two runs sha256-identical, r13 parts manifest gained an additive `round14_recovery` section. Gate render VIEWED: bulk1934 torso + arms + shoulder armor part, coherent. Decoder parity: non-7 formats byte-identical to r9 |
| COM notation layer (B4) | **Glyph→input map PROVEN for 16 codepoints; notation layer decoded.** Font charmap in EBOOT (VA 0x08bae818) runs the PUA notation block consecutively E000–E07E; proven semantics: directions E000=d/b, E001=d, E002=d/f, E003=b, E004=f, E005=u/b, E007=u/f, E00C=repeat/hold mark (contextual); buttons E015=1, E016=2, E017=1+2, E018=3, E019=1+3, E01B=1+2+3, E01C=4, E01E=2+4, E020=3+4 — each fixed by exact decodes of known moves against cited Tekken 6 notation (Giant Swing motion + chain, Hunting Hawk, Tombstone Piledriver, Stonehead, Median Line Destruction, Kazama 5-Hit, Chicken Wing Face Lock). Shipped additively: `movesets/t6psp-*-moveset-v2.json` ×18 — 6,814 moves carry notation, 6,209 fully decoded, 605 partial (12 unproven codepoints kept as U+Exxx tokens, moves flagged). Originals byte-identical (7,341 moves field-checked). Compression probes on slots 25/26/30 ×18 files: **0/54** — not zlib/gzip/raw-deflate/LZ4/bzip2/xz/zstd/LZO, not the container cipher; packed-structure interpretation stands |
