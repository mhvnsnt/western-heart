/* suite.js — Creation Suite hub logic.
   Laws: tap slot → scroll library → tap to assign. NO drag-and-drop anywhere. Phone-first.
   Menu trees verbatim from teardown games (see menu-data.js + UI-EXTRACTION-LOG.md). */
import { SuiteViewer } from './viewer3d.js';
import { ATTIRE_TREE, BODY_TREE, PARTS_TREE, JIGGLE_AREAS, JIGGLE_PARAMS, JIGGLE_FAMILIES, PLACE_AXES, MENU_SRC, WWE_ATTIRE_TREE } from './menu-data.js';
/* Real morph catalog + DNA/body engine from packages/creation-suite
   (importmap: wh-creation-suite/ -> ../../packages/creation-suite/src/).
   Thin adapter below maps morph ids onto DNA sliders — logic is NOT forked. */
import { BODY_MORPHS, FACE_SHAPE_MORPHS, applyMorphProxies } from 'wh-creation-suite/morphs.js';
import { SLIDERS as DNA_SLIDERS } from 'wh-creation-suite/dna.js';
import { applySliders as applyBodySliders } from 'wh-creation-suite/body.js';
/* The game's own moveset engine (same module the fight runs): notation tables, slots, loadouts. */
import * as MS from '../../../game/js/movesets.js';
MS.setMovesetBase('../../game/assets/movesets/');

const LS_KEY = 'wh_creation_suite_v1';
const START_MONEY = 12400;
const $ = s=>document.querySelector(s);

/* Body types: the 16 male + 9 female CAW body classes of the wrestling teardowns, with GENERIC names (names law,
   AGENTS.md: no real wrestlers or source-game fighters on screen). Saved fighters with the old labels migrate
   through BODY_TYPE_ALIAS. */
const BODY_TYPES = ['Skinny 1','Skinny 2','Medium 1','Medium 2','Thick 1','Thick 2','Fat 1','Fat 2',
  'Brawler','Showman','Super Heavy','Icon','Hairy 1','Hairy 2','Monarch Frame','Sumo Frame',
  'Skinny F','Medium F','Thick F','Fat F','Athletic F','Curvy F','Petite F','Tall F','Dancer F'];
const BODY_TYPE_ALIAS = { Austin:'Brawler', HBK:'Showman', Rikishi:'Super Heavy', Rock:'Icon',
  'King Frame':'Monarch Frame', 'Ganryu Frame':'Sumo Frame', Chyna:'Athletic F', 'Fit 2':'Athletic F', 'Petit 1':'Petite F' };
/* CREATE starts from a WWE-style base body (customization/templates/body-templates.json: Heavyweight /
   Cruiserweight / Women's divisions), never the stock "Soldier" model (owner 2026-11-01). */
const LEGACY_SOLDIER_GLB = 'customization/create-fighter/assets/Soldier.glb';
const DEFAULT_TEMPLATE_ID = 'technician';
const templateGlb = id => `customization/templates/meshes/${id}.glb`;
let TEMPLATES = [];   // customization/templates/body-templates.json templates[]
const SKIN_TONES = ['#f1c9a5','#e8b48a','#dba06e','#c98d5e','#a06a42','#7c4a2d','#5a3420','#3f2417'];
const PROPS = [['height','Height',0.85,1.15],['weight','Weight',0.85,1.3],['muscle','Muscle',0.85,1.3],
  ['shoulder','Shoulders',0.85,1.25],['chest','Chest',0.85,1.3],['waist','Waist',0.85,1.25],
  ['hips','Hips',0.85,1.3],['arms','Arms',0.85,1.3],['legs','Legs',0.85,1.3]];
const SOULS=['—','TOU','SHA','YIN','YANG','KAMI','ONI','RYU','TEN'];
const TITLE_A=['RAGING','SILENT','GOLDEN','BROKEN','HOWLING','IRON','CRIMSON','LONE'];
const TITLE_B=['BEAST','PANTHER','KING','GHOST','STORM','WOLF','TIGER','DEMON'];

/* suite_slot -> ATTIRE category slot key (registry suite_slots mapped onto
   the T7 spine per UNIFIED-UI-SPEC §7; build_suite_catalog.py stamps the
   same mapping as t7_slot on every catalog entry) */
const SLOT2CAT = { mask:'3', eye_lenses:'6', cowl:'3', gauntlets:'H', hair:'2',
  decal_logo:'8', eye:'EYES', tights:'11', pants:'11', top:'9', outfit:'9', scarf:'12', face:'8',
  upper_body:'9', lower_body:'11', gloves:'H', shoes:'F', gear:'12', accessory:'12', attire:'10',
  eyebrows:'6', fullbody:'11' };
/* suite_slot -> fallback 3D socket for texture-part markers (registry has no placement block for texture parts) */
const SLOT2SOCKET = { eye:'face', face:'face', decal_logo:'chest', top:'chest', outfit:'chest',
  scarf:'chest', tights:'waist', pants:'waist', hair:'head', mask:'face', eye_lenses:'face', cowl:'head', gauntlets:'hands' };
const partSocket = p => p.socket || SLOT2SOCKET[p.suite_slot] || 'chest';

function blankAttire(){ return { name:'', thumb:'', equipped:{}, owned:[], colors:{}, placements:{} }; }
function blankFighter(){
  return { version:1, app:'wh-creation-suite',
    profile:{ name:'NEW FIGHTER', short_name:'NEWF', soul:'—', title:['',''] },
    body:{ body_type:'Medium 1', skin_tone:'#c98d5e',
      proportions:{ height:1, weight:1, muscle:1, shoulder:1, chest:1, waist:1, hips:1, arms:1, legs:1 } },
    morphs:{},
    jiggle:{ family:'female', areas:{} },
    attireIndex:0, attires:[blankAttire(),blankAttire(),blankAttire(),blankAttire()],
    wardrobe:[null,null,null,null,null,null,null,null,null,null],
    wallet:START_MONEY,
    /* Roster mode (UNIFIED-UI-SPEC §2): mode 'blank' keeps the legacy
       blank-fighter state in the top-level fields above (the legacy key
       wh_creation_suite_v1 keeps working for game/js/custom-fighter.js);
       per-attire records live in records[], keyed 'fighter::attire_id'
       ('blank' for the blank fighter). */
    mode:'blank', rosterRef:null, records:{},
    template:DEFAULT_TEMPLATE_ID, baseGlb:templateGlb(DEFAULT_TEMPLATE_ID) };
}
let F = blankFighter();
let PARTS = [];       // parts-catalog.json parts[] (unified catalog v2)
let PARTS_META = null; // parts-catalog.json header (counts/sources)
let ROSTER = null;    // data/roster-attires.json (build_roster_attires.py)
let JIGGLE = null;    // jiggle-schema.json
let FPARTS = null;    // data/fighter-parts.json (Phase 1: SmutBase-6 own-mesh parts)
let viewer = null;
let ui = { tab:'body', attireMode:'tekken', attireCat:null, partsCat:null, selPart:null, wardSel:0, nudgeStep:0.001, page:0, query:'' };

const attire = ()=>F.attires[F.attireIndex];

/* ---------- roster mode (UNIFIED-UI-SPEC §2 entry flow) ----------
   pick fighter -> pick attire -> hub, loading THAT attire's real GLB.
   Working state stays in the top-level F fields; switching stashes the
   current state into F.records[key] and restores the target's record. */
const BLANK_GLB = templateGlb(DEFAULT_TEMPLATE_ID);
const currentKey = ()=> F.mode==='roster' && F.rosterRef ? `${F.rosterRef.fighter}::${F.rosterRef.attire}` : 'blank';
function snapshotWorking(){
  return JSON.parse(JSON.stringify({
    profile:F.profile, body:F.body, morphs:F.morphs||{}, jiggle:F.jiggle,
    attireIndex:F.attireIndex, attires:F.attires, wardrobe:F.wardrobe,
    wallet:F.wallet, baseGlb:F.baseGlb }));
}
function applySnapshot(s){
  F.profile=s.profile; F.body=s.body; F.morphs=s.morphs||{}; F.jiggle=s.jiggle;
  F.attireIndex=s.attireIndex||0; F.attires=s.attires; F.wardrobe=s.wardrobe;
  F.wallet=s.wallet; F.baseGlb=s.baseGlb||BLANK_GLB;
}
function stashCurrent(){ F.records = F.records||{}; F.records[currentKey()] = snapshotWorking(); }
function rosterFighter(slug){ return ROSTER && ROSTER.fighters.find(f=>f.fighter===slug); }
/* WH display name (build_roster_attires.py display_name); never the source-model folder name */
function rosterName(f){ return (f && (f.display_name || (f.unassigned ? 'UNASSIGNED BODY' : f.fighter_name))) || ''; }
function rosterAttire(slug, attireId){
  const f = rosterFighter(slug); if(!f) return null;
  return f.attires.find(a=>a.attire_id===attireId) || null;
}
async function loadBaseModel(){
  if(!viewer) return;
  const url = '../../'+F.baseGlb;
  try{ await viewer.loadBase(url); }
  catch(e){ console.warn('[WH] base model failed', F.baseGlb, e); toast('Model failed to load: '+F.baseGlb); }
  renderAll();
}
/* Select a roster fighter+attire: stash current, restore (or seed) its
   record, then load its real GLB in the viewer. Blank mode: fighter=null. */
async function selectRosterAttire(fighter, attireId){
  stashCurrent();
  if(!fighter){
    F.mode='blank'; F.rosterRef=null;
    if(F.records.blank) applySnapshot(F.records.blank);
    else { const keep=F.records; Object.assign(F, blankFighter()); F.records=keep; }
  } else {
    const rf = rosterFighter(fighter), ra = rosterAttire(fighter, attireId);
    if(!rf || !ra){ toast('Attire not found in roster data'); return; }
    F.mode='roster'; F.rosterRef={ fighter, attire:attireId };
    const key = currentKey();
    if(F.records[key]) applySnapshot(F.records[key]);
    else {
      const keep=F.records;
      Object.assign(F, blankFighter()); F.records=keep;
      F.mode='roster'; F.rosterRef={ fighter, attire:attireId };
      F.profile.name = rosterName(rf).toUpperCase();
      F.profile.short_name = rosterName(rf).replace(/[^A-Z0-9]/gi,'').slice(0,4).toUpperCase();
      F.attires = rf.attires.map(a=>{ const b=blankAttire(); b.name=a.attire_name; return b; });
      F.attireIndex = Math.max(0, rf.attires.findIndex(a=>a.attire_id===attireId));
      F.baseGlb = ra.glb;
    }
    // attire tab switches within this fighter re-point baseGlb at that attire
    F.baseGlb = ra.glb;
  }
  ui.selPart=null; hidePlaceDock();
  persistQuiet();
  await loadBaseModel();
  // Item 4: if this attire has an in-repo customization.json and no local
  // record existed for it, fetch + restore it (per-attire save format).
  if(fighter && !F.records[currentKey()]){
    const ra2 = rosterAttire(fighter, attireId);
    if(ra2 && ra2.customization_json){
      try{
        const r = await fetch('../../'+ra2.customization_json);
        if(r.ok){ const rec = await r.json();
          if(rec && rec.app==='wh-creation-suite'){ applyCustomizationRecord(rec); stashCurrent(); persistQuiet(); renderAll(); toast('Restored customization.json ✓'); } }
      }catch(e){ console.warn('[WH] customization.json fetch failed', e); }
    }
  }
}

/* ---------- per-attire customization record (customization.json v1) ---------- */
function customizationRecord(){
  const a = attire();
  const parts={}, textures=[];
  for(const [slotKey, partId] of Object.entries(a.equipped)){
    const p = PARTS.find(x=>x.id===partId); if(!p) continue;
    const key = p.suite_slot || slotKey;
    if(p.part_class==='mesh_part' && p.glb){
      parts[key] = { part_id:p.id, glb:p.glb,
        placement: a.placements[p.id] || (p.placement? { px:(p.placement.offset||[0,0,0])[0], py:(p.placement.offset||[0,0,0])[1], pz:(p.placement.offset||[0,0,0])[2], rx:(p.placement.rotation||[0,0,0])[0], ry:(p.placement.rotation||[0,0,0])[1], rz:(p.placement.rotation||[0,0,0])[2], s:p.placement.scale||1 } : null) };
    } else {
      textures.push({ part_id:p.id, kind:p.kind||p.suite_slot, image:p.asset||p.glb,
        material:(p.placement&&p.placement.material)||null,
        rect:(p.placement&&p.placement.pixel_rect)||null });
      if(p.part_class==='mesh_part') parts[key] = { part_id:p.id, glb:null, placement:null, geometry_pending:true };
    }
  }
  const morphs={}; for(const [k,v] of Object.entries(F.morphs||{})) if(v) morphs[k]=v;
  // Phase 1: per-part toggles on the fighter's own meshes (OUTFIT tab)
  const part_states={};
  for(const [pid, st] of Object.entries(a.partStates||{})){
    if(!st) continue;
    if((st.mode&&st.mode!=='shown')||st.color||st.swap)
      part_states[pid]={ mesh:st.mesh||null, label:st.label||pid, category:st.category||null,
        mode:st.mode||'shown', color:st.color||null, swap:st.swap||null };
  }
  return { version:1, app:'wh-creation-suite',
    fighter: F.mode==='roster' ? F.rosterRef.fighter : 'blank',
    attire: F.mode==='roster' ? F.rosterRef.attire : `attire${F.attireIndex+1}`,
    base_glb: F.baseGlb, out_glb: null,
    body:{ body_type:F.body.body_type, skin_tone:F.body.skin_tone },
    morphs, parts, textures, part_states,
    colors:{ hair:(a.colors&&a.colors.hair)||null, skin:F.body.skin_tone } };
}
function applyCustomizationRecord(rec){
  if(rec.body){ if(rec.body.body_type) F.body.body_type=rec.body.body_type;
    if(rec.body.skin_tone) F.body.skin_tone=rec.body.skin_tone; }
  F.morphs = rec.morphs||{};
  const a = attire();
  a.equipped={}; a.placements={};
  for(const [slot, entry] of Object.entries(rec.parts||{})){
    if(!entry || !entry.part_id) continue;
    a.equipped[slot]=entry.part_id;
    if(entry.placement) a.placements[entry.part_id]=entry.placement;
    if(!a.owned.includes(entry.part_id)) a.owned.push(entry.part_id);
  }
  for(const t of (rec.textures||[])){
    if(!t || !t.part_id) continue;
    const p = PARTS.find(x=>x.id===t.part_id);
    a.equipped[(p&&p.suite_slot)||'face']=t.part_id;
  }
  if(rec.colors && rec.colors.hair){ a.colors=a.colors||{}; a.colors.hair=rec.colors.hair; }
  // Phase 1: per-part toggles on the fighter's own meshes (OUTFIT tab)
  a.partStates = rec.part_states ? JSON.parse(JSON.stringify(rec.part_states)) : {};
}
function saveToAttire(){
  stashCurrent(); persistQuiet();
  const rec = customizationRecord();
  const json = JSON.stringify(rec, null, 2);
  const blob = new Blob([json], {type:'application/json'});
  const aEl = document.createElement('a'); aEl.href=URL.createObjectURL(blob);
  aEl.download='customization.json'; aEl.click(); URL.revokeObjectURL(aEl.href);
  modal('SAVE TO ATTIRE — customization.json',
    `<p>Record for <b>${esc(rec.fighter)} / ${esc(rec.attire)}</b> (base: <span class="chip">${esc(rec.base_glb||'')}</span>) was persisted locally and downloaded as <b>customization.json</b>.</p>
     <p class="note">Same flow as dome-params.json: drop the downloaded file into the attire folder in the repo
     (<span class="chip">${F.mode==='roster' ? esc((rosterAttire(F.rosterRef.fighter, F.rosterRef.attire)||{}).dir||'') : 'blank fighter — no repo folder'}</span>)
     and commit it — the next time this attire is selected here, the suite fetches that file and restores it automatically.</p>
     <textarea id="cust-json-copy" readonly rows="12" style="width:100%;background:#0a0d15;color:var(--txt);border:1px solid var(--line);border-radius:8px;font-family:ui-monospace,monospace;font-size:11px">${esc(json)}</textarea>`,
    [{label:'DONE', cls:'btn-gold'}]);
  const t=document.querySelector('#cust-json-copy'); if(t){ t.focus(); t.select(); }
  toast('Saved to attire ✓');
}
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

/* ---------- morphs adapter (packages dna.js/body.js live preview) ----------
   morphs.js ids -> DNA slider keys (weighted). DNA sliders drive body.js
   procedural morph targets + bone scales on the loaded roster model.
   Face morphs have no DNA region: they are stored in the record and also
   passed to morphs.js applyMorphProxies (bone-name proxies where the rig
   supports them); the baked MPFB shape keys remain the ground truth. */
const MORPH2DNA = {
  height:[['height',1]], bulk:[['weight',0.6],['muscle',0.4]], muscle:[['muscle',1]],
  fat:[['weight',1]], belly:[['belly',1]], chest:[['chest',1]], waist:[['belly',0.5]],
  hips:[['hips',1]], shoulders:[['shoulders',1]], limbs:[['armLen',0.5],['legLen',0.5]],
  neck:[['neck',1]], hands:[], feet:[],
};
const FRAME_IDS = ['height','shoulders','limbs','neck','hands','feet'];
function morphsToDnaSliders(morphs){
  const out={};
  for(const [id,v] of Object.entries(morphs||{})){
    if(!v) continue;
    for(const [key,w] of (MORPH2DNA[id]||[])){
      const s=DNA_SLIDERS[key]; if(!s) continue;
      out[key]=Math.min(s.range[1], Math.max(s.range[0], (out[key]||0)+v*w));
    }
  }
  return out;
}
function syncMorphs(){
  if(!viewer || !viewer.model) return;
  const sliders = morphsToDnaSliders(F.morphs);
  try{ if(Object.keys(sliders).length || viewer.model.userData._csPrepared) { applyBodySliders(viewer.model, sliders); viewer.model.userData._csPrepared=true; } }catch(e){ console.warn('[WH] body sliders failed', e); }
  try{ applyMorphProxies(viewer.model, F.morphs||{}); }catch(e){}
}

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
  for(const pid of [...viewer.parts.keys()])
    if(!seen.has(pid) && !pid.startsWith('swap:')) viewer.detachPart(pid); // swap: keys are owned by applyPartStates3D
}
function syncPreview(){
  if(!viewer) return;
  viewer.setProportions(F.body.proportions);
  if(F.mode==='blank') viewer.setSkinTone(F.body.skin_tone);
  syncMorphs();
  syncParts3D();
  // texture parts: live swap first (packages parts.js semantics — match the
  // registry placement's material/texture on the loaded model); when no
  // material matches this model, fall back to the socket marker (honest:
  // the part applies at that socket, it is not preview-swappable here).
  const texSeen = new Set();
  for(const [slotKey, partId] of Object.entries(attire().equipped)){
    const p = PARTS.find(x=>x.id===partId);
    if(p && p.part_class!=='mesh_part'){
      texSeen.add('tex-'+p.id);
      const asset = p.asset||p.glb;
      if(viewer.model && p.placement && p.placement.material && asset && /\.(png|jpe?g)$/i.test(asset)){
        if(!viewer.texSwaps || !viewer.texSwaps.has(p.id))
          viewer.swapTexturePreview(p.id, '../../'+asset, p.placement).then(ok=>{
            if(!ok) viewer.setMarker('tex-'+p.id, partSocket(p), '#e8b64c', p.name); });
      } else {
        viewer.setMarker('tex-'+p.id, partSocket(p), '#e8b64c', p.name);
      }
    }
  }
  for(const key of [...viewer.markers.keys()]) if(!texSeen.has(key)) viewer.clearMarker(key);
  if(viewer.texSwaps) for(const id of [...viewer.texSwaps.keys()])
    if(!Object.values(attire().equipped).includes(id)) viewer.restoreTexture(id);
  applyPartStates3D();
}

/* ================= OUTFIT — the fighter's own parts (Phase 1) =================
   Per-part toggles for the SmutBase-6 fighters' own modeled meshes
   (data/fighter-parts.json, built from each roster dir's PARTS.md — every
   mesh name verified against the fighter's model.glb):
     show/hide · invisible (hidden but the slot stays occupied, for layering)
     · recolor (per-part color override) · delete (removed from this attire's
     config) · swap (compatible unified-catalog part replaces it).
   State is per attire: attire().partStates[partId] = {mesh,label,category,
   mode,color,swap}. Saved per attire via customizationRecord().part_states
   (customization.json v1) and applied in-fight by
   game/js/customization-consumer.js. */
const fpartsForCurrent = () =>
  (F.mode==='roster' && F.rosterRef && FPARTS && FPARTS.fighters[F.rosterRef.fighter]) || null;
const fpartDef = pid => { const fp=fpartsForCurrent(); return fp && fp.parts.find(p=>p.id===pid); };
const fpartState = pid => (attire().partStates||{})[pid] || { mode:'shown', color:null, swap:null };
function setFpartState(pid, patch){
  const a = attire(); a.partStates = a.partStates || {};
  const def = fpartDef(pid) || {};
  const cur = a.partStates[pid] || { mesh:def.mesh, label:def.label, category:def.category, mode:'shown', color:null, swap:null };
  if(def.mesh && !cur.mesh){ cur.mesh=def.mesh; cur.label=def.label; cur.category=def.category; }
  a.partStates[pid] = Object.assign(cur, patch);
  applyPartStates3D(); persistQuiet();
}
const OUTFIT_SWAP_SOCKET = { hair:'hair', headwear:'head', face:'face', tops:'torso', bottoms:'legs',
  fullbody:'torso', underwear:'legs', hosiery:'legs', gloves:'hands', footwear:'feet', accessories:'accessory' };
function swapCandidates(fp){
  const slots = (FPARTS.swap_slots||{})[fp.category] || [];
  return PARTS.filter(p=>p.part_class==='mesh_part' && p.glb && slots.includes(p.suite_slot));
}
function applyPartStates3D(){
  if(!viewer || !viewer.ready) return;
  const fp = fpartsForCurrent();
  const states = (fp && attire().partStates) || {};
  const seenSwap = new Set();
  for(const part of (fp?fp.parts:[])){
    const st = states[part.id];
    if(!st){ viewer.setBaseMeshMode(part.mesh,'shown'); viewer.setBaseMeshColor(part.mesh,null); continue; }
    viewer.setBaseMeshMode(part.mesh, st.mode||'shown');
    viewer.setBaseMeshColor(part.mesh, st.color||null);
    if(st.swap && st.swap.glb && (st.mode||'shown')==='shown'){
      const key='swap:'+part.id; seenSwap.add(key);
      if(!viewer.parts.has(key))
        viewer.attachPart(key, '../../'+st.swap.glb, { socket: st.swap.socket || OUTFIT_SWAP_SOCKET[part.category] || 'accessory' },
          st.swap.placement||{px:0,py:0,pz:0,rx:0,ry:0,rz:0,s:1}).catch(()=>{});
    }
  }
  for(const k of [...viewer.parts.keys()])
    if(k.startsWith('swap:') && !seenSwap.has(k)) viewer.detachPart(k);
}
function renderOutfit(el){
  const fp = fpartsForCurrent();
  if(!fp){
    $('#panel-sub').textContent='Fighter parts — own-mesh toggles';
    el.innerHTML=`<div class="note">🧥 <b>OUTFIT</b> lists the fighter's <b>own modeled meshes</b>
      (labeled per <span class="chip">roster/*/PARTS.md</span>) with per-part toggles:
      👁 show/hide · 👻 invisible (slot stays occupied, for layering) · 🎨 recolor ·
      🗑 delete from this attire · 🔀 swap with a compatible catalog part.<br><br>
      ${F.mode!=='roster'
        ? 'Pick a roster fighter first: <b>🧍 FIGHTER SELECT</b> below, then choose one of the SmutBase 6 — <b>Ryusan, Tobi, Chatur, Pond, Megami, Menajerii</b>.'
        : `No parts inventory for <b>${esc(F.rosterRef.fighter)}</b> yet — Phase 1 covers the SmutBase 6; the full roster lands in Phase 5.`}
      <br><br>Toggles apply live to the 3D preview and save into this attire's record (PROFILE → SAVE TO ATTIRE).</div>`;
    return;
  }
  const fname = fp.fighter_name || (F.rosterRef&&F.rosterRef.fighter) || '';
  $('#panel-sub').textContent=`${fname} — ${fp.parts.length} labeled parts · toggles save per attire`;
  const cats = (FPARTS.categories||[]).filter(c=>fp.parts.some(p=>p.category===c.key));
  el.innerHTML = `<div class="note">🧥 Every mesh <b>${esc(fname)}</b> shipped with, labeled per
      <span class="chip">PARTS.md</span>. Tap a toggle — the 3D preview updates live.
      States save per attire (PROFILE → <b>SAVE TO ATTIRE</b>) and apply in-fight.</div>` +
    cats.map(c=>`<div class="sect">${c.icon} ${c.label}</div><div id="of-${c.key}"></div>`).join('');
  for(const c of cats){
    const host = el.querySelector('#of-'+c.key);
    fp.parts.filter(p=>p.category===c.key).forEach(p=>host.appendChild(outfitRow(p)));
  }
}
function outfitRow(p){
  const st = fpartState(p.id);
  const d = document.createElement('div');
  d.className='of-row'; d.id='ofrow-'+p.id.replace(/[^a-z0-9]+/gi,'-');
  const modeLabel = {shown:'SHOWN',hidden:'HIDDEN',invisible:'INVISIBLE',deleted:'DELETED'}[st.mode||'shown'];
  d.innerHTML=`
    <div class="of-main">
      <div class="of-name">${esc(p.label)}${p.signature?' <span class="chip" title="canon signature part — delete blocked">⭐ signature</span>':''}${p.base?' <span class="chip">base</span>':''}</div>
      <div class="of-mesh">${esc(p.mesh)}</div>
      <div class="of-state"><span class="chip of-${st.mode||'shown'}">${modeLabel}</span>${st.swap?` <span class="chip">🔀 ${esc(st.swap.name||st.swap.part_id||'')}</span>`:''}${st.color?` <span class="chip">🎨 <i style="display:inline-block;width:10px;height:10px;background:${st.color};border-radius:2px"></i></span>`:''}</div>
      ${p.notes?`<div class="of-notes">${esc(p.notes)}</div>`:''}
    </div>
    <div class="of-ctl"></div>`;
  const ctl = d.querySelector('.of-ctl');
  if(p.base){
    ctl.innerHTML=`<div class="note" style="margin:0">🔒 base mesh — never removed</div>`;
    return d;
  }
  const bVis=document.createElement('button'); bVis.className='btn btn-sm';
  bVis.textContent=(st.mode==='hidden'||st.mode==='invisible')?'👁 SHOW':'👁 HIDE';
  bVis.onclick=()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:(cur==='hidden'||cur==='invisible')?'shown':'hidden'}); renderPanel(); };
  const bInv=document.createElement('button'); bInv.className='btn btn-sm'; bInv.textContent='👻 INVISIBLE';
  bInv.title='Hidden, but the slot stays occupied (layering)';
  bInv.onclick=()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:cur==='invisible'?'shown':'invisible'}); renderPanel(); };
  const bCol=document.createElement('label'); bCol.className='btn btn-sm'; bCol.textContent='🎨';
  bCol.title='Recolor this part'; bCol.style.position='relative'; bCol.style.overflow='hidden';
  const inp=document.createElement('input'); inp.type='color'; inp.value=st.color||'#ffffff'; inp.setAttribute('aria-label','Recolor '+p.label);
  inp.style.cssText='position:absolute;inset:0;opacity:0;width:100%;height:100%;cursor:pointer';
  inp.oninput=()=>{ setFpartState(p.id,{color:inp.value}); };
  inp.onchange=()=>{ renderPanel(); };
  bCol.appendChild(inp);
  const bColX=document.createElement('button'); bColX.className='btn btn-sm'; bColX.textContent='🎨✕'; bColX.title='Clear recolor';
  bColX.onclick=()=>{ setFpartState(p.id,{color:null}); renderPanel(); };
  const bDel=document.createElement('button');
  bDel.className='btn btn-sm '+((st.mode==='deleted')?'btn-green':'btn-red');
  const canDelete = p.swappable && !p.signature;
  bDel.textContent = st.mode==='deleted' ? '↩ RESTORE' : '🗑 DELETE';
  bDel.disabled = !canDelete && st.mode!=='deleted';
  bDel.title = p.signature ? 'Signature part — canon: never removed' : (p.swappable?'Remove from this attire':'Not separable — hide/recolor only');
  bDel.onclick=()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:cur==='deleted'?'shown':'deleted'}); renderPanel(); };
  const bSwap=document.createElement('button'); bSwap.className='btn btn-sm btn-blue';
  bSwap.textContent = st.swap ? '🔀 SWAPPED ✓' : '🔀 SWAP';
  bSwap.disabled = !p.swappable;
  bSwap.title = p.swappable ? 'Replace with a compatible catalog part' : 'Not swappable';
  bSwap.onclick=()=>openSwapLibrary(p);
  [bVis,bInv,bCol,bColX,bDel,bSwap].forEach(b=>ctl.appendChild(b));
  return d;
}
function openSwapLibrary(p){
  const cands = swapCandidates(p);
  const st = fpartState(p.id);
  const rows = cands.slice(0,120).map(c=>`
    <button class="ms-row" data-id="${esc(c.id)}">
      <span class="ms-in">${esc(c.suite_slot||'')}</span>
      <span class="ms-name">${esc(c.name)}</span>
      <span class="ms-tag">${esc(c.source||'')}</span>
    </button>`).join('');
  modal(`SWAP — ${p.label}`,
    `<div class="note">Replace <b>${esc(p.label)}</b> (<span class="chip">${esc(p.mesh)}</span>) with a compatible catalog part.
     The original mesh hides; the swap saves into this attire.</div>
     ${st.swap?`<div class="btn-row"><button class="btn btn-red" id="swap-clear">REMOVE SWAP — restore ${esc(p.label)}</button></div>`:''}
     <div class="note">${cands.length} compatible parts${cands.length>120?' (first 120 — use the PARTS tab search to narrow)':''}.</div>
     <div class="ms-lib">${rows||'<div class="note">No compatible catalog parts with meshes yet.</div>'}</div>`,
    [{label:'CLOSE'}]);
  const mb=$('#modal-body');
  mb.querySelectorAll('.ms-row').forEach(b=>b.onclick=()=>{
    const c=PARTS.find(x=>x.id===b.dataset.id); if(!c) return;
    setFpartState(p.id,{mode:'shown', swap:{part_id:c.id, name:c.name, glb:c.glb, socket:partSocket(c), placement:defaultPlacement(c)}});
    closeModal(); renderPanel(); toast('Swapped ✓');
  });
  const clr=mb.querySelector('#swap-clear');
  if(clr) clr.onclick=()=>{ setFpartState(p.id,{swap:null}); closeModal(); renderPanel(); toast('Swap removed ✓'); };
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
    b.onclick=()=>{ if(F.mode==='roster' && F.rosterRef){
        const rf=rosterFighter(F.rosterRef.fighter);
        if(rf && rf.attires[i]){ selectRosterAttire(F.rosterRef.fighter, rf.attires[i].attire_id); return; } }
      F.attireIndex=i; ui.selPart=null; renderAll(); };
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
  ({body:renderBody,attire:renderAttire,parts:renderParts,outfit:renderOutfit,jiggle:renderJiggle,
    wardrobe:renderWardrobe,profile:renderProfile,moveset:renderMoveset,dome:renderDome})[ui.tab](body);
}

/* ================= BODY ================= */
function renderBody(el){
  $('#panel-sub').textContent='Base body, build, skin and face';
  const tpl = F.mode==='blank' ? templateById(F.template) : null;
  el.innerHTML=`
    ${F.mode==='blank' ? `<div class="sect">BASE BODY</div>
    <div class="tpl-current"><div><b>${esc(tpl ? tpl.name : 'Custom body')}</b><br><small>${esc(tpl ? `${tpl.division} · ${tpl.gender==='female'?'Women':'Men'}` : '')}</small></div>
      <button class="btn btn-gold btn-sm" id="tpl-change">CHANGE</button></div>` : ''}
    <div class="sect">BODY TYPE</div><div class="roster-grid" id="btypes"></div>
    <div class="sect">SKIN TONE</div><div class="swatches" id="stones"></div>
    <div class="sect">PROPORTIONS</div><div id="psl"></div>
    <div class="sect">FRAME</div><div id="mframe"></div>
    <div class="sect">MASS</div><div id="mmass"></div>
    <div class="sect">FACE SHAPE</div><div id="mface"></div>`;
  const tc = el.querySelector('#tpl-change'); if(tc) tc.onclick=()=>openTemplateSelect();
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
  const addMorph=(host, m)=>{
    const v=(F.morphs && F.morphs[m.id])||0;
    const d=document.createElement('div'); d.className='ctl'; d.id='morph-'+m.id;
    d.innerHTML=`<label>${m.label}<span class="val">${v.toFixed(2)}</span></label>
      <input type="range" min="${m.range[0]}" max="${m.range[1]}" step="0.01" value="${v}" data-morph="${m.id}" aria-label="${m.label}">`;
    const inp=d.querySelector('input');
    inp.oninput=()=>{ F.morphs=F.morphs||{}; F.morphs[m.id]=+inp.value;
      d.querySelector('.val').textContent=(+inp.value).toFixed(2); syncMorphs(); persistQuiet(); };
    host.appendChild(d);
  };
  const hf=el.querySelector('#mframe'), hm=el.querySelector('#mmass'), hface=el.querySelector('#mface');
  BODY_MORPHS.forEach(m=> addMorph(FRAME_IDS.includes(m.id)?hf:hm, m));
  FACE_SHAPE_MORPHS.forEach(m=> addMorph(hface, m));
}

/* ================= ATTIRE (T7 spine) ================= */
function partsForCat(slotKey){
  return PARTS.filter(p=>SLOT2CAT[p.suite_slot]===slotKey);
}
function renderAttire(el){
  if(!ui.attireCat){
    const mode = ui.attireMode||'tekken';
    $('#panel-sub').textContent = mode==='wwe'
      ? 'WWE CAW clothing — region → garment type (2K22)'
      : 'Tekken item shop — pick a category (T7 slots verbatim)';
    el.innerHTML=`<div class="note">Buy → Equip loop · hover try-on · conflict Replace/Cancel · 5 color channels.
      Browse the same catalog two ways — WWE runs the creator's internal hierarchy (owner division 2026-10-22).</div>
      <div class="btn-row" id="attire-mode-row">
        <button class="btn btn-sm ${mode==='tekken'?'btn-gold':''}" id="am-tekken">TEKKEN SLOTS</button>
        <button class="btn btn-sm ${mode==='wwe'?'btn-gold':''}" id="am-wwe">WWE REGIONS</button>
      </div><div id="cats"></div>`;
    el.querySelector('#am-tekken').onclick=()=>{ ui.attireMode='tekken'; renderAll(); };
    el.querySelector('#am-wwe').onclick=()=>{ ui.attireMode='wwe'; renderAll(); };
    const host=el.querySelector('#cats');
    if(mode==='wwe'){ renderWweRegions(host); return; }
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
  const cat = ui.attireCat;
  renderPartGrid(el, cat, cat.wweRegion ? partsForWwe(cat) : partsForCat(cat.slot), 'attireCat');
}

/* ---- WWE region browse: union of the region's T7 slots, deduped.
   Equipping files each part under its NATURAL T7 slot (via cat.slotFor),
   so the Tekken view and WWE view stay consistent. ---- */
function partsForWwe(cat){
  const seen=new Set(); const out=[];
  (cat.slots||[]).forEach(s=>partsForCat(s).forEach(p=>{ if(!seen.has(p.id)){ seen.add(p.id); out.push(p); } }));
  return out;
}
function renderWweRegions(host){
  WWE_ATTIRE_TREE.forEach(r=>{
    const n=partsForWwe(r).length;
    const eqd=(r.slots||[]).some(s=>attire().equipped[s]);
    const b=document.createElement('button');
    b.className='subcat'+(eqd?' equipped':''); b.id='wcat-'+r.key;
    b.innerHTML=`<span class="sc-ico">${r.icon}</span><span>${r.label}${eqd?'<br><small style="color:var(--green)">✓ equipped</small>':''}<br><small style="color:var(--dim)">${r.sub}</small></span><span class="sc-count">${n} parts</span>`;
    b.onclick=()=>{ ui.attireCat={ key:'wwe-'+r.key, label:r.label+' · WWE', wweRegion:true, slots:r.slots,
      slotFor:(p)=>p.t7_slot||SLOT2CAT[p.suite_slot]||r.slots[0] };
      ui.selPart=null; ui.page=0; ui.query=''; renderAll(); };
    host.appendChild(b);
  });
}

/* ================= PARTS (wired libraries) ================= */
const T7_SLOT_LABELS = { '1':'Head','2':'Hairstyle','3':'Full Head','4':'Hair Accessory','5':'Glasses','6':'Face','7':'Facial Hair','8':'Face Paint','9':'Upper Body','10':'Full Body','11':'Lower Body','H':'Hands','F':'Feet','12':'Upper Accessory','13':'Lower Accessory','14':'Extra','15':'Effects','17':'Aura','EYES':'Eyes' };
function renderParts(el){
  if(!ui.partsCat){
    $('#panel-sub').textContent='Unified parts catalog — browse by T7 slot, tap to assign';
    const countsTxt = PARTS_META ? Object.entries(PARTS_META.counts||{}).map(([k,v])=>`${k}: ${v}`).join(' · ') : '';
    el.innerHTML=`<div class="note">ONE unified catalog (${PARTS.length} parts) built by
      <span class="chip">build_suite_catalog.py</span> — ${esc(countsTxt)}.
      Source labels are shown on every part. Tap a T7 slot → scroll → tap part to assign. No drag-and-drop.</div>
      <div class="sect">BROWSE BY T7 SLOT</div><div id="pcats"></div>
      <div class="sect">LIBRARIES</div><div id="plibs"></div>`;
    const host=el.querySelector('#pcats');
    const bySlot={};
    PARTS.forEach(p=>{ const s=p.t7_slot||SLOT2CAT[p.suite_slot]||'?'; (bySlot[s]=bySlot[s]||[]).push(p); });
    Object.keys(bySlot).sort().forEach(s=>{
      const b=document.createElement('button'); b.className='subcat'; b.id='pslot-'+s;
      b.innerHTML=`<span class="sc-ico">🎭</span><span>${esc(T7_SLOT_LABELS[s]||('Slot '+s))}<br><small style="color:var(--dim)">T7 slot ${esc(s)}</small></span><span class="sc-count">${bySlot[s].length} parts</span>`;
      b.onclick=()=>{ ui.partsCat={key:'slot-'+s, slot:s, label:(T7_SLOT_LABELS[s]||('Slot '+s))+' · T7 '+s, list:bySlot[s]}; ui.selPart=null; ui.page=0; ui.query=''; renderAll(); };
      host.appendChild(b);
    });
    const libs=el.querySelector('#plibs');
    PARTS_TREE.forEach(c=>{
      if(c.key==='eyes'){
        // Owner eye verdict (2026-10-20): eyes are REAL PLACEABLE MESH PARTS.
        // Placeable eye/brow parts and legacy texture variants are SEPARATE lists.
        const placeable = PARTS.filter(p=>p.eye_kind==='placeable_part');
        const variants = PARTS.filter(p=>p.eye_kind==='texture_variant');
        [['👁️ PLACEABLE EYE PARTS — mesh, position them yourself', placeable, 'eyes-placeable'],
         ['🎨 EYE TEXTURE VARIANTS — legacy swaps only, NOT the eye solution', variants, 'eyes-textures']].forEach(([label, list, key])=>{
          const b=document.createElement('button'); b.className='subcat'; b.id='pcat-'+key;
          b.innerHTML=`<span class="sc-ico">👁️</span><span>${label}</span><span class="sc-count">${list.length} parts</span>`;
          b.onclick=()=>{ ui.partsCat={key, label, list}; ui.selPart=null; ui.page=0; ui.query=''; renderAll(); };
          libs.appendChild(b);
        });
        return;
      }
      const list = c.key==='decals' ? PARTS.filter(p=>['decal_logo','tights','pants'].includes(p.suite_slot))
        : c.key==='masks' ? PARTS.filter(p=>['mask','eye_lenses','cowl','gauntlets'].includes(p.suite_slot))
        : PARTS.filter(p=>p.suite_slot==='hair');
      const b=document.createElement('button'); b.className='subcat'; b.id='pcat-'+c.key;
      b.innerHTML=`<span class="sc-ico">${c.icon}</span><span>${c.label}<br><small style="color:var(--dim)">${esc(c.note.split('—')[0])}</small></span><span class="sc-count">${list.length} parts</span>`;
      b.onclick=()=>{ ui.partsCat={...c, list}; ui.selPart=null; ui.page=0; ui.query=''; renderAll(); };
      libs.appendChild(b);
    });
    return;
  }
  renderPartGrid(el, ui.partsCat, ui.partsCat.list, 'partsCat');
}

/* ---- shared tap-to-assign grid (search + paging for the 1,149-part catalog) ---- */
const PAGE_SIZE = 60;
function renderPartGrid(el, cat, list, backKey){
  const slotKey = cat.slot || cat.key;
  const q = (ui.query||'').toLowerCase();
  const filtered = q ? list.filter(p=>p.name.toLowerCase().includes(q)||p.id.toLowerCase().includes(q)||(p.library||'').toLowerCase().includes(q)) : list;
  const pages = Math.max(1, Math.ceil(filtered.length/PAGE_SIZE));
  ui.page = Math.min(ui.page||0, pages-1);
  const pageItems = filtered.slice(ui.page*PAGE_SIZE, ui.page*PAGE_SIZE+PAGE_SIZE);
  $('#panel-sub').textContent=`${cat.label} — ${filtered.length} parts · tap to assign (no drag-and-drop)`;
  el.innerHTML=`
    <div class="back-row"><button class="btn back-btn" id="btn-back">← ${backKey==='attireCat'?'CATEGORIES':'SLOTS / LIBRARIES'}</button></div>
    <input class="search" id="part-search" type="search" placeholder="Search parts…" value="${esc(ui.query||'')}" aria-label="Search parts">
    <div class="pager"><button class="btn btn-sm" id="pg-prev" ${ui.page===0?'disabled':''}>← PREV</button>
      <span class="bb-hint">Page ${ui.page+1} / ${pages}</span>
      <button class="btn btn-sm" id="pg-next" ${ui.page>=pages-1?'disabled':''}>NEXT →</button></div>
    <div class="item-grid" id="grid"></div><div id="pdetail"></div>`;
  el.querySelector('#btn-back').onclick=()=>{ ui[backKey]=null; ui.selPart=null; ui.query=''; hidePlaceDock(); renderAll(); };
  const search=el.querySelector('#part-search');
  search.oninput=()=>{ ui.query=search.value; ui.page=0;
    const pos=search.selectionStart; renderPanel();
    const s2=document.querySelector('#part-search'); if(s2){ s2.focus(); s2.setSelectionRange(pos,pos); } };
  el.querySelector('#pg-prev').onclick=()=>{ ui.page--; renderPanel(); };
  el.querySelector('#pg-next').onclick=()=>{ ui.page++; renderPanel(); };
  const grid=el.querySelector('#grid');
  pageItems.forEach(p=>{
    const owned = attire().owned.includes(p.id);
    const eqd = Object.values(attire().equipped).includes(p.id);
    const d=document.createElement('div');
    d.className='item-card'+(ui.selPart&&ui.selPart.id===p.id?' selected':'')+(eqd?' equipped':'');
    d.id='part-'+p.id;
    d.innerHTML=`<div class="item-mono">${p.part_class==='mesh_part'?'🧩':'🎨'}</div>
      <div class="item-name">${esc(p.name)}</div>
      <div class="item-meta">${p.part_class==='mesh_part'?'mesh · '+esc(p.socket||'—'):esc(p.library||'')}<br>
      <span class="chip" style="font-size:9px">${esc(p.source||p.library||'')}</span>
      ${p.eye_kind==='placeable_part'?' <span class="geo-badge" style="background:#12331c;color:#46c46a">PLACEABLE PART</span>':''}
      ${p.eye_kind==='texture_variant'?' <span class="geo-badge">TEXTURE VARIANT (LEGACY)</span>':''}
      ${p.geometry_pending?' <span class="geo-badge">GEOMETRY PENDING</span>':''}<br>
      ${owned?'<span class="owned">OWNED</span>':'<span class="price">500G</span>'}</div>`;
    d.onclick=()=>{ ui.selPart=p; renderPanel(); renderTopbar(); };
    grid.appendChild(d);
  });
  if(ui.selPart && list.includes(ui.selPart)) renderPartDetail(el.querySelector('#pdetail'), ui.selPart,
    (cat.slotFor && ui.selPart) ? cat.slotFor(ui.selPart) : slotKey);
}
function renderPartDetail(el, p, slotKey){
  const owned = attire().owned.includes(p.id);
  const eqd = Object.values(attire().equipped).includes(p.id);
  el.innerHTML=`
    <div class="sect">SELECTED — ${esc(p.name)}</div>
    <div class="kv"><span>Part ID</span><b style="font-size:11px">${esc(p.id)}</b></div>
    <div class="kv"><span>Class</span><b>${esc(p.part_class)}</b></div>
    <div class="kv"><span>Library</span><b>${esc(p.library||'—')}</b></div>
    <div class="kv"><span>Source</span><b style="font-size:11px">${esc(p.source||'—')}</b></div>
    <div class="kv"><span>T7 slot</span><b>${esc(p.t7_slot||SLOT2CAT[p.suite_slot]||'—')} · suite slot ${esc(p.suite_slot||'—')}</b></div>
    ${p.eye_kind==='placeable_part'?'<div class="note">👁️ <b>Real placeable eye part</b> (owner verdict: eyes are parts, not decals). Equip it, then use <b>PLACEMENT</b> to set position / rotation / scale yourself — placement saves into this attire\'s record.</div>':''}
    ${p.eye_kind==='texture_variant'?'<div class="note">🎨 <b>Legacy texture variant</b> — an eye texture swap only. This is NOT the eye solution (owner verdict 2026-10-20: eyes are real placeable parts with eyelashes + eyebrows, placed by hand in this suite).</div>':''}
    ${p.geometry_pending?'<div class="note">⚠️ Geometry pending — this registry part has no converted mesh yet; applying records it on the attire and marks its socket.</div>':''}
    ${p.glb?`<div class="kv"><span>Mesh</span><b style="font-size:11px">${esc(p.glb)}</b></div>
    <div class="kv"><span>Socket</span><b>${esc(p.socket||'—')}</b></div>`:''}
    <div class="btn-row" id="p-actions"></div>`;
  const box=el.querySelector('#p-actions');
  if(p.part_class==='mesh_part' && !p.glb){
    // geometry-pending registry part: record + socket marker, no fake mesh
    if(!eqd){
      const b=document.createElement('button'); b.className='btn btn-green'; b.id='btn-apply-part'; b.textContent='APPLY (GEOMETRY PENDING)';
      b.onclick=()=>{ attire().equipped[slotKey]=p.id; renderAll(); toast('Recorded ✓ — geometry pending'); };
      box.appendChild(b);
    } else {
      const b=document.createElement('button'); b.className='btn btn-red'; b.id='btn-unequip-part'; b.textContent='REMOVE';
      b.onclick=()=>{ for(const k of Object.keys(attire().equipped)) if(attire().equipped[k]===p.id) delete attire().equipped[k]; renderAll(); };
      box.appendChild(b);
    }
  } else if(p.part_class==='mesh_part'){
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
    b.onclick=()=>{ attire().equipped[slotKey]=p.id; renderAll(); toast('Applied ✓'); };
    box.appendChild(b);
    if(eqd){
      const b2=document.createElement('button'); b2.className='btn btn-red'; b2.id='btn-remove-part'; b2.textContent='REMOVE';
      b2.onclick=()=>{ for(const k of Object.keys(attire().equipped)) if(attire().equipped[k]===p.id) delete attire().equipped[k];
        if(viewer){ viewer.restoreTexture(p.id); viewer.clearMarker('tex-'+p.id); }
        renderAll(); };
      box.appendChild(b2);
    }
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
    <div class="note">🔒 Moveset, AI style, parameters shared across all 4 attire slots (No Mercy rule).</div>
    <div class="sect">PER-ATTIRE SAVE — customization.json</div>
    <div class="note">Records are keyed <b>fighter + attire</b> in this suite. <b>Save to Attire</b> persists the record, downloads <span class="chip">customization.json</span> and shows a copyable panel.
      Drop that file into the attire's repo folder and commit it — the same flow as <span class="chip">dome-params.json</span> for Doc Frank's dome — and selecting this attire here restores it automatically.</div>
    <div class="btn-row"><button class="btn btn-blue" id="prof-save-attire">🎽 SAVE TO ATTIRE</button></div>
    <div class="kv"><span>Current record key</span><b id="prof-rec-key"></b></div>`;
  el.querySelectorAll('[data-pk]').forEach(i=>i.onchange=()=>{ F.profile[i.dataset.pk]=i.value; renderTopbar(); persistQuiet(); });
  const rk=el.querySelector('#prof-rec-key'); if(rk) rk.textContent=currentKey();
  const ps=el.querySelector('#prof-save-attire'); if(ps) ps.onclick=saveToAttire;
}
/* ---------- MOVESET EDITOR (WWE 2K slot-first flow over Tekken inputs) ----------
   Every input (notation) of the fighter is a slot. TAP a slot -> the move library opens:
   SAME INPUT (every source's version of that input: T8 / T7 / T3 / history / donors),
   ALL MOVES of this fighter, or any OTHER FIGHTER's moves. TAP a move -> assigned.
   Saved in localStorage wh_moveset_loadout_v1 — the exact table the fight engine reads
   (game/js/movesets.js resolveMove), so the next fight plays it. No drag-and-drop. */
const MS_CATS = [['all','ALL'],['stand','STANDING'],['string','STRINGS'],['crouch','CROUCH / WS'],['stance','STANCES'],
  ['motion','MOTIONS'],['throw','THROWS'],['rage','RAGE / HEAT'],['sig','SIGNATURE'],['edited','EDITED']];
const ROSTER2GAME = { 'kiko-tanaka':'rave', 'jin':'jin_soul', 'doc-frank':'docfrank', 'sam-ur-a1':'samura1', 'saku-ra':'sakura' };
const msUi = { fid:null, cat:'all', q:'', page:0 };
function gameIdFor(rosterId){
  const idx = (MS.getMovesetIndex()||{}).fighters || {};
  for (const c of [ROSTER2GAME[rosterId], rosterId, String(rosterId||'').replace(/-/g,''), String(rosterId||'').replace(/-/g,'_')])
    if (c && idx[c]) return c;
  return null;
}
const WORD_NAME = {0x412:'high',0x217:'mid',0x10f:'low',0x31f:'s.mid',0x607:'unblk',0x706:'unblk',0x800:'throw'};
function msSrc(m){
  if(!m) return '';
  if(m.wh_original || m.move_class==='signature') return 'WH';
  const s=m.merge_source||'';
  if(m.t8_id || s.startsWith('t8')) return 'T8';
  if(m.t7_move_id || s.startsWith('t7')) return 'T7';
  if(s.startsWith('donor')) return 'DONOR';
  if(m.t3_source) return 'T3';
  for(const k of Object.keys(m)) if(/^(sf6|sfv|sf4|doa|ur|vf|nomercy)_/.test(k)) return k.split('_')[0].toUpperCase();
  return 'WH';
}
function msInfo(ms, key, m){
  const w = ms && ms.hit_words ? ms.hit_words[key] : undefined;
  const f = Math.round((m.startup||0)*60);
  return `i${f} · ${WORD_NAME[w]||'—'} · ${Math.round(m.damage||0)} dmg`;
}
function msCat(n, m){
  if(!m) return 'stand';
  if(m.wh_original || m.move_class==='signature') return 'sig';
  if(m.move_class==='throw' || m.isGrab) return 'throw';
  if(/^(R|H)\./.test(n)) return 'rage';
  if(/^(FC|WS)\./.test(n) || /^d\+/.test(n)) return 'crouch';
  if(/^[A-Za-z_][A-Za-z0-9_]*\./.test(n)) return 'stance';
  if(MS.parseMotion(n)) return 'motion';
  if(n.includes(',')) return 'string';
  return 'stand';
}
function msNotations(ms){
  if(ms.slots) return Object.keys(ms.slots);
  return Object.keys(ms.moves).filter(k=>/^[A-Za-z0-9_./+,~:*]+$/.test(k) && !/__|~|_t\d$|_r\d|_c\d/.test(k));
}
function msAlternates(ms, n){
  const out=[];
  for(const [k,m] of Object.entries(ms.moves)){
    const base=k.split(/__|~|_t\d$|_r\d|_c\d/)[0];
    if(k===n || base===n || m.input===n) out.push([k,m]);
  }
  return out;
}
async function renderMoveset(el){
  $('#panel-sub').textContent='Tap an input → tap a move to assign · saved for the fight';
  if(!MS.getMovesetIndex()) { el.innerHTML='<div class="note">Loading move lists…</div>'; await MS.loadFighterMovesets(); }
  const idx=(MS.getMovesetIndex()||{}).fighters||{};
  const ids=Object.keys(idx).sort();
  const custom = F.mode!=='roster';
  if(!msUi.fid) msUi.fid = custom ? 'custom' : (gameIdFor(F.rosterRef && F.rosterRef.fighter) || ids[0]);
  const fid=msUi.fid;
  const lo=MS.getLoadout(fid);
  if(fid==='custom' && !lo.__base){ MS.setLoadoutSlot('custom','__base','demonio'); }
  await MS.ensureMovesets([fid]);
  const ms=MS.playedMoveset(fid);
  const opt=(id,sel)=>`<option value="${id}" ${id===sel?'selected':''}>${esc((idx[id]||{}).display||id)} — ${esc((idx[id]||{}).tekken_base||'')}</option>`;
  el.innerHTML=`<div class="field"><label>FIGHTER</label><select id="ms-fid">${custom?`<option value="custom" ${fid==='custom'?'selected':''}>YOUR CREATED FIGHTER</option>`:''}${ids.map(i=>opt(i,fid)).join('')}</select></div>
    ${fid==='custom'?`<div class="field"><label>BASE MOVESET</label><select id="ms-base">${ids.map(i=>opt(i,MS.getLoadout('custom').__base)).join('')}</select></div>`:''}
    <div class="ms-cats">${MS_CATS.map(([k,l])=>`<button class="chip ms-cat ${msUi.cat===k?'on':''}" data-c="${k}">${l}</button>`).join('')}</div>
    <div class="field"><input id="ms-q" type="search" placeholder="search input or move name" value="${esc(msUi.q)}"></div>
    <div class="note" id="ms-count"></div>
    <div id="ms-list"></div>
    <div class="btn-row"><button class="btn" id="ms-more">MORE</button><button class="btn btn-red" id="ms-reset">RESET ALL EDITS</button></div>`;
  el.querySelector('#ms-fid').onchange=e=>{ msUi.fid=e.target.value; msUi.page=0; renderPanel(); };
  const bs=el.querySelector('#ms-base'); if(bs) bs.onchange=async e=>{ MS.setLoadoutSlot('custom','__base',e.target.value); await MS.ensureMovesets([e.target.value]); renderPanel(); toast('Base moveset set ✓'); };
  el.querySelectorAll('.ms-cat').forEach(b=>b.onclick=()=>{ msUi.cat=b.dataset.c; msUi.page=0; renderPanel(); });
  const q=el.querySelector('#ms-q'); q.oninput=()=>{ msUi.q=q.value; msUi.page=0; drawList(); };
  el.querySelector('#ms-more').onclick=()=>{ msUi.page++; drawList(); };
  el.querySelector('#ms-reset').onclick=()=>modal('RESET ALL EDITS',`<p>Every input of <b>${esc((idx[fid]||{}).display||fid)}</b> goes back to its default move.</p>`,
    [{label:'CANCEL'},{label:'RESET',cls:'btn-red',fn:()=>{ for(const n of Object.keys(MS.getLoadout(fid))) if(n!=='__base') MS.setLoadoutSlot(fid,n,null); renderPanel(); toast('Defaults restored ✓'); }}]);
  function drawList(){
    const list=el.querySelector('#ms-list'); if(!ms){ list.innerHTML='<div class="note">No moveset for this fighter yet.</div>'; return; }
    const lo=MS.getLoadout(fid), ql=msUi.q.toLowerCase();
    const rows=[];
    for(const n of msNotations(ms)){
      const r=MS.resolveMove(fid,n); if(!r) continue;
      const edited = !!lo[n];
      const cat = msCat(n, r.move);
      if(msUi.cat==='edited' ? !edited : (msUi.cat!=='all' && cat!==msUi.cat)) continue;
      if(ql && !n.toLowerCase().includes(ql) && !String(r.move.name||'').toLowerCase().includes(ql)) continue;
      rows.push([n,r,edited]);
    }
    el.querySelector('#ms-count').textContent=`${rows.length} inputs · ${Object.keys(ms.moves).length} moves in ${esc((idx[fid]||{}).display||fid)}'s library`;
    const N=40*(msUi.page+1);
    list.innerHTML=rows.slice(0,N).map(([n,r,ed],i)=>`<button class="ms-row ${ed?'edited':''}" data-n="${esc(n)}">
      <span class="ms-in">${esc(n)}</span><span class="ms-name">${esc(r.move.name||'')}${r.from!==fid?` <i>(${esc(r.from)})</i>`:''}</span>
      <span class="ms-tag">${msSrc(r.move)}</span><span class="ms-fd">${msInfo(r.ms,r.key,r.move)}</span></button>`).join('');
    el.querySelector('#ms-more').hidden = rows.length<=N;
    list.querySelectorAll('.ms-row').forEach(b=>b.onclick=()=>openMoveLibrary(fid, b.dataset.n));
  }
  drawList();
}
async function openMoveLibrary(fid, n, tab='same', other=null, q=''){
  const ms=MS.playedMoveset(fid), idx=(MS.getMovesetIndex()||{}).fighters||{};
  const cur=MS.resolveMove(fid,n);
  let src=ms, srcId=fid, rows=[];
  if(tab==='same') rows=msAlternates(ms,n);
  else if(tab==='all') rows=Object.entries(ms.moves);
  else { srcId=other||Object.keys(idx).find(i=>i!==fid); await MS.ensureMovesets([srcId]); src=MS.getFighterMoveset(srcId); rows=src?Object.entries(src.moves):[]; }
  const ql=q.toLowerCase();
  if(ql) rows=rows.filter(([k,m])=>k.toLowerCase().includes(ql)||String(m.name||'').toLowerCase().includes(ql));
  const shown=rows.slice(0,120);
  const tabs=[['same','SAME INPUT'],['all','ALL MOVES'],['other','OTHER FIGHTER']];
  const body=`<div class="kv"><span>Input</span><b>${esc(n)}</b></div>
    <div class="kv"><span>Now</span><b>${esc(cur?cur.move.name||cur.key:'—')} ${cur?`· ${msSrc(cur.move)} · ${msInfo(cur.ms,cur.key,cur.move)}`:''}</b></div>
    <div class="ms-cats">${tabs.map(([k,l])=>`<button class="chip ms-tab ${tab===k?'on':''}" data-t="${k}">${l}</button>`).join('')}</div>
    ${tab==='other'?`<div class="field"><select id="lib-fid">${Object.keys(idx).sort().map(i=>`<option value="${i}" ${i===srcId?'selected':''}>${esc((idx[i]||{}).display||i)} — ${esc((idx[i]||{}).tekken_base||'')}</option>`).join('')}</select></div>`:''}
    <div class="field"><input id="lib-q" type="search" placeholder="search" value="${esc(q)}"></div>
    <div class="note">${rows.length} moves${rows.length>shown.length?` (first ${shown.length}; search to narrow)`:''}. Tap one to assign it to <b>${esc(n)}</b>.</div>
    <div class="ms-lib">${shown.map(([k,m])=>`<button class="ms-row" data-k="${esc(k)}"><span class="ms-in">${esc(m.input||k)}</span>
      <span class="ms-name">${esc(m.name||k)}</span><span class="ms-tag">${msSrc(m)}</span><span class="ms-fd">${msInfo(src,k,m)}</span></button>`).join('')}</div>`;
  modal(`MOVE LIBRARY — ${esc(n)}`, body, [{label:'RESET TO DEFAULT',cls:'btn-red',fn:()=>{ MS.setLoadoutSlot(fid,n,null); renderPanel(); toast('Default restored ✓'); }},{label:'CLOSE'}]);
  const mb=$('#modal-body');
  mb.querySelectorAll('.ms-tab').forEach(b=>b.onclick=()=>openMoveLibrary(fid,n,b.dataset.t,null,''));
  const lf=mb.querySelector('#lib-fid'); if(lf) lf.onchange=()=>openMoveLibrary(fid,n,'other',lf.value,'');
  const lq=mb.querySelector('#lib-q'); if(lq) lq.onchange=()=>openMoveLibrary(fid,n,tab,srcId,lq.value);
  mb.querySelectorAll('.ms-row').forEach(b=>b.onclick=()=>{
    const k=b.dataset.k; MS.setLoadoutSlot(fid, n, srcId===fid ? k : `${srcId}::${k}`);
    closeModal(); renderPanel(); toast(`${n} → ${(src.moves[k]||{}).name||k} ✓`);
  });
}

/* ================= DOME (Doc Frank Wowomomo — owner edits it himself) =================
   Owner 2026-10-19: "put all the abilities in the creation suite for me to change
   and edit and move all that stuff around while having a visual preview."
   Mounts game/js/dome-params.js (DOME_PARAM_SCHEMA + load/save) into the live
   menu flow. Live preview = cross-section canvas drawn from the params.
   Params persist per-attire in localStorage AND via Save (dome-params.json). */
const DOME_ATTIRE_PATH = 'roster/doc-frank/attires/attire2';
const DOME_LS_KEY = 'wh_dome_params_v1';
let domeMod = null, domeParams = null;

async function getDomeMod(){
  if(domeMod) return domeMod;
  try{ domeMod = await import('../../../game/js/dome-params.js'); }
  catch(e){ console.warn('[WH] dome-params import failed:', e); }
  return domeMod;
}

function drawDomePreview(cv, p){
  const ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height;
  ctx.clearRect(0,0,W,H);
  // Scale: z 0.10..0.50 maps to bottom..top of canvas; x -0.12..0.12
  const z2y = z => H - ((z-0.10)/(0.50-0.10))*H;
  const x2x = x => W/2 + (x/0.12)*(W/2);
  // Head/face reference (schematic): face center z≈0.33, half-width 0.075
  ctx.fillStyle = 'rgba(200,170,140,0.25)';
  ctx.beginPath(); ctx.ellipse(W/2, z2y(0.345), x2x(0.075)-W/2, (z2y(0.28)-z2y(0.41))/2, 0, 0, Math.PI*2); ctx.fill();
  // Brain (existing brain floats in the fluid — never add another)
  ctx.fillStyle = 'rgba(255,150,180,0.8)';
  ctx.beginPath(); ctx.ellipse(W/2, z2y(0.375), 16, 10, 0, 0, Math.PI*2); ctx.fill();
  // Liquid: forward offset shifts it toward the viewer (drawn as +x here)
  const lr = 0.077 * (p.liquid_radius_scale||1);
  const lx = p.liquid_forward_offset||0;
  const fc = p.fluid_color||[0.30,0.85,0.40,1];
  ctx.fillStyle = `rgba(${Math.round(fc[0]*255)},${Math.round(fc[1]*255)},${Math.round(fc[2]*255)},0.55)`;
  ctx.fillRect(x2x(lx-lr), z2y(p.fluid_z_top), x2x(lx+lr)-x2x(lx-lr), z2y(p.fluid_z_bot)-z2y(p.fluid_z_top));
  // Glass: full 360 dome — outer shell from glass_z_bot up over the top
  ctx.strokeStyle = 'rgba(180,230,255,0.95)'; ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x2x(-0.0967), z2y(p.glass_z_bot));
  ctx.lineTo(x2x(-0.0967), z2y(p.glass_joint_z));
  ctx.quadraticCurveTo(x2x(-0.0967), z2y(0.50), x2x(0), z2y(0.50));
  ctx.quadraticCurveTo(x2x(0.0967), z2y(0.50), x2x(0.0967), z2y(p.glass_joint_z));
  ctx.lineTo(x2x(0.0967), z2y(p.glass_z_bot));
  ctx.stroke();
  // Face coverage readout
  const top = p.fluid_z_top, bot = p.fluid_z_bot;
  const covered = (top>=0.41 && bot<=0.28) ? 'FACE FULLY SUBMERGED' : 'FACE PARTIALLY COVERED';
  ctx.fillStyle = '#fff'; ctx.font = 'bold 13px sans-serif'; ctx.textAlign = 'center';
  ctx.fillText(covered, W/2, 18);
  ctx.font = '11px sans-serif';
  ctx.fillText(`liquid ${bot.toFixed(3)} → ${top.toFixed(3)} · fwd ${lx.toFixed(3)} · width ×${(p.liquid_radius_scale||1).toFixed(2)} · glass bottom ${p.glass_z_bot.toFixed(3)}`, W/2, H-8);
}

async function renderDome(el){
  $('#panel-sub').textContent='Doc Frank Wowomomo dome — liquid / glass / effects (owner-editable)';
  el.innerHTML=`<div class="note">🫧 Dome parameters for <span class="chip">${DOME_ATTIRE_PATH}</span>.
    Live cross-section preview below. <b>Save to Attire</b> writes dome-params.json — the build script
    (build-dome-v5.py) reads the same file, so your edits rebuild the in-game dome straight from the files.</div>
    <canvas id="dome-preview" width="340" height="240" style="width:100%;max-width:340px;background:#10141c;border-radius:8px;display:block;margin:8px auto"></canvas>
    <div id="dome-controls"><div class="note">Loading dome parameters…</div></div>`;
  const mod = await getDomeMod();
  const cv = el.querySelector('#dome-preview');
  if(!mod){
    el.querySelector('#dome-controls').innerHTML = '<div class="note">⚠️ dome-params module failed to load (game/js/dome-params.js).</div>';
    return;
  }
  if(!domeParams){
    domeParams = await mod.loadDomeParams(DOME_ATTIRE_PATH);
    try{ const saved = JSON.parse(localStorage.getItem(DOME_LS_KEY)||'null');
      if(saved) for(const k of Object.keys(mod.DOME_PARAM_DEFAULTS)) if(k in saved) domeParams[k]=saved[k];
    }catch(e){}
  }
  const onChange = ()=>{ drawDomePreview(cv, domeParams);
    try{ localStorage.setItem(DOME_LS_KEY, JSON.stringify(domeParams)); }catch(e){} };
  el.querySelector('#dome-controls').dataset.attirePath = DOME_ATTIRE_PATH;
  mod.createDomeParamUI(el.querySelector('#dome-controls'), domeParams, onChange);
  drawDomePreview(cv, domeParams);
}

/* ---------- CREATE: base-body templates (WWE 2K-style template select) ---------- */
function templateById(id){ return TEMPLATES.find(t=>t.id===id) || null; }
/* Saved fighters from before 2026-11-01: the stock Soldier base becomes the default template body, and body types
   named after real people take their generic names. */
function migrateLegacy(){
  const fix = o => { if(!o) return;
    if(!o.baseGlb || o.baseGlb===LEGACY_SOLDIER_GLB){ o.baseGlb = BLANK_GLB; if(o===F) F.template = F.template || DEFAULT_TEMPLATE_ID; }
    if(o.body && BODY_TYPE_ALIAS[o.body.body_type]) o.body.body_type = BODY_TYPE_ALIAS[o.body.body_type]; };
  fix(F);
  for(const k of Object.keys(F.records||{})) fix(F.records[k]);
  if(F.mode==='blank' && !F.template) F.template = DEFAULT_TEMPLATE_ID;
}
function bodyTypeForTemplate(t){
  const bt = BODY_TYPE_ALIAS[t.body_type] || t.body_type;
  return BODY_TYPES.includes(bt) ? bt : (t.gender==='female' ? 'Medium F' : 'Medium 1');
}
/* Start a NEW fighter from template t: base mesh, body class, build, skin, jiggle family. */
async function applyTemplate(t){
  if(F.mode!=='blank') stashCurrent();   // keep the roster attire being edited; the new fighter is the blank slot
  const keep = F.records;
  Object.assign(F, blankFighter()); F.records = keep;
  F.template = t.id; F.baseGlb = t.base_mesh || templateGlb(t.id);
  F.body.body_type = bodyTypeForTemplate(t);
  if(t.skin_tone) F.body.skin_tone = t.skin_tone;
  const pr = t.proportions || {};
  for(const k of ['height','weight','muscle']) if(typeof pr[k]==='number') F.body.proportions[k] = pr[k];
  F.jiggle.family = t.gender==='female' ? 'female' : 'male';
  ui.selPart=null; hidePlaceDock(); setTab('body');
  persistQuiet();
  await loadBaseModel();
  toast(`${t.name} — now make them yours`);
}
function openTemplateSelect(){
  if(!TEMPLATES.length){ modal('CREATE A FIGHTER','<p>Base bodies failed to load (customization/templates/body-templates.json).</p>',[{label:'CLOSE',cls:'btn-gold'}]); return; }
  const groups = {};
  for(const t of TEMPLATES) (groups[t.division] = groups[t.division] || []).push(t);
  const html = Object.entries(groups).map(([div, list])=>`<div class="sect">${esc(div).toUpperCase()}</div>
    <div class="tpl-grid">${list.map(t=>`<button class="tpl-card${F.mode==='blank'&&F.template===t.id?' active':''}" data-t="${esc(t.id)}">
      <span class="tpl-name">${esc(t.name)}</span><span class="tpl-meta">${t.gender==='female'?'Women':'Men'} · ${esc(bodyTypeForTemplate(t))}</span>
      <span class="tpl-desc">${esc(t.desc||'')}</span></button>`).join('')}</div>`).join('');
  modal('CREATE A FIGHTER — CHOOSE A BASE BODY', html, [{label:'CANCEL',cls:''}]);
  document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{ const t=templateById(b.dataset.t); closeModal(); if(t) applyTemplate(t); });
}

/* ---------- roster / save / export ---------- */
$('#btn-roster').onclick=()=>{
  if(!ROSTER){ modal('FIGHTER SELECT','<p>Roster data (data/roster-attires.json) failed to load.</p>',[{label:'CLOSE',cls:'btn-gold'}]); return; }
  /* One card per WH fighter (names law: the WH name, never the source model's folder name); folders that hold the
     same fighter merge their attires. Unassigned base bodies get their own section: start a new fighter from one. */
  const groups = new Map();
  for(const f of ROSTER.fighters){
    const name = rosterName(f), key = f.unassigned ? 'u:'+f.fighter : 'n:'+name;
    if(!groups.has(key)) groups.set(key, { name, unassigned:!!f.unassigned, folders:[] });
    groups.get(key).folders.push(f);
  }
  const card = (g, i)=>{ const n = g.folders.reduce((a,f)=>a+f.attires.length,0);
    const on = F.rosterRef && g.folders.some(f=>f.fighter===F.rosterRef.fighter);
    return `<button class="roster-card${on?' active':''}" data-g="${i}">${esc(g.name)}<br><small style="color:var(--dim)">${n} attire${n===1?'':'s'}</small></button>`; };
  const list = [...groups.values()];
  const named = list.map((g,i)=>[g,i]).filter(([g])=>!g.unassigned).sort((a,b)=>a[0].name.localeCompare(b[0].name));
  const unassigned = list.map((g,i)=>[g,i]).filter(([g])=>g.unassigned);
  const fighters = named.map(([g,i])=>card(g,i)).join('');
  const bodies = unassigned.map(([g,i])=>card(g,i)).join('');
  modal('FIGHTER SELECT',`<div class="sect">CREATE</div>
    <div class="roster-grid"><button class="roster-card${F.mode==='blank'?' active':''}" data-f="">＋ CREATE A FIGHTER<br><small style="color:var(--dim)">start from a base body</small></button></div>
    <div class="sect">EDIT A FIGHTER — pick the fighter, then the attire</div>
    <div class="roster-grid">${fighters}</div>
    ${bodies ? `<div class="sect">UNASSIGNED BASE BODIES — make one into a new fighter</div><div class="roster-grid">${bodies}</div>` : ''}
    <div id="roster-attires"></div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  { const cb=document.querySelector('[data-f=""]'); if(cb) cb.onclick=()=>{ closeModal(); openTemplateSelect(); }; }
  document.querySelectorAll('[data-g]').forEach(b=>b.onclick=()=>{
    const g=list[+b.dataset.g]; if(!g) return;
    const host=document.querySelector('#roster-attires');
    const items=[]; for(const f of g.folders) for(const a of f.attires) items.push({ f:f.fighter, a });
    host.innerHTML=`<div class="sect">${esc(g.name)} — ATTIRE</div><div class="roster-grid">${
      items.map((it,k)=>`<button class="roster-card" data-k="${k}">${esc(it.a.attire_name)}<br><small style="color:var(--dim)">ATTIRE ${k+1}</small></button>`).join('')}</div>`;
    host.querySelectorAll('[data-k]').forEach(ab=>ab.onclick=()=>{ const it=items[+ab.dataset.k]; closeModal(); selectRosterAttire(it.f, it.a.attire_id); });
    host.scrollIntoView({ block:'nearest' });
  });
};
$('#btn-save').onclick=persist;
{ const bsa=$('#btn-save-attire'); if(bsa) bsa.onclick=saveToAttire; }
/* Stream 4: in-game wiring — back to the game menu (saves first). */
{ const bg=$('#btn-back-game'); if(bg) bg.onclick=()=>{ persistQuiet(); window.location.href='../../index.html'; } }
$('#btn-export').onclick=()=>{
  const blob=new Blob([JSON.stringify(F,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='creation-suite-fighter.json'; a.click(); URL.revokeObjectURL(a.href); toast('Exported ✓');
};

/* ---------- boot ---------- */
async function boot(){
  let firstVisit = true;
  try{ const s=localStorage.getItem(LS_KEY); if(s){ F=Object.assign(blankFighter(), JSON.parse(s)); firstVisit=false; } }catch(e){}
  try{
    const [parts, jig, roster, fparts] = await Promise.all([
      fetch('data/parts-catalog.json').then(r=>r.json()),
      fetch('data/jiggle-schema.json').then(r=>r.json()),
      fetch('data/roster-attires.json').then(r=>r.ok?r.json():null).catch(()=>null),
      fetch('data/fighter-parts.json').then(r=>r.ok?r.json():null).catch(()=>null),
      fetch('../templates/body-templates.json').then(r=>r.ok?r.json():null).catch(()=>null),
    ]).then(([parts, jig, roster, fparts, tpls])=>{ TEMPLATES = (tpls && tpls.templates) || []; return [parts, jig, roster, fparts]; });
    PARTS = Array.isArray(parts) ? parts : (parts.parts||[]);
    PARTS_META = Array.isArray(parts) ? null : parts;
    // normalize legacy curated entries (pre-unified catalogs) to the v2 shape
    PARTS.forEach(p=>{ if(!p.asset) p.asset=p.glb||null; if(!p.source) p.source=p.library||'curated';
      if(!p.t7_slot) p.t7_slot=SLOT2CAT[p.suite_slot]||null;
      if(p.geometry_pending===undefined) p.geometry_pending=!!p.geometryPending; });
    JIGGLE=jig; ROSTER=roster; FPARTS=fparts;
  }catch(e){
    $('#loader').innerHTML='<div>DATA LOAD FAILED — serve over http</div>'; return;
  }
  if(!Array.isArray(F.records)) F.records = F.records||{};
  if(F.mode==='roster' && (!F.rosterRef || !rosterAttire(F.rosterRef.fighter, F.rosterRef.attire))){ F.mode='blank'; F.rosterRef=null; F.baseGlb=BLANK_GLB; }
  migrateLegacy();
  viewer=new SuiteViewer($('#stage3d'));
  // frame the fighter in the area the top bar, rails, side panel / bottom sheet and bottom bar leave free
  viewer.setInsets(()=>{
    const r = id => { const e=document.getElementById(id); return e && !e.hidden ? e.getBoundingClientRect() : null; };
    const W=innerWidth, H=innerHeight, tb=r('topbar'), lr=r('left-rail'), rr=r('right-rail'), bb=r('bottombar');
    let right=0, bottom = bb ? Math.max(0, H-bb.top) : 0;
    if(rr){ if(rr.top > H*0.3) bottom = Math.max(bottom, H-rr.top); else right = Math.max(0, W-rr.left); }
    return { left: lr ? lr.right : 0, right, top: tb ? tb.bottom : 0, bottom };
  });
  window.__suite={ viewer, get F(){return F;}, ui, setTab, selectRosterAttire, customizationRecord, currentKey, get ROSTER(){return ROSTER;}, get PARTS(){return PARTS;}, get FPARTS(){return FPARTS;} };
  viewer.onReady=()=>{ renderAll(); };
  await loadBaseModel();
  renderAll();
  $('#loader').classList.add('done');
  // first visit: CREATE opens on the base-body select (WWE 2K flow), not on a default model
  if(firstVisit && F.mode==='blank') openTemplateSelect();
}
boot();

