# Pantera (King T7) input → move → clip matrix — pass 1 (2026-11-10, MoneyManBusch / Grok)

Owner (t386u): Pantera first, 100% King T7, proven by real on-screen presses. This is pass 1:
the movement rows only, driven through the SAME per-frame path game.js runs
(`TekkenBuffer.noteDirection(stick, dt)` → new latch → `trySystemMotion(dir)` → `_tickState`)
at 60 fps in node (`test/tekken-dash-pantera.test.mjs`). **Node proof only — no touchscreen /
browser proof yet.** Not a claim of 100%.

Sources: King T7 motbin `kinmot.json` (the reverse-engineering repo, tkdata mothead json),
own-slot bank `game/assets/anim/t3/t7_king/` (real King T7 generic clips, 60 fps).

| Command | Stick per frame (60 fps) | Recognized | Exact clip | Result (node) | Pass |
|---|---|---|---|---|---|
| f,f (dash) | f×2, n×2, f×1 | `tekdash` dash (Kg_sDASHF) | t7_king `dash` (coyt_dash125) | +1.41 m over 30 f, then idle | ✅ |
| b,b (backdash) | b×2, n×2, b×1 | `tekdash` backdash (sDASH_00B) | t7_king `backdash` (coyt_newback) | −0.667 m over 30 f, no invuln, mirrored at facing −1 | ✅ |
| f (single tap) | f×1, n×30 | — | — | no dash, no travel | ✅ (negative) |
| f held | f×40 | — | — | no dash | ✅ (negative) |
| f,b | f×2, n×2, b×2 | — | — | no dash | ✅ (negative) |
| f,f airborne | — | — | — | refused | ✅ (negative) |
| f,f then 1 | dash, then button 1 | `f,F+1` Jaguar Hook | **`f,F+1` row: `UNMAPPED:t7-clip-pending`** (the `f,F+1~t7.king` row has `t7:king:king_48`) | attack fires from the dash | ⚠️ fires, **wrong row / no real clip** |

## Before this pass (main `fb21d043`)
f,f and b,b did **nothing** for Pantera: the latch only starts KOF `system` rows and
`pantera.json` has none. The same test on main fails 4/5 (only the negatives pass).

## Not yet sourced / not done (next passes)
- **KBD (backdash cancel).** `sDASH_00B`'s own cancel list has u/b → `Kg_wDASH_00B`, n (frames 1–29) → `sDASH_00BLp`, end at 30 → `sWALK_00B`. The crouch (d/b) cancel lives in the packed group-cancel table (needs decoding). Not invented.
- **f re-press at dash frame 12** → `Kg_sDASHF` again / `sRUN__00F` (run). Not wired.
- **Crouch dash `f,n,d,df`.** `pantera.json` has no `cd_entry`, so the buffer never latches CD.
- **Duplicate rows.** Plain vs `~t7.king` rows (e.g. `f,F+1`, `f,F+2` "Beast Elbow" vs "Rolling Elbow") — the resolver picks the plain unmapped row.
- **Sidestep clip choice, all 13 T7 generic banks.** They are baked forward = +x, lateral = z, but `t3anims.js` `lateralDx` reads x (≈ +0.005 for both sidesteps), so the right sidestep never finds a clip. The sign of z (is `sSTEP_01L` +z the character's left?) needs a rendered check before the fix.
- **Touchscreen proof** (real presses on the deployed build) — parent computerUse task.

## Clip provenance, every Pantera row (`tools/anim/pantera_clip_provenance.mjs` → `clip-provenance.tsv`)
Probe: the clip `Fighter._attackClipPlan` plays for each row, with King's T7 move pack loaded as at boot. Node proof; main `50ba753f`.

| Rows | Real King T7 clip | T3 King bank row | Bank generic (light / medium) |
|---|---:|---:|---:|
| 643 plain rows (what button presses resolve) | **41** | **521** | 53 / 28 |
| 72 throw-class plain rows (1+3, 2+4, …) | 0 | 65 | 7 / 0 |

**Root cause of "moves not playing King T7":**
- `game/assets/anim/t7/king/moves.pack.json` holds only **29** real King T7 clips, all single inputs (1, 2, 3, 4, d/f+1, …), and no throws.
- Strings, dash moves (f,F+1, f,f,F+3), stance moves and throws have no King T7 clip in the repo at all, so they fall to T3 King rows.
- This is a missing bake, not a wiring bug. It needs `tools/anim/t7_move_resolve.py` and `tools/anim/t7_move_bake.py` run over King's motbin (`kinmot.json`, the reverse-engineering repo) for every row.
- Bake tool gates: multi-hit moves are skipped (one clip, one hit) and 0x64 clips need T7_EXE.

## Pass 2 (2026-11-10): real King T7 string steps extracted and wired
- **Resolver v2.** `tools/anim/t7_move_resolve.py --strings` handles T7 string-step rows (`(1), 2` = the 2 of 1,2). It walks King's cancel graph from `Kg_sKAM00_` through the bracketed prefix steps, then requires the final move's damage and first active frame to equal the row's T7 frame data. Default (v1) output is byte-identical.
  - 24 string-step rows: **17 mapped**, 7 no-match (throw enders 2+4 / d+2+4, `(d/f+3), 4`, `(b+1), 4`, `(b+2), 1+2`). Details: `king-string-resolve.json`.
- **Bake.** `tools/anim/t7_move_bake.py`, unchanged, with the community path its docs name:
  - Koenji's TekkenMannequin_no_ik.blend (sha256 `ce817108…`, same as the committed skeleton's provenance);
  - Kiloutre's TekkenAnimHelper.py at `bebb3d8b` (sha256 `1b447b1f…`);
  - Blender 4.2.3;
  - T7_EXE = the game's own sampler (sha256 `7f2b6872…`).
  - A re-bake of `1~t7.king` reproduced the committed clip exactly before anything new was baked.
- **Pack** `game/assets/anim/t7/king/moves.pack.json`: 29 → **44 moves** (29 → 43 clips).
  - All 29 old moves and clips are byte-identical.
  - `d+3+4,4` / `d+3+4,4,4` (`sukg_ari2`) were rejected by the in-game plausibility gate ("does not start upright"). They are recorded in `skipped` and nothing is substituted.
- **Wiring.** `t7MoveClip` adds an exact string-input map (`t7NormString`). A played row with the identical string input plays that step's clip; motions (f,F+1), stance prefixes and single inputs never match.

| Plain rows (643) | Real King T7 | T3 King row | Generic light / medium |
|---|---:|---:|---:|
| Before (main `b391b820`) | 41 | 521 | 53 / 28 |
| After | **61** | 516 | 46 / 20 |

The 20 rows that changed (each now plays its exact motbin move; no row moved to a non-T7 clip):
- 1,2 / 1,2,1 / 2,1
- 1+2,1 / 1+2,3
- f+2,1 / f+2,d+1,2
- d/f+1,2 / d/f+2,1 / d/f+4,3 / d/f+4,3,4 / d/f+4,3,d+4, each spelled both `df+` and `d/f+`
- b+1,2 / b+2,1 / b+2,4

Test: `test/t7-king-strings.test.mjs`.

**Still not King T7 (next passes):**
- Motion inputs (f,F+*, f,f,*, qcf), stance moves (WS / FC / SS / BT / JGS), throws (own pair path, 0 T7), and chain-throw branches.
- 516 rows still on T3 King. Multi-hit single moves are still skipped by the bake gate (one clip, one hit).
- Touchscreen and rendered-model proof: not done (browser unavailable).
