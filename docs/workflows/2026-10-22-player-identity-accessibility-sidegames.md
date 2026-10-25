# WORKFLOW — Player Identity + Accessibility + Side Games (worker 35)
2026-10-22 ~13:35–14:30 CDT · branch: `identity/w35-player-identity`

## Task
Player identity (titles, customizable player cards, in-game currency, treasure
boxes/loot), accessibility (button remapping, colorblind options, difficulty
assists), and Tekken Bowl-style side games — each with WH canon mapping.
All naming/identity creative calls flagged for owner approval, nothing locked.

## Teardown pulls (grounded)
- Tekken 7 Fight Money: earned every battle win or lose, spent on customization,
  "G" economy, 5M/10M lifetime achievements (web-verified via Tekken Wiki/Fandom,
  Push Square, Steam community).
- Tekken 7 Treasure Battle: 1–3 chests/victory, bonus chest for Perfect/Great/
  Double-KO, rarities Bronze/Ruby < Silver/Emerald < Gold < Rainbow, Special
  Matches drop Gold/Rainbow, chest-only items never in shop.
- Tekken 7 titles: unlockable, shown on player info/versus.
- SFV Fighter Profile: name/title/comment/favorite/stats/custom background.
- SF6 Modern (one-button specials, auto-combos) + Dynamic controls.
- Modern fighters (SF6/GGST): player-pickable colorblind-safe UI palettes.
- In-repo teardowns are models/movesets/arenas-heavy; these systems were
  grounded via web search per skill instructions.

## Method
- Fresh main SHA via github_api.py at start (be7d2eda). Full `cp -r` of the repo
  FAILED (sandbox write limits on large files) — worked around it: all new files
  written via muse.write into ~/workspace/fix3/identity/ mirroring repo paths.
- Staleness check per edited file via git blob SHA vs main: input.js MATCHED main
  (safe to edit); index.html was STALE → fetched exact current content via the
  Git Database API (blob 6a179f83) and reproduced it verbatim + surgical additions.
  game.js/fighter.js/modes.js were stale → NOT touched (damage assists ship as
  live multiplier + specified hook for the combat worker).
- WORKLOG.md (125KB, high-churn shared file) not round-tripped; logged here per
  AGENTS.md ("WORKLOG.md or docs/workflows/") to avoid append-conflict clobber risk.

## Files (no deletions)
- game/js/identity.js (NEW, 18KB): profile core — titles, cards, currency, loot,
  remap tables, colorblind presets, assists; awardMatch/openCache economy.
- game/js/wh-boot.js (NEW): boot wiring — colorblind class, touch remap, result
  observer (currency+cache awards, title checks), HUD nameplate card paint.
- game/identity.html (NEW): player hub — name, titles, card editor w/ live SVG
  preview (seigaiha/asanoha/shippo/mandala/ichimatsu), shard ledger, Soul Caches.
- game/settings.html (NEW): keyboard remap UI, touch-button layout, 5 colorblind
  presets, 5 assists (3 input-wired, 2 via live multiplier + hook spec).
- game/side-games.html (NEW): 12 mythology concepts (myth root + WH identity +
  how it plays + home) + 2 playable prototypes (Soul-Fruit Harvest canvas game,
  Trader's Chō-han dice).
- game/css/identity.css (NEW), game/css/colorblind.css (NEW).
- game/index.html (MODIFIED, surgical): 3 menu links (IDENTITY/SIDE GAMES/ACCESS &
  ASSISTS), colorblind.css link, identity.js + wh-boot.js scripts.
- game/js/input.js (MODIFIED, surgical): _remapCode(), remap-aware keyup,
  _physicalCode(), WHAssists hooks in _push.
- docs/identity/IDENTITY-CANON-MAPPING.md (NEW): per-system canon mapping +
  approval flags.
- docs/workflows/2026-10-22-player-identity-accessibility-sidegames.md (this file).

## Canon mappings proposed (ALL need owner approval)
- Currency: "Soul Shards" (shipped) / "Trader's Coin" / "Death Tithe"
- Loot: "Soul Caches" (shipped) / "Shrine Offerings" / "Trader's Stashes"
- Titles: 16-title Trial/Nine-Soul list (proposed)
- Side games: 12 concepts — Soul-Fruit Harvest, Trader's Chō-han (playable),
  Daruma Drop, Koi-Scooping, Oni Hunt, Hyakumonogatari, Eyeball Auction,
  The Nine Trials, Scimitar's Ledger, Kagome Circle, Soul Karuta, Kemari of
  the Nine. Suggested first full builds: Daruma Drop + Oni Hunt.
- Assists philosophy: damage sliders honest-help vs too-much (owner call).

## Verification
- node --check on all JS (identity.js, wh-boot.js, input.js): PASS (see below).
- Headless Chromium screenshots of identity.html, settings.html, side-games.html:
  rendered, viewed (proof attached to PR).
- Anti-clobber: deletion-guard — gh_push.py refuses deletions; change set is
  8 new files + 2 surgical modifies; no other files touched.

## Flags for coordinator
- Damage-scaling assists need the 4-line hook in game.js (specified in the
  canon-mapping doc) — combat worker's lane.
- Elemental-bearer titles + "Whole" are manual unlocks — story/mode worker should
  call WHIdentity.unlock(id) at the claim moments.
- Rename of currency/loot = one constant each in game/js/identity.js once the
  owner picks.
