/* art.js — ART tab: image editing wired into the creation suite.
   Two tools, per the TOOL-TO-MENU WIRING LAW (art/texture section):
     STUDIO  — TOAST UI Image Editor (MIT, vendored): manual editing
               (crop, rotate, filters, text, shapes, draw). Opens art-studio.html.
     AI EDIT — generative editing: image + natural-language instruction ->
               tools/image-edit/server.py (/api/ai-edit). Needs the server
               running (python tools/image-edit/server.py --port 8791).

   The in-conversation path (assistant editing via Muse's media pipeline)
   is separate; this panel is for the user working in the suite directly. */

const AI_EDIT_SERVER = 'http://127.0.0.1:8791';   // tools/image-edit/server.py
const LS_SERVER_KEY = 'wh_art_server_url';

function serverUrl(){
  try { return localStorage.getItem(LS_SERVER_KEY) || AI_EDIT_SERVER; }
  catch(e){ return AI_EDIT_SERVER; }
}

function esc(s){
  return String(s==null?'':s).replace(/[&<>"']/g, c=>(
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

export function renderArt(el, ui, helpers){
  const { toast } = helpers || {};
  const say = toast || ((m)=>{ const t=document.querySelector('#save-toast'); if(t){ t.textContent=m; setTimeout(()=>{t.textContent='';},2500);} });

  el.innerHTML = `
    <div class="sect">IMAGE EDITING</div>
    <div class="note">Two editors, one tab. <b>STUDIO</b> is the manual editor
      (crop, rotate, filters, text, draw) — runs fully in the browser, no server.
      <b>AI EDIT</b> takes an image + a plain-English instruction
      ("make the shell red and white") and needs the image-edit server running:
      <span style="font-size:11px">python tools/image-edit/server.py --port 8791</span></div>
    <div class="btn-row" style="margin-bottom:12px">
      <button class="btn btn-gold" id="art-open-studio">🎨 OPEN STUDIO</button>
    </div>
    <div class="sect">AI EDIT — GENERATIVE</div>
    <div class="field"><label>SERVER URL</label>
      <input type="text" id="art-server" value="${esc(serverUrl())}" style="width:100%">
    </div>
    <div class="btn-row"><button class="btn" id="art-check-server">CHECK SERVER</button>
      <span id="art-server-status" class="bb-hint"></span></div>
    <div class="field"><label>SOURCE IMAGE</label>
      <input type="file" id="art-file" accept="image/*">
    </div>
    <div id="art-preview-wrap" style="margin:8px 0; display:none">
      <img id="art-preview" style="max-width:100%; border:1px solid var(--edge); border-radius:6px" alt="source preview">
    </div>
    <div class="field"><label>INSTRUCTION — describe the edit in plain words</label>
      <textarea id="art-instruction" rows="3" style="width:100%" placeholder="make the shell red and white like a Mario Koopa shell, keep everything else the same"></textarea>
    </div>
    <div class="field"><label>BACKEND</label>
      <select id="art-backend">
        <option value="auto">auto (first available)</option>
        <option value="pollinations">pollinations (free, no key — guided generation)</option>
        <option value="hf">hf (needs HF_TOKEN — surgical editing)</option>
        <option value="local">local (needs GPU — fully offline)</option>
      </select>
    </div>
    <div class="btn-row">
      <button class="btn btn-green" id="art-run">✨ RUN AI EDIT</button>
      <span id="art-run-status" class="bb-hint"></span>
    </div>
    <div id="art-result-wrap" style="margin:8px 0; display:none">
      <div class="sect">RESULT</div>
      <img id="art-result" style="max-width:100%; border:1px solid var(--edge); border-radius:6px" alt="ai edit result">
      <div class="btn-row">
        <button class="btn btn-gold" id="art-download">⤓ DOWNLOAD RESULT</button>
        <button class="btn" id="art-open-in-studio">🎨 OPEN IN STUDIO</button>
      </div>
    </div>`;

  el.querySelector('#art-open-studio').onclick = ()=>{
    location.href = 'art-studio.html';
  };

  const serverInput = el.querySelector('#art-server');
  serverInput.onchange = ()=>{
    try { localStorage.setItem(LS_SERVER_KEY, serverInput.value.trim()); } catch(e){}
  };

  el.querySelector('#art-check-server').onclick = async ()=>{
    const st = el.querySelector('#art-server-status');
    st.textContent = 'checking…';
    try {
      const r = await fetch(serverInput.value.trim().replace(/\/$/,'') + '/api/backends');
      if(!r.ok) throw new Error('HTTP '+r.status);
      const list = await r.json();
      const avail = list.filter(b=>b.available).map(b=>b.name).join(', ') || 'none';
      st.textContent = '✓ server up — backends: ' + avail;
    } catch(e){
      st.textContent = '✗ no server — run: python tools/image-edit/server.py --port 8791';
    }
  };

  let fileDataUrl = null;
  el.querySelector('#art-file').onchange = (e)=>{
    const f = e.target.files[0];
    if(!f) return;
    const rd = new FileReader();
    rd.onload = ()=>{
      fileDataUrl = rd.result;
      const pv = el.querySelector('#art-preview');
      pv.src = fileDataUrl;
      el.querySelector('#art-preview-wrap').style.display = 'block';
    };
    rd.readAsDataURL(f);
  };

  el.querySelector('#art-run').onclick = async ()=>{
    const st = el.querySelector('#art-run-status');
    const instruction = el.querySelector('#art-instruction').value.trim();
    if(!fileDataUrl){ st.textContent = 'pick a source image first'; return; }
    if(!instruction){ st.textContent = 'describe the edit first'; return; }
    const backend = el.querySelector('#art-backend').value;
    const base = serverInput.value.trim().replace(/\/$/,'');
    st.textContent = 'working… (generative edits take 30–120s)';
    try {
      // dataURL -> blob for multipart upload
      const blob = await (await fetch(fileDataUrl)).blob();
      const fd = new FormData();
      fd.append('image', blob, 'source.png');
      fd.append('instruction', instruction);
      fd.append('backend', backend);
      const r = await fetch(base + '/api/ai-edit', { method:'POST', body: fd });
      if(!r.ok){
        const err = await r.json().catch(()=>({error:'HTTP '+r.status}));
        throw new Error(err.error || ('HTTP '+r.status));
      }
      const outBlob = await r.blob();
      const outUrl = URL.createObjectURL(outBlob);
      el.querySelector('#art-result').src = outUrl;
      el.querySelector('#art-result-wrap').style.display = 'block';
      st.textContent = '✓ done';
      el.querySelector('#art-download').onclick = ()=>{
        const a = document.createElement('a');
        a.href = outUrl; a.download = 'wh-ai-edit.png';
        document.body.appendChild(a); a.click(); a.remove();
      };
      el.querySelector('#art-open-in-studio').onclick = ()=>{
        // TOAST UI loads from URL — blob URLs work via the ?img= param
        location.href = 'art-studio.html?img=' + encodeURIComponent(outUrl);
      };
      say('AI edit complete ✓');
    } catch(e){
      st.textContent = '✗ ' + e.message;
    }
  };
}
