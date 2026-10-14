# docs/t7t8-reference
Owner-approved (Oct 14 2026): Tekken 7/8 public data is the WH baseline (heights from PR #120).
- `heights_check.md` - #120 heights vs T7 and T8 public sources, mismatches flagged.
- `frame-data/<body>.json` - T8 frame data/move lists from wavu.wiki (CC0). Schema: id,name,input,parent,target,damage,startup,recv,tot,crush,block,hit,ch. Refresh: `python3 tools/fetch_wavu_framedata.py King Jin ...`
- `wh_body_map.json` - WH fighter -> body, heights, frame-data file. Move-set editor / frame-data systems read this.
- `stages.md`, `roster.md`, `REFERENCE_SOURCES.md`.
WH move names/inputs must be re-authored on top of this data before sale; never show Tekken names on screen.
