# Deploy split: Pages shell + GLBs on R2

Owner decision 2026-10-26 (tapped option, verbatim): "Split it: Pages shell + GLBs on R2".
This replaces the pending "what gets cut" question. Nothing is cut from the game,
only from the deploy. Research basis: `agent-ops` PR #161,
`research-friction-20261025/01-deploy-pages-limit.md` (all limits verified live
2026-10-25/26).

## The problem

- GitHub Pages caps a published site at **1 GB** (hard, from GitHub's own docs).
- The full deploy set is **6,052.0 MB** (7,632 files, measured 2026-10-27).
- The live site `https://mhvnsnt.github.io/western-heart/` is frozen on the Oct 24 build.
- The bloat is concentrated: **176 GLBs over 20 MB hold 5,914 MB** (73% of all GLB bytes).

## The shape

| Piece | Host | Contents | Size |
|---|---|---|---|
| Shell | GitHub Pages (unchanged URL) | code + UI + portraits + 1 stage + 2–4 bundled fighters + movesets | 739.5 MB measured (5,394 files), well under 1 GB |
| Models | Cloudflare R2 (one bucket, CORS `*`) | every GLB in the deploy set, at its repo path | 5,329.7 MB (manifest), inside the free 10 GB tier, $0 egress |
| Store of record | GitHub Releases (unchanged) | originals + archives | — |

Releases are NOT the runtime CDN: verified live 2026-10-26, release assets send
no `Access-Control-Allow-Origin` header, so `fetch()` from the game fails.
jsDelivr is NOT a second base: verified live, it 403s every file over 20 MB —
exactly the 176 files that are the whole problem. It is kept only as a
fallback candidate for small files (see `game/js/asset-config.js`).
The LOCAL URL is always a candidate too: in dev/CI the full repo is served
locally, and without it every non-bundled model fetched from jsDelivr instead
of disk — the menu-touch e2e fight load timed out on PR #1152 (run
40434489083) until the local fallback was added. On the Pages shell the local
candidate 404s fast (non-bundled GLBs are not in the shell), so it costs
nothing in production.

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
  fetch order: bundled models local, everything else R2 first, then the
  local URL, then jsDelivr last. Decision: **R2 as the remote base, local
  as the dev/CI fallback** (one manifest, one URL shape, no 20 MB cap,
  $0 egress; local 404s fast on the Pages shell).
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
Do NOT upload that ZIP to itch.io; itch.io will reject it.

## itch.io trimmed shell — `--itch` mode (done 2026-10-27, itch-trim lane)

`tools/deploy/build_pages.py --itch` builds the trimmed shell: the
shell-only set minus the cuts below, then the build FAILS (exit 1, nothing
written) if the result is over any hard itch cap. Measured from main
(`113cc24a`, the split commit), own-eyes:

- **ZIP `wh-itch-trimmed.zip`: 203,663,576 bytes compressed,
  282,824,816 bytes extracted, 881 entries, largest file 30,118,392 bytes
  (`roster/awa-pop/attires/attire2/model-rigged.glb`), longest
  filename 71 chars.** Caps: 881/1,000 files, 282.8/500 MB, 30.1/200 MB
  per file — all pass with margin. The ZIP is stored as a GitHub release
  asset (see the release line below) so the owner can pull it for the
  itch upload later; the local ZIP and build dir were cleared off disk
  after the release verified byte-identical.
- Rebuild command (one command, from the repo root, reproducible from main):
  `python3 tools/deploy/build_pages.py --ref origin/main --itch --out <dir>
  && cd <dir> && zip -r ../wh-itch-trimmed.zip . -x deploy-manifest.json
  .deploy-files.txt`
- Play proof: [see "itch play proof" below].

### What was cut (nothing is cut from the game, only from this deploy)

The itch build plays the bundled fighters only (demonio, pantera, awa-pop,
baek). Everything else loads from the remote asset base exactly like the
Pages shell does. Each rule carries its runtime evidence in
`itch_drop_reason()` (`tools/deploy/build_pages.py`); the headline cuts:

- Parts media: `customization/parts-converted/` 2,262 files +
  `customization/parts/` 697 files (catalog JSONs stay, so the creation
  suite still opens; the bundled fighters' GLBs are self-contained Tripo
  models and need no parts). Decal + reskin libraries (34 files) and the
  suite demo video (1 file) go with them — customization media, not fight
  assets.
- Non-bundled movesets: 198 files (only the 8 bundled movesets +
  `index.json` + `t3_input_tables.json` ship; `movesets/t7/` overlays are
  validation-tool data, not runtime — `movesets.js` fetches one JSON per
  fighter and never follows refs inside it).
- Non-bundled anim banks: 607 files (only jin, king_on_pantera_leoman,
  nina, bryan ship — the moveset index's `anim_bank` for the 4 bundled
  fighters). Unused anim: 31 files (`ur-general-*`, `t7/`, `made/`,
  `oss/` — no referrers in `game/js`).
- Music: 44 of 48 MP3s (only the 4 mode tracks ship: title-meditation,
  menu-deliberate, select-exhilarate, battle-volatile). `music.js`
  filters to what exists and never throws; CI runs menu-touch-e2e with
  music excluded entirely.
- Sound bank: all 229 `game/assets/sounds/` OGGs — `voice.js`
  `playSound(bankId)` has zero callers repo-wide; fight voices come from
  `game/assets/voices/` via the voice manifests (demonio 6 + pantera 52
  ship; the other 49 voice OGGs and 45 non-bundled voice manifests go).
- Non-bundled portraits: 66 files + 4 zui UI portraits (the select
  screen's `portraitHTML` falls back to a procedural SVG + monogram, so a
  missing portrait never breaks a card — verified in the play check).
- Stage thumbs: all 60 files (stages.js falls back to the palette swatch
  — verified in the play check: the stage screen renders swatch
  gradients). Stage files themselves all ship (T3 retro + No Mercy
  stages load via constructed paths, so they stay).
- Tests (55), docs (23), `data/t7-frame-data` (45), `data/movesets` (4),
  `data/moveset-library` (11 — its module has no importer), legacy
  `*_moves.json` (8), accessories docs (10), archive (10), model renders
  (7), ai-pass compare images (6), superseded `pano.png` originals (6),
  poses (4), sunra preview media (3).
- Kept deliberately: all code, all stages, all fight effects
  (`game/assets/fx/effekseer`), eastern-mind stage audio (referenced by
  `game/js/audio.js`), `game/data/t8_frame_tables.json` (the fight's
  frame data — `fighter.js` → `frame-tables.js`), music-library,
  jukebox-pools, sound-bank.json, story files, the 4 bundled GLBs
  (16.4 MB).
- **Fight models that ship although the shell-only filter drops them
  (5 files, 111.2 MB):** the split's `SHELL_BUNDLED_MODELS` names the
  BASE glbs, but the fight loads the fighters' ATTIRE models — the
  itch build would not play its bundled fighters without these:
  `roster/demonio/attires/attire1/model.glb` (27.5 MB, demonio-a1,
  Attire 1), `roster/demonio/attires/winged-devil/model-rigged.glb`
  (18.1 MB) + `roster/demonio/attires/human/model-rerig.glb` (27.4 MB)
  (demonio's transform targets, preloaded by `startFight` — the fight
  fails to start without them), `roster/awa-pop/attires/attire2/
  model-rigged.glb` (28.7 MB, awa-pop-attire2, Attire 2),
  `roster/pantera/attires/leomon/model.glb` (4.2 MB, pantera's
  select-pane attire — stops the panes retrying a missing model).
  Evidence: `attires.js` ATTIRE_VARIANTS (demonio Attire 1 =
  demonio-a1; the BASE demonio.glb "rendered the wrong body on
  select"), roster `model` fields (demonio `demonio-a1`, awapop
  `awa-pop-attire2`, pantera `pantera`, baek-master-white `baek`),
  `startFight`'s transform preload. **Same gap on the Pages shell:**
  a demonio or awa-pop fight fails there too until the remote base
  exists — that is a split follow-up (bundle the attire models in the
  shell, or land the remote base), not this lane.

### itch play proof

Run locally 2026-10-27 against the trimmed build served from disk
(`python3 -m http.server`, headless Chromium, iPhone 13 touch profile,
menu-touch-e2e variant picking the bundled fighters). The full flow ran
end to end: menu 8/8 tappable, versus -> solo -> select (pantera picked,
demonio picked, both confirms), stage confirmed (SHRINE OF THE BLADE),
fight HUD up reading PANTERA vs DEMONIO. `04-fight.png` viewed with my
own eyes: both fighters rendered in the arena in fighting stance, full
HUD (health bars, timer 60, round pips, NINE-SOUL METER, touch controls).
**0 bundled-asset 404s** across the run; the only 404s are non-bundled
portraits/movesets the remote base serves. (One pre-existing repo gap
surfaced: `game/js/intro-interactions.js` does not exist on main — a
dynamic import from `versus-banter.js`, one of the 4 named 404s from the
2026-10-25 friction research; the game degrades cleanly and the fight
still loads.)

Timer caveat, stated plainly: the timer read 60 at the HUD and still 60
after 180s. That is the test box, not the fight: this box renders through
SwiftShader (software GL) at a measured median **2,850 ms per frame** on
the menu, and the game clock is frame-rate-coupled (`frameDt` clamped to
0.05s, `FIXED_DT` 1/120), so the clock runs at ~0.018x real time on the
menu and slower in the heavier fight scene — one timer tick needs ~20
frames, i.e. ~100-200+ real seconds here. The same fight code counts the
timer and drops health on a real GPU (Oct 25 play-verify, Pantera vs
Demonio). No timer tick was captured on the trimmed build in this session;
the fight loading, rendering, and HUD are proven, the tick is not.

Harness notes (environment, not game defects): Playwright's tap
actionability wait starves on the panes' continuous rAF loop at this
frame rate, so the confirm buttons are clicked with a real force click
after a hit check proves the button is topmost at its center; the
confirm-stage screenshot is best-effort (the compositor can starve past
120s while the fight renders). CI covers the same flow via
menu-touch-e2e.

### itch release

- Release: `wh-itch-trimmed-v1` on mhvnsnt/western-heart —
  asset `wh-itch-trimmed.zip` (203,663,576 bytes, sha256
  `dbe6a5711e6d5c34a4e0c175642926cbe683c4769e4b29ddb3b9db715d357615`),
  verified byte-identical by re-download 2026-10-27; local ZIP + build
  dir cleared off disk after verify.

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
