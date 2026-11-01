// Real Tekken 7 per-move clips converted from 0x64 (compressed) clips (2026-11-01). Node, no browser.
// Run: node --test test/t7-moves-0x64.test.mjs
// Every T7 attack is 0x64. tools/anim/t7_anim64_to_c8.py converts each one with the game's OWN sampler (read from
// TekkenGame-Win64-Shipping.exe; docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md) into 0xC8 values, then
// tools/anim/t7_move_bake.py bakes it through the same proven 0xC8 path as the stances, for the rows
// tools/anim/t7_move_resolve.py maps exactly (input path from the base's stance AND exact T7 frame data).
// One block per single-source fighter (Pantera: test/t7-moves-king.test.mjs). `base` is the T7 source-set DATA dir. Fighters sharing a base dir have
// their own pack (`pack`). Add the next fighter as one FIGHTERS row once its pack is baked and wired in T7_MOVES.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (f) => readFileSync(join(ROOT, f), 'utf8');
const firstInt = (s) => { const m = String(s ?? '').match(/-?\d+/); return m ? +m[0] : null; };
const EXE_SHA = '7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed';
const FIGHTERS = [
  { fighter: 'purplerain', base: 'lee', bank: 'jin', moveset: 'purplerain', stance: 'Le_sKAM00_' },
  { fighter: 'chordz', base: 'lars', bank: 'jin', moveset: 'chordz', stance: 'La_sKAM00_' },
  { fighter: 'diablo', base: 'heihachi', bank: 'heihachi', moveset: 'diablo', stance: 'He_sKAM00_' },
  { fighter: 'skull', base: 'bryan', bank: 'bryan', moveset: 'skull', stance: 'Bx_sKAM00_', pack: 'moves.skull.pack.json' },
  { fighter: 'retsu', base: 'bryan', bank: 'bryan', moveset: 'retsu', stance: 'Bx_sKAM00_', pack: 'moves.retsu.pack.json' },
  { fighter: 'sakura', base: 'xiaoyu', bank: 'xiaoyu', moveset: 'sakura', stance: 'Fu_sKAM00_', pack: 'moves.sakura.pack.json' },
  { fighter: 'sha', base: 'xiaoyu', bank: 'xiaoyu', moveset: 'sha', stance: 'Fu_sKAM00_', pack: 'moves.sha.pack.json' },
  { fighter: 'phantom', base: 'yoshimitsu', bank: 'yoshimitsu', moveset: 'phantom', stance: 'Ym_sKAM00_' },
  { fighter: 'gyou', base: 'hwoarang', bank: 'hwoarang', moveset: 'gyou', stance: 'Hw_sKAM00_', pack: 'moves.gyou.pack.json' },
  { fighter: 'tobi', base: 'hwoarang', bank: 'hwoarang', moveset: 'tobi', stance: 'Hw_sKAM00_', pack: 'moves.tobi.pack.json' },
  { fighter: 'gashadokuro', base: 'kuma', bank: 'kuma', moveset: 'gashadokuro', stance: 'Km_sKAM00_' },
  { fighter: 'aotsuki', base: 'panda', bank: 'kuma', moveset: 'aotsuki', stance: 'Km_sKAM00_' },
  { fighter: 'nightwolf', base: 'julia', bank: 'julia', moveset: 'nightwolf', stance: 'Jl_sKAM00_' },
];

const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
const qrot = (q, v) => { const [x, y, z, w] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]; };
const poser = (skel) => {
  const REST = {}, PAR = {};
  for (const j of skel.joints) { REST[j.name] = j.rest; PAR[j.name] = j.parent; }
  return (clip, f) => {
    const G = {}, X = {};
    for (const j of skel.joints.map(k => k.name)) {
      const q = clip.rot_xyzw[j][f], p = PAR[j];
      if (!p) { G[j] = q; X[j] = clip.root_t[f]; continue; }
      G[j] = qmul(G[p], q);
      const o = qrot(G[p], [REST[j][0] - REST[p][0], REST[j][1] - REST[p][1], REST[j][2] - REST[p][2]]);
      X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
    }
    return X;
  };
};

for (const F of FIGHTERS) {
  const DIR = `game/assets/anim/t7/${F.base}/`, PACK = F.pack || 'moves.pack.json';
  if (!existsSync(join(ROOT, DIR, PACK))) {
    test(`${F.fighter}: moves pack present`, () => assert.fail(`${DIR}${PACK} missing`));
    continue;
  }
  const pack = JSON.parse(src(DIR + PACK));
  const skel = JSON.parse(src(DIR + 'skeleton.json'));
  const moveset = JSON.parse(src(`game/assets/movesets/${F.moveset}.json`)).moves;
  const pose = poser(skel);

  test(`${F.fighter}: FIGHT-only pack, 0x64 clips converted by the game sampler, FK exact`, () => {
    assert.equal(pack.format, 'wh-t7-moves/1');
    assert.equal(pack.fighter, F.fighter);
    assert.equal(pack.anim_set, 'FIGHT');
    assert.equal(pack.skeleton, 'skeleton.json');
    assert.ok(Object.keys(pack.moves).length >= 15, `${Object.keys(pack.moves).length} moves`);
    for (const [cname, c] of Object.entries(pack.clips)) {
      assert.equal(c.format, 'wh-anim/1', cname);
      assert.equal(c.fps, 60, cname);
      assert.equal(c.anim_set, 'FIGHT', cname);
      assert.equal(c.loop, false, cname);
      assert.ok(['0x64', '0xC8'].includes(c.t7_source.format), `${cname} format ${c.t7_source.format}`);
      if (c.t7_source.format === '0x64') {  // converted by the game's own sampler (0xC8 clips bake directly)
        assert.equal(c.t7_source.conversion.tool, 'tools/anim/t7_anim64_to_c8.py', cname);
        assert.equal(c.t7_source.conversion.exe_sha256, EXE_SHA, cname);
      }
      assert.ok(c.fk_selfcheck_max_m <= 1e-5, `${cname} FK ${c.fk_selfcheck_max_m}`);
      assert.equal(c.applier.commit, 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1');
      assert.equal(c.root_motion_fwd_m.length, c.root_t.length, `${cname} root motion per frame`);
      assert.equal(c.root_motion_fwd_m[0], 0, `${cname} root motion starts at 0`);
    }
  });

  test(`${F.fighter}: every mapped row keeps its exact T7 frame data and plays a real clip`, () => {
    for (const [key, m] of Object.entries(pack.moves)) {
      const row = moveset[key];
      assert.ok(row, `${key} is a ${F.moveset}.json row`);
      assert.ok(row.t7_damage_raw != null, `${key} has T7 frame data`);
      assert.equal(m.active_frames[0], firstInt(row.t7_startup_frames), `${key}: first active frame = T7 startup`);
      assert.ok(pack.clips[m.clip], `${key} -> ${m.clip}`);
      assert.ok(m.verified.startsWith(`input path from ${F.stance} + exact T7 frame data`), `${key}: ${m.verified}`);
      assert.ok(!row.isGrab && !row.throw, `${key} is a strike`);
    }
  });

  // Real T7 moves include flips, drop kicks that end on the floor, ground hits, and impacts that snap in 1-2 frames
  // (King's kick 3 extends the knee from 108 deg to straight on one frame; the game's own sampler agrees). The guard is
  // what a broken conversion would break: upright start from the stance, floor contact within mannequin tolerance,
  // and no joint jump a limb flip would make (a 180 deg thigh flip moves the foot ~2 leg lengths).
  test(`${F.fighter}: every clip is physically plausible (upright start, floor contact, no limb flips)`, () => {
    for (const [cname, c] of Object.entries(pack.clips)) {
      const X0 = pose(c, 0);
      assert.ok(X0.Head[1] > X0.Hips[1] + 0.2, `${cname}: starts upright (head ${(X0.Head[1] - X0.Hips[1]).toFixed(2)} m above hips)`);
      let prev = null;
      for (let f = 0; f < c.root_t.length; f++) {
        const X = pose(c, f);
        const low = Math.min(...Object.values(X).map(p => p[1]));
        assert.ok(low > -0.08, `${cname} f${f}: lowest joint ${low.toFixed(3)}`);
        if (prev) {
          for (const j of Object.keys(X)) {
            if (j === 'Hips') continue;
            const d = Math.hypot(X[j][0] - X.Hips[0] - (prev[j][0] - prev.Hips[0]), X[j][1] - X.Hips[1] - (prev[j][1] - prev.Hips[1]),
              X[j][2] - X.Hips[2] - (prev[j][2] - prev.Hips[2]));
            assert.ok(d < 1.5, `${cname} f${f}: ${j} jumps ${d.toFixed(2)} m in one frame`);
          }
        }
        prev = X;
      }
    }
  });

  test(`${F.fighter}: wired to load from the stance skeleton dir`, () => {
    const t3 = src('game/js/t3anims.js');
    const mv = t3.match(/export const T7_MOVES = \{([\s\S]*?)\n\};/);
    assert.ok(mv, 'T7_MOVES');
    const line = `${F.fighter}: { bank: '${F.bank}', dir: 'assets/anim/t7/${F.base}/'`;
    assert.ok(mv[1].includes(line + (F.pack ? `, pack: '${F.pack}' }` : ' }')), `T7_MOVES has ${line}${F.pack ? ', pack: ' + F.pack : ''}`);
    const st = t3.match(/export const T7_STANCES = \{([\s\S]*?)\n\};/);
    assert.ok(st && st[1].includes(line + ' }'), 'stance and moves share the skeleton dir');
  });

  test(`${F.fighter}: the real loader builds its move clips, for itself only`, async () => {
    await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
    const THREE = await import('three');
    const T = await import(join(ROOT, 'game/js/t3anims.js'));
    const r = await T.ensureT7Moves(F.fighter, THREE);
    assert.ok(r, 'pack loaded');
    const key = Object.keys(pack.moves)[0];
    const mc = T.t7MoveClip(F.fighter, F.bank, key);
    assert.ok(mc && mc.clip, `${key} clip`);
    assert.equal(mc.name, 't7:' + key);
    assert.deepEqual(mc.active, pack.moves[key].active_frames);
    assert.ok(Array.isArray(mc.clip.userData.rootMotionT), 'root motion track');
    assert.equal(T.t7MoveClip(F.fighter, F.bank === 'king' ? 'bryan' : 'king', key), null, 'only on its own bound bank');
    assert.equal(T.t7MoveClip('negativo', F.bank, key), null, 'never for another fighter');
    // a row the game prefers for the same single input reaches the pack clip (input fallback)
    const [pk, pm] = Object.entries(pack.moves).find(([, m]) => m.input && !String(m.input).includes(',')) || [];
    if (pk) {
      const m = T.t7MoveClip(F.fighter, F.bank, '__another_row_for_' + pm.input, null, pm.input);
      assert.ok(m, `input ${pm.input} -> ${pk}`);
    }
    assert.equal(T.t7MoveClip(F.fighter, F.bank, '1,2', null, '1,2'), null, 'strings never take a single-input clip');
  });

  test(`${F.fighter}: the rows its 1-4 slots fire reach its T7 clips by their input (probe 2026-11-01)`, async () => {
    await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
    const THREE = await import('three');
    const T = await import(join(ROOT, 'game/js/t3anims.js'));
    await T.ensureT7Moves(F.fighter, THREE);
    const ms = JSON.parse(src(`game/assets/movesets/${F.moveset}.json`));
    for (const b of ['1', '2', '3', '4']) {
      const played = ms.slots[b], [packKey] = Object.entries(pack.moves).find(([, m]) => m.input === b) || [];
      if (!packKey || !played) continue;
      const m = T.t7MoveClip(F.fighter, F.bank, played, null, ms.moves[played].input);
      assert.ok(m, `${b}: slot row ${played} (input ${ms.moves[played].input}) -> ${packKey}`);
      assert.equal(m.name, 't7:' + packKey);
    }
  });
}
