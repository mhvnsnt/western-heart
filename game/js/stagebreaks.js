/* ============================================================
   WESTERN HEART — Stage mechanics (breakable geometry)
   Pulled from the teardowns:
   • TEKKEN floor breaks (T7: Forgotten Realm, Brimstone & Fire,
     Devil's Pit): a heavy slam / bound on a cracked floor section
     shatters it — both fighters drop to a lower level, the slammed
     fighter eats bonus damage, the fight continues below.
   • TEKKEN wall breaks (TTT2/T7): a heavy hit that splats the
     opponent into a breakable wall shatters it — bounds extend,
     bonus damage (DOA "Danger Zone" style).
   • TEKKEN balcony breaks (T7 Jungle Outpost 2): same as a floor
     break off a ledge edge.
   • DOA4/5/6 knock-through: power blows near breakable walls/floors
     burst INTO a new area — the transition IS the mechanic.
   Stage defs declare `breakables: [{type:'floor'|'wall'|'balcony',
   x, z, r, depth, ...}]`. Walls default ON for every stage (spirit
   barriers at ±wallDistance) unless the def sets `noWallBreak`.
   Breaks persist for the whole match (T7/DOA authentic) and reset on
   the next match.
   ============================================================ */
import * as THREE from 'three';
import { audio } from './audio.js';
// NOTE (loadspeed lane): this module must NOT statically import
// fighter.js (setArenaLimit/setGroundY stream via lazy.js). The Game
// injects them: bindStage(stageDef, fx) with
// fx = { setArenaLimit, setGroundY }.

export const WALL_BREAK_BONUS = 8;   // DOA danger-zone style bonus damage
export const FLOOR_BREAK_BONUS = 12;  // T7 floor-break slam bonus
const WALL_EXTEND = 4.5;             // bounds grow past a broken wall

function _crackTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d');
  x.fillStyle = 'rgba(0,0,0,0)'; x.fillRect(0, 0, 256, 256);
  x.strokeStyle = 'rgba(20,8,4,0.95)'; x.lineWidth = 5;
  // radial cracks from the center, like a stressed floor panel
  for (let i = 0; i < 11; i++) {
    const a = (i / 11) * Math.PI * 2 + Math.random() * 0.3;
    x.beginPath(); x.moveTo(128, 128);
    let px = 128, py = 128;
    for (let k = 0; k < 5; k++) {
      px += Math.cos(a + (Math.random() - 0.5) * 0.7) * 26;
      py += Math.sin(a + (Math.random() - 0.5) * 0.7) * 26;
      x.lineTo(px, py);
    }
    x.stroke();
  }
  x.strokeStyle = 'rgba(255,120,40,0.5)'; x.lineWidth = 2; // ember seams
  x.beginPath(); x.arc(128, 128, 120, 0, Math.PI * 2); x.stroke();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function _shimmerTexture() {
  const c = document.createElement('canvas'); c.width = 64; c.height = 128;
  const x = c.getContext('2d');
  const g = x.createLinearGradient(0, 0, 0, 128);
  g.addColorStop(0, 'rgba(255,255,255,0)');
  g.addColorStop(0.5, 'rgba(255,255,255,0.55)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 64, 128);
  const t = new THREE.CanvasTexture(c);
  return t;
}

export class StageBreaks {
  constructor(game) {
    this.game = game;
    this.group = new THREE.Group();
    this.group.name = 'stage-breaks';
    this.defs = [];
    this.stageDef = null;
    this.broken = new Set();
    this.groundY = 0;
    this._built = false;
    this._debris = [];
    this._barriers = new Map(); // id -> mesh
    this._zones = new Map();    // id -> mesh (floor/balcony markers)
    this._t = 0;
    this.fx = null; // injected { setArenaLimit, setGroundY } (see bindStage)
  }

  /* Bind to a stage at match start. Resets all break state. */
  bindStage(stageDef, fx) {
    if (fx) this.fx = fx;
    this.reset();
    this.stageDef = stageDef;
    const wallD = stageDef.dims.wallDistance;
    const defs = (stageDef.breakables || []).map((d) => ({ ...d }));
    if (!stageDef.noWallBreak) {
      defs.push({ type: 'wall', side: -1, x: -wallD });
      defs.push({ type: 'wall', side: 1, x: wallD });
    }
    this.defs = defs;
    const scene = this.game.arena && this.game.arena.scene;
    if (scene && !this.group.parent) scene.add(this.group);
  }

  /* Full reset (new match / leaving the fight): visuals out, bounds back. */
  reset() {
    for (const d of this._debris) this.group.remove(d.mesh);
    this._debris = [];
    this._barriers.clear();
    this._zones.clear();
    this.group.clear();
    this.broken.clear();
    this.defs = [];
    this.groundY = 0;
    this._built = false;
    if (this.fx) {
      this.fx.setGroundY(0);
      if (this.stageDef) this.fx.setArenaLimit(this.stageDef.dims.wallDistance);
    }
  }

  /* Per-round: NOT a reset — T7/DOA breaks persist for the whole match. */
  syncRound() {
    if (this.fx) this.fx.setGroundY(this.groundY);
  }

  /* Build breakable visuals lazily (stage content streams in async). */
  _ensureBuilt() {
    if (this._built || !this.stageDef) return;
    const arena = this.game.arena;
    if (!arena || !arena._stage || arena._stage.def.id !== this.stageDef.id) return;
    const tint = new THREE.Color(this.stageDef.swatch ? this.stageDef.swatch[1] : '#ff7a3c');
    for (const def of this.defs) {
      const id = this._id(def);
      if (def.type === 'wall') {
        const w = this.stageDef.dims.depth + 4, h = 3.4;
        const m = new THREE.Mesh(
          new THREE.PlaneGeometry(w, h),
          new THREE.MeshBasicMaterial({
            map: _shimmerTexture(), color: tint, transparent: true,
            opacity: 0.35, side: THREE.DoubleSide, depthWrite: false,
            blending: THREE.AdditiveBlending,
          })
        );
        m.position.set(def.x, 1.7, 0);
        m.rotation.y = Math.PI / 2;
        m.userData.barrier = true;
        this.group.add(m);
        this._barriers.set(id, m);
      } else { // floor / balcony: visible cracked weak section
        const r = def.r || 2.5;
        const m = new THREE.Mesh(
          new THREE.CircleGeometry(r, 28),
          new THREE.MeshBasicMaterial({ map: _crackTexture(), transparent: true, opacity: 0.85, depthWrite: false })
        );
        m.rotation.x = -Math.PI / 2;
        m.position.set(def.x || 0, 0.03, def.z || 0);
        this.group.add(m);
        this._zones.set(id, m);
        if (def.type === 'balcony') { // railing along the ledge edge
          const railMat = new THREE.MeshStandardMaterial({ color: 0x4a3220, roughness: 0.85 });
          const wdt = (def.w || 4);
          for (let i = 0; i <= 4; i++) {
            const post = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.1, 0.14), railMat);
            post.position.set((def.x || 0) - wdt / 2 + (i / 4) * wdt, 0.55, def.z || 0);
            post.castShadow = true;
            this.group.add(post);
            def._railPosts = def._railPosts || []; def._railPosts.push(post);
          }
          const rail = new THREE.Mesh(new THREE.BoxGeometry(wdt + 0.2, 0.1, 0.16), railMat);
          rail.position.set(def.x || 0, 1.12, def.z || 0);
          this.group.add(rail);
          (def._railPosts = def._railPosts || []).push(rail);
        }
      }
    }
    this._built = true;
  }

  _id(def) { return `${def.type}:${def.side ?? ''}${def.x ?? ''},${def.z ?? ''}`; }

  update(dt) {
    this._t += dt;
    this._ensureBuilt();
    // shimmer pulse on unbroken barriers
    for (const [id, m] of this._barriers) {
      if (this.broken.has(id)) continue;
      m.material.opacity = 0.28 + Math.sin(this._t * 3.1 + m.position.x) * 0.1;
    }
    // debris physics
    for (let i = this._debris.length - 1; i >= 0; i--) {
      const d = this._debris[i];
      d.life -= dt;
      if (d.life <= 0) { this.group.remove(d.mesh); this._debris.splice(i, 1); continue; }
      d.vel.y -= 18 * dt;
      d.mesh.position.addScaledVector(d.vel, dt);
      d.mesh.rotation.x += d.spin * dt; d.mesh.rotation.z += d.spin * 0.7 * dt;
      const f = Math.min(1, d.life / 0.6);
      d.mesh.material.opacity = f;
      if (d.mesh.position.y < this.groundY - (d.depth || 0)) {
        d.mesh.position.y = this.groundY - (d.depth || 0);
        d.vel.set(0, 0, 0); d.spin = 0;
      }
    }
  }

  _burst(x, y, z, color, n = 26, spread = 5, depth = 0) {
    const geo = new THREE.BoxGeometry(0.22, 0.22, 0.22);
    for (let i = 0; i < n; i++) {
      const mat = new THREE.MeshBasicMaterial({ color, transparent: true });
      const m = new THREE.Mesh(geo, mat);
      m.position.set(x + (Math.random() - 0.5), y + Math.random() * 0.8, z + (Math.random() - 0.5) * 2);
      const a = Math.random() * Math.PI * 2;
      this._debris.push({
        mesh: m, life: 1.1 + Math.random() * 0.7, depth,
        vel: new THREE.Vector3(Math.cos(a) * spread * Math.random(), 3 + Math.random() * 5, Math.sin(a) * spread * Math.random()),
        spin: (Math.random() - 0.5) * 12,
      });
      this.group.add(m);
    }
  }

  _bonusDamage(defender, amount, attacker) {
    if (defender.dead) return 'ko';
    defender.hp = Math.max(0, defender.hp - amount);
    if (defender.hp <= 0) {
      const dir = Math.sign(defender.root.position.x - attacker.root.position.x) || 1;
      defender._knockout(dir);
      return 'ko';
    }
    return 'hit';
  }

  /**
   * Called from Game._resolveCombat after a landed hit. Evaluates every
   * unbroken surface: heavy hits near breakable geometry break it.
   */
  checkHit(attacker, defender, move, result) {
    if (!this.stageDef || !this.game || this.game.roundState !== 'fight') return;
    if (result !== 'hit' && result !== 'counter' && result !== 'ko') return;
    this._ensureBuilt();
    const px = defender.root.position.x, pz = defender.root.position.z;
    const heavy = (move.knock >= 4) || !!move.launch || result === 'ko';
    if (!heavy) return;
    for (const def of this.defs) {
      const id = this._id(def);
      if (this.broken.has(id)) continue;
      if (def.type === 'wall') {
        // slammed into the wall: at/near the bound on that side
        if (Math.sign(px) === def.side && Math.abs(px) >= Math.abs(def.x) - 0.9) {
          this._breakWall(def, id, attacker, defender);
          return;
        }
      } else {
        // floor / balcony: slam-class hit landing inside the weak zone
        const slam = (move.knock >= 6) || !!move.launch || !!move.knockdown || result === 'ko';
        if (!slam) continue;
        const dx = px - (def.x || 0), dz = pz - (def.z || 0);
        const r = def.r || 2.5;
        if (dx * dx + dz * dz <= r * r) {
          if (def.type === 'balcony') this._breakBalcony(def, id, attacker, defender);
          else this._breakFloor(def, id, attacker, defender);
          return;
        }
      }
    }
  }

  /* ---------------- break sequences ---------------- */

  _breakWall(def, id, attacker, defender) {
    this.broken.add(id);
    const bar = this._barriers.get(id);
    if (bar) bar.visible = false;
    const bx = def.x, tint = 0xffb060;
    this._burst(bx, 1.6, 0, tint, 34, 6);
    this._burst(bx, 0.6, 0, 0x6a5a48, 20, 4);
    // DOA knock-through: the wall is GONE — bounds extend into the new area
    const newLimit = Math.abs(def.x) + WALL_EXTEND;
    if (this.fx) this.fx.setArenaLimit(newLimit);
    // breach dressing: broken chunks + glow beyond the breach (the "new area")
    const dir = Math.sign(def.x);
    for (let i = 0; i < 5; i++) {
      const chunk = new THREE.Mesh(
        new THREE.BoxGeometry(0.7 + Math.random(), 0.5 + Math.random() * 0.8, 0.7),
        new THREE.MeshStandardMaterial({ color: 0x5a4a3a, roughness: 0.95 })
      );
      chunk.position.set(bx + dir * (1 + Math.random() * 3), 0.3, (Math.random() - 0.5) * 7);
      chunk.rotation.y = Math.random() * 3;
      chunk.castShadow = true;
      this.group.add(chunk);
    }
    const glow = new THREE.Mesh(
      new THREE.PlaneGeometry(7, 4),
      new THREE.MeshBasicMaterial({ color: 0xff8a3c, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })
    );
    glow.position.set(bx + dir * 3.5, 2, 0);
    glow.rotation.y = Math.PI / 2;
    this.group.add(glow);
    const bonus = this._bonusDamage(defender, WALL_BREAK_BONUS, attacker);
    const g = this.game;
    g.arena.shake(0.55, 0.45);
    g._hitStop = Math.max(g._hitStop || 0, 0.14);
    try { audio.grab(); } catch (e) {}
    if (g.ui && g.ui.banner) g.ui.banner('WALL BREAK');
    if (bonus === 'ko') g.rage.onHitKO(attacker, defender);
    console.log(`[WH] stage break: wall (${def.side < 0 ? 'P1' : 'P2'} side) — bounds now ±${newLimit.toFixed(1)}`);
  }

  _breakFloor(def, id, attacker, defender) {
    this.broken.add(id);
    const zone = this._zones.get(id);
    if (zone) zone.visible = false;
    const fx = def.x || 0, fz = def.z || 0, r = def.r || 2.5;
    const depth = def.depth || 6;
    this._burst(fx, 0.4, fz, 0x8a7a68, 30, 5, depth);
    this._burst(fx, 0.2, fz, 0xff7a30, 14, 3, depth);
    // T7 floor break: the level drops — physics ground moves down, both
    // fighters fall through the hole, the fight continues below.
    this.groundY = -(depth);
    if (this.fx) this.fx.setGroundY(this.groundY);
    // lower-tier dressing: dark stone disc + ember lights (the level below)
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(r + 7.5, 36),
      new THREE.MeshStandardMaterial({ color: 0x241a14, roughness: 0.95 })
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.set(fx, this.groundY - 0.02, fz);
    disc.receiveShadow = true;
    this.group.add(disc);
    for (let i = 0; i < 3; i++) {
      const l = new THREE.PointLight(0xff6a2a, 14, 16, 2);
      const a = (i / 3) * Math.PI * 2;
      l.position.set(fx + Math.cos(a) * (r + 3.5), this.groundY + 2.2, fz + Math.sin(a) * (r + 3.5));
      this.group.add(l);
    }
    const bonus = this._bonusDamage(defender, FLOOR_BREAK_BONUS, attacker);
    const g = this.game;
    g.arena.shake(0.7, 0.6);
    g._hitStop = Math.max(g._hitStop || 0, 0.18);
    try { audio.ko(); } catch (e) {}
    if (g.ui && g.ui.banner) g.ui.banner('FLOOR BREAK');
    if (g.ui && g.ui.updateHP && g.p1 && g.p2) g.ui.updateHP(g.p1, g.p2);
    if (bonus === 'ko') g.rage.onHitKO(attacker, defender);
    console.log(`[WH] stage break: floor at (${fx},${fz}) — dropped to y=${this.groundY}`);
  }

  _breakBalcony(def, id, attacker, defender) {
    this.broken.add(id);
    const zone = this._zones.get(id);
    if (zone) zone.visible = false;
    // railing shatters outward
    for (const post of def._railPosts || []) {
      this._debris.push({
        mesh: post, life: 1.4, depth: def.depth || 6,
        vel: new THREE.Vector3((Math.random() - 0.5) * 3, 2 + Math.random() * 3, (Math.random() - 0.5) * 3),
        spin: (Math.random() - 0.5) * 10,
      });
      if (!post.parent) this.group.add(post);
    }
    def._railPosts = [];
    const fx = def.x || 0, fz = def.z || 0, r = def.r || 2.5;
    const depth = def.depth || 6;
    this._burst(fx, 1.0, fz, 0x7a5a40, 26, 5, depth);
    this.groundY = -(depth);
    if (this.fx) this.fx.setGroundY(this.groundY);
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(r + 7.5, 36),
      new THREE.MeshStandardMaterial({ color: 0x1c1620, roughness: 0.95 })
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.set(fx, this.groundY - 0.02, fz);
    disc.receiveShadow = true;
    this.group.add(disc);
    const bonus = this._bonusDamage(defender, FLOOR_BREAK_BONUS, attacker);
    const g = this.game;
    g.arena.shake(0.7, 0.6);
    g._hitStop = Math.max(g._hitStop || 0, 0.18);
    try { audio.ko(); } catch (e) {}
    if (g.ui && g.ui.banner) g.ui.banner('BALCONY BREAK');
    if (g.ui && g.ui.updateHP && g.p1 && g.p2) g.ui.updateHP(g.p1, g.p2);
    if (bonus === 'ko') g.rage.onHitKO(attacker, defender);
    console.log(`[WH] stage break: balcony at (${fx},${fz}) — dropped to y=${this.groundY}`);
  }
}
