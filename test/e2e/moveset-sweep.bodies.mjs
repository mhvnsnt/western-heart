// Moveset id -> the WH roster fighter body it is played on (owner 2026-10-28: armor-king is
// YUKIHYO, never zen). Order: a roster fighter with a model; '<id>-attireN' on its roster
// fighter's attire model; the roster fighter whose CANON base is this moveset's fighter;
// the roster fighter this id is a variant of (burger-demon -> burger); the moveset's own
// roster/<id> model. Every model file must exist on disk. Without one the row says where the
// source lives: 'needs rescan/GLB' (a source exists) or no model found (searched roster/,
// MODEL_URLS, lab T3 bakes, teardown/ incl. T7, and the GRE pulls).
import fs from 'node:fs';
const root = new URL('../../', import.meta.url);
const { FULL_ROSTER } = await import(new URL('game/js/roster-full.js', root));
const src = fs.readFileSync(new URL('game/js/assets.js', root), 'utf8');
const URLS = {}; for (const m of src.matchAll(/^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'/gm)) URLS[m[1]] ??= m[2];
const norm = (s) => String(s || '').toLowerCase().replace(/\(.*?\)/g, '').replace(/[^a-z0-9]/g, '');
const onDisk = (k) => !!URLS[k] && fs.existsSync(new URL('game/' + URLS[k].replace(/^\.\//, ''), root));
const MODEL_ALIAS = { gyou: 'gyou-spirit', 'gyou-spirit-body': 'gyou-spirit' }; // roster/gyou spirit form
const ROSTER_ALIAS = { jin_soul: 'phantom' }; // JIN folded into Phantom's ladder (roster-full.js tier note)
// Owner rule: a roster fighter plays on its attire-1 model (roster_map.json attires slot 1),
// which is what the game loads (e.g. kingtyrant -> king-tyrant-attire1, baek-master-white -> kevin-tripo).
const RMAP = JSON.parse(fs.readFileSync(new URL('game/data/roster_map.json', root), 'utf8'));
const A1 = {}; for (const f of (Array.isArray(RMAP) ? RMAP : RMAP.fighters || [])) { const a = (f.attires || []).find((x) => x.slot === 1); if (a && a.model) A1[f.id] = a.model; }
const M = (model, how, rosterId = null) => ({ rosterId, model, how, ok: onDisk(model), file: URLS[model] || null });
export function bodyFor(id, meta = {}) {
  const names = [meta.tekken_base, meta.display, meta.name].filter(Boolean);
  const has = (f) => f && f.model && onDisk(f.model);
  const exact = FULL_ROSTER.find((f) => f.id === id);
  if (MODEL_ALIAS[id]) return M(MODEL_ALIAS[id], `roster/${id.split('-')[0]} spirit model`, exact ? id : null);
  if (exact && A1[id] && onDisk(A1[id])) return M(A1[id], 'roster attire 1', id);
  if (has(exact)) return M(exact.model, 'roster id', id);
  // A roster fighter with no model never plays on another fighter's body (main.js MODEL PENDING rule).
  if (exact) return { rosterId: id, model: null, ok: false, how: 'roster fighter is modelPending; no file in roster/, teardown/ (T3/T7), or GRE pulls', file: null };
  // A guest with its own roster/<id> model plays on it, unless its CANON.md marks it OBSOLETE
  // (armor-king -> YUKIHYO, roster/armor-king/CANON.md).
  const canon = new URL(`roster/${id}/CANON.md`, root), obsolete = fs.existsSync(canon) && /OBSOLETE/.test(fs.readFileSync(canon, 'utf8').slice(0, 400));
  if (!obsolete && onDisk(id) && fs.existsSync(new URL('roster/' + id, root))) return M(id, `own roster/${id} model`);
  const att = /^(.*)-(attire\d)$/.exec(id); if (att && onDisk(id)) return M(id, `${att[2]} of roster '${att[1]}'`, att[1]);
  if (ROSTER_ALIAS[id]) { const f = FULL_ROSTER.find((x) => x.id === ROSTER_ALIAS[id]); if (has(f)) return M(f.model, 'roster alias', f.id); }
  const base = FULL_ROSTER.find((f) => has(f) && (names.some((n) => norm(f.base) === norm(n)) || norm(f.base) === norm(id)));
  if (base) return M(base.model, `roster base '${base.base}'`, base.id);
  const pre = FULL_ROSTER.filter((f) => has(f) && norm(id).startsWith(norm(f.id)) && norm(f.id).length >= 3).sort((a, b) => b.id.length - a.id.length)[0];
  if (pre) return M(pre.model, `variant of roster '${pre.id}'`, pre.id);
  if (onDisk(id) && fs.existsSync(new URL('roster/' + id, root))) return M(id, `own roster/${id} model`);
  const t3 = meta.t3_source && [`lab/game/assets/t3_${meta.t3_source}_t3real.glb`, `lab/game/assets/t3_${meta.t3_source}.glb`].find((q) => fs.existsSync(new URL(q, root)));
  const own = id.replace(/^(t3|sf|doa|vf)-/, '');
  const pose = fs.existsSync(new URL(`teardown/tekken3/renders/pose-check/${own}_stance75.obj`, root)) ? `teardown/tekken3/renders/pose-check/${own}_stance75.obj` : null;
  if (id.startsWith('t3-') && onDisk(id)) return M(id, 'T3 teardown rig GLB (private lab/)');
  if (pose || (t3 && id.startsWith('t3-'))) return { rosterId: exact ? id : null, model: null, ok: false, how: 'needs rescan/GLB (T3 teardown source only, no rigged game model)', file: [t3, pose].filter(Boolean).join(' + ') };
  if (/^sf-/.test(id)) return { rosterId: null, model: null, ok: false, how: 'no model on box (source URLs only)', file: 'teardown/street-fighter-5/CAST-STATUS.md' };
  return { rosterId: exact ? id : null, model: null, ok: false, how: exact ? 'roster fighter is modelPending; no file in roster/, teardown/ (T3/T7), or GRE pulls' : 'no model found in roster/, MODEL_URLS, teardown/ (T3/T7), or GRE pulls', file: t3 ? `moveset bakes from ${t3}` : null };
}
export { FULL_ROSTER };
