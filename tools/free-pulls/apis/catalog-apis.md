# Free APIs catalog for Western Heart (WH)

Verified live on **2026-10-24** from this VM. Every claim below comes from an
actual HTTP call or a documentation page read that day — not from memory.
No API keys, tokens, or credentials appear anywhere in this directory.
Scripts are Python 3, standard library only, and were all run successfully
(except where a script's own honest stop-condition fired — those are marked).

**Total pulled: ~9.4 MB** (well under the 50 MB lane budget). Nothing in this
lane downloads model weights, large datasets, or big binaries.

**Integration point (all scripts):** this directory is the lane's staging area.
When WH adopts a script, copy it into the game repo (e.g. `tools/pulls/` or
`tools/assets/`) and point its `--out` at the repo's asset pipeline
(`assets/textures/`, `assets/fonts/`, `assets/audio/`); the per-API "WH use"
notes below say where each asset type belongs. Nothing here was pushed to
any repo — deliverable is files only, per the brief.

---

## 1. Poly Haven — ✅ WORKS, no auth

- **Endpoint (CORRECTED):** `https://api.polyhaven.com`
  - `GET /assets?type=textures|hdris|models` → JSON dict keyed by asset id
    (869 textures on 2026-10-24; categories via `GET /categories/{type}`).
  - `GET /files/{asset_id}` → download URLs by map / resolution / format
    on `dl.polyhaven.org`.
  - ⚠️ The brief's host `api.polyhaven.org` is **wrong**: it returned
    **HTTP 522** on 2026-10-24. Use `.com`. Also `GET /assets/{id}` is
    **404** (`Cannot GET /assets/aerial_asphalt_01`) — the list endpoint
    and `/files/{id}` are the working pair.
- **License:** CC0 (all assets, per Poly Haven; re-check the asset page).
- **Free-tier limits:** No account, no key, no published rate limit seen.
- **Auth:** None.
- **Script:** `polyhaven.py` — `--list`, `--search <q>`, `--download <id>
  --map Diffuse --res 1k --format jpg`. Re-tested end-to-end: re-downloaded
  `sand_01` 1K JPG, 485,088 bytes on disk = API's stated size.
- **What was pulled:** 3× 1K diffuse JPGs (1024×1024, verified with `file`):
  `aerial_asphalt_01` (635,143 B), `sand_01` (485,088 B), `rock_01` (688,083 B).
- **WH use:** Arena ground/road/rock textures for the Three.js fighter.
  1K for web builds; re-pull 2K/4K from the same `/files` endpoint for hero arenas.
  HDRIs from the same API are the arena-lighting source.

## 2. ambientCG — ✅ WORKS, no auth

- **Endpoint:** `https://ambientcg.com/api/v3/assets`
  (docs: `https://docs.ambientcg.com/api/v3/assets/`; v2 `full_json` /
  `downloads_csv` still exist but v3 is the documented current API).
  - Without `include=downloads` the API returns **ids only**
    (`totalResults: 2037` materials, first page `Fabric086`, `Bricks113A`).
  - With `include=downloads,maps,thumbnails,url` it returns real zip URLs,
    e.g. `Fabric086` 1K-JPG → `https://ambientcg.com/get?file=Fabric086_1K-JPG.zip`
    (7,733,757 B per API). A bogus id (`Rock047A`) returns 200 with
    `totalResults: 0` — ids are case-sensitive in practice; search first.
  - One transient `RemoteDisconnected` was seen on a search call; the
    script now retries once and then fails loudly instead of faking data.
- **License:** CC0. **Auth:** None (no account to download).
- **Free-tier limits:** No published hard limit; keep requests polite
  (one at a time, small `limit`).
- **Script:** `ambientcg.py` — `--search`, `--id`, `--download <id>
  --variant 1K-JPG`.
- **What was pulled:** `Fabric086` 1K-JPG zip (7,733,757 B, zip integrity
  test OK: Color, NormalDX/GL, Roughness, Displacement JPGs + `.blend`,
  `.mtlx`, `.tres`) + 256px thumbnail (91,907 B).
- **WH use:** PBR materials for costumes, banners, arena dressing.
  Unzip into the material pipeline; prefer 1K-JPG for web.

## 3. Google Fonts — ✅ WORKS, no key

- **Endpoint:** `https://fonts.googleapis.com/css2?family=...&display=swap`
  — no key, no account. The *separate* Google Fonts Developer API
  (metadata JSON) does need a key; WH does not need it.
  - Gotcha 1 (caught live): with a plain Python UA the server returns
    **TTF** URLs; with a browser UA it returns **WOFF2**. The script sends
    a browser UA.
  - Gotcha 2 (caught live): the script's first version omitted `:wght@`
    and Google answered **HTTP 400**. Fixed; the script now builds
    `family=Inter:wght@400;700` correctly.
  - Gotcha 3 (verified, not a bug): Inter and Oswald are **variable
    fonts** — css2 returns the *same* woff2 URL for weights 400 and 700
    (identical bytes, md5-verified). The script therefore writes **one**
    file per variable font with a weight-range `@font-face` rule, not two
    identical files.
- **License:** OFL (SIL Open Font License) for these families.
- **Free-tier limits:** None applicable (public CSS endpoint).
- **Auth:** None.
- **Script:** `google_fonts.py` — `--families "Bebas Neue" "Inter:400;700"
  "Oswald:600;700" --out samples/fonts`. Writes woff2 files + `fonts.css`.
- **What was pulled:** `BebasNeue-400.woff2` (13,768 B, display),
  `Inter-variable.woff2` (48,256 B, 400–700, body),
  `Oswald-variable.woff2` (21,472 B, 600–700, alt display) + `fonts.css`
  with self-hosted `@font-face` rules and a hosted `<link>` alternative.
- **WH use:** `.wh-display { 'Bebas Neue', 'Oswald' }` for fight UI / VS
  banners / health-bar names; `.wh-body { 'Inter' }` for menus, movelists,
  settings, HUD text. Drop `fonts.css` into the game's CSS or use the
  hosted link in the snippet.

## 4. Free Music Archive (FMA) — ❌ API SHUT DOWN, no key path exists

- **Endpoint (dead):** `https://freemusicarchive.org/api/get/tracks.json`
  → **HTTP 404** on 2026-10-24.
- **Proof:** FMA's own page `https://freemusicarchive.org/app-developers/`
  states: *"Free Music Archive used to have an API … we unfortunately had
  to shut down our API."* There is **no api_key signup** that restores it.
  Any older write-up claiming a 1,000-calls/day key (or an env-var key
  flow) is stale — this script does **not** implement one, because it
  would be fiction.
- **Rules that still apply (same page):** NO hotlinking (host any FMA
  track you use on your own server, under its CC licence); do NOT forward
  user search queries to FMA's search engine or scrape its HTML without
  explicit FMA approval. This lane therefore pulled **no audio files**.
- **License:** Per-track Creative Commons; several candidates below are
  **CC BY-NC-SA (NonCommercial)** — reference/temp tracks only until the
  licence is re-checked on the track page.
- **Auth:** N/A (no API). **Free-tier limits:** N/A.
- **Script:** `fma.py` — `--probe` (reports the 404 honestly),
  `--candidates` (prints the curated list), `--template` (blank metadata
  record to fill in by hand after a manual download).
- **What was pulled:** Metadata only (`samples/fma_candidates.json`), from
  FMA's public genre/track pages read in a browser (NOT an API):
  1. "Cowboy Surfer" — The Vivisectors, *Happy Halloween*, 03:42,
     CC BY-NC-SA, Rock/Surf/Halloween.
  2. "Duane Stomp" — The Vivisectors, *Happy Halloween*, 02:39, CC BY-NC-SA.
  3. "Halloween Surf Rock With Theramin" — Greg Kirkelie, *Halloween Music*,
     02:10 (licence: re-check on the track page).
  4. "Ghost Surf Rock" — Loyalty Freak Music, *WITCHY, BATTY, SPOOKY,
     HALLOWEEN IN SEPTEMBER !!*, 04:07 — the FMA record for the
     Cape Jones theme.
- **WH use:** Spooky/surf fight-vibe reference tracks. Adopt by hand:
  download from the FMA track page, self-host, credit the artist, obey
  the licence. Never hotlink, never auto-scrape.

## 5. OpenGameArt — ⚠️ NO JSON API (HTML search only)

- **Endpoint:** There is **no public JSON search API**. Appending
  `?format=json` to
  `https://opengameart.org/art-search-advanced?keys=fighting&sort_by=count&sort_order=DESC`
  returns **HTTP 200, `Content-Type: text/html`** (the normal search page),
  not JSON. The browser search itself works: "Displaying 1 – 24 of 194"
  for `keys=fighting` on 2026-10-24.
- **License:** Varies per asset (CC-BY, CC0, GPL, etc.) — always re-check
  the asset page; notes below are what the pages showed on 2026-10-24.
- **Auth:** No API key. Some file downloads on detail pages may ask for a
  free OGA site login — that is a site login, not an API credential, and
  no script here asks for it.
- **Script:** `opengameart.py` — `--probe` (proves `?format=json` returns
  HTML), `--records` (prints the curated records). It does **not** scrape.
- **What was pulled:** Metadata only (`samples/opengameart_records.json`),
  from detail pages read in a browser:
  1. "Fighting Robot for Ultimate Smash Friends" — Stephen Challener
     (Redshrike); page states CC-By with a link back to OpenGameArt.org;
     animated robot sprite (idle/shock/kick).
  2. "Voiceover Pack: Fighter (40+ taunts)" — Kenney.nl (credit requested,
     not mandatory); separate OGGs for Round 1/2/3, Fight, Flawless
     victory, Combo breaker, Winner, You lose, etc. — the most
     WH-relevant hit (announcer/VO placeholders).
  3. "Streets of Fight" — ansimuz (attribution optional); beat-'em-up
     pack, `streets_of_fight_files.zip` 294.9 KB, 1,098 downloads per page.
- **WH use:** VO placeholders + 2D reference art / side-mode backgrounds.
  NOT the 3D fighter itself. Download chosen assets by hand from their
  OGA pages.

## 6. Sketchfab — ⚠️ SEARCH works unauthenticated; DOWNLOAD needs auth

- **Endpoints (Data API v3):**
  - `GET https://api.sketchfab.com/v3/search?type=models&downloadable=true&q=torso&count=2`
    (no auth) → **HTTP 200**, e.g. "Marble torso from a statue of
    Dionysos" (uid `de078950bd474c73bb6cd7e1cf31de9b`, downloadable=true,
    307 likes, 15,373 views).
  - `GET https://api.sketchfab.com/v3/models/{uid}/download` (no auth)
    → **HTTP 401** `{"detail": "Authentication credentials were not provided."}`
    (verified 2026-10-24).
- **Auth for downloads:** OAuth2 user token (`Authorization: Bearer …`)
  on the Download API, or a personal API token (`Authorization: Token …`)
  on Data API v3, from your Sketchfab account. Download permission still
  depends on the creator allowing downloads, and attribution (creator,
  source, licence) must be displayed per Sketchfab's terms.
- **License:** Per-model (varies; many CC). **Free-tier limits:** Search
  is public; downloads are per-account/per-model, not a free bulk pipe.
- **Script:** `sketchfab.py` — `--search` (no auth), `--download <uid>`
  (reads `SKETCHFAB_API_TOKEN` from the environment **only**, never
  prints or stores it; without it the script stops with the 401
  explanation — exit 2, verified — instead of faking a download).
- **What was pulled:** Search output only
  (`samples/sketchfab_search_torso.txt`, 3 hits incl. "Female Torso Base
  Mesh", 650 likes — the most WH-relevant hit for anatomy/base-mesh
  reference). **No model file was downloaded** (auth-gated, correctly).
- **WH use:** Discovery/reference only. Note: Sketchfab's catalogue is
  migrating to Fab (Epic) — treat it as a discovery source, not a
  permanent pipeline dependency; keep a local copy + attribution record
  for anything adopted.

## 7. Hugging Face — ✅ WORKS, no auth (metadata only)

- **Endpoints:**
  - `GET https://huggingface.co/api/models?search=image-to-3d&limit=3`
    → 200, e.g. `AIExxplorer/AIEXX_GENAI_IMAGE_TO_3D` (image-to-3d,
    Apache-2.0), `kushbhargav/image_to_3d` (MIT),
    `cebas/oneClick_Windows_ImageTo3D_install` (text-to-3d, Apache-2.0).
  - `GET https://huggingface.co/api/datasets?search=motion%20capture&limit=3`
    → 200, e.g. `OpenLoong-Official/Motion-Capture` (CC-BY-2.0),
    `OpenLoong/Motion-Capture` (CC-BY-2.0),
    `nekomata-project/motion-capture-data` (licence: other).
  - `GET https://huggingface.co/api/models?limit=2` → 200 (baseline check).
- **License:** Per-model/dataset (shown in output via `license:*` tags).
- **Free-tier limits:** Unauthenticated reads work; no fixed published
  number — keep `limit` small. Gated/private items return 401 and are
  skipped, never worked around.
- **Auth:** None needed for reads. A `HF_TOKEN` is **not** read or needed.
- **Script:** `huggingface.py` — `--models <q>`, `--datasets <q>`,
  `--limit N`; default sweep covers image-to-3d, text-to-3d, motion
  capture, human pose. **It never downloads model weights** — metadata
  only, by design (weights would blow the lane's size budget and need
  their own approval).
- **What was pulled:** Metadata listings only (printed to stdout, not
  saved as fake "samples" — see the script's output in the verification
  run).
- **WH use:** Pipeline research — image-to-3D / text-to-3D model
  candidates for the creation suite, mocap + pose datasets for animation
  reference. Any weight download is a separate, explicitly approved step.

## 8. Kaggle — 🔒 AUTH REQUIRED (documented only; no live call made here)

- **Auth:** Kaggle account + API token. Kaggle web → profile → Account
  Settings → API → "Create New API Token" downloads `kaggle.json`; place
  at `~/.kaggle/kaggle.json` with **mode 600** (`chmod 600
  ~/.kaggle/kaggle.json`). Official CLI: `pip install kaggle`, then
  `kaggle datasets list -s "motion capture"`.
- **Status on this VM (2026-10-24, checked without reading any secret):**
  `~/.kaggle/kaggle.json` **exists with mode 600** (verified via `ls -l`
  / `os.stat` only — contents were never read, printed, or transmitted),
  but the **`kaggle` CLI is NOT installed** (no binary found). The live
  `--list` path was therefore **not run here**; running it would be a
  sign-in/API call, which the brief forbids for this lane.
- **License:** Per-dataset (Kaggle datasets carry their own licences).
- **Free-tier limits:** Kaggle accounts are free; API usage follows the
  account's terms (no fixed quota quoted here — check Kaggle's docs).
- **Script:** `kaggle.py` — **default is check-only**: reports file
  presence/mode, CLI presence, and the exact commands to run by hand;
  makes **no** API call and no sign-in. `--list "<term>"` is the explicit
  live path (shells out to the official CLI, which reads `kaggle.json`
  itself; no credential is passed on the command line).
- **What was pulled:** Nothing (by design).
- **WH use:** Once the CLI is installed on an authorized machine, search
  `motion capture`, `human pose estimation`, `fighting game`,
  `3d human mesh`, `animation` for mocap/animation datasets to feed the
  animation pipeline. Keep any download small and licence-checked.

---

## Verification log (commands run 2026-10-24)

- `polyhaven.py --search sand` → hits incl. `aerial_beach_01`,
  `coast_sand_01`; `--list --limit 3` → 869 textures total, top
  `plywood` (732,665 downloads). `--download sand_01` → 485,088 B = API size.
- `ambientcg.py --search rock --limit 2` → `totalResults: 76`
  (`Ground111`, `Rock064`); `--id Fabric086` → 1K-JPG zip URL + maps
  (color, displacement, normal, roughness).
- `google_fonts.py` → 3 woff2 files + `fonts.css` (after fixing the
  `:wght@` 400 and the variable-font grouping; md5-verified distinct
  per family, `file` confirms WOFF2).
- `fma.py --probe` → HTTP 404 confirmed; `--candidates` → 4 records.
- `opengameart.py --probe` → HTTP 200 `text/html` for `?format=json`;
  `--records` → 3 records.
- `sketchfab.py --search torso --count 2` → 2 hits; `--download …`
  without a token → clean stop, exit 2 (no fake file).
- `huggingface.py --models image-to-3d --datasets "motion capture"`
  → 3 + 3 records, metadata only.
- `kaggle.py` (check-only) → kaggle.json present, mode 0o600, CLI absent.
- Samples verified: Poly Haven JPGs are 1024×1024 (`file`); AmbientCG zip
  integrity test OK; fonts are WOFF2 (`file`); manifest JSON parses.

## Known deviations from the brief (honest, not hidden)

1. Poly Haven host is `api.polyhaven.com`, not `api.polyhaven.org` (522).
2. FMA has **no** working key flow — the API is shut down, so no
   env-var-key script was written for it; the script documents the
   shutdown + manual curation instead. Writing an `FMA_API_KEY` script
   would have been fabrication.
3. OGA has **no** JSON API — the script proves it and curates records
   instead of scraping.
4. Sketchfab downloads and Kaggle live calls were **not** executed
   (auth-gated / sign-in), exactly as the brief required; their scripts
   contain the gated paths for an authorized run.
5. One AmbientCG search call dropped mid-flight once
   (`RemoteDisconnected`); the script retries once, then errors loudly.
