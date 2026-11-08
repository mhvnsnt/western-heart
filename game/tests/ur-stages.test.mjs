/* ur-stages.test.mjs — Urban Reign stage arenas (Lane 4 follow-on 5).
 *
 * The 6 decoded UR stage PPKs (003/004/028/029/030/031; stage020's geometry
 * is NOT decodable in-VM — see UR-STAGE-MISSION-DECODE.md) are wired as
 * selectable arenas: real decoded VMD geometry exported to OBJ
 * (game/assets/stages/ur/stageNNN.obj, vertices + UVs + decoded vertex
 * colors, metres, no scale) + registry defs in game/js/stages.js
 * (builder 'urstage', tier 'URBAN REIGN').
 *
 * This test validates the shipped artifacts + the wiring WITHOUT importing
 * stages.js (its import graph needs a browser 'three' build; no test in
 * the repo imports stages.js today). The OBJ parse below mirrors the
 * game's own parseStageOBJ (game/js/stages.js): v / vt / f triangles,
 * vertex colors on the v lines when present. The live proof (a stage
 * loading + fighting in the game) is the parent's playthrough lane.
 *
 * Expected counts are the measured decode numbers (export report); the
 * test guards the OBJs against corruption or bad regeneration.
 *
 * Run: node --test game/tests/ur-stages.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const STAGES = join(ROOT, 'game', 'js', 'stages.js');
const UR_DIR = join(ROOT, 'game', 'assets', 'stages', 'ur');

// Measured decode numbers (meshes.load on the stage VMD; see
// ~/workspace/urban-reign-redux/decoded/UR-STAGE-MISSION-DECODE.md).
// Filled in by the export lane; exact verts/tris per stage.
// Measured bounds_world from the export report (meshes.load, metres).
// The raw VMD world includes backdrop geometry: stage003/029/030 span
// hundreds of metres (the ±215.92 / ±539.8 symmetric boxes are backdrop
// shells), while 004/028/031 are compact. No guessed floor/extent here —
// the test asserts the OBJ matches the measured bounds exactly.
const EXPECTED = {
  stage003: { verts: 57621, tris: 36953, min: [-215.92, -8.34, -215.92], max: [215.92, 97.6, 215.92] },
  stage004: { verts: 38747, tris: 22769, min: [-14.61, -0.44, -15.84], max: [19.2, 14.03, 7.06] },
  stage028: { verts: 26759, tris: 16117, min: [-8.0, -1.07, -10.74], max: [8.24, 10.44, 10.2] },
  stage029: { verts: 77032, tris: 49442, min: [-539.8, -2.0, -539.8], max: [539.8, 244.0, 539.8] },
  stage030: { verts: 34873, tris: 20757, min: [-539.8, -49.68, -172.61], max: [539.8, 209.32, 518.37] },
  stage031: { verts: 46941, tris: 28017, min: [-73.47, -0.26, -69.88], max: [73.47, 60.75, 69.88] },
};

function parseObj(text) {
  let verts = 0, uvs = 0, faces = 0, colored = 0;
  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
  for (const line of text.split('\n')) {
    if (line.startsWith('v ')) {
      const p = line.split(/\s+/);
      verts++;
      const x = +p[1], y = +p[2], z = +p[3];
      if (x < minX) minX = x; if (y < minY) minY = y; if (z < minZ) minZ = z;
      if (x > maxX) maxX = x; if (y > maxY) maxY = y; if (z > maxZ) maxZ = z;
      if (p.length >= 7 && p[4] !== '') colored++;
    } else if (line.startsWith('vt ')) {
      uvs++;
    } else if (line.startsWith('f ')) {
      faces++;
      assert.equal(line.trim().split(/\s+/).length, 4, `face is a triangle: ${line}`);
    }
  }
  return { verts, uvs, faces, colored, bounds: { min: [minX, minY, minZ], max: [maxX, maxY, maxZ] } };
}

for (const [tag, exp] of Object.entries(EXPECTED)) {
  test(`UR ${tag}.obj parses with the decoded geometry`, () => {
    const path = join(UR_DIR, `${tag}.obj`);
    assert.ok(existsSync(path), `${tag}.obj exists`);
    const parsed = parseObj(readFileSync(path, 'utf8'));
    assert.equal(parsed.verts, exp.verts, `${tag} vertex count`);
    assert.equal(parsed.faces, exp.tris, `${tag} triangle count`);
    assert.ok(parsed.uvs >= parsed.verts, `${tag} has a UV per vertex`);
    assert.equal(parsed.colored, parsed.verts, `${tag} every vertex carries a decoded color`);
    // OBJ bounds match the measured decode bounds (within rounding).
    for (let i = 0; i < 3; i++) {
      assert.ok(Math.abs(parsed.bounds.min[i] - exp.min[i]) < 0.02, `${tag} min[${i}] matches decode`);
      assert.ok(Math.abs(parsed.bounds.max[i] - exp.max[i]) < 0.02, `${tag} max[${i}] matches decode`);
    }
  });
}

test('UR stages are registered in stages.js', () => {
  const src = readFileSync(STAGES, 'utf8');
  assert.ok(src.includes(`'URBAN REIGN'`), 'URBAN REIGN tier is in STAGE_TIERS');
  assert.ok(src.includes('urstage: buildURStage'), 'urstage builder is registered in BUILDERS');
  assert.ok(src.includes('async function buildURStage'), 'buildURStage exists');
  // The defs are table-driven (URBAN_REIGN rows + one STAGES.push loop),
  // so the ids are built as `ur-${ppk}` — assert the table rows + the loop.
  assert.ok(src.includes('id: `ur-${ppk}`'), 'UR defs build ur-<ppk> ids');
  assert.ok(src.includes('obj: `assets/stages/ur/${ppk}.obj`'), 'UR defs point at their OBJs');
  for (const tag of Object.keys(EXPECTED)) {
    assert.ok(src.includes(`'${tag}', 'UR Arena ${tag.slice(5)}'`), `${tag} is in the URBAN_REIGN table`);
  }
  // UR stages carry their own floor at y=0 — the platform must be hidden
  // (same rule as the No Mercy GLB arenas), or it z-fights the model floor.
  const urBlock = src.slice(src.indexOf('const URBAN_REIGN'));
  assert.ok(urBlock.includes('hidePlatform: true'), 'UR defs hide the platform');
  // No canon name invented: the labels are the PPK ids, flagged PROPOSED.
  assert.ok(src.includes('PROPOSED'), 'UR defs carry the PROPOSED naming flag');
});

test('stage020 is NOT registered (geometry undecodable in-VM)', () => {
  const src = readFileSync(STAGES, 'utf8');
  assert.ok(!src.includes(`ur-stage020`), 'no stage020 def — its VMD fails read_mesh');
  assert.ok(!existsSync(join(UR_DIR, 'stage020.obj')), 'no stage020 OBJ');
});
