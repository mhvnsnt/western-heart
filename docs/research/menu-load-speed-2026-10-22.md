# Menu Load Speed — audit, Tekken techniques, fixes (2026-10-22)

**Lane:** loadspeed (worker 4 of 4, character-select overhaul)
**Owner instruction:** "we need to make the menus look a little cleaner and load a little faster because they take forever to load and all of that I don't know what Tekken does about that in their files and all the tear down games do about that in their files how we can pull it in from those"

## 1. Audit — what the menu path actually loads

Measured with `tools/loadbench/` (Node harness: serves `game/` over HTTP,
replays each transition's exact fetch sequence with browser-like 6-way
parallelism, plus real V8 parse timing). Localhost numbers are lower bounds —
a phone on 10 Mbps sees far worse, especially on the multi-MB GLB fetches.

### BEFORE (base e8562339)

| Transition | Files | Bytes | Wall (localhost) | Notes |
|---|---|---|---|---|
| T1 boot → menu interactive | 43 | 2.00 MB | ~330 ms + ~105–210 ms V8 parse | 39 JS modules incl. three.module.js (1.27 MB); ALL fight systems parsed before first paint |
| T1b boot async fetches | 13 | 0.39 MB | ~50 ms | 7 real-moveset JSONs (~300 KB), moveset index, facing table, tripo list, title-bg — contends with T1 |
| T2 menu → char select | 4 | **26.13 MB** | ~330–550 ms localhost | `preloadAll()` fired 4 base GLBs the instant select opened — **~21 s of pipe saturation on 10 Mbps**, starving every later fetch |
| T3 select → stage select | 41 | 3.25 MB | ~260–300 ms | 41 separate thumb PNG requests (+17 more that 404'd) |
| T4 card tap → 3D preview | 1 | 17.17 MB | ~210–360 ms | full Tripo GLB per tap (~14 s on 10 Mbps); superseded taps kept downloading |
| T4b T3 anim bank per preview | 34 | 3.24 MB | ~200–320 ms | already cached per bank (`_t3clipCache`) — fine |

Biggest offender by far: **T2**. The select screen itself painted instantly
(DOM was ready), but the 26 MB prefetch stampede made everything after it —
preview taps, CONFIRM — crawl on real networks. That is the "takes forever".

## 2. What the teardown games do (and what we pulled in)

| Technique (source) | Applicable to our no-build Three.js game? | Pulled in? |
|---|---|---|
| **Tekken 3 BNS: index first, records on demand** (`teardown/tekken3/docs/TEKKEN3-ARCHITECTURE.md` — "the BNS table is an index — the game loads specific records on demand") | Yes — the core idea behind `game/js/lazy.js` | **Yes.** Boot graph 39 → 34 files (−0.22 MB JS): `fighter.js`, `movesets.js`, `t3anims.js`, `transform-cinematic.js` (via `game.js` startMatch), `modes.js`, `heartmind.js`, `episodes.js` now `import()` on first use, warmed during idle. Already-present on-demand GLB loading kept. |
| **Tekken 3: don't load fighters at boot** (same doc; already applied in `assets.js`/`main.js` comments) | Already applied | Kept + extended: real-moveset JSONs (~300 KB) moved from boot module-eval to `startFight` |
| **Background streaming while the player idles** (general fighting-game practice; Tekken streams the next fight's data behind VS screens) | Yes via `requestIdleCallback` | **Yes.** Base-model warm moved off select-open into the idle lane (`assets.preloadBaseIdle`); fight-only JS modules warmed via `warmIdle()` at boot end |
| **Priority lanes: user input preempts background work** | Yes via `AbortController` | **Yes.** `loadModels` is now fetch + `parseAsync` (abort-aware); a card tap aborts superseded preview downloads AND the idle base warm, so the tapped model gets the full pipe |
| **Urban Reign VGS: UI screens as ONE tiled texture atlas** (`teardown/urban-reign/UI-SYSTEM.md` — every menu screen is a grid of tiles in a single `.vgs`) | Yes | **Yes.** 41 stage thumbs → one 3360×1620 `atlas.png` + `atlas.json`; stage-select thumb requests 41 → 2 (atlas + its JSON); 17 stages that never had thumbs keep the swatch fallback (they 404'd before) |
| **Compressed delivery (meshopt/KTX2/WebP)** (`docs/research/procgen-asset-pipelines/06-gltf-web-delivery-2026.md`) | Partially (meshopt already on for Tripo GLBs) | Not in this lane — the GLB recompression pipeline belongs to the model crew; noted as the next biggest lever (some GLBs are 40–90 MB) |
| **Proxy-first then refine (LOD)** | Possible (portrait plate → 3D) | Not needed — the plate (name/stats/portrait) already paints instantly; the 3D pane was the only waiter and now gets full bandwidth |
| **Persistent asset cache across sessions (Tekken "install")** | IndexedDB GLB cache | Not built — HTTP caching already covers repeat visits; in-memory `assets.gltfs` covers menu↔fight revisits within a session. Flagged as follow-up if the owner wants offline-first |

## 3. What changed (files)

- `game/js/lazy.js` (new) — cached dynamic importers + `warmIdle()`
- `game/js/loadperf.js` (new) — `boot→menu`, `menu→select`, `select→stage`, `highlight→preview` marks; `window.__loadperf.summary()`
- `game/js/main.js` — deferred `ModeController` (built on first mode tap), moveset JSONs → `startFight`, `preloadAll()` → `preloadBaseIdle(hasCustom)`, stage-thumb atlas renderer, timing marks, `?fighter` behavior unchanged
- `game/js/assets.js` — `loadModels` rewritten as abort-aware fetch + `parseAsync` (same ingest path: clip pinning, grounding, facing); in-flight dedup; idle/user lanes with preemption; `preloadAll()` kept as back-compat alias
- `game/js/select-screen.js` — preview loads abort on supersede; T3/fighter/moveset imports → lazy inside `showOnSide`
- `game/js/menus.js` — `modes.js`/`heartmind.js`/`episodes.js` → lazy on first use
- `game/js/game.js` — `fighter.js` → lazy inside `startMatch` (async now; all callers already await it)
- `game/index.html` — earliest-possible boot stamp for loadperf
- `game/assets/stages/thumbs/atlas.png` + `atlas.json` (generated by `tools/loadbench/` PIL script; committed artifacts)
- `tools/loadbench/` — `server.mjs`, `bench.mjs`, `trace.mjs`, manifests, BEFORE/AFTER logs (re-runnable)

## 4. AFTER numbers (same harness, same conditions)

| Transition | BEFORE | AFTER | Delta |
|---|---|---|---|
| T1 boot blocking JS | 43 files, 2.00 MB | 38 files, **1.78 MB** | −0.22 MB, −5 modules parsed before first paint |
| T1b boot async | 13 files, 0.39 MB | 3 files, **0.05 MB** | −0.34 MB (moves JSON → fight time; index → idle) |
| T2 menu → select | 26.13 MB fired on open | **0 bytes blocking** (24.07 MB idle lane; `custom` skipped when absent saves 2.2 MB) | select paints instantly; pipe free for first tap |
| T3 stage thumbs | 41 files, 3.25 MB | **2 files, 3.34 MB** | −39 requests |
| T4 preview | 17.17 MB, no abort | 17.17 MB **+ abort superseded + preempts idle** | doomed downloads cancelled; full bandwidth per tap |

Projected real-world (10 Mbps): T2's ~21 s of pipe saturation is gone from the
critical path; a Tripo preview tap drops from ~14 s (contended) toward ~14 s
uncontended — the remaining lever is GLB size (model-crew pipeline work).

## 5. Verification

- `node --check` on all 8 touched JS files: pass
- Import-graph trace: deferred modules absent from boot graph
- Node harness against real served GLBs: fetch+parse+ingest OK (progress
  callbacks fire), mid-flight abort rejects cleanly with nothing cached,
  concurrent loads dedup to one fetch, idle lane warms bases, `lazy.*`
  modules load with caching
- Stage atlas: 41/58 stages tiled; 17 thumb-less stages keep swatch fallback
  (identical to old `onerror` behavior)
- In-browser timing: `loadperf` marks wired; run `window.__loadperf.summary()`
  in a live session for device-real numbers (no live browser on this worker)

## 6. Not done / follow-ups

- GLB recompression (meshopt/KTX2 across the 40–90 MB models) — model pipeline crew
- IndexedDB persistent GLB cache — flagged, not built
- Portrait-card lazy work belongs to worker 1's grid redesign (not touched)
- Game inputs untouched (deferred per owner)
