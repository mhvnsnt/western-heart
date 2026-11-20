# SmutBase T7 banks: Pond (Raven) + Ryusan (Lucky Chloe) — 2026-11-03

Owner order (2026-11-03 ~16:30 CST): "all of this stuff that you said also
100% of all of this stuff" — both the T7 bank production and the TTT2
research at 100%. This handoff covers the T7 half: Pond and Ryusan had NO
move banks (final-three evidence, PR #1543: t3actions 0, no FIGHTER_BANK
entry, motbin playable_wiring "NONE"). They now have real Tekken 7 banks,
wired and play-proven.

## Route: OFFLINE — the Windows live-extraction route is NOT needed

The earlier recorded unblock ("TKMovesets2 live-memory extraction on
Windows") is superseded. The #1466/#1469 offline pipeline generalizes to
Raven (frv) and Lucky Chloe (dnc) from data already in hand:

1. Source data from the private GRE repo (mhvnsnt/game-reverse-engineering,
   teardown/tekken7-steam/tkdata/mothead/): frv.json, dnc.json,
   frvrotsm.arc, dncrotsm.arc, common.arc, frvmot.bin, dncmot.bin — all
   size-verified against the API listing.
2. `tools/anim/t7_move_resolve.py` maps moveset rows to motbin moves only
   when the stance cancel-graph input path AND exact T7 frame data
   (damage + first active frame) both match.
   - Pond/frv: 292 rows → 28 mapped exactly (22 rotsm + 5 motbin +
     1 common; all 0x64), 1 ambiguous (f+2), 5 no-match, 258
     not-single-input (strings/stance rows).
   - Ryusan/dnc: 205 rows → 31 mapped exactly (23 rotsm + 8 motbin; all
     0x64), 0 ambiguous, 6 no-match, 168 not-single-input.
3. 0x64 clips are converted by `tools/anim/t7_anim64_to_c8.py`, which
   samples the game's own sampler from the shipping exe
   (TekkenGame-Win64-Shipping.exe, sha256
   7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed, GRE
   release t7-shipping-exe-20261031) under Unicorn. Round-trip check on
   frvrotsm.arc: worst error 1.79e-07 (gate 1e-4). Run all bakes with a
   python that has unicorn+pefile (the bake shells out via sys.executable).
4. Clips bake through Blender 5.2.3 (xvfb-run -a env -u PYTHONPATH —
   bare -b segfaults on this VM) + Koenji TekkenMannequin_no_ik.blend +
   Kiloutre TekkenAnimHelper.py (sha256
   1b447b1fec432b34d59889e3ade5647f90014b6e6bbc221a439ebcc0ac32777c,
   byte-identical to documented commit bebb3d8) via
   `tools/anim/t7_move_bake.py` / `t7_c8_stance_bake.py`.

## What was built

Per owner doctrine (docs/anim/RAVEN-ANIM-GAP-20261023.md: never another
character's clips, no proxy banks), each fighter got a TRUE bank from her
own T7 motion:

- T7 packs `game/assets/anim/t7/raven/` + `t7/luckychloe/`
  (stance.json + moves.pack.json + skeleton.json):
  - Pond: stance Nj_sKAM00_ 160 frames; pack 27 moves / 26 clips.
    Skipped: d/f+3, gated OUT by the bake's own in-game plausibility gate
    (LeftToeBase 0.10 m below floor on frame 4, mannequin proportions —
    the same gate that held Bryan's d/f+3 in #1469). That row keeps its
    bank animation.
  - Ryusan: stance Dc_sKAM00_ 1,249 frames (her dance kamae); pack
    27 moves / 25 clips. Skipped (4): 1+2, u+3+4, f+3+4, b+1+2 — the
    bake's deliberate one-clip-one-hit rule for multi-hit rows; they keep
    their bank animation.
- Generic banks `game/assets/anim/t3/raven/` + `t3/luckychloe/`:
  20/20 FIGHT slots each, every clip the character's OWN motbin state
  move (stance, own 1/3/4 basics, stance-wired B2 throw as grab, guard,
  hit, launch, ko, walks, dashes, crouch, jumps, sidesteps), baked with
  the new repo tool `tools/anim/t7_generic_bank_bake.py` (equivalence
  proven: full raven re-bake = 21/21 files byte-identical to the
  development driver). Every clip FK self-check 0.000000 m.
  - Omitted (logged gap): intro (t3_stance.json) and win (t3_win_rp.json)
    SHOW slots — no body-clip candidate exists in either motbin table
    (only WIN-named entry is a facial animation). Loader tolerates the
    missing files.
- Wiring: `game/js/t3anims.js` (T3_BANKS + SOURCE_TO_BANK raven/
  luckychloe; T7_STANCES + T7_MOVES for pond/ryusan keyed to those banks),
  `game/js/fighter.js` (FIGHTER_BANK pond: 'raven', ryusan: 'luckychloe'),
  movesets: ryusan.json gained its `slots` identity map (every row's
  input equals its key — the map the game already derived at runtime);
  both movesets' playable_wiring text updated to the shipped state.
- Tests: `test/t7-moves-0x64.test.mjs` FIGHTERS rows for pond + ryusan —
  6/6 PASS each locally (pack format/FIGHT-only/FK exact, exact frame
  data per row, plausibility, stance-dir wiring, the real loader building
  clips for that fighter only, slot rows reaching T7 clips by input).

## Play-verification (identity-gated stepped probe)

Game boots into a zen-vs-pantera attract fight first; the probe gates on
p1.char.id before measuring (ungated runs have measured the wrong fighter
before and were retracted). Verdicts in
docs/proof/2026-11-03/smutbase-t7-banks/:

- **Pond: t3actions 20 (was 0); 11/13 sampled inputs fire.**
  9 real T7 clips: 1 (Nj_lp002), 2 (Nj_rp00), 3 (Nj_lk00), 4 (Nj_rk00),
  1+2 (Nj_shinrp00), d/f+1 (Nj_bodylp), d/f+2 (Nj_t_srpFS), u/f+4
  (Nj_jprk00F), b+1 (Nj_hizi00). 2 own-bank generics: d+1 (light),
  1+3 (grab). 2 NOFIRE: d/f+1,2 (string — needs a sequenced second press)
  and f,f+2 (dash-motion input) — probe-method limits, same class as the
  established control fighter's NOFIREs in the final-three lane.
- **Ryusan: t3actions 20 (was 0); 12/13 sampled inputs fire.**
  8 real T7 clips: 1 (Dc_lp00), 2 (Dc_rp00), 3 (Dc_lk00), 4 (Dc_rk00),
  d/f+1 (Dc_t_slpF), d+1 (Dc_t_slp00), u/f+4 (Dc_jprk00F), f+2
  (Dc_rp00F). 4 own-bank generics: 1+2, d/f+2, 1+3 (grab), 1,2.
  1 NOFIRE: d+3 — not a resolver-mapped row.
- Pond was re-probed AFTER her model fix (see
  docs/handoffs/POND-MODEL-FIX-2026-11-03.md) — bank still binds and fires
  on the fixed model (pond-verdict-fixedmodel.json in that proof folder).

## Video proof

docs/proof/2026-11-03/smutbase-t7-banks/ + ~/workspace/your_files/
smutbase-banks-proof/: fighting-pose + attack stills and short mp4s for
both fighters, captured in real fights from the served build.
Pond's video from this lane is labeled BANK-PROOF-ONLY: her final video
records the fixed model (model-fix PR) — see pond-final-20261103.mp4 in
the same folders.

Capture note for the next lane: the old probe screenshots were pure black
because the probe grabbed canvas.toDataURL on a PAUSED game. Working
pattern (capture_fixed.py in the lane scratch, report in the proof
folder): identity gate → game UNPAUSED → requestAnimationFrame grabs →
stub stageBreaks.checkHit (the 1+2 slam breaks the shrine floor and sinks
the camera) → fire attacks at whiff spacing (1.7 m).

## Remaining gaps (logged, with evidence above)

- Pond d/f+3 clip (plausibility gate), Ryusan 4 multi-hit clips
  (one-clip-one-hit rule), Pond f+2 (ambiguous mapping), the resolver
  no-match rows, intro/win SHOW slots (no body-clip candidate).
- Sequenced-press strings (e.g. d/f+1,2) are wired via step plans but the
  stepped probe cannot fire them with single notation presses; a
  sequenced-press probe is the follow-up check.

## Repeat for the next fighter

Resolve (cancel-graph + exact frame data) → convert 0x64 via the exe
sampler → stance + pack bake → generic bank bake with
tools/anim/t7_generic_bank_bake.py (slot basis: the character's own
motbin state names + the stance move's cancel wiring, e.g. stance dir
0x40→walk-fwd, 0x8001→dash-fwd; grab = stance-wired B2 throw) → wire
T3_BANKS/SOURCE_TO_BANK/T7_STANCES/T7_MOVES/FIGHTER_BANK → extend
test/t7-moves-0x64.test.mjs → identity-gated probe → capture with the
unpaused rAF pattern.
