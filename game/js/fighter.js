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
import { getT3Clips, createT3Actions, retargetT3Clips, SOURCE_TO_BANK } from './t3anims.js';
import { TekkenBuffer, getFighterMoveset, getMovesetInfo, resolveMove } from './movesets.js';
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
  // Stream 6 (2026-10-19): Cain Elias (Undertaker archetype -> King bank).
  'cainelias': 'king',
  // Sketchfab intake (owner 2026-10-19): working names.
  zangief: 'king', blanka: 'bryan', vega: 'xiaoyu', iori: 'heihachi',
  // CHARGER (owner 2026-10-20): Blanka replacement — plays Blanka's bryan bank.
  charger: 'bryan', 'charger-attire2': 'bryan',
  'armor-king': 'king',
  // Teardown-integration (owner 2026-10-19): aggregate-bank fallback for the
  // roster ids whose per-fighter files landed with the full-moveset wiring.
  kronos: 'king', 'kronos-attire2': 'king',
  'demonio-human': 'demonio', 'doc-frank-wowomomo': 'gunjack',
  'doc-frank-hood': 'gunjack', 'doc-frank-frankenstein': 'gunjack',
  // Late additions (anim audit 2026-10-19): were missing from the map.
  'demonio-winged': 'demonio', deathfang: 'heihachi', 'ryuji-rock': 'king',
  koreshi: 'heihachi',
};

/* Animation bank for a fighter (GYRO-ARMS FIX 2026-10-19).
   A fighter plays the REAL T3 motion bank of the moveset SOURCE their
   frame data was built from (per-fighter moveset JSON t3_source first,
   MOVESET_MAP as fallback) — mapped through SOURCE_TO_BANK in
   t3anims.js (demonio -> jin bank, deviljin -> jin; bosconovitch and
   heihachi resolve to their own real banks since 2026-10-20).
   Returns the bank id, or null when no decoded bank exists for the
   source: those fighters get NO T3 actions — embedded locomotion +
   procedural combat — never another character's clips. */
export function bankIdFor(charId, movesetId) {
  // Armor King override (2026-10-20, T3 bank remainder lane): his
  // t3_source is 'king', but the 'king' bank is King motion retargeted
  // onto the pantera_leoman rig for Pantera. The 'armorking' bank is
  // the SAME divmot03_king motion baked on King's OWN rig, matching
  // Armor King's King-proportioned model. Every other king-source
  // fighter keeps the king_on_pantera_leoman bank untouched.
  if (charId === 'armor-king') return 'armorking';
  // Per-fighter bank overrides (2026-10-20, anim-bank wiring lane; owner
  // order: every fighter animates on THEIR OWN base character's clips).
  // These fighters' moveset DATA was built on a proxy source's move table
  // (their t3_source names the data provenance), but their CANON base is a
  // different T3 character whose decoded bank now exists on main (PR #405).
  // The override binds the ACTION clips (stance/light/medium/heavy/block/
  // hit/walk/...) to the base character's own bank. Per-move row clips are
  // unaffected: _t3RowClipForMove only plays a row clip when the move's own
  // t3source maps to the bound bank, so proxy-table moves keep falling back
  // to the generic actions until the moveset lane rebuilds them on the true
  // base table — never another character's per-move clips.
  //   awapop     -> nina     (CANON: Awa Pop base = Nina Williams)
  //   torch      -> anna     (CANON: Torch base = Anna Williams)
  //   kingtyrant -> eddy     (CANON: King Tyrant base = Eddy Gordo)
  //   kai        -> eddy     (nine-souls appendix: KAI's vessel base = Eddy)
  //   tou        -> paul     (nine-souls appendix: TOU's vessel base = Paul)
  //   byou       -> lei      (nine-souls appendix: BYOU's vessel base = Lei)
  //   gyou       -> hwoarang (nine-souls appendix: GYOU's vessel base = Hwoarang)
  //   zen        -> julia    (nine-souls appendix: ZEN's vessel base = Julia)
  //   rave       -> lei      (CANON: Rave base = Lei Wulong)
  //   yukihyo    -> armorking (CANON: Yukihyo base = Armor King; same
  //                 rationale as the armor-king override above — the 'king'
  //                 bank is baked on Pantera's Leo-man rig, the 'armorking'
  //                 bank on King's own rig matching his proportions)
  //   nightwolf  -> julia    (CANON.md base = Julia Chang. Owner order
  //                 2026-10-20 names Wolf Hawkfield (Virtua Fighter) for
  //                 Nightwolf's clips, but NO VF motion data exists in any
  //                 of our teardown stores (VF5 extraction holds models;
  //                 its motion data was never converted) — Julia is his
  //                 canon Tekken base and her bank exists. FLAGGED in
  //                 docs/anim/BANK-TABLE-2026-10-20.md for owner confirm;
  //                 revert is deleting this one line.)
  // byou -> lei REMOVED 2026-10-21 (owner: "Lei wulong is not byou, he is Rave/Kiko tanaka, that's
  // been clarified"). Byou keeps its own moveset's bank until the owner names Byou's base.
  // zen -> julia kept as the anim-bank lane set it; CANON.md appendix lists Julia -> NIGHTWOLF /
  // soul ZEN as an unresolved three-way conflict while roster-full.js says Zen = Heihachi —
  // put to the owner, not decided here.
  const FIGHTER_BANK = {
    awapop: 'nina', torch: 'anna', kingtyrant: 'eddy', kai: 'eddy',
    tou: 'paul', gyou: 'hwoarang', zen: 'julia', rave: 'lei',
    yukihyo: 'armorking', nightwolf: 'julia',
  };
  if (Object.prototype.hasOwnProperty.call(FIGHTER_BANK, charId)) return FIGHTER_BANK[charId];
  let src = null;
  try {
    const info = getMovesetInfo(movesetId || charId);
    // anim_bank = the bank of the character this fighter is BUILT ON (tools/moveset-merge
    // annotate(): first T3 base with a decoded bank on disk). t3_source may still name the
    // proxy bank the old generator used; the base's own motion wins (owner 2026-10-20:
    // "Doc Frank ... should be Dr bosconovitch stance, movements, animations").
    src = (info && info.anim_bank) || (info && info.t3_source) || null;
  } catch (e) { /* per-fighter movesets not loaded yet */ }
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
  const res = resolveMove(charId, tekken);
  const ms = (res && res.ms) || getFighterMoveset(charId) || window.WH_MOVESETS?.[charId];
  if (ms) {
    // New shape: per-fighter moveset { moves: { key: {...} }, slots: { notation: key } }.
    // The notation resolves through the player's loadout (own or borrowed moves), then the
    // default slots.
    if (ms.moves) {
      const key = res ? res.key : (ms.moves[tekken] ? tekken : null);
      const mv = key && ms.moves[key];
      if (mv) {
        const anim = mv.anim_t3 || null;
        return {
          startup: mv.startup, active: mv.active, recovery: mv.recovery,
          damage: mv.damage, knock: mv.knock ?? 2.2,
          soulGain: mv.soulGain ?? 8, cost: 0,
          limb: mv.limb || 'armR', heavy: !!mv.heavy,
          unblockable: !!mv.unblockable, isGrab: !!mv.isGrab,
          tekkenInput: tekken, moveKey: key,
          t3row: mv.t3_row, t3source: mv.t3_source || (mv.t3_row != null ? ms.t3_source : null), moveName: mv.name,
          animBank: anim ? anim.bank : null, animRow: anim ? anim.row : null,
          // decoded T3 attack word (high 0x412 / mid 0x217 / low 0x10F / s.mid 0x31F / unblockable 0x607)
          hitWord: ms.hit_words ? ms.hit_words[key] : undefined,
          stanceAfter: ms.stance_after ? ms.stance_after[key] : undefined,
          launch: !!mv.launch, knockdown: !!mv.knockdown,
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
    // Stream 6: lateral (z-axis) velocity for sidesteps / sidewalk.
    this.vz = 0; this.ssDir = 0;

    // state machine
    this.state = 'idle'; this.stateT = 0;
    this.attack = null; this.attackName = null; this._attackPhase = 'startup';
    this.hasHit = false; this.stun = 0; this.invuln = 0; this.dodgeDir = 0;
    this.dead = false; this.combo = 0; this._comboTimer = 0;
    this.tekken = new TekkenBuffer(charData.id); // strings / motion specials / directionals
    // Tekken states (2026-10-21, decoded T3 rules — see _guardBits/canBeHitBy):
    // stance = character stance code after a move whose source notes say "Transition to X"
    // (moveset stance_after), rising = while-standing window after leaving a crouch,
    // stick = facing-relative direction (guard + posture), juggle = hits taken airborne.
    this.stance = null; this.stanceT = 0; this._risingT = 0; this._stickDir = 'n';
    this._juggle = 0; this._rageUsed = false; this._queuedNext = null;

    // Stream 6: throw-lock (throw break window). When a throw connects,
    // attacker enters 'throwing' and victim 'thrown' for THROW_LOCK_T;
    // the victim may break with the matching input (see tryThrowBreak).
    this.lockT = 0; this.lockMove = null; this.lockPartner = null;

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
    // No palette tint over the fighter's own textures; only an explicitly
    // colorized fighter (custom skin tone) is tinted. (TINT FIX: the old
    // char.tintStrength ?? 0.45 default washed both fighters in a constant
    // suit color; real texture colors now render for the whole fight.)
    const inst = assets.createInstance(
      this.char.model || 'pantera',
      this.char.colors.suit, this.char.colors.trim,
      this.char.colorize ? (this.char.tintStrength ?? 0.3) : 0
    );
    this.bones = inst.bones;
    this.mixer = inst.mixer;
    this.actions = inst.actions;

    // REAL T3 animation clips — this fighter's OWN moveset-source bank
    // (see bankIdFor), RETARGETED onto this model's rig (t3anims.js
    // retargetT3Clips: the bank's local rotations only mean something
    // on the identity-rest rig they were baked onto, so they are
    // rebuilt per rig from the decoded frames + both rest poses).
    // A rig without the core humanoid bones keeps embedded locomotion
    // + procedural combat.
    this.t3actions = {};
    this._t3current = null;
    this._t3stateKey = null;
    this._bindT3(inst.model, this._movesetId, this.char.model);

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
      (this.state === 'idle' || this.state === 'walk' || this.state === 'jump' || this.state === 'crouch');
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
        this.char.colorize ? (this.char.tintStrength ?? 0.3) : 0 // TINT FIX: real texture colors unless explicitly colorized
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
    // the (possibly new) moveset source after the form change, and
    // retargeted onto the new form's rig.
    this.t3actions = {};
    this._t3current = null;
    this._t3stateKey = null;
    this._bindT3(inst.model, t.moveset || this._movesetId, t.target);
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

  /* Bind this fighter's own T3 bank, retargeted onto `model`'s rig.
     Must run before the model's mixer first updates (rest pose). */
  _bindT3(model, movesetId, modelKey) {
    const bank = bankIdFor(this.char.id, movesetId);
    if (!bank) {
      console.log(`[WH-T3] no decoded anim bank for ${this.char.id} (source has none yet) — embedded/procedural fallback`);
      return;
    }
    const t3clips = getT3Clips(bank);
    if (!t3clips || !Object.keys(t3clips).length) return;
    const clips = retargetT3Clips(t3clips, bank, model, THREE, modelKey);
    if (!clips || !Object.keys(clips).length) {
      console.log(`[WH-T3] ${this.char.id}: rig '${modelKey}' lacks core humanoid bones — bank '${bank}' not bound`);
      return;
    }
    this.t3actions = createT3Actions(this.mixer, clips, THREE);
    // Move rows retarget lazily on first use (same captured rest pose).
    this._t3 = { bank, clips: t3clips, model, modelKey };
    console.log(`[WH] Fighter ${this.char.id}: ${Object.keys(this.t3actions).length} real T3 actions from bank '${bank}' (retargeted onto ${modelKey})`);
  }

  /* The move's OWN decoded T3 animation (its t3_row in this fighter's
     bank, tools/anim/t3_row_bake.py), retargeted on first use and
     time-scaled so the clip spans the move's startup+active+recovery.
     Returns the action name, or null when the move has no row clip. */
  _moveRowAction(move) {
    if (!this._t3 || !move) return null;
    let row = move.t3row;
    let ok = false;
    if (row != null) {
      const srcBank = move.t3source ? SOURCE_TO_BANK[move.t3source] : this._t3.bank;
      // king/armorking family (anim-bank wiring lane, 2026-10-20): the
      // 'armorking' bank is the SAME divmot03_king motion stream baked on
      // King's own rig (PR #405), and its rows.pack carries the king-row
      // clips — so king-sourced move rows are native to the armorking bank,
      // not foreign clips. Every other source/bank mismatch still blocks.
      const kingFamily = srcBank === 'king' && this._t3.bank === 'armorking';
      ok = srcBank === this._t3.bank || kingFamily;
    }
    if (!ok && move.animRow != null && (SOURCE_TO_BANK[move.animBank] || move.animBank) === this._t3.bank) {
      row = move.animRow; ok = true; // T7/T8 move: its base character's decoded T3 row (anim_t3)
    }
    if (!ok) return null;
    const name = 'row:' + row;
    if (!this.t3actions[name]) {
      if (!this._t3.clips[name]) return null;
      const rc = retargetT3Clips(this._t3.clips, this._t3.bank, this._t3.model, THREE, this._t3.modelKey, [name]);
      if (!rc || !rc[name]) return null;
      Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
    }
    const a = this.t3actions[name];
    const total = (move.startup || 0) + (move.active || 0) + (move.recovery || 0);
    a.timeScale = total > 0.05 ? a.getClip().duration / total : 1;
    return name;
  }

  tryMove(dir) {
    if (!this.canAct()) return;
    this.vx = this.state === 'crouch' ? 0 : dir * this.stats.speed; // no walking while crouched
  }

  /* Facing-relative stick direction this frame ('f','b','u','d','d/f','d/b','u/f','u/b','n'). */
  setStick(dir) { this._stickDir = dir || 'n'; }

  /* Tekken crouch: hold down. Releasing it opens the while-standing (WS.) window. */
  tryCrouch(on) {
    if (this.dead) return;
    if (on && this.onGround && (this.state === 'idle' || this.state === 'walk' || this.state === 'block')) {
      this._enter('crouch'); this.vx = 0;
    } else if (!on && this.state === 'crouch') {
      this._enter('idle'); this._risingT = 0.35;
      if (this.stance === 'FC') { this.stance = null; this.stanceT = 0; } // standing up ends FC
    }
  }

  /* Context the input buffer resolves notations against (WS./FC./SS./BT./R./stance codes). */
  _inputCtx() {
    const st = this.stance;
    return {
      stance: st && st !== 'BT' && st !== 'FC' && st !== 'SS' ? st : null,
      backturned: st === 'BT',
      sidestep: this.state === 'sidestep',
      crouching: this.state === 'crouch' || st === 'FC',
      rising: this._risingT > 0,
      rage: !this._rageUsed && this.hp > 0 && this.hp <= this.maxHp * 0.25,
      inMove: this.state === 'attack',
    };
  }

  /* DECODED T3 RULES (n0madic/Tekken3Remake docs/research/code/combat.md, "Attack levels,
     postures and guards"; HitClassify 0x80044D24, physics guard update).
     Posture bits: 1 crouching, 2 standing, 4 down. Guard bits: 0x08 crouching, 0x10 standing.
     An attack word hits a posture when (word & posture) != 0 and is blocked when
     (guard & word) != 0 while the defender faces the attacker. Guard comes from the stick:
     back -> standing guard (state 0x1052), down-back -> crouching guard (0x2829); the standing
     (0x1952) and crouching (0x3129) stances also guard for human-controlled fighters (bit 8). */
  _postureBits() {
    if (this.state === 'knockdown' && this.onGround) return 4;
    if (this.state === 'crouch' || this.stance === 'FC') return 1;
    if (this.state === 'attack' && /^(FC\.|d\+)/.test(this.attackName || '')) return 1;
    return 2;
  }
  _guardBits() {
    if (!this.onGround || this.dead) return 0;
    const s = this.state;
    if (!(s === 'idle' || s === 'walk' || s === 'crouch' || s === 'block')) return 0;
    const d = this._stickDir || 'n';
    const low = s === 'crouch' || d === 'd' || d === 'd/b';
    if (s === 'block') return low ? 0x08 : 0x10;          // WH block button
    if (d === 'b') return 0x10;
    if (d === 'd/b') return 0x08;
    if (this.isPlayer) return d === 'n' ? 0x10 : (d === 'd' || s === 'crouch') ? 0x08 : 0;
    return 0;
  }
  static defaultWord(move) {
    if (move.isGrab) return 0x800;
    if (move.unblockable) return 0x607;
    return 0x217; // no decoded level in the data: mid (hits every posture, standing guard blocks)
  }
  /* Can `move` connect at all? (highs pass over crouchers, lows over jumpers, standing
     throws whiff crouching/airborne fighters — T3 throw targeting 0x40 standing / 0x20 crouching). */
  canBeHitBy(move) {
    if (this.dead || this.invuln > 0) return false;
    const posture = this._postureBits();
    if (move.isGrab) {
      if (!this.onGround) return false;
      if (posture === 1) return /^(d\+|d\/[fb]\+|FC\.|CROUCHING\.)/.test(move.tekkenInput || '');
      return posture === 2;
    }
    const word = move.hitWord ?? Fighter.defaultWord(move);
    if (!(word & 7 & posture)) return false;
    if ((word & 0x18) === 0x08 && (word & 7) === 7 && !this.onGround) return false; // lows vs airborne
    return true;
  }
  tryJump() { if (this.canAct() && this.onGround) { this.vy = this.stats.jump; this.onGround = false; this._enter('jump'); } }
  tryBlock(on) {
    if (this.dead) return;
    if (on && this.canAct() && this.onGround) { this._enter('block'); this._blendW = 0; }
    else if (!on && this.state === 'block') this._enter('idle');
  }
  tryDodge() {
    if (!this.canAct() || !this.onGround) return;
    this._enter('dodge'); this.invuln = 0.34; this.dodgeDir = -this.facing;
    this._dodgeId = (this._dodgeId || 0) + 1;
    this.vx = this.dodgeDir * this.stats.speed * 1.7;
  }

  /* ---------------- Stream 6: sidestep (Tekken) ----------------
     Tap u/d on the joystick (or W/S) = sidestep into the background
     (dir=-1) / foreground (dir=+1). Grounded in T3-era frame data
     (Tekkenpedia side-step chart: 43f total, no block 1-11f, attacks
     cancelable from 8f): 0.55s total, 0.12s evasion vs strikes,
     attack-cancelable after 0.15s. Evasion is positional — the hurtboxes
     genuinely move off the attack's line on the z-axis. */
  trySidestep(dir) {
    if (!this.canAct() || !this.onGround) return false;
    this._enter('sidestep');
    this.ssDir = dir;
    this._ssId = (this._ssId || 0) + 1;
    this.vz = dir * 3.4;
    this.invuln = 0.12; // early step crushes linear strikes
    return true;
  }
  get sidestepCancelable() { return this.state === 'sidestep' && this.stateT > 0.15; }

  /* ---------------- Stream 6: throw lock / throw breaks (Tekken) ----------------
     When a throw's active frames connect, both fighters enter the lock:
     attacker 'throwing', victim 'thrown', THROW_LOCK_T = 0.3s (18f) break
     window. Victim breaks with the matching input (T3-T7 rules):
       1+3-family -> '1' (LP)      2+4-family -> '2' (RP)
       1+2/3+4/chains -> '1+2' (both punches; '3+4' accepted on mobile)
     Read the attacker's lead arm: left arm = break 1, right arm = break 2,
     both arms = break 1+2. Wrong input or timeout = full throw damage. */
  startThrowLock(move, attacker) {
    this.state = 'thrown'; this.stateT = 0;
    this.lockT = 0.3; this.lockMove = move; this.lockPartner = attacker;
    this.vx = 0; this.vz = 0;
    // face the attacker during the lock
    const want = Math.sign(attacker.root.position.x - this.root.position.x) || 1;
    this.facing = want;
  }
  startThrowing(victim) {
    this.state = 'throwing'; this.stateT = 0;
    this.lockT = 0.3; this.lockVictim = victim; this.lockMove = this.attack;
    this.vx = this.facing * 1.2; // step in with the grab
    this._breakCueT = 0;
  }
  get throwBreakInput() { return this.lockMove && this.lockMove.throw_break; }
  tryThrowBreak(btn) {
    if (this.state !== 'thrown' || !this.lockMove) return false;
    const want = this.lockMove.throw_break || '1';
    const got = (btn === '3+4') ? '1+2' : btn; // mobile: both-kicks = both-punches
    if (got !== want) return false;
    // ESCAPED — both fighters reset, attacker eats whiff recovery
    const attacker = this.lockPartner;
    this.lockT = 0; this.lockMove = null; this.lockPartner = null;
    this._enter('idle');
    this.vx = -this.facing * 2.0; // shoved back out of range
    if (attacker) {
      attacker.lockT = 0; attacker.lockVictim = null; attacker.lockMove = null;
      attacker._enter('idle');
      attacker.stun = Math.max(attacker.stun, 0.3); // whiffed throw = punishable
      attacker.vx = 0;
    }
    this._throwEscaped = true;
    return true;
  }
  completeThrow() {
    // Break window expired — the throw lands for real. Clears both sides of
    // the lock, then routes through the normal receiveHit path.
    const throwing = this.state === 'throwing';
    const attacker = throwing ? this : this.lockPartner;
    const victim = throwing ? this.lockVictim : this;
    const move = this.lockMove;
    const inLock = this.state === 'thrown' || this.state === 'throwing';
    for (const f of [attacker, victim]) {
      if (!f) continue;
      f.lockT = 0; f.lockMove = null; f.lockPartner = null; f.lockVictim = null;
    }
    if (attacker && victim && move && inLock) {
      attacker._enter('idle'); attacker.vx = 0; attacker.vz = 0;
      return victim.receiveHit(move, attacker);
    }
    if (inLock) this._enter('idle');
    return null;
  }
  tryAttack(name) {
    // A press during a string-capable move buffers the next hit (Tekken input buffer):
    // it fires when the current hit's active frames end.
    if (this.state === 'attack' && this.attack && /^[1234](\+[1234])*$/.test(name)) {
      const cont = this.tekken.continuation(name);
      if (cont) { this._queuedNext = cont; return true; }
      // Chord upgrade: input.js emits the first button at once and the chord when the second
      // lands inside its 140 ms window, so '1' then '1+3' means the player pressed 1+3. If the
      // single that just started is part of this chord, the chord replaces it.
      if (name.includes('+') && this.stateT <= 0.14 && this._attackPhase === 'startup' && !this.hasHit) {
        const single = String(this.attackName || '').split(/[,.]/).pop();
        const btn = single.split('+').pop();
        if (/^[1234]$/.test(btn) && name.split('+').includes(btn)) {
          this.tekken.lastMove = this._chordBase || null;
          const saved = { state: this.state, attack: this.attack, attackName: this.attackName, stateT: this.stateT };
          this.state = 'idle';
          if (this._tryAttackFresh(name)) return true;
          Object.assign(this, saved);
        }
      }
    }
    return this._tryAttackFresh(name);
  }
  _tryAttackFresh(name) {
    if (!this.canAct() && !this.sidestepCancelable) return false;
    // Tekken notation resolution: strings (1,2), motion specials (qcf+2),
    // directionals (f+1), state/stance prefixes (WS. FC. SS. BT. R. SNK. ...)
    // via the fighter's TekkenBuffer + its moveset's notation table.
    let notation = LEGACY_TO_TEKKEN[name] || name;
    const ctx = this._inputCtx();
    this._chordBase = this.tekken.lastMove;
    if (/^[1234]$/.test(notation)) {
      const resolved = this.tekken.pressButton(notation, ctx);
      // Stream 6: if the fighter has no move on this limb, keep the raw
      // notation so the base-move fallback below still fires (no dead buttons).
      if (resolved) notation = resolved;
    } else if (/^[1234](\+[1234])+$/.test(notation)) {
      const resolved = this.tekken.pressChord(notation, ctx);
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
    this._queuedNext = null;
    if (/^R\./.test(notation)) this._rageUsed = true; // rage art: once per round
    this.stance = null; this.stanceT = 0; this._risingT = 0;
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup';
    if (name === 'surge') this._auraFlash = 0.7;
    if (move.isGrab || notation === '1+3' || notation === '2+4') this.vx = this.facing * 2.5; // lunge into the grab
    return true;
  }
  /* Start the move for an already-resolved notation (buffered string hits). */
  _fireNotation(notation) {
    const move = getRealMove(this._movesetId, notation);
    if (!move) return false;
    this.tekken._recordMove(notation);
    this.attack = move; this.attackName = notation; this.hasHit = false;
    this._attackId = (this._attackId || 0) + 1;
    this._queuedNext = null;
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup';
    return true;
  }
  _enter(state) { this.state = state; this.stateT = 0; }

  /* ---------------- defense / damage ---------------- */
  isBlocking() { return this.state === 'block'; }

  receiveHit(move, attacker) {
    if (this.dead || this.invuln > 0) return 'dodge';
    const facingAttacker = Math.sign(attacker.root.position.x - this.root.position.x) === this.facing;
    // T3 HitClassify: guarded when (guard & attack word) != 0 and the defender faces the
    // attacker. Standing guard blocks highs/mids, crouching guard blocks lows; throws and
    // unblockables carry no guard bits.
    const word = move.hitWord ?? Fighter.defaultWord(move);
    const guarded = !move.unblockable && !move.isGrab && facingAttacker && (this._guardBits() & word) !== 0;
    if (guarded) {
      // FIRE force (modes lane): strikes chip through guard — chipMult on attacker stats.
      const chip = move.damage * attacker.stats.power * 0.12 * (attacker.stats.chipMult || 1) / this.stats.defense;
      this.hp = Math.max(0, this.hp - chip);
      this.stun = 0.18 + move.damage * 0.01;
      this.vx = Math.sign(this.root.position.x - attacker.root.position.x) * move.knock * 0.5;
      this.meter = Math.min(this.maxMeter, this.meter + 4); // +4 soul on block
      if (this.hp <= 0) { this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || 1); return 'ko'; }
      return 'block';
    }
    let dmg = move.damage * attacker.stats.power / this.stats.defense;
    // T3 HitDamage: counter hit when the defender is in the startup of its own attack:
    // d = e + d*12/10, e = |defender move damage| * 3/10 * 3/10 * (frames into startup / startup).
    let counter = false;
    if (this.state === 'attack' && this._attackPhase === 'startup' && this.attack && this.attack.damage > 0) {
      counter = true;
      const prog = this.attack.startup > 0 ? Math.min(1, this.stateT / this.attack.startup) : 1;
      dmg = this.attack.damage * 0.09 * prog + dmg * 1.2;
    }
    // Juggle scaling: first airborne hit x0.8, later ones x0.5.
    if (!this.onGround && !move.isGrab) { dmg *= this._juggle === 0 ? 0.8 : 0.5; this._juggle++; }
    this.lastCounterHit = counter;
    this.hp = Math.max(0, this.hp - dmg);
    this.meter = Math.min(this.maxMeter, this.meter + 6); // +6 soul on taking damage
    const dir = Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing;
    this.vx = dir * move.knock;
    if (this.hp <= 0) { this._knockout(dir); return 'ko'; }
    if (move.isGrab || move.knock >= 6 || move.launch || (counter && move.knockdown)) {
      this.vy = move.isGrab ? 5.2 : 4.6; this.onGround = false; this.stun = 0.55; this._enter('knockdown');
    } else { this.stun = 0.2 + move.damage * 0.012 + (counter ? 0.12 : 0); this._enter('hitstun'); }
    this.stance = null;
    return counter ? 'counter' : 'hit';
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
    // Throw cinematic: both locked fighters are committed, not hittable.
    if (this.state === 'thrown' || this.state === 'throwing') return [];
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
    if (this.lockT > 0) this.lockT -= dt; // throw-break window
    if (this._risingT > 0) this._risingT -= dt;
    if (this.stanceT > 0) { this.stanceT -= dt; if (this.stanceT <= 0) this.stance = null; }
    if (this.onGround && this.state !== 'knockdown') this._juggle = 0;
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
        else {
          const after = m.stanceAfter;
          this.attack = null; this.attackName = null; this._enter('idle');
          // Source notes "Transition to X": the move ends in that stance (FC = crouch).
          if (after === 'FC') { this._enter('crouch'); this.stance = 'FC'; this.stanceT = 0.5; }
          else if (after) { this.stance = after; this.stanceT = 0.8; }
        }
        // Buffered string hit fires once this hit's active frames are over.
        if (this._queuedNext && this.state === 'attack' && this._attackPhase === 'recovery') {
          const next = this._queuedNext; this._queuedNext = null;
          this.state = 'idle'; // release the current hit into the next one
          if (!this._fireNotation(next)) this.state = 'attack';
        }
        break;
      }
      case 'crouch': break;
      case 'jump': if (this.onGround) this._enter('idle'); break;
      case 'hitstun': if (this.stun <= 0) this._enter('idle'); break;
      case 'knockdown': if (this.onGround && this.stun <= 0) this._enter('idle'); break;
      case 'dodge': if (this.stateT > 0.34) { this.vx = 0; this._enter('idle'); } break;
      case 'sidestep':
        if (this.stateT > 0.55) { this.vz = 0; this._enter('idle'); }
        break;
      case 'thrown':
      case 'throwing':
        // Throw-lock: game.js resolves the lock when the break window
        // (lockT) expires, so hit feedback stays in one place.
        break;
      case 'idle': case 'walk':
        this.state = (Math.abs(this.vx) > 0.4 && this.onGround) ? 'walk' : 'idle';
        break;
    }
  }

  _physics(dt, opponent) {
    if (!this.onGround) this.vy -= 22 * dt;
    if (this.onGround && this.state !== 'walk' && this.state !== 'dodge' && this.state !== 'sidestep' && !(this.state === 'attack' && this.attackName === 'grab')) {
      this.vx *= Math.pow(0.0001, dt);
      if (Math.abs(this.vx) < 0.05) this.vx = 0;
    }
    // Lateral drift decays once the sidestep ends.
    if (this.state !== 'sidestep') {
      this.vz *= Math.pow(0.0001, dt);
      if (Math.abs(this.vz) < 0.05) this.vz = 0;
    }
    this.root.position.x += this.vx * dt;
    this.root.position.y += this.vy * dt;
    this.root.position.z += this.vz * dt;
    // Sidestep range: about one body width into the background/foreground.
    this.root.position.z = Math.max(-2.4, Math.min(2.4, this.root.position.z));

    if (this.root.position.y <= GROUND_Y) {
      this.root.position.y = GROUND_Y; this.vy = 0;
      if (!this.onGround) { this.onGround = true; if (this.state === 'knockdown') this.stun = Math.max(this.stun, 0.4); }
    }
    this.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, this.root.position.x));

    // Body-vs-body pushout — fighters NEVER interpenetrate (x and z).
    if (opponent) {
      const dx = this.root.position.x - opponent.root.position.x;
      const dz = this.root.position.z - opponent.root.position.z;
      const minDist = 1.45;
      if (Math.abs(this.root.position.y - opponent.root.position.y) < 1.8) {
        if (Math.abs(dx) < minDist && Math.abs(dz) < 0.9) {
          const push = (minDist - Math.abs(dx)) / 2 * (dx >= 0 ? 1 : -1);
          this.root.position.x += push; opponent.root.position.x -= push;
        }
        // lateral separation after sidesteps
        if (Math.abs(dz) < 0.7 && Math.abs(dx) < minDist) {
          const zp = (0.7 - Math.abs(dz)) / 2 * (dz >= 0 ? 1 : -1);
          this.root.position.z += zp; opponent.root.position.z -= zp;
        }
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

  /* The bank's side-step clip that travels toward the character's
     left (wantLeft) or right, chosen by the decoded root drift. */
  _sidestepClip(wantLeft) {
    for (const n of ['sidestepA', 'sidestepB']) {
      const a = this.t3actions[n];
      const dx = a && a.getClip().userData.lateralDx;
      if (a && dx && (dx > 0) === wantLeft) return n;
    }
    return null;
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

    // 2) Which REAL T3 clip owns this state? (FROZEN-IDLE FIX 2026-10-20:
    // the bank's animated stance/walk clips existed but were NEVER played
    // — idle fell through to _stopT3() and the near-static embedded Idle,
    // whose rotation range is <=4.8 deg and whose Hips bob is pinned away
    // at load. Headless diag on the old code: t3 stance t=0 w=0 while the
    // mixer advanced the embedded Idle at w=1; bone movement over 2 s
    // measured 0.0-1.0 deg on every bone.)
    const T3_ATTACK_MAP = { punch: 'light', kick: 'medium', grab: 'grab', surge: 'heavy', heavy: 'heavy',
      '1': 'light', '2': 'light', '3': 'medium', '4': 'medium', '1+3': 'grab', '2+4': 'grab' };
    const attackClipFor = () => {
      let n = T3_ATTACK_MAP[this.attackName];
      if (!n && typeof this.attackName === 'string') {
        const lastBtn = this.attackName.split(',').pop().split('+').pop();
        n = T3_ATTACK_MAP[lastBtn] || 'heavy'; // strings -> last hit's clip; specials -> heavy
      }
      return n;
    };
    // Reverse the walk cycle when backing away so retreating reads
    // as a back-step instead of a moonwalk.
    const dirSign = Math.abs(this.vx) > 0.05 ? (Math.sign(this.vx) === this.facing ? 1 : -1) : 1;
    let t3Wanted = null;
    switch (this.state) {
      case 'idle': t3Wanted = 'stance'; break;
      case 'walk': t3Wanted = dirSign < 0 ? 'walkBack' : 'walkFwd'; break;
      case 'block': t3Wanted = 'block'; break;
      case 'crouch': t3Wanted = this.t3actions.crouchHold ? 'crouchHold' : 'crouch'; break;
      case 'victory': t3Wanted = 'win'; break;
      case 'hitstun': t3Wanted = 'hit'; break;
      case 'knockdown': t3Wanted = 'launch'; break;
      case 'ko': t3Wanted = 'ko'; break;
      case 'attack': t3Wanted = attackClipFor(); break;
    }
    if (t3Wanted && !this.t3actions[t3Wanted] && this.t3actions.stance) t3Wanted = 'stance';
    const t3Active = !!(t3Wanted && this.t3actions[t3Wanted]);

    // 3) Locomotion crossfade (embedded mocap base layer). When a T3 clip
    // owns the state, the embedded layer is driven to ZERO: the per-frame
    // setEffectiveWeight below re-asserts it every fixed step, and at
    // weight ~1 it diluted every T3 clip ~50/50 with the held embedded
    // pose (vendor three: setEffectiveWeight stops fades but the weight
    // itself is re-applied before every mixer.update).
    let tIdle = 1, tWalk = 0, tRun = 0;
    if (this.state === 'walk') {
      const fast = Math.abs(this.vx) > this.stats.speed * 0.9;
      tIdle = 0; tWalk = fast ? 0 : 1; tRun = fast ? 1 : 0;
    } else if (this.state === 'dodge') { tIdle = 0; tRun = 1; }
    if (t3Active) { tIdle = 0; tWalk = 0; tRun = 0; }
    const rate = 1 - Math.exp(-dt / 0.12);
    this._locoIdle += (tIdle - this._locoIdle) * rate;
    this._locoWalk += (tWalk - this._locoWalk) * rate;
    this._locoRun += (tRun - this._locoRun) * rate;
    if (this.actions.Idle) this.actions.Idle.setEffectiveWeight(this._locoIdle);
    if (this.actions.Walk) this.actions.Walk.setEffectiveWeight(this._locoWalk);
    if (this.actions.Run) this.actions.Run.setEffectiveWeight(this._locoRun);
    if (this.actions.Walk) this.actions.Walk.timeScale = dirSign;
    if (this.actions.Run) this.actions.Run.timeScale = dirSign;

    // 4) Advance clips (writes the posed skeleton into bones)
    this.mixer.update(dt);

    // 5) Refresh world matrices so IK reads the posed skeleton
    this.root.updateWorldMatrix(true, true);

    // 6) Combat override layer (IK) + lean targets
    this._leanT.x = 0; this._leanT.z = 0;
    this.trail.visible = false;
    // REAL T3 clips per state (falls back to procedural if unavailable)
    switch (this.state) {
      case 'idle':
      case 'walk':
        // Animated bank stance / walk cycle — the living fighting idle.
        if (t3Active) this._playT3(t3Wanted, { loop: true });
        else this._stopT3();
        break;
      case 'attack': {
        // Main's move-row mapping first (PR #338), then the attackName fallback.
        const t3name = this._moveRowAction(this.attack) || attackClipFor();
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
      case 'crouch':
        // Bank crouch hold (T3 crouching stance, slot 40) — the posture lows/FC moves use.
        if (!(t3Active && this._playT3(t3Wanted, { loop: true, fade: 0.08 }))) { this._leanT.x = 0.25; this._stopT3(); }
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
      case 'dodge':
        // The dodge moves the fighter backwards: T3's own back-dash
        // (b,b branch of the neutral row) when the bank is bound.
        if (!this._playT3Once('backdash', 'dodge:' + this._dodgeId)) {
          this._leanT.z = this.dodgeDir * this.facing * 0.32; this._stopT3();
        }
        break;
      case 'sidestep': {
        // Real T3 side step when the bank is bound: the clip whose decoded
        // root drift goes the same way as this step (character-left is
        // world -z when facing +x). Otherwise lean into the lateral step;
        // slight crouch like a real sidestep.
        const ss = this._sidestepClip(this.ssDir === -this.facing);
        if (!ss || !this._playT3Once(ss, 'ss:' + this._ssId)) {
          this._leanT.z = this.ssDir * 0.38;
          this._leanT.x = 0.1;
          this._stopT3();
        }
        break;
      }
      case 'throwing': {
        // Hold the double-arm snatch; flash the LEAD arm as the break cue
        // (Tekken: left arm forward = break 1, right arm = break 2, both = 1+2).
        const brk = this.lockMove && this.lockMove.throw_break;
        this._leanT.x = -0.22;
        const pulse = 0.55 + 0.45 * Math.sin(performance.now() * 0.03);
        if (brk === '1') this._showTrail(this.bones.LeftHand, pulse);
        else if (brk === '2') this._showTrail(this.bones.RightHand, pulse);
        else { this._showTrail(this.bones.RightHand, pulse); this._showTrail(this.bones.LeftHand, pulse * 0.9); }
        // A bound bank keeps its grab clip clamped on the snatch; stopping
        // it would drop the rig to its rest (T-)pose.
        if (!this.t3actions.grab) this._stopT3();
        break;
      }
      case 'thrown':
        // Victim caught: rocked back, arms up (T3 hit reaction when bound).
        this._leanT.x = 0.3;
        if (!this._playT3Once('hit', 'thrown')) this._stopT3();
        break;
      case 'jump': {
        const jn = Math.abs(this.vx) < 0.4 ? 'jumpUp' : (Math.sign(this.vx) === this.facing ? 'jumpFwd' : 'jumpBack');
        if (!this._playT3Once(this.t3actions[jn] ? jn : 'jumpUp', 'jump')) { this._animJump(); this._stopT3(); }
        break;
      }
      default: {
        // idle / walk: the bank's neutral stance and walk cycles. Without
        // a bound bank the embedded Mixamo locomotion layer (above) shows.
        let loco = null;
        if (this.state === 'walk' && this.t3actions.walkFwd) loco = dirSign > 0 || !this.t3actions.walkBack ? 'walkFwd' : 'walkBack';
        else if (this.t3actions.stance) loco = 'stance';
        if (loco && this._playT3(loco, { loop: true, fade: 0.12 })) this._t3stateKey = null;
        else this._stopT3();
        break;
      }
    }

    // 7) Smooth & apply lean (body english) — composed with facing
    const lr = 1 - Math.exp(-dt / 0.05);
    this._lean.x += (this._leanT.x - this._lean.x) * lr;
    this._lean.z += (this._leanT.z - this._lean.z) * lr;
    this.lean.rotation.x = this._lean.x;
    this.lean.rotation.z = this._lean.z;

    // 8) Aura + trail visuals — particles rise and flicker around the body
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
