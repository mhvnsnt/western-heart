// WH GLB validator — Khronos glTF-Validator (Apache-2.0), library edition.
// Wiring target in repo: tools/glb-tools/validate.mjs (pipeline gate).
// Usage: node validate.mjs <file.glb> [<file2.glb> ...]
// Exit code: 0 = no errors, 1 = errors found. Warnings/infos never fail.
// Proven 2026-10-24: caught 6 real errors in a WH GNM head GLB
// (ACCESSOR_TOO_LONG x2, ACCESSOR_INVALID_IBM x3, EMPTY_ENTITY) that also
// made gltfpack refuse the file ("buffer too short") — validator first,
// optimizer second, always in that order.
import { validateBytes } from 'gltf-validator';
import { readFileSync } from 'node:fs';
let failed = false;
for (const file of process.argv.slice(2)) {
  const report = await validateBytes(new Uint8Array(readFileSync(file)));
  const { numErrors, numWarnings, numInfos, messages } = report.issues;
  console.log(`${file} | ${numErrors} errors, ${numWarnings} warnings, ${numInfos} infos`);
  for (const m of messages.slice(0, 20)) console.log(`  ${m.severity} ${m.code} - ${m.message}`);
  if (numErrors > 0) failed = true;
}
process.exit(failed ? 1 : 0);
