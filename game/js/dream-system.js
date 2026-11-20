/* ============================================================
   WESTERN HEART — Dream System core (Phase 2: LSD dream core)
   Pure logic, no imports, no DOM: safe to import in node and in
   the browser. The playable shell is game/dream.html; the data
   tables are game/data/dream-stages.json.

   PROVENANCE — what this is built from (see also
   docs/DREAM-SYSTEM-LSD-CORE.md):
   - The working JS base: TheShovel/lsd-dream-emu-ds, lsd-web/js/game.js
     (a JS port of figglewatts/LSDRevamped's DreamSystem.cs, MIT) —
     DreamSequence / Journal / DreamSystem shape, constants and flow.
     TheShovel declares NO licence; its upstream Revamped is MIT.
     That port is UNVERIFIED as working (no demo/README/tests, video
     paths stubbed) and implements Revamped's approximations.
   - The verified truth: klnuno/lsd-decomp docs/engine (MATCHING decomp,
     1,447/1,447 functions) — dream-system.md, links.md,
     stages-and-places.md. Where the JS port and the decomp disagree,
     THIS MODULE FOLLOWS THE DECOMP. Every such divergence is marked
     DIVERGENCE below and in the doc.
   - WH data (stages, links, entities, special days) is WH-authored
     canon — WH places, WH characters. Never LSD's stages or entities.

   MECHANICS (decomp-faithful):
   - One dream = one day. DreamSys lives for the session; the Journal
     (save block) holds year, day 1..365, 365 graph points, 3 scores,
     10 flashbacks, 30 navigation flags, dynamic link count.
   - Mood: two s8 axes, -9..9. Every chunk has one mood; every entity
     type has one. Walking into a chunk logs it; touching an entity
     logs it. Day point = mean of the chunk and entity resolves.
     Resolve per axis: sum/count + last/3 (C truncation), wrap past +-9.
   - Day colour: each axis banded (<-3: 0, -3..3: 1, >=4: 2) into the
     3x3 g_moodColors table (0 black, 1 blue, 2 green, 3 cyan, 4 red,
     5 pink, 6 yellow, 7 white).
   - Tomorrow's start: yesterday's graph point -> first chunk with
     that mood (stages scanned in order, row by row) -> that stage's
     arrival point, else chunkKey % count; no matching chunk -> stage 1
     at a random arrival point. Dream length comes from the start stage.
   - Links, 6 kinds, all as data tables searched by one Link_Find:
     fixed (wall), random (wall, timer%16==0), facing (walk forward
     onto a marked tile, yaw within +-44 deg), extra (list switched on
     by some stages/characters; same-place move, +10 s), scripted
     (stage-0-style walks), character-sent (bump / link radius), and
     falls off an edge (ends the day).
   - Timer ticks at 15/s. Random link: rand()%6 among stages 0..5,
     current stage shifts to next. Scores: navigation 1,000,000 per
     nav flag (50,000,000 if all 30), minus 11,024 per dynamic link,
     floor 0; instance = entity record points x 1000, clamped
     0..50,000,000. Flashback menu unlocks above 9,999,999 unlock
     score + at least one kept memory.
   - Flashbacks: on time-up and on each touch, rand()%3==0 keeps the
     moment {stage, place, rotation, 16 s, day}; max 10, overflow
     overwrites entry timer%9.
   - RNG: one PSY-Q LCG (state*0x41C64E6D+0x3039, bits 16..30),
     seeded once. Texture sets cycle on a 40-day clock (days 1-10
     one set, 11-20 two, 21-30 three, 31-40 four). Ambience follows
     (day + stage) & 15.
   ============================================================ */

export const TICKS_PER_SECOND = 15;
export const CHUNK_TILES = 20; // a chunk is 20x20 tiles
export const TILE_UNITS = 0x800; // one tile is 0x800 units
export const CHUNK_UNITS = 0xA000; // one chunk is 0xA000 units square
export const DAYS_PER_YEAR = 365;
export const MOOD_MIN = -9;
export const MOOD_MAX = 9;
export const NAV_GOAL_COUNT = 30;
export const NAV_FLAG_POINTS = 1000000;
export const NAV_ALL_FLAGS_BONUS = 50000000;
export const DYNAMIC_LINK_PENALTY = 11024;
export const INSTANCE_SCORE_MAX = 50000000;
export const FLASHBACK_UNLOCK_SCORE = 9999999;
export const FLASHBACK_MAX = 10;
export const FLASHBACK_LENGTH_SECONDS = 16;
export const LINK_PERIOD_TICKS = 16; // a wall links only on timer % 16 == 0
export const FACING_TOLERANCE_DEG = 44;
export const EXTRA_LINK_BONUS_SECONDS = 10;
export const TEXTURE_CYCLE_DAYS = 40;
export const SAVE_MAGIC = 'WH-DREAM-1';

// Transition codes (decomp dream-system.md): 0xA time up, 0xB start
// chosen, 0xC random link, 0xD fixed link, 0xE next flashback,
// 0xF facing link, 0x10 fall, 0x11 extra link.
export const TRANSITION = Object.freeze({
  TIME_UP: 0xA, START: 0xB, RANDOM_LINK: 0xC, FIXED_LINK: 0xD,
  NEXT_FLASHBACK: 0xE, FACING_LINK: 0xF, FALL: 0x10, EXTRA_LINK: 0x11,
});

// Day-colour table g_moodColors[x band][y band]; names per lsddecomp:
// 0 black, 1 blue, 2 green, 3 cyan, 4 red, 5 pink, 6 yellow, 7 white.
export const MOOD_COLORS = Object.freeze([[6, 7, 2], [4, 7, 1], [3, 0, 5]]);
export const MOOD_COLOR_NAMES = Object.freeze([
  'black', 'blue', 'green', 'cyan', 'red', 'pink', 'yellow', 'white',
]);

/* ---------------- PSY-Q LCG (decomp randomness.md) ----------------
   state = state * 0x41C64E6D + 0x3039; rand() returns bits 16..30. */
export class PsyqRand {
  constructor(seed) {
    // Seeded once per session. A seed of 0 still advances (the LCG
    // adds 0x3039 every step), matching the decomp's single seed.
    this.state = (seed >>> 0) || 0x12345678;
  }
  next() {
    this.state = (Math.imul(this.state, 0x41C64E6D) + 0x3039) >>> 0;
    return (this.state >>> 16) & 0x7FFF;
  }
  int(n) { // C rand() % n
    return this.next() % n;
  }
  pick(list) {
    if (!list || !list.length) return undefined;
    return list[this.int(list.length)];
  }
  floatMinMax(min, max) {
    return min + (this.next() / 0x7FFF) * (max - min);
  }
  oneIn(n) { return this.int(n) === 0; }
}

/* ---------------- Mood math (decomp dream-system.md) ---------------- */

// Wrap past +-9 the decomp way: above 9 becomes -9, below -9 becomes 9
// (a single conditional, not a modulo).
export function wrapMoodAxis(v) {
  if (v > MOOD_MAX) return MOOD_MIN;
  if (v < MOOD_MIN) return MOOD_MAX;
  return v;
}

// Mood_Resolve / Mood_CalcAxis per axis: sum/count + last/3, C integer
// division (truncates toward zero — Math.trunc matches).
export function resolveMoodAxis(sum, count, last) {
  if (!count) return 0;
  return wrapMoodAxis(Math.trunc(sum / count) + Math.trunc(last / 3));
}

export class MoodAccumulator {
  constructor() { this.reset(); }
  reset() { this.sumX = 0; this.sumY = 0; this.count = 0; this.lastX = 0; this.lastY = 0; }
  log(x, y) {
    this.sumX += x; this.sumY += y; this.count++;
    this.lastX = x; this.lastY = y;
  }
  resolve() {
    return [
      resolveMoodAxis(this.sumX, this.count, this.lastX),
      resolveMoodAxis(this.sumY, this.count, this.lastY),
    ];
  }
}

// DreamSys_ComputeDayPoint: mean of the chunk and entity results; the
// chunk result alone when nothing was touched.
export function computeDayPoint(chunkAcc, entityAcc) {
  const c = chunkAcc.resolve();
  if (!entityAcc || entityAcc.count === 0) return c;
  const e = entityAcc.resolve();
  return [Math.trunc((c[0] + e[0]) / 2), Math.trunc((c[1] + e[1]) / 2)];
}

export function moodBand(v) {
  if (v < -3) return 0;
  if (v <= 3) return 1;
  return 2;
}

export function dayColorIndex(point) {
  return MOOD_COLORS[moodBand(point[0])][moodBand(point[1])];
}

export function dayColorName(point) {
  return MOOD_COLOR_NAMES[dayColorIndex(point)];
}

/* ---------------- Keys (decomp links.md) ----------------
   chunk key: col | row << 8; tile key: tileX | tileY << 8. */
export function chunkKey(col, row) { return (col & 0xFF) | ((row & 0xFF) << 8); }
export function tileKey(x, y) { return (x & 0xFF) | ((y & 0xFF) << 8); }
export function parseChunkKey(k) { return { col: k & 0xFF, row: (k >> 8) & 0xFF }; }
export function parseTileKey(k) { return { x: k & 0xFF, y: (k >> 8) & 0xFF }; }

/* ---------------- Chunk moods ----------------
   Each chunk has one mood (decomp: g_stageChunkMoods[stage], row-major).
   WH stages carry explicit overrides for their key chunks; every other
   chunk's mood is derived deterministically from the stage seed + its
   coordinates (FNV-1a hash -> -9..9 per axis), so the same chunk always
   has the same mood on every visit and every day. */
export function moodFromSeed(seed, col, row) {
  let h = (0x811C9DC5 ^ (seed >>> 0)) >>> 0;
  const mix = (v) => { h ^= (v & 0xFF); h = Math.imul(h, 0x01000193) >>> 0; };
  mix(col); mix(row); mix(seed >>> 8); mix(seed >>> 16);
  const d = (h % 19) - 9;
  h = Math.imul(h ^ (h >>> 13), 0x5BD1E995) >>> 0;
  const u = (h % 19) - 9;
  return [d, u];
}

export function chunkMood(stage, col, row) {
  const key = `${col},${row}`;
  if (stage.moodOverrides && stage.moodOverrides[key]) {
    return stage.moodOverrides[key].slice();
  }
  return moodFromSeed(stage.moodSeed || 0, col, row);
}

// Stage_FindChunkByMood: scan stages in order, chunks row by row, first
// chunk whose mood equals the point. Returns {stage, col, row} or null.
export function findChunkByMood(stages, point) {
  for (let s = 0; s < stages.length; s++) {
    const st = stages[s];
    for (let row = 0; row < st.rows; row++) {
      for (let col = 0; col < st.cols; col++) {
        const m = chunkMood(st, col, row);
        if (m[0] === point[0] && m[1] === point[1]) return { stage: s, col, row };
      }
    }
  }
  return null;
}

/* ---------------- Link tables (decomp links.md) ----------------
   Four link lists share one format and one search, Link_Find:
   each entry {chunk:[col,row], tile:[x,y] | null, toStage, toIndex}.
   A tile below 0 (null here) matches any tile of the chunk. On a match
   Link_Find writes the target arrival point into out. The fixed and
   facing lists are the 30 navigation goals. */
export function findLink(list, stageIndex, place) {
  if (!list || !list[stageIndex]) return null;
  const ck = chunkKey(place.chunkCol, place.chunkRow);
  const tk = tileKey(place.tileX, place.tileY);
  for (let i = 0; i < list[stageIndex].length; i++) {
    const e = list[stageIndex][i];
    const eck = chunkKey(e.chunk[0], e.chunk[1]);
    if (eck !== ck) continue;
    if (e.tile) {
      const etk = tileKey(e.tile[0], e.tile[1]);
      if (etk !== tk) continue;
    }
    return { entry: e, index: i };
  }
  return null;
}

export function headingWithin(yawDeg, headingDeg, toleranceDeg = FACING_TOLERANCE_DEG) {
  let d = ((yawDeg - headingDeg) % 360 + 540) % 360 - 180;
  return Math.abs(d) <= toleranceDeg;
}

/* ---------------- DreamSequence ----------------
   Shape taken from the working JS port (TheShovel game.js, ported from
   Revamped's DreamSequence.cs); the evaluation is the DECOMP's
   Mood_Resolve, not Revamped's banded-last approximation (DIVERGENCE 1).
   One sequence = one day's log. */
export class DreamSequence {
  constructor(dayNumber) {
    this.dayNumber = dayNumber || 0;
    this.chunkMood = new MoodAccumulator();
    this.entityMood = new MoodAccumulator();
    this.visited = []; // [{name, count}]
    this.touched = []; // [{type, points}] — feeds the instance score
  }
  logChunk(x, y) { this.chunkMood.log(x, y); }
  logEntity(x, y, type, points) {
    this.entityMood.log(x, y);
    this.touched.push({ type, points: points || 0 });
  }
  evaluateGraphPosition() { return computeDayPoint(this.chunkMood, this.entityMood); }
  toJSON() {
    return {
      dayNumber: this.dayNumber,
      chunk: { sumX: this.chunkMood.sumX, sumY: this.chunkMood.sumY, count: this.chunkMood.count, lastX: this.chunkMood.lastX, lastY: this.chunkMood.lastY },
      entity: { sumX: this.entityMood.sumX, sumY: this.entityMood.sumY, count: this.entityMood.count, lastX: this.entityMood.lastX, lastY: this.entityMood.lastY },
      visited: this.visited,
      touched: this.touched,
    };
  }
  static fromJSON(j) {
    const s = new DreamSequence(j.dayNumber);
    const load = (acc, o) => {
      if (!o) return;
      acc.sumX = o.sumX || 0; acc.sumY = o.sumY || 0; acc.count = o.count || 0;
      acc.lastX = o.lastX || 0; acc.lastY = o.lastY || 0;
    };
    load(s.chunkMood, j.chunk); load(s.entityMood, j.entity);
    s.visited = j.visited || []; s.touched = j.touched || [];
    return s;
  }
}

/* ---------------- Journal (the save block) ----------------
   Shape from the JS port's JournalSaveData; scoring + flashback gate
   are the DECOMP's (DIVERGENCE 4): unlockScore = nav + instance, and
   FLASHBACK unlocks above 9,999,999 with at least one kept memory.
   dayNumber is 1-based (decomp GetDayNumber = day + 1); graph is 365
   points, null for days not yet dreamed. */
export class Journal {
  constructor() {
    this.dayNumber = 1;
    this.yearNumber = 0;
    this.graph = new Array(DAYS_PER_YEAR).fill(null);
    this.sequences = [];
    this.navFlags = new Array(NAV_GOAL_COUNT).fill(false);
    this.dynamicLinkCount = 0;
    this.instanceScore = 0;
    this.flashbacks = []; // [{stage, place, rotation, length, day}]
    this.reel = false;
    this.shake = false;
  }
  previousPoint() {
    if (this.sequences.length === 0) return [0, 0];
    const last = this.sequences[this.sequences.length - 1];
    return last.evaluateGraphPosition();
  }
  calcNavScore() {
    const set = this.navFlags.filter(Boolean).length;
    let score = set === NAV_GOAL_COUNT
      ? NAV_ALL_FLAGS_BONUS
      : set * NAV_FLAG_POINTS;
    score -= DYNAMIC_LINK_PENALTY * this.dynamicLinkCount;
    return Math.max(0, score);
  }
  calcUnlockScore() {
    return this.calcNavScore() + Math.min(INSTANCE_SCORE_MAX, Math.max(0, this.instanceScore));
  }
  canFlashback() {
    return this.calcUnlockScore() > FLASHBACK_UNLOCK_SCORE && this.flashbacks.length >= 1;
  }
  incrementDayWithSequence(seq) {
    const point = seq.evaluateGraphPosition();
    this.graph[this.dayNumber - 1] = point;
    this.sequences.push(seq);
    this.dayNumber++;
    if (this.dayNumber > DAYS_PER_YEAR) { this.dayNumber = 1; this.yearNumber++; }
  }
  addFlashback(entry, timerTicks) {
    if (this.flashbacks.length < FLASHBACK_MAX) {
      this.flashbacks.push(entry);
    } else {
      // Decomp: overflow overwrites entry timer % 9.
      this.flashbacks[timerTicks % 9] = entry;
    }
  }
  toJSON() {
    return {
      magic: SAVE_MAGIC, day: this.dayNumber, year: this.yearNumber,
      graph: this.graph, sequences: this.sequences.map((s) => s.toJSON()),
      navFlags: this.navFlags, dynamicLinkCount: this.dynamicLinkCount,
      instanceScore: this.instanceScore, flashbacks: this.flashbacks,
      reel: this.reel, shake: this.shake,
    };
  }
  static fromJSON(j) {
    const s = new Journal();
    if (!j || j.magic !== SAVE_MAGIC) return s;
    s.dayNumber = j.day || 1;
    s.yearNumber = j.year || 0;
    s.graph = Array.isArray(j.graph) && j.graph.length === DAYS_PER_YEAR
      ? j.graph : new Array(DAYS_PER_YEAR).fill(null);
    s.sequences = (j.sequences || []).map((x) => DreamSequence.fromJSON(x));
    s.navFlags = Array.isArray(j.navFlags) && j.navFlags.length === NAV_GOAL_COUNT
      ? j.navFlags.slice() : new Array(NAV_GOAL_COUNT).fill(false);
    s.dynamicLinkCount = j.dynamicLinkCount || 0;
    s.instanceScore = j.instanceScore || 0;
    s.flashbacks = j.flashbacks || [];
    s.reel = !!j.reel; s.shake = !!j.shake;
    return s;
  }
}

/* ---------------- Texture sets + ambience ----------------
   40-day clock (decomp randomness.md): days 1-10 only set A, 11-20
   A/B, 21-30 A-C, 31-40 A-D, picked by rand() % n. */
export function textureSetForDay(dayNumber, sets, rng) {
  const d = ((dayNumber - 1) % TEXTURE_CYCLE_DAYS) + 1;
  const n = d <= 10 ? 1 : d <= 20 ? 2 : d <= 30 ? 3 : 4;
  const pool = sets.slice(0, Math.min(n, sets.length));
  if (rng) return pool[rng.int(pool.length)];
  return pool[0];
}

// Ambience: family g_ambienceFamilyCycle[(day + stage) & 15], then
// record (day + stage) % count of that family (decomp stages-and-places).
export function ambienceFor(dayNumber, stageIndex, families) {
  if (!families || !families.length) return null;
  const fam = families[(dayNumber + stageIndex) & 15] || families[0];
  const recs = fam.records || [fam];
  return recs[(dayNumber + stageIndex) % recs.length] || null;
}

export function specialDayFor(data, dayNumber) {
  if (!data || !data.specialDays) return null;
  return data.specialDays[String(dayNumber)] || null;
}

/* ---------------- DreamSys ----------------
   The state object. Shape/flow from the JS port's DreamSystem class;
   every rule below is the decomp's. Data (stages, links, entities,
   special days) is injected — this module holds no stage data. */
export class DreamSys {
  constructor(data, opts = {}) {
    if (!data || !Array.isArray(data.stages) || !data.stages.length) {
      throw new Error('DreamSys needs dream data with a stages array');
    }
    this.data = data;
    this.rng = new PsyqRand(opts.seed !== undefined ? opts.seed : ((Date.now() % 2147483647) | 0));
    this.journal = opts.journal instanceof Journal ? opts.journal : Journal.fromJSON(opts.journalJson || null);
    this.dreamer = opts.dreamer || null; // {id, name} — a WH fighter/soul
    this.stageIndex = -1;
    this.place = null; // {chunkCol, chunkRow, tileX, tileY, yawDeg}
    this.timerTicks = 0;
    this.timeLimitTicks = -1; // -1 = no limit (decomp: "none")
    this.transition = 0;
    this.inDream = false;
    this.inFlashback = false;
    this.sequence = null;
    this.extraListOn = false;
    this.scriptedWalk = null; // {script, ticksLeft, target}
    this.textureSet = null;
    this.specialDay = null;
    this.savedDay = 1;
  }

  get dayNumber() { return this.journal.dayNumber; }
  get yearNumber() { return this.journal.yearNumber; }
  get currentStage() { return this.stageIndex >= 0 ? this.data.stages[this.stageIndex] : null; }
  get elapsedSeconds() { return this.timerTicks / TICKS_PER_SECOND; }
  get dynamicLinkOn() { return this.timerTicks % LINK_PERIOD_TICKS === 0; }

  /* ---------- day flow ---------- */
  startDay() {
    this.timerTicks = 0;
    this.savedDay = this.journal.dayNumber;
    this.sequence = new DreamSequence(this.journal.dayNumber);
    this.specialDay = specialDayFor(this.data, this.journal.dayNumber);
    if (this.specialDay) return { specialDay: this.specialDay };
    const start = this.chooseStart();
    this.stageIndex = start.stageIndex;
    this.place = start.place;
    this.timeLimitTicks = this.currentStage.timeLimitSeconds * TICKS_PER_SECOND;
    this.textureSet = textureSetForDay(this.journal.dayNumber, this.currentStage.textureSets || ['clear'], this.rng);
    this.extraListOn = !!this.currentStage.extraListOn;
    this.inDream = true;
    this.transition = TRANSITION.START;
    this.logCurrentChunk();
    return { stageIndex: start.stageIndex, place: start.place };
  }

  // DreamSys_ChooseStart: yesterday's point -> first chunk with that
  // mood -> that stage's arrival point, else chunkKey % count; no match
  // -> stage 1 at a random arrival point. (DIVERGENCE 2: the JS port
  // uses a 19x19 spawnMap instead of this scan.)
  chooseStart() {
    const point = this.journal.previousPoint();
    const found = findChunkByMood(this.data.stages, point);
    if (found) {
      const stage = this.data.stages[found.stage];
      const ck = chunkKey(found.col, found.row);
      let arrival = stage.arrivalPoints.find((a) => chunkKey(a.chunk[0], a.chunk[1]) === ck);
      if (!arrival) arrival = stage.arrivalPoints[ck % stage.arrivalPoints.length];
      return { stageIndex: found.stage, place: arrivalToPlace(arrival) };
    }
    const stage = this.data.stages[1] || this.data.stages[0];
    const arrival = this.rng.pick(stage.arrivalPoints);
    return { stageIndex: 1, place: arrivalToPlace(arrival) };
  }

  enterPlace(place) {
    this.place = { ...place };
    this.logCurrentChunk();
  }

  logCurrentChunk() {
    if (!this.sequence || !this.place || this.inFlashback) return;
    const m = chunkMood(this.currentStage, this.place.chunkCol, this.place.chunkRow);
    this.sequence.logChunk(m[0], m[1]);
  }

  touchEntity(typeId) {
    if (!this.sequence || this.inFlashback) return null;
    const rec = (this.data.entities || []).find((e) => e.id === typeId);
    if (!rec) return null;
    this.sequence.logEntity(rec.mood[0], rec.mood[1], typeId, rec.points || 0);
    this.journal.instanceScore += (rec.points || 0) * 1000;
    this.maybeSaveFlashback();
    if (rec.linkStage !== undefined && rec.linkStage !== null) {
      return this.linkCharacter(rec);
    }
    return { kind: 'touch', entity: rec };
  }

  /* ---------- one tick (DreamSys_OnClock) ---------- */
  tick() {
    if (!this.inDream) return { ended: false };
    this.timerTicks++;
    if (this.timeLimitTicks >= 0 && this.timerTicks > this.timeLimitTicks) {
      return this.endDay('time-up');
    }
    if (this.scriptedWalk) return this.tickScriptedWalk();
    return { ended: false };
  }

  endDay(reason) {
    const wasFlashback = this.inFlashback;
    if (!wasFlashback && this.sequence) {
      this.maybeSaveFlashback();
      this.journal.incrementDayWithSequence(this.sequence);
    }
    const point = this.sequence ? this.sequence.evaluateGraphPosition() : [0, 0];
    const result = {
      ended: true, reason, dayPoint: point,
      dayColor: dayColorName(point),
      day: this.savedDay, year: this.journal.yearNumber,
      unlockScore: this.journal.calcUnlockScore(),
      navScore: this.journal.calcNavScore(),
      canFlashback: this.journal.canFlashback(),
    };
    this.sequence = null;
    this.inDream = false;
    this.inFlashback = false;
    this.transition = TRANSITION.TIME_UP;
    this.timerTicks = 0;
    this.timeLimitTicks = -1;
    return result;
  }

  // A special day replaces the dream: the vignette plays, then the day
  // advances like a normal day end (decomp: StartDay returns -1 and the
  // runner ends the day at once with result 2).
  endSpecialDay() {
    if (!this.sequence) return null;
    this.journal.incrementDayWithSequence(this.sequence);
    const result = {
      ended: true, reason: 'special-day',
      dayPoint: this.sequence.evaluateGraphPosition(),
      day: this.savedDay, year: this.journal.yearNumber,
      unlockScore: this.journal.calcUnlockScore(),
    };
    this.sequence = null;
    this.specialDay = null;
    this.inDream = false;
    return result;
  }

  maybeSaveFlashback() {
    if (!this.sequence || this.inFlashback) return false;
    if (!this.rng.oneIn(3)) return false; // rand() % 3 == 0 keeps it
    this.journal.addFlashback({
      stage: this.stageIndex,
      place: this.place ? { ...this.place } : null,
      rotation: this.place ? this.place.yawDeg || 0 : 0,
      length: FLASHBACK_LENGTH_SECONDS,
      day: this.savedDay,
    }, this.timerTicks);
    return true;
  }

  /* ---------- links (decomp links.md) ---------- */
  // The step the dreamer stands on: scripted, then extra, then facing.
  // Returns a link result or null when the dreamer just moves.
  linksOnStep({ walkingForward = true, yawDeg = 0 } = {}) {
    if (!this.inDream || !this.place) return null;
    if (this.scriptedWalk) return null;
    const scripted = this.tryScriptedLink(yawDeg, walkingForward);
    if (scripted) return scripted;
    const extra = this.tryExtraLink();
    if (extra) return extra;
    return this.tryFacingLink(yawDeg, walkingForward);
  }

  // Wall touch: fixed link first, then (timer%16==0) a random link.
  // DIVERGENCE 3: the JS port has no link tables — TriggerLink entities
  // + random-linkable only. These tables are the decomp's Link_Find.
  linksOnWallTouch() {
    if (!this.inDream || !this.place) return null;
    const stage = this.currentStage;
    const fixed = findLink(this.data.links && this.data.links.fixed, this.stageIndex, this.place);
    if (fixed) return this.runLink('fixed', fixed.entry, TRANSITION.FIXED_LINK, true);
    if (this.dynamicLinkOn) return this.linkRandom();
    return null;
  }

  runLink(kind, entry, transition, setNavFlag) {
    const targetStage = this.data.stages[entry.toStage];
    if (!targetStage) return null;
    const target = targetStage.arrivalPoints[entry.toIndex % targetStage.arrivalPoints.length];
    if (!target) return null;
    if (setNavFlag && typeof target.navFlag === 'number') {
      this.journal.navFlags[target.navFlag] = true;
    }
    this.transition = transition;
    // A link deletes the Place and builds a new one: the stage changes
    // and the dreamer arrives at the target. The dream timer is NOT
    // reset: one dream has one timer, and the limit stays the one set
    // at the start (decomp: the limit is set at the start of a dream
    // from the start stage; links do not re-set it).
    this.stageIndex = entry.toStage;
    this.place = arrivalToPlace(target);
    this.extraListOn = !!this.currentStage.extraListOn;
    this.logCurrentChunk();
    return { kind, toStage: entry.toStage, place: { ...this.place }, transition };
  }

  tryFacingLink(yawDeg, walkingForward) {
    if (!walkingForward) return null;
    const list = this.data.links && this.data.links.facing;
    const hit = findLink(list, this.stageIndex, this.place);
    if (!hit) return null;
    const heading = (this.data.headings || [])[hit.entry.heading || 0];
    if (heading === undefined) return null;
    if (!headingWithin(yawDeg, heading, FACING_TOLERANCE_DEG)) return null;
    const res = this.runLink('facing', hit.entry, TRANSITION.FACING_LINK, true);
    if (res) res.arrivalHeading = (this.data.headings || [])[hit.entry.arrivalHeading || 0];
    return res;
  }

  tryExtraLink() {
    if (!this.extraListOn) return null;
    const list = this.data.links && this.data.links.extra;
    const hit = findLink(list, this.stageIndex, this.place);
    if (!hit) return null;
    // Extra links do NOT rebuild the place: same-place move, and the
    // time limit becomes elapsed + 10 s (decomp DreamSys_LinkExtra).
    const targetStage = this.data.stages[hit.entry.toStage];
    const target = targetStage.arrivalPoints[hit.entry.toIndex % targetStage.arrivalPoints.length];
    this.transition = TRANSITION.EXTRA_LINK;
    this.place = arrivalToPlace(target);
    if (this.timeLimitTicks >= 0) this.timeLimitTicks = this.timerTicks + EXTRA_LINK_BONUS_SECONDS * TICKS_PER_SECOND;
    this.transition = 0;
    this.logCurrentChunk();
    return { kind: 'extra', toStage: hit.entry.toStage, place: { ...this.place }, transition: TRANSITION.EXTRA_LINK };
  }

  tryScriptedLink(yawDeg, walkingForward) {
    const list = this.data.links && this.data.links.scripted;
    const hit = findLink(list, this.stageIndex, this.place);
    if (!hit || !walkingForward) return null;
    const heading = (this.data.headings || [])[hit.entry.heading || 0];
    if (heading === undefined) return null;
    if (!headingWithin(yawDeg, heading, FACING_TOLERANCE_DEG)) return null;
    const scriptId = hit.entry.script !== undefined ? hit.entry.script : 0;
    const target = this.data.stages[hit.entry.toStage].arrivalPoints[hit.entry.toIndex];
    this.scriptedWalk = {
      script: scriptId,
      ticksLeft: (this.data.scriptedWalks || [])[scriptId]?.ticksWalking || 0x85,
      target: arrivalToPlace(target),
    };
    return { kind: 'scripted-start', script: scriptId, place: { ...this.place } };
  }

  tickScriptedWalk() {
    if (!this.scriptedWalk) return { ended: false };
    this.scriptedWalk.ticksLeft--;
    if (this.scriptedWalk.ticksLeft <= 0) {
      const target = this.scriptedWalk.target;
      this.scriptedWalk = null;
      this.place = { ...target };
      this.logCurrentChunk();
      return { ended: false, scriptedDone: true, place: { ...this.place } };
    }
    return { ended: false, scriptedWalking: true, ticksLeft: this.scriptedWalk.ticksLeft };
  }

  // Character-sent link (event 10): stage is taken negative so the
  // target stage is fixed and the arrival point random.
  linkCharacter(entityRec) {
    if (!this.inDream) return null;
    const toStage = entityRec.linkStage;
    if (toStage === undefined || toStage === null) return null;
    return this.linkRandom(-toStage);
  }

  // DreamSys_LinkDynamic / Spawn_PickRandom: rand()%6 among stages 0..5,
  // a draw equal to the current stage moves to the next (5 wraps to 0);
  // a negative stage is taken as-is. Every call counts a dynamic link.
  linkRandom(forcedStage) {
    let toStage = forcedStage;
    if (toStage === undefined || toStage === null) {
      toStage = this.rng.int(6);
      if (toStage === this.stageIndex) toStage = (toStage + 1) % 6;
    } else if (toStage < 0) {
      toStage = -toStage;
    }
    toStage = Math.max(0, Math.min(toStage, this.data.stages.length - 1));
    const stage = this.data.stages[toStage];
    const arrival = this.rng.pick(stage.arrivalPoints);
    this.journal.dynamicLinkCount++;
    this.transition = TRANSITION.RANDOM_LINK;
    this.stageIndex = toStage;
    this.place = arrivalToPlace(arrival);
    this.extraListOn = !!this.currentStage.extraListOn;
    this.logCurrentChunk();
    return { kind: 'random', toStage, place: { ...this.place }, transition: TRANSITION.RANDOM_LINK };
  }

  // Falls: off an edge (no ground), or stage 9 with ground found.
  // Link_PickFallStage: -1 except in the data's fallStages; an odd
  // timer makes the stage 12 (WH: data.fallOddStage).
  linkFall() {
    if (!this.inDream) return null;
    const rules = this.data.fall || {};
    const from = this.stageIndex;
    let toStage = -1;
    if (rules.stages && Object.prototype.hasOwnProperty.call(rules.stages, String(from))) {
      toStage = rules.stages[String(from)];
    }
    if (toStage === -1) {
      // No fall stage from here: the dreamer is put back (no link).
      return null;
    }
    if (this.timerTicks % 2 === 1 && rules.oddStage !== undefined) toStage = rules.oddStage;
    this.transition = TRANSITION.FALL;
    // A fall ends the day; the picked stage is never built.
    return this.endDay('fall');
  }

  /* ---------- flashback replay ---------- */
  beginFlashback() {
    if (!this.journal.canFlashback()) return null;
    this.inFlashback = true;
    this.inDream = true;
    this.sequence = null;
    const first = this.journal.flashbacks[0];
    if (!first) return null;
    this.stageIndex = first.stage;
    this.place = first.place ? { ...first.place } : null;
    this.timeLimitTicks = (first.length + 4) * TICKS_PER_SECOND;
    this.timerTicks = 0;
    this.transition = TRANSITION.NEXT_FLASHBACK;
    return { flashback: first };
  }

  /* ---------- save ---------- */
  toJSON() { return this.journal.toJSON(); }
  static fromJournalJson(data, json, opts) {
    return new DreamSys(data, { ...opts, journalJson: json });
  }
}

export function arrivalToPlace(arrival) {
  return {
    chunkCol: arrival.chunk[0], chunkRow: arrival.chunk[1],
    tileX: arrival.tile[0], tileY: arrival.tile[1],
    yawDeg: arrival.yawDeg || 0,
  };
}
