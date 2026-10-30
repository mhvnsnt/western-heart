/* T3 branch-row conditions (gen-movesets-t3.py `t3_condition`).
   Semantics decoded from n0madic/Tekken3Remake docs/research/code/moves.md#branch-conditions
   (BranchCondition 0x8002E310, verified there against the original code in an emulated CPU):
   0 always, 1 contact, 2-0x13 throw situation, 0x14-0x17 situation pairs, 0x18/0x19 near/far,
   0x1A hit, 0x1B guarded, 0x1C whiffed, 0x1D-0x23 opponent action/posture, 0x24-0x2E facing,
   0x2F never, 0x30 high attack incoming, 0x31/0x32 knock-down recovery, 0x33/0x34 body contact,
   0x35-0x38 opponent down, 0x39 counter hit, 0x3A-0x3C button taps, 0x3D KO, 0x3E-0x41 side
   flag, 0x42 not launched, 0x43/0x44 power timer, 0x45-0x4B reversals (hit incoming).
   WH is a 2.5D game: heading is facing +-1 (back turned = BT stance or facing away), the
   opponent's side quadrants 1/3 are its sidestep, and the row parameter P is not extracted,
   so the distance tests use the game's own throw / close ranges. */
const BODY = 1.5;      // bodies in contact: grounded fighters are held 1.45 m apart (fighter.js)
const CLOSE = 1.6;     // near range (m)
const SITUATION_RANGE = 2.0; // contact follow-up range: own hit + its pushback (row P not extracted)
const HIGH_RANGE = 2.0; // 0x30: dist < 0x700
const CONTACT_WINDOW = 1.5; // s: contact of the move just played still counts for the branch pressed out of it

export const T3_CONDITION_NAMES = {
  0: 'always', 1: 'own attack made contact', 0x14: 'throw situation 2/6', 0x15: 'throw situation 3/7',
  0x16: 'throw situation 4/8', 0x17: 'throw situation 5/9', 0x18: 'near', 0x19: 'far', 0x1A: 'own hit (not guarded)',
  0x1B: 'opponent guarded', 0x1C: 'own whiff', 0x1D: 'opponent not throwing', 0x1E: 'opponent attacking',
  0x1F: 'opponent attacking standing', 0x20: 'opponent attacking crouching', 0x21: 'opponent not attacking',
  0x22: 'opponent standing', 0x23: 'opponent crouching', 0x24: 'back turned', 0x25: 'turned away (side A)',
  0x26: 'turned away (side B)', 0x27: 'facing quadrant 0', 0x28: 'facing quadrant 1', 0x29: 'facing quadrant 3',
  0x2A: 'facing quadrant 2', 0x2B: 'opponent quadrant 0', 0x2C: 'opponent quadrant 1', 0x2D: 'opponent quadrant 3',
  0x2E: 'opponent quadrant 2', 0x2F: 'never', 0x30: 'high attack incoming', 0x31: 'knock-down recovered',
  0x32: 'knock-down recovering', 0x33: 'body contact', 0x34: 'body contact, opponent grounded',
  0x35: 'opponent down', 0x36: 'opponent not down', 0x37: 'opponent down near', 0x38: 'opponent down, turned away',
  0x39: 'opponent took a counter hit', 0x3A: 'LP tap', 0x3B: 'RP tap', 0x3C: 'LP+RP tap', 0x3D: 'own KO',
  0x3E: 'side flag clear', 0x3F: 'side flag set', 0x40: 'side flag clear, back turned', 0x41: 'side flag set, back turned',
  0x42: 'not launched', 0x43: 'power on', 0x44: 'power off', 0x45: 'reversal: hit incoming', 0x46: 'reversal: high',
  0x47: 'reversal: mid', 0x48: 'reversal: low', 0x49: 'reversal: high/mid', 0x4A: 'reversal: slot', 0x4B: 'reversal: anim',
};
for (let c = 2; c <= 0x13; c++) T3_CONDITION_NAMES[c] = `throw situation ${c}`;

const px = (f) => f.root.position;
const dist = (s, o) => Math.hypot(px(s).x - px(o).x, (px(s).z || 0) - (px(o).z || 0));
const down = (f) => f.state === 'knockdown' && f.onGround;
const airborne = (f) => !f.onGround || px(f).y > 0.05;
const attacking = (f) => f.state === 'attack' && f.attack && (f.attack.damage || 0) > 0;
const crouching = (f) => f.state === 'crouch' || f.stance === 'FC';
/** own back towards the opponent (relAngle > 90deg) */
const turnedAway = (s, o) => s.stance === 'BT' || Math.sign(px(o).x - px(s).x) !== s.facing;
/** quadrant of `a` that faces `b`: 0 front, 2 back, 1 / 3 the sides (a sidestepping) */
function quadrant(a, b) {
  if (a.state === 'sidestep') return (a._ssDir || a.ssDir || 1) > 0 ? 1 : 3;
  return turnedAway(a, b) ? 2 : 0;
}
const contact = (s) => s._t3Contact && (s._clock || 0) - s._t3Contact.t <= CONTACT_WINDOW ? s._t3Contact : null;
const level = (f) => { const w = f.attack ? (f.attack.hitWord ?? 0) : 0; const hl = String(f.attack?.hitLevel || '').toLowerCase();
  if ((w & 7) === 4 || /^h/.test(hl)) return 'high'; if ((w & 0x18) === 0x08 && (w & 7) === 7 || /^l/.test(hl)) return 'low'; return 'mid'; };
const incoming = (o) => attacking(o) && o._attackPhase !== 'recovery';

/** SituationClassify: throw situation code 2..19, or -1. */
export function situation(s, o) {
  if (!contact(s) || airborne(o) || incoming(o)) return -1;
  const q = quadrant(o, s), off = { 0: 0, 1: 2, 3: 3, 2: 1 }[q];
  if (turnedAway(s, o) && !down(o) && !crouching(o)) return q === 0 ? 18 : q === 2 ? 19 : -1;
  if (down(o)) return (o._faceDown ? 14 : 10) + off;
  if (crouching(o)) return 6 + off;
  return 2 + off;
}

/** Does T3 branch condition `c` hold for self `s` against opponent `o` when `notation` is pressed? */
export function t3ConditionHolds(c, s, o, notation = '') {
  if (c == null || c === 0) return true;
  if (!o) return false;
  const d = dist(s, o), btn = String(notation).replace(/^.*\+(?=[1-4](\+[1-4])*$)/, '').split('.').pop();
  const P = { 0x14: [2, 6], 0x15: [3, 7], 0x16: [4, 8], 0x17: [5, 9] };
  if (c >= 2 && c <= 0x13) return situation(s, o) === c && d <= SITUATION_RANGE;
  if (P[c]) return P[c].includes(situation(s, o)) && d <= SITUATION_RANGE;
  const ct = contact(s);
  switch (c) {
    case 1: return !!ct;
    case 0x18: return d <= CLOSE;
    case 0x19: return d >= CLOSE;
    case 0x1A: return !!ct && !ct.guarded;
    case 0x1B: return !!ct && ct.guarded;
    case 0x1C: return !!s._t3Whiff && (s._clock || 0) - s._t3Whiff <= CONTACT_WINDOW;
    case 0x1D: return !/throw/.test(o.state);
    case 0x1E: return attacking(o);
    case 0x1F: return attacking(o) && !crouching(o) && !airborne(o);
    case 0x20: return attacking(o) && crouching(o);
    case 0x21: return !attacking(o);
    case 0x22: return !crouching(o) && !airborne(o) && !down(o);
    case 0x23: return crouching(o) && !airborne(o);
    case 0x24: case 0x25: case 0x26: return turnedAway(s, o);
    case 0x27: return quadrant(s, o) === 0; case 0x28: return quadrant(s, o) === 1;
    case 0x29: return quadrant(s, o) === 3; case 0x2A: return quadrant(s, o) === 2;
    case 0x2B: return quadrant(o, s) === 0; case 0x2C: return quadrant(o, s) === 1;
    case 0x2D: return quadrant(o, s) === 3; case 0x2E: return quadrant(o, s) === 2;
    case 0x2F: return false;
    case 0x30: return incoming(o) && level(o) === 'high' && d < HIGH_RANGE;
    case 0x31: return !down(s) && !(s._risingT > 0);
    case 0x32: return down(s) || s._risingT > 0;
    case 0x33: return d <= BODY;
    case 0x34: return d <= BODY && !airborne(o) && !down(o);
    case 0x35: return down(o);
    case 0x36: return !down(o);
    case 0x37: return down(o) && d <= CLOSE;
    case 0x38: return down(o) && turnedAway(s, o);
    case 0x39: return !!o.lastCounterHit && !airborne(o);
    case 0x3A: return /^1$/.test(btn) || /(^|\+)1$/.test(notation);
    case 0x3B: return /^2$/.test(btn) || /(^|\+)2$/.test(notation);
    case 0x3C: return /1\+2$/.test(notation);
    case 0x3D: return s.hp <= 0;
    case 0x3E: return px(s).x <= px(o).x; case 0x3F: return px(s).x > px(o).x;
    case 0x40: return px(s).x <= px(o).x && turnedAway(s, o); case 0x41: return px(s).x > px(o).x && turnedAway(s, o);
    case 0x42: return !airborne(s) && s.hp > 0;
    case 0x43: return !!(s._rageActive || s._urgeOn); case 0x44: return !(s._rageActive || s._urgeOn);
    case 0x45: case 0x4A: case 0x4B: return incoming(o);
    case 0x46: return incoming(o) && level(o) === 'high';
    case 0x47: return incoming(o) && level(o) === 'mid';
    case 0x48: return incoming(o) && level(o) === 'low';
    case 0x49: return incoming(o) && level(o) !== 'low';
    default: return false;
  }
}
