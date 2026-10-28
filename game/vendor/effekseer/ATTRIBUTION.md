# Effekseer — vendored runtime (MIT)

**What:** Effekseer 1.80.7 — the open-source particle effects engine
(https://github.com/effekseer/Effekseer). Used as Western Heart's GPU
particle runtime for hit impacts, kick wind trails, KO blasts, and
Soul Urge visual cues.

**Source:** Official release asset `EffekseerForWebGL1.80.7.zip`
(downloaded 2026-10-23 from
https://github.com/effekseer/Effekseer/releases/download/1807/EffekseerForWebGL1.80.7.zip)
plus the MIT license text from https://api.github.com/licenses/mit.

**Files in this directory:**
- `effekseer.min.js` — official WASM loader + JS bridge (unmodified)
- `effekseer.wasm` — official compiled runtime (unmodified)
- `effekseer.d.ts` — official TypeScript definitions (unmodified)
- `LICENSE` — canonical MIT license text

**Sample effects:** `../assets/fx/effekseer/` holds the official
EffekseerForWebGL test resources (`tests/Resources`: ToonHit, Blow1,
Light, Cure1, Arrow1, ToonWater `.efkefc` + textures), unmodified,
from https://github.com/effekseer/EffekseerForWebGL.

**License:** MIT. © Effekseer contributors. No modifications made to
the vendored binaries; see LICENSE for the full text.

**Version note:** 1.80.7 was the latest release on 2026-10-23.
