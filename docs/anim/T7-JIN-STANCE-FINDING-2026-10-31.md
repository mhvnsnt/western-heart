# T7 Jin Stance — Demonio Lane Finding (2026-10-31)

Demonio T7-treatment lane. Question: can Jin's real Tekken 7 stance be baked
onto Demonio's Attire 1 rig through the proven format-200 (0xC8) path — the
same path that landed King's stance on Pantera (PR #1300)?

**Answer: no — not today, and the reason is measured, not guessed. Jin's
named stance is a format-100 (0x64) clip, and the 0x64 joint frame is still
unsolved. No f200 clip in the jin bank is Jin's stance; the bank's f200 set
is the shared system set. Demonio therefore keeps his T3 jin-bank stance
(rated correct in `game/assets/anim/t7/STANCE-STATUS.json`) until the 0x64
frame lands. Nothing was wired, nothing was fabricated.**

## The evidence chain

1. **The named stance.** GRE jinmot.json (the real T7 motbin walk) proves
   Jin's stance move: `Jz_sKAM00_` → anim `kmjz_kamae(DVD)`, anim_id
   **16511 (0x407F)**. The anim_id − 0x4000 = §0 entry rule (the same rule
   the demonio clip-map uses) lands on **jinrotsm.arc §0 entry 127**.
2. **Entry 127 is format-100.** Slice header: format_word **100**, 4,884 B,
   sha256 `b67600411f2269e75caaddac9d3ba2137c20622be5a4312284c78b79c2ad38cf`
   — byte-identical to the GRE index entry. (King's stance, by the same
   walk: `Kg_sKAM00_` → `nakg_kg2kam`, anim_id 0x4084 → kin §0 entry 132,
   which IS format-200 — that is why King's bake worked and Jin's cannot
   take the same path.)
3. **The jin bank's format-200 set is the shared set.** Of jin's 88 f200
   clips, **86 are byte-identical (sha256) to clips in the kin bank, and
   the same 86 are in the bry bank** — the universal motion set every T7
   character bank carries. The 2 jin-unique f200 clips are entry 668
   (`jz_w01`, his win pose, motbin-named) and entry 468 (below).
4. **Control tests** (canonical `tools/anim/t7_c8_control_test.py`, Koenji
   TekkenMannequin, Kiloutre importer — the PR #1300 harness):
   - Entry 92 (a shared 90f clip): a clean standing guard loop — hip
     0.981–1.002 m, foot bottoms −0.004 m, loop seam 0.001 m. It is the
     SHARED system guard, not Jin's stance; wiring it as "Jin's stance"
     would be the cousin-sharing error STANCE-STATUS warns against.
   - Entry 468 (jin-unique bytes, 90f): same metrics (hip 0.981–1.002,
     seam 0.001) and its relative pose aligns to entry 92's within
     max 0.022 m / mean 0.003 m after a 90° facing rotation — the same
     shared guard motion with a different baked root placement, not a
     Jin-distinctive idle.
   - Entries 36 / 79 / 37 (60f / 80f): rejected — metres of vertical/root
     travel (falls and cinematics, not idles).
5. **Corroboration on main.** `game/js/t3anims.js` (T7_STANCES header)
   already records Jin among the banks whose stances "wait for the 0x64
   joint frame"; `docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md` and the
   F11 negative results stand — the 0x64 basis change is unsolved.

## What this unblocks / what waits

- Demonio's T7 ATTACK clips are already resolved and on main
  (`game/assets/anim/t7/clip-maps/demonio-clip-map.json`: 50 clips from
  `jin_clips.bin`, sha-verified against GRE release `t7-rotsm-clips-v1`).
  They wire through the general T7 loader when it lands (Claude lane,
  after PR #1377) — same `t7:` pick + `rootMotionT` conventions as the
  Burger clip-map wiring (PR #1378). No parallel mechanism was built here.
- The day the 0x64 joint frame lands, Jin's stance bake is a one-clip job:
  §0 entry 127, `kmjz_kamae(DVD)`, sha256 above.

Scratch evidence (lane-local): `_demonio-t7-20261031/step2/` — control
readbacks for entries 36/92/468 + the rejected batch metrics.
