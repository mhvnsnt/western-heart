#!/usr/bin/env node
/* Builds game/data/creation-suite/move-catalog.json — the one searchable
   move list the Creation Suite MOVESET editor and MOVE CREATOR pick from.
   Every row comes from a file already in this repo (no invented moves):
     tekken    game/assets/movesets/<fighter>.json  (T8/T7 frame data on T3-decoded rows)
     t3        game/data/moveset-library/banks/t3.json
     nomercy   game/data/moveset-library/banks/wrestling.json (WWF No Mercy mat-kings DB)
     wmxix     game/data/moveset-library/banks/wmxix.json (WWE WrestleMania XIX YANM clips)
     doa/vf/vf5 game/data/moveset-library/banks/*.json (federation conversions)
     2k19      customization/wwe2k-caw/moveset-library-2k19.txt (createmode.pac string table:
               NAMES ONLY — animation blobs not decoded yet, so rows are flagged anim:null)
   Row: {id, n, g(game), by(fighter/character), c(category), in(input), f:[startup,active,recovery] frames,
         d(damage), k(knock), l(limb), a(anim ref "bank:row" or null), x(flags)}
   Usage: node tools/creation-suite/build_move_catalog.mjs */
import fs from 'node:fs'; import path from 'node:path';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const rd = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const rows = []; const seen = new Set();
const F = s => (s == null ? null : Math.round(s * 60));
function push(r){ if (seen.has(r.id)) return; seen.add(r.id); rows.push(r); }

/* Category = the WWE 2K19 Create-A-Moveset slot family the move fits, plus
   the Tekken command-list families for our fighting game. */
export function categorize({ name = '', type = '', position = '', input = '', mk = '', cls = '' }){
  const n = (name + ' ' + mk).toLowerCase(), i = String(input || '');
  if (/kesshou|決勝/.test(n)) return 'KESSHOU';
  if (/soul release|九魂/.test(n)) return 'SOUL_RELEASE';
  if (/reihou|霊放/.test(n)) return 'REIHOU';
  if (/trial'?s seal|試練/.test(n)) return 'TRIALS_SEAL';
  if (/spirit action|魂/.test(n) || /^H\./.test(i)) return 'SPIRIT';
  if (/rage art|rage drive/.test(n) || /^R[D]?\./.test(i)) return 'RAGE';
  if (/taunt|victory|pose|celebrat/.test(n)) return 'TAUNT';
  if (/finisher|special grapple|special ground|special irish|master move/.test(n)) return 'FINISHER';
  if (/counter|reversal|parry/.test(n) || type === 'counter') return 'REVERSAL';
  if (/turnbuckle|corner|avalanche/.test(n) || position === 'corner') return 'CORNER';
  if (/apron|ringside|barricade/.test(n)) return 'APRON';
  if (/flying|diving|top rope|splash|senton|moonsault|450|630|springboard|frog/.test(n) || type === 'aerial' || position === 'airborne') return 'AERIAL';
  if (/irish whip|running|spear|rebound/.test(n) || position === 'running') return 'RUNNING';
  if (/ground|laying|sitting|mount|facing (up|down)/.test(n) || position === 'grounded') return 'GROUND';
  if (/back (strong|weak|special|grapple|running)|from behind|rear/.test(n)) return 'BACK_GRAPPLE';
  if (/lock|stretch|choke|crab|submission|hold|clutch|crossface|sharpshooter|armbar/.test(n)) return 'SUBMISSION';
  if (type === 'grapple' || type === 'throw' || cls === 'throw' || /grapple|suplex|slam|driver|bomb|ddt|neckbreaker|backbreaker|throw|piledriver/.test(n)) return type === 'throw' || cls === 'throw' ? 'THROW' : 'FRONT_GRAPPLE';
  if (cls === 'string' || /,/.test(i)) return 'STRING';
  return 'STRIKE';
}

// 1) Tekken per-fighter movesets (the real playable lists)
const msDir = path.join(ROOT, 'game/assets/movesets');
for (const f of fs.readdirSync(msDir).filter(f => f.endsWith('.json') && !f.startsWith('_') && f !== 'index.json')) {
  let ms; try { ms = rd('game/assets/movesets/' + f); } catch { continue; }
  if (!ms || !ms.moves) continue;
  const fid = ms.fighter || f.replace(/\.json$/, '');
  for (const [key, mv] of Object.entries(ms.moves)) {
    if (!mv || key.includes('__')) continue;
    const t7 = mv.t7 && mv.t7.wired ? mv.t7 : null;
    let c = categorize({ name: mv.name, input: mv.input || key, cls: mv.move_class });
    if (mv.launch && c === 'STRIKE') c = 'LAUNCHER';
    const x = []; if (mv.isGrab) x.push('grab'); if (mv.launch) x.push('launch'); if (mv.heavy) x.push('heavy'); if (ms.proxy) x.push('proxy');
    push({ id: `tekken:${fid}:${key}`, n: mv.name || key, g: t7 ? 'tekken7' : 'tekken3', by: fid, key, c, in: mv.input || key,
      f: [F(mv.startup), F(mv.active), F(mv.recovery)], d: mv.damage ?? null, k: mv.knock ?? null, l: mv.limb || null,
      a: mv.t3_row != null ? `${mv.t3_source || ms.t3_source}:${mv.t3_row}` : (mv.anim_t3 ? `${mv.anim_t3.bank}:${mv.anim_t3.row}` : null),
      hl: (t7 && t7.hit_level) || mv.hit_level || null, x });
  }
}
// 2) Moveset-library banks
const GAME = { wrestling: 'nomercy', wmxix: 'wmxix', t3: 'tekken3', doa: 'doa', vf: 'vf', vf5: 'vf5' };
for (const b of Object.keys(GAME)) {
  let d; try { d = rd(`game/data/moveset-library/banks/${b}.json`); } catch { continue; }
  for (const mv of d.moves) {
    const fr = mv.frames || {};
    const a = /^t3:([a-z]+):row:(\d+)$/.exec(mv.anim_ref || '');
    push({ id: mv.id, n: mv.name, g: GAME[b], by: mv.source_character || null,
      c: categorize({ name: mv.name, type: mv.type, position: mv.position, input: mv.input, mk: (mv.provenance || {}).mk_category || '' }),
      in: mv.input || null, f: [fr.startup ?? null, fr.active ?? null, fr.recovery ?? null], tf: fr.total ?? null, d: mv.damage ?? null,
      k: (mv.wh || {}).knock ?? null, l: mv.limb || null, a: a ? `${a[1]}:${a[2]}` : null, src: mv.anim_ref || null,
      mk: (mv.provenance || {}).mk_category || undefined, x: [] });
  }
}
// 3) WWE 2K19 Create-A-Moveset names (createmode.pac string table)
const txt = fs.readFileSync(path.join(ROOT, 'customization/wwe2k-caw/moveset-library-2k19.txt'), 'utf8').split('\n').map(s => s.trim()).filter(Boolean);
txt.forEach((n, i) => push({ id: `2k19:${i}`, n, g: '2k19', by: null, c: categorize({ name: n }), in: null, f: [null, null, null], d: null, k: null, l: null, a: null, x: ['name-only'] }));

const counts = {}; for (const r of rows) { counts[r.g] = (counts[r.g] || 0) + 1; }
const cats = {}; for (const r of rows) cats[r.c] = (cats[r.c] || 0) + 1;
const out = { schema: 'wh-move-catalog/v1', built: new Date().toISOString().slice(0, 10), builder: 'tools/creation-suite/build_move_catalog.mjs',
  honesty: '2k19 rows are names only (anim:null) until the createmode/motion pacs are decoded; t3/nomercy/wmxix labels keep their bank name_status.',
  counts, categories: cats, rows };
const dst = path.join(ROOT, 'game/data/creation-suite/move-catalog.json');
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.writeFileSync(dst, JSON.stringify(out));
console.log('rows', rows.length, counts, cats, (fs.statSync(dst).size / 1e6).toFixed(2) + ' MB');
