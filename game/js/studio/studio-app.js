/* WESTERN HEART — Studios hub. Two front doors, one app:
   - in-game: main menu → CREATION SUITE → STUDIOS (game/studio.html)
   - standalone: game/studio.html?standalone=1 — adds the cross-game
     LIBRARY (import/export models, poses, clips, bundles from every game). */
import { ROSTER } from '../characters.js';
import { StudioViewer } from './studio-viewer.js';
import { initNav } from './studio-nav.js';
import { mountPoseStudio } from './studio-pose.js';
import { exportBundle, importBundle } from './studio-store.js';
import { STUDIOS } from './studio-registry.js';

const qs = new URLSearchParams(location.search);
const STANDALONE = qs.has('standalone');
const $ = (id) => document.getElementById(id);
let viewer = null, current = null, tabKeys = [], tabOn = null, tabCb = null;
let fi = Math.max(0, ROSTER.findIndex(f => f.id === (qs.get('fighter') || 'pantera')));

function toast(m){ const t = $('toast'); t.textContent = m; t.classList.add('on'); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('on'), 1600); }
function download(name, data, type){ const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([data], { type })); a.download = name; a.click(); }

function hub(){
  current = null; $('editor').style.display = 'none'; $('hub').style.display = 'block'; $('st-title').textContent = STANDALONE ? 'WH STUDIO' : 'STUDIOS'; $('st-crumb').textContent = STANDALONE ? 'standalone · every game' : '';
  const list = STUDIOS.filter(s => STANDALONE || !s.standaloneOnly);
  const groups = [...new Set(list.map(s => s.group))];
  $('hub').innerHTML = groups.map(g => `<div class="hub-sec">${g}</div><div class="hub-grid">${list.filter(s => s.group === g).map(s =>
    `<button class="tile" data-s="${s.id}"><span class="tag${s.live ? ' live' : ''}">${s.live ? 'READY' : 'NEXT UPDATE'}</span><span class="ic">${s.icon}</span><span class="nm">${s.name}</span><span class="ds">${s.desc}</span></button>`).join('')}</div>`).join('');
  $('hub').querySelectorAll('[data-s]').forEach(b => b.onclick = () => open(b.dataset.s));
  const f = $('hub').querySelector('.tile'); f && f.focus();
}
function setTabs(list, on, cb){ tabKeys = list.map(x => x[0]); tabOn = on; tabCb = cb; $('tabs').innerHTML = list.map(([k, n]) => `<button class="tab${k === on ? ' on' : ''}" data-t="${k}">${n}</button>`).join(''); $('tabs').querySelectorAll('[data-t]').forEach(b => b.onclick = () => pickTab(b.dataset.t)); }
function pickTab(k){ tabOn = k; $('tabs').querySelectorAll('[data-t]').forEach(b => b.classList.toggle('on', b.dataset.t === k)); tabCb && tabCb(k); }
function stepTab(d){ if (!tabKeys.length) return; const i = (tabKeys.indexOf(tabOn) + d + tabKeys.length) % tabKeys.length; pickTab(tabKeys[i]); }

async function showFighter(){
  const f = ROSTER[fi]; $('st-crumb').textContent = f.name || f.id;
  const nm = document.querySelector('#fstep .name'); if (nm) nm.textContent = (f.name || f.id).toUpperCase();
  try { await viewer.loadFighter(f.model); } catch (e) { toast('Model unavailable: ' + (f.name || f.id)); }
  current && current.refresh && current.refresh();
}
async function open(id){
  const s = STUDIOS.find(x => x.id === id); if (!s) return;
  if (!s.live) { toast(s.name + ' arrives in the next update'); return; }
  $('hub').style.display = 'none'; $('editor').style.display = 'block'; $('st-title').textContent = s.name;
  if (!viewer) viewer = new StudioViewer($('view')); else viewer._resize();
  const body = $('pbody');
  body.innerHTML = '';
  const step = document.createElement('div'); step.className = 'stepper'; step.id = 'fstep';
  step.innerHTML = '<button aria-label="Previous fighter">‹</button><div class="name"></div><button aria-label="Next fighter">›</button>';
  const inner = document.createElement('div');
  body.append(step, inner);
  step.children[0].onclick = () => { fi = (fi - 1 + ROSTER.length) % ROSTER.length; showFighter(); };
  step.children[2].onclick = () => { fi = (fi + 1) % ROSTER.length; showFighter(); };
  const ctx = { viewer, el: inner, toast, download, setTabs, getFighterId: () => ROSTER[fi].id, getFighter: () => ROSTER[fi], STANDALONE, importBundle, exportBundle };
  current = s.mount === 'pose' ? mountPoseStudio(ctx) : await s.load().then(m => m.mount(ctx));
  await showFighter();
  const first = inner.querySelector('button'); first && first.focus();
}
function back(){ if (current) hub(); else if (!STANDALONE) location.href = 'index.html'; }
$('st-back').onclick = back;
initNav({ onBack: back, onTab: stepTab });
window.__whStudio = { open, hub, get viewer(){ return viewer; }, ROSTER };
const deep = qs.get('studio'); if (deep) open(deep); else hub();
