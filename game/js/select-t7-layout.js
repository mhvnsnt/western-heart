/* T7 select proportion system (2026-10-23, owner t182u).
   Measured from the real Tekken 7 select textures (private repo
   mhvnsnt/game-reverse-engineering teardown/tekken7-steam/pakchunk0_P/
   textures/UI_common/flash/SW_UI_CharacterSelect, 1920x1080 authoring):
     card panel Rep_CS_CH_PANEL_*  96x148 tex, 91x129 drawn  -> aspect 0.705
     card gap ~4px; roster band = 2 rows across the full width (landscape)
     P1/P2 slot frames SlotRed/Blue_OnGradient 208x336, FrontPanel 184x316
   Phones: every card must be on screen at once (no scrolling, CONFIRM
   always visible), so the fitter picks the column count that gives the
   biggest T7-aspect card inside the grid box. Landscape keeps T7's
   2-row band when it fits (cards >= 30px), portrait stacks more rows
   under the stage like the owner's Brutal Fist select. */
export const T7 = { ref: [1920, 1080], card: [91, 129], gap: 4, slot: [208, 336] };
const ASPECT = T7.card[0] / T7.card[1];

export function fitGrid(n, W, H, gap) {
  let best = { cols: n, w: 0 };
  for (let cols = 1; cols <= n; cols++) {
    const rows = Math.ceil(n / cols);
    const w = Math.min((W - gap * (cols - 1)) / cols, ((H - gap * (rows - 1)) / rows) * ASPECT);
    if (w > best.w) best = { cols, rows, w };
  }
  best.w = Math.floor(best.w); best.h = Math.floor(best.w / ASPECT);
  return best;
}

export function layoutSelect() {
  const root = document.getElementById('screen-select');
  const wrap = root && root.querySelector('.grid-wrap');
  const grid = root && root.querySelector('#char-grid');
  if (!wrap || !grid || !root.classList.contains('active')) return;
  const n = grid.querySelectorAll('.char-card').length;
  if (!n) return;
  const r = wrap.getBoundingClientRect();
  const cs = getComputedStyle(wrap);
  const W = r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const H = r.height - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const s = Math.min(innerWidth / T7.ref[0], innerHeight / T7.ref[1]);
  const gap = Math.max(2, Math.round(T7.gap * s * 2));
  const f = fitGrid(n, W, H, gap);
  root.style.setProperty('--t7-cols', f.cols);
  root.style.setProperty('--t7-card-w', f.w + 'px');
  root.style.setProperty('--t7-card-h', f.h + 'px');
  root.style.setProperty('--t7-gap', gap + 'px');
  root.dataset.t7Grid = `${f.cols}x${f.rows}`;
}

let raf = 0;
const schedule = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(layoutSelect); };
addEventListener('resize', schedule);
addEventListener('orientationchange', schedule);
const watch = () => {
  const root = document.getElementById('screen-select');
  if (!root) return setTimeout(watch, 200);
  new MutationObserver(schedule).observe(root, { attributes: true, attributeFilter: ['class'] });
  new MutationObserver(schedule).observe(root.querySelector('#char-grid'), { childList: true });
  schedule();
};
watch();
