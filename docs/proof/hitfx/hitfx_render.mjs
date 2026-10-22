#!/usr/bin/env node
/* HitFX proof: loads the REAL game/js/hitfx.js texture builders (with a
   node-canvas document stub + minimal THREE stub), renders the spark / dot /
   ring textures to PNG, composites a mock impact frame, and logic-tests
   spawn()/update() incl. the hitstop-freeze behavior. */
import { createCanvas } from 'canvas';
import { writeFileSync } from 'fs';

// ---- document stub (node-canvas) ----
function stubElement() {
  return { style: {}, };
}
globalThis.document = {
  createElement(tag) {
    if (tag === 'canvas') return createCanvas(4, 4);
    if (tag === 'div') return stubElement();
    throw new Error('unexpected ' + tag);
  },
  body: { appendChild() {} },
};
globalThis.window = globalThis;

// ---- minimal THREE stub ----
class CanvasTexture { constructor(image) { this.image = image; } }
const THREE = {
  CanvasTexture,
  SRGBColorSpace: 'srgb',
  AdditiveBlending: 2,
  SpriteMaterial: class {
    constructor(o) { Object.assign(this, o); this.opacity = 1; this.rotation = 0; }
    dispose() {}
  },
  Sprite: class {
    constructor(mat) {
      this.material = mat;
      const p = { x: 0, y: 0, z: 0 };
      p.set = (x, y, z) => { p.x = x; p.y = y; p.z = z; };
      this.position = p;
      const s = { x: 1, y: 1, z: 1 };
      s.setScalar = (v) => { s.x = s.y = s.z = v; };
      this.scale = s;
      this.renderOrder = 0;
    }
  },
};
const scene = { added: [], add(o) { this.added.push(o); }, remove(o) { const i = this.added.indexOf(o); if (i >= 0) this.added.splice(i, 1); } };

// import the real module (data: URL with stubbed imports)
import { readFileSync } from 'fs';
let src = readFileSync('/home/hatch/workspace/fix3/hitfx/game/js/hitfx.js', 'utf8');
src = src.replace("import * as THREE from 'three';", '');
const modUrl = 'data:text/javascript;base64,' + Buffer.from(
  `const THREE = globalThis.__THREE_STUB__;\n` + src
).toString('base64');
globalThis.__THREE_STUB__ = THREE;
const hitfx = await import(modUrl);
const { makeSparkTexture, makeDotTexture, makeRingTexture, STYLE, HitFX } = hitfx;

const out = '/home/hatch/workspace/fix3/hitfx/proof';
// 1 — raw textures
for (const [name, fn] of [['spark', makeSparkTexture], ['dot', makeDotTexture], ['ring', makeRingTexture]]) {
  const tex = fn();
  writeFileSync(`${out}/fx-tex-${name}.png`, tex.image.toBuffer('image/png'));
  console.log(`fx-tex-${name}.png`, tex.image.width + 'x' + tex.image.height);
}

// 2 — composite mock impact frame (dark bg, gold hit spark + debris + ring)
function tint(canvas, hex) {
  const c = createCanvas(canvas.width, canvas.height);
  const x = c.getContext('2d');
  x.drawImage(canvas, 0, 0);
  x.globalCompositeOperation = 'source-atop';
  x.fillStyle = hex;
  x.fillRect(0, 0, c.width, c.height);
  return c;
}
{
  const W = 480, H = 320;
  const frame = createCanvas(W, H);
  const x = frame.getContext('2d');
  const bg = x.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#0a0812'); bg.addColorStop(1, '#161020');
  x.fillStyle = bg; x.fillRect(0, 0, W, H);
  // mock fighters: two dark silhouettes
  x.fillStyle = '#241d33';
  x.fillRect(120, 90, 60, 170); x.fillRect(300, 90, 60, 170);
  x.beginPath(); x.arc(150, 70, 22, 0, 7); x.fill();
  x.beginPath(); x.arc(330, 70, 22, 0, 7); x.fill();
  // impact at (240,160): ring + debris + spark, gold 'hit' style
  const cx = 240, cy = 160;
  const ring = tint(makeRingTexture().image, '#ffd76a');
  x.globalAlpha = 0.85; x.drawImage(ring, cx - 70, cy - 70, 140, 140); x.globalAlpha = 1;
  const dot = tint(makeDotTexture().image, '#ffca55');
  let seed = 42; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 12; i++) {
    const a = rnd() * Math.PI * 2, d = 24 + rnd() * 60, s = 6 + rnd() * 10;
    x.globalAlpha = 0.9;
    x.drawImage(dot, cx + Math.cos(a) * d - s / 2, cy + Math.sin(a) * d - s / 2, s, s);
  }
  x.globalAlpha = 1;
  const spark = tint(makeSparkTexture().image, '#ffd76a');
  x.drawImage(spark, cx - 64, cy - 64, 128, 128);
  writeFileSync(`${out}/fx-impact-hit.png`, frame.toBuffer('image/png'));
  console.log('fx-impact-hit.png (mock frame: gold spark + debris + ring)');
}
{
  // counter-hit variant: red-orange, bigger
  const W = 480, H = 320;
  const frame = createCanvas(W, H);
  const x = frame.getContext('2d');
  const bg = x.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#0a0812'); bg.addColorStop(1, '#161020');
  x.fillStyle = bg; x.fillRect(0, 0, W, H);
  x.fillStyle = '#241d33';
  x.fillRect(120, 90, 60, 170); x.fillRect(300, 90, 60, 170);
  x.beginPath(); x.arc(150, 70, 22, 0, 7); x.fill();
  x.beginPath(); x.arc(330, 70, 22, 0, 7); x.fill();
  const cx = 240, cy = 160;
  const ring = tint(makeRingTexture().image, '#ff4a1e');
  x.globalAlpha = 0.9; x.drawImage(ring, cx - 95, cy - 95, 190, 190); x.globalAlpha = 1;
  const dot = tint(makeDotTexture().image, '#ff6a2a');
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 18; i++) {
    const a = rnd() * Math.PI * 2, d = 26 + rnd() * 80, s = 6 + rnd() * 12;
    x.globalAlpha = 0.9;
    x.drawImage(dot, cx + Math.cos(a) * d - s / 2, cy + Math.sin(a) * d - s / 2, s, s);
  }
  x.globalAlpha = 1;
  const spark = tint(makeSparkTexture().image, '#ff4a1e');
  x.drawImage(spark, cx - 88, cy - 88, 176, 176);
  writeFileSync(`${out}/fx-impact-counter.png`, frame.toBuffer('image/png'));
  console.log('fx-impact-counter.png (mock frame: red-orange counter spark, bigger)');
}

// 3 — logic test: spawn every type, step update, verify drain + hitstop freeze
{
  const fx = new HitFX(scene);
  const types = Object.keys(STYLE);
  let totalSpawned = 0;
  for (const t of types) { fx.spawn(t, 0, 1.2, 0, { dirX: 1 }); totalSpawned += fx._items.length; }
  console.log(`spawned ${types.length} types -> ${totalSpawned} live items (spark+debris+ring each)`);
  const before = fx._items.length;
  fx.update(0); fx.update(0); // hitstop: dt=0 must freeze, not advance
  console.log(`hitstop freeze check: items before=${before} after dt=0 x2 -> ${fx._items.length} ${fx._items.length === before ? 'FROZEN OK' : 'FAIL'}`);
  let steps = 0;
  while (fx._items.length > 0 && steps < 600) { fx.update(1 / 60); steps++; }
  console.log(`drain: ${steps} steps @60fps to clear all effects ${fx._items.length === 0 ? 'OK' : 'FAIL (leak!)'}`);
  console.log(`scene sprites remaining: ${scene.added.length} ${scene.added.length === 0 ? 'OK' : 'FAIL (leak!)'}`);
  // flash element check
  fx.spawn('ko', 0, 1, 0);
  console.log(`screen flash on KO: ${fx._flashT > 0 ? 'OK' : 'FAIL'}`);
  fx.update(0.2);
  console.log(`flash decayed after 0.2s: ${fx._flashT <= 0 ? 'OK' : 'FAIL'}`);
}
console.log('HITFX PROOF COMPLETE');
