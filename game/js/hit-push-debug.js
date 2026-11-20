/* ============================================================
   WESTERN HEART — hitbox / hurtbox / pushbox debug overlay
   ------------------------------------------------------------
   OpenKumite / FightingEngine public rule: hit boxes and push
   boxes are separate systems. WH already separates them
   (hitbox.js capsules vs fighter.js ground push cylinders).
   This module only visualizes them — it does not change combat.

   Toggle: press F4 in a fight, or load with ?hitboxes=1.
   Self-registers; looks for window.__whFight / __whGame fighters.
   ============================================================ */

const STATE = { on: false, lines: null, hooked: false };

function ensureLines(scene) {
  if (STATE.lines || !scene || !globalThis.THREE) return STATE.lines;
  const THREE = globalThis.THREE;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(4096 * 3);
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setDrawRange(0, 0);
  const mat = new THREE.LineBasicMaterial({ vertexColors: true, depthTest: false });
  STATE.lines = new THREE.LineSegments(geo, mat);
  STATE.lines.frustumCulled = false;
  STATE.lines.renderOrder = 999;
  scene.add(STATE.lines);
  return STATE.lines;
}

function colorFor(kind) {
  // hit = red, hurt = green, push = cyan (distinct; not gameplay)
  if (kind === 'hit') return [1, 0.15, 0.15];
  if (kind === 'push') return [0.15, 0.85, 1];
  return [0.2, 1, 0.35]; // hurt
}

function pushCapsule(arr, colors, x, y, z, r, h, kind) {
  const [cr, cg, cb] = colorFor(kind);
  const y0 = y, y1 = y + h;
  // vertical edges of an 8-gonal prism approx
  for (let i = 0; i < 8; i++) {
    const a0 = (i / 8) * Math.PI * 2;
    const a1 = ((i + 1) / 8) * Math.PI * 2;
    const x0 = x + Math.cos(a0) * r, z0 = z + Math.sin(a0) * r;
    const x1 = x + Math.cos(a1) * r, z1 = z + Math.sin(a1) * r;
    for (const yy of [y0, y1]) {
      arr.push(x0, yy, z0, x1, yy, z1);
      colors.push(cr, cg, cb, cr, cg, cb);
    }
    arr.push(x0, y0, z0, x0, y1, z0);
    colors.push(cr, cg, cb, cr, cg, cb);
  }
}

function fightersFromGame(g) {
  if (!g) return [];
  const out = [];
  if (g.p1) out.push(g.p1);
  if (g.p2) out.push(g.p2);
  if (Array.isArray(g.fighters)) out.push(...g.fighters);
  return out.filter(Boolean);
}

function findGame() {
  return globalThis.__whFight || globalThis.__whGame || globalThis.game || null;
}

function redraw() {
  if (!STATE.on) return;
  const g = findGame();
  if (!g || !g.scene) return;
  const lines = ensureLines(g.scene);
  if (!lines) return;
  const arr = [];
  const colors = [];
  for (const f of fightersFromGame(g)) {
    const root = f.root?.position;
    if (!root) continue;
    // pushbox — ground cylinder approx (matches fighter.js 1.45 ground / 0.55 air)
    const air = !f.onGround;
    const pushR = air ? 0.275 : 0.725;
    const pushH = air ? 0.55 : 1.7;
    pushCapsule(arr, colors, root.x, root.y, root.z, pushR, pushH, 'push');
    try {
      const hurts = typeof f.getHurtboxes === 'function' ? f.getHurtboxes() : [];
      for (const h of hurts || []) {
        const r = h.r || h.radius || 0.12;
        const p = h.pos || h.center || h;
        const x = p.x ?? root.x, y = p.y ?? root.y + 1, z = p.z ?? root.z;
        pushCapsule(arr, colors, x, y - r, z, r, r * 2, 'hurt');
      }
    } catch (_) { /* overlay only */ }
    try {
      const hb = typeof f.getHitbox === 'function' ? f.getHitbox() : null;
      if (hb) {
        const r = hb.r || hb.radius || 0.18;
        const p = hb.pos || hb.point || hb;
        const x = p.x ?? root.x, y = p.y ?? root.y + 1, z = p.z ?? root.z;
        pushCapsule(arr, colors, x, y - r, z, r, r * 2, 'hit');
      }
    } catch (_) { /* overlay only */ }
  }
  const pos = lines.geometry.getAttribute('position');
  const need = arr.length / 3;
  if (!lines.geometry.getAttribute('color') || lines.geometry.getAttribute('color').count < need) {
    lines.geometry.setAttribute('color', new globalThis.THREE.BufferAttribute(new Float32Array(Math.max(need, 1) * 3), 3));
  }
  const col = lines.geometry.getAttribute('color');
  if (need > pos.count) {
    lines.geometry.setAttribute('position', new globalThis.THREE.BufferAttribute(new Float32Array(arr), 3));
    lines.geometry.setAttribute('color', new globalThis.THREE.BufferAttribute(new Float32Array(colors), 3));
  } else {
    pos.array.set(arr);
    pos.needsUpdate = true;
    col.array.set(colors);
    col.needsUpdate = true;
  }
  lines.geometry.setDrawRange(0, need);
  lines.visible = true;
  requestAnimationFrame(redraw);
}

export function setHitPushDebug(on) {
  STATE.on = !!on;
  if (STATE.lines) STATE.lines.visible = STATE.on;
  if (STATE.on) requestAnimationFrame(redraw);
}

export function toggleHitPushDebug() {
  setHitPushDebug(!STATE.on);
  return STATE.on;
}

function boot() {
  if (STATE.hooked) return;
  STATE.hooked = true;
  const params = new URLSearchParams(location.search);
  if (params.get('hitboxes') === '1' || params.get('hitbox') === '1') setHitPushDebug(true);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'F4') {
      e.preventDefault();
      const on = toggleHitPushDebug();
      console.info('[WH] hit/hurt/push debug', on ? 'ON' : 'OFF');
    }
  });
}

boot();
