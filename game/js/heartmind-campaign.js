/* ============================================================
   WESTERN HEART — Heart and Mind Within: campaign layer
   (Lane 6, story + canon, 2026-10-24)

   This module is the STRUCTURE layer for "Heart and Mind Within"
   (game/js/heartmind.js, "The Heart and Mind Inside"). It adds, on
   top of heartmind.js's existing T5 Devil Within skeleton (5 inner
   stages -> echo waves -> stage boss -> shadow self at the still
   point), the structure pulled from T6 Scenario Campaign and from
   the MK adventure/beat-em-up games the owner liked (adventure
   structure and customization ONLY — the owner does not like MK
   fighting games, and no MK fighting system is pulled here):

   • ROADS, not portals. Canon: "the lands where souls fight, the
     roads between them, the shrine where it ends" (CANON.md L28),
     and "the long walks between the lands — the tunnels, the
     stairs, the desert" (CANON.md L1391). Every descent step is a
     walk down a road; realm-to-realm travel is traversal with
     things to encounter on the way, never a teleport. See also
     docs/research/REALM-TRAVEL-CANON-2026-10-23.md (roads are the
     vessels between organs of one body).
   • PARTY SWITCHING. Scenario Campaign model: the player leads one
     fighter while a companion travels with them, and unlocked
     fighters can be chosen for later stages; boss-defeat unlocks
     (Tekkenpedia/Neoseeker Scenario Campaign summaries, 2026-10-24
     research). WH version: a party of souls descends together and
     the active fighter may be switched BETWEEN fights (never
     mid-fight). Each member keeps their own stage/wave/HP progress.
     In-fight partner AI is NOT here — that is the combat lane's
     work; this module only owns the party state + the switch rule.
   • STAGE JOURNAL. Scenario Campaign's post-stage journal entries
     (Alisa's Journal, then Raven's) become WH data: a cleared-stage
     record per fighter. Presentation (title card) is the UI lane's
     work; no journal prose is invented here.
   • RAGDOLL CONTEXTS. Owner law (2026-10-23): ragdoll is
     contextual ONLY — it fires in the moment it would happen in a
     Tekken game (launches, KOs, wall splats), never always-on.
     This module names the story/adventure-mode contexts where the
     physics lane may trigger it. The physics itself belongs to the
     open-source/physics lane, not here.
   • STORY-ENGINE ADAPTER. Ink is the pick for heavily branching
     story, Yarn where writers author visually (PR #1044: Yarn
     parser + Ink loader). This module NEVER statically imports
     those files — PR #1044 is still open, so a static import
     would break main. Both loaders are dynamic-imported with a
     null fallback: when the engines are absent, the caller keeps
     using heartmind.js's built-in story beats. No behaviour
     changes until PR #1044 merges.

   Dependency-free (browser + Node). heartmind.js imports this
   module; this module imports nothing from heartmind.js, so there
   is no import cycle. Stage keys MUST match HEARTMIND_STAGES in
   game/js/heartmind.js (threshold, masks, drowning, furnace,
   stillpoint) — the test in game/tests/heartmind-campaign.test.mjs
   asserts that by reading both files, without importing the
   browser-only controller.

   Canon rule for everything here: every item below carries a
   CANON.md anchor, or is marked SYSTEM (a game system, not a
   canon location/being). No invented locations, beings, or
   backstory. Tekken/MK names appear in this technical comment
   only, never in in-game text.
   ============================================================ */

/* Stage keys, in descent order. Mirrors HEARTMIND_STAGES keys in
   game/js/heartmind.js — keep the two lists identical. */
export const HM_STAGE_KEYS = ['threshold', 'masks', 'drowning', 'furnace', 'stillpoint'];

/* ---------------- Roads ----------------
   One road per descent step. `walk` is a plain description of the
   walk, not a new place name: the road itself is the canon object
   (CANON.md L28), the rooms it connects are heartmind.js's inner
   stages, and the anchors name the canon passage each walk leans
   on. The Threshold road leans on the Threshold's Face room
   (CANON.md L1363-1367: faces "hung like masks in a green room");
   the last road ends at the still point, the Octagonal Shrine's
   stillness (CANON.md L38, L461-475 ladder: the Shrine is the
   source, "the still point at the center" per RIN's entry). */
export const HM_ROADS = [
  {
    from: 'threshold', to: 'masks',
    walk: 'Down from the Threshold, past the hung faces. The masks come off one by one.',
    canon: 'CANON.md L28 (roads between the lands); CANON.md L1363-1367 (Threshold keeps a Face — faces hung like masks)',
  },
  {
    from: 'masks', to: 'drowning',
    walk: 'Down from the gallery, to where what was buried waits under water.',
    canon: 'CANON.md L28 (roads); CANON.md L1391 (long walks between the lands)',
  },
  {
    from: 'drowning', to: 'furnace',
    walk: 'Up out of the water, toward what burns.',
    canon: 'CANON.md L28 (roads); CANON.md L1391 (long walks)',
  },
  {
    from: 'furnace', to: 'stillpoint',
    walk: 'Out of the furnace, up the stairs that count the climber back, to the still point.',
    canon: 'CANON.md L28 (roads); CANON.md L1347-1362 (Octagonal Shrine Par-fang, climbed by stairs that count the climber back)',
  },
];

/* Road into a stage, or null for the first stage (the descent
   begins at the Threshold — there is no road in). */
export function roadInto(stageKey) {
  return HM_ROADS.find((r) => r.to === stageKey) || null;
}

/* Road out of a stage, or null for the last stage (the still
   point is the end of the descent). */
export function roadOutOf(stageKey) {
  return HM_ROADS.find((r) => r.from === stageKey) || null;
}

/* ---------------- Party ----------------
   A party is the souls descending together. `progress` holds one
   entry per member: { stage, wave, hp, cleared[] }. hp is null
   until the member has fought (heartmind.js fills it with the
   soul-ember restore between waves). Switching never erases
   progress: the outgoing member's progress is saved by the caller
   (HeartmindController.switchFighter) before the swap. */
export function createPartyState(fighterIds) {
  const members = [...new Set((fighterIds || []).filter(Boolean))];
  const progress = {};
  for (const id of members) progress[id] = { stage: 0, wave: 0, hp: null, cleared: [] };
  return { members, active: members[0] || null, progress };
}

/* Switch the active fighter. Pure state swap — the caller owns
   saving the outgoing fighter's live run progress first, and
   owns re-running the stage card after. Returns { ok } or
   { ok: false, reason }. */
export function switchPartyFighter(state, fighterId) {
  if (!state || !Array.isArray(state.members) || !state.members.includes(fighterId)) {
    return { ok: false, reason: 'not-in-party' };
  }
  state.active = fighterId;
  const p = state.progress[fighterId] || { stage: 0, wave: 0, hp: null, cleared: [] };
  state.progress[fighterId] = p;
  return { ok: true, fighterId, progress: { stage: p.stage, wave: p.wave, hp: p.hp } };
}

/* Record a cleared stage for one party member (journal data).
   Idempotent: clearing the same stage twice records it once. */
export function recordPartyStageClear(state, fighterId, stageKey) {
  if (!state || !state.progress[fighterId]) return false;
  const cleared = state.progress[fighterId].cleared;
  if (!cleared.includes(stageKey)) cleared.push(stageKey);
  return true;
}

/* The stage journal: one data row per cleared stage, newest
   last. Presentation (title card, companion voice) is the UI
   lane's work — this is the record, not the prose. */
export function partyJournal(state) {
  if (!state) return [];
  const rows = [];
  for (const id of state.members) {
    const p = state.progress[id];
    if (!p) continue;
    for (const stage of p.cleared) rows.push({ fighter: id, stage });
  }
  return rows;
}

/* ---------------- Ragdoll contexts (story/adventure) ----------------
   SYSTEM, not canon: these are trigger contexts for the physics
   lane, named so story/adventure code and physics code agree on
   the vocabulary. Rule (owner 2026-10-23): ragdoll fires ONLY in
   these moments — launches, KOs, wall splats, and the floor-drop
   that follows a stage break — and ONLY in adventure/story
   modes. Versus-mode use is the engine lane's decision, not
   asserted here. `ragdollAllowed` is the single gate both sides
   should call. */
export const HM_RAGDOLL_CONTEXTS = [
  { id: 'launch', trigger: 'fighter launched into the air', mode: 'heartmind' },
  { id: 'ko', trigger: 'KO blow lands', mode: 'heartmind' },
  { id: 'wall-splat', trigger: 'fighter splats into a wall or spirit barrier', mode: 'heartmind' },
  { id: 'floor-drop', trigger: 'floor or balcony break drops the fighters to a lower level', mode: 'heartmind' },
];

export function ragdollAllowed(contextId, mode) {
  if (mode !== 'heartmind' && mode !== 'adventure') return false;
  return HM_RAGDOLL_CONTEXTS.some((c) => c.id === contextId);
}

/* ---------------- Story-engine adapter ----------------
   Dynamic imports only (see header: PR #1044 still open).
   Returns null when the engine file is absent, so callers fall
   back to heartmind.js's built-in beats. Never throws for a
   missing engine file. */

/* Yarn: parse + run a .yarn script. Returns { kind, runner,
   parsed } or null. Runner surface is PR #1044's YarnRunner:
   next() -> { type: 'line'|'choices'|'end', ... }, choose(). */
export async function loadYarnDialogue(yarnText, startNode) {
  try {
    const m = await import('./yarn-parse.js');
    const parsed = m.parseYarn(yarnText);
    const runner = new m.YarnRunner(parsed, startNode || undefined);
    return { kind: 'yarn', runner, parsed };
  } catch {
    return null;
  }
}

/* Ink: build a runnable story from compiled Ink JSON. The inkjs
   runtime is vendored at game/vendor/inkjs/ink.mjs (inkle inkjs
   2.4.0, MIT) and the loader is PR #1044's game/js/ink-loader.js
   (BOM strip + validation). Returns { kind, story, run } or
   null. `run(pickFn)` steps the story with ink-loader's
   runInkStory driver. */
export async function loadInkDialogue(jsonText) {
  try {
    const loader = await import('./ink-loader.js');
    const ink = await import('../vendor/inkjs/ink.mjs');
    const story = loader.createInkStory(ink.Story, jsonText);
    return {
      kind: 'ink',
      story,
      run: (pickFn) => loader.runInkStory(story, pickFn),
    };
  } catch {
    return null;
  }
}
