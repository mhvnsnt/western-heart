# Decision log — Cape Jones arenas (2026-10-24)

Owner directives 2026-10-24 20:35 + 20:38 CDT; coordinator confirmations
2026-10-24 20:42–20:52 CDT (Lane 5 base, stage-id confirmation, GAME
FIRST scope law). This log records what was built, what was verified by
code/tests, and what is explicitly NOT claimed.

## Built (this PR, base = main, no Lane 5 files)

- `game/js/stages.js` (surgical): two defs (`cape-jones-arena`,
  `cape-jones-halloween-beach`), tier `CAPE JONES` in STAGE_TIERS,
  builders `capehouse` + `capebeach` registered in BUILDERS. No
  `main.js` change: stage select iterates STAGE_TIERS already.
- `game/netlify.toml` + `game/_redirects` (mirrored pair): `/stages/*`
  200 proxy, preventive for the future `stages/cape-house/living-room.glb`.
- `test/cape-arenas.test.mjs`: 10 tests over the defs + Netlify pair.
- `docs/arenas/cape-jones-arenas.md`: full design doc (spec, asset
  status, music coordination, Netlify, GPU pack, playtest steps).
- `docs/arenas/cape-jones-show-locations.md`: show-location log (doc
  note only, per the GAME FIRST scope law).
- `tools/cape-arenas-gpu/`: run sheet + `cape-gpu-jobs.py` (prepared,
  not run — no cape inputs exist yet).

## Verified by code/tests (this lane)

- `node --check` passes on the edited `stages.js` (ESM parse).
- `node --test test/cape-arenas.test.mjs` — see WORKLOG for the run
  output (run against a work-tree layout mirroring the repo).
- Stage ids match music-wiring PR #1072 exactly: house
  `cape-jones-arena` (PR #1037 tag, kept), beach
  `cape-jones-halloween-beach` (PR #1072's new-track tag). Verified by
  reading #1072's file patch via the GitHub API: its 8 new tracks carry
  both tags; its patch does NOT touch the original 8 Cape tracks.
- Main's `game/assets/music/` holds no `cape-jones-*.mp3` (verified via
  the contents API) and main's `music-library.json` holds no cape-tagged
  tracks — so no Ghost Surf Rock audibility is claimed for v1.
- Netlify files on main match the checkout copies byte-for-byte before
  editing (verified via the contents API), so the proxy edit is clean.

## Explicitly NOT verified / NOT claimed

- Live play (menu → select → stage → FIGHT on each arena, phone
  portrait, VIDEO proof): delegated to the coordinator's browser lane
  with exact steps in the design doc. Not run by this lane (no live
  browser). Never claim fight-load works before that check.
- Ghost Surf Rock audible on either arena: depends on the audio lane's
  MP3 downloads + tags (see design doc § music coordination). The
  engine falls back to the procedural loop until MP3s land.
- Real GLB assets (house export, beach pack): pending, with exact
  unblock paths in the design doc. The v1 builders are playable sets in
  the canon-stage style, NOT presented as shipped real assets.
- GPU jobs: prepared only. No nvidia-smi / torch.cuda proof, no wall
  times, no CPU baselines exist for cape inputs yet — the script records
  all of them at run time. Nothing is measured here because there is
  nothing to measure yet.
- Lane 5 merge order: this PR is independent of open PR #1061. If #1061
  merges first, the deploy lane's 3-way merge reconciles `stages.js`
  (preload code vs these defs/builders); the defs declare no
  breakables, so the generic stage-levels treatment applies either way.

## Decisions

- Beach id `cape-jones-halloween-beach` confirmed verbatim (matches
  #1072; no retag needed). Tagging the original 8 Cape tracks stays
  with the audio lane — this lane does not touch
  `game/data/music-library.json` (would collide with open #1072/#1058).
- Fight bounds stay at WH standard (16.8 / 8.4 / ±3.5) for both arenas,
  with the house-reading caveat recorded in the design doc for owner
  correction (canon room scale 7.0 x 6.0 m is show-room scale).
- Beach sky stops/fog/grade are exact-match tested = color-locked.
- No thumb atlas tiles in this PR (swatch fallback renders today);
  tiles are a follow-up render job, not a blocker for playability.
