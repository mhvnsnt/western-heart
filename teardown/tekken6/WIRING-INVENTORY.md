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
