# Republish the deployable build — the one path

Owner order (2026-10-30): "make sure every single thing you do is going up on
the deployable build so I can test it and play it." Every finished piece is
not done until it is on BOTH deployable surfaces below, verified live.

Surfaces:

| Surface | Where | Served from |
|---|---|---|
| GitHub Pages (playable in browser) | https://mhvnsnt.github.io/western-heart/ | branch `gh-pages-m1-20261029` (Pages source, legacy build type) |
| itch.io HTML5 (draft) | project on https://mhvnsnt.itch.io/ | `wh-itch-trimmed.zip` built by `build_pages.py --itch` |

Facts that decide the commands (do not re-derive):

- The Pages source branch is **`gh-pages-m1-20261029`**, NOT `gh-pages`
  (the plain `gh-pages` branch is the retired Oct 27 target; deploying
  there changes nothing the owner sees). Confirm anytime with
  `gh api repos/mhvnsnt/western-heart/pages --jq .source.branch`.
- R2 is parked by owner order. The shell ships on the local/jsDelivr
  fallback in `game/js/asset-config.js`; `SHELL_BUNDLED_MODELS` in that
  file is the single source of truth for which models are bundled.
- Deploys are add/update-only. Nothing is ever removed from the deploy
  branch, and it is never force-pushed.
- The live build's identity is `deploy-manifest.json` at the site root:
  its `commit` field is the origin/main commit the site was built from.

## 1. Pages shell — standard route (any machine with working git)

```sh
git clone --filter=blob:none https://github.com/mhvnsnt/western-heart.git
cd western-heart
git fetch origin main gh-pages-m1-20261029
python3 tools/deploy/build_pages.py --ref origin/main --shell-only \
    --onto origin/gh-pages-m1-20261029 --branch gh-pages-m1-20261029 --push
```

Then verify (section 3). The builder prints the file count and total
bytes before pushing; the shell must stay under the 1 GB Pages cap
(2026-10-30 build: 2,068 files / 959,002,557 bytes).

## 2. Pages shell — Git Data API delta route (no local git needed)

When only a few files changed since the manifest's `commit` (the common
case for data-only merges), the same deploy can be made with pure API
calls — this is how the 2026-10-30 delta (781db7db..adf15d61) shipped
from a sandbox where git object writes were blocked:

1. `GET /repos/mhvnsnt/western-heart/compare/<manifest-commit>...main`
   and keep the changed files that belong to the deploy set (everything
   under `game/`, `customization/`, `packages/`, `roster/` that the
   shell ships; skip `docs/`, `teardown/`, `tools/`).
2. For each kept path, take its blob `sha` from main's tree
   (`GET /git/trees/main:game?recursive=1` etc.).
3. Create a new `deploy-manifest.json` blob (`POST /git/blobs`,
   base64) with `commit` = the main commit being shipped and
   `files`/`bytes` adjusted by the delta.
4. `POST /git/trees` with `base_tree` = the deploy branch tip's tree
   and one entry per kept path plus `deploy-manifest.json`.
5. `POST /git/commits` with that tree and `parents` = [deploy tip].
6. `PATCH /git/refs/heads/gh-pages-m1-20261029` with the new commit,
   `force: false`. A 422 means another lane deployed first — stop,
   recompute the delta from the new tip, never force.

## 3. Verify the Pages deploy (always, before calling it done)

```sh
gh api repos/mhvnsnt/western-heart/pages --jq .status   # -> "built"
curl -s https://mhvnsnt.github.io/western-heart/deploy-manifest.json
# its "commit" must equal the main commit you shipped
```

Spot-check one newly shipped file and one bundled model with `HEAD`
requests (200 + the exact byte size from main's tree), e.g.
`game/assets/models/pantera.glb` and the file your change touched.

Also verify the deployed tree's module graph is complete — a delta
deploy that ships a JS module without a file it imports breaks every
fight until a follow-up deploy lands (2026-10-30: fighter.js shipped
without step-plan-bank.js). Against a checkout of the deploy branch:

```sh
python3 tools/deploy/check_module_graph.py <deploy-branch-checkout>
# must exit 0 (warnings are pre-existing guarded/dynamic references)
```

## 4. itch.io trimmed build

Local route (canonical, from `tools/deploy/build_pages.py`):

```sh
python3 tools/deploy/build_pages.py --ref origin/main --itch --out itch-out
cd itch-out && zip -r ../wh-itch-trimmed.zip . -x deploy-manifest.json .deploy-files.txt
sha256sum ../wh-itch-trimmed.zip
```

The `--itch` build enforces itch.io's HTML5 caps itself (<=1,000 files,
<=500 MB extracted, <=200 MB per file, <=240-char names) and fails
without writing anything if a cap is exceeded.

CI route (no local build): run the **build-itch-zip** workflow
(Actions -> build-itch-zip -> Run workflow). It builds the same zip
from current main and uploads it to the GitHub release
`wh-itch-trimmed-v2`.

Upload to itch.io (DRAFT only — no public launch, no price change):

- With butler + an itch.io API key for the account:
  `butler push wh-itch-trimmed.zip mhvnsnt/western-heart:html5`
  (the project must already exist; butler cannot create projects).
- Or in the owner's logged-in browser session: itch.io dashboard ->
  the Western Heart project -> upload `wh-itch-trimmed.zip`, kind
  "HTML5", leave the project in Draft, save.

## 5. Definition of done for any finished piece

1. Merged on main.
2. Pages manifest `commit` == that main commit, Pages status `built`,
   spot checks pass.
3. Fresh `wh-itch-trimmed.zip` built from that commit and uploaded to
   the itch project as a draft.
4. The result reported with the manifest commit and the zip's sha256 —
   numbers, not "deployed".
