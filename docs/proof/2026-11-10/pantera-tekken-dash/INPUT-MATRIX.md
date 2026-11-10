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

## Pass 3 (2026-11-10): King T7 dash and run moves (f,F+X / f,f,n,X / f,f,f+X)
- **Resolver v3.** `tools/anim/t7_move_resolve.py --strings --motions` walks King's own link tables in `kinmot.json`:
  - stance `Kg_sKAM00_` → cancel command **0x8001** (the forward double tap; the same 0x8001 the slot plan records for dash_fwd) → `Kg_sDASHF`;
  - then the dash's own `f+X` (F+X) or `n+X` cancel;
  - or for run moves, the dash's `f` cancel → `sRUN__00F`, then the run's X.
  - The final move must match the row's T7 damage and first active frame. Nothing is timed by us.
- **Result:** 11 motion rows, **8 mapped**, 3 no-match (`WR 4`, `WR+1+2`, and `f, f, n, 1+2`, which has no damage value). Details: `king-motion-resolve.json`.
- **Earlier lead corrected.** The dash's plain `1` → `Kg_jprk00F` is a requirement-gated generic cancel. Jaguar Hook `f, F+1` is the dash's `f+1` → `Kg_lygerlp00`.
- **Bake.** Same verified setup as pass 2 (unchanged tool; Koenji mannequin, Kiloutre helper, game sampler, Blender 4.2.3). It adds 7 moves / 7 clips; the pack goes from 44 to **51 moves**, with all 44 old moves and clips byte-identical. `(f, F+2), 1` (`Kg_fallerurari`) was rejected by the plausibility gate ("does not start upright") and recorded in `skipped`.

| Press (stick frames @60fps + button) | Resolved row | King T7 motbin move | Clip | Fwd travel |
|---|---|---|---|---|
| f×2 n×2 f×3 + 1 | `f,F+1` | Kg_lygerlp00 | kgss_66lp(DVD) rotsm#439 | 2.41 m |
| f×2 n×2 f×3 + 2 | `f,F+2` | Kg_p00 | sukg_falleru(DVD) rotsm#442 | 1.57 m |
| f×2 n×2 f×3 + 4 | `f,F+4` | Kg_tkr01 | mokg_tkr(DVD) rotsm#458 | 0.74 m |
| f×2 n×2 f×3 + 3+4 | `f,F+3+4` | Kg_dki10 | kin_dki10(DVD) rotsm#481 | 2.50 m |
| f×2 n×2 f×2 n×3 + 2 | `f,f,n,2` | Kg_p01 | k_p01(DVD) rotsm#447 | 0.89 m |
| f×2 n×2 f×2 n×2 f×2 + 3 | `f,f,f+3` | Kg_666lk (via sRUN__00F) | kgss_bomaknee(DVD) rotsm#997 | 3.36 m |
| f×2 n×2 f×2 n×2 f×2 + 3+4 | `f,f,f+3+4` | Kg_dki11 (via sRUN__00F) | kgss_s4_666wk motbin#118 | 3.50 m |

Node test: `test/t7-king-motions.test.mjs` (fails 9/10 on main, passes here).

| Plain rows (643) | Real King T7 | T3 King row | Generic light / medium |
|---|---:|---:|---:|
| Before pass 3 | 61 | 516 | 46 / 20 |
| After pass 3 | **68** | 509 | 46 / 20 |

**Not done:**
- WH's duplicate spellings `f,f,F+3` / `f,f,F+3+4` ("Strong Knee" / "Running Exploder") keep T3; only the exact `f,f,f+3` spelling is wired.
- `WR 4` / `WR+1+2` do not verify through `sRUN__00F`.
- Close/far `f,F+1+2` and `f,F+2+3`, and throws, are excluded.
- `f,n,d,D/F+X` (crouch dash): its entry is not the 0x8001 path. The stance's input-sequence commands (0x80b0–0x80b7 class) are undecoded, as is the KBD group-cancel table.
- No touchscreen or rendered-model proof.

## Pass 4 (2026-11-10): run-alias fix, KBD crouch cancel, King T7 table decode

**Decode tool:** `tools/anim/t7_table_dump.py` (read-only). Its output is `docs/proof/2026-11-10/pantera-tekken-dash/king-t7-tables.json`: all 259 input sequences, plus every link (own list and expanded groups) of `Kg_sDASHF`, `sDASH_00B`, `sDASH_00BLp`, `Kg_st2cr00B`, `Kg_st2cr00_`, `st2cr_00_Rv` and `sRUN__00F`, each with window, starting frame and requirement rows.

**Verified table structures:**
- **Input-sequence cancel command.** Index = cmd − 0x800D into `input_sequences` (stride 16: `input_window_frames`, `input_amount`, `unk_0x4`, `input_idx`). That points into `inputs` (`{direction, button}`), listed in time order; the last element carries press flag 0x40000000. Verified at 0x80b6 = `n,f,n,f,n,f+3` in 99 frames → `Kg_666lk`, the same move the pass-3 dash→`sRUN__00F`→3 path resolved independently.
- **Group cancels.** An own cancel with cmd 0x800B points at `group_cancels[move_id]`. Each row is 40 bytes `<QQQIIIHH` (cmd, req, ext, detection_start, detection_end, starting_frame, move_id, option), and the group ends at 0x800C.
- **Requirements.** `requirements[idx…]` rows are `{condition, param}`, terminated by condition 881. req 0 = (0,0), unconditional. Gated (condition meanings not decoded, so nothing is bypassed):

  | req | Row | Used by |
  |---|---|---|
  | 2130 | (35,1800) | stance b,b backdash |
  | 2132 | (36,3800) | dash n → run |
  | 1085 | (124,0) | f re-dash |
  | 539 | (254,1) | run input sequences |
  | 40 | (72,0) | — |

**Sourced links used or checked this pass:**

| From | Input (cmd) | → To | req | Window | Status |
|---|---|---|---|---|---|
| `sDASH_00B` backdash | d/b (group) | `Kg_st2cr00B` | 0 | [1,32767] | **wired: KBD crouch cancel** |
| `sDASH_00B` | d (group) | `Kg_st2cr00_` | 0 | [1,32767] | **wired** (any down) |
| `sDASH_00B` | d/f (group) | `st2cr_00F` | 0 | [1,32767] | **wired** (any down) |
| `sDASH_00B` | END 0x8000 @30 | `sWALK_00B` | 0 | — | wired (pass 1) |
| stance / `st2cr_00_Rv` / `cr2st_00_` | 0x8002 (b,b) | `sDASH_00B` | 2130 | [1,32767] | WH's existing b,b latch (same gate in both places) |
| `sDASH_00B` | 0x8002 | `sDASH_00B` | — | — | **no such link**, so none added (test asserts no restart) |
| `Kg_sDASHF` dash | f state @12 | `sRUN__00F` | 0 | [12,12] | **not wired**: run clip `Bco_run00(DVD)` anim 0x8043 (common.arc) not baked |
| `Kg_sDASHF` | f @12 | `Kg_sDASHF` (re-dash) | 1085 | [12,12] | gated, not wired |
| `Kg_sDASHF` | n [1,12] | `sRUN__00F` | 2132 | [1,12] | gated, not wired |
| stance / backdash / run | seq 0x80b0–0x80b7 `n,f,n,f,n,f+X` (99 f) | `Co_runchop`/`Kg_dki11`/`Thrmv_B0_02`/`Kg_lp00F`/`Kg_rp00F`/`Kg_666lk`/`Kg_runrk00` | 539 (throws 527–536) | [1,32767] | 666lk/dki11 already play via the run path; the rest are not mapped |

**Crouch dash.** The `f,n,d,d/f+X` sequences exist in the table (0x80e5–0x80eb, 0x80f5–0x80f6) but **no King T7 move references them**. King T7 has no crouch dash, so WH's `f,n,d,D/F+X` rows cannot be sourced from King T7 and stay as they are.

**Run alias fix (no blind case folding).** `t7NormMotion` canonicalizes only the third input of `f,f,F+X` to `f,f,f+X`, because that input is a direction-state test on the dash (f @12 → `sRUN__00F`), so held and tapped reach the same move. A held second input (`f,F+X`, the dash's own move), `F,f,f`, `f,F,f`, `f,f+X` and `b,b,B+X` stay null (tested).

| Press | Before | After |
|---|---|---|
| f×2 n×2 f×2 n×2 f×20 + 3 (`f,f,F+3` Strong Knee) | T3 row:54 | **t7 `Kg_666lk`** |
| f×2 n×2 f×2 n×2 f×20 + 3+4 (`f,f,F+3+4` Running Exploder) | T3 row:35 | **t7 `Kg_dki11`** |
| b,b → d/b (frame ≥1) | backdash ran its full 30 f | **crouch**; b,b again → new backdash (KBD loop) |

| Plain rows (643) | Real King T7 | T3 King row | Generic light / medium |
|---|---:|---:|---:|
| Before pass 4 | 68 | 509 | 46 / 20 |
| After pass 4 | **70** | 507 | 46 / 20 |

**Tests.** `test/t7-king-motions.test.mjs` and `test/tekken-dash-pantera.test.mjs`: 4 new positive tests fail on main and pass here; the negatives pass on both. Full suite failure set is identical to main (83 sparse-checkout-only).

**Exact next implementation (not done):**
1. **Run locomotion.** Bake the `sRUN__00F` clip `Bco_run00(DVD)` (anim_id 0x8043, common bank) and its transition move (id 52) as locomotion clips, not attacks. The bake's resolve path is damage/startup-gated, so add a locomotion entry without frame-data checks. Then in `tekdash` (dir f), at exactly frame 12 with stick f held (req 0), enter a `tekrun` state that plays that clip with its own root travel.
2. **Run attacks from a real run** (`WR`): map `sRUN__00F`'s own button links once the run state exists. Check WR 4 against `Kg_runrk00` / 0x80b7 and WR+1+2 against `Co_runchop` / 0x80b0 by damage and startup in `t7_move_resolve.py`. Not verified yet.
3. **Requirement conditions** 35/36/124/254/72 need the community condition table before any gated link (re-dash, n→run, input sequences) is wired.
4. **Throws** (`Thrmv_*`; 0 on T7 today) need paired-throw clip extraction. Not started.

## Pass 5 (2026-11-10): real run locomotion from King's T7 tables

**Sources** (restored to the persistent `/workspace/pantera-t7-sources`, all hash-verified: mothead blobs, exe sha256 `7f2b6872…2d60ed`, mannequin `ce817108…2321`, helper `1b447b1f…777c`).

**Bake:** `T7_EXE=<exe> python tools/anim/t7_generic_bank_bake.py --code kin --fighter pantera --character "King (Tekken 7)" --mothead <mothead> --mannequin <blend> --helper <helper> --blender <blender 4.2.3> --out-dir <scratch> --slots docs/proof/2026-11-10/pantera-tekken-dash/king-run-slots.json`. The game's own sampler handles the 0x64 clips; the skeleton is byte-identical to the existing `t7_king` bank. Only the three new files were added, and no existing clip changed.

| Run move (King T7) | Anim | Clip (bank#idx, fmt) | Frames | Root fwd | FK check |
|---|---|---|---:|---:|---:|
| `sRUN__00F` | Bco_run00 | common#67 0x64 → `t3_run_start.json` | 32 | +3.13 m | 0.000001 m |
| `sRUN__01F` / `sRUN__03F` | Bco_run01 | rotsm#0 0x64 → `t3_run_a.json` | 16 | +1.79 m | 0.000000 m |
| `sRUN__02F` | Bco_run02 | common#35 0x64 → `t3_run_b.json` | 16 | +1.79 m | 0.000000 m |

**Transitions (all requirement 0):**
- **Entry:** dash `Kg_sDASHF`, stick f **state** at frame [12,12] → `sRUN__00F`.
- **Chain** (each move's end 0x8000): 00F → 01F → 02F → 03F → 02F, looping.
- **Exits:** b → `sWALK_00B`; d / d/b / d/f → crouch transitions (group cancels, window [1,32767]).
- **No requirement-0 neutral stop.** WH ends the run at the current clip's end when f is released. This is a WH boundary, **not** a King timing.
- **Gated and not wired:** run stomp/tackle (`Co_fumuA00` 1093, `Co_runtac00` 1098, `Co_runspA00` 1104), f re-dash (1085), n → run (2132).

**Tests.** `test/tekken-run-pantera.test.mjs` tests locomotion only:
- entry at frame 12;
- the chain playing start → a → b;
- travel on the clips' own roots;
- negatives: released before 12, re-pressed after 12, a plain held f, and b,b;
- the exits;
- a button press from the run firing an attack (which move it resolves to is not asserted).

The 4 positive tests fail on main and pass here. The alias and KBD tests still pass. Run-attack recognition is tested separately in `test/t7-king-motions.test.mjs`. Node only; no touch or model proof.
