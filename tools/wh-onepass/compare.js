// WH visual-regression compare CLI (pixelmatch).
// Usage:
//   node compare.js <baseline.png> <current.png> <diff.png> [--threshold=0.03]
// Semantics (same as the Playwright snapshot pattern):
//   - baseline missing -> copy current to baseline, exit 0 ("baseline created")
//   - mismatch % <= threshold -> exit 0 (pass)
//   - mismatch % > threshold -> exit 1 (fail), diff.png written
//   - identical pixels render grayscale in diff; changed pixels red.
// Requires: npm install pixelmatch pngjs
// WebGL gotcha (documented, not hidden): capture screenshots immediately
// after render, or set preserveDrawingBuffer:true in TEST builds only --
// never in the shipped build (perf cost).
const fs = require('fs');
const { PNG } = require('pngjs');
// pixelmatch v5+ is ESM-only: require() returns {default: fn}.
// The fallback keeps this working on both CJS and ESM builds.
const _pm = require('pixelmatch');
const pixelmatch = _pm.default || _pm;

function readPng(path) {
  return PNG.sync.read(fs.readFileSync(path));
}

function main() {
  const args = process.argv.slice(2);
  let threshold = 0.03;
  const files = [];
  for (const a of args) {
    if (a.startsWith('--threshold=')) threshold = parseFloat(a.split('=')[1]);
    else files.push(a);
  }
  if (files.length !== 3) {
    console.error('usage: node compare.js <baseline> <current> <diff> [--threshold=0.03]');
    process.exit(2);
  }
  const [baselinePath, currentPath, diffPath] = files;
  if (!fs.existsSync(baselinePath)) {
    fs.copyFileSync(currentPath, baselinePath);
    console.log('baseline created: ' + baselinePath);
    process.exit(0);
  }
  const baseline = readPng(baselinePath);
  const current = readPng(currentPath);
  if (baseline.width !== current.width || baseline.height !== current.height) {
    console.log('mismatch 100.00% (dimensions differ: '
      + baseline.width + 'x' + baseline.height + ' vs '
      + current.width + 'x' + current.height + ')');
    process.exit(1);
  }
  const diff = new PNG({ width: baseline.width, height: baseline.height });
  const changed = pixelmatch(
    baseline.data, current.data, diff.data,
    baseline.width, baseline.height, { threshold: 0.1 });
  const total = baseline.width * baseline.height;
  const pct = (changed / total) * 100;
  fs.writeFileSync(diffPath, PNG.sync.write(diff));
  console.log('mismatch ' + pct.toFixed(2) + '% (' + changed + '/' + total
    + ' px), threshold ' + (threshold * 100).toFixed(2) + '%');
  process.exit(pct / 100 <= threshold ? 0 : 1);
}

main();
