/* app.js — Create Fighter hub logic.
   Tekken loop: pick category -> grid -> hover try-on -> BUY -> EQUIP -> conflict
   check (Replace/Cancel) -> color/material edit. Fighter JSON save format matches
   customization/CHARACTER-CREATION.md §6, extended with wardrobe/attire slots. */
import { Preview3D, SKIN_TONES } from './preview3d.js';
import { Catalog, CATEGORIES, CONFLICTS } from './catalog.js';

const LS_KEY = 'wh_create_fighter_v1';
const START_MONEY = 12400;

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

const ROSTER = [
  { id:'new', name:'NEW FIGHTER', desc:'WMXIX default CAW base', tone:'#c98d5e' },
  { id:'pantera', name:'PANTERA', desc:'Roster — grappler', tone:'#7c4a2d' },
  { id:'demonio', name:'DEMONIO', desc:'Roster — striker', tone:'#a06a42' },
];

/* ---------------- state ---------------- */
function blankAttire(){ return { name:'', thumb:'', equipped:{}, owned:[], colors:{} }; }
function blankFighter(){
  return {
    version: 1, app:'wh-create-fighter',
    profile:{ name:'NEW FIGHTER', short_name:'NEWF', alias:'', height:`6'0"`, weight:220,
      music:'', titantron:'', soul:'—', element:'—', land:'—',
      title:['',''], picture:'' },
    base:'new',
    body:{ body_type:'Medium 1', skin_tone:'#c98d5e', head_shape:'male_3',
      proportions:{ height:1, weight:1, muscle:1 } },
    attireIndex: 0,
    attires:[ blankAttire(), blankAttire(), blankAttire(), blankAttire() ],
    wardrobe:[ null,null,null,null,null,null,null,null,null,null ],
    moveset:{},   // slotName -> move_id
    fighting_style:{ archetype:'grappler', aggression:5, high_flyer:5, technical:5 },
    parameters:{ head:{offense:5,defense:5}, body:{offense:5,defense:5}, arms:{offense:5,defense:5},
                 legs:{offense:5,defense:5}, flying:{offense:5,defense:5} },
    wallet: START_MONEY,
  };
}
let F = blankFighter();
let catalog=null, moveDb=null, moveSlots=null;
let preview=null;
let ui = { tab:'body', attireCat:null, gridPage:0, gridQuery:'', selPart:null, selSlot:null, wardSel:0 };

const $ = s=>document.querySelector(s);
const attire = ()=>F.attires[F.attireIndex];

/* ---------------- persistence ---------------- */
function persist(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(F)); }catch(e){} toast('Saved ✓'); }
function loadStored(){ try{ const s=localStorage.getItem(LS_KEY); if(s){ F=Object.assign(blankFighter(), JSON.parse(s)); return true; } }catch(e){} return false; }
function toast(msg){ const t=$('#save-toast'); t.textContent=msg; setTimeout(()=>t.textContent='',2500); }

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
  preview.setSkinTone(F.body.skin_tone);
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
    b.innerHTML = `<span class="athumb" ${a.thumb?`style="background-image:url('${a.thumb}')"`:''}></span>${nm}`;
    b.title = nm + (i>0?'':' (clone source for empty slots)');
    b.onclick=()=>{ F.attireIndex=i; if(!F.attires[i].name && i>0){ /* empty slot: clone attire 1 appearance */ const src=JSON.parse(JSON.stringify(F.attires[0])); src.name=''; src.thumb=''; F.attires[i]=src; } ui.selPart=null; renderAll(); };
    tabs.appendChild(b);
  });
}

/* ---------------- left rail ---------------- */
function setTab(tab){
  ui.tab=tab; ui.attireCat=null; ui.selPart=null; ui.gridPage=0;
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
  ({ body:renderBody, attire:renderAttire, wardrobe:renderWardrobe, profile:renderProfile, moveset:renderMoveset })[ui.tab](body);
}

/* ================= BODY ================= */
function renderBody(el){
  $('#panel-sub').textContent = 'Wrestling CAW — body, skin, head, hair';
  el.innerHTML = `
    <div class="sect">BODY TYPE — No Mercy 14</div>
    <div class="roster-grid" id="bodytypes"></div>
    <div class="sect">SKIN TONE — 8 tones</div>
    <div class="swatches" id="skintones"></div>
    <div class="sect">PROPORTIONS — WMXIX parametric</div>
    <div id="propsliders"></div>
    <div class="sect">HEAD</div>
    <div class="field"><label>HEAD SHAPE</label><select id="headshape">
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
    b.onclick=()=>{ F.body.body_type=t.name; renderAll(); };
    bt.appendChild(b);
  });
  const st=el.querySelector('#skintones');
  SKIN_TONES.forEach(hex=>{
    const s=document.createElement('div');
    s.className='swatch'+(F.body.skin_tone===hex?' active':'');
    s.style.background=hex; s.title=hex;
    s.onclick=()=>{ F.body.skin_tone=hex; renderAll(); };
    st.appendChild(s);
  });
  const sl=el.querySelector('#propsliders');
  [['height','Height',0.85,1.15],['weight','Weight',0.85,1.3],['muscle','Muscle',0.85,1.3]].forEach(([k,label,lo,hi])=>{
    const d=document.createElement('div'); d.className='ctl';
    d.innerHTML=`<label>${label}<span class="val">${F.body.proportions[k].toFixed(2)}</span></label>
      <input type="range" min="${lo}" max="${hi}" step="0.01" value="${F.body.proportions[k]}" aria-label="${label}">`;
    d.querySelector('input').oninput=e=>{ F.body.proportions[k]=+e.target.value;
      d.querySelector('.val').textContent=(+e.target.value).toFixed(2); syncPreview(); persistQuiet(); };
    d.querySelector('input').onchange=()=>persistQuiet();
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
  if(!ui.attireCat){
    $('#panel-sub').textContent = 'Tekken item shop — pick a category';
    const eq = attire().equipped;
    el.innerHTML = `<div class="note">Buy → Equip loop. Items try on instantly. <span class="geo-badge">GEOMETRY PENDING</span> on every part: real ymg/obj meshes aren't wired yet, so equip shows a labeled socket marker + records the part in your fighter JSON. No fake equipped meshes — ever.</div>`;
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
    <div id="style-sl"></div>
    <div class="sect">PARAMETERS — offense/defense per zone (1–10)</div>
    <div id="param-sl"></div>
    <div class="note">🔒 Moveset, AI style, and parameters are <b>shared across all 4 attire slots</b> (No Mercy rule). Appearance differs per attire.</div>`;
  el.querySelectorAll('[data-pk]').forEach(inp=>{
    inp.onchange=()=>{ F.profile[inp.dataset.pk]=inp.type==='number'?+inp.value:inp.value; renderTopbar(); persistQuiet(); };
  });
  el.querySelector('#arch').onchange=e=>{ F.fighting_style.archetype=e.target.value; persistQuiet(); };
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
}

/* ================= MOVESET ================= */
function flatSlots(){
  // walk MOVE-SLOTS.json -> [{group, key, slot}]
  // handles both forms: {slots:{input:slot}} and direct {input:slot}, plus bare arrays
  const out=[];
  const walk=(o,path)=>{
    if(!o||typeof o!=='object') return;
    if(Array.isArray(o)){
      if(o.every(v=>typeof v==='string'))
        o.forEach(v=>out.push({group:path.join(' › '),key:v,slot:v}));
      return;
    }
    if(o.slots&&typeof o.slots==='object'&&!Array.isArray(o.slots)){
      for(const [k,v] of Object.entries(o.slots)) out.push({group:path.join(' › '),key:k,slot:v});
      return;
    }
    const entries=Object.entries(o).filter(([k])=>!k.startsWith('_'));
    if(entries.length&&entries.every(([,v])=>typeof v==='string')){
      for(const [k,v] of entries) out.push({group:path.join(' › '),key:k,slot:v});
      return;
    }
    for(const [k,v] of entries) walk(v,[...path,k]);
  };
  walk(moveSlots,[]);
  return out;
}
function renderMoveset(el){
  const slots=flatSlots();
  $('#panel-sub').textContent=`${slots.length} slots · WWE layout, Tekken striking depth`;
  const groups={};
  slots.forEach(s=>{ (groups[s.group]=groups[s.group]||[]).push(s); });
  el.innerHTML=`
    <div class="note">🥊 <b>Two-fighter preview is live</b> — the grey dummy is in the ring with your fighter.
    Pick a slot, assign a move. <b>Live animation test on move select is pending</b>: most move entries have <span class="chip">anim_ref: null</span> until per-move clip links land (see CHARACTER-CREATION.md §9.4). Slot → move data saves today; animation playback wires in with the clip links.</div>
    <div class="sect">MOVE SLOTS (${slots.length})</div>
    <div id="ms-groups"></div>
    <div id="ms-detail"></div>`;
  const host=el.querySelector('#ms-groups');
  Object.entries(groups).forEach(([g,ss])=>{
    const wrap=document.createElement('div'); wrap.className='ms-group';
    const btn=document.createElement('button'); btn.textContent=`${g} (${ss.length})`;
    const list=document.createElement('div'); list.className='ms-slots'; list.style.display='none';
    btn.onclick=()=>{ list.style.display=list.style.display==='none'?'block':'none'; };
    ss.forEach(s=>{
      const mvId=F.moveset[s.slot];
      const mv=mvId&&moveDb.sample_moves.find(m=>m.move_id===mvId);
      const b=document.createElement('button'); b.className='ms-slot'+(ui.selSlot===s.slot?' active':'');
      b.innerHTML=`<span class="slot-key">${esc(s.key)}</span><span class="slot-move">${mv?esc(mv.move_name):'<span style="color:var(--dim)">— empty —</span>'}</span>`;
      b.onclick=()=>{ ui.selSlot=s.slot; renderPanel(); };
      list.appendChild(b);
    });
    wrap.appendChild(btn); wrap.appendChild(list); host.appendChild(wrap);
  });
  if(ui.selSlot) renderMoveDetail(el.querySelector('#ms-detail'), slots.find(s=>s.slot===ui.selSlot));
}
function renderMoveDetail(el, s){
  const cur=F.moveset[s.slot];
  const eligible=moveDb.sample_moves.filter(m=>(m.slot_eligibility||[]).includes(s.slot));
  const others=moveDb.sample_moves.filter(m=>!(m.slot_eligibility||[]).includes(s.slot));
  el.innerHTML=`
    <div class="sect">ASSIGN — ${esc(s.slot)}</div>
    <div class="kv"><span>Input</span><b>${esc(s.key)}</b></div>
    <div class="kv"><span>Group</span><b>${esc(s.group)}</b></div>
    ${eligible.length?'<div class="sect">ELIGIBLE MOVES</div>':''}
    <div id="mv-list"></div>
    ${others.length?'<div class="sect">FULL LIBRARY (Combot rule — any move, any slot)</div><div id="mv-list2"></div>':''}
    ${cur?`<div class="btn-row"><button class="btn btn-red" id="mv-clear">CLEAR SLOT</button></div>`:''}
    <div class="note">Database: ${moveDb.sample_moves.length} sample moves loaded from MOVE-DATABASE.json (skeleton — full 400+ No Mercy list populates as the library grows). Combot precedent: cross-roster mixing allowed.</div>`;
  const mk=(host,list,elig)=>{
    list.forEach(m=>{
      const b=document.createElement('button'); b.className='move-row'+(elig?' eligible':'');
      b.innerHTML=`<div class="mv-name">${esc(m.move_name)} ${cur===m.move_id?'<span class="owned">✓ ASSIGNED</span>':''}</div>
        <div class="mv-meta">${esc(m.move_id)} · ${esc(m.source)} · power ${esc(String(m.power))}${m.properties&&m.properties.length?' · '+m.properties.map(esc).join(', '):''}${m.anim_ref?' · 🎬 anim linked':' · <span class="chip">anim_ref: null</span>'}</div>`;
      b.onclick=()=>{ F.moveset[s.slot]=m.move_id; persistQuiet(); renderPanel();
        toast(`${m.move_name} → ${s.slot}`); };
      host.appendChild(b);
    });
  };
  mk(el.querySelector('#mv-list'), eligible, true);
  mk(el.querySelector('#mv-list2'), others, false);
  const c=el.querySelector('#mv-clear');
  if(c) c.onclick=()=>{ delete F.moveset[s.slot]; renderPanel(); };
}

/* ================= fighter select / photo / save-load ================= */
$('#btn-roster').onclick=()=>{
  modal('FIGHTER SELECT', `<div class="roster-grid">${ROSTER.map(r=>
    `<button class="roster-card${F.base===r.id?' active':''}" data-r="${r.id}"><div>${r.name}</div><div style="font-size:12px;color:var(--dim);font-weight:400;margin-top:4px">${r.desc}</div></button>`).join('')}</div>
    <div class="note">Roster fighters' bodies are canon (BODY tab locks for them). NEW FIGHTER gets full BODY access.</div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  document.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>{
    const r=ROSTER.find(x=>x.id===b.dataset.r);
    F.base=r.id; F.profile.name=r.name;
    if(r.id!=='new') F.body.skin_tone=r.tone;
    closeModal(); renderAll();
  });
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
  try{
    const [pi,md,ms]=await Promise.all([
      fetch('data/PARTS-INDEX.json').then(r=>r.json()),
      fetch('data/MOVE-DATABASE.json').then(r=>r.json()),
      fetch('data/MOVE-SLOTS.json').then(r=>r.json()),
    ]);
    catalog=new Catalog(pi); moveDb=md; moveSlots=ms;
  }catch(e){
    console.error('data load failed',e);
    document.getElementById('loader').innerHTML='<div>DATA LOAD FAILED — serve over http</div>';
    return;
  }
  preview=new Preview3D($('#preview3d'));
  window.__preview=preview;   // debug/testing handle
  preview.onReady=()=>{ renderAll(); };
  renderAll();
  if(!had) toast('New fighter — start with BODY');
}
boot();
