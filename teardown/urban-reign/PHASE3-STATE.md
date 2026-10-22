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
