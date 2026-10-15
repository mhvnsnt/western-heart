# T7/T8 reference sources (links + license notes)

Free PUBLIC frame data, move lists, combo guides, stage layouts.

- **CC0 / public-domain:** copied into this directory.
- **Non-CC0 / unverified license:** links only below. Do NOT paste copyrighted text or tables wholesale.
- Combo guides: link + short summary of useful routes; no full copyrighted guide text.
- Stage layouts: dimensions, hazards, camera notes as structured JSON/MD authored
  from public facts, with source links.

| Source | URL | License | Covers | In git? |
|---|---|---|---|---|
| heights_check.md (existing) | ./heights_check.md | authored from public facts | T7/T8 fighter heights | yes |
| Wavu Wiki (Tekken) | https://wavu.wiki/ | unverified (community wiki, likely CC-BY-SA) | T7/T8 frame data, movelists, combos, punishers | links only |
| Wavu King T7 | https://wavu.wiki/t/King_(Tekken_7) | see above | King movelist + frames | summarized in frame-data/king-pantera.json |
| Wavu Jin T7 | https://wavu.wiki/t/Jin_(Tekken_7) | see above | Jin movelist + frames | summarized in frame-data/jin-demonio.json |
| Wavu Yoshimitsu T7 | https://wavu.wiki/t/Yoshimitsu_(Tekken_7) | see above | Yoshimitsu movelist + frames | summarized in frame-data/yoshimitsu-phantom.json |
| Wavu Bryan T7 | https://wavu.wiki/t/Bryan_(Tekken_7) | see above | Bryan movelist + frames | summarized in frame-data/bryan-skull.json |

## Frame data files

`frame-data/*.json` — key moves authored from public frame-data facts (numbers are
facts, not copied tables). Each file maps Tekken moves to WH move slots.

## Adding fighters

Keep `wh_body_map.json` in sync when you add fighters (see `docs/t7t8-reference/`).
