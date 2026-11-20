# T7 mega-batch — research report (2026-10-24, one pass)

## Coverage achieved (file-grounded, scripted)
- **mot.bin decoded at move level:** 51 batch + Alisa/Bob/Lee (private main)
  + Raven/Chloe (prior work) = 56 fighters with move→clip maps, 0 bank
  anomalies. Total mot moves across WH-mapped fighters: ~90,000.
- **.mvl display parsed:** all 53 files → titles + LP1/RP2/LK3/RK4 presses
  (6,000+ titled displayables).
- **Unified index:** 38 WH fighters (see
  `docs/research/t7-unified-index-2026-10-24.json`): mot moves/cancels/
  banks + display titles + TheBigTuna frame data + input-matched join.
- **Join totals (frame rows):** 1,322 JOINED-BY-INPUT, 740 AMBIGUOUS,
  2,426 UNMATCHED of 4,488. Joined rows are hypotheses (input-matched),
  never presented as file-verified identity.
- **Live moveset patch (8 MOD fighters):** 1,411 T8 anim refs removed from
  playable moves (772 kept as UNMAPPED fallback, 631 quarantined in-file,
  4 string-referenced restored), 1,789 body damages synced to MOD,
  0 remaining T8 anims, 0 remaining numeric-single mismatches,
  0 string→chord violations, 0 newly-broken string hits.

## Per-fighter join snapshot (joined / ambiguous / unmatched)
Pantera 75/23+/42+ (see unified index for exact per-fighter counts;
qualifier-stripped and state-stripped joins are labeled on each row).

## Known blockers (not hidden, not worked around by guessing)
1. **0x8000-bank clip bytes:** keys are exact (bank + index into main
   character MOTA) but bytes live in pakchunk data / live game memory,
   not in tkdata. Move-level decode is complete; clip playback for
   0x8000 moves needs that data.
2. **Notation↔mot-move identity:** input matching + cancel-walk are
   partial (requirement/group-cancel semantics are not statically
   resolvable). Live extraction remains the true join.
3. **Fahkumram / Leroy:** no mot.bin, no TheBigTuna. wavu T7 movelists
   are the documented next source (fetch failed on a local tool error
   in this lane; needs a live-browser fetch).
4. **Alisa note:** asamot.json IS Alisa (2,464 moves) — earlier records
   saying "no Alisa mot.bin" were wrong; Cape Jones's base IS decoded.

## GPU notebook
`docs/research/kaggle-t7-batch-notebook.ipynb` — prepared Kaggle
(2x T4) notebook: fetch T3 bank rows.pack.json + reactions from the
public repo, probe schema, classify every clip in parallel
(hip-Y trajectory: rise+fall = jumping, level = standing, down =
crouching), and verify reaction/throw-receiver wiring. NOT executed in
this lane (no live browser); run it from the Kaggle notebook URL and
it prints a classification report for the animation lane.

## Files in this PR
- `game/assets/movesets/{pantera,burger,demonio,diablo,kinpo,phantom,scimitar,skull}.json`
  (patched: T8 purge + MOD damage sync + quarantine sections)
- `game/js/main.js`, `game/js/audio.js`, `game/index.html`
  (tap-for-audio removal + SETTINGS audio toggle)
- `test/mega-batch-t7.test.mjs` (repo verification test)
- `docs/decisions/2026-10-24-mega-batch-t7.md` (this decision log)
- `docs/research/t7-unified-index-2026-10-24.json` (full unified index)
- `docs/research/t7-move-clip-maps/*.csv` (8 patched fighters' maps;
  all 56 maps live in workspace `batch-motbin/maps/`)
- `docs/research/kaggle-t7-batch-notebook.ipynb` (GPU batch notebook)
