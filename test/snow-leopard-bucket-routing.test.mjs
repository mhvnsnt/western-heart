// test/snow-leopard-bucket-routing.test.mjs — Snow Leopard bucket-routing fix (2026-11-02).
// The three models below live in the repo but are missing from the remote asset
// bucket (bucket 404, verified live 2026-11-02), although the R2 upload manifest
// lists them. The fix bundles them in the Pages shell, so resolveAssetCandidates
// returns the local URL first and the game no longer depends on the bucket copy.
// Blob SHAs come from `git ls-tree HEAD` (tree entries only — no blob downloads,
// so this test runs on CI's sparse checkout, which does not carry roster/).
// A blob SHA pins the exact bytes, which pins the size too; the byte sizes
// below were verified against the R2 upload manifest and the 2026-11-02
// task (snow-leopard 7,434,348; bobcat-pride 33,257,868; tiger-king 32,100,272).
import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const AC = await import(join(ROOT, 'game/js/asset-config.js'));

// [repo path, blob SHA on main] — SHAs from `git ls-tree -r HEAD` (2026-11-02).
const FIXED = [
  ['roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb', 'ab46d87309e31bc60c186ae4c529dbb9ed797577'],
  ['roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride-rigged.glb', 'deac50e24633612140168cbb8669d1c357b20b5b'],
  ['roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king-rigged.glb', '6222d4e8139f4a268cc5b7e3dc85460f553b6e4e'],
];

test('fixed models are shell-bundled, local-first, and present at the verified blob', () => {
  for (const [path, sha] of FIXED) {
    assert.ok(AC.SHELL_BUNDLED_MODELS.includes(path), `not bundled: ${path}`);
    const url = `../${path}`;
    const cands = AC.resolveAssetCandidates(url);
    assert.equal(cands[0], url, `not local-first: ${path} -> ${cands[0]}`);
    const ls = execFileSync('git', ['ls-tree', 'HEAD', '--', path], { encoding: 'utf8' }).trim();
    const m = ls.match(/^100644 blob ([0-9a-f]{40})\t/);
    assert.ok(m, `ls-tree gave no blob for ${path}: ${JSON.stringify(ls)}`);
    assert.equal(m[1], sha, `blob drift for ${path}: ls-tree ${m[1]} != ${sha}`);
  }
});

test('yukihyo attire 1 stays remote-first (its bucket copy returns 200)', () => {
  const a1 = 'roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb';
  assert.ok(!AC.SHELL_BUNDLED_MODELS.includes(a1), 'attire 1 must not be bundled');
  const cands = AC.resolveAssetCandidates(`../${a1}`);
  assert.ok(cands[0].startsWith('https://'), `attire 1 should stay remote-first, got ${cands[0]}`);
});
