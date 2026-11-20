# Asset CDN Worker — B2 bypass via GitHub Releases (2026-11-06)

Owner decision 2026-11-06 (verbatim pick): "Wire up GitHub Releases + the Worker".

## Why

The Backblaze B2 bucket `western-heart-assets` is over its 10 GB no-card
daily storage cap (11 GB stored). Uploads fail `storage_cap_exceeded`, and
the cap cannot be edited until a card is on file. The owner chose NOT to
add a card. Instead, the files B2 refuses are served from GitHub Releases
behind the existing Cloudflare Worker (`western-heart-assets.mhvnsnt.workers.dev`),
keeping the exact key/URL shape the game already requests
(`game/js/asset-config.js` `remoteBase` + repo-relative key). B2 keeps
serving the 2,186 objects it already holds; the Worker falls through to
B2 for every key not in the release manifest. Game side: NO change.

## What landed

- **Release `assets-cdn-v1`** on this repo:
  https://github.com/mhvnsnt/western-heart/releases/tag/assets-cdn-v1
  58 model assets, 1,524,629,804 bytes total, plus `assets-manifest.json`.
  Asset name rule: bucket key with `/` replaced by `__`.
  Contents = the 7 priority files (Negativo refit, Purple Rain re-rig,
  packed Kiko, Demonio attire 1, and the current Pond #1571 / Megami #1576 /
  Menajerii #1577 rebuild models) + all 53 files from the B2 "missing 53"
  set (`_b2-upload-20261031/missing53.json`). Two keys overlap
  (tsuyu-asui + vixen rebuilds were in the 53), so 7 + 53 − 2 = 58 unique.
- **Manifest**: `tools/asset-cdn-worker/assets-manifest.json` (same file is
  a release asset). Key → asset name, size, sha256 for all 58.
- **Worker source**: `tools/asset-cdn-worker/worker.js` (+ `wrangler.toml`).
  Behavior: GET/HEAD only; if the decoded path is a manifest key, fetch the
  GitHub release asset (redirect followed, Range forwarded when present),
  strip `content-disposition`, serve with `Access-Control-Allow-Origin: *`
  and `Cache-Control: public, max-age=3600` — the same header shape the B2
  path produces today. Every other key runs the original SigV4 B2 proxy
  code, unchanged.

## Sources of the bytes

Model bytes were fetched from this repo's `main` (branch tip at fetch
time; HEAD `b6add3fa` at fetch start), except Negativo refit and Purple
Rain re-rig, which came from the hash-verified staged copies kept from the
B2 lane (`_b2-upload-20261031/reupload-20261101/`, identical to main).
Known-good hashes re-confirmed on the fetched bytes:
Negativo refit sha256 `9eab7cc949194d6e…`, Purple Rain re-rig
`f8fae3a27f587f46…`, Kiko `7289654c2050c363…` (20,234,944 B — main carries
the packed file), Demonio attire 1 `b95e71252ba1…` (28,793,068 B, the
PR #1524 file at `roster/demonio/attires/attire1/model.glb`).

## Verification (done)

- Release side: all 58 assets re-read through the GitHub API — every
  `size` and every `digest` (sha256) matches the manifest exactly. No
  sampling; 58/58.
- Baseline (pre-deploy) Worker behavior recorded: B2-only keys
  `roster/zen/attires/attire1/model-rigged.glb` (200, 29,237,496 B,
  sha256 d37b4e7c…) and `game/assets/models/cyborg-x.glb` (200,
  41,346,180 B, sha256 3d50d0bc…) serve from B2; priority key
  `roster/negativo/attires/attire1/source/negativo-a1-refit.glb` is 404.

## REMAINING STEP — Worker deploy (blocked on B2 secret values)

The new Worker code is written and syntax-checked but NOT yet deployed.
Both Cloudflare upload APIs (legacy script PUT and the Versions API)
reject the upload with error 10021 — "invalid or missing text property
for binding B2_APP_KEY" — because a code upload must re-declare the
script's `secret_text` bindings WITH their values, and the B2_KEY_ID /
B2_APP_KEY values are not held in any file, checkpoint, or connector
(they were set on the script at creation, 2026-10-29). The rejected PUTs
changed nothing: the live Worker still runs the original code (baseline
re-verified after the attempts — zen + cyborg-x 200 with correct
Content-Lengths, negativo-refit still 404).

To finish, ONE of:
1. Paste `tools/asset-cdn-worker/worker.js` into the script in the
   Cloudflare dashboard editor and deploy (the dashboard preserves the
   stored secrets), or
2. Supply the two secret values through the approved credential path,
   then re-run the API deploy (script kept with the lane's records:
   `_assets-cdn-v1/deploy_worker.py` in the agent workspace).

After deploying, verify: every manifest key returns HTTP 200 at
`https://western-heart-assets.mhvnsnt.workers.dev/<key>` with body
sha256 == manifest, and the two B2-only baseline keys above still serve
200 byte-identical.

## Notes

- The B2 upload key (`western-heart-reupload-20261101`) was NOT revoked
  and no card was added anywhere, per the owner's decision.
- Nothing was deleted: staged B2 files and all local records remain.
- The old local Worker source in the agent workspace (`wh-worker/`)
  stays as the record of the previously deployed code; this repo
  (`tools/asset-cdn-worker/`) is the canonical home from now on.
