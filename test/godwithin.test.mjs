// God Within mode core (branch godwithin/wiring-20261126, 2026-11-26).
// Run: node test/godwithin.test.mjs
//
// Every number below is grounded in the wireup lanes' verified
// evidence (lane-a-wh-state.md, lane-b-inventory.md,
// lane-c-reskin-map.md) or in the live GLB verification this lane
// ran 2026-11-26 (Worker HEAD checks + R2 upload manifest +
// git tree at d65c53a9) — never invented. Wiring markers are
// asserted against the shipped source text of modes.js /
// mainmenu.js / stages.js so a later edit that drops the wiring
// fails this test.
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const M = await import(join(ROOT, 'game', 'js', 'godwithin.js'));
const MODES_SRC = readFileSync(join(ROOT, 'game', 'js', 'modes.js'), 'utf8');
const MENU_SRC = readFileSync(join(ROOT, 'game', 'js', 'mainmenu.js'), 'utf8');
const STAGES_SRC = readFileSync(join(ROOT, 'game', 'js', 'stages.js'), 'utf8');

// The roster ids come from the shipped roster-full.js (read live,
// not hand-typed) so the pool-size test tracks the real roster.
import { FULL_ROSTER } from '../game/js/roster-full.js';
const ROSTER_IDS = FULL_ROSTER.map((c) => c.id);
const MODEL_PENDING = FULL_ROSTER.filter((c) => c.modelPending || !c.model).map((c) => c.id);

test('roster fixture: 85 entries, exactly byou + ryuji model-pending', () => {
  assert.equal(FULL_ROSTER.length, 85);
  assert.deepEqual(MODEL_PENDING.sort(), ['byou', 'ryuji']);
});

test('anchors: 12, distributed 3+2+2+2+3 across the 5 chapters', () => {
  assert.equal(M.GODWITHIN_ANCHORS.length, 12);
  const per = [1, 2, 3, 4, 5].map(
    (n) => M.GODWITHIN_ANCHORS.filter((a) => a.chapter === n).length,
  );
  assert.deepEqual(per, [3, 2, 2, 2, 3]);
  assert.equal(new Set(M.GODWITHIN_ANCHORS.map((a) => a.anchor)).size, 12);
});

test('chapters: 5 DW stages map to WH stages, each with a WH boss body', () => {
  assert.equal(M.GODWITHIN_CHAPTERS.length, 5);
  assert.deepEqual(M.GODWITHIN_CHAPTERS.map((c) => c.dwStage),
    ['lab_A', 'lab_B', 'egy_A', 'blu_A', 'blu_B']);
  for (const c of M.GODWITHIN_CHAPTERS) {
    assert.ok(c.boss.id, `chapter ${c.n} has a boss body`);
    assert.ok(c.boss.dwBoss, `chapter ${c.n} names its DW boss`);
    assert.equal(c.anchors.length,
      M.GODWITHIN_ANCHORS.filter((a) => a.chapter === c.n).length);
  }
  // Final guardian sequence, DW5: PANTERA → DIABLO → DEMONIO.
  const dw5 = M.GODWITHIN_ANCHORS.filter((a) => a.chapter === 5).map((a) => a.guardianId);
  assert.deepEqual(dw5, ['demonio', 'diablo', 'pantera']);
});

test('rungs: 7 (5 chapters + Trader + final Shrine), forces in Trial order', () => {
  assert.equal(M.GODWITHIN_RUNGS.length, 7);
  assert.deepEqual(M.GODWITHIN_RUNGS.slice(0, 5).map((r) => r.forceKey),
    ['wood', 'fire', 'earth', 'metal', 'water']);
  assert.ok(M.GODWITHIN_RUNGS[5].trader);
  assert.ok(M.GODWITHIN_RUNGS[6].boss);
});

test('vessel pool: 83 of 85 — byou + ryuji excluded, dead ids excluded', () => {
  const pool = M.godwithinVesselPool(ROSTER_IDS, MODEL_PENDING);
  assert.equal(pool.length, 83);
  assert.ok(!pool.includes('byou') && !pool.includes('ryuji'));
  assert.ok(!pool.includes('jin_soul') && !pool.includes('sha'));
  assert.ok(!M.godwithinIsPlayable('byou', MODEL_PENDING));
  assert.ok(!M.godwithinIsPlayable('ryuji', MODEL_PENDING));
  assert.ok(M.godwithinIsPlayable('rave', MODEL_PENDING));
});

test('featured cast: 16 playable + byou (no GLB) + Trader (NPC only)', () => {
  assert.equal(M.GODWITHIN_FEATURED.length, 18);
  assert.equal(M.GODWITHIN_PLAYABLE_FEATURED.length, 16);
  const byou = M.GODWITHIN_FEATURED.find((f) => f.id === 'byou');
  assert.equal(byou.verified, 'no-glb');
  const trader = M.GODWITHIN_FEATURED.find((f) => f.id === 'trader');
  assert.equal(trader.verified, 'not-rostered');
  // Every playable featured fighter resolves to a verified GLB path.
  for (const f of M.GODWITHIN_PLAYABLE_FEATURED) {
    assert.ok(f.glb, `${f.id} has a GLB path`);
    assert.ok(['r2-200', 'r2-200-alt', 'tree-blob'].includes(f.verified),
      `${f.id} verified=${f.verified}`);
  }
  // PRAYER stand-in: RAVE guards it, flagged as BYOU's stand-in.
  const prayer = M.GODWITHIN_ANCHORS.find((a) => a.anchor === 'PRAYER');
  assert.equal(prayer.guardianId, 'rave');
  assert.equal(prayer.standIn, 'byou');
});

test('reincarnation: full-pool picks include vessels with no affinity entry', () => {
  // VESSEL_AFFINITY on main covers 36 vessels; a fighter outside it
  // (e.g. megami) must still be offerable via the neutral fallback.
  // Fixture uses the real affinity values for pantera + diablo.
  const affinity = {
    pantera: { aggro: 0.7, grapple: 1, defense: 0, trick: 0, surge: 0 },
    diablo: { aggro: 1, grapple: 0.3, defense: 0.3, trick: 0, surge: 0.3 },
  };
  const profile = { aggro: 1, grapple: 0, defense: 0, trick: 0, surge: 0 };
  const picks = M.chooseGodwithinVessels(profile, affinity, ROSTER_IDS, 'rin', 0);
  assert.equal(picks.length, 3);
  assert.ok(!picks.includes('rin'));
  assert.ok(!picks.includes('diablo'), 'Diablo gated below 3 deaths');
  const picksD3 = M.chooseGodwithinVessels(profile, affinity, ROSTER_IDS, 'rin', 3);
  assert.equal(picksD3[0], 'diablo', 'at 3+ deaths the intruder offers himself first');
  // Neutral fallback is a stated default, not per-fighter invention.
  assert.deepEqual(M.GODWITHIN_NEUTRAL_AFFINITY,
    { aggro: 0.3, grapple: 0.3, defense: 0.3, trick: 0.3, surge: 0.3 });
});

test('RNF face-pick: Art thresholds 50/40/30, scoring is exact', () => {
  assert.deepEqual(M.GODWITHIN_RNF.thresholds, { trueFace: 50, offered: 40, copy: 30 });
  assert.equal(M.rnfScoreFacePick([0, 0, 0], [0, 0, 0]).art, 50);
  assert.equal(M.rnfScoreFacePick([0, 0, 0], [0, 0, 0]).status, 'true');
  assert.equal(M.rnfScoreFacePick([0, 0, 1], [0, 0, 0]).art, 40);
  assert.equal(M.rnfScoreFacePick([0, 1, 1], [0, 0, 0]).art, 30);
  assert.equal(M.rnfScoreFacePick([1, 1, 1], [0, 0, 0]).art, 20);
  assert.equal(M.rnfScoreFacePick([1, 1, 1], [0, 0, 0]).status, 'locked');
  assert.equal(M.GODWITHIN_RNF.faces.length, 9);
  assert.equal(M.GODWITHIN_RNF.provisionalFaces.length, 3);
  assert.equal(M.GODWITHIN_RNF.triplesProvisional, true, 'manual PDF missing — triples provisional');
  assert.equal(M.GODWITHIN_RNF.routeFinals.length, 4);
});

test('run state machine: guardians → boss → advance; deaths keep rooms', () => {
  const run = M.createGodwithinRun('rin');
  assert.equal(run.lives, 9);
  // Rung 1 (DW1): three guardians, then the SAM-UR-A1 boss.
  let foe = M.godwithinNextFoe(run, 0);
  assert.deepEqual([foe.kind, foe.anchor], ['guardian', 'PYRAMSTP']);
  let res = M.godwithinMarkWin(run, 0, foe);
  assert.equal(res.advanced, false);
  assert.equal(res.shards, M.GODWITHIN_ECONOMY.payouts.guardianWin);
  foe = M.godwithinNextFoe(run, 0);
  assert.equal(foe.anchor, 'TAJI');
  M.godwithinMarkWin(run, 0, foe);
  foe = M.godwithinNextFoe(run, 0);
  assert.equal(foe.anchor, 'STPAUL');
  M.godwithinMarkWin(run, 0, foe);
  foe = M.godwithinNextFoe(run, 0);
  assert.deepEqual([foe.kind, foe.id], ['boss', 'samura1']);
  res = M.godwithinMarkWin(run, 0, foe);
  assert.equal(res.advanced, true);
  assert.equal(res.forceKey, 'wood');
  assert.equal(M.godwithinNextFoe(run, 0), null, 'rung complete');
  // Death does not clear rooms: a fresh progress read keeps them.
  const p = M.godwithinRungProgress(run, 0);
  assert.deepEqual([p.guardiansCleared, p.guardiansTotal, p.bossCleared, p.complete], [3, 3, true, true]);
  // Trader rung → toll; final rung → Assembled Soul → completion.
  assert.equal(M.godwithinNextFoe(run, 5).kind, 'toll');
  assert.equal(M.godwithinNextFoe(run, 6).kind, 'final');
  const fin = M.godwithinMarkWin(run, 6, { kind: 'final' });
  assert.equal(fin.complete, true);
  assert.equal(fin.shards, M.GODWITHIN_ECONOMY.payouts.completion);
});

test('between-lives records: dream pays the dream.html day-end minimum', () => {
  const run = M.createGodwithinRun('rin');
  const n = M.godwithinRecordDream(run, { day: 1, stage: 'Palace of Dreaming', shards: 20 });
  assert.equal(n, 1);
  assert.equal(run.shards, 20);
  assert.equal(M.GODWITHIN_ECONOMY.payouts.dreamNight, 20);
  M.godwithinRecordVoyage(run, { area: 'JAPAN', scene: 'PON', item: 'PON', shards: 25 });
  assert.equal(run.voyages.length, 1);
  M.godwithinRecordFace(run, { vessel: 'tou', art: 50, status: 'true' });
  assert.equal(run.faces.length, 1);
});

test('economy: one shared wallet, slot pays 10×/2×, forces never won on a machine', () => {
  assert.deepEqual(M.GODWITHIN_ECONOMY.slotPays, { three: 10, two: 2 });
  assert.equal(M.GODWITHIN_ECONOMY.payouts.completion, 100000);
  assert.ok(M.GODWITHIN_ECONOMY.rules.some((r) => r.includes('never won on a machine')));
});

test('sky layer is data-only and gated until the Planetokio discs land in-repo', () => {
  assert.equal(M.GODWITHIN_SKY.gated, true);
  assert.equal(M.GODWITHIN_SKY.islands.length, 12);
  assert.ok(M.GODWITHIN_SKY.islands.every((i) => i.possession.includes('quest/vaccine')));
});

test('combat tables: DW kit + 10 UR rows + 8 Def Jam rows, Icon excluded', () => {
  assert.equal(M.GODWITHIN_COMBAT.dwBaseKit.inputs.length, 12);
  assert.equal(M.GODWITHIN_COMBAT.urbanReign.length, 10);
  assert.equal(M.GODWITHIN_COMBAT.defJam.length, 8);
  const icon = M.GODWITHIN_COMBAT.defJam.find((r) => r.system.includes('Icon'));
  assert.equal(icon.status, 'excluded-owner-call');
  assert.ok(M.GODWITHIN_COMBAT.blockingDoor.rule.includes('DOES block'));
  assert.deepEqual(M.GODWITHIN_COMBAT.styleSchools.tou, ['Streetfighting', 'Kickboxing']);
});

test('flow: 11 steps, menu → select → rung → fight → death → dream → voyage → face-pick → reincarnate → next life → shrine', () => {
  assert.equal(M.GODWITHIN_FLOW.length, 11);
  assert.deepEqual(M.GODWITHIN_FLOW.map((s) => s.name),
    ['MENU', 'SELECT', 'RUNG', 'FIGHT', 'DEATH', 'DREAM', 'VOYAGE', 'FACE-PICK', 'REINCARNATE', 'NEXT LIFE', 'SHRINE']);
});

test('gaps: every known gap is listed, owner calls flagged, none hidden', () => {
  assert.ok(M.GODWITHIN_GAPS.length >= 18);
  const ids = M.GODWITHIN_GAPS.map((g) => g.id);
  for (const need of ['GW-1', 'GW-2', 'GW-3', 'GW-4', 'GW-5', 'GW-6', 'GW-19']) {
    assert.ok(ids.includes(need), `gap ${need} listed`);
  }
  const ownerCalls = M.GODWITHIN_GAPS.filter((g) => g.ownerCall);
  assert.ok(ownerCalls.some((g) => g.id === 'GW-5'), 'Icon is an owner call');
  assert.ok(ownerCalls.some((g) => g.id === 'GW-9'), 'Redux shape is an owner call');
});

test('wiring: modes.js carries the God Within entry + startMode + confirm + between-lives hook', () => {
  assert.ok(MODES_SRC.includes("import { GODWITHIN_MODE, GODWITHIN_RUNGS, GODWITHIN_ANCHORS, GODWITHIN_CHAPTERS, GODWITHIN_ECONOMY, GODWITHIN_RNF, chooseGodwithinVessels, godwithinVesselPool, createGodwithinRun, godwithinNextFoe, godwithinMarkWin, godwithinRungProgress, godwithinChapterForRung, godwithinRecordDream, godwithinRecordVoyage, godwithinRecordFace, rnfScoreFacePick, godwithinRnfFaceFor } from './godwithin.js';"), 'modes.js imports godwithin.js');
  assert.ok(MODES_SRC.includes("key: 'godwithin'"), 'MODE_LIST has godwithin');
  assert.ok(MODES_SRC.includes("mode === 'godwithin'"), 'startMode handles godwithin');
  assert.ok(MODES_SRC.includes("if (this.mode === 'godwithin')"), 'confirm routes godwithin');
  assert.ok(MODES_SRC.includes('_godwithinBetweenLives'), 'between-lives hook exists');
  assert.ok(MODES_SRC.includes('_godwithinFight'), 'godwithin fight path exists');
  assert.ok(MODES_SRC.includes('_godwithinEnd'), 'godwithin end path exists');
  assert.ok(MODES_SRC.includes('_godwithinStageIntro'), 'godwithin stage intro exists');
  assert.ok(MODES_SRC.includes('dream-system.js'), 'death hooks the dream system');
  assert.ok(MODES_SRC.includes('rolypolys-hub.js'), 'death hooks the Banabana hub');
});

test('wiring: main menu carries the GOD WITHIN card; stages carry guardian rooms', () => {
  assert.ok(MENU_SRC.includes("t: 'GOD WITHIN'"), 'menu card exists');
  assert.ok(MENU_SRC.includes("action: 'mode-godwithin'"), 'menu card routes mode-godwithin');
  assert.ok(STAGES_SRC.includes('GODWITHIN_GUARDIAN_ROOMS'), 'stages.js exports guardian rooms');
  assert.ok(STAGES_SRC.includes("anchor: 'PYRAMSTP'"), 'guardian rooms list anchors');
  assert.ok(STAGES_SRC.includes("guardianId: 'demonio'"), 'DEVIL room guarded by DEMONIO');
});
