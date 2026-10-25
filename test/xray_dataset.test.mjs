// Tests for schema v3 dataset mesh support
import { parseAnatomyLayers, normDatasetMesh } from '../game/js/xray.js';

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL -', name); }
}

// ================= normDatasetMesh =================
ok(normDatasetMesh({
  url: 'roster/pantera/anatomy/meshes/skull.glb',
  dataset: 'bodyparts3d',
  license: 'CC-BY-4.0'
}).dataset === 'bodyparts3d', 'normDatasetMesh valid');

ok(normDatasetMesh({
  url: 'test.glb',
  dataset: 'bodyparts3d'
  // missing license
}) === null, 'normDatasetMesh rejects missing license');

ok(normDatasetMesh({
  dataset: 'bodyparts3d',
  license: 'CC-BY-4.0'
  // missing url
}) === null, 'normDatasetMesh rejects missing url');

ok(normDatasetMesh(null) === null, 'normDatasetMesh rejects null');

// ================= parseAnatomyLayers with meshes =================
const v3fixture = {
  $schema: 'wh.anatomy-layers/3',
  fighter: 'test',
  layers: {
    bone: {
      primitives: [
        { id: 'skull', kind: 'sphere', center: [0, 1.7, 0], r: 0.1 }
      ],
      meshes: [
        {
          id: 'skull',
          url: 'roster/test/anatomy/meshes/skull.glb',
          dataset: 'bodyparts3d',
          dataset_version: '4.0',
          license: 'CC-BY-4.0',
          attribution: 'BodyParts3D, © DBCLS CC BY 4.0',
          joint: 'head'
        }
      ]
    },
    muscle: { groups: [] },
    organ: { primitives: [] }
  }
};

const parsed = parseAnatomyLayers(v3fixture);
ok(parsed !== null, 'parseAnatomyLayers v3 with meshes');
ok(parsed.datasetMeshes.bone.length === 1, 'dataset mesh parsed');
ok(parsed.datasetMeshes.bone[0].license === 'CC-BY-4.0', 'license preserved');
ok(parsed.datasetMeshes.bone[0].attribution.includes('BodyParts3D'), 'attribution preserved');

// Mesh without license is skipped
const badFixture = {
  $schema: 'wh.anatomy-layers/3',
  layers: {
    bone: {
      primitives: [],
      meshes: [{ id: 'x', url: 'y.glb', dataset: 'z' }] // no license
    },
    muscle: { groups: [] },
    organ: { primitives: [] }
  }
};
const badParsed = parseAnatomyLayers(badFixture);
ok(badParsed === null || badParsed.datasetMeshes.bone.length === 0, 'unlicensed mesh skipped');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail > 0 ? 1 : 0);
