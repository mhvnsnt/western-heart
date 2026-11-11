# Fight HUD clean-up and lag in hits / inputs (2026-11-11)

Owner, 2026-11-11:
- "Also u stated putting info and data on screen during matches that I didn't ask for and that Tekken games and code do
  not do it's ugly and distracting and obstruct the combat do research look at the Tekken code and stop adding stuff
  into the actual fights and combat that are only for debug and practice type shit like how much damage a hit is giving
  popping up big across the screen that's stupid AF to have in normal fights and even if it did happen in practice u
  should do it like Tekken not that ugly hand tooled bullshit but straight from the games source files of tekken"
- "U gotta get the game lesss laggy and slow it's running too slow"
- "No it's mostly in hits and inputs it's getting slow but whatever speeds you the game in general for my phone and internet"

## 1. Nothing over a normal fight that the fight does not show

Research from the game's own executable: `docs/research/2026-11-11-in-fight-hud.md`. The battle HUD movie
(SW_UI_HUD) has life gauges, round counters, timer, names, rank, rage and side gauges, and no hit counter, damage
number or hit-type text. Hit data is a separate practice movie, SW_UI_AttackData (practice message ids prc_573..581),
with exactly: Damage, Combo Damage, Hit Combo, Max Combo Damage, Total Damage + Clean Hit / Counter Hit / Wall Hit /
Punish lamps.

Removed from normal fights (versus, arcade, story, survival, ranked, online):
- the big gold "N HITS" counter on every landed hit, and the damage popup with CLEAN HIT / COUNTER / BLOCKED / TOTAL;
- the rejected-grab and rejected-Surge reason notes;
- the "BREAK THE THROW — TAP LP" prompt and the "ESCAPED!" text;
- subtitles for hit cries, KO cries, taunts and announcer calls (the ROUND / FIGHT / K.O. banners already show those;
  subtitles stay for intro lines, win quotes and story scenes);
- the 6 s control-hints bar at fight start; the frame-data option.

Practice mode (training and the fight lab) shows the practice panel built from that field list, one per side, at the
screen edge under the gauges, the changed value glowing; the throw-break prompt, control hints and frame-data option
are practice aids there.

Screenshots (pantera vs thor, hits landing, 960x540): `normal.png` (normal fight), `practice.png` (practice mode);
`overlays.json` lists every visible text overlay in each (tools/ui/fight_overlay_probe.mjs).

## 2. Lag in hits and inputs

Measured with tools/perf/sim_spike_probe.mjs (the real fight sim stepped at 60 fps on a simulated clock, rendering
taken out, P2's AI fighting, P1 pressing a move every 450 ms; 1800 frames) and tools/perf/break_compile_probe.mjs.

| what | before | after |
|---|---|---|
| CPU in three.js over the run (BVH hit verify baking skinned bodies after hits) | 5248 ms | 215 ms (`sim-spikes-before.json` vs `sim-spikes-verify-off.json`) |
| three-mesh-bvh CPU over the run | 430 ms | 0 |
| worst frame on a floor-break hit (sim only) | 29.7 ms: `stageBreaks.checkHit` 21.9 (`sim-spikes-attributed.json`) | shards still built at the hit (inside the 0.18 s break freeze); lights and materials no longer |
| shader programs compiled AT a floor break | +12 (31 -> 43), lights 15 -> 18 (`break-compile-old.json`) | 0 (46 -> 46, lights 18 from stage build; `break-compile-new.json`) |
| first press of a move (clip retarget + bind at the press) | 3-14 ms per first press, 23 ms worst (`sim-spikes-before.json` byKind) | bound ahead: `sim-spikes-prewarmed.json` |

Fixes:
- `game/js/hitdetect.js`: the BVH "verify" tuning instrument is opt-in (`?hitverify=1`). It ran after every landed hit
  of every fight, only to log sphere/BVH disagreements, and its first hit on each fighter baked the whole skinned body
  on the CPU and built a BVH.
- `game/js/stagebreaks.js`: everything a break shows is built and compiled with the stage (ember lights at intensity 0,
  hidden disc / wall chunks / glow, shard material through a hidden probe mesh, pooled burst particles). Adding lights
  at the hit changed the scene's light count, which made three.js recompile every lit shader in the scene.
- `game/js/fighter.js` `prewarmAttackClips` + `game/js/game.js` `_prewarmTick`: the first 120 neutral presses per
  fighter (shortest first) are retargeted and bound through the same `_attackClip` path in time-boxed slices after
  drawn frames (5 ms outside the fight, 1 ms during it), instead of at their first press.
- `game/js/main.js`: HUD writers (HP, meter, timer) look elements up once and write only changed values; they ran
  on every 120 Hz sim step and the timer's text node was replaced every step.
- `game/js/scene.js` + `game/js/menus.js`: GRAPHICS QUALITY now changes the composer's resolution too (the fight
  renders into the composer: LOW never reduced a phone's fill), and phone-width screens get dynamic resolution
  between the quality's bounds (frame time over 19 ms for 2 s steps down 15 %, 8 smooth seconds step up 10 %).

Phone-size static load before the change (`frame-budget-phone-before.json`, 412x915 at DPR 2): Megami is 516k
triangles in 26 skinned meshes with 469 bones (Pantera 48k / 1 / 22); 15 lights; bloom + PCF soft shadows. Software
WebGL here cannot give a phone's GPU numbers, so this PR does not claim a phone fps; the probes above measure what
moved off the hit and input frames.

Tests: `test/practice-attack-data.test.mjs`, `test/lag-hits-inputs.test.mjs`, plus the existing suites
(`test/hitbox.test.mjs`, `game/tests/stagerage.test.mjs`, `test/e2e/menu-touch.e2e.mjs` updated for the
no-announcer-subtitle rule).
