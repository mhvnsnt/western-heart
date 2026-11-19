# Pantera to 100% — live proof (2026-11-18)

Lane D (proof). Pantera vs Demonio, shrine stage, 960x720, headless Chromium
(Xvfb + Mesa/ANGLE) driving the game hand-stepped at 60 Hz, frames read from
the renderer's own canvas (Nov 3 method). Every frame below was own-eyes
checked by the lane agent; every log line is a per-frame sim record
(`video-pantera-log*.json`).

**Two main commits were proven, and they are NOT the same build.** Runs 4–10
prove `43d29bf` (Nov 17, pre-B/C). Runs 11–13 prove `df0e900` (Nov 19, after
Lane B PR #1750 and Lane C PR #1749 merged). Each verdict names its commit.
Nothing here proves unmerged work, and nothing here is a live-site capture
(see Deviations).

## Verdicts

| Item | Verdict | Commit | Evidence |
|---|---|---|---|
| KBD loop | **PROVEN** | 43d29bf | `frame-kbd-snap-crouch.png` — mid-hold state `crouch` all 3 cycles; x −1.18 → −1.57 → −1.95 |
| f,f dash | **PROVEN** (travel gap noted) | 43d29bf + df0e900 | `frame-003-dash-mid.png`, `frame-dash-df0e900-mid.png` — state `tekdash`, travels forward. Live travel 0.79 m / peak 0.89 m vs node-proven ~1.41 m — flag for Lane B |
| Run (enter) | **PROVEN** | 43d29bf + df0e900 | `frame-004-run-mid.png`, `frame-run-df0e900-mid.png` — state `tekrun` |
| Run attack f+4 | **PROVEN** (falls back to plain f+4) | 43d29bf | `frame-005-run-attack.png` — run+4 fires `f+4` "Rolling Sobat", 40.3 dmg. pantera.json has NO distinct WR+4 move (only WR.1+2) |
| WR.1+2 | **PROVEN FIRED** | df0e900 | run 12 log — attacks `['WR.1+2']`, 18.2 dmg. Lane B's WR fix works live. Note: the fighter walked (not `tekrun`) in that run's logged frames — the buffer's running latch and the fighter's run state disagreed that once; run 13 proves `tekrun` itself enters live on df0e900 |
| Kick string 3,2,2 | **PROVEN** | 43d29bf | `frame-011-kickstring-end.png` — fired `3,3,2,3,2,2` in order, 88.4 dmg (180 → 91.6). Owner's Nov 11 "kick strings aren't working" resolved for this string |
| Kick string d/f+4,3 (Lane B fix) | **PROVEN** | df0e900 | runs 11 + 12 logs — attacks `['d/f+4','d/f+4,3']`, 35.1 dmg (180 → 144.9) |
| 2+4 paired throw | **PROVEN** (first on-camera completion) | 43d29bf | `pantera-2plus4-throw-20261118.mp4` (2.2 s, 20 fps, 44 distinct frames) + `frame-008/009-throw24-*.png` + `frame-vid24-*.png`. Thrower attack/throwing/throwExec, victim idle/thrown/thrownExec/knockdown, 24.7 dmg (180 → 155.3). Closes the Nov 3 gap (2+4 never completed on camera then) |
| 1+3 paired throw | **PROVEN** | 43d29bf | run 4 log — completes, 24.7 dmg, same states as 2+4 |
| Grapple chain 1+3,1 | **PROVEN** | df0e900 | run 12 log + `frame-chain-13-1-link.png` — link `1+3,1` fires (clip `t3_king_grab`), total 52 dmg (180 → 128). Lane C's merged chain runtime works on screen |
| Grapple chain 2+4,1 | **PROVEN** | df0e900 | run 12 log + `frame-chain-24-1-link.png` — link `2+4,1` fires (clip `t3_king_grab`), total 52 dmg (180 → 128) |
| BT entry | **PROVEN on 43d29bf / UNPROVEN on df0e900** | see below | see BT section |
| BT attack (BT.1 / BT.4) | **FIRED, HIT UNPROVEN** | 43d29bf | log-proven (BT.1 40 frames clip `t3_king_row110`; BT.4 42 frames clip `t3_king_row216`). Both whiffed on spacing — see BT section. No usable mid-attack frame (camera blocker, see below) |
| Throw victim clip | **GAP (Lane C)** | 43d29bf | Victim plays NO clip in ANY throw state: 0 clips across 23 thrown + 61 thrownExec + 34 knockdown frames, for BOTH throws. The throw still reads (pair math inverts the victim mid-swing, `frame-009`), but his limbs hold a frozen pose |

## BT (back-turned) — the full story

- **Turn Around (`b+1+2,1+2`) never enters BT on either commit.** It fired
  both hits but WHIFFED at gaps 1.0 and 0.5 (p2 hp 180 → 180) and `_bt`
  stayed false. Code (`game/js/fighter.js` `_tickState`): `stanceAfter`
  applies at attack completion regardless of hit, so Turn Around SHOULD set
  `_bt` if its `stanceAfter` were `'BT'` — it is not (derivation or
  move-resolution gap). Flag for Lane B.
- **FC.1+2 Ultimate Tackle enters BT — on 43d29bf only.** Runs 6–10:
  crouch → FC.1+2 fires, `_bt=true`, p2 hp 180 → 164.1 (hit, 15.9 dmg).
  BT.1 and BT.4 then FIRED from BT (log + clips above) but WHIFFED: FC.1+2's
  knockback throws the opponent 4+ m away before `_bt` even turns true
  (gap 1.97 at hit → 3.63 by frame 60 → 4.37 when BT.4 fires; p2 ends at
  x=7.14, gap 7.53). Walking toward re-faces (clears `_bt`), so the gap
  cannot be closed while back-turned. The whiff is spacing, not a move
  defect.
- **FC.1+2 is UNREACHABLE by keyboard on df0e900 — Lane B regression.**
  Identical input, different result: held `d` + `1+2` resolves `d+1+2`
  (real T7 clip, 36.4 dmg) on df0e900 vs `FC.1+2` on 43d29bf; released `d`
  + `1+2` resolves `WS.1+2` ("Snap Uppercut"). Mechanism: `tryCrouch`
  flips crouch → idle + WS window (0.35 s) in the SAME `_update` before
  input consumption (`game/js/game.js` order), so a neutral-direction
  `1+2` always lands WS; holding `d`/`d/b`/`d/f` makes the
  direction-prefixed move win (`d+1+2`, `d/b+1+2`, `d/f+1+2` all exist).
  No FC-ending moves exist in pantera.json (0 `(FC)` rows) to enter
  crouch key-free. The Ultimate Tackle cannot be reached by its natural
  input on current main.
- **WR entry `t7.king_289` ("WR f, f, F", on_block −5 (BT)):** one attempt
  (run 13) flaked to walk (input flake, see below) — mechanism UNTESTED,
  not disproven.
- **BT.1/BT.4 play T3 clips, not their T7 anim_refs:** BT.1
  (`t7:king:king_152`) plays `t3_king_row110`; BT.4 (`t7:king:king_174`)
  plays `t3_king_row216`. Lane A note.
- **No usable BT mid-attack frame:** the shrine's central debris mound
  blocks the free camera once FC.1+2 knockback drifts the midpoint to
  x≈2 — four blocked grabs (front, back, top-down, high). The P1-framed
  grab works (see `frame-003-bt-4-p1cam-mid.png` in the workdir — the
  `d+1+2` hit, not a BT attack).

## Node tests

- On `43d29bf` (`node-tests-20261118.log`): dash 7/7, run 5/5, back-turned
  17 pass + 1 env skip, t3-throw 8/8, pantera-wiring 5/5 — **37 pass,
  1 env skip, 0 fail**.
- On `df0e900` (`node-tests-df0e900.log`): dash 7/7, run 5/5, back-turned
  17 pass + 1 env skip, t3-throw 8/8, wiring 5/5, lane-b 6/6,
  t7-king-strings 4/4, throw-chain **8/9** — **60 pass, 1 real fail,
  1 env skip**. The fail is real: `test/throw-chain.test.mjs` "break
  inside the window" expects the original thrower to end `knockdown`,
  actual `idle` — Lane C reported 9/9 on its branch, so the B+C merge
  broke the escape-break knockdown. Flag for Lane C.

## Deviations (read before judging the verdicts)

1. **Local serve of main, not the live site.** Headless Chromium in this
   environment cannot reach ANY https site (`net::ERR_TUNNEL_CONNECTION_FAILED`
   for all hosts, including the egress proxy) — live-site capture is
   impossible from here. The build served locally IS main (sparse clone at
   the named commit). The live build was verified byte-identical to main
   `43d29bf` (`game/js/fighter.js` md5 `07ad998aad84f8150cb8354ed0412aa0`,
   291,328 B; `index.html` md5 `a63ea59c2781551a4816cd2959170f76`) on BOTH
   `https://western-heart.pages.dev` and `https://mhvnsnt.github.io/western-heart/`
   at that time. The live site was NOT re-verified after the merge to
   `df0e900` — see Parent-browser requirement.
2. **Opponent is Demonio, not Zen.** Zen's model is NOT shell-bundled:
   `resolveAssetCandidates` tries the remote Worker first on a non-full-site
   host, headless Chromium cannot reach it, the 45 s stall abort fires
   before the local candidate is tried, and fight-load recovery reloads
   forever. Demonio is the repo's play-verify pair with Pantera and IS
   shell-bundled.
3. **KBD cancel needs a real-time hold.** `input.js` `_udPress` starts a
   200 ms REAL-time setTimeout before `inp.down` becomes true; hand-stepped
   sim frames execute in ~ms of wall time, so a sim-only hold can never
   trip it (runs 4–5 "failed" KBD for this harness reason, not a game
   bug). Runs 6+ hold `d/b` 300 ms of real time before stepping.
   Related: the f,f double-tap is also real-time-sensitive and flakes
   under VM load in later phases (run 12 WR phase + run 13 B5 walked
   instead of dashing; the dash/run themselves pass cleanly when the
   input lands). Harness note, not a game bug — node dash is 7/7.
4. **Dash travel gap (live vs node).** Live f,f dash travels 0.79 m /
   peak 0.89 m vs node-proven ~1.41 m at frame 30; the x curve rises to
   +0.09 at frame 18 then drifts BACK to −0.01. Unprobed mechanism
   (retarget-scale hypothesis: live retarget may scale root motion; node
   skips retarget when skeleton.json is absent). Flag for Lane B.

## Parent-browser requirement

Headless capture cannot reach the live site from this VM. The parent
browser should confirm on `https://western-heart.pages.dev/game/`:
1. The `df0e900` build is live (`game/js/fighter.js` 297,581 B).
2. A BT attack LANDING — vs a stationary/cornered opponent, or after
   Turn Around / FC.1+2 is fixed (the live path to a BT hit is blocked
   on spacing + the FC.1+2 regression above).
3. The throw victim-clip gap (victim frozen pose mid-throw) on the live
   site.
4. The dash travel gap (live 0.79 m vs node 1.41 m).

## Files

- `README.md` — this file.
- `video-pantera-log.json` — run 4 per-phase log (43d29bf, all items).
- `video-pantera-log-run5b.json` — run 5b (43d29bf, video throw + dash
  re-measure). `video-pantera-log-run6.json` — run 6 (43d29bf, KBD snap +
  BT entry). `video-pantera-log-run11.json` — run 11 (df0e900).
  `video-pantera-log-run12.json` — run 12 (df0e900, chains + d/f+4,3 +
  WR.1+2). `video-pantera-log-run13.json` — run 13 (df0e900, dash/run +
  WR-BT attempt).
- `node-tests-20261118.log`, `node-tests-df0e900.log` — node results.
- `pantera-2plus4-throw-20261118.mp4` — 960x720 h264, 20 fps, 2.2 s,
  44 distinct frames, continuous 2+4 throw footage (run 5b).
- `frame-*.png` — own-eyes-verified stills (idle, KBD backdash, dash,
  run, run attack, 2+4 mid-throw ×2, kick-string end, video frames
  `frame-vid24-*.png`, KBD crouch snap, chain links ×2, dash/run on
  df0e900).
- `pantera-proof*.e2e.mjs` — capture scripts (Playwright + Xvfb/ANGLE,
  hand-stepped 60 Hz sim, canvas-read frames). `pantera-proof.e2e.mjs`
  = run 4, `pantera-proof2` = run 5b, `pantera-proof3` = run 6,
  `pantera-proof8` = run 11, `pantera-proof9` = run 12,
  `pantera-proof10` = run 13. (proof4–7 were BT-camera intermediates,
  superseded; not staged.)

## Method note (for the next proof lane)

- Serve the sparse checkout with a threaded HTTP server; the fight needs
  the base GLBs AND the attire models (`roster/*/attires/*/model*.glb`).
- String grace is 500 ms of REAL time — no mid-string grabs.
- Write the per-phase log after EVERY phase (a runtime restart killed
  run 5 and its log with it).
- Never `pkill -f` with a pattern matching your own command line.
