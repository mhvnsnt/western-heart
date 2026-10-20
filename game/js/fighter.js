/* ============================================================
   WESTERN HEART — Fighter
   Rigged 3D human (Mixamo skeleton). Mocap base layer (Idle /
   Walk / Run) + procedural CCD-IK combat layer on the real bones.

   WESTERN HEART systems (WH-original, per owner design):
     • NINE-SOUL METER — 0..100. Light hit +8, heavy +11, taking
       damage +6, blocking +4. All 9 souls lit = Soul Surge ready.
     • SOUL SURGE — costs 100. 0.24s startup / 0.20s active /
       18 damage (before defense scaling), per-character aura.
     • COMMAND GRAB — unblockable at close range (P+K / J+K / U).
       Pantera is built around it (grappler).
   Combat frame data: REAL Tekken 3 (teardown/tekken3/movesets/).
     • Pantera = King (652 T3 moves), Demonio = Jin (413 T3 moves).
     • Startup/active/recovery from 60fps frame counts; damage
       scaled T3 170HP -> WH 100HP. See game/assets/*_moves.json.
   Hitboxes vs hurtboxes, blocking w/ 12% chip + blockstun,
   hitstop, knockback, launchers, camera shake.
   ============================================================ */
import * as THREE from 'three';
import { assets } from './assets.js';
import { getT3Clips, createT3Actions, SOURCE_TO_BANK } from './t3anims.js';
import { TekkenBuffer, getFighterMoveset } from './movesets.js';
import { TransformCinematic } from './transform-cinematic.js';

// ---- Frame data: REAL Tekken 3 data (teardown/tekken3/movesets/moveset_king.json, moveset_jin.json)
// NOTE (owner canon 2026-10-19): Tekken's Jin = DEMONIO in Western Heart. The 'jin' moveset family is now 'demonio'.
// Extracted 2026-10-14: representative light/medium/heavy from 652 King / 413 Jin moves.
// 60fps frame counts -> seconds. Damage scaled T3 170HP -> WH 100HP.
// game/assets/king_moves.json + jin_moves.json hold the full extraction (jin = demonio per canon).
// This fallback uses King averages; the JSONs load per-character at boot.
let MOVES = {
  punch: { startup: 0.30, active: 0.017, recovery: 0.55, damage: 7, knock: 2.2, soulGain: 8, cost: 0, limb: 'armR', heavy: false },
  kick: { startup: 0.25, active: 0.017, recovery: 0.80, damage: 15, knock: 4.2, soulGain: 11, cost: 0, limb: 'legR', heavy: true },
  grab: { startup: 0.467, active: 0.05, recovery: 0.633, damage: 24, knock: 6.5, soulGain: 10, cost: 0, limb: 'armR', heavy: true, unblockable: true, isGrab: true },
  surge: { startup: 0.24, active: 0.20, recovery: 0.42, damage: 18, knock: 7.8, soulGain: 0, cost: 100, limb: 'armR', heavy: true },
};

/* Fighter ID -> real T3 moveset. Every fighter uses frame data from the
   closest available Tekken 3 teardown moveset (teardown/tekken3/movesets/).
   T3 only shipped 7 extracted movesets; fighters whose Tekken base wasn't
   extracted map to the closest archetype. */
const MOVESET_MAP = {
  // THE NINE SOULS
  rin: 'demonio', byou: 'demonio', tou: 'heihachi', sha: 'xiaoyu', kai: 'demonio',
  jin_soul: 'yoshimitsu', retsu: 'bryan', zen: 'heihachi', gyou: 'demonio',
  // MAIN ROSTER
  pantera: 'king', demonio: 'demonio', phantom: 'yoshimitsu', diablo: 'heihachi',
  skull: 'bryan', samura1: 'gunjack', sakura: 'xiaoyu',
  // BONUS ROSTER
  zui: 'demonio', kinpo: 'demonio', waterfall: 'demonio', kingtyrant: 'xiaoyu', burger: 'bryan',
  awapop: 'demonio', scimitar: 'demonio', purplerain: 'demonio', nightwolf: 'xiaoyu',
  dio: 'heihachi', cyborgx: 'gunjack', michiko: 'demonio', star: 'xiaoyu',
  torch: 'demonio', bruno: 'bryan', negativo: 'bryan', thor: 'bryan',
  yukihyo: 'king', slice: 'bryan', docfrank: 'gunjack',
  // Reskin wave (2026-10-19): first custom attires as selectable fighters.
  'demonio-bloodline-ember': 'demonio', 'doc-frank-machine-shop': 'gunjack',
  'baek-master-white': 'bryan', 'mariposa-monarch': 'xiaoyu',
  'dxmmii-patchwork': 'demonio',
  // Sketchfab intake (owner 2026-10-19): working names.
  zangief: 'king', blanka: 'bryan', vega: 'xiaoyu', iori: 'heihachi',
  'armor-king': 'king',
  // Teardown-integration (owner 2026-10-19): aggregate-bank fallback for the
  // roster ids whose per-fighter files landed with the full-moveset wiring.
  kronos: 'king', 'kronos-attire2': 'king',
  'demonio-human': 'demonio', 'doc-frank-wowomomo': 'gunjack',
  'doc-frank-hood': 'gunjack',
  // Late additions (anim audit 2026-10-19): were missing from the map.
  'demonio-winged': 'demonio', deathfang: 'heihachi', 'ryuji-rock': 'king',
  koreshi: 'heihachi',
};

/* Animation bank for a fighter (GYRO-ARMS FIX 2026-10-19).
   A fighter plays the REAL T3 motion bank of the moveset SOURCE their
   frame data was built from (per-fighter moveset JSON t3_source first,
   MOVESET_MAP as fallback) — mapped through the SOURCE_TO_BANK fixups
   in t3anims.js (demonio -> jin bank, bosconovitch -> gunjack,
   deviljin -> jin). Returns the bank id, or null when no decoded bank
   exists for the source (heihachi): those fighters get NO T3 actions —
   embedded locomotion + procedural combat — never another
   character's clips. */
export function bankIdFor(charId, movesetId) {
  let src = null;
  try { src = getFighterMoveset(movesetId || charId)?.t3_source || null; } catch (e) { /* per-fighter movesets not loaded yet */ }
  if (!src) src = MOVESET_MAP[movesetId || charId] || MOVESET_MAP[charId] || null;
  if (!src) return null;
  return Object.prototype.hasOwnProperty.call(SOURCE_TO_BANK, src) ? SOURCE_TO_BANK[src] : null;
}

export async function loadRealMovesets() {
  try {
    const names = ['king', 'demonio', 'bryan', 'heihachi', 'xiaoyu', 'yoshimitsu', 'gunjack'];
    // FIX (anim audit 2026-10-19): there is no assets/demonio_moves.json —
    // the file on disk is jin_moves.json (demonio is the game's rename of
    // Jin). The old fetch 404'd, Promise.all rejected, and the whole
    // aggregate moveset map silently never built.
    const FILE_FOR = { demonio: 'jin' };
    const data = await Promise.all(
      names.map(n => fetch(`assets/${FILE_FOR[n] || n}_moves.json`).then(r => r.json()))
    );
    const byName = {};
    names.forEach((n, i) => byName[n] = data[i]);
    // Map every fighter ID to its T3 moveset
    window.WH_MOVESETS = {};
    for (const [fid, msName] of Object.entries(MOVESET_MAP)) {
      window.WH_MOVESETS[fid] = byName[msName];
    }
    console.log('[WH] Real T3 movesets loaded for 36 fighters (7 T3 sources)');
  } catch (e) {
    console.warn('[WH] Could not load real movesets, using fallback:', e);
  }
}

// Legacy action names -> Tekken notation (AI + old UI keep working)
const LEGACY_TO_TEKKEN = { punch: '1', kick: '4', grab: '1+3' };

export function getRealMove(charId, moveType) {
  const tekken = LEGACY_TO_TEKKEN[moveType] || moveType;
  const ms = window.WH_MOVESETS?.[charId];
  if (ms) {
    // New shape: per-fighter moveset { moves: { '1': {...}, '1+3': {...}, ... } }
    if (ms.moves) {
      const mv = ms.moves[tekken];
      if (mv) {
        return {
          startup: mv.startup, active: mv.active, recovery: mv.recovery,
          damage: mv.damage, knock: mv.knock ?? 2.2,
          soulGain: mv.soulGain ?? 8, cost: 0,
          limb: mv.limb || 'armR', heavy: !!mv.heavy,
          unblockable: !!mv.unblockable, isGrab: !!mv.isGrab,
          tekkenInput: mv.input, t3row: mv.t3_row, moveName: mv.name,
        };
      }
    } else {
      // Old shape: aggregate T3 { light, medium, grab } (pre-lane-3)
      const key = moveType === 'punch' ? 'light' : moveType === 'kick' ? 'medium' : moveType === 'grab' ? 'grab' : null;
      const data = key && ms[key];
      if (data) {
        return {
          startup: data.startup, active: data.active, recovery: data.recovery,
          damage: data.dmg, knock: moveType === 'punch' ? 2.2 : moveType === 'kick' ? 4.2 : 6.5,
          soulGain: moveType === 'punch' ? 8 : 11, cost: 0,
          limb: moveType === 'punch' ? 'armR' : 'legR',
          heavy: moveType !== 'punch',
        };
      }
    }
  }
  return null;
}

const GROUND_Y = 0;
let ARENA_LIMIT = 8.4; // default: shrine.json arena 16.8 wide; set per-stage via setArenaLimit()
/* Lane 4: collision bounds come from the stage def (stages.js dims.wallDistance). */
export function setArenaLimit(v) { ARENA_LIMIT = v; }

let _glowTex = null;
function _glowTexture() {
  if (_glowTex) return _glowTex;
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.5)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 64, 64);
  _glowTex = new THREE.CanvasTexture(c);
  return _glowTex;
}

// scratch objects (avoid per-frame allocations)
const _v1 = new THREE.Vector3(), _v2 = new THREE.Vector3(), _v3 = new THREE.Vector3();
const _q1 = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _q3 = new THREE.Quaternion();
// PRIVATE scratch for Fighter._ik ONLY (gyro-arms fix 2026-10-19): callers
// pass _v2 as the IK target, so _ik must never touch _v1/_v2/_v3/_q*.
const _ikT = new THREE.Vector3();
const _ikV1 = new THREE.Vector3(), _ikV2 = new THREE.Vector3(), _ikV3 = new THREE.Vector3();
const _ikQ1 = new THREE.Quaternion(), _ikQ2 = new THREE.Quaternion(), _ikQ3 = new THREE.Quaternion();

export class Fighter {
  constructor(charData, startX, facing, isPlayer) {
    this.char = charData;
    this.isPlayer = isPlayer;
    this.facing = facing;
    // Default stats for fighters without explicit stats (from ROSTER.md archetypes)
    // Tekken-style walk speed: deliberate, not twitchy. (Was 4.4 — felt like teleporting.)
    this.stats = charData.stats || { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 };
    // Clamp explicit stats too — no fighter should move at teleport speed
    if (this.stats.speed > 3.5) this.stats.speed = 3.5;
    this.aiProfile = charData.ai || { aggression: 0.6, grabBias: 0.15, reaction: 0.55 };

    // vitals
    this.maxHp = 100; this.hp = 100;
    this.meter = 0; this.maxMeter = 100; // NINE-SOUL METER

    // physics
    this.vx = 0; this.vy = 0; this.onGround = true;

    // state machine
    this.state = 'idle'; this.stateT = 0;
    this.attack = null; this.attackName = null; this._attackPhase = 'startup';
    this.hasHit = false; this.stun = 0; this.invuln = 0; this.dodgeDir = 0;
    this.dead = false; this.combo = 0; this._comboTimer = 0;
    this.tekken = new TekkenBuffer(charData.id); // strings / motion specials / directionals

    // smoothed lean (body english)
    this._lean = { x: 0, z: 0 };
    this._leanT = { x: 0, z: 0 };
    this._locoIdle = 1; this._locoWalk = 0; this._locoRun = 0;
    this._auraFlash = 0;

    // MID-MATCH TRANSFORMATION (Roshi-style, owner 2026-10-19).
    // Fighters with charData.transform (single) or charData.forms (multi-form
    // map keyed by current model key) swap models mid-fight.
    // Single: { targetModel, powerMult, speedMult, defenseMult, bodyScale }.
    // Multi: { 'model-key': { target, label, powerMult, speedMult, defenseMult,
    //   bodyScale, moveset }, 'model-key': { up: {...}, down: {...} } }.
    this._forms = null;
    this.formKey = charData.model;
    if (charData.forms) {
      this._forms = charData.forms;
    } else if (charData.transform) {
      const t0 = charData.transform;
      this._forms = { [charData.model]: {
        target: t0.targetModel, label: 'TRANSFORM',
        powerMult: t0.powerMult, speedMult: t0.speedMult,
        defenseMult: t0.defenseMult, bodyScale: t0.bodyScale } };
    }
    this.transformed = false;
    this._movesetId = charData.id; // may be overridden by transform
    // Transformation cinematic (v1, owner 2026-10-19): timeline-based,
    // personalized per fighter. Replaces the instant model swap.
    this._cinematic = null;
    this._sceneRef = null; // set by game.js — arena scene for shake()

    this._build(startX);
  }

  _build(startX) {
    const inst = assets.createInstance(
      this.char.model || 'pantera',
      this.char.colors.suit, this.char.colors.trim,
      this.char.tintStrength ?? 0.45
    );
    this.bones = inst.bones;
    this.mixer = inst.mixer;
    this.actions = inst.actions;

    // REAL T3 animation clips — this fighter's OWN moveset-source bank
    // (see bankIdFor). The clips carry absolute bone quaternions keyed
    // to the canonical 22-bone Mixamo-name skeleton; if this model
    // lacks those bones the actions can't bind, so skip them and stay
    // on embedded locomotion + procedural combat.
    this.t3actions = {};
    this._t3current = null;
    this._t3stateKey = null;
    const bank = bankIdFor(this.char.id, this._movesetId);
    const t3clips = bank ? getT3Clips(bank) : null;
    if (t3clips && Object.keys(t3clips).length > 0 && this.bones.Hips && this.bones.RightArm) {
      this.t3actions = createT3Actions(this.mixer, t3clips, THREE);
      console.log(`[WH] Fighter ${this.char.id}: ${Object.keys(this.t3actions).length} real T3 actions from bank '${bank}'`);
    } else if (!bank) {
      console.log(`[WH-T3] no decoded anim bank for ${this.char.id} (source has none yet) — embedded/procedural fallback`);
    }

    // root (world position) -> lean (facing + body english) -> model
    this.root = new THREE.Group();
    this.root.position.set(startX, GROUND_Y, 0);
    // Custom fighters: apply body type proportions (height + width)
    // from the CAW suite. Standard fighters use uniform bodyScale.
    if (this.char.bodyWidth && this.char.bodyWidth !== 1) {
      const h = this.char.bodyScale || 1;
      const w = this.char.bodyWidth;
      this.root.scale.set(w, h, w);
    } else {
      this.root.scale.setScalar(this.char.bodyScale || 1);
    }

    this.lean = new THREE.Group();
    this.lean.rotation.y = this.facing * Math.PI / 2;
    this.lean.add(inst.model);
    this.root.add(this.lean);
    this.model = inst.model;
    // ?debug=1 → on-page fighter diagnostics (no devtools needed)
    if (new URLSearchParams(location.search).has('debug')) {
      let sm = 0, bones = 0, vis = true;
      inst.model.traverse(o => {
        if (o.isSkinnedMesh) { sm++; bones = Math.max(bones, o.skeleton ? o.skeleton.bones.length : -1); }
        if (o.visible === false) vis = false;
      });
      const d = document.createElement('div');
      d.id = 'wh-debug';
      d.style.cssText = 'position:fixed;top:0;left:0;z-index:9999;background:rgba(0,0,0,0.85);color:#0f0;font:12px monospace;padding:10px;white-space:pre;pointer-events:none';
      const wp = new THREE.Vector3();
      this.root.updateMatrixWorld(true);
      this.root.getWorldPosition(wp);
      d.textContent = `fighter=${this.char.id} model=${this.char.model}\nskinnedMeshes=${sm} maxBones=${bones} allVisible=${vis}\nrootPos=(${wp.x.toFixed(1)},${wp.y.toFixed(1)},${wp.z.toFixed(1)}) rootVisible=${this.root.visible}\nmodelType=${inst.model.type} children=${inst.model.children.length}`;
      document.body.appendChild(d);
    }

    // Soul aura for Soul Surge — PARTICLE aura clinging to the body
    // (Pantera: purple/red panther flame; Demonio: cold blue-white).
    // No white sphere; the particles sample a body-hugging capsule.
    const surgeColor = this.char.surge ? this.char.surge.color : this.char.colors.trim;
    const surgeAccent = this.char.surge ? (this.char.surge.accent ?? 0xffffff) : 0xffffff;
    const AURA_N = 140;
    const pos = new Float32Array(AURA_N * 3);
    const seed = new Float32Array(AURA_N * 2);
    for (let i = 0; i < AURA_N; i++) {
      // capsule: y in [0.1, 1.9], radius shrinks toward head/feet
      const y = 0.1 + Math.random() * 1.8;
      const rr = 0.42 * Math.sin(Math.PI * Math.min(1, Math.max(0.05, y / 2.0)));
      const a = Math.random() * Math.PI * 2;
      pos[i * 3] = Math.cos(a) * rr;
      pos[i * 3 + 1] = y;
      pos[i * 3 + 2] = Math.sin(a) * rr;
      seed[i * 2] = Math.random() * 100;      // phase
      seed[i * 2 + 1] = 0.5 + Math.random();  // speed
    }
    const auraGeo = new THREE.BufferGeometry();
    auraGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const c1 = new THREE.Color(surgeColor), c2 = new THREE.Color(surgeAccent);
    const cols = new Float32Array(AURA_N * 3);
    for (let i = 0; i < AURA_N; i++) {
      const c = c1.clone().lerp(c2, Math.random() * 0.45);
      cols[i * 3] = c.r; cols[i * 3 + 1] = c.g; cols[i * 3 + 2] = c.b;
    }
    auraGeo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
    this.aura = new THREE.Points(auraGeo, new THREE.PointsMaterial({
      size: 0.09, vertexColors: true, transparent: true, opacity: 0,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
    }));
    this.aura.userData.seed = seed;
    this.aura.frustumCulled = false;
    this.root.add(this.aura);
    // rim light that flares with the surge
    this.auraLight = new THREE.PointLight(surgeColor, 0, 4.5, 1.8);
    this.auraLight.position.y = 1.2; this.root.add(this.auraLight);

    // Contact shadow blob
    this.blob = new THREE.Mesh(
      new THREE.CircleGeometry(0.6, 24),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.34, depthWrite: false })
    );
    this.blob.rotation.x = -Math.PI / 2; this.blob.position.y = 0.02; this.root.add(this.blob);

    // Attack glow sprite that follows the active weapon
    this.trail = new THREE.Sprite(new THREE.SpriteMaterial({
      map: _glowTexture(), color: this.char.colors.trim,
      transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false
    }));
    this.trail.visible = false; this.root.add(this.trail);
  }

  /* ---------------- combat intents ---------------- */
  canAct() {
    // Mid-cinematic: rooted, cannot act (but still vulnerable — damage
    // applies separately). Owner spec: vulnerable during transform.
    if (this._cinematic && !this._cinematic.done) return false;
    return !this.dead && this.stun <= 0 &&
      (this.state === 'idle' || this.state === 'walk' || this.state === 'jump');
  }
  _resolveTransform(direction) {
    const f = this._forms && this._forms[this.formKey];
    if (!f) return null;
    return f.target ? f : (f[direction] || null);
  }
  canTransform(direction='up') {
    return !!(this._resolveTransform(direction) && this.canAct());
  }

  /* Mid-match transformation (Roshi-style power-up, owner 2026-10-19).
     v1 cinematic: validates, spends the gauge, then runs a personalized
     timeline (phases) instead of an instant swap. The model swap fires at
     the cinematic's climax via _doModelSwap().
     Tekken mirror: Devil Jin needs a FULL Devil Gauge — here the transform
     needs a FULL nine-soul meter, which is spent on the transform.
     Touch button only, no keyboard.
     Returns true if the transform fired. */
  tryTransform(direction='up') {
    const t = this._resolveTransform(direction);
    if (!t || !this.canAct()) return false;
    if (this.meter < this.maxMeter) return false; // gauge must be full
    if (this._cinematic && !this._cinematic.done) return false; // already transforming
    this.meter = 0; // spend the gauge
    // Start the personalized cinematic timeline. The model swap happens
    // at the climax (see TransformCinematic).
    const phases = TransformCinematic.phasesFor(this.char.id);
    this._cinematic = new TransformCinematic(this, this._sceneRef, {
      phases,
      swapAt: phases.reduce((m, p) => Math.max(m, p.t + p.dur), 0) * 0.75,
      onSwap: (f) => f._doModelSwap(t, direction),
    });
    // Fighter is vulnerable but rooted during the cinematic.
    this._enter('idle');
    this.vx = 0; this.vy = 0;
    console.log(`[WH] ${this.char.id} TRANSFORM CINEMATIC start (${direction}) -> ${t.target}`);
    return true;
  }

  /* The actual model swap — called by the cinematic at the climax.
     (Was inline in tryTransform; extracted so the cinematic owns timing.) */
  _doModelSwap(t, direction='up') {
    let inst;
    try {
      inst = assets.createInstance(
        t.target,
        this.char.colors.suit, this.char.colors.trim,
        this.char.tintStrength ?? 0.45
      );
    } catch (e) {
      console.error(`[WH] transform failed — unknown model ${t.target}:`, e.message || e);
      return false;
    }
    // Swap under the same lean group: facing + body english preserved.
    this.lean.remove(this.model);
    this.lean.add(inst.model);
    this.model = inst.model;
    this.bones = inst.bones;
    this.mixer = inst.mixer;
    this.actions = inst.actions;
    // Rebuild the T3 action set on the new mixer — bank recomputed from
    // the (possibly new) moveset source after the form change.
    this.t3actions = {};
    this._t3current = null;
    this._t3stateKey = null;
    const tbank = bankIdFor(this.char.id, t.moveset || this._movesetId);
    const tt3clips = tbank ? getT3Clips(tbank) : null;
    if (tt3clips && Object.keys(tt3clips).length > 0 && this.bones.Hips && this.bones.RightArm) {
      this.t3actions = createT3Actions(this.mixer, tt3clips, THREE);
    }
    // Bigger = more damage, slower (owner spec).
    this.stats = {
      ...this.stats,
      power: this.stats.power * (t.powerMult ?? 1.35),
      speed: Math.min(3.5, this.stats.speed * (t.speedMult ?? 0.9)),
      defense: this.stats.defense * (t.defenseMult ?? 1.1),
    };
    if (t.bodyScale) this.root.scale.setScalar(t.bodyScale);
    this.formKey = t.target;
    if (t.moveset) {
      this._movesetId = t.moveset;
      if (this.tekken) this.tekken.fighterId = t.moveset;
    }
    this.transformed = true;
    this._auraFlash = 1.0; // full-body flash on transform
    this._enter('idle');
    console.log(`[WH] ${this.char.id} TRANSFORMED (${direction}) -> ${t.target}${t.label ? ' ['+t.label+']' : ''}`);
    return true;
  }

  tryMove(dir) { if (this.canAct()) this.vx = dir * this.stats.speed; }
  tryJump() { if (this.canAct() && this.onGround) { this.vy = this.stats.jump; this.onGround = false; this._enter('jump'); } }
  tryBlock(on) {
    if (this.dead) return;
    if (on && this.canAct() && this.onGround) { this._enter('block'); this._blendW = 0; }
    else if (!on && this.state === 'block') this._enter('idle');
  }
  tryDodge() {
    if (!this.canAct() || !this.onGround) return;
    this._enter('dodge'); this.invuln = 0.34; this.dodgeDir = -this.facing;
    this.vx = this.dodgeDir * this.stats.speed * 1.7;
  }
  tryAttack(name) {
    if (!this.canAct()) return false;
    // Tekken notation resolution: strings (1,2), motion specials (qcf+2),
    // directionals (f+1) via the fighter's TekkenBuffer. Legacy names map.
    let notation = LEGACY_TO_TEKKEN[name] || name;
    if (/^[1234]$/.test(notation)) {
      const resolved = this.tekken.pressButton(notation);
      if (resolved) notation = resolved;
      else return false;
    } else if (/^[1234]\+[1234]$/.test(notation)) {
      const resolved = this.tekken.pressChord(notation);
      if (!resolved) return false; // chord with no matching move: whiff, no action
      notation = resolved;
    }
    // Use REAL per-fighter T3 moveset data when available, fallback to base MOVES
    let move = getRealMove(this._movesetId, notation) || MOVES[name] || MOVES[notation];
    if (!move) {
      // Last resort: moveset JSONs failed to load - map Tekken buttons to base moves
      const fb = { '1': 'punch', '2': 'punch', '3': 'kick', '4': 'kick',
                   '1+3': 'grab', '2+4': 'grab', '1+2': 'grab', '3+4': 'grab' }[notation];
      if (fb) move = MOVES[fb];
    }
    if (!move) return false;
    // Preserve WH-specific properties (grab unblockable, surge cost)
    if (MOVES[name]) {
      move = { ...move, ...Object.fromEntries(
        Object.entries(MOVES[name]).filter(([k]) => ['unblockable','isGrab','cost','soulGain'].includes(k))
      )};
    }
    if (move.cost > 0 && this.meter < move.cost) return false;
    if (move.cost > 0) this.meter = Math.max(0, this.meter - move.cost);
    this.attack = move; this.attackName = notation; this.hasHit = false;
    this._attackId = (this._attackId || 0) + 1;
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup';
    if (name === 'surge') this._auraFlash = 0.7;
    if (move.isGrab || notation === '1+3' || notation === '2+4') this.vx = this.facing * 2.5; // lunge into the grab
    return true;
  }
  _enter(state) { this.state = state; this.stateT = 0; }

  /* ---------------- defense / damage ---------------- */
  isBlocking() { return this.state === 'block'; }

  receiveHit(move, attacker) {
    if (this.dead || this.invuln > 0) return 'dodge';
    const facingAttacker = Math.sign(attacker.root.position.x - this.root.position.x) === this.facing;
    // Throws are unblockable — blocking does nothing against a grab.
    if (this.isBlocking() && facingAttacker && !move.unblockable) {
      // FIRE force (modes lane): strikes chip through guard — chipMult on attacker stats.
      const chip = move.damage * attacker.stats.power * 0.12 * (attacker.stats.chipMult || 1) / this.stats.defense;
      this.hp = Math.max(0, this.hp - chip);
      this.stun = 0.18 + move.damage * 0.01;
      this.vx = Math.sign(this.root.position.x - attacker.root.position.x) * move.knock * 0.5;
      this.meter = Math.min(this.maxMeter, this.meter + 4); // +4 soul on block
      if (this.hp <= 0) { this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || 1); return 'ko'; }
      return 'block';
    }
    const dmg = move.damage * attacker.stats.power / this.stats.defense;
    this.hp = Math.max(0, this.hp - dmg);
    this.meter = Math.min(this.maxMeter, this.meter + 6); // +6 soul on taking damage
    const dir = Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing;
    this.vx = dir * move.knock;
    if (this.hp <= 0) { this._knockout(dir); return 'ko'; }
    if (move.isGrab || move.knock >= 6) {
      this.vy = move.isGrab ? 5.2 : 4.6; this.onGround = false; this.stun = 0.55; this._enter('knockdown');
    } else { this.stun = 0.2 + move.damage * 0.012; this._enter('hitstun'); }
    return 'hit';
  }
  _knockout(dir) {
    this.dead = true; this.vx = dir * 5.5; this.vy = 6; this.onGround = false;
    this._enter('ko'); this.stun = 999;
  }
  victory() { if (!this.dead) this._enter('victory'); }
  addMeter(v) { this.meter = Math.min(this.maxMeter, this.meter + v); }

  /* ---------------- hit / hurt queries (world-space spheres) ---------------- */
  _weaponBone() {
    // Tekken notation: 3/4 are kicks -> foot; throws/specials use the move's limb
    const limb = this.attack?.limb || '';
    if (limb.startsWith('leg') || this.attackName === 'kick' || this.attackName === '3' || this.attackName === '4') {
      return limb === 'legL' ? this.bones.LeftFoot : this.bones.RightFoot;
    }
    if (limb === 'armL') return this.bones.LeftHand;
    return this.bones.RightHand;
  }
  getHitbox() {
    if (this.state !== 'attack' || this._attackPhase !== 'active' || this.hasHit) return null;
    const node = this._weaponBone(); if (!node) return null;
    node.getWorldPosition(_v1);
    let r = this.attackName === 'surge' ? 1.0 : 0.5;
    if (this.attack?.isGrab || this.attackName === 'grab' || this.attackName === '1+3' || this.attackName === '2+4') r = 0.95; // generous grab sphere
    r *= (this.stats.reachMult || 1); // WOOD force (modes lane): reach extends
    return { x: _v1.x, y: _v1.y, z: _v1.z, r, move: this.attack };
  }
  getHurtboxes() {
    if (this.invuln > 0 || this.dead) return [];
    const out = [];
    if (this.bones.Spine1) { this.bones.Spine1.getWorldPosition(_v1); out.push({ x: _v1.x, y: _v1.y, z: _v1.z, r: 0.58 }); }
    if (this.bones.Head) { this.bones.Head.getWorldPosition(_v1); out.push({ x: _v1.x, y: _v1.y, z: _v1.z, r: 0.34 }); }
    return out;
  }
  registerHit() { this.hasHit = true; this.addMeter(this.attack.soulGain); }
  registerCombo() { this.combo++; this._comboTimer = 1.2; return this.combo; }

  /* ---------------- per-frame update ---------------- */
  update(dt, opponent) {
    this.stateT += dt;
    // Drive the transformation cinematic timeline.
    if (this._cinematic && !this._cinematic.done) {
      this._cinematic.update(dt);
      if (this._cinematic.done) this._cinematic = null;
    }
    // METAL force (modes lane): wounds close as you fight.
    if (this.stats.regenPerSec && this.hp > 0 && this.hp < this.maxHp) {
      this.hp = Math.min(this.maxHp, this.hp + this.stats.regenPerSec * dt);
    }
    if (this.stun > 0 && this.state !== 'ko') this.stun -= dt;
    if (this.invuln > 0) this.invuln -= dt;
    if (this._comboTimer > 0) { this._comboTimer -= dt; if (this._comboTimer <= 0) this.combo = 0; }
    if (this._auraFlash > 0) this._auraFlash -= dt;

    if (opponent && this.canAct()) {
      const want = opponent.root.position.x >= this.root.position.x ? 1 : -1;
      if (want !== this.facing) this.facing = want;
    }

    this._tickState();
    this._physics(dt, opponent);
    this._animate(dt);
  }

  _tickState() {
    switch (this.state) {
      case 'attack': {
        const m = this.attack, t = this.stateT;
        if (t < m.startup) this._attackPhase = 'startup';
        else if (t < m.startup + m.active) this._attackPhase = 'active';
        else if (t < m.startup + m.active + m.recovery) this._attackPhase = 'recovery';
        else { this.attack = null; this.attackName = null; this._enter('idle'); }
        break;
      }
      case 'jump': if (this.onGround) this._enter('idle'); break;
      case 'hitstun': if (this.stun <= 0) this._enter('idle'); break;
      case 'knockdown': if (this.onGround && this.stun <= 0) this._enter('idle'); break;
      case 'dodge': if (this.stateT > 0.34) { this.vx = 0; this._enter('idle'); } break;
      case 'idle': case 'walk':
        this.state = (Math.abs(this.vx) > 0.4 && this.onGround) ? 'walk' : 'idle';
        break;
    }
  }

  _physics(dt, opponent) {
    if (!this.onGround) this.vy -= 22 * dt;
    if (this.onGround && this.state !== 'walk' && this.state !== 'dodge' && !(this.state === 'attack' && this.attackName === 'grab')) {
      this.vx *= Math.pow(0.0001, dt);
      if (Math.abs(this.vx) < 0.05) this.vx = 0;
    }
    this.root.position.x += this.vx * dt;
    this.root.position.y += this.vy * dt;

    if (this.root.position.y <= GROUND_Y) {
      this.root.position.y = GROUND_Y; this.vy = 0;
      if (!this.onGround) { this.onGround = true; if (this.state === 'knockdown') this.stun = Math.max(this.stun, 0.4); }
    }
    this.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, this.root.position.x));

    // Body-vs-body pushout — fighters NEVER interpenetrate.
    if (opponent) {
      const dx = this.root.position.x - opponent.root.position.x;
      const minDist = 1.45;
      if (Math.abs(dx) < minDist && Math.abs(this.root.position.y - opponent.root.position.y) < 1.8) {
        const push = (minDist - Math.abs(dx)) / 2 * (dx >= 0 ? 1 : -1);
        this.root.position.x += push; opponent.root.position.x -= push;
      }
    }

    const h = this.root.position.y;
    this.blob.position.y = 0.02 - h;
    const s = Math.max(0.4, 1 - h * 0.12);
    this.blob.scale.set(s, s, s); this.blob.material.opacity = 0.34 * s;
  }

  /* ---------------- REAL T3 animation clips ---------------- */
  // Plays a real decoded T3 clip, fading out the Mixamo base layer.
  // Returns true if the clip played, false if not available (use procedural fallback).
  _playT3(name, { loop = false, fade = 0.08 } = {}) {
    const action = this.t3actions[name];
    if (!action) return false;
    // Don't restart if already playing this clip
    if (this._t3current === action && action.isRunning()) return true;
    // Fade out current T3 clip
    if (this._t3current && this._t3current !== action) {
      this._t3current.fadeOut(0.1);
    }
    // Fade out Mixamo locomotion base
    for (const n of ['Idle', 'Walk', 'Run']) {
      if (this.actions[n]) this.actions[n].fadeOut(0.1);
    }
    action.reset();
    action.setEffectiveWeight(1);
    action.fadeIn(fade);
    action.play();
    this._t3current = action;
    return true;
  }

  _stopT3(fade = 0.15) {
    if (this._t3current) {
      this._t3current.fadeOut(fade);
      this._t3current = null;
    }
    this._t3stateKey = null;
  }

  // Play a T3 one-shot once per state entry (not every frame)
  _playT3Once(name, stateKey) {
    if (this._t3stateKey === stateKey) {
      // Already triggered for this state entry; check if still playing
      const action = this.t3actions[name];
      return action && this._t3current === action;
    }
    this._t3stateKey = stateKey;
    return this._playT3(name, { loop: false });
  }

  /* ---------------- animation ---------------- */
  _animate(dt) {
    // 1) Facing
    this.lean.rotation.y = this.facing * Math.PI / 2;

    // 2) Locomotion crossfade (real mocap base layer)
    let tIdle = 1, tWalk = 0, tRun = 0;
    if (this.state === 'walk') {
      const fast = Math.abs(this.vx) > this.stats.speed * 0.9;
      tIdle = 0; tWalk = fast ? 0 : 1; tRun = fast ? 1 : 0;
    } else if (this.state === 'dodge') { tIdle = 0; tRun = 1; }
    const rate = 1 - Math.exp(-dt / 0.12);
    this._locoIdle += (tIdle - this._locoIdle) * rate;
    this._locoWalk += (tWalk - this._locoWalk) * rate;
    this._locoRun += (tRun - this._locoRun) * rate;
    if (this.actions.Idle) this.actions.Idle.setEffectiveWeight(this._locoIdle);
    if (this.actions.Walk) this.actions.Walk.setEffectiveWeight(this._locoWalk);
    if (this.actions.Run) this.actions.Run.setEffectiveWeight(this._locoRun);
    // Reverse the walk cycle when backing away so retreating reads
    // as a back-step instead of a moonwalk.
    const dirSign = Math.abs(this.vx) > 0.05 ? (Math.sign(this.vx) === this.facing ? 1 : -1) : 1;
    if (this.actions.Walk) this.actions.Walk.timeScale = dirSign;
    if (this.actions.Run) this.actions.Run.timeScale = dirSign;

    // 3) Advance mocap clips (writes base pose into bones)
    this.mixer.update(dt);

    // 4) Refresh world matrices so IK reads the posed skeleton
    this.root.updateWorldMatrix(true, true);

    // 5) Combat override layer (IK) + lean targets
    this._leanT.x = 0; this._leanT.z = 0;
    this.trail.visible = false;
    // REAL T3 clips for combat states (falls back to procedural if unavailable)
    const T3_ATTACK_MAP = { punch: 'light', kick: 'medium', grab: 'grab', surge: 'heavy', heavy: 'heavy',
      '1': 'light', '2': 'light', '3': 'medium', '4': 'medium', '1+3': 'grab', '2+4': 'grab' };
    switch (this.state) {
      case 'attack': {
        let t3name = T3_ATTACK_MAP[this.attackName];
        if (!t3name && typeof this.attackName === 'string') {
          const lastBtn = this.attackName.split(',').pop().split('+').pop();
          t3name = T3_ATTACK_MAP[lastBtn] || 'heavy'; // strings -> last hit's clip; specials -> heavy
        }
        if (t3name && this._playT3Once(t3name, 'atk:' + this.attackName + ':' + this._attackId)) {
          // Real T3 clip playing; add slight lean for body english
          this._leanT.x = -0.1;
        } else {
          this._animAttack(); // procedural fallback
        }
        break;
      }
      case 'block':
        if (!this._playT3('block', { loop: true })) this._animBlock();
        break;
      case 'hitstun':
        this._leanT.x = 0.28;
        this._playT3Once('hit', 'hit:' + Math.floor(this.stateT * 10));
        break;
      case 'knockdown':
        this._leanT.x = Math.min(0.9, this.stateT * 3.0);
        this._playT3Once('launch', 'kd:' + Math.floor(this.stateT * 10));
        break;
      case 'ko':
        this._leanT.x = Math.min(0.9, this.stateT * 3.0);
        this._playT3Once('ko', 'ko:' + Math.floor(this.stateT * 10));
        break;
      case 'victory':
        this._playT3('win', { loop: true });
        break;
      case 'dodge': this._leanT.z = this.dodgeDir * this.facing * 0.32; this._stopT3(); break;
      case 'jump': this._animJump(); this._stopT3(); break;
      default: this._stopT3(); break;
    }

    // 6) Smooth & apply lean (body english) — composed with facing
    const lr = 1 - Math.exp(-dt / 0.05);
    this._lean.x += (this._leanT.x - this._lean.x) * lr;
    this._lean.z += (this._leanT.z - this._lean.z) * lr;
    this.lean.rotation.x = this._lean.x;
    this.lean.rotation.z = this._lean.z;

    // 7) Aura + trail visuals — particles rise and flicker around the body
    const auraOn = (this.attackName === 'surge') || this._auraFlash > 0;
    const am = this.aura.material;
    am.opacity += ((auraOn ? 0.95 : 0) - am.opacity) * Math.min(1, dt * 10);
    this.auraLight.intensity += ((auraOn ? 14 : 0) - this.auraLight.intensity) * Math.min(1, dt * 10);
    if (am.opacity > 0.01) {
      const p = this.aura.geometry.attributes.position;
      const seed = this.aura.userData.seed;
      const k = performance.now() * 0.001;
      for (let i = 0; i < p.count; i++) {
        const s0 = seed[i * 2], s1 = seed[i * 2 + 1];
        // rise, wrap around the capsule
        let y = p.getY(i) + dt * 1.6 * s1;
        if (y > 2.0) y = 0.1;
        const wob = Math.sin(k * 9 * s1 + s0) * 0.07;
        p.setY(i, y);
        p.setX(i, p.getX(i) + wob * dt * 8);
      }
      p.needsUpdate = true;
      const as = 1 + Math.sin(k * 12) * 0.08; this.aura.scale.set(as, 1, as);
    }
  }

  _attackProgress() {
    const m = this.attack, t = this.stateT;
    const extendEnd = m.startup + m.active;
    let ext = t < extendEnd ? t / extendEnd : 1 - (t - extendEnd) / m.recovery;
    ext = Math.max(0, Math.min(1, ext));
    return ext * ext * (3 - 2 * ext); // smoothstep
  }

  _animAttack() {
    const e = this._attackProgress();
    const fwd = _v3.set(this.facing, 0, 0); // world forward
    const name = this.attackName;

    const isKick = name === 'kick' || name === '3' || name === '4' || this.attack?.limb?.startsWith('leg');
    const isThrow = name === 'grab' || name === '1+3' || name === '2+4' || this.attack?.isGrab;
    if (isKick) {
      this._leanT.x = -0.18 * e; this._leanT.z = this.facing * 0.12 * e;
      this.bones.Hips.getWorldPosition(_v1);
      const reach = 0.5 + e * 1.5;
      _v2.copy(_v1).addScaledVector(fwd, reach); _v2.y = _v1.y - 0.1 + e * 0.6;
      this._ik(['RightUpLeg', 'RightLeg'], 'RightFoot', _v2, e * 0.95);
      this._showTrail(this.bones.RightFoot, e);
    } else if (isThrow) {
      // Double-arm snatch: both hands drive forward at chest height.
      this._leanT.x = -0.22 * e;
      this.bones.Spine2.getWorldPosition(_v1);
      const reach = 0.35 + e * 1.1;
      _v2.copy(_v1).addScaledVector(fwd, reach); _v2.y = _v1.y + 0.1;
      this._ik(['RightArm', 'RightForeArm'], 'RightHand', _v2, e * 0.95);
      _v2.copy(_v1).addScaledVector(fwd, reach * 0.92); _v2.y = _v1.y - 0.05;
      this._ik(['LeftArm', 'LeftForeArm'], 'LeftHand', _v2, e * 0.95);
      this._showTrail(this.bones.RightHand, e);
    } else {
      // punch / surge: straight arm strike(s)
      this._leanT.x = -0.12 * e;
      this.bones.Spine2.getWorldPosition(_v1);
      const reach = 0.4 + e * 1.35;
      _v2.copy(_v1).addScaledVector(fwd, reach); _v2.y = _v1.y + 0.05;
      this._ik(['RightArm', 'RightForeArm'], 'RightHand', _v2, e * 0.96);
      if (name === 'surge') {
        _v2.copy(_v1).addScaledVector(fwd, reach); _v2.y = _v1.y - 0.05;
        this._ik(['LeftArm', 'LeftForeArm'], 'LeftHand', _v2, e * 0.96);
      }
      this._showTrail(this.bones.RightHand, e);
    }
  }

  _animBlock() {
    this._blendW = Math.min(0.9, (this._blendW || 0) + 0.18);
    this._leanT.x = 0.06;
    this.bones.Spine2.getWorldPosition(_v1);
    const fwd = _v3.set(this.facing, 0, 0);
    _v2.copy(_v1).addScaledVector(fwd, 0.42); _v2.y = _v1.y + 0.35;
    this._ik(['RightArm', 'RightForeArm'], 'RightHand', _v2, this._blendW);
    _v2.copy(_v1).addScaledVector(fwd, 0.42); _v2.y = _v1.y + 0.2;
    this._ik(['LeftArm', 'LeftForeArm'], 'LeftHand', _v2, this._blendW);
  }
  _animJump() {
    this.bones.Hips.getWorldPosition(_v1);
    _v2.copy(_v1); _v2.y -= 0.35; _v2.addScaledVector(_v3.set(this.facing, 0, 0), 0.25);
    this._ik(['RightUpLeg', 'RightLeg'], 'RightFoot', _v2, 0.7);
    this._ik(['LeftUpLeg', 'LeftLeg'], 'LeftFoot', _v2, 0.6);
  }

  _showTrail(bone, e) {
    if (!bone || e < 0.3) { this.trail.visible = false; return; }
    bone.getWorldPosition(_v1);
    this.root.worldToLocal(_v1);
    this.trail.visible = true;
    this.trail.position.copy(_v1);
    const s = 0.9 + e * 0.7;
    this.trail.scale.set(s, s, s);
    this.trail.material.opacity = (e - 0.3) * 1.1;
  }

  /* ---------------- CCD inverse kinematics ----------------
     Bends `chain` (root→tip bones) so `endBone` reaches `target`
     (world space). Axis-agnostic: each step rotates a bone by the
     world-space delta that swings the effector toward the target.
     `weight` blends the IK result against the mocap base pose.

     GYRO-ARMS FIX (owner playtest 2026-10-19): every caller passes
     the shared scratch vector _v2 as `target`, but the old body of
     this function ALSO used _v1/_v2/_v3 internally — the first
     getWorldPosition() overwrote the target, and the solve then
     aimed each limb at a direction derived from its own current
     pose. Two CCD iterations per frame chasing their own tail =
     limbs spinning like gyroscopes, detaching visually from the
     body. This function now uses ONLY its own private scratch
     objects (_ikT/_ikV1/_ikV2/_ikV3/_ikQ1/_ikQ2/_ikQ3) and
     snapshots `target` before touching anything. */
  _ik(chainNames, endName, target, weight) {
    if (weight <= 0.001) return;
    const chain = chainNames.map(n => this.bones[n]);
    const endBone = this.bones[endName];
    if (!endBone || chain.some(b => !b)) return;

    _ikT.copy(target); // snapshot: callers reuse _v2 across calls
    const base = chain.map(b => b.quaternion.clone());
    const ITER = 2;
    for (let it = 0; it < ITER; it++) {
      for (let i = chain.length - 1; i >= 0; i--) {
        const bone = chain[i];
        bone.getWorldPosition(_ikV1);
        endBone.getWorldPosition(_ikV2);
        _ikV2.sub(_ikV1).normalize();
        _ikV3.copy(_ikT).sub(_ikV1).normalize();
        _ikQ1.setFromUnitVectors(_ikV2, _ikV3);
        bone.getWorldQuaternion(_ikQ2);
        _ikQ3.copy(_ikQ1).multiply(_ikQ2);
        bone.parent.getWorldQuaternion(_ikQ2);
        bone.quaternion.copy(_ikQ2.invert().multiply(_ikQ3));
        bone.updateWorldMatrix(false, true);
      }
    }
    for (let i = 0; i < chain.length; i++) {
      const solved = chain[i].quaternion.clone();
      chain[i].quaternion.copy(base[i]).slerp(solved, Math.min(1, weight));
    }
    chain[0].updateWorldMatrix(false, true);
  }
}
