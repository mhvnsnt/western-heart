/* ============================================================
   WESTERN HEART — Studio consumers (the real game reads studio saves)
   - applyPoseOverlay(): additive per-bone rotation on top of whatever
     the mixer wrote this frame (Tekken bank stance stays the base; the
     studio pose rides on top — Bannon poseStudio's J[j].set on a rig).
   - applyCharOverrides(): AI DNA + strike tuning onto the fighter's
     real aiProfile/stats (clamped to the game's own limits).
   ============================================================ */
import { getFighterData, clamp } from './studio-store.js';

export function normBone(n){ return String(n||'').replace(/^mixamorig[:_]?/i,'').replace(/[^a-z0-9]/gi,'').toLowerCase(); }
const ALIASES = { spine1:['spine1','spine2','chest','upperchest'], spine:['spine','waist'], hips:['hips','pelvis','root'] };

export function boneIndex(model){
  const idx = {};
  model && model.traverse(o => { if (o.isBone) { const k = normBone(o.name); if (!idx[k]) idx[k] = o; } });
  return idx;
}
export function findBone(idx, joint){
  const k = normBone(joint);
  if (idx[k]) return idx[k];
  for (const a of (ALIASES[k] || [])) if (idx[a]) return idx[a];
  return null;
}
/* pose: { Joint: [rx, ry, rz] } radians. Works with any THREE build (uses
   the bone quaternion's own constructor family via setFromEuler on a clone). */
export function applyPoseOverlay(model, pose, weight = 1, cache){
  if (!model || !pose) return 0;
  if (cache && cache.model !== model) { cache.model = model; cache.idx = null; }
  const idx = (cache && cache.idx) || boneIndex(model); if (cache) cache.idx = idx;
  let n = 0;
  for (const j in pose) {
    const b = findBone(idx, j); const r = pose[j]; if (!b || !r) continue;
    const q = b.quaternion.clone();
    const e = new (b.rotation.constructor)(r[0]*weight, r[1]*weight, r[2]*weight, 'XYZ');
    q.setFromEuler(e); b.quaternion.multiply(q); n++;
  }
  return n;
}
export function studioPoseFor(id, slot){ const f = getFighterData(id); return f && f[slot] && Object.keys(f[slot]).length ? f[slot] : null; }

export function applyCharOverrides(fighter){
  const id = fighter && fighter.char && fighter.char.id; if (!id) return false;
  const f = getFighterData(id); if (!f) return false;
  if (f.ai) {
    const a = { ...(fighter.aiProfile || {}) };
    if (f.ai.aggression != null) a.aggression = clamp(f.ai.aggression, 0, 1);
    if (f.ai.grabBias != null) a.grabBias = clamp(f.ai.grabBias, 0, 1);
    if (f.ai.reaction != null) a.reaction = clamp(f.ai.reaction, 0, 1);
    for (const k of ['defense','patience','risk','range','showmanship']) if (f.ai[k] != null) a[k] = clamp(f.ai[k], 0, 1);
    fighter.aiProfile = a;
  }
  if (f.strike) {
    const s = { ...(fighter.stats || {}) };
    if (f.strike.power != null) s.power = clamp(f.strike.power, 0.8, 1.4);
    if (f.strike.speed != null) s.speed = clamp(f.strike.speed, 2.0, 3.5);
    fighter.stats = s;
  }
  fighter.studio = f; return true;
}
