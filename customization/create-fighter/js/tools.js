/* tools.js — Creation Suite menu pass (worker 38, 2026-10-22; rebased 2026-10-22
   onto worker 37's flow module — no duplication).
   Owner directives implemented here:
   - WWE-template-first flow: the TEMPLATE SELECT screen is owned by
     js/creation-flow.js (data-driven from customization/templates/
     body-templates.json, MB-Lab-baked base meshes). This module does NOT
     ship a competing select — the TEMPLATE tab below is a thin wrapper that
     shows the current template and re-opens the flow module's select.
   - WWE creation sequence: template -> body -> head/face -> skin -> hair ->
     facial hair -> attire -> wardrobe -> profile (+ moveset, limbs, art,
     jobs, tools). Dedicated SKIN / HAIR / FACIAL HAIR steps.
   - Tool-to-menu wiring: every pipeline tool gets a menu home (TOOLS tab).
   - Three access layers: (1) UNIFIED per-domain systems, (2) SEPARATE per-tool
     menus, (3) UNIVERSAL MODE — the flow module's WWE step wizard
     (window.__flow.startWizard), the one combined front-end.

   All tool params below are grounded in the repo: MB-Lab spec params from the
   run_mblab_job.py docstring, Tripo intake flags from tools/tripo-intake/README,
   glTF-Transform from tools/anim/gltf_codec.mjs, MPFB2/GNM from
   customization/body-morphs + face-morphs + tools/gnm/WH-INTEGRATION.md.
   Tools not in this repo are badged FILED IN INTAKE / FETCH VIA SETUP —
   never presented as wired. */

/* ============ TOOL REGISTRY (grounded — see header) ============ */
const STATUS = {
  repo:   ['IN REPO', 'owned'],
  setup:  ['FETCH VIA SETUP', 'price'],
  intake: ['FILED IN INTAKE', 'price'],
};
/* Layer 2 — each tool's own menu. params: [key, label, type, options/default] */
export const SEPARATE_TOOLS = [
  { id:'mblab', name:'MB-Lab', icon:'🧬', status:'setup',
    desc:'Parametric humanoid generator (Blender addon). Headless job: blender -b --python tools/mb-lab/run_mblab_job.py.',
    params:[
      ['character','Character','select',['male_01','female_01']],
      ['phenotype','Phenotype','text',''],
      ['seed','Seed (deterministic randomize)','number',''],
      ['expression','Expression preset','text',''],
      ['finalize','Finalize to standard model','check',true],
    ],
    command:'blender -b --python tools/mb-lab/run_mblab_job.py -- --spec <spec.json> --out <file.glb>',
    spec:'mblab' },
  { id:'buildabod', name:'Build-A-Bod', icon:'🏗️', status:'intake',
    desc:'Male + female body builder for body-scaling work (filed into intake).',
    params:[
      ['preset','Body preset','select',['male-athletic','male-heavy','female-athletic','female-curvy']],
      ['scale_targets','Scale targets','text','height,shoulder,chest,waist,hips'],
    ],
    command:'(intake) build-a-bod --preset <preset> --out <file.glb>',
    spec:'buildabod' },
  { id:'mpfb2', name:'MPFB 2', icon:'🧍', status:'repo',
    desc:'MakeHuman Plugin for Blender — parametric bodies, auto-rig, procedural skin. 13 macro + 12 face morphs wired (customization/body-morphs/).',
    params:[ ['bake','Bake morphs to MPFB_<id> shape keys','action',''] ],
    command:'python3 customization/body-morphs/apply_mpfb_morphs.py --fighter <json> --out <glb>',
    spec:'mpfb2' },
  { id:'gnm', name:'GNM Face', icon:'🙂', status:'repo',
    desc:"Google Research Generative aNthropometric Model — parametric head/face/neck/eyes/teeth/tongue (customization/tools/gnm/, Apache-2.0).",
    params:[ ['preset','Expression preset','action','(use FACE tab)'] ],
    command:'(see customization/tools/gnm/WH-INTEGRATION.md)',
    spec:'gnm' },
  { id:'gamerig', name:'GameRig', icon:'🦴', status:'repo',
    desc:'Auto-rig backend (tools/open-source/gamerig, vendored in tools/auto_rig/vendor). The proven Tripo-static pipeline.',
    params:[
      ['backend','Rig backend','select',['gamerig']],
      ['facing','Facing axis','select',['auto','+z','-z','+x','-x']],
      ['validate','Run playable-gate validation','check',true],
    ],
    command:'python3 tools/auto_rig/rig_tripo_static.py --in <glb> --facing <axis> --out <glb>',
    spec:'gamerig' },
  { id:'naughtyrig', name:'NaughTyRig', icon:'🦴', status:'intake',
    desc:'Rigify feature set for anatomy rigging (filed into intake).',
    params:[ ['anatomy_set','Anatomy set','select',['full','torso','face']] ],
    command:'(intake) naughtyrig --anatomy <set> --rig <rig>',
    spec:'naughtyrig' },
  { id:'fluidpainter', name:'Fluid Painter', icon:'🖌️', status:'intake',
    desc:'Texture painting addon (NSFW build filed into intake) — paints skin detail onto the skin texture set.',
    params:[
      ['target','Target texture set','select',['skin-full','face','body']],
      ['layers','Paint layers','text','base,detail,tattoo'],
    ],
    command:'(intake) fluid-painter --target <set> --out <png>',
    spec:'fluidpainter' },
  { id:'tripo', name:'Tripo Intake', icon:'📥', status:'repo',
    desc:'Auto-intake: rigs new Tripo statics ASAP to the character rig (tools/tripo-intake/intake.py).',
    params:[
      ['fighter','Fighter (roster dir)','text',''],
      ['attire','Attire slot','number','1'],
      ['dry_run','Dry run (stage to /tmp, touch nothing)','check',true],
    ],
    command:'python3 tools/tripo-intake/intake.py --scan | --in <glb> --fighter <id> --attire <n> [--dry-run]',
    spec:'tripo' },
  { id:'export', name:'Export (glTF)', icon:'📦', status:'repo',
    desc:'glTF-Transform 4.1.1 + meshoptimizer 0.22.0 — decode/encode, compress (tools/anim/gltf_codec.mjs).',
    params:[
      ['codec','Compression','select',['meshopt','draco','none']],
      ['quantize','Quantize','check',true],
    ],
    command:'node tools/anim/gltf_codec.mjs encode --in <glb> --out <glb> --codec <meshopt|draco>',
    spec:'export' },
];
/* Layer 1 — unified per-domain systems (genuinely merged, not a launcher). */
export const UNIFIED_SYSTEMS = [
  { id:'body-system', name:'BODY SYSTEM', icon:'🦾',
    desc:'Unified body: MPFB2 parametric morphs + Build-A-Bod scaling + MB-Lab generation. One body pipeline — pick any source, same sliders, same bake.',
    tools:['mpfb2','buildabod','mblab'] },
  { id:'face-system', name:'FACE SYSTEM', icon:'😀',
    desc:'Unified face: GNM semantic params (20) + expression presets + placeable eye/brow mesh parts. One face pipeline.',
    tools:['gnm'] },
  { id:'skin-system', name:'SKIN SYSTEM', icon:'🎨',
    desc:'Unified skin: 8 No Mercy tones + 233 skin textures + 1,470 WMXIX decoded PNGs + Fluid Painter painting. One skin pipeline.',
    tools:['fluidpainter'] },
  { id:'rig-system', name:'RIG SYSTEM', icon:'🦴',
    desc:'Unified rigging: GameRig auto-rig + NaughTyRig anatomy features. One rig pipeline — rig once, jiggle-ready.',
    tools:['gamerig','naughtyrig'] },
  { id:'import-system', name:'IMPORT', icon:'📥',
    desc:'Unified import: Tripo auto-intake + teardown extraction. Drop a model, it gets claimed, faced, rigged, gated, staged.',
    tools:['tripo'] },
  { id:'export-system', name:'EXPORT', icon:'📦',
    desc:'Unified export: fighter JSON + GLB via glTF-Transform/meshoptimizer. One export, compressed and playable.',
    tools:['export'] },
];
export function toolById(id){ return SEPARATE_TOOLS.find(t=>t.id===id); }

/* job-spec download: the menu writes the spec, the pipeline runs it */
export function downloadJobSpec(specId, params){
  const tool = toolById(specId);
  const spec = {
    app:'wh-create-fighter', version:1, tool:specId,
    tool_name: tool?tool.name:specId,
    created:new Date().toISOString(),
    params, command: tool?tool.command:'',
  };
  const blob = new Blob([JSON.stringify(spec,null,2)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `wh-job-${specId}-${Date.now()}.json`;
  a.click(); URL.revokeObjectURL(a.href);
}

/* ============ TEMPLATE TAB — thin wrapper over the flow module ============
   The template select screen itself is owned by js/creation-flow.js
   (data-driven from customization/templates/body-templates.json). This tab
   shows the current pick and re-opens their select — no competing select. */
export function currentTemplate(ctx){
  const tpls = (window.__suite && window.__suite.TEMPLATES && window.__suite.TEMPLATES.body) || [];
  return tpls.find(t=>t.id===ctx.F.template) || null;
}
export function renderTemplateTab(ctx, el){
  const t = currentTemplate(ctx);
  el.innerHTML = `
    <div class="sect">CURRENT TEMPLATE</div>
    <div class="kv"><span>Template</span><b>${t?ctx.esc(t.name):'<span style="color:var(--dim)">— none picked —</span>'}</b></div>
    ${t?`<div class="kv"><span>Division</span><b>${ctx.esc(t.division||'—')}</b></div>
    <div class="kv"><span>Source</span><b style="font-size:11px">${ctx.esc(t.source||'—')}</b></div>`:''}
    <div class="btn-row"><button class="btn btn-gold" id="btn-retemplate">🧍 CHANGE TEMPLATE</button></div>
    <div class="note">Templates come from <span class="mono">customization/templates/body-templates.json</span> (WWE 2K-style, MB-Lab-baked base meshes). The select screen is owned by the creation-flow module — this tab just re-opens it.</div>`;
  el.querySelector('#btn-retemplate').onclick=()=>{
    if(window.__flow && window.__flow.openTemplateSelect) window.__flow.openTemplateSelect();
    else ctx.toast('Flow module not loaded');
  };
}

/* ============ SKIN TAB (WWE step 4) ============ */
export function renderSkinTab(ctx, el){
  const { F, isCustom, catalog, esc } = ctx;
  const locked = !isCustom();
  const tones = ctx.SKIN_TONES;
  el.innerHTML = `
    ${locked?`<div class="note">🔒 <b>Canon skin</b> — roster fighters keep their real textures. NEW FIGHTER gets full SKIN access.</div>`:''}
    <div class="sect">SKIN TONE — No Mercy tones</div>
    <div class="swatches" id="skintones"></div>
    <div class="sect">SKIN TEXTURES — ${catalog.count('skins')} No Mercy + 1,470 WMXIX decoded PNGs</div>
    <div class="note">233 No Mercy skin PNGs + 1,470 WMXIX decoded textures, browsable below. <b>SKIN SYSTEM</b> (TOOLS tab): Fluid Painter paints detail onto these sets.</div>
    <div class="btn-row"><button class="btn" id="btn-skintex">BROWSE SKIN TEXTURES</button>
    <button class="btn" id="btn-skinsys">SKIN SYSTEM →</button></div>
    <div class="sect">FLUID PAINTER — paint onto the skin set</div>
    <div class="field"><label>TARGET SET</label><select id="fp-target">
      <option>skin-full</option><option>face</option><option>body</option></select></div>
    <div class="field"><label>LAYERS</label><input id="fp-layers" value="base,detail,tattoo"></div>
    <div class="btn-row"><button class="btn btn-gold" id="btn-fpspec">⤓ FLUID PAINTER JOB SPEC</button></div>
    <div class="note">The spec downloads as JSON — the pipeline (Blender + Fluid Painter addon) consumes it. Filed in intake; not executed from the browser.</div>`;
  const st = el.querySelector('#skintones');
  tones.forEach(hex=>{
    const s = document.createElement('div');
    s.className = 'swatch'+(F.body.skin_tone===hex?' active':'');
    s.style.background = hex; s.title = hex;
    if(locked) s.style.opacity = '0.35';
    s.onclick = ()=>{ if(locked) return; F.body.skin_tone = hex; ctx.renderAll(); };
    st.appendChild(s);
  });
  el.querySelector('#btn-skintex').onclick=()=>{
    ctx.setTab('attire');
    ctx.ui.attireCat = ctx.CATEGORIES.find(c=>c.key==='skins');
    ctx.ui.gridPage=0; ctx.ui.gridQuery=''; ctx.ui.selPart=null;
    ctx.renderAll();
  };
  el.querySelector('#btn-skinsys').onclick=()=>ctx.setTab('tools');
  el.querySelector('#btn-fpspec').onclick=()=>{
    downloadJobSpec('fluidpainter', {
      target: el.querySelector('#fp-target').value,
      layers: el.querySelector('#fp-layers').value.split(',').map(s=>s.trim()),
      skin_tone: F.body.skin_tone,
    });
    ctx.toast('Fluid Painter job spec downloaded ✓');
  };
}

/* ============ HAIR / FACIAL HAIR TABS (WWE steps 5-6) ============ */
/* these steps ARE their category view — the grid's back button returns to
   the ATTIRE step's category list instead of looping back into the step */
function rebindStepBack(ctx, el){
  const bb = el.querySelector('#btn-back');
  if(bb){ bb.textContent='← ATTIRE'; bb.onclick = ()=>{ ctx.ui.attireCat=null; ctx.ui.selPart=null; ctx.setTab('attire'); }; }
}
export function renderHairTab(ctx, el){
  ctx.ui.attireCat = ctx.CATEGORIES.find(c=>c.key==='hair');
  ctx.ui.gridPage = 0; ctx.ui.selPart = null;
  ctx.renderItemGrid(el, ctx.ui.attireCat);
  rebindStepBack(ctx, el);
}
export function renderFacialHairTab(ctx, el){
  const cat = ctx.CATEGORIES.find(c=>c.key==='facialhair');
  ctx.ui.attireCat = cat;
  ctx.ui.gridPage = 0; ctx.ui.selPart = null;
  const host = document.createElement('div');
  el.appendChild(host);
  el.insertAdjacentHTML('afterbegin',
    `<div class="note">🧔 In the AKI engine, beards live in the <b>face texture</b> parts — this step merges face textures + head parts into T7 slot 7 (Facial Hair). Conflicts with Full Head (slot 3), Tekken rule.</div>`);
  ctx.renderItemGrid(host, cat);
  rebindStepBack(ctx, host);
}

/* ============ TOOLS TAB — three access layers ============ */
export function renderToolsTab(ctx, el){
  el.innerHTML = `
    <div class="sect">LAYER 1 — UNIFIED SYSTEMS</div>
    <div class="note">Genuinely merged systems — one pipeline per domain, all sources inside. Not a launcher.</div>
    <div id="layer1"></div>
    <div class="sect">LAYER 2 — SEPARATE TOOLS</div>
    <div class="note">Every tool in its own menu, with its real parameters. Menus write <b>job-spec JSONs</b> the pipeline consumes — nothing executes from the browser. (The JOBS tab runs live jobs via the suite job server.)</div>
    <div id="layer2"></div>
    <div class="sect">LAYER 3 — UNIVERSAL MODE</div>
    <div class="note">One combined front-end for the full creation flow — the WWE step wizard (template → body → face → skin → hair → facial hair → attire → profile → moveset → done), stepping over the real tab panels.</div>
    <div class="btn-row"><button class="btn btn-gold" id="btn-universal">🌐 START UNIVERSAL MODE</button></div>`;
  const l1 = el.querySelector('#layer1');
  UNIFIED_SYSTEMS.forEach(s=>{
    const b = document.createElement('button');
    b.className = 'subcat';
    b.innerHTML = `<span class="sc-ico">${s.icon}</span><span>${s.name}<br><small style="color:var(--dim)">${ctx.esc(s.tools.map(t=>toolById(t).name).join(' + '))}</small></span><span class="sc-count">→</span>`;
    b.onclick = ()=>renderUnifiedDetail(ctx, el, s);
    l1.appendChild(b);
  });
  const l2 = el.querySelector('#layer2');
  SEPARATE_TOOLS.forEach(t=>{
    const [badge, cls] = STATUS[t.status];
    const b = document.createElement('button');
    b.className = 'subcat';
    b.innerHTML = `<span class="sc-ico">${t.icon}</span><span>${t.name}<br><small style="color:var(--dim)">${ctx.esc(t.desc.split('.')[0])}</small></span><span class="${cls}" style="font-size:10px">${badge}</span>`;
    b.onclick = ()=>renderToolDetail(ctx, el, t);
    l2.appendChild(b);
  });
  el.querySelector('#btn-universal').onclick=()=>{
    if(window.__flow && window.__flow.startWizard) window.__flow.startWizard();
    else ctx.toast('Flow module not loaded');
  };
}

function backToTools(ctx, el){
  const back = document.createElement('div');
  back.className = 'back-row';
  back.innerHTML = `<button class="btn back-btn" id="btn-tools-back">← TOOLS</button>`;
  back.querySelector('#btn-tools-back').onclick=()=>{ ctx.setTab('tools'); };
  el.prepend(back);
}

function renderUnifiedDetail(ctx, el, s){
  el.innerHTML = '';
  backToTools(ctx, el);
  const host = document.createElement('div');
  host.innerHTML = `
    <div class="sect">${s.icon} ${s.name} — UNIFIED</div>
    <div class="note">${ctx.esc(s.desc)}</div>
    <div class="sect">MEMBER TOOLS</div>
    <div id="umembers"></div>
    <div class="sect">UNIFIED ACTIONS</div>
    <div id="uacts"></div>`;
  el.appendChild(host);
  const um = host.querySelector('#umembers');
  s.tools.forEach(tid=>{
    const t = toolById(tid);
    const [badge, cls] = STATUS[t.status];
    const b = document.createElement('button');
    b.className = 'subcat';
    b.innerHTML = `<span class="sc-ico">${t.icon}</span><span>${t.name}</span><span class="${cls}" style="font-size:10px">${badge}</span>`;
    b.onclick = ()=>renderToolDetail(ctx, el, t);
    um.appendChild(b);
  });
  const ua = host.querySelector('#uacts');
  unifiedActions(ctx, s.id).forEach(a=>{
    const b = document.createElement('button');
    b.className = 'btn '+(a.cls||'');
    b.textContent = a.label;
    b.onclick = a.fn;
    const row = document.createElement('div');
    row.className = 'btn-row'; row.appendChild(b);
    ua.appendChild(row);
  });
}
/* each unified system exposes the merged pipeline's real actions */
function unifiedActions(ctx, sysId){
  const { F } = ctx;
  const spec = (toolId, params)=>()=>{ downloadJobSpec(toolId, params); ctx.toast('Job spec downloaded ✓'); };
  switch(sysId){
    case 'body-system': return [
      { label:'⤓ BAKE MPFB2 MORPHS → shape keys', cls:'btn-gold',
        fn: spec('mpfb2', { morphs:F.morphs||{}, out:'<fighter>.glb' }) },
      { label:'⤓ MB-LAB GENERATE (headless spec)', fn:()=>renderToolDetail(ctx, document.querySelector('#panel-body'), toolById('mblab')) },
      { label:'BODY sliders live here too →', fn:()=>ctx.setTab('body') },
    ];
    case 'face-system': return [
      { label:'FACE tab (GNM params + presets) →', cls:'btn-gold', fn:()=>ctx.setTab('face') },
      { label:'⤓ GNM job spec', fn: spec('gnm', { preset:F.face?.preset||'', params:F.face?.params||{} }) },
    ];
    case 'skin-system': return [
      { label:'SKIN tab (tones + textures) →', cls:'btn-gold', fn:()=>ctx.setTab('skin') },
      { label:'⤓ FLUID PAINTER job spec', fn: spec('fluidpainter', { target:'skin-full', skin_tone:F.body.skin_tone }) },
    ];
    case 'rig-system': return [
      { label:'⤓ AUTO-RIG job spec (GameRig)', cls:'btn-gold',
        fn: spec('gamerig', { backend:'gamerig', facing:'auto', validate:true, model:F.model }) },
      { label:'⤓ NAUGHTYRIG anatomy job spec', fn: spec('naughtyrig', { anatomy_set:'full', model:F.model }) },
    ];
    case 'import-system': return [
      { label:'⤓ TRIPO INTAKE job spec', cls:'btn-gold',
        fn:()=>renderToolDetail(ctx, document.querySelector('#panel-body'), toolById('tripo')) },
    ];
    case 'export-system': return [
      { label:'⤓ EXPORT GLB (glTF-Transform)', cls:'btn-gold',
        fn: spec('export', { codec:'meshopt', quantize:true, fighter:F.profile.name }) },
      { label:'⤓ EXPORT fighter JSON', fn:()=>document.querySelector('#btn-export').click() },
    ];
    default: return [];
  }
}

function renderToolDetail(ctx, el, t){
  const { esc } = ctx;
  el.innerHTML = '';
  backToTools(ctx, el);
  const [badge, cls] = STATUS[t.status];
  const host = document.createElement('div');
  host.innerHTML = `
    <div class="sect">${t.icon} ${esc(t.name)} <span class="${cls}" style="font-size:10px">${badge}</span></div>
    <div class="note">${esc(t.desc)}</div>
    <div class="kv"><span>Command</span><b style="font-size:11px">${esc(t.command)}</b></div>
    <div class="sect">PARAMETERS</div>
    <div id="tparams"></div>
    <div class="btn-row"><button class="btn btn-gold" id="btn-jobspec">⤓ DOWNLOAD JOB SPEC</button></div>
    <div class="note">The menu writes the spec — the pipeline runs it. ${t.status!=='repo'?'This tool is not in the browser build: '+(t.status==='setup'?'fetch it with <span class="mono">tools/setup/setup_toolchain.sh</span>.':'it is filed in intake — see the SmutBase intake rundown.'):'This tool is in the repo; the spec targets it directly.'}</div>`;
  el.appendChild(host);
  const tp = host.querySelector('#tparams');
  const vals = {};
  t.params.forEach(([key,label,type,def])=>{
    vals[key] = def;
    const d = document.createElement('div');
    d.className = 'field';
    if(type==='select'){
      d.innerHTML = `<label>${esc(label).toUpperCase()}</label><select data-pk="${key}">${def.map(o=>`<option>${esc(o)}</option>`).join('')}</select>`;
      d.querySelector('select').onchange = e=>{ vals[key]=e.target.value; };
    } else if(type==='check'){
      d.innerHTML = `<label>${esc(label).toUpperCase()}</label><input type="checkbox" data-pk="${key}" ${def?'checked':''} style="width:24px;height:24px">`;
      d.querySelector('input').onchange = e=>{ vals[key]=e.target.checked; };
    } else if(type==='number'){
      d.innerHTML = `<label>${esc(label).toUpperCase()}</label><input type="number" data-pk="${key}" value="${esc(String(def))}">`;
      d.querySelector('input').onchange = e=>{ vals[key]=+e.target.value; };
    } else if(type==='action'){
      d.innerHTML = `<div class="note">${esc(label)}: ${esc(def)}</div>`;
    } else {
      d.innerHTML = `<label>${esc(label).toUpperCase()}</label><input data-pk="${key}" value="${esc(String(def))}">`;
      d.querySelector('input').onchange = e=>{ vals[key]=e.target.value; };
    }
    tp.appendChild(d);
  });
  host.querySelector('#btn-jobspec').onclick=()=>{
    downloadJobSpec(t.spec, vals);
    ctx.toast(`${t.name} job spec downloaded ✓`);
  };
}
