// ANIMATION GATE (owner t117u, 2026-10-23). Hard wall between show/story clips and fight movesets.
// Contexts: FIGHT (live gameplay), INTRO_OUTRO, CUTSCENE, SHOW.
// - FIGHT: only moveset clips. Any show clip (userData.animSet === 'show') is rejected + logged.
// - Fight clip outside FIGHT: only if listed in game/data/crossover.json fight_to_show.
// - Show clip outside FIGHT: only if listed in crossover.json show_to_fight for that context.
// Pure JS, no THREE dependency, so CI can test it in node.
export const CTX = Object.freeze({ FIGHT: 'FIGHT', INTRO_OUTRO: 'INTRO_OUTRO', CUTSCENE: 'CUTSCENE', SHOW: 'SHOW' });

const DEFAULT_CROSSOVER = {
  fight_to_show: { allowed_contexts: ['SHOW', 'CUTSCENE', 'INTRO_OUTRO'], clips: ['stance', 'intro', 'light', 'medium', 'heavy', 'win', 'walkFwd', 'walkBack', 'block', 'hit', 'sidestepA', 'sidestepB'] },
  show_to_fight: { allowed_contexts: ['INTRO_OUTRO', 'CUTSCENE', 'SHOW'], clips: ['idle', 'walk', 'run', 'sit_idle', 'sit_stand', 'sit_couch', 'talk_gesture', 'wave', 'react_laugh', 'react_anger', 'drink'] },
};
let _xo = DEFAULT_CROSSOVER;
let _ctx = CTX.FIGHT; // default is the strictest context
export const gateLog = []; // { t, ctx, clip, set, verdict, reason }

export function setCrossover(json) {
  if (!json || !json.fight_to_show || !json.show_to_fight) throw new Error('anim-gate: bad crossover json');
  if ((json.show_to_fight.allowed_contexts || []).includes(CTX.FIGHT)) throw new Error('anim-gate: show_to_fight may never allow FIGHT (needs a moveset PR)');
  _xo = json;
}
export function setAnimContext(ctx) { if (!CTX[ctx]) throw new Error('anim-gate: unknown context ' + ctx); _ctx = ctx; }
export function getAnimContext() { return _ctx; }

/** Tag a clip as a show clip. Every loader of anims/show/ must call this. */
export function markShowClip(clip, slot) {
  clip.userData = clip.userData || {};
  clip.userData.animSet = 'show';
  clip.userData.showSlot = slot || clip.name;
  return clip;
}
export function isShowClip(clip) { return !!(clip && clip.userData && clip.userData.animSet === 'show'); }

/** Decide whether `clip` (named `name`) may play in `ctx`. Returns { ok, reason } and logs rejections. */
export function checkClip(name, clip, ctx = _ctx) {
  const show = isShowClip(clip) || /^show[:/]/.test(name) || String(name).includes('anims/show/');
  let ok, reason;
  if (ctx === CTX.FIGHT) {
    ok = !show; reason = show ? 'show clip in FIGHT' : 'moveset clip';
  } else if (show) {
    const slot = (clip && clip.userData && clip.userData.showSlot) || String(name).replace(/^show[:/]/, '').split('/').pop();
    ok = _xo.show_to_fight.allowed_contexts.includes(ctx) && _xo.show_to_fight.clips.includes(slot);
    reason = ok ? 'show clip allowlisted' : 'show clip not allowlisted for ' + ctx;
  } else {
    const base = String(name).replace(/^row:.*/, 'row');
    ok = _xo.fight_to_show.allowed_contexts.includes(ctx) && _xo.fight_to_show.clips.includes(base);
    reason = ok ? 'fight clip allowlisted' : 'fight clip not allowlisted for ' + ctx;
  }
  if (!ok) {
    gateLog.push({ t: Date.now(), ctx, clip: name, set: show ? 'show' : 'fight', verdict: 'rejected', reason });
    if (typeof console !== 'undefined') console.warn(`[WH-ANIM-GATE] rejected '${name}' in ${ctx}: ${reason}`);
  }
  return { ok, reason };
}

/** Filter a { name: clip } map down to what `ctx` allows. Used by createT3Actions. */
export function gateClips(clips, ctx = _ctx) {
  const out = {};
  for (const [n, c] of Object.entries(clips || {})) if (checkClip(n, c, ctx).ok) out[n] = c;
  return out;
}
