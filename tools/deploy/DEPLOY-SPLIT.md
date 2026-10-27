# Deploy split: Pages shell + GLBs on R2

Owner decision 2026-10-26 (tapped option, verbatim): "Split it: Pages shell + GLBs on R2".
This replaces the pending "what gets cut" question. Nothing is cut from the game,
only from the deploy. Research basis: `agent-ops` PR #161,
`research-friction-20261025/01-deploy-pages-limit.md` (all limits verified live
2026-10-25/26).

## The problem

- GitHub Pages caps a published site at **1 GB** (hard, from GitHub's own docs).
- The full deploy set is **~5,969 MB** (7,545 files, measured 2026-10-25).
- The live site `https://mhvnsnt.github.io/western-heart/` is frozen on the Oct 24 build.
- The bloat is concentrated: **176 GLBs over 20 MB hold 5,914 MB** (73% of all GLB bytes).

## The shape

| Piece | Host | Contents | Size |
|---|---|---|---|
| Shell | GitHub Pages (unchanged URL) | code + UI + portraits + 1 stage + 2–4 bundled fighters + movesets | ~70–170 MB, well under 1 GB |
| Models | Cloudflare R2 (one bucket, CORS `*`) | every GLB in the deploy set, at its repo path | 5,969 MB, inside the free 10 GB tier, $0 egress |
| Store of record | GitHub Releases (unchanged) | originals + archives | — |

Releases are NOT the runtime CDN: verified live 2026-10-26, release assets send
no `Access-Control-Allow-Origin` header, so `fetch()` from the game fails.
jsDelivr is NOT a second base: verified live, it 403s every file over 20 MB —
exactly the 176 files that are the whole problem. It is kept only as a
fallback candidate for small files when R2 is down (see `game/js/asset-config.js`).

## What landed in this lane

- `tools/deploy/build_pages.py --shell-only` — deploys the shell only.
  Bundled models are read from `game/js/asset-config.js` (`SHELL_BUNDLED_MODELS`,
  single source of truth; the script falls back to its built-in list if the
  file cannot be read from the ref). Also fixed: `ls-tree -z` — the script
  died on main tip (2026-10-26) because 4 mojibake filenames under
  `customization/parts*` come back C-quoted from `ls-tree`.
- `game/js/asset-config.js` — the one-line config. `remoteBase` is the R2
  public URL; until it is filled in, the placeholder `__WH_R2_PUBLIC_URL__`
  stands and `isRemoteReady()` is false. `resolveAssetCandidates()` is the
  fetch order: bundled models local, everything else R2 first, jsDelivr
  fallback. Decision: **R2-only as the remote base** (one manifest, one URL
  shape, no 20 MB cap, $0 egress).
- `game/js/assets.js`, `game/js/stages.js`, `game/js/customization-consumer.js` —
  all three GLB loaders now go through the candidate order. No per-model
  changes anywhere; `MODEL_URLS` and stage defs are untouched.
- `tools/deploy/r2-upload-manifest.py` + `tools/deploy/r2-upload-manifest.json` —
  every model to upload, with repo path, R2 key (= repo path), bytes, blob SHA,
  and the matching release asset where one exists by (name, size). Built from
  live GitHub (same closure as the deploy script), never from local disk.
- Known limitation: the persistent Cache API only stores same-origin or
  relative URLs, so cross-origin remote loads re-download each session until
  served same-origin. R2 egress is $0, so this costs time, not money.

## Owner steps — R2 (BLOCKED on these, owner-only, card rules apply)

Cloudflare may ask for a payment method on file even on the free tier. Do NOT
let any lane sign up on your behalf. Tap through this yourself:

1. Create a Cloudflare account at https://dash.cloudflare.com/sign-up
   (email + password; use your own).
2. Left nav: **R2 Object Storage** → **Create bucket**.
   - Bucket name: `western-heart-assets` (lowercase, dashes; this name is a
     suggestion — any name works, but the runbook below assumes this one).
   - Location: Automatic. Click **Create bucket**.
3. Open the bucket → **Settings** → **Public access**: allow public access
   (R2.dev subdomain). Note the public URL — it looks like
   `https://pub-<hash>.r2.dev`. (A custom domain can replace it later.)
4. Same bucket → **Settings** → **CORS policy** → add this rule:
   ```json
   [{"AllowedOrigins": ["*"], "AllowedMethods": ["GET", "HEAD"], "AllowedHeaders": ["*"]}]
   ```
   (`AllowedOrigins: *` is what the game needs: the shell on
   `mhvnsnt.github.io` and the itch.io player both fetch cross-origin.)
5. Tell the lane the public URL (paste it in chat). The lane then sets
   `ASSET_CONFIG.remoteBase` in `game/js/asset-config.js` to that URL
   (one line, PR + merge), uploads the manifest, and verifies with
   `curl -I -H "Origin: https://mhvnsnt.github.io"` plus a real browser
   fetch of a >25 MB GLB.

## Upload runbook (lane job, after the bucket exists)

1. Regenerate the manifest against latest main:
   `python3 tools/deploy/r2-upload-manifest.py --ref origin/main`
2. Upload every entry to its `r2_key`, fetching bytes from the listed
   `source` (release asset where matched, else the pinned repo blob via
   git/raw) — never from local disk. `wrangler r2 object put` or the
   S3-compatible API, in 100 MB parts where the tool needs it.
3. Verify: `curl -I -H "Origin: https://mhvnsnt.github.io" <r2-url>/game/assets/models/cape-jones.glb`
   must return 200 with `Access-Control-Allow-Origin: *`; then a real
   browser `fetch()` of the same URL must return the bytes.
4. Flip `remoteBase` in `game/js/asset-config.js` (PR + merge), then
   deploy the shell: `python3 tools/deploy/build_pages.py --ref origin/main
   --shell-only --onto origin/gh-pages --push` and confirm the live site
   updates and a non-bundled fighter loads from R2.

## itch.io setup sheet (owner taps; lane preps)

Account + payout setup is owner-only (phone). The shell ZIP is built by the
lane from the same shell set (`build_pages.py --shell-only --out`, then zip;
limits: ≤500 MB extracted, ≤1,000 files, ≤200 MB per file).

**CORRECTION — measured 2026-10-27, this lane (supersedes the research
estimate of "70–170 MB, a few hundred files"):** the real shell set is
**5,395 files / 739.5 MB** (`wh-itch-shell-20261026.zip`: 490,419,079 bytes
compressed, 739,520,900 bytes extracted, 5,634 entries). It fits Pages
(<1 GB) but it does **NOT** fit itch.io HTML5 as-is: extracted size is
239.5 MB over the 500 MB cap and entries are 4,634 over the 1,000 cap.
Breakdown of the 718 MB on disk: JSON 295.8 MB (1,190 files — movesets +
anim data for ALL fighters), MP3 236.8 MB (48 files — all music), PNG
113.4 MB (2,991 files), OGG 30.6 MB, bundled GLBs 17.2 MB, rest ~24 MB.
The itch build needs its own trimmed shell (a `--itch` mode: only the
bundled fighters' movesets/anim data, a music subset, and the PNGs those
screens use) — **follow-up lane, not done here**. Do NOT upload this ZIP
to itch.io; itch.io will reject it. Rebuild command (from the repo):
`python3 tools/deploy/build_pages.py --ref origin/main --shell-only --out
<dir> && cd <dir> && zip -r ../wh-itch-shell.zip . -x deploy-manifest.json
.deploy-files.txt`.

1. Create the itch.io account at https://itch.io/register (email + password).
2. **Create new project** → kind **HTML5** → upload the shell ZIP.
   - Viewport: set to the game's size; enable **SharedArrayBuffer** only if
     the game needs it (it does not today).
   - Check **This file will be played in the browser**.
3. **Distribute → Payout mode**: pick one now so the account is money-ready:
   - **Direct to you** (each purchase straight to your PayPal/Stripe, no
     itch threshold, you handle VAT/tax), or
   - **Collected by itch.io** (7-day hold, $5.00 minimum payout, payout
     review typically 10–14 days, PayPal or Payoneer, one-time $3 tax
     interview verification fee).
   - Revenue share is open: seller picks itch.io's cut 0–100% (default 10%);
     payment-processor fees separate (Stripe ~2.9% + $0.30).
4. Turn **donations** on for the HTML5 project. Note: HTML5 games can only
   take donations — charging for access needs a **Downloadable** project kind.
   The money path is: free HTML5 shell (donations on) + a paid Downloadable
   build later (butler CLI, 2 GB default cap — increase on request).
5. The shell lazy-loads GLBs from R2 over HTTPS, which itch.io allows for
   HTML5 projects. Absolute paths (`/...`) break on itch's player — the
   loader uses relative paths locally and absolute R2/jsDelivr URLs remotely,
   so nothing needs to change for itch.

## Verification checklist (before calling the split done)

- [x] Shell dry-run: `build_pages.py --ref origin/main --dry-run --shell-only`
      reports **5,394 files / 739.5 MB** (measured 2026-10-27; full set is
      7,632 files / 6,052.0 MB — both verified from the build log).
- [x] R2 manifest: 2,242 models / 5,329.7 MB, fits the free 10 GB tier.
- [ ] R2 `curl` CORS probe returns `Access-Control-Allow-Origin: *`.
- [ ] Browser `fetch()` of a >25 MB GLB from R2 returns bytes.
- [ ] Live Pages site updates from the shell-only deploy.
- [ ] A non-bundled fighter (e.g. Jin) loads in a real fight from R2.
- [ ] itch.io HTML5 project live with donations on (owner step) — BLOCKED on
      the itch-trim follow-up: the Pages shell (739.5 MB / 5,395 files)
      exceeds itch's 500 MB / 1,000-file caps (see itch section above).
