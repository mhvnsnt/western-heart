// theme.js — binds theme/theme.json asset slots to the DOM.
// A slot with a real extracted file becomes a CSS variable / img src /
// @font-face. A slot without one leaves the labeled CSS reconstruction
// fallback in suite2.css untouched. Nothing here invents art.
// Dynamic rows (re-rendered on navigation) read URLs through
// themeSlotUrl/themeIconUrl instead of the one-time DOM binding.
const SLOT_URLS = {};
const ICON_URLS = {};
export function themeSlotUrl(name) { return SLOT_URLS[name] || null; }
export function themeIconUrl(name) { return ICON_URLS[name] || null; }

export async function loadTheme() {
  let manifest = { slots: {} };
  try {
    const res = await fetch(new URL('./theme/theme.json', import.meta.url));
    if (res.ok) manifest = await res.json();
  } catch (e) { /* fall back to reconstruction styling */ }
  const root = document.documentElement;
  const slots = manifest.slots || {};
  const bound = [], fallback = [];
  for (const [name, slot] of Object.entries(slots)) {
    const usable = slot && slot.file && slot.status === 'extracted';
    if (name === 'fontDisplay') {
      if (usable) {
        const st = document.createElement('style');
        st.textContent = `@font-face { font-family: 'CSThemeFont'; src: url("${new URL('./theme/' + slot.file.split('/').pop(), import.meta.url)}") format("woff2"); }`;
        document.head.appendChild(st);
        root.style.setProperty('--font-display', "'CSThemeFont', 'Arial Narrow', sans-serif");
        bound.push(name);
      } else fallback.push(name);
      continue;
    }
    if (usable) {
      const url = new URL('./theme/' + slot.file.replace(/^\.\//, ''), import.meta.url).href;
      SLOT_URLS[name] = url;
      root.style.setProperty('--art-' + name, `url("${url}")`);
      document.querySelectorAll(`img.glyph[data-glyph="${name}"]`).forEach((img) => { img.src = url; img.hidden = false; });
      bound.push(name);
    } else {
      fallback.push(name);
    }
  }
  for (const [name, icon] of Object.entries(manifest.icons || {})) {
    if (icon && icon.file && icon.status === 'extracted') {
      ICON_URLS[name] = new URL('./theme/' + icon.file.replace(/^\.\//, ''), import.meta.url).href;
      bound.push('icon:' + name);
    } else fallback.push('icon:' + name);
  }
  return { bound, fallback, manifest };
}
