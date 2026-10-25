# Fight load fails at ~6% on Netlify, kicks back to stage select — diagnosis + fix (2026-10-24)

## Owner report (verbatim, 2026-10-24 18:14 CDT)

> "I picked my character. I got to the character select screen. I got past
> all the options. I got to stage select. I selected the stage and then when
> I hit fight, it went to the loading screen. It loaded to about 6% and then
> it kicked me back out to the stage select screen and it did that a couple
> times."

Menu navigation (PR #1018) works — the user reached character select and
stage select. The new blocker is fight loading only.

## Root cause: every roster/ fighter model 404s on Netlify

- The Netlify site publishes `game/` as its root
  (`https://endearing-scone-b3d816.netlify.app/`).
- Fighter models are NOT all under `game/assets/models/`. `MODEL_URLS` in
  `game/js/assets.js` points most fighters' default models at
  `../roster/<fighter>/attires/.../*.glb` — i.e. repo-root `roster/`,
  outside `game/`.
- `fetch()` resolves relative to the page, so on Netlify `../roster/...`
  becomes `/roster/...`, which does not exist in the game-only publish dir.
- `game/netlify.toml` (PR #1018) proxied `/customization/*`, `/packages/*`
  and `/game/*` to gh-pages, but NOT `/roster/*`. So every roster-model
  fetch 404s: `_loadOne` throws `HTTP 404 loading <id>`, retries once,
  throws again, `loadModels` rejects, `startFight`'s load catch returns
  `false`.
- This is deterministic, not flaky: retrying the same fight fails the same
  way ("it did that a couple times"). It is also Netlify-only: on GitHub
  Pages the game lives under `/western-heart/game/` and `roster/` is
  deployed alongside it, so the same paths resolve — matching the user's
  report that the GitHub version did not do this.

Verified on gh-pages (branch `gh-pages`, head `09ec3660` at diagnosis time),
not guessed:

- `roster/` exists on gh-pages (71 entries).
- All 7 sampled default-model GLBs exist there with real sizes:
  `diablo/attires/attire1/model-rigged.glb` (22,100,148 bytes),
  `phantom/attires/attire1/model-rerig.glb` (29,340,456),
  `zen/attires/attire1/model-rigged.glb` (29,237,496),
  `skull/attires/attire1/model-rerig.glb` (33,398,296),
  `sam-ur-a1/attires/attire1/model-rerig.glb` (30,667,524),
  `sakura/attires/attire1/model-rerig.glb` (28,382,684),
  `zui/attires/attire1/model-rigged.glb` (31,930,816).
  A `/roster/*` proxy to gh-pages therefore resolves them; no model files
  need to be pulled or moved for this fix.
- Default-model mapping (from `game/js/roster-full.js` + `MODEL_URLS`):
  Pantera is the exception (`assets/models/pantera.glb`, inside `game/`);
  Phantom, Diablo, Skull, Sam-ur-a1, Saku-ra, Zui, Zen and most of the
  roster default to `roster/` paths. The random P2 opponent makes even a
  Pantera pick fail unless the opponent also happens to be an
  `assets/`-only model. So effectively all versus fights fail on Netlify
  without the proxy.

What is NOT the cause (checked, not assumed):

- Stage geometry: `game/js/stages.js` fetches `assets/stages/...` (inside
  `game/`) and `Arena.setStage` catches build failures internally — a stage
  failure logs but cannot throw `startMatch`.
- Movesets: `assets/movesets/` (inside `game/`).
- T3 animation banks: `assets/anim/t3/` (inside `game/`; a previous
  `../assets` 404 bug there was already fixed by moving them under
  `game/assets/`).
- The random-opponent path, transform targets and form targets in
  `startFight` all funnel through the same `loadModels` call, so the same
  proxy fixes them too.

## Why "about 6%" — the bar math, not the failure point

`game/js/load-progress.js` maps model bytes to 5%..85% and creeps toward
`real + 0.06` when no bytes arrive. A fast 404 produces zero byte
progress, so `real` stays 0 and the creep cap sits at ~6%. The same 6%
stall appears when models are already cached (prefetch) and the load is
in the moveset/T3/`startMatch` phases. 6% therefore means "no model
bytes yet", not "failed at 6% of the work" — the failure itself is the
roster 404 above. After the proxy fix, model bytes flow and the bar
moves past 6%.

## How games deal with loading failures (pattern this fix follows)

From this repo's own teardown lessons, not invented:

- Tekken 3 lesson (already in the code): load on demand per fight from an
  index, never the whole roster at boot (`game/js/lazy.js`).
- Retry once (`assets.js` `_loadOne`: one retry, aborts never retry).
- Fall back, never hard-fail, where a fallback exists: stage panoramas
  fall back to palette tint when an atlas fails (`stages.js`); T3 clips
  fall back to procedural combat (`main.js`); model-pending fighters swap
  to the first ready fighter (`main.js` `startFight`).
- What was MISSING and this fix adds: a specific, visible error plus a
  working retry. Previously a fight-load failure showed the generic
  "Failed to load fighters. Check connection and try again.", kept the
  loading overlay up (only its 45s safety timer or a `startMatch`
  wrapper hid it), and never named the asset — so a host-only 404
  looked like a mystery 6% kick-back. Now the stage hint names the
  failing asset and message (e.g. `HTTP 404 loading diablo`), the
  overlay hides immediately, and CONFIRM retries the same fight
  (`pendingFight` is kept on failure, as before).

## Fix (this PR, one pass)

1. `game/_redirects` (new): publish-dir redirect file — the mechanism
   Netlify documents for redirects/rewrites when the publish directory
   differs from the base. Proxies `/roster/*`, `/customization/*`,
   `/packages/*`, `/game/*` to gh-pages with status 200 (`:splat`).
   Publish-dir files always win; only missing paths fall through.
2. `game/netlify.toml` (updated): same four rules as `[[redirects]]`,
   adding `/roster/*` to the three PR #1018 rules. Kept in sync with
   `game/_redirects`; whichever mechanism Netlify applies, the rules
   agree.
3. `game/js/main.js` (`startFight`, surgical only):
   - Load phases mirrored to the stage hint (the visible hint in versus
     flow), and the model id is shown during model byte progress, so a
     stall says WHERE it stalled.
   - Load-failure catch: hides the loading overlay immediately and
     shows `Failed to load fighters: <detail> — tap CONFIRM to retry.`
     on both hints.
   - `startMatch` catch: same treatment
     (`Failed to start the fight: <detail> — ...`), overlay hidden,
     back to stage select for retry.
   - No change to load order, timeouts, retry policy, or any fighter,
     stage, moveset, or animation data. No deletions.

## gh-pages-only companion file (not in this PR's main-branch diff)

`netlify.toml` at the gh-pages ROOT is added directly to `gh-pages`
after this PR merges and deploys (same pattern as the existing
gh-pages-only `.nojekyll` and root `index.html`). Reason:
`tools/deploy/build_pages.py` builds gh-pages from `main` by roots
(`game/`, `customization/...`, `packages/...`) plus a reference closure
over runtime extensions — a root `.toml` is neither under a root nor in
the closure extension set, so it would not be copied from `main`.
`build_pages.py` never deletes, so the gh-pages-only root file persists
across later deploys. Primary mechanism remains `game/_redirects`;
the root file is belt-and-braces for base-directory config reading.

## What this does NOT claim

- Live touch play-testing on Netlify was not done by this lane (subagents
  cannot run the live browser). CI checks plus the gh-pages blob
  verification are the proof here; the owner playing on Netlify is the
  final step.
- Two fighters at 22–33 MB each means a first fight load is 44–66 MB
  before any caching. That is slow on cellular but is not this failure;
  it is noted, not changed, here.
- Fighters whose models are quarantined by the material gate, or whose
  GLBs are missing from gh-pages entirely, would still fail — but now
  the stage hint will NAME the file, instead of failing silently. No
  such missing-default case was found in the 7 sampled defaults above.

## Verification owed (parent browser task)

1. Confirm the Netlify deploy for the new gh-pages commit succeeded.
2. Play the Netlify build phone-portrait with touch taps: Versus →
   pick a roster-model fighter (e.g. Diablo, Phantom, Zen) → stage
   select → FIGHT → must reach the fight (not kick back to stage
   select, not stall at 6%).
3. Control: Pantera (assets-model) fight must also load.
4. If anything still fails, the stage hint now names the asset — report
   that exact text back instead of a percentage.
