# Kaggle GPU preload lane — decision log (2026-10-24)

Owner instruction (verbatim, 2026-10-24 19:47 CDT): "find a way to hook
up the Kaggle GPU inside the repo to the full game so everything loads
faster so we get faster loading screens so the character cards are all
preloaded on the character select screen when you select them so you
don't have to wait for things to render or for anything 3D or 2D to load
or render so we can speed up the loading speeds and times and also any
other way that you can use the GPU or anything else that you can find
and pull in and wire up".

## What was actually wrong (measured from repo files, not guessed)

1. **Cards used `loading="lazy"`** (`game/js/select-screen.js`,
   `portraitHTML`): each card image fetched only when scrolled into
   view. Tapping a fighter could therefore wait on a fresh image fetch.
2. **Preview loaded a full GLB per tap** (`PreviewPane.show` →
   `assets.loadModels([modelId])`): a ~20–30MB model download + parse
   stood between a tap and a visible preview, with no placeholder
   shown during that wait (the portrait fallback only appeared on
   failure or on no-WebGL).
3. **Only Pantera + Demonio warmed at idle**
   (`assets.preloadBaseIdle`): every other fighter's first preview
   started cold. The old `preloadAll()` (four base GLBs, ~26MB, the
   instant select opened) had been deliberately removed by the
   loadspeed lane because it saturated the pipe the first preview
   tap needed — so bulk-warming GLBs is the wrong fix, and this lane
   does not bring it back.

## What this lane does (and does not do)

**Runtime (`game/js/preload.js`, wired into select-screen + main):**

- `warmSelect()` on select show (after paint): preloads **every
  select card image** (2D, small) via `Image` cache, so any tap shows
  its card from cache. It takes the live select roster
  (`selectRoster()`), never a hardcoded count: `roster-full.js` holds
  59 entries, select hides 10 soul/duplicate ids and filters by
  passing attire, so the warmed set is exactly the visible cards.
- `showOnSide` now shows the fighter's portrait plate **immediately**
  while the GLB streams in, and hides it only when the 3D model is
  ready (progressive loading: instant 2D, 3D fades in when ready).
- `warmFight()` on lock (select confirm) and again on stage show:
  prefetches the locked fighters' GLBs through the existing
  `assets.prefetch` (deduped, user-lane, abort-safe) so stage-screen
  dwell warms the fight. Non-versus random opponents cannot be warmed
  (the enemy is picked at fight time) — that limit is stated, not hidden.
- `loading="lazy"` on the DOM card images is kept: the preload warms
  the browser cache, so the lazy images resolve from cache instantly,
  while first paint is not blocked by 50 eager image fetches.
- Loadperf marks `cards-preloaded` / `fight-warmed` + the
  `window.__whCardsPreloaded` record exist so a live playtest can
  report real before/after timings. No browser millisecond numbers
  are claimed in this PR — live Netlify timing needs a live-browser
  playtest, which this lane cannot do from a VM.

**Build-time (`tools/kaggle-gpu-pipeline/`):**

- `kaggle_card_factory.py` + README: the repeatable Kaggle GPU job
  (pre-rendered cards, gltfpack optimization, WebP textures, LODs for
  non-skinned meshes, manifest + size report, GPU proof that fails
  loudly without CUDA). See the README for the honest architecture:
  Kaggle GPU is a build-time factory whose outputs ship in the repo;
  it is **not** a live accelerator for the phone game, and this PR
  claims nothing of the sort.
- No rendered cards ship in this PR: renders need a Blender GPU run
  on the Kaggle notebook (browser delegation). Pending-render rows
  write no placeholder images. The runtime preload works today on
  the existing portraits; factory cards swap in later in one PR.

**Explicitly out of scope here (other lanes own them, no clobber):**

- Creation-suite fixes (Mixamo removal, real templates, sub-menus,
  MPFB, morphing/swapping, blank-CAW fix, fighter-select taps) — the
  creation-suite lane owns those files; this PR touches only
  `game/js/preload.js` (new), `game/tests/preload.test.mjs` (new),
  `tools/kaggle-gpu-pipeline/` (new), this decision doc (new), and
  surgical hooks in `game/js/select-screen.js` + `game/js/main.js`.
- Tekken OST / Nosferatu track downloads and the Kaggle GPU cut job
  (music lane, PR #1030, still open at time of writing).

## Verification in this PR

- `node --test game/tests/preload.test.mjs`: 6/6 pass (card URL,
  always-resolve on missing portraits, dedup + free second warm,
  warmSelect result, warmFight exact-id prefetch, wiring guard
  asserting select-screen + main actually call the new hooks).
- Surgical-edit proof: every edit anchor asserted exactly once
  before replacement (script aborts on any other count); the
  select-screen diff is import + placeholder + lock warm + show warm
  + `warmLockedFighters`, and the main diff is one guarded stage
  block. No other behaviour changed.
- Still owed (not claimed done): live-browser playtest on Netlify
  reporting `window.__whCardsPreloaded`, loadperf transitions, and
  FIGHT time before/after; the Kaggle Blender render run; the
  full main→gh-pages sync so Netlify picks this up.
