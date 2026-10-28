/* WESTERN HEART — CREATION SUITE shell (one template every editor reuses).
   Layout sources (docs/tech/STUDIOS.md): T7 Customization tabs + centre-stage model,
   2K19 Creation Suite pinned button-legend footer + section grouping, Fire Pro Edit
   body-part silhouette, Wrestling Empire tap-the-body part select.
   ctx API for editors: el (context panel), setTabs, setFooter, setSilhouette,
   onPickBone, viewer, toast, getFighter/getFighterId. */
import { ROSTER } from '../characters.js';
import { StudioViewer } from './studio-viewer.js';
import { initNav } from './studio-nav.js';
import { mountPoseStudio } from './studio-pose.js';
import { exportBundle, importBundle } from './studio-store.js';
import { STUDIOS, LABELS_UI } from './studio-registry.js';

const qs = new URLSearchParams(location.search);
const STANDALONE = qs.has('standalone');
const $ = (id) => document.getElementById(id);
let viewer = null, current = null, tabKeys = [], tabOn = null, tabCb = null, face = {}, pickCb = null;
let fi = Math.max(0, ROSTER.findIndex(f => f.id === (qs.get('fighter') || 'pantera')));

function toast(m){ const t = $('toast'); t.textContent = m; t.classList.add('on'); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('on'), 1600); }
function download(name, data, type){ const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([data], { type })); a.download = name; a.click(); }

/* footer: [{k:'b'|'a'|'x'|'y', label, fn, pri, disabled}] — 2K19 legend bar */
function setFooter(items){
  face = {}; const f = $('foot');
  f.innerHTML = items.map((it, i) => `<button data-i="${i}" class="${it.pri ? 'pri' : ''}" ${it.disabled ? 'disabled' : ''}><b>${it.k.toUpperCase()}</b>${it.label}</button>`).join('');
  f.querySelectorAll('[data-i]').forEach(b => { const it = items[+b.dataset.i]; b.onclick = () => it.fn(); face[it.k] = it; });
}
function hub(){
  current = null; pickCb = null; $('editor').style.display = 'none'; $('hub').style.display = 'grid';
  $('st-title').textContent = STANDALONE ? LABELS_UI.standalone : LABELS_UI.suite; $('st-crumb').textContent = '';
  const list = STUDIOS.filter(s => STANDALONE || !s.standaloneOnly);
  const groups = [...new Set(list.map(s => s.group))];
  $('hub').innerHTML = groups.map(g => `<div class="hub-sec">${g}</div>${list.filter(s => s.group === g).map(s =>
    `<button class="tile" data-s="${s.id}"><span class="tag${s.live ? ' live' : ''}">${s.live ? 'READY' : 'SOON'}</span><span class="ic">${s.icon}</span><span class="nm">${s.name}</span><span class="ds">${s.desc}</span></button>`).join('')}`).join('');
  $('hub').querySelectorAll('[data-s]').forEach(b => b.onclick = () => open(b.dataset.s));
  setFooter([{ k: 'b', label: 'BACK', fn: back }, { k: 'a', label: 'SELECT', pri: true, fn: () => document.activeElement && document.activeElement.click() }]);
  const f = $('hub').querySelector('.tile'); f && f.focus();
}
function setTabs(list, on, cb){ tabKeys = list.map(x => x[0]); tabOn = on; tabCb = cb; $('tabs').innerHTML = list.map(([k, n]) => `<button class="tab${k === on ? ' on' : ''}" data-t="${k}">${n}</button>`).join(''); $('tabs').querySelectorAll('[data-t]').forEach(b => b.onclick = () => pickTab(b.dataset.t)); }
function pickTab(k){ tabOn = k; $('tabs').querySelectorAll('[data-t]').forEach(b => b.classList.toggle('on', b.dataset.t === k)); tabCb && tabCb(k); }
function stepTab(d){ if (!tabKeys.length) return; const i = (tabKeys.indexOf(tabOn) + d + tabKeys.length) % tabKeys.length; pickTab(tabKeys[i]); }
$('tab-l').onclick = () => stepTab(-1); $('tab-r').onclick = () => stepTab(1);

/* swipe on the panel = L1/R1 (mobile) */
(() => { let x0 = null, y0 = 0; const p = $('pbody');
  p.addEventListener('touchstart', e => { if (e.target.type === 'range') return; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
  p.addEventListener('touchend', e => { if (x0 == null) return; const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null; if (Math.abs(dx) > 60 && Math.abs(dy) < 40) stepTab(dx < 0 ? 1 : -1); }); })();

/* tap the model to pick a bone: nearest projected bone within 40px */
function bindPick(){
  const c = viewer.renderer.domElement; let d0 = null;
  c.addEventListener('pointerdown', e => d0 = [e.clientX, e.clientY]);
  c.addEventListener('pointerup', e => {
    if (!d0 || !pickCb || !viewer.model || Math.hypot(e.clientX - d0[0], e.clientY - d0[1]) > 6) return;
    const r = c.getBoundingClientRect(); let best = null, bd = 40;
    viewer.model.updateMatrixWorld(true);
    viewer.model.traverse(o => { if (!o.isBone) return; const v = o.getWorldPosition(o.position.clone()).project(viewer.camera);
      const sx = r.left + (v.x + 1) / 2 * r.width, sy = r.top + (1 - v.y) / 2 * r.height, dd = Math.hypot(sx - e.clientX, sy - e.clientY);
      if (dd < bd) { bd = dd; best = o; } });
    if (best) pickCb(best);
  });
}
async function showFighter(){
  const f = ROSTER[fi]; $('st-crumb').textContent = f.name || f.id;
  document.querySelector('#fstep .name').textContent = (f.name || f.id).toUpperCase();
  try { await viewer.loadFighter(f.model); } catch (e) { toast('Model unavailable: ' + (f.name || f.id)); }
  current && current.refresh && current.refresh();
}
async function open(id){
  const s = STUDIOS.find(x => x.id === id); if (!s) return;
  if (s.href) { location.href = s.href; return; }
  if (!s.live) { toast(s.name + ' arrives in the next update'); return; }
  $('hub').style.display = 'none'; $('editor').style.display = 'grid'; $('st-title').textContent = s.name.toUpperCase();
  if (!viewer) { viewer = new StudioViewer($('view')); bindPick(); } else viewer._resize();
  const step = $('fstep');
  step.children[0].onclick = () => { fi = (fi - 1 + ROSTER.length) % ROSTER.length; showFighter(); };
  step.children[2].onclick = () => { fi = (fi + 1) % ROSTER.length; showFighter(); };
  const el = $('pbody'); el.innerHTML = '';
  const ctx = { viewer, el, toast, download, setTabs, setFooter, back, sil: $('sil'), onPickBone: (fn) => { pickCb = fn; },
    getFighterId: () => ROSTER[fi].id, getFighter: () => ROSTER[fi], STANDALONE, importBundle, exportBundle };
  current = s.mount === 'pose' ? mountPoseStudio(ctx) : await s.load().then(m => m.mount(ctx));
  requestAnimationFrame(() => viewer._resize());
  await showFighter();
  const first = el.querySelector('button'); first && first.focus();
}
function back(){ if (current) hub(); else if (!STANDALONE) location.href = 'index.html'; }
$('st-back').onclick = back;
addEventListener('resize', () => viewer && viewer._resize());
initNav({ onBack: back, onTab: stepTab, onFace: (k) => face[k] && !face[k].disabled && face[k].fn() });
window.__whStudio = { open, hub, get viewer(){ return viewer; }, ROSTER, get current(){ return current; } };
const deep = qs.get('studio'); if (deep) open(deep); else hub();
