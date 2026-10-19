/* suite.js — Creation Suite hub logic.
   Laws: tap slot → scroll library → tap to assign. NO drag-and-drop anywhere. Phone-first.
   Menu trees verbatim from teardown games (see menu-data.js + UI-EXTRACTION-LOG.md). */
import { SuiteViewer } from './viewer3d.js';
import { ATTIRE_TREE, BODY_TREE, PARTS_TREE, JIGGLE_AREAS, JIGGLE_PARAMS, JIGGLE_FAMILIES, PLACE_AXES, MENU_SRC } from './menu-data.js';

const LS_KEY = 'wh_creation_suite_v1';
const START_MONEY = 12400;
const $ = s=>document.querySelector(s);

const BODY_TYPES = ['Skinny 1','Skinny 2','Medium 1','Medium 2','Thick 1','Thick 2','Fat 1','Fat 2',
  'Austin','HBK','Rikishi','Rock','Hairy 1','Hairy 2','King Frame','Ganryu Frame',
  'Skinny F','Medium F','Thick F','Fat F','Athletic F','Curvy F','Petite F','Tall F','Dancer F'];
const SKIN_TONES = ['#f1c9a5','#e8b48a','#dba06e','#c98d5e','#a06a42','#7c4a2d','#5a3420','#3f2417'];
const PROPS = [['height','Height',0.85,1.15],['weight','Weight',0.85,1.3],['muscle','Muscle',0.85,1.3],
  ['shoulder','Shoulders',0.85,1.25],['chest','Chest',0.85,1.3],['waist','Waist',0.85,1.25],
  ['hips','Hips',0.85,1.3],['arms','Arms',0.85,1.3],['legs','Legs',0.85,1.3]];
const SOULS=['—','TOU','SHA','YIN','YANG','KAMI','ONI','RYU','TEN'];
const TITLE_A=['RAGING','SILENT','GOLDEN','BROKEN','HOWLING','IRON','CRIMSON','LONE'];
const TITLE_B=['BEAST','PANTHER','KING','GHOST','STORM','WOLF','TIGER','DEMON'];

/* suite_slot -> ATTIRE category slot key */
const SLOT2CAT = { mask:'3', eye_lenses:'6', cowl:'3', gauntlets:'H', hair:'2',
  decal_logo:'8', eye:'EYES', tights:'11', pants:'11', top:'9', outfit:'9', scarf:'12', face:'8' };

function blankAttire(){ return { name:'', thumb:'', equipped:{}, owned:[], colors:{}, placements:{} }; }
function blankFighter(){
  return { version:1, app:'wh-creation-suite',
    profile:{ name:'NEW FIGHTER', short_name:'NEWF', soul:'—', title:['',''] },
    body:{ body_type:'Medium 1', skin_tone:'#c98d5e',
      proportions:{ height:1, weight:1, muscle:1, shoulder:1, chest:1, waist:1, hips:1, arms:1, legs:1 } },
    jiggle:{ family:'female', areas:{} },
    attireIndex:0, attires:[blankAttire(),blankAttire(),blankAttire(),blankAttire()],
    wardrobe:[null,null,null,null,null,null,null,null,null,null],
    wallet:START_MONEY };
}
let F = blankFighter();
let PARTS = [];       // parts-catalog.json
let JIGGLE = null;    // jiggle-schema.json
let viewer = null;
let ui = { tab:'body', attireCat:null, partsCat:null, selPart:null, wardSel:0, nudgeStep:0.001 };

const attire = ()=>F.attires[F.attireIndex];
const esc = s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- persistence ---------- */
function persistQuiet(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(F)); }catch(e){} }
function persist(){ persistQuiet(); toast('Saved ✓'); }
function toast(m){ const t=$('#save-toast'); t.textContent=m; t.classList.add('show');
  clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'),2200); }

/* ---------- modal ---------- */
function modal(title, bodyHTML, actions){
  $('#modal-title').textContent=title; $('#modal-body').innerHTML=bodyHTML;
  const box=$('#modal-actions'); box.innerHTML='';
  (actions||[{label:'OK',cls:'btn-gold'}]).forEach(a=>{
    const b=document.createElement('button'); b.className='btn '+(a.cls||''); b.textContent=a.label;
    b.onclick=()=>{ closeModal(); a.fn&&a.fn(); }; box.appendChild(b); });
  $('#modal').hidden=false; $('#modal-scrim').hidden=false;
}
function closeModal(){ $('#modal').hidden=true; $('#modal-scrim').hidden=true; }
$('#modal-scrim').onclick=closeModal;

/* ---------- 3D sync ---------- */
function defaultPlacement(def){
  const o = def.offset||[0,0,0];
  return { px:o[0], py:o[1], pz:o[2], rx:0, ry:0, rz:0, s:def.scale||1 };
}
function syncParts3D(){
  if(!viewer||!viewer.ready) return;
  const eq = attire().equipped, seen = new Set();
  for(const [slotKey, partId] of Object.entries(eq)){
    const p = PARTS.find(x=>x.id===partId);
    if(!p || p.part_class!=='mesh_part' || !p.glb){ continue; }
    seen.add(partId);
    const place = Object.assign(defaultPlacement(p), attire().placements[partId]||{});
    if(!viewer.parts.has(partId))
      viewer.attachPart(partId, '../../'+p.glb, p, place).catch(()=>{});
    else
      viewer.updatePlacement(partId, place);
  }
  for(const pid of [...viewer.parts.keys()]) if(!seen.has(pid)) viewer.detachPart(pid);
}
function syncPreview(){
  if(!viewer) return;
  viewer.setProportions(F.body.proportions);
  syncParts3D();
}

/* ---------- topbar ---------- */
function renderTopbar(){
  $('#fighter-name').textContent = F.profile.name||'NEW FIGHTER';
  $('#breadcrumb').textContent = `${F.profile.name||'New Fighter'} > Attire ${F.attireIndex+1} > ${ui.tab.toUpperCase()}${ui.attireCat?' > '+ui.attireCat.label:''}${ui.partsCat?' > '+ui.partsCat.label:''}`;
  $('#wallet-amt').textContent = F.wallet.toLocaleString();
  const tabs=$('#attire-tabs'); tabs.innerHTML='';
  F.attires.forEach((a,i)=>{
    const b=document.createElement('button');
    b.className='attire-tab'+(i===F.attireIndex?' active':''); b.setAttribute('role','tab');
    b.innerHTML=`<span class="athumb"${a.thumb?` style="background-image:url('${a.thumb}')}`:''}></span>${esc(a.name||`ATTIRE ${i+1}`)}`;
    b.onclick=()=>{ F.attireIndex=i; ui.selPart=null; renderAll(); };
    tabs.appendChild(b);
  });
}

/* ---------- rail ---------- */
function setTab(t){
  ui.tab=t; ui.attireCat=null; ui.partsCat=null; ui.selPart=null;
  document.querySelectorAll('.rail-btn').forEach(x=>x.classList.toggle('active',x.dataset.tab===t));
  if(t!=='parts') hidePlaceDock();
  renderAll();
}
document.querySelectorAll('.rail-btn').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));

function renderAll(){ renderTopbar(); renderPanel(); syncPreview(); persistQuiet(); }
function renderPanel(){
  const body=$('#panel-body');
  $('#panel-title').textContent=ui.tab.toUpperCase(); $('#panel-sub').textContent='';
  body.innerHTML='';
  ({body:renderBody,attire:renderAttire,parts:renderParts,jiggle:renderJiggle,
    wardrobe:renderWardrobe,profile:renderProfile,moveset:renderMoveset})[ui.tab](body);
}

/* ================= BODY ================= */
function renderBody(el){
  $('#panel-sub').textContent='Wrestling CAW — No Mercy body types, WMXIX proportions';
  el.innerHTML=`
    <div class="sect">BODY TYPE — 14M + 9F (No Mercy)</div><div class="roster-grid" id="btypes"></div>
    <div class="sect">SKIN TONE — 8 tones</div><div class="swatches" id="stones"></div>
    <div class="sect">PROPORTIONS — WMXIX parametric (live)</div><div id="psl"></div>`;
  const bt=el.querySelector('#btypes');
  BODY_TYPES.forEach(t=>{ const b=document.createElement('button');
    b.className='roster-card'+(F.body.body_type===t?' active':''); b.textContent=t;
    b.onclick=()=>{ F.body.body_type=t; renderAll(); }; bt.appendChild(b); });
  const st=el.querySelector('#stones');
  SKIN_TONES.forEach(h=>{ const s=document.createElement('div');
    s.className='swatch'+(F.body.skin_tone===h?' active':''); s.style.background=h; s.title=h;
    s.onclick=()=>{ F.body.skin_tone=h; renderAll(); }; st.appendChild(s); });
  const sl=el.querySelector('#psl');
  PROPS.forEach(([k,label,lo,hi])=>{
    const d=document.createElement('div'); d.className='ctl'; d.id='prop-'+k;
    d.innerHTML=`<label>${label}<span class="val">${F.body.proportions[k].toFixed(2)}</span></label>
      <input type="range" min="${lo}" max="${hi}" step="0.01" value="${F.body.proportions[k]}" aria-label="${label}">`;
    const inp=d.querySelector('input');
    inp.oninput=()=>{ F.body.proportions[k]=+inp.value;
      d.querySelector('.val').textContent=(+inp.value).toFixed(2); syncPreview(); persistQuiet(); };
    sl.appendChild(d);
  });
}

/* ================= ATTIRE (T7 spine) ================= */
function partsForCat(slotKey){
  return PARTS.filter(p=>SLOT2CAT[p.suite_slot]===slotKey);
}
function renderAttire(el){
  if(!ui.attireCat){
    $('#panel-sub').textContent='Tekken item shop — pick a category (T7 slots verbatim)';
    el.innerHTML=`<div class="note">Buy → Equip loop · hover try-on · conflict Replace/Cancel · 5 color channels.
      Categories are Tekken 7's real 17 slot IDs + T6 subdivisions (see UI-EXTRACTION-LOG.md).</div><div id="cats"></div>`;
    const host=el.querySelector('#cats');
    ATTIRE_TREE.forEach(c=>{
      const b=document.createElement('button');
      b.className='subcat'+(attire().equipped[c.slot]?' equipped':'');
      b.id='cat-'+c.slot;
      const n=partsForCat(c.slot).length;
      b.innerHTML=`<span class="sc-ico">${c.icon}</span><span>${c.label}${attire().equipped[c.slot]?'<br><small style="color:var(--green)">✓ equipped</small>':''}</span><span class="sc-count">${n} parts</span>`;
      b.onclick=()=>{ ui.attireCat=c; ui.selPart=null; renderAll(); };
      host.appendChild(b);
      (c.children||[]).forEach(sc=>{
        const sb=document.createElement('button');
        sb.className='subcat'+(attire().equipped[sc.slot]?' equipped':'');
        sb.id='cat-'+sc.slot; sb.style.marginLeft='18px';
        sb.innerHTML=`<span class="sc-ico">${sc.icon}</span><span>↳ ${sc.label}</span><span class="sc-count">${partsForCat(sc.slot).length} parts</span>`;
        sb.onclick=()=>{ ui.attireCat=sc; ui.selPart=null; renderAll(); };
        host.appendChild(sb);
      });
    });
    return;
  }
  renderPartGrid(el, ui.attireCat, partsForCat(ui.attireCat.slot), 'attireCat');
}

/* ================= PARTS (wired libraries) ================= */
function renderParts(el){
  if(!ui.partsCat){
    $('#panel-sub').textContent='Wired part libraries — tap a library, tap a part';
    el.innerHTML=`<div class="note">Eyes, decals, masks, hair — pulled from the real repo libraries
      (PARTS-REGISTRY.json, eye-library/, decal-library/). Tap library → scroll → tap part to assign.</div><div id="pcats"></div>`;
    const host=el.querySelector('#pcats');
    PARTS_TREE.forEach(c=>{
      const list = c.key==='eyes' ? PARTS.filter(p=>p.suite_slot==='eye')
        : c.key==='decals' ? PARTS.filter(p=>['decal_logo','tights','pants'].includes(p.suite_slot))
        : c.key==='masks' ? PARTS.filter(p=>['mask','eye_lenses','cowl','gauntlets'].includes(p.suite_slot))
        : PARTS.filter(p=>p.suite_slot==='hair');
      const b=document.createElement('button'); b.className='subcat'; b.id='pcat-'+c.key;
      b.innerHTML=`<span class="sc-ico">${c.icon}</span><span>${c.label}<br><small style="color:var(--dim)">${esc(c.note.split('—')[0])}</small></span><span class="sc-count">${list.length} parts</span>`;
      b.onclick=()=>{ ui.partsCat={...c, list}; ui.selPart=null; renderAll(); };
      host.appendChild(b);
    });
    return;
  }
  renderPartGrid(el, ui.partsCat, ui.partsCat.list, 'partsCat');
}

/* ---- shared tap-to-assign grid ---- */
function renderPartGrid(el, cat, list, backKey){
  const slotKey = cat.slot || cat.key;
  $('#panel-sub').textContent=`${cat.label} — ${list.length} parts · tap to ${cat.key==='eyes'||cat.key==='decals'?'apply':'equip'}`;
  el.innerHTML=`
    <div class="back-row"><button class="btn back-btn" id="btn-back">← ${backKey==='attireCat'?'CATEGORIES':'LIBRARIES'}</button></div>
    <div class="item-grid" id="grid"></div><div id="pdetail"></div>`;
  el.querySelector('#btn-back').onclick=()=>{ ui[backKey]=null; ui.selPart=null; hidePlaceDock(); renderAll(); };
  const grid=el.querySelector('#grid');
  list.forEach(p=>{
    const owned = attire().owned.includes(p.id);
    const eqd = Object.values(attire().equipped).includes(p.id);
    const d=document.createElement('div');
    d.className='item-card'+(ui.selPart&&ui.selPart.id===p.id?' selected':'')+(eqd?' equipped':'');
    d.id='part-'+p.id;
    d.innerHTML=`<div class="item-mono">${p.part_class==='mesh_part'?'🧩':'🎨'}</div>
      <div class="item-name">${esc(p.name)}</div>
      <div class="item-meta">${p.part_class==='mesh_part'?'mesh · '+esc(p.socket||''):esc(p.library||'')}<br>
      ${owned?'<span class="owned">OWNED</span>':'<span class="price">500G</span>'}</div>`;
    d.onclick=()=>{ ui.selPart=p; renderPanel(); renderTopbar(); };
    grid.appendChild(d);
  });
  if(ui.selPart) renderPartDetail(el.querySelector('#pdetail'), ui.selPart, slotKey);
}
function renderPartDetail(el, p, slotKey){
  const owned = attire().owned.includes(p.id);
  const eqd = Object.values(attire().equipped).includes(p.id);
  el.innerHTML=`
    <div class="sect">SELECTED — ${esc(p.name)}</div>
    <div class="kv"><span>Part ID</span><b style="font-size:11px">${esc(p.id)}</b></div>
    <div class="kv"><span>Class</span><b>${esc(p.part_class)}</b></div>
    <div class="kv"><span>Library</span><b>${esc(p.library||'—')}</b></div>
    ${p.glb?`<div class="kv"><span>Mesh</span><b style="font-size:11px">${esc(p.glb)}</b></div>
    <div class="kv"><span>Socket</span><b>${esc(p.socket||'—')}</b></div>`:''}
    <div class="btn-row" id="p-actions"></div>`;
  const box=el.querySelector('#p-actions');
  if(p.part_class==='mesh_part'){
    if(!eqd){
      const b=document.createElement('button'); b.className='btn btn-gold'; b.id='btn-equip-part';
      b.textContent=owned?'EQUIP':'BUY — 500G';
      b.onclick=()=>{ if(!owned){ if(F.wallet<500){ modal('NOT ENOUGH FIGHT MONEY','<p>Need <b>500G</b>.</p>',[{label:'OK',cls:'btn-gold'}]); return; }
          F.wallet-=500; attire().owned.push(p.id); }
        attire().equipped[slotKey]=p.id;
        if(!attire().placements[p.id]){ const def=PARTS.find(x=>x.id===p.id); attire().placements[p.id]=defaultPlacement(def||{}); }
        renderAll(); showPlaceDock(p); toast('Equipped ✓ — nudge it into place'); };
      box.appendChild(b);
    } else {
      const b1=document.createElement('button'); b1.className='btn btn-blue'; b1.id='btn-place-part'; b1.textContent='⌖ PLACEMENT';
      b1.onclick=()=>showPlaceDock(p); box.appendChild(b1);
      const b2=document.createElement('button'); b2.className='btn btn-red'; b2.id='btn-unequip-part'; b2.textContent='UNEQUIP';
      b2.onclick=()=>{ for(const k of Object.keys(attire().equipped)) if(attire().equipped[k]===p.id) delete attire().equipped[k];
        hidePlaceDock(); renderAll(); }; box.appendChild(b2);
    }
  } else {
    const b=document.createElement('button'); b.className='btn btn-green'; b.id='btn-apply-part'; b.textContent='APPLY';
    b.onclick=()=>{ attire().equipped[slotKey]=p.id;
      if(viewer) viewer.setMarker('tex-'+p.id, p.socket||'face', '#e8b64c', p.name);
      renderAll(); toast('Applied ✓'); };
    box.appendChild(b);
  }
}

/* ================= PLACEMENT DOCK (accuracy UI) ================= */
function showPlaceDock(p){
  ui.selPart=p;
  $('#place-dock').hidden=false;
  $('#pd-partname').textContent=p.name;
  $('#pd-socket').textContent=(p.socket||'head')+(p.modeled_in_place_for?` (modeled in place for ${p.modeled_in_place_for})`:'');
  if(!attire().placements[p.id]) attire().placements[p.id]=defaultPlacement(p);
  buildPlaceAxes();
  updatePlaceReadout();
  syncParts3D();
}
function hidePlaceDock(){ $('#place-dock').hidden=true; }
$('#pd-close').onclick=hidePlaceDock;
document.querySelectorAll('#pd-steps button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#pd-steps button').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); ui.nudgeStep=+b.dataset.step; });
function placeVal(){ return attire().placements[ui.selPart.id]; }
function buildPlaceAxes(){
  const host=$('#pd-axes'); host.innerHTML='';
  const pl=placeVal();
  PLACE_AXES.forEach(ax=>{
    const d=document.createElement('div'); d.className='pd-axis'; d.id='pax-'+ax.key;
    d.innerHTML=`<div class="pd-lbl"><span>${ax.label} (${ax.unit})</span><b>${fmtAx(ax,pl[ax.key])}</b></div>
      <div class="pd-ctl">
        <button data-dir="-1" aria-label="nudge down">−</button>
        <input type="range" min="${ax.min}" max="${ax.max}" step="${ax.step}" value="${pl[ax.key]}" aria-label="${ax.label}">
        <button data-dir="1" aria-label="nudge up">+</button>
      </div>`;
    const inp=d.querySelector('input');
    inp.oninput=()=>{ pl[ax.key]=+inp.value; afterPlace(ax,d); };
    d.querySelectorAll('button').forEach(btn=>btn.onclick=()=>{
      const nv=Math.min(ax.max,Math.max(ax.min, pl[ax.key]+(+btn.dataset.dir)*ui.nudgeStep*(ax.unit==='°'?10:1)));
      pl[ax.key]=Math.round(nv/ax.step)*ax.step;
      inp.value=pl[ax.key]; afterPlace(ax,d);
    });
    host.appendChild(d);
  });
}
function afterPlace(ax,d){
  const pl=placeVal();
  d.querySelector('.pd-lbl b').textContent=fmtAx(ax,pl[ax.key]);
  viewer&&viewer.updatePlacement(ui.selPart.id, pl);
  updatePlaceReadout(); persistQuiet();
}
function fmtAx(ax,v){ return ax.unit==='°'? v.toFixed(1)+'°' : ax.unit==='×'? v.toFixed(2)+'×' : (+v).toFixed(3)+'m'; }
function updatePlaceReadout(){
  const p=ui.selPart; if(!p) return;
  const pl=placeVal();
  $('#pd-readout').textContent=
    `pos  [${pl.px.toFixed(3)}, ${pl.py.toFixed(3)}, ${pl.pz.toFixed(3)}] m\n`+
    `rot  [${pl.rx.toFixed(1)}°, ${pl.ry.toFixed(1)}°, ${pl.rz.toFixed(1)}°]\n`+
    `scale ${pl.s.toFixed(2)}× · step ${ui.nudgeStep}`;
}
$('#pd-snap').onclick=()=>{ const p=ui.selPart; if(!p) return;
  attire().placements[p.id]=defaultPlacement(p); buildPlaceAxes(); updatePlaceReadout(); syncParts3D(); toast('Snapped to socket ✓'); };
$('#pd-reset').onclick=()=>{ const p=ui.selPart; if(!p) return;
  attire().placements[p.id]={px:0,py:0,pz:0,rx:0,ry:0,rz:0,s:1}; buildPlaceAxes(); updatePlaceReadout(); syncParts3D(); };

/* ================= JIGGLE ================= */
function jiggleVal(area, param){
  const fam = (JIGGLE.families[F.jiggle.family]||JIGGLE.families.female).defaults[area]||{};
  const over = ((F.jiggle.areas[area]||{})[param]);
  if(over!==undefined) return over;
  const co = (((JIGGLE.character_overrides||{})[F.profile.name.toLowerCase()]||{}).overrides||{})[area]||{};
  if(co[param]!==undefined) return co[param];
  return fam[param]!==undefined?fam[param]:JIGGLE.parameters[param].default;
}
function renderJiggle(el){
  $('#panel-sub').textContent='Per-area jiggle scales — WWE/Tekken fat-mass model';
  el.innerHTML=`
    <div class="note">Jiggle is driven by <b>fat mass per area</b> — even muscular masses jiggle.
      Amplitude/frequency/damping/stiffness per area. Schema: <span class="chip">data/jiggle-schema.json</span>
      (real spring-bone parameters land with the jiggle physics lane).</div>
    <div class="sect">PROFILE FAMILY</div><div class="roster-grid" id="jfam"></div>
    <div id="jareas"></div>`;
  const fh=el.querySelector('#jfam');
  JIGGLE_FAMILIES.forEach(f=>{
    const b=document.createElement('button');
    b.className='roster-card'+(F.jiggle.family===f.key?' active':'');
    b.innerHTML=`${f.label}<div style="font-size:11px;color:var(--dim);font-weight:400">${f.note||''}</div>`;
    b.onclick=()=>{ F.jiggle.family=f.key; renderAll(); };
    fh.appendChild(b);
  });
  const host=el.querySelector('#jareas');
  JIGGLE_AREAS.forEach(a=>{
    const w=document.createElement('div'); w.innerHTML=`<div class="sect">${a.label.toUpperCase()}</div>`;
    JIGGLE_PARAMS.forEach(pr=>{
      const spec=JIGGLE.parameters[pr.key];
      const v=jiggleVal(a.key, pr.key);
      const d=document.createElement('div'); d.className='ctl'; d.id=`jg-${a.key}-${pr.key}`;
      d.innerHTML=`<label>${pr.label}<span class="val">${v.toFixed(2)}</span></label>
        <input type="range" min="${spec.min}" max="${spec.max}" step="${spec.step}" value="${v}" aria-label="${a.label} ${pr.label}"
          title="${esc(spec.note)}">`;
      d.querySelector('input').oninput=e=>{
        const nv=+e.target.value;
        F.jiggle.areas[a.key]=F.jiggle.areas[a.key]||{};
        F.jiggle.areas[a.key][pr.key]=nv;
        d.querySelector('.val').textContent=nv.toFixed(2); persistQuiet();
      };
      w.appendChild(d);
    });
    host.appendChild(w);
  });
}

/* ================= WARDROBE / PROFILE / MOVESET ================= */
function renderWardrobe(el){
  $('#panel-sub').textContent='DOA loadouts — 10 quick slots per fighter';
  el.innerHTML=`<div class="sect">WARDROBE SLOTS</div><div class="ward-grid" id="wards"></div>
    <div class="btn-row"><button class="btn btn-gold" id="w-save">SAVE CURRENT LOOK → SLOT ${ui.wardSel+1}</button>
    <button class="btn btn-red" id="w-clear">CLEAR SLOT ${ui.wardSel+1}</button></div>
    <div class="sect">TITLE — two phrases (DOA6)</div>
    <div class="field"><label>PHRASE 1</label><select id="t1">${TITLE_A.map(t=>`<option ${F.profile.title[0]===t?'selected':''}>${t}</option>`).join('')}</select></div>
    <div class="field"><label>PHRASE 2</label><select id="t2">${TITLE_B.map(t=>`<option ${F.profile.title[1]===t?'selected':''}>${t}</option>`).join('')}</select></div>`;
  const wg=el.querySelector('#wards');
  F.wardrobe.forEach((w,i)=>{ const b=document.createElement('button');
    b.className='ward-slot'+(w?' filled':''); b.innerHTML=`<span class="ws-thumb"></span><span>${i+1}</span>`;
    b.style.outline=i===ui.wardSel?'2px solid var(--gold)':'';
    b.onclick=()=>{ ui.wardSel=i;
      if(w){ F.attires[F.attireIndex]=JSON.parse(JSON.stringify(w.attire)); F.profile.title=w.title.slice(); renderAll(); toast(`Wardrobe ${i+1} loaded ✓`); }
      else renderPanel(); };
    wg.appendChild(b); });
  el.querySelector('#w-save').onclick=()=>{ F.wardrobe[ui.wardSel]={attire:JSON.parse(JSON.stringify(attire())),title:F.profile.title.slice()}; renderAll(); toast('Saved ✓'); };
  el.querySelector('#w-clear').onclick=()=>{ F.wardrobe[ui.wardSel]=null; renderPanel(); };
  el.querySelector('#t1').onchange=e=>{ F.profile.title[0]=e.target.value; persistQuiet(); };
  el.querySelector('#t2').onchange=e=>{ F.profile.title[1]=e.target.value; persistQuiet(); };
}
function renderProfile(el){
  $('#panel-sub').textContent='No Mercy page 1 + Western Heart canon';
  const pf=F.profile;
  el.innerHTML=`<div class="sect">IDENTITY</div>
    <div class="field"><label>NAME</label><input data-pk="name" type="text" value="${esc(pf.name)}"></div>
    <div class="field"><label>SHORT NAME</label><input data-pk="short_name" type="text" value="${esc(pf.short_name)}"></div>
    <div class="sect">WESTERN HEART CANON</div>
    <div class="field"><label>SOUL</label><select data-pk="soul">${SOULS.map(s=>`<option ${pf.soul===s?'selected':''}>${s}</option>`).join('')}</select></div>
    <div class="note">🔒 Moveset, AI style, parameters shared across all 4 attire slots (No Mercy rule).</div>`;
  el.querySelectorAll('[data-pk]').forEach(i=>i.onchange=()=>{ F.profile[i.dataset.pk]=i.value; renderTopbar(); persistQuiet(); });
}
function renderMoveset(el){
  $('#panel-sub').textContent='Tap slot → scroll library → tap to assign';
  el.innerHTML=`<div class="note">🥊 The moveset editor lives in <span class="chip">moveset-library/</span>
    (WWE 2K slot-first flow + MDickie tap grammar + Tekken inputs — see MOVESET-EDITOR-RESEARCH.md).
    Full 176-slot editor wires into this tab next; the tap-to-assign law already governs every picker in this suite.</div>
    <div class="btn-row"><button class="btn btn-blue" id="ms-open">OPEN MOVESET EDITOR DOC</button></div>`;
  el.querySelector('#ms-open').onclick=()=>modal('MOVESET EDITOR',
    `<p><b>Law (verbatim):</b> TAP a move slot → SCROLL the move library → TAP the move to assign it. NO drag-and-drop anywhere. Phone-first.</p>
     <p>WWE 2K is the editor model (slot-first, positional categories, strict eligibility). Tekken is the fighting (inputs/playstyle). MDickie is the phone reference.</p>
     <p>Research: <span class="chip">moveset-library/MOVESET-EDITOR-RESEARCH.md</span></p>`,
    [{label:'GOT IT',cls:'btn-gold'}]);
}

/* ---------- roster / save / export ---------- */
$('#btn-roster').onclick=()=>{
  modal('FIGHTER SELECT',`<div class="roster-grid">
    ${['NEW FIGHTER','PANTERA','STAR','KEVIN','MARIPOSA','SILVERTONGUE'].map(r=>
    `<button class="roster-card${F.profile.name===r?' active':''}" data-r="${r}">${r}</button>`).join('')}</div>
    <div class="note">Entry flow (verbatim T7): pick fighter → pick attire slot → customize. Roster bodies are canon.</div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  document.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>{ F.profile.name=b.dataset.r; closeModal(); renderAll(); });
};
$('#btn-save').onclick=persist;
$('#btn-export').onclick=()=>{
  const blob=new Blob([JSON.stringify(F,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='creation-suite-fighter.json'; a.click(); URL.revokeObjectURL(a.href); toast('Exported ✓');
};

/* ---------- boot ---------- */
async function boot(){
  try{ const s=localStorage.getItem(LS_KEY); if(s) F=Object.assign(blankFighter(), JSON.parse(s)); }catch(e){}
  try{
    const [parts, jig] = await Promise.all([
      fetch('data/parts-catalog.json').then(r=>r.json()),
      fetch('data/jiggle-schema.json').then(r=>r.json()),
    ]);
    PARTS=parts; JIGGLE=jig;
  }catch(e){
    $('#loader').innerHTML='<div>DATA LOAD FAILED — serve over http</div>'; return;
  }
  viewer=new SuiteViewer($('#stage3d'));
  window.__suite={ viewer, get F(){return F;}, ui, setTab };
  viewer.onReady=()=>{ renderAll(); };
  try{ await viewer.loadBase('../create-fighter/assets/Soldier.glb'); }
  catch(e){ console.warn('base model failed', e); renderAll(); }
  renderAll();
  $('#loader').classList.add('done');
  $('#src-note').textContent='Menus: T7 slots verbatim · WWE 2K CAW flows · No Mercy/WMXIX/DOA — see UI-EXTRACTION-LOG.md';
  if(!localStorage.getItem(LS_KEY)) toast('Tap PARTS → Masks → tap the mask to equip it');
}
boot();
