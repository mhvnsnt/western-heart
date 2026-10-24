/* ============================================================
   WESTERN HEART — Studio store (Bannon studios port, 2026-10-23)
   One save record shared by every studio (Pose, Bannon Studio, Mocap,
   Move Forge, Strike/Dive Lab, Creation Suite, Live Deformation).
   The REAL game systems read it: select-screen.js (select pose),
   fighter.js (fight stance overlay, AI DNA, strike tuning, live
   deformation). Port of Bannon's STUDIO saveDB/loadDB (index.html
   ~L18860) re-shaped per fighter. Pure ES module, no DOM, node-testable.
   ============================================================ */
export const STORE_KEY = 'wh_studio_v1';
export const SCHEMA = 1;

/* Canon humanoid joint set the editors expose (Bannon J11 widened to a
   full Tekken-style skeleton). Names match the canonical rig bones. */
export const JOINTS = ['Hips','Spine','Spine1','Neck','Head',
  'LeftShoulder','LeftArm','LeftForeArm','LeftHand',
  'RightShoulder','RightArm','RightForeArm','RightHand',
  'LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot'];
export const LABELS = {Hips:'Hips',Spine:'Waist',Spine1:'Chest',Neck:'Neck',Head:'Head',
  LeftShoulder:'L Shoulder',LeftArm:'L Upper Arm',LeftForeArm:'L Forearm',LeftHand:'L Hand',
  RightShoulder:'R Shoulder',RightArm:'R Upper Arm',RightForeArm:'R Forearm',RightHand:'R Hand',
  LeftUpLeg:'L Thigh',LeftLeg:'L Shin',LeftFoot:'L Foot',RightUpLeg:'R Thigh',RightLeg:'R Shin',RightFoot:'R Foot'};
export const MIRROR = {};
for (const j of JOINTS) { if (j.startsWith('Left')) { MIRROR[j]='Right'+j.slice(4); MIRROR['Right'+j.slice(4)]=j; } }

/* Fighters whose select pose is owner-locked: editors refuse to write it. */
export const LOCKED_SELECT_POSE = new Set(['buffalo-bill','buffalobill']);

let _mem = null;
function ls(){ try { return (typeof localStorage!=='undefined') ? localStorage : null; } catch { return null; } }
export function emptyDB(){ return { v: SCHEMA, fighters: {}, library: { poses:{}, clips:{}, moves:{}, presets:{} } }; }
export function loadDB(){
  const s = ls();
  if (s) { try { const r = JSON.parse(s.getItem(STORE_KEY)||'null'); if (r && r.v===SCHEMA) return normalize(r); } catch {} }
  return _mem ? normalize(_mem) : emptyDB();
}
function normalize(d){ d.fighters ||= {}; d.library ||= {}; for (const k of ['poses','clips','moves','presets']) d.library[k] ||= {}; return d; }
export function saveDB(d){ _mem = d; const s = ls(); if (s) { try { s.setItem(STORE_KEY, JSON.stringify(d)); } catch {} } return d; }
export function fighter(d, id){ return (d.fighters[id] ||= {}); }
export function getFighterData(id){ return loadDB().fighters[id] || null; }
export function patchFighter(id, patch){
  const d = loadDB(); const f = fighter(d, id);
  if (patch.selectPose && LOCKED_SELECT_POSE.has(id)) { patch = { ...patch }; delete patch.selectPose; }
  Object.assign(f, patch, { updated: new Date().toISOString() });
  saveDB(d); return f;
}
export function clamp(v, lo, hi){ return Math.max(lo, Math.min(hi, +v || 0)); }

/* Cross-game bundle: export/import between WH, the standalone studio and
   other games' extracted data. `source` tags where a piece came from
   (wh | t8 | t7 | ttt2 | 2k19 | firepro | gangbeasts | bannon | file). */
export function exportBundle(ids){
  const d = loadDB(); const fighters = {};
  for (const id of (ids || Object.keys(d.fighters))) if (d.fighters[id]) fighters[id] = d.fighters[id];
  return { format: 'wh-studio-bundle', v: SCHEMA, exported: new Date().toISOString(), fighters, library: d.library };
}
export function importBundle(b, { merge = true } = {}){
  if (!b || b.format !== 'wh-studio-bundle') throw new Error('not a wh-studio-bundle');
  const d = merge ? loadDB() : emptyDB();
  for (const [id, f] of Object.entries(b.fighters || {})) {
    const cur = fighter(d, id);
    const inc = { ...f }; if (LOCKED_SELECT_POSE.has(id)) delete inc.selectPose;
    Object.assign(cur, inc);
  }
  for (const k of Object.keys(b.library || {})) Object.assign((d.library[k] ||= {}), b.library[k]);
  return saveDB(d);
}
export function _resetForTest(){ _mem = null; }
