# game-hud

> **A HUD needs a world behind it.** Get web-ready 3D models at
> **[threejsassets.com](https://threejsassets.com/?utm_source=github&utm_medium=readme&utm_campaign=game-hud&utm_content=top-cta)** — 300+ free
> Draco-compressed GLBs and themed packs (city, farm, cozy village, desert
> kingdom, …) that drop straight into Three.js. Made by the same team.

**One HUD markup, 12 skins, zero dependencies.** A complete game UI kit in pure
HTML + CSS + vanilla JS — health bars with damage ghosts, minimap, hotbar,
boss bars, dialogue, inventory, skill trees, and 60+ more components that
restyle completely by swapping a single CSS file.

![The same HUD cycling through all 12 skins](docs/skins.gif)

Works with any engine or framework that renders to a browser: Three.js,
Phaser, PixiJS, Unity WebGL, Godot HTML5, or a plain `<canvas>`.

**[Live demo →](https://threejsassets.github.io/game-hud/)** — switch skins and
try the interactive in-game preview (FPS, battle royale, RTS, MOBA, racing,
tactics, survival, card battler layouts).

## Skins

Futuristic · Modern military · Sci-Fi · Fantasy · Horror · Pixel ·
Cyberpunk · Cartoon · Glass · Steampunk · Rust · Nature

Every skin restyles identical markup purely through CSS variables and
overrides — your HTML never changes.

## Quick start

CDN, no install:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/game-hud/dist/core.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/game-hud/dist/skins/fantasy.css">
<body data-skin="fantasy">
  <div class="vital" data-k="hp">
    <span class="v-ico">♥</span>
    <span class="v-track">
      <span class="v-ghost" style="width:80%"></span><!-- delayed damage drain -->
      <span class="v-fill" style="width:62%"></span>
      <span class="v-num">62 / 100</span>
    </span>
  </div>
</body>
```

Or via npm:

```sh
npm install game-hud
```

```js
import 'game-hud/dist/core.css';
import 'game-hud/dist/skins/cyberpunk.css';
```

Files:

- `dist/core.css` — reset + all component styles + polish layer (required)
- `dist/skins/<name>.css` — one per skin; load one, or several and switch via `<body data-skin="...">`
- `dist/layout.css` — optional full-screen HUD zone layout (`.hud`, `.hz-tl` … `.hz-br`)
- `dist/game-hud.css` — everything bundled

### Fonts

Skins use Google Fonts (Orbitron, Rajdhani, Cinzel, Press Start 2P, …). Add
the `<link>` from [`index.html`](index.html) — or skip it and each skin falls
back to system fonts. For offline games, self-host only the families your
chosen skin uses (see `--font-head` / `--font-body` in the skin file).

## Components

Player vitals (with AAA damage-ghost drain) · compass · currency · minimap ·
quests · pause menu · d-pad + action cluster · XP bar · hotbar · boss bar ·
dialogue · buffs/debuffs · inventory grid with rarity · world map · skill
tree · tabbed menu · tooltips · kill feed · waypoint · cooldown rings · cast
bar · settings widgets · leaderboard · interaction prompts · hearts · ammo ·
wave timer · floating combat text — plus genre suites for RTS/4X/city-builder,
MOBA/battle-royale/fighting/racing/sports, and turn-based/survival/card games.

Markup templates for every component live in [`index.html`](index.html)
(the `r*()` render functions) — copy the HTML shape, style comes from the kit.

## Building

`index.html` is the single source of truth; `dist/` is generated:

```sh
npm run build
```

## Contributing

New skins are the ideal contribution: copy an existing `body[data-skin="..."]`
variable block plus its `<style id="css-skin-...">` overrides in `index.html`,
rename, and re-theme. PRs welcome.

## License

[MIT](LICENSE) © Aron & Sharon / [threejsassets.com](https://threejsassets.com/?utm_source=github&utm_medium=readme&utm_campaign=game-hud&utm_content=license)
