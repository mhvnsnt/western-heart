# Roster path-fix — thor / cyborgx / mariposa-monarch / buffalo-bill (2026-11-04)

## Verdict

**There is no repo path defect for these four fighters.** On a byte-verified
clean tree of main `fa150d8e` (the PR #1559 merge commit), all four instance
as P1 and fight, with the identity-gated BASICS probe matching or beating
their roster-pass verdicts — with zero manual file placements. The roster
pass's "RESCUED … the game requests `roster/<id>/attires/attire1/model.glb`"
notes (docs/proof/2026-11-03/roster/roster-verdicts-20261103.json) describe
the lane's partial snapshot/vendor trees, not the repo: no request for any
`attire1/model.glb` path for these fighters appears in any of the lane's
server logs (http8766/8767/8771/8791/8793), and the game's actual requests —
in the roster lane's own successful main-tree runs and again on this lane's
clean tree — are the `MODEL_URLS` paths in `game/js/assets.js`, every one of
which exists on main. This doc supersedes the "RESCUED" framing for these
four fighters; their probe verdicts from PR #1559 stand unchanged.

No model file, roster JSON, or config was changed by this lane. The only
genuine gap found is a **bucket upload gap** (Mariposa Slot 3, below) that
no repo change can fix; it belongs to the B2 upload queue.

## How a fight model path actually resolves

1. `game/js/roster-full.js` — fighter entry's `model` field is a MODEL_URLS
   key (e.g. thor → `'thor'`, cyborgx → `'cyborg-x'`,
   mariposa-monarch → `'mariposa-butterfly-default'`,
   buffalo-bill → `'buffalo-bill'`).
2. `game/js/attires.js` — per-fighter attire ladder (MODEL_URLS keys).
   `game/js/characters.js` seats the fighter on the first ladder attire that
   passes the material audit (`game/js/material-status.js`), replacing the
   roster `model` if it is not in the passing ladder.
3. `game/js/assets.js` — `MODEL_URLS[key]` is the URL (relative to `game/`).
4. `game/js/asset-config.js` — `resolveAssetCandidates()`: shell-bundled
   models load local-first; everything else tries the B2 bucket Worker
   (`western-heart-assets.mhvnsnt.workers.dev/<repo-path>`), then the local
   URL, then jsDelivr (which refuses files > 20 MB).

## Per-fighter root cause and evidence

### thor — PERFECT on the clean tree (10/10, zero diffs vs roster pass)
- Chain: fighter `thor` → key `thor` → `../roster/thor/attires/attire1/model-rerig.glb`
  (30,869,328 B, on main; also bucket HTTP 200 at the exact size).
- Clean-tree server log: `GET /roster/thor/attires/attire1/model-rerig.glb 200`.
- The repo also contains `roster/thor/attires/attire1/model.glb`
  (21,459,020 B) and `model-rigged.glb` (20,721,672 B); neither is referenced
  by his MODEL_URLS keys (`thor` → model-rerig; `thor-attire2` →
  attire2/model.glb). The 21 MB model.glb is a stray, not a missing target.
- Probe: 9 strikes correct + 1+3 throw connects (19.3 dmg) — identical
  verdicts to PR #1559. Proof video:
  docs/proof/2026-11-04/roster-pathfix/thor-pathfix-proof-20261104.mp4
  (109 frames, 960×720; sampled frames hash-distinct; mid-fight frame viewed:
  Thor airborne mid-attack vs Pantera on the shrine stage).

### cyborgx (Cape Jones) — 6 correct + throw, zero diffs
- Chain: fighter `cyborgx` → roster model key `cyborg-x` →
  `game/assets/models/cyborg-x.glb`. That key is **material-gate blocked**
  ("cyborg-x": "6 untextured" in material-status.js), and his attires.js
  ladder has exactly one entry, `cape-jones-attire1` →
  `../roster/cyborg-x/attires/attire1/model-rigged.glb` (86,192,130 B, on
  main). characters.js therefore seats him on the ladder model.
- Clean-tree server log: `GET /roster/cyborg-x/attires/attire1/model-rigged.glb 200`.
  That path is also in `SHELL_BUNDLED_MODELS` (asset-config.js) and the
  bucket serves it (200, exact size) — he loads on the live build from the
  shell itself.
- Probe: 1/2/3/4, d/f+2, u/f+4 correct; 1+2, d/f+1, d+1 fire-no-damage;
  1+3 throw connects (17.4 dmg) — verdict-for-verdict identical to PR #1559.
- Note: a video capture was attempted twice; both takes hit the camera-miss
  transient the roster lane also documented for this fighter (fighters leave
  the frame). The captured frames are NOT used as proof; the identity-gated
  probe above is his proof.

### mariposa-monarch — 8 correct + throw, zero diffs; one live-build attire gap (bucket, not repo)
- Chain: fighter `mariposa-monarch` → key `mariposa-butterfly-default` →
  `../roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb`
  (5,840,076 B, on main). Her attires.js ladder (keyed `mariposa-monarch` —
  she is ONE character; see the dedup comment in attires.js) is:
  Slot 1 butterfly-default · Slot 2 `mariposa` (game/assets/models/mariposa.glb,
  90,428,947 B) · Slot 3 `mariposa-monarch` (roster/mariposa/attires/monarch/
  mariposa-monarch-rigged.glb, 90,429,536 B) · Slot 4 `zafina-golden-pharaoh`
  (6,271,368 B) · Slot 5 `zafina` (game/assets/models/zafina.glb, 6,357,128 B).
  Every one of these files exists on main.
- Clean-tree server log: butterfly-default 200; the game also fetched
  Slot 3's mariposa-monarch-rigged.glb during her session → 200. (In the
  roster lane's partial tree that file was absent, hence its 404s there.)
- Probe: 8 correct, 1+2 fires-no-damage, 1+3 throw connects — identical
  verdicts to PR #1559.
- **Live-build status (Pages shell + bucket, checked 2026-11-04):**
  Slot 1: bucket 404 → falls through to jsDelivr (5.84 MB < 20 MB) — loads.
  Slot 2: bucket 200 exact — loads. Slot 3: bucket 404 and 90 MB, so
  jsDelivr refuses it — **Slot 3 cannot load on the current live build.**
  Slot 4: bucket 404 → jsDelivr (6.27 MB) — loads. Slot 5: bucket 200 — loads.
  Her default fight model (Slot 1) works live; only the Slot 3 attire pick
  is broken live. All five paths are listed in
  tools/deploy/r2-upload-manifest.json — Slot 3 (and the Slot 1/4 bucket
  copies) are upload gaps of the same family as the 2026-11-02 Snow Leopard
  case. The fix is a bucket upload (B2 lane; storage-cap blocked), not a
  repo change: the repo file is present, correct, and probe-proven.

### buffalo-bill — 7 correct + throw (totals identical to roster pass)
- Chain: fighter `buffalo-bill` → key `buffalo-bill` →
  `../roster/buffalo-bill/attires/attire3/model-rigged.glb`
  (30,836,224 B, on main; bucket 200 exact). Clean-tree log: 200.
- Attires 1/2: he has **no attires.js ladder and no MODEL_URLS keys for
  attires 1/2** — by design (assets.js + roster-full.js comments: Attire 3
  "Ashes" is his only on-main model; the base key points there). The
  attire1/attire2 `source/` GLBs in the repo are unwired source models.
  Nothing needs adding for attires 1/2; the game never requests them.
- Probe: totals identical to PR #1559 (7 correct, 2 fires-no-damage, throw
  connects). Two per-input boundary swaps vs the roster pass (1+2
  fires-no-damage → correct; d/f+1 correct → fires-no-damage) — the
  0-damage-at-probe-spacing class, not a wiring change: the tree, code, and
  model bytes are identical to the roster pass's main.

## Clean-tree proof method

- Tree assembled from main `fa150d8e80ad801b1c294588f42c4bfd69415544`
  (PR #1559's merge) git-tree listings: game/ (full), roster/ for pantera,
  zen, thor, cyborg-x, zafina, mariposa, buffalo-bill (full), packages/,
  anims/, arenas/, stages/, shared/, moveset-library/ (full), and the
  customization JSON layer + the two non-JSON customization files the game
  fetches outside the creation suite (evidence: the roster lane's request
  log). Every file was placed only after its git blob SHA-1 matched main's
  (local hardlink after hash verification, or blobs-API download verified
  after write; five ~90 MB blobs that choke the base64 API were fetched via
  raw.githubusercontent with resume and SHA-verified the same way).
- Final audit: **3,513 desired files / 0 missing / 0 bad / extras purged** —
  the served tree is exactly main's files, no placements, no edits.
- Probe: the roster pass's own harness (roster_main.py; identity gate
  `p1.char.id` + `roundState === 'fight'`; deterministic stepping), verdicts
  classified with the roster pass's rules (assemble_verdicts.py classify()).
  Full records: docs/proof/2026-11-04/roster-pathfix/clean-tree-probe-verdicts.json.
- Request audit across all four sessions (1,336 requests): every model,
  moveset, portrait, and anim request returned 200. The only 404s:
  `/deploy-manifest.json` (deploy-only artifact, tolerated in dev),
  `game/js/intro-interactions.js` (see side findings), and the two
  anatomy-layers paths below. **No model path 404'd.**

## Side findings (observed, not fixed here — out of this lane's scope)

1. `roster/cyborgx/anatomy/anatomy-layers.json` and
   `roster/mariposa-monarch/anatomy/anatomy-layers.json` 404 in-game: the
   anatomy fetch is keyed by fighter id, but cyborgx's directory is
   `roster/cyborg-x/` and mariposa-monarch has no roster directory (her
   anatomy lives under `roster/mariposa/`). Non-fatal (fights proceed);
   affects the X-ray/anatomy feature only. Same id-vs-directory pattern
   class as the model issue that wasn't — worth a small follow-up if the
   anatomy feature is prioritized.
2. `game/js/intro-interactions.js` does not exist on main;
   `game/js/versus-banter.js` dynamically imports it (guarded, fails soft —
   one of the known guarded/dynamic warnings from the deploy module-graph
   verification). Pre-existing and repo-wide, unrelated to these fighters.

## What this PR changes

Adds this handoff doc, the clean-tree probe records, and Thor's proof
video. No code, config, roster data, or model files are touched, and the
PR #1559 verdict records are left as history — this doc is the correction
layer for the four "RESCUED" notes.
