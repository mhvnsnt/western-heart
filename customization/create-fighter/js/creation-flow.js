/* creation-flow.js — Create New Fighter journey (owner 2026-10-22).
 *
 * 1. TEMPLATE SELECT screen FIRST (WWE 2K style): division tabs -> template
 *    cards from customization/templates/body-templates.json -> pick one.
 *    The Mixamo soldier is dead; the base model comes from the template's
 *    base_mesh (MB-Lab bake).
 * 2. WWE STEP WIZARD: the No Mercy Edit-a-Superstar sequence as a step bar
 *    over the real tab panels (body -> face -> skin -> hair -> facial hair
 *    -> attire -> profile -> moveset -> done). No duplicated panels.
 * 3. JOBS panel: Blender-backed tools (MB-Lab generate, GNM head bake,
 *    gltfpack optimize, ...) submit real jobs to tools/suite-jobs/server.py
 *    and poll live status. No dead buttons.
 *
 * Talks to window.__suite (exposed by app.js). Registers window.__flow.
 */
(function(){
'use strict';
const S = ()=>window.__suite;
const esc = s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ============================== styles ============================== */
const CSS = `
#tmpl-overlay{position:fixed;inset:0;z-index:60;display:flex;flex-direction:column;
  background:radial-gradient(1200px 700px at 50% 20%,#1c2740 0%,#0a0e16 70%);color:#eef;}
#tmpl-overlay[hidden]{display:none;}
.tmpl-head{padding:18px 26px 8px;display:flex;align-items:baseline;gap:18px;}
.tmpl-head h1{margin:0;font-size:26px;letter-spacing:2px;}
.tmpl-head .sub{color:#8fa0c0;font-size:13px;}
.tmpl-divs{display:flex;gap:10px;padding:10px 26px;}
.tmpl-div{padding:8px 18px;border:1px solid #33415f;border-radius:20px;background:#141b2c;
  color:#cfe0ff;cursor:pointer;font-size:14px;}
.tmpl-div.active{background:#d8a93f;border-color:#d8a93f;color:#111;font-weight:700;}
.tmpl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
  gap:14px;padding:14px 26px;overflow-y:auto;}
.tmpl-card{background:#141b2cf2;border:1px solid #2c3a58;border-radius:12px;padding:14px;
  cursor:pointer;transition:transform .12s,border-color .12s;}
.tmpl-card:hover{transform:translateY(-3px);border-color:#d8a93f;}
.tmpl-card .swatch{height:74px;border-radius:8px;margin-bottom:10px;
  display:flex;align-items:flex-end;justify-content:center;}
.tmpl-card .swatch span{font-size:34px;filter:drop-shadow(0 2px 4px #000a);}
.tmpl-card h3{margin:0 0 4px;font-size:17px;}
.tmpl-card .meta{font-size:11px;color:#8fa0c0;margin-bottom:6px;}
.tmpl-card p{font-size:12.5px;color:#b9c6de;margin:0 0 8px;min-height:34px;}
.tmpl-card .src{font-size:10.5px;color:#6b7c9c;}
.tmpl-note{padding:8px 26px 18px;color:#6b7c9c;font-size:12px;}
#wizard-bar{position:fixed;left:50%;transform:translateX(-50%);bottom:54px;z-index:55;
  display:flex;align-items:center;gap:8px;background:#101623ee;border:1px solid #2c3a58;
  border-radius:24px;padding:8px 12px;color:#dfe8fa;}
#wizard-bar[hidden]{display:none;}
.wz-step{width:26px;height:26px;border-radius:50%;border:1px solid #3a4a6c;background:#182036;
  color:#9fb2d8;font-size:11px;cursor:pointer;}
.wz-step.done{background:#2c5f3a;border-color:#2c5f3a;color:#fff;}
.wz-step.cur{background:#d8a93f;border-color:#d8a93f;color:#111;font-weight:700;}
.wz-label{font-size:12px;min-width:150px;text-align:center;}
.wz-btn{background:#1d2942;border:1px solid #3a4a6c;color:#dfe8fa;border-radius:16px;
  padding:6px 14px;cursor:pointer;font-size:12.5px;}
.wz-btn.primary{background:#d8a93f;border-color:#d8a93f;color:#111;font-weight:700;}
.job-row{display:flex;gap:8px;align-items:center;padding:8px;border:1px solid #2c3a58;
  border-radius:8px;margin-bottom:8px;background:#141b2c;}
.job-row .st{font-size:11px;padding:2px 8px;border-radius:10px;background:#333;}
.job-row .st.done{background:#2c5f3a;} .job-row .st.error{background:#7a2c2c;}
.job-row .st.running{background:#2c4a7a;} .job-row .st.queued{background:#555;}
`;
const st = document.createElement('style'); st.textContent = CSS;
document.head.appendChild(st);

/* ============================== template select ============================== */
const DIVISIONS = ['Heavyweight','Cruiserweight',"Women's"];
let tmplDiv = DIVISIONS[0];

function ensureOverlay(){
  let ov = document.getElementById('tmpl-overlay');
  if(ov) return ov;
  ov = document.createElement('div');
  ov.id = 'tmpl-overlay'; ov.hidden = true;
  ov.innerHTML = `
    <div class="tmpl-head"><h1>CHOOSE YOUR BASE</h1>
      <span class="sub">WWE-style templates — pulled from the teardown CAW library, baked parametric. Pick one to start.</span></div>
    <div class="tmpl-divs" id="tmpl-divs"></div>
    <div class="tmpl-grid" id="tmpl-grid"></div>
    <div class="tmpl-note">Base meshes baked from these specs by MB-Lab (headless Blender 4.0.2) — re-bake any of them 1:1 with
      <span style="font-family:monospace">tools/mb-lab/run_mblab_job.py</span>. New templates drop into
      <span style="font-family:monospace">customization/templates/body-templates.json</span> — no code changes.</div>`;
  document.body.appendChild(ov);
  return ov;
}

function renderTemplateGrid(){
  const s = S(); if(!s) return;
  const divs = document.getElementById('tmpl-divs');
  divs.innerHTML = '';
  DIVISIONS.forEach(d=>{
    const b = document.createElement('button');
    b.className = 'tmpl-div' + (d===tmplDiv?' active':'');
    b.textContent = d.toUpperCase();
    b.onclick = ()=>{ tmplDiv = d; renderTemplateGrid(); };
    divs.appendChild(b);
  });
  const grid = document.getElementById('tmpl-grid');
  grid.innerHTML = '';
  const list = (s.TEMPLATES.body||[]).filter(t=>t.division===tmplDiv);
  const faces = s.TEMPLATES.faces||[];
  list.forEach(t=>{
    const card = document.createElement('div');
    card.className = 'tmpl-card';
    const wweFace = faces.find(f=>f.gender===(t.gender==='female'?'female':'male')&&f.layer==='wwe');
    card.innerHTML = `
      <div class="swatch" style="background:linear-gradient(135deg,${t.skin_tone},#1a2233)">
        <span>${t.gender==='female'?'🤼‍♀️':'🤼'}</span></div>
      <h3>${esc(t.name)}</h3>
      <div class="meta">${esc(t.division)} · ${esc(t.body_type)} · ${esc(t.skin_tone)}</div>
      <p>${esc(t.desc)}</p>
      <div class="src">src: ${esc(t.source||'')} · face: ${esc(wweFace?wweFace.name:'—')}</div>`;
    card.onclick = ()=>applyTemplate(t);
    grid.appendChild(card);
  });
  if(!list.length) grid.innerHTML = '<div class="tmpl-note">No templates in this division yet.</div>';
}

function applyTemplate(t){
  const s = S(); if(!s) return;
  const F = s.F;
  F.base = 'new';
  F.template = t.id;
  F.model = s.templateMeshUrl(t);
  F.body.body_type = t.body_type;
  F.body.proportions = { height:t.proportions.height, weight:t.proportions.weight, muscle:t.proportions.muscle };
  F.body.skin_tone = t.skin_tone;
  F.body.head_shape = t.head_shape;
  F.profile.name = 'NEW FIGHTER';
  document.getElementById('tmpl-overlay').hidden = true;
  if(s.preview) s.preview.loadModel(F.model);
  s.setTab('body');
  startWizard();
  s.toast(`Template "${t.name}" loaded ✓`);
}

function openTemplateSelect(){
  const ov = ensureOverlay();
  renderTemplateGrid();
  ov.hidden = false;
}

/* ============================== WWE step wizard ============================== */
// No Mercy Edit-a-Superstar order, over the real panels (docs/CREATION-FLOW-MAP.md)
const STEPS = [
  { id:'template', label:'Template', go(){ openTemplateSelect(); } },
  { id:'body',     label:'Body',     go(){ const s=S(); s.setTab('body'); } },
  { id:'face',     label:'Head/Face',go(){ const s=S(); s.setTab('face'); } },
  { id:'skin',     label:'Skin',     go(){ const s=S(); s.setTab('body');
      setTimeout(()=>{ const el=document.querySelector('#panel-body'); if(el) el.scrollTop=0; },50); } },
  { id:'hair',     label:'Hair',     go(){ gotoAttireCat('hair'); } },
  { id:'facial',   label:'Facial Hair', go(){ gotoAttireCat('faces'); } },
  { id:'attire',   label:'Attire',   go(){ const s=S(); s.setTab('attire'); s.ui.attireCat=null; s.renderAll(); } },
  { id:'profile',  label:'Profile',  go(){ const s=S(); s.setTab('profile'); } },
  { id:'moveset',  label:'Moveset',  go(){ const s=S(); s.setTab('moveset'); } },
  { id:'done',     label:'Done ✓',   go(){ finishWizard(); } },
];
let wzIndex = 1, wizardOn = false;

function gotoAttireCat(key){
  const s = S(); if(!s) return;
  s.setTab('attire');
  const cat = (s.catalog.CATEGORIES||s.catalog.cats||[]).find(c=>c.key===key);
  // catalog exposes CATEGORIES via catForPart; fall back to renderAttire default
  s.ui.attireCat = null; s.ui.gridPage = 0;
  s.renderAll();
  if(cat){ s.ui.attireCat = cat; s.renderAll(); }
}

function ensureWizardBar(){
  let bar = document.getElementById('wizard-bar');
  if(bar) return bar;
  bar = document.createElement('div');
  bar.id = 'wizard-bar'; bar.hidden = true;
  document.body.appendChild(bar);
  return bar;
}

function renderWizardBar(){
  const bar = ensureWizardBar();
  if(!wizardOn){ bar.hidden = true; return; }
  bar.hidden = false;
  bar.innerHTML = '';
  const back = document.createElement('button');
  back.className = 'wz-btn'; back.textContent = '← BACK';
  back.onclick = ()=>{ if(wzIndex>1){ wzIndex--; STEPS[wzIndex].go(); renderWizardBar(); } };
  bar.appendChild(back);
  STEPS.forEach((st2,i)=>{
    if(i===0) return; // template step lives in the overlay
    const d = document.createElement('button');
    d.className = 'wz-step' + (i===wzIndex?' cur':(i<wzIndex?' done':''));
    d.textContent = i;
    d.title = st2.label;
    d.onclick = ()=>{ wzIndex=i; STEPS[wzIndex].go(); renderWizardBar(); };
    bar.appendChild(d);
  });
  const lab = document.createElement('span');
  lab.className = 'wz-label';
  lab.textContent = `${wzIndex}. ${STEPS[wzIndex].label}`;
  bar.appendChild(lab);
  const next = document.createElement('button');
  next.className = 'wz-btn primary';
  next.textContent = wzIndex>=STEPS.length-1 ? 'FINISH ✓' : 'NEXT →';
  next.onclick = ()=>{
    if(wzIndex>=STEPS.length-1){ finishWizard(); return; }
    wzIndex++; STEPS[wzIndex].go(); renderWizardBar();
  };
  bar.appendChild(next);
  const exit = document.createElement('button');
  exit.className = 'wz-btn'; exit.textContent = '✕';
  exit.title = 'Exit guided creation';
  exit.onclick = ()=>{ wizardOn=false; renderWizardBar(); };
  bar.appendChild(exit);
}

function startWizard(){ wzIndex = 1; wizardOn = true; renderWizardBar(); }
function finishWizard(){
  wizardOn = false; renderWizardBar();
  const s = S();
  s.modal('FIGHTER READY',
    `<p>Your fighter is built. Save it, export the JSON, or keep tweaking.</p>
     <div class="note">Fighter JSON matches <span style="font-family:monospace">customization/CHARACTER-CREATION.md §6</span> — the game consumes it as-is.</div>`,
    [{label:'💾 SAVE',cls:'btn-green',fn:()=>{ try{localStorage.setItem('wh_create_fighter_v1',JSON.stringify(s.F));}catch(e){} s.toast('Saved ✓'); }},
     {label:'KEEP EDITING',cls:'btn-gold'}]);
}

/* ============================== jobs panel ============================== */
const JOB_SERVER = 'http://127.0.0.1:8766';
let jobTimer = null;

async function serverTools(){
  try{
    const r = await fetch(JOB_SERVER+'/tools');
    if(!r.ok) throw 0;
    return await r.json();
  }catch(e){ return null; }
}

function renderJobs(el){
  const s = S();
  el.innerHTML = `
    <div class="sect">BLENDER JOB QUEUE</div>
    <div id="job-server-status"><div class="note">Checking job server…</div></div>
    <div class="sect">SUBMIT A JOB</div>
    <div class="field"><label>TOOL</label><select id="job-tool">
      <option value="mb-lab">mb-lab — parametric character bake</option>
      <option value="gnm">gnm — parametric head bake</option>
      <option value="gltfpack">gltfpack — optimize GLB</option>
      <option value="mpfb2-live">mpfb2-live — MPFB2 bake (needs Blender 4.2+)</option>
    </select></div>
    <div class="field"><label>PARAMS (JSON)</label>
      <textarea id="job-params" rows="5" style="width:100%;font-family:monospace;font-size:11px">{"character":"m_ca01","morphs":{"Mass":0.4,"Tone":0.7}}</textarea></div>
    <div class="field"><label>OUTPUT PATH (on the machine running the server)</label>
      <input id="job-out" style="width:100%" value="customization/templates/meshes/custom-bake.glb"></div>
    <div class="btn-row"><button class="btn btn-gold" id="job-submit">▶ SUBMIT JOB</button></div>
    <div class="sect">JOBS</div>
    <div id="job-list"><div class="note">No jobs yet.</div></div>
    <div class="note">The server runs Blender headless and reports live status here.
      Start it with: <span style="font-family:monospace">python3 tools/suite-jobs/server.py</span>
      (from the repo root). One-shot alternative:
      <span style="font-family:monospace">python3 tools/suite-jobs/run_job.py --spec jobs/x.json</span></div>`;
  const update = async ()=>{
    const tools = await serverTools();
    const box = el.querySelector('#job-server-status');
    if(!box.isConnected) { clearInterval(jobTimer); return; }
    if(!tools){
      box.innerHTML = `<div class="note">⚠️ Job server not reachable at <span style="font-family:monospace">${JOB_SERVER}</span>.<br>
        Start it: <span style="font-family:monospace">python3 tools/suite-jobs/server.py</span> — then jobs run here with live status.</div>`;
      return;
    }
    const rows = tools.map(t=>`<div class="kv"><span>${esc(t.tool)}</span><b>${t.runnable?'✅':'❌'} <small style="color:var(--dim)">${esc(t.detail||'')}</small></b></div>`).join('');
    box.innerHTML = `<div class="note">✅ Job server live.</div>${rows}`;
    try{
      const jobs = await (await fetch(JOB_SERVER+'/jobs')).json();
      const jl = el.querySelector('#job-list');
      jl.innerHTML = jobs.length ? jobs.map(j=>`
        <div class="job-row"><span class="st ${j.state}">${j.state.toUpperCase()}</span>
        <span style="flex:1"><b>${esc(j.id)}</b><br><small style="color:var(--dim)">${esc(j.tool)}</small></span>
        <button class="btn" data-job="${esc(j.id)}">STATUS</button></div>`).join('')
        : '<div class="note">No jobs yet.</div>';
      jl.querySelectorAll('[data-job]').forEach(b=>b.onclick=async ()=>{
        const st2 = await (await fetch(JOB_SERVER+'/jobs/'+b.dataset.job)).json();
        s.modal('JOB '+esc(st2.id),
          `<div class="kv"><span>State</span><b>${esc(st2.state)}</b></div>
           <div class="kv"><span>Output</span><b style="font-size:11px">${esc(st2.out||'—')}</b></div>
           <div class="sect">LOG</div>
           <pre style="max-height:220px;overflow:auto;font-size:10.5px">${esc((st2.log||[]).join('\n')).slice(-3000)}</pre>`,
          st2.state==='done'&&st2.out?[{label:'LOAD GLB IN PREVIEW',cls:'btn-green',fn:()=>{
              // server-side path -> suite-relative URL best effort
              const p = String(st2.out).split('customization/'); 
              s.preview.loadModel(p.length>1?'../customization/'+p[1]:st2.out);
            }},{label:'CLOSE',cls:''}]:[{label:'CLOSE',cls:'btn-gold'}]);
      });
    }catch(e){ /* keep list as-is */ }
  };
  el.querySelector('#job-tool').onchange = e=>{
    const presets = {
      'mb-lab': '{"character":"m_ca01","morphs":{"Mass":0.4,"Tone":0.7}}',
      'gnm': '{"identity":{"gender":"female","seed":3},"expression":{"happy":0.7}}',
      'gltfpack': '{"in":"customization/templates/meshes/technician.glb"}',
      'mpfb2-live': '{"target":"bulk","value":0.5}',
    };
    el.querySelector('#job-params').value = presets[e.target.value]||'{}';
  };
  el.querySelector('#job-submit').onclick = async ()=>{
    let params={};
    try{ params = JSON.parse(el.querySelector('#job-params').value||'{}'); }
    catch(e){ s.toast('Params are not valid JSON'); return; }
    const spec = { tool: el.querySelector('#job-tool').value, params,
                   out: el.querySelector('#job-out').value.trim() };
    try{
      const r = await fetch(JOB_SERVER+'/jobs',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(spec)});
      const j = await r.json();
      if(j.id){ s.toast('Job '+j.id+' queued ✓'); update(); }
      else s.toast('Job rejected: '+(j.error||'unknown'));
    }catch(e){ s.toast('Job server not running — start it first'); }
  };
  update();
  clearInterval(jobTimer);
  jobTimer = setInterval(update, 3000);
}

/* ============================== wire it up ============================== */
function init(){
  // JOBS rail button (added if the suite HTML has the rail)
  const rail = document.getElementById('left-rail');
  if(rail && !document.querySelector('[data-tab="jobs"]')){
    const b = document.createElement('button');
    b.className='rail-btn'; b.dataset.tab='jobs';
    b.setAttribute('aria-label','Jobs');
    b.innerHTML='<span class="rail-ico">⚙️</span><span class="rail-tx">JOBS</span>';
    b.onclick=()=>{ const s=S(); if(s){ s.setTab('jobs'); } };
    rail.appendChild(b);
  }
  // patch setTab/renderPanel to route the jobs tab
  // (app.js renderPanel already routes ui.tab==='jobs' to renderJobsTab,
  // which delegates to window.__flow.renderJobs)
  window.__flow = { openTemplateSelect, applyTemplate, startWizard, renderJobs,
                    gotoStep(i){ wzIndex=i; STEPS[i].go(); renderWizardBar(); } };
  // app.js boots before this classic script runs, so a fresh fighter's
  // template-select call at boot time found no window.__flow. Re-check here:
  // a NEW FIGHTER with no template yet opens the template select FIRST.
  const s = S();
  if(s && s.F && s.F.base==='new' && !s.F.template){
    openTemplateSelect();
  }
}
// app.js boots async; retry until window.__suite exists
let tries = 0;
const iv = setInterval(()=>{
  tries++;
  if(window.__suite){ clearInterval(iv); init(); }
  else if(tries>100){ clearInterval(iv); }
},100);
})();
