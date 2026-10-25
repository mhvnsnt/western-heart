/* ============================================================
   WESTERN HEART — Announcer event resolver (2026-10-24, Lane 4)
   Pure mapping from fight/select events to the announcer
   manifest (game/data/voices/announcer.json). No DOM, no fetch,
   no audio bytes: the announcer bank on main is SUBTITLE-ONLY
   placeholders (11 clips, no files), so this resolver returns
   clip ids + status and the voice engine (game/js/voice.js
   announce()) decides subtitle vs audio. No stage sounds, music,
   or SFX are ever presented as dialogue here — this table maps
   announcer calls only.

   Audit result baked into game/data/announcer-events.json:
   round-start / fight / KO / double-KO / perfect / time-up /
   draw / win clips EXIST as placeholders; character-select has
   NO clip (status 'needs-recording', clipId null — the line is
   to be written/recorded by the canon/voice lane, never invented
   here and never synth-presented as final).

   Hook status (audited 2026-10-24 over game/js/main.js, game.js,
   modes.js, fighter.js, select-screen.js, episodes.js,
   versus-setup.js, stage-intros.js, combat-core.js, wh-boot.js):
   NO call site for voice.announce() was found in those files.
   The engine method exists (voice.announce(trigger)); the fight
   and select flows do not call it yet. Wire it at the hook points
   named in announcer-events.json — that wiring edit belongs to
   the fight/select lanes (this lane does not touch fighter.js,
   menus/HTML, or story files).
   ============================================================ */

export function resolveAnnouncerClip(eventsDoc, eventName, opts = {}) {
  const events = (eventsDoc && eventsDoc.events) || {};
  const ev = events[eventName];
  if (!ev) return null;
  const cid = (c) => (c && (c.clipId || c.id)) || null;
  if (eventName === 'round-start') {
    if (opts.finalRound) {
      const clip = (ev.clips || []).find((c) => cid(c) === 'final-round');
      return clip ? { event: eventName, clipId: cid(clip), trigger: clip.trigger, status: clip.status } : null;
    }
    const n = opts.round;
    const clip = (ev.clips || []).find((c) => cid(c) === `round-${n}`);
    return clip ? { event: eventName, clipId: cid(clip), trigger: clip.trigger, status: clip.status } : null;
  }
  const clips = ev.clips || [];
  if (!clips.length) {
    return { event: eventName, clipId: null, trigger: ev.trigger || null, status: ev.status || 'needs-recording' };
  }
  const clip = clips[0];
  return { event: eventName, clipId: cid(clip), trigger: clip.trigger, status: clip.status };
}

export function announcerEventNames(eventsDoc) {
  return Object.keys((eventsDoc && eventsDoc.events) || {});
}
