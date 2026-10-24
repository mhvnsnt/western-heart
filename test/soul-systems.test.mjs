// SOUL-SYSTEMS.md: Nine-Soul Release, Reihou, Trial's Seal, per-fighter variants (incl. KESSHOU).
import assert from 'node:assert/strict';
import fs from 'node:fs';
const S = await import('../game/js/soul-systems.js');
const { FULL_ROSTER } = await import('../game/js/roster-full.js');
const V = JSON.parse(fs.readFileSync(new URL('../game/data/soul-variants.json', import.meta.url)));
S.setVariants(V);
const _dl = new URL('../tools/canon/denylist.json', import.meta.url);
// CI game-unit-tests uses a sparse checkout without tools/canon; canon-names job covers the leak check there.
const deny = fs.existsSync(_dl) ? JSON.parse(fs.readFileSync(_dl)).terms : [];
let n = 0; const t = (_, f) => { f(); n++; };
const mk = (id, o = {}) => ({ char: { id }, meter: 0, hp: 100, maxHp: 100, canAct: () => true, receiveHit(m) { this.hp -= m.damage; return 'hit'; }, ...o });
t('every roster fighter has a variant row', () => { for (const c of FULL_ROSTER) if (c && c.id) assert.ok(V.fighters[c.id], c.id); });
t('every fighter meets its minimum (>=3) in all four systems', () => {
  for (const [id, f] of Object.entries(V.fighters)) { assert.ok(f.min >= 3, id);
    for (const s of ['kesshou', 'release', 'reihou', 'seal']) { assert.ok(f[s].length >= f.min, `${id}.${s}`);
      for (const [fid, form] of Object.entries(f.forms || {})) assert.ok(form[s].length >= 3, `${id}/${fid}.${s}`); } } });
t('stronger canon tier -> more variants', () => { const r = Object.values(V.fighters); const hi = r.filter(f => f.tier >= 5), lo = r.filter(f => f.tier <= 2);
  assert.ok(hi.length && hi.every(f => f.min >= 5)); assert.ok(lo.every(f => f.min <= 4)); });
t('variants draw on real move types', () => { for (const [id, f] of Object.entries(V.fighters)) for (const v of f.release) if (f.moveTypes.length) assert.ok(f.moveTypes.includes(v.moveType), id); });
t('no source names in variant data', () => { const txt = JSON.stringify(V).toLowerCase(); for (const w of deny) assert.ok(!new RegExp(`\\b${w}\\b`).test(txt), w); assert.ok(!/heat action|climax/i.test(txt)); });
t('canon labels', () => { assert.equal(S.LABELS.ready, 'SOUL RELEASE READY'); assert.match(S.LABELS.release, /九魂解放/); assert.match(S.LABELS.reihou, /霊放/); assert.match(S.LABELS.seal, /試練の封/); });
t('release needs full meter and spends it', () => { const ss = new S.SoulSystems({}); const a = mk('demonio', { meter: 99 }), d = mk('pantera');
  assert.equal(ss.release(a, d), null); a.meter = 100; const v = ss.release(a, d); assert.ok(v.name.startsWith('NINE-SOUL RELEASE')); assert.equal(a.meter, 0); assert.ok(d.hp < 100); });
t('release claims 1+2+3+4 only at full meter', () => { const ss = new S.SoulSystems({}); const a = mk('demonio', { meter: 50 }), d = mk('x');
  assert.equal(ss.claimRelease(a, d, ['1', '2', '3', '4']), false); a.meter = 100; assert.equal(ss.claimRelease(a, d, ['1', '2', '3', '4']), true); });
t('ready callout once', () => { const banners = []; const g = { p1: mk('a', { meter: 100 }), p2: mk('b'), ui: { banner: x => banners.push(x) } }; const ss = new S.SoulSystems(g);
  ss.update(); ss.update(); assert.deepEqual(banners, ['SOUL RELEASE READY']); });
t('reihou purges foe rage', () => { const ss = new S.SoulSystems({}); const a = mk('demonio', { meter: 60 }), d = mk('b', { _rageOn: true });
  assert.ok(ss.tryReihou(a, d)); assert.equal(d._rageOn, false); assert.equal(d._rageUsed, true); assert.equal(a.meter, 10); assert.equal(a._spiritFlare, 1); });
t('reihou blocked without foe rage', () => assert.equal(new S.SoulSystems({}).tryReihou(mk('a', { meter: 100 }), mk('b')), null));
t("trial's seal: decisive verdict, not death", () => { const g = { p1: mk('demonio', { hp: 70 }), p2: mk('b', { hp: 0 }), matchStats: {} }; const ss = new S.SoulSystems(g);
  const v = ss.onRoundEnd(false, true); assert.ok(v.name.startsWith("TRIAL'S SEAL")); assert.equal(g.matchStats.seals.p1, 1); assert.equal(g.p2.dead, undefined); });
t('seal skipped on close round, granted via soul KO', () => { const g = { p1: mk('a', { hp: 20 }), p2: mk('b', { hp: 0 }) }; const ss = new S.SoulSystems(g);
  assert.equal(ss.onRoundEnd(false, true), null); ss.lastSoulKill = g.p1; assert.ok(ss.onRoundEnd(false, true)); });
t('form variants used when form active', () => { const id = Object.keys(V.fighters).find(k => Object.keys(V.fighters[k].forms).length); const fid = Object.keys(V.fighters[id].forms)[0];
  assert.ok(S.variantsFor(id, 'kesshou', fid).length >= 3); });
t('variant matches last move type', () => { const a = mk('demonio', { _lastMoveType: V.fighters.demonio.moveTypes[1] }); assert.equal(S.pickVariant(a, 'kesshou').moveType, V.fighters.demonio.moveTypes[1]); });
console.log(`soul-systems.test: ${n} passed`);
