# Settings > Dev Sandbox (Oct 14, 2026)

**What**: the main menu's OPTIONS item now opens an Options screen. It has a **DEV SANDBOX** submenu page that embeds the Western Heart Dev Sandbox (repo `mhvnsnt/physics-playground-pwa`, live at https://physics-playground-pwa.pages.dev/), plus BACK.
**Files**: `game/ui-wh/index.html` (new sections `options` and `devsandbox`), `game/ui-wh/ui.js` (OPTIONS list, routing, lazy iframe, Esc/back handling), `game/ui-wh/ui.css` (styles plus a mobile/portrait layout).
**Navigation**: Menu → OPTIONS → DEV SANDBOX. BACK or Esc returns to Options, and Esc again returns to Menu. "Open full screen" opens the sandbox in a new tab.
**Rules**: Scarlett and Madelyn are sandbox-only test assets, not roster fighters; the roster is unchanged. The iframe only loads while the page is open.
**Verified**: headless Chromium at 1280x720 and 412x915. Routes options→devsandbox→back→esc all work with 0 page errors. Screenshots are in the PR.
