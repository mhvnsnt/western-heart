# Urban Reign — Phase 3 State (Attempt 3)

Branch: `ur-phase3-textures` — base: `ur-phase2-motion` @ 739185d (PR #442 head).
Lane: TEARDOWN COMPLETION SWEEP, Phase 3, Attempt 3. Attempts 1–2 died to infra
failures before landing anything (attempt 1: clone setup; attempt 2: cloned and
extracted Job-3 source data, zero commits, no state file). This file + PR exist
FIRST per the first-minutes order, so a later attempt inherits a live PR.

Owner acceptance target (2026-10-20 ~20:57 CDT): DONE = UR fighters fighting
with REAL UR movesets + animations LIVE in the western-heart playable build,
verified in `game/`.

## Inherited state (coordinator-verified — do not re-derive)

- PR #429 OPEN: all 72 characters as skinned GLBs (bind matrices exact, max dev 3.7e-08).
- PR #434 OPEN: wired into `game/` (roster 130, 72/72 resolution PASS).
- PR #442 OPEN (this base): `.gyu` motion cracked (56,844 tracks, 0 failures;
  `ur_gyu.py`); 31/72 fighters NATIVE animation embedded; 41/72 proxy (their
  motions are in the 829 converted general-pool banks, unassigned); named
  movelists proxy for all 72 (motdat lists held, correlation unproven);
  textures NOT cracked.
- Read first (after this commit): `docs/urban-reign/UR-PHASE2-REPORT.md` on the
  base branch, esp. §6.
- Already extracted by attempt 2 (verify against the AFS before trusting):
  `~/workspace/ur-phase3-work/scratch/dvd000_afs_map.json` +
  `~/workspace/ur-phase3-work/scratch/motdat/` (motion_test / motion_wptest
  `.info` + `.bin` files — the Job 3 inputs).
- Sources: ISO on WH release `urban-reign-iso-v1`; SLUS_212.09 MD5
  0fa29bd55638f9ebe49feb494d4decd5; phase-1 worklog release
  `ur-sweep1-worklog-2026-10-21`. Older recon dirs `~/workspace/ur-texcrack/`,
  `~/workspace/ur-texture/`, `~/workspace/ur-decode/` — check for reusable
  texture work, verify before use.
- Residuals: char064 short one s16 group (1197/1260); 11 chars ≥1 unproven
  accessory; char001 accessory swings wide f47–70 (true node graph open;
  mapping is motion bone b → GLB node b).

## §6 texture route (from Phase-2 report §6)

PPK tail = ONE interleaved VIF/GIF stream (WH #306). Route: VIF/GIF stream
walker → virtual GS memory → deswizzle from stream-declared TEX0 (+ CLUT) → PNG.

## Jobs

- JOB 1 — TEXTURE CRACK: research + pull-in first (PS2 GS tooling: VIF/GIF
  parsers, GS deswizzle libraries, PCSX2 GS-dump tooling, Namco-PS2 texture
  research; wire best into `teardown/urban-reign/tools/` with license noted;
  hand-build only what provably doesn't exist — research notes + pull-ins
  committed BEFORE building). Implement §6 walker → virtual GS memory → TEX0
  deswizzle + CLUT → PNG. PROOF GATE: char001 textured GLB front render in
  REAL colors, viewed own-eyes (plausible colors, not noise; iterate if
  noise). On proof: batch all 72, wire into game GLBs or loader-supported
  sidecar path. Caveat: Blender's glTF importer mangles these GLBs' bone
  frames — render via three.js semantics / numpy baking.
- JOB 2 — GENERAL-POOL ASSIGNMENT (the 41): how does the GAME assign
  general-pool motions to fighters without pmot banks? Character tables,
  fncc, mission data, bank indexing — file or SLUS loader-code (Ghidra
  `~/workspace/tools/ghidra/`) evidence only. Assign only what's proven;
  proxy flags off per fighter as natives land; rest documented.
- JOB 3 — NAME MAPPING: scratch/motdat inputs + pmotID tables → correlate
  name lists (294 + 35) to bank indices on ordering/count evidence ONLY.
  Exact alignment = stated proof; partial = proven entries only. NO guessed names.
- JOB 4 — POLISH (after 1–3 land or are proven-blocked on record): char064
  s16 group; 11 accessories; node-graph hunt for the swing residual.

## Discipline

PER-CHARACTER ISOLATION. Additions-only; commit SPECIFIC paths (never
`git add -A`); push every turn; own-eyes on every render, unique filenames;
delete nothing except own verified-mirrored intermediates (log to
`~/workspace/agent-ops/disk-cleanup-log.md`).

## Progress log

- Attempt 3 start: branch + this state file + PR opened BEFORE any research,
  extraction, or coding. Reused clone at `~/workspace/ur-phase3-work/wh`
  (HEAD 739185d verified; sparse-checkout `D` lines are artifacts, not
  deletions — the working tree did not materialize under disk pressure, so
  all commits in this lane use exact-path pathspec commits).
- Attempt 6 start: pipeline check
- Attempt 6: pipeline check pushed (c3e0ea0, PR #464 head verified via API). char001 tail census LANDED: source verified vs AFS map (776960 B, MD5 c97d8315..., 3 local copies identical); tail = type-0x0002 chunk @0xE800, 717568 B. RESULT = proven negative for the Phase-2 S6 VIF/GIF framing: tail head = proven vertex records (3615 seps, 12/20/28-float grammar); strict VIF walks die on word 1 at 11/14 starts (rest = NOP runs in zero pads); framed TEX0/BITBLTBUF/TRX A+D writes = 0 (aligned A+D-shaped = 1533 PRIM + 2 RGBAQ only); unframed TEX0-value candidates 1403 loose / 99 strict = candidates only. Post-vertex 423168 B is a record/table/payload mosaic (25 u16 ramps, descriptor-like pointer rows at 0x56600+). Next tests named in census MD: DMA-tag walk, SLUS chunk-0x0002 consumer trace, then PSM decision. Census + tool committed.
- Attempt 6: DMA-tag chain probe folded into census tool + JSON: NEGATIVE (26,447 starts walked, max chain 5 steps, DMA-ID histogram near-uniform = random signature). No anchored DMA chain wraps the tail.
- Attempt 6 JOB3: motdat .info format CRACKED (u32 N + Nx u32 table k*60 + N x 60B records [idx][name32][date20][00010203]; size=4+64N exact on all 7 files; indices sequential 0..N-1, 0 bad records). All 10 scratch inputs size-verified vs AFS entries. Parsed 689 records (test Gnrl 294, test30 Gnrl 257, P1 35, P42 55, wptest Gnrl 44, P44 1, P55 3) -> motion-names/motdat-info-tables.json. Bank alignment NOT proven and naive theory DISPROVEN: no list count equals a bank count (342/373/114), no subset/subsequence relations between lists (668 unique names shared vocabulary). ZERO names assigned (per no-guessing rule). Next: decode motdat .bin records (P1 .bin held, 253728 B) + pmotID bridge (gyuindex re-verified: 37 pmot + 10 tmot pairs).
- Attempt 6 JOB2 (general-pool assignment): NOT STARTED this attempt beyond inherited evidence (gyuindex 37 pmot pairs re-verified under Job 3). JOB4 polish: not started (conditional on 1-3). Remaining Job-1 blocker is now precise: no in-file TEX0 source exists in char001 tail at any framing; the loader-code path (SLUS chunk-0x0002 consumer via Ghidra) or descriptor-record decode at post-vertex 0x56600+ is the named route.
- Attempt 6 (steer 2026-10-21 ~19:31 CDT): shipping target changed to native mobile executable (web/Three.js build retired; engine pick pending, Godot 4 frontrunner). Teardown deliverables unchanged. Job-1 end-step changed: land textured GLBs + inventory + WIRING-INVENTORY note; no web-build-specific polish. Priority unchanged: texture crack proof (char001 real colors, viewed) first. Route this attempt: post-vertex descriptor records (0x56600+) + loader-code evidence (recomp source + Ghidra project).
- Attempt 6 JOB1: **TEXTURE FORMAT CRACKED — PROOF GATE PASSED (own-eyes).** The census's A+D framing was wrong (addr byte at +8, not +12). The tail holds TWO descriptor tables: (1) upload table — 128 B DMA/GIF packets (BITBLTBUF/TRXPOS/TRXREG/TRXDIR + IMAGE + DMA REF), 28 unique uploads tiling a contiguous REF pool, all PSMCT32-shaped; (2) draw table — TEX1_1/TEX0_1 pairs, PSM 19/20 (PSMT8/PSMT4, INDEXED), TBP0↔image DBP, CBP↔CLUT DBP (16×16 = 256-entry CLUTs, 8×2 = 16-entry). REF addrs are relative to a per-file pool base (char001 0x57480, char002 0x57800), auto-discovered by CLUT-likeness slide. Decode = COMPOSED mapping: stream word → CT32-swizzled VRAM → sampled as PSMT8/PSMT4 → CLUT. Proof renders viewed: char001 hands (128×128 PSMT8), face (256×256 PSMT8, real colors), snakeskin + jacket + leather pants (PSMT4). Extractor `tools/ur_tex_extract.py` v2; outputs `textures/char001/` (10 decoded PNGs + inventory) and `textures/char002/` (same structure, own base; 8/10 textures byte-identical to char001 — costume-variant PPKs at source level, hands + tex08 differ). Full write-up: `textures/char001-census-addendum.md`. Open edges: 1 narrow-buffer PSMT4 pair undecoded; 3 TEX0 records unpaired (template copies). NEXT: batch all 72 PPKs, then textured GLBs (embed PNGs per owner TEXTURES-BAKED-IN rule) + WIRING-INVENTORY note.
- Attempt 9 JOB1a: **DECODE SETS 72/72.** Attempt-8's untracked char013–072 sets survived locally; each verified against the banked batch-1 pattern (inventory JSON parses, every listed PNG exists with header dims == inventory w/h, file count == PNGs+1, pool_base present; spot color-diversity = full 256-entry CLUTs) and committed in 3 batches. char010 was missing because attempt-8's batch script skipped its pre-existing EMPTY dir; decoded fresh (17 paired, base 0x4e980) and verified the same way.
- Attempt 9 JOB1b: **TEXTURED GLBs 72/72** in `teardown/urban-reign/textured-models/` (+ `MANIFEST.json`). Phase-1 GLBs recovered from PR #429 branch `ur-sweep1-char-decode` (`teardown/urban-reign/models/charNNN/`; char042's blob needed an explicit cat-file fetch). Builder `tools/ur_build_textured.py` (attempt-8's, banked): geometry/skinning UNTOUCHED — per-character verts/indices/joints verified IDENTICAL to phase-1 for all 72; embedded image count == banked PNG count for every character (733 images total). Renders (software rasterizer `tools/ur_bake_render.py`, skinning baked — bind pose is identity: TT-convention bake == stored positions byte-for-byte in extents): 6-character profile sample in `textured-models/renders/`, viewed own-eyes: char001 coherent stance with real texture shading; char010 shows readable "EAST CITY" shirt text (unambiguous real mapping); char020/035/050/072 are dark/patterned kits in action bind poses and read poorly in this orthographic rasterizer — recorded honestly, NOT claimed as clean visual proof; the quantitative image-count gate is the primary proof.
- Attempt 9 JOB3: .bin bridge structure cracked (see motion-names addendum): count parity 35/35, 1/1, 3/3 + monotonic offset tables on all held pairs. Name↔bank-index correlation STILL UNPROVEN; zero names assigned.
- Attempt 9 JOB2: no new assignments proven this attempt (window consumed by Job 1 landing + render verification). Native count unchanged: 31/72 native, 41 proxy unassigned. Route unchanged: SLUS_212.09 loader evidence (kg_human/kg_objdata) or file-table proof per fighter, per-character isolation clips required before any assignment counts.
- Attempt 9 JOB4: no closures this attempt. Open exactly as inherited: char064 missing s16 group (1197/1260 verts); 11 characters with ≥1 unproven accessory piece; node-graph hunt still open (standing documented assumption: motion bone b → GLB node b).
