# Tekken 8 Character Select — Design Decode (Grid Transplant, 2026-10-22)

Owner order (verbatim): "pull in like the Tekken 8 character select menu and
decode it and everything all the UI and menu art and the selections how it's
set up and get our characters put onto the Tekken the most recent Tekken game
menu grid that you can get a hold of and upgrade the character select menu"

The Steam/depot route for real T8 UI files is DEAD (owner does not own T8 on
Steam). This decode is built from PUBLIC VISUAL REFERENCES (screenshots,
press, footage write-ups) and recreated with OUR OWN original art. No ripped
Tekken UI files are in this repo — owner rule 8 (no copyrighted/leaked game
files in public repos or Pages). Community-posted T8 UI textures were surveyed
as reference only and NOT committed (they are repackaged game assets).

## 1. Sources

- In-game T8 character select screenshot (versus, both players locked —
  tekkenzone.net press screenshot, 1280×720): the primary visual reference.
  Studied pixel-level: layout, card geometry, cursors, name banners, fact
  blocks, hints bar, background.
- eventhubs.com, 2023-07-21 (CNT select): grid organized horizontally, 8
  characters top row / 8 bottom row; icons "quite small in relation to
  everything else", "room for a good amount of expansion"; fighters perform
  "little personal acts" while waiting (Xiaoyu brushes her bangs, Lili pets
  her cat).
- gamerant.com, 2023-05-15 (PlayX4 leak): "Jun and Kazuya on screen, along
  with smaller picture boxes in the middle for the other characters" —
  confirms the final layout: big models flanking, compact grid center.
- twistedvoxel.com T7-vs-T8 comparison (2023-05-15).
- tk8.tekken-official.jp customize page: ten costume slots per fighter,
  "select your favourite slot in the Character Select".
- CDDTreborn/Tekken-8-Resources wiki (UI folder reference: CS = Character
  Select) — structural naming only, no assets taken.

## 2. Layout decode (1280×720 reference)

```
+----------------------------------------------------------+
|  [P1 ZONE: big 3D model, left]   [P2 ZONE: big 3D, right] |
|  faded portrait art behind each (red wash P1 / blue P2)  |
|                                                          |
|  REINA (big italic name, left)        JIN (right)         |
|  [Fighting Style] [Nationality]      [Fighting Style]... |
|  Unknown / Unknown ...               Karate / Japan ...  |
|                                                          |
|              +--[ COMPACT GRID ]--+                      |
|              | [][][][][][][][][]|  ~12 cols, small      |
|              | [][][][][][][][][]|  square portrait      |
|              | [][][][][][P2][?] |  cards, centered      |
|              +--------------------+                      |
|  X Confirm   O Back   [] Customized Slots   (bottom-left)|
+----------------------------------------------------------+
```

- The stage is FULL-SCREEN. P1's fighter stands big on the LEFT half, P2's
  on the RIGHT half — live animated 3D models doing idle "personal acts".
- Behind each model: a LARGE faded portrait render of that fighter, tinted
  dark red (P1) / dark blue (P2), fading into the near-black stage.
- The GRID floats centered over the lower-middle of the stage, ~12 columns
  of small square portrait cards (face art only, no text on cards). It
  overlaps the stage background, not the models' heads.
- Name banners: BIG italic condensed white type at the outer edges
  (REINA left edge, JIN right edge), roughly at the models' shoulder height.
- Fact blocks sit under each name: small COLORED LABEL CHIPS
  (FIGHTING STYLE / NATIONALITY / HEIGHT / WEIGHT) with the value in white
  below each chip, stacked vertically per side.
- Bottom-left hints bar: PlayStation button glyphs + labels —
  "✕ Confirm · ◯ Back · ▢ Customized Slots".
- Cursors: P1 = hot pink/red ring on the card; P2 = blue ring. A locked
  fighter's card carries a small "P2"/"P1" tag. "?" random slot sits inside
  the grid flow (black card, white ?).
- Timer: the versus select runs a countdown (separate from our 99s Tekken
  standard, which we keep per owner spec).

## 3. Card arrangement

- Square cards, face-art portraits, 2px dark frames; ~12 columns at
  1280×720 → cards ≈ 60px. Icons deliberately small ("room for expansion").
- Cursor card is slightly emphasized (brighter frame + glow); locked cards
  get the P1/P2 tag chip at top-right.
- No tier labels, no names on cards — the highlighted fighter's identity
  lives in the name banner + fact block.

## 4. Fonts

- Display: bold italic CONDENSED grotesque (custom Bandai Namco face,
  Eurostile-adjacent). Names are uppercase, tight letter-spacing, italic
  slant ≈ 7–10°.
- Body/labels: neutral grotesque, small caps-ish labels on the chips.
- Our recreation: `"Arial Narrow", "Helvetica Neue", Helvetica, Impact`
  display stack with CSS `skewX(-7°)` for the italic — no bundled font file
  yet (a future skin may ship a woff2; see js/ui-skin.js drop-in contract).

## 5. Colors

- P1 accent: hot pink-red ≈ #ff2d55 (cursor ring, fact chips, P1 tag).
- P2 accent: bright blue ≈ #2f9dff.
- Stage: near-black #07040d → deep blue-purple #141024 radial haze at the
  bottom; red wash behind P1 art, blue wash behind P2 art; cool spotlight
  from top-center.
- Cards: very dark fill #101018, 2px rgba(255,255,255,0.16) frames.
- Names: white with a soft accent-colored glow.

## 6. Background

- Dark arena void: vignette + blue/purple floor haze + a top-center
  spotlight bloom. No busy scenery — the fighters ARE the scenery.
- Our recreation: layered CSS radial/linear gradients (no image), plus the
  per-side portrait art wash (our own portraits, huge, faded, masked).

## 7. Animations / transitions

- Idle "personal acts": every highlighted fighter plays a looping
  personality idle on the big model (T8). Ours: the validated T3 teardown
  stance clip where the bank fits the rig, else the GLB's own idle, else a
  slow turntable — live 3D, never a still (owner law).
- Cursor move: quick frame-glow shift (we do a 0.12s scale/glow transition
  + the T3 aperture rule: the cursor card renders larger than neighbors).
- Tap/select: brief brightness flash on the tapped card (our `tap-flash`).
- Attire switch: the big model swaps LIVE on the select screen (T8
  "customized slots" → our attire chips + P/K buttons).
- Confirm: lock badge + card tag; versus hands the cursor to P2 (T8
  two-cursor flow).

## 8. What we changed vs. T8 (documented deviations)

1. Tier dividers (TRIPO ORIGINALS / THE NINE SOULS / MAIN ROSTER / BONUS
   ROSTER): T8 has none. Ours keep the owner's DISPLAY ORDER LAW visible
   (Tripo-first). Slim full-width labels, not cards.
2. Names on cards: T8 cards are face-only. Ours keep the small name strip
   per the 2026-10-18 owner spec (names on cards killed the "no names"
   embarrassment; the directive was never revoked).
3. Fact block rows: T8 = Fighting Style / Nationality / Height / Weight.
   Ours = FIGHTING STYLE (style) / ARCHETYPE / ORIGIN ("Parts unknown"
   canon fallback) — height/weight are NOT shown because we have no
   measured data and never invent it. The POW/SPD/JMP/DEF mini-bars are
   kept underneath (our game's real numbers, owner-spec stats).
4. Hints bar keeps our functional P/K attire buttons (owner's classic
   Tekken-1 scheme) styled as prompt chips; T8's ▢ maps to our attire
   chips on the plate.
5. 99s timer kept (Tekken standard selector / owner spec), not T8's.
6. Phone layout: T8 is a landscape console screen; ours stacks
   stage → grid (own scroll box) → hints on portrait phones, and floats
   the grid over the stage only on ≥900px widths.

## 9. Skin-swap layer

All of §2–§7's visual tokens live in `game/js/ui-skin.js` (colors, fonts,
card geometry, fact rows, texture paths). select-screen.js reads them via
`getSkin()`/`applySkin()`; select.css consumes only the resulting CSS vars.
The drop-in contract (new skins, texture naming, copyright rule) is
documented at the top of ui-skin.js. Changing the look never touches the
screen logic.
