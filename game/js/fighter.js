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
import { getT3Clips, createT3Actions, retargetT3Clips, SOURCE_TO_BANK,
  clipStrikeProfile, clipHitWindow, bankAttackPool, attackLevelOfWord, attackClipTime, clipIsThrow, BUTTON_LIMB } from './t3anims.js';
import { TekkenBuffer, getFighterMoveset, getMovesetInfo, resolveMove } from './movesets.js';
import { TransformCinematic } from './transform-cinematic.js';
import { V, vskillFor, vtriggerEnhance, vreversalMove } from './v-system.js';
import { JiggleRig } from './jiggle.js';
import { SoftBody } from './softbody.js';
import { FaceRig } from './faceRig.js';
import { HandPoseBlender } from './handPoses.js';
import { t8Frame, stunFromAdvantage } from './frame-tables.js';
import { hitWordFor, attackPhase, moveReach, PressBuffer } from './combat-core.js';

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
  'doc-frank-hood': 'gunjack',
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
    // 2026-10-23 (Claude session): the last decoded T3 banks (tools/anim/t3_bake_bank.py). These movesets
    // name their source as a teardown path or not at all, so bind each to its base's own bank here.
    chatur: 'ogre', dorowani: 'gon', menajerii: 'kuma',
    // 2026-10-23 (landing wave 3): the bear-bank successors + Silvertongue.
    // Their index entries name the bank (anim_bank/t3_source), but the
    // portrait-capture page resolves banks without the moveset index
    // loaded, so bind them here like the 2026-10-23 additions above.
    //   gashadokuro -> kuma (CANON: his base is the Kuma bank)
    //   aotsuki     -> kuma (CANON: Panda shares Kuma's T3 bank)
    //   silvertongue -> xiaoyu (her kit's T3 bank, per lili.json t3_source)
    gashadokuro: 'kuma', aotsuki: 'kuma', silvertongue: 'xiaoyu',
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
/* Donor keys, most to least specific, for borrowing an animated row:
   exact command, last segment, dir+last button, last button, limb. */
export function rowDonorKeys(input, limb) {
  const n = String(input).replace(/^[A-Z_]+\./, '').trim();
  const last = n.split(',').pop().trim();
  const m = last.match(/^(d\/f|d\/b|u\/f|u\/b|f|b|u|d)?\+?([1-4](?:\+[1-4])*)/i);
  const keys = ['c:' + n, 's:' + last];
  if (m) { keys.push('db:' + (m[1] || 'n').toLowerCase() + '+' + m[2]); keys.push('b:' + m[2]); keys.push('b:' + m[2].split('+').pop()); }
  if (limb) keys.push('l:' + limb);
  return keys;
}
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
          hitWord: (ms.hit_words && ms.hit_words[key] != null) ? ms.hit_words[key] : hitWordFor(mv),
          hitLevel: mv.hit_level, reach: mv.reach,
          stanceAfter: ms.stance_after ? ms.stance_after[key] : undefined,
          launch: !!mv.launch, knockdown: !!mv.knockdown,
          armor: !!mv.armor,
          rageArt: !!mv.rageArt, rageDrive: !!mv.rageDrive,
          urgeEngager: !!mv.urgeEngager,
          urgeBurst: !!mv.urgeBurst, urgeSmash: !!mv.urgeSmash,
          // T8 frame tables (wavu.wiki CC0): block/hit/CH advantage + throw break.
          t8: t8Frame(ms, tekken),
          throw_break: mv.throw_break || (t8Frame(ms, tekken) || {}).brk || undefined,
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

const GROUND_Y_DEFAULT = 0;
let GROUND_Y = 0; // stage-break lane: floor/balcony breaks drop the fighting level
export function setGroundY(v) { GROUND_Y = v; }
export function getGroundY() { return GROUND_Y; }
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
    this._rageOn = false;
    this._urgeOn = false; this._urgeUsed = false; this._urgeT = 0; this._urgePips = 0;
    this._urgeDashT = 0;

    // Stream 6: throw-lock (throw break window). When a throw connects,
    // attacker enters 'throwing' and victim 'thrown' for THROW_LOCK_T;
    // the victim may break with the matching input (see tryThrowBreak).
    this.lockT = 0; this.lockMove = null; this.lockPartner = null;

    // V-System (owner 2026-10-22): Nine-Soul meter resource game.
    // _vtriggerT = install timer, _vbreakT = V-Shift Break window,
    // _vparryT = V-Skill parry active window, _vshiftProc = shift evaded.
    this._vtriggerT = 0; this._vbreakT = 0; this._vparryT = 0;
    this._vshiftProc = false;

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
      this.char.model,
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

    // Secondary systems (teardown wiring 2026-10-22): jiggle spring bones,
    // face morph driver + blink timer, hand pose library.
    // Jiggle: family from char data (default by model); intensity presets.
    const jiggleFamily = this.char.jiggleFamily || 'female';
    this._jiggle = null;
    // Find first skinned mesh for jiggle rig
    this.root.traverse(o => {
      if (!this._jiggle && o.isSkinnedMesh) {
        try { this._jiggle = JiggleRig.fromMesh(o, jiggleFamily); } catch (e) {}
      }
    });
    const jiggleIntensity = this.char.jiggleIntensity || 'natural';
    if (this._jiggle) this._jiggle.setIntensity(jiggleIntensity);
    // Soft-body muscle volume (PBD lane, 2026-10-23): Jolt XPBD torso volume
    // for muscle deformation on hit + volume-grounded jiggle. Same pattern
    // as jiggle: inert until Jolt loads, every call guarded, never crashes
    // the fight. char.softbody === false opts out.
    this._softbody = null;
    const softSpec = SoftBody.anatomyFor(this.char);
    if (softSpec) {
      this.root.traverse(o => {
        if (!this._softbody && o.isSkinnedMesh) {
          try { this._softbody = SoftBody.fromMesh(o, softSpec); } catch (e) {}
        }
      });
    }
    // Face rig: morph driver + blink timer
    this._face = FaceRig.attach(this.root);
    // Hand poses: fist default, blended per state
    this._hands = new HandPoseBlender();
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

  /* ATTACK CLIP SELECTION (lane D, 2026-10-24; owner: "the different move inputs from the move
     lists ... aren't working ... just random stuff is happening"). Before this, every move with no
     row clip played the bank's generic light/medium/heavy (Skull: 205 of 293 inputs), so different
     inputs looked the same, and those clips ran at timeScale 1, unsynced to the move's startup.
     The move that resolved now plays a clip of the fighter's OWN bank, first match wins (never
     another character's per-move clips; docs/RULES_NO_GUESSING.md — nothing authored):
       own       the move's decoded T3 row: t3_row (a string's list names one row per hit; the key
                 fires the last), when its t3_source maps to the bound bank
       notation  the decoded T3 row (own t3_row) of the move this fighter's moveset binds to the SAME
                 input — the T3 copy of the move a merged T7/T8 move replaced in its slot (Skull's
                 T3 '1' = row 50, the i10 jab, for the T8 Jab)
       anim      anim_t3 {bank,row} 'same-notation' (tools/moveset-merge: the first T3 move found with
                 that notation, any stance) — merge-time guess, so after notation. anim_t3 'nearest'
                 (approximate) is tried only after match: it disagrees with the pressed button 43%.
       match     the bank's decoded attack row (hit_frames.json) started by the SAME buttons (decoded
                 branch command; 1/2/3/4 = L/R punch, L/R kick), then the same limb, at the move's
                 height (decoded attack word / T8 / T7 hit level), nearest decoded hit frame to its
                 startup — closest real clip of the same character, flagged 'match'
       generic   the bank's light/medium/heavy (grab for throws) striking with that limb (measured)
     STRIKE vs THROW (owner: "pressing 1 ... can show a THROW"): every candidate's decoded row type
     (hit_frames.json throw flag) must agree with the move — a strike never plays a throw row, a throw
     (isGrab / throw level / 1+3 / 2+4, as the game treats it) never plays a strike row. A conflicting
     row is skipped and logged in plan.rejected (moveset data to fix), e.g. Pantera's T8 Jab, whose
     anim_t3 'same-notation' row 290 is King's decoded throw attempt. Throws without a throw row of
     their own match the bank's decoded throw-attempt rows instead of the strike pool.
     Returns { name, kind, why, limb, level, timing, rejected } or null (no bank: procedural).
     timing = clip hit window -> move active frames (see _applyAttackWarp). Pure: no actions made. */
  static attackLimb(move, attackName) {
    const L = move && move.limb;
    if (L === 'armL' || L === 'armR' || L === 'legL' || L === 'legR') return L;
    const hit = String(attackName || (move && move.tekkenInput) || '').split(/[,.]/).pop();
    const b = (hit.match(/[1-4]/) || [])[0];
    return { 1: 'armL', 2: 'armR', 3: 'legL', 4: 'legR' }[b] || (L === 'both' && /[34]/.test(hit) ? 'legR' : 'armR');
  }
  /* Button mask of the hit a notation fires (its last hit, after any stance prefix):
     1 LP, 2 RP, 4 LK, 8 RK (the T3 command bits); else the move's limb as one button; 0 unknown. */
  static attackButtons(move, attackName) {
    const hit = String(attackName || (move && move.tekkenInput) || '').split(/[,.~:]/).pop();
    let m = 0;
    for (const b of hit.match(/(?<![a-z/])[1-4](?![0-9])/gi) || []) m |= 1 << (+b - 1);
    if (m) return m;
    return { armL: 1, armR: 2, legL: 4, legR: 8 }[move && move.limb] || 0;
  }
  static attackLevel(move, raw) {
    if (move && move.hitWord != null) { const l = attackLevelOfWord(move.hitWord); if (l) return l; }
    const lab = (move && move.t8 && move.t8.tgt) || (raw && (raw.hit_level || (raw.t7 && raw.t7.hit_level))) || '';
    const tok = String(lab).split(',').map(s => s.trim()).filter(Boolean).pop() || '';
    const t = tok.toLowerCase().replace(/[!()\s.]/g, '');
    if (!t || t === '-') return null;
    if (/throw|^th|^t/.test(t)) return 't';
    if (/^s(m|mid)/.test(t)) return 's';
    return { h: 'h', m: 'm', l: 'l' }[t[0]] || ({ high: 'h', mid: 'm', low: 'l' })[t] || (t.startsWith('sl') ? 'l' : null);
  }
  _attackRowIndex() {
    // This fighter's own decoded T3 rows (t3_row in the bound bank) by input, from its moveset:
    // a move keyed by the notation first, then the slots table, then the moves' input fields.
    const t3 = this._t3, msId = this._movesetId;
    if (t3.rowIdx && t3.rowIdx.ms === msId) return t3.rowIdx;
    const idx = { ms: msId, byInput: new Map() };
    const ms = getFighterMoveset(msId);
    if (ms && ms.moves) {
      const add = (n, name) => { if (!n) return; const l = idx.byInput.get(n) || []; if (!l.includes(name)) l.push(name); idx.byInput.set(n, l); };
      const keyRow = {};
      for (const [k, m] of Object.entries(ms.moves)) {
        const r = m && this._ownRow({ t3row: m.t3_row, t3source: m.t3_source || (m.t3_row != null ? ms.t3_source : null) }, 'own');
        if (r) keyRow[k] = r.name;
      }
      for (const [k, name] of Object.entries(keyRow)) add(k, name);
      for (const [n, k] of Object.entries(ms.slots || {})) if (keyRow[k]) add(n, keyRow[k]);
      for (const [k, name] of Object.entries(keyRow)) add(ms.moves[k].input, name);
    }
    t3.rowIdx = idx;
    return idx;
  }
  _ownRow(move, which = null) {
    const t3 = this._t3, clips = t3.clips;
    const last = (r) => (Array.isArray(r) ? r[r.length - 1] : r);
    // king/armorking family (anim-bank wiring lane, 2026-10-20): the 'armorking' bank is the SAME
    // divmot03_king motion stream baked on King's own rig (PR #405), so king rows are native to it.
    const same = (b) => b === t3.bank || (b === 'king' && t3.bank === 'armorking');
    if (which !== 'anim' && move.t3row != null) {
      const r = last(move.t3row);
      if (same(move.t3source ? SOURCE_TO_BANK[move.t3source] : t3.bank) && clips['row:' + r]) return { name: 'row:' + r, kind: 'own' };
    }
    if (which !== 'own' && move.animRow != null) {
      const r = last(move.animRow);
      if (same(SOURCE_TO_BANK[move.animBank] || move.animBank) && clips['row:' + r]) return { name: 'row:' + r, kind: 'anim' };
    }
    return null;
  }
  _attackClipPlan(move, attackName) {
    if (!this._t3 || !this._t3.clips) return null;
    const { bank, clips } = this._t3;
    const ms = getFighterMoveset(this._movesetId);
    const raw = move && move.moveKey && ms && ms.moves ? ms.moves[move.moveKey] : null;
    const limb = Fighter.attackLimb(move, attackName);
    const level = Fighter.attackLevel(move, raw);
    // Throw as the game treats it (_tryAttackFresh lunge / getHitbox grab sphere / canBeHitBy).
    const grab = !!(move && move.isGrab) || /^(grab|1\+3|2\+4)$/.test(String(attackName || '')) || level === 't';
    const S = move && Number.isFinite(move.startup) ? move.startup : 0;
    const rejected = [];
    // A row whose decoded type disagrees with the move is skipped (strike <-> throw).
    const fits = (c) => {
      if (!c || !clips[c.name]) return null;
      const thr = clipIsThrow(clips[c.name]), atk = !!(clips[c.name].userData.hit && clips[c.name].userData.hit[0] > 0);
      if (grab ? thr : !thr) return c;
      if (grab && !atk) return c; // a throw on a non-attack row (no decoded hit at all): nothing contradicts it
      rejected.push(`${c.kind} ${c.name} is a ${thr ? 'throw' : 'strike'} row`);
      return null;
    };
    let pick = move ? fits(this._ownRow(move, 'own')) : null;
    if (!pick) {
      const idx = this._attackRowIndex();
      for (const n of [move && move.tekkenInput, attackName, raw && raw.input]) {
        for (const name of (n && idx.byInput.get(n)) || []) {
          pick = fits({ name, kind: 'notation', why: `same input '${n}'` });
          if (pick) break;
        }
        if (pick) break;
      }
    }
    // anim_t3 'nearest' rows (merge-time limb/class/startup guess, flagged approximate) show a
    // different button than the input on 43% of slots (measured 2026-10-24); they come after match.
    const animNearest = !!(raw && raw.anim_t3 && /nearest/.test(String(raw.anim_t3.match || '')));
    if (!pick && move && !animNearest) pick = fits(this._ownRow(move, 'anim'));
    // Main's animated-row donor (combat pt198u, kept): the decoded row of the closest animated move in the SAME
    // moveset (same command, else same direction+button, else same button/limb), strike/throw-checked like the rest.
    if (!pick && move) { const d = this._rowDonor(move); if (d != null) pick = fits({ name: 'row:' + d, kind: 'donor', why: `donor row ${d}` }); }
    // The move's buttons (last hit of its notation: 1 LP, 2 RP, 3 LK, 4 RK) and the limb they name.
    const btn = Fighter.attackButtons(move, attackName);
    const btnLimb = BUTTON_LIMB[btn] || limb;
    if (!pick) {
      // Same buttons first, then the same limb, each at the move's height then any height;
      // nearest decoded hit frame to the move's startup inside the first tier that has rows.
      const NEAR = { h: ['h', 'm'], m: ['m', 's', 'u'], s: ['s', 'l', 'm'], l: ['l', 's'], u: ['u', 'm'] };
      const all = bankAttackPool(bank, { throws: grab });
      const tiers = [];
      for (const pool of [btn ? all.filter(c => c.btn === btn) : [], all.filter(c => c.limb === btnLimb)]) {
        if (!grab && level && NEAR[level]) for (const l of NEAR[level]) tiers.push(pool.filter(c => c.level === l));
        tiers.push(pool);
      }
      if (grab) tiers.push(all); // throw reach: any decoded throw attempt of this character
      for (const tier of tiers) {
        if (!tier.length) continue;
        let best = tier[0];
        for (const c of tier) if (Math.abs(c.t0 - S) < Math.abs(best.t0 - S)) best = c;
        pick = { name: best.name, kind: 'match', why: `${grab ? 'throw ' : ''}btn ${best.btn || '?'} ${best.limb}${best.limbSrc === 'measured' ? '(measured)' : ''} ${best.level || '?'}${level && best.level !== level ? ` (move ${level})` : ''} hit@${Math.round(best.t0 * 60)}f` };
        break;
      }
    }
    if (!pick && move && animNearest) pick = fits(this._ownRow(move, 'anim'));
    if (!pick) {
      // Generic action clips, by the button of the row each one plays (decoded), else measured limb.
      const cands = (grab ? ['grab'] : []).concat(['light', 'medium', 'heavy']).filter(n => clips[n] && clipIsThrow(clips[n]) === grab);
      const limbOf = (n) => { const h = clips[n].userData.hit; const p = clipStrikeProfile(bank, clips[n]); return BUTTON_LIMB[h && h[5]] || (p && p.dominant); };
      const arm = (l) => l && l.startsWith('arm');
      let best = grab && clips.grab && clipIsThrow(clips.grab) ? 'grab' : null;
      for (const want of [(d) => d === btnLimb, (d) => arm(d) === arm(btnLimb)]) {
        if (best) break;
        for (const n of cands) if (want(limbOf(n))) { best = n; break; }
      }
      // Last resort (a bank with no decoded throw row baked): the bank's own grab action, flagged.
      best = best || (grab ? 'grab' : arm(btnLimb) ? 'light' : 'medium');
      if (clips[best]) pick = { name: best, kind: 'generic', why: `generic ${best} for ${btnLimb}${grab && !clipIsThrow(clips[best]) ? ' (NOT a throw row)' : ''}` };
    }
    if (!pick) return null;
    // Timing: the clip's hit window (decoded T3 active frames, else the measured extension peak of
    // the move's limb) is placed on the move's active frames; recovery fills the move's total.
    const src = clips[pick.name];
    const A = move && Number.isFinite(move.active) ? move.active : 0;
    const R = move && Number.isFinite(move.recovery) ? move.recovery : 0;
    let timing = null;
    if (src && S + A + R > 0.05) {
      const w = clipHitWindow(bank, src, limb);
      const D = src.duration;
      const t0 = w ? Math.min(w.t0, D) : D * S / (S + A + R);
      const t1 = w ? Math.min(Math.max(w.t1, t0), D) : D * (S + A) / (S + A + R);
      timing = { S, A, R, t0, t1, D, src: w ? w.src : 'proportional' };
    }
    return { ...pick, limb, level, grab, timing, rejected };
  }

  /* The action for the current attack (plan cached per attack id; row clips retarget lazily on
     first use, same captured rest pose). */
  _attackClip(move, attackName) {
    if (!this._t3) return null;
    const p = this._atkPlan;
    if (p && p.id === this._attackId && p.move === move) return p.name;
    const plan = this._attackClipPlan(move, attackName);
    let name = plan ? plan.name : null;
    if (name && !this.t3actions[name] && name.startsWith('row:')) {
      const rc = retargetT3Clips(this._t3.clips, this._t3.bank, this._t3.model, THREE, this._t3.modelKey, [name]);
      if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
    }
    if (name && !this.t3actions[name]) name = null;
    this._atkPlan = { id: this._attackId, move, name, kind: plan && plan.kind, why: plan && plan.why,
      limb: plan && plan.limb, timing: plan && plan.timing, rejected: plan && plan.rejected };
    return name;
  }

  /* Drive the attack clip's time from the move's own clock (stateT), before the mixer samples:
     clip hit window -> the move's active frames (attackClipTime). The clip is held at timeScale 0
     while warped; released (timeScale 1) when the attack ends or another clip takes over. */
  _applyAttackWarp() {
    const w = this._atkWarp;
    const attacking = this.state === 'attack' || this.state === 'vskill' || this.state === 'vreversal';
    if (w && (!attacking || w.id !== this._attackId || this._t3current !== w.action)) {
      w.action.timeScale = 1;
      this._atkWarp = null;
    }
    const p = this._atkPlan;
    if (!attacking || !p || p.id !== this._attackId || !p.name || !p.timing) return;
    const a = this.t3actions[p.name];
    if (!a || this._t3current !== a) return; // starts in this frame's state switch
    if (!this._atkWarp) this._atkWarp = { id: p.id, action: a };
    a.timeScale = 0;
    a.time = attackClipTime(p.timing, this.stateT);
  }

  _rowDonor(move) {
    const ms = getFighterMoveset(this._movesetId);
    if (!ms || !ms.moves || !this._t3) return null;
    if (!this._donorIdx || this._donorIdx.ms !== ms) {
      const idx = new Map();
      const bank = this._t3.bank;
      for (const mv of Object.values(ms.moves)) {
        if (mv.t3_row == null) continue;
        const src = mv.t3_source || ms.t3_source;
        if ((SOURCE_TO_BANK[src] || src) !== bank && !(src === 'king' && bank === 'armorking')) continue;
        for (const k of rowDonorKeys(mv.input || '', mv.limb)) if (!idx.has(k)) idx.set(k, mv.t3_row);
      }
      this._donorIdx = { ms, idx };
    }
    for (const k of rowDonorKeys(move.tekkenInput || '', move.limb)) {
      const r = this._donorIdx.idx.get(k);
      if (r != null && this._t3.clips['row:' + r]) return r;
    }
    return null;
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
      urgeOn: !!this._urgeOn,
      urgeAvailable: !this._urgeUsed && !this._urgeOn && this.hp > 0,
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
    // FIGHTER DEPTH (worker 34): soul kindle flash — cannot block during it (T7).
    if (on && this.kindle && !this.kindle.canBlock()) return;
    if (on && this.canAct() && this.onGround) { this._enter('block'); this._blendW = 0; }
    else if (!on && this.state === 'block') this._enter('idle');
  }
  tryDodge() {
    if (!this.canAct() || !this.onGround) return;
    this._enter('dodge'); this.invuln = 0.34; this.dodgeDir = -this.facing;
    this._dodgeId = (this._dodgeId || 0) + 1;
    this.vx = this.dodgeDir * this.stats.speed * 1.7;
  }

  /* ---------------- V-System (owner 2026-10-22) ----------------
     One input ('vskill': KeyV / V button), three context moves —
     Tekken-ified from SFV's V-Skill / V-Trigger / V-Reversal, plus
     V-Shift on block double-tap. Names «TBD» pending user approval. */
  _startVAttack(move, state, name) {
    this.attack = move; this.attackName = name; this.hasHit = false;
    this._attackId = (this._attackId || 0) + 1;
    this._queuedNext = null;
    this.vx = 0; this._enter(state); this._attackPhase = 'startup';
    return true;
  }
  tryVSkill() {
    // Per-character unique V-Skill. V-Trigger enhances it (EX: armored).
    if (!this.canAct() || !this.onGround) return false;
    const base = vskillFor(this.char.id);
    const move = this._vtriggerT > 0 ? vtriggerEnhance(base) : base;
    if (move.kind === 'parry') this._vparryT = V.PARRY_WINDOW;
    this.addMeter(V.SKILL_SOUL_ON_USE);
    return this._startVAttack(move, 'vskill', 'vskill:' + base.id);
  }
  tryVTrigger() {
    // Full-meter install: 12s of +15% damage, chip on block, EX V-Skill.
    // Allowed from neutral or a calm block — not from blockstun (that's
    // V-Reversal's lane).
    const calmBlock = this.state === 'block' && this.stun <= 0.05;
    if (this.dead || !this.onGround) return false;
    if (!this.canAct() && !calmBlock) return false;
    if (this.meter < V.TRIGGER_COST || this._vtriggerT > 0) return false;
    this.meter = 0;
    this._vtriggerT = V.TRIGGER_DURATION;
    this._auraFlash = 1.0;
    return true;
  }
  tryVReversal() {
    // Guard-cancel counter from blockstun. Strike-invulnerable through
    // startup+active — the "get off me" that costs 50 souls.
    if (this.state !== 'block' || this.stun <= 0.05 || !this.onGround) return false;
    if (this.meter < V.REVERSAL_COST) return false;
    this.meter -= V.REVERSAL_COST;
    const move = vreversalMove();
    this.invuln = move.startup + move.active;
    return this._startVAttack(move, 'vreversal', 'vreversal');
  }
  tryVShift() {
    // Double-tap block: 0.35s invulnerable backshift. Evading an attack
    // (game.js) triggers slow-mo + the V-Shift Break window.
    if (!this.canAct() || !this.onGround) return false;
    this._enter('vshift');
    this.invuln = V.SHIFT_DURATION;
    this.dodgeDir = -this.facing; // vshift rides the dodge presentation
    this.vx = -this.facing * (V.SHIFT_BACK_DIST / V.SHIFT_DURATION);
    this._vshiftProc = false;
    return true;
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
    // T8 tables: 'none' = unbreakable, '1|2' = either punch breaks.
    if (want === 'none' || !want.split('|').includes(got)) return false;
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
    // Break window expired — the throw lands for real. Both fighters enter
    // the throw execution: attacker lifts and slams, victim is thrown.
    // (Owner playtest bug 2026-10-23: was routing through receiveHit, which
    // launched the victim across the room with no throw animation.)
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
      attacker._enterThrowExec(victim, move);
      const result = victim._enterThrownExec(attacker, move);
      return result; // 'throw' or 'ko'
    }
    if (inLock) this._enter('idle');
    return null;
  }
  /* Throw execution (Tekken): after the break window, the attacker performs
     the throw — lift (0-0.45s), slam (0.45-0.6s), recover (0.6-0.9s).
     Damage lands at the slam. The victim stays near the attacker; no launch. */
  _enterThrowExec(victim, move) {
    this.state = 'throwExec'; this.stateT = 0;
    this._throwVictim = victim; this._throwMove = move;
    this._throwHitDone = false;
    this.vx = 0; this.vz = 0; this.vy = 0;
    const want = Math.sign(victim.root.position.x - this.root.position.x) || this.facing;
    this.facing = want;
  }
  _enterThrownExec(attacker, move) {
    this.state = 'thrownExec'; this.stateT = 0;
    this._throwAttacker = attacker; this._throwMove = move;
    this.vx = 0; this.vz = 0; this.vy = 0;
    this.onGround = false; // lifted during the throw
    const want = Math.sign(attacker.root.position.x - this.root.position.x) || this.facing;
    this.facing = want;
    this.meter = Math.min(this.maxMeter, this.meter + 6); // +6 soul on taking damage
    return 'throw';
  }
  _throwSlamDamage() {
    // Damage at the slam moment, from the attacker's stored throw.
    const attacker = this._throwAttacker, move = this._throwMove;
    if (!attacker || !move || this._throwHitDone) return null;
    this._throwHitDone = true;
    let dmg = move.damage * attacker.stats.power / this.stats.defense;
    this.hp = Math.max(0, this.hp - dmg);
    if (this.hp <= 0) {
      this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
      return 'ko';
    }
    return 'throw';
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
    if (this._tryAttackFresh(name)) { this._pressBuf && this._pressBuf.clear(); return true; }
    // Tekken input buffer: a press made while still recovering / in
    // hitstun is held ~10 frames and fires on the first actionable frame.
    if (/^[1234](\+[1234])*$/.test(name) && !this.dead) {
      (this._pressBuf ||= new PressBuffer(10)).push(name, this._clock || 0);
    }
    return false;
  }
  /* Retry a buffered press once the fighter can act (called each update). */
  _drainPressBuffer() {
    if (!this._pressBuf || !this.canAct()) return;
    const name = this._pressBuf.take(this._clock || 0);
    if (!name) return;
    this._pressBuf.clear();
    this._tryAttackFresh(name);
  }
  setRageAura(on) {
    this._rageAura = !!on;
    if (this.aura && this.aura.material) this.aura.material.color.set(on ? 0xff2a1a : 0xffffff);
    if (this.auraLight) this.auraLight.color.set(on ? 0xff2a1a : 0xffffff);
  }
  setUrgeAura(on) {
    this._urgeAura = !!on;
    if (this.aura && this.aura.material && !this._rageAura) this.aura.material.color.set(on ? 0x3aa8ff : 0xffffff);
    if (this.auraLight && !this._rageAura) this.auraLight.color.set(on ? 0x3aa8ff : 0xffffff);
  }
  tryUrgeDash() {
    if (!this._urgeOn || this._urgePips < 1 || !this.canAct()) return false;
    const g = this.game;
    if (g && g.soulurge) g.soulurge.spendPip(this);
    else this._urgePips -= 1;
    this._urgeDashT = 0.45;
    this.vx = this.facing * 9;
    this._enter('dash');
    return true;
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
      if (notation === '1+2' && ctx.urgeOn && !ctx.rage) return this.tryUrgeDash();
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
    if (/^(R|RD)\./.test(notation)) this._rageUsed = true; // rage art/drive: once per round
    this.stance = null; this.stanceT = 0; this._risingT = 0;
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup'; this._prevAtkT = 0;
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
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup'; this._prevAtkT = 0;
    return true;
  }
  _enter(state) { this.state = state; this.stateT = 0; }

  /* ---------------- defense / damage ---------------- */
  isBlocking() { return this.state === 'block'; }

  receiveHit(move, attacker) {
    if (this.dead || this.invuln > 0) return 'dodge';
    // V-System: an armored V-Skill absorbs the hit outright (no damage,
    // no stun) while it isn't in recovery. game.js shows the spark.
    if (this.state === 'vskill' && this.attack && this.attack.armor &&
        this._attackPhase !== 'recovery') {
      return 'armor';
    }
    // Rage lane (T7): armored moves (rage arts, urge burst/smash) absorb the
    // hit — damage applies, but the move is never interrupted mid-swing.
    const armored = !!(this.attack && this.attack.armor && this._attackPhase !== 'recovery'
      && !move.unblockable && !move.isGrab);
    const facingAttacker = Math.sign(attacker.root.position.x - this.root.position.x) === this.facing;
    // T3 HitClassify: guarded when (guard & attack word) != 0 and the defender faces the
    // attacker. Standing guard blocks highs/mids, crouching guard blocks lows; throws and
    // unblockables carry no guard bits.
    const word = move.hitWord ?? Fighter.defaultWord(move);
    const guarded = !move.unblockable && !move.isGrab && facingAttacker && (this._guardBits() & word) !== 0;
    if (guarded) {
      // GAME OPTION / VERSUS SETUP: GUARD DAMAGE OFF = no chip at all.
      // (V-Trigger chip is part of guard damage too.)
      let chip = 0;
      if (!this.game || this.game.guardDamage !== false) {
        // FIRE force (modes lane): strikes chip through guard — chipMult on attacker stats.
        chip = move.damage * attacker.stats.power * 0.12 * (attacker.stats.chipMult || 1) / this.stats.defense;
        // V-System: V-Trigger install — EVERYTHING chips through guard.
        if (attacker._vtriggerT > 0 && !move.isGrab) {
          chip += move.damage * V.TRIGGER_CHIP_MULT * attacker.stats.power / this.stats.defense;
        }
      }
      // Soul Urge lane (T8 Heat): block chip can never kill — floor at 1 HP.
      this.hp = attacker._urgeOn ? Math.max(1, this.hp - chip) : Math.max(0, this.hp - chip);
      this.stun = (move.t8 && move.t8.blk != null) ? stunFromAdvantage(move.t8.blk, move)
        : 0.18 + move.damage * 0.01;
      this.vx = Math.sign(this.root.position.x - attacker.root.position.x) * move.knock * 0.5;
      this.meter = Math.min(this.maxMeter, this.meter + 4); // +4 soul on block
      if (this.hp <= 0) { this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || 1); return 'ko'; }
      return 'block';
    }
    let dmg = move.damage * attacker.stats.power / this.stats.defense;
    // FIGHTER DEPTH (worker 34): soul kindle — the kindled fighter takes
    // +10% damage while kindled (Tekken 7 ki charge).
    if (this.kindle) dmg *= this.kindle.damageTakenMult();
    // T3 HitDamage: counter hit when the defender is in the startup of its own attack:
    // d = e + d*12/10, e = |defender move damage| * 3/10 * 3/10 * (frames into startup / startup).
    let counter = false;
    // (V-Skill / V-Reversal startups are CH-able like any attack.)
    if ((this.state === 'attack' || this.state === 'vskill' || this.state === 'vreversal') &&
        this._attackPhase === 'startup' && this.attack && this.attack.damage > 0) {
      counter = true;
      const prog = this.attack.startup > 0 ? Math.min(1, this.stateT / this.attack.startup) : 1;
      dmg = this.attack.damage * 0.09 * prog + dmg * 1.2;
    }
    // FIGHTER DEPTH (worker 34): soul kindle — the attacker's next landed
    // hit is a guaranteed counter-hit (Tekken 7 ki charge). Consumes the
    // kindle; CH damage bump matches the T3 formula's x1.2 term.
    if (!counter && attacker.kindle && attacker.kindle.consumeOnHitLanded()) {
      counter = true;
      dmg = dmg * 1.2;
    }
    // V-System: V-Trigger install (+15% damage) and the V-Shift Break
    // window (+50%, auto counter-hit, consumed by the one attack).
    if (attacker._vtriggerT > 0 && !move.isGrab) dmg *= V.TRIGGER_DMG_MULT;
    if (attacker._vbreakT > 0 && !move.isGrab) {
      dmg *= V.BREAK_DMG_MULT; counter = true; attacker._vbreakT = 0;
    }
    // Juggle scaling: first airborne hit x0.8, later ones x0.5.
    if (!this.onGround && !move.isGrab) { dmg *= this._juggle === 0 ? 0.8 : 0.5; this._juggle++; }
    this.lastCounterHit = counter;
    this.hp = Math.max(0, this.hp - dmg);
    if (armored) {
      // Rage lane (T7): armor absorbs — damage lands, the swing continues.
      this.meter = Math.min(this.maxMeter, this.meter + 6);
      if (this.hp <= 0) {
        this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
        return 'ko';
      }
      return 'hit';
    }
    this.meter = Math.min(this.maxMeter, this.meter + 6); // +6 soul on taking damage
    const dir = Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing;
    this.vx = dir * move.knock;
    if (this.hp <= 0) { this._knockout(dir); return 'ko'; }
    if (move.isGrab || move.knock >= 6 || move.launch || (counter && move.knockdown)) {
      this.vy = move.isGrab ? 5.2 : 4.6; this.onGround = false; this.stun = 0.55; this._enter('knockdown');
    } else {
      const t8adv = move.t8 ? (counter && move.t8.ch != null ? move.t8.ch : move.t8.hit) : null;
      this.stun = t8adv != null ? stunFromAdvantage(t8adv, move)
        : 0.2 + move.damage * 0.012 + (counter ? 0.12 : 0);
      this._enter('hitstun');
    }
    this.stance = null;
    // Soft-body hit injection: dent the muscle volume at the impact point.
    if (this._softbody) {
      try {
        const hb = attacker && attacker.getHitbox ? attacker.getHitbox() : null;
        if (hb) { _v1.set(hb.x, hb.y, hb.z); this._softbody.hit(_v1, dir, move.damage || 8); }
      } catch (e) {}
    }
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
    // V-System: vskill/vreversal are attacks too. Parry-kind V-Skills
    // (noHitbox) never produce a hitbox.
    if ((this.state !== 'attack' && this.state !== 'vskill' && this.state !== 'vreversal') ||
        this._attackPhase !== 'active' || this.hasHit) return null;
    if (this.attack && this.attack.noHitbox) return null;
    const node = this._weaponBone();
    if (node) node.getWorldPosition(_v1);
    else _v1.set(this.root.position.x + this.facing * 0.8, this.root.position.y + 1.2, this.root.position.z); // no rig bone (T-pose/procedural): frame-data box
    let r = this.attackName === 'surge' ? 1.0 : 0.5;
    if (this.attack?.isGrab || this.attackName === 'grab' || this.attackName === '1+3' || this.attackName === '2+4') r = 0.95; // generous grab sphere
    r *= (this.stats.reachMult || 1); // WOOD force (modes lane): reach extends
    return { x: _v1.x, y: _v1.y, z: _v1.z, r, move: this.attack,
             reach: moveReach(this.attack, String(this.attackName || '')) * (this.stats.reachMult || 1) };
  }
  getHurtboxes() {
    if (this.invuln > 0 || this.dead) return [];
    // Throw cinematic: both locked fighters are committed, not hittable.
    if (this.state === 'thrown' || this.state === 'throwing' ||
        this.state === 'thrownExec' || this.state === 'throwExec') return [];
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
    this._clock = (this._clock || 0) + dt;
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
    // V-System timers.
    if (this._vtriggerT > 0) this._vtriggerT -= dt;
    if (this._vbreakT > 0) this._vbreakT -= dt;
    if (this._vparryT > 0) this._vparryT -= dt;
    if (this._risingT > 0) this._risingT -= dt;
    if (this.stanceT > 0) { this.stanceT -= dt; if (this.stanceT <= 0) this.stance = null; }
    if (this.onGround && this.state !== 'knockdown') this._juggle = 0;
    if (this._comboTimer > 0) { this._comboTimer -= dt; if (this._comboTimer <= 0) this.combo = 0; }
    if (this._auraFlash > 0) this._auraFlash -= dt;
    if (this._urgeDashT > 0) {
      this._urgeDashT -= dt;
      if (this.onGround && this.state === 'dash') this.vx = this.facing * 9;
      if (this._urgeDashT <= 0 && this.state === 'dash') { this._enter('idle'); this.vx = 0; }
    }

    if (opponent && this.canAct()) {
      const want = opponent.root.position.x >= this.root.position.x ? 1 : -1;
      if (want !== this.facing) this.facing = want;
      // QA 2026-10-23 targeting fix (T7 tracking): in neutral a fighter turns to
      // face the opponent in 3D, not just along x, so after a sidestep the
      // body and the next attack point at the opponent.
      this._faceYaw = Math.atan2(opponent.root.position.x - this.root.position.x,
        opponent.root.position.z - this.root.position.z);
    }

    this._tickState();
    this._drainPressBuffer();
    this._physics(dt, opponent);
    this._animate(dt);

    // Secondary systems update (after animation, before render)
    if (this._jiggle) {
      try { this._jiggle.update(dt); } catch (e) {}
    }
    // Soft-body AFTER jiggle: volume deformation rides on the posed mesh.
    if (this._softbody) {
      try { this._softbody.update(dt); } catch (e) {}
    }
    if (this._face) {
      // Face expression by state
      if (this.state === 'victory') this._face.setExpression('victory');
      else if (this.state === 'ko') this._face.setExpression('ko');
      else if (this.state === 'hitstun' || this.state === 'knockdown') this._face.setExpression('pain');
      else if (this.state === 'attack') this._face.setExpression('angry');
      else this._face.setExpression('neutral');
      this._face.update(dt, this.state);
    }
    if (this._hands) {
      // Hand pose by state: fist for attacks, open for block/parry, point for victory taunt
      let pose = 'fist';
      if (this.state === 'block') pose = 'open';
      else if (this.state === 'victory') pose = 'point';
      else if (this.state === 'attack' && this.attackName && /grab|throw/i.test(this.attackName)) pose = 'grip';
      this._hands.setPose(pose);
      this._hands.update(this.bones, dt);
    }
  }

  _tickState() {
    switch (this.state) {
      // V-System: vskill/vreversal run the same attack timing as 'attack'.
      case 'attack': case 'vskill': case 'vreversal': {
        const m = this.attack, t = this.stateT;
        // combat-core: >=3-frame active floor + swept check, so a 30 fps
        // tick can no longer step over a 1-frame active window (whiffs).
        const ph = attackPhase(m, t, this._prevAtkT ?? 0);
        this._prevAtkT = t;
        if (ph !== 'done') this._attackPhase = ph;
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
      case 'vshift':
        // V-Shift: invulnerable backshift; game.js may proc the evade.
        if (this.stateT >= V.SHIFT_DURATION) { this.vx = 0; this._enter('idle'); }
        break;
      case 'sidestep':
        if (this.stateT > 0.55) { this.vz = 0; this._enter('idle'); }
        break;
      case 'thrown':
      case 'throwing':
        // Throw-lock: game.js resolves the lock when the break window
        // (lockT) expires, so hit feedback stays in one place.
        break;
      case 'throwExec': {
        // Attacker performing the throw: lift, slam, recover (0.9s total).
        // Damage lands at the slam (t=0.55s) via the victim's _throwSlamDamage.
        if (this.stateT >= 0.9) {
          this._throwVictim = null; this._throwMove = null;
          this._enter('idle');
        }
        break;
      }
      case 'thrownExec': {
        // Victim being thrown: lifted by the attacker, then slammed down
        // in front of them. Stays near the attacker — no launch across the room.
        const t = this.stateT, attacker = this._throwAttacker;
        if (attacker) {
          const dir = Math.sign(this.root.position.x - attacker.root.position.x) || 1;
          const ax = attacker.root.position.x;
          if (t < 0.45) {
            // Lift phase: rise up in the attacker's grip
            const k = t / 0.45;
            this.root.position.y = GROUND_Y + Math.sin(k * Math.PI * 0.5) * 1.3;
            this.root.position.x = ax + dir * 0.85;
            this.root.position.z = attacker.root.position.z;
          } else if (t < 0.6) {
            // Slam phase: driven down in front of the attacker
            const k = (t - 0.45) / 0.15;
            this.root.position.y = GROUND_Y + 1.3 * (1 - k);
            this.root.position.x = ax + dir * (0.85 + k * 0.75);
            this.root.position.z = attacker.root.position.z;
            if (!this._throwHitDone && k >= 0.9) this._throwSlamDamage();
          } else {
            // On the ground, recovering
            this.root.position.y = GROUND_Y;
            this.onGround = true;
          }
        }
        if (t >= 0.9) {
          const res = this._throwHitDone ? null : this._throwSlamDamage();
          this._throwAttacker = null; this._throwMove = null;
          // KO'd by the slam: _throwSlamDamage already ran _knockout.
          if (!this.dead) {
            this.stun = 0.55;
            this._enter('knockdown');
          }
          break;
        }
        break;
      }
      case 'idle': case 'walk':
        this.state = (Math.abs(this.vx) > 0.4 && this.onGround) ? 'walk' : 'idle';
        break;
    }
  }

  _physics(dt, opponent) {
    // Throw execution: positions are driven by _tickState (lift/slam),
    // so physics must not integrate velocity or gravity here.
    const inThrowAnim = this.state === 'throwExec' || this.state === 'thrownExec';
    if (!inThrowAnim) {
      if (!this.onGround) this.vy -= 22 * dt;
    }
    if (this.onGround && this.state !== 'walk' && this.state !== 'dodge' && this.state !== 'sidestep' && !(this.state === 'attack' && this.attackName === 'grab')) {
      this.vx *= Math.pow(0.0001, dt);
      if (Math.abs(this.vx) < 0.05) this.vx = 0;
    }
    // Lateral drift decays once the sidestep ends.
    if (this.state !== 'sidestep') {
      this.vz *= Math.pow(0.0001, dt);
      if (Math.abs(this.vz) < 0.05) this.vz = 0;
      // QA 2026-10-23 targeting fix: T7 rotates the fight axis after a
      // sidestep so both fighters are back on one line. Our camera axis is
      // fixed, so a fighter in neutral drifts back to the line (z=0). Before
      // this, one sidestep left |dz| > 0.75 forever and every strike whiffed.
      if (this.canAct() && this.onGround && this.vz === 0) {
        this.root.position.z *= Math.pow(0.004, dt);
        if (Math.abs(this.root.position.z) < 0.01) this.root.position.z = 0;
      }
    }
    if (!inThrowAnim) {
      this.root.position.x += this.vx * dt;
      this.root.position.y += this.vy * dt;
      this.root.position.z += this.vz * dt;
    }
    // Sidestep range: about one body width into the background/foreground.
    this.root.position.z = Math.max(-2.4, Math.min(2.4, this.root.position.z));

    if (this.root.position.y <= GROUND_Y) {
      this.root.position.y = GROUND_Y; this.vy = 0;
      if (!this.onGround) { this.onGround = true; if (this.state === 'knockdown') this.stun = Math.max(this.stun, 0.4); }
    }
    this.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, this.root.position.x));

    // Body-vs-body pushout, T7/T8 style (owner bug 2026-10-23: cross-ups impossible).
    // Tekken pushboxes are ground collision cylinders: while airborne the box
    // shrinks and is off above the opponent's waist, so a jump arc can pass
    // over and land on the far side (facing re-resolves on landing). Ground
    // push is split between both bodies; when one is against the stage wall
    // the remaining push goes to the other body, so nobody leaves the stage.
    if (opponent) {
      const dx = this.root.position.x - opponent.root.position.x;
      const dz = this.root.position.z - opponent.root.position.z;
      const air = Math.max(this.root.position.y, opponent.root.position.y) - GROUND_Y;
      const airborne = !this.onGround || !opponent.onGround;
      // ground: 1.45 wide; airborne: 0.55 low, none once over the waist (0.85)
      const minDist = !airborne ? 1.45 : (air < 0.85 ? 0.55 : 0);
      if (minDist > 0 && Math.abs(dx) < minDist && Math.abs(dz) < 0.9) {
        // side from x, or from travel direction when perfectly stacked
        const side = dx !== 0 ? Math.sign(dx) : (Math.sign(this.vx - opponent.vx) || this.facing * -1);
        const total = minDist - Math.abs(dx);
        let a = total / 2, b = total / 2;
        const L = ARENA_LIMIT;
        const roomA = side > 0 ? L - this.root.position.x : this.root.position.x + L;
        const roomB = side > 0 ? opponent.root.position.x + L : L - opponent.root.position.x;
        if (a > roomA) { b += a - roomA; a = roomA; }
        if (b > roomB) { a += b - roomB; b = roomB; }
        this.root.position.x += side * a; opponent.root.position.x -= side * b;
      }
      // lateral separation after sidesteps (grounded only)
      // (contact fix: this used to fire at every touching distance (<1.45),
      // pushing both fighters 0.7 m off-line so strikes whiffed past the
      // body; now only when bodies are stacked after a sidestep.)
      if (!airborne && Math.abs(dz) < 0.7 && Math.abs(dx) < 0.6) {
        const zp = (0.7 - Math.abs(dz)) / 2 * (dz >= 0 ? 1 : -1);
        this.root.position.z += zp; opponent.root.position.z -= zp;
      }
      this.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, this.root.position.x));
      opponent.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, opponent.root.position.x));
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
    // 1) Facing (3D yaw toward the opponent when known; sign convention kept)
    this.lean.rotation.y = (typeof this._faceYaw === 'number') ? this._faceYaw : this.facing * Math.PI / 2;

    // 2) Which REAL T3 clip owns this state? (FROZEN-IDLE FIX 2026-10-20:
    // the bank's animated stance/walk clips existed but were NEVER played
    // — idle fell through to _stopT3() and the near-static embedded Idle,
    // whose rotation range is <=4.8 deg and whose Hips bob is pinned away
    // at load. Headless diag on the old code: t3 stance t=0 w=0 while the
    // mixer advanced the embedded Idle at w=1; bone movement over 2 s
    // measured 0.0-1.0 deg on every bone.)
    // Attacks: the resolved move's own clip, else the closest real clip of this bank
    // (_attackClipPlan, lane D 2026-10-24 — replaces the T3_ATTACK_MAP button -> light/medium/heavy map).
    const attackClipFor = () => this._attackClip(this.attack, this.attackName);
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
      case 'attack': case 'vskill': case 'vreversal': t3Wanted = attackClipFor(); break;
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

    // 4) Advance clips (writes the posed skeleton into bones). The attack clip's time is set from
    // the move clock first, so its hit frame lands on the move's active frames (lane D).
    this._applyAttackWarp();
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
      case 'attack': case 'vskill': case 'vreversal': {
        // The move's own row / closest real clip (_attackClipPlan), time-warped onto its frames.
        // V-Skill / V-Reversal ride the same attack presentation.
        const t3name = attackClipFor();
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
      case 'dodge': case 'vshift':
        // The dodge moves the fighter backwards: T3's own back-dash
        // V-Shift rides the same presentation (a fast defensive shift).
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
      case 'throwExec': {
        // Attacker performing the throw: heave back to lift (0-0.45s),
        // drive forward for the slam (0.45-0.6s), settle (0.6-0.9s).
        const t = this.stateT;
        if (t < 0.45) this._leanT.x = -0.35 * (t / 0.45); // lean back, lifting
        else if (t < 0.6) this._leanT.x = -0.35 + 0.75 * ((t - 0.45) / 0.15); // slam forward
        else this._leanT.x = 0.4 * (1 - (t - 0.6) / 0.3); // settle
        // Keep the grab clip if bound; otherwise the procedural snatch pose.
        if (this.t3actions.grab) this._playT3('grab', { loop: false });
        else this._animThrowExec(t);
        break;
      }
      case 'thrownExec': {
        // Victim being thrown: lifted, then slammed. T3 launch clip sells
        // the airborne part; the position is driven by _tickState.
        this._leanT.x = 0.25;
        if (!this._playT3Once('launch', 'thrownExec')) this._stopT3();
        break;
      }
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
    const auraOn = (this.attackName === 'surge') || this._auraFlash > 0 || this._rageAura || this._urgeAura;
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
  /* Procedural throw execution (no T3 throw clip bound): arms haul the
     victim up overhead during the lift, then drive down for the slam. */
  _animThrowExec(t) {
    const fwd = _v3.set(this.facing, 0, 0);
    this.bones.Spine2.getWorldPosition(_v1);
    let lift, push;
    if (t < 0.45) { const k = t / 0.45; lift = k; push = 0.3 + k * 0.3; }
    else if (t < 0.6) { const k = (t - 0.45) / 0.15; lift = 1 - k * 0.9; push = 0.6 + k * 0.6; }
    else { lift = 0.1; push = 1.2 * (1 - (t - 0.6) / 0.3); }
    _v2.copy(_v1).addScaledVector(fwd, push); _v2.y = _v1.y + 0.2 + lift * 0.9;
    this._ik(['RightArm', 'RightForeArm'], 'RightHand', _v2, 0.95);
    _v2.copy(_v1).addScaledVector(fwd, push * 0.92); _v2.y = _v1.y + 0.1 + lift * 0.85;
    this._ik(['LeftArm', 'LeftForeArm'], 'LeftHand', _v2, 0.95);
    this._showTrail(this.bones.RightHand, Math.min(1, lift + 0.3));
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
