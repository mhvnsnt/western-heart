# X-ray KO anatomy layers on the live build (2026-11-02)

**Bug.** The live build (GitHub Pages, at its 1 GB cap) does not ship `roster/<fighter>/anatomy/anatomy-layers.json`.
`game/js/xray.js` fetched only the page copy, so on the live site every Rage Art / Urge Smash X-ray KO played the
skin / camera beat with no bone, muscle or organ reveal. Found in the live fight probe after the #1492 deploy:

```
81.6s [http 404] https://mhvnsnt.github.io/western-heart/roster/demonio/anatomy/anatomy-layers.json
81.6s [http 404] https://mhvnsnt.github.io/western-heart/roster/pantera/anatomy/anatomy-layers.json
```

**Fix.** `XraySystem.prefetch` tries the page first, then jsDelivr (`ASSET_CONFIG.jsdelivrBase`), the same order as
`asset-config.js resolveAssetCandidates` and `t3anims.js fetchT7Json`. All 43 files are under 66 KB, and jsDelivr
serves them with `access-control-allow-origin: *` (checked). The page copy still wins on dev / CI / full deploys
(one request, no CDN).

**Check:** `node tools/proof-harness/xray_anatomy_live_check.cjs <site-base> [--block-local] [fighter ...]`

Before (the live site, old `xray.js`):
```
LAYERS {"pantera":null,"demonio":null}
404 https://mhvnsnt.github.io/western-heart/roster/pantera/anatomy/anatomy-layers.json
404 https://mhvnsnt.github.io/western-heart/roster/demonio/anatomy/anatomy-layers.json
FAIL: a fighter has no layers
```

After (this branch served locally, `roster/*/anatomy/` blocked = live conditions):
```
LAYERS {"pantera":{"bone":12,"muscle":25,"organ":0},"demonio":{"bone":12,"muscle":25,"organ":0},"vega":{"bone":12,"muscle":25,"organ":0}}
404 http://127.0.0.1:8765/roster/pantera/anatomy/anatomy-layers.json
200 https://cdn.jsdelivr.net/gh/mhvnsnt/western-heart@main/roster/pantera/anatomy/anatomy-layers.json
...
PASS: every fighter got its anatomy layers
```

Unit test: `test/xray.test.mjs` "live build" section (page first, then jsDelivr; page copy wins; nothing anywhere -> null;
network error -> jsDelivr). 57 passed.

Also seen in the same probe, left as is: `game/js/versus-banter.js` imports `./intro-interactions.js`, which was never
landed; the import is guarded and falls back to the plain versus intro (one 404 per fight start, no effect on play).
