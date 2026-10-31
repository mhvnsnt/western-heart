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
   GAP-FILL LANE 1 (2026-10-24, combat systems): Power Crush
   absorb (mid/high only), Screw (T7) + Tornado (T8) as the
   single once-per-combo extender, wall splat as a distinct
   state (3 hits, then drop), T8 recoverable pool from chip
   (attack-only restore, never over time), Soul Urge wiring
   completion (Burst on block, Dash as recovery cancel, 2+3
   Burst/Smash routing), item-gated moves, per-move hitbox
   lookup with honest UNMAPPED fallback. PROPRIETARY NAMES:
   NEEDS NAME for Power Crush / Screw / Tornado / wall splat /
   recoverable / item moves (owner names them); only Soul Urge
   is user-locked. Tekken names in this file are technical
   references only, never canon. Buttons: LP1/RP2/LK3/RK4.
   CORRECTION to the gap doc: no Bound state machine exists
   in this file (its "bound" hits are throw-pair / anim-bank
   binding) and no low-parry system exists either — so Screw
   was added without removing anything, and low-parry Bound
   is open follow-up work, not a preserved behavior.
   ============================================================ */
import * as THREE from 'three';
import { assets } from './assets.js';
import { getT3Clips, createT3Actions, retargetT3Clips, SOURCE_TO_BANK, T3_BANKS,
  clipStrikeProfile, clipHitWindow, bankAttackPool, attackLevelOfWord, attackClipTime, clipIsThrow, BUTTON_LIMB,
  loadT3Clips, loadT3ReactionClip, getT3ReactionPackScale, loadReactionPack, getReactionPack, getReactionClip,
  applyT7Stance } from './t3anims.js';
import { effectiveStepPlay, playableStepPlay, stepActionName, stepPlanBanksFor } from './step-plan-bank.js';
import { selectThrow, resolveThrowClips, throwBreaks, throwDamageTimeSec, throwPairDurationSec,
  escapePairFor, anchorAt, sharedFramePos, throwQuadrant, attemptRowForInput, hexSlot, bankDirOf } from './t3-throw.js';
import { TekkenBuffer, getFighterMoveset, getMovesetInfo, resolveMove, resolveMoveKey, hasStrPrefix, variantBase, throwStageTag, throwStageKeys, systemRows, systemTagOf } from './movesets.js';
import { TransformCinematic } from './transform-cinematic.js';
import { V, vskillFor, vtriggerEnhance, vreversalMove } from './v-system.js';
import { JiggleRig } from './jiggle.js';
import { SoftBody } from './softbody.js';
import { MpmTissue } from './mpm-tissue.js';
import { FaceRig } from './faceRig.js';
import { HandPoseBlender } from './handPoses.js';
import { canonRootScale } from './canon-sizing.js';
import { t8Frame, stunFromAdvantage } from './frame-tables.js';
import { hitWordFor, attackPhase, moveReach, PressBuffer,
  isPowerCrushMove, powerCrushAbsorbs, extenderKind, SCREW_SLUMP_STUN,
  TORNADO_BOUND_STUN, EXTENDER_LAND_STUN_FLOOR, WALL_SPLAT_MAX_HITS,
  WALL_SPLAT_STUN, nextWallSplatState, itemGate,
  resolvePerMoveHitbox, resolvePerMoveHurtbox } from './combat-core.js';
import { HURT_SEGMENTS, WEAPON_SEGMENTS, LIMB_RADIUS, fallbackHurts } from './hitbox.js';
import { selectReactionSlot, reactionSlotBank } from './t3-reaction-select.js';
import { soulStates } from './full-movelist.js';
import { t3ConditionHolds } from './t3-conditions.js';

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
  jin_soul: 'yoshimitsu', retsu: 'bryan', zen: 'heihachi', gyou: 'demonio', // zen 'heihachi' here is INTERIM frame-data provenance ONLY (his 639 interim rows) — his BANK is UNMAPPED (see FIGHTER_BANK), NOT Heihachi as a base.
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
  //   zen        -> UNMAPPED (owner decision 2026-10-24: Zen is NEITHER Heihachi NOR Julia — see FIGHTER_BANK note)
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
  // ZEN CONFLICT RESOLVED 2026-10-24 (owner decision, docs/decisions/2026-10-24-zen-base-decision.md):
  // Zen is NEITHER Heihachi NOR Julia. Heihachi is Diablo's base; Julia is Nightwolf's base
  // (CANON.md appendix: Julia -> NIGHTWOLF / soul ZEN). Zen's base chain is Eleven/Twelve
  // (Street Fighter, 2D concept) -> Dural (Virtua Fighter 5, 3D implementation: the closest
  // 3D thing to Eleven/Twelve) -> Zen's own canon moves on top, with X.COPY as ONE super.
  // No Dural bank exists in the repo (no game/assets/anim/vf5/, no 'dural' in SOURCE_TO_BANK)
  // and no Twelve 2D->3D conversion exists, so zen maps to null (UNMAPPED) here: bankIdFor
  // returns null and Zen falls back to embedded locomotion + procedural combat — never
  // another character's clips. When VF5 Dural motion lands, bind 'dural' here.
  const FIGHTER_BANK = {
    // zen: null = UNMAPPED (owner decision 2026-10-24). A null value is intentional:
    // hasOwnProperty('zen') is true, so bankIdFor returns null before any Heihachi/Julia
    // fallback can bind. Do NOT restore 'julia' or 'heihachi' here without a new owner decision.
    awapop: 'nina', torch: 'anna', kingtyrant: 'eddy', kai: 'eddy',
    tou: 'paul', gyou: 'hwoarang', zen: null, rave: 'lei',
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
    // 2026-10-24 (stance fix lane; owner: "too many are sharing them"):
    // these three fighters' Tekken bases have decoded T3 banks on disk,
    // but they were falling back to a shared moveset bank (docfrank) or
    // to no bank at all (tobi, buffalo-bill). Each now binds its own base's
    // bank, so its stance is distinct, not shared.
    //   docfrank    -> bosconovitch (CANON: Doc Frank base = Bosconovitch;
    //                 bank exists on disk; was incorrectly on gunjack bank)
    //   tobi        -> hwoarang (CANON: Tobi base = Hwoarang; bank exists;
    //                 was returning null — no bank, CMU fallback shared)
    //   buffalo-bill -> law (CANON: Buffalo Bill base = Marshall Law;
    //                 bank exists; was returning null — no bank, CMU fallback)
    docfrank: 'bosconovitch', tobi: 'hwoarang', 'buffalo-bill': 'law',
  };
  // 2026-10-28: Zen binds the VF5 Dural bank (T3_BANKS.dural) only in a private build — the
  // decoded VF5 motion lives in the private game-reverse-engineering repo and is copied to
  // game/assets/private/anim/vf5/dural/. Public builds keep zen UNMAPPED (null) as before.
  if (charId === 'zen' && T3_BANKS.dural) return 'dural';
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

export function getRealMove(charId, moveType, opts) {
  const tekken = LEGACY_TO_TEKKEN[moveType] || moveType;
  const res = resolveMove(charId, tekken, opts);
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
          unblockable: !!mv.unblockable,
          // T3 throw-situation rows (branch conditions 2-0x17) are the throw executions a
          // connecting grab branches into by the opponent's posture / side (moves.md SituationClassify)
          // moveset sweep 2026-10-29: a move the moveset classes as a throw (move_class 'throw',
          // e.g. pantera d/f+1+2) is a grab too; before, it played as a strike (knockdown, no
          // thrower/victim exec clips).
          isGrab: !!mv.isGrab || mv.move_class === 'throw' || (mv.t3_condition >= 2 && mv.t3_condition <= 0x17),
          tekkenInput: tekken, moveKey: key,
          system: systemTagOf(mv.input), // KOF XV system row (fighter.js KOF)
          // T3 branch-row condition (t3-conditions.js): the row only fires while it holds
          t3Condition: mv.t3_condition ?? null,
          t3row: mv.t3_row, t3source: mv.t3_source || (mv.t3_row != null ? ms.t3_source : null), moveName: mv.name,
          animBank: anim ? anim.bank : null, animRow: anim ? anim.row : null,
          // decoded T3 attack word (high 0x412 / mid 0x217 / low 0x10F / s.mid 0x31F / unblockable 0x607)
          // T7 '[mid throw]' tackles are blockable mids that are NOT grabs: the
          // decoded throw word (0x800, no posture bits) would make them whiff
          // every posture, so they take the mid word.
          // SWEEP 2026-10-29: the same applies to ANY non-grab strike whose
          // decoded word carries no posture bits (T3 cross-character rows such
          // as jin_soul b+3+4 from yoshimitsu r194 = 0x800): it could never
          // connect, so it takes the mid word too.
          hitWord: (!mv.isGrab && ms.hit_words && ms.hit_words[key] != null && !(ms.hit_words[key] & 7)) ? 0x217
            : (!mv.isGrab && /\[mid throw\]/.test(mv.note || '') && !((ms.hit_words && ms.hit_words[key]) & 7)) ? 0x217
            : (ms.hit_words && ms.hit_words[key] != null) ? ms.hit_words[key] : hitWordFor(mv),
          hitLevel: mv.hit_level,
          // T3 situation follow-ups engage on contact: reach covers own hit + pushback.
          reach: (Number(mv.reach) > 0) ? mv.reach : (mv.t3_condition >= 2 && mv.t3_condition <= 0x17) ? 2.0 : mv.reach,
          stanceAfter: ms.stance_after ? ms.stance_after[key] : undefined,
          launch: !!mv.launch, knockdown: !!mv.knockdown,
          // T8 launcher frame advantage on hit, e.g. '+34a (+24)' (airborne): sets the juggle airtime
          launchAdv: (() => { const m = /\+(\d+)a/.exec(String(mv.on_hit || '')); return m ? +m[1] : null; })(),
          armor: !!mv.armor,
          rageArt: !!mv.rageArt, rageDrive: !!mv.rageDrive,
          urgeEngager: !!mv.urgeEngager,
          urgeBurst: !!mv.urgeBurst, urgeSmash: !!mv.urgeSmash,
          // GAP-FILL LANE 1 (2026-10-24): combat-system flags, read
          // from the move record only — never invented here. No WH
          // moveset carries these flags yet (moveset lane owns the
          // data); until it does, every move reads UNMAPPED/false
          // and the engine falls back to the pre-existing behavior.
          // PROPRIETARY NAMES: NEEDS NAME (owner names them).
          powerCrush: isPowerCrushMove(mv),
          screw: !!mv.screw || !!mv.tailspin || !!(mv.t7 && mv.t7.screw),
          tornado: !!mv.tornado || !!(mv.t8 && mv.t8.tornado),
          requiresItem: mv.requiresItem || mv.requiredItem || mv.item || null,
          itemMove: !!mv.itemMove || !!(mv.requiresItem || mv.requiredItem || mv.item),
          hitbox: mv.hitbox ?? (mv.t7 && mv.t7.hitbox) ?? (mv.t8 && mv.t8.hitbox) ?? null,
          hurtbox: mv.hurtbox ?? (mv.t7 && mv.t7.hurtbox) ?? (mv.t8 && mv.t8.hurtbox) ?? null,
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
const JUGGLE_PEAK = 1.2; // m: launcher pop height (juggle airtime comes from the move's frame data)
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

/* ============================================================
   ROOT MOTION (2026-10-24) — why attacks were stuck in place.
   The decoded T3 clips DO carry travel: every clip's raw root_t
   (t3anims.js jsonToClip / decodePackRow, in metres, canonical
   source frame: forward = +Z, character-left = +X, already turned
   180 deg for the banks baked facing -Z) is the root bone's
   trajectory. But the game never read it horizontally:
   t3anims.js retargetT3Clips keeps ONLY the vertical (y) part of
   root_t for the Hips.position track, and fighter.js _physics
   decays vx to ~0 during attacks, so every attack played in place.
   The only attack travel before this was the authored grab lunge
   (vx = facing * 2.5 in _tryAttackFresh) and frame-data reach
   (combat-core.js moveReach), which decides CONTACT, not position.
   rootMotionSample returns a clip's horizontal displacement from
   its own frame 0 at clip time t (seconds), linearly interpolated
   between the decoded frames (fps, usually 30). Vertical (y) is
   deliberately NOT returned: hip height already rides the retargeted
   Hips.position track, and gravity/vy owns root.position.y — applying
   y here would double-apply it and sink/lift the fighter through
   the floor. Pure: no THREE, no game state, unit-testable.
   Mapping to game axes (see _rootMotionApply): forward (source +Z)
   -> world x * facing; lateral (source +X, character-left) -> world
   z * -facing (character-left is world -z when facing +x, as the
   sidestep comment in _animate already records).
   Whiff vs hit is irrelevant here on purpose: this is animation
   time, not hit detection — a whiffed lunge travels exactly as far
   as a connected one, as in Tekken. */
export function rootMotionSample(root_t, fps, t) {
  if (!root_t || root_t.length < 2 || !(fps > 0) || !Number.isFinite(t)) return { fwd: 0, lat: 0 };
  const n = root_t.length;
  const f = Math.max(0, Math.min(n - 1, t * fps));
  const i = Math.floor(f), k = Math.min(n - 1, i + 1), a = f - i;
  const r0 = root_t[0], ra = root_t[i], rb = root_t[k];
  // Displacement from frame 0 (ra/rb are absolute source positions).
  const fwd = ((ra[2] + (rb[2] - ra[2]) * a) - r0[2]);
  const lat = ((ra[0] + (rb[0] - ra[0]) * a) - r0[0]);
  return { fwd: Number.isFinite(fwd) ? fwd : 0, lat: Number.isFinite(lat) ? lat : 0 };
}

/* KOF XV system actions (Dream Cancel wiki, KOF XV Defense / Offense / Meters and Gauges).
   WH gauge = 100 souls; one KOF power stock = 25 souls (XV first character holds 3-5 stocks). */
export const KOF = {
  STOCK: 25,
  GC_COST: 1,            // guard cancel roll (GCAB) and blowback (GCCD): 1 stock, blockstun only
  MAX_COST: 2,           // MAX Mode (raw): 2 stocks
  MAX_DMG: 1.25,         // +25% damage on normals, throws, command and special moves
  MAX_SECONDS: 10,       // APPROXIMATE: XV's MAX gauge is 1000 pts; its drain rate is not public
  ROLL_INVULN: 24 / 60,  // rolls last 33f, invulnerable 1-24 (strikes), 9f recovery
  ROLL_TOTAL: 33 / 60,
  TAUNT_LOCK: 49 / 60,   // taunt cannot be cancelled for 49f; no gauge effect in XV
  ESCAPE_WINDOW: 11 / 60 // normal throw break: first 11 frames of the throw
};
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

    // vitals — Tekken 7 round health: 180 (owner order 2026-10-29).
    // Move damage values are unchanged; the HUD bars draw hp/maxHp as a
    // percentage (game/js/main.js), so each hit now takes a smaller,
    // Tekken-7-sized slice of the bar (~10-15 clean hits plus combos).
    this.maxHp = 180; this.hp = 180;
    this.meter = 0; this.maxMeter = 100; // NINE-SOUL METER
    // SOUL-SPIRIT TOGGLE (worker 83, owner directive 2026-10-22 ~23:02 CDT):
    // a vessel-matched soul feeds its vessel faster meter gain.
    this.soulMeterMult = charData.soulMeterMult || 1;

    // physics
    this.vx = 0; this.vy = 0; this.onGround = true;
    // Stream 6: lateral (z-axis) velocity for sidesteps / sidewalk.
    this.vz = 0; this.ssDir = 0;

    // state machine
    this.state = 'idle'; this.stateT = 0;
    this.attack = null; this.attackName = null; this._attackPhase = 'startup';
    this._rmPrev = null; // root-motion cursor for the current attack (see _rootMotionApply)
    this.hasHit = false; this._prevHitPoint = null; this._reactionSel = null; this._reactLoading = null; this._reactChainDepth = 0; this.stun = 0; this.invuln = 0; this.dodgeDir = 0;
    this.dead = false; this.combo = 0; this._comboTimer = 0;
    this.tekken = new TekkenBuffer(charData.id); // strings / motion specials / directionals
    // Tekken states (2026-10-21, decoded T3 rules — see _guardBits/canBeHitBy):
    // stance = character stance code after a move whose source notes say "Transition to X"
    // (moveset stance_after), rising = while-standing window after leaving a crouch,
    // stick = facing-relative direction (guard + posture), juggle = hits taken airborne.
    this.stance = null; this.stanceT = 0; this._risingT = 0; this._stickDir = 'n';
    this._juggle = 0; this._rageUsed = false; this._queuedNext = null; this._queuedAfter = null;
    this._stepChain = null; // whole-string step chain (Batch 1 step plans): {key, steps, idx}
    this._stringGraceUntil = 0; // wall-clock end of the post-move string window (see _tryAttackFresh)
    this._rageOn = false;
    this._urgeOn = false; this._urgeUsed = false; this._urgeT = 0; this._urgePips = 0;
    this._urgeDashT = 0;

    // GAP-FILL LANE 1 (2026-10-24): combo-extender / wall / recoverable
    // / item state. _extenderUsed is the single once-per-combo slot
    // shared by Screw (T7) and Tornado (T8); it clears when the
    // victim recovers to neutral (see update()), never mid-combo.
    // PROPRIETARY NAMES: NEEDS NAME (owner names them).
    this._extenderUsed = false; this._extenderKind = null;
    this._inScrew = false; this._inTornado = false;
    this._wallSplatHits = 0; this._wallSplatArmed = false;
    // T8 recoverable pool (white gauge): chip damage taken lands
    // here instead of vanishing; landing hits / forcing blocks
    // heals it back (see _recoverOnAttack). Per-round: cleared by
    // SoulUrge.resetRound() alongside the per-round urge gauge.
    this._recoverable = 0;
    // Item-move loadout: equipped customization item ids, set by
    // the customization lane via setEquippedItems(). Empty = no
    // item-gated move can fire (itemGate in combat-core.js).
    this.equippedItems = [];

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

    /* ---- HEART AND MIND WITHIN: 3D brawler mode (worker 20, 2026-10-22) ----
       When brawler=true, the fighter runs in free-3D: `yaw` (world-space
       radians) drives the visual facing, movement uses vx+vz, and
       knockback/guard resolve in 3D. Versus logic is untouched when
       brawler=false. */
    this.brawler = false;
    this.yaw = 0;
    // Soul Surge form: the Devil Within devil-form analog. Timed powered
    // state (stat boosts + aura), entered at full meter via the transform
    // input in brawler mode; drains meter while active.
    this.surgeForm = false;
    this._surgeT = 0;
    this._surgeBaseStats = null;

    // MID-MATCH TRANSFORMATION (Roshi-style, owner 2026-10-19).
    // Fighters with charData.transform (single) or charData.forms (multi-form
    // map keyed by current model key) swap models mid-fight.
    // Single: { targetModel, powerMult, speedMult, defenseMult, bodyScale }.
    // Multi: { 'model-key': { target, label, powerMult, speedMult, defenseMult,
    //   bodyScale, moveset }, 'model-key': { up: {...}, down: {...} } }.
    this._forms = null;
    this.formKey = charData.model;
    this._canonSizeTick = 0;
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
      this.char.colorize ? (this.char.tintStrength ?? 0.3) : 0,
      this.char.eyeGlow // per-attire emissive eyes (owner 2026-10-22; attires.js slot config)
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
    // Soft-body muscle volume (tissue backend lane, 2026-10-23): Jolt XPBD
    // torso volume for muscle deformation on hit + volume-grounded jiggle.
    // Same pattern as jiggle: inert until the backend is ready, every call
    // guarded, never crashes the fight. char.softbody === false opts out.
    //
    // NEXTGEN-2026-10-23 tissue backends (see
    // docs/research/SOFTBODY-NEXTGEN-2026-10-23.md):
    //   'jolt'  (default) — Jolt XPBD lattice (game/js/softbody.js)
    //   'mpm'             — CPU MPM-lite, SurRoL-inspired (game/js/mpm-tissue.js)
    //   'femfx'           — FEMFX WASM w/ Jolt fallback (game/js/femfx-adapter.js)
    // Pick with window.WH_PHYSICS_BACKEND or per-character
    // char.softbodyBackend. All three share the integration contract and
    // the 'wh_softbody_v1' quality store, so switching never changes the
    // visual mapping — only the solver.
    this._softbody = null;
    const softSpec = SoftBody.anatomyFor(this.char);
    if (softSpec) {
      const backend = (typeof window !== 'undefined' && window.WH_PHYSICS_BACKEND)
        || this.char.softbodyBackend || 'jolt';
      this.root.traverse(o => {
        if (!this._softbody && o.isSkinnedMesh) {
          try {
            if (backend === 'mpm') {
              this._softbody = MpmTissue.fromMesh(o, softSpec);
            } else if (backend === 'femfx') {
              // FEMFX WASM is async; the adapter falls back to Jolt when
              // the module is missing. Import lazily so the default path
              // pays zero cost.
              import('./femfx-adapter.js').then((m) => {
                if (!this._softbody && !this._disposed) {
                  try { this._softbody = m.FemfxBody.fromMesh(o, softSpec); } catch (e) {}
                }
              }).catch(() => {});
            } else {
              this._softbody = SoftBody.fromMesh(o, softSpec);
            }
          } catch (e) {}
        }
      });
    }
    // Face rig: morph driver + blink timer
    this._face = FaceRig.attach(this.root);
    // Hand poses: fist default, blended per state
    this._hands = new HandPoseBlender();
  }

  /* ---------------- combat intents ---------------- */
  _hasGroundMoves(p = 'FUFT') {
    if (this._groundMovesFor !== this._movesetId) { this._groundMovesFor = this._movesetId; this._groundMoves = {}; }
    if (this._groundMoves[p] == null) {
      this._groundMoves[p] = ['3', '4', '3,3', '1', '2', '1+2', '3+4'].some((b) => !!resolveMoveKey(this._movesetId, p + '.' + b));
    }
    return this._groundMoves[p];
  }
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

  /* SOUL SURGE FORM — the Devil Within devil-form analog for the brawler.
     Full nine-soul meter + transform input: a TIMED powered state with no
     model swap — the fighter keeps their own moveset and model, boosted
     stats, and their surge aura burning for the duration. Any WH character
     can surge (character select, not forced Jin). Manual re-trigger ends it
     early; the meter drain ends it when empty. */
  startSurgeForm() {
    if (this.surgeForm) { this.endSurgeForm(); return true; }
    if (this.meter < this.maxMeter || !this.canAct()) return false;
    this.surgeForm = true;
    this._surgeT = 25; // seconds of devil time
    this._surgeBaseStats = { ...this.stats };
    this.stats = {
      ...this.stats,
      power: this.stats.power * 1.45,
      speed: Math.min(3.8, this.stats.speed * 1.15),
      defense: this.stats.defense * 1.2,
    };
    this._auraFlash = 1.0;
    return true;
  }
  endSurgeForm() {
    if (!this.surgeForm) return;
    this.surgeForm = false;
    this._surgeT = 0;
    if (this._surgeBaseStats) { this.stats = this._surgeBaseStats; this._surgeBaseStats = null; }
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
        this.char.colorize ? (this.char.tintStrength ?? 0.3) : 0, // TINT FIX: real texture colors unless explicitly colorized
        this.char.eyeGlow // per-attire emissive eyes ride along on transforms (owner 2026-10-22)
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
    applyT7Stance(this.char.id, bank, clips, model, THREE, modelKey); // real T7 stance where baked (t3anims.js T7_STANCES)
    this.t3actions = createT3Actions(this.mixer, clips, THREE);
    this._stepBankClips = {}; // per-step-bank source clips (see _attackClip)
    // Reaction pack prefetch (hit-reaction lane): the JSON arrives
    // in the background so the first hit's slot is usually decoded
    // already; decoding itself stays on demand, one slot at a time.
    try { loadReactionPack(THREE, bank); } catch (e) {}
    // Per-step-bank preload (torch, 2026-10-25): a fighter whose step
    // plans name another bank (torch plans name jin beside the bound
    // anna) starts loading that bank now, fire-and-forget, so its
    // override steps are cached by first use. Until a bank is cached,
    // its steps fail safe to UNMAPPED (playableStepPlay) — they never
    // play a bound-bank clip of the same number while loading.
    try {
      const msB = getFighterMoveset(movesetId);
      for (const b of stepPlanBanksFor(msB, bank)) {
        const pre = getT3Clips(b);
        if (pre) { (this._stepBankClips || (this._stepBankClips = {}))[b] = pre; }
        else {
          const pr = loadT3Clips(THREE, b);
          if (pr && pr.then) pr.then((cl) => { if (cl) (this._stepBankClips || (this._stepBankClips = {}))[b] = cl; }).catch(() => {});
          else if (pr && pr.catch) pr.catch(() => {});
        }
      }
    } catch (e) {}
    // Move rows retarget lazily on first use (same captured rest pose).
    // dir is the reactions.json banks key (the T3_BANKS folder name).
    this._t3 = { bank, clips: t3clips, model, modelKey, dir: bankDirOf(T3_BANKS[bank]) };
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
  /* Batch 1 step plan (2026-10-24, docs/movesets/BATCH1-STEP-PLANS-2026-10-24.md):
     a string move carrying a moveset string_step_plans entry plays per-STEP rows,
     never one row for the whole string. A step plays its row when it has an
     EFFECTIVE play (step-plan-bank.js effectiveStepPlay): a verified step
     plays its row, and a BANK-BLOCKED review step (bank_verified_row +
     its own bank + a BANK-BLOCKED reason) plays that row FROM ITS OWN
     BANK — the per-step-bank rule (torch, 2026-10-25). Any other
     review/unmapped step plays NO bank row (null plan -> the existing
     procedural fallback in _animate) and is flagged in plan.unmapped —
     never a donor, match, or generic row. This branch runs BEFORE the
     own/notation/anim/donor/match/generic tiers, so a planned string
     can never silently donor-fall-back. A step whose play bank's clips
     are not cached (override bank still loading, or no such row in
     that bank) also plays NO row — UNMAPPED, never the bound bank's
     clip of the same number. Bound-bank steps keep the #1096 action
     name 'row:<row>' exactly; override steps use 'row:<bank>:<row>'
     so they can never collide with a bound-bank action of the same
     number on this fighter's mixer. Whole-string firing drives steps
     through _stepChain (see _tryAttackFresh): while a chain is active,
     the current prefix move resolves to its plan step row. The
     per-press (_pressV2) path uses the LAST step: the clip fired on
     the final press must be the final step's clip, which is what the
     string move's own row already meant for T3-generated moves. No
     blend is added here: pose continuity between steps is UNPROVEN,
     and a blend ships only if play shows a snap. */
  _resolveStepPlan(move, attackName, ms) {
    if (!ms || !ms.string_step_plans || !ms.string_step_plans.plans) return null;
    const plans = ms.string_step_plans.plans;
    const bound = this._t3 && this._t3.bank;
    // Clip existence is checked in the PLAY bank's own cached clips:
    // the bound bank's clips for bound steps; for an override step,
    // THIS FIGHTER's per-step-bank cache (_stepBankClips, filled by
    // the _bindT3 preload) — never the process-global bank cache, so
    // one fighter's loaded bank can never make another fighter's
    // BANK-BLOCKED step "playable" with a namespaced action name the
    // bound bank's clip map cannot resolve. A bank this fighter has
    // not preloaded fails safe here: the step is UNMAPPED.
    const hasClip = (bank, row) => {
      const c = (bank === bound) ? (this._t3 && this._t3.clips)
        : (this._stepBankClips && this._stepBankClips[bank]);
      return !!(c && c['row:' + row]);
    };
    const resolve = (step, why) => {
      const play = playableStepPlay(step, bound, hasClip);
      return { playBank: play ? play.bank : (step && step.bank) || bound, playRow: play ? play.row : null,
        playName: play ? stepActionName(play, bound) : null, why };
    };
    // Unmapped means "plays no row for this fighter right now": the
    // same playability gate playback uses, so a BANK-BLOCKED step
    // whose bank this fighter has not cached is reported unmapped
    // (the step-plan contract), not silently dropped from the list.
    const unmappedFor = (steps) => steps.filter(s => !playableStepPlay(s, bound, hasClip)).map(s => s.prefix);
    // Chain-active step: the prefix currently playing in a whole-string chain.
    const ch = this._stepChain;
    if (ch && ch.steps && ch.idx < ch.steps.length && move && move.moveKey === ch.steps[ch.idx].prefix) {
      const st = ch.steps[ch.idx];
      const r = resolve(st, `step-plan chain step ${ch.idx + 1}/${ch.steps.length} (${st.prefix})`);
      return { steps: ch.steps, unmapped: unmappedFor(ch.steps),
        playName: r.playName, playBank: r.playBank, playRow: r.playRow, why: r.why };
    }
    const key = (move && move.moveKey) || attackName;
    const plan = key && plans[key];
    if (!plan || !Array.isArray(plan.steps) || plan.steps.length < 2) return null;
    const last = plan.steps[plan.steps.length - 1];
    const r = resolve(last, `step-plan last step (${last.prefix})`);
    return { steps: plan.steps, unmapped: unmappedFor(plan.steps),
      playName: r.playName, playBank: r.playBank, playRow: r.playRow, why: r.why };
  }
  _attackClipPlan(move, attackName) {
    if (!this._t3 || !this._t3.clips) return null;
    const { bank, clips } = this._t3;
    const ms = getFighterMoveset(this._movesetId);
    const raw = move && move.moveKey && ms && ms.moves ? ms.moves[move.moveKey] : null;
    const sp = this._resolveStepPlan(move, attackName, ms);
    if (sp) {
      const limb0 = Fighter.attackLimb(move, attackName);
      const level0 = Fighter.attackLevel(move, raw);
      const grab0 = !!(move && move.isGrab) || /^(grab|1\+3|2\+4)$/.test(String(attackName || '')) || level0 === 't';
      // The step's source clip lives in its PLAY bank, never assumed
      // to be the bound bank: an override step's 'row:<bank>:<row>'
      // action name is not a bound-bank clip name, and the bound
      // bank's row of the same number must never stand in for it.
      const srcClips = (sp.playBank === bank) ? clips : getT3Clips(sp.playBank);
      const src0 = (sp.playName && sp.playRow != null && srcClips) ? srcClips['row:' + sp.playRow] : null;
      if (!sp.playName || !src0) {
        if (sp.unmapped.length) console.log(`[WH-STEP-PLAN] ${this._movesetId} ${move && move.moveKey}: UNMAPPED steps [${sp.unmapped.join(', ')}] — no bank row played, never donor fallback`);
        else if (sp.playBank !== bank) console.log(`[WH-STEP-PLAN] ${this._movesetId} ${move && move.moveKey}: override bank '${sp.playBank}' row ${sp.playRow} unavailable — no bank row played, never bound-bank fallback`);
        return { kind: 'step-plan', name: null, steps: sp.steps, unmapped: sp.unmapped, limb: limb0, level: level0, grab: grab0, timing: null, rejected: [], stepBank: sp.playBank, stepRow: sp.playRow };
      }
      // Timing for the step row, same rule as the single-row tail below:
      // the row's hit window placed on the move's active frames. The
      // hit window is read from the PLAY bank (its decoded frames),
      // not the bound bank's.
      const S0 = move && Number.isFinite(move.startup) ? move.startup : 0;
      const A0 = move && Number.isFinite(move.active) ? move.active : 0;
      const R0 = move && Number.isFinite(move.recovery) ? move.recovery : 0;
      let timing0 = null;
      if (src0 && S0 + A0 + R0 > 0.05) {
        const w0 = clipHitWindow(sp.playBank, src0, limb0);
        const D0 = src0.duration;
        const t0 = w0 ? Math.min(w0.t0, D0) : D0 * S0 / (S0 + A0 + R0);
        const t1 = w0 ? Math.min(Math.max(w0.t1, t0), D0) : D0 * (S0 + A0) / (S0 + A0 + R0);
        timing0 = { S: S0, A: A0, R: R0, t0, t1, D: D0, src: w0 ? w0.src : 'proportional' };
      }
      return { kind: 'step-plan', name: sp.playName, why: sp.why, steps: sp.steps, unmapped: sp.unmapped, limb: limb0, level: level0, grab: grab0, timing: timing0, rejected: [], stepBank: sp.playBank, stepRow: sp.playRow };
    }
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
      if (plan.stepBank && plan.stepBank !== this._t3.bank && plan.stepRow != null) {
        // Per-step-bank action: retarget the override bank's own
        // 'row:<row>' source clip, then clone + rename it to the
        // namespaced action name. The clone keeps the retarget cache
        // untouched, and the namespace keeps this action from ever
        // colliding with the bound bank's 'row:<row>' action.
        const srcClips = getT3Clips(plan.stepBank);
        const srcName = 'row:' + plan.stepRow;
        const rc = srcClips && retargetT3Clips(srcClips, plan.stepBank, this._t3.model, THREE, this._t3.modelKey, [srcName]);
        if (rc && rc[srcName]) {
          const c = rc[srcName].clone ? rc[srcName].clone() : rc[srcName];
          c.name = name;
          Object.assign(this.t3actions, createT3Actions(this.mixer, { [name]: c }, THREE));
          (this._stepBankClips || (this._stepBankClips = {}))[plan.stepBank] = srcClips;
        }
      } else {
        const rc = retargetT3Clips(this._t3.clips, this._t3.bank, this._t3.model, THREE, this._t3.modelKey, [name]);
        if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
      }
    }
    if (name && !this.t3actions[name]) name = null;
    this._atkPlan = { id: this._attackId, move, name, kind: plan && plan.kind, why: plan && plan.why,
      limb: plan && plan.limb, timing: plan && plan.timing, rejected: plan && plan.rejected,
      steps: plan && plan.steps, unmapped: plan && plan.unmapped,
      stepBank: plan && plan.stepBank, stepRow: plan && plan.stepRow };
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

  /* ROOT MOTION application (2026-10-24). Runs from _physics, once per
     frame, during attack / vskill / vreversal ONLY — never during block,
     sidestep, dodge, jump, throw execution, hitstun or knockdown, whose
     positions are already driven (procedural vx/vz, gravity, or the
     throw lift/slam in _tickState). The clip is the one _attackClipPlan
     already chose for this attack (own row, notation, donor, match —
     never another character's), read from this._t3.clips, the SOURCE
     clips that still carry userData.raw.root_t (the retargeted
     t3actions copies drop raw, so they cannot be used here).
     Clip time follows the SAME warp as the visible animation
     (_applyAttackWarp: attackClipTime(plan.timing, stateT)), so the
     body arrives exactly when the animated limbs do; without a timing
     (tiny/degenerate move) it follows the action's own time. The
     displacement is applied INCREMENTALLY (this frame's sample minus
     the previous frame's), so a clip that steps forward and settles
     back (e.g. a dash row peaking mid-clip) moves the fighter back
     too, and a string's next hit starts from where the last hit left
     the fighter — never a snap-back to the move's start, never a
     double-count. facing is frozen during attacks (update() only
     re-faces when canAct()), so the facing captured per frame is the
     attack's facing throughout.
     SCOPE GUARDS (no guessing, per docs/RULES_NO_GUESSING):
     - Row clips only (plan.name 'row:*'): decoded move rows whose
       travel IS the move's travel. Generic light/medium/heavy/grab
       fallbacks are excluded — light/medium travel 0, but heavy/grab
       are the row-230 throw-execution clip (2.63 m forward), whose
       travel belongs to throwExec, not to an attack attempt. A move
       with no row clip and no raw root_t gets NO root motion (today's
       in-place behaviour), marked UNMAPPED in docs — never an
       invented distance.
     - Horizontal only (see rootMotionSample): y stays with gravity
       and the retargeted hip-height track.
     - No hit dependence: hasHit / hit detection are never read. */
  _rootMotionApply() {
    const attacking = this.state === 'attack' || this.state === 'vskill' || this.state === 'vreversal';
    if (!attacking) { this._rmPrev = null; return; }
    const p = this._atkPlan;
    if (!p || p.id !== this._attackId || !p.name || !String(p.name).startsWith('row:')) { this._rmPrev = null; return; }
    // T3 throw-situation rows (conditions 2-0x17) are throw executions: like the row-230
    // clip, their travel positions the thrown pair and belongs to the throw, not the attempt.
    const tc = this.attack && this.attack.t3Condition;
    if (tc >= 2 && tc <= 0x17) { this._rmPrev = null; return; }
    // Root motion reads the PLAY bank's source clip: an override step's
    // travel is its own bank's row travel, never the bound bank's row.
    let clip = null;
    if (p.stepBank && this._t3 && p.stepBank !== this._t3.bank && p.stepRow != null) {
      const oc = (this._stepBankClips && this._stepBankClips[p.stepBank]) || getT3Clips(p.stepBank);
      clip = oc ? oc['row:' + p.stepRow] : null;
    } else clip = this._t3 && this._t3.clips ? this._t3.clips[p.name] : null;
    const raw = clip && clip.userData && clip.userData.raw;
    const rt = raw && raw.root_t;
    if (!rt || rt.length < 2) { this._rmPrev = null; return; }
    let clipTime = null;
    if (p.timing) clipTime = attackClipTime(p.timing, this.stateT);
    else { const a = this.t3actions && this.t3actions[p.name]; if (a) clipTime = a.time; }
    if (!Number.isFinite(clipTime)) { this._rmPrev = null; return; }
    const cur = rootMotionSample(rt, raw.fps || 30, clipTime);
    let prev = this._rmPrev;
    if (!prev || prev.id !== this._attackId || prev.name !== p.name) {
      // First frame this attack's plan is visible (_animate builds the
      // plan after _physics on frame 1): anchor on the clip's frame 0
      // and apply the travel so far in this same call, so nothing is lost.
      prev = { id: this._attackId, name: p.name, ...rootMotionSample(rt, raw.fps || 30, 0) }; prev.lat0 = prev.lat; prev.fwd0 = prev.fwd;
    }
    // LATERAL CLAMP (moveset sweep 2026-10-28): some decoded T3 rows carry a metre-scale
    // sideways root track (bad frame-0 anchor in the source), which threw the attacker
    // off the fight line (|dz| > 0.75) so the strike whiffed every time. Tekken attacks
    // drift sideways well under 0.5 m (Beast Elbow ~0.40 m); cap the total lateral travel per attack inside the 0.75 m reach band.
    const LAT_MAX = 0.45, cl = (v) => Math.max(-LAT_MAX, Math.min(LAT_MAX, v));
    cur.lat = cl(cur.lat - (prev.lat0 ?? prev.lat)) + (prev.lat0 ?? prev.lat);
    // BACKWARD CLAMP (moveset sweep 2026-10-29): donor rows retargeted from another bank
    // (e.g. lili 2 on xiaoyu@silvertongue) can carry a backward root track that slid the
    // attacker 0.75 m away during startup, so a point-blank jab whiffed. Cap total
    // backward travel per attack; forward travel (lunges) is untouched.
    const BACK_MAX = 0.3, f0 = prev.fwd0 ?? prev.fwd;
    cur.fwd = Math.max(f0 - BACK_MAX, cur.fwd);
    const df = cur.fwd - prev.fwd, dl = cur.lat - prev.lat;
    if (df || dl) {
      this.root.position.x += this.facing * df;   // source forward (+Z) -> facing direction
      this.root.position.z += -this.facing * dl;  // source left (+X) -> world -z when facing +x
    }
    this._rmPrev = { id: this._attackId, name: p.name, fwd: cur.fwd, lat: cur.lat, lat0: prev.lat0 ?? prev.lat, fwd0: prev.fwd0 ?? prev.fwd };
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
  setStick(dir) { this._stickDir = dir || 'n'; this._dirHoldUpgrade(); }
  /* Held direction ending ('SS.2,U' vs 'SS.2:u', TekkenDocs: capital = hold): a direction
     follow-up resolves to the tapped spelling first; still held 6f later it becomes the held row. */
  _dirHoldUpgrade() {
    const dq = this._dirFollowQ; if (!dq || dq.held || this._stickDir !== dq.d) return;
    if ((this._clock || 0) - dq.t < 0.08) return;
    const D = dq.d.toUpperCase(); if (D === dq.d || dq.c.endsWith(D)) return;
    const up = [',', '~', ':'].map((s) => `${dq.b}${s}${D}`).find((k) => resolveMoveKey(this._movesetId, k));
    dq.held = true; if (!up) return;
    const q = this._queuedAfter && this._queuedAfter.length ? this._queuedAfter : null;
    if ((q ? q[q.length - 1] : this._queuedNext) !== dq.c) {
      // already started: swap to the held row while still in its first frames
      if (this.state === 'attack' && this.attackName === dq.c && this.stateT < 0.15) { this.attack = null; this.attackName = null; if (this._fireNotation(up)) dq.c = up; }
      return; }
    if (q) q[q.length - 1] = up; else this._queuedNext = up; dq.c = up;
  }

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
  // Where this fighter stands relative to the opponent's facing: 'L' / 'R' (their left/right
  // side, well off their line in z — source left maps to world -z when facing +x), 'B' (behind them),
  // null in front.
  _foeFlank() {
    const o = this._opp;
    if (!o || !o.root || !this.root) return null;
    // a sidestep keeps its SS. moves; a foe in a hit reaction is not set up for a side/back throw
    if (this.state === 'sidestep' || /hit|stun|knock|launch|juggle|air|down|thrown/i.test(o.state || '')) return null;
    const dx = this.root.position.x - o.root.position.x, dz = this.root.position.z - o.root.position.z;
    // facing is ±x only, and grounded bodies keep 1.45 m of x apart while |dz| < 0.9, so a
    // sidestep that ends 0.6 m+ off the opponent's line (at least 0.4 of the x gap) is at their side
    if (Math.abs(dz) >= 0.6 && Math.abs(dz) >= 0.4 * Math.abs(dx)) return dz * -(o.facing || 1) > 0 ? 'L' : 'R';
    if (dx * (o.facing || 1) < 0) return 'B';
    return null;
  }

  _inputCtx() {
    const st = this.stance;
    return {
      stance: st && st !== 'BT' && st !== 'FC' && st !== 'SS' ? st : null,
      backturned: st === 'BT',
      sidestep: this.state === 'sidestep',
      crouching: this.state === 'crouch' || st === 'FC',
      rising: this._risingT > 0,
      airborne: !this.onGround, // Tekken jump attacks resolve from AIR. while this holds
      rage: !this._rageUsed && this.hp > 0 && this.hp <= this.maxHp * 0.25,
      urgeOn: !!this._urgeOn,
      urgeAvailable: !this._urgeUsed && !this._urgeOn && this.hp > 0,
      running: !!(this.tekken && this.tekken.running && this.tekken.running() && this.onGround) || (this.state === 'attack' && /^WR\./.test(this.attackName || '') && this.stateT <= 0.14), // Tekken WR (and its chord-upgrade window)
      inMove: this.state === 'attack',
      attackT: this.state === 'attack' ? this.stateT : null, // time into the current hit ('~' window)
      // close/far normals (KOF/SF) pick by root distance; stance spin variants by re-entries
      dist: this._opp && this._opp.root && this.root ? Math.hypot(this._opp.root.position.x - this.root.position.x, this._opp.root.position.z - this.root.position.z) : null,
      stanceSpins: this.stance ? (this._stanceSpins || 1) : 0,
      foeFlank: this._foeFlank(), // batch 8: 'L' / 'R' / 'B' when at the opponent's side or back
      soulStates: soulStates(this), // pt217u: 魂 ACTION / KESSHOU / 九魂解放 / 霊放 / 試練の封 gates
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
    if (this.brawler) {
      // BRAWLER: hop straight back along the facing yaw (3D).
      const s = this.stats.speed * 1.7;
      this.vx = -Math.sin(this.yaw) * s;
      this.vz = -Math.cos(this.yaw) * s;
    } else {
      this.vx = this.dodgeDir * this.stats.speed * 1.7;
    }
  }

  /* ---------------- V-System (owner 2026-10-22) ----------------
     One input ('vskill': KeyV / V button), three context moves —
     Tekken-ified from SFV's V-Skill / V-Trigger / V-Reversal, plus
     V-Shift on block double-tap. Canon name unassigned (NEEDS NAME) — no name text is shown in-game. */
  _startVAttack(move, state, name) {
    this.attack = move; this.attackName = name; this.hasHit = false; this._prevHitPoint = null;
    this._attackId = (this._attackId || 0) + 1;
    this._queuedNext = null; this._stepChain = null; this._queuedAfter = null;
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
  /* TEKKEN GRAPPLE (2026-10-24, t3-throw.js + docs/anim/T3-REACTIONS.md):
     On connect, the file's throw pair replaces the legacy lock.
     The attempt clip already played (attack state); now, with no
     further button press, the thrower and victim play the paired
     slot clips in sync on the shared root frame, the break window
     is the first frames of those same clips, and damage lands at
     the file's damage_frames. When the file has no pair for this
     throw (or its clips are not loaded), this falls through to
     the legacy 0.3 s lock below — UNMAPPED, never an invented
     pairing. game.js's lock-resolution loop skips paired
     fighters (lockMove is null), so completeThrow() never fires
     for a pair; _tickState advances the pair instead. */
  startThrowLock(move, attacker) {
    const pair = attacker && attacker._throwPairFor(move, this);
    if (pair && pair.pair && attacker._bindThrowPair(pair.pair, this)) {
      attacker._startThrowPair(pair.pair, this);
      return;
    }
    if (pair && pair.reason) console.log(`[WH-THROW] ${attacker.char.id} vs ${this.char.id}: no file pair (${pair.reason}) — legacy lock`);
    this.state = 'thrown'; this.stateT = 0;
    this.lockT = 0.3; this.lockMove = move; this.lockPartner = attacker;
    this.vx = 0; this.vz = 0;
    // face the attacker during the lock
    if (this.brawler) {
      const ax = attacker.root.position.x - this.root.position.x;
      const az = attacker.root.position.z - this.root.position.z;
      this.yaw = Math.atan2(ax, az);
    } else {
      const want = Math.sign(attacker.root.position.x - this.root.position.x) || 1;
      this.facing = want;
    }
  }
  startThrowing(victim) {
    this.state = 'throwing'; this.stateT = 0;
    this.lockT = 0.3; this.lockVictim = victim; this.lockMove = this.attack;
    this.vx = this.facing * 1.2; // step in with the grab
    this._breakCueT = 0;
  }
  /* Resolve the file's throw pair for a grab that just connected.
     Attempt row priority: (1) the attempt clip plan's own row
     ('row:<n>' — the file row the reach actually played), else
     (2) the file's throw_inputs row for an exact LP1+LK3 /
     RP2+RK4 chord. A generic 'grab' action has no row of its own
     and is NOT mapped through throw_inputs — its chord is
     ambiguous, and guessing it would wire the wrong attempt. */
  _throwPairFor(move, victim) {
    const R = globalThis.WH_T3_REACTIONS;
    if (!R) return { pair: null, reason: 'throw tables not loaded' };
    const aDir = this._t3 && this._t3.dir, vDir = victim._t3 && victim._t3.dir;
    if (!aDir) return { pair: null, reason: `no T3 bank for ${this.char.id} (UNMAPPED)` };
    if (!vDir) return { pair: null, reason: `no T3 bank for ${victim.char.id} (UNMAPPED)` };
    let attemptRow = null;
    const planName = this._atkPlan && this._atkPlan.name;
    // A per-step-bank action name is 'row:<bank>:<row>', which
    // parseInt cannot read ('jin:220' -> NaN); the plan's own stepRow
    // is authoritative whenever the attack came from a step plan.
    if (this._atkPlan && this._atkPlan.stepRow != null) attemptRow = this._atkPlan.stepRow;
    else if (planName && planName.startsWith('row:')) attemptRow = parseInt(planName.slice(4), 10);
    if (attemptRow == null && (this.attackName === '1+3' || this.attackName === '2+4')) {
      attemptRow = attemptRowForInput(R, aDir, this.attackName, this.stance === 'FC', false);
    }
    if (attemptRow == null || Number.isNaN(attemptRow)) {
      return { pair: null, reason: `no T3 attempt row for '${this.attackName}' (UNMAPPED)` };
    }
    const dx = victim.root.position.x - this.root.position.x;
    const dz = victim.root.position.z - this.root.position.z;
    const posture = victim.state === 'crouch' ? 'crouching' : victim.state === 'knockdown' ? 'lying' : 'standing';
    const quadrant = throwQuadrant(this.root.position, victim.root.position, victim.facing);
    const rp = getReactionPack(this._t3.bank);
    const sel = selectThrow(R, aDir, attemptRow, { posture, quadrant,
      distanceM: Math.hypot(dx, dz), anchorScale: rp ? rp.pack.anchor_mm_to_rig_m : 0 });
    if (!sel.throw) return { pair: null, reason: sel.reason };
    const clips = resolveThrowClips(R, sel.throw, aDir, vDir);
    if (!clips.throwerBank || !clips.victimBank) return { pair: null, reason: clips.note || 'unresolved clip bank (UNMAPPED)' };
    return { pair: { throw: sel.throw, branch: sel.branch, code: sel.code, clips,
      breaks: throwBreaks(sel.throw), damageTimeSec: throwDamageTimeSec(sel.throw),
      durationSec: throwPairDurationSec(sel.throw), whMove: move, isEscape: false, hitDone: false }, reason: null };
  }
  /* Bank key (t3anims.js T3_BANKS key) for a reactions.json dir. */
  _bankIdForDir(dir) {
    for (const [k, v] of Object.entries(T3_BANKS)) if (bankDirOf(v) === dir) return k;
    return null;
  }
  /* Retarget one reaction-pack slot clip onto this fighter's rig
     as action `name`. Returns the action name or null. */
  _reactionAction(bankId, slot, name) {
    if (!bankId || !this._t3 || this.t3actions[name]) return this.t3actions[name] ? name : null;
    const canonical = getReactionClip(bankId, slot, THREE);
    if (!canonical) return null;
    const rc = retargetT3Clips({ [name]: canonical }, bankId, this._t3.model, THREE, this._t3.modelKey, [name]);
    if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
    return this.t3actions[name] ? name : null;
  }
  /* Bind both clips of a pair (thrower on `thrower`, victim on
     `victim`; this method is called on the thrower). Also records
     the pack rows the shared-frame drive reads anchors from, and
     the thrower's anchor scale (used for both clips, per doc).
     Returns false when either clip is unavailable — the caller
     then keeps the legacy lock instead of a half pair. */
  _bindThrowPair(pair, victim) {
    const thrower = this;
    const tBank = thrower._bankIdForDir(pair.clips.throwerBank);
    const vBank = victim._bankIdForDir(pair.clips.victimBank);
    const tRp = tBank && getReactionPack(tBank);
    const vRp = vBank && getReactionPack(vBank);
    if (!tRp || !vRp) return false;
    pair.throwerPackRow = tRp.pack.rows[hexSlot(pair.clips.throwerSlot)];
    pair.victimPackRow = vRp.pack.rows[hexSlot(pair.clips.victimSlot)];
    if (!pair.throwerPackRow || !pair.victimPackRow) return false;
    pair.anchorScale = tRp.pack.anchor_mm_to_rig_m;
    pair.throwerAction = thrower._reactionAction(tBank, pair.clips.throwerSlot, 'throw:' + hexSlot(pair.clips.throwerSlot));
    pair.victimAction = victim._reactionAction(vBank, pair.clips.victimSlot, 'victim:' + hexSlot(pair.clips.victimSlot));
    return !!(pair.throwerAction && pair.victimAction);
  }
  /* Start a bound pair: shared root frame anchored at the
     victim's root, H = victim heading turned 180 deg (doc:
     H_yaw = -victim.facing * PI/2). Both fighters' pair clocks
     (_throwPairT) run from this moment; the clips themselves
     are NOT restarted on the throwing -> throwExec transition,
     so the pair stays in sync. */
  _startThrowPair(pair, victim) {
    const thrower = this;
    pair.thrower = thrower; pair.victim = victim;
    pair.anchor = { x: victim.root.position.x, z: victim.root.position.z };
    pair.hYaw = -victim.facing * Math.PI / 2;
    for (const [f, row] of [[thrower, pair.throwerPackRow], [victim, pair.victimPackRow]]) {
      f._throwPair = pair; f._throwPairT = 0;
      f.lockT = 0; f.lockMove = null;
      f.vx = 0; f.vz = 0; f.vy = 0;
      f._faceYaw = pair.hYaw + (row.yaw0 || 0);
    }
    thrower.lockVictim = victim;
    victim.lockPartner = thrower;
    thrower.state = 'throwing'; thrower.stateT = 0;
    victim.state = 'thrown'; victim.stateT = 0;
  }
  /* Damage for a paired throw, at the file's damage time.
     Main pair: the WH move's own damage (MOD decision). Escape
     pair: not a WH move — the file damage scaled T3 170 -> WH 100. */
  _throwPairDamage() {
    const pair = this._throwPair, attacker = pair && pair.thrower;
    if (!pair || !attacker || pair.hitDone) return null;
    pair.hitDone = true;
    const base = pair.isEscape ? pair.throw.damage * 100 / 170 : (pair.whMove && pair.whMove.damage) || 0;
    const dmg = base * attacker.stats.power / this.stats.defense;
    this.hp = Math.max(0, this.hp - dmg);
    if (this.hp <= 0) {
      this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
      return 'ko';
    }
    return 'throw';
  }
  get throwBreakInput() {
    if (this._throwPair && this._throwPair.breaks && this._throwPair.breaks[0]) return this._throwPair.breaks[0].input;
    return this.lockMove && this.lockMove.throw_break;
  }
  tryThrowBreak(btn) {
    if (this.state === 'thrown' && this._throwPair) {
      // File pair break: input must match AND the pair clock must
      // be inside the file's break window (first frames of the
      // same clips). A correct input outside the window does not
      // break — the throw lands. On break, the file's escape pair
      // starts with roles swapped; if it cannot bind, fall back
      // to the legacy escape (both idle, attacker punishable).
      const pair = this._throwPair, brk = pair.breaks && pair.breaks[0];
      if (!brk) return false;
      const got = (btn === '3+4') ? '1+2' : btn;
      if (got !== brk.input) return false;
      const t = this._throwPairT || 0;
      if (t < brk.windowSec[0] || t > brk.windowSec[1]) return false;
      const attacker = pair.thrower;
      const R = globalThis.WH_T3_REACTIONS;
      const esc = R && escapePairFor(R, pair.throw, pair.breaks, attacker._t3.dir, this._t3.dir);
      this._throwPair = null; if (attacker) attacker._throwPair = null;
      if (esc) {
        const newPair = { throw: esc.throw, branch: null, code: null, clips: esc.clips,
          breaks: throwBreaks(esc.throw), damageTimeSec: throwDamageTimeSec(esc.throw),
          durationSec: throwPairDurationSec(esc.throw), whMove: null, isEscape: true, hitDone: false };
        if (this._bindThrowPair(newPair, attacker)) { this._startThrowPair(newPair, attacker); this._throwEscaped = true; return true; }
      }
      this._enter('idle');
      this.vx = -this.facing * 2.0;
      if (attacker) {
        attacker.lockT = 0; attacker.lockVictim = null; attacker.lockMove = null;
        attacker._enter('idle');
        attacker.stun = Math.max(attacker.stun, 0.3);
        attacker.vx = 0;
      }
      this._throwEscaped = true;
      return true;
    }
    if (this.state !== 'thrown' || !this.lockMove) return false;
    // KOF XV throw escape row: its own input breaks during the first 11 frames of the throw.
    const esc = systemRows(this._movesetId).find((r) => r.sys === 'throw_escape' && r.input === btn);
    if (esc && (this.stateT || 0) > KOF.ESCAPE_WINDOW) return false;
    const want = esc ? btn : (this.lockMove.throw_break || '1');
    const got = (btn === '3+4') ? '1+2' : btn; // mobile: both-kicks = both-punches
    // T8 tables: 'none' = unbreakable, '1|2' = either punch breaks.
    if (!esc && (want === 'none' || !want.split('|').includes(got))) return false;
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
    // Paired throws never route here: their break window is the
    // first frames of the pair clips and _tickState advances the
    // pair to throwExec/thrownExec when it ends (see below).
    if (this._throwPair) return null;
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
    if (attacker._maxT > 0) dmg *= KOF.MAX_DMG; // KOF XV MAX Mode
    this.hp = Math.max(0, this.hp - dmg);
    if (this.hp <= 0) {
      this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
      return 'ko';
    }
    return 'throw';
  }
  tryAttack(name) {
    // KOF XV system rows (guard cancel from blockstun only; throw escape only while thrown).
    if (/^[1234](\+[1234])*$/.test(name)) { const r = this._systemPress(name); if (r !== undefined) return r; }
    // KOF run / backstep: a button during the dash row is the dash move (f,f+2), so the press
    // cancels the system dash; if nothing resolves, the dash keeps going.
    if (this.state === 'attack' && this.attack && (this.attack.system === 'dash' || this.attack.system === 'backdash') && /^[1234](\+[1234])*$/.test(name)) {
      const sv = { state: this.state, stateT: this.stateT, attack: this.attack, attackName: this.attackName, _attackPhase: this._attackPhase, _prevAtkT: this._prevAtkT, _sysVx: this._sysVx };
      this.state = 'idle'; this.attack = null;
      if (this._tryAttackFresh(name)) return true;
      Object.assign(this, sv);
    }
    // Chain throws: buttons during a throw pick the next stage (Tekken multi-part throws).
    if ((this.state === 'throwing' || this.state === 'throwExec') && /^[1234](\+[1234])*$/.test(name)) return this._throwChainPress(name);
    // A press during a string-capable move buffers the next hit (Tekken input buffer):
    // it fires when the current hit's active frames end.
    if (this.state === 'attack' && this.attack && /^[1234](\+[1234])*$/.test(name)) {
      // A hit already queued is the string's next step: a further press chains on from
      // it (2,1 then 2 -> 2,1,2), never re-resolves against the move still playing,
      // which overwrote the queue (2 -> 2,2) and dropped 3+ hit strings.
      // '3,d+1+2' (TekkenDocs: direction and button pressed together): the stick lands a
      // frame or two before the buttons, so a dir-only follow-up ('3,d') queued just now is
      // the first half of the dir+button step. Sweep 2026-10-29: the dir-only key stole it.
      const dq = this._dirFollowQ;
      if (dq && this._queuedNext && (this._clock || 0) - dq.t < 0.1) {
        const up = [`${dq.b}${dq.sep}${dq.d}+${name}`, `${dq.b}${dq.sep}${dq.d.toUpperCase()}+${name}`].find((k) => resolveMoveKey(this._movesetId, k));
        const q = this._queuedAfter && this._queuedAfter.length ? this._queuedAfter : null;
        if (up && (q ? q[q.length - 1] : this._queuedNext) === dq.c) {
          if (q) q[q.length - 1] = up; else this._queuedNext = up;
          this._dirFollowQ = null; return true; }
      }
      if (this._queuedNext) {
        const chain = this._queuedAfter || (this._queuedAfter = []);
        const saved = this.tekken.lastMove;
        // Chord upgrade on a queued hit: input.js emits '1' then '1+2' for one 1+2 press,
        // so a queued '...,1' whose button is in the chord becomes '...,1+2' (f+2~1+2).
        if (name.includes('+')) {
          const tail = chain.length ? chain[chain.length - 1] : this._queuedNext;
          const single = tail.split(/[,~:]/).pop();
          if (/^[1234]$/.test(single) && name.split('+').includes(single) &&
              (this._clock || 0) - (this._queuedPressT || -1) < 0.06) {
            this.tekken.lastMove = chain.length > 1 ? chain[chain.length - 2] : chain.length ? this._queuedNext : saved;
            const up = this.tekken.continuation(name, this._inputCtx());
            this.tekken.lastMove = saved;
            if (up) { if (chain.length) chain[chain.length - 1] = up; else this._queuedNext = up; return true; }
          }
        }
        this.tekken.lastMove = chain.length ? chain[chain.length - 1] : this._queuedNext;
        // '~' window on a queued hit: time since that hit's own press, not into the move still playing.
        const qctx = Object.assign(this._inputCtx(), { attackT: (this._clock || 0) - (this._queuedPressT != null ? this._queuedPressT : -1) });
        let after = this.tekken.continuation(name, qctx);
        if (!after) {
          // '1' after f+2 resolved as 'f+2,1', but the list's 3-hit route is 'f+2~1,1+2':
          // re-route the queued tail through its other separator when only that one continues.
          const tail = this.tekken.lastMove, cut = Math.max(tail.lastIndexOf(','), tail.lastIndexOf('~'));
          for (const sep of [',', '~']) {
            if (cut <= 0 || tail[cut] === sep) continue;
            const alt = tail.slice(0, cut) + sep + tail.slice(cut + 1);
            if (!resolveMoveKey(this.tekken.fighterId, alt)) continue;
            this.tekken.lastMove = alt;
            const via = this.tekken.continuation(name, qctx);
            if (via) { if (chain.length) chain[chain.length - 1] = alt; else this._queuedNext = alt; after = via; break; }
          }
        }
        this.tekken.lastMove = saved;
        if (after) { chain.push(after); this._queuedPressT = this._clock || 0; }
        return true;
      }
      const cont = this.tekken.continuation(name, this._inputCtx());
      if (cont) { this._queuedNext = cont; this._queuedPressT = this._clock || 0; return true; }
      if (this.tekken._strPending) { this._stringGraceUntil = Math.max(this._stringGraceUntil || 0, performance.now() + 500); return true; } // extends an open partial string; fires at its full step
      // Chord upgrade: input.js emits the first button at once and the chord when the second
      // lands inside its 140 ms window, so '1' then '1+3' means the player pressed 1+3. If the
      // single that just started is part of this chord, the chord replaces it.
      if (name.includes('+') && this.stateT <= 0.14 && this._attackPhase === 'startup' && !this.hasHit) {
        // Tekken '~' (wavu wiki: "immediately after"): '3~4' is 4 pressed a frame or two after 3,
        // which input.js reports as the chord 3+4. When the move has a tilde follow-up for the
        // later button(s) and they came after the first frame, it is the tilde, not the chord.
        if (this.stateT > 0 && this.tekken && this.tekken.lastMove) {
          const first = String(this.attackName || '').split('+').pop().slice(-1);
          const rest = name.split('+').filter((b) => b !== first).join('+');
          const tk = rest && `${this.tekken.lastMove}~${rest}`;
          if (tk && resolveMoveKey(this.tekken.fighterId, tk)) { this._queuedNext = this.tekken._recordMove(tk); this._queuedPressT = this._clock || 0; return true; }
        }
        const single = String(variantBase(this._movesetId, this.attackName) || this.attackName || '').split(/[,.]/).pop(); // close/far normal: its plain button
        const btn = single.split('+').pop();
        if (/^[1234]$/.test(btn) && name.split('+').includes(btn)) {
          this.tekken.lastMove = this._chordBase || null;
          const saved = { state: this.state, attack: this.attack, attackName: this.attackName, stateT: this.stateT,
            stance: this.stance, stanceT: this.stanceT, _risingT: this._risingT };
          // Moveset sweep 2026-10-28: re-resolve the chord in the state the single was pressed
          // from (stance / crouch / while-rising), not plain idle — SAV.1+2, WS.1+2, FC.1+2 and
          // stance throws (SIDE_L.1+3) came out as the neutral chord.
          const pre = this._preAtk || {};
          this.state = pre.state === 'crouch' ? 'crouch' : 'idle';
          this.stance = pre.stance || null; this.stanceT = pre.stanceT || 0; this._risingT = pre.risingT || 0;
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
  /* Direction-only string follow-ups (moveset sweep 2026-10-28): rows like 'f+4,u' or
     'f+3,d/f' end (or continue) on a bare stick step, a stance/cancel transition in Tekken.
     Only buttons reached tryAttack, so these were unreachable. A fresh stick direction
     during a string-capable move queues the follow-up exactly like a buffered button. */
  tryDirFollow(dir) {
    if (!dir || dir === 'n') return false;
    // Throw follow-ups ('d/f+1+2,F' = throw, then Savage Stance): the stick during the throw
    // picks the row; its stance applies when the throw ends (_endThrowFollow).
    if ((this.state === 'throwing' || this.state === 'throwExec') && this.tekken.lastMove && !this._throwFollow) {
      for (const d of [dir, dir.toUpperCase()]) { const c = `${this.tekken.lastMove},${d}`;
        if (!resolveMoveKey(this._movesetId, c)) continue;
        this._throwFollow = c; this.tekken._recordMove(c); this.attackName = c; return true; }
      return false;
    }
    if (this.state !== 'attack' || !this.attack) return false;
    // Same follow-up entered during the grab's own startup/active (before it connects): it
    // rides on the throw instead of queueing a string hit the throw lock would drop.
    if (this.attack.isGrab && this.tekken.lastMove && !this._throwFollow) {
      for (const d of [dir, dir.toUpperCase()]) { const c = `${this.tekken.lastMove},${d}`;
        if (!resolveMoveKey(this._movesetId, c)) continue;
        this._throwFollow = c; this.tekken._recordMove(c); this.attackName = c; return true; }
    }
    const T = this.tekken, ms = this._movesetId;
    const last = (this._queuedAfter && this._queuedAfter.length) ? this._queuedAfter[this._queuedAfter.length - 1] : (this._queuedNext || T.lastMove);
    if (!last) return false;
    const bases = [last]; const t = last.indexOf('~'); if (t > 0) bases.push(last.slice(0, t));
    /* Direction-only endings over several taps ('1+2,f,f', 'd/f+1,2,f,F', TekkenDocs): a tap that
       only opens the tail ('1+2,f') is kept as a pending path; the next tap completes it. */
    const dp = this._dirPath;
    if (dp && dp.from === last && (this._clock || 0) - dp.t < 0.4) bases.unshift(dp.p);
    // Lowercase (tapped) spelling first across all separators, then the held capital ('SS.2:u' before 'SS.2,U').
    for (const b of bases) for (const d of [dir, dir.toUpperCase()]) for (const sep of [',', '~', ':']) {
      const c = `${b}${sep}${d}`;
      if (!resolveMoveKey(ms, c)) continue;
      this._dirPath = null;
      if (this._queuedNext) (this._queuedAfter || (this._queuedAfter = [])).push(c); else this._queuedNext = c;
      this._queuedPressT = this._clock || 0;
      this._dirFollowQ = { c, b, sep, d: dir, t: this._clock || 0 };
      return true;
    }
    for (const b of bases) for (const d of [dir, dir.toUpperCase()]) { const c = `${b},${d}`;
      if (hasStrPrefix(ms, c)) { this._dirPath = { p: c, from: last, t: this._clock || 0 }; return true; } }
    return false;
  }
  /* Held-button moves (moveset sweep 2026-10-28): 'd/b+1*' / 'SAV.1+2*' = keep the limb(s)
     down. The press starts the tap version; still held after HOLD_UPGRADE_S of startup, the
     move becomes its held version. Before, '*' rows were reachable only with no tap version. */
  tryHoldUpgrade(held) {
    if (this.state !== 'attack' || this._attackPhase !== 'startup' || !held) return false;
    const n = this.attackName || '';
    if (!n || n.endsWith('*') || this.stateT < 0.15) return false;
    const btns = (n.split(/[,~:]/).pop().match(/[1-4](?:\+[1-4])*$/) || [''])[0].split('+').filter(Boolean);
    if (!btns.length || !btns.every((b) => held[b])) return false;
    const base = n.indexOf('~') > 0 && !resolveMoveKey(this._movesetId, n + '*') ? n.slice(0, n.indexOf('~')) : n;
    const k = base + '*';
    if (!resolveMoveKey(this._movesetId, k)) return false;
    return this._fireNotation(k);
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
  /* GAP-FILL LANE 1: item-move loadout (T7 item-gated attacks). */
  setEquippedItems(list) { this.equippedItems = Array.isArray(list) ? [...list] : []; }
  equipItem(id) { if (id && !this.equippedItems.includes(id)) this.equippedItems.push(id); }
  unequipItem(id) { this.equippedItems = this.equippedItems.filter((e) => e !== id); }
  hasItem(id) { return this.equippedItems.includes(id); }

  /* GAP-FILL LANE 1: recoverable pool (T8 white gauge, verified
     absent before this lane — WH chip was permanent loss).
     Pool accrues ONLY from chip actually lost on block (see
     receiveHit); aerial/grounded recoverable fractions are NOT
     implemented because no verified T8 fraction was found in
     this lane's sources — inventing one would break the
     no-guesses rule. Attacking recovers: landing a hit or
     forcing a block heals up to the damage forced, capped by
     the pool and by max HP. Never recovers over time. */
  _addRecoverable(amount) {
    if (amount > 0) this._recoverable = Math.min(this.maxHp, (this._recoverable || 0) + amount);
  }
  _recoverOnAttack(amount) {
    const pool = this._recoverable || 0;
    if (pool <= 0 || !(amount > 0)) return 0;
    const healed = Math.min(pool, amount, Math.max(0, this.maxHp - this.hp));
    if (healed > 0) { this.hp += healed; this._recoverable = pool - healed; }
    return healed;
  }
  tryUrgeDash() {
    // GAP-FILL LANE 1 (Soul Urge completeness): T8 Heat Dash is a
    // CANCEL, not just a neutral input — it may also fire from an
    // attack's recovery, cancelling the tail of the move.
    const cancel = this.state === 'attack' && this._attackPhase === 'recovery';
    if (!this._urgeOn || this._urgePips < 1 || (!this.canAct() && !cancel)) return false;
    const g = this.game;
    if (g && g.soulurge) g.soulurge.spendPip(this);
    else this._urgePips -= 1;
    if (cancel) { this.attack = null; this.attackName = null; }
    this._urgeDashT = 0.45;
    this.vx = this.facing * 9;
    this._enter('dash');
    return true;
  }
  /** KOF system row on this press, if one applies in the current state; undefined = not a system press. */
  _systemPress(name) {
    const rows = systemRows(this._movesetId); if (!rows.length) return undefined;
    const d = this.tekken && this.tekken.lastDir; const dn = d && d !== 'n' ? d + '+' + name : name;
    const row = rows.find((r) => (r.sys === 'guard' || r.sys === 'throw_escape') && (r.input === dn || r.input === name));
    if (!row) return undefined;
    if (row.sys === 'throw_escape') return this.state === 'thrown' ? this.tryThrowBreak(name) : undefined;
    if (!(this.state === 'block' && this.stun > 0.05 && this.onGround)) return undefined;
    if (this.meter < KOF.GC_COST * KOF.STOCK) return false;
    const ms = getFighterMoveset(this._movesetId); const mv = ms && ms.moves[row.key]; if (!mv) return false;
    this.meter -= KOF.GC_COST * KOF.STOCK;
    this.stun = 0;
    this._startSystemMove(row.key, mv);
    // GC roll: invulnerable through the whole roll, delay included; GCCD: strike-invulnerable to its active end
    this.invuln = mv.damage > 0 ? (mv.startup || 0) + (mv.active || 0) : (mv.startup || 0) + (mv.active || 0) + (mv.recovery || 0);
    if (!(mv.damage > 0)) this.vx = (/^b/.test(row.input) ? -1 : 1) * this.facing * 6;
    return true;
  }
  /** Does this fighter's moveset own `input` as a KOF system row (optionally of `sys`)? */
  systemRowOn(input, sys) { return systemRows(this._movesetId).find((r) => r.input === input && (!sys || r.sys === sys)) || null; }
  _startSystemMove(key, move) {
    this._preAtk = { state: this.state, stance: this.stance, stanceT: this.stanceT, risingT: this._risingT };
    this.attack = move; this.attackName = key; this.hasHit = false; this._prevHitPoint = null;
    this._attackId = (this._attackId || 0) + 1;
    this._queuedNext = null; this._queuedAfter = null; this.stance = null; this.stanceT = 0;
    this._throwFollow = null; this._chainFrom = null; this._chainNext = null; this._chainSeq = [];
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup'; this._prevAtkT = 0;
  }
  /** Double tap f/b (input buffer dash latch): the fighter's dash / backdash row, or its roll
      row when no dash row owns that direction. */
  trySystemMotion(dir) {
    if (!this.canAct() || !this.onGround) return false;
    const rows = systemRows(this._movesetId); const dd = dir + ',' + dir;
    const want = dir === 'f' ? 'dash' : 'backdash';
    const row = rows.find((r) => r.sys === want && r.input === dd) || rows.find((r) => r.sys === 'roll' && r.input === dd);
    if (!row) return false;
    const ms = getFighterMoveset(this._movesetId); const mv = ms && ms.moves[row.key]; if (!mv) return false;
    this._startSystemMove(row.key, mv);
    const sgn = dir === 'f' ? 1 : -1;
    if (row.sys === 'roll') { this.invuln = KOF.ROLL_INVULN; this._sysVx = sgn * this.facing * 2.6 / KOF.ROLL_TOTAL; }
    else this._sysVx = sgn * this.facing * (row.sys === 'dash' ? 7 : 6);
    return true;
  }
  /* Advance a whole-string step chain: fire the next prefix step. Returns true
     when a step fired; false when the chain is finished or broken (chain cleared).
     A user-queued hit always wins over the chain: callers clear _stepChain first
     when _queuedNext is set, so a pressed continuation replaces the auto-chain. */
  _advanceStepChain() {
    const ch = this._stepChain;
    if (!ch || ch.idx + 1 >= ch.steps.length) { this._stepChain = null; return false; }
    const next = ch.steps[ch.idx + 1].prefix;
    ch.idx += 1;
    this.attack = null; this.attackName = null;
    if (this._fireNotation(next)) return true;
    this._stepChain = null; return false;
  }
  _tryAttackFresh(name) {
    if (!this.canAct() && !this.sidestepCancelable) return false;
    // A fresh press cancels any auto step chain: the player is driving now.
    this._stepChain = null;
    // Tekken notation resolution: strings (1,2), motion specials (qcf+2),
    // directionals (f+1), state/stance prefixes (WS. FC. SS. BT. R. SNK. ...)
    // via the fighter's TekkenBuffer + its moveset's notation table.
    let notation = LEGACY_TO_TEKKEN[name] || name;
    const ctx = this._inputCtx();
    /* WH legacy buttons (moveset sweep 2026-10-28): signature moves keyed 'S' / 'b+S' / 'D+S'
       fire on the 'sig' action, and a fighter's own 'P+K' move fires on the grab action
       (U / J+K) instead of the generic 1+3 throw. Resolved with the held stick like any button. */
    if (name === 'sig' || (name === 'grab' && resolveMoveKey(this._movesetId, 'P+K'))) {
      const btn = name === 'sig' ? 'S' : 'P+K';
      const r = this.tekken.press(btn, ctx);
      if (!r || !getRealMove(this._movesetId, r)) return false;
      notation = r; name = r;
    }
    this._chordBase = this.tekken.lastMove;
    // GAP-FILL LANE 1 (Soul Urge completeness): Urge Dash as a
    // recovery cancel — reachable even though canAct() is false
    // mid-attack. tryUrgeDash() itself enforces the cancel window.
    if (notation === '1+2' && ctx.urgeOn && !ctx.rage &&
        this.state === 'attack' && this._attackPhase === 'recovery') {
      return this.tryUrgeDash();
    }
    // String grace (2026-10-24, Pantera string fix; batch 2026-10-24: 200 -> 500 ms
    // for touch cadence): a tap landing just after the previous hit fully
    // recovered still continues the string — 500 ms past move end. The window
    // is set in _tickState when
    // a non-grab attack completes and cleared on hitstun/knockdown/KO, so
    // getting hit kills it and a throw never chains. canAct-only: it must
    // not chain out of a sidestep-cancel.
    if (this.canAct() && /^[1234](\+[1234])*$/.test(notation) &&
        (typeof performance !== 'undefined' ? performance.now() : 0) < this._stringGraceUntil) {
      const grace = this.tekken.continuation(notation);
      if (grace && this._fireNotation(grace)) return true;
      // extends an open partial string (no standalone step): consume, keep the grace window open
      if (!grace && this.tekken._strPending) { this._stringGraceUntil = performance.now() + 500; return true; }
    }
    if (/^[1234]$/.test(notation)) {
      const pathT0 = this.tekken._strPathT;
      const resolved = this.tekken.pressButton(notation, ctx);
      // Moveset sweep 2026-10-28: the press opened a string whose first step has no standalone
      // move ('u+1' of 'u+1,1'). The resolver deliberately fires nothing and waits for the next
      // hit; falling back to the plain button here fired '1' and the string was unreachable.
      if (!resolved && this.tekken._strPath && this.tekken._strPathT !== pathT0) return true;
      // Stream 6: if the fighter has no move on this limb, keep the raw
      // notation so the base-move fallback below still fires (no dead buttons).
      if (resolved) notation = resolved;
    } else if (/^[1234](\+[1234])+$/.test(notation)) {
      if (notation === '1+2' && ctx.urgeOn && !ctx.rage) return this.tryUrgeDash();
      // GAP-FILL LANE 1 (Soul Urge completeness): LP1+RP2 is the
      // dash (above); LK3+RK4-adjacent chord 2+3 is Burst/Smash.
      // Buttons here are Tekken numbers per the file convention;
      // user-facing text uses LP1/RP2/LK3/RK4. During Soul Urge,
      // 2+3 fires the synthesized Urge Smash; with Soul Urge
      // available but not active, 2+3 fires Urge Burst. If neither
      // synthesized move exists (moveset not yet injected), fall
      // through to normal chord resolution instead of dead input.
      if (notation === '2+3' && (!this.tekken.lastDir || this.tekken.lastDir === 'n')
        && !(ctx.soulStates || []).some((sp) => resolveMoveKey(this.tekken.fighterId, sp + '.2+3'))
        && !(ctx.running && resolveMoveKey(this.tekken.fighterId, 'WR.2+3'))) { // soul-state finisher outranks urge
        if (ctx.urgeOn && this._fireNotation('US.2+3')) return true;
        if (ctx.urgeAvailable && this._fireNotation('UB.2+3')) return true;
      }
      const resolved = this.tekken.pressChord(notation, ctx);
      if (!resolved) return false; // chord with no matching move: whiff, no action
      notation = resolved;
    }
    // Use REAL per-fighter T3 moveset data when available, fallback to base MOVES
    if (this.state === 'attack' && this.attack && !this.hasHit) this._t3Whiff = this._clock || 0;
    let move = getRealMove(this._movesetId, notation) || MOVES[name] || MOVES[notation];
    // A T3 branch-condition row (equipped via the moveset editor) fires only while its condition
    // holds; otherwise the input plays the fighter's default move for that notation.
    if (move && move.t3Condition != null && !t3ConditionHolds(move.t3Condition, this, this._opp, notation)) {
      move = getRealMove(this._movesetId, notation, { noLoadout: true }) || MOVES[name] || MOVES[notation];
    }
    if (!move) {
      // Last resort: moveset JSONs failed to load - map Tekken buttons to base moves
      const fb = { '1': 'punch', '2': 'punch', '3': 'kick', '4': 'kick',
                   '1+3': 'grab', '2+4': 'grab', '1+2': 'grab', '3+4': 'grab' }[notation];
      if (fb) move = MOVES[fb];
    }
    if (!move) return false;
    // GAP-FILL LANE 1 (item moves): a move gated by an item the
    // fighter has not equipped does not fire at all — no fallback
    // to a generic strike, so an unequipped item move is never
    // silently replaced by a different move.
    if (itemGate(move, this.equippedItems).blocked) return false;
    // Preserve WH-specific properties (grab unblockable, surge cost)
    if (MOVES[name]) {
      move = { ...move, ...Object.fromEntries(
        Object.entries(MOVES[name]).filter(([k]) => ['unblockable','isGrab','cost','soulGain'].includes(k))
      )};
    }
    if (move.cost > 0 && this.meter < move.cost) return false;
    if (move.cost > 0) this.meter = Math.max(0, this.meter - move.cost);
    // Batch 1 step plans: a whole-string key fired at once (AI / trials / movelist
    // demo / buffered full notation) plays as a chain of its prefix steps through
    // the existing _fireNotation path — never one row for the whole string. The
    // chain needs every prefix to be a real move; when any prefix is missing
    // (e.g. jumping strings have no standalone 'u+1' move) the string fires
    // normally and _attackClipPlan's step-plan branch picks its clip instead.
    // The per-press path never enters here: each press already fires one prefix.
    {
      const ms0 = getFighterMoveset(this._movesetId);
      const raw0 = ms0 && ms0.moves ? ms0.moves[move.moveKey] : null;
      const plan0 = ms0 && ms0.string_step_plans && ms0.string_step_plans.plans ? ms0.string_step_plans.plans[move.moveKey] : null;
      if (plan0 && Array.isArray(plan0.steps) && plan0.steps.length >= 2 && raw0 && raw0.move_class === 'string'
          && plan0.steps.every(s => getRealMove(this._movesetId, s.prefix))) {
        this._stepChain = { key: move.moveKey, steps: plan0.steps, idx: 0 };
        if (this._fireNotation(plan0.steps[0].prefix)) return true;
        this._stepChain = null;
      }
    }
    // KOF system rows off their state: guard cancels need blockstun, throw escape needs a throw.
    if (move.system === 'guard' || move.system === 'throw_escape') return false;
    if (move.system === 'max') {
      if (this._maxT > 0 || this.meter < KOF.MAX_COST * KOF.STOCK) return false;
      this.meter -= KOF.MAX_COST * KOF.STOCK; this._maxT = KOF.MAX_SECONDS; this._auraFlash = 1.0;
    }
    if (move.system === 'taunt') { const t = (move.startup || 0) + (move.active || 0);
      move = { ...move, recovery: Math.max(move.recovery || 0, KOF.TAUNT_LOCK - t) }; } // 49f uncancellable
    this._preAtk = { state: this.state, stance: this.stance, stanceT: this.stanceT, risingT: this._risingT };
    this.attack = move; this.attackName = notation; this.hasHit = false; this._prevHitPoint = null;
    this._attackId = (this._attackId || 0) + 1;
    this._queuedNext = null; this._queuedAfter = null; this._stepChain = null;
    if (/^(R|RD)\./.test(notation)) this._rageUsed = true; // rage art/drive: once per round
    // stance spin count (T7 JGS* (N spins)): re-entering the stance the move started from adds a spin
    this._spinNext = move.stanceAfter && this.stance === move.stanceAfter ? (this._stanceSpins || 1) + 1 : 1;
    this.stance = null; this.stanceT = 0; this._risingT = 0;
    this._throwFollow = null; this._chainFrom = null; this._chainNext = null; this._chainSeq = [];
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup'; this._prevAtkT = 0;
    if (name === 'surge') this._auraFlash = 0.7;
    if (move.isGrab || notation === '1+3' || notation === '2+4') this.vx = this.facing * 2.5; // lunge into the grab
    // batch 11: a side / back throw (FLANK_L/R/B, T7 'Left throw' / 'Back throw') is taken from
    // off the fight line: turn at the opponent and close the z gap through the grab (the
    // sidestep re-align path), lunging at them rather than along our own facing.
    if (/^FLANK_[LRB]\./.test(notation) && this._opp && this._opp.root) {
      this._ssAlign = true;
      this.vx = (Math.sign(this._opp.root.position.x - this.root.position.x) || this.facing) * 2.5;
    }
    return true;
  }
  /* Chain throws (2026-10-29): a throw whose name carries a stage tag ('Arm Breaker (AB1)')
     takes the stage's follow-up rows ('AB1.1,1+2') as button sequences entered while it
     plays. A full match queues that row; when the current throw part ends, the row starts
     on the same victim (still locked, still on its feet in Tekken's chain), so each part
     plays its own clip and damage. A prefix match keeps listening; anything else resets. */
  _throwChainPress(name) {
    const ms = getFighterMoveset(this._movesetId);
    const an = this._chainFrom || this.attackName;
    const cur = ms && (ms.moves[resolveMoveKey(this._movesetId, an) || an] || ms.moves[an]);
    const tag = cur && throwStageTag(cur.name); let keys = tag ? throwStageKeys(this._movesetId, tag) : [];
    /* Throw follow-ups written as a plain string ('2+4,2', '2+4,1,2,1', '1+3,1'; TekkenDocs / wavu
       wiki notation) have no stage tag: the throw's own key is the stage. Before (moveset sweep
       2026-10-29), only tagged chain throws ('AB1.1,1+2') could be continued, so every untagged
       throw follow-up in every fighter's list stopped at the throw. A tag with no stage rows
       (a named throw that only has plain follow-ups) is the same case. */
    if (!keys.length || !(this._chainSeq || []).length) {
      // Played through the string resolver (continuation): same lists, T7/T8 copies,
      // partial steps and alias spellings as a string off a normal hit.
      if (this.state !== 'throwing' && this.state !== 'throwExec') return false;
      const saved = this.tekken.lastMove;
      if (this._chainNext) this.tekken.lastMove = this._chainNext;
      const c = this.tekken.continuation(name, this._inputCtx());
      // a tagged chain throw whose own key also has plain follow-ups: the plain string
      // wins when it exists, else the press falls through to the stage rows below
      if (!c && this.tekken._strPending) { this.tekken.lastMove = saved; return true; }
      if (!c) { this.tekken.lastMove = saved; if (!keys.length) return false; } else {
      this._chainNext = c; this.tekken.lastMove = c;
      // a longer tagged stage on the same press ('SLEEPER.1,1,1+2' vs 'DMD.2,1') keeps listening;
      // the stage replaces the plain follow-up once its next press arrives
      this._chainOpen = keys.some((k) => k.startsWith(`${tag}.${name},`) || k.startsWith(`${tag}.${name}+`));
      if (this._chainOpen) { this._chainSeq = [name]; this._chainPressT = this._clock || 0; }
      return true; }
    }
    const pre = `${tag}.`;
    if (this._chainNext && !this._chainOpen) return false;
    const now = this._clock || 0; let seq = this._chainSeq || [];
    const tail = seq[seq.length - 1];
    // input.js emits '1' then '1+2' for one chord press: the chord replaces its single.
    if (name.includes('+') && tail && /^[1234]$/.test(tail) && name.split('+').includes(tail) && now - (this._chainPressT || -1) < 0.06) seq = seq.slice(0, -1);
    this._chainPressT = now;
    for (const s of [[...seq, name], [name]]) {
      const k = `${pre}${s.join(',')}`;
      if (keys.includes(k)) { this._chainNext = k; this._chainSeq = []; this._chainOpen = false; return true; }
      // ',' = more presses follow; '+' = this single is the first half of a chord press
      if (keys.some((x) => x.startsWith(k + ',') || x.startsWith(k + '+'))) { this._chainSeq = s; return true; }
    }
    this._chainSeq = []; const open = this._chainOpen; this._chainOpen = false; return !!open;
  }
  _startThrowChain(victim) {
    const key = this._chainNext; this._chainNext = null; this._chainSeq = []; this._chainOpen = false;
    const m = key && getRealMove(this._movesetId, key);
    if (!m || !victim || victim.dead || this.dead) return false;
    victim._throwPair = null; victim._throwPairT = 0; victim._throwAttacker = null; victim._throwMove = null;
    victim.stun = 0; victim.vy = 0; victim.onGround = true; victim.root.position.y = GROUND_Y; victim.state = 'idle';
    this._throwPair = null; this._throwPairT = 0; this._throwVictim = null; this._throwMove = null;
    this.attack = { ...m, isGrab: true }; this.attackName = key; this._chainFrom = key; this.hasHit = true;
    this.tekken._recordMove(key);
    victim.startThrowLock(this.attack, this);
    if (!this._throwPair) this.startThrowing(victim);
    return true;
  }
  _endThrowFollow() {
    const c = this._throwFollow; this._throwFollow = null; if (!c) return;
    const m = getRealMove(this._movesetId, c), after = m && m.stanceAfter;
    if (after === 'FC') { this._enter('crouch'); this.stance = 'FC'; this.stanceT = 0.5; }
    else if (after) { this._stanceSpins = this._spinNext || 1; this.stance = after; this.stanceT = 0.8; }
  }
  /* Start the move for an already-resolved notation (buffered string hits). */
  _fireNotation(notation) {
    let move = getRealMove(this._movesetId, notation);
    if (move && move.t3Condition != null && !t3ConditionHolds(move.t3Condition, this, this._opp, notation)) {
      move = getRealMove(this._movesetId, notation, { noLoadout: true });
    }
    if (!move) return false;
    // GAP-FILL LANE 1: item gate applies to string continuations
    // exactly as to fresh inputs (an item move mid-string with
    // the item unequipped ends the string, it does not swap).
    if (itemGate(move, this.equippedItems).blocked) return false;
    this.tekken._recordMove(notation);
    this.attack = move; this.attackName = notation; this.hasHit = false; this._prevHitPoint = null;
    this._attackId = (this._attackId || 0) + 1;
    // A hit pressed while this one was still queued chains on from it.
    this._queuedNext = (this._queuedAfter && this._queuedAfter.shift()) || null;
    if (this._queuedAfter && !this._queuedAfter.length) this._queuedAfter = null;
    this.vx = 0; this._enter('attack'); this._attackPhase = 'startup'; this._prevAtkT = 0;
    return true;
  }
  _enter(state) {
    // A move out of a sidestep (SS.X, or any attack cancelling the step) is aimed at the
    // opponent: Tekken re-aligns the fight axis on the step (TekkenDocs / wavu wiki
    // 'SS' moves). Moveset sweep 2026-10-29: the body kept its pre-step yaw, so every SS.*
    // row in the roster swung past the opponent's side.
    if (state === 'attack' && this.state === 'sidestep' && this._opp && this._opp.root && !this.brawler) {
      this.vz = 0; this._ssAlign = true;
    }
    if (state !== 'attack') this._ssAlign = false;
    this.state = state; this.stateT = 0;
  }

  /* ---------------- defense / damage ---------------- */
  isBlocking() { return this.state === 'block'; }

  /* Normalized world-space vector pointing AWAY from `attacker` on the
     ground plane (brawler knockback direction). */
  _awayFrom(attacker) {
    const dx = this.root.position.x - attacker.root.position.x;
    const dz = this.root.position.z - attacker.root.position.z;
    const d = Math.hypot(dx, dz) || 1;
    return [dx / d, dz / d];
  }

  receiveHit(move, attacker) {
    if (this.dead || this.invuln > 0) return 'dodge';
    // Posture snapshot for the T3 reaction pick below (the state is
    // overwritten by _enter('hitstun'/'knockdown') before we return).
    const _wasCrouch = this.state === 'crouch' || this.stance === 'FC';
    const _wasAirborne = !this.onGround;
    const _wasDown = this.state === 'knockdown' && this.onGround;
    // GAP-FILL LANE 1: wall-splat follow-up counting (one count per
    // landed hit on a splatted victim; the 3-hit drop lives below).
    const _wasWallSplat = this.state === 'wallsplat';
    if (_wasWallSplat) this._wallSplatHits++;
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
    // GAP-FILL LANE 1: Power Crush (T7) is NOT the generic armor
    // above. Generic armor absorbs everything except grabs; a
    // Power Crush absorbs only mid/high strikes (lows, throws,
    // unblockables and Rage Arts break it — combat-core.js).
    const crushActive = (this.state === 'attack' || this.state === 'vskill' || this.state === 'vreversal') &&
      powerCrushAbsorbs(this.attack, this._attackPhase, this.stateT, move);
    // BRAWLER: guard requires the defender's facing yaw to be within ~110°
    // of the direction to the attacker (3D); versus keeps the x-sign rule.
    let facingAttacker;
    if (this.brawler) {
      const ax = attacker.root.position.x - this.root.position.x;
      const az = attacker.root.position.z - this.root.position.z;
      const wantYaw = Math.atan2(ax, az);
      const dy = Math.atan2(Math.sin(wantYaw - this.yaw), Math.cos(wantYaw - this.yaw));
      facingAttacker = Math.abs(dy) < 1.92;
    } else {
      facingAttacker = Math.sign(attacker.root.position.x - this.root.position.x) === this.facing;
    }    // T3 HitClassify: guarded when (guard & attack word) != 0 and the defender faces the
    // attacker. Standing guard blocks highs/mids, crouching guard blocks lows; throws and
    // unblockables carry no guard bits.
    const word = move.hitWord ?? Fighter.defaultWord(move);
    const guarded = !move.unblockable && !move.isGrab && facingAttacker && (this._guardBits() & word) !== 0;
    if (attacker) attacker._t3Contact = { t: attacker._clock || 0, guarded }; // T3 conditions 1 / 0x1A / 0x1B / situations
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
      const _hpBeforeBlock = this.hp;
      this.hp = attacker._urgeOn ? Math.max(1, this.hp - chip) : Math.max(0, this.hp - chip);
      // GAP-FILL LANE 1: recoverable pool (T8 white gauge, verified
      // absent before this lane). Chip actually lost becomes the
      // pool; the attacker forcing the block recovers from their
      // own pool up to the chip forced. Urge Burst activates on
      // block too (T8) — soulurge.onBlockedHit already existed
      // but had no fighter-side caller for the block path.
      this._addRecoverable(_hpBeforeBlock - this.hp);
      if (attacker && typeof attacker._recoverOnAttack === 'function') attacker._recoverOnAttack(chip);
      if (move.urgeBurst && this.game && this.game.soulurge &&
          typeof this.game.soulurge.onBlockedHit === 'function') {
        this.game.soulurge.onBlockedHit(attacker, move);
      }
      this.stun = (move.t8 && move.t8.blk != null) ? stunFromAdvantage(move.t8.blk, move)
        : 0.18 + move.damage * 0.01;
      if (this.brawler) {
        const [nx, nz] = this._awayFrom(attacker);
        this.vx = nx * move.knock * 0.5;
        this.vz = nz * move.knock * 0.5;
      } else {
        this.vx = Math.sign(this.root.position.x - attacker.root.position.x) * move.knock * 0.5;
      }
      this.meter = Math.min(this.maxMeter, this.meter + 4 * this.soulMeterMult); // +4 soul on block      if (this.hp <= 0) { this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || 1); return 'ko'; }
      this._reactionSel = this._pickReaction(move, attacker, { guarded: true, counter: false,
        crouch: _wasCrouch, airborne: false, down: false, forState: 'block' });
      return 'block';
    }
    let dmg = move.damage * attacker.stats.power / this.stats.defense;
    if (attacker._maxT > 0) dmg *= KOF.MAX_DMG; // KOF XV MAX Mode
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
    // GAP-FILL LANE 1: the attacker recovers from their own
    // recoverable pool whenever they land damage (T8: recover
    // only by attacking — never over time). Applies to crush-,
    // armor- and normal-path hits alike: damage did land.
    if (attacker && typeof attacker._recoverOnAttack === 'function') attacker._recoverOnAttack(dmg);
    if (crushActive) {
      // T7 Power Crush absorb: full damage lands (see above),
      // but the swing is never interrupted — no hitstun, no
      // knockdown, no reaction clip. The absorbed hit stalls
      // the swing a few frames (T7 behavior), it does not cancel
      // it. A killing absorbed hit still KOs (armor is not
      // invulnerability — same rule as the rage-art armor path).
      this.meter = Math.min(this.maxMeter, this.meter + 6);
      // COMBAT SYSTEMS 2026-10-24 (delta on GAP-FILL LANE 1):
      // T8 rule — damage absorbed by a Power Crush becomes
      // RECOVERABLE (wavu King Muscle Armor note), capped so
      // hp + pool never exceeds maxHp.
      this._addRecoverable(Math.max(0, Math.min(dmg, this.maxHp - this.hp - (this._recoverable || 0))));
      if (this.hp <= 0) {
        this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
        return 'ko';
      }
      this.stateT = Math.max(0, this.stateT - 0.05);
      return 'hit';
    }
    if (armored) {
      // Rage lane (T7): armor absorbs — damage lands, the swing continues.
      this.meter = Math.min(this.maxMeter, this.meter + 6);
      if (this.hp <= 0) {
        this._knockout(Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing);
        return 'ko';
      }
      return 'hit';
    }
    this.meter = Math.min(this.maxMeter, this.meter + 6 * this.soulMeterMult); // +6 soul on taking damage

    const dir = Math.sign(this.root.position.x - attacker.root.position.x) || -this.facing;
    if (this.brawler) {
      // BRAWLER: knockback radiates away from the attacker on the ground
      // plane (Devil Within enemies fly away from Jin, not along x).
      const [nx, nz] = this._awayFrom(attacker);
      const k = move.knock;
      this.vx = nx * k;
      this.vz = nz * k;
    } else {
      this.vx = dir * move.knock;
    }
    if (this.hp <= 0) { this._knockout(dir); return 'ko'; }
    if (move.isGrab || move.knock >= 6 || move.launch || (counter && move.knockdown)) {
      this.vy = move.isGrab ? 5.2 : 4.6; this.onGround = false; this.stun = 0.55;
      this._juggleG = 0;
      /* Juggle airtime (moveset sweep 2026-10-29): a launcher keeps the victim airborne for the
         rest of the attacker's move plus its T8 on-hit advantage (default +30f), as in Tekken, so
         a follow-up can juggle. The pop peaks at JUGGLE_PEAK m and gravity is set from that airtime
         (a floatier arc, not a higher one). Plain knockdowns keep the 4.6 m/s pop and 22 m/s² fall. */
      if (move.launch && !move.isGrab) {
        const left = Math.max(0, (move.startup || 0) + (move.active || 0.05) + (move.recovery || 0.4) - (attacker.stateT || 0));
        const T = Math.min(1.6, Math.max(0.42, left + (move.launchAdv != null ? move.launchAdv : 30) / 60));
        this.vy = 4 * JUGGLE_PEAK / T; this._juggleG = 8 * JUGGLE_PEAK / (T * T);
      }
      this._queuedNext = null; this._queuedAfter = null; this._stepChain = null; this._stringGraceUntil = 0; // getting hit kills your string
      // Hit in the back (BT) the victim falls forward past its feet: it lands head towards the attacker.
      this._kdHeadTowards = this.stance === 'BT';
      this._enter('knockdown');
    } else {
      const t8adv = move.t8 ? (counter && move.t8.ch != null ? move.t8.ch : move.t8.hit) : null;
      this.stun = t8adv != null ? stunFromAdvantage(t8adv, move)
        : 0.2 + move.damage * 0.012 + (counter ? 0.12 : 0);
      this._queuedNext = null; this._queuedAfter = null; this._stepChain = null; this._stringGraceUntil = 0; // getting hit kills your string
      this._enter('hitstun');
    }
    // GAP-FILL LANE 1: this unguarded, non-armor, non-grab hit
    // arms the next wall splat (fighter knocked back toward a
    // wall) and may fire the combo extender. Grabs do not arm
    // it — throw victims travel by cinematic, not knockback.
    if (!move.isGrab) this._wallSplatArmed = true;
    // Combo extender (T7 Screw / T8 Tornado): airborne victim,
    // slot still free, one slot per combo. Screw = spin into a
    // slump (long window, low pop); Tornado = flip into a
    // ground-bound state (higher pop). A grounded connect, a
    // second extender in the same combo, or an Urge Burst (T8
    // pseudo-bound, which does NOT consume the slot) all fall
    // through to the normal path above. Bound is NOT touched
    // here: no Bound state machine exists in fighter.js (the
    // "bound" hits in this file are throw-pair / anim-bank
    // binding), so there is nothing to preserve — low-parry
    // Bound is flagged as follow-up work, not claimed.
    const _ek = extenderKind(move);
    if (_ek && _wasAirborne && !this._extenderUsed && !move.isGrab) {
      this._extenderUsed = true; this._extenderKind = _ek;
      if (_ek === 'screw') {
        this._inScrew = true; this.vy = 2.0;
        this.stun = Math.max(this.stun, SCREW_SLUMP_STUN);
      } else {
        this._inTornado = true; this.vy = 3.0;
        this.stun = Math.max(this.stun, TORNADO_BOUND_STUN);
      }
      this.vx = dir * (move.knock || 2) * 0.5; this.onGround = false;
      this._kdHeadTowards = true; // screw/tornado spins the body round: lands head towards
      this._enter('knockdown');
    }
    // Wall-splat follow-up (distinct from wall break): a splatted
    // victim stays stuck to the wall for WALL_SPLAT_MAX_HITS
    // hits, then drops fast (knockdown). The splat state itself
    // is entered by _physics() when knockback reaches the wall.
    if (_wasWallSplat && this.hp > 0) {
      if (this._wallSplatHits >= WALL_SPLAT_MAX_HITS) {
        this._wallSplatHits = 0;
        this.vx = dir * (move.knock || 2);
        this._kdHeadTowards = true; // slides down the wall head-first towards the attacker
        this._enter('knockdown');
      } else {
        this.vx = 0; this.vy = 0; this.stun = WALL_SPLAT_STUN;
        this._enter('wallsplat');
      }
    }
    this.stance = null; this._stanceSpins = 0;
    // Soft-body hit injection: dent the muscle volume at the impact point.
    if (this._softbody) {
      try {
        const hb = attacker && attacker.getHitbox ? attacker.getHitbox() : null;
        if (hb) { _v1.set(hb.x, hb.y, hb.z); this._softbody.hit(_v1, dir, move.damage || 8); }
      } catch (e) {}
    }
    this._reactionSel = this._pickReaction(move, attacker, { guarded, counter,
      crouch: _wasCrouch, airborne: _wasAirborne, down: _wasDown,
      forState: this.state === 'knockdown' ? 'knockdown' : 'hitstun' });
    return counter ? 'counter' : 'hit';
  }
  /* T3 reaction pick (PR #1003 data, t3-reaction-select.js; playback
     wired by the hit-reaction lane, 2026-10-24). Runs only when a
     loader has set globalThis.WH_T3_REACTIONS (parsed
     reactions.json, fetched with the bank load in t3anims.js);
     without it returns null and the generic 'hit' clip plays, as
     before. The slot itself plays through _reactionActionName,
     which resolves it defender-bank-first from the packs.
     UNMAPPED here (existing fallback kept, never a guessed clip):
     - wall splat: the decoded records carry no wall field or slot
       (record_fields has no wall entry), so a wall hit keeps the
       existing knockback; no wall reaction is invented.
     - downOther (lying the other way, state 0x200): WH has no such
       state, so downOther is always false in this pick.
     - close-range reactions when the defender's reaction pack has
       not loaded yet: the close distance is in T3 units and only
       the pack's anchor scale converts it, so close stays false
       until a pack is cached (packs prefetch at _bindT3).
     - air kind 1 (slam, needs hitDirY) and kind 5 (launch-branch
       only): WH move data carries neither, so they are never
       picked here; kinds 0/2/3/4 below are the file's rules. */
  _pickReaction(move, attacker, o) {
    try {
      const R = globalThis.WH_T3_REACTIONS;
      const rowKey = move && move.t3row;
      if (!R || rowKey == null || !attacker) return null;
      const dirOf = (f) => { const b = f && f._t3 && f._t3.bank; const base = b && T3_BANKS[b];
        return base ? base.split('/').filter(Boolean).pop() : null; };
      const aDir = dirOf(attacker), vDir = dirOf(this);
      const bankRows = aDir && R.banks[aDir] ? R.banks[aDir].rows : null;
      const row = (bankRows && bankRows[rowKey]) || (R.common_rows && R.common_rows[rowKey]) || null;
      if (!row) return null;
      const dx = attacker.root.position.x - this.root.position.x;
      const dz = attacker.root.position.z - this.root.position.z;
      const quadrant = Math.abs(dz) > Math.abs(dx) ? (dz > 0 ? 1 : 3) : (dx * this.facing > 0 ? 0 : 2);
      // Close-range substitution (docs/anim/T3-REACTIONS.md): the
      // fighters must be closer than close_reactions[closeIdx][1]
      // T3 units, converted with the defender pack's anchor scale.
      let close = false;
      const closeIdx = row[1];
      if (closeIdx && R.close_reactions && R.close_reactions[closeIdx]) {
        const vBank = vDir ? this._bankIdForDir(vDir) : null;
        const scale = vBank ? getT3ReactionPackScale(vBank) : null;
        if (scale) close = Math.hypot(dx, dz) < R.close_reactions[closeIdx][1] * scale;
      }
      // Air kind (AirReactionKind): stick in kind 2 when already in
      // an air reaction (kind 2 itself, or kinds 3/4 past frame 18
      // at 30 fps ~ 0.6 s of state time); else the quadrant side
      // kinds; else kind 0. Kind 1/5 are UNMAPPED (see header).
      let airKind = 0;
      if (o.airborne && R.air_kinds) {
        const prev = this._reactionSel;
        const airSlots = R.air_kinds.map((k) => k[1]);
        if (prev && airSlots.includes(prev.slot) && (prev.slot === 3426 || this.stateT > 0.6)) airKind = 2;
        else if (quadrant === 1) airKind = 4;
        else if (quadrant === 3) airKind = 3;
      }
      const sel = selectReactionSlot(R, row, { guarded: !!o.guarded, crouch: !!o.crouch, counter: !!o.counter,
        airborne: !!o.airborne, down: !!o.down, quadrant, close, airKind });
      if (!sel) return null;
      this._reactChainDepth = 0;
      return { ...sel, bank: vDir, defenderDir: vDir, attackerDir: aDir, forState: o.forState || null };
    } catch (e) { return null; }
  }

  /* Reaction playback (hit-reaction wiring lane, 2026-10-24).
     _ensureReactionAction fetches the owning bank's pack (once)
     and retargets ONLY the picked slot into a 'react:<slot>' action
     — defender bank first, attacker bank second, exactly as the
     file's DivmotMergeSharedSlots lookup orders it. A slot no pack
     defines returns null from the loader and the caller keeps its
     generic fallback (UNMAPPED, never guessed). */
  _ensureReactionAction() {
    const rs = this._reactionSel;
    if (!rs || !this._t3 || !this._t3.model) return;
    const name = 'react:' + rs.slot;
    if (this.t3actions[name] || this._reactLoading === name) return;
    const R = globalThis.WH_T3_REACTIONS;
    if (!R) return;
    const ownerDir = reactionSlotBank(R, rs.defenderDir, rs.attackerDir, rs.slot);
    const bankId = ownerDir ? this._bankIdForDir(ownerDir) : null;
    if (!bankId) return; // UNMAPPED: owning bank has no pack path (forestlaw_on_law)
    this._reactLoading = name;
    loadT3ReactionClip(THREE, bankId, rs.slot, { noRise: rs.code === 0x24 })
      .then((clip) => {
        this._reactLoading = null;
        if (!clip) return;
        const rc = retargetT3Clips({ [name]: clip }, bankId, this._t3.model, THREE, this._t3.modelKey, [name]);
        if (rc && rc[name]) Object.assign(this.t3actions, createT3Actions(this.mixer, rc, THREE));
      })
      .catch(() => { this._reactLoading = null; });
  }

  /* The reaction action to play this frame, or null for the caller's
     generic fallback. Follows the file's continuation chain
     (bank slots[].next) when a clip finishes, until a slot whose
     next is itself — then the finished pose is held (_chainDone)
     instead of replaying a generic clip. Block is the exception:
     a finished guard reaction falls back to the block loop. */
  _reactionActionName() {
    const rs = this._reactionSel;
    // A 'block' pick also matches while its blockstun runs, because
    // receiveHit never _enters 'block': guarded hits land in idle,
    // walk or crouch when the defender is holding back.
    const stateMatch = rs && (rs.forState === this.state ||
      (rs.forState === 'block' && this.stun > 0 &&
        (this.state === 'idle' || this.state === 'walk' || this.state === 'crouch')));
    if (!rs || !stateMatch) return null;
    this._ensureReactionAction();
    const name = 'react:' + rs.slot;
    const a = this.t3actions[name];
    if (!a) return null;
    if (this._t3current === a) {
      if (a.isRunning()) return name;
      const R = globalThis.WH_T3_REACTIONS;
      const ownerDir = R ? reactionSlotBank(R, rs.defenderDir, rs.attackerDir, rs.slot) : null;
      const plan = ownerDir && R.banks[ownerDir] && R.banks[ownerDir].slots
        ? R.banks[ownerDir].slots['0x' + (rs.slot & 0xffff).toString(16)] : null;
      const next = plan ? plan.next : null;
      if (next == null || next === rs.slot || this._reactChainDepth >= 8) {
        if (this.state === 'block') return null;
        this._reactionSel = { ...rs, _chainDone: true };
        return null;
      }
      this._reactChainDepth++;
      this._reactionSel = { ...rs, slot: next, field: 'chain' };
      this._ensureReactionAction();
      const nextName = 'react:' + next;
      return this.t3actions[nextName] ? nextName : null;
    }
    return name;
  }

  /* Guard reaction override for locomotion states: a guarded hit
     does not change state, so idle/walk/crouch check for a live
     guard reaction before playing their locomotion clip. */
  _guardReactionName() {
    const rs = this._reactionSel;
    if (!rs || rs.code !== 0x23 || this.stun <= 0) return null;
    return this._reactionActionName();
  }

  _knockout(dir) {
    this.dead = true; this.vx = dir * 5.5; this.vy = 6; this.onGround = false;
    if (this.brawler) {
      // BRAWLER: keep the 3D knockback velocity receiveHit computed,
      // boosted to KO strength — the body flies away from the attacker.
      const s = Math.hypot(this.vx, this.vz);
      if (s > 0.01) {
        const k = 7.5 / s;
        this.vx *= k; this.vz *= k;
      } else { this.vx = dir * 5.5; this.vz = 0; }
    }
    // KO collapse (docs/anim/T3-REACTIONS.md): a KO'd fighter plays
    // the collapse slot 0xD66 from the file, not the generic ko clip,
    // when the tables are loaded; otherwise the ko fallback below.
    try {
      const R = globalThis.WH_T3_REACTIONS;
      const b = this._t3 && this._t3.bank, base = b && T3_BANKS[b];
      const vDir = base ? base.split('/').filter(Boolean).pop() : null;
      this._reactionSel = (R && R.collapse_slot != null)
        ? { record: 0, field: 'ko', slot: R.collapse_slot, code: 0, push: null, angle: null,
            bank: vDir, defenderDir: vDir, attackerDir: null, forState: 'ko' } : null;
      this._reactChainDepth = 0;
    } catch (e) { this._reactionSel = null; }
    this._queuedNext = null; this._queuedAfter = null; this._stepChain = null; this._stringGraceUntil = 0; // getting hit kills your string
    this._enter('ko'); this.stun = 999;
  }
  victory() { if (!this.dead) this._enter('victory'); }
  addMeter(v) { this.meter = Math.min(this.maxMeter, this.meter + v * this.soulMeterMult); }

  /* ---------------- hit / hurt queries (swept capsules, hitbox.js) ----------------
     HITBOX LANE 2026-10-24 (owner playtest: "contacts not being made"):
     - Hitbox = the weapon limb's SEGMENT (elbow->fist, knee->foot)
       at this frame + the weapon point's TRAVEL segment (previous
       frame -> this frame), so a fast limb cannot step past a hurt
       capsule between 120 Hz ticks. 'both'-limb moves sweep BOTH
       arms (the old code swept only the right hand).
     - Hurtbox = 14 capsules over the LIVE posed bones (hitbox.js
       HURT_SEGMENTS). A rig missing a bone falls back to the
       root-anchored twin for that segment; a rig missing the core
       bones falls back to all 14 root-anchored capsules — a live,
       hittable defender NEVER returns [] any more (the old
       Spine1+Head-only shape returned [] for foreign rigs, which
       silently disabled game.js's range fallback too, since that
       fallback requires hurts.length > 0).
     - x/y/z/r on the returned hitbox stay the weapon endpoint +
       radius, so existing readers (game.js FX, soft-body, xray)
       keep working; segments/travel/limb are additive. */
  _weaponSegments() {
    // Tekken notation: 3/4 are kicks -> foot; throws/specials use the move's limb
    const limb = this.attack?.limb || '';
    let key = 'armR';
    if (limb === 'both') key = 'both';
    else if (limb.startsWith('leg') || this.attackName === 'kick' || this.attackName === '3' || this.attackName === '4') {
      key = limb === 'legL' ? 'legL' : 'legR';
    } else if (limb === 'armL') key = 'armL';
    return WEAPON_SEGMENTS[key];
  }
  _weaponBone() {
    // Kept for any external reader: the endpoint of the first weapon segment.
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
    const isGrab = !!(this.attack?.isGrab || this.attackName === 'grab' || this.attackName === '1+3' || this.attackName === '2+4');
    // GAP-FILL LANE 1 (per-move hitbox, ENGINE side): when the
    // moveset lane has authored per-move geometry, its radius /
    // reach replace the generic capsule values; when absent
    // (UNMAPPED — the current state of every WH moveset), the
    // generic values below stand, honestly, with no invented box.
    const _pm = resolvePerMoveHitbox(this.attack);
    let r = (this.attackName === 'surge' ? LIMB_RADIUS.surge : isGrab ? LIMB_RADIUS.grab : LIMB_RADIUS.strike)
      * (this.stats.reachMult || 1); // WOOD force (modes lane): reach extends
    if (_pm.mapped && _pm.radius != null) r = _pm.radius * (this.stats.reachMult || 1);
    const segments = [];
    let end = null;
    for (const seg of this._weaponSegments()) {
      const na = this.bones[seg.a], nb = this.bones[seg.b];
      if (na && nb) {
        na.getWorldPosition(_v1); nb.getWorldPosition(_v2);
        segments.push({ ax: _v1.x, ay: _v1.y, az: _v1.z, bx: _v2.x, by: _v2.y, bz: _v2.z });
        end = { x: _v2.x, y: _v2.y, z: _v2.z };
      }
    }
    if (!segments.length) {
      // No rig bone (T-pose/procedural): frame-data box, as before.
      end = { x: this.root.position.x + this.facing * 0.8, y: this.root.position.y + 1.2, z: this.root.position.z };
      segments.push({ ax: end.x, ay: end.y, az: end.z, bx: end.x, by: end.y, bz: end.z });
    }
    // Swept travel: previous frame's weapon point -> this frame's.
    let travel = null;
    if (this._prevHitPoint && end) {
      travel = { ax: this._prevHitPoint.x, ay: this._prevHitPoint.y, az: this._prevHitPoint.z,
                 bx: end.x, by: end.y, bz: end.z };
    }
    this._prevHitPoint = end;
    return { x: end.x, y: end.y, z: end.z, r, move: this.attack, segments, travel,
             limb: this.attack?.limb || null, perMoveHitbox: _pm,
             reach: ((_pm.mapped && _pm.reach != null) ? _pm.reach
               : moveReach(this.attack, String(this.attackName || ''))) * (this.stats.reachMult || 1) };
  }
  getHurtboxes() {
    if (this.invuln > 0 || this.dead) return [];
    // Throw cinematic: both locked fighters are committed, not hittable.
    if (this.state === 'thrown' || this.state === 'throwing' ||
        this.state === 'thrownExec' || this.state === 'throwExec') return [];
    const out = [];
    let fbById = null;
    for (const def of HURT_SEGMENTS) {
      const na = this.bones[def.a], nb = this.bones[def.b];
      if (na && nb) {
        na.getWorldPosition(_v1); nb.getWorldPosition(_v2);
        out.push({ id: def.id, band: def.band, r: def.r,
          x1: _v1.x, y1: _v1.y, z1: _v1.z, x2: _v2.x, y2: _v2.y, z2: _v2.z,
          x: (_v1.x + _v2.x) / 2, y: (_v1.y + _v2.y) / 2, z: (_v1.z + _v2.z) / 2 });
      } else {
        // Missing bone: the root-anchored twin, never a dropped segment.
        // Built lazily, only when a rig actually lacks a bone.
        if (!fbById) {
          const crouch = this.state === 'crouch' || this.stance === 'FC';
          fbById = new Map(fallbackHurts(this.root.position, this.facing, crouch).map((s) => [s.id, s]));
        }
        out.push(fbById.get(def.id));
      }
    }
    // GAP-FILL LANE 1 (per-move hurtbox, ENGINE side): only when
    // the defender's current move itself authors a radiusScale
    // does it scale these capsules; otherwise they stand exactly
    // as before. No scale is ever guessed from limb or class.
    const _ph = resolvePerMoveHurtbox(this.attack);
    if (_ph.mapped && _ph.radiusScale != null) {
      for (const h of out) if (h) h.r = h.r * _ph.radiusScale;
    }
    return out;
  }
  registerHit() { this.hasHit = true; this.addMeter(this.attack.soulGain); }
  registerCombo() { this.combo++; this._comboTimer = 1.2; return this.combo; }

  /* ---------------- per-frame update ---------------- */
  update(dt, opponent) {
    this._opp = opponent;
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
    if (this._maxT > 0) this._maxT = Math.max(0, this._maxT - dt);
    if (this._sysVx && this.state === 'attack' && this.attack && this.attack.system) this.vx = this._sysVx;
    else this._sysVx = 0;
    if (this._vbreakT > 0) this._vbreakT -= dt;
    if (this._vparryT > 0) this._vparryT -= dt;
    if (this._risingT > 0) this._risingT -= dt;
    if (this.stanceT > 0) { this.stanceT -= dt; if (this.stanceT <= 0) { this.stance = null; this._stanceSpins = 0; } }
    // GAP-FILL LANE 1: combo ends when the victim recovers to
    // neutral on the ground — juggle count AND the single
    // extender slot both clear here, never mid-combo.
    if (this.onGround && this.state !== 'knockdown') {
      this._juggle = 0;
      this._extenderUsed = false; this._extenderKind = null;
      this._inScrew = false; this._inTornado = false;
      if (this.state !== 'wallsplat') this._wallSplatArmed = false;
    }
    if (this._comboTimer > 0) { this._comboTimer -= dt; if (this._comboTimer <= 0) this.combo = 0; }
    if (this._auraFlash > 0) this._auraFlash -= dt;
    if (this._urgeDashT > 0) {
      this._urgeDashT -= dt;
      if (this.onGround && this.state === 'dash') this.vx = this.facing * 9;
      if (this._urgeDashT <= 0 && this.state === 'dash') { this._enter('idle'); this.vx = 0; }
    }
    // SOUL SURGE FORM (brawler devil-form analog): timed — drains meter.
    if (this.surgeForm) {
      this._surgeT -= dt;
      this.meter = Math.max(0, this.meter - 4 * dt);
      if (this._surgeT <= 0 || this.meter <= 0) this.endSurgeForm();
    }

    // BRAWLER: facing is yaw-driven by the brawler controller (free 3D) —
    // never x-snap toward a single opponent.
    if (opponent && this.canAct() && !this.brawler) {
      const want = opponent.root.position.x >= this.root.position.x ? 1 : -1;
      if (want !== this.facing) this.facing = want;
      // QA 2026-10-23 targeting fix (T7 tracking): in neutral a fighter turns to
      // face the opponent in 3D, not just along x, so after a sidestep the
      // body and the next attack point at the opponent.
      this._faceYaw = Math.atan2(opponent.root.position.x - this.root.position.x,
        opponent.root.position.z - this.root.position.z);
    }

    this._tickState(dt);
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

  /* Shared-root-frame drive for a paired throw (doc formula):
     each fighter's root follows its own clip's ax/az anchor
     around the pair anchor P, at the thrower's anchor scale,
     with lean yaw H + the clip's yaw0. Frame = pair clock at
     30 fps (the packs' fps), clamped to the clip length. */
  _driveThrowPair() {
    const pair = this._throwPair;
    if (!pair) return;
    const isThrower = pair.thrower === this;
    const row = isThrower ? pair.throwerPackRow : pair.victimPackRow;
    if (!row) return;
    const f = Math.floor((this._throwPairT || 0) * 30);
    const a = anchorAt(row, f);
    const pos = sharedFramePos(pair.anchor, pair.hYaw, a, pair.anchorScale || 0);
    this.root.position.x = pos.x;
    this.root.position.z = pos.z;
    this._faceYaw = pair.hYaw + (row.yaw0 || 0);
  }
  _tickState(dt) {
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
          // BATCH STRING FIX (2026-10-24): a string hit queued during this move
          // fires on completion, not just during recovery — short moves can jump
          // active->done in one tick, skipping recovery and dropping the queued
          // hit, which broke 3+ hit strings (user: longest combo was 1-2).
          // A user-queued hit cancels any auto step chain (player driving).
          if (this._queuedNext) this._stepChain = null;
          // Whole-string step chain advances on completion, like a queued hit.
          if (this._advanceStepChain()) break;
          if (this._queuedNext) {
            const next = this._queuedNext; this._queuedNext = null;
            this.attack = null; this.attackName = null;
            if (this._fireNotation(next)) break;
            this._enter('idle');
          } else {
            // T3 condition 0x1C (own whiff): an attack that recovers without hitting counts as a
            // whiff for the branch pressed within CONTACT_WINDOW after it, not only a cancelled one.
            if (!this.hasHit) this._t3Whiff = this._clock || 0;
            this.attack = null; this.attackName = null; this._enter('idle');
          }
          // String grace starts when a non-grab attack completes (see _tryAttackFresh).
          // BATCH: 200 -> 500 ms for touch cadence (phone taps are slower than stick).
          if (!m.isGrab) this._stringGraceUntil = (typeof performance !== 'undefined' ? performance.now() : 0) + 500;
          // Source notes "Transition to X": the move ends in that stance (FC = crouch).
          if (after === 'FC') { this._enter('crouch'); this.stance = 'FC'; this.stanceT = 0.5; }
          else if (after) { this._stanceSpins = this._spinNext || 1; this.stance = after; this.stanceT = 0.8; }
        }
        // Buffered string hit fires once this hit's active frames are over.
        if (this._queuedNext && this.state === 'attack' && this._attackPhase === 'recovery') {
          this._stepChain = null; // user-queued hit replaces the auto chain
          const next = this._queuedNext; this._queuedNext = null;
          this.state = 'idle'; // release the current hit into the next one
          if (!this._fireNotation(next)) this.state = 'attack';
        } else if (this._stepChain && this.state === 'attack' && this._attackPhase === 'recovery') {
          // Whole-string step chain advances during recovery, like a queued hit.
          // (Inline, not _advanceStepChain: on a failed fire the current attack
          // must survive, so attack/attackName are only replaced by _fireNotation.)
          const ch = this._stepChain;
          if (ch.idx + 1 < ch.steps.length) {
            const next = ch.steps[ch.idx + 1].prefix;
            ch.idx += 1;
            this.state = 'idle';
            if (!this._fireNotation(next)) { this.state = 'attack'; this._stepChain = null; }
          } else this._stepChain = null;
        }
        break;
      }
      case 'crouch': break;
      case 'jump': if (this.onGround) this._enter('idle'); break;
      case 'hitstun': if (this.stun <= 0) this._enter('idle'); break;
      case 'knockdown': if (this.onGround && this.stun <= 0) {
        this._enter('idle');
        /* Tekken ground state (sweep 2026-10-29): leaving a knockdown the fighter is still on
           its back for a short window; moves listed 'while on back[, feet towards opponent]'
           (FUFT.) are pressed from it, like any stance prefix. Only when the moveset has them. */
        const gs = this._kdHeadTowards && this._hasGroundMoves('FUHT') ? 'FUHT' : 'FUFT';
        if (this._hasGroundMoves(gs)) { this.stance = gs; this.stanceT = 0.6; }
        this._kdHeadTowards = false;
      } break;
      // GAP-FILL LANE 1: wall splat sticks the victim to the
      // wall for its stun window; expiry returns to neutral and
      // clears the splat hit count (the 3-hit drop is in
      // receiveHit, not here — expiry is not a hit).
      case 'wallsplat': if (this.stun <= 0) { this._wallSplatHits = 0; this._enter('idle'); } break;
      case 'dodge': if (this.stateT > 0.34) { this.vx = 0; this._enter('idle'); } break;
      case 'vshift':
        // V-Shift: invulnerable backshift; game.js may proc the evade.
        if (this.stateT >= V.SHIFT_DURATION) { this.vx = 0; this._enter('idle'); }
        break;
      case 'sidestep':
        if (this.stateT > 0.55) { this.vz = 0; this._enter('idle'); }
        break;
      case 'thrown':
      case 'throwing': {
        if (this._throwPair) {
          // Paired throw: shared-root-frame drive + pair clock.
          // Both clips started on the same frame; the break window
          // ends -> both fighters move to the exec states WITHOUT
          // restarting the clips (mixer time is the pair clock's
          // twin; _throwPairT is the logic clock and is NOT reset
          // by _enter, so damage/end timing survives the switch).
          this._throwPairT = (this._throwPairT || 0) + dt;
          this._driveThrowPair();
          const brk = this._throwPair.breaks && this._throwPair.breaks[0];
          const winEnd = brk ? brk.windowSec[1] : 0;
          if (this._throwPairT > winEnd) {
            this._enter(this.state === 'throwing' ? 'throwExec' : 'thrownExec');
          }
          break;
        }
        // Throw-lock: game.js resolves the lock when the break window
        // (lockT) expires, so hit feedback stays in one place.
        break;
      }
      case 'throwExec': {
        if (this._throwPair) {
          this._throwPairT = (this._throwPairT || 0) + dt;
          this._driveThrowPair();
          if (this._throwPairT >= this._throwPair.durationSec) {
            if (this._chainNext && this._startThrowChain(this._throwPair.victim)) break;
            this._throwPair = null; this._throwPairT = 0;
            this._throwVictim = null; this._throwMove = null; this._chainFrom = null; this._chainSeq = [];
            this._enter('idle'); this._endThrowFollow();
          }
          break;
        }
        // Attacker performing the throw: lift, slam, recover (0.9s total).
        // Damage lands at the slam (t=0.55s) via the victim's _throwSlamDamage.
        if (this.stateT >= 0.9) {
          if (this._chainNext && this._startThrowChain(this._throwVictim)) break;
          this._throwVictim = null; this._throwMove = null; this._chainFrom = null; this._chainSeq = [];
          this._enter('idle'); this._endThrowFollow();
        }
        break;
      }
      case 'thrownExec': {
        if (this._throwPair) {
          this._throwPairT = (this._throwPairT || 0) + dt;
          this._driveThrowPair();
          const pair = this._throwPair;
          if (pair.damageTimeSec != null && !pair.hitDone && this._throwPairT >= pair.damageTimeSec) this._throwPairDamage();
          if (this._throwPairT >= pair.durationSec) {
            if (!pair.hitDone) this._throwPairDamage();
            const dead = this.dead;
            this._throwPair = null; this._throwPairT = 0;
            this._throwAttacker = null; this._throwMove = null;
            if (!dead) { this.stun = 0.55; this._enter('knockdown'); }
            // dead: _throwPairDamage already _knockout'd into 'ko'; do not override it.
          }
          break;
        }
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
        // BRAWLER: walk on 2D ground speed, not the 1v1 x-axis.
        this.state = ((this.brawler ? Math.hypot(this.vx, this.vz) : Math.abs(this.vx)) > 0.4 && this.onGround) ? 'walk' : 'idle';
        break;
    }
  }

  _physics(dt, opponent) {
    // Throw execution: positions are driven by _tickState (lift/slam),
    // so physics must not integrate velocity or gravity here.
    const inThrowAnim = this.state === 'throwExec' || this.state === 'thrownExec';
    if (!inThrowAnim) {
      if (!this.onGround) this.vy -= ((this._juggleG && this.state === 'knockdown') ? this._juggleG : 22) * dt;
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
      if (this._ssAlign && this.state === 'attack' && this.onGround && opponent) {
        // the step's re-aligned axis: back onto the fight line through the move, body
        // turned at the opponent the whole way (see _enter)
        this.root.position.z += (opponent.root.position.z - this.root.position.z) * (1 - Math.pow(1e-5, dt));
        this._faceYaw = Math.atan2(opponent.root.position.x - this.root.position.x, opponent.root.position.z - this.root.position.z);
      } else if (this.canAct() && this.onGround && this.vz === 0) {
        this.root.position.z *= Math.pow(0.004, dt);
        if (Math.abs(this.root.position.z) < 0.01) this.root.position.z = 0;
      }
    }
    if (!inThrowAnim) {
      this.root.position.x += this.vx * dt;
      this.root.position.y += this.vy * dt;
      this.root.position.z += this.vz * dt;
    }
    // ROOT MOTION (2026-10-24): attack-clip travel, applied here so the
    // arena clamp and body-vs-body pushout below see it this same frame
    // (wall: clamped to ARENA_LIMIT; opponent: pushed apart, never passed
    // through). Does not touch y; does not run for block/sidestep/jump.
    this._rootMotionApply();
    // Sidestep range: about one body width into the background/foreground.
    // BRAWLER: free 3D — clamp to the arena bounds instead.
    const zLim = this.brawler ? ARENA_LIMIT : 2.4;
    this.root.position.z = Math.max(-zLim, Math.min(zLim, this.root.position.z));

    if (this.root.position.y <= GROUND_Y) {
      this.root.position.y = GROUND_Y; this.vy = 0; this._juggleG = 0;
      if (!this.onGround) {
        this.onGround = true;
        if (this.state === 'knockdown') {
          // GAP-FILL LANE 1: a Screw slump / Tornado bound keeps
          // its follow-up window on landing instead of collapsing
          // to the generic 0.4 s knockdown floor.
          this.stun = Math.max(this.stun, (this._inScrew || this._inTornado) ? EXTENDER_LAND_STUN_FLOOR : 0.4);
        }
      }
    }
    this.root.position.x = Math.max(-ARENA_LIMIT, Math.min(ARENA_LIMIT, this.root.position.x));

    // GAP-FILL LANE 1: wall splat (DISTINCT from wall break).
    // A knockback victim armed by a landed hit (see receiveHit)
    // who reaches the arena wall sticks to it in 'wallsplat'
    // instead of sliding along it. Breaks do not false-trigger
    // this: stagebreaks.checkHit() runs before the next physics
    // tick and extends ARENA_LIMIT on a break, so a broken wall
    // is no longer at the limit by the time this check runs.
    // PROPRIETARY NAME for this state: NEEDS NAME (owner names).
    if (this._wallSplatArmed && (this.state === 'hitstun' || this.state === 'knockdown') &&
        Math.abs(this.root.position.x) >= ARENA_LIMIT - 0.01) {
      this._wallSplatArmed = false;
      this.vx = 0; this.vy = 0; this.stun = Math.max(this.stun, WALL_SPLAT_STUN);
      this._wallSplatHits = 0;
      this._enter('wallsplat');
      if (this.game && this.game.stageBreaks && typeof this.game.stageBreaks.noteSplat === 'function') {
        try { this.game.stageBreaks.noteSplat(opponent, this); } catch (e) { /* record-only hook */ }
      }
    }

    // Body-vs-body pushout, T7/T8 style (owner bug 2026-10-23: cross-ups impossible).
    // Tekken pushboxes are ground collision cylinders: while airborne the box
    // shrinks and is off above the opponent's waist, so a jump arc can pass
    // over and land on the far side (facing re-resolves on landing). Ground
    // push is split between both bodies; when one is against the stage wall
    // the remaining push goes to the other body, so nobody leaves the stage.
    if (opponent && !this._throwPair) {
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
    // BRAWLER: yaw drives the facing directly in free 3D (brawler.js updates
    // f.yaw per frame); sync it into _faceYaw so the facing line below stays
    // the single source of truth in both modes.
    if (this.brawler) this._faceYaw = this.yaw;
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
    // BRAWLER: velocity is 2D (vx+vz) — compare its heading against the
    // facing yaw instead of the 1v1 x-axis sign.
    const _bSpd = this.brawler ? Math.hypot(this.vx, this.vz) : 0;
    let dirSign;
    if (this.brawler && _bSpd > 0.05) {
      const _va = Math.atan2(this.vx, this.vz);
      const _dd = Math.atan2(Math.sin(_va - this.yaw), Math.cos(_va - this.yaw));
      dirSign = Math.abs(_dd) > Math.PI / 2 ? -1 : 1;
    } else {
      dirSign = Math.abs(this.vx) > 0.05 ? (Math.sign(this.vx) === this.facing ? 1 : -1) : 1;
    }
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
      const _spdNow = this.brawler ? Math.hypot(this.vx, this.vz) : Math.abs(this.vx);
      const fast = _spdNow > this.stats.speed * 0.9;
      tIdle = 0; tWalk = fast ? 0 : 1; tRun = fast ? 1 : 0;
    } else if (this.state === 'dodge') { tIdle = 0; tRun = 1; }
    if (t3Active || this._throwPair) { tIdle = 0; tWalk = 0; tRun = 0; }
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

    // 4b) CANON SIZING (game/data/canon-sizing.js): once per model/form, after
    // the stance has posed a couple of frames, scale the root so the stance
    // height matches this version's canon height (+ girth). No mesh is cut.
    if (this._canonSizedKey !== this.formKey && ++this._canonSizeTick > 2) {
      this._canonSizedKey = this.formKey; this._canonSizeTick = 0;
      try {
        const cs = canonRootScale(this.formKey, this.model, this.root);
        if (cs) {
          this.root.scale.set(cs.w, cs.h, cs.w);
          this.canonSize = { key: this.formKey, h: cs.h, w: cs.w, measured: cs.measured, height_cm: cs.entry.height_cm, girth: cs.entry.girth };
          console.log(`[SIZE] ${this.formKey} stance=${cs.measured.toFixed(3)} -> ${cs.entry.height_cm}cm scale h=${cs.h.toFixed(3)} w=${cs.w.toFixed(3)}`);
        }
      } catch (e) { /* sizing is cosmetic: never break the fight */ }
    }

    // 5) Refresh world matrices so IK reads the posed skeleton
    this.root.updateWorldMatrix(true, true);

    // 6) Combat override layer (IK) + lean targets
    this._leanT.x = 0; this._leanT.z = 0;
    this.trail.visible = false;
    // REAL T3 clips per state (falls back to procedural if unavailable)
    switch (this.state) {
      case 'idle':
      case 'walk': {
        // Guard reaction during blockstun overrides locomotion.
        const grn = this._guardReactionName();
        if (grn) { this._playT3Once(grn, 'react:' + this._reactionSel.slot); break; }
        // Animated bank stance / walk cycle — the living fighting idle.
        if (t3Active) this._playT3(t3Wanted, { loop: true });
        else this._stopT3();
        break;
      }
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
      case 'block': {
        // Guard reaction (record guard field, code 0x23) when the
        // pack has it; otherwise the block loop, as before. When
        // the guard clip finishes, the block loop resumes.
        const rn = (this._reactionSel && this._reactionSel.code === 0x23) ? this._reactionActionName() : null;
        if (rn) this._playT3Once(rn, 'react:' + this._reactionSel.slot);
        else if (!this._playT3('block', { loop: true })) this._animBlock();
        break;
      }
      case 'crouch': {
        // Guard reaction during blockstun overrides the crouch hold.
        const grn = this._guardReactionName();
        if (grn) { this._playT3Once(grn, 'react:' + this._reactionSel.slot); break; }
        // Bank crouch hold (T3 crouching stance, slot 40) — the posture lows/FC moves use.
        if (!(t3Active && this._playT3(t3Wanted, { loop: true, fade: 0.08 }))) { this._leanT.x = 0.25; this._stopT3(); }
        break;
      }
      case 'hitstun': {
        this._leanT.x = 0.28;
        // File reaction clip (stagger / crumple chain / counter
        // reaction, per the picked record field) when its pack slot
        // has loaded; otherwise the generic 'hit' clip (UNMAPPED
        // fallback — the pairing is never guessed).
        const rn = this._reactionActionName();
        if (rn) this._playT3Once(rn, 'react:' + this._reactionSel.slot);
        else if (!this._reactionSel || !this._reactionSel._chainDone) this._playT3Once('hit', 'hit:' + Math.floor(this.stateT * 10));
        break;
      }
      case 'knockdown': {
        this._leanT.x = Math.min(0.9, this.stateT * 3.0);
        // Launch / air / down reaction when the hit that caused
        // this knockdown picked one; throw knockdowns stay generic
        // here (the grapple lane owns throw victim playback).
        const rn = this._throwAttacker ? null : this._reactionActionName();
        if (rn) this._playT3Once(rn, 'react:' + this._reactionSel.slot);
        else if (!this._reactionSel || !this._reactionSel._chainDone) this._playT3Once('launch', 'kd:' + Math.floor(this.stateT * 10));
        break;
      }
      case 'ko': {
        this._leanT.x = Math.min(0.9, this.stateT * 3.0);
        // Collapse slot 0xD66 + its file get-up chain when loaded;
        // otherwise the generic 'ko' clip.
        const rn = this._reactionActionName();
        if (rn) this._playT3Once(rn, 'react:' + this._reactionSel.slot);
        else if (!this._reactionSel || !this._reactionSel._chainDone) this._playT3Once('ko', 'ko:' + Math.floor(this.stateT * 10));
        break;
      }
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
        // Paired throw: the thrower's slot clip (NOT the grab action).
        // _playT3 does not restart an already-running action, so this
        // same action continues into throwExec below, in sync with
        // the victim's clip. Break cue comes from the file's break
        // input, not from the WH move's throw_break.
        if (this._throwPair) {
          this._leanT.x = 0;
          this._playT3(this._throwPair.throwerAction, { loop: false });
          const brk = this._throwPair.breaks && this._throwPair.breaks[0] ? this._throwPair.breaks[0].input : null;
          const pulse = 0.55 + 0.45 * Math.sin(performance.now() * 0.03);
          if (brk === '1') this._showTrail(this.bones.LeftHand, pulse);
          else if (brk === '2') this._showTrail(this.bones.RightHand, pulse);
          else { this._showTrail(this.bones.RightHand, pulse); this._showTrail(this.bones.LeftHand, pulse * 0.9); }
          break;
        }
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
        // Paired throw: the victim's slot clip (the receiver clip),
        // same action continuing into thrownExec below.
        if (this._throwPair) {
          this._leanT.x = 0;
          if (!this._playT3(this._throwPair.victimAction, { loop: false })) this._stopT3();
          break;
        }
        // Victim caught: rocked back, arms up (T3 hit reaction when bound).
        this._leanT.x = 0.3;
        if (!this._playT3Once('hit', 'thrown')) this._stopT3();
        break;
      case 'throwExec': {
        if (this._throwPair) {
          this._leanT.x = 0;
          if (!this._playT3(this._throwPair.throwerAction, { loop: false })) this._stopT3();
          break;
        }
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
        if (this._throwPair) {
          this._leanT.x = 0;
          if (!this._playT3(this._throwPair.victimAction, { loop: false })) this._stopT3();
          break;
        }
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
    const auraOn = (this.attackName === 'surge') || this._auraFlash > 0 || this._rageAura || this._urgeAura || this.surgeForm;
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

  /* World-space forward vector (brawler: from yaw; versus: from x-facing).
     Used by the procedural combat layer so strikes aim where the body faces. */
  fwdVec(out) {
    if (this.brawler) return out.set(Math.sin(this.yaw), 0, Math.cos(this.yaw));
    return out.set(this.facing, 0, 0);
  }

  _attackProgress() {
    const m = this.attack, t = this.stateT;
    const extendEnd = m.startup + m.active;
    let ext = t < extendEnd ? t / extendEnd : 1 - (t - extendEnd) / m.recovery;
    ext = Math.max(0, Math.min(1, ext));
    return ext * ext * (3 - 2 * ext); // smoothstep
  }

  _animAttack() {
    // Rigs without Hips/Spine2 (e.g. cainelias) skip the procedural
    // attack lean — the authored clip still plays; this used to throw
    // every frame and abort the attack.
    if (!this.bones || !this.bones.Hips || !this.bones.Spine2) return;
    const e = this._attackProgress();
    const fwd = this.fwdVec(_v3); // world forward (yaw-aware in brawler mode)
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
    if (!this.bones || !this.bones.Hips || !this.bones.Spine2) return; // non-standard rig: clip only
    this._blendW = Math.min(0.9, (this._blendW || 0) + 0.18);
    this._leanT.x = 0.06;
    this.bones.Spine2.getWorldPosition(_v1);
    const fwd = this.fwdVec(_v3);
    _v2.copy(_v1).addScaledVector(fwd, 0.42); _v2.y = _v1.y + 0.35;
    this._ik(['RightArm', 'RightForeArm'], 'RightHand', _v2, this._blendW);
    _v2.copy(_v1).addScaledVector(fwd, 0.42); _v2.y = _v1.y + 0.2;
    this._ik(['LeftArm', 'LeftForeArm'], 'LeftHand', _v2, this._blendW);
  }
  /* Procedural throw execution (no T3 throw clip bound): arms haul the
     victim up overhead during the lift, then drive down for the slam. */
  _animThrowExec(t) {
    if (!this.bones || !this.bones.Hips || !this.bones.Spine2) return; // non-standard rig: clip only
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
    if (!this.bones || !this.bones.Hips || !this.bones.Spine2) return; // non-standard rig: clip only
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
