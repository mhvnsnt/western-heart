# Community pull — handoff notes (add to TASKBOARD.md / CLAIMS.md once #850 merges)

- **Fight / moveset executor:** `tekken8/movesets/kaiutzi21/t8_LEE_v2/t8_LEE.summary.json` (Purple Rain), `t8_LAW` (Buffalo Bill), `t8_KING_v2` + `t8_ARMOR_KING` (King-based fighters), `t8_PAUL`. Each summary = per-move hitlevel, active frames, airborne window, cancel index. Full data in the `.json.gz` (cancels, input_sequences, throws). Regenerate with `summarize.py`. For Bob/Alisa use `tekken7/framedata/rbnorway/csv/{Bob,Alisa}`.
- **Character select / HUD executor:** HUD + announcer ZIPs and T8 artwork are catalogued in `docs/tech/COMMUNITY-SOURCES.md` #3-#6. They need a browser download (Cloudflare).
- **Stages / menus executor:** nothing new this batch.
