# Tekken 8 — Character Select teardown (decode)

Sources: owner reference captures of the Tekken 8 select screen
(`refs/t8-select-ref-1..3.png`, supplied by the owner, t133u, 2026-10-23) and
`docs/select-redesign/T8-GRID-DECODE.md`.

| # | T8 element | Decode | WH implementation |
|---|---|---|---|
| 1 | Stage | Full-bleed dark stage, red wash left (P1), blue wash right (P2), cool light from top centre | `game/select-t8.css` `#screen-select.t8` background |
| 2 | Fighters | Large 3D model per side in its idle fight stance, P1 left facing right, P2 right facing left; faded portrait art behind | `.side-pane` 50% halves, `PreviewPane` (bank stance), `.pane-artwash` |
| 3 | Name | Huge italic condensed uppercase at the outer edge, glow in player colour | `.pane-name` |
| 4 | Facts | Small coloured label chips **Fighting Style / Nationality / Height / Weight**, white value under each; T8 prints "Unknown" for unset facts | `.pane-facts` (`renderPlate`) |
| 5 | Grid | Compact centred block of small square face cards, no names, ~12 per row; P1 cursor red `#ff2d55`, P2 cursor blue `#2f9dff` | `#char-grid` single grid, `.char-card` 1:1 |
| 6 | Random | Black card with white "?" inside the grid (bottom row) | `.random-card` inserted in the last row |
| 7 | Hints | Bottom-left glyph hints "✕ Confirm  ◯ Back  ▢ Customized Slots" | `.hints-bar` buttons (≥44 px touch) |
| 8 | Timer | Countdown top centre, no screen title | `.select-timer`; header title hidden |

Phone portrait (not in T8): stage stacked over grid, 8 columns — taken from the
owner's Brutal Fist select (`mhvnsnt/Brutal-Fist` `src/components/CharacterSelect.tsx`,
57% P1|P2 stage over square-card grid). AshLane (`mhvnsnt/AshLanev2`) has no select
code; only its concept art `public/concept-art/menu/menu-character-select.webp` was consulted.
