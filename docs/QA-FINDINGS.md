# Western Heart Lab — QA findings, 2026-10-14 (Grok Bot QA lane)

Build: `main` @ 1b312e6f (after #117). Harness: `lab/game/tests/qa_playtest.gd`. Proof: `docs/qa/2026-10-14/` (7 frames, `qa_playtest.mp4`, `qa_log.csv`).
P1 = Pantera (King T3 table), P2 = King dummy. 60 fps. Tekken refs are typical T5/T6/T7 public-wiki values (verify per character on wavu.wiki before tuning).

## Measured vs Tekken
| Check | Lab measured | Tekken reference | Verdict |
|---|---|---|---|
| Input delay | 0 f (press f1 → attack state f1) | ~0–1 f offline (+ display lag) | OK |
| Jab (light) startup | hit on f20 → **i19** | jab **i10** | too slow ×2 |
| Jab whiff total | 60 f (idle again f61) | ~27–30 f | far too long |
| Jab on hit / block | **+7 / 0** | +8 / +1 | close (block 1 f short) |
| Jab pushback on hit | 0.05 m | small | OK |
| Medium startup | hit f17 → i16 | 1,2 / d/f+1 i12–i13 | slow |
| Heavy ("launcher" stand-in) | hit f30 → i29, on block **−12** | d/f+2 launcher i15, −12/−13 block, launches | startup 2× slow; **no launch/juggle state** |
| Throw | i29, uses **heavy's row 230**, result is ordinary hitstun, HUD says "heavy" | i12, throw anim, 1/2 break window | wrong move + wrong outcome |
| Throw vs blocking opp | connects (unblockable) | connects | OK |
| Walk fwd / back | 1.70 / 1.30 m/s | ~similar, back slower | OK |
| Dash (f,f) | **none** — double-tap = 2 walk steps (0.11 m) | f,f dash ~0.8 m, b,b backdash | missing |
| 10-hit string (J every 4 f) | **1 hit**, other 9 presses dropped | 10-hit string chains on rhythm | missing |
| Input buffer | press during recovery dropped | ~ few-frame buffer + string windows | missing |
| Hitstun / hitstop | hitstop 6/9/12 fallback (rows have hit_freeze 0) | ~ 6–12 hitstop | OK-ish, data missing |
| KO | heavy on 10 hp → KO f30, round restarts | — | OK |
| Camera | side follow, z = 4.4 + 0.55·sep, lerp 0.12 | similar 2D-plane cam | OK; no sidestep axis |
| Crouch / sidestep / low-high | **none** | core | missing |

Timing source note: King T3 rows say `active_first` 18 for jab (row 35). Either the row mapping picks a non-jab row or T3 stream frames are 30 fps-ish counts. Worth checking `teardown/tekken3/movesets/moveset_king.json` row for 1 (King's jab is i10 in T3).

## Prioritized bug list (drafts — not yet filed as GitHub issues, awaiting owner OK)
1. **P1 — Grab is a copy of Heavy** (`summary.grab.t3_row == summary.heavy.t3_row == 230` in `lab/game/data/moves/king.json`; HUD shows "heavy"). Repro: `qa_playtest.gd` scenario `throw_vs_blocking`. Proof `08_throw_vs_blocking_f030.jpg`. Fix: map grab to King's real throw row, add a throw state (attacker+defender paired anim, no hitstun).
2. **P1 — Startup ~2× Tekken** (jab i19 vs i10, heavy i29 vs i15). Repro `jab_on_hit`. Proof `03_jab_on_hit_f020.jpg`. Check row mapping / frame-rate conversion in `move_table.gd` + `export_moves.py`.
3. **P1 — No strings / no input buffer**: 10 jab presses → 1 hit. Repro `ten_hit_string_mash_J_every4f`, `jab_buffered_during_recovery`. Proof `09_...f036.jpg`. Fix: buffer (~8 f) + string cancel windows from T3 `branches`.
4. **P1 — No dash / backdash** (f,f / b,b). Repro `dash_fwd_doubletap`.
5. **P2 — No launcher/juggle state**: heavy just causes hitstun. Repro `heavy_launcher_standin_on_hit`.
6. **P2 — King model broken visually**: head + Bannon mask float above torso, body parts gapped, feet detached (known KMD seam-vertex gap, README M1). Proof `03_jab_on_hit_f020.jpg`.
7. **P2 — Fighters interpenetrate on grab/medium step-in** (separation 0.6 m too small for Pantera's mane). Proof `08_...`.
8. **P2 — Stage panorama not visible**: background is flat colour + stray blue box top-left; T3 stage `l` not showing. Proof all frames.
9. **P3 — Whiff recovery too long** (jab 60 f total).
10. **P3 — Heavy −12 on block vs designed −8** (BLOCK_ADV lab rule off by hitstop/active remainder).
11. **P3 — Touch labels**: buttons read LP / MP / K / GRB but keyboard doc says light/medium/kick(heavy)/grab — "K" is heavy; inconsistent naming.
12. **P3 — Shutdown errors** `mesh_get_surface_count: Parameter "m" is null` ×3 on headless exit.
13. **Missing core**: crouch, sidestep, high/mid/low.
