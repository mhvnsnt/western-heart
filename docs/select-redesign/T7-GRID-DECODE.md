# Tekken 7 Character Select — Design Decode (T7 rebuild, 2026-10-23)

Owner order (verbatim, via coordinator): "Rebuild the character select
screen from Tekken 7's (and TTT2's) actual character select. Study the
real thing: grid layout, fighter card/portrait structure, player 1P/2P
cursor behavior, stage select flow that follows, announcer voice cues,
visual design."

The Steam/depot route for real T7/T8 UI files is DEAD (owner does not own
either on Steam/PC). This decode is built from PUBLIC VISUAL REFERENCES
(screenshots, press, footage write-ups, manuals) and recreated with OUR
OWN original art and CSS. No ripped Tekken UI files are in this repo —
owner rule 8 (no copyrighted/leaked game files in public repos or Pages).
Community-posted T7 UI textures were surveyed as reference only and NOT
committed (they are repackaged game assets).

This decode SUPERSEDES the T8 grid transplant's layout (the T8 decode doc
stays in the repo as history; the 't8' ui-skin.js entry is intact — when
the owner's T8 reference/art lands, setSkin('t8') restores the T8 look
with no restructuring).

## 1. Sources

- T7 versus character select, public screenshots/footage (tekkenzone.net,
  eventhubs.com T7 coverage, Bandai Namco press kit): the primary visual
  reference. Studied: header, 2-row portrait grid, flanking P1/P2 renders,
  cursors, "?" random panel, hints bar, timer, stage select strip.
- Tekken 7 Xbox One/PS4 manual conventions (regvault.org Tekken 1 PSX
  manual lineage, carried through the series): punch button = costume 1,
  kick button = costume 2 on the select screen; the 99-second selector
  timer; timeout locks the highlighted fighter (the timer never leaves a
  side unpicked).
- TTT2 (gamesdb/launchbox write-ups; TTT PS2 manual via archive.org):
  the two-cursor flow (P1 cursor + P2 cursor over the portrait field) and
  the "?" convention for unrevealed/locked fighters.
- T6 (neogaf.com T6 thread, 2009): "?" random slots at the ends of the
  portrait row.
- T8 CNT coverage (eventhubs.com, 2023-07-21) cross-checked the announcer
  cue points the series keeps: "Choose your fighter!" on entry, fighter
  name shouts on lock, "Choose your stage!" + stage-name callouts.

## 2. Layout decode (T7 versus select)

```
+----------------------------------------------------------+
| BACK   C H O O S E   Y O U R   F I G H T E R        [99]  |
|                                                          |
| [P1 ZONE: big 3D render] [2-ROW PORTRAIT GRID] [P2 ZONE] |
|  1P tag, red wash           [][][][][][]...      2P tag,  |
|  BIG ITALIC NAME            [][][][][][]...      blue wash|
|  style / archetype /        ...scrolls horizontally      |
|  origin + stat bars                                      |
|                                                          |
|  [P] ATTIRE 1    hint text    [K] ATTIRE 2   [CONFIRM]    |
+----------------------------------------------------------+
```

- The grid is EXACTLY 2 ROWS of portrait panels, column-major, scrolling
  horizontally inside its own box. Panels: portrait bust + name in steep
  italic condensed type; sharp ANGULAR frames (cut corners, parallelogram
  energy), dark fill, thin light frame.
- P1's fighter stands big on the LEFT, P2's on the RIGHT — live animated
  3D renders (ours: the same GLBs + stance clips the fight uses; never a
  still — owner law). Behind each: a faded portrait-art wash, red (P1) /
  blue (P2).
- Name banners: BIG steep-italic condensed white type under each render.
- Cursors: P1 = hot-red glowing frame on the card; P2 = blue glowing
  frame (pulsing). A locked fighter's card carries a "1P"/"2P" tag.
- "?" RANDOM panel at the END of the grid.
- Timer: "99" top-right in an angular plate, counting down; on timeout
  the highlighted fighter is locked for the active side (random when
  nothing is highlighted) — the real Tekken rule.
- Bottom hints bar: T7's prompt chips (arrows select, triangle preset,
  circle confirm, cross back). Ours: tap-to-preview, P/K attire preset
  buttons (the owner's classic Tekken-1 punch/kick scheme), CONFIRM.
- After both fighters lock: the STAGE SELECT — "CHOOSE YOUR STAGE"
  header, big preview pane with the stage-name banner, ONE horizontal
  strip of stage cards (thumbnail + name), "?" random card in the strip,
  announcer stage-name callouts, BACK to the fighter grid, CONFIRM to
  the fight.

## 3. Card arrangement

- Portrait-orientation panels (~3:4), 2 rows, horizontal scroll; the
  cursor card renders LARGER than its neighbours (the T3 aperture rule
  the series keeps).
- Slim in-flow tier dividers keep the owner's DISPLAY ORDER LAW visible
  (Tripo originals → SmutBase originals → main roster). T7 has no tiers;
  ours do — documented deviation, same as the T8 decode's §8.1.
- No Tekken names anywhere on the cards (in-universe law): WH names
  only. The replacement map is structural — one WH card per Tekken slot,
  no duplicates; the Tekken originals ladder at the BACK of each
  fighter's attire list (slots 5–7 rule), never as cards.

## 4. Fonts

- Display: bold italic CONDENSED grotesque, uppercase, tight spacing,
  slant ≈ 10° (steeper than T8's ≈ 7°).
- Our recreation: `"Arial Narrow", "Helvetica Neue", Helvetica, Impact`
  display stack with CSS `skewX(-10deg)` — no bundled font file yet
  (a future skin may ship a woff2; see js/ui-skin.js drop-in contract).

## 5. Colors

- P1 accent: hot red ≈ #ff2e2e (cursor ring, tags, fact chips).
- P2 accent: bright blue ≈ #2f9dff.
- Stage: ember-smoke near-black #0a0505 → deep ember #220d0d; drifting
  ember particles (CSS); red wash behind P1 art, blue wash behind P2.
- Cards: very dark fill #161013, 2px rgba(255,255,255,0.14) frames.
- Names: white with accent-colored glow.

## 6. Announcer cue points (T7 flow, our voice pipeline)

- Screen opens → `voice.announce('choose-your-fighter')` ("Choose your
  fighter!").
- Fighter locks → the fighter's own `select-01` voice line (real
  owner-original audio where recorded; subtitle fallback otherwise)
  PLUS the announcer name-shout subtitle ("PANTERA!").
- Stage strip opens → `voice.announce('choose-your-stage')`.
- Stage highlighted → announcer stage-name subtitle ("FORGOTTEN REALM!").
- All announcer lines are subtitle-only placeholders until the
  proprietary announcer voice lands (owner law: no Tekken audio bytes;
  same placeholder policy as the fight announcer).

## 7. Animations / transitions

- Live 3D previews with validated teardown-bank stance clips (kept from
  the earlier build); turntable fallback; portrait plate when WebGL is
  unavailable.
- Cursor move: 0.12s scale/glow transition + the aperture rule.
- Tap: brief brightness flash on the tapped card (`tap-flash`).
- Attire switch: the big model swaps LIVE (P/K buttons + attire chips —
  T7's on-screen costume presets).
- Confirm: lock badge + 1P/2P card tag; versus hands the cursor to P2.

## 8. What we changed vs. T7 (documented deviations)

1. Tier dividers (TRIPO ORIGINALS / SMUTBASE ORIGINALS / MAIN ROSTER):
   T7 has none. Ours keep the owner's DISPLAY ORDER LAW visible
   (Tripo-first; the 6 hand-picked SmutBase primaries right behind —
   extended law 2026-10-23). Slim in-flow labels, not cards.
2. Fact block rows: T7 = Fighting Style / Nationality / Height-Weight.
   Ours = FIGHTING STYLE / ARCHETYPE / ORIGIN ("Parts unknown" canon
   fallback) — height/weight are NOT shown because we have no measured
   data and never invent it. The POW/SPD/JMP/DEF mini-bars are kept
   underneath (our game's real numbers).
3. Hints bar keeps our functional P/K attire buttons (owner's classic
   Tekken-1 scheme) as prompt chips; T7's triangle-preset maps to our
   attire chips on the plate.
4. Phone layout: T7 is a landscape console screen; on portrait phones
   the panes sit side-by-side on top and the 2-row grid runs full-width
   below, all inside non-scrolling screen chrome. PORTRAIT PHONE IS
   PRIMARY (owner law 2026-10-23): this is a mobile game.
5. TOUCH LAW (owner 2026-10-23, standing): SCREEN TAPS, not button
   clicks — minimum 44px tap targets (ours are 48px+), NO hand-tooled
   touch math and NO hover-dependent UI anywhere. Input uses the
   researched proven stack: the native Pointer Events API
   (pointerdown/pointerup/pointermove with setPointerCapture) plus
   CSS touch-action: manipulation on tappables — the 2026 baseline,
   no dependency (game/js/tap.js; no gesture library needed — the
   grids scroll natively and the platform's pointercancel voids a tap
   that becomes a scroll). Tap a card = preview on your side; tap the
   highlighted card again (or CONFIRM) = lock. Every interactive
   element is 48px+ — no dead ends, no tiny text links. Portrait
   phone is primary.
6. Nine Souls redesign (2026-10-23): seven souls stay OFF the grid as
   standalone cards; ZEN and GYOU stay selectable (their models are
   real: Zen's Tripo spirit body, Gyou's build).
7. Header text: T7's exact "CHOOSE YOUR FIGHTER" / "CHOOSE YOUR STAGE".

## 9. Skin-swap layer

All of §2–§5's visual tokens live in `game/js/ui-skin.js` (the new 't7'
skin; colors, fonts, card geometry, fact rows, texture paths).
select-screen.js reads them via `getSkin()`/`applySkin()` (called on
build() and onShow()); select.css consumes only the resulting CSS vars.
The drop-in contract (new skins, texture naming, copyright rule) is
documented at the top of ui-skin.js. The 't8' skin entry is INTACT:
when the owner's T8 reference/art lands, setSkin('t8') (or ?skin=t8)
restores the T8 look with no restructuring.
