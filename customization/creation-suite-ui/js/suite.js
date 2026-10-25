/* suite.js — Creation Suite hub logic.
   Laws: tap slot → scroll library → tap to assign. NO drag-and-drop anywhere. Phone-first.
   Menu trees verbatim from teardown games (see menu-data.js + UI-EXTRACTION-LOG.md). */
import { SuiteViewer } from './viewer3d.js';
import { ATTIRE_TREE, BODY_TREE, PARTS_TREE, JIGGLE_AREAS, JIGGLE_PARAMS, JIGGLE_FAMILIES, PLACE_AXES, MENU_SRC } from './menu-data.js';
/* Real morph catalog + DNA/body engine from packages/creation-suite
   (importmap: wh-creation-suite/ -> ../../packages/creation-suite/src/).
   Thin adapter below maps morph ids onto DNA sliders — logic is NOT forked. */
import { BODY_MORPHS, FACE_SHAPE_MORPHS, applyMorphProxies } from 'wh-creation-suite/morphs.js';
import { SLIDERS as DNA_SLIDERS } from 'wh-creation-suite/dna.js';
import { applySliders as applyBodySliders } from 'wh-creation-suite/body.js';
/* Body-type -> template/proportions mapping (pure, Node-tested) + WWE 2K19
   layering conflicts. Importmap: wh-creation-suite/ -> packages/creation-suite/src/. */
import { bodyTypeToDNA, propsToDNA, mergeDNA, DEFAULT_PROPS } from 'wh-creation-suite/template-map.js';
import { SLOT_CONFLICTS } from 'wh-creation-suite/layering.js';
/* The game's own moveset engine (same module the fight runs): notation tables, slots, loadouts. */
import * as MS from '../../../game/js/movesets.js';
MS.setMovesetBase('../../game/assets/movesets/');

const LS_KEY = 'wh_creation_suite_v1';
const START_MONEY = 12400;
const $ = s=>document.querySelector(s);
/* tap() — PR #1018 menu-fix pattern, reused for fighter-select taps (user
   2026-10-24 19:45 CDT: taps on fighter cards did nothing). A tap inside a
   scrollable list is cancelled by a small scroll-drag, so click-only handlers
   silently drop it; tap() fires on touchend unless the finger dragged >12px,
   and dedups the synthesized click that follows a touchend for 600ms so one
   tap never fires twice. */
function tap(el, fn){
  if(!el) return;
  let sx=0, sy=0, moved=false;
  el.addEventListener('touchstart', e=>{ const t=e.touches[0]; sx=t.clientX; sy=t.clientY; moved=false; }, {passive:true});
  el.addEventListener('touchmove', e=>{ const t=e.touches[0]; if(Math.abs(t.clientX-sx)>12 || Math.abs(t.clientY-sy)>12) moved=true; }, {passive:true});
  el.addEventListener('touchend', e=>{ if(moved) return; const now=Date.now(); if(el._tapLast && now-el._tapLast<600) return; el._tapLast=now; e.preventDefault(); fn(e); });
  el.addEventListener('click', e=>{ const now=Date.now(); if(el._tapLast && now-el._tapLast<600) return; el._tapLast=now; fn(e); });
}

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
    baseGlb:'customization/templates/meshes/technician.glb' };
}
let F = blankFighter();
let PARTS = [];       // parts-catalog.json parts[] (unified catalog v2)
let PARTS_META = null; // parts-catalog.json header (counts/sources)
let ROSTER = null;    // data/roster-attires.json (build_roster_attires.py)
let JIGGLE = null;    // jiggle-schema.json
let FPARTS = null;    // data/fighter-parts.json (Phase 1: SmutBase-6 own-mesh parts)
let TEMPLATES = [];   // customization/templates/body-templates.json (9 MB-Lab bodies)
let FACE_PRESETS = []; // customization/templates/face-presets.json (wwe + gnm layers)
let viewer = null;
let ui = { tab:'body', bodySec:null, attireCat:null, partsCat:null, selPart:null, wardSel:0, nudgeStep:0.001, page:0, query:'' };

const attire = ()=>F.attires[F.attireIndex];

/* ---------- roster mode (UNIFIED-UI-SPEC §2 entry flow) ----------
   pick fighter -> pick attire -> hub, loading THAT attire's real GLB.
   Working state stays in the top-level F fields; switching stashes the
   current state into F.records[key] and restores the target's record. */
const BLANK_GLB = 'customization/templates/meshes/technician.glb';
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
function rosterAttire(slug, attireId){
  const f = rosterFighter(slug); if(!f) return null;
  return f.attires.find(a=>a.attire_id===attireId) || null;
}
async function loadBaseModel(){
  if(!viewer) return;
  /* Mixamo removal: no special-case anymore. The blank base IS the Technician
     MB-Lab bake (body-templates.json, No Mercy Medium 1) and resolves through
     the same '../../' prefix as every other model. */
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
      F.profile.name = rf.fighter_name.toUpperCase();
      F.profile.short_name = rf.fighter_name.slice(0,4).toUpperCase();
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
  // Universal mesh toggles (OUTFIT tab, every model)
  const mesh_states={};
  for(const [mn, st] of Object.entries(a.meshStates||{})){
    if(!st) continue;
    if((st.mode&&st.mode!=='shown')||st.color)
      mesh_states[mn]={ mode:st.mode||'shown', color:st.color||null };
  }
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
    body:{ body_type:F.body.body_type, skin_tone:F.body.skin_tone,
           head_shape:F.body.head_shape||null, face_preset:F.body.face_preset||null,
           proportions:F.body.proportions||null },
    morphs, parts, textures, part_states, mesh_states,
    colors:{ hair:(a.colors&&a.colors.hair)||null, skin:F.body.skin_tone } };
}
function applyCustomizationRecord(rec){
  if(rec.body){ if(rec.body.body_type) F.body.body_type=rec.body.body_type;
    if(rec.body.skin_tone) F.body.skin_tone=rec.body.skin_tone;
    if(rec.body.head_shape) F.body.head_shape=rec.body.head_shape;
    if(rec.body.face_preset) F.body.face_preset=rec.body.face_preset;
    if(rec.body.proportions) F.body.proportions={ ...F.body.proportions, ...rec.body.proportions }; }
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
  // Universal mesh toggles (OUTFIT tab, every model)
  a.meshStates = rec.mesh_states ? JSON.parse(JSON.stringify(rec.mesh_states)) : {};
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
    tap(b, ()=>{ closeModal(); a.fn&&a.fn(); }); box.appendChild(b); });
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
  /* WMXIX props are the coarse template proportions, morphs the fine layer:
     both feed the DNA engine additively (template-map mergeDNA), clamped to
     each slider's range. Height/weight stay out — viewer.setProportions()
     owns those as uniform model scale, so they are never applied twice. */
  const sliders = mergeDNA(propsToDNA(F.body.proportions), morphsToDnaSliders(F.morphs));
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
  viewer.setSkinTone(F.body.skin_tone);
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
/* Universal part toggles: any loaded model (not just the SmutBase 6 with a
   fighter-parts inventory) exposes its own meshes for show/hide/invisible/
   recolor via attire().meshStates. Stored per attire like partStates. */
const meshState = mn => (attire().meshStates||{})[mn] || { mode:'shown', color:null };
function setMeshState(mn, patch){
  const a = attire(); a.meshStates = a.meshStates || {};
  a.meshStates[mn] = { ...meshState(mn), ...patch };
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
  /* Universal mesh toggles (see meshState above): apply to every model,
     whether or not it has a fighter-parts inventory. */
  for(const [meshName, st] of Object.entries(attire().meshStates||{})){
    viewer.setBaseMeshMode(meshName, st.mode||'shown');
    viewer.setBaseMeshColor(meshName, st.color||null);
  }
}
function renderOutfit(el){
  const fp = fpartsForCurrent();
  if(!fp){
    /* Universal OUTFIT: no labeled parts inventory for this model — toggle
       the model's OWN meshes directly. This is what makes per-part toggles
       work on EVERY model (owner directive 2026-10-24 19:54 CDT), not just
       the SmutBase 6. The old branch was a dead-end note telling the user to
       pick a different fighter. */
    $('#panel-sub').textContent='Model meshes — per-part toggles (works on every model)';
    const meshes = (viewer && viewer.listBaseMeshes) ? viewer.listBaseMeshes() : [];
    el.innerHTML=`<div class="note">🧥 No labeled parts inventory for this model — toggling
      the model's OWN meshes directly (universal: every model, every rig).
      👁 show/hide · 👻 invisible (slot stays occupied, for layering) · 🎨 recolor.
      States save per attire (PROFILE → SAVE TO ATTIRE) and apply in-fight.</div>
      <div class="sect">MESHES — ${meshes.length}</div><div id="of-generic"></div>`;
    const host = el.querySelector('#of-generic');
    meshes.forEach(mn => host.appendChild(meshRow(mn)));
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
function meshRow(mn){
  const st = meshState(mn);
  const d = document.createElement('div');
  d.className='of-row';
  d.innerHTML=`
    <div class="of-main">
      <div class="of-name">${esc(mn)}</div>
      <div class="of-state"><span class="chip of-${st.mode||'shown'}">${{shown:'SHOWN',hidden:'HIDDEN',invisible:'INVISIBLE',deleted:'DELETED'}[st.mode||'shown']}</span>${st.color?` <span class="chip">🎨 <i style="display:inline-block;width:10px;height:10px;background:${st.color};border-radius:2px"></i></span>`:''}</div>
    </div>
    <div class="of-ctl"></div>`;
  const ctl = d.querySelector('.of-ctl');
  const bVis=document.createElement('button'); bVis.className='btn btn-sm';
  bVis.textContent=(st.mode==='hidden'||st.mode==='invisible')?'👁 SHOW':'👁 HIDE';
  tap(bVis, ()=>{ const cur=meshState(mn).mode||'shown';
    setMeshState(mn,{mode:(cur==='hidden'||cur==='invisible')?'shown':'hidden'}); renderPanel(); });
  const bInv=document.createElement('button'); bInv.className='btn btn-sm'; bInv.textContent='👻 INVISIBLE';
  bInv.title='Hidden, but the slot stays occupied (layering)';
  tap(bInv, ()=>{ const cur=meshState(mn).mode||'shown';
    setMeshState(mn,{mode:cur==='invisible'?'shown':'invisible'}); renderPanel(); });
  const bCol=document.createElement('label'); bCol.className='btn btn-sm'; bCol.textContent='🎨';
  bCol.title='Recolor this mesh'; bCol.style.position='relative'; bCol.style.overflow='hidden';
  const inp=document.createElement('input'); inp.type='color'; inp.value=st.color||'#ffffff'; inp.setAttribute('aria-label','Recolor '+mn);
  inp.style.cssText='position:absolute;inset:0;opacity:0;width:100%;height:100%;cursor:pointer';
  inp.oninput=()=>{ setMeshState(mn,{color:inp.value}); };
  inp.onchange=()=>{ renderPanel(); };
  bCol.appendChild(inp);
  const bColX=document.createElement('button'); bColX.className='btn btn-sm'; bColX.textContent='🎨✕'; bColX.title='Clear recolor';
  tap(bColX, ()=>{ setMeshState(mn,{color:null}); renderPanel(); });
  [bVis,bInv,bCol,bColX].forEach(b=>ctl.appendChild(b));
  return d;
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
  tap(bVis, ()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:(cur==='hidden'||cur==='invisible')?'shown':'hidden'}); renderPanel(); });
  const bInv=document.createElement('button'); bInv.className='btn btn-sm'; bInv.textContent='👻 INVISIBLE';
  bInv.title='Hidden, but the slot stays occupied (layering)';
  tap(bInv, ()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:cur==='invisible'?'shown':'invisible'}); renderPanel(); });
  const bCol=document.createElement('label'); bCol.className='btn btn-sm'; bCol.textContent='🎨';
  bCol.title='Recolor this part'; bCol.style.position='relative'; bCol.style.overflow='hidden';
  const inp=document.createElement('input'); inp.type='color'; inp.value=st.color||'#ffffff'; inp.setAttribute('aria-label','Recolor '+p.label);
  inp.style.cssText='position:absolute;inset:0;opacity:0;width:100%;height:100%;cursor:pointer';
  inp.oninput=()=>{ setFpartState(p.id,{color:inp.value}); };
  inp.onchange=()=>{ renderPanel(); };
  bCol.appendChild(inp);
  const bColX=document.createElement('button'); bColX.className='btn btn-sm'; bColX.textContent='🎨✕'; bColX.title='Clear recolor';
  tap(bColX, ()=>{ setFpartState(p.id,{color:null}); renderPanel(); });
  const bDel=document.createElement('button');
  bDel.className='btn btn-sm '+((st.mode==='deleted')?'btn-green':'btn-red');
  const canDelete = p.swappable && !p.signature;
  bDel.textContent = st.mode==='deleted' ? '↩ RESTORE' : '🗑 DELETE';
  bDel.disabled = !canDelete && st.mode!=='deleted';
  bDel.title = p.signature ? 'Signature part — canon: never removed' : (p.swappable?'Remove from this attire':'Not separable — hide/recolor only');
  tap(bDel, ()=>{ const cur=fpartState(p.id).mode||'shown';
    setFpartState(p.id,{mode:cur==='deleted'?'shown':'deleted'}); renderPanel(); });
  const bSwap=document.createElement('button'); bSwap.className='btn btn-sm btn-blue';
  bSwap.textContent = st.swap ? '🔀 SWAPPED ✓' : '🔀 SWAP';
  bSwap.disabled = !p.swappable;
  bSwap.title = p.swappable ? 'Replace with a compatible catalog part' : 'Not swappable';
  tap(bSwap, ()=>openSwapLibrary(p));
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
  mb.querySelectorAll('.ms-row').forEach(b=>tap(b, ()=>{
    const c=PARTS.find(x=>x.id===b.dataset.id); if(!c) return;
    setFpartState(p.id,{mode:'shown', swap:{part_id:c.id, name:c.name, glb:c.glb, socket:partSocket(c), placement:defaultPlacement(c)}});
    closeModal(); renderPanel(); toast('Swapped ✓');
  }));
  const clr=mb.querySelector('#swap-clear');
  if(clr) tap(clr, ()=>{ setFpartState(p.id,{swap:null}); closeModal(); renderPanel(); toast('Swap removed ✓'); });
}

/* ---------- topbar ---------- */
function renderTopbar(){
  $('#fighter-name').textContent = F.profile.name||'NEW FIGHTER';
  $('#breadcrumb').textContent = `${F.profile.name||'New Fighter'} > Attire ${F.attireIndex+1} > ${ui.tab.toUpperCase()}${ui.bodySec?' > '+ui.bodySec.toUpperCase():''}${ui.attireCat?' > '+ui.attireCat.label:''}${ui.partsCat?' > '+ui.partsCat.label:''}`;
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
  ui.tab=t; ui.bodySec=null; ui.attireCat=null; ui.partsCat=null; ui.selPart=null;
  document.querySelectorAll('.rail-btn').forEach(x=>x.classList.toggle('active',x.dataset.tab===t));
  if(t!=='parts') hidePlaceDock();
  renderAll();
}
document.querySelectorAll('.rail-btn').forEach(b=>tap(b, ()=>setTab(b.dataset.tab)));

function renderAll(){ renderTopbar(); renderPanel(); syncPreview(); persistQuiet(); }
function renderPanel(){
  const body=$('#panel-body');
  $('#panel-title').textContent=ui.tab.toUpperCase(); $('#panel-sub').textContent='';
  body.innerHTML='';
  ({body:renderBody,attire:renderAttire,parts:renderParts,outfit:renderOutfit,jiggle:renderJiggle,
    wardrobe:renderWardrobe,profile:renderProfile,moveset:renderMoveset,dome:renderDome,tools:renderTools})[ui.tab](body);
}

/* ================= BODY ================= */
/* ================= BODY — nested like WWE 2K CAW =================
   WWE 2K CAW nesting (customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md §2.2:
   Custom Superstar -> Appearance -> Body -> presets / morph sliders) +
   Tekken customization slots for attire. The old BODY tab rendered all six
   sections flat in one long scroll — the "ugly flat menu" in the user's
   2026-10-24 screenshot. Now: one section list, one section at a time, a
   back button that always works, and the 3D preview always visible. */
const BODY_SECTIONS = [
  { key:'templates', icon:'🧱', label:'TEMPLATES', note:'9 real MB-Lab bodies (No Mercy) — tap to swap the whole body' },
  { key:'bodytype', icon:'👤', label:'BODY TYPE', note:'23 No Mercy types — tap to apply proportions (+ mesh where a template exists)' },
  { key:'skintone', icon:'🎨', label:'SKIN TONE', note:'8 tones' },
  { key:'props', icon:'📏', label:'PROPORTIONS', note:'WMXIX parametric sliders (live)' },
  { key:'morphs', icon:'💪', label:'MORPHS', note:'Frame / Mass / Face Shape' },
  { key:'face', icon:'😀', label:'FACE', note:'12 presets — No Mercy faces + GNM expressions' },
];
function renderBody(el){
  $('#panel-sub').textContent='Wrestling CAW — No Mercy body types, WMXIX proportions';
  if(!ui.bodySec){
    el.innerHTML=`<div class="note">Appearance → Body, nested like WWE 2K CAW
      (Custom Superstar → Appearance → Body) and Tekken customization: pick a
      section, change it, back out. The 3D preview stays visible throughout.</div>` +
      BODY_SECTIONS.map(s=>`<button class="subcat" data-bs="${s.key}"><span class="sc-ico">${s.icon}</span><span>${s.label}<br><small style="color:var(--dim)">${s.note}</small></span></button>`).join('');
    el.querySelectorAll('[data-bs]').forEach(b=>tap(b, ()=>{ ui.bodySec=b.dataset.bs; renderPanel(); }));
    return;
  }
  const backTo = ui.bodySec.startsWith('morph-') ? 'morphs' : null;
  el.innerHTML=`<div class="back-row"><button class="btn back-btn" id="btn-body-back">← ${backTo ? 'MORPHS' : 'BODY'}</button></div><div id="body-sec"></div>`;
  tap(el.querySelector('#btn-body-back'), ()=>{ ui.bodySec=backTo; renderPanel(); });
  const host = el.querySelector('#body-sec');
  ({ templates:renderBodyTemplates, bodytype:renderBodyType, skintone:renderBodySkin,
     props:renderBodyProps, morphs:renderBodyMorphMenu, 'morph-frame':h=>renderBodyMorphList(h,'frame'),
     'morph-mass':h=>renderBodyMorphList(h,'mass'), 'morph-face':h=>renderBodyMorphList(h,'face'),
     face:renderBodyFace })[ui.bodySec](host);
}
/* Apply a full template: body type + proportions + skin + head + MESH.
   Switching templates changes the character (mesh + proportions + parts),
   not just a label — the mesh swap is the visible proof. Proportions reset
   to the template (defaults + template values); fine morphs stay on top. */
function applyTemplate(t){
  F.body.body_type = t.body_type;
  F.body.proportions = { ...DEFAULT_PROPS, ...(t.proportions||{}) };
  F.body.skin_tone = t.skin_tone;
  F.body.head_shape = t.head_shape;
  const meshChanged = F.baseGlb !== t.base_mesh;
  F.baseGlb = t.base_mesh;
  toast(`Template: ${t.name} ✓`);
  if(meshChanged) loadBaseModel(); else renderAll();
}
function renderBodyTemplates(host){
  $('#panel-sub').textContent='Templates — 9 real MB-Lab bodies (body-templates.json)';
  if(!TEMPLATES.length){ host.innerHTML='<div class="note">Templates failed to load (customization/templates/body-templates.json).</div>'; return; }
  host.innerHTML=`<div class="note">Tap a template — the mesh, proportions, skin tone
    and head shape all change. Technician (Medium 1) is the blank CAW canvas.</div>` +
    TEMPLATES.map(t=>`<button class="subcat" data-t="${esc(t.id)}"><span class="sc-ico">🧱</span><span>${esc(t.name)}<br><small style="color:var(--dim)">${esc(t.body_type)} · ${esc(t.division)} · ${esc(t.gender)} · ${esc(t.desc||'')}</small></span></button>`).join('');
  host.querySelectorAll('[data-t]').forEach(b=>tap(b, ()=>{
    const t=TEMPLATES.find(x=>x.id===b.dataset.t); if(t) applyTemplate(t); }));
}
/* Apply a body type: proportions from template-map (dedicated template, or
   legacy h/w + family muscle, or whole family proportions for F types).
   The basis is shown in the toast — a family fallback is never presented
   as extracted data. Where the resolved template has a different mesh, the
   mesh swaps too, so the type change is visible. */
function applyBodyType(type){
  const r = bodyTypeToDNA(type, TEMPLATES);
  F.body.body_type = type;
  F.body.proportions = { ...DEFAULT_PROPS, ...r.proportions };
  let meshChanged = false;
  if(r.templateId){
    const t = TEMPLATES.find(x=>x.id===r.templateId);
    if(t && F.baseGlb !== t.base_mesh){ F.baseGlb = t.base_mesh; meshChanged = true; }
  }
  toast(`${type} ✓ (${r.basis})`);
  if(meshChanged) loadBaseModel(); else renderAll();
}
function renderBodyType(host){
  $('#panel-sub').textContent='Body type — 23 No Mercy types';
  host.innerHTML=`<div class="sect">BODY TYPE — 14M + 9F (No Mercy)</div><div class="roster-grid" id="btypes"></div>`;
  const bt=host.querySelector('#btypes');
  BODY_TYPES.forEach(t=>{ const b=document.createElement('button');
    b.className='roster-card'+(F.body.body_type===t?' active':''); b.textContent=t;
    tap(b, ()=>applyBodyType(t)); bt.appendChild(b); });
}
function renderBodySkin(host){
  $('#panel-sub').textContent='Skin tone — 8 tones';
  host.innerHTML=`<div class="sect">SKIN TONE — 8 tones</div><div class="swatches" id="stones"></div>`;
  const st=host.querySelector('#stones');
  SKIN_TONES.forEach(h=>{ const s=document.createElement('div');
    s.className='swatch'+(F.body.skin_tone===h?' active':''); s.style.background=h; s.title=h;
    tap(s, ()=>{ F.body.skin_tone=h; renderAll(); }); st.appendChild(s); });
}
function renderBodyProps(host){
  $('#panel-sub').textContent='Proportions — WMXIX parametric (live)';
  host.innerHTML=`<div class="sect">PROPORTIONS — WMXIX parametric (live)</div><div id="psl"></div>
    <div class="note">Height/weight scale the whole model; muscle, shoulders, chest,
    waist, hips, arms and legs morph it through the DNA engine (template-map).
    Every slider visibly changes the preview — these are not labels.</div>`;
  const sl=host.querySelector('#psl');
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
function renderBodyMorphMenu(host){
  $('#panel-sub').textContent='Morphs — Frame / Mass / Face Shape';
  host.innerHTML=`<div class="note">Real packages/creation-suite morph catalog,
    driven live through dna.js/body.js on the loaded model. Values save into
    this attire's customization record. Face values also record for the MPFB
    bake (shape keys are the ground truth).</div>` +
    [['morph-frame','💪','FRAME','Height, shoulders, limbs, neck, hands, feet'],
     ['morph-mass','🏋️','MASS','Bulk, weight, muscle, belly'],
     ['morph-face','😀','FACE SHAPE','Jaw, cheeks, brow, nose, eyes, mouth, chin']].map(([k,ico,lbl,note])=>
    `<button class="subcat" data-ms="${k}"><span class="sc-ico">${ico}</span><span>${lbl}<br><small style="color:var(--dim)">${note}</small></span></button>`).join('');
  host.querySelectorAll('[data-ms]').forEach(b=>tap(b, ()=>{ ui.bodySec=b.dataset.ms; renderPanel(); }));
}
function addMorphSlider(host, m){
  const v=(F.morphs && F.morphs[m.id])||0;
  const d=document.createElement('div'); d.className='ctl'; d.id='morph-'+m.id;
  d.innerHTML=`<label>${m.label}<span class="val">${v.toFixed(2)}</span></label>
    <input type="range" min="${m.range[0]}" max="${m.range[1]}" step="0.01" value="${v}" data-morph="${m.id}" aria-label="${m.label}">`;
  const inp=d.querySelector('input');
  inp.oninput=()=>{ F.morphs=F.morphs||{}; F.morphs[m.id]=+inp.value;
    d.querySelector('.val').textContent=(+inp.value).toFixed(2); syncMorphs(); persistQuiet(); };
  host.appendChild(d);
}
function renderBodyMorphList(host, kind){
  const title = { frame:'MORPHS — FRAME', mass:'MORPHS — MASS', face:'MORPHS — FACE SHAPE' }[kind];
  $('#panel-sub').textContent=title;
  host.innerHTML=`<div class="sect">${title} (packages morphs.js)</div><div id="mlist"></div>`;
  const h=host.querySelector('#mlist');
  if(kind==='face') FACE_SHAPE_MORPHS.forEach(m=>addMorphSlider(h, m));
  else if(kind==='frame') BODY_MORPHS.filter(m=>FRAME_IDS.includes(m.id)).forEach(m=>addMorphSlider(h, m));
  else BODY_MORPHS.filter(m=>!FRAME_IDS.includes(m.id)).forEach(m=>addMorphSlider(h, m));
}
function renderBodyFace(host){
  $('#panel-sub').textContent='Face — 12 presets (No Mercy + GNM)';
  if(!FACE_PRESETS.length){ host.innerHTML='<div class="note">Face presets failed to load (customization/templates/face-presets.json).</div>'; return; }
  const byLayer = l => FACE_PRESETS.filter(p=>p.layer===l);
  const card = p=>`<button class="subcat" data-fp="${esc(p.id)}"><span class="sc-ico">${p.layer==='wwe'?'🎭':'😀'}</span><span>${esc(p.name)}<br><small style="color:var(--dim)">${esc(p.desc||'')} · ${p.layer==='wwe' ? 'No Mercy face texture (bake)' : 'GNM expression (bake)'}${F.body.face_preset===p.id?' · ✓ selected':''}</small></span></button>`;
  host.innerHTML=`<div class="note">Tap a preset — it records into this attire (PROFILE →
    SAVE TO ATTIRE) for the face bake. No Mercy textures (146 in
    customization/parts/no-mercy/faces/) and GNM expressions bake through the
    pipeline (TOOLS tab); for a face change you can SEE right now, use
    MORPHS → FACE SHAPE, which morphs the live preview.</div>
    <div class="sect">NO MERCY FACES — wwe layer</div>${byLayer('wwe').map(card).join('')}
    <div class="sect">GNM EXPRESSIONS — gnm layer</div>${byLayer('gnm').map(card).join('')}
    <div class="btn-row"><button class="btn btn-blue" id="btn-face-shape">💪 SHAPE THE FACE (live morphs) →</button></div>`;
  host.querySelectorAll('[data-fp]').forEach(b=>tap(b, ()=>{
    F.body.face_preset=b.dataset.fp; renderPanel();
    toast(`Face preset: ${FACE_PRESETS.find(p=>p.id===b.dataset.fp)?.name||b.dataset.fp} ✓ (recorded for bake)`); }));
  tap(host.querySelector('#btn-face-shape'), ()=>{ ui.bodySec='morph-face'; renderPanel(); });
}


/* ================= TOOLS — tool-to-menu map (owner law 2026-10-22) =================
   Every open-source tool lives in the menu where it belongs. In-suite actions
   run in this page; pipeline actions run via the repo script shown — Blender
   and GPU jobs cannot run inside a browser page, so the entry shows its real
   path and status instead of a fake button. */
const TOOLS_MAP = [
  { icon:'🧱', name:'MPFB / MB-Lab', menu:'BODY → Templates + Morphs',
    what:'Parametric bodies. Template meshes are MB-Lab bakes; BODY morph sliders are the MPFB-derived morph ground truth (shape keys).',
    path:'customization/templates/ (meshes + specs)',
    status:'In-suite: templates + morphs live. Bake script tools/mb-lab/run_mblab_job.py is ABSENT from the repo (dir holds only .gitignore) — re-bake path is MPFB2 per templates README.',
    action:'Tap BODY → TEMPLATES or MORPHS.' },
  { icon:'👤', name:'Build-A-Bod', menu:'BODY → Templates',
    what:'SmutBase body builds pulled 2026-10-22. Template meshes derive from the same body family.',
    path:'customization/templates/meshes/',
    status:'In-suite via templates.',
    action:'Tap BODY → TEMPLATES.' },
  { icon:'🦴', name:'GameRig / NaughTyRig', menu:'All rigs (automatic)',
    what:'Auto-rigging for Tripo/custom models. In-suite, the rig adapter resolves every rig family to canonical bones so sockets, morphs and swaps work regardless of skeleton.',
    path:'packages/creation-suite/src/rig-adapter.js',
    status:'In-suite: rig adapter live on every model load (see CURRENT MODEL below).',
    action:'Load any model — sockets and morphs follow its own bones.' },
  { icon:'🎨', name:'Fluid Painter', menu:'BODY → Skin Tone + OUTFIT recolor',
    what:'Skin/texture painting (Blender add-on). In-suite, skin tones + per-part recolor apply live to the preview.',
    path:'Blender add-on (pipeline-side)',
    status:'In-suite: skin tone + recolor live. Full texture painting is a Blender-side job.',
    action:'BODY → SKIN TONE, OUTFIT → recolor.' },
  { icon:'😀', name:'Google GNM', menu:'BODY → Face',
    what:'Google Research Generative aNthropometric Model (Apache 2.0) — parametric head/face from 3D scans. GNM expression presets live in BODY → FACE; full head bakes run offline.',
    path:'tools/gnm/run_gnm_job.py',
    status:'In-suite: 4 GNM presets in FACE. Bake needs gated HuggingFace weights (google/gnm-3, license accept) + optional TensorFlow — cannot run in-browser.',
    action:'BODY → FACE → pick a GNM preset (recorded for bake).' },
  { icon:'📥', name:'Tripo intake / extraction', menu:'FIGHTER SELECT',
    what:'Tripo models are the user\'s own models FIRST on select (display-order law). Roster Tripo attires load as real GLBs through FIGHTER SELECT.',
    path:'roster/*/attires/ (Tripo models in-repo)',
    status:'In-suite via FIGHTER SELECT.',
    action:'FIGHTER SELECT → pick a fighter → attire.' },
  { icon:'📦', name:'gltfpack / glTF-Transform', menu:'EXPORT',
    what:'GLB optimization (meshopt). The suite EXPORT button writes the fighter JSON; gltfpack optimization of the GLB runs as a pipeline step (proven in studio-pipeline tests: stance GLBs −54% to −65%, stage −59%).',
    path:'tools/wh-asset-pipeline/ (studio-workflow PR payload, landing pending)',
    status:'Pipeline-side. Do NOT claim in-suite GLB optimization until that script lands in-repo.',
    action:'EXPORT writes fighter JSON now.' },
];
function renderTools(el){
  const rp = viewer && viewer.rigProfile;
  $('#panel-sub').textContent='Tool-to-menu map — every tool, where it lives, what it does here';
  el.innerHTML = `<div class="note">Owner law (2026-10-22): every open-source tool lives in the
    menu where it belongs. The suite is ONE system, not disconnected scripts.
    In-suite actions run in this page; pipeline actions run via the repo
    script shown (Blender/GPU jobs cannot run inside a browser page — the
    entry still belongs here, with its real path, not a fake button).</div>` +
    (rp ? `<div class="sect">CURRENT MODEL — RIG COMPATIBILITY</div>
      <div class="kv"><span>Bones in model</span><b>${rp.boneCount}</b></div>
      <div class="kv"><span>Canonical bones resolved</span><b>${rp.found} / ${rp.total}</b></div>
      <div class="kv"><span>Naming style</span><b>${esc(rp.namingStyles.join(', '))}</b></div>
      ${rp.missing.length ? `<div class="note">Not resolved on this rig (reported, not guessed):
      ${esc(rp.missing.join(', '))}. Morphs/sockets that need those bones fall back
      visibly instead of binding wrong.</div>` : `<div class="note">✓ All canonical bones resolve on this rig — morphing, sockets and part swaps work here.</div>`}` : '') +
    TOOLS_MAP.map(t=>`<div class="sect">${t.icon} ${t.name} → ${t.menu}</div>
      <div class="note">${t.what}<br><span class="chip">${esc(t.path)}</span><br>Status: <b>${esc(t.status)}</b><br>In-suite: ${esc(t.action)}</div>`).join('');
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
  tap(el.querySelector('#btn-back'), ()=>{ ui[backKey]=null; ui.selPart=null; ui.query=''; hidePlaceDock(); renderAll(); });
  const search=el.querySelector('#part-search');
  search.oninput=()=>{ ui.query=search.value; ui.page=0;
    const pos=search.selectionStart; renderPanel();
    const s2=document.querySelector('#part-search'); if(s2){ s2.focus(); s2.setSelectionRange(pos,pos); } };
  tap(el.querySelector('#pg-prev'), ()=>{ ui.page--; renderPanel(); });
  tap(el.querySelector('#pg-next'), ()=>{ ui.page++; renderPanel(); });
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
    tap(d, ()=>{ ui.selPart=p; renderPanel(); renderTopbar(); });
    grid.appendChild(d);
  });
  if(ui.selPart && list.includes(ui.selPart)) renderPartDetail(el.querySelector('#pdetail'), ui.selPart, slotKey);
}
/* WWE 2K19 layering (packages/creation-suite/src/layering.js): equipping a
   part unequips the parts it conflicts with (full body vs upper/lower).
   Conflicts match on suite_slot, because attire().equipped is keyed by T7
   slot. Registry spelling 'fullbody' is normalized to layering spelling
   'full_body'. Removed parts are named in the toast — never silently
   dropped. Coverage note: only parts carrying layering-vocabulary suite_slots
   trigger the suite_slot rule; the T7-slot rule below covers the rest. */
function equipWithConflicts(slotKey, p){
  const norm = s => (s === 'fullbody' ? 'full_body' : s);
  const conflicts = (p.suite_slot && SLOT_CONFLICTS[norm(p.suite_slot)]) || [];
  const removed = [];
  const pushRemoved = n => { if(!removed.includes(n)) removed.push(n); };
  if(conflicts.length){
    for(const [k, pid] of Object.entries(attire().equipped)){
      if(k===slotKey) continue;
      const other = PARTS.find(x=>x.id===pid);
      if(other && conflicts.includes(norm(other.suite_slot))){ delete attire().equipped[k]; pushRemoved(other.name||pid); }
    }
  }
  /* T7 zone conflicts (MENU_SRC T7_CONFLICTS: FULL_BODY vs UPPER/LOWER):
     T7 slots 9 = Upper Body, 10 = Full Body, 11 = Lower Body. */
  const t7Conflicts = slotKey==='10' ? ['9','11'] : (slotKey==='9'||slotKey==='11' ? ['10'] : []);
  for(const k of t7Conflicts){
    const pid = attire().equipped[k];
    if(pid){ const other = PARTS.find(x=>x.id===pid); delete attire().equipped[k]; pushRemoved((other&&other.name)||pid); }
  }
  attire().equipped[slotKey]=p.id;
  return removed;
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
      tap(b, ()=>{ const removed=equipWithConflicts(slotKey,p); renderAll();
        toast('Recorded ✓ — geometry pending'+(removed.length?` · unequipped (layer conflict): ${removed.join(', ')}`:'')); });
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
      tap(b, ()=>{ if(!owned){ if(F.wallet<500){ modal('NOT ENOUGH FIGHT MONEY','<p>Need <b>500G</b>.</p>',[{label:'OK',cls:'btn-gold'}]); return; }
          F.wallet-=500; attire().owned.push(p.id); }
        const removed=equipWithConflicts(slotKey,p);
        if(!attire().placements[p.id]){ const def=PARTS.find(x=>x.id===p.id); attire().placements[p.id]=defaultPlacement(def||{}); }
        renderAll(); showPlaceDock(p);
        toast('Equipped ✓ — nudge it into place'+(removed.length?` · unequipped (layer conflict): ${removed.join(', ')}`:'')); });
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
    tap(b, ()=>{ const removed=equipWithConflicts(slotKey,p); renderAll();
      toast('Applied ✓'+(removed.length?` · unequipped (layer conflict): ${removed.join(', ')}`:'')); });
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

/* ---------- roster / save / export ---------- */
/* FIGHTER SELECT, drill-down (user 2026-10-24 19:45 CDT: taps did nothing).
   The old modal appended the attire grid BELOW the fighter grid inside a
   50vh scroll box, so tapping a fighter looked like nothing happened. Now
   tapping a fighter REPLACES the grid with that fighter's attire grid + a
   BACK button + scroll-to-top — one level visible at a time, like the
   ATTIRE/PARTS drill-downs. Cards use tap(), not click-only. */
function showRosterFighters(){
  if(!ROSTER){ modal('FIGHTER SELECT','<p>Roster data (data/roster-attires.json) failed to load.</p>',[{label:'CLOSE',cls:'btn-gold'}]); return; }
  const fighters = ROSTER.fighters.map(f=>
    `<button class="roster-card${F.rosterRef&&F.rosterRef.fighter===f.fighter?' active':''}" data-f="${esc(f.fighter)}">${esc(f.fighter_name)}<br><small style="color:var(--dim)">${f.attires.length} attire${f.attires.length===1?'':'s'}</small></button>`).join('');
  modal('FIGHTER SELECT',`<div class="sect">EDIT FIGHTER — pick fighter, then attire (UNIFIED-UI-SPEC §2)</div>
    <div class="roster-grid"><button class="roster-card${F.mode==='blank'?' active':''}" data-f="">🧍 NEW FIGHTER<br><small style="color:var(--dim)">Technician — blank CAW canvas (No Mercy Medium 1)</small></button>${fighters}</div>
    <div class="note">Entry flow (verbatim T7): pick fighter → pick attire slot → customize. Selecting loads that attire's real GLB. Blank-fighter mode stays intact.</div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  document.querySelectorAll('#modal [data-f]').forEach(b=>tap(b, ()=>{
    const slug=b.dataset.f;
    if(!slug){ closeModal(); selectRosterAttire(null); return; }
    showRosterAttires(slug);
  }));
}
function showRosterAttires(slug){
  const rf=rosterFighter(slug); if(!rf) return;
  modal('FIGHTER SELECT — '+rf.fighter_name.toUpperCase(),`<div class="back-row"><button class="btn back-btn" id="btn-roster-back">← FIGHTERS</button></div>
    <div class="sect">${esc(rf.fighter_name).toUpperCase()} — ATTIRE</div><div class="roster-grid">${
      rf.attires.map(a=>`<button class="roster-card" data-a="${esc(a.attire_id)}">${esc(a.attire_name)}<br><small style="color:var(--dim)">${esc(a.glb.split('/').pop())}</small></button>`).join('')}</div>`,
    [{label:'CLOSE',cls:'btn-gold'}]);
  tap(document.querySelector('#btn-roster-back'), showRosterFighters);
  document.querySelectorAll('#modal [data-a]').forEach(ab=>tap(ab, ()=>{ closeModal(); selectRosterAttire(slug, ab.dataset.a); }));
  const mb=document.querySelector('#modal-body'); if(mb) mb.scrollTop=0;
}
tap($('#btn-roster'), showRosterFighters);
tap($('#btn-save'), persist);
{ const bsa=$('#btn-save-attire'); if(bsa) tap(bsa, saveToAttire); }
/* Stream 4: in-game wiring — back to the game menu (saves first). */
{ const bg=$('#btn-back-game'); if(bg) tap(bg, ()=>{ persistQuiet(); window.location.href='../../index.html'; }); }
tap($('#btn-export'), ()=>{
  const blob=new Blob([JSON.stringify(F,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='creation-suite-fighter.json'; a.click(); URL.revokeObjectURL(a.href); toast('Exported ✓');
});

/* ---------- boot ---------- */
async function boot(){
  try{ const s=localStorage.getItem(LS_KEY); if(s) F=Object.assign(blankFighter(), JSON.parse(s)); }catch(e){}
  /* Mixamo removal migration: saved states pointing at Soldier.glb now load
     the Technician blank CAW base instead (user: fully take him out). */
  if(F.baseGlb && /soldier/i.test(F.baseGlb)) F.baseGlb = BLANK_GLB;
  try{
    const [parts, jig, roster, fparts, tpl, face] = await Promise.all([
      fetch('data/parts-catalog.json').then(r=>r.json()),
      fetch('data/jiggle-schema.json').then(r=>r.json()),
      fetch('data/roster-attires.json').then(r=>r.ok?r.json():null).catch(()=>null),
      fetch('data/fighter-parts.json').then(r=>r.ok?r.json():null).catch(()=>null),
      /* Templates + face presets were NEVER loaded (the unwired gap behind
         the user's "templates not hooked up" complaint) — now they are. */
      fetch('../templates/body-templates.json').then(r=>r.ok?r.json():null).catch(()=>null),
      fetch('../templates/face-presets.json').then(r=>r.ok?r.json():null).catch(()=>null),
    ]);
    PARTS = Array.isArray(parts) ? parts : (parts.parts||[]);
    PARTS_META = Array.isArray(parts) ? null : parts;
    // normalize legacy curated entries (pre-unified catalogs) to the v2 shape
    PARTS.forEach(p=>{ if(!p.asset) p.asset=p.glb||null; if(!p.source) p.source=p.library||'curated';
      if(!p.t7_slot) p.t7_slot=SLOT2CAT[p.suite_slot]||null;
      if(p.geometry_pending===undefined) p.geometry_pending=!!p.geometryPending; });
    JIGGLE=jig; ROSTER=roster; FPARTS=fparts;
    TEMPLATES = (tpl && tpl.templates) || [];
    FACE_PRESETS = (face && face.presets) || [];
  }catch(e){
    $('#loader').innerHTML='<div>DATA LOAD FAILED — serve over http</div>'; return;
  }
  if(!Array.isArray(F.records)) F.records = F.records||{};
  if(F.mode==='roster' && (!F.rosterRef || !rosterAttire(F.rosterRef.fighter, F.rosterRef.attire))){ F.mode='blank'; F.rosterRef=null; F.baseGlb=BLANK_GLB; }
  viewer=new SuiteViewer($('#stage3d'));
  window.__suite={ viewer, get F(){return F;}, ui, setTab, selectRosterAttire, customizationRecord, currentKey, get ROSTER(){return ROSTER;}, get PARTS(){return PARTS;}, get FPARTS(){return FPARTS;}, get TEMPLATES(){return TEMPLATES;}, get FACE_PRESETS(){return FACE_PRESETS;} };
  viewer.onReady=()=>{ renderAll(); };
  await loadBaseModel();
  renderAll();
  $('#loader').classList.add('done');
  $('#src-note').textContent='Menus: T7 slots verbatim · WWE 2K CAW flows · No Mercy/WMXIX/DOA — see UI-EXTRACTION-LOG.md';
  if(!localStorage.getItem(LS_KEY)) toast('Tap PARTS → Masks → tap the mask to equip it');
}
boot();
