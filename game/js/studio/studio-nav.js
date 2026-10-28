/* Controller + keyboard navigation for the studios: d-pad/arrows move
   focus spatially, A/Enter activates, B/Esc goes back, LB/RB (Q/E) cycle
   tabs, left/right on a focused slider nudges it. Touch works natively. */
export function initNav(opts){ const { onBack, onTab } = opts;
  const focusables = () => [...document.querySelectorAll('button:not([disabled]),input[type=range],input[type=file]+label')].filter(e => e.offsetParent);
  function move(dx, dy){
    const all = focusables(); const cur = document.activeElement;
    if (!all.includes(cur)) { all[0] && all[0].focus(); return; }
    const r = cur.getBoundingClientRect(); const cx = r.left + r.width/2, cy = r.top + r.height/2;
    let best = null, bd = 1e9;
    for (const e of all) { if (e === cur) continue; const q = e.getBoundingClientRect();
      const ex = q.left + q.width/2 - cx, ey = q.top + q.height/2 - cy;
      if (dx && Math.sign(ex) !== dx) continue; if (dy && Math.sign(ey) !== dy) continue;
      if (dx && Math.abs(ex) < 4) continue; if (dy && Math.abs(ey) < 4) continue;
      const d = dx ? Math.abs(ex) + Math.abs(ey) * 2.5 : Math.abs(ey) + Math.abs(ex) * 2.5;
      if (d < bd) { bd = d; best = e; } }
    if (best) { best.focus(); best.scrollIntoView({ block: 'nearest' }); }
  }
  function nudge(dir){ const e = document.activeElement; if (e && e.type === 'range') { const st = +e.step || 0.01; e.value = (+e.value) + dir * st * 5; e.dispatchEvent(new Event('input', { bubbles: true })); return true; } return false; }
  addEventListener('keydown', ev => {
    const k = ev.key;
    if (k === 'ArrowLeft') { if (!nudge(-1)) move(-1, 0); ev.preventDefault(); }
    else if (k === 'ArrowRight') { if (!nudge(1)) move(1, 0); ev.preventDefault(); }
    else if (k === 'ArrowUp') { move(0, -1); ev.preventDefault(); }
    else if (k === 'ArrowDown') { move(0, 1); ev.preventDefault(); }
    else if (k === 'Escape' || k === 'Backspace') { onBack(); ev.preventDefault(); }
    else if (k === 'q' || k === 'Q') onTab(-1); else if ((k === 'y' || k === 'x') && opts.onFace && !(ev.target && ev.target.tagName === 'INPUT' && ev.target.type === 'text')) opts.onFace(k); else if (k === 'e' || k === 'E') onTab(1);
  });
  const prev = {}; let rep = 0;
  function poll(t){
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (const p of pads) { if (!p) continue;
      const b = i => p.buttons[i] && p.buttons[i].pressed;
      const ax = p.axes[0] || 0, ay = p.axes[1] || 0;
      const st = { u: b(12) || ay < -.6, d: b(13) || ay > .6, l: b(14) || ax < -.6, r: b(15) || ax > .6, a: b(0), bk: b(1), x: b(2), y: b(3), lb: b(4), rb: b(5) };
      const edge = k => st[k] && !prev[k];
      const held = k => st[k] && prev[k] && t - rep > 160;
      if (edge('u') || held('u')) { move(0, -1); rep = t; }
      if (edge('d') || held('d')) { move(0, 1); rep = t; }
      if (edge('l') || held('l')) { if (!nudge(-1)) move(-1, 0); rep = t; }
      if (edge('r') || held('r')) { if (!nudge(1)) move(1, 0); rep = t; }
      if (edge('a') && document.activeElement) document.activeElement.click();
      if (edge('bk')) onBack(); if (edge('x') && opts.onFace) opts.onFace('x'); if (edge('y') && opts.onFace) opts.onFace('y'); if (edge('lb')) onTab(-1); if (edge('rb')) onTab(1);
      Object.assign(prev, st); break; }
    requestAnimationFrame(poll);
  }
  requestAnimationFrame(poll);
}
