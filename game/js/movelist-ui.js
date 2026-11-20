/* ============================================================
   WESTERN HEART — Movelist UI (in-game move reference)
   Owner-approved 2026-10-22 (learning tools: YES, ALL).
   The pause-menu movelist, Tekken-style: every move the vessel can
   perform, listed with notation, name, damage, startup, and properties —
   read live from the loaded moveset (movesets.js), never a stale copy.
   Features: filter by input type (strikes / strings / throws / specials),
   search by name, sort by damage or startup. Touch-friendly rows
   (min 44px targets). Pure data builders — unit-testable, no DOM in
   the core; renderMovelist() builds the overlay.
   WH canon mapping (PROPOSED — needs owner approval):
     "INSCRIPTIONS" — the Trial's stone tablets listing each vessel's
     techniques. Same canon source as Combo Trials ("Trial Inscriptions"):
     the stones SHOW (movelist) and then TEST (trials). One system, two
     faces. Alternative: "Soul Manual" — flagged for owner call.
   ============================================================ */

import { getFighterMoveset } from './movesets.js';
import { installAddedMoves, fullMoveList } from './full-movelist.js';

/* Flatten a moveset into sorted, filterable rows. Pure. */
export function movelistRows(fighterId) {
  const ms = getFighterMoveset(fighterId);
  if (!ms || !ms.moves) return [];
  // pt217u: FULL list = base moves + EMWH additions (魂 ACTION, KESSHOU, 九魂解放, 霊放, 試練の封),
  // canon-named through tools/canon, one row per reachable input.
  installAddedMoves(fighterId, ms);
  if (ms.slots) return fullMoveList(fighterId, ms).map(r => ({ ...r, notation: r.notation, knock: 0, heavy: false, limb: '' }));
  const rows = [];
  for (const [key, m] of Object.entries(ms.moves)) {
    rows.push({ key, notation: m.input || key, name: m.name || key, damage: m.damage || 0,
      startupF: m.startup != null ? Math.round(m.startup * 60) : null, moveClass: m.move_class || 'strike',
      limb: m.limb || '', heavy: !!m.heavy, knock: m.knock || 0 });
  }
  return rows;
}

export function filterMovelist(rows, { query = '', cls = 'all', sort = 'notation' } = {}) {
  let r = rows;
  if (cls !== 'all') r = r.filter(x => x.moveClass === cls);
  if (query) {
    const q = query.toLowerCase();
    r = r.filter(x => x.name.toLowerCase().includes(q) || x.notation.toLowerCase().includes(q));
  }
  const by = {
    notation: (a, b) => String(a.notation).localeCompare(String(b.notation)),
    damage: (a, b) => b.damage - a.damage,
    startup: (a, b) => (a.startupF ?? 999) - (b.startupF ?? 999),
  }[sort] || ((a, b) => 0);
  return r.slice().sort(by);
}

export function movelistClasses(rows) {
  const s = new Set(rows.map(r => r.moveClass));
  return ['all', ...Array.from(s)];
}

/* ---------- overlay (DOM) ---------- */
const OVERLAY_ID = 'wh-movelist';
function _ensureStyle() {
  if (typeof document === 'undefined' || document.getElementById(OVERLAY_ID + '-style')) return;
  const st = document.createElement('style');
  st.id = OVERLAY_ID + '-style';
  st.textContent = `
#${OVERLAY_ID} { position: fixed; inset: 0; z-index: 230; display: none; align-items: center; justify-content: center; background: rgba(8,4,14,.8); }
#${OVERLAY_ID}.show { display: flex; }
.wh-ml-card { width: min(94vw, 640px); max-height: 84vh; display: flex; flex-direction: column; background: rgba(20,12,32,.96); border: 1px solid rgba(255,177,77,.4); border-radius: 14px; padding: 16px; }
.wh-ml-head { letter-spacing: 4px; font-size: 12px; color: #b48cff; margin-bottom: 8px; }
.wh-ml-tools { display: flex; gap: 8px; margin-bottom: 10px; }
.wh-ml-tools input, .wh-ml-tools select { flex: 1; min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.06); color: #fff; padding: 0 12px; font-size: 14px; }
.wh-ml-list { overflow-y: auto; flex: 1; }
.wh-ml-row { display: flex; gap: 10px; align-items: center; min-height: 48px; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,.07); font-size: 14px; }
.wh-ml-not { color: #ffb14d; font-weight: 700; min-width: 92px; }
.wh-ml-name { color: #fff; flex: 1; }
.wh-ml-meta { color: rgba(255,255,255,.55); font-size: 12px; text-align: right; }`;
  document.head.appendChild(st);
}

export function renderMovelist(fighterId, fighterName) {
  if (typeof document === 'undefined') return movelistRows(fighterId).length;
  _ensureStyle();
  let ov = document.getElementById(OVERLAY_ID);
  if (!ov) { ov = document.createElement('div'); ov.id = OVERLAY_ID; document.body.appendChild(ov); }
  const rows = movelistRows(fighterId);
  const classes = movelistClasses(rows);
  const draw = (f) => {
    const list = filterMovelist(rows, f);
    ov.querySelector('.wh-ml-list').innerHTML = list.map(r =>
      `<div class="wh-ml-row"><span class="wh-ml-not">${r.notation}</span><span class="wh-ml-name">${r.name}${r.ja ? ' <small>' + r.ja + '</small>' : ''}</span><span class="wh-ml-meta">${r.hitLevel ? r.hitLevel + ' · ' : ''}${r.damage}dmg${r.startupF != null ? ' · i' + r.startupF : ''}${r.activeF != null ? '/' + r.activeF + '/' + r.recoveryF : ''}${r.onBlock != null ? ' · B' + r.onBlock : ''}<br>${r.moveClass}${r.origin === 'added' ? ' · added' : ''}${r.routes && r.routes.length ? ' → ' + r.routes.map(x => x.type).join(',') : ''}</span></div>`
    ).join('') || '<div class="wh-ml-row">No techniques inscribed. The stones are silent.</div>';
  };
  const f = { query: '', cls: 'all', sort: 'notation' };
  ov.innerHTML = `<div class="wh-ml-card">
    <div class="wh-ml-head">INSCRIPTIONS — ${String(fighterName || fighterId).toUpperCase()}</div>
    <div class="wh-ml-tools">
      <input id="wh-ml-q" placeholder="Search techniques…" aria-label="Search techniques">
      <select id="wh-ml-c" aria-label="Filter by type">${classes.map(c => `<option value="${c}">${c}</option>`).join('')}</select>
      <select id="wh-ml-s" aria-label="Sort"><option value="notation">Notation</option><option value="damage">Damage</option><option value="startup">Startup</option></select>
    </div>
    <div class="wh-ml-list"></div>
    <div style="text-align:right;margin-top:10px;"><button id="wh-ml-close" style="padding:10px 18px;border-radius:10px;border:1px solid rgba(255,255,255,.25);background:rgba(20,12,32,.8);color:#fff;min-height:44px;">CLOSE ▸</button></div>
  </div>`;
  ov.classList.add('show');
  draw(f);
  ov.querySelector('#wh-ml-q').addEventListener('input', e => { f.query = e.target.value; draw(f); });
  ov.querySelector('#wh-ml-c').addEventListener('change', e => { f.cls = e.target.value; draw(f); });
  ov.querySelector('#wh-ml-s').addEventListener('change', e => { f.sort = e.target.value; draw(f); });
  ov.querySelector('#wh-ml-close').addEventListener('click', () => ov.classList.remove('show'));
  return rows.length;
}
export function hideMovelist() {
  if (typeof document === 'undefined') return;
  const ov = document.getElementById(OVERLAY_ID);
  if (ov) ov.classList.remove('show');
}
