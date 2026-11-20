# Snow Leopard bucket routing fix — 2026-11-02

## What was wrong

Three models live in the repo but are missing from the remote asset bucket,
although the R2 upload manifest (`tools/deploy/r2-upload-manifest.json`,
2,242 entries) lists all three. The game loads non-bundled models remote-first
(`game/js/asset-config.js` `resolveAssetCandidates`: remote, then local, then
jsDelivr), so a missing bucket object means a failed primary fetch every time.

Spelling lock (Mars confirmed 2026-11-02): "Yukio" was speech-to-text for
Yukihyō. There is no separate Yukio fighter — no `yukio` roster directory and
no `yukio` id in `game/js/roster-full.js`. The fighter is `yukihyo` (roster id
`yukihyo`, name `YUKIHYŌ`, title `Snow Leopard Ninja`). This fix covers
Pantera and Yukihyō only.

## Bucket key vs repo path (verified live 2026-11-02, HEAD status only)

The bucket key IS the repo path (`repoPathForModelUrl` maps a MODEL_URLS entry
to its repo-relative path, and the manifest's `r2_key` equals that path). There
is no key mismatch — the objects themselves are absent from the bucket.

| Fighter / attire | Bucket key = repo path | Bytes | Bucket | jsDelivr | Production result before fix |
|---|---|---|---|---|---|
| Pantera, Attire 4 · SNOW LEOPARD | `roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb` | 7,434,348 | 404 | 200 | Loads, only via 3rd-candidate fallback |
| Yukihyo, Attire 1 (Tripo) | `roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb` | 33,174,092 | 200 | 403 (over 20 MB) | Loads via remote primary |
| Yukihyo, Attire 2 · BOBCAT PRIDE (Tripo) | `roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride-rigged.glb` | 33,257,868 | 404 | 403 (over 20 MB) | FAILS — every candidate fails |
| Yukihyo, Attire 3 · TIGER KING (Tripo) | `roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king-rigged.glb` | 32,100,272 | 404 | 403 (over 20 MB) | FAILS — every candidate fails |
| Yukihyo, Attire 4 · CLASSIC | `game/assets/models/yukihyo.glb` | (not re-measured) | 200 | — | Loads via remote primary |
| Pantera base model (control) | `game/assets/models/pantera.glb` | — | 404 | — | Loads: already shell-bundled (local-first) |

So the hard failures are Yukihyo attires 2 and 3: bucket 404 + local 404 (not
bundled; the Pages shell ships only `SHELL_BUNDLED_MODELS`) + jsDelivr 403
(files over 20 MB). Pantera Snow Leopard is softer — it loads through jsDelivr —
but its primary is broken and it depends on the fallback.

No model was missing from the repo, and no new model was supplied or fabricated.
All three fixed files are the existing repo copies.

## The fix (this PR)

Point the game at the repo copies by bundling the three broken models in the
Pages shell — the supported mechanism (`SHELL_BUNDLED_MODELS` in
`game/js/asset-config.js` is the single source of truth; `build_pages.py` reads
it at deploy time). Bundled models load local-first, so they no longer depend
on the bucket at all. This is the same precedent as the Doc Frank attire-1
bundle (25.2 MB, bundled because jsDelivr 403s files over 20 MB).

- `game/js/asset-config.js`: 3 paths added to `SHELL_BUNDLED_MODELS` (19 → 22).
- `tools/deploy/build_pages.py`: same 3 paths added to the built-in fallback
  list. Note: that fallback list was already stale (4 entries vs 19 in the JS
  source of truth); a full re-sync is a separate cleanup, not this fix.
- `test/snow-leopard-bucket-routing.test.mjs`: new test — the 3 paths are
  bundled, resolve local-first, and exist on main at the verified blob SHAs
  (via plain `git ls-tree`, tree entries only, no blob downloads, so it runs
  on CI's sparse checkout; a blob SHA pins the exact bytes and therefore the
  size); control assertion that Yukihyo attire 1 stays remote-first.
- Yukihyo attire 1 is deliberately NOT bundled: its bucket copy returns 200.

Shell size: bundled models 389.5 MB → 462.3 MB (manifest sizes), still under
the 1 GB Pages cap; each added file is under the 100 MB per-file cap (the
32–33 MB files exceed the 25 MiB soft cap, which the `build_pages.py` comment
explicitly allows for named bundled models). Itch: the trimmed set grows by at
most the 7.4 MB Pantera file (Yukihyo is not an itch-bundled fighter), far
under the 500 MB itch cap.

## What this does NOT do

- No bucket re-upload was performed: bucket writes need Cloudflare/B2
  credentials that are owner-only (`tools/deploy/DEPLOY-SPLIT.md`: "Cloudflare
  signup is owner-only"). Bundling removes the need for a re-upload — after
  the next republish, these three models load from the shell whether or not
  the bucket objects ever appear. Re-uploading the three keys later is
  optional and harmless (bundled models load local-first either way).
- No deploy was made by this PR. The fix lands in the repo; it goes live at
  the next republish, which remains held for the owner's playtest.
- No MODEL_URLS key changed, so the material gate and rig guard are
  unaffected. No menu markup changed, so the ui_sources gate is unaffected.
- No source-game character names appear in player-facing UI (none touched)
  and this doc names fighters by their Western Heart names only.

## How to verify after the next republish

1. Open the live build, pick Pantera Attire 4 · SNOW LEOPARD and Yukihyo
   attires 2 and 3: all three must load with no failed network fetch.
2. Optional: re-HEAD the three bucket keys — 404s there no longer matter.
3. If the owner later re-uploads the three keys, nothing changes in-game
   (local-first still wins); no code change is needed for that.

## Still owed (not this PR)

- ORDER-doc batch update (parts, Roger, WWE/Tekken, and this fix) — held until
  PR #1498 merges, to avoid a conflict with its Phase 4b row edit.
- Full re-sync of the `build_pages.py` fallback bundled list (pre-existing
  drift, 4 vs 19 before this fix).
- The bucket's missing objects (these 3, plus the bundled `pantera.glb`
  control) stay absent until someone with bucket-write access re-uploads
  them; not required for the game to work after this fix ships.
