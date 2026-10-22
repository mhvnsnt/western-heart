/* ============================================================
   WESTERN HEART — "The Heart and Mind Inside": DEVIL WITHIN BRAWLER
   (worker 20, 2026-10-22 — phase 1: the Devil Within foundation)

   The 3D brawler core, cloned from Tekken 5's Devil Within skeleton:
     • free-roam 3D movement, third-person camera behind the fighter
     • simultaneous multi-enemy waves (melee / brute / gunner types)
     • 5 stages, zone-by-zone progression, a boss per stage:
         1. WARDEN (Gun-Jack analog: bruiser + heavy projectiles)
         2. THE MASKS (Heihachi-clone analog: 1, then 3 at once)
         3. THE DROWNED OGRE (True-Ogre analog: teleports, homing
            projectiles, fire blast)
         4. THE SOUL SPHERE (energy orb: contact damage, spawns monsters)
         5. SHADOW SELF → THE UNMASKED (True→Monstrous Ogre analog:
            second form, same descent)
     • Devil Gauge analog: the Nine-Soul Meter — full meter + transform
       input = SOUL SURGE FORM (timed devil-form power-up, any fighter)
     • soul-ember pickups (Devil Within's healing gems)
     • per-stage ranking (time / damage taken)

   CHARACTER SELECT, NOT FORCED JIN: any WH fighter plays the descent
   with THEIR moveset — attacks resolve through the fighter's
   TekkenBuffer + per-fighter moveset (worker 11's system, reused here,
   never duplicated).

   Layering: this module owns MECHANICS. The proprietary WH layer
   (per-character stories, echoes-as-inner-demons, shadow self, records)
   is owned by heartmind.js, which drives this module through hooks and
   passes its content builders in (no import cycle).
   ============================================================ */
import * as THREE from 'three';
import { Fighter, setArenaLimit, bankIdFor } from './fighter.js';
import { assets } from './assets.js';
import { getStage } from './stages.js';
import { ensureMovesets } from './movesets.js';
import { loadT3Clips } from './t3anims.js';
import { scaledAi } from './modes.js';
import { audio } from './audio.js';
import { applyFighterProfile } from './customization-consumer.js';
import { showLoading, hideLoading } from './menus.js';

const FIXED_DT = 1 / 120;
const MAX_ALIVE = 5;          // simultaneous enemies (Devil Within density)
const EMBER_HEAL = 22;        // soul-ember pickup heal
const EMBER_DROP_CHANCE = 0.35;

/* ---------------- small math ---------------- */
function angDiff(a, b) {
  return Math.atan2(Math.sin(a - b), Math.cos(a - b));
}
function turnToward(cur, want, maxStep) {
  const d = angDiff(want, cur);
  return cur + (Math.abs(d) <= maxStep ? d : Math.sign(d) * maxStep);
}

/* ---------------- wave tables ----------------
   Per stage key: zones of { waves: [ [ {t, n} ] ], boss }.
   t: echo | brute | gunner. Bosses are special-cased spawns. */
const WAVE_TABLES = {
  threshold: [
    { waves: [[{ t: 'echo', n: 2 }], [{ t: 'echo', n: 3 }]] },
    { waves: [[{ t: 'echo', n: 2 }, { t: 'gunner', n: 1 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }]] },
    { boss: 'warden' },
  ],
  masks: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'echo', n: 2 }, { t: 'gunner', n: 1 }]] },
    { waves: [[{ t: 'brute', n: 1 }, { t: 'echo', n: 2 }], [{ t: 'gunner', n: 2 }, { t: 'echo', n: 2 }]] },
    { boss: 'masks' },
  ],
  drowning: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'brute', n: 1 }, { t: 'gunner', n: 1 }]] },
    { waves: [[{ t: 'echo', n: 4 }], [{ t: 'brute', n: 2 }]] },
    { boss: 'ogre' },
  ],
  furnace: [
    { waves: [[{ t: 'gunner', n: 2 }, { t: 'echo', n: 2 }], [{ t: 'brute', n: 1 }, { t: 'echo', n: 3 }]] },
    { waves: [[{ t: 'echo', n: 4 }], [{ t: 'brute', n: 2 }, { t: 'gunner', n: 1 }]] },
    { boss: 'sphere' },
  ],
  stillpoint: [
    { waves: [[{ t: 'echo', n: 3 }], [{ t: 'brute', n: 1 }, { t: 'gunner', n: 1 }]] },
    { boss: 'shadow' },
  ],
};

const BOSS_LABEL = {
  warden: 'WARDEN OF THE THRESHOLD',
  masks: 'THE MASKS',
  ogre: 'THE DROWNED OGRE',
  sphere: 'THE SOUL SPHERE',
  shadow: null, // per-character (story.bossName)
};

/* ============================================================
   BrawlerAI — 3D beat-em-up brains for one enemy fighter.
   kind: echo | brute | gunner | warden | mask | ogre | shadow | shadow2
   ============================================================ */
class BrawlerAI {
  constructor(fighter, kind, personality, brawler) {
    this.f = fighter;
    this.kind = kind;
    this.B = brawler;
    this.aggr = personality.aggression ?? 0.6;
    this.react = personality.reaction ?? 0.55;
    this.thinkT = Math.random() * 0.8;
    this.strafeT = 0;
    this.strafeDir = 1;
    this.orbit = false;
    this.blockT = 0;
    this.shootT = 1.5 + Math.random() * 2;
    this.teleportT = 6 + Math.random() * 4;
    this.blastT = 3 + Math.random() * 3;
    this.slamT = 3 + Math.random() * 3;
  }

  get _ranged() { return this.kind === 'gunner'; }

  update(dt) {
    const f = this.f, p = this.B.player;
    if (!p || f.dead || f.state === 'ko') return;
    const dx = p.root.position.x - f.root.position.x;
    const dz = p.root.position.z - f.root.position.z;
    const dist = Math.hypot(dx, dz) || 0.001;

    // Face the player when free to act (smooth, brawler yaw).
    if (f.canAct() && dist < 16) {
      f.yaw = turnToward(f.yaw, Math.atan2(dx, dz), dt * 5);
    }
    // Thrown / in a throw lock: the brawler resolves the lock.
    if (f.state === 'thrown' || f.state === 'throwing') return;

    if (this._ranged) { this._updateRanged(dt, dx, dz, dist); return; }
    this._updateMelee(dt, dx, dz, dist);
    // Boss extras
    if (this.kind === 'ogre') this._ogreTricks(dt, dx, dz, dist);
    else if (this.kind === 'warden') this._wardenSlam(dt, dist);
    else if ((this.kind === 'shadow' || this.kind === 'shadow2') && f.meter >= f.maxMeter && dist < 3.2 && f.canAct()) {
      if (f.tryAttack('surge')) { audio.soulSurge(f.char.id); this.B._burst(f.root.position.x, 1.4, f.root.position.z, 0xb28dff, 1.6); }
    }
  }

  _moveToward(dx, dz, dist, speedMul = 1) {
    const f = this.f;
    if (!f.canAct()) return;
    const s = f.stats.speed * speedMul;
    f.vx = (dx / dist) * s;
    f.vz = (dz / dist) * s;
  }

  _updateMelee(dt, dx, dz, dist) {
    const f = this.f, p = this.B.player;
    const range = this.kind === 'brute' || this.kind === 'warden' ? 2.6 : 2.3;
    this.thinkT -= dt;

    // Reactive defense (gated by reaction stat).
    const pAttacking = p.state === 'attack' && p._attackPhase !== 'recovery';
    if (pAttacking && dist < 3.4 && f.canAct() && Math.random() < this.react * dt * 2.4) {
      const r = Math.random();
      if (r < 0.5) { f.tryBlock(true); this.blockT = 0.35 + Math.random() * 0.3; }
      else f.tryDodge();
      this.thinkT = Math.max(this.thinkT, 0.5);
      return;
    }
    if (f.isBlocking()) {
      this.blockT -= dt;
      if (this.blockT <= 0 || !pAttacking) f.tryBlock(false);
      else return;
    }

    if (dist > range) {
      // Approach — brutes lumber, masks dart. Occasional orbit strafing
      // so the pack doesn't stack up in a conga line (Devil Within packs
      // circle the player).
      this.strafeT -= dt;
      if (this.strafeT <= 0) {
        this.strafeT = 0.9 + Math.random() * 1.8;
        this.strafeDir = Math.random() < 0.5 ? -1 : 1;
        this.orbit = Math.random() < 0.4;
      }
      let mx = dx / dist, mz = dz / dist;
      if (this.orbit && dist < 7) {
        mx = (-dz / dist) * this.strafeDir * 0.85 + (dx / dist) * 0.45;
        mz = (dx / dist) * this.strafeDir * 0.85 + (dz / dist) * 0.45;
      }
      const spd = f.stats.speed * (this.kind === 'brute' || this.kind === 'warden' ? 0.92 : 1.12);
      if (f.canAct()) { f.vx = mx * spd; f.vz = mz * spd; }
    } else if (this.thinkT <= 0 && f.canAct()) {
      // In range: strike with a Tekken limb — the fighter's own moveset
      // resolves the notation (strings/motions via its TekkenBuffer).
      const r = Math.random();
      let act;
      if ((this.kind === 'brute' || this.kind === 'warden') && r < 0.22) {
        act = Math.random() < 0.5 ? '1+3' : '2+4'; // grapplers hunt throws
      } else {
        act = ['1', '2', '3', '4'][Math.floor(Math.random() * 4)];
      }
      if (f.tryAttack(act)) audio.whiff();
      this.thinkT = 0.5 + Math.random() * Math.max(0.4, 2.0 - this.aggr * 1.4);
    }
  }

  _updateRanged(dt, dx, dz, dist) {
    const f = this.f;
    this.shootT -= dt;
    if (dist > 10) this._moveToward(dx, dz, dist, 1.05);
    else if (dist < 5.5) this._moveToward(-dx, -dz, dist, 0.9); // keep distance
    else if (f.canAct()) {
      // strafe slowly while holding range
      this.strafeT -= dt;
      if (this.strafeT <= 0) { this.strafeT = 1.4 + Math.random(); this.strafeDir = Math.random() < 0.5 ? -1 : 1; }
      f.vx = (-dz / dist) * this.strafeDir * f.stats.speed * 0.5;
      f.vz = (dx / dist) * this.strafeDir * f.stats.speed * 0.5;
    }
    if (this.shootT <= 0 && dist < 12.5 && f.canAct()) {
      this.B._fireProjectile(f, this.B.player, {
        speed: 9.5, dmg: 9, color: 0xff5544, r: 0.32, unblockable: false,
      });
      f.tryAttack('2'); // the shot plays off a jab anim
      audio.whiff();
      this.shootT = 2.3 + Math.random() * 1.7;
    }
  }

  _ogreTricks(dt, dx, dz, dist) {
    const f = this.f, B = this.B, p = B.player;
    // Teleport near the player, then a homing volley (True Ogre).
    this.teleportT -= dt;
    if (this.teleportT <= 0 && f.canAct()) {
      this.teleportT = 7 + Math.random() * 5;
      const a = Math.random() * Math.PI * 2;
      const px = p.root.position.x, pz = p.root.position.z;
      f.root.position.x = px + Math.sin(a) * 4.2;
      f.root.position.z = pz + Math.cos(a) * 4.2;
      f.vx = 0; f.vz = 0;
      B._burst(f.root.position.x, 1.2, f.root.position.z, 0x39d353, 1.8);
      audio.soulSurge(f.char.id);
      for (let i = 0; i < 3; i++) {
        setTimeout(() => {
          if (!f.dead && B.state === 'play') {
            B._fireProjectile(f, p, {
              speed: 7.5, dmg: 11, color: 0x39d353, r: 0.36,
              homing: 2.6, unblockable: true,
            });
          }
        }, i * 260);
      }
      return;
    }
    // Fire blast: point-blank AoE, telegraphed by the burst.
    this.blastT -= dt;
    if (this.blastT <= 0 && dist < 4.2 && f.canAct()) {
      this.blastT = 4.5 + Math.random() * 3;
      B._burst(f.root.position.x, 1.0, f.root.position.z, 0xff7a1a, 2.6);
      B.game.arena.shake(0.5, 0.35);
      audio.soulSurge(f.char.id);
      const pd = Math.hypot(
        p.root.position.x - f.root.position.x,
        p.root.position.z - f.root.position.z);
      if (pd < 3.8) {
        p.receiveHit({ damage: 16, knock: 6, unblockable: true, hitWord: 0x607, soulGain: 0 }, f);
        B._onPlayerDamaged(16);
        B._burst(p.root.position.x, 1.2, p.root.position.z, 0xff7a1a, 1.4);
      }
    }
  }

  _wardenSlam(dt, dist) {
    // Modified Gun-Jack analog: heavy blockable projectiles.
    const f = this.f;
    this.slamT -= dt;
    if (this.slamT <= 0 && dist < 9 && dist > 2.5 && f.canAct()) {
      this.slamT = 4 + Math.random() * 2.5;
      this.B._fireProjectile(f, this.B.player, {
        speed: 11, dmg: 17, color: 0xffb020, r: 0.45, unblockable: false,
      });
      f.tryAttack('2');
      audio.whiff();
    }
  }
}

/* ---------------- glow texture (shared) ---------------- */
let _glowTex = null;
function glowTexture() {
  if (_glowTex) return _glowTex;
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.45)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 64);
  _glowTex = new THREE.CanvasTexture(c);
  return _glowTex;
}

const DUMMY_HP = { hp: 1, maxHp: 1 };
const DUMMY_METER = { meter: 0, maxMeter: 100 };

/* ============================================================
   BrawlerGame — owns the whole descent run.
   deps: { game, input, ui, getChar, roster, content }
   content: { stages, makeEcho, buildShadowSelf } (from heartmind.js)
   hooks: { onStageIntro, onBossIntro, onStageClear, onVictory, onDeath }
   ============================================================ */
export class BrawlerGame {
  constructor(deps) {
    this.game = deps.game;
    this.input = deps.input;
    this.ui = deps.ui;
    this.getChar = deps.getChar;
    this.roster = deps.roster || [];
    this.content = deps.content;
    this.state = 'idle'; // idle | loading | play | over
    this.zoneState = 'idle'; // idle | combat | advance
    this.player = null;
    this.playerChar = null;
    this.enemies = [];
    this.projectiles = [];
    this.pickups = [];
    this.sphere = null;
    this.spawnQueue = [];
    this.zones = [];
    this._casts = [];
    this._hitStop = 0;
    this._acc = 0;
    this._blocking = false;
    this._dying = false;
    this._deathT = 0;
    this._victoryT = 0;
    this._zoneLive = false;
    this._bossPhase = null;
    this._shadowBase = null;
    this._statusT = 0;
    this.camYaw = Math.PI / 2;
    this.stats = { stageTime: 0, dmgTaken: 0, kills: 0, embers: 0, rank: [] };
    // Boss-label override for the proprietary layer (stage 5 story name).
    this.bossLabelFor = null;
  }

  /* ---------------- run setup ---------------- */
  async begin(charId, hooks) {
    this.hooks = hooks || {};
    this.state = 'loading';
    const char = this.getChar(charId);
    if (!char) throw new Error('[WH] brawler: unknown fighter ' + charId);
    this.playerChar = char;
    this.stats = { stageTime: 0, dmgTaken: 0, kills: 0, embers: 0, rank: [] };
    showLoading('DESCENDING…');
    try {
      // Fresh sim (also stops any previous brawler via Game's guard).
      this.game.resetFightState();
      this.input.brawlerMode = true;
      this.input.reset();
      this.input.enable(false); // enabled once the run is live

      // Model + moveset preload: the player, every stage's echo cast,
      // and the player's transform targets (mid-match forms).
      const needModels = new Set([char.model || 'pantera']);
      const needMoves = new Set([char.id]);
      if (char.transform && char.transform.targetModel) needModels.add(char.transform.targetModel);
      if (char.forms) for (const fk of Object.keys(char.forms)) {
        const fe = char.forms[fk];
        for (const t of (fe.target ? [fe] : [fe.up, fe.down].filter(Boolean))) {
          if (t.target) needModels.add(t.target);
          if (t.moveset) needMoves.add(t.moveset);
        }
      }
      this._casts = [];
      for (let s = 0; s < this.content.stages.length; s++) {
        const cast = this._buildCast(char.id, 5);
        this._casts.push(cast);
        for (const base of cast) {
          needModels.add(base.model || 'pantera');
          needMoves.add(base.id);
        }
      }
      await assets.loadModels([...needModels], (p) => {
        showLoading(`ENTERING… ${Math.round(p * 100)}%`);
      });
      await ensureMovesets([...needMoves]);
      try {
        const banks = [...new Set([...needMoves].map((id) => bankIdFor(id)).filter(Boolean))];
        await Promise.all(banks.map((b) => loadT3Clips(THREE, b)));
      } catch (e) {
        console.warn('[WH] brawler T3 clips fallback:', e.message || e);
      }

      // The player — any WH fighter, their own moveset, brawler body.
      const p = new Fighter(char, 0, 1, true);
      p.brawler = true;
      p.yaw = Math.PI / 2;
      p._sceneRef = this.game.arena;
      applyFighterProfile(p); // async, fire-and-forget (same as versus)
      this.game.arena.scene.add(p.root);
      this.player = p;
      this.enemies = [];
      this.projectiles = [];
      this.pickups = [];
      this.sphere = null;
      this.spawnQueue = [];
      this._hitStop = 0;
      this._acc = 0;
      this._blocking = false;
      this._dying = false;
      this._zoneLive = false;
      this._bossPhase = null;
      this.camYaw = Math.PI / 2;
      this.ui.setNames(char.name, 'THE DARK INSIDE');
      this.ui.setRounds({ p1: 0, p2: 0 });
      const st0 = document.getElementById('brawler-status');
      if (st0) st0.style.display = 'block';
      this.game.arena.camOverride = (dt, cam, sh) => this._camera(dt, cam, sh);
      this.game.brawler = this;
      this.state = 'play';
      this.input.enable(true);
      hideLoading();
      this._startStage(0);
    } catch (e) {
      hideLoading();
      this.input.brawlerMode = false;
      this.state = 'idle';
      console.error('[WH] brawler begin failed:', e);
      throw e;
    }
  }

  _buildCast(playerId, n) {
    const pool = this.roster.filter((c) => c.id !== playerId && !c.boss);
    const list = pool.length >= n ? pool : this.roster.filter((c) => c.id !== playerId);
    const cast = [];
    const used = new Set();
    let guard = 0;
    while (cast.length < Math.min(n, list.length) && guard++ < 200) {
      const c = list[Math.floor(Math.random() * list.length)];
      if (!c || used.has(c.id)) continue;
      used.add(c.id);
      cast.push(c);
    }
    return cast;
  }

  /* ---------------- stages & zones ---------------- */
  _startStage(i) {
    this.stageIdx = i;
    const st = this.content.stages[i];
    this.stageDef = st;
    const arenaStage = getStage(st.stage);
    setArenaLimit(arenaStage.dims.wallDistance);
    this.arenaR = arenaStage.dims.wallDistance;
    this.game.arena.setStage(st.stage);
    if (this.ui.setStageName) this.ui.setStageName(st.name);
    this._layoutZones(st);
    this.stats.stageTime = 0;
    this.stats.dmgTaken = 0;
    // breather between stages: the eater grows
    const p = this.player;
    p.hp = Math.min(p.maxHp, p.hp + p.maxHp * 0.25);
    p.vx = 0; p.vz = 0; p.vy = 0;
    const z0 = this.zones[0];
    p.root.position.set(z0.cx - z0.r * 0.4, 0, z0.cz);
    p.yaw = Math.PI / 2;
    this.camYaw = Math.PI / 2;
    const done = () => {
      this.ui.banner(st.name);
      this._startZone(0);
    };
    if (this.hooks.onStageIntro) this.hooks.onStageIntro(i, done);
    else done();
  }

  _layoutZones(st) {
    const table = WAVE_TABLES[st.key] || WAVE_TABLES.threshold;
    const R = this.arenaR;
    const n = table.length;
    this.zones = table.map((zd, i) => {
      const cx = n === 1 ? 0 : -R * 0.52 + (i * (R * 1.04)) / (n - 1);
      return {
        cx, cz: 0, r: Math.min(6.5, R * 0.44),
        waves: zd.waves ? zd.waves.map((w) => w.map((s) => ({ ...s }))) : null,
        boss: zd.boss || null,
        waveIdx: 0,
      };
    });
  }

  _startZone(z) {
    this.zoneIdx = z;
    this.zoneState = 'combat';
    this._zoneLive = false;
    const zone = this.zones[z];
    zone.waveIdx = 0;
    if (zone.boss) {
      const def = BOSS_LABEL[zone.boss] || 'THE BOSS';
      const label = this.bossLabelFor
        ? this.bossLabelFor(this.stageIdx, zone.boss, def) || def
        : def;
      const go = () => {
        this._zoneLive = true;
        this.ui.banner(label);
        this.ui.setNames(this.playerChar.name, label);
        this._spawnBoss(zone.boss, zone);
      };
      if (this.hooks.onBossIntro) this.hooks.onBossIntro(this.stageIdx, zone.boss, label, go);
      else go();
    } else {
      this._zoneLive = true;
      this.ui.banner(`ZONE ${z + 1} — ${this.stageDef.name}`);
      this._queueWave(zone);
    }
  }

  _queueWave(zone) {
    const wave = zone.waves[zone.waveIdx];
    if (!wave) return;
    let t = 0.3;
    for (const spec of wave) {
      for (let k = 0; k < spec.n; k++) {
        const a = Math.random() * Math.PI * 2;
        const rr = zone.r * (0.55 + Math.random() * 0.35);
        let x = zone.cx + Math.sin(a) * rr;
        let zz = zone.cz + Math.cos(a) * rr;
        // never spawn on top of the player
        const pd = Math.hypot(x - this.player.root.position.x, zz - this.player.root.position.z);
        if (pd < 3.5) { x = zone.cx - Math.sin(a) * rr; zz = zone.cz - Math.cos(a) * rr; }
        this.spawnQueue.push({ type: spec.t, x, z: zz, t });
        t += 0.7;
      }
    }
    zone.waveIdx++;
  }

  /* ---------------- spawning ---------------- */
  _spawnEnemy(type, x, z) {
    const st = this.stageDef;
    const diff = st.diff || 0.5;
    const statMul = 0.75 + diff * 0.55;
    const cast = this._casts[this.stageIdx];
    const base = cast[Math.floor(Math.random() * cast.length)];
    let charData = this.content.makeEcho(base, diff);
    let hp = 60, scale = 1;
    if (type === 'brute') {
      hp = 150; scale = 1.22;
      charData = { ...charData, name: 'BRUTE ECHO' };
    } else if (type === 'gunner') {
      hp = 50;
      charData = { ...charData, name: 'ECHO GUNNER' };
    }
    const f = new Fighter(charData, x, 1, false);
    f.brawler = true;
    f.root.position.z = z;
    f.yaw = Math.atan2(this.player.root.position.x - x, this.player.root.position.z - z);
    // Echoes fight with their base fighter's REAL moveset (worker 11's
    // per-fighter data), not the generic fallback: rebind the moveset id
    // and the T3 anim bank onto the echo's rig.
    f._movesetId = base.id;
    if (f.tekken) f.tekken.fighterId = base.id;
    try { f._bindT3(f.model, base.id, charData.model); } catch (e) { /* procedural fallback */ }
    if (scale !== 1) f.root.scale.multiplyScalar(scale);
    if (type === 'brute') f.stats.power *= 1.3;
    f.maxHp = Math.round(hp * statMul);
    f.hp = f.maxHp;
    f._sceneRef = this.game.arena;
    applyFighterProfile(f);
    this.game.arena.scene.add(f.root);
    const e = {
      fighter: f,
      ai: new BrawlerAI(f, type, charData.ai || { aggression: 0.55, reaction: 0.5 }, this),
      kind: type, boss: false, deathT: 0,
    };
    this.enemies.push(e);
    this._burst(x, 1.0, z, 0x6a1fb0, 1.2);
    return f;
  }

  _spawnBossFighter(kind, x, z, o = {}) {
    const diff = this.stageDef.diff || 0.5;
    const statMul = 0.8 + diff * 0.6;
    let charData = o.charData;
    if (!charData) {
      const cast = this._casts[this.stageIdx];
      const base = cast[(this.stageIdx + this.enemies.length) % cast.length];
      charData = this.content.makeEcho(base, diff);
      o.movesetId = o.movesetId || base.id;
    }
    if (o.label) charData = { ...charData, name: o.label };
    if (o.powerMul) {
      charData = {
        ...charData,
        stats: { ...(charData.stats || {}), power: ((charData.stats || {}).power || 1.1) * o.powerMul },
      };
    }
    const f = new Fighter(charData, x, 1, false);
    f.brawler = true;
    f.root.position.z = z;
    if (o.scale && o.scale !== 1) f.root.scale.multiplyScalar(o.scale);
    f.yaw = Math.atan2(this.player.root.position.x - x, this.player.root.position.z - z);
    if (o.movesetId) {
      f._movesetId = o.movesetId;
      if (f.tekken) f.tekken.fighterId = o.movesetId;
      try { f._bindT3(f.model, o.movesetId, charData.model); } catch (e) { /* procedural */ }
    }
    f.maxHp = Math.round((o.hp || 300) * statMul);
    f.hp = f.maxHp;
    f._sceneRef = this.game.arena;
    applyFighterProfile(f);
    this.game.arena.scene.add(f.root);
    const e = {
      fighter: f,
      ai: new BrawlerAI(f, kind, charData.ai || { aggression: 0.7, reaction: 0.6 }, this),
      kind, boss: true, deathT: 0,
    };
    this.enemies.push(e);
    this._burst(x, 1.2, z, 0xb28dff, 1.8);
    return f;
  }

  _spawnBoss(kind, zone) {
    const zx = zone.cx, zz = zone.cz;
    if (kind === 'masks') {
      // Devil Within's Heihachi clones: ONE first, then THREE at once.
      this._spawnBossFighter('mask', zx + 3, zz,
        { hp: 135, scale: 1.05, label: 'MASK OF ' + this.stageDef.name, powerMul: 1.15 });
      this._bossPhase = { kind: 'masks', stage: 1 };
    } else if (kind === 'sphere') {
      this._spawnSphere(zone);
      this._bossPhase = { kind: 'sphere' };
    } else if (kind === 'shadow') {
      this._shadowBase = this.content.buildShadowSelf(this.playerChar);
      this._spawnBossFighter('shadow', zx + 3.5, zz,
        { hp: 460, scale: 1.0, charData: this._shadowBase, movesetId: this.playerChar.id });
      this._bossPhase = { kind: 'shadow', stage: 1 };
    } else {
      // warden (Gun-Jack analog) / ogre (True-Ogre analog)
      const hp = kind === 'ogre' ? 520 : 380;
      const scale = kind === 'ogre' ? 1.42 : 1.35;
      this._spawnBossFighter(kind, zx + 3.5, zz,
        { hp, scale, label: BOSS_LABEL[kind], powerMul: 1.45 });
      this._bossPhase = { kind, stage: 1 };
    }
  }

  _spawnShadowForm2(x, z) {
    // True→Monstrous Ogre: the shadow refuses to fall — second form,
    // same descent. Bigger, meaner, its own bar.
    const base = this._shadowBase;
    const charData = {
      ...base,
      id: base.id + '-unmasked',
      name: 'THE UNMASKED',
      title: 'Yourself, Unmasked — Unleashed',
      stats: {
        ...base.stats,
        power: base.stats.power * 1.3,
        speed: Math.min(3.6, base.stats.speed * 1.12),
        defense: base.stats.defense * 1.1,
      },
      colors: { suit: 0x0a0a14, trim: 0xff2a55 },
    };
    return this._spawnBossFighter('shadow2', x, z, {
      hp: 320, scale: 1.28, charData, movesetId: this.playerChar.id,
    });
  }

  _spawnSphere(zone) {
    const g = new THREE.Group();
    const core = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.05, 1),
      new THREE.MeshBasicMaterial({ color: 0xb28dff, transparent: true, opacity: 0.92 })
    );
    const glow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0x8a2be2, transparent: true, opacity: 0.75,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    glow.scale.set(4.2, 4.2, 1);
    const light = new THREE.PointLight(0x9a5cff, 20, 9, 1.8);
    g.add(core); g.add(glow); g.add(light);
    g.position.set(zone.cx + 3.5, 1.7, zone.cz);
    this.game.arena.scene.add(g);
    this.sphere = {
      mesh: g, core, hp: 420, maxHp: 420, spawnT: 6, contactT: 0,
      r: 1.25, t: Math.random() * 10,
    };
    this._burst(zone.cx + 3.5, 1.7, zone.cz, 0x9a5cff, 2.2);
  }

  /* ---------------- projectiles & pickups ---------------- */
  _fireProjectile(from, target, { speed, dmg, color, r, homing, unblockable }) {
    const a = from.root.position;
    const b = target.root.position;
    const dx = b.x - a.x, dz = b.z - a.z;
    const d = Math.hypot(dx, dz) || 1;
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(r, 10, 10),
      new THREE.MeshBasicMaterial({ color })
    );
    const glow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color, transparent: true, opacity: 0.8,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    glow.scale.set(r * 6, r * 6, 1);
    mesh.add(glow);
    mesh.position.set(a.x + (dx / d) * 0.8, 1.3, a.z + (dz / d) * 0.8);
    this.game.arena.scene.add(mesh);
    this.projectiles.push({
      mesh, vx: (dx / d) * speed, vz: (dz / d) * speed, speed,
      dmg, r, homing: homing || 0, unblockable: !!unblockable,
      life: 4, from,
    });
  }

  _dropEmber(x, z) {
    const mesh = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(), color: 0xffd76a, transparent: true, opacity: 0.95,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    mesh.scale.set(0.9, 0.9, 1);
    mesh.position.set(x, 0.8, z);
    this.game.arena.scene.add(mesh);
    this.pickups.push({ mesh, t: Math.random() * 10, life: 25 });
  }

  /* ---------------- main loop (driven by Game._loop) ---------------- */
  frame(dt) {
    if (this.state !== 'play') return;
    // Tekken hitstop freezes the sim (hitfx already keys off game._hitStop).
    if (this.game._hitStop > 0) { this.game._hitStop -= dt; return; }
    this._acc += dt;
    let n = 0;
    while (this._acc >= FIXED_DT && n < 6) { this._update(FIXED_DT); this._acc -= FIXED_DT; n++; }
    if (n === 6) this._acc = 0;
    this._hud();
  }

  _update(dt) {
    if (this.state !== 'play') return;
    this.stats.stageTime += dt;

    // Dying: let the death read, no input, no AI.
    if (this._dying) {
      this._deathT -= dt;
      this.player.update(dt, null);
      for (const e of this.enemies) if (!e.fighter.dead) e.fighter.update(dt, null);
      if (this._deathT <= 0) {
        this.state = 'over';
        if (this.hooks.onDeath) this.hooks.onDeath(
          { stage: this.stageIdx + 1, zone: this.zoneIdx + 1, kills: this.stats.kills },
          () => {});
      }
      return;
    }
    // Victory beat: pose, then hand off.
    if (this._victoryT > 0) {
      this._victoryT -= dt;
      this.player.update(dt, null);
      if (this._victoryT <= 0) {
        this.state = 'over';
        if (this.hooks.onVictory) this.hooks.onVictory(() => {});
      }
      return;
    }

    // Spawn queue (staggered, capped simultaneous).
    for (let i = this.spawnQueue.length - 1; i >= 0; i--) {
      const s = this.spawnQueue[i];
      s.t -= dt;
      if (s.t <= 0) {
        const alive = this.enemies.filter((e) => !e.fighter.dead).length;
        if (alive < MAX_ALIVE) {
          if (s.boss) this._spawnBossFighter(s.boss, s.x, s.z, s.bossOpts || {});
          else this._spawnEnemy(s.type, s.x, s.z);
          this.spawnQueue.splice(i, 1);
        } else {
          s.t = 0.5; // wait for room on screen
        }
      }
    }

    this._updatePlayer(dt);
    for (const e of this.enemies) {
      e.ai.update(dt);
      e.fighter.update(dt, null);
      if (e.fighter.dead && !e.counted) {
        e.counted = true;
        e.deathT = 2.2;
        this.stats.kills++;
        this._burst(e.fighter.root.position.x, 1.0, e.fighter.root.position.z, 0x3a2a5a, 1.3);
        if (Math.random() < EMBER_DROP_CHANCE) {
          this._dropEmber(e.fighter.root.position.x, e.fighter.root.position.z);
        }
        if (e.boss) this._bossDown(e);
      }
      if (e.counted) {
        e.deathT -= dt;
        if (e.deathT <= 0 && !e.removed) {
          e.removed = true;
          this.game.arena.scene.remove(e.fighter.root);
        }
      }
    }
    this._updateProjectiles(dt);
    this._updatePickups(dt);
    this._updateSphere(dt);
    this._separate();
    this._resolveHits();
    this._resolveThrowLocks();
    this._clampToZone();
    this._checkZoneClear();
  }

  /* ---------------- player ---------------- */
  _updatePlayer(dt) {
    const p = this.player, inp = this.input;
    // Camera-relative movement (Devil Within analog run).
    let mx = inp.axisX, mz = inp.axisY;
    if (Math.abs(inp.joyY) > Math.abs(mz)) mz = inp.joyY;
    const mLen = Math.hypot(mx, mz);
    if (mLen > 0.15 && p.canAct()) {
      const sy = Math.sin(this.camYaw), cy = Math.cos(this.camYaw);
      // forward = (sy, cy); right = (-cy, sy)
      const wx = sy * (mz / mLen) + -cy * (mx / mLen);
      const wz = cy * (mz / mLen) + sy * (mx / mLen);
      const spd = p.stats.speed * 1.4;
      const cl = Math.min(1, mLen);
      p.vx = wx * spd * cl;
      p.vz = wz * spd * cl;
      p.yaw = turnToward(p.yaw, Math.atan2(wx, wz), dt * 11);
      // swing the camera behind the run direction
      const dy = angDiff(p.yaw, this.camYaw);
      if (Math.abs(dy) > 0.5) this.camYaw = turnToward(this.camYaw, p.yaw, dt * 2.0);
      // feed the Tekken direction buffer for motion/directional inputs
      const fx = Math.sin(p.yaw), fz = Math.cos(p.yaw);
      const f = wx * fx + wz * fz;
      const stick = f > 0.25 ? 'f' : f < -0.25 ? 'b' : 'n';
      p.tekken.noteDirection(stick);
      p.setStick(stick);
    } else {
      p.setStick('n');
    }

    // Caught in a throw: limb inputs are break attempts (Tekken rules).
    if (p.state === 'thrown') {
      for (const act of inp.consume()) {
        if (/^[1234](\+[1234])*$/.test(act) && p.tryThrowBreak(act)) {
          this.ui.throwEscape(true);
          audio.block();
        }
      }
      p.update(dt, null);
      return;
    }
    if (p.state === 'throwing') { p.update(dt, null); inp.consume(); return; }

    for (const act of inp.consume()) {
      if (act === 'punch' || act === 'kick' || act === 'grab' ||
          /^[1234](\+[1234])*$/.test(act)) {
        // Devil Within auto-face: snap to the nearest foe before striking.
        const tgt = this._nearestFoe(3.8);
        if (tgt) p.yaw = Math.atan2(tgt.x - p.root.position.x, tgt.z - p.root.position.z);
        if (p.tryAttack(act)) audio.whiff();
      }
      else if (act === 'surge') {
        if (p.tryAttack('surge')) {
          audio.soulSurge(p.char.id);
          this.ui.surgeFlash(p.char.surge.color, p.char.surge.accent);
          this.ui.surgeName(p.char.surge.name);
        }
      }
      else if (act === 'transform') {
        // Devil Within: FULL gauge + transform = devil form.
        if (p.canTransform('up')) {
          if (p.tryTransform('up')) audio.soulSurge(p.char.id);
        } else if (p.startSurgeForm()) {
          audio.soulSurge(p.char.id);
          this.ui.surgeFlash(p.char.surge.color, p.char.surge.accent);
          this.ui.surgeName(p.char.surge.name);
          this.ui.banner('SOUL SURGE — ' + p.char.surge.name);
        }
      }
      else if (act === 'transform-down') {
        if (p.tryTransform('down')) audio.soulSurge(p.char.id);
        else p.startSurgeForm();
      }
      else if (act === 'dodge') { p.tryDodge(); }
    }
    // Block (edge-triggered).
    const wantBlock = !!inp.held.block;
    if (wantBlock !== this._blocking) {
      this._blocking = wantBlock;
      p.tryBlock(wantBlock);
    }
    p.update(dt, null);
  }

  _nearestFoe(maxDist) {
    let best = null, bd = maxDist;
    const px = this.player.root.position.x, pz = this.player.root.position.z;
    const consider = (x, z) => {
      const d = Math.hypot(x - px, z - pz);
      if (d < bd) { bd = d; best = { x, z }; }
    };
    for (const e of this.enemies) {
      if (e.fighter.dead) continue;
      consider(e.fighter.root.position.x, e.fighter.root.position.z);
    }
    if (this.sphere && this.sphere.hp > 0) {
      consider(this.sphere.mesh.position.x, this.sphere.mesh.position.z);
    }
    return best;
  }

  _onPlayerDamaged(dealt) {
    this.stats.dmgTaken += Math.max(0, dealt);
  }

  /* ---------------- combat resolution (multi-target) ---------------- */
  _resolveHits() {
    const p = this.player;
    if (p.dead) return;
    // enemies -> player
    for (const e of this.enemies) {
      const f = e.fighter;
      if (f.dead) continue;
      const hb = f.getHitbox();
      if (hb) this._hitFighterVs(f, p, hb);
      if (p.dead) return;
    }
    // player -> enemies (one hit per swing, Tekken rule)
    const phb = p.getHitbox();
    if (phb) {
      for (const e of this.enemies) {
        const f = e.fighter;
        if (f.dead) continue;
        if (this._hitFighterVs(p, f, phb)) break;
      }
      // player -> soul sphere
      if (this.sphere && this.sphere.hp > 0) {
        const s = this.sphere.mesh.position;
        const dx = phb.x - s.x, dy = phb.y - s.y, dz = phb.z - s.z;
        const rr = phb.r + this.sphere.r;
        if (dx * dx + dy * dy + dz * dz <= rr * rr) {
          p.registerHit();
          const dmg = phb.move.damage * p.stats.power;
          this.sphere.hp -= dmg;
          this._burst(s.x, s.y, s.z, 0xb28dff, 1.2);
          audio.punch();
          this.game._hitStop = Math.max(this.game._hitStop, 0.05);
          this.game.arena.shake(0.25, 0.18);
          this.ui.combo(Math.max(1, p.registerCombo()));
          if (this.sphere.hp <= 0) this._sphereDown();
        }
      }
    }
  }

  _hitFighterVs(attacker, defender, hb) {
    const hurts = defender.getHurtboxes();
    for (const hu of hurts) {
      const dx = hb.x - hu.x, dy = hb.y - hu.y, dz = hb.z - hu.z;
      const rr = hb.r + hu.r;
      if (dx * dx + dy * dy + dz * dz > rr * rr) continue;
      if (!defender.canBeHitBy(hb.move)) return null;
      attacker.registerHit();
      // Throws enter the breakable lock (both directions).
      if (hb.move.isGrab && defender.onGround &&
          defender.state !== 'thrown' && defender.state !== 'throwing') {
        defender.startThrowLock(hb.move, attacker);
        attacker.startThrowing(defender);
        if (defender.isPlayer) this.ui.throwBreakPrompt(true, hb.move.throw_break || '1');
        audio.grab();
        this.game.arena.shake(0.3, 0.2);
        this.game._hitStop = Math.max(this.game._hitStop, 0.06);
        return 'throw';
      }
      const hpBefore = defender.hp;
      const result = defender.receiveHit(hb.move, attacker);
      const dealt = Math.max(0, hpBefore - defender.hp);
      if (result === 'block') {
        audio.block();
        this.game._hitStop = Math.max(this.game._hitStop, 0.04);
        attacker.combo = 0;
        this._burst(hb.x, hb.y, hb.z, 0x9adfff, 0.7);
      } else if (result === 'dodge') {
        // i-frames: nothing
      } else if (result === 'ko') {
        audio.ko(); audio.grunt(defender.isPlayer ? 1.1 : 0.85);
        this.game.arena.shake(0.5, 0.4);
        this.game._hitStop = Math.max(this.game._hitStop, 0.12);
        this._burst(hb.x, hb.y, hb.z, 0xffcf4d, 1.4);
      } else {
        const heavy = (hb.move.knock || 0) >= 4;
        if (attacker.attackName === 'kick') audio.kick();
        else if (attacker.attackName === 'grab') audio.grab();
        else if (attacker.attackName !== 'surge') audio.punch();
        audio.grunt(defender.isPlayer ? 1.05 : 0.9);
        this.game.arena.shake(heavy ? 0.35 : 0.18, 0.18);
        this.game._hitStop = Math.max(this.game._hitStop, heavy ? 0.08 : 0.05);
        const col = attacker.attackName === 'surge'
          ? attacker.char.surge.color
          : (attacker.char.colors.trim || 0xffffff);
        this._burst(hb.x, hb.y, hb.z, col, heavy ? 1.0 : 0.6);
        if (attacker.isPlayer) this.ui.combo(Math.max(1, attacker.registerCombo()));
      }
      if (defender.isPlayer) {
        this._onPlayerDamaged(dealt);
        if (result === 'ko') this._playerDown();
      }
      return result;
    }
    return null;
  }

  _resolveThrowLocks() {
    const all = [this.player, ...this.enemies.map((e) => e.fighter)];
    for (const atk of all) {
      if (atk.state === 'throwing' && atk.lockT <= 0 && atk.lockMove) {
        const def = atk.lockVictim;
        const hpBefore = def ? def.hp : 0;
        const result = atk.completeThrow();
        const dealt = def ? Math.max(0, hpBefore - def.hp) : 0;
        this.ui.throwBreakPrompt(false);
        if (result === 'ko') {
          audio.ko();
          this.game.arena.shake(0.5, 0.4);
          this.game._hitStop = Math.max(this.game._hitStop, 0.12);
          if (def) this._burst(def.root.position.x, 1.2, def.root.position.z, 0xffcf4d, 1.4);
        } else if (result && result !== 'dodge') {
          audio.grab();
          this.game.arena.shake(0.45, 0.28);
          this.game._hitStop = Math.max(this.game._hitStop, 0.1);
          if (def) this._burst(def.root.position.x, 1.2, def.root.position.z, 0xffffff, 1.1);
        }
        if (def && def.isPlayer) {
          this._onPlayerDamaged(dealt);
          if (result === 'ko') this._playerDown();
        } else if (def && atk.isPlayer && result && result !== 'dodge') {
          this.ui.combo(Math.max(1, atk.registerCombo()));
        }
      }
    }
  }

  /* ---------------- projectiles ---------------- */
  _updateProjectiles(dt) {
    const p = this.player;
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const pr = this.projectiles[i];
      pr.life -= dt;
      if (pr.homing > 0 && !p.dead) {
        const px = p.root.position.x - pr.mesh.position.x;
        const pz = p.root.position.z - pr.mesh.position.z;
        const d = Math.hypot(px, pz) || 1;
        const k = Math.min(1, pr.homing * dt);
        pr.vx = (pr.vx / pr.speed + (px / d - pr.vx / pr.speed) * k) * pr.speed;
        pr.vz = (pr.vz / pr.speed + (pz / d - pr.vz / pr.speed) * k) * pr.speed;
      }
      pr.mesh.position.x += pr.vx * dt;
      pr.mesh.position.z += pr.vz * dt;
      let dead = pr.life <= 0;
      if (!p.dead && !dead) {
        for (const hu of p.getHurtboxes()) {
          const dx = pr.mesh.position.x - hu.x;
          const dy = pr.mesh.position.y - hu.y;
          const dz = pr.mesh.position.z - hu.z;
          const rr = pr.r + hu.r;
          if (dx * dx + dy * dy + dz * dz <= rr * rr) {
            const fake = {
              damage: pr.dmg, knock: 4.5, soulGain: 0,
              unblockable: pr.unblockable,
              hitWord: pr.unblockable ? 0x607 : 0x217,
            };
            if (p.canBeHitBy(fake)) {
              const hpBefore = p.hp;
              const res = p.receiveHit(fake, pr.from);
              this._onPlayerDamaged(Math.max(0, hpBefore - p.hp));
              this._burst(pr.mesh.position.x, pr.mesh.position.y, pr.mesh.position.z, 0xffaa33, 1.1);
              audio.grunt(1.0);
              this.game.arena.shake(0.3, 0.22);
              if (res === 'ko') this._playerDown();
            }
            dead = true;
            break;
          }
        }
      }
      if (dead) {
        this.game.arena.scene.remove(pr.mesh);
        pr.mesh.geometry.dispose();
        pr.mesh.material.dispose();
        this.projectiles.splice(i, 1);
      }
    }
  }

  /* ---------------- pickups ---------------- */
  _updatePickups(dt) {
    const pp = this.player.root.position;
    for (let i = this.pickups.length - 1; i >= 0; i--) {
      const pk = this.pickups[i];
      pk.life -= dt;
      pk.t += dt;
      pk.mesh.position.y = 0.8 + Math.sin(pk.t * 3) * 0.15;
      const dx = pp.x - pk.mesh.position.x, dz = pp.z - pk.mesh.position.z;
      const d = Math.hypot(dx, dz) || 1;
      if (d < 2.6 && d > 0.01) {
        // soul embers drift to the eater
        pk.mesh.position.x += (dx / d) * 6 * dt;
        pk.mesh.position.z += (dz / d) * 6 * dt;
      }
      let take = false;
      if (d < 0.9) take = true;
      if (take || pk.life <= 0) {
        if (take && !this.player.dead) {
          this.player.hp = Math.min(this.player.maxHp, this.player.hp + EMBER_HEAL);
          this.player.addMeter(10);
          this.stats.embers++;
          audio.uiClick();
          this._burst(pk.mesh.position.x, 1.0, pk.mesh.position.z, 0xffd76a, 1.0);
        }
        this.game.arena.scene.remove(pk.mesh);
        pk.mesh.material.dispose();
        this.pickups.splice(i, 1);
      }
    }
  }

  /* ---------------- soul sphere boss ---------------- */
  _updateSphere(dt) {
    const s = this.sphere;
    if (!s) return;
    s.t += dt;
    const p = this.player.root.position;
    s.mesh.position.y = 1.7 + Math.sin(s.t * 1.7) * 0.25;
    s.core.rotation.y += dt * 1.3;
    s.core.rotation.x += dt * 0.6;
    const dx = p.x - s.mesh.position.x, dz = p.z - s.mesh.position.z;
    const d = Math.hypot(dx, dz) || 1;
    if (!this.player.dead) {
      if (d > 4.2) {
        s.mesh.position.x += (dx / d) * 1.6 * dt;
        s.mesh.position.z += (dz / d) * 1.6 * dt;
      } else if (d < 2.6) {
        s.mesh.position.x -= (dx / d) * 1.2 * dt;
        s.mesh.position.z -= (dz / d) * 1.2 * dt;
      }
    }
    // Contact damage — the sphere burns on touch (Devil Within).
    s.contactT -= dt;
    if (d < 1.9 && s.contactT <= 0 && !this.player.dead) {
      s.contactT = 1.1;
      const dummy = { root: { position: s.mesh.position }, stats: { power: 1.1 } };
      const hpBefore = this.player.hp;
      this.player.receiveHit(
        { damage: 13, knock: 5, unblockable: true, hitWord: 0x607, soulGain: 0 }, dummy);
      this._onPlayerDamaged(Math.max(0, hpBefore - this.player.hp));
      this._burst(p.x, 1.2, p.z, 0x9a5cff, 1.3);
      audio.grunt(1.0);
      if (this.player.hp <= 0) this._playerDown();
    }
    // Generate monsters (Devil Within: the sphere spits them out).
    s.spawnT -= dt;
    const minions = this.enemies.filter((e) => !e.fighter.dead).length;
    if (s.spawnT <= 0 && minions < 4 && !this._dying) {
      s.spawnT = 11;
      this.ui.banner('THE SPHERE SPITS OUT DEMONS');
      for (let k = 0; k < 2; k++) {
        const a = Math.random() * Math.PI * 2;
        this.spawnQueue.push({
          type: 'echo',
          x: s.mesh.position.x + Math.sin(a) * 2.5,
          z: s.mesh.position.z + Math.cos(a) * 2.5,
          t: 0.5 + k * 0.8,
        });
      }
    }
  }

  _sphereDown() {
    const s = this.sphere;
    if (!s) return;
    const sp = s.mesh.position;
    this._burst(sp.x, sp.y, sp.z, 0x9a5cff, 3.0);
    audio.ko();
    this.game.arena.shake(0.6, 0.4);
    for (let k = 0; k < 3; k++) {
      this._dropEmber(sp.x + (Math.random() - 0.5) * 3, sp.z + (Math.random() - 0.5) * 3);
    }
    this.game.arena.scene.remove(s.mesh);
    this.sphere = null;
  }

  /* ---------------- bodies, zones, flow ---------------- */
  _separate() {
    const bodies = [this.player];
    for (const e of this.enemies) if (!e.fighter.dead) bodies.push(e.fighter);
    for (let i = 0; i < bodies.length; i++) {
      for (let j = i + 1; j < bodies.length; j++) {
        const a = bodies[i], b = bodies[j];
        if (a.dead || b.dead) continue;
        if (Math.abs(a.root.position.y - b.root.position.y) > 1.8) continue;
        const dx = a.root.position.x - b.root.position.x;
        const dz = a.root.position.z - b.root.position.z;
        const d = Math.hypot(dx, dz);
        const min = 1.15;
        if (d < min && d > 0.001) {
          const push = (min - d) / 2;
          const nx = dx / d, nz = dz / d;
          a.root.position.x += nx * push; a.root.position.z += nz * push;
          b.root.position.x -= nx * push; b.root.position.z -= nz * push;
        }
      }
    }
  }

  _clampToZone() {
    const p = this.player.root.position;
    if (this.zoneState === 'combat') {
      const z = this.zones[this.zoneIdx];
      if (!z) return;
      const clamp = (v, r) => {
        const dx = v.x - z.cx, dz = v.z - z.cz;
        const d = Math.hypot(dx, dz);
        if (d > r && d > 0.001) {
          v.x = z.cx + (dx / d) * r;
          v.z = z.cz + (dz / d) * r;
        }
      };
      clamp(p, z.r);
      // Enemies stay in the fight pocket too (Devil Within): a kiting
      // gunner must not be able to leave the zone and stall the wave
      // forever while the player is walled inside it.
      for (const e of this.enemies) {
        if (!e.fighter.dead) clamp(e.fighter.root.position, z.r + 1.5);
      }
    } else if (this.zoneState === 'advance') {
      const nz = this.zones[this.zoneIdx + 1];
      if (nz && Math.hypot(p.x - nz.cx, p.z - nz.cz) < nz.r * 0.75) {
        this._startZone(this.zoneIdx + 1);
      }
    }
  }

  _checkZoneClear() {
    if (this.zoneState !== 'combat' || !this._zoneLive || this._dying) return;
    const zone = this.zones[this.zoneIdx];
    if (!zone) return;
    if (this.spawnQueue.length > 0) return;
    const alive = this.enemies.some((e) => !e.fighter.dead);
    // A boss killed by the player's blow this same tick hasn't run
    // _bossDown yet (deaths process in the enemies loop). Don't clear
    // the zone before multi-phase transitions (shadow form 2) spawn.
    const unprocessedBossDeath = this.enemies.some(
      (e) => e.boss && e.fighter.dead && !e.counted);
    const sphereAlive = this.sphere && this.sphere.hp > 0;
    if (alive || unprocessedBossDeath || sphereAlive) return;
    if (!zone.boss && zone.waveIdx < zone.waves.length) {
      this._queueWave(zone);
      this.ui.banner(`WAVE ${zone.waveIdx + 1}/${zone.waves.length}`);
      return;
    }
    if (this.zoneIdx + 1 < this.zones.length) {
      this.zoneState = 'advance';
      this.ui.banner('PATH OPEN — PUSH FORWARD');
      audio.bell();
    } else {
      this._stageClear();
    }
  }

  _bossDown(e) {
    const bp = this._bossPhase;
    const fp = e.fighter.root.position;
    this._burst(fp.x, 1.2, fp.z, 0xffd76a, 2.0);
    audio.ko();
    if (!bp) return;
    if (bp.kind === 'masks' && bp.stage === 1) {
      // Devil Within's Heihachi clones: the first falls, THREE rise at once.
      bp.stage = 2;
      this.ui.banner('THE MASKS MULTIPLY');
      const zone = this.zones[this.zoneIdx];
      for (let k = 0; k < 3; k++) {
        this.spawnQueue.push({
          boss: 'mask', x: zone.cx + (k - 1) * 2.5, z: zone.cz + (k % 2 ? 2 : -2),
          t: 0.6 + k * 0.7,
          bossOpts: { hp: 135, scale: 1.05, label: 'MASK OF ' + this.stageDef.name, powerMul: 1.15 },
        });
      }
    } else if (bp.kind === 'shadow' && bp.stage === 1) {
      // True→Monstrous Ogre: the shadow refuses to fall — second form.
      bp.stage = 2;
      this.ui.banner('THE SHADOW REFUSES TO FALL');
      this.game.arena.shake(0.6, 0.5);
      const x = fp.x, z = fp.z;
      this.game.arena.scene.remove(e.fighter.root);
      e.removed = true;
      // _spawnShadowForm2 pushes its own form-2 rec; pop it back off and
      // place it in form-1's slot (pop+replace is safe mid-iteration;
      // splice is not). No double-spawn, no skipped enemies.
      this._spawnShadowForm2(x, z);
      const form2 = this.enemies.pop();
      const idx = this.enemies.indexOf(e);
      if (idx >= 0) this.enemies[idx] = form2;
      else this.enemies.push(form2);
      this.ui.setNames(this.playerChar.name, 'THE UNMASKED');
    }
  }

  _rank() {
    const t = this.stats.stageTime, d = this.stats.dmgTaken;
    if (t < 150 && d < 50) return 'S';
    if (t < 240 && d < 120) return 'A';
    if (t < 360) return 'B';
    return 'C';
  }

  _stageClear() {
    const i = this.stageIdx;
    const rank = this._rank();
    this.stats.rank[i] = rank;
    this.ui.banner(`STAGE ${i + 1} CLEARED — RANK ${rank}`);
    audio.bell();
    const next = () => {
      if (i + 1 >= this.content.stages.length) {
        // The descent is complete.
        this._victoryT = 1.4;
        this.player.victory();
      } else {
        this._startStage(i + 1);
      }
    };
    if (this.hooks.onStageClear) this.hooks.onStageClear(i, rank, next);
    else next();
  }

  _playerDown() {
    if (this._dying || this.state !== 'play') return;
    this._dying = true;
    this._deathT = 1.8;
    audio.ko();
    this.game.arena.shake(0.6, 0.5);
  }

  /* ---------------- third-person camera ---------------- */
  _camera(dt, camera, sh) {
    if (!this.player) return;
    const p = this.player.root.position;
    const sy = Math.sin(this.camYaw), cy = Math.cos(this.camYaw);
    const tx = p.x - sy * 5.8, ty = p.y + 3.3, tz = p.z - cy * 5.8;
    const k = Math.min(1, dt * 3.2);
    camera.position.x += (tx - camera.position.x) * k;
    camera.position.y += (ty - camera.position.y) * k;
    camera.position.z += (tz - camera.position.z) * k;
    camera.position.x += sh.ox;
    camera.position.y += sh.oy;
    camera.lookAt(p.x + sy * 1.9, p.y + 1.35, p.z + cy * 1.9);
  }

  /* ---------------- HUD ---------------- */
  _bossView() {
    let best = null;
    for (const e of this.enemies) {
      if (e.fighter.dead) continue;
      if (e.boss) return e.fighter; // the boss owns the bar
      if (!best || e.fighter.hp > best.hp) best = e.fighter;
    }
    return best || DUMMY_HP;
  }

  _hud() {
    if (!this.player || this.state === 'idle') return;
    const p = this.player;
    this.ui.updateHP(p, this._bossView());
    this.ui.updateMeter(p, DUMMY_METER);
    this.ui.setTimer(Math.floor(this.stats.stageTime));
    const now = performance.now();
    if (now - this._statusT > 250) {
      this._statusT = now;
      const el = document.getElementById('brawler-status');
      if (el) {
        const foes = this.enemies.filter((e) => !e.fighter.dead).length +
          (this.sphere && this.sphere.hp > 0 ? 1 : 0);
        const z = this.zones[this.zoneIdx];
        const where = z && z.boss ? 'BOSS' : `ZONE ${this.zoneIdx + 1}/${this.zones.length}`;
        el.textContent = `STAGE ${this.stageIdx + 1}/5 · ${where} · FOES ${foes}`;
      }
    }
  }

  /* ---------------- impact FX ---------------- */
  _burst(x, y, z, color, scale = 1) {
    const scene = this.game.arena.scene;
    const group = new THREE.Group();
    const mat = new THREE.MeshBasicMaterial({
      color, transparent: true, opacity: 1,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const flash = new THREE.Mesh(new THREE.SphereGeometry(0.45 * scale, 12, 12), mat);
    group.add(flash);
    const parts = [];
    const pgeo = new THREE.SphereGeometry(0.12, 6, 6);
    for (let i = 0; i < 10; i++) {
      const m = new THREE.Mesh(pgeo, mat.clone());
      const a = (i / 10) * Math.PI * 2 + Math.random() * 0.5;
      m.userData.v = new THREE.Vector3(
        Math.cos(a) * (3 + Math.random() * 2),
        1 + Math.random() * 3,
        Math.sin(a) * (3 + Math.random() * 2));
      group.add(m);
      parts.push(m);
    }
    group.position.set(x, y, z);
    scene.add(group);
    let life = 0.4;
    const tick = () => {
      life -= 0.016;
      const f = Math.max(0, life / 0.4);
      flash.scale.setScalar(1 + (1 - f) * 2.2);
      flash.material.opacity = f * 0.9;
      for (const m of parts) {
        m.position.addScaledVector(m.userData.v, 0.016);
        m.userData.v.y -= 9 * 0.016;
        m.material.opacity = f;
        m.scale.setScalar(Math.max(0.01, f));
      }
      if (life > 0) requestAnimationFrame(tick);
      else {
        scene.remove(group);
        flash.geometry.dispose();
        pgeo.dispose();
      }
    };
    requestAnimationFrame(tick);
  }

  /* ---------------- teardown ---------------- */
  stop() {
    if (this.state === 'idle') return;
    this.state = 'idle';
    try {
      this.input.brawlerMode = false;
      this.input.enable(false);
      this.game.arena.camOverride = null;
      const scene = this.game.arena.scene;
      if (this.player) scene.remove(this.player.root);
      for (const e of this.enemies) scene.remove(e.fighter.root);
      for (const pr of this.projectiles) scene.remove(pr.mesh);
      for (const pk of this.pickups) scene.remove(pk.mesh);
      if (this.sphere) scene.remove(this.sphere.mesh);
      const el = document.getElementById('brawler-status');
      if (el) el.style.display = 'none';
      this.ui.throwBreakPrompt(false);
    } catch (e) {
      console.warn('[WH] brawler stop:', e.message || e);
    }
    this.player = null;
    this.enemies = [];
    this.projectiles = [];
    this.pickups = [];
    this.sphere = null;
    if (this.game.brawler === this) this.game.brawler = null;
  }
}
