# SMUTBASE T7-bank capture — fix report (2026-11-03/04)

Worker: finishing worker for the SMUTBASE T7 BANK lane (mhvnsnt/western-heart),
taking over from the capture worker that died in a daemon restart.
No GLB model was edited. Nothing committed/pushed.

## Root cause of the original black frames (predecessor's finding, confirmed)

`serve2/game/js/scene.js` creates the renderer **without**
`preserveDrawingBuffer`, so the WebGL drawing buffer is cleared at
compositing. `playprobe2.py` grabbed `canvas.toDataURL()` synchronously from
`page.evaluate()` — outside `requestAnimationFrame`, on an already-composited
(and `g.paused = true`) game — and always read the cleared buffer
(7965 B, md5 `06c55af9e9d136262f49dd7eb66f8676`, brightness 0.0).
Fix pattern (fightshot2.py): identity gate (`p1.char.id` + `roundState ===
'fight'` + SkinnedMesh present), game **unpaused**, every grab inside
`requestAnimationFrame(() => canvas.toDataURL(...))`.

## Bugs in the predecessor's capture_fixed.py and the fixes applied

1. **Lock-retry infinite recursion** (`capture_fixed2.log`: one
   `LOCK retry maximum recursion depth exceeded` line before every frame):
   `safe_lock()` called **itself** instead of `pg.evaluate(LOCK_JS)`, so the
   HP/timer lock was never applied. → Bounded 3-try loop around
   `pg.evaluate(LOCK_JS)`. Zero LOCK-retry lines in all finishing runs.
2. **STATE_JS crash** (`capture_fixed.log` run 1:
   `Page.evaluate: SyntaxError: Unexpected end of input` at the first
   `pg.evaluate(STATE_JS)` after the idle segment). → State probe rewritten
   as an **IIFE expression string** (Playwright evaluates it directly instead
   of unwrapping a bare arrow-function string), null-guards `window.__game`,
   and also returns `f._atkPlan.kind` / `.why` (the deliverable requires
   plan name **and** kind per attack).
3. **Renderer crashes under memory pressure** (this VM: 7.9 GB RAM shared
   with a Blender render lane + other Chromium lanes; renderer died with
   "Target crashed" mid-run, and `pg.goto` itself crashed once, escaping the
   old script). → Capture now runs in **resumable sessions** (max 10):
   any Playwright death (grab/lock/state/wait/goto) restarts the browser,
   re-runs gate/setup/camera, and resumes the unfinished phase — idle count,
   hero-burst frames, and per-attack frame progress are all tracked
   incrementally. Pre-existing frames in the output dir are **archived**
   (`frames-<fid>-full-archive-<ts>/`), never deleted.
4. **Plan misattribution by lag**: `_atkPlan` read at +120 ms still showed
   the *previous* attack's plan (run 4 logged ATK 2 as `t7:1~...`). → The
   attack loop records the pre-fire plan and polls until the plan **changes**
   to the current attack's plan before grabbing.
5. **Hit-FX renderer kills**: firing at 1.1 m made strikes connect; sessions
   repeatedly died in the first attack grabs. → Attacks fire at **1.7 m**
   spacing (clean whiffs for most moves; the '4' kick still reaches and
   connects — see the impact spark in both attack stills). Plan/clip firing
   is identical, which is what a bank proof measures.
6. **Stage floor-break camera sink** (pond run 5): the `1+2` slam broke the
   shrine floor at frame f0050; the ground-following camera sank under the
   stage for the remaining 27 frames (dark floor tiles, no fighters, mean
   brightness 7.9 on f0070). → `SETUP_JS` stubs `g.stageBreaks.checkHit`
   (proof captures only; logged as `stageBreaksStubbed: true`). Run 6's
   `1+2` frames are 327–337 KB full-detail, fighters on camera throughout,
   sequence brightness range 36.5–118.2 with no dead frames.
7. **Attack-still selection**: a global max-diff-vs-idle pick chose the
   camera-displaced floor-break frame (diff 63.3, no fighter visible). →
   Candidates restricted to the **hero-burst frames** (one continuous swing,
   stable camera); winning frames were also **visually verified** (below).

## Stray-process handling (start of shift)

- PID 96535 `python3 capture_fixed.py pond` (predecessor run 2, orphaned
  PPID 1, LOCK-recursion bug, writing to the wrong dir `frames-pond/`, no
  Ryusan path) + its Chromium child 96662: positively identified as this
  lane's stale capture process and stopped, per the serial-run rule.
  Its 17 frames remain in `probe-fixed/frames-pond/`.
- Two other Chromium trees belonged to other lanes (probe_run on 8791;
  Pantera video lane) — **not touched**.
- The VM itself restarted twice during this shift (~23:56 and ~02:27 UTC),
  killing detached runs; the 8767 server was restarted from
  `serve2/` (`python3 -m http.server 8767`, verified: `/game/` 200,
  raven + luckychloe T7 packs 200) and is still running.

## Camera

`window.__game.arena` fight camera: in landscape it pins distance ≥ 10.5 m
and resets `camera.fov` to `arena._baseFov` each frame, so SETUP sets both
to **34** (fitDist ≈ 9.3 m < 10.5 m floor → pure FOV zoom, fighters ~1.3×
larger). Logged `{"zoom": true, "fov": 34}` in both final runs. Identity
gate untouched.

## Per-attack plans logged from f._atkPlan (settled reads)

Pond (Raven bank) — capture run 6 in-run logs 7/8; attack `1` read `None`
under lag in run 6, but was logged in run 5 (`capture-pond-full5.log`) and
in the probe verdict, identically:

| input | plan | kind | why |
|---|---|---|---|
| 1 | t7:1~t7.masterraven | t7 | real T7 Nj_lp002 (frsd_lp_DVD) |
| 2 | t7:2~t7.masterraven | t7 | real T7 Nj_rp00 (oznj_rp_DVD) |
| 3 | t7:3~t7.masterraven | t7 | real T7 Nj_lk00 (oznj_lk_DVD) |
| 4 | t7:4~t7.masterraven | t7 | real T7 Nj_rk00 (isnj_rk2_DVD) |
| 1+2 | t7:1+2~t7.masterraven | t7 | real T7 Nj_shinrp00 (frss_wp) |
| d/f+1 | t7:d/f+1~t7.masterraven | t7 | real T7 Nj_bodylp (oznj_hara_DVD) |
| d/f+2 | t7:d/f+2~t7.masterraven | t7 | real T7 Nj_t_srpFS (nanj_upsp_DVD) |
| u/f+4 | t7:u/f+4~t7.masterraven | t7 | real T7 Nj_jprk00F (sunj_jmawa_DVD) |

Ryusan (Lucky Chloe bank) — capture run in-run logs, 8/8, single session:

| input | plan | kind | why |
|---|---|---|---|
| 1 | t7:1 | t7 | real T7 Dc_lp00 (dcto_lp_DVD) |
| 2 | t7:2 | t7 | real T7 Dc_rp00 (dcss_rp_DVD) |
| 3 | t7:3 | t7 | real T7 Dc_lk00 (dcto_hilk_DVD) |
| 4 | t7:4 | t7 | real T7 Dc_rk00 (dcto_rk_DVD) |
| d/f+1 | t7:d/f+1 | t7 | real T7 Dc_t_slpF (dcto_uplp_short_DVD) |
| d+1 | t7:d+1 | t7 | real T7 Dc_t_slp00 (dcss_sylp_DVD) |
| u/f+4 | t7:u/f+4 | t7 | real T7 Dc_jprk00F (dcss_jrk_DVD) |
| f+2 | t7:f+2 | t7 | real T7 Dc_rp00F (dcto_6rp_DVD) |

Every attack: 7 frames grabbed, `tryAttack` returned `ok: true`,
state `attack`. Hero bursts ('4'): pond `t7:4~t7.masterraven`,
ryusan `t7:4` — both kind `t7`.

> Note: a fast `plan_probe.py` experiment was discarded as FLAWED
> (`probe-fixed/plan-probe-pond-FLAWED.json`): polling every 250 ms and
> breaking on the *first* plan change catches the transitional generic plan
> before the T7 binding settles. The capture runs' settled reads above,
> concordant with the predecessor's probe verdicts, are authoritative.

## Verification numbers (verify_proof.py → verify-proof-20261103.json)

Old black reference: 7,965 B, md5 06c55af9e9d136262f49dd7eb66f8676,
brightness 0.0. All stills exist in BOTH `probe-fixed/` and
`~/workspace/your_files/smutbase-banks-proof/` with identical md5s.

### Pond — frames: probe-fixed/frames-pond-full/ (77 frames, 77 distinct md5)
- idle still `pond-visible-idle-20261103.png`: **291,950 B**,
  md5 `8f041b71e31dcd9e522a1007974d765e`, mean brightness **43.005**
- attack still `pond-visible-attack-20261103.png` (source frame f0018,
  hero burst): **310,818 B**, md5 `fec811dd324bd3156f5219ffd4dac8f6`,
  mean brightness **51.734** — visually verified: Pond's kick fully
  extended into Pantera with impact glow; idle still shows Pond in T7
  stance vs Pantera on the shrine stage.
- idle md5 ≠ attack md5: **true**. Sequence brightness min/max: 36.480 / 118.167.
- video: `~/workspace/your_files/smutbase-banks-proof/pond-t7-bank-proof-only-20261103.mp4`
  (**BANK-PROOF-ONLY** — her model fix is a separate job), **641,600 B**,
  ffprobe: h264, 640×480, 77 frames, **7.7 s** @ 10 fps.
  Frames extracted from the mp4 itself: brightness **39.669** and **116.950**
  (u/f+4 energy-burst frame) — non-black, plays.

### Ryusan — frames: probe-fixed/frames-ryusan-full/ (77 frames, 77 distinct md5)
- idle still `ryusan-visible-idle-20261103.png`: **328,103 B**,
  md5 `e7eeda6cf2509290d5d9eda122e9a0a1`, mean brightness **59.233**
- attack still `ryusan-visible-attack-20261103.png` (source frame f0018,
  hero burst): **337,564 B**, md5 `8c80847a38fdfe7088ad2b7e84cbc004`,
  mean brightness **68.094** — visually verified: Ryusan's leg fully
  extended in a kick toward Pantera with impact glow; idle still shows her
  in fighting stance vs Pantera.
- idle md5 ≠ attack md5: **true**. Sequence brightness min/max: 38.608 / 70.191.
- video: `~/workspace/your_files/smutbase-banks-proof/ryusan-t7-bank-proof-20261103.mp4`,
  **658,340 B**, ffprobe: h264, 640×480, 77 frames, **7.7 s** @ 10 fps.
  Frames extracted from the mp4 itself: brightness **42.931** and **58.188**
  — non-black, plays.

## Files

- Fixed script: `capture_fixed.py` (this dir); per-fighter machine reports:
  `probe-fixed/capture-report-pond.json`, `probe-fixed/capture-report-ryusan.json`
- Run logs: `capture-pond-full5.log` (pond, all plans), `capture-pond-full6.log`
  (pond final frames), `capture-ryusan-full2.log` (ryusan final)
- Verification: `verify_proof.py`, `verify-proof-20261103.json`,
  `mp4-check-pond/`, `mp4-check-ryusan/` (frames extracted from the mp4s)
- Archived superseded runs (kept, not deleted):
  `probe-fixed/frames-pond-full-archive-1793754698/` (run 4, 52 frames),
  `probe-fixed/frames-pond-full-archive-1793756499/` (run 5, 77 frames —
  last 27 are the floor-break camera sink documented above),
  `probe-fixed/frames-pond-full-partial1/` (19 frames),
  `probe-fixed/frames-ryusan-full-archive-1793759348/` (26 frames, VM-restart kill)
