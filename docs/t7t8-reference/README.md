# docs/t7t8-reference
Owner-approved (Oct 14 2026): Tekken 7/8 public data is the WH baseline (heights from PR #120).
- `heights_check.md` - #120 heights vs T7 and T8 public sources, mismatches flagged.
- `frame-data/<body>.json` - T8 frame data/move lists from wavu.wiki (CC0). Schema: id,name,input,parent,target,damage,startup,recv,tot,crush,block,hit,ch. Refresh: `python3 tools/fetch_wavu_framedata.py King Jin ...`
- `frame-data-t8-full/<body>.json` - (2026-10-21) ALL 41 T8 characters from wavu.wiki (CC0), 6,284 moves, extra fields alias/alt/reach/tracksLeft/tracksRight/notes. `python3 tools/fetch_wavu_framedata.py --full --all --out docs/t7t8-reference/frame-data-t8-full`. The Oct 14 `frame-data/` files are left byte-identical.
- `frame-data-t7/<label>.json` - (2026-10-21) Tekken 7 frame data, 47 characters / 11,137 rows, t7chicken (dayhaysoos/t7chickenplus-graphql @ 91a054e8, ISC, TekkenBot-extracted), SHA-256 per file in `SOURCE.json`. `python3 tools/fetch_t7chicken_framedata.py [--check]`.
- `wh_body_map.json` - WH fighter -> body, heights, frame-data file. Move-set editor / frame-data systems read this.
- `stages.md`, `roster.md`, `REFERENCE_SOURCES.md`.
WH move names/inputs must be re-authored on top of this data before sale; never show Tekken names on screen.
