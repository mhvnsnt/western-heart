/* ============================================================
   WESTERN HEART — UI skin / theme layer (character select)
   ------------------------------------------------------------
   WHY THIS FILE EXISTS
   The select screen's LOOK (colors, fonts, card geometry, texture
   paths) is fully data-driven through this module. select-screen.js
   owns the LOGIC (grid, cursors, confirm flow, 3D previews) and reads
   every visual token from the active skin — so the look can be
   refined or swapped without rewriting the screen logic.

   TEKKEN 8 LOOK — SOURCE (owner 2026-10-22: "pull in like the
   Tekken 8 character select menu and decode it ... get our
   characters put onto the Tekken the most recent Tekken game menu
   grid that you can get a hold of").
   The Steam/depot route for T8 assets is DEAD (owner does not own
   T8 on Steam), so the T8 look here is DECODED FROM PUBLIC
   REFERENCES and recreated with OUR OWN original art — no ripped
   Tekken UI files (owner rule 8: no copyrighted/leaked game files
   in public repos or Pages). The decode is documented in
   docs/select-redesign/T8-GRID-DECODE.md. Community-posted T8 UI
   textures were surveyed as reference only and NOT committed.

   ------------------------------------------------------------
   DROP-IN CONTRACT — how a new skin (or real T8 textures) lands
   ------------------------------------------------------------
   1. Add a new entry to UI_SKINS below (key = skin id, e.g. 't8',
      't7', 'wh-classic'). Every key documented in the SKIN FIELDS
      table is required; a skin missing a field falls back to the
      't8' default for that field (see getSkin).
   2. Textures live under game/assets/ui/<skin-id>/. Naming:
        bg-select.jpg        full-screen select backdrop (optional;
                             the skin's CSS gradient is the fallback)
        card-frame.png       9-slice-ish frame drawn behind each card
                             (optional; CSS frame is the fallback)
        banner-p1.png        name-banner plate art, P1 side (optional)
        banner-p2.png        name-banner plate art, P2 side (optional)
        cursor-p1.png        P1 cursor art (optional; CSS ring fallback)
        cursor-p2.png        P2 cursor art (optional; CSS ring fallback)
        hints-bar.png        bottom hints bar background (optional)
      Any texture may be omitted — the CSS fallback always renders.
      Paths in the skin are RELATIVE TO game/ (e.g.
      'assets/ui/t8/bg-select.jpg').
   3. COPYRIGHT: only commit textures you have reuse rights for
      (original art, licensed packs, or owner-supplied files).
      NEVER commit ripped game UI textures to this public repo.
   4. Activate at runtime: setSkin('t8') (persisted to localStorage
      'wh_ui_skin'); or ?skin=<id> deep link. select-screen.js calls
      applySkin() on build() and onShow() — no other code changes.
   5. Resolution guidance: card portraits are square-ish; provide
      >= 256px. Backdrops >= 1920px wide. Keep total skin payload
      under ~2 MB (Tekken lesson: menus must load fast — the
      select screen may not block on texture downloads; every
      texture below is progressive-enhancement, never a gate).

   SKIN FIELDS
   - id, label               identity
   - colors { p1, p1Soft, p2, p2Soft, bg0, bg1, ink, gold,
              cardBg, cardFrame, hintBg }
   - fonts { display, body } CSS font-family stacks. The T8 look is
                             a bold italic condensed grotesque; we
                             fake the italic with skewX on the
                             display stack (no bundled font file yet —
                             a future skin may point at a woff2 via
                             @font-face and list it here).
   - grid { cardMin, gap, maxCols, maxWidth, cardRadius }
                             cardMin: smallest card width (px);
                             columns = auto-fill; maxCols caps them
                             on very wide screens.
   - banner { slantDeg, nameScale }
   - facts                   ordered [label, fighterField] rows for
                             the T8-style fact block.
   - textures { ... }        optional texture paths (see §2 above).
   ============================================================ */

const DISPLAY_STACK =
  '"Arial Narrow", "Helvetica Neue", Helvetica, Impact, sans-serif';
const BODY_STACK =
  'system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

export const UI_SKINS = {
  /* Tekken 8 decode — recreated look (default). Source: public
     references, docs/select-redesign/T8-GRID-DECODE.md. */
  t8: {
    id: 't8',
    label: 'Tekken 8 grid (recreated)',
    colors: {
      p1: '#ff2d55',      // T8 P1 cursor/label pink-red
      p1Soft: 'rgba(255,45,85,0.55)',
      p2: '#2f9dff',      // T8 P2 cursor/label blue
      p2Soft: 'rgba(47,157,255,0.55)',
      bg0: '#07040d',     // near-black stage
      bg1: '#141024',     // deep blue-purple haze
      ink: '#f4f1ff',
      gold: '#ffb14d',    // WH accent (confirm, timer)
      cardBg: '#101018',
      cardFrame: 'rgba(255,255,255,0.16)',
      hintBg: 'rgba(10,6,18,0.96)',
    },
    fonts: { display: DISPLAY_STACK, body: BODY_STACK },
    grid: {
      cardMin: 76,        // px; auto-fill columns from here
      gap: 6,
      maxCols: 12,        // T8 final: ~12 columns on desktop
      maxWidth: 920,      // px; the grid stays T8-compact, centered
      cardRadius: 4,
    },
    banner: { slantDeg: -7, uppercase: true },
    // T8 fact block rows: [LABEL, fighter field]. 'origin' falls back
    // to canon "Parts unknown" (never invented per select spec).
    facts: [
      ['FIGHTING STYLE', 'style'],
      ['ARCHETYPE', 'archetype'],
      ['ORIGIN', 'origin'],
    ],
    textures: {
      // All optional — CSS fallbacks render when absent.
      // bg: 'assets/ui/t8/bg-select.jpg',
    },
  },
};

export const DEFAULT_SKIN_ID = 't8';
const LS_KEY = 'wh_ui_skin';

/* Resolve a skin id to a full skin object: missing fields fall back
   to the default skin's fields (never undefined at runtime). */
export function getSkin(id) {
  const base = UI_SKINS[DEFAULT_SKIN_ID];
  const s = UI_SKINS[id] || {};
  return {
    ...base,
    ...s,
    colors: { ...base.colors, ...(s.colors || {}) },
    fonts: { ...base.fonts, ...(s.fonts || {}) },
    grid: { ...base.grid, ...(s.grid || {}) },
    banner: { ...base.banner, ...(s.banner || {}) },
    textures: { ...(s.textures || {}) },
    facts: s.facts || base.facts,
  };
}

export function activeSkinId() {
  try {
    const q = new URLSearchParams(location.search).get('skin');
    if (q && UI_SKINS[q]) return q;
    const ls = localStorage.getItem(LS_KEY);
    if (ls && UI_SKINS[ls]) return ls;
  } catch (e) { /* non-browser / private mode */ }
  return DEFAULT_SKIN_ID;
}

export function setSkin(id) {
  if (!UI_SKINS[id]) return false;
  try { localStorage.setItem(LS_KEY, id); } catch (e) { /* ignore */ }
  const root = document.getElementById('screen-select');
  if (root) applySkin(root, getSkin(id));
  return true;
}

/* Push every visual token into CSS custom properties on the select
   root. select.css consumes ONLY these vars for skin-driven values —
   that is the whole swap mechanism. */
export function applySkin(root, skin) {
  const c = skin.colors, g = skin.grid;
  const v = {
    '--sk-p1': c.p1,
    '--sk-p1-soft': c.p1Soft,
    '--sk-p2': c.p2,
    '--sk-p2-soft': c.p2Soft,
    '--sk-bg0': c.bg0,
    '--sk-bg1': c.bg1,
    '--sk-ink': c.ink,
    '--sk-gold': c.gold,
    '--sk-card-bg': c.cardBg,
    '--sk-card-frame': c.cardFrame,
    '--sk-hint-bg': c.hintBg,
    '--sk-display': skin.fonts.display,
    '--sk-body': skin.fonts.body,
    '--sk-card-min': `${g.cardMin}px`,
    '--sk-grid-gap': `${g.gap}px`,
    '--sk-grid-maxw': `${g.maxWidth}px`,
    '--sk-card-radius': `${g.cardRadius}px`,
    '--sk-slant': `${skin.banner.slantDeg}deg`,
  };
  for (const [k, val] of Object.entries(v)) root.style.setProperty(k, val);
  root.dataset.skin = skin.id;
  // Optional backdrop texture: progressive enhancement, never a gate.
  if (skin.textures.bg) {
    root.style.setProperty('--sk-bg-url', `url('${skin.textures.bg}')`);
  } else {
    root.style.removeProperty('--sk-bg-url');
  }
}
