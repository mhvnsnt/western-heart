/* ============================================================
   WESTERN HEART — loadperf: menu load-speed instrumentation
   (loadspeed lane, 2026-10-22).

   Tiny, dependency-free timing helper. Marks the menu transitions
   the owner complained about ("menus take forever to load") so
   before/after numbers come from the real browser, not guesses:

     boot        -> main menu interactive
     menu        -> character select interactive
     select      -> stage select interactive
     highlight   -> 3D preview ready

   Usage: loadperf.mark('menu-interactive') etc.; then
   window.__loadperf.summary() prints a console table, or read
   window.__loadperf.marks directly in a QA pass.
   ============================================================ */
const marks = {};
const _t0 = (typeof performance !== 'undefined' && performance.now)
  ? performance.now.bind(performance) : Date.now;
/* boot-start defaults to the inline <head> stamp (window.__whBootT0,
   set before any CSS/JS loads) so "boot -> menu" spans the real
   navigation-to-interactive window, not just module evaluation. */
try {
  marks['boot-start'] = (typeof window !== 'undefined' && window.__whBootT0)
    || _t0();
} catch { marks['boot-start'] = _t0(); }

export function mark(name) {
  marks[name] = _t0();
  if (typeof console !== 'undefined' && console.debug) {
    console.debug(`[WH-loadperf] mark ${name}`);
  }
}
/* Milliseconds between two marks (null when either is missing). */
export function delta(a, b) {
  if (marks[a] == null || marks[b] == null) return null;
  return marks[b] - marks[a];
}
/* The four owner-facing transitions, each measured to the frame
   where the new screen is actually painted (call sites pass a
   requestAnimationFrame tick after the DOM switch). */
export function transitions() {
  const t = (a, b) => { const d = delta(a, b); return d == null ? null : Math.round(d); };
  return {
    'boot -> menu (ms)': t('boot-start', 'menu-interactive'),
    'menu -> select (ms)': t('select-open', 'select-interactive'),
    'select -> stage (ms)': t('stage-open', 'stage-interactive'),
    'highlight -> preview (ms)': t('preview-start', 'preview-ready'),
  };
}
export function summary() {
  const rows = transitions();
  if (typeof console !== 'undefined' && console.table) console.table(rows);
  return rows;
}
export const loadperf = { mark, delta, transitions, summary, marks };
if (typeof window !== 'undefined') window.__loadperf = loadperf;
