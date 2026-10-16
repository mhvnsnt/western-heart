// fighter-sim.js -- deterministic 1v1 fighting-game simulation for lite-rollback.
//
// A minimal Tekken-shaped sim: walk, jump, 4 attacks, block, hitstun/blockstun,
// pushback, KO, round timer. ALL arithmetic is integer (positions in 1/16 px) --
// no floats, no Math.random, no Date. Same (fields, inputs, frame) always gives
// the same next fields, which is the whole contract rollback needs.
//
// Field schema is passed directly to createSession({ fields: FIELDS }).

export const FP = 16; // fixed-point subpixels per pixel

export const STAGE = Object.freeze({
  W: 960 * FP,
  BODY_W: 40 * FP,
  WALK: 3 * FP,
  JUMP_V: -13 * FP,
  GRAV: 1 * FP,
  HP: 100,
  ROUND_TIME: 3600, // 60 s at 60 Hz
});

// States
export const ST = Object.freeze({
  IDLE: 0, WALK: 1, JUMP: 2, ATTACK: 3, HITSTUN: 4, BLOCKSTUN: 5, KO: 6,
});

// Input bits (inputWords = 1)
export const INPUT = Object.freeze({
  LEFT: 0x01, RIGHT: 0x02, UP: 0x04, DOWN: 0x08,
  LP: 0x10, HP: 0x20, LK: 0x40, HK: 0x80, BLOCK: 0x100,
});

// Attack table: [startup, active, recovery, range(px*FP), damage, hitstun, blockstun, pushback(px*FP)]
// Index 0 = none.
export const ATTACKS = Object.freeze([
  null,
  Object.freeze({ su: 4,  ac: 3, rec: 8,  range: 70 * FP,  dmg: 6,  hs: 12, bs: 8,  pb: 40 * FP }), // LP jab
  Object.freeze({ su: 10, ac: 4, rec: 16, range: 82 * FP,  dmg: 12, hs: 18, bs: 12, pb: 70 * FP }), // HP heavy
  Object.freeze({ su: 7,  ac: 4, rec: 12, range: 92 * FP,  dmg: 9,  hs: 15, bs: 10, pb: 55 * FP }), // LK kick
  Object.freeze({ su: 14, ac: 5, rec: 22, range: 100 * FP, dmg: 16, hs: 22, bs: 14, pb: 90 * FP }), // HK heavy kick
]);

// Attack button priority when several are pressed on the same frame.
const ATK_PRIORITY = [4, 2, 3, 1]; // HK, HP, LK, LP
const ATK_BIT = [0, INPUT.LP, INPUT.HP, INPUT.LK, INPUT.HK];

// Field schema -- pass directly to createSession({ fields }).
export const FIELDS = Object.freeze({
  pos:    { type: Int32Array, length: 2 }, // x, 1/16 px
  y:      { type: Int32Array, length: 2 }, // y, 1/16 px (0 = ground, negative = air)
  vel:    { type: Int32Array, length: 2 }, // x velocity
  vy:     { type: Int32Array, length: 2 }, // y velocity
  hp:     { type: Int16Array, length: 2 },
  state:  { type: Uint8Array, length: 2 },
  stateT: { type: Int16Array, length: 2 }, // frames remaining in state
  atk:    { type: Uint8Array, length: 2 }, // current attack id
  hit:    { type: Uint8Array, length: 2 }, // attack already connected this swing
  blk:    { type: Uint8Array, length: 2 }, // blocking this frame
  facing: { type: Int8Array,  length: 2 }, // +1 faces right, -1 faces left
  timer:  { type: Int16Array, length: 1 },
  flags:  { type: Uint8Array, length: 1 }, // bit0: round over
  rng:    { type: Uint32Array, length: 1 },// reserved; sim is fully input-driven
});

/** Reset fields to round start. Call once after session construction. */
export function initFighterState(fields, seed = 0xC0FFEE) {
  fields.pos[0] = 320 * FP; fields.pos[1] = 640 * FP;
  fields.y[0] = 0; fields.y[1] = 0;
  fields.vel[0] = 0; fields.vel[1] = 0;
  fields.vy[0] = 0; fields.vy[1] = 0;
  fields.hp[0] = STAGE.HP; fields.hp[1] = STAGE.HP;
  fields.state[0] = ST.IDLE; fields.state[1] = ST.IDLE;
  fields.stateT[0] = 0; fields.stateT[1] = 0;
  fields.atk[0] = 0; fields.atk[1] = 0;
  fields.hit[0] = 0; fields.hit[1] = 0;
  fields.blk[0] = 0; fields.blk[1] = 0;
  fields.facing[0] = 1; fields.facing[1] = -1;
  fields.timer[0] = STAGE.ROUND_TIME;
  fields.flags[0] = 0;
  fields.rng[0] = seed >>> 0;
}

function clampStage(x) {
  if (x < 0) return 0;
  if (x > STAGE.W) return STAGE.W;
  return x;
}

/**
 * fighterSimulate(fields, inputs, frame) -- the tick function.
 * inputs: Uint32Array[numPlayers]. Deterministic: integer ops only.
 */
export function fighterSimulate(fields, inputs, frame) {
  const { pos, y, vel, vy, hp, state, stateT, atk, hit, blk, facing, timer, flags } = fields;

  if (flags[0] & 1) return; // round over

  // Round timer.
  timer[0]--;
  if (timer[0] <= 0) {
    timer[0] = 0;
    flags[0] |= 1;
    // Timeout: lower HP loses. Tie -> player 0 wins (documented deterministic tiebreak).
    const loser = hp[1] > hp[0] ? 0 : 1;
    hp[loser] = 0;
    state[loser] = ST.KO; stateT[loser] = 9999;
    return;
  }

  for (let p = 0; p < 2; p++) {
    const o = 1 - p;
    if (state[p] === ST.KO) continue;

    if (stateT[p] > 0) stateT[p]--;

    const grounded = y[p] === 0;

    // Face the opponent while free.
    if ((state[p] === ST.IDLE || state[p] === ST.WALK) && grounded) {
      facing[p] = pos[o] >= pos[p] ? 1 : -1;
    }

    const inp = inputs[p] >>> 0;

    switch (state[p]) {
      case ST.HITSTUN:
      case ST.BLOCKSTUN:
        if (stateT[p] <= 0) { state[p] = ST.IDLE; }
        break;

      case ST.ATTACK: {
        const a = ATTACKS[atk[p]];
        const elapsed = (a.su + a.ac + a.rec) - stateT[p];
        // Active window: try to connect.
        if (!hit[p] && elapsed >= a.su && elapsed < a.su + a.ac && state[o] !== ST.KO) {
          const dx = pos[o] - pos[p];
          const dist = dx < 0 ? -dx : dx;
          if (dist <= a.range + STAGE.BODY_W / 2 && y[o] === 0) {
            hit[p] = 1;
            const blocked = blk[o] === 1;
            const dmg = blocked ? Math.max(1, a.dmg >> 3) : a.dmg;
            hp[o] -= dmg;
            const dir = dx >= 0 ? 1 : -1;
            pos[o] = clampStage(pos[o] + dir * a.pb);
            if (hp[o] <= 0) {
              hp[o] = 0;
              state[o] = ST.KO; stateT[o] = 9999;
              flags[0] |= 1;
            } else {
              state[o] = blocked ? ST.BLOCKSTUN : ST.HITSTUN;
              stateT[o] = blocked ? a.bs : a.hs;
              atk[o] = 0;
            }
          }
        }
        if (stateT[p] <= 0) { state[p] = ST.IDLE; atk[p] = 0; }
        break;
      }

      case ST.JUMP: {
        vy[p] += STAGE.GRAV;
        y[p] += vy[p];
        pos[p] = clampStage(pos[p] + vel[p]);
        if (y[p] >= 0) { y[p] = 0; vy[p] = 0; vel[p] = 0; state[p] = ST.IDLE; }
        break;
      }

      case ST.IDLE:
      case ST.WALK: {
        // Blocking: BLOCK bit, or holding away from the opponent.
        const away = facing[p] === 1 ? INPUT.LEFT : INPUT.RIGHT;
        blk[p] = ((inp & INPUT.BLOCK) !== 0 || (inp & away) !== 0) ? 1 : 0;

        // Attack?
        let chosen = 0;
        for (const id of ATK_PRIORITY) {
          if ((inp & ATK_BIT[id]) !== 0) { chosen = id; break; }
        }
        if (chosen !== 0 && grounded) {
          const a = ATTACKS[chosen];
          state[p] = ST.ATTACK;
          stateT[p] = a.su + a.ac + a.rec;
          atk[p] = chosen;
          hit[p] = 0;
          blk[p] = 0;
          vel[p] = 0;
          break;
        }
        // Jump?
        if ((inp & INPUT.UP) !== 0 && grounded) {
          state[p] = ST.JUMP;
          vy[p] = STAGE.JUMP_V;
          vel[p] = 0;
          if ((inp & INPUT.LEFT) !== 0) vel[p] = -STAGE.WALK;
          else if ((inp & INPUT.RIGHT) !== 0) vel[p] = STAGE.WALK;
          blk[p] = 0;
          break;
        }
        // Walk.
        if ((inp & INPUT.LEFT) !== 0 && !((inp & INPUT.RIGHT) !== 0)) {
          state[p] = ST.WALK;
          pos[p] = clampStage(pos[p] - STAGE.WALK);
        } else if ((inp & INPUT.RIGHT) !== 0) {
          state[p] = ST.WALK;
          pos[p] = clampStage(pos[p] + STAGE.WALK);
        } else {
          state[p] = ST.IDLE;
        }
        break;
      }
    }
  }

  // Body push: fighters can't overlap.
  const dx = pos[1] - pos[0];
  const adx = dx < 0 ? -dx : dx;
  if (adx < STAGE.BODY_W && y[0] === 0 && y[1] === 0 && state[0] !== ST.KO && state[1] !== ST.KO) {
    const push = (STAGE.BODY_W - adx) >> 1;
    const dir = dx >= 0 ? 1 : -1;
    pos[0] = clampStage(pos[0] - dir * push);
    pos[1] = clampStage(pos[1] + dir * push);
  }
}
