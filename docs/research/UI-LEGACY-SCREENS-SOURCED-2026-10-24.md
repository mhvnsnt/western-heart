# 7 legacy-unsourced screens: sourced (2026-10-24, UI follow-up lane)

## Rule applied

Menus from teardowns only. A screen is marked `sourced` here only if
its structure matches a teardown file that exists on main, or if its
markup was restructured in this PR to the closest teardown-based
structure (with the restructure in the diff, not just claimed). The
ui-sources gate (`tools/ui-sources/check.py`) only validates screens
whose section markup changed or whose listed files changed — but every
entry below uses main-existing teardown paths regardless, so the gate
passes either way.

## Per-screen verdicts

| Screen | Before | After | Structure source (exists on main) | What changed |
|---|---|---|---|---|
| `screen-online` | legacy-unsourced placeholder | sourced | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (Base_OnlineMenu dark-glass vertical list) + the `game/js/online.js` hub template (TTT2-style quick match, SFV battle lounge — lineage per gap doc + template labels) | Section restructured: the placeholder shadowed the online.js hub template (`buildOnlineScreens` early-returns when the section exists) and lacked the `#online-player-line` / `#online-event` ids the hub fills, so the hub could never open. The section now carries the hub's own rows (QUICK MATCH / FIND LOUNGE / CREATE LOUNGE / TOURNAMENT / DAILY CHALLENGES / BACK) routed through the existing document-level online actions. Netcode honestly pending (signaling server hint kept). Connection bars NOT claimed (online lane). |
| `screen-collection` | legacy-unsourced placeholder | sourced | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (main-menu column system); component organization per T7 Collection (Gallery / Jukebox / Replays — gap doc Gaps 11/12/20) | Section restructured from blurb to a hub listing: the three components as static rows (NOT fake buttons) + a hint that the live screens open from the Collection submenu + BACK. Live Gallery (Endings / Episodes / Unlocked tabs, WH content only, never Tekken FMVs), jukebox per-mode choice, and replay theater ship in PR #1056 from the Collection submenu — this lane does not duplicate them. Jukebox contract noted: UI stores per-mode choice in `wh_jukebox_v1`, engine (#1058) reads the same key; treasure choice stored but UNPLAYED (no treasure music call site — tracked gap). |
| `screen-daily` | legacy-unsourced placeholder | sourced | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (main-menu list structure); board lineage = online hub (gap doc groups daily challenges with `online.js` + netplay) | Section restructured: states the board rule (fixed fighter, fixed foe, one cruel modifier; streaks earn titles) and routes with a real action (`online-challenges`) to the live board (`online.js` screen-challenges, driven by `challenges.js`). No trial data invented, no dead end. |
| `screen-howto` | legacy-unsourced | sourced | `teardown/tekken7/tekkenmods-docs/files/en/Tekken_8/Basic_Information/Overview/Moveset/Structures/Input_Sequence/index.md` + `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` | No structural change needed (the grid was already real and complete). Notation converted to the mandated form: LP/RP → LP1/RP2, LK/RK → LK3/RK4, LP+LK → LP1+LK3, RP+RK → RP2+RK4, LP+RP → LP1+RP2, strings → LP1,RP2 / f+LP1 / d/f+RP2 / qcf+RP2. Keyboard keys (1/2/3/4) kept as key labels alongside. |
| `screen-movelist` | legacy-unsourced | sourced | Input_Sequence structures doc (above) + `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` | No structural change needed: grouped rows (input \| name \| damage) built from real fighter moveset files. This is the read view for the Create-A-Move List editor (`packages/creation-suite/src/movelist-editor.js`, PR #998 merged 2026-10-24 — LP1/RP2/LK3/RK4 throughout, context validation: jumping slots take only jumping animations, crouching only crouching, standing only standing, grapple only grapple, directional only matching direction). The editor is the write view; this screen is the read view. |
| `screen-modewin` | legacy-unsourced | sourced | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (Result_Lightning win screen) | No structural change needed: VICTORY / DEFEAT + tier / points + rank-event rows + NEXT BATTLE / RANK HALL / MAIN MENU (`game/js/ranks.js`) follows the T7 result structure. Win-screen texture verified on #863 at `teardown/tekken7-steam/pakchunk0/textures/UI_common/flash/SW_UI_Result_Lightning/Result_Lightning_02.png` (resolves on main at #863 merge; see citation doc). |
| `screen-reincarnate` | legacy-unsourced | sourced | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md` (select cards: 96x148 portrait cards) | No structural change needed: vessel cards (portrait + name + style + reincarnation reason, `game/js/modes.js`) follow the T7 select-card structure. CONTENT is Western Heart canon, not Tekken: Nine Souls death-and-rebirth (CANON.md) — no Tekken equivalent is claimed for the mechanic. |

## What was NOT done (honest boundaries)

- `screen-sidegames`, `screen-stage-intro`, `screen-trader` stay
  `legacy-unsourced`: untouched by this PR, so the gate grandfathers
  them. They are not in this lane's 7 and are not claimed sourced.
- Creation-suite menu structure stays UNSOURCED (PR #1056's honest
  gap): not restructured here, not claimed here.
- No shop screen invented (PR #1056's honest gap).
- No select-screen CSS, load order, roster, or grid changes (Lane H
  T8 spec, PR #1070): `select.css` → `select-t8.css` → `select-t7.css`
  order and the T7 structure (card 96x148, P1 cursor 208x336 red
  #e0182a, P2 cursor 208x336 blue #1a8cff, side panels 108x292,
  random 68x68, stage panel 1180x696, gradient #1b2740 → #0d1322 →
  #04060a, last-fighter/attire save) are untouched by this lane.
  Phone-portrait stacking (stage over grid, 8 columns) is the owner's
  Brutal Fist select, NOT T8 — never cited as T8 here.

## Mobile conformance (everything touched)

- Buttons: existing classes only — `.btn-primary` (~59px tall:
  16px padding + up to 22px type), `.btn-ghost` (~52px), `.wh-menu-btn`
  (64px min-height). All ≥44px (48px preferred met by wh-menu-btn
  and btn-primary). No CSS file touched, so no new gate surface.
- Routing: all new rows use `data-action` handled by existing
  document-level delegation (main.js router with touchend
  re-dispatch; online.js global actions). No hover-only controls.
- Preview: new hub rows sit in normal section flow; no modal covers
  a preview. Collection rows are static list items, not fake buttons
  — no dead ends, no fake interactivity.
- Notation: LP1/RP2/LK3/RK4 in all touched user-facing text
  (LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
  LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4).
