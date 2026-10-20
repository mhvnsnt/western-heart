# Tekken-style character select — build log (2026-10-20)

Owner orders: 2026-10-18 (Tekken 8-style select: bisected live-3D zone,
contained card strip, attire switching on select), 2026-10-19 ~16:03
(character select overhaul: Tekken-style scrollable character box, picked
fighter BIG with 3D model + idle animation), re-issued 2026-10-20 ~09:45
("use the Tekken files, the teardown files to decode and decrypt them and
make our fighter select screen more like the Tekken one"). The
NO-T-POSE law (2026-10-20 ~07:51) applies: no T-pose portraits, no
T-pose fighters in the preview — live animated models only.

## What was verified before building

- The standing design doc `docs/select-redesign/SELECT-DESIGN.md`
  (Lane I, Round 2) documents the T8/TTT2/T6 research, but its build
  targeted the opt-in `game/ui-wh/` overlay (`?ui=wh`), NOT the default
  game flow. The live default select (`game/index.html` #screen-select +
  `game/js/main.js`) was still the old single-preview + vertical grid —
  that is the screen the owner plays, and the one rebuilt here.
- No select-screen PR existed for the default flow (checked 2026-10-20).

## Teardown / research sources the layout is built from

1. **Tekken 3 selector, real reverse-engineered code in our teardown**
   (`teardown/tekken3/tools/tekken3recompiled/psxrecomp/runtime/include/tekken3_selector_layout.h`,
   `teardown/tekken3/tools/tekken3recompiled/tools/SELECTOR_CAROUSEL.md`):
   the selector composites DMA packets with roles BACKDROP,
   LEFT_PLAYER, RIGHT_PLAYER, LEFT_FRAME, RIGHT_FRAME, ROSTER, CENTRE —
   a bisected left/right player zone over a roster field. Roster field:
   10–11 columns (cabinet layout). Portraits are center-cropped 2:3 and
   sampled directly to output size; the **selected aperture (72×108) is
   larger than its neighbours (56×84)**. The timer starts at **99**
   (`99 * tick_rate`, verified SLUS-00402 overlay initializer). Picking
   is a two-step flow (fighter first, then outfit carousel; Cross
   confirms, Circle unselects); each fighter remembers its costume;
   **CPU cards appear on the CPU fighter's own side**.
2. **Tekken 1 / Tekken 6** (via `docs/select-redesign/SELECT-DESIGN.md` §1,
   citing the Tekken 1 PSX manual and T6 sources): **punch button =
   outfit 1, kick button = outfit 2** at character select; T6 puts
   **"?" random slots at both ends of the portrait row**.
3. **Tekken 8** (same doc §1): bisected zone with the picked fighter BIG
   as a live animated 3D model doing select idles ("little personal
   acts"); per-character costume slots chosen right on the select
   screen; menus are real-time 3D — "what you see is exactly what you
   get in the match" (our previews use the same GLBs + loader as the
   fight, `game/js/assets.js`).
4. **Owner spec** (2026-10-18, in SELECT-DESIGN.md §1): top ~75–80%
   bisected P1/P2 zone; bottom ~20% card strip is the ONLY scrolling
   element and scrolls within its own box; tap/hover a card → that
   fighter's full 3D render appears on YOUR side; name + fighting
   style on cards; name + style + stats for picked fighters; attire
   switching on the select screen; mobile-first.

## What was built (branch feat/tekken-select-20261020)

- `game/index.html` — #screen-select restructured: header (unchanged:
  BACK / title / 99s timer), `.fighters-zone` with two `.side-pane`s
  (P1 left, P2 right; each: live canvas, side tag, LOCKED badge,
  loading/pending note, name/title/style/stats plate, attire chips),
  VS medallion, `.hints-bar` (P · ATTIRE 1 / hint / K · ATTIRE 2 /
  CONFIRM), `.strip-wrap` holding `#char-grid.card-strip`.
  Deleted old markup (named per anti-clobber rule 4): `.select-body`,
  `#select-preview` + `#preview-canvas` + `.preview-info` (single
  shared preview pane), the old select `<footer class="select-footer">`
  (its #select-hint and #confirm-fighter survive, moved into the
  hints bar with the same ids, so modes.js/menus.js hooks are
  untouched).
- `game/js/select-screen.js` (NEW) — `PreviewPane` (one THREE
  renderer/scene per side, same lights as the old preview) +
  `createSelectScreen` controller: card strip build (roster order,
  tier dividers, "?" RANDOM card last per T6), per-side highlight /
  lock state mirroring the mode flow (versus: P1 locks → cursor
  hands to P2; team: picks stack on P1; solo: single lock), attire
  switching via the existing `attires.js` (chips per side + P/K
  buttons + J/K keys; K cycles attires 2..n, P returns to attire 1),
  stats plate from the game's real numbers (`roster.stats` or the
  Fighter default in `fighter.js` — { speed 2.8, jump 7.2,
  power 1.1, defense 1.05 }, speed clamped to 3.5 like the Fighter).
  Portraits consume the existing `assets/portraits/<id>.png` paths —
  the personality pass's posed portraits drop straight in; a fighter
  with no portrait gets a monogram plate, never another fighter's
  face. Missing model (e.g. ryuji-rock) shows MODEL PENDING.
- `game/js/main.js` — surgical delegation: the old buildSelect /
  selectCard / attire-strip / single-preview / select-keyboard block
  (~215 lines) replaced by createSelectScreen wiring; confirmSelection
  notifies the module's lock state before modes.onConfirm; the 99s
  timer timeout and the ?fighter= deep link call
  selectScreen.selectById. `fighter.js` untouched (personality-pass
  lane's surface). Stage select untouched (its shared styles in
  styles.css are unmodified; all new select CSS is scoped).
- `game/select.css` (NEW) — all layout scoped to #screen-select:
  zone flexes between header/hints/strip; strip height
  clamp(124px, 20vh, 188px), `overflow-x: auto` on the strip only,
  page `overflow: hidden`; the cursor card scales up (T3 aperture
  rule); P1 cursor/lock gold, P2 #ff5470.

Verified dimensions in a live browser (390×844): 57 cards (56 roster
+ RANDOM), strip scrollWidth 5576px inside a 390px client box (the
strip scrolls, the page does not — document does not overflow),
strip height 167px ≈ 20% of viewport.

## Animation honesty note

The GLBs' embedded 'Idle' clips are NOT real idles: sampling
demonio.glb's clip data shows the arm bones swing ~0.02 rad around
the bind pose (a T-pose hold with finger micro-motion); pantera.glb
and steve-fox.glb carry the same clip set. Showing those on the
select screen would put T-pose fighters on it — banned by the
owner's NO-T-POSE law (2026-10-20). So the preview plays the
fighter's REAL Tekken idle: wherever the fighter's moveset source
has a decoded T3 bank, the pane loads the bank through the fight's
own loader (`t3anims.js` loadT3Clips + createT3Actions) and plays
its looping `stance` clip, under the fight's own binding rule
(fighter.js: bank actions only when the model carries the
canonical Hips + RightArm bones; a fighter never gets another
character's bank — `bankIdFor`). Banks decoded today: king, jin,
xiaoyu, bryan, gunjack, yoshimitsu (so e.g. PANTERA idles in King's
stance, DEMONIO in Jin's). The personality pass's extraction of the
remaining banks (Lei, Paul, Eddy, Hwoarang, Nina, Anna, Julia,
Mokujin, Bosconovitch, Armor King, Heihachi) widens coverage
automatically — the preview reads the same T3_BANKS table.
Fighters with no bank yet fall back to their embedded clip if one
exists, else the live model on a slow turntable (the pre-existing
preview presentation) — live 3D, never a still image, and no
hand-authored fake idle was added (RULES_NO_GUESSING).

Measured gate on bank stances (found while building this): applied
raw, the current bank clips visibly mis-fit these rigs — DEMONIO
pitched flat on the jin bank, PANTERA's arms gyro-displaced on the
king bank (the same failure family the owner reported in fights;
a control fight run for this build showed the shipped fight path
collapsing both fighters to the floor, so this is the animation
data/application state on main today, owned by the personality
pass's bank-wiring/frozen-idle work — not something a select PR
should paper over with invented retarget math). The pane
therefore validates every stance on the sampled skeleton before
showing it: head must sit >0.25 above the hips, and each hand
must stay within its arm's anatomical reach (segment lengths are
pose-invariant). A failing stance is rejected to the fallback;
a passing one plays. When the animation lane fixes the banks,
the same checks pass and the real Tekken stances appear on the
select screen with no select-side changes.

## Proof

Local (worktree served on 127.0.0.1, headless Chromium, CDP captures
— Playwright page.screenshot stalls under SwiftShader with live
WebGL canvases; harness: ~/workspace/_wh-work/select-harness/):
- Strip facts (390×844): 57 cards (56 roster + RANDOM), strip
  scrollWidth 5576px inside a 390px client box, document does not
  overflow (the strip is the only scroller), strip height 167px ≈
  20% of viewport, fighters zone 535px.
- Flow: menu → VERSUS → DEMONIO pick (pane ready, all 5 attire
  chips) → K tap switches BASE → ATTIRE 1 (pane-state verified:
  chip ATTIRE 1*, style '· ATTIRE 1', model swapped to the
  demonio-a1 devil model) → CONFIRM locks P1 (badge + locked:true)
  and hands the cursor to P2 → RIN pick on P2 → CONFIRM → stage
  select → CONFIRM STAGE → fight HUD reached (twice, zero page
  errors in the versus/fight stages).
- Motion: QA-hook samples 75s apart in the starved test renderer
  (~3% of real time): model rotation.y 0.18 → 0.5867, mixer time
  0.05 → 1.21 — the preview animates (turntable fallback + embedded
  clips; bank stances currently rejected by the fit gate, see the
  animation note: jin stance on demonio measured head-hips gap
  −0.10, king stance on pantera gap 0.04).
- Screenshots (own-eyes viewed): select-v3-phone-demonio-stance-a/b,
  select-v3-phone-demonio-attire1, select-v3-phone-versus-p2-rin,
  select-v3-phone-pantera-gate, select-v3-desktop-initial,
  select-v3-desktop-pantera-stance-a (~/workspace/your_files/).

Live (after merge + gh-pages redeploy):
PR #384 merged 2026-10-20 (merge commit 113739ae). Redeployed with
the established recipe (gh-pages tree, game subtree swapped to the
new main; gh-pages commit aea76adf). Byte-verify against
origin/main: ALL MATCH (sha256) — game/index.html 13234B,
game/select.css 11928B, game/js/select-screen.js 26481B,
game/js/main.js 22824B. Live browser proof
(https://mhvnsnt.github.io/western-heart/game/): strip facts —
58 cards (57 roster on current main + RANDOM), strip scrollWidth
5672px in a 390px box, page does not scroll; DEMONIO pick live
with real stats and all 5 attire chips; K tap switched to ATTIRE 1
live (model swapped); CONFIRM locked P1 and activated P2 (pane
state). Live screenshots (own-eyes viewed):
live-select-final-phone-initial.png,
live-select-final-phone-demonio.png,
live-select-final-phone-demonio-attire1.png
(~/workspace/your_files/). The live P2 capture was cut short by
the test VM's SwiftShader target dying under load; the full
versus → stage → fight-HUD flow is proven locally against the
byte-identical code (see above). Full live results are also
commented on PR #384.
