/* ============================================================
   WESTERN HEART — fight-load recovery (FIGHT-LOAD RECOVERY v2, 2026-11-01)
   Owner: "the loading when you pick an arena ... it keeps kicking me back out to the arena select menu and then I
   have to end up reloading the game ... it would keep infinitely kicking you out to the arena page over and over ...
   that needs to be fixed 100%".

   main.js startFight never sends the player back to the stage screen first any more:
     1. a failed load retries the same fight on its own, then once more in SAFE LOAD (each fighter's default model,
        no transform models);
     2. a fight that fails to BUILD (fighter rig / arena) gets one clean rebuild in SAFE LOAD;
     3. a failed game-module import (a deploy landed while the tab was open: the browser's module map keeps that
        failure for the life of the page, so only a reload fixes it), or any failure the retries did not fix,
        RELOADS THE PAGE STRAIGHT BACK INTO THE SAME FIGHT: a resume token in sessionStorage, read at boot;
     4. only if that also fails (inside the 60 s reload guard) does the stage screen show the real error.
   The old path asked for a CONFIRM tap to reload and allowed one reload per browser session, so a second deploy
   in the same session turned it back into the endless bounce.

   Pure functions over an injected Storage (sessionStorage in the game), unit-tested in
   test/fight-load-recovery.test.mjs.
   ============================================================ */

export const RESUME_KEY = 'wh_fight_resume';
export const RELOAD_GUARD_KEY = 'wh_fight_reload_t';
/** at most one automatic reload per minute: a deploy that is itself broken can never cause a reload loop */
export const RELOAD_GUARD_MS = 60000;
/** a resume token older than this is stale (the player left and came back later): boot normally */
export const RESUME_MAX_AGE_MS = 180000;

/** A dynamic-import / module-link failure, which no in-page retry can fix (Chrome, Firefox, Safari wordings). */
export function isModuleLoadError(detail) {
  return /dynamically imported module|Importing a module script failed|does not provide an export named|Importing binding name/i
    .test(String(detail));
}

/** May the page reload itself now? Records the reload time when it may (the 60 s guard). */
export function claimReload(storage, now = Date.now()) {
  try {
    const last = +storage.getItem(RELOAD_GUARD_KEY) || 0;
    if (now - last < RELOAD_GUARD_MS) return false;
    storage.setItem(RELOAD_GUARD_KEY, String(now));
    return true;
  } catch (e) { return false; }  // storage unavailable: no automatic reload (no way to stop a loop)
}

/** A fight a reload can resume: two roster ids, no mode-built fighter entries (arcade / story ladders live in memory). */
export function resumable(p1, p2, opts = {}) {
  return typeof p1 === 'string' && !!p1 && !opts.playerChar && !opts.enemyChar && !opts.tagTeams &&
    (!opts.mode || opts.mode === 'versus');
}

/** Save the resume token for the fight being reloaded into. Returns true when one was saved. */
export function saveResume(storage, { p1, p2, stage, mode, spirit }, now = Date.now()) {
  try {
    storage.setItem(RESUME_KEY, JSON.stringify({
      p1, p2: typeof p2 === 'string' ? p2 : null, stage: stage || null, mode: mode || null, spirit: spirit || null, t: now }));
    return true;
  } catch (e) { return false; }
}

/** Read AND clear the resume token (one use). Null when absent, unreadable or stale. */
export function takeResume(storage, now = Date.now()) {
  let r = null;
  try { r = JSON.parse(storage.getItem(RESUME_KEY) || 'null'); storage.removeItem(RESUME_KEY); } catch (e) { r = null; }
  if (!r || typeof r.p1 !== 'string' || !r.p1) return null;
  if (!(now - (+r.t || 0) <= RESUME_MAX_AGE_MS)) return null;
  return r;
}

/** The fight started: a later failure may reload straight into its fight again. */
export function fightStarted(storage) {
  try { storage.removeItem(RELOAD_GUARD_KEY); storage.removeItem('wh_module_reload_once'); } catch (e) { /* noop */ }
}

/** What the load catch does next for a failure: 'retry' (same fight), 'safe' (default outfits, no transform models),
 *  'reload' (reload straight back into the fight) or 'report' (show the error on the stage screen). */
export function nextStep({ moduleFailed, retry = 0 }) {
  if (moduleFailed) return 'reload';
  if (retry === 0) return 'retry';
  if (retry === 1) return 'safe';
  return 'reload';
}
