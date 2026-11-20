// generate.mjs — TRACK 5 demo CLI: generate a zone and render proof artifacts.
//
// Usage:
//   node tools/worldgen/generate.mjs --ruleset temple-courtyard --seed 1337
//   node tools/worldgen/generate.mjs --ruleset hmw-forest --seed 2026 --out tools/worldgen/demo
//
// Writes into <out>/:
//   layout.json   tile grid + meta
//   layout.txt    ASCII art of the layout
//   heightmap.ppm terrain as a color PPM image (no deps needed to view/convert)
//   demo.html     standalone canvas visualization (open in any browser)
//   timings.json  generation time + memory budget numbers
import { writeFileSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, '..', '..');

const args = {};
for (let i = 2; i < process.argv.length; i += 2) {
  args[process.argv[i].replace(/^--/, '')] = process.argv[i + 1];
}
const kind = args.ruleset || 'temple-courtyard';
const seed = args.seed != null ? Number(args.seed) : 1337;
const outDir = join(repoRoot, args.out || 'tools/worldgen/demo');
mkdirSync(outDir, { recursive: true });

const { generateZone, RULESETS } = await import(join(repoRoot, 'game/js/worldgen/worldgen.js'));

const t0 = Date.now();
const zone = generateZone({ kind, seed });
const wallMs = Date.now() - t0;

if (!zone.layout.success) {
  console.error(`[worldgen] layout FAILED after ${zone.layout.attempts} attempts (seed ${seed})`);
  process.exit(1);
}

// ---- layout.json ----
const layoutJson = {
  kind, seed,
  width: zone.layout.width, height: zone.layout.height,
  tileset: zone.layout.tileset,
  names: zone.layout.names,
  meta: zone.meta,
};
writeFileSync(join(outDir, `${kind}-layout.json`), JSON.stringify(layoutJson));

// ---- layout.txt (ASCII) ----
const GLYPHS = {
  'temple-courtyard': { floor: '.', moss: ',', path: '#', 'path-corner': '+', 'path-t': 'T', pillar: 'P', wall: 'W', 'wall-corner': 'C', gate: 'G', lantern: 'o', pond: '~', tree: '*' },
  'hmw-forest': { clearing: '.', grass: ',', path: '#', 'path-corner': '+', tree: '*', rock: 'r', shrine: 'S', water: '~' },
};
const glyph = GLYPHS[kind] || {};
const ascii = zone.layout.names.map((row) => row.map((n) => glyph[n] || '?').join('')).join('\n');
writeFileSync(join(outDir, `${kind}-layout.txt`), `# ${kind} — seed ${seed} — ${zone.layout.width}x${zone.layout.height} — WFC attempts: ${zone.layout.attempts}\n${ascii}\n`);

const ruleset = RULESETS[zone.layout.ruleset] || RULESETS[kind];
// ---- layout.ppm (P6 binary, tile colors from the ruleset) ----
{
  const cmap = {};
  for (const t of ruleset.tiles) cmap[t.name] = t.color || [255, 0, 255];
  const lw = zone.layout.width, lh = zone.layout.height, s = 8;
  const px = Buffer.alloc(lw * s * lh * s * 3);
  zone.layout.names.forEach((row, y) => row.forEach((n, x) => {
    const c = cmap[n] || [255, 0, 255];
    for (let dy = 0; dy < s; dy++) for (let dx = 0; dx < s; dx++) {
      const i = ((y * s + dy) * lw * s + x * s + dx) * 3;
      px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2];
    }
  }));
  const header = Buffer.from(`P6\n# ${kind} WFC layout seed ${seed}\n${lw * s} ${lh * s}\n255\n`);
  writeFileSync(join(outDir, `${kind}-layout.ppm`), Buffer.concat([header, px]));
}

// ---- heightmap.ppm (P6 binary, terrain color ramp) ----
function terrainColor(h, min, max) {
  const t = Math.max(0, Math.min(1, (h - min) / (max - min || 1)));
  // deep water -> sand -> grass -> rock -> snow
  const stops = [[40, 90, 160], [194, 178, 128], [110, 150, 90], [130, 125, 115], [240, 244, 248]];
  const x = t * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(x));
  const f = x - i;
  return stops[i].map((c, k) => Math.round(c + (stops[i + 1][k] - c) * f));
}
{
  const { data, width, height, min, max } = zone.heightmap;
  const px = Buffer.alloc(width * height * 3);
  for (let i = 0; i < data.length; i++) {
    const [r, g, b] = terrainColor(data[i], min, max);
    px[i * 3] = r; px[i * 3 + 1] = g; px[i * 3 + 2] = b;
  }
  const header = Buffer.from(`P6\n# ${kind} heightmap seed ${seed}\n${width} ${height}\n255\n`);
  writeFileSync(join(outDir, `${kind}-heightmap.ppm`), Buffer.concat([header, px]));
}

// ---- demo.html (standalone, data embedded) ----
const tileColors = {};
for (const t of ruleset.tiles) tileColors[t.name] = t.color || [128, 128, 128];
// downsample heightmap for embedding
const HW = zone.heightmap.width, HH = zone.heightmap.height;
const dw = Math.min(HW, 80), dh = Math.min(HH, 56);
const small = [];
for (let y = 0; y < dh; y++) {
  for (let x = 0; x < dw; x++) {
    const sx = Math.floor((x / dw) * HW), sy = Math.floor((y / dh) * HH);
    small.push(Math.round(zone.heightmap.data[sy * HW + sx] * 100) / 100);
  }
}
const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WorldGen demo — ${kind} (seed ${seed})</title>
<style>body{margin:0;background:#0b0d12;color:#cfd6e4;font:14px system-ui}
h1{font-size:16px;padding:12px 16px 0}canvas{display:block;margin:12px 16px;border:1px solid #2a3040;max-width:calc(100vw - 32px)}
p{padding:0 16px;color:#8b93a8}</style></head><body>
<h1>Western Heart worldgen demo — ${kind} · seed ${seed} · layout ${zone.layout.width}×${zone.layout.height} · terrain ${HW}×${HH}</h1>
<canvas id="layout" width="${zone.layout.width * 8}" height="${zone.layout.height * 8}"></canvas>
<canvas id="terrain" width="${dw * 4}" height="${dh * 4}"></canvas>
<p>WFC layout (left): one 8px cell per tile, colored by ruleset tile color. FastNoiseLite terrain (right):
grayscale heightmap, min ${zone.heightmap.min.toFixed(2)} / max ${zone.heightmap.max.toFixed(2)}.
Generated in ${zone.meta.generatedMs.toFixed(0)} ms (runtime) — deterministic for this seed.</p>
<script>
const names = ${JSON.stringify(zone.layout.names)};
const colors = ${JSON.stringify(tileColors)};
const hm = ${JSON.stringify(small)};
const hmin = ${zone.heightmap.min}, hmax = ${zone.heightmap.max};
const lc = document.getElementById('layout').getContext('2d');
names.forEach((row, y) => row.forEach((n, x) => {
  const c = colors[n] || [255, 0, 255];
  lc.fillStyle = 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')';
  lc.fillRect(x * 8, y * 8, 8, 8);
}));
const tc = document.getElementById('terrain').getContext('2d');
hm.forEach((h, i) => {
  const x = i % ${dw}, y = Math.floor(i / ${dw});
  const t = Math.max(0, Math.min(1, (h - hmin) / ((hmax - hmin) || 1)));
  const v = Math.round(t * 255);
  tc.fillStyle = 'rgb(' + v + ',' + v + ',' + v + ')';
  tc.fillRect(x * 4, y * 4, 4, 4);
});
</script></body></html>`;
writeFileSync(join(outDir, `${kind}-demo.html`), html);

// ---- timings.json ----
const hBytes = zone.heightmap.data.byteLength;
const timings = {
  kind, seed,
  wallMs,
  runtimeReportedMs: Math.round(zone.meta.generatedMs * 10) / 10,
  layout: { w: zone.layout.width, h: zone.layout.height, attempts: zone.layout.attempts, success: zone.layout.success },
  terrain: { w: HW, h: HH, bytes: hBytes, min: zone.heightmap.min, max: zone.heightmap.max },
  props: zone.props.length,
  caveMask: zone.caveMask ? { w: zone.caveMask.width, h: zone.caveMask.height, openFraction: zone.caveMask.openFraction } : null,
  approxPeakMemoryKB: Math.round((hBytes + zone.layout.width * zone.layout.height * 64) / 1024),
  node: process.version, platform: process.platform,
};
writeFileSync(join(outDir, `${kind}-timings.json`), JSON.stringify(timings, null, 2));

console.log(`[worldgen] ${kind} seed ${seed}: layout ${zone.layout.width}x${zone.layout.height} ` +
  `ok in ${zone.layout.attempts} attempt(s), terrain ${HW}x${HH}, ${zone.props.length} props, ` +
  `${wallMs}ms wall -> ${outDir}`);
