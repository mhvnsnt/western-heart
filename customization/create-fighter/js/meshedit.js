/* meshedit.js — in-suite hand-tooling UI ("MODEL EDIT" mode), worker 66, 2026-10-22.
   Owner directive: "make it where I can do the hand-tooling part IN the character creation
   suite — where I don't have to actually use Blender, but Blender's just hooked up in the
   character creation suite."

   Architecture (see docs/decisions/2026-10-22-W66-mesh-edit-architecture.md):
   - Layer 1 (instant, in-browser): an edit MANIFEST per fighter — hide/show (visibility),
     soft-delete, staged transforms. Applied live to the three.js scene, fully reversible.
   - Layer 2 (baked, server-side): Blender jobs through the EXISTING suite job queue
     (tools/suite-jobs/server.py, tool 'mesh-edit' → tools/mesh-edit/run_mesh-edit_job.py) —
     hard delete, baked transforms, duplicate, part import (interchange/add), sculpt,
     remodel. The JOBS tab already renders these jobs; results load via its LOAD GLB button.

   Touch-first: tap-to-select (raycast, pointer events), big gizmo-mode buttons, numeric
   nudge sliders as the precision path (fat-finger-safe; Prisma3D-style vocabulary).
   Gizmo = three.js TransformControls, lazy-imported from the vendored addons dir so the
   suite still loads when it is not vendored yet (falls back to numeric nudge).

   Integration: registered in js/tools.js (layer 1 UNIFIED_SYSTEMS 'model-edit-system' +
   layer 2 per-op menus). Menu home: Appearance → Attire Parts → MODEL EDIT (hand-tooling)
   submenu of the WWE flow (worker 65's blueprint owns the tree; this module owns the mode).
   Mesh labels resolve through worker 64's taxonomy when present, else raw GLB node names.
*/
import * as THREE from 'three';

/* The suite already has a job server (tools/suite-jobs/server.py, port 8766) owned by
   the creation-flow module's JOBS tab — this module submits to THAT server, never a
   parallel one (TOOL UNIFICATION LAW). Spec shape: {tool:'mesh-edit', params:{...}, out}. */
const SERVER_URL = () =>
  (window.WH_MESHEDIT_URL) || 'http://127.0.0.1:8766';
const GIZMO_URL = './vendor/addons/controls/TransformControls.js';

/* ---------------- edit manifest (suite-side, reversible) ---------------- */
export function newManifest(fighter, attire){
  return { app:'wh-model-edit', version:1, fighter, attire: attire||'attire1',
    hidden:[], deleted:[], transforms:{}, baked:[] };
}
function applyManifest(preview, manifest){
  preview.scene.traverse(o=>{
    if(!o.isMesh) return;
    const t = manifest.transforms[o.name];
    o.visible = !(manifest.hidden.includes(o.name) || manifest.deleted.includes(o.name));
    if(t){
      o.position.set(...(t.translate||[0,0,0]));
      o.rotation.set(...(t.rotate_euler||[0,0,0]));
      o.scale.set(...(t.scale||[1,1,1]));
    } else { o.position.set(0,0,0); o.rotation.set(0,0,0); o.scale.set(1,1,1); }
  });
}

/* ---------------- job client (existing suite-jobs server API) ---------------- */
async function serverTools(){
  try{
    const r = await fetch(`${SERVER_URL()}/tools`, { signal: AbortSignal.timeout(2500) });
    if(r.ok) return await r.json();
  }catch(e){ /* unreachable */ }
  return null;
}
function meshEditRunnable(tools){
  const t = (tools||[]).find(t=>t.tool==='mesh-edit');
  return t ? t.runnable : false;
}
async function submitJob(spec){
  const r = await fetch(`${SERVER_URL()}/jobs`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(spec) });
  const j = await r.json();
  if(!r.ok || !j.id) throw new Error('job rejected: ' + (j.error || r.status));
  return j.id;
}
async function pollJob(id, onTick){
  for(let i=0;i<240;i++){
    await new Promise(r=>setTimeout(r, 2000));
    const r = await fetch(`${SERVER_URL()}/jobs/${id}`);
    if(!r.ok) throw new Error('job poll failed');
    const rec = await r.json();
    onTick && onTick(rec);
    if(rec.state==='done'||rec.state==='error') return rec;
  }
  throw new Error('job timed out waiting');
}
export function downloadJobSpec(spec){
  const blob = new Blob([JSON.stringify(spec,null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `meshedit-${spec.params?.fighter||'job'}-${Date.now()}.json`;
  a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 5000);
}

/* ---------------- the mode ---------------- */
export class MeshEditMode {
  constructor(ctx, preview){
    this.ctx = ctx; this.preview = preview;
    this.manifest = newManifest(ctx.F?.profile?.name || 'custom', 'attire1');
    this.selected = null; this.gizmo = null; this.gizmoMode = 'translate';
    this.meshes = []; this.panel = null; this._ray = new THREE.Raycaster();
    this._ptr = new THREE.Vector2(); this._downAt = 0; this._downXY = null;
    this._onPointerDown = this._onPointerDown.bind(this);
    this._onPointerUp = this._onPointerUp.bind(this);
    // Capture-phase guard: while the gizmo is being dragged, swallow the event
    // before preview3d's own (bubble-phase) orbit handlers see it — no edits to
    // preview3d.js needed.
    this._onPointerCapture = (e)=>{ if(this._gizmoDragging) e.stopImmediatePropagation(); };
    this._gizmoDragging = false;
    this._sculptPick = false;
  }

  inventory(){
    const out = [];
    this.preview.scene.traverse(o=>{
      if(o.isMesh && !o.userData.isGizmo && !o.userData.isProxy){
        const label = (window.__whMeshTaxonomy && window.__whMeshTaxonomy[o.name]) || o.name;
        out.push({ name:o.name, label,
          verts: o.geometry?.attributes?.position?.count ?? 0,
          hidden: this.manifest.hidden.includes(o.name) });
      }
    });
    this.meshes = out;
    return out;
  }

  async enter(){
    this.preview.autoRotate = false;
    this.inventory(); applyManifest(this.preview, this.manifest);
    this._buildPanel();
    const cv = this.preview.canvas;
    cv.addEventListener('pointerdown', this._onPointerCapture, true);
    cv.addEventListener('pointermove', this._onPointerCapture, true);
    cv.addEventListener('pointerdown', this._onPointerDown);
    cv.addEventListener('pointerup', this._onPointerUp);
    try{
      const { TransformControls } = await import(GIZMO_URL);
      this.gizmo = new TransformControls(this.preview.camera, this.preview.canvas);
      this.gizmo.setMode(this.gizmoMode);
      // fat-finger help: bigger handles on touch devices
      if('ontouchstart' in window && this.gizmo.setSize) this.gizmo.setSize(1.35);
      this.gizmo.addEventListener('dragging-changed', e=>{ this._gizmoDragging = !!e.value; });
      this.gizmo.addEventListener('objectChange', ()=>this._stageGizmoTransform());
      this.preview.scene.add(this.gizmo);
    }catch(e){
      this.gizmo = null; // numeric-nudge fallback (panel sliders)
      this._note('Gizmo module not vendored yet — numeric nudge active.');
    }
    this._renderList();
    this.ctx.toast && this.ctx.toast('MODEL EDIT on — tap a mesh, then move/scale/hide it.');
  }

  exit(){
    if(this.gizmo){ this.preview.scene.remove(this.gizmo); this.gizmo.dispose(); this.gizmo=null; }
    const cv = this.preview.canvas;
    cv.removeEventListener('pointerdown', this._onPointerCapture, true);
    cv.removeEventListener('pointermove', this._onPointerCapture, true);
    cv.removeEventListener('pointerdown', this._onPointerDown);
    cv.removeEventListener('pointerup', this._onPointerUp);
    this.panel && this.panel.remove(); this.panel = null;
    this.selected = null;
    this.preview.autoRotate = true;
  }

  /* ----- selection (tap, touch-safe) ----- */
  _onPointerDown(e){ this._downAt = Date.now(); this._downXY = [e.clientX, e.clientY]; }
  _onPointerUp(e){
    if(!this._downXY) return;
    const moved = Math.hypot(e.clientX-this._downXY[0], e.clientY-this._downXY[1]);
    const dt = Date.now()-this._downAt; this._downXY = null;
    if(moved > 12 || dt > 600) return; // it was a drag/orbit, not a tap
    if(this._sculptPick){ this._pickSculptCenter(e); return; }
    const r = this.preview.canvas.getBoundingClientRect();
    this._ptr.set(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
    this._ray.setFromCamera(this._ptr, this.preview.camera);
    const hits = this._ray.intersectObjects(
      this.meshes.map(m=>this.preview.scene.getObjectByName(m.name)).filter(Boolean), false);
    this.select(hits.length ? hits[0].object.name : null);
  }
  select(name){
    this.selected = name;
    if(this.gizmo){
      if(name){ const o = this.preview.scene.getObjectByName(name); o && this.gizmo.attach(o); }
      else this.gizmo.detach();
    }
    this._renderList(); this._renderNudge();
  }

  _stageGizmoTransform(){
    if(!this.selected || !this.gizmo) return;
    const o = this.gizmo.object; if(!o) return;
    this.manifest.transforms[this.selected] = {
      translate:[o.position.x,o.position.y,o.position.z],
      rotate_euler:[o.rotation.x,o.rotation.y,o.rotation.z],
      scale:[o.scale.x,o.scale.y,o.scale.z] };
    this._renderNudge();
  }

  /* ----- manifest ops (instant, reversible) ----- */
  hideSelected(){ if(!this.selected) return;
    this._push('hidden', this.selected); applyManifest(this.preview,this.manifest); this._renderList(); }
  showSelected(){ if(!this.selected) return;
    this.manifest.hidden = this.manifest.hidden.filter(m=>m!==this.selected);
    applyManifest(this.preview,this.manifest); this._renderList(); }
  showAll(){ this.manifest.hidden = []; applyManifest(this.preview,this.manifest); this._renderList(); }
  softDelete(){ if(!this.selected) return;
    this._push('deleted', this.selected); applyManifest(this.preview,this.manifest);
    this.ctx.toast && this.ctx.toast('Soft-deleted (reversible). BAKE to hard-delete via Blender.');
    this.select(null); }
  undo(){ // drop the last staged change of any kind
    const m = this.manifest;
    const tk = Object.keys(m.transforms);
    if(tk.length){ delete m.transforms[tk[tk.length-1]]; }
    else if(m.deleted.length){ m.deleted.pop(); }
    else if(m.hidden.length){ m.hidden.pop(); }
    applyManifest(this.preview,m); this._renderList();
  }
  resetAll(){ this.manifest = newManifest(this.manifest.fighter, this.manifest.attire);
    applyManifest(this.preview,this.manifest); this.select(null); }
  _push(k, v){ if(!this.manifest[k].includes(v)) this.manifest[k].push(v); }

  /* ----- Blender-baked ops (existing suite-jobs queue) ----- */
  _baseJob(ops){
    const stamp = Date.now();
    const out_glb = `customization/edit-output/${this.manifest.fighter}-edit-${stamp}.glb`;
    return { tool:'mesh-edit',
      params: { fighter:this.manifest.fighter, attire:this.manifest.attire,
        source_glb: this.preview.modelUrl || '<fighter>.glb',
        ops,
        out_glb,
        out_report: `customization/edit-output/${this.manifest.fighter}-edit-${stamp}.report.json`,
        reweight:'auto' },
      out: out_glb };
  }
  async _runJob(ops, label){
    const spec = this._baseJob(ops);
    const tools = await serverTools();
    if(!tools || !meshEditRunnable(tools)){
      downloadJobSpec(spec);
      this._note('Job server unreachable or mesh-edit not runnable — spec downloaded for the crew. ' +
        'Start it: python3 tools/suite-jobs/server.py (Blender via tools/setup/setup_toolchain.sh).');
      return;
    }
    this._note(`${label} — queued…`);
    try{
      const id = await submitJob(spec);
      this._note(`${label} — running (job ${id})…`);
      const rec = await pollJob(id, r=>this._note(`${label} — ${r.state}…`));
      if(rec.state==='done'){
        this.manifest.baked.push(id);
        this._note(`${label} done ✓ — see JOBS tab for the log; LOAD GLB IN PREVIEW there.`);
        this.ctx.toast && this.ctx.toast(`${label} baked ✓ — JOBS tab has the result`);
      } else {
        this._note(`${label} FAILED — ${(rec.error||'see JOBS tab log').toString().slice(0,160)}`);
      }
    }catch(e){ this._note(`${label} error: ${e.message}`); }
  }
  bakeDelete(){ if(!this.selected) return;
    this._runJob([{op:'mesh_delete', mesh:this.selected}], 'Hard delete'); }
  bakeTransform(){ if(!this.selected) return;
    const t = this.manifest.transforms[this.selected];
    if(!t){ this._note('No staged transform — drag the gizmo or nudge first.'); return; }
    this._runJob([{op:'mesh_transform', mesh:this.selected, ...t}], 'Bake transform'); }
  duplicate(mirror){ if(!this.selected) return;
    this._runJob([{op:'mesh_duplicate', mesh:this.selected, mirror_x:!!mirror}], 'Duplicate'); }
  importPart(donor, socket, scaleToBone){ if(!donor) return;
    this._runJob([{op:'part_import', donor, socket, fit:{scale_to_bone:!!scaleToBone}}], 'Import part'); }
  sculpt(strokes){ if(!this.selected || !strokes.length) return;
    this._runJob([{op:'mesh_sculpt', mesh:this.selected, strokes}], 'Sculpt'); }
  remodel(spec){ if(!this.selected) return;
    this._runJob([{op:'mesh_remodel', mesh:this.selected, spec}], 'Remodel'); }

  _pickSculptCenter(e){
    const r = this.preview.canvas.getBoundingClientRect();
    this._ptr.set(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
    this._ray.setFromCamera(this._ptr, this.preview.camera);
    const o = this.preview.scene.getObjectByName(this.selected);
    const hits = o ? this._ray.intersectObject(o, false) : [];
    if(hits.length){
      const p = o.worldToLocal(hits[0].point.clone());
      this._sculptCenter = [p.x,p.y,p.z];
      this._note(`Sculpt center set (${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)}). Set brush, then SCULPT.`);
    }
    this._sculptPick = false;
  }

  /* ----- panel UI (touch-first) ----- */
  _buildPanel(){
    const p = document.createElement('div');
    p.id = 'meshedit-panel';
    p.innerHTML = `
      <div class="me-head"><b>🛠️ MODEL EDIT</b>
        <span id="me-note" class="me-note"></span>
        <button class="btn" id="me-exit">✕</button></div>
      <div class="me-row" id="me-modes">
        <button class="btn" data-m="translate">↔ MOVE</button>
        <button class="btn" data-m="rotate">⟳ ROTATE</button>
        <button class="btn" data-m="scale">⤢ SCALE</button>
      </div>
      <div class="me-row" id="me-list"></div>
      <div class="me-row" id="me-nudge"></div>
      <div class="me-row">
        <button class="btn" id="me-hide">🙈 HIDE</button>
        <button class="btn" id="me-show">👁 SHOW</button>
        <button class="btn" id="me-showall">👁 ALL</button>
        <button class="btn" id="me-del">🗑 DELETE</button>
      </div>
      <div class="me-row">
        <button class="btn" id="me-baket">⬇ BAKE MOVE</button>
        <button class="btn" id="me-bakedel">⬇ BAKE DELETE</button>
        <button class="btn" id="me-dupe">⧉ DUPLICATE</button>
        <button class="btn" id="me-mirror">⧉ MIRROR</button>
      </div>
      <div class="me-row">
        <button class="btn" id="me-pick">🎯 PICK SCULPT POINT</button>
        <select id="me-brush"><option value="smooth">smooth</option><option value="grab">grab</option><option value="inflate">inflate</option><option value="pinch">pinch</option></select>
        <button class="btn" id="me-sculpt">🖌 SCULPT</button>
      </div>
      <div class="me-row">
        <input id="me-donor" placeholder="donor library:id or GLB url" style="flex:1">
        <button class="btn" id="me-import">📥 IMPORT PART</button>
      </div>
      <div class="me-row">
        <button class="btn" id="me-undo">↩ UNDO</button>
        <button class="btn" id="me-reset">♻ RESET ALL</button>
      </div>`;
    document.body.appendChild(p);
    this.panel = p;
    const q = s=>p.querySelector(s);
    q('#me-exit').onclick = ()=>this.exit();
    q('#me-modes').querySelectorAll('button').forEach(b=>b.onclick=()=>{
      this.gizmoMode = b.dataset.m;
      if(this.gizmo) this.gizmo.setMode(this.gizmoMode);
      this.ctx.toast && this.ctx.toast('Gizmo: '+this.gizmoMode);
    });
    q('#me-hide').onclick = ()=>this.hideSelected();
    q('#me-show').onclick = ()=>this.showSelected();
    q('#me-showall').onclick = ()=>this.showAll();
    q('#me-del').onclick = ()=>this.softDelete();
    q('#me-baket').onclick = ()=>this.bakeTransform();
    q('#me-bakedel').onclick = ()=>this.bakeDelete();
    q('#me-dupe').onclick = ()=>this.duplicate(false);
    q('#me-mirror').onclick = ()=>this.duplicate(true);
    q('#me-pick').onclick = ()=>{ this._sculptPick = true; this._note('Tap the mesh to set the sculpt center.'); };
    q('#me-sculpt').onclick = ()=>{
      if(!this._sculptCenter){ this._note('Pick a sculpt point first (🎯).'); return; }
      this.sculpt([{ brush:q('#me-brush').value, strength:0.4, radius:0.05, center:this._sculptCenter }]);
    };
    q('#me-import').onclick = ()=>this.importPart(q('#me-donor').value.trim(), null, true);
    q('#me-undo').onclick = ()=>this.undo();
    q('#me-reset').onclick = ()=>this.resetAll();
  }
  _note(t){ const n = this.panel && this.panel.querySelector('#me-note'); if(n) n.textContent = t; }
  _renderList(){
    const host = this.panel && this.panel.querySelector('#me-list'); if(!host) return;
    host.innerHTML = '';
    this.meshes.forEach(m=>{
      const b = document.createElement('button');
      b.className = 'btn' + (m.name===this.selected ? ' btn-gold' : '');
      b.textContent = `${m.hidden?'🙈 ':''}${m.label} (${m.verts})`;
      b.onclick = ()=>this.select(m.name);
      host.appendChild(b);
    });
  }
  _renderNudge(){
    const host = this.panel && this.panel.querySelector('#me-nudge'); if(!host) return;
    host.innerHTML = '';
    if(!this.selected){ host.innerHTML = '<span class="me-note">Select a mesh to nudge it.</span>'; return; }
    const o = this.preview.scene.getObjectByName(this.selected);
    if(!o) return;
    const mk = (label, get, set)=>{
      const w = document.createElement('div'); w.className='me-nudge';
      w.innerHTML = `<span>${label}</span>`;
      const s = document.createElement('input');
      s.type='range'; s.min='-1'; s.max='1'; s.step='0.01'; s.value='0';
      s.style.flex='1';
      s.oninput = ()=>{ set(parseFloat(s.value)); };
      s.onchange = ()=>{ s.value='0'; this._stageGizmoTransform(); };
      w.appendChild(s); host.appendChild(w);
    };
    const px=o.position.x, py=o.position.y, pz=o.position.z;
    mk('X', null, v=>o.position.set(px+v, o.position.y, o.position.z));
    mk('Y', null, v=>o.position.set(o.position.x, py+v, o.position.z));
    mk('Z', null, v=>o.position.set(o.position.x, o.position.y, pz+v));
    const note = document.createElement('div');
    note.className='me-note'; note.textContent='Nudge = staged in manifest (reversible). BAKE MOVE sends it to Blender.';
    host.appendChild(note);
  }
}

/* singleton entry used by the TOOLS tab unified action */
let active = null;
export function enterMeshEdit(ctx, preview){
  preview = preview || (window.__suite && window.__suite.preview) || null;
  if(!preview){ (ctx.toast||alert)('3D preview not ready — open the suite viewport first.'); return null; }
  if(active) active.exit();
  active = new MeshEditMode(ctx, preview);
  active.enter();
  return active;
}
export function exitMeshEdit(){ if(active){ active.exit(); active = null; } }
