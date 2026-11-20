/* ============================================================
   WESTERN HEART — Jukebox era browse (2026-10-24, Lane 4 audio)
   T7 Jukebox structure, WH content: T7's Jukebox browses by game
   (T1–T6/TTT2); Western Heart browses by collection/era, because
   its soundtrack is WH's own — originals, the Nosferatu synth
   score, and the Cape Jones Loyalty Freak set — plus one
   data-only era that is listed for transparency and NEVER played.

   This module is pure and side-effect free (no DOM, no fetch, no
   localStorage reads at import): the caller supplies the parsed
   eras doc (game/data/jukebox-eras.json), the library tracks
   (game/data/music-library.json tracks), and a state object it
   persists however it likes. game/js/jukebox.js (PR #1046) owns
   the Settings pool switch; this module owns era browsing and
   era playback order, and the two compose: a pool id and an era
   id are different selectors over the same library.

   Availability rule (shared with game/js/music.js): a track is
   playable only when it has a file or remote AND its status is
   not 'pending-download'. 'pending-file' tracks (file field set,
   bytes not yet in the repo — the 8 Cape Jones MP3s) are listed
   and returned by era resolution, and the engine falls back to
   its procedural loop if the fetch fails — the game never goes
   silent. 'pending-download' tracks (file null — the 5 Tekken
   data-only slots) are NEVER returned by any resolver here.

   Cape Jones rule (user directive 2026-10-24 19:41 CDT, LOCKED):
   Ghost Surf Rock by Loyalty Freak Music is the Cape Jones theme
   song and the MAIN track; it leads every rotation cycle of the
   cape-jones era, with the other 7 tracks interchanging around
   it. The cycle rest is the cape era's own tracks only — never
   the whole library (that is the PR #1046 pools-file bug this
   module deliberately does not repeat: its cape pool's rest was
   every available library track).
   ============================================================ */

export function isPlayableTrack(t) {
  return !!(t && (t.file || t.remote) && t.status !== 'pending-download');
}

export function getEra(erasDoc, eraId) {
  const eras = (erasDoc && erasDoc.eras) || [];
  return eras.find((e) => e.id === eraId) || null;
}

/* Browse list: every era id + name + playability + track count.
   Data-only eras are listed (transparency) with playable: false. */
export function listEras(erasDoc) {
  const eras = (erasDoc && erasDoc.eras) || [];
  return eras.map((e) => ({
    id: e.id,
    name: e.name,
    description: e.description || '',
    playable: e.playable !== false,
    mainTrackId: e.mainTrackId || null,
    trackCount: Array.isArray(e.trackIds) ? e.trackIds.length : 0,
  }));
}

/* Browse tracks for an era, in era order, with their status kept
   visible (so a UI can grey out pending entries). This is a LISTING
   function: it includes pending-download tracks, flagged by status.
   Never use its output directly as a play queue — use
   resolveEraTrack, which filters to playable tracks only. */
export function browseEraTracks(erasDoc, libraryTracks, eraId) {
  const era = getEra(erasDoc, eraId);
  if (!era || !Array.isArray(era.trackIds)) return [];
  const tracks = Array.isArray(libraryTracks) ? libraryTracks : [];
  return era.trackIds
    .map((id) => tracks.find((t) => t.id === id))
    .filter(Boolean);
}

/* Playable era queue, in play order. Cape Jones: main track first,
   then the rest of the era in era order. Every other playable era:
   era order as listed. Pending-download tracks are dropped here. */
export function playableEraQueue(erasDoc, libraryTracks, eraId) {
  const era = getEra(erasDoc, eraId);
  if (!era || era.playable === false) return [];
  const ordered = browseEraTracks(erasDoc, libraryTracks, eraId)
    .filter(isPlayableTrack);
  if (era.mainTrackId) {
    const main = ordered.find((t) => t.id === era.mainTrackId);
    if (!main) return ordered;
    return [main, ...ordered.filter((t) => t.id !== era.mainTrackId)];
  }
  return ordered;
}

/* Pure era playback resolution (unit-tested, no I/O).
   state: caller-owned object; mutated + returned so the caller can
   persist it. Returns a track object, or null = nothing playable
   in this era (unknown era, data-only era, or an empty queue);
   callers fall back to stage rotation / the procedural loop.
   Sequential advance with wrap; the Cape Jones main track leads
   every cycle because playableEraQueue puts it first and the
   cycle repeats the whole queue. */
export function resolveEraTrack({ erasDoc, libraryTracks, eraId, state }) {
  const st = state || {};
  const queue = playableEraQueue(erasDoc, libraryTracks, eraId);
  if (!queue.length) return null;
  const key = `era:${eraId}`;
  const idx = ((st[key] == null ? 0 : st[key]) % queue.length + queue.length) % queue.length;
  st[key] = (idx + 1) % queue.length;
  return queue[idx];
}

/* Consistency guard for the Settings-pool file (game/data/
   jukebox-pools.json, PR #1046) against the library. Returns a
   list of mismatch strings (empty = consistent). The pool file is
   NOT read here — the caller supplies its parsed pools object, so
   this stays testable without the file existing yet.
   Known mismatch this catches (2026-10-24): PR #1046's cape pool
   names mainTrack id 'ghost-surf-rock' with file
   'assets/music/ghost-surf-rock.mp3', but the canonical library
   entry is id 'cape-jones-ghost-surf-rock' with file
   'assets/music/cape-jones-ghost-surf-rock.mp3' — neither the id
   nor the file matches, so the pool's lead slot can never resolve
   to the downloaded file. Fix in the pools file: set mainTrack.id
   and mainTrack.file to the canonical values. */
export function checkPoolsConsistency({ libraryTracks, pools }) {
  const problems = [];
  const tracks = Array.isArray(libraryTracks) ? libraryTracks : [];
  const byId = new Map(tracks.map((t) => [t.id, t]));
  const byFile = new Map(tracks.filter((t) => t.file).map((t) => [t.file, t]));
  const list = (pools && pools.pools) || [];
  for (const pool of list) {
    const main = pool && pool.mainTrack;
    if (!main) continue;
    if (!byId.has(main.id)) {
      problems.push(`pool '${pool.id}': mainTrack id '${main.id}' is not a library track id`);
    } else if (main.file && byId.get(main.id).file !== main.file) {
      problems.push(`pool '${pool.id}': mainTrack file '${main.file}' does not match library file '${byId.get(main.id).file}' for id '${main.id}'`);
    }
    if (main.file && !byFile.has(main.file)) {
      problems.push(`pool '${pool.id}': mainTrack file '${main.file}' matches no library track file`);
    }
  }
  return problems;
}
