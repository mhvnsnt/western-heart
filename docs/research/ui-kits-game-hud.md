# Research: game UI kits (dark/gold fighting-game aesthetic)

## What it is
The Creation Suite (`tools/creation-suite/`, web app) needs a visual upgrade
toward a dark/gold fighting-game aesthetic. Evaluated open-source game UI kits.

## Candidates
| Kit | License | Verdict |
|---|---|---|
| **threejsassets/game-hud** (https://github.com/threejsassets/game-hud) | **MIT** | **PULLED.** Pure HTML+CSS+vanilla JS, zero deps, 60+ components (health bars, boss bars, dialogue, inventory, skill trees), 12 CSS skins. Its **Fantasy skin is already dark+gold** (`#f2b01e`/`#e89b12` on `#211d18`). Built for Three.js web games — matches our stack. |
| bakeolam-beep/gaming-hud | MIT | Cyberpunk HUD, wrong aesthetic. Skipped. |
| Kenney UI packs (CC0) | CC0 | Cartoon style, wrong aesthetic for dark/gold. Noted, not pulled. |

## Where landed
- `tools/creation-suite/ui-kit/game-hud/` — `dist/` (built CSS + 12 skins), `index.html` (markup templates), `LICENSE-MIT.txt`, upstream `README.md`, `WH-README.md` (Western Heart wiring notes).

## Follow-ups (wiring lane)
- Author a `western-heart` skin derived from the Fantasy skin with our exact gold + typography.
- Bind health-bar/boss-bar components to the Creation Suite viewer.
