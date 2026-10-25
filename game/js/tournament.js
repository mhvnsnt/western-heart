/* ============================================================
   WESTERN HEART — Tournament brackets (single elimination)

   TTT2 lineage: the World Arena's tournament room randomly matched
   competitors in a bracket; SFV's Battle Lounge culture runs casual
   lounge tournaments the same way. This is the DOM-free bracket
   engine: build -> play matches in round order -> report winners ->
   champion. UI lives in tournament-ui.js; online sync goes through
   the lobby host's `bracket` broadcast (lobby-protocol.js).

   Bracket JSON is plain data (serializable) so the host can broadcast
   it and every client renders the same bracket.

   Seeding: standard 1vN / 2v(N-1) placement. Sizes 4/8/16; short fields
   are padded with CPU fighters (or BYEs when explicitly requested).
   ============================================================ */

/** Canonical bracket sizes. */
export const BRACKET_SIZES = [4, 8, 16];

/**
 * Seed order for a power-of-two bracket (recursive 1vN placement).
 * seedOrder(8) -> [1,8,4,5,2,7,3,6] (1-based seed numbers).
 */
export function seedOrder(size) {
  if (size === 2) return [1, 2];
  const prev = seedOrder(size / 2);
  const out = [];
  for (const s of prev) { out.push(s, size + 1 - s); }
  return out;
}

/** Mulberry32 seeded RNG (offline bracket sim + shuffle). */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * buildBracket(entries, opts) -> bracket object (plain JSON).
 * entries: [{ id, name, cpu? }] in seed order (entries[0] = #1 seed).
 * opts: { size (4|8|16, default: next power of two >= entries),
 *         fillCpu: [{id,name}] pool to pad short fields (default: []),
 *         byes: bool (pad with BYE instead of CPU; default false),
 *         seed: number (shuffle seed for CPU fill order) }
 */
export function buildBracket(entries, opts = {}) {
  const list = (entries || []).slice();
  let size = opts.size || 4;
  while (size < list.length) size *= 2;
  if (!BRACKET_SIZES.includes(size)) {
    throw new Error(`tournament: bad size ${size}; want one of ${BRACKET_SIZES}`);
  }
  const rng = mulberry32(opts.seed ?? 0x70A6);
  // Pad the field.
  const pool = (opts.fillCpu || []).slice();
  // shuffle the CPU pool so the same pool fills differently per tournament
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  while (list.length < size) {
    if (opts.byes) list.push({ id: '__bye', name: 'BYE', bye: true });
    else if (pool.length) { const c = pool.pop(); list.push({ id: c.id, name: c.name, cpu: true }); }
    else list.push({ id: `__cpu${list.length}`, name: 'CPU RIVAL', cpu: true });
  }
  const order = seedOrder(size);
  // order[k] = seed number (1-based) -> entries are already in seed order
  const seeded = order.map((s) => list[s - 1]);

  const rounds = Math.log2(size);
  const matches = [];
  let mid = 0;
  // Round 0 (quarter/semi depending on size).
  const roundNames = size === 4
    ? ['SEMIFINAL', 'FINAL']
    : size === 8 ? ['QUARTERFINAL', 'SEMIFINAL', 'FINAL']
    : ['ROUND OF 16', 'QUARTERFINAL', 'SEMIFINAL', 'FINAL'];
  const mkMatch = (round, p1, p2) => ({
    id: `m${mid++}`, round, roundName: roundNames[round],
    p1: p1 ? { ...p1 } : null, p2: p2 ? { ...p2 } : null,
    winner: null, next: null, nextSlot: null,
  });
  const byRound = [];
  for (let r = 0; r < rounds; r++) {
    const n = size / 2 ** (r + 1);
    const arr = [];
    for (let i = 0; i < n; i++) arr.push(mkMatch(r, null, null));
    byRound.push(arr);
    matches.push(...arr);
  }
  // Wire next pointers.
  for (let r = 0; r < rounds - 1; r++) {
    byRound[r].forEach((m, i) => {
      m.next = byRound[r + 1][Math.floor(i / 2)].id;
      m.nextSlot = i % 2 === 0 ? 'p1' : 'p2';
    });
  }
  // Seed round 0.
  for (let i = 0; i < seeded.length; i += 2) {
    byRound[0][i / 2].p1 = { ...seeded[i] };
    byRound[0][i / 2].p2 = { ...seeded[i + 1] };
  }
  // Auto-advance BYEs (a BYE never fights: opponent walks over).
  const bracket = {
    size, rounds: roundNames, matches,
    champion: null, createdAt: Date.now(), seed: opts.seed ?? null,
  };
  for (const m of byRound[0]) {
    if (m.p1 && m.p1.bye && m.p2 && !m.p2.bye) _propagateWin(bracket, m.id, m.p2.id, true);
    else if (m.p2 && m.p2.bye && m.p1 && !m.p1.bye) _propagateWin(bracket, m.id, m.p1.id, true);
  }
  return bracket;
}

function _find(bracket, matchId) {
  return bracket.matches.find((m) => m.id === matchId);
}

function _propagateWin(bracket, matchId, winnerId, walkover = false) {
  const m = _find(bracket, matchId);
  if (!m || m.winner) return false;
  const winner = m.p1 && m.p1.id === winnerId ? m.p1
    : m.p2 && m.p2.id === winnerId ? m.p2 : null;
  if (!winner) return false;
  m.winner = winnerId;
  m.walkover = !!walkover;
  if (m.next) {
    const nxt = _find(bracket, m.next);
    nxt[m.nextSlot] = { ...winner };
    // Chain BYE walkovers forward.
    const other = m.nextSlot === 'p1' ? nxt.p2 : nxt.p1;
    if (other && other.bye) _propagateWin(bracket, nxt.id, winnerId, true);
    else if (!other) { /* waiting on the sibling match */ }
  } else {
    bracket.champion = { ...winner };
  }
  return true;
}

/**
 * reportWinner(bracket, matchId, winnerId) -> bool (accepted?).
 * Mutates the bracket (plain JSON): sets winner, feeds next round.
 */
export function reportWinner(bracket, matchId, winnerId) {
  return _propagateWin(bracket, matchId, winnerId, false);
}

/** Matches in the current (earliest incomplete) round that can be played. */
export function pendingMatches(bracket) {
  const out = [];
  for (const m of bracket.matches) {
    if (m.winner || !m.p1 || !m.p2) continue;
    if (m.p1.bye || m.p2.bye) continue;
    out.push(m);
  }
  // Earliest round first.
  out.sort((a, b) => a.round - b.round);
  const r = out.length ? out[0].round : -1;
  return out.filter((m) => m.round === r);
}

/** True when every match has a winner. */
export function isComplete(bracket) {
  return !!bracket.champion;
}

/** Round-grouped view for rendering: [{ name, matches }]. */
export function bracketView(bracket) {
  return bracket.rounds.map((name, r) => ({
    name, round: r,
    matches: bracket.matches.filter((m) => m.round === r),
  }));
}

/**
 * describeMatch(m) -> human line, e.g. "PANTERA vs CPU RIVAL — QUARTERFINAL".
 */
export function describeMatch(m) {
  const n = (p) => (p ? p.name : 'TBD');
  return `${n(m.p1)} vs ${n(m.p2)} — ${m.roundName}`;
}
