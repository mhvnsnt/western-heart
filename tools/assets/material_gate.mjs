#!/usr/bin/env node
// tools/assets/material_gate.mjs — CI gate: every model wired in MODEL_URLS
// (game/js/assets.js) must pass game/js/material-resolve.js auditGltf.
//   node tools/assets/material_gate.mjs [--json out.json] [--write-status]
// Reads GLBs straight from git (`git cat-file`) so sparse/partial checkouts work.
// --write-status regenerates game/js/material-status.js (the runtime
// resolve plans + quarantine list). The gate FAILS when:
//   * a model fails the audit and is not in material-status.json quarantine, or
//   * material-status.json is stale (lists a model that now passes / misses one that fails).
// Quarantined keys are never offered at character select or loaded into a
// fight (game/js/material-quarantine.js); they go back in by fixing the model.
// RUNTIME-TINTED TEMPLATE EXEMPTION (owner decision 2026-11-02, option A:
// "Narrow the gate rule for runtime-tinted template bodies" — NOT a rebake):
// the 9 Creation Suite template bodies below ship MB-Lab materials with no
// baked base-colour texture; their skin colour is applied at runtime by
// createInstance (custom fighter, colorize: true, tintStrength 0.3). An
// "untextured"-only failure on exactly these keys, at exactly their
// customization/templates/meshes/*.glb URLs, is therefore expected, not
// broken. Missing or placeholder verdicts are NEVER exempted, and no other
// key or URL is exempted.
const RUNTIME_TINTED_TEMPLATES = new Map([
  ['custom-template-super-heavyweight', '../customization/templates/meshes/super-heavyweight.glb'],
  ['custom-template-powerhouse', '../customization/templates/meshes/powerhouse.glb'],
  ['custom-template-showman', '../customization/templates/meshes/showman.glb'],
  ['custom-template-technician', '../customization/templates/meshes/technician.glb'],
  ['custom-template-highflyer', '../customization/templates/meshes/highflyer.glb'],
  ['custom-template-luchador', '../customization/templates/meshes/luchador.glb'],
  ['custom-template-powerhouse-w', '../customization/templates/meshes/powerhouse-w.glb'],
  ['custom-template-athletic-w', '../customization/templates/meshes/athletic-w.glb'],
  ['custom-template-striker-w', '../customization/templates/meshes/striker-w.glb'],
]);
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { auditGltf, parseGlb, donorPlan, authoredFlat } from '../../game/js/material-resolve.js';

const root = execFileSync('git', ['rev-parse', '--show-toplevel']).toString().trim();
const args = process.argv.slice(2);
const src = fs.readFileSync(path.join(root, 'game/js/assets.js'), 'utf8');
const block = src.slice(src.indexOf('MODEL_URLS = {'), src.indexOf('\n};', src.indexOf('MODEL_URLS = {')));
const keys = [...block.matchAll(/^\s*'?([\w-]+)'?:\s*'([^']+\.glb)'/gm)].map(m => ({ key: m[1], url: m[2] }));
const repoPath = u => path.posix.normalize(path.posix.join('game', u));
const blob = p => execFileSync('git', ['cat-file', 'blob', `HEAD:${p}`], { cwd: root, maxBuffer: 2 ** 31 });
const tracked = new Set(execFileSync('git', ['ls-files'], { cwd: root, maxBuffer: 2 ** 28 }).toString().split('\n'));

const results = {};
for (const { key, url } of keys) {
  const p = repoPath(url);
  if (!tracked.has(p)) { results[key] = { url, ok: false, error: 'file not in repo' }; continue; }
  try {
    const { json, binLength } = parseGlb(new Uint8Array(blob(p)));
    const a = auditGltf(json, { binLength, fileExists: u => tracked.has(path.posix.join(path.posix.dirname(p), u)) });
    results[key] = { url, ok: a.ok, counts: a.counts, t7: a.t7, findings: a.findings.slice(0, 8).map(f => `${f.verdict}: ${f.where} ${f.why}`) };
  } catch (e) { results[key] = { url, ok: false, error: String(e.message || e) }; }
}
// Same-model donor resolve: a textureless re-export of a part set that another
// wired model carries WITH textures is resolved at load (runtime) from that donor.
const jsonCache = {};
const jsonOf = (key) => {
  if (!(key in jsonCache)) { const p = repoPath(results[key].url);
    try { jsonCache[key] = parseGlb(new Uint8Array(blob(p))).json; } catch { jsonCache[key] = null; } }
  return jsonCache[key];
};
const resolve = {};
for (const key of Object.keys(results).filter(k => !results[k].ok && !results[k].error)) {
  const t = jsonOf(key); if (!t) continue;
  let best = null;
  // donor = the SAME model family only (pantera_alt1 / pantera-body -> pantera), never another attire
  const stem = key.replace(/(_alt\d+|-body|-legacy)$/, '');
  for (const d of [stem, stem + '_alt1', stem + '-attire1']) {
    if (!results[d]) continue;
    if (d === key || !results[d].ok || results[d].url === results[key].url) continue;
    const dj = jsonOf(d); if (!dj) continue;
    const plan = donorPlan(t, dj);
    if (plan && plan.complete) { best = { donor: d, map: plan.map }; break; }
  }
  if (best) { resolve[key] = best; results[key].ok = true; results[key].resolvedFrom = best.donor; }
}
// Runtime-tinted templates: untextured-only failures at their exact template
// URLs pass the gate (see RUNTIME_TINTED_TEMPLATES above). Missing or
// placeholder verdicts still fail, as does any other key.
const runtimeTinted = [];
for (const [key, url] of RUNTIME_TINTED_TEMPLATES) {
  const r = results[key];
  if (!r || r.ok || r.error) continue;
  if (r.url !== url) continue;
  if (r.counts.missing === 0 && r.counts.placeholder === 0 && r.counts.untextured > 0) {
    r.ok = true; r.runtimeTinted = true; runtimeTinted.push(key);
  }
}
// OWNER OUTFIT-NOT-THE-GATE EXEMPTION (owner rule 2026-11-03: "if a fighter
// has no outfit textures, show her without the outfit — what matters is her
// skin texture, eyes, and hair; outfits can be added later from parts"):
// Megami's playable variant (model-rigged-nooutfit.glb) excludes the
// textureless 24_/25_ outfit + headgear shells, which never had textures in
// her source file. Her skin, eyes and hair are textured from her own source
// (audit ok prims). The remaining untextured findings are source-faithful
// traits, enumerated in the landing PR: clear eye shells (EyeMoisture /
// Cornea, transparent by design), one hair-strand material (Bangs1-1 — no
// strand texture exists in any copy of her source), the inner Torso-6 shell
// (textureless in the source itself), and shoe / panties parts carrying
// authored near-black colours. An untextured-only failure on exactly these
// keys at exactly this URL is therefore expected, not broken. Missing or
// placeholder verdicts are NEVER exempted, any 24_/25_ material still in
// the file voids the exemption, and no other key or URL is exempted.
// FIDELITY REBUILD (2026-11-05): the loaded URL is now model-rigged.glb,
// rebuilt from the recovered commission blend. The 2026-11-03 premise was
// wrong about the source: in the blend the 24_/25_ outfit is FULLY
// textured (all seven 24_/25_ materials carry base textures in the
// rebuild) — the textureless shells were an artifact of the stripped
// 2026-10-23 conversion, not of her file. The exemption therefore now
// voids only on a TEXTURELESS 24_/25_ outfit material (a shell), not on
// the outfit's presence. The remaining untextured findings on the rebuild
// are the same source-faithful classes named above (EyeMoisture-3/-4,
// Cornea-2 clear shells; Torso-6 inner shell), verified in the landing PR.
const OWNER_OUTFIT_RULE_EXEMPT = new Map([
  ['megami', '../roster/parvati/attires/attire1/model-rigged.glb'],
  ['megami-attire1', '../roster/parvati/attires/attire1/model-rigged.glb'],
]);
const ownerOutfitRule = [];
for (const [key, url] of OWNER_OUTFIT_RULE_EXEMPT) {
  const r = results[key];
  if (!r || r.ok || r.error) continue;
  if (r.url !== url) continue;
  if (!(r.counts.missing === 0 && r.counts.placeholder === 0 && r.counts.untextured > 0)) continue;
  const t = jsonOf(key); if (!t) continue;
  const usedMats = new Set();
  for (const m of t.meshes || []) for (const pr of m.primitives || []) if (pr.material !== undefined) usedMats.add(pr.material);
  const outfitLeft = [...usedMats].some(mi => {
    const mat = t.materials[mi];
    if (!mat || !/^2[45]_/.test(mat.name || '')) return false;
    const pb = mat.pbrMetallicRoughness || {};
    return !pb.baseColorTexture && !authoredFlat(pb.baseColorFactor);
  });
  if (outfitLeft) continue;
  r.ok = true; r.ownerOutfitRule = true; ownerOutfitRule.push(key);
}
const failing = Object.keys(results).filter(k => !results[k].ok).sort();
const statusPath = path.join(root, 'game/js/material-status.js');
const readStatus = () => { const t = fs.readFileSync(statusPath, 'utf8'); return JSON.parse(t.slice(t.indexOf('{'), t.lastIndexOf('}') + 1)); };
if (args.includes('--write-status')) {
  const q = {};
  for (const k of failing) q[k] = results[k].error || Object.entries(results[k].counts).filter(([v, n]) => v !== 'ok' && n).map(([v, n]) => `${n} ${v}`).join(', ');
  fs.writeFileSync(statusPath, '// GENERATED by tools/assets/material_gate.mjs --write-status — do not hand-edit.\n' +
    'export const MATERIAL_STATUS = ' + JSON.stringify({ format: 'wh-material-status/1',
    note: 'GENERATED by tools/assets/material_gate.mjs --write-status. Keys here failed the material audit and are kept out of select + fight until fixed.',
    resolve, quarantine: q }, null, 1) + ';\n');
}
if (args.includes('--json')) fs.writeFileSync(args[args.indexOf('--json') + 1], JSON.stringify(results, null, 1));
const statusFile = fs.existsSync(statusPath) ? readStatus() : {};
const status = statusFile.quarantine || {};
const resolveStale = JSON.stringify(statusFile.resolve || {}) !== JSON.stringify(resolve);
if (resolveStale) console.log('::error::material-status.json resolve plans are stale — rerun with --write-status');
const leak = failing.filter(k => !(k in status));
const stale = Object.keys(status).filter(k => !failing.includes(k));
console.log(`material gate: ${keys.length} keys, ${keys.length - failing.length - Object.keys(resolve).length - runtimeTinted.length - ownerOutfitRule.length} pass as-is, ${Object.keys(resolve).length} resolved from a same-model donor, ${runtimeTinted.length} runtime-tinted templates exempted (untextured-only), ${ownerOutfitRule.length} owner outfit-rule exempted (untextured-only, outfit shells excluded), ${failing.length} quarantined`);
for (const k of leak) console.log(`::error::${k} (${results[k].url}) has broken materials and is NOT quarantined: ${results[k].error || results[k].findings.join(' | ')}`);
for (const k of stale) console.log(`::error::${k} is quarantined but now passes or is gone — rerun with --write-status`);
process.exit(leak.length || stale.length || resolveStale ? 1 : 0);
