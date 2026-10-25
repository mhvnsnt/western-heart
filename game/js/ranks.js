/* ============================================================
   WESTERN HEART — Rank system (meta layer, worker 30)
   Dan/kyu-style progression, Tekken-flavored, WH-canon named.

   THE RANK NAMES LIVE IN game/data/ranks.json — NOT HERE.
   Rename tiers, insert tiers, extend the S-tier list, or name the
   RESERVED placeholders purely by editing that JSON. This file
   only implements the structural logic (points, promotion /
   demotion series, protection, tracks, persistence) and never
   hardcodes a single rank name.

   Structure pulled from the Tekken teardown (see
   docs/research/rank-system.md):
     - separate OFFLINE and ONLINE tracks (T7 gives every player
       two ranks: one offline, one ranked)
     - per-CHARACTER ranks on each track (T7 ranks characters,
       not accounts)
     - points bar per tier; beating same-rank foes pays best,
       upset scaling by tier difference (sdtekken IC-card formula
       family: vs same = full, vs higher = less risk, vs lower =
       less reward)
     - bar full -> PROMOTION series (T7's "promotion chance" as a
       best-of-N); bar empty -> DEMOTION risk series
     - demotion protection right after promotion (no instant
       yo-yo); bottom floor can't demote (T7: 1st Dan hardcapped)
     - placement bouts for new fighters (bigger swings)
     - local leaderboard per track (online ladder hooks for
       game/netplay ranked when it lands)
   ============================================================ */

export const RANK_LS_KEY = 'wh_ranks';
export const RANK_JSON_URL = new URL('../data/ranks.json', import.meta.url);

let TABLE = null;          // the rank table (data, never code)
let tablePromise = null;

/* ---------- table loading ---------- */
export async function initRanks() {
  if (TABLE) return TABLE;
  if (!tablePromise) {
    tablePromise = (async () => {
      // Preferred: JSON module import (single source of truth).
      try {
        const mod = await import('../data/ranks.json', { with: { type: 'json' } });
        TABLE = mod.default;
      } catch (e) {
        // Fallback: plain fetch (older bundlers / odd servers).
        const res = await fetch(RANK_JSON_URL);
        if (!res.ok) throw new Error('rank table fetch failed: ' + res.status);
        TABLE = await res.json();
      }
      if (!TABLE || !Array.isArray(TABLE.tiers) || !TABLE.tiers.length) {
        throw new Error('rank table missing tiers');
      }
      return TABLE;
    })();
  }
  return tablePromise;
}
export function ranksReady() { return !!TABLE; }
export function rankTable() {
  if (!TABLE) throw new Error('ranks not initialized — await initRanks() first');
  return TABLE;
}
/** For unit tests / node: inject a table object directly. */
export function _setTableForTest(t) { TABLE = t; }

/* ---------- pure table helpers (no DOM, no storage) ---------- */
export function tierCount() { return rankTable().tiers.length; }
export function tierAt(idx) {
  const tiers = rankTable().tiers;
  return tiers[Math.max(0, Math.min(tiers.length - 1, idx))];
}
export function tierIndexById(id) {
  const tiers = rankTable().tiers;
  const i = tiers.findIndex((t) => t.id === id);
  return i === -1 ? 0 : i; // unknown id -> entry tier (table was edited; degrade gracefully)
}
export function tierById(id) { return tierAt(tierIndexById(id)); }
export function sectionDef(sectionId) {
  return (rankTable().sections || []).find((s) => s.id === sectionId) || null;
}
export function sectionOf(tier) { return sectionDef(tier.section) || { id: tier.section, label: tier.section, color: '#888' }; }
export function barFor(tier) {
  const bars = (rankTable().rules.bar || {});
  return bars[tier.section] ?? bars.default ?? 400;
}
export function promoBestOfFor(tier) {
  const m = (rankTable().rules.promotion.seriesBestOf || {});
  return m[tier.section] ?? m.default ?? 3;
}
export function isReserved(tier) { return !!(tier && tier.reserved); }
export function displayName(tier) {
  if (!tier) return '—';
  if (tier.unnamed) return '??? (unnamed)';
  return tier.name;
}
export function displayFull(tier) {
  if (!tier) return '—';
  const ja = tier.nameJa ? ` ${tier.nameJa}` : '';
  return displayName(tier) + ja;
}

/* ---------- persistence (localStorage, guarded) ---------- */
function blankFighter() {
  return {
    tierId: rankTable().rules.entryTierId,
    points: 0,
    wins: 0, losses: 0, streak: 0,
    placementLeft: rankTable().rules.placementMatches ?? 5,
    series: null,   // { kind:'promo'|'demo', wins, losses, bestOf }
    protect: 0,     // demotion-protection matches remaining
    topHeld: 0,     // matches held at the top tier (drives future reserved-tier invention)
  };
}
function loadStore() {
  try {
    const raw = localStorage.getItem(RANK_LS_KEY);
    const s = raw ? JSON.parse(raw) : null;
    if (s && typeof s === 'object') {
      s.offline = s.offline || {}; s.online = s.online || {};
      s.leaderboard = s.leaderboard || { offline: [], online: [] };
      return s;
    }
  } catch (e) { /* corrupted -> reset below */ }
  return { offline: {}, online: {}, leaderboard: { offline: [], online: [] } };
}
function saveStore(s) {
  try { localStorage.setItem(RANK_LS_KEY, JSON.stringify(s)); } catch (e) { /* private mode etc. */ }
}
function normTrack(track) { return track === 'online' ? 'online' : 'offline'; }

export function getFighterRank(track, charId) {
  const t = normTrack(track);
  const s = loadStore();
  if (!s[t][charId]) { s[t][charId] = blankFighter(); saveStore(s); }
  return s[t][charId];
}
function putFighterRank(track, charId, fr) {
  const t = normTrack(track);
  const s = loadStore();
  s[t][charId] = fr; saveStore(s);
}

/* ---------- core: record one ranked result ----------
   opts: { track, charId, foeTierIdx (or foeTierId), won,
           playerName } -> { events, state }
   events drive the result UI (promoted!, series started, ...). */
export function recordResult(opts) {
  const table = rankTable();
  const rules = table.rules;
  const track = normTrack(opts.track);
  const charId = opts.charId;
  const fr = getFighterRank(track, charId);
  const myIdx = tierIndexById(fr.tierId);
  const myTier = tierAt(myIdx);
  const lastIdx = tierCount() - 1;
  const foeIdx = (opts.foeTierIdx != null) ? opts.foeTierIdx
    : (opts.foeTierId ? tierIndexById(opts.foeTierId) : myIdx);
  const placing = fr.placementLeft > 0;
  const events = [];
  const need = (n) => Math.ceil(n / 2);

  const push = (e) => events.push(e);

  if (fr.series) {
    // ---- inside a promotion / demotion series: the match counts as a series game
    const se = fr.series;
    if (opts.won) se.wins++; else se.losses++;
    fr.wins += opts.won ? 1 : 0; fr.losses += opts.won ? 0 : 1;
    const winNeed = need(se.bestOf);
    if (se.kind === 'promo') {
      if (se.wins >= winNeed) {
        const from = myTier;
        if (myIdx < lastIdx) {
          const to = tierAt(myIdx + 1);
          fr.tierId = to.id;
          fr.points = Math.round(barFor(to) * (rules.promotion.promoteStartFrac ?? 0.25));
          fr.protect = rules.demotion.protectionMatches ?? 3;
          push({ type: 'promoted', fromId: from.id, toId: to.id, fromIdx: myIdx, toIdx: myIdx + 1 });
        } else {
          fr.topHeld++;
          push({ type: 'top-held', held: fr.topHeld, tierId: from.id });
        }
        fr.series = null;
      } else if (se.losses >= winNeed) {
        fr.series = null;
        fr.points = Math.round(barFor(myTier) * (rules.promotion.seriesLossBarFrac ?? 0.5));
        push({ type: 'promo-failed', tierId: myTier.id, points: fr.points, bar: barFor(myTier) });
      } else {
        push({ type: 'series-update', kind: 'promo', wins: se.wins, losses: se.losses, bestOf: se.bestOf, need: winNeed });
      }
    } else { // demo series
      if (se.losses >= winNeed) {
        const from = myTier;
        const ni = Math.max(0, myIdx - 1);
        const to = tierAt(ni);
        fr.tierId = to.id;
        fr.points = Math.round(barFor(to) * (rules.demotion.demoteStartFrac ?? 0.75));
        fr.protect = 0; fr.series = null;
        push({ type: 'demoted', fromId: from.id, toId: to.id, fromIdx: myIdx, toIdx: ni });
      } else if (se.wins >= winNeed) {
        fr.series = null;
        fr.points = Math.round(barFor(myTier) * (rules.demotion.seriesWinBarFrac ?? 0.15));
        push({ type: 'demo-survived', tierId: myTier.id, points: fr.points, bar: barFor(myTier) });
      } else {
        push({ type: 'series-update', kind: 'demo', wins: se.wins, losses: se.losses, bestOf: se.bestOf, need: winNeed });
      }
    }
  } else {
    // ---- regular ranked match: points swing
    const P = rules.points;
    const diff = Math.max(-(P.upsetCapTiers ?? 3),
      Math.min((P.upsetCapTiers ?? 3), foeIdx - myIdx));
    let delta;
    if (opts.won) {
      const mult = Math.max(P.underdogFloorMult ?? 0.5, 1 + (P.upsetPerTier ?? 0.25) * diff);
      const streakBonus = Math.min(P.winStreakCap ?? 5, fr.streak) * (P.winStreakBonus ?? 15);
      delta = Math.round((P.baseWin ?? 100) * mult * (placing ? (rules.placementSwingMult ?? 2) : 1) + streakBonus);
      fr.streak = Math.min((P.winStreakCap ?? 5) + 1, fr.streak + 1);
      fr.wins++;
      fr.points += delta;
      const bar = barFor(myTier);
      push({ type: 'points', delta: +delta, points: fr.points, bar, tierId: myTier.id });
      if (fr.points >= bar) {
        if (myIdx >= lastIdx) {
          fr.points = bar; fr.topHeld++;
          push({ type: 'top-held', held: fr.topHeld, tierId: myTier.id });
        } else {
          const bestOf = promoBestOfFor(myTier);
          fr.series = { kind: 'promo', wins: 0, losses: 0, bestOf };
          fr.points = bar;
          push({ type: 'promo-series', tierId: myTier.id, bestOf, need: need(bestOf) });
        }
      }
    } else {
      const mult = Math.max(P.underdogFloorMult ?? 0.5, 1 + (P.upsetPerTier ?? 0.25) * (-diff));
      delta = -Math.round((P.baseLoss ?? 70) * mult * (placing ? (rules.placementSwingMult ?? 2) : 1));
      fr.streak = 0;
      fr.losses++;
      fr.points = Math.max(0, fr.points + delta);
      const bar = barFor(myTier);
      push({ type: 'points', delta, points: fr.points, bar, tierId: myTier.id });
      if (fr.points <= 0 && myIdx > 0 && fr.protect <= 0 && !placing) {
        const bestOf = rules.demotion.seriesBestOf ?? 3;
        fr.series = { kind: 'demo', wins: 0, losses: 0, bestOf };
        push({ type: 'demo-series', tierId: myTier.id, bestOf, need: need(bestOf) });
      } else if (fr.points <= 0 && fr.protect > 0) {
        push({ type: 'protected', protectLeft: fr.protect, tierId: myTier.id });
      }
    }
    if (fr.protect > 0) fr.protect--;
    if (placing) {
      fr.placementLeft--;
      push({ type: 'placement', left: fr.placementLeft });
    }
  }

  putFighterRank(track, charId, fr);
  touchLeaderboard(track, {
    name: opts.playerName || 'YOU',
    charId,
    tierId: fr.tierId,
    points: fr.points,
    wins: fr.wins, losses: fr.losses,
    at: Date.now(),
  });
  return { events, state: JSON.parse(JSON.stringify(fr)) };
}

/* ---------- offline rank-battle helpers ---------- */
/** Pick a CPU foe tier near the player's (arcade-style drift). */
export function rankBattleFoeTier(playerIdx, rng) {
  const spread = (rankTable().rules.tracks.offline.foeTierSpread ?? 2);
  const r = rng || Math.random;
  const d = Math.floor(r() * (spread * 2 + 1)) - spread;
  return Math.max(0, Math.min(tierCount() - 1, playerIdx + d));
}
/** AI difficulty scales with tier — the ladder gets meaner as you climb. */
export function rankBattleAiDiff(tierIdx) {
  const c = (rankTable().rules.tracks.offline || {});
  const base = c.aiBase ?? 0.45, per = c.aiPerTier ?? 0.012, cap = c.aiCap ?? 0.97;
  return Math.min(cap, base + tierIdx * per);
}
/** Short badge line for the fight HUD, e.g. "RANK · WARLORD 320/500". */
export function rankBadgeText(track, charId) {
  try {
    const fr = getFighterRank(track, charId);
    const tier = tierById(fr.tierId);
    const bar = barFor(tier);
    const series = fr.series ? ` · ${fr.series.kind === 'promo' ? 'PROMO' : 'DEMO'} ${fr.series.wins}-${fr.series.losses}` : '';
    return `RANK ${displayName(tier).toUpperCase()} · ${fr.points}/${bar}${series}`;
  } catch (e) { return 'RANK —'; }
}

/* ---------- leaderboards (local; online ladder hooks for netplay) ---------- */
export function getLeaderboard(track) {
  const t = normTrack(track);
  const s = loadStore();
  return (s.leaderboard[t] || []).slice();
}
/** Upsert a fighter into the track's leaderboard, sorted by tier then points. */
export function touchLeaderboard(track, entry) {
  const t = normTrack(track);
  const s = loadStore();
  const lb = s.leaderboard[t] || [];
  const key = (entry.name || 'YOU') + '|' + entry.charId;
  const ix = lb.findIndex((e) => ((e.name || 'YOU') + '|' + e.charId) === key);
  const rec = { ...entry, key };
  if (ix === -1) lb.push(rec); else lb[ix] = rec;
  const rankOf = (e) => tierIndexById(e.tierId);
  lb.sort((a, b) => (rankOf(b) - rankOf(a)) || (b.points - a.points) || (b.wins - a.wins));
  const size = rankTable().rules.leaderboard?.size ?? 25;
  s.leaderboard[t] = lb.slice(0, size);
  saveStore(s);
}
/** Minimum matches before a fighter shows on the public ladder. */
export function qualifiesForLadder(track, charId) {
  const fr = getFighterRank(track, charId);
  return (fr.wins + fr.losses) >= (rankTable().rules.leaderboard?.minMatches ?? 3);
}

/* ---------- event -> human text (result screens) ---------- */
export function describeEvent(ev) {
  switch (ev.type) {
    case 'points':
      return { title: (ev.delta >= 0 ? '+' : '') + ev.delta + ' PTS', sub: `Bar: ${ev.points}/${ev.bar}`, cls: ev.delta >= 0 ? 'win' : 'lose' };
    case 'promo-series':
      return { title: 'PROMOTION SERIES', sub: `Win ${ev.need} of ${ev.bestOf} to rank up. This is the moment.`, cls: 'promo' };
    case 'series-update': {
      const k = ev.kind === 'promo' ? 'PROMOTION' : 'DEMOTION';
      return { title: `${k} SERIES ${ev.wins}–${ev.losses}`, sub: `First to ${ev.need}.`, cls: 'promo' };
    }
    case 'promoted': {
      const to = tierById(ev.toId);
      return { title: 'RANK UP — ' + displayName(to).toUpperCase(), sub: displayFull(to) + (isReserved(to) ? ' · an unnamed throne, earned into existence' : ''), cls: 'win promo' };
    }
    case 'promo-failed':
      return { title: 'PROMOTION DENIED', sub: 'The ladder keeps you. Bar reset — climb again.', cls: 'lose' };
    case 'demo-series':
      return { title: 'DEMOTION RISK', sub: `Lose ${ev.need} of ${ev.bestOf} and you fall a rank. Hold the line.`, cls: 'demo' };
    case 'demoted': {
      const to = tierById(ev.toId);
      return { title: 'DEMOTED — ' + displayName(to).toUpperCase(), sub: 'The climb resumes. It always does.', cls: 'lose demo' };
    }
    case 'demo-survived':
      return { title: 'RANK HELD', sub: 'Demotion dodged. Breathe.', cls: 'win' };
    case 'protected':
      return { title: 'PROTECTED', sub: `Fresh promotion — demotion can't touch you for ${ev.protectLeft} more.`, cls: 'win' };
    case 'placement':
      return ev.left > 0
        ? { title: 'PLACEMENT ' + ((rankTable().rules.placementMatches ?? 5) - ev.left) + '/' + (rankTable().rules.placementMatches ?? 5), sub: 'The ladder is still measuring you.', cls: '' }
        : { title: 'PLACEMENT COMPLETE', sub: 'The ladder knows your name now.', cls: 'win' };
    case 'top-held':
      return { title: 'SUMMIT HELD — ' + ev.held, sub: 'Hold the top long enough and new thrones get invented above you.', cls: 'win promo' };
    default:
      return { title: ev.type, sub: '', cls: '' };
  }
}

/* ---------- Rank Hub UI (overlay: your ranks, leaderboards, full ladder) ---------- */
let hubEl = null;

function el(tag, cls, text) {
  const d = document.createElement(tag);
  if (cls) d.className = cls;
  if (text != null) d.textContent = text;
  return d;
}

function trackCard(track, charId, charName) {
  const fr = getFighterRank(track, charId);
  const tier = tierById(fr.tierId);
  const sec = sectionOf(tier);
  const bar = barFor(tier);
  const card = el('div', 'rank-track-card');
  const label = (rankTable().rules.tracks[track] || {}).label || track.toUpperCase();
  card.appendChild(el('div', 'rank-track-label', label + ' TRACK'));
  const name = el('div', 'rank-tier-name', displayFull(tier));
  name.style.color = sec.color || '#fff';
  if (isReserved(tier)) name.classList.add('rank-reserved');
  card.appendChild(name);
  card.appendChild(el('div', 'rank-section', sec.label || ''));
  const barWrap = el('div', 'rank-bar');
  const fill = el('div', 'rank-bar-fill');
  fill.style.width = Math.min(100, Math.round((fr.points / Math.max(1, bar)) * 100)) + '%';
  fill.style.background = sec.color || '#fff';
  barWrap.appendChild(fill);
  card.appendChild(barWrap);
  card.appendChild(el('div', 'rank-bar-num', `${fr.points} / ${bar} pts`));
  let status = `${fr.wins}W – ${fr.losses}L · streak ${fr.streak}`;
  if (fr.placementLeft > 0) status += ` · placement ${fr.placementLeft} left`;
  if (fr.protect > 0) status += ` · protected ×${fr.protect}`;
  if (fr.series) status += ` · ${fr.series.kind === 'promo' ? 'PROMOTION' : 'DEMOTION'} SERIES ${fr.series.wins}–${fr.series.losses} (best of ${fr.series.bestOf})`;
  if (fr.topHeld > 0) status += ` · summit held ×${fr.topHeld}`;
  card.appendChild(el('div', 'rank-status', status));
  return card;
}

function ladderTable(track) {
  const lb = getLeaderboard(track);
  const wrap = el('div', 'rank-ladder');
  if (!lb.length) {
    wrap.appendChild(el('div', 'rank-ladder-empty', 'No ranked fights yet on this track. The ladder is waiting.'));
    return wrap;
  }
  const tbl = el('table', 'rank-ladder-table');
  const head = el('tr');
  ['#', 'FIGHTER', 'CHARACTER', 'RANK', 'PTS', 'W–L'].forEach((h) => head.appendChild(el('th', '', h)));
  tbl.appendChild(head);
  lb.forEach((e, i) => {
    const tier = tierById(e.tierId);
    const tr = el('tr');
    tr.appendChild(el('td', 'rank-pos', String(i + 1)));
    tr.appendChild(el('td', '', e.name || 'YOU'));
    tr.appendChild(el('td', '', e.charId));
    const td = el('td', 'rank-tier-cell', displayName(tier));
    td.style.color = (sectionOf(tier).color || '#fff');
    tr.appendChild(td);
    tr.appendChild(el('td', '', String(e.points)));
    tr.appendChild(el('td', '', `${e.wins}–${e.losses}`));
    tbl.appendChild(tr);
  });
  wrap.appendChild(tbl);
  return wrap;
}

function fullTierList(highlightId) {
  const wrap = el('div', 'rank-tierlist');
  rankTable().tiers.forEach((t, i) => {
    const sec = sectionOf(t);
    const row = el('div', 'rank-tier-row' + (t.id === highlightId ? ' current' : ''));
    row.appendChild(el('span', 'rank-tier-num', String(i + 1).padStart(2, '0')));
    const nm = el('span', 'rank-tier-nm', displayFull(t));
    nm.style.color = sec.color || '#fff';
    row.appendChild(nm);
    row.appendChild(el('span', 'rank-tier-sec', sec.label || ''));
    if (isReserved(t)) row.appendChild(el('span', 'rank-tier-res', 'RESERVED'));
    wrap.appendChild(row);
  });
  return wrap;
}

/** Open the Rank Hub overlay. opts: { charId, charName } */
export function openRankHub(opts) {
  opts = opts || {};
  closeRankHub();
  if (!ranksReady()) return;
  ensureRankCss();
  const charId = opts.charId || 'demonio';
  const charName = opts.charName || charId;

  hubEl = el('div', 'rank-hub');
  hubEl.id = 'rank-hub';
  const inner = el('div', 'rank-hub-inner');
  inner.appendChild(el('h2', 'rank-hub-title', 'RANK HALL'));
  inner.appendChild(el('div', 'rank-hub-sub', `${charName} — two tracks, one climb. Ranks are per character, Tekken-style.`));

  const cards = el('div', 'rank-cards');
  cards.appendChild(trackCard('offline', charId, charName));
  cards.appendChild(trackCard('online', charId, charName));
  inner.appendChild(cards);

  // leaderboard tabs
  const tabs = el('div', 'rank-tabs');
  const pages = el('div', 'rank-pages');
  let cur = 'offline';
  const renderTabs = () => {
    tabs.innerHTML = ''; pages.innerHTML = '';
    ['offline', 'online'].forEach((t) => {
      const b = el('button', 'rank-tab' + (t === cur ? ' active' : ''), t.toUpperCase() + ' LADDER');
      b.addEventListener('click', () => { cur = t; renderTabs(); });
      tabs.appendChild(b);
    });
    const note = el('div', 'rank-ladder-note',
      cur === 'online'
        ? 'Online ladder: local versus feeds it until netplay ranked lands (game/netplay).'
        : 'Offline ladder: earned in Rank Battle vs the CPU.');
    pages.appendChild(note);
    pages.appendChild(ladderTable(cur));
  };
  renderTabs();
  inner.appendChild(tabs);
  inner.appendChild(pages);

  inner.appendChild(el('h3', 'rank-hub-h3', 'THE LADDER — 53 TIERS'));
  const fr = getFighterRank('offline', charId);
  inner.appendChild(fullTierList(fr.tierId));

  const close = el('button', 'btn-ghost rank-hub-close', 'CLOSE');
  close.addEventListener('click', closeRankHub);
  inner.appendChild(close);

  hubEl.appendChild(inner);
  document.body.appendChild(hubEl);
}
export function closeRankHub() {
  if (hubEl && hubEl.parentNode) hubEl.parentNode.removeChild(hubEl);
  hubEl = null;
}

/** Render rank events into a result screen (called after _modeWin shows). */
export function showRankResult(result) {
  const screen = document.getElementById('screen-modewin');
  if (!screen) return;
  let box = document.getElementById('rank-events');
  if (box) box.remove();
  box = el('div', 'rank-events');
  box.id = 'rank-events';
  (result.events || []).forEach((ev) => {
    const d = describeEvent(ev);
    const row = el('div', 'rank-event ' + d.cls);
    row.appendChild(el('div', 'rank-event-title', d.title));
    if (d.sub) row.appendChild(el('div', 'rank-event-sub', d.sub));
    box.appendChild(row);
  });
  const btns = document.getElementById('modewin-buttons');
  if (btns && btns.parentNode) btns.parentNode.insertBefore(box, btns);
  else screen.appendChild(box);
}

/* ---------- Rank Battle: offline arcade-style ranked ladder ----------
   Tekken structure: offline rank climbs happen in arcade/treasure-style
   fights vs the CPU. Wins and losses move the fighter's OFFLINE rank
   through recordResult(); promotion/demotion series play out as
   best-of-N sets inside the ladder. */
export class RankBattleController {
  constructor(deps) {
    this.game = deps.game; this.ui = deps.ui; this.show = deps.show;
    this.startFight = deps.startFight; this.roster = deps.roster;
    this.getChar = deps.getChar; this.audio = deps.audio;
    this.active = false;
    this.fighterId = null;
    this.foeTierIdx = 0;
    this._foeEntry = null;
    this._el = (id) => document.getElementById(id);
  }

  async start() {
    await initRanks();
    ensureRankCss();
    this.active = true;
    this.fighterId = null;
    this.show('select');
    const hint = this._el('select-hint');
    if (hint) hint.textContent = 'RANK BATTLE — choose your soul. Wins and losses move your OFFLINE rank. Promotion series are best-of-N.';
  }
  clear() {
    this.active = false; this.fighterId = null; this._foeEntry = null;
    this._badge('');
    if (this.game) this.game.onMatchEnd = null;
  }
  /** Select-screen confirm routing. Returns true when the flow is consumed. */
  onConfirm(charId) {
    if (!this.active || !charId) return false;
    this.fighterId = charId;
    this._next();
    return true;
  }

  _pickFoe(excludeId) {
    const ids = this.roster.map((c) => c.id).filter((id) => id !== excludeId && id !== 'custom');
    const avail = ids.map((id) => this.getChar(id)).filter(Boolean);
    const list = avail.length ? avail : this.roster.filter((c) => c.id !== excludeId);
    return list[Math.floor(Math.random() * list.length)];
  }
  _scaleAi(char, diff) {
    const base = char.ai || { aggression: 0.6, grabBias: 0.15, reaction: 0.55 };
    const d = Math.max(0.15, Math.min(1, diff));
    return {
      aggression: Math.min(1, base.aggression * (0.6 + d * 0.7)),
      grabBias: base.grabBias ?? 0.15,
      reaction: Math.min(1, base.reaction * (0.5 + d * 0.8)),
    };
  }
  _badge(text) {
    const b = this._el('mode-badge');
    if (b) { b.textContent = text; b.style.display = text ? 'block' : 'none'; }
  }

  _next() {
    const fr = getFighterRank('offline', this.fighterId);
    const myIdx = tierIndexById(fr.tierId);
    const myTier = tierAt(myIdx);
    const foeIdx = rankBattleFoeTier(myIdx);
    this.foeTierIdx = foeIdx;
    const foe = this._pickFoe(this.fighterId);
    const foeEntry = { ...foe, ai: this._scaleAi(foe, rankBattleAiDiff(foeIdx)) };
    const foeTier = tierAt(foeIdx);
    this._foeEntry = foeEntry;
    const series = fr.series ? ` · ${fr.series.kind === 'promo' ? 'PROMOTION' : 'DEMOTION'} SERIES ${fr.series.wins}–${fr.series.losses}` : '';
    this._badge(`RANK BATTLE · ${displayName(myTier).toUpperCase()} ${fr.points}/${barFor(myTier)}${series}`);
    if (this.ui && this.ui.banner) this.ui.banner(`RANK BATTLE — ${foe.name} · ${displayName(foeTier)}`);
    this.game.onMatchEnd = (won) => this._end(won);
    this.startFight(this.fighterId, null, { mode: 'rankbattle', enemyChar: foeEntry });
    if (this.audio && this.audio.uiClick) this.audio.uiClick();
  }

  _end(won) {
    const res = recordResult({
      track: 'offline', charId: this.fighterId,
      foeTierIdx: this.foeTierIdx, won, playerName: 'YOU',
    });
    this._resultScreen(won, res);
  }

  _resultScreen(won, res) {
    this.game.onMatchEnd = null;
    const me = this.getChar(this.fighterId) || {};
    const fr = res.state;
    const tier = tierById(fr.tierId);
    const title = this._el('modewin-title');
    const sub = this._el('modewin-sub');
    const wrap = this._el('modewin-buttons');
    if (title) { title.textContent = won ? 'VICTORY' : 'DEFEAT'; title.className = won ? 'win' : 'lose'; }
    if (sub) sub.textContent = `${me.name || this.fighterId} — ${displayFull(tier)} · ${fr.points}/${barFor(tier)} pts`;
    // rank events box (replaces any previous)
    const screen = this._el('screen-modewin');
    let box = document.getElementById('rank-events');
    if (box) box.remove();
    box = el('div', 'rank-events'); box.id = 'rank-events';
    (res.events || []).forEach((ev) => {
      const d = describeEvent(ev);
      const row = el('div', 'rank-event ' + d.cls);
      row.appendChild(el('div', 'rank-event-title', d.title));
      if (d.sub) row.appendChild(el('div', 'rank-event-sub', d.sub));
      box.appendChild(row);
    });
    if (wrap) {
      wrap.innerHTML = '';
      const mk = (label, cls, fn) => {
        const b = document.createElement('button');
        b.className = cls; b.textContent = label;
        b.addEventListener('click', () => { if (this.audio && this.audio.uiClick) this.audio.uiClick(); fn(); });
        wrap.appendChild(b);
      };
      mk('NEXT BATTLE', 'btn-primary', () => this._next());
      mk('RANK HALL', 'btn-ghost', () => openRankHub({ charId: this.fighterId, charName: me.name || this.fighterId }));
      mk('MAIN MENU', 'btn-ghost', () => {
        this.game.leaveFight(); this.clear();
        this.show('menu');
        if (this.audio && this.audio.stopMusic) this.audio.stopMusic();
      });
      if (wrap.parentNode) wrap.parentNode.insertBefore(box, wrap);
      else if (screen) screen.appendChild(box);
    }
    this.show('modewin');
  }
}

/* ---------- rank CSS (injected once; no stylesheet edit needed) ---------- */
let cssDone = false;
export function ensureRankCss() {
  if (cssDone || typeof document === 'undefined') return;
  cssDone = true;
  const st = document.createElement('style');
  st.id = 'wh-rank-css';
  st.textContent = `
.rank-hub{position:fixed;inset:0;z-index:2000;background:rgba(8,6,18,.96);overflow-y:auto;display:flex;justify-content:center;padding:24px 12px}
.rank-hub-inner{max-width:860px;width:100%;color:#eee;font-family:inherit}
.rank-hub-title{font-size:34px;letter-spacing:.2em;text-align:center;margin:8px 0;color:#ffd60a}
.rank-hub-sub{text-align:center;opacity:.75;margin-bottom:18px}
.rank-cards{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin-bottom:18px}
.rank-track-card{flex:1 1 300px;background:#141126;border:1px solid #3a2f6b;border-radius:12px;padding:16px}
.rank-track-label{font-size:11px;letter-spacing:.25em;opacity:.6;margin-bottom:6px}
.rank-tier-name{font-size:26px;font-weight:800;margin-bottom:2px}
.rank-tier-name.rank-reserved{font-style:italic;opacity:.8}
.rank-section{font-size:12px;opacity:.65;margin-bottom:10px}
.rank-bar{height:10px;background:#0a0818;border-radius:6px;overflow:hidden;margin-bottom:4px}
.rank-bar-fill{height:100%;border-radius:6px;transition:width .4s}
.rank-bar-num{font-size:12px;opacity:.7;margin-bottom:8px}
.rank-status{font-size:12px;line-height:1.5;opacity:.85}
.rank-tabs{display:flex;gap:8px;justify-content:center;margin:10px 0}
.rank-tab{background:#141126;color:#ccc;border:1px solid #3a2f6b;border-radius:8px;padding:8px 18px;cursor:pointer}
.rank-tab.active{background:#3a2f6b;color:#fff}
.rank-ladder-note{text-align:center;font-size:12px;opacity:.6;margin-bottom:8px}
.rank-ladder-table{width:100%;border-collapse:collapse;font-size:13px}
.rank-ladder-table th{font-size:11px;letter-spacing:.15em;opacity:.55;text-align:left;padding:6px 8px;border-bottom:1px solid #3a2f6b}
.rank-ladder-table td{padding:6px 8px;border-bottom:1px solid #221d40}
.rank-ladder-empty{text-align:center;opacity:.6;padding:18px}
.rank-hub-h3{text-align:center;letter-spacing:.2em;margin:22px 0 10px;color:#cdb4ff}
.rank-tierlist{max-height:320px;overflow-y:auto;border:1px solid #2a2350;border-radius:10px;padding:6px 10px;background:#0d0a1e}
.rank-tier-row{display:flex;gap:10px;align-items:center;padding:4px 6px;border-radius:6px;font-size:13px}
.rank-tier-row.current{background:#2a2350;outline:1px solid #ffd60a}
.rank-tier-num{opacity:.45;width:26px}
.rank-tier-nm{font-weight:700;flex:1}
.rank-tier-sec{font-size:11px;opacity:.55}
.rank-tier-res{font-size:10px;color:#ff5d8f;border:1px solid #ff5d8f;border-radius:4px;padding:1px 6px;letter-spacing:.1em}
.rank-hub-close{display:block;margin:20px auto 30px}
.rank-events{margin:14px auto;max-width:520px;display:flex;flex-direction:column;gap:8px}
.rank-event{background:#141126;border:1px solid #3a2f6b;border-radius:10px;padding:10px 14px;text-align:center}
.rank-event-title{font-weight:800;letter-spacing:.08em}
.rank-event-sub{font-size:12px;opacity:.7;margin-top:2px}
.rank-event.win .rank-event-title{color:#7bf1a8}
.rank-event.lose .rank-event-title{color:#ff8a8a}
.rank-event.promo{border-color:#ffd60a}
.rank-event.promo .rank-event-title{color:#ffd60a}
.rank-event.demo{border-color:#ff5d8f}
.rank-event.demo .rank-event-title{color:#ff5d8f}
`;
  document.head.appendChild(st);
}
// Back-compat: showRankResult renders into the modewin screen (used by other callers).
export { showRankResult as renderRankResult };
