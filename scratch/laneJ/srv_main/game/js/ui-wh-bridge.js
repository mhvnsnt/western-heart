/* ============================================================
   WESTERN HEART — ui-wh bridge (toggle: ?ui=wh, or localStorage wh_ui=wh;
   ?ui=classic forces the old menu). The new menu/UI (game/ui-wh/) runs in a
   transparent full-screen iframe over the 3D canvas. Menus → select → VS run
   inside it; the fight runs in the real Game; live HP / meter / timer / rounds /
   combo are posted into the ui-wh HUD; Esc → ui-wh pause; match end → ui-wh
   results. The classic DOM menus stay in index.html untouched as the fallback.
   ============================================================ */
export function whUiEnabled() {
  const q = new URLSearchParams(location.search).get('ui');
  if (q === 'classic') return false;
  if (q === 'wh') return true;
  try { return localStorage.getItem('wh_ui') === 'wh'; } catch { return false; }
}

export function mountWhUi(api) {
  const { game, ui, show, startFight, ROSTER } = api;
  const f = document.createElement('iframe');
  f.id = 'wh-ui';
  const tq = new URLSearchParams(location.search).get('title');  // title variant pass-through (v1|v2|v3)
  f.src = 'ui-wh/index.html?embed=1' + (tq ? '&title=' + encodeURIComponent(tq) : '') + '#title';
  f.setAttribute('allowtransparency', 'true');
  Object.assign(f.style, { position: 'fixed', inset: '0', width: '100%', height: '100%', border: '0', zIndex: '50', background: 'transparent' });
  document.body.appendChild(f);
  document.body.classList.add('wh-ui');
  const css = document.createElement('style');
  css.textContent = `body.wh-ui #hud .hud-top, body.wh-ui #combo-pop, body.wh-ui #tap-to-start { display:none !important; }`;
  document.head.appendChild(css);
  show('none');

  const norm = (s) => String(s).replace(/[^a-z0-9]/g, '');
  const find = (id) => ROSTER.find((c) => norm(c.id) === norm(id)) || { id: String(id), modelPending: true }; // no Pantera fallback (t183u)
  const post = (m) => f.contentWindow && f.contentWindow.postMessage({ src: 'wh-game', ...m }, '*');
  let last = null, hudT = null, t0 = 0, maxCombo = 0;

  const fighting = (on) => {
    f.style.pointerEvents = on ? 'none' : 'auto';
    if (on) { f.blur(); window.focus(); }
  };
  const stopHud = () => { clearInterval(hudT); hudT = null; };
  const startHud = () => {
    stopHud();
    hudT = setInterval(() => {
      const g = game; if (!g.p1 || !g.p2) return;
      const pf = (x) => ({ hp: x.hp, maxHp: x.maxHp, meter: x.meter, maxMeter: x.maxMeter });
      post({ type: 'hud', p1: pf(g.p1), p2: pf(g.p2), timer: Math.max(0, Math.ceil(g.timer)), wins: g.wins, round: g.round });
    }, 100);
  };

  async function fight(p1, p2) {
    last = { p1, p2 }; maxCombo = 0;
    post({ type: 'fighters', p1, p2 });
    const a = find(p1), b = find(p2);
    if (a.modelPending || b.modelPending) { console.warn('[WH] bridge: model-pending fighter, fight not started', a.id, b.id); post({ type: 'show', screen: 'select' }); return; }
    fighting(true);
    await startFight(a.id, b.id);
    if (!game.running) { fighting(false); post({ type: 'show', screen: 'select' }); return; }
    t0 = performance.now();
    post({ type: 'show', screen: 'hud' });
    startHud();
  }
  function toMenu(screen) {
    stopHud(); game.leaveFight(); fighting(false); show('none');
    post({ type: 'show', screen });
  }

  const origCombo = ui.combo.bind(ui);
  ui.combo = (n) => { origCombo(n); maxCombo = Math.max(maxCombo, n); post({ type: 'combo', n }); };
  ui.matchOver = (playerWon) => {
    const w = { ...game.wins }; stopHud(); fighting(false); show('none');
    const s = Math.round((performance.now() - t0) / 1000);
    post({ type: 'results', winner: playerWon ? last.p1 : last.p2,
      stats: [['RESULT', playerWon ? 'P1 WINS' : 'CPU WINS'], ['ROUNDS', `${w.p1} – ${w.p2}`],
        ['TIME', `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`], ['MAX COMBO', `${maxCombo} HITS`]] });
  };

  const pause = () => {
    if (!game.running || game.paused) return;
    game.paused = true; fighting(false); post({ type: 'show', screen: 'pause' });
  };
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && f.style.pointerEvents === 'none') pause(); });

  addEventListener('message', (e) => {
    const m = e.data || {}; if (m.src !== 'wh-ui') return;
    if (m.type === 'fight') fight(m.p1, m.p2);
    else if (m.type === 'pause') pause();
    else if (m.type === 'resume') { game.paused = false; fighting(true); post({ type: 'show', screen: 'hud' }); }
    else if (m.type === 'restart' || m.type === 'rematch') { stopHud(); game.leaveFight(); post({ type: 'show', screen: 'vs' }); setTimeout(() => fight(last.p1, last.p2), 1200); }
    else if (m.type === 'select') toMenu('select');
    else if (m.type === 'menu') toMenu('menu');
  });
  window.__whUi = { frame: f, fight, pause };
  return f;
}
