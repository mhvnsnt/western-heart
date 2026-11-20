// tools/proofs/gltf-validate.mjs — validation step for WH GLBs, PROOFS ONLY.
//
// This does NOT duplicate tools/anim/gltf_codec.mjs and does NOT re-encode
// anything. The codec (decode/encode, meshopt + quantization) stays the only
// place that transforms a GLB. This script only reads and reports, and it is
// meant to run AFTER `gltf_codec.mjs encode` and BEFORE a proof GLB is shared:
//
//   node tools/anim/gltf_codec.mjs encode in.glb out.glb
//   node tools/proofs/gltf-validate.mjs out.glb            # must exit 0
//
// Two tiers, both honest about what ran:
//   Tier 1 (always): pure-Node GLB container + JSON validation. No deps.
//     - magic "glTF", version 2, chunk lengths consistent with file size
//     - exactly 0-1 buffers in a GLB (the rule that bit model-rigged.glb,
//       see gltf_codec.mjs: a meshopt GLB's fallback buffer must be merged)
//     - JSON chunk parses; asset.version present; extension names listed
//     - mesh / node / skin / animation counts reported
//   Tier 2 (only when the codec's own deps resolve): deep parse with
//   @gltf-transform/core, the SAME pinned versions gltf_codec.mjs uses
//   (@gltf-transform/core@4.1.1, @gltf-transform/extensions@4.1.1,
//    @gltf-transform/functions@4.1.1, meshoptimizer@0.22.0). If those deps
//   are absent, Tier 2 is reported as SKIPPED, not faked, and Tier 1 still
//   gates the file. A deep parse that fails is a hard failure, not a skip.
//
// Usage: node tools/proofs/gltf-validate.mjs FILE.glb [--json]
// Exit: 0 valid, 1 invalid, 2 usage error.

import { readFileSync } from 'node:fs';

const [,, file, flag] = process.argv;
if (!file || (flag && flag !== '--json')) {
  console.error('usage: node gltf-validate.mjs FILE.glb [--json]');
  process.exit(2);
}

const failures = [];
const notes = [];
const buf = readFileSync(file);
const fail = (m) => failures.push(m);

// ---- Tier 1: GLB container -------------------------------------------------
if (buf.length < 20) fail(`file too small for a GLB header (${buf.length} bytes)`);
const magic = buf.length >= 4 ? buf.toString('ascii', 0, 4) : '';
if (magic !== 'glTF') fail(`bad GLB magic: ${JSON.stringify(magic)} (expected "glTF")`);
const version = buf.length >= 8 ? buf.readUInt32LE(4) : 0;
if (version !== 2) fail(`unsupported glTF version: ${version} (expected 2)`);
const totalLength = buf.length >= 12 ? buf.readUInt32LE(8) : 0;
if (totalLength !== buf.length) {
  fail(`GLB length header (${totalLength}) != file size (${buf.length})`);
}

let json = null;
if (buf.length >= 20) {
  const chunkLen = buf.readUInt32LE(12);
  const chunkType = buf.readUInt32LE(16);
  if (chunkType !== 0x4E4F534A) fail(`first chunk is not JSON (type 0x${chunkType.toString(16)})`);
  const jsonEnd = 20 + chunkLen;
  if (jsonEnd > buf.length) fail(`JSON chunk overruns file (${jsonEnd} > ${buf.length})`);
  else {
    try { json = JSON.parse(buf.toString('utf8', 20, jsonEnd)); }
    catch (e) { fail(`JSON chunk does not parse: ${e.message}`); }
  }
  // A BIN chunk, if present, must also fit inside the file.
  if (jsonEnd < buf.length) {
    if (buf.length - jsonEnd < 8) fail('trailing bytes too small for a BIN chunk header');
    else {
      const binLen = buf.readUInt32LE(jsonEnd);
      if (jsonEnd + 8 + binLen > buf.length) fail('BIN chunk overruns file');
    }
  }
}

let report = {
  file, tier1: 'run', tier2: 'skipped (gltf-transform deps not resolvable)',
  buffers: null, meshes: null, nodes: null, skins: null, animations: null,
  extensionsUsed: [], failures, notes,
};
if (json) {
  if (!json.asset || typeof json.asset.version !== 'string') fail('missing asset.version');
  const buffers = Array.isArray(json.buffers) ? json.buffers : [];
  report.buffers = buffers.length;
  if (buffers.length > 1) fail(`GLB holds ${buffers.length} buffers (GLB allows 0-1; merge with gltf_codec.mjs / unpartition)`);
  report.meshes = Array.isArray(json.meshes) ? json.meshes.length : 0;
  report.nodes = Array.isArray(json.nodes) ? json.nodes.length : 0;
  report.skins = Array.isArray(json.skins) ? json.skins.length : 0;
  report.animations = Array.isArray(json.animations) ? json.animations.length : 0;
  report.extensionsUsed = Array.isArray(json.extensionsUsed) ? json.extensionsUsed : [];
  if (report.skins > 0) {
    const bad = (json.skins || []).filter((s) => !Array.isArray(s.joints) || s.joints.length === 0);
    if (bad.length) fail(`${bad.length} skin(s) with no joints`);
  }
  notes.push(`extensions used: ${report.extensionsUsed.join(', ') || '(none)'}`);
}

// ---- Tier 2: deep parse with the codec's own deps, if present --------------
if (json && failures.length === 0) {
  try {
    const { NodeIO } = await import('@gltf-transform/core');
    const { ALL_EXTENSIONS } = await import('@gltf-transform/extensions');
    const { MeshoptDecoder } = await import('meshoptimizer');
    await MeshoptDecoder.ready;
    const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
      .registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
    const doc = await io.read(file);
    const root = doc.getRoot();
    report.tier2 = 'run (gltf-transform deep parse ok)';
    report.meshes = root.listMeshes().length;
    report.nodes = root.listNodes().length;
    report.skins = root.listSkins().length;
    report.animations = root.listAnimations().length;
    notes.push('deep parse: document read back through @gltf-transform/core');
  } catch (e) {
    if (/Cannot find (module|package)/.test(e.message)) {
      notes.push('tier 2 skipped: @gltf-transform/meshoptimizer not installed; '
        + 'install the gltf_codec.mjs pinned deps to enable it');
    } else {
      fail(`deep parse failed: ${e.message}`);
    }
  }
}

report.failures = failures;
report.notes = notes;
if (flag === '--json') console.log(JSON.stringify(report, null, 2));
else {
  console.log(`validate ${file}`);
  console.log(`  tier1: container+JSON ${failures.length ? 'FAIL' : 'ok'}`);
  console.log(`  tier2: ${report.tier2}`);
  console.log(`  buffers=${report.buffers} meshes=${report.meshes} nodes=${report.nodes} skins=${report.skins} animations=${report.animations}`);
  for (const n of notes) console.log(`  note: ${n}`);
  for (const f of failures) console.log(`  FAIL: ${f}`);
}
process.exit(failures.length ? 1 : 0);
