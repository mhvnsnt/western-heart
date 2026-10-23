# Tekken 7 — Character Select: layout source record (teardown lane)

Owner law: no hand-made menus. This file is the teardown lane's source record
for the T7 character-select layout that Western Heart's select screen is
rebuilt from. The full decode lives at
`docs/select-redesign/T7-GRID-DECODE.md`; this file exists so the
`ui-sources` gate has a machine-checkable `teardown/` citation.

## Status

T7 UI asset extraction has NOT landed (no T7 select-screen textures, fonts,
or layout binaries in this repo — owner rule 8: no ripped Tekken UI in public
repos). The in-game select screen is therefore a clean-room CSS recreation of
the layout recorded here. When the T7 UI extraction lands, its assets drop
into the same structure with no restructuring (the `t8` ui-skin entry is the
same mechanism for T8 art).

## Sources (public visual references — surveyed, not committed)

1. T7 versus character select, public screenshots and footage (tekkenzone.net,
   eventhubs.com T7 coverage, Bandai Namco press kit): header, 2-row portrait
   grid, flanking P1/P2 renders, red/blue cursors, "?" random panel, hints
   bar, 99-second timer, stage-select strip.
2. Tekken 7 Xbox One/PS4 manual conventions: punch button = costume 1, kick
   button = costume 2 on the select screen; the 99-second selector timer;
   timeout locks the highlighted fighter (the timer never leaves a side
   unpicked).
3. TTT2 (gamesdb/launchbox write-ups; TTT PS2 manual via archive.org): the
   two-cursor flow (P1 cursor + P2 cursor over the portrait field) and the "?"
   convention.
4. T6 (neogaf.com T6 thread, 2009): "?" random slots at the ends of the
   portrait row.

## Layout elements (what the rebuild implements)

- `screen-select`: "CHOOSE YOUR FIGHTER" header + 99s timer; 2-row portrait
  grid, column-major, horizontal scroll in its own box; P1 red / P2 blue
  cursors with 1P/2P tags; "?" random panel at the grid end; tap-card =
  preview, tap-highlighted-card = lock; P/K on-screen attire presets;
  announcer cues (choose-your-fighter on entry, fighter name shout on lock).
- `screen-stage`: "CHOOSE YOUR STAGE" header; big preview pane + name banner;
  one horizontal stage strip; "?" random card in-flow; announcer cues
  (choose-your-stage, stage-name callouts on highlight).
