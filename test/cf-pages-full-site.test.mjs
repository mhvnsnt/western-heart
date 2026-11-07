// Cloudflare Pages full build (2026-11-06, owner: "a free fix for my cap on my storage for game assets to the
// deployable build"): on western-heart.pages.dev the page's own copy of a model is tried first; the GitHub Pages shell
// keeps remote-first. Plus the site builder's limits. Run: node --test test/cf-pages-full-site.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without tools/ or .github/: a file not on disk is read from git's object
// store (the commit under test), as test/creation-suite-templates.test.mjs does.
const src = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel), 'utf8')
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 26 }).toString('utf8');
const AC = await import(join(ROOT, 'game/js/asset-config.js'));
const url = '../roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb';

test('full-site host check matches only the Cloudflare Pages project', () => {
  assert.equal(AC.isFullSiteHost('western-heart.pages.dev'), true);
  assert.equal(AC.isFullSiteHost('abc123.western-heart.pages.dev'), true, 'preview deployments too');
  assert.equal(AC.isFullSiteHost('mhvnsnt.github.io'), false);
  assert.equal(AC.isFullSiteHost('127.0.0.1'), false);
  assert.equal(AC.isFullSiteHost('evil-western-heart.pages.dev.example.com'), false);
});

test('on the Cloudflare full site a model loads from the page first, then remote, then jsDelivr', () => {
  const save = globalThis.location;
  try {
    globalThis.location = { hostname: 'western-heart.pages.dev' };
    const c = AC.resolveAssetCandidates(url);
    assert.equal(c[0], url);
    assert.ok(c[c.length - 1].startsWith(AC.ASSET_CONFIG.jsdelivrBase));
  } finally {
    if (save === undefined) delete globalThis.location; else globalThis.location = save;
  }
});

test('elsewhere (GitHub Pages shell, dev, Node) the order is unchanged: remote first', () => {
  const c = AC.resolveAssetCandidates(url);
  assert.ok(c[0].startsWith('https://'), c[0]);
});

test('the site builder enforces the Cloudflare Pages per-file and per-deployment limits', () => {
  const py = src('tools/deploy/build_cf_pages.py');
  assert.match(py, /CF_FILE_MAX = 25 \* 1024 \* 1024/);
  assert.match(py, /CF_FILE_COUNT_MAX = 20000/);
  assert.match(py, /os\.path\.join\(a\.out, '404\.html'\)/, 'a top-level 404.html turns off the Pages SPA fallback');
  const wf = src('.github/workflows/deploy-cloudflare-pages.yml');
  assert.match(wf, /wrangler@4\.150\.0 pages deploy cf-site --project-name western-heart/);
  assert.match(wf, /filter: blob:none/, 'never checks out the 14 GB tree');
  assert.match(wf, /missing file -> \$code"; \[ "\$code" = "404" \]/, 'the live check proves missing files 404');
});
