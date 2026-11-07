# Live Cloudflare build: fights bounced on load (2026-11-07)

**What the owner would have hit.** The first real fight on `https://western-heart.pages.dev/game/` (built from main
`7f62516e1`) bounced back to stage select: "Failed to load fighters: Unexpected token '<', \"<!doctype \"... is not
valid JSON".

**Two causes, both fixed:**
1. **Cloudflare Pages single-page-app fallback.** With no top-level `404.html`, Pages answers every missing path with
   `index.html` and HTTP 200 (checked with curl on a made-up path). Demonio's fight model is 28.8 MB, over Pages' 25 MiB
   file limit, so it is not on the site: the loader's page-first candidate got HTML. Fix: `tools/deploy/build_cf_pages.py`
   writes `404.html` (missing paths become real 404s); the deploy's live check now follows Pages' 308 and proves a
   missing file is a 404.
2. **The model loader trusted any 200.** `game/js/assets.js` cached the bytes and parsed them with no fallback, so an
   HTML page failed the whole fight (and sat in the 48 h browser asset cache). Fix: `looksLikeModel()`
   (`game/js/asset-config.js`: GLB magic `glTF` or `.gltf` JSON) gates every cache write and parse; a cached HTML entry
   is skipped, and a non-model or unparseable response moves on to the next candidate (the remote asset server).

**Reproduced and fixed locally** (`tools/proof-harness/fight_entry_probe.mjs`, with the local server answering
Demonio's model with an HTML page + 200, as Cloudflare did; `probe-before-after.json`):
- main's loader: `BOUNCED` with the exact live error;
- fixed loader: `FIGHT` (Demonio loaded from the remote asset server), `after-fight-loads.png`.

Unit tests: `test/model-response-guard.test.mjs`, `test/cf-pages-full-site.test.mjs`.
