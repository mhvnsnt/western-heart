/* app.js — Create Fighter hub logic.
   Tekken loop: pick category -> grid -> hover try-on -> BUY -> EQUIP -> conflict
   check (Replace/Cancel) -> color/material edit. Fighter JSON save format matches
   customization/CHARACTER-CREATION.md §6, extended with wardrobe/attire slots,
   roster base models (data/ROSTER-BASE.json) and the preset library.
   v0.2: fighter select loads REAL roster GLBs from game/assets/models/; BODY tab
   locks for canon roster bodies; presets = named saved fighters (save/load/delete). */
import { Preview3D, SKIN_TONES } from './preview3d.js';
import { Catalog, CATEGORIES, CONFLICTS } from './catalog.js';

const LS_KEY = 'wh_create_fighter_v1';
const PRESET_LS_KEY = 'wh_create_fighter_presets';
const START_MONEY = 12400;
const SOLDIER_GLB = 'assets/Soldier.glb';   // WMXIX default CAW base rig

const BODY_TYPES = [
  { name:'Skinny 1', h:1.02, w:0.86, m:0.85 }, { name:'Skinny 2', h:0.98, w:0.88, m:0.85 },
  { name:'Medium 1', h:1.00, w:1.00, m:1.00 }, { name:'Medium 2', h:1.01, w:1.04, m:1.05 },
  { name:'Thick 1', h:0.99, w:1.14, m:1.05 }, { name:'Thick 2', h:1.00, w:1.20, m:1.10 },
  { name:'Fat 1', h:0.97, w:1.30, m:0.95 }, { name:'Fat 2', h:0.96, w:1.38, m:0.95 },
  { name:'Austin', h:1.00, w:1.12, m:1.15 }, { name:'HBK', h:0.99, w:1.02, m:1.10 },
  { name:'Rikishi', h:1.02, w:1.42, m:1.05 }, { name:'Rock', h:1.01, w:1.16, m:1.22 },
  { name:'Hairy 1', h:1.00, w:1.08, m:1.08 }, { name:'Hairy 2', h:1.01, w:1.10, m:1.10 },
  { name:'King Frame', h:1.04, w:1.14, m:1.18 }, { name:'Ganryu Frame', h:0.96, w:1.34, m:1.02 },
];
const SOULS = ['—','TOU','SHA','YIN','YANG','KAMI','ONI','RYU','TEN'];
const ELEMENTS = ['—','Wood','Fire','Earth','Metal','Water'];
const LANDS = ['—','Tree of Life','Iron Desert','Silent Sea','Cinder Wastes','Hollow Peaks'];
const TITLE_A = ['RAGING','SILENT','GOLDEN','BROKEN','HOWLING','IRON','CRIMSON','LONE'];
const TITLE_B = ['BEAST','PANTHER','KING','GHOST','STORM','WOLF','TIGER','DEMON'];
const TIERS = [['custom','CUSTOM'],['souls','THE NINE SOULS'],['main','MAIN ROSTER'],['bonus','BONUS ROSTER']];

/* ROSTER is data-driven: 'new' + the 36 named fighters from data/ROSTER-BASE.json
   (ids/names/tiers trace to game/js/roster-full.js; GLB paths verified in
   game/assets/models/). Filled at boot; the 'new' entry is always present. */
let ROSTER = [
  { id:'new', name:'NEW FIGHTER', desc:'WMXIX default CAW base', glb:SOLDIER_GLB, tier:'custom', modelSrc:'exact' },
];

/* ---------------- state ---------------- */
function blankAttire(){ return { name:'', thumb:'', equipped:{}, owned:[], colors:{} }; }
function blankFighter(){
  return {
    version: 2, app:'wh-create-fighter',
    profile:{ name:'NEW FIGHTER', short_name:'NEWF', alias:'', height:`6'0"`, weight:220,
      music:'', titantron:'', soul:'—', element:'—', land:'—',
      title:['',''], picture:'' },
    base:'new',
    model:SOLDIER_GLB,   // base GLB, relative to customization/create-fighter/
    body:{ body_type:'Medium 1', skin_tone:'#c98d5e', head_shape:'male_3',
      proportions:{ height:1, weight:1, muscle:1 } },
    attireIndex: 0,
    attires:[ blankAttire(), blankAttire(), blankAttire(), blankAttire() ],
    wardrobe:[ null,null,null,null,null,null,null,null,null,null ],
    moveset:{},   // tekken_input -> move_id (v0.3; older WWE slot keys kept as-is)
    performance:{   // PERFORMANCE tab — WWE 2K22 Performance-section pattern, Tekken flavor
      intro:'t3_walk_fwd', victory:'t3_win_rp', victory_alignment:'Face',
      taunt:'t3_stance', signature:'', finisher:'',
    },
    decals:[],   // [{lib, entry_id, placement}] — options stack, never overwrite
    fighting_style:{ archetype:'grappler', aggression:5, high_flyer:5, technical:5 },
    parameters:{ head:{offense:5,defense:5}, body:{offense:5,defense:5}, arms:{offense:5,defense:5},
                 legs:{offense:5,defense:5}, flying:{offense:5,defense:5} },
    limbs:{   // DXMMII 4-arm limb system — tools/limb-system/dxmmii/
      enabled:false,
      preset:'default',
      presets:{},   // name -> { sockets:{L:[x,y,z],R:[x,y,z]}, state, notes }
      sockets:{ L:[0.068,0.01,0.28], R:[-0.068,0.01,0.28] },  // from dxrm_manifest.json
      arm_state:'attached',   // attached | retracting | hidden | growing | gyro-detached
    },
    wallet: START_MONEY,
  };
}
let F = blankFighter();
let catalog=null, moveDb=null, moveSlots=null, tekkenLib=null;
let decalLibs=[];   // [{lib, manifest}]
let djMerged=false;
let preview=null;
let ui = { tab:'body', attireCat:null, gridPage:0, gridQuery:'', selPart:null, selSlot:null, wardSel:0, selMove:null, perfPreview:null };

/* Decal library registry — add one line per fighter as libraries land.
   Pattern: customization/decal-library/<fighter>/MANIFEST.json */
const DECAL_LIBS = ['pantera'];

const $ = s=>document.querySelector(s);
const attire = ()=>F.attires[F.attireIndex];
const isCustom = ()=>F.base==='new';

/* ---------------- persistence ---------------- */
function persist(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(F)); }catch(e){} toast('Saved ✓'); }
function loadStored(){ try{ const s=localStorage.getItem(LS_KEY); if(s){ F=Object.assign(blankFighter(), JSON.parse(s)); return true; } }catch(e){} return false; }
function toast(msg){ const t=$('#save-toast'); t.textContent=msg; setTimeout(()=>t.textContent='',2500); }

/* ---------------- preset library (named saved fighters) ---------------- */
function getPresets(){ try{ return JSON.parse(localStorage.getItem(PRESET_LS_KEY)||'{}'); }catch(e){ return {}; } }
function setPresets(p){ try{ localStorage.setItem(PRESET_LS_KEY, JSON.stringify(p)); }catch(e){} }

/* ---------------- modal ---------------- */
function modal(title, bodyHTML, actions){
  $('#modal-title').textContent = title;
  $('#modal-body').innerHTML = bodyHTML;
  const box = $('#modal-actions'); box.innerHTML='';
  for(const a of actions){
    const b=document.createElement('button');
    b.className='btn '+(a.cls||''); b.textContent=a.label;
    b.onclick=()=>{ closeModal(); a.fn&&a.fn(); };
    box.appendChild(b);
  }
  $('#modal').hidden=false; $('#modal-scrim').hidden=false;
}
function closeModal(){ $('#modal').hidden=true; $('#modal-scrim').hidden=true; }
$('#modal-scrim').onclick=closeModal;

/* ---------------- preview sync ---------------- */
function syncPreview(){
  if(!preview) return;
  if(F.model && preview.modelUrl!==F.model && !preview._loading){ preview.loadModel(F.model); return; }
  if(isCustom()){
    preview.setSkinTone(F.body.skin_tone);
  } // roster fighters keep their real textures — never tint canon models
  const bt = BODY_TYPES.find(b=>b.name===F.body.body_type);
  const p = F.body.proportions;
  preview.setProportions({
    height:(bt?bt.h:1)*p.height, weight:(bt?bt.w:1)*p.weight, muscle:(bt?bt.m:1)*p.muscle });
  preview.clearAllProxies();
  const eq = attire().equipped;
  for(const slotId of Object.keys(eq)){
    const cat = catalog.catBySlotId(slotId); if(!cat) continue;
    const col = (attire().colors[eq[slotId]]||{}).c1 || '#e8b64c';
    preview.setProxy(slotId, cat.anchor, col, eq[slotId]);
  }
  if(ui.selPart){ // try-on preview
    const cat = catalog.catForPart(ui.selPart.part_id);
    if(cat) preview.setProxy('tryon', cat.anchor, '#7fd4ff', ui.selPart.displayName);
  }
  preview.setDummyVisible(ui.tab==='moveset');
}

/* ---------------- top bar / attire slots ---------------- */
function renderTopbar(){
  $('#fighter-name').textContent = F.profile.name || 'NEW FIGHTER';
  $('#breadcrumb').textContent = `${F.profile.name||'New Fighter'} > Attire ${F.attireIndex+1} > ${ui.tab.toUpperCase()}${ui.attireCat?' > '+ui.attireCat.label:''}`;
  $('#wallet-amt').textContent = F.wallet.toLocaleString();
  const tabs = $('#attire-tabs'); tabs.innerHTML='';
  F.attires.forEach((a,i)=>{
    const b=document.createElement('button');
    b.className='attire-tab'+(i===F.attireIndex?' active':'');
    b.setAttribute('role','tab');
    const nm = a.name || `ATTIRE ${i+1}`;
    b.innerHTML = `<span class="athumb" ${a.thumb?`style="background-image:url('${a.thumb}')"` : ''}></span>${nm}`;
    b.title = nm + (i>0?'':' (clone source for empty slots)');
    b.onclick=()=>{ F.attireIndex=i; if(!F.attires[i].name && i>0){ /* empty slot: clone attire 1 appearance */ const src=JSON.parse(JSON.stringify(F.attires[0])); src.name=''; src.thumb=''; F.attires[i]=src; } ui.selPart=null; renderAll(); };
    tabs.appendChild(b);
  });
}

/* ---------------- left rail ---------------- */
function setTab(tab){
  ui.tab=tab; ui.attireCat=null; ui.selPart=null; ui.gridPage=0; ui.selMove=null;
  if(preview) preview.playIdle();   // stop any looping performance/move preview
  document.querySelectorAll('.rail-btn').forEach(x=>x.classList.toggle('active',x.dataset.tab===tab));
  renderAll();
}
document.querySelectorAll('.rail-btn').forEach(b=>{ b.onclick=()=>setTab(b.dataset.tab); });

/* ---------------- panel framework ---------------- */
function renderAll(){ renderTopbar(); renderPanel(); syncPreview(); persistQuiet(); }
function persistQuiet(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(F)); }catch(e){} }
function renderPanel(){
  const body=$('#panel-body');
  $('#panel-title').textContent = ui.tab.toUpperCase();
  $('#panel-sub').textContent = '';
  body.innerHTML='';
  ({ body:renderBody, attire:renderAttire, wardrobe:renderWardrobe, profile:renderProfile, moveset:renderMoveset, performance:renderPerformance, limbs:renderLimbs })[ui.tab](body);
}

/* ================= BODY ================= */
function renderBody(el){
  const locked = !isCustom();   // roster fighters' bodies are canon — lock per UI promise
  $('#panel-sub').textContent = 'Wrestling CAW — body, skin, head, hair';
  el.innerHTML = `
    ${locked?`<div class="note">🔒 <b>Canon body</b> — ${esc(F.profile.name)}'s body is locked. Switch to NEW FIGHTER for full BODY access. Body type, skin tone, proportions and head shape stay with the custom base.</div>`:''}
    <div class="sect">BODY TYPE — No Mercy 14</div>
    <div class="roster-grid" id="bodytypes"></div>
    <div class="sect">SKIN TONE — 8 tones</div>
    <div class="swatches" id="skintones"></div>
    <div class="sect">PROPORTIONS — WMXIX parametric</div>
    <div id="propsliders"></div>
    <div class="sect">HEAD</div>
    <div class="field"><label>HEAD SHAPE</label><select id="headshape" ${locked?'disabled':''}>
      ${['male_1','male_2','male_3','male_4','male_5','male_6','male_7','female_1','female_2','female_3'].map(h=>`<option ${F.body.head_shape===h?'selected':''}>${h}</option>`).join('')}
    </select></div>
    <div class="note">Face (348) &amp; Hair (156) live under ATTIRE — they equip into the Face / Hairstyle slots with the same buy/equip loop.</div>
    <div class="sect">BODY PARTS — ${catalog.count('bodies')} meshes</div>
    <div class="note">220 No Mercy body-part meshes. <span class="geo-badge">GEOMETRY PENDING</span> .obj wiring not in this build — equip records the part in your fighter JSON and shows a socket marker.</div>
    <div class="btn-row"><button class="btn" id="btn-bodyparts">BROWSE BODY PARTS</button></div>`;
  const bt=el.querySelector('#bodytypes');
  BODY_TYPES.forEach(t=>{
    const b=document.createElement('button');
    b.className='roster-card'+(F.body.body_type===t.name?' active':'');
    b.textContent=t.name;
    if(locked) b.disabled=true;
    b.onclick=()=>{ F.body.body_type=t.name; renderAll(); };
    bt.appendChild(b);
  });
  const st=el.querySelector('#skintones');
  SKIN_TONES.forEach(hex=>{
    const s=document.createElement('div');
    s.className='swatch'+(F.body.skin_tone===hex?' active':'');
    s.style.background=hex; s.title=hex;
    if(locked) s.style.opacity='0.35';
    s.onclick=()=>{ if(locked) return; F.body.skin_tone=hex; renderAll(); };
    st.appendChild(s);
  });
  const sl=el.querySelector('#propsliders');
  [['height','Height',0.85,1.15],['weight','Weight',0.85,1.3],['muscle','Muscle',0.85,1.3]].forEach(([k,label,lo,hi])=>{
    const d=document.createElement('div'); d.className='ctl';
    d.innerHTML=`<label>${label}<span class="val">${F.body.proportions[k].toFixed(2)}</span></label>
      <input type="range" min="${lo}" max="${hi}" step="0.01" value="${F.body.proportions[k]}" aria-label="${label}" ${locked?'disabled':''}>`;
    if(!locked){
      d.querySelector('input').oninput=e=>{ F.body.proportions[k]=+e.target.value;
        d.querySelector('.val').textContent=(+e.target.value).toFixed(2); syncPreview(); persistQuiet(); };
      d.querySelector('input').onchange=()=>persistQuiet();
    }
    sl.appendChild(d);
  });
  el.querySelector('#headshape').onchange=e=>{ F.body.head_shape=e.target.value; persistQuiet(); };
  el.querySelector('#btn-bodyparts').onclick=()=>{
    ui.tab='attire';
    document.querySelectorAll('.rail-btn').forEach(x=>x.classList.toggle('active',x.dataset.tab==='attire'));
    ui.attireCat=CATEGORIES.find(c=>c.key==='bodies');
    ui.gridPage=0; ui.gridQuery=''; ui.selPart=null;
    renderAll();
  };
}

/* ================= ATTIRE ================= */
function renderAttire(el){
  if(ui.attireCat && ui.attireCat.key==='decals'){ renderDecalBrowser(el); return; }
  if(!ui.attireCat){
    $('#panel-sub').textContent = 'Tekken item shop — pick a category';
    const eq = attire().equipped;
    el.innerHTML = `<div class="note">Buy → Equip loop. Items try on instantly. <span class="geo-badge">GEOMETRY PENDING</span> on every part: real ymg/obj meshes aren't wired yet, so equip shows a labeled socket marker + records the part in your fighter JSON. No fake equipped meshes — ever.</div>
      <div class="note" id="dj-note">${djMerged?'✅ <b>Def Jam library merged</b> — 22,360 indexed parts in the grids below.':'⏳ Merging the Def Jam part library (22,360 indexed parts)…'}</div>`;
    // Def Jam index: lazy-merge once (6.9MB — not in the boot bundle)
    if(!djMerged){
      fetch('../parts/defjam/PARTS-INDEX.json').then(r=>r.json()).then(dj=>{
        const n = catalog.mergeExternal(dj);
        djMerged = true;
        console.log(`[WH] Def Jam merged: ${n} parts`);
        if(ui.tab==='attire' && !ui.attireCat) renderPanel();
      }).catch(e=>console.warn('defjam merge failed', e));
    }
    // DECALS entry — WWE 2K logo-placement pattern, manifest-driven
    const dc = document.createElement('button');
    dc.className = 'subcat';
    const dcCount = decalLibs.reduce((n,l)=>n+((l.manifest.entries||[]).length),0);
    dc.innerHTML = `<span class="sc-ico">🏷️</span><span>Decals<br><small style="color:var(--dim)">logo / tights placement</small></span><span class="sc-count">${dcCount}</span>`;
    dc.onclick = ()=>{ ui.attireCat={key:'decals',label:'Decals',icon:'🏷️'}; ui.gridPage=0; renderPanel(); };
    el.appendChild(dc);
    CATEGORIES.filter(c=>c.key!=='bodies'&&c.key!=='skins').forEach(c=>{
      const b=document.createElement('button'); b.className='subcat'+(eq[c.slotId]?' equipped':'');
      b.innerHTML=`<span class="sc-ico">${c.icon}</span><span>${c.label}${eq[c.slotId]?'<br><small style="color:var(--green)">✓ '+esc(catalog.get(eq[c.slotId])?.displayName||eq[c.slotId])+'</small>':''}</span><span class="sc-count">${catalog.count(c.key)}</span>`;
      b.onclick=()=>{ ui.attireCat=c; ui.gridPage=0; ui.gridQuery=''; ui.selPart=null; renderPanel(); syncPreview(); renderTopbar(); };
      el.appendChild(b);
    });
    return;
  }
  renderItemGrid(el, ui.attireCat);
}

/* ================= DECALS — WWE 2K logo-placement pattern, manifest-driven ================
   Libraries live at customization/decal-library/<fighter>/MANIFEST.json.
   Options STACK (owner law): applying never overwrites — the fighter JSON keeps
   every applied decal, each swappable/removable. */
function renderDecalBrowser(el){
  $('#panel-sub').textContent = 'Decals — logo / tights placement';
  el.innerHTML = `
    <div class="back-row"><button class="btn back-btn" id="btn-back">← CATEGORIES</button></div>
    <div class="note">🏷️ <b>Decals stack — applying never overwrites.</b> Each entry composites onto the
    fighter's textures at its manifest placement. Applied decals save into your fighter JSON.</div>
    <div class="sect">APPLIED (${F.decals.length})</div>
    <div id="dc-applied"></div>
    <div class="sect">LIBRARIES</div>
    <div id="dc-libs"></div>`;
  el.querySelector('#btn-back').onclick = ()=>{ ui.attireCat=null; renderAll(); };
  const ap = el.querySelector('#dc-applied');
  if(!F.decals.length) ap.innerHTML = `<div class="note">None yet — pick a decal below.</div>`;
  F.decals.forEach((d,i)=>{
    const row = document.createElement('div');
    row.className = 'kv';
    row.innerHTML = `<span>${esc(d.name)}<br><small style="color:var(--dim)">${esc(d.lib)} · ${esc(d.type)} · ${esc(d.placement||'canonical')}</small></span>
      <span><button class="btn btn-red" data-rm="${i}">REMOVE</button></span>`;
    ap.appendChild(row);
  });
  ap.querySelectorAll('[data-rm]').forEach(b=>b.onclick=()=>{
    F.decals.splice(+b.dataset.rm,1); persistQuiet(); renderPanel(); toast('Decal removed');
  });
  const libs = el.querySelector('#dc-libs');
  if(!decalLibs.length) libs.innerHTML = `<div class="note">No decal libraries found.</div>`;
  decalLibs.forEach(({lib, manifest})=>{
    const wrap = document.createElement('div');
    wrap.innerHTML = `<div class="sect">${esc(manifest.library||lib)} — ${esc(manifest.character||'')}</div>`;
    libs.appendChild(wrap);
    (manifest.entries||[]).forEach(e=>{
      const applied = F.decals.some(d=>d.lib===lib && d.entry_id===e.id);
      const card = document.createElement('div');
      card.className = 'item-card'+(applied?' equipped':'');
      card.innerHTML = `<div class="item-mono">🏷️</div>
        <div class="item-name">${esc(e.name)}</div>
        <div class="item-meta">${esc(e.type)} · ${e.size_px?e.size_px.join('×')+'px':''}<br>
        <span style="font-size:11px">${esc(e.notes||'')}</span><br>
        ${applied?'<span class="owned">✓ APPLIED</span>':`<button class="btn btn-gold" data-apply="${esc(e.id)}">APPLY</button>`}</div>`;
      const btn = card.querySelector('[data-apply]');
      if(btn) btn.onclick = ()=>{
        F.decals.push({ lib, entry_id:e.id, name:e.name, type:e.type,
          png:e.png, placement:e.default_placement||'canonical_logo_placement',
          applied:new Date().toISOString() });
        persistQuiet(); renderPanel(); toast(`Decal applied ✓ (${F.decals.length} stacked)`);
      };
      libs.appendChild(card);
    });
  });
}

function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

function renderItemGrid(el, cat){
  $('#panel-sub').textContent = `${cat.label} — ${catalog.count(cat.key)} parts · slot ${cat.slotId}`;
  const all = catalog.items(cat.key);
  const q = ui.gridQuery.trim().toLowerCase();
  const list = q ? all.filter(p=>(p.displayName+' '+p.part_id).toLowerCase().includes(q)) : all;
  const per=24, pages=Math.max(1,Math.ceil(list.length/per));
  ui.gridPage=Math.min(ui.gridPage,pages-1);
  const page=list.slice(ui.gridPage*per,(ui.gridPage+1)*per);
  const eqId = attire().equipped[cat.slotId];
  el.innerHTML=`
    <div class="back-row"><button class="btn back-btn" id="btn-back">← CATEGORIES</button>
      ${eqId?`<button class="btn btn-red back-btn" id="btn-unequip">UNEQUIP</button>`:''}</div>
    <input class="search" id="grid-q" placeholder="Search ${cat.label}…" value="${esc(ui.gridQuery)}" aria-label="Search">
    <div class="item-grid" id="grid"></div>
    <div class="pager"><button class="btn" id="pg-prev" ${ui.gridPage===0?'disabled':''}>← PREV</button>
      <span class="bb-hint">Page ${ui.gridPage+1} / ${pages} · ${list.length} items</span>
      <button class="btn" id="pg-next" ${ui.gridPage>=pages-1?'disabled':''}>NEXT →</button></div>
    <div id="item-detail"></div>`;
  el.querySelector('#btn-back').onclick=()=>{ ui.attireCat=null; ui.selPart=null; renderAll(); };
  const un=el.querySelector('#btn-unequip');
  if(un) un.onclick=()=>{ delete attire().equipped[cat.slotId]; ui.selPart=null; renderAll(); toast('Unequipped'); };
  el.querySelector('#pg-prev').onclick=()=>{ ui.gridPage--; renderPanel(); };
  el.querySelector('#pg-next').onclick=()=>{ ui.gridPage++; renderPanel(); };
  const qi=el.querySelector('#grid-q');
  qi.oninput=()=>{ ui.gridQuery=qi.value; ui.gridPage=0;
    clearTimeout(qi._t); qi._t=setTimeout(()=>{
      const val=ui.gridQuery; renderPanel();
      const nq=document.querySelector('#grid-q');   // keep focus while typing
      if(nq){ nq.focus(); try{ nq.setSelectionRange(val.length,val.length); }catch(e){} }
    },350); };
  const grid=el.querySelector('#grid');
  page.forEach(p=>{
    const owned = attire().owned.includes(p.part_id);
    const d=document.createElement('div');
    d.className='item-card'+(ui.selPart&&ui.selPart.part_id===p.part_id?' selected':'')+(eqId===p.part_id?' equipped':'');
    d.innerHTML=`<div class="item-mono">${cat.icon}</div>
      <div class="item-name">${esc(p.displayName)}</div>
      <div class="item-meta"><span class="stars">${'★'.repeat(p.rarity)}${'☆'.repeat(5-p.rarity)}</span><br>
      <span class="geo-badge">GEOMETRY PENDING</span><br>
      ${owned?'<span class="owned">OWNED</span>':`<span class="price">${p.price.toLocaleString()}G</span>`}<br>
      <span title="${esc(p.part_id)}">${esc(p.source_game)}</span></div>`;
    d.onclick=()=>{ ui.selPart=p; renderPanel(); syncPreview(); };
    grid.appendChild(d);
  });
  if(ui.selPart) renderItemDetail(el.querySelector('#item-detail'), ui.selPart, cat);
}

function renderItemDetail(el, p, cat){
  const owned = attire().owned.includes(p.part_id);
  const equipped = attire().equipped[cat.slotId]===p.part_id;
  const col = attire().colors[p.part_id]||{c1:'#e8b64c',c2:'#7fd4ff',c3:'#ff5d5d',metal:0.1,rough:0.7};
  el.innerHTML=`
    <div class="sect">SELECTED — ${esc(p.displayName)}</div>
    <div class="kv"><span>Part ID</span><b style="font-size:11px">${esc(p.part_id)}</b></div>
    <div class="kv"><span>Source</span><b>${esc(p.source_game)}</b></div>
    <div class="kv"><span>Slot</span><b>${cat.label} (${cat.slotId})</b></div>
    <div class="kv"><span>Socket</span><b>${cat.anchor}</b></div>
    <div class="kv"><span>File</span><b style="font-size:11px">${esc(p.file_path||'—')}</b></div>
    <div class="note"><span class="geo-badge">GEOMETRY PENDING</span> 3D mesh for this part isn't wired yet (ymg/obj parser pending).
      Equip records it in your fighter JSON and shows a pulsing socket marker at the <b>${cat.anchor}</b> anchor in your chosen colors. Color/material edits below apply to the marker now and to the real mesh when it lands.</div>
    <div class="sect">COLOR / MATERIAL</div>
    ${['c1','c2','c3'].map((k,i)=>`<div class="color-row"><span class="chip">CH ${i+1}</span>
      <input type="color" value="${col[k]}" data-ck="${k}" aria-label="Channel ${i+1}"></div>`).join('')}
    <div class="ctl"><label>Metalness <span class="val">${col.metal}</span></label>
      <input type="range" min="0" max="1" step="0.05" value="${col.metal}" data-mk="metal"></div>
    <div class="ctl"><label>Roughness <span class="val">${col.rough}</span></label>
      <input type="range" min="0" max="1" step="0.05" value="${col.rough}" data-mk="rough"></div>
    <div class="btn-row">
      ${equipped?`<span class="owned" style="font-size:18px;align-self:center">✓ EQUIPPED</span>`
        :owned?`<button class="btn btn-green" id="btn-equip">EQUIP</button>`
        :`<button class="btn btn-gold" id="btn-buy">BUY — ${p.price.toLocaleString()}G</button>`}
    </div>`;
  el.querySelectorAll('input[type=color]').forEach(inp=>{
    inp.oninput=()=>{ col[inp.dataset.ck]=inp.value; attire().colors[p.part_id]=col; syncPreview(); persistQuiet(); };
  });
  el.querySelectorAll('input[type=range]').forEach(inp=>{
    inp.oninput=()=>{ col[inp.dataset.mk]=+inp.value; attire().colors[p.part_id]=col;
      inp.closest('.ctl').querySelector('.val').textContent=(+inp.value).toFixed(2); persistQuiet(); };
  });
  const bb=el.querySelector('#btn-buy');
  if(bb) bb.onclick=()=>{
    if(F.wallet<p.price){ modal('NOT ENOUGH FIGHT MONEY',`<p>You need <b>${p.price.toLocaleString()}G</b> — wallet has <b>${F.wallet.toLocaleString()}G</b>.</p>`,[{label:'OK',cls:'btn-gold'}]); return; }
    F.wallet-=p.price; attire().owned.push(p.part_id);
    modal('PURCHASED',`<p><b>${esc(p.displayName)}</b> is yours.</p><p>Press EQUIP to wear it.</p>`,
      [{label:'EQUIP NOW',cls:'btn-green',fn:()=>tryEquip(p,cat)},{label:'LATER',cls:''}]);
    renderAll();
  };
  const be=el.querySelector('#btn-equip');
  if(be) be.onclick=()=>tryEquip(p,cat);
}

function tryEquip(p, cat){
  const conflicts = (CONFLICTS[cat.slotId]||[]).filter(s=>attire().equipped[s]);
  if(conflicts.length){
    const names = conflicts.map(s=>{ const c=catalog.catBySlotId(s); const id=attire().equipped[s];
      return `${c?c.label:s}: ${esc(catalog.get(id)?.displayName||id)}`; }).join('<br>');
    modal('SLOT CONFLICT',`<p><b>${esc(p.displayName)}</b> conflicts with:</p><p>${names}</p><p>Tekken rule: replace it, or cancel.</p>`,
      [{label:'REPLACE',cls:'btn-gold',fn:()=>{ conflicts.forEach(s=>delete attire().equipped[s]); doEquip(p,cat); }},
       {label:'CANCEL',cls:''}]);
    return;
  }
  doEquip(p,cat);
}
function doEquip(p,cat){ attire().equipped[cat.slotId]=p.part_id; ui.selPart=p; renderAll(); toast('Equipped ✓'); }

/* ================= WARDROBE ================= */
function renderWardrobe(el){
  $('#panel-sub').textContent='DOA loadouts — 10 quick slots per fighter';
  el.innerHTML=`
    <div class="sect">WARDROBE SLOTS</div>
    <div class="ward-grid" id="wards"></div>
    <div class="btn-row">
      <button class="btn btn-gold" id="w-save">SAVE CURRENT LOOK → SLOT ${ui.wardSel+1}</button>
      <button class="btn btn-red" id="w-clear">CLEAR SLOT ${ui.wardSel+1}</button>
    </div>
    <div class="sect">TITLE — two phrases (DOA6)</div>
    <div class="field"><label>PHRASE 1</label><select id="t1">${TITLE_A.map(t=>`<option ${F.profile.title[0]===t?'selected':''}>${t}</option>`).join('')}</select></div>
    <div class="field"><label>PHRASE 2</label><select id="t2">${TITLE_B.map(t=>`<option ${F.profile.title[1]===t?'selected':''}>${t}</option>`).join('')}</select></div>
    <div class="note">Wardrobe slots are snapshots: ATTIRE slots + BODY hair/glasses + title. Loading swaps the full look instantly. The 4 No Mercy attire slots stay the deep slots.</div>`;
  const wg=el.querySelector('#wards');
  F.wardrobe.forEach((w,i)=>{
    const b=document.createElement('button');
    b.className='ward-slot'+(w?' filled':'');
    b.innerHTML=`${w&&w.thumb?`<span class="ws-thumb" style="background-image:url('${w.thumb}')"></span>`:'<span class="ws-thumb"></span>'}<span>${i+1}</span>`;
    b.style.outline = i===ui.wardSel?'2px solid var(--gold)':'';
    b.onclick=()=>{ ui.wardSel=i;
      if(w){ // LOAD
        F.attires[F.attireIndex]=JSON.parse(JSON.stringify(w.attire));
        F.body.skin_tone=w.skin_tone; F.profile.title=w.title.slice();
        renderAll(); toast(`Wardrobe ${i+1} loaded ✓`);
      } else renderPanel();
    };
    wg.appendChild(b);
  });
  el.querySelector('#w-save').onclick=()=>{
    F.wardrobe[ui.wardSel]={ attire:JSON.parse(JSON.stringify(attire())), skin_tone:F.body.skin_tone,
      title:F.profile.title.slice(), thumb:preview?preview.snapshot():'' };
    renderAll(); toast(`Saved to wardrobe ${ui.wardSel+1} ✓`);
  };
  el.querySelector('#w-clear').onclick=()=>{ F.wardrobe[ui.wardSel]=null; renderPanel(); };
  el.querySelector('#t1').onchange=e=>{ F.profile.title[0]=e.target.value; persistQuiet(); };
  el.querySelector('#t2').onchange=e=>{ F.profile.title[1]=e.target.value; persistQuiet(); };
}

/* ================= PROFILE ================= */
function renderProfile(el){
  $('#panel-sub').textContent='No Mercy page 1 + Western Heart canon';
  const pf=F.profile;
  el.innerHTML=`
    <div class="sect">IDENTITY</div>
    ${[['name','NAME','text'],['short_name','SHORT NAME','text'],['alias','ALIAS (meter)','text'],
       ['music','ENTRANCE MUSIC','text'],['titantron','TITANTRON VIDEO','text']].map(([k,l,t])=>
      `<div class="field"><label>${l}</label><input data-pk="${k}" type="${t}" value="${esc(pf[k]||'')}"></div>`).join('')}
    <div class="field"><label>HEIGHT</label><input data-pk="height" value="${esc(pf.height)}"></div>
    <div class="field"><label>WEIGHT (lbs)</label><input data-pk="weight" type="number" min="100" max="599" value="${pf.weight}"></div>
    <div class="sect">WESTERN HEART CANON</div>
    <div class="field"><label>SOUL (Nine Souls)</label><select data-pk="soul">${SOULS.map(s=>`<option ${pf.soul===s?'selected':''}>${s}</option>`).join('')}</select></div>
    <div class="field"><label>ELEMENT</label><select data-pk="element">${ELEMENTS.map(s=>`<option ${pf.element===s?'selected':''}>${s}</option>`).join('')}</select></div>
    <div class="field"><label>LAND OF ORIGIN</label><select data-pk="land">${LANDS.map(s=>`<option ${pf.land===s?'selected':''}>${s}</option>`).join('')}</select></div>
    <div class="sect">FIGHTING STYLE — No Mercy + Tekken archetype</div>
    <div class="field"><label>ARCHETYPE</label><select id="arch">${['grappler','rushdown','turtle','zoner','stance-dancer','all-rounder'].map(a=>`<option ${F.fighting_style.archetype===a?'selected':''}>${a}</option>`).join('')}</select></div>
    <div class="field"><label>CROWD REACTION — Face / Heel / Tweener</label><select id="align">
      ${['Face','Heel','Tweener'].map(a=>`<option ${F.performance.victory_alignment===a?'selected':''}>${a}</option>`).join('')}
    </select></div>
    <div class="note">Crowd reaction picks your victory-scene flavor (WWE 2K Face/Heel/Tweener rule) — set the win pose itself on the PERFORMANCE tab.</div>
    <div id="style-sl"></div>
    <div class="sect">PARAMETERS — offense/defense per zone (1–10)</div>
    <div id="param-sl"></div>
    <div class="note">🔒 Moveset, AI style, and parameters are <b>shared across all 4 attire slots</b> (No Mercy rule). Appearance differs per attire.</div>
    <div class="sect">FIGHTER SLOTS — 4 save slots (v0.3)</div>
    <div id="fslots"></div>
    <div class="note">Slot 1 is also the game-page slot: the versus screen loads slot 1 (falling back to the legacy autosave). Save here, then take it into versus from the GAME page.</div>`;
  el.querySelectorAll('[data-pk]').forEach(inp=>{
    inp.onchange=()=>{ F.profile[inp.dataset.pk]=inp.type==='number'?+inp.value:inp.value; renderTopbar(); persistQuiet(); };
  });
  el.querySelector('#arch').onchange=e=>{ F.fighting_style.archetype=e.target.value; persistQuiet(); };
  el.querySelector('#align').onchange=e=>{ F.performance.victory_alignment=e.target.value; persistQuiet(); };
  const mk=(host,obj,keys)=>{ keys.forEach(k=>{ const d=document.createElement('div'); d.className='ctl';
    d.innerHTML=`<label style="text-transform:capitalize">${k.replace('_',' ')} <span class="val">${obj[k]}</span></label>
      <input type="range" min="1" max="10" step="1" value="${obj[k]}">`;
    d.querySelector('input').oninput=e=>{ obj[k]=+e.target.value; d.querySelector('.val').textContent=e.target.value; persistQuiet(); };
    host.appendChild(d); }); };
  mk(el.querySelector('#style-sl'), F.fighting_style, ['aggression','high_flyer','technical']);
  const ph=el.querySelector('#param-sl');
  Object.keys(F.parameters).forEach(zone=>{
    const d=document.createElement('div'); d.innerHTML=`<div class="sect" style="margin-top:10px">${zone.toUpperCase()}</div>`;
    ph.appendChild(d); mk(ph, F.parameters[zone], ['offense','defense']);
  });
  renderFighterSlots(el.querySelector('#fslots'));
}

/* ================= FIGHTER SLOTS (v0.3 multi-save) ================= */
const LS_SLOTS = 'wh_create_fighter_slots';
function getSlots(){ try{ const s=JSON.parse(localStorage.getItem(LS_SLOTS)||'[]'); return Array.isArray(s)?s:[]; }catch(e){ return []; } }
function setSlots(s){ try{ localStorage.setItem(LS_SLOTS, JSON.stringify(s)); }catch(e){} }
function renderFighterSlots(host){
  if(!host) return;
  const slots = getSlots();
  host.innerHTML = '';
  for(let i=0;i<4;i++){
    const s = slots[i];
    const b = document.createElement('div');
    b.className = 'kv';
    b.innerHTML = `<span><b>SLOT ${i+1}</b><br><small style="color:var(--dim)">${s&&s.fighter?esc(s.fighter.profile?.name||'CUSTOM')+' · '+esc((s.saved||'').slice(0,10)):'— empty —'}</small></span>
      <span><button class="btn btn-green" data-ss="${i}">💾 SAVE</button> ${s&&s.fighter?`<button class="btn btn-gold" data-sl="${i}">⤒ LOAD</button>`:''}</span>`;
    host.appendChild(b);
  }
  host.querySelectorAll('[data-ss]').forEach(x=>x.onclick=()=>{
    const i=+x.dataset.ss; const slots2=getSlots();
    slots2[i]={ slot:i, saved:new Date().toISOString(), fighter:JSON.parse(JSON.stringify(F)) };
    setSlots(slots2); persistQuiet(); renderFighterSlots(host);
    toast(`Saved to fighter slot ${i+1} ✓`);
  });
  host.querySelectorAll('[data-sl]').forEach(x=>x.onclick=()=>{
    const i=+x.dataset.sl; const slots2=getSlots();
    if(!slots2[i]||!slots2[i].fighter) return;
    F=Object.assign(blankFighter(), JSON.parse(JSON.stringify(slots2[i].fighter)));
    F.performance=Object.assign(blankFighter().performance, F.performance||{});
    if(!Array.isArray(F.decals)) F.decals=[];
    ui.selPart=null; ui.attireCat=null; ui.selSlot=null; ui.selMove=null;
    renderAll(); toast(`Fighter slot ${i+1} loaded ✓`);
  });
}

/* ================= MOVESET — WWE 2K browser, MDickie tap, Tekken content =================
   Slot browser = Tekken input groups (the language). Tap a slot → tap a move
   once = LIVE preview on the fighter (MDickie pattern) → ASSIGN commits.
   Never drag-and-drop. Library = TEKKEN-LIBRARY.json (539 real Tekken moves +
   federation moves, every one showing Tekken input notation). */
function groupOfInput(inp){
  if(inp==='finisher') return 'FINISHER';
  if(inp==='taunt') return 'MOTION / SPECIAL';
  if(inp==='1+3'||inp==='2+4') return 'THROWS — 1+3 · 2+4';
  if(/^[1234]$/.test(inp)) return 'LIMBS — 1 · 2 · 3 · 4';
  if((inp||'').includes(',')) return 'STRINGS';
  return 'MOTION / SPECIAL';
}
const INPUT_GROUP_ORDER = ['LIMBS — 1 · 2 · 3 · 4','THROWS — 1+3 · 2+4','STRINGS','MOTION / SPECIAL','FINISHER'];
function tekkenInputs(){
  if(!tekkenLib) return [];
  const order = { '1':0,'2':1,'3':2,'4':3,'1+3':4,'2+4':5,'finisher':98,'taunt':99 };
  return [...new Set(tekkenLib.moves.map(m=>m.input))].sort((a,b)=>{
    const ga=INPUT_GROUP_ORDER.indexOf(groupOfInput(a)), gb=INPUT_GROUP_ORDER.indexOf(groupOfInput(b));
    if(ga!==gb) return ga-gb;
    return (order[a]??50)-(order[b]??50) || (a<b?-1:1);
  });
}
function moveById(id){ return tekkenLib && tekkenLib.moveById[id]; }
function movesForInput(inp){
  if(!tekkenLib) return [];
  const exact = tekkenLib.moves.filter(m=>m.input===inp);
  const rest = tekkenLib.moves.filter(m=>m.input!==inp);
  return { exact, rest };   // Combot rule: any move, any slot — full library below
}
function renderMoveset(el){
  const inputs = tekkenInputs();
  const assignedCount = inputs.filter(i=>F.moveset[i]).length;
  $('#panel-sub').textContent = `${tekkenLib?tekkenLib.total_moves:0} moves · ${assignedCount}/${inputs.length} slots filled · tap = preview, ASSIGN = commit`;
  el.innerHTML = `
    <div class="note">🥊 <b>Tap an input slot, then tap a move to preview it LIVE on your fighter — then ASSIGN.</b>
    Tap once = preview (MDickie pattern), ASSIGN = commit. No drag-and-drop — WWE 2K, Tekken and MDickie never do that.
    The grey dummy is your opponent. Preview plays the real T3 clip mapped to that input (DESIGN-v0.3 §3);
    a move with a linked <span class="chip">anim_ref</span> plays its own animation instead.</div>
    <div class="sect">TEKKEN INPUT SLOTS (${inputs.length})</div>
    <div id="ms-groups"></div>
    <div id="ms-detail"></div>`;
  const host = el.querySelector('#ms-groups');
  INPUT_GROUP_ORDER.forEach(g=>{
    const ss = inputs.filter(i=>groupOfInput(i)===g);
    if(!ss.length) return;
    const wrap = document.createElement('div'); wrap.className='ms-group';
    const btn = document.createElement('button'); btn.textContent=`${g} (${ss.length})`;
    const list = document.createElement('div'); list.className='ms-slots'; list.style.display='none';
    btn.onclick=()=>{ list.style.display = list.style.display==='none'?'block':'none'; };
    ss.forEach(inp=>{
      const mvId = F.moveset[inp];
      const mv = mvId && moveById(mvId);
      const b = document.createElement('button');
      b.className = 'ms-slot'+(ui.selSlot===inp?' active':'');
      b.innerHTML = `<span class="slot-key">${esc(inp)}</span><span class="slot-move">${mv?esc(mv.move_name):'<span style="color:var(--dim)">— empty —</span>'}</span>`;
      b.onclick = ()=>{ ui.selSlot=inp; ui.selMove=null; renderPanel(); };
      list.appendChild(b);
    });
    wrap.appendChild(btn); wrap.appendChild(list); host.appendChild(wrap);
  });
  if(ui.selSlot) renderMoveDetail(el.querySelector('#ms-detail'), ui.selSlot);
}
function renderMoveDetail(el, input){
  const cur = F.moveset[input] && moveById(F.moveset[input]);
  const { exact, rest } = movesForInput(input);
  el.innerHTML = `
    <div class="sect">ASSIGN — input ${esc(input)}</div>
    <div class="kv"><span>Group</span><b>${esc(groupOfInput(input))}</b></div>
    <div class="kv"><span>Currently</span><b>${cur?esc(cur.move_name):'— empty —'}</b></div>
    <input class="search" id="mv-q" placeholder="Search ${tekkenLib?tekkenLib.total_moves:0} moves…" aria-label="Search moves">
    <div class="sect">MOVES FOR ${esc(input)} (${exact.length})</div>
    <div id="mv-list"></div>
    <div class="sect">FULL LIBRARY — Combot rule: any move, any slot (${rest.length})</div>
    <div id="mv-list2"></div>
    ${cur?`<div class="btn-row"><button class="btn btn-red" id="mv-clear">CLEAR SLOT</button></div>`:''}
    <div class="note">Tap a move <b>once</b> to preview it live on your fighter. Tap <b>ASSIGN</b> to commit it to ${esc(input)}.
    Every entry shows Tekken input notation — wrestling-federation moves carry a 🤼 badge and a Tekken input, never wrestling controls.</div>
    <div id="mv-preview"></div>`;
  const q = el.querySelector('#mv-q');
  const draw = (query)=>{
    const ql = (query||'').trim().toLowerCase();
    const filt = list => ql ? list.filter(m=>(m.move_name+' '+m.move_id+' '+m.input+' '+(m.source_display||'')).toLowerCase().includes(ql)) : list;
    const host1 = el.querySelector('#mv-list'); host1.innerHTML='';
    const host2 = el.querySelector('#mv-list2'); host2.innerHTML='';
    // cap full-library rendering for scroll performance on phone
    mkMoveRows(host1, filt(exact).slice(0,60), input, true);
    mkMoveRows(host2, filt(rest).slice(0,60), input, false);
    if(filt(rest).length>60) host2.insertAdjacentHTML('beforeend',
      `<div class="note">Showing 60 of ${filt(rest).length} — refine the search to see more.</div>`);
  };
  q.oninput = ()=>{ clearTimeout(q._t); q._t=setTimeout(()=>draw(q.value), 300); };
  draw('');
  const c = el.querySelector('#mv-clear');
  if(c) c.onclick = ()=>{ delete F.moveset[input]; ui.selMove=null; renderPanel(); };
}
function mkMoveRows(host, list, input, eligible){
  list.forEach(m=>{
    const b = document.createElement('button');
    const isCur = F.moveset[input]===m.move_id;
    const isSel = ui.selMove===m.move_id;
    b.className = 'move-row'+(eligible?' eligible':'')+(isSel?' selected':'');
    b.innerHTML = `<div class="mv-name">${m.federation?'🤼 ':''}${esc(m.move_name)} ${isCur?'<span class="owned">✓ ASSIGNED</span>':''}</div>
      <div class="mv-meta"><b>${esc(m.input)}</b> · ${esc(m.move_id)} · ${esc(m.source_display||m.source)}${m.damage!=null?' · dmg '+esc(String(m.damage)):''}${m.limb?' · '+esc(m.limb):''}${m.t3_command?' · '+esc(m.t3_command):''}${m.anim_ref?' · 🎬 anim linked':' · <span class="chip">preview: '+esc(m.preview_clip)+'</span>'}</div>`;
    b.onclick = ()=>{   // TAP ONCE = live preview (MDickie); ASSIGN commits
      ui.selMove = m.move_id;
      // Honest preview: real T3 clip mapped to the input. A linked anim_ref
      // (.npy / PAC) isn't browser-playable yet — the mapping stands in.
      if(preview) preview.playClip(m.preview_clip, false);
      drawMovePreview(input, m);
      host.querySelectorAll('.move-row').forEach(x=>x.classList.remove('selected'));
      b.classList.add('selected');
    };
    host.appendChild(b);
  });
}
function drawMovePreview(input, m){
  const host = document.querySelector('#mv-preview');
  if(!host) return;
  host.innerHTML = `
    <div class="sect">PREVIEW — ${esc(m.move_name)}</div>
    <div class="kv"><span>Input</span><b>${esc(m.input)} → slot ${esc(input)}</b></div>
    <div class="kv"><span>Source</span><b>${esc(m.source_display||m.source)}${m.federation?' 🤼 federation-mapped':''}</b></div>
    ${m.startup!=null?`<div class="kv"><span>Startup</span><b>${m.startup}s</b></div>`:''}
    ${m.damage!=null?`<div class="kv"><span>Damage</span><b>${esc(String(m.damage))}</b></div>`:''}
    <div class="btn-row">
      <button class="btn" id="mv-replay">↻ REPLAY PREVIEW</button>
      <button class="btn btn-green" id="mv-assign">ASSIGN → ${esc(input)}</button>
    </div>`;
  host.querySelector('#mv-replay').onclick = ()=>{ if(preview) preview.playClip(m.preview_clip, false); };
  host.querySelector('#mv-assign').onclick = ()=>{
    F.moveset[input] = m.move_id;
    // link signature/finisher shortcuts
    if(input==='finisher') F.performance.finisher = m.move_id;
    ui.selMove = null;
    persistQuiet(); renderPanel();
    toast(`${m.move_name} → ${input} ✓`);
  };
  host.scrollIntoView({ block:'nearest', behavior:'smooth' });
}

/* ================= PERFORMANCE — intro / victory / taunt / signature / finisher ===
   WWE 2K22 Performance-section pattern (quick-picks INSIDE the superstar flow),
   Tekken flavor (walk in, say something, interact — then FIGHT). First clip set =
   real T3 motion (game/js/t3anims.js source). Tap an option = looped live preview. */
const PERF_OPTIONS = {
  intro: [
    { id:'t3_walk_fwd',   name:'Walk In',      desc:'Steady Tekken walk-in' },
    { id:'t3_walk_fwd_b', name:'Walk In (Alt)', desc:'Alternate walk-in' },
    { id:'t3_dash_fwd',   name:'Dash In',      desc:'Fast dash entrance' },
  ],
  victory: [
    { id:'t3_win_rp', name:'Victory · Right Punch', desc:'Classic T3 King win pose' },
    { id:'t3_win_lp', name:'Victory · Left Punch',  desc:'T3 King win pose' },
    { id:'t3_win_rk', name:'Victory · Right Kick',  desc:'T3 King win pose' },
    { id:'t3_win_lk', name:'Victory · Left Kick',   desc:'T3 King win pose' },
  ],
  taunt: [
    { id:'t3_stance',   name:'Taunt · Stance',   desc:'Fighting stance taunt' },
    { id:'t3_stance_b', name:'Taunt · Stance B', desc:'Alternate stance taunt' },
    { id:'t3_stance_c', name:'Taunt · Stance C', desc:'Alternate stance taunt' },
  ],
};
function renderPerformance(el){
  $('#panel-sub').textContent = 'WWE 2K22 Performance pattern · Tekken flavor: walk in, say something, fight';
  const P = F.performance;
  el.innerHTML = `
    <div class="note">🎬 <b>Tap an option — your fighter performs it LIVE.</b> Real Tekken 3 motion clips.
    <b>Tekken flavor:</b> walk in, say something, interact — then FIGHT. Not a wrestling entrance.</div>
    <div class="sect">INTRO — walk-in</div>
    <div class="roster-grid" id="pf-intro"></div>
    <div class="sect">VICTORY — win pose</div>
    <div class="field"><label>CROWD REACTION (Face / Heel / Tweener)</label><select id="pf-align">
      ${['Face','Heel','Tweener'].map(a=>`<option ${P.victory_alignment===a?'selected':''}>${a}</option>`).join('')}
    </select></div>
    <div class="roster-grid" id="pf-victory"></div>
    <div class="sect">TAUNT</div>
    <div class="roster-grid" id="pf-taunt"></div>
    <div class="sect">SIGNATURE / FINISHER</div>
    <div id="pf-sigfin"></div>
    <div class="note">Signature + Finisher are move slots — assign them on the MOVESET tab (FINISHER group),
    or tap below to quick-pick any library move. They save into your fighter and play in matches.</div>`;
  const mk = (hostSel, key, opts)=>{
    const host = el.querySelector(hostSel);
    opts.forEach(o=>{
      const b = document.createElement('button');
      b.className = 'roster-card'+(P[key]===o.id?' active':'');
      b.innerHTML = `<div>${o.name}</div><div style="font-size:11px;color:var(--dim);font-weight:400;margin-top:4px">${o.desc}</div>`;
      b.onclick = ()=>{
        P[key] = o.id;
        if(preview) preview.playClip(o.id, true);   // loop the preview
        persistQuiet(); renderPanel();
      };
      host.appendChild(b);
    });
  };
  mk('#pf-intro','intro',PERF_OPTIONS.intro);
  mk('#pf-victory','victory',PERF_OPTIONS.victory);
  mk('#pf-taunt','taunt',PERF_OPTIONS.taunt);
  el.querySelector('#pf-align').onchange = e=>{ P.victory_alignment=e.target.value; persistQuiet(); };
  // signature / finisher quick-pick from the library
  const sf = el.querySelector('#pf-sigfin');
  [['signature','SIGNATURE'],['finisher','FINISHER']].forEach(([key,label])=>{
    const mv = P[key] && moveById(P[key]);
    const row = document.createElement('div');
    row.className = 'kv';
    row.innerHTML = `<span>${label}</span><span><b>${mv?esc(mv.move_name):'— not set —'}</b>
      <button class="btn btn-gold" id="pf-pick-${key}">PICK</button>
      ${mv?`<button class="btn" id="pf-prev-${key}">↻ PREVIEW</button>`:''}</span>`;
    sf.appendChild(row);
    row.querySelector(`#pf-pick-${key}`).onclick = ()=>perfMovePicker(key, label);
    const pv = row.querySelector(`#pf-prev-${key}`);
    if(pv) pv.onclick = ()=>{ if(preview&&mv) preview.playClip(mv.preview_clip, false); };
  });
}
function perfMovePicker(key, label){
  const moves = tekkenLib ? tekkenLib.moves : [];
  modal(`PICK ${label}`,
    `<input class="search" id="pfq" placeholder="Search ${moves.length} moves…" aria-label="Search moves">
     <div id="pf-list" style="max-height:50vh;overflow-y:auto"></div>
     <div class="note">Tap a move once = live preview on your fighter. Tap SET = assign as ${label}.</div>`,
    [{label:'CANCEL',cls:''}]);
  const list = document.querySelector('#pf-list');
  const draw = (query)=>{
    const ql = (query||'').trim().toLowerCase();
    list.innerHTML = '';
    moves.filter(m=>!ql || (m.move_name+' '+m.move_id+' '+m.input).toLowerCase().includes(ql))
      .slice(0,80).forEach(m=>{
        const b = document.createElement('button');
        b.className = 'move-row';
        b.innerHTML = `<div class="mv-name">${m.federation?'🤼 ':''}${esc(m.move_name)}</div>
          <div class="mv-meta"><b>${esc(m.input)}</b> · ${esc(m.source_display||m.source)}${m.damage!=null?' · dmg '+esc(String(m.damage)):''}</div>
          <div class="btn-row"><button class="btn btn-green">SET AS ${label}</button></div>`;
        // tap row (not the SET button) = preview
        b.onclick = (e)=>{
          if(e.target.closest('.btn')) return;
          if(preview) preview.playClip(m.preview_clip, false);
        };
        b.querySelector('.btn').onclick = ()=>{
          F.performance[key] = m.move_id;
          if(key==='finisher') F.moveset['finisher'] = m.move_id;
          persistQuiet(); closeModal(); renderPanel();
          toast(`${m.move_name} → ${label} ✓`);
        };
        list.appendChild(b);
      });
  };
  document.querySelector('#pfq').oninput = e=>draw(e.target.value);
  draw('');
}

/* ================= LIMBS — DXMMII 4-arm system ================= */
function renderLimbs(el){
  $('#panel-sub').textContent = 'DXMMII 4-arm limb placement — tools/limb-system/dxmmii/';
  const L = F.limbs;
  const presets = Object.keys(L.presets||{});
  el.innerHTML = `
    <div class="sect">LIMB SYSTEM</div>
    <div class="field"><label>ENABLE 4-ARM RIG</label>
      <input type="checkbox" id="limb-enable" ${L.enabled?'checked':''} style="width:24px;height:24px">
    </div>
    <div class="note">774-bone Rigify meta-rig, 39-part modular body, 5-state arm machine.
    Full toolkit: <span class="mono">tools/limb-system/dxmmii/</span> — Blender scripts 01→04, .blend files, QC renders.</div>
    <div class="sect">ARM STATE</div>
    <div class="field"><label>STATE</label><select id="limb-state">
      ${['attached','retracting','hidden','growing','gyro-detached'].map(s=>`<option ${L.arm_state===s?'selected':''}>${s}</option>`).join('')}
    </select></div>
    <div class="sect">SOCKET POSITIONS — L / R (meters, from dxrm_manifest.json)</div>
    <div id="limb-sockets"></div>
    <div class="sect">PRESETS — save your arm placements</div>
    <div class="field"><label>PRESET NAME</label><input type="text" id="limb-preset-name" placeholder="e.g. wide-combat" style="width:100%"></div>
    <div class="btn-row">
      <button class="btn btn-green" id="limb-save-preset">💾 SAVE PRESET</button>
    </div>
    <div class="field"><label>SAVED PRESETS (${presets.length})</label><select id="limb-preset-load">
      <option value="">— select —</option>
      ${presets.map(p=>`<option>${p}</option>`).join('')}
    </select></div>
    <div class="btn-row">
      <button class="btn" id="limb-load-preset">⤒ LOAD</button>
      <button class="btn" id="limb-del-preset">🗑 DELETE</button>
    </div>
    <div class="sect">BLENDER WORKFLOW</div>
    <div class="note">1. Open <span class="mono">tools/limb-system/dxmmii/blend/dxmmii_4arm_rig.blend</span><br>
    2. Run <span class="mono">scripts/01_metarig.py → 02_generate.py → 03_build_body.py → 04_states_demo.py</span><br>
    3. Place arms, save preset here — presets store in fighter JSON.</div>`;

  el.querySelector('#limb-enable').onchange=e=>{ F.limbs.enabled=e.target.checked; renderAll(); };
  el.querySelector('#limb-state').onchange=e=>{ F.limbs.arm_state=e.target.value; persistQuiet(); };

  const sk=el.querySelector('#limb-sockets');
  ['L','R'].forEach(side=>{
    ['x','y','z'].forEach((ax,ai)=>{
      const d=document.createElement('div'); d.className='ctl';
      const v=F.limbs.sockets[side][ai];
      d.innerHTML=`<label>${side}.${ax}<span class="val">${v.toFixed(3)}</span></label>
        <input type="range" min="-0.5" max="0.5" step="0.001" value="${v}" aria-label="${side} ${ax}">`;
      d.querySelector('input').oninput=e=>{
        F.limbs.sockets[side][ai]=+e.target.value;
        d.querySelector('.val').textContent=(+e.target.value).toFixed(3);
        persistQuiet();
      };
      sk.appendChild(d);
    });
  });

  el.querySelector('#limb-save-preset').onclick=()=>{
    const name=(el.querySelector('#limb-preset-name').value||'').trim();
    if(!name){ toast('Name the preset first'); return; }
    F.limbs.presets[name]={
      sockets:JSON.parse(JSON.stringify(F.limbs.sockets)),
      state:F.limbs.arm_state, enabled:F.limbs.enabled,
      saved:new Date().toISOString()
    };
    F.limbs.preset=name;
    renderAll(); toast('Preset saved ✓');
  };
  el.querySelector('#limb-load-preset').onclick=()=>{
    const name=el.querySelector('#limb-preset-load').value;
    if(!name||!F.limbs.presets[name]) return;
    const p=F.limbs.presets[name];
    F.limbs.sockets=JSON.parse(JSON.stringify(p.sockets));
    F.limbs.arm_state=p.state; F.limbs.enabled=p.enabled; F.limbs.preset=name;
    renderAll(); toast('Preset loaded ✓');
  };
  el.querySelector('#limb-del-preset').onclick=()=>{
    const name=el.querySelector('#limb-preset-load').value;
    if(!name) return;
    delete F.limbs.presets[name];
    renderAll(); toast('Preset deleted');
  };
}

/* ================= fighter select / presets / photo / save-load ================= */
function selectBase(id){
  const r=ROSTER.find(x=>x.id===id); if(!r) return;
  F.base=r.id;
  F.model=r.glb||SOLDIER_GLB;
  F.profile.name=r.name;
  ui.selPart=null; ui.attireCat=null;
  if(preview) preview.loadModel(F.model);
}

$('#btn-roster').onclick=()=>{
  const groups=TIERS.map(([tk,label])=>{
    const items=ROSTER.filter(r=>(r.tier||'custom')===tk);
    if(!items.length) return '';
    return `<div class="sect">${label} (${items.length})</div><div class="roster-grid">`+items.map(r=>
      `<button class="roster-card${F.base===r.id?' active':''}" data-r="${r.id}"><div>${r.name}</div>`+
      `<div style="font-size:12px;color:var(--dim);font-weight:400;margin-top:4px">${r.desc||r.title||''}</div>`+
      (r.id!=='new'
        ? `<div style="font-size:10px;margin-top:4px"><span class="${r.modelSrc==='exact'?'owned':'price'}">${r.modelSrc==='exact'?'● REAL MODEL':'● BASE MODEL'}</span></div>`
        : `<div style="font-size:10px;margin-top:4px"><span class="owned">● SOLDIER BASE RIG</span></div>`)+
      `</button>`).join('')+`</div>`;
  }).join('');
  modal('FIGHTER SELECT', groups+
    `<div class="note">Roster fighters load their real GLB from <span class="mono">game/assets/models/</span> — bodies are canon, BODY tab locks. NEW FIGHTER gets full BODY access on the Soldier base rig. <span class="owned">● REAL MODEL</span> = fighter-specific GLB · <span class="price">● BASE MODEL</span> = shared base until a dedicated extraction lands.</div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  document.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>{
    selectBase(b.dataset.r);
    closeModal(); renderAll();
  });
};

$('#btn-presets').onclick=()=>{
  const draw=()=>{
    const ps=getPresets();
    const names=Object.keys(ps).sort();
    modal('FIGHTER PRESETS',
      `<div class="field"><label>SAVE CURRENT AS</label><input id="preset-name" placeholder="e.g. my-pantera-alt" style="width:100%"></div>
       <div class="btn-row"><button class="btn btn-green" id="preset-save">💾 SAVE PRESET</button></div>
       <div class="sect">SAVED PRESETS (${names.length})</div>
       <div id="preset-list">${
         names.length?names.map(n=>{
           const pf=ps[n].fighter||{};
           return `<div class="kv"><span>${esc(n)}<br><small style="color:var(--dim)">${esc(pf.profile?.name||'')} · ${esc(pf.base||'')}</small></span>`+
             `<span><button class="btn btn-gold" data-pl="${esc(n)}">⤒ LOAD</button> <button class="btn btn-red" data-pd="${esc(n)}" data-armed="">🗑</button></span></div>`;
         }).join(''):'<div class="note">No presets yet — name your build above and hit SAVE PRESET.</div>'
       }</div>
       <div class="note">Presets store the full fighter JSON (appearance, moveset, limbs, wardrobe). Loading replaces the current fighter. The autosave slot (<span class="mono">wh_create_fighter_v1</span>) keeps updating as you work.</div>`,
      [{label:'CLOSE',cls:''}]);
    const bodyEl=$('#modal-body');
    bodyEl.querySelector('#preset-save').onclick=()=>{
      const n=(bodyEl.querySelector('#preset-name').value||'').trim();
      if(!n){ toast('Name the preset first'); return; }
      const ps2=getPresets();
      ps2[n]={ saved:new Date().toISOString(), fighter:JSON.parse(JSON.stringify(F)) };
      setPresets(ps2); draw(); toast('Preset saved ✓');
    };
    bodyEl.querySelectorAll('[data-pl]').forEach(b=>b.onclick=()=>{
      const n=b.dataset.pl; const ps2=getPresets();
      if(!ps2[n]) return;
      F=Object.assign(blankFighter(), JSON.parse(JSON.stringify(ps2[n].fighter)));
      ui.selPart=null; ui.attireCat=null; ui.selSlot=null;
      closeModal(); renderAll(); toast(`Preset "${n}" loaded ✓`);
    });
    bodyEl.querySelectorAll('[data-pd]').forEach(b=>b.onclick=()=>{
      if(!b.dataset.armed){ b.dataset.armed='1'; b.textContent='SURE?'; return; }  // two-step delete
      const n=b.dataset.pd; const ps2=getPresets();
      delete ps2[n]; setPresets(ps2); draw(); toast('Preset deleted');
    });
  };
  draw();
};

$('#btn-photo').onclick=()=>{
  if(!preview) return;
  const url=preview.snapshot();
  attire().thumb=url; attire().name=attire().name||F.profile.name;
  renderTopbar(); persist(); toast('Photo captured ✓');
};

$('#btn-save').onclick=()=>{ persist(); };
$('#btn-back-game').onclick=()=>{ persist(); window.location.href='../../game/index.html'; };
$('#btn-export').onclick=()=>{
  const blob=new Blob([JSON.stringify(F,null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=`${(F.profile.name||'fighter').toLowerCase().replace(/\s+/g,'-')}-wh.json`;
  a.click(); URL.revokeObjectURL(a.href); toast('Exported ✓');
};
$('#btn-load').onclick=()=>$('#file-load').click();
$('#file-load').onchange=e=>{
  const f=e.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=()=>{ try{ F=Object.assign(blankFighter(), JSON.parse(r.result)); ui.selPart=null; ui.attireCat=null; renderAll(); toast('Fighter loaded ✓'); }
    catch(err){ modal('LOAD FAILED','<p>Not a valid fighter JSON.</p>',[{label:'OK',cls:'btn-gold'}]); } };
  r.readAsText(f); e.target.value='';
};

/* ================= boot ================= */
async function boot(){
  const had=loadStored();
  // v0.3 migration: older saves lack performance/decals — merge, don't clobber
  const blank = blankFighter();
  F.performance = Object.assign(blank.performance, F.performance||{});
  if(!Array.isArray(F.decals)) F.decals = [];
  try{
    const [pi,md,ms,rb,tl]=await Promise.all([
      fetch('data/PARTS-INDEX.json').then(r=>r.json()),
      fetch('data/MOVE-DATABASE.json').then(r=>r.json()),
      fetch('data/MOVE-SLOTS.json').then(r=>r.json()),
      fetch('data/ROSTER-BASE.json').then(r=>r.json()),
      fetch('data/TEKKEN-LIBRARY.json').then(r=>r.json()).catch(()=>null),
    ]);
    catalog=new Catalog(pi); moveDb=md; moveSlots=ms;
    if(tl){
      tl.moveById = {};
      tl.moves.forEach(m=>{ tl.moveById[m.move_id]=m; });
      tekkenLib = tl;
    }
    // decal libraries (pattern: customization/decal-library/<fighter>/MANIFEST.json)
    decalLibs = [];
    await Promise.all(DECAL_LIBS.map(async lib=>{
      try{
        const man = await fetch(`../decal-library/${lib}/MANIFEST.json`).then(r=>r.json());
        decalLibs.push({ lib, manifest:man });
      }catch(e){ console.warn('decal lib failed:', lib); }
    }));
    ROSTER=[
      { id:'new', name:'NEW FIGHTER', desc:'WMXIX default CAW base', glb:SOLDIER_GLB, tier:'custom', modelSrc:'exact' },
      ...rb.fighters.map(f=>({ id:f.id, name:f.name, desc:f.title, title:f.title, glb:f.glb,
        tier:f.tier, modelSrc:f.modelSrc, style:f.style, archetype:f.archetype, base:f.base })),
    ];
    // a stored fighter may reference a base that no longer exists — fall back to new
    if(!ROSTER.some(r=>r.id===F.base)){ F.base='new'; F.model=SOLDIER_GLB; }
    if(!F.model) F.model=SOLDIER_GLB;
  }catch(e){
    console.error('data load failed',e);
    document.getElementById('loader').innerHTML='<div>DATA LOAD FAILED — serve over http</div>';
    return;
  }
  preview=new Preview3D($('#preview3d'));
  window.__preview=preview;   // debug/testing handle
  preview.onReady=()=>{ renderAll(); };
  // load the stored/current fighter's model (roster GLB or Soldier base)
  if(F.model && F.model!==SOLDIER_GLB) preview.loadModel(F.model);
  renderAll();
  if(!had) toast('New fighter — start with BODY');
}
boot();
