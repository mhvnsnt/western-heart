// t133u: select portraits must exist, come from the fighter's ATTIRE-1 model
// (attires.js ladder, owner's own models first) and be posed in the fighter's
// own moveset-bank stance (not bind/T-pose). Data: game/assets/portraits/
// portraits-manifest.json, written by tools/portraits/capture.mjs.
// A fighter whose bank stance is rejected by the select fit gates may only
// pass while listed in tools/portraits/POSE-BLOCKERS.json (visible debt; the
// list must shrink, a fixed fighter left on it fails too).
//
// M2 (Roster-100 Wave 2, 2026-11-05): freshness gate. The checks above never
// compared PNG bytes, so 7 placeholder cards sharing one byte-identical dark
// PNG passed CI while the manifest claimed captures from other fighters'
// models (#1565 inventory). The section below hashes every top-level card
// and fails on: placeholder bytes outside the dated registry in
// tools/portraits/KNOWN-PLACEHOLDERS.json (exactly the L3 missing-model
// fighters; the registry must shrink as L3 lands — a registered fighter
// whose bytes changed fails too), any other byte-identical card group that
// is not a registered known-duplicate group, and any manifest entry that
// claims a capture model for a fighter who has no attire-1 model at all
// (the false-claim class), unless registered.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { FULL_ROSTER } from '../game/js/roster-full.js';
import { attiresFor } from '../game/js/attires.js';
const DIR = new URL('../game/assets/portraits/', import.meta.url);
const man = JSON.parse(fs.readFileSync(new URL('portraits-manifest.json', DIR))).fighters;
const blockers = JSON.parse(fs.readFileSync(new URL('../tools/portraits/POSE-BLOCKERS.json', import.meta.url))).blocked;
const src = fs.readFileSync(new URL('../game/js/select-screen.js', import.meta.url), 'utf8');
const hidden = new Set([...src.match(/SELECT_HIDDEN = new Set\(\[([^\]]*)\]/)[1].matchAll(/'([^']+)'/g)].map(m => m[1]));
// Material-quarantined fighters (no usable attire) are dropped from ROSTER
// (characters.js) so they never reach select; treat them as hidden here too.
for (const c of FULL_ROSTER) if (!attiresFor(c).length) hidden.add(c.id);
const fails = []; let n = 0;
for (const c of FULL_ROSTER) {
  if (hidden.has(c.id)) continue;
  n++;
  const want = attiresFor(c)[0].model, m = man[c.id];
  if (!fs.existsSync(new URL(`${c.id}.png`, DIR))) fails.push(`${c.id}: portrait png missing`);
  if (!m) { fails.push(`${c.id}: not in portraits-manifest (run tools/portraits/capture.mjs)`); continue; }
  if (m.error) fails.push(`${c.id}: capture error ${m.error}`);
  if (m.model !== want) fails.push(`${c.id}: portrait rendered from '${m.model}', attire-1 model is '${want}' (wrong model)`);
  if (!m.stance && !blockers[c.id]) fails.push(`${c.id}: portrait is bind/T-posed (bank '${m.bank}' stance not applied) and not listed in POSE-BLOCKERS.json`);
  if (m.stance && blockers[c.id]) fails.push(`${c.id}: stance now works - remove it from POSE-BLOCKERS.json`);
}
for (const id of Object.keys(blockers)) if (!FULL_ROSTER.some(c => c.id === id) || hidden.has(id)) fails.push(`POSE-BLOCKERS lists '${id}', not a select fighter`);

// ---- M2 freshness gate: card bytes vs registry + manifest claims ----
const reg = JSON.parse(fs.readFileSync(new URL('../tools/portraits/KNOWN-PLACEHOLDERS.json', import.meta.url)));
const phHash = reg.placeholderSha256, regIds = new Set(Object.keys(reg.placeholders));
const hashes = new Map();
for (const f of fs.readdirSync(DIR)) {
  if (!f.endsWith('.png')) continue;
  const u = new URL(f, DIR);
  if (!fs.statSync(u).isFile()) continue;
  hashes.set(f.slice(0, -4), crypto.createHash('sha256').update(fs.readFileSync(u)).digest('hex'));
}
for (const id of regIds) {
  if (!FULL_ROSTER.some(c => c.id === id)) fails.push(`KNOWN-PLACEHOLDERS lists '${id}', not a roster fighter`);
  if (hashes.get(id) !== phHash) fails.push(`${id}: registered placeholder but its card bytes changed - remove it from KNOWN-PLACEHOLDERS.json (the registry shrinks as L3 lands)`);
}
for (const [id, h] of hashes) if (h === phHash && !regIds.has(id)) fails.push(`${id}: portrait is the shared placeholder PNG but is not registered in KNOWN-PLACEHOLDERS.json`);
const byHash = new Map();
for (const [id, h] of hashes) byHash.set(h, [...(byHash.get(h) || []), id]);
const dupReg = new Map((reg.knownDuplicateGroups || []).map(g => [g.sha256, g.ids.slice().sort().join(',')]));
const dupIds = new Set((reg.knownDuplicateGroups || []).flatMap(g => g.ids));
for (const [h, ids] of byHash) {
  if (ids.length < 2) continue;
  const key = ids.slice().sort().join(',');
  if (h === phHash) {
    if (key !== [...regIds].sort().join(',')) fails.push(`placeholder-byte card group (${key}) does not match the KNOWN-PLACEHOLDERS registry`);
    continue;
  }
  if (dupReg.get(h) !== key) fails.push(`byte-identical portraits shared by ${key} - not the placeholder set and not a registered duplicate group in KNOWN-PLACEHOLDERS.json`);
}
for (const [h, want] of dupReg) {
  const got = (byHash.get(h) || []).slice().sort().join(',');
  if (got !== want) fails.push(`KNOWN-PLACEHOLDERS duplicate group (${want}) no longer shares bytes - remove or update that entry`);
}
for (const c of FULL_ROSTER) {
  const m = man[c.id];
  if (m && m.model && !attiresFor(c).length && !regIds.has(c.id) && !dupIds.has(c.id))
    fails.push(`${c.id}: portraits-manifest claims a capture from '${m.model}' but the fighter has no attire-1 model (false claim; register in KNOWN-PLACEHOLDERS.json only if it is the L3 placeholder class)`);
}

console.log(`portraits: ${n} select fighters, ${Object.keys(blockers).length} pose blockers, ${regIds.size} registered placeholders`);
if (fails.length) { console.error('FAIL\n  ' + fails.join('\n  ')); process.exit(1); }
console.log('PASS');
