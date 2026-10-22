/* ============================================================
   WESTERN HEART — Voice Pipeline (VoiceEngine)
   File-based character voice: manifests in game/data/voices/<id>.json,
   recordings in game/assets/voices/<id>/. Dorowani is the pilot.

   Contract: docs/VOICE-PIPELINE.md
   • play() never throws: no manifest -> silent no-op; no audio file ->
     subtitle-only + console.info (placeholder policy — we never synth
     fake "voice" and present it as final).
   • Subtitles: single bottom-center layer, latest line wins.
   • Cutscene hook: playCue() — the cutscene timeline calls it; the
     engine treats cues like lines with explicit timing.
   ============================================================ */
import { audio } from './audio.js';

const SUB_ID = 'wh-voice-sub';
const SUB_HOLD_MS = 2200;

class VoiceEngine {
  constructor() {
    this.manifests = new Map(); // fighterId -> manifest object
    this.buffers = new Map();   // clip file url -> AudioBuffer
    this._loading = new Map();  // url -> in-flight decode promise
    this.enabled = true;
    this.debugBleeps = false;   // dev-only timing blips; NEVER on for the user
    this._subEl = null;
    this._subTimer = 0;
  }

  /* Must be called from a user gesture (mobile autoplay policy). Safe to
     call repeatedly; also builds the subtitle layer. Never throws —
     headless/test contexts without window are tolerated. */
  unlock() {
    try { if (typeof audio.unlock === 'function') audio.unlock(); } catch (e) { /* no window */ }
    this._ensureSubtitleLayer();
  }

  setEnabled(on) { this.enabled = !!on; }

  /* Fetch + cache a fighter's voice manifest. Returns null when the
     fighter has no voice yet — that is a normal state, not an error. */
  async loadManifest(fighterId) {
    if (!fighterId) return null;
    if (this.manifests.has(fighterId)) return this.manifests.get(fighterId);
    let man = null;
    try {
      const res = await fetch(`data/voices/${fighterId}.json`, { cache: 'force-cache' });
      if (res.ok) man = await res.json();
    } catch (e) { /* offline / not yet authored -> placeholder path */ }
    this.manifests.set(fighterId, man);
    if (!man) console.info(`[WH voice] no manifest for '${fighterId}' (voice not yet authored)`);
    return man;
  }

  /* Pick a clip for a trigger. variantIdx selects a specific variant;
     omitted -> random. Returns null when nothing is authored. */
  async _resolveClip(fighterId, trigger, variantIdx) {
    const man = await this.loadManifest(fighterId);
    if (!man || !Array.isArray(man.clips)) return null;
    const pool = man.clips.filter(c => c.trigger === trigger);
    if (!pool.length) return null;
    if (variantIdx == null) return pool[Math.floor(Math.random() * pool.length)];
    return pool[variantIdx % pool.length];
  }

  _clipById(fighterId, clipId) {
    const man = this.manifests.get(fighterId);
    if (!man || !Array.isArray(man.clips)) return null;
    return man.clips.find(c => c.id === clipId) || null;
  }

  /* Decode (and cache) a clip's audio file. Resolves null when the file
     is missing — the caller falls back to subtitle-only. */
  async _bufferFor(clip) {
    if (!clip || !clip.file) return null;
    if (this.buffers.has(clip.file)) return this.buffers.get(clip.file);
    if (this._loading.has(clip.file)) return this._loading.get(clip.file);
    const p = (async () => {
      try {
        const res = await fetch(clip.file, { cache: 'force-cache' });
        if (!res.ok) return null;
        const raw = await res.arrayBuffer();
        const ctx = audio.ctx;
        if (!ctx || !ctx.decodeAudioData) return null;
        const buf = await ctx.decodeAudioData(raw);
        this.buffers.set(clip.file, buf);
        return buf;
      } catch (e) {
        return null;
      } finally {
        this._loading.delete(clip.file);
      }
    })();
    this._loading.set(clip.file, p);
    return p;
  }

  /* Fire-and-forget: play a random (or indexed) clip for a trigger.
     Never throws, never blocks the caller (e.g. the 3 s win beat). */
  play(fighterId, trigger, variantIdx) {
    if (!this.enabled || !fighterId || !trigger) return;
    this._resolveClip(fighterId, trigger, variantIdx).then(clip => {
      if (!clip) return;
      this._speak(fighterId, clip, clip.text);
    }).catch(() => {});
  }

  /* Awaitable explicit line: used by intro interactions & cutscenes.
     subtitleOverride lets the beat text differ from the manifest text. */
  async playLine(fighterId, clipId, subtitleOverride) {
    if (!this.enabled) return;
    await this.loadManifest(fighterId);
    const clip = this._clipById(fighterId, clipId);
    const text = subtitleOverride || (clip && clip.text) || '';
    if (!clip) {
      // No authored clip: still show the beat's subtitle so the
      // interaction reads correctly before recordings exist.
      if (text) this.subtitle(fighterId, text);
      console.info(`[WH voice] placeholder line for '${fighterId}' (no clip '${clipId}' yet)`);
      await this._wait(SUB_HOLD_MS);
      return;
    }
    await this._speak(fighterId, clip, text);
  }

  /* Cutscene timeline hook (see docs/CUTSCENE-SPEC.md): a cue is
     { fighter, clip, text, at } — the timeline schedules it. */
  async playCue(cue) {
    if (!cue) return;
    await this.playLine(cue.fighter, cue.clip, cue.text);
  }

  async _speak(fighterId, clip, text) {
    if (text) this.subtitle(fighterId, text);
    const placeholder = !clip.file || clip.status === 'placeholder';
    const buf = placeholder ? null : await this._bufferFor(clip);
    if (buf && audio.ctx && audio.enabled) {
      try {
        const src = audio.ctx.createBufferSource();
        src.buffer = buf;
        const bus = (typeof audio.voiceBus === 'function') ? audio.voiceBus() : null;
        src.connect(bus || audio.ctx.destination);
        src.start();
        console.info(`[WH voice] ${fighterId}/${clip.id} playing (${clip.file})`);
        await this._wait(Math.min(6000, (buf.duration * 1000) + 350));
        return;
      } catch (e) { /* fall through to subtitle-only */ }
    }
    if (this.debugBleeps) this._bleep();
    if (placeholder || !buf) {
      console.info(`[WH voice] placeholder — '${fighterId}/${clip.id}': "${text}" (no recording yet)`);
    }
    await this._wait(SUB_HOLD_MS);
  }

  /* Dev-only timing blip. audibly NOT a voice — never enabled in user builds. */
  _bleep() {
    if (typeof audio._osc === 'function' && audio.enabled) {
      const t = audio.now;
      audio._osc('square', 660, t, t + 0.09, 0.08);
    }
  }

  _wait(ms) { return new Promise(r => setTimeout(r, ms)); }

  /* ---- subtitles ---- */
  _ensureStyle() {
    if (typeof document === 'undefined' || document.getElementById('wh-voice-style')) return;
    const st = document.createElement('style');
    st.id = 'wh-voice-style';
    st.textContent = `
#wh-voice-sub { position: fixed; left: 0; right: 0; bottom: max(12vh, 64px); z-index: 216;
  display: none; justify-content: center; pointer-events: none;
  padding: 0 16px; text-align: center; }
#wh-voice-sub.show { display: flex; }
#wh-voice-sub .wh-voice-name { color: var(--gold, #ffb14d); font-weight: 800;
  letter-spacing: 2px; font-size: 13px; margin-right: 10px;
  text-shadow: 0 2px 8px #000; }
#wh-voice-sub .wh-voice-line { color: #fff; font-size: 18px; font-weight: 600;
  text-shadow: 0 2px 10px #000, 0 0 24px rgba(0,0,0,.8); }`;
    document.head.appendChild(st);
  }

  _ensureSubtitleLayer() {
    if (this._subEl || typeof document === 'undefined') return;
    this._ensureStyle();
    let el = document.getElementById(SUB_ID);
    if (!el) {
      el = document.createElement('div');
      el.id = SUB_ID;
      el.setAttribute('aria-live', 'polite');
      document.body.appendChild(el);
    }
    this._subEl = el;
  }

  subtitle(fighterId, text) {
    this._ensureSubtitleLayer();
    if (!this._subEl || !text) return;
    const label = (fighterId || '').toUpperCase();
    this._subEl.innerHTML = '';
    const name = document.createElement('span');
    name.className = 'wh-voice-name';
    name.textContent = label;
    const line = document.createElement('span');
    line.className = 'wh-voice-line';
    line.textContent = text;
    this._subEl.appendChild(name);
    this._subEl.appendChild(line);
    this._subEl.classList.add('show');
    clearTimeout(this._subTimer);
    this._subTimer = setTimeout(() => this._subEl && this._subEl.classList.remove('show'), SUB_HOLD_MS);
  }
}

export const voice = new VoiceEngine();
