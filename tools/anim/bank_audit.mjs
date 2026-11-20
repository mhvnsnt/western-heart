// tools/anim/bank_audit.mjs — which animation bank does every fighter bind, and is it their OWN character's?
//
// Owner 2026-11-07: "ur using incorrect banks for some characters and some have mixed banks on purpose but some should
// have fully one character banks and data unless it comes from Tekken code like that".
//
// For every roster fighter, through the game's own modules: the canon base (roster-full.js `base`), the bank the game
// binds (fighter.js bankIdFor), the T7 stance / move dirs (t3anims.js T7_STANCES / T7_MOVES), and every bank of the
// base character that exists on disk (T3 / own-rig / TTT2 `<name>/` or `<name>_ttt2/` / T7 dirs), with the action slots
// each one covers. A fighter is flagged when it binds another character's bank while its own exists.
//
//   node tools/anim/bank_audit.mjs [--json out.json] [--md out.md]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
await import(path.join(ROOT, 'tools/anim/node_game_env.mjs'));
const quiet = console.log;
console.log = () => {}; console.warn = () => {};
const M = await import(path.join(ROOT, 'game/js/movesets.js'));
const F = await import(path.join(ROOT, 'game/js/fighter.js'));
const T = await import(path.join(ROOT, 'game/js/t3anims.js'));
const { FULL_ROSTER } = await import(path.join(ROOT, 'game/js/roster-full.js'));
await M.loadFighterMovesets();
await M.ensureMovesets(FULL_ROSTER.map((c) => c.id));
console.log = quiet;

// Canon base (roster-full `base`) -> the bank directory names that hold THAT character's own motion.
// T3 = Tekken 3 divmot banks, TTT2 = Fill 3 banks (docs/tech/ttt2-mota/join/FILL3-BANKS.md; a name that collides with a
// T3 bank lands as <name>_ttt2), T7 = game/assets/anim/t7/<dir>.
export const BASE_BANKS = {
  'Jin Kazama': { t3: ['jin', 'jin_ttt2'], t7: [] }, 'Paul Phoenix': { t3: ['paul', 'paul_ttt2'] },
  Xiaoyu: { t3: ['xiaoyu', 'lin_xiaoyu'], t7: ['xiaoyu'] }, 'Eddy Gordo': { t3: ['eddy', 'eddy_ttt2'] },
  'Bryan Fury': { t3: ['bryan', 'bryan_ttt2'], t7: ['bryan'] }, Hwoarang: { t3: ['hwoarang', 'hwoarang_ttt2'], t7: ['hwoarang'] },
  King: { t3: ['king'], t7: ['king'] }, Yoshimitsu: { t3: ['yoshimitsu', 'yoshimitsu_ttt2'], t7: ['yoshimitsu'] },
  Heihachi: { t3: ['heihachi', 'heihachi_ownrig', 'heihachi_ttt2'], t7: ['heihachi'] }, 'Jack-7': { t3: ['gunjack', 'jack'] },
  'Steve Fox': { t3: ['steve_fox'] }, Asuka: { t3: ['asuka'] }, Josie: { t3: [] }, Bob: { t3: ['bob_satsuma'], t7: ['bob'] },
  Nina: { t3: ['nina', 'nina_ttt2'] }, Shaheen: { t3: [] }, Lee: { t3: ['lee'], t7: ['lee'] }, Julia: { t3: ['julia', 'julia_ttt2'], t7: ['julia'] },
  Akuma: { t3: [] }, Alisa: { t3: ['alisa'] }, Katarina: { t3: [] }, Christie: { t3: ['christie'] }, Anna: { t3: ['anna', 'anna_ttt2'] },
  Miguel: { t3: ['miguel'] }, Negan: { t3: [], t7: ['negan'] }, Ganryu: { t3: ['ganryu'] }, 'Armor King': { t3: ['armorking', 'armor_king'] },
  Dragunov: { t3: ['dragunov'] }, Bosconovitch: { t3: ['bosconovitch', 'bosconovitch_ttt2'] }, Kevin: { t3: [] },
  Zafina: { t3: ['zafina'] }, Mokujin: { t3: [] }, Gon: { t3: ['gon'] }, 'True Ogre': { t3: ['ogre'] }, Raven: { t3: ['raven'], t7: ['raven'] },
  'Lucky Chloe': { t3: ['luckychloe'], t7: ['luckychloe'] }, 'Jun Kazama': { t3: ['jun'] }, 'Roger Jr.': { t3: ['roger'] },
  'Lei Wulong': { t3: ['lei', 'lei_wulong'] }, 'Marshall Law': { t3: ['law', 'law_ttt2'] }, Lars: { t3: ['lars'], t7: ['lars'] },
  Kuma: { t3: ['kuma', 'kuma_ttt2'], t7: ['kuma'] }, Panda: { t3: ['panda'], t7: ['panda'] }, Lili: { t3: ['emilie'] },
  'Wang Jinrei': { t3: ['wang'] }, 'Undertaker (WWE)': { t3: [] }, 'Bass Armstrong': { t3: [] },
  // non-Tekken bases: no Tekken bank of their own can exist; a stand-in is by necessity
  Blanka: { t3: [] }, 'Zangief + Golem': { t3: [] }, 'Iori Yagami': { t3: [] }, 'Ryuji Yamazaki': { t3: [] },
  'Ryuji Yamazaki + The Rock': { t3: [] }, 'Kakashi + Super Saiyan': { t3: [] },
};
// Owner rulings that override the base field (fighter.js FIGHTER_BANK notes): Zen is neither Heihachi nor Julia
// (2026-10-24, docs/decisions/2026-10-24-zen-base-decision.md) and stays unmapped in public builds.
const OWNER_RULED = { zen: 'owner ruling 2026-10-24: unmapped (not Heihachi); VF5 Dural bank in private builds only' };
const T3_DIR = path.join(ROOT, 'game/assets/anim/t3');
const slotsOf = (dir) => { try { return fs.readdirSync(path.join(T3_DIR, dir)).filter((f) => /^t3_.*\.json$/.test(f)).map((f) => f.slice(3, -5)); } catch { return null; } };
const KEY = ['neutral', 'stance', 'walk_fwd', 'walk_back', 'light', 'medium', 'heavy', 'block', 'hit', 'ko'];
const bankDirOf = (bank) => (T.T3_BANKS[bank] || '').replace(/^assets\/anim\/t3\//, '').replace(/\/$/, '');

const rows = [];
for (const c of FULL_ROSTER) {
  let bank = null; try { bank = F.bankIdFor(c.id, c.moveset || c.id); } catch (e) { bank = 'ERR'; }
  const own = BASE_BANKS[c.base] || null;
  const ownT3 = own ? own.t3.map((d) => ({ dir: d, slots: slotsOf(d) })).filter((x) => x.slots) : [];
  const boundDir = bank ? bankDirOf(bank) : null;
  const boundIsOwn = !!bank && !!own && own.t3.some((d) => d === bank || d === boundDir || bankDirOf(d) === boundDir);
  const t7s = T.T7_STANCES[c.id] || null;
  const t7m = T.T7_MOVES[c.id] || null;
  let verdict;
  if (OWNER_RULED[c.id]) verdict = OWNER_RULED[c.id];
  else if (c.modelPending) verdict = 'no model (pending)';
  else if (!own) verdict = 'base not in BASE_BANKS (add it)';
  else if (!own.t3.length && !(own.t7 || []).length) verdict = 'no own bank exists (stand-in by necessity)';
  else if (boundIsOwn) verdict = 'OWN';
  else if (!ownT3.length && (t7s || t7m)) verdict = 'own T7 stance' + (t7m ? ' + moves' : '') + '; no own action bank exists, actions on stand-in ' + bank;
  else verdict = 'STAND-IN while own exists: ' + ownT3.map((x) => `${x.dir}(${KEY.filter((k) => x.slots.includes(k)).length}/${KEY.length} key slots)`).join(' ');
  const cand = (F.OWN_SLOT_CANDIDATES || {})[c.id] || null;
  const active = (F.OWN_SLOT_BANKS || {})[c.id] || null;
  rows.push({ id: c.id, base: c.base || null, bank, t7stance: t7s && t7s.dir, t7moves: t7m && t7m.dir, own: ownT3,
    ownSlots: active ? `${active} (active)` : cand ? `${cand} (candidate, not active)` : null, verdict });
}
const md = ['# Bank audit (`tools/anim/bank_audit.mjs`)', '',
  'Key slots counted: ' + KEY.join(', ') + '.', '',
  '| fighter | canon base | bound bank | T7 stance | T7 moves | own-slot bank (fighter.js) | verdict |', '|---|---|---|---|---|---|---|',
  ...rows.map((r) => `| ${r.id} | ${r.base || '—'} | ${r.bank || '—'} | ${(r.t7stance || '—').replace('assets/anim/t7/', '')} | ${(r.t7moves || '—').replace('assets/anim/t7/', '')} | ${r.ownSlots || '—'} | ${r.verdict} |`)].join('\n') + '\n';
if (opt('--json')) fs.writeFileSync(opt('--json'), JSON.stringify(rows, null, 1));
if (opt('--md')) fs.writeFileSync(opt('--md'), md);
quiet(md);
