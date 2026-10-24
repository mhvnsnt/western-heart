/* ============================================================
   WESTERN HEART — Move Melding (procedural grapple combinations)

   Design: docs/research/MOVE-MELDING-2026-10-23.md
   Inspiration (proprietary concept — studied, NOT copied): MDickey's
   Wrestling Empire "move melding": combine moves in real time
   (hurricanrana-to-piledriver), physics-based animation where
   "anything can happen at any moment"; every new move adds a new
   counter + a new hybrid.

   WH-native implementation, original code. Tekken throws are the base
   (fixed, frame-data-driven); melding is the extension layer that
   offers EXITS from one grapple into another at defined phase windows.

   Model:
     - Every grapple move decomposes into phases:
       entry -> contact -> payload -> release
     - Grip vocabulary per phase per participant is the compatibility
       contract (MDickey's "puzzle": the end pose of move A must be a
       legal start pose of move B, or no meld).
     - MeldEdge: {from, fromPhase, to, kind} where kind is
       'chain' (attacker continues), 'counter' (victim reverses roles),
       'assist' (second attacker joins — future).
     - Hybrids are generated data: meld(from, to) concatenates phases,
       blends damage, keeps/caches the hybrid so it can be melded from.

   Pure logic: no THREE, no DOM, no Yuka. node-testable. The Yuka
   grapple chain (grapple-chains.js) stays advisory: it asks this
   engine for candidates and emits a 'chain-meld' intent; the
   AIController owns execution.
   ============================================================ */

export const MELD_VERSION = '1.0.0';

export const PHASES = ['entry', 'contact', 'payload', 'release'];

export const MELD_KIND = {
  CHAIN: 'chain',     // attacker flows into the next move
  COUNTER: 'counter', // victim reverses: becomes the hybrid's attacker
  ASSIST: 'assist',   // second attacker joins (double-team; future)
};

/* Closed grip vocabulary — extend by adding rows, never by guessing. */
export const GRIPS = [
  'none', 'wrist', 'headlock', 'waistlock', 'leg-hook', 'shoulders',
  'inverted', 'carry-shoulder', 'front-facelock', 'back-control',
  'ground-mount', 'ground-side', 'ground-back', 'prone', 'seated',
];

function _freeze(o) { return Object.freeze(JSON.parse(JSON.stringify(o))); }

/**
 * Define a grapple move. Validates the shape; returns a frozen def.
 * spec: { id, name, archetype, roles, grips, meldWindows, duration,
 *         damage, endState }
 * grips: { [phase]: { attacker: [...], victim: [...] } }
 * meldWindows: [{ at, into: [moveIds], kind }]
 */
export function defineMove(spec) {
  const req = ['id', 'name', 'grips', 'duration', 'damage'];
  for (const k of req) {
    if (spec[k] === undefined) throw new Error(`defineMove: missing '${k}'`);
  }
  for (const ph of PHASES) {
    const g = spec.grips[ph];
    if (!g || !Array.isArray(g.attacker) || !Array.isArray(g.victim)) {
      throw new Error(`defineMove(${spec.id}): grips.${ph} needs {attacker:[], victim:[]}`);
    }
    for (const who of ['attacker', 'victim']) {
      for (const grip of g[who]) {
        if (!GRIPS.includes(grip)) throw new Error(`defineMove(${spec.id}): unknown grip '${grip}'`);
      }
    }
  }
  for (const w of spec.meldWindows || []) {
    if (!PHASES.includes(w.at)) throw new Error(`defineMove(${spec.id}): bad window phase '${w.at}'`);
    if (!Object.values(MELD_KIND).includes(w.kind)) throw new Error(`defineMove(${spec.id}): bad kind '${w.kind}'`);
  }
  return _freeze({
    archetype: 'grappler',
    roles: { attacker: 'standing', victim: 'standing' },
    meldWindows: [],
    endState: { attacker: 'standing', victim: 'prone' },
    ...spec,
  });
}

/* ---------- starter move library (real wrestling vocabulary) ---------- */

function _lib() {
  const G = (a, v) => ({ attacker: a, victim: v });
  const moves = [
    defineMove({
      id: 'hurricanrana', name: 'Hurricanrana', archetype: 'lucha',
      grips: {
        entry: G(['leg-hook'], ['none']),
        contact: G(['leg-hook', 'headlock'], ['shoulders']),
        payload: G(['leg-hook'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'payload', into: ['piledriver', 'powerbomb'], kind: MELD_KIND.CHAIN },
        { at: 'contact', into: ['ace-crusher'], kind: MELD_KIND.COUNTER },
      ],
      duration: 1.4, damage: 22,
    }),
    defineMove({
      id: 'piledriver', name: 'Piledriver', archetype: 'power',
      grips: {
        entry: G(['waistlock'], ['inverted']),
        contact: G(['waistlock'], ['inverted']),
        payload: G(['waistlock'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'release', into: ['rear-naked-choke', 'armbar'], kind: MELD_KIND.CHAIN },
        { at: 'entry', into: ['back-body-drop'], kind: MELD_KIND.COUNTER },
      ],
      duration: 1.6, damage: 30,
    }),
    defineMove({
      id: 'back-body-drop', name: 'Back Body Drop', archetype: 'power',
      grips: {
        entry: G(['waistlock'], ['none']),
        contact: G(['waistlock'], ['shoulders']),
        payload: G(['waistlock'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'payload', into: ['vertical-suplex'], kind: MELD_KIND.CHAIN },
      ],
      duration: 1.2, damage: 20,
    }),
    defineMove({
      id: 'vertical-suplex', name: 'Vertical Suplex', archetype: 'technical',
      grips: {
        entry: G(['front-facelock'], ['none']),
        contact: G(['front-facelock', 'waistlock'], ['shoulders']),
        payload: G(['front-facelock'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'release', into: ['armbar'], kind: MELD_KIND.CHAIN },
      ],
      duration: 1.5, damage: 24,
    }),
    defineMove({
      id: 'powerbomb', name: 'Powerbomb', archetype: 'power',
      grips: {
        // entry catches an inverted victim: the meld path (e.g. out of a
        // hurricanrana) lifts straight into the shoulders carry
        entry: G(['shoulders'], ['inverted']),
        contact: G(['shoulders'], ['inverted']),
        payload: G(['shoulders'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [],
      duration: 1.7, damage: 32,
    }),
    defineMove({
      id: 'ace-crusher', name: 'Ace Crusher', archetype: 'lucha',
      grips: {
        entry: G(['headlock'], ['shoulders']),
        contact: G(['headlock'], ['shoulders']),
        payload: G(['headlock'], ['prone']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [],
      duration: 1.1, damage: 21,
    }),
    defineMove({
      id: 'rear-naked-choke', name: 'Rear Naked Choke', archetype: 'submission',
      roles: { attacker: 'standing', victim: 'prone' },
      grips: {
        entry: G(['back-control'], ['prone']),
        contact: G(['back-control'], ['prone']),
        payload: G(['back-control'], ['seated']),
        release: G(['back-control'], ['seated']),
      },
      meldWindows: [],
      duration: 2.2, damage: 14,
      endState: { attacker: 'ground-back', victim: 'seated' },
    }),
    defineMove({
      id: 'armbar', name: 'Armbar', archetype: 'submission',
      roles: { attacker: 'standing', victim: 'prone' },
      grips: {
        entry: G(['wrist'], ['prone']),
        contact: G(['wrist', 'ground-mount'], ['prone']),
        payload: G(['ground-mount'], ['prone']),
        release: G(['ground-mount'], ['prone']),
      },
      meldWindows: [],
      duration: 2.0, damage: 12,
      endState: { attacker: 'ground-mount', victim: 'prone' },
    }),
    defineMove({
      id: 'ddt', name: 'DDT', archetype: 'technical',
      grips: {
        entry: G(['front-facelock'], ['none']),
        contact: G(['front-facelock'], ['shoulders']),
        payload: G(['front-facelock'], ['prone']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'contact', into: ['ace-crusher'], kind: MELD_KIND.CHAIN },
      ],
      duration: 1.0, damage: 19,
    }),
    defineMove({
      id: 'german-suplex', name: 'German Suplex', archetype: 'technical',
      grips: {
        entry: G(['waistlock'], ['none']),
        contact: G(['waistlock'], ['shoulders']),
        payload: G(['waistlock'], ['inverted']),
        release: G(['none'], ['prone']),
      },
      meldWindows: [
        { at: 'release', into: ['rear-naked-choke'], kind: MELD_KIND.CHAIN },
        { at: 'contact', into: ['ace-crusher'], kind: MELD_KIND.COUNTER },
      ],
      duration: 1.5, damage: 26,
    }),
  ];
  return moves;
}

/* ---------- blend cost: how smooth is the body path? ---------- */

/**
 * Cost 0..1 for flowing from move A at phase P into move B's entry.
 * MDickey's "puzzle", formalized with an asymmetric gate:
 *  - VICTIM (hard gate): the victim's body must be continuous — they
 *    can't teleport. Every victim grip A holds at the end of P must be
 *    satisfiable by B's entry victim grips (or B is unconstrained there).
 *  - ATTACKER (soft cost): the attacker is allowed to re-grip mid-flow
 *    (that re-grip IS the skill of the transition); novel grips add cost.
 * Soft cost also grows with phase lateness (later windows are tighter).
 * Returns Infinity when no legal body path exists.
 */
export function blendCost(fromMove, fromPhase, toMove) {
  const pi = PHASES.indexOf(fromPhase);
  const vHave = fromMove.grips[fromPhase].victim;
  const vNeed = toMove.grips.entry.victim;
  const victimOk = vHave.every((g) => g === 'none' || vNeed.includes(g) || vNeed.includes('none'));
  if (!victimOk) return Infinity; // no legal body path
  const aHave = fromMove.grips[fromPhase].attacker;
  const aNeed = toMove.grips.entry.attacker;
  const novel = (have, need) => need.filter((g) => g !== 'none' && !have.includes(g)).length;
  const needCount = Math.max(1,
    aNeed.filter((g) => g !== 'none').length + vNeed.filter((g) => g !== 'none').length);
  const gripDist = (novel(aHave, aNeed) + novel(vHave, vNeed)) / needCount;
  const lateness = pi / (PHASES.length - 1);
  return Math.min(1, 0.55 * gripDist + 0.45 * (0.25 + 0.75 * lateness));
}

/* ---------- the meld engine ---------- */

export class MeldEngine {
  constructor() {
    this.moves = new Map();   // id -> GrappleMove
    this.hybrids = new Map(); // id -> Hybrid
    for (const m of _lib()) this.moves.set(m.id, m);
  }

  addMove(spec) {
    const m = defineMove(spec);
    if (this.moves.has(m.id)) throw new Error(`MeldEngine: duplicate move '${m.id}'`);
    this.moves.set(m.id, m);
    return m;
  }

  getMove(id) { return this.moves.get(id) || null; }

  /**
   * Legal melds out of (moveId @ phase). ctx: { rolesOk?: bool } —
   * the caller (grapple chain) confirms both fighters still match the
   * target's entry roles; defaults true in the pure engine.
   * Returns ranked [{ to, hybrid, kind, cost, counterBy }] (cost asc).
   */
  findMelds(moveId, phase, ctx = {}) {
    const from = this.moves.get(moveId);
    if (!from) return [];
    const out = [];
    for (const w of from.meldWindows) {
      if (w.at !== phase) continue;
      for (const toId of w.into) {
        const to = this.moves.get(toId);
        if (!to) continue;
        if (ctx.rolesOk === false) continue;
        const cost = blendCost(from, phase, to);
        if (!isFinite(cost)) continue; // grip gate failed
        out.push({
          to: toId,
          kind: w.kind,
          cost,
          counterBy: w.kind === MELD_KIND.COUNTER ? (w.counterBy || 'victim') : 'attacker',
          hybrid: this.meld(moveId, toId, { fromPhase: phase, kind: w.kind }),
        });
      }
    }
    out.sort((a, b) => a.cost - b.cost);
    return out;
  }

  /** Counter melds only (victim-authored). Used with the reversal brain. */
  findCounters(moveId, phase, ctx = {}) {
    return this.findMelds(moveId, phase, ctx).filter((m) => m.kind === MELD_KIND.COUNTER);
  }

  hybridId(fromId, toId, fromPhase) {
    return `${fromId}-x-${toId}@${fromPhase}`;
  }

  /**
   * Build (or fetch cached) the hybrid descriptor for from -> to.
   * Phases: from's phases up to and including fromPhase, then to's
   * phases after entry. Counters flip the roles.
   */
  meld(fromId, toId, opts = {}) {
    const from = this.moves.get(fromId), to = this.moves.get(toId);
    if (!from || !to) throw new Error(`meld: unknown move(s) ${fromId} -> ${toId}`);
    const fromPhase = opts.fromPhase || 'payload';
    const kind = opts.kind || MELD_KIND.CHAIN;
    const id = opts.hybridId || this.hybridId(fromId, toId, fromPhase);
    if (this.hybrids.has(id)) return this.hybrids.get(id);
    const pi = PHASES.indexOf(fromPhase);
    const phases = [...PHASES.slice(0, pi + 1), ...PHASES.slice(1)];
    const roles = kind === MELD_KIND.COUNTER
      ? { attacker: 'victim', victim: 'attacker' } // roles reverse
      : { attacker: 'attacker', victim: 'victim' };
    const hybrid = _freeze({
      id,
      name: hybridName(from.name, to.name),
      from: fromId, to: toId, fromPhase, kind,
      phases,
      duration: +(from.duration * 0.45 + to.duration).toFixed(2), // setup is "paid for"
      damage: Math.round(from.damage * 0.4 + to.damage),
      roles,
      endState: to.endState,
      counterOf: kind === MELD_KIND.COUNTER ? fromId : null,
    });
    this.hybrids.set(id, hybrid);
    return hybrid;
  }
}

/** "Hurricanrana" + "Piledriver" -> "Hurricane Piledriver". */
const HYBRID_STEMS = { hurricanrana: 'Hurricane' };
export function hybridName(fromName, toName) {
  const key = fromName.toLowerCase();
  const head = HYBRID_STEMS[key]
    || fromName.replace(/(suplex|drop|bomb|crusher|choke|bar|driver)$/i, '').trim()
    || fromName;
  return `${head} ${toName}`.replace(/\s+/g, ' ').trim();
}

/** Map throw progress 0..1 to a meld phase. */
export function phaseAtProgress(p) {
  if (p < 0.25) return 'entry';
  if (p < 0.5) return 'contact';
  if (p < 0.75) return 'payload';
  return 'release';
}
