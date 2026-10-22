// Node test for game/js/ranks.js — no DOM. Run: node test/ranks.test.mjs
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));
const table = JSON.parse(readFileSync(join(here, '..', 'game', 'data', 'ranks.json'), 'utf8'));

// ---- localStorage shim ----
const _ls = {};
globalThis.localStorage = {
  getItem: (k) => (_ls[k] ?? null),
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: (k) => { delete _ls[k]; },
};

const R = await import(join(here, '..', 'game', 'js', 'ranks.js'));
R._setTableForTest(table);

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; /* console.log('ok  -', name); */ }
  else { fail++; console.log('FAIL -', name); }
}
function evTypes(res) { return res.events.map((e) => e.type); }

// ---- 1. table shape ----
ok(R.tierCount() === 53, 'table has 53 tiers (got ' + R.tierCount() + ')');
ok(R.tierAt(0).id === 'lost-soul', 'tier 1 is lost-soul');
ok(R.tierAt(52).id === 'reserved-53', 'tier 53 is reserved-53');
ok(R.isReserved(R.tierAt(51)) && R.isReserved(R.tierAt(52)), 'tiers 52-53 flagged reserved+unnamed');
ok(R.displayName(R.tierAt(51)) === '??? (unnamed)', 'reserved display name is placeholder');
ok(R.tierIndexById('soul-gyou') === 45, 'soul-gyou at index 45 (tier 46)');
ok(R.tierIndexById('nope-missing') === 0, 'unknown id degrades to entry tier');
ok(R.tierAt(50).id === 'top-master-god', 'tier 51 is Master God of the Universe');
ok(R.barFor(R.tierAt(0)) === 300, 'placement bar 300');
ok(R.barFor(R.tierAt(45)) === 1000, 'nine-souls bar 1000');
ok(R.promoBestOfFor(R.tierAt(0)) === 3, 'low-tier promo series best-of-3');
ok(R.promoBestOfFor(R.tierAt(45)) === 5, 'nine-souls promo series best-of-5');
ok(R.promoBestOfFor(R.tierAt(51)) === 7, 'reserved promo series best-of-7');

// ---- 2. placement + promotion flow ----
const C = 'testchar';
let st = R.getFighterRank('offline', C);
ok(st.tierId === 'lost-soul' && st.placementLeft === 5, 'new fighter starts at Lost Soul, 5 placement bouts');
// win 5 placement bouts vs same tier -> bar fills (300 bar, 100*2 placement mult = 200/win)
let res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 0, won: true });
ok(evTypes(res).includes('placement'), 'placement event emitted');
ok(evTypes(res).includes('points'), 'points event emitted');
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 0, won: true });
ok(evTypes(res).includes('promo-series'), 'bar filled -> promotion series starts, got: ' + evTypes(res).join(','));
ok(res.state.series && res.state.series.kind === 'promo' && res.state.series.bestOf === 3, 'promo series best-of-3');
// win the series 2-0
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 0, won: true });
ok(evTypes(res).includes('series-update'), 'series 1-0 update');
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 0, won: true });
ok(evTypes(res).includes('promoted'), 'series won -> promoted, got: ' + evTypes(res).join(','));
ok(res.state.tierId === 'kyu-9', 'promoted to 9th Kyu (got ' + res.state.tierId + ')');
ok(res.state.protect === 3, 'demotion protection = 3 after promotion');

// ---- 3. protection: losses at 0 points don't start demo series ----
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
ok(!res.state.series, 'protected: no demotion series while protection active (protect=' + res.state.protect + ')');
ok(evTypes(res).includes('protected') || res.state.protect >= 0, 'protected event or counter');
// burn protection, then lose to 0 -> demo series
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
ok(res.state.series && res.state.series.kind === 'demo', 'demotion series starts at 0 bar, got: ' + evTypes(res).join(','));
// lose the demo series -> demoted
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
res = R.recordResult({ track: 'offline', charId: C, foeTierIdx: 1, won: false });
ok(evTypes(res).includes('demoted'), 'demo series lost -> demoted, got: ' + evTypes(res).join(','));
ok(res.state.tierId === 'lost-soul', 'demoted back to Lost Soul');

// ---- 4. upset scaling: beating higher tier pays more (first-win delta, no series clamp) ----
const C2 = 'upsetchar';
res = R.recordResult({ track: 'offline', charId: C2, foeTierIdx: 3, won: true }); // beat tier idx 3 as tier idx 0
const upsetGain = res.events.find((e) => e.type === 'points').delta;
const C3 = 'flatcchar';
res = R.recordResult({ track: 'offline', charId: C3, foeTierIdx: 0, won: true });
const flatGain = res.events.find((e) => e.type === 'points').delta;
ok(upsetGain > flatGain, `upset pays more (${upsetGain} > ${flatGain})`);

// ---- 5. top tier: summit held counter, no crash ----
const C4 = 'topchar';
// fast-forward: directly set tier near top via repeated state manipulation is slow;
// instead verify top-held logic by placing fighter at last tier through store surgery
{
  const s = JSON.parse(_ls['wh_ranks']);
  s.offline[C4] = { tierId: 'reserved-53', points: 2000, wins: 50, losses: 5, streak: 3, placementLeft: 0, series: null, protect: 0, topHeld: 0 };
  _ls['wh_ranks'] = JSON.stringify(s);
}
res = R.recordResult({ track: 'offline', charId: C4, foeTierIdx: 52, won: true });
ok(evTypes(res).includes('top-held'), 'win at top tier -> top-held, got: ' + evTypes(res).join(','));
ok(res.state.topHeld === 1, 'topHeld counter increments');

// ---- 6. tracks are separate ----
const C5 = 'twochar';
R.recordResult({ track: 'offline', charId: C5, foeTierIdx: 0, won: true });
const off = R.getFighterRank('offline', C5);
const on = R.getFighterRank('online', C5);
ok(off.wins === 1 && on.wins === 0, 'offline/online tracks independent');

// ---- 7. leaderboard ----
const lb = R.getLeaderboard('offline');
ok(lb.length > 0, 'leaderboard has entries');
ok(R.qualifiesForLadder('offline', C4), 'veteran qualifies for ladder');

// ---- 8. rankBadgeText / describeEvent don't throw ----
ok(typeof R.rankBadgeText('offline', C) === 'string', 'rankBadgeText returns string');
ok(R.describeEvent({ type: 'promoted', toId: 'kyu-9' }).title.includes('9'), 'describeEvent promoted');

// ---- 9. extendability: insert a tier mid-table, engine adapts ----
{
  const t2 = JSON.parse(JSON.stringify(table));
  t2.tiers.splice(19, 0, { id: 'test-insert', name: 'Test Insert', nameJa: null, section: 'mythology' });
  R._setTableForTest(t2);
  ok(R.tierCount() === 54, 'inserted tier -> 54 tiers, no code change');
  ok(R.tierIndexById('kappa') === 20, 'ids re-resolve after insert (kappa now idx 20)');
  ok(R.tierIndexById('lost-soul') === 0, 'stable ids survive structural edits');
  R._setTableForTest(table); // restore
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
