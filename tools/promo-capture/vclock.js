// Deterministic frame stepping for headless capture (injected before page scripts).
// Real-time until window.__vclock.begin(); afterwards time only advances via __vclock.step(ms),
// which runs exactly one queued requestAnimationFrame batch per step.
(() => {
  const rRAF = window.requestAnimationFrame.bind(window), rCAF = window.cancelAnimationFrame.bind(window);
  const rPerf = performance.now.bind(performance), rDate = Date.now;
  let virtual = false, vt = 0, dateOff = 0, nextId = 1; let q = new Map();
  const pump = () => { if (!virtual) { const cbs = q; q = new Map(); const t = rPerf(); for (const cb of cbs.values()) { try { cb(t); } catch (e) { console.error(e); } } } rRAF(pump); };
  rRAF(pump);
  window.requestAnimationFrame = cb => { const id = nextId++; q.set(id, cb); return id; };
  window.cancelAnimationFrame = id => { q.delete(id); };
  performance.now = () => virtual ? vt : rPerf();
  Date.now = () => virtual ? Math.round(vt + dateOff) : rDate();
  window.__vclock = {
    begin() { if (virtual) return; vt = rPerf(); dateOff = rDate() - vt; virtual = true; },
    end() { virtual = false; },
    step(ms = 1000 / 30) { vt += ms; const cbs = q; q = new Map(); for (const cb of cbs.values()) { try { cb(vt); } catch (e) { console.error(e); } } return vt; },
    get virtual() { return virtual; }, now: () => vt,
  };
})();
