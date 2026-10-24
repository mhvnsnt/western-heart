/* POSE STUDIO — port of Bannon's poseStudio (index.html L18846: STUDIO.work,
   joint chips, X/Y/Z sliders, MIRROR, SET KEYFRAME, timeline, saved clips)
   rebuilt as a T7-customization style menu. Writes to the fighter's studio
   record: selectPose (select screen), fightPose (fight stance overlay),
   clips (custom animations, read by Bannon Studio / Move Forge). */
import { JOINTS, LABELS, MIRROR, LOCKED_SELECT_POSE, loadDB, saveDB, fighter, patchFighter } from './studio-store.js';
import { boneIndex, findBone, applyPoseOverlay } from './studio-apply.js';

const DEG = Math.PI / 180;
export function samplePoseKeys(keys, t){
  if (!keys.length) return {}; if (keys.length === 1 || t <= keys[0].t) return keys[0].pose;
  for (let i = 1; i < keys.length; i++) { const a = keys[i - 1], b = keys[i]; if (t <= b.t) { const u = (t - a.t) / Math.max(1e-6, b.t - a.t); const out = {};
    for (const j of new Set([...Object.keys(a.pose), ...Object.keys(b.pose)])) { const p = a.pose[j] || [0,0,0], q = b.pose[j] || [0,0,0]; out[j] = [0,1,2].map(k => p[k] + (q[k] - p[k]) * u); } return out; } }
  return keys[keys.length - 1].pose;
}

export function mountPoseStudio(ctx){
  const { viewer, el, toast, getFighterId, setTabs } = ctx;
  const S = { slot: 'selectPose', sel: 'RightArm', mirror: true, work: {}, keys: [], dur: 1.5, playT: 0, playing: false, rest: null, idx: null };
  function captureRest(){ S.idx = boneIndex(viewer.model); S.rest = new Map(); for (const k in S.idx) S.rest.set(S.idx[k], S.idx[k].quaternion.clone()); }
  function loadSlot(){ const f = loadDB().fighters[getFighterId()] || {}; S.work = JSON.parse(JSON.stringify(f[S.slot] || {})); const c = (f.clips || {}).custom; S.keys = c ? c.keys : []; S.dur = c ? c.dur : 1.5; }
  viewer.onFrame = (dt) => {
    if (!viewer.model) return; if (!S.rest || S.restModel !== viewer.model) { captureRest(); S.restModel = viewer.model; }
    for (const [b, q] of S.rest) b.quaternion.copy(q);
    let pose = S.work;
    if (S.playing && S.keys.length) { S.playT = (S.playT + dt) % S.dur; pose = samplePoseKeys(S.keys, S.playT); const tl = el.querySelector('#ps-tl'); if (tl) tl.value = S.playT; }
    applyPoseOverlay(viewer.model, pose, 1, { idx: S.idx, model: viewer.model });
  };
  const cur = () => (S.work[S.sel] ||= [0, 0, 0]);
  function setAxis(a, v){ cur()[a] = v; if (S.mirror && MIRROR[S.sel]) { const m = (S.work[MIRROR[S.sel]] ||= [0,0,0]); m[a] = a === 0 ? v : -v; } }
  function render(){
    const fid = getFighterId(); const locked = S.slot === 'selectPose' && LOCKED_SELECT_POSE.has(fid);
    const p = cur(); const missing = viewer.model && S.idx && !findBone(S.idx, S.sel);
    el.innerHTML = `
      <div class="lbl">BODY PART</div>
      <div class="row" id="ps-joints">${JOINTS.map(j => `<button class="chip${j === S.sel ? ' sel' : ''}" data-j="${j}">${LABELS[j]}</button>`).join('')}</div>
      ${missing ? '<div class="note">This rig has no matching bone for that part.</div>' : ''}
      ${['TILT', 'TURN', 'TWIST'].map((n, a) => `<label class="slider"><span>${n}</span><input type="range" min="-180" max="180" step="1" data-a="${a}" value="${Math.round(p[a] / DEG)}"><output>${Math.round(p[a] / DEG)}°</output></label>`).join('')}
      <div class="btns">
        <button class="btn" id="ps-mirror">MIRROR: ${S.mirror ? 'ON' : 'OFF'}</button>
        <button class="btn" id="ps-zero">RESET PART</button>
        <button class="btn" id="ps-clear">RESET ALL</button>
        <button class="btn pri" id="ps-save" ${locked ? 'disabled' : ''}>${locked ? 'POSE LOCKED' : 'SAVE'}</button>
      </div>
      <div class="lbl" style="margin-top:14px">ANIMATION</div>
      <label class="slider"><span>TIME</span><input type="range" id="ps-tl" min="0" max="${S.dur}" step="0.01" value="${S.playT}"><output>${S.keys.length} keys</output></label>
      <div class="btns">
        <button class="btn" id="ps-key">SET KEYFRAME</button>
        <button class="btn" id="ps-play">${S.playing ? 'STOP' : 'PLAY'}</button>
        <button class="btn" id="ps-clip">SAVE ANIMATION</button>
        <button class="btn" id="ps-lib">SAVE TO LIBRARY</button>
      </div>
      <div class="note" style="margin-top:10px">${locked ? 'This fighter\'s select pose is locked by the owner.' : S.slot === 'selectPose' ? 'Saved pose shows on the character select screen.' : 'Saved stance rides on top of the fighter\'s real Tekken stance in fights.'}</div>`;
    el.querySelectorAll('[data-j]').forEach(b => b.onclick = () => { S.sel = b.dataset.j; render(); el.querySelector(`[data-j="${S.sel}"]`).focus(); });
    el.querySelectorAll('input[data-a]').forEach(r => r.oninput = () => { setAxis(+r.dataset.a, r.value * DEG); r.nextElementSibling.textContent = r.value + '°'; });
    el.querySelector('#ps-mirror').onclick = () => { S.mirror = !S.mirror; render(); };
    el.querySelector('#ps-zero').onclick = () => { S.work[S.sel] = [0,0,0]; if (S.mirror && MIRROR[S.sel]) S.work[MIRROR[S.sel]] = [0,0,0]; render(); };
    el.querySelector('#ps-clear').onclick = () => { S.work = {}; render(); };
    el.querySelector('#ps-save').onclick = () => { const clean = {}; for (const j in S.work) if (S.work[j].some(v => Math.abs(v) > 1e-4)) clean[j] = S.work[j]; patchFighter(fid, { [S.slot]: clean }); toast(S.slot === 'selectPose' ? 'Select pose saved' : 'Fight stance saved'); };
    el.querySelector('#ps-tl').oninput = (e) => { S.playing = false; S.playT = +e.target.value; S.work = JSON.parse(JSON.stringify(samplePoseKeys(S.keys, S.playT))); };
    el.querySelector('#ps-key').onclick = () => { const t = S.keys.length ? Math.min(S.dur, S.playT || S.keys[S.keys.length - 1].t + 0.25) : 0; S.keys = S.keys.filter(k => Math.abs(k.t - t) > 0.01); S.keys.push({ t, pose: JSON.parse(JSON.stringify(S.work)) }); S.keys.sort((a, b) => a.t - b.t); S.dur = Math.max(S.dur, t); S.playT = t; render(); toast('Keyframe at ' + t.toFixed(2) + 's'); };
    el.querySelector('#ps-play').onclick = () => { S.playing = !S.playing; render(); };
    el.querySelector('#ps-clip').onclick = () => { const d = loadDB(); const f = fighter(d, fid); (f.clips ||= {}).custom = { dur: S.dur, keys: S.keys }; saveDB(d); toast('Animation saved'); };
    el.querySelector('#ps-lib').onclick = () => { const d = loadDB(); const n = 'pose-' + Object.keys(d.library.poses).length; d.library.poses[n] = { from: fid, pose: S.work }; saveDB(d); toast('Saved to library as ' + n); };
  }
  setTabs([['selectPose', 'SELECT POSE'], ['fightPose', 'FIGHT STANCE']], S.slot, (k) => { S.slot = k; loadSlot(); render(); });
  loadSlot(); render();
  return { refresh(){ S.rest = null; loadSlot(); render(); }, state: S };
}
