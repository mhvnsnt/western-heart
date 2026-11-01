# Load times — research, measurements, fixes (2026-11-01)

Owner order (2026-11-01): research load times / load speeds in the GRE
files, in Tekken, in the WWE games, and in industry-standard material,
then pull in and wire up what helps — "especially into the arena…
excruciatingly long… all the waiting times and load times are way too
long."

Lane rule applied throughout: **measure before fixing** — every fix
below names the before-number it improves, and every number in this
document comes from a run this lane actually did (local benches are
labelled as such; phone numbers are the owner's to judge).

---

## 1. Research findings — and what each one changed

### Tekken 7 (GRE `teardown/tekken7-steam/`)

- Content is chunked by role: `pakchunk0` = characters (200 skeletal
  meshes; a base costume is separate face / hair / upper / lower
  meshes), `pakchunk1` = stages; `_P` variants are patch/DLC chunks.
  Moveset/motion data is NOT in the model paks: `tkdata.bin` (305 MB)
  holds indexed per-character motbin banks, loaded by record.
- **What we did with it:** Western Heart already mirrors this shape
  (per-model on-demand loads + separate T3 banks + moveset JSONs).
  The gap is transport, not structure: T7 seeks indexed chunks off a
  local disk; WH downloads whole 20–92 MB GLBs over HTTP. Fixes F1
  (persistent cache) and F3 (meshopt packing) attack exactly that
  transport gap. Splitting fighters into per-part GLBs (T7's
  face/hair/upper/lower) is backlog item B4, not a quick fix.

### WWE 2K19 (GRE `teardown/wwe2k19/` + WH `customization/wwe2k-caw/`)

- CAW is componentized: PACs split `edit/body`, `edit/ch`,
  `edit/head`, `edit/fullbody_type`; a created wrestler is tiny part
  tables (5 CNPC + 5 CNCT in the pull) over shared body templates.
  CAW-STRUCTURE §4 documents the load as sequential layering of small
  pieces over one shared base body.
- **What we did with it:** nothing for fight loads — the suite already
  follows this (shared base-body GLBs are bundled). It confirms the
  direction of backlog B4 (shared parts, per-fighter deltas) for
  customization loading. The teardown's own open item (YOBJ→glTF
  conversion) is the WWE transfer lane's, not this lane's.

### Industry / web (sources in the lane research notes)

- Tekken 8 (Digital Foundry): ~4–5 s character-select → arena on
  consoles; the VS presentation IS the load window; SSD required.
  Pattern copied: Western Heart already prefetches on select
  highlight/lock (`assets.prefetch`, `warmFight`, `preloadStage`) —
  the loader-side API exists, so no new select-screen work was needed
  from this lane.
- Meshoptimizer / glTF Transform guidance: EXT_meshopt_compression
  (geometry, ~2–4× beyond quantization; Wasm decode 1–3 GB/s) is the
  right tool for skinned fighters — Draco compresses static meshes
  only and decodes slower; KTX2/Basis is the texture-side win (VRAM +
  upload), orthogonal to geometry. This matches the repo's own
  gltfpack policy (`tools/gltfpack/README.md`): `-cc` always, `-kn`
  for skinned, `-tc` opt-in per asset with measurement, `-si`
  simplification off by default (owner eye-check).
- Cache practice for versioned assets: long-lived HTTP caching +
  app-controlled Cache Storage. Western Heart's Worker serves
  `Cache-Control: public, max-age=3600` (measured live 2026-11-01)
  and the game's Cache API wrapper is the app-controlled layer — F1
  fixed the wrapper; the Worker header is backlog B2 (the Worker
  source is not in this repo).

## 2. Where the fight-load time actually goes (measured)

Bench setup: local static server + headless Chromium, the game's own
three r160 GLTFLoader and vendored MeshoptDecoder; medians of 3 runs.
Fetch is loopback (not a phone network) unless stated.

| component | before | note |
|---|---|---|
| Kiko Tanaka model download | 92,208,012 B | largest uncompressed main model; header audit: ten of the largest GLBs all raw (no meshopt, no KTX2) |
| Kiko fetch (loopback) | 535 ms | scales with bytes on any real network |
| Kiko parse | 1,010 ms | 1,022,970 verts / 1,964,560 tris |
| Kiko first render (compile+draw) | 2,567 ms | swiftshader on this VM — relative, not phone-absolute |
| Demonio attire1 parse (already meshopt, 28.7 MB) | 4,532 ms | 1,290,149 verts — parse cost is vertex-count-driven |
| Pantera model (7.6 MB bundled) | 345 ms parse | small models are not the problem |
| Remote model download, real Worker | 21.9 MB in 64.4 s; 28.7 MB in 51.4 s | curl from this VM, 2026-11-01 — ~0.5 MB/s effective; **and it repeated every session** (see F1) |
| Fight data chain (serial, after models) | moveset JSONs ~1.0–1.2 MB per fighter + ~1 MB of T3 clips per bank + reaction packs 0.9–6.6 MB per bank | repo tree audit; `game/assets/anim` = 162 MB / 840 files total |
| Stage GLBs | warmed bytes were discarded (cross-origin cache refusal) and re-fetched by the arena builder | code-verified in stages.js/assets.js |

Structural findings (code, main @ d2cd6e20):

- `asset-cache.js` refused every cross-origin URL, so NOTHING served
  from the remote asset base (most of the roster) was ever
  persistently cached; `preloadStage`'s warm fetch was stored under a
  remote URL and likewise discarded.
- `startFight` ran models → full movesets → T3 banks → throw tables
  strictly serially, though the data chain depends only on fighter
  ids. (An earlier same-day LOADSPEED pass had already parallelized
  the lazy modules and deferred form models past fight start.)
- `assets.js`'s header claims the Tripo mains "ship
  meshopt-compressed" — stale: later raw re-exports replaced the
  packed files (see the header audit above).

## 3. What landed

### F1 — persistent cache for remote-base models — PR #1478, MERGED (f7cdd9af)

`game/js/asset-cache.js`: absolute http(s) URLs are cacheable (puts
only ever store buffers the game already fetched through its normal
CORS load, wrapped in a synthetic Response — the old "opaque
response" rationale never applied to this code path). Every entry
carries a 48 h freshness stamp (`x-wh-cached-at`); stale entries are
misses and are evicted — model files are replaced in place at the
same URL when a rig is re-done, so an unbounded cache would serve
replaced rigs forever. Comments updated in `asset-config.js` and
`assets.js`. New tests `game/tests/asset-cache.test.mjs` (7 pass,
locally and in CI).
**Effect:** every non-bundled fighter/stage downloads at most once
per 48 h per device instead of once per session; `preloadStage`
warming now works for remote stage GLBs. Before-number: the measured
51–64 s per-model Worker downloads above, paid per session, now paid
at most once per 48 h per device.

### F2 — fight data chain overlaps model downloads — PR #1479, MERGED (710a8440)

`game/js/main.js` startFight: ensureMovesets + T3 banks + throw
tables/reaction packs run as a concurrent lane with `loadModels`
(the moved blocks are verbatim). Error/retry semantics preserved
(models awaited first, then the lane; fail-soft steps keep their
try/catch).
**Effect:** the data chain's fetch+parse (§2) hides under the model
transfer on cold loads instead of adding to it.

### F3 — Kiko Tanaka meshopt-packed — PR #1482, MERGED (d3908647)

`game/assets/models/kiko-tanaka.glb`: 92,208,012 → 20,234,944 B
(−78.1%), packed with the repo pipeline (gltfpack v0.22, `-cc -kn`,
no `-tc`, no `-si`). Equivalence proven before landing
(`docs/proof/2026-11-01/loadtimes/kiko-equivalence.md` + A/B renders):
vertex/triangle/bone counts identical; 3 embedded textures
byte-identical; world-space geometry aggregates equal to quantization
rounding; per-bone skin-weight mass worst delta 0.02%; bind-pose and
posed renders visually identical. Bench after: fetch 535 → 109 ms
(loopback), parse 1,010 → 1,395 ms (meshopt decode offsets the smaller
read on this CPU — the win is the 72 MB not downloaded: ~2 minutes at
the measured Worker rate).
**Deployment note:** kiko is not shell-bundled; live players receive
the packed bytes once the B2 lane re-uploads the packed file at the
bucket key `game/assets/models/kiko-tanaka.glb`. The repo file merged
here is the source of truth for that upload.

## 4. Ranked backlog

- **B1 — pack the remaining raw mains** (each its own PR with the F3
  equivalence run): kiko-tanaka_alt1 (~91 MB), mariposa +
  mariposa-monarch (~90 MB each), purple-rain-main (~89.5 MB),
  saku-ra-main (~88.7 MB), cyborg-x attire1 (~86 MB), cape-jones
  (~86 MB), pantera leopard-king (~81.6 MB). Expected −70–75 MB per
  model on the wire.
- **B2 — Worker cache headers**: raise `max-age=3600` for versioned
  asset paths (immutable-style). Needs the Worker source (not in this
  repo) or the Cloudflare lane. F1 makes this non-critical: the
  game's own cache now persists regardless of the HTTP header.
- **B3 — KTX2 textures for texture-bound models**: Pantera's 7.6 MB
  is 6.7 MB of embedded images; several packed models are likewise
  texture-bound. Needs the Basis transcoder wired into the loader +
  per-asset measurement (`-tc` grew one textured model +7% in the
  repo's own precedent) — measure per asset, never blanket.
- **B4 — per-part fighter splits** (Tekken/WWE structure): shared
  base + attire parts instead of monolith GLBs. Big refactor; the
  creation suite's part system is the natural home.
- **B5 — shader/texture pre-warm during the VS screen**:
  `renderer.compileAsync` + `initTexture` for the two locked
  fighters — the bench's ~2.5 s first-render line is partly this.
  Loader-side hook exists (warmFight); needs a renderer-side call
  once models land.
- **B6 — T3 bank / anim-data packing**: 162 MB of JSON in
  `game/assets/anim`; per-fight slices are small but parse as text.
  A packed binary or per-bank merged file would cut parse time;
  needs the anim lanes' agreement.
- **B7 — Demonio attire1 parse cost**: 4.5 s parse at 1.29M verts.
  Vertex reduction is a rig decision (owner eye-check), not a loader
  fix. ALSO FLAGGED: the repo lists `roster/demonio/attires/attire1/
  model.glb` at 28,793,068 B while the bucket serves 28,872,600 B for
  the same key — reconcile which file is canonical before any
  Demonio asset work.
- **B8 — full-game A/B harness**: a served-tree Pantera-vs-Demonio
  wall-clock run (baseline vs F1+F2) belongs in
  `tools/proof-harness/`; this lane's per-component benches stand in
  until it exists.

## 5. Method note

All PRs in this lane were built from HEAD-pinned, hash-verified file
copies (an early read of `game/js/main.js` in this lane came back
stale from the egress proxy and was caught by blob-hash comparison
before any edit was based on it). Merges are to main only; deployment
is Ashes' central step, as instructed.
