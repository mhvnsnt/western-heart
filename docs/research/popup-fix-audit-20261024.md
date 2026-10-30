# POPUP FIX — FIGHT UI AUDIT + TEKKEN-EXACT DISPOSITIONS (2026-10-24)

Owner priority reset 2026-10-24 20:56 CDT (verbatim intent): "The joystick
works perfectly fine now. Um the words V shift, rage, time shift, uh TBD
stuff like that keeps popping up real big on the screen in the middle of
the fight, I keep telling you I don't like that, and to find out how um
Tekken does stuff like that so you can place that stuff better make that
the very next thing you do that gets pushed to the playable build so that
stops happening it's really annoying."

This restates the UI IMMERSION LAW (never big WALL BREAK / TIME BREAK style
text during fights). The failure: every mid-fight system trigger in
`game/js/` was routed through one shared renderer, `ui.banner()` in
`game/js/main.js`, which writes into `#round-banner` — styled in
`game/styles.css` as `position: fixed; inset: 0`, centered,
`font-size: clamp(40px, 14vw, 120px)`, i.e. real big, over the whole fight,
1.4 s per trigger. That single path is the whole complaint.

## 1. How Tekken actually does it (verified sources, not memory)

- **Rage (T7):** activates automatically at low HP; the fighter gets a red
  aura and "their health bar will also flash red" — no center-screen text.
  Sources: https://tekken.fandom.com/wiki/Rage ("the fighter a red aura",
  "health bar a red glow"); https://www.magicgameworld.com/tekken-7-rage-guide/
  ("enveloped in a red aura. Their health bar will also flash red").
- **Heat (T8):** "The Heat indicator. This is a blue bar located below your
  HP" that "changes to purple and will steadily decrease"; the fighter is
  "covered in blue flames while the Heat Timer ticks down" — a HUD bar +
  character glow, never big center text. Sources: official T8 battle page
  https://tk8.tekken-official.jp/en/battle/basic_operations.php ("Heat
  Timer: Timer counts down when Heat is activated", listed under Game
  Screen gauges alongside Health Gauge); https://realsport101.com/article/tekken-8-heat-system-explained;
  https://www.eventhubs.com/news/2023/feb/05/breakdown-tekken8-heat-system-mechanics/
  ("indicated by a blue glow").
- **Round announcements:** Tekken's big text is a round-BOUNDARY ritual —
  "Round One! Fight!" before action starts, "K.O.!" when the round ends
  (announcer lines, pre-fight ritual, not mid-action). WH already had this
  shape in `game/js/game.js` (`ROUND n` / `FIGHT!` / `K.O.`); it stays.
- **Stage breaks:** Tekken shows no "WALL BREAK" text — the wall/floor
  itself breaking, the camera shake and the level drop ARE the feedback.
  WH's shake/hitstop/particles already do this; the banner was redundant.
- **"TIME SHIFT":** no literal "TIME SHIFT" string exists anywhere in the
  fight UI. The closest match is the V-Shift Break path: `V.SLOWMO_DURATION`
  slow-mo + the `V-SHIFT «name TBD» — BREAK!` banner in `game/js/main.js`.
  The banner is deleted; the slow-mo mechanic itself is untouched (it is
  not text).

Rule applied to every row below: round-boundary announcements stay at
round boundaries and only there; EVERY mid-fight system trigger becomes a
HUD indicator (glow / bar effect / existing HUD tag) and emits no text.

## 2. Audit table — every fight-UI popup found, and its disposition

`banner()` = the 40–120px full-screen center renderer. `flash` = the
existing full-screen non-text glow (`surge-flash` / `rage-flash`).

| # | Trigger (file:line at audit) | Old on-screen text | Disposition |
|---|---|---|---|
| 1 | V-Trigger install (`game/js/main.js` `vTrigger`, via `game/js/game.js`) | `V-TRIGGER «name TBD» — SOUL AWAKENED` big center | DELETED. Gold glow (`surgeFlash`) only. NEEDS NAME (no canon name). |
| 2 | V-Reversal (`main.js` `vReversal`) | `V-REVERSAL «name TBD»` big center | DELETED. Blue glow only. NEEDS NAME. |
| 3 | V-Shift Break (`main.js` `vShiftBreak`) | `V-SHIFT «name TBD» — BREAK!` big center | DELETED. White/cyan glow + existing slow-mo only. This is the user's "V shift" (and the "time shift" slow-mo pairing). NEEDS NAME. |
| 4 | V-Skill parry (`main.js` `vParry`) | `V-SKILL PARRY «name TBD»` big center | DELETED. Pale-blue glow only. NEEDS NAME. |
| 5 | V-Shift itself (`main.js` `vShift`) | (none — already flash-only) | UNCHANGED. Already Tekken-correct; proves the pattern. |
| 6 | Rage start (`game/js/rage.js` update) | `RAGE` big center | DELETED. Kept: red aura on fighter + pulsing HUD tag under the health bar (now NAMELESS — see §3) + rage sound. Tekken-exact. NEEDS NAME. |
| 7 | Rage Art connect (`rage.js` `rageArtHit`) | `RAGE ART` big center | DELETED. Kept: hitstop + shake + slow-mo + red flash. The cinematic move itself is the feedback. NEEDS NAME. |
| 8 | Soul Urge activate (`game/js/soulurge.js` activate) | `SOUL URGE` big center | DELETED. Kept: `SOUL URGE` HUD wrap (locked canon name, HUD-sized 7px label + fill bar) + aura. |
| 9 | Urge Smash connect (`soulurge.js` `urgeSmashHit`) | `URGE SMASH` big center | DELETED. Kept: hitstop + shake + flash. |
| 10 | Nine-Soul Release (`game/js/soul-systems.js` release) | `NINE-SOUL RELEASE 九魂解放` big center | DELETED. Gold glow only; damage + variant still apply. Canon-named system, but mid-fight text is banned regardless — glow carries it. |
| 11 | Reihou (`soul-systems.js` tryReihou) | `REIHOU 霊放` big center | DELETED. Blue glow + spirit flare + rage purge still apply. |
| 12 | Release ready (`soul-systems.js` update) | `SOUL RELEASE READY` big center | DELETED. Replaced by a REAL HUD indicator: new `ui.setSoulReady()` glows the Nine-Soul Meter wrap gold (T8 Heat-timer pattern: a bar under the health bar). Previously `setSoulReady` was called but never implemented — now it is. |
| 13 | Trial's Seal (`soul-systems.js` onRoundEnd) | `TRIAL'S SEAL 試練の封` big center | KEPT — round-boundary announcement (fires from `_endRound`, after K.O.). Canon name, boundary only. |
| 14 | Wall / Floor / Balcony break (`game/js/stagebreaks.js`) | `WALL BREAK` / `FLOOR BREAK` / `BALCONY BREAK` big center | DELETED (all three). Kept: shake + hitstop + particles + level drop. Tekken-exact: no text. NEEDS NAME for any future label (none shown). |
| 15 | Spirit action (`game/js/spirit-actions.js` trySpirit) | `魂 ACTION` big center | DELETED. Gold glow only; damage + context still apply. Canon label survives as move data, not on screen mid-fight. |
| 16 | KESSHOU finisher (`game/js/finisher.js` tryFinisher) | `FINISHER — <name>` big center | DELETED. Finisher fires mid-fight (gates: full meter + victim ≤25% HP), so it is mid-fight text. Kept: the cinematic beat sequence itself. |
| 17 | Soul Surge name (`game/js/main.js` `surgeName`, via `game/js/game.js` ×2) | `SOUL SURGE — <name>` big text at top 22%, 22–52px | DELETED — method, both call sites, `#surge-name` element, and its CSS. Kept: `surgeFlash` glow + surge sound. |
| 18 | Round flow (`game/js/game.js`) | `ROUND n`, `FIGHT!`, `K.O.`, `DOUBLE K.O.` | KEPT — round-boundary announcements only (intro / round end). |
| 19 | Training reset (`game/js/game.js`) | `RESET — DUMMY RESTORED` | KEPT — round-boundary (round restarts, not mid-action). |
| 20 | Mode/episode/heartmind/rank intros (`game/js/modes.js`, `episodes.js`, `heartmind.js`, `ranks.js`) | `FIGHT n — <foe>`, `WAVE n`, `<stage> CLEARED`, `RANK BATTLE — …`, etc. | KEPT — all fire BEFORE `startFight` (loading/intro) or AFTER `onMatchEnd` (wave/stage transitions), never during live action. Audited call by call; none fires mid-fight. |
| 21 | WebGL context lost (`game/js/scene.js`) | `GRAPHICS PAUSED — RESTORING…` | KEPT — error state, not a fight popup; hiding it would hide a real failure. |
| 22 | Combo counter (`main.js` `combo`) | `<n> HITS`, left side, not center | KEPT — Tekken-faithful side counter (left 8%, top 28%), not center-screen. Not a system announcement. |
| 23 | Throw-break prompt (`main.js` `throwBreakPrompt`) | `BREAK THE THROW — TAP LP/RP/LP+RP`, 20px top-center | KEPT — gameplay-critical input prompt (Tekken throw-break rule), small, timed 0.9s. Not an announcement. Uses LP1/RP2/LK3/RK4 naming. |
| 24 | 3D in-world labels (`game/js/labels3d.js` `banner`) | 3D world-space text (fontSize 0.8 world units) | KEPT — different renderer (in-world, not screen-space); no callers route fight announcements through it. |

## 3. TBD removal — total

- All four `«name TBD»` mid-fight banners deleted with their call sites
  (§2 rows 1–4).
- `«name TBD»` stripped from `game/js/v-system.js` data names
  (`V-SKILL — Soul Palm`, etc.) and from comments in `game/js/main.js`,
  `game/js/v-system.js`, `game/js/fighter.js`. The EX-variant builder now
  appends ` EX` instead of replacing a marker that no longer exists.
  These V-System names remain TECHNICAL data names only; they are never
  rendered mid-fight. Their canon names are still unassigned → NEEDS NAME.
- Tournament bracket empty slot: `TBD` → `—`
  (`game/js/tournament-ui.js`, `game/js/tournament.js`). Menu-only, but
  removed under the total-removal order.
- Post-fix grep proof (run against the branch): zero `TBD` in
  `game/js/main.js`, `v-system.js`, `fighter.js`, `rage.js`, `soulurge.js`,
  `soul-systems.js`, `stagebreaks.js`, `spirit-actions.js`, `finisher.js`,
  `game.js`, `tournament-ui.js`, `tournament.js`; zero `«name TBD»`
  anywhere in `game/js/`; zero `banner(` calls in the mid-fight files
  listed in the regression test. (`placeholder` survives only in the asset
  pipeline — material-name regexes, voice-clip logs — which never render
  fight text. `TODO` in `game/js/custom-fighter.js` is a code comment
  about a creation-suite slot, not fight UI.)

## 4. Proprietary names — NEEDS NAME flags (nothing invented)

Locked canon name used HUD-sized only: SOUL URGE (urge-wrap label).
Canon-named but mid-fight text removed anyway: Nine-Soul Release, Reihou,
Trial's Seal (boundary only), 魂 ACTION (data only).
NEEDS NAME (no name in `CANON.md` / `docs/design/SOUL-SYSTEMS.md` — checked
by grep; the CANON.md hits for "rage" are unrelated prose): Rage, V-Shift,
V-Trigger, V-Reversal, V-Skill/parry, Rage Art/Drive, Wall/Floor/Balcony
Break, Urge Smash, Power Crush, Screw, Bound, Time Shift (no such string
exists — see §1). Clean solution applied: all become NAMELESS HUD
indicators (glow / bar / aura), no invented name and no Tekken name on
screen. OUT OF SCOPE, flagged not fixed: the touch-pad button still labeled
`RAGE` (`game/index.html` + `game/js/identity.js` `TOUCH_LABELS`) and the
`HEAT` touch label — persistent controls, not popups; renaming them needs
the same NEEDS NAME decisions and touches input UI, so they are flagged
for the coordinator rather than renamed here with an invented name.

## 5. Files changed (surgical only)

`game/js/main.js`, `game/js/rage.js`, `game/js/soulurge.js`,
`game/js/soul-systems.js`, `game/js/stagebreaks.js`,
`game/js/spirit-actions.js`, `game/js/finisher.js`, `game/js/game.js`,
`game/js/v-system.js`, `game/js/fighter.js` (comment only),
`game/js/tournament-ui.js`, `game/js/tournament.js`, `game/index.html`,
`game/styles.css`, `game/tests/popup-hud.test.mjs` (new),
`docs/research/popup-fix-audit-20261024.md` (this file).
No combat/animation logic touched (priority #2 lane owns that); no
joystick/input code touched (joystick is CLOSED, user-confirmed).
`game/index.html` edits touch only the HUD section (not any
`<section id="screen-*">`) and `game/styles.css` is already listed under
the sourced `hud-fight` screen in `game/ui_sources.json`, so the
ui-sources gate is unaffected.

## 6. Tests

`game/tests/popup-hud.test.mjs` (new): static regression tests — no TBD in
fight UI paths; no `banner(` in any mid-fight file; `game.js` banners
restricted to the boundary set; V-System methods contain no banner and
`surgeName` is gone; `setSoulReady` exists; Trial's Seal boundary banner
kept; index.html has no `#surge-name` and no `RAGE` tag text; CSS has the
`soul-ready` meter glow and no `.surge-name` rule; V-Skill catalog names
contain no TBD and the EX variant appends ` EX`. Run:
`node --test game/tests/popup-hud.test.mjs` (and the full
`node --test game/tests/*.test.mjs` suite before filing).

## 7. Live verification (for the coordinator's parent browser delegation)

Play a FULL fight on the deployed playable build, phone portrait, touch
taps like the user plays: (a) trigger V-Shift Break, V-Trigger,
V-Reversal, V-Skill parry, Rage (drop a fighter below 25% HP), Rage Art,
Soul Urge, Urge Smash, Nine-Soul Release, Reihou, a wall break, a spirit
action, and a KESSHOU finisher — confirm ZERO big center-screen text for
any of them and ZERO `TBD` anywhere; (b) confirm the HUD indicators ARE
visible instead (glows, red aura + nameless red HUD bar for Rage, SOUL
URGE wrap + fill, gold meter-wrap glow when Release is ready); (c)
confirm round announcements (`ROUND n`, `FIGHT!`, `K.O.`) appear ONLY at
round boundaries. Tests are NOT playtest — the deploy is not verified
until this live pass passes.

## 8. GPU note (honest scope)

No GPU job is fabricated for this text-deletion fix. The honest GPU piece
is a visual-regression batch (fight screenshots before/after, pixelmatch
comparison proving no big popups) on the Kaggle T4 x2 notebook pipeline
(https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit, Colab as
overflow). That job package — with measured times (nvidia-smi +
torch.cuda proof, input size, output, wall time, CPU-baseline time) — is
prepared for the coordinator's browser lane; it is not claimed as done
here.
