# Tekken 8 Customization Layout Research (STEP 1 — creation-suite-layout-fix)

Generated 2026-10-22 by overnight-idle-pipeline. **All numbers below are MEASURED
from real Tekken 8 screenshots** (own-eyes + visual-grounding bboxes), NOT from
training data. Marked `measured-reference`. T8 art files are NOT in our holdings;
nothing here is file-derived. (Note: `research.py compare` failed this run —
proxy contention, "Remote end closed connection" — so this was researched
directly via image search + own-eyes measurement instead.)

## Source A — Item screen (Character Customize / Upper body)
- Screenshot: real T8 "CHARACTER CUSTOMIZE" screen (Kazuya, Long T-Shirt grid),
  879x558, via mobiplus Tekken 8 tips ebook
  (`https://de.mobiplus.me/games/assets/ebooks/tekken8/tekken_05.jpg`,
  page `https://de.mobiplus.me/games/tips/65/tekken8`). Viewed own-eyes.
- Measured regions (normalized 0-1000):
  - Category rail (Head / Full-Face / Glasses / Entire body / Upper body /
    Lower body / Shoes / Unique): x 47-198 (**15% of width**), y 141-474
    (**33% of height**, top-aligned under title). 8 rows, active row = magenta
    underline. Narrow rail, does NOT extend full height.
  - Item grid panel ("Long T-Shirt (Fujin & Raijin)" header, 5-col thumbnail
    grid, "35/53" page indicator bottom-right): x 227-553 (**33% of width**),
    y 96-885 (**79% of height**).
  - Fighter preview (Kazuya): x 628-995 (**37% of width**), y 2-1000 (full
    height, head at top edge to below knees). **Zero overlap with panels** —
    panels end x=553, fighter starts x=628 (clear gutter).
- Combined: UI panels occupy left ~55-60% of the 16:9 frame; fighter owns the
  right ~40% and is ALWAYS fully in frame.

## Source B — Adjust screen (accessory "Ball" placement sliders)
- Screenshot: real T8 accessory adjust screen (Xiaoyu, slider list), 1280x720,
  via tekken8combo customization guide
  (`https://tekken8combo.kagewebsite.com/tpl/img/customization/customization-1274/image-1274_2.jpg`).
  Viewed own-eyes.
- Measured regions (normalized 0-1000):
  - Slot selector (slots 1/2 mini-panel): x 63-195 (**13% wide**), y 185-290.
  - Adjust panel (header "Ball" + Confirm button + 9 sliders: Equip Location,
    Overall Size, Front/Back Width, Move Up/Down, Move Left/Right,
    Move Back/Front, Rotate Up/Down, Rotate Left/Right, Tilt): x 220-508
    (**29% of width**), y 102-827 (**73% of height**). Single column, no
    scrolling visible.
  - Fighter (Xiaoyu, head to feet): x 589-783 (**19% wide**), y 129-927
    (**80% of height, head AND feet in frame**). Fully visible on the adjust
    screen — the exact screen our v2 proof broke.
  - Bottom control hint bar (Confirm / Back / L2R2 Zoom / Move Camera /
    R Rotate Camera): x 46-456, y 945-972 — a thin strip, **~3% of height**,
    bottom-anchored, never covers the fighter.
  - "Fight Money" readout bottom-right.

## Derived layout rules for our ui2 rebuild (portrait-first 390x844)
1. **Fighter fully visible on EVERY screen** — item, try-on, adjust, morph,
   drill-down, wardrobe, conflict, fighters. In T8 the fighter is never
   occluded by panels on any screen type. Sliver = fail.
2. **Panels dock in a bounded zone sized from the research**: on 16:9 T8 the
   widest panel zone is ~55-60% of frame width. For portrait 390x844 this
   translates to: panels as a bottom sheet / compact dock occupying at most
   ~55-60% of the vertical space, OR a narrow side rail + panel column —
   never covering the fighter's body.
3. **Bottom bar is a thin strip** (~3-4% of height), bottom-anchored, hints only.
4. **Category rail is narrow** (~13-15% of width) and short (~33% of height),
   top-aligned — not a full-height sidebar.
5. Fighter placement: right side on landscape; on portrait, fighter centered/
   upper with panels docked below — camera framing keeps head-to-feet in frame
   (T8 adjust screen shows the FULL body while sliders are edited).

## What this does NOT cover (honest gaps)
- T8 file-derived measurements (we have no T8 art files; never claim them).
- The morph / conflict / wardrobe screens were not screenshotted here; the
  rules above generalize from item + adjust, the two screens the owner flagged.
- Portrait-mode T8 references: T8 is landscape-first; the portrait translation
  in rule 2/5 is derived, marked as such.

## Next (STEP 2, for the lane)
- Finish the sparse checkout of `packages/creation-suite/ui2` (+ theme) into
  `~/workspace/_csui-layout-work/repo` (previous attempts died mid-setup;
  network is proxy-contended tonight — retry when quiet, or reuse the
  `_csui-v2-work` checkout if it fits).
- Apply the rules above to EVERY screen (root, items, try-on, adjust, morph,
  drill-down, wardrobe, conflict, fighters); data layer intact; theme.json +
  t7DropIn keep working.
- Land this research as `docs/CREATION-SUITE-T8-LAYOUT-RESEARCH-2026-10-21.md`
  in the repo (RESEARCH-TO-REPO law).
