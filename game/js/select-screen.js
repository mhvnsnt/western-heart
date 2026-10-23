/* ============================================================
   WESTERN HEART — Tekken-style character select (T7 rebuild, 2026-10-23)
   Rebuilt from the TEKKEN 7 character select (layout lineage decoded in
   docs/select-redesign/T7-GRID-DECODE.md; TTT2 contributes the two-cursor
   flow and the "?" hidden-fighter convention):
   - "CHOOSE YOUR FIGHTER" header + 99s timer (T7 standard selector)
   - the signature 2-ROW PORTRAIT GRID, P1's big render flanking left,
     P2's flanking right; P1 red / P2 blue cursors with 1P/2P tags
   - "?" RANDOM panel at the end of the grid (T6/T7 convention)
   - costume presets ON the select screen (T7's triangle-preset ->
     our P/K attire buttons + attire chips, owner's classic scheme)
   - announcer cues at T7's cue points: "Choose your fighter!" on
     entry, the fighter's name shouted on lock, "Choose your stage!"
     + stage-name callouts on the arena strip
   - stage select AFTER both fighters lock (T7 flow), then the fight
   Earlier lineage (kept): the T8 grid transplant's live-3D preview
   panes (owner law: live animated 3D, never a still), the T3 aperture
   rule (selected card renders larger), the classic punch=attire-1 /
   kick=attire-2 rule, the ui-skin.js skin layer (the intact 't8' skin
   restores the T8 look later via setSkin('t8') — no restructuring).
   Owner spec (2026-10-18, still standing): the page itself never
   scrolls; the grid scrolls inside its own box (horizontal now, T7);
   tap a card -> that fighter's animated model appears on YOUR side;
   name + style + stats on the picked side; attire switching on the
   select screen; touch first, 48px+ targets.
   Previews reuse the existing model pipeline (assets.js
   loadModels/createInstance) — the same GLBs and Idle clips the fight
   itself uses. Stats shown are the game's real numbers: roster `stats`
   or the Fighter default (fighter.js). No invented fighters, no
   invented stats, no Tekken names on the cards (in-universe law).
   ============================================================ */
import * as THREE from 'three';
import { assets } from './assets.js';
import { attiresFor, selectedAttireModel, setAttire, attireLabel } from './attires.js';
import { loadT3Clips, createT3Actions, retargetT3Clips } from './t3anims.js';
import { bankIdFor } from './fighter.js';
import { getMovesetInfo } from './movesets.js';
import { voice } from './voice.js';
import { getSkin, applySkin, activeSkinId } from './ui-skin.js';

const DEFAULT_STATS = { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 };
const clamp01 = (v) => Math.max(0, Math.min(1, v));

export function statsFor(c) {
  const s = { ...DEFAULT_STATS, ...(c && c.stats ? c.stats : {}) };
  if (s.speed > 3.5) s.speed = 3.5; // same clamp the Fighter applies
  return s;
}

/* ---------------- one side's live 3D preview pane ---------------- */
class PreviewPane {
  constructor(canvas, side) {
    this.side = side; // 'p1' | 'p2'
    this.canvas = canvas;
    // The renderer is created LAZILY on first use and its creation is
    // failure-proof: THREE.WebGLRenderer throws when a context cannot
    // be created, and that must never take down game init (the old
    // single preview also created its renderer lazily). A pane whose
    // GPU is unavailable degrades to the fighter's portrait plate.
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.failed = false;
    this.mixer = null;
    this.model = null;
    this.hasStance = false;
    this.baseRotY = side === 'p1' ? 0.18 : -0.18;
    this._token = 0;
    this._loading = false;
    this._bodyScale = 1;
    this._fitW = 0; this._fitH = 0; this._fitCY = 0;
    const host = canvas.parentElement;
    new ResizeObserver(() => this._resize()).observe(host);
  }

  /* Create renderer/scene/camera on first use. Returns false when
     WebGL is unavailable — the pane then degrades gracefully. */
  _ensure() {
    if (this.renderer) return true;
    if (this.failed) return false;
    try {
      this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
    } catch (e) {
      console.warn('[WH] select preview: WebGL unavailable on this device', e.message || e);
      this.failed = true;
      return false;
    }
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.scene = new THREE.Scene();
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x332244, 1.1));
    const key = new THREE.DirectionalLight(0xffffff, 1.6);
    key.position.set(2.5, 4, 3); this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x9fd8ff, 0.9);
    rim.position.set(-3, 2, -2.5); this.scene.add(rim);
    const gold = new THREE.PointLight(0xffb14d, 12, 12);
    gold.position.set(0, 0.4, 2.2); this.scene.add(gold);
    this.camera = new THREE.PerspectiveCamera(32, 1, 0.01, 50);
    this.camera.position.set(0, 1.15, 3.4);
    this.camera.lookAt(0, 0.95, 0);
    this._resize();
    return true;
  }

  _resize() {
    if (!this.renderer || !this.camera) return;
    const host = this.canvas.parentElement;
    if (!host) return;
    const w = host.clientWidth, h = host.clientHeight;
    if (w < 2 || h < 2) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this._frame();
  }

  /* Frame the model from its measured bind-pose bounds: the camera
     pulls back until BOTH the figure's height and its width (a
     T-pose arm span is as wide as the model is tall) fit the pane.
     The old single preview only had to fit one wide canvas; a
     half-screen phone pane is tall and narrow, so width rules. */
  _frame() {
    if (!this.camera) return;
    const s = this._bodyScale;
    const aspect = Math.max(this.camera.aspect || 1, 0.2);
    const tanH = Math.tan(THREE.MathUtils.degToRad(this.camera.fov / 2));
    const w = (this._fitW || 1) * s, h = (this._fitH || 2) * s;
    const dist = THREE.MathUtils.clamp(
      Math.max(3.4 * s, (h * 0.62) / tanH, (w * 0.62) / (tanH * aspect)), 3.2, 11);
    const cy = (this._fitCY || 0.95) * s;
    this.camera.position.set(0, cy + 0.18 * s, dist);
    this.camera.lookAt(0, cy, 0);
  }

  /* Show a fighter (roster entry) with a specific attire model id.
     Resolves false when the model could not be loaded. */
  async show(c, modelId) {
    const token = ++this._token;
    this._loading = true;
    if (!this._ensure()) { this._loading = false; return false; }
    try {
      await assets.loadModels([modelId]);
      if (token !== this._token) return true; // superseded by a newer tap
      const inst = assets.createInstance(
        modelId, c.colors?.suit ?? 0xffffff, c.colors?.trim ?? 0x888888,
        c.colorize ? (c.tintStrength ?? 0.3) : 0); // TINT FIX: own textures, no palette wash (real colors)
      this._clearModel();
      this.model = inst.model;
      this.model.rotation.y = this.baseRotY;
      this._bodyScale = c.bodyScale || 1;
      const bb = new THREE.Box3().setFromObject(inst.model);
      const sz = bb.getSize(new THREE.Vector3());
      if (sz.y > 0.1) { this._fitW = sz.x; this._fitH = sz.y; this._fitCY = bb.min.y + sz.y / 2; }
      this._frame();
      this.scene.add(this.model);
      this.mixer = inst.mixer;
      this.hasStance = false;
      // REAL TEKKEN IDLE (owner: use the teardown files; NO-T-POSE
      // law): where this fighter's moveset source has a decoded T3
      // bank, play the bank's looping stance clip on the preview
      // mixer — the exact clips and binding rule the fight itself
      // uses (fighter.js: bank actions only when the model carries
      // the canonical Hips/RightArm bones). The GLBs' embedded
      // 'Idle' clips are near-static bind-pose holds (verified by
      // sampling demonio.glb: arm-bone swing ~0.02 rad), so the
      // bank stance takes precedence wherever a bank exists.
      // Bind-pose reference (shoulder orientations) for the fit gate,
      // sampled from this instance before any bank clip is applied.
      let bindQ = null;
      if (inst.bones && inst.bones.LeftShoulder && inst.bones.RightShoulder) {
        this.model.updateWorldMatrix(true, true);
        bindQ = {
          LeftShoulder: inst.bones.LeftShoulder.getWorldQuaternion(new THREE.Quaternion()),
          RightShoulder: inst.bones.RightShoulder.getWorldQuaternion(new THREE.Quaternion()),
        };
      }
      try {
        // The fighter's OWN moveset file decides its bank (its base's motion), same as in the fight.
        const bank = bankIdFor(c.id, getMovesetInfo(c.id) ? c.id : (c.moveset || c.id));
        const clips = bank ? await loadT3Clips(THREE, bank) : null;
        if (token !== this._token) return true; // superseded while loading
        if (clips && clips.stance && inst.bones && inst.bones.Hips && inst.bones.RightArm && inst.bones.Head) {
          // Retargeted onto this rig (t3anims.js retargetT3Clips) — the
          // raw bank quaternions only fit the rig they were baked onto.
          const t3 = createT3Actions(inst.mixer, retargetT3Clips(clips, bank, inst.model, THREE, modelId) || {}, THREE);
          if (t3.stance) {
            if (inst.actions && inst.actions.Idle) inst.actions.Idle.setEffectiveWeight(0);
            t3.stance.setEffectiveWeight(1);
            t3.stance.play();
            // Retarget sanity checks, measured not guessed, on the
            // sampled pose: (a) the head stays well above the hips —
            // a bank applied against an incompatible bind pose
            // pitches the body flat or upside down; (b) each hand
            // stays within its arm's anatomical reach of the upper
            // arm — gyro-displaced limbs violate this. A stance
            // failing either check is rejected and the preview
            // falls back rather than show a mangled model; when
            // the bank data is fixed upstream the same checks pass
            // and the real stance appears with no select changes.
            inst.mixer.update(0.05);
            this.model.updateWorldMatrix(true, true);
            const gp = (b) => b.getWorldPosition(new THREE.Vector3());
            const hv = gp(inst.bones.Head), wv = gp(inst.bones.Hips);
            let fit = hv.y - wv.y > 0.25;
            let why = fit ? '' : `head-hips gap ${(hv.y - wv.y).toFixed(2)}`;
            if (fit) {
              for (const s of ['Left', 'Right']) {
                const arm = inst.bones[s + 'Arm'], fore = inst.bones[s + 'ForeArm'], hand = inst.bones[s + 'Hand'];
                if (!arm || !fore || !hand) continue;
                // bone segment lengths are pose-invariant
                const reach = (gp(arm).distanceTo(gp(fore)) + gp(fore).distanceTo(gp(hand))) * 1.25 + 0.05;
                if (gp(arm).distanceTo(gp(hand)) > reach) { fit = false; why = `${s} hand beyond arm reach`; break; }
              }
            }
            if (fit && bindQ) {
              // (c) clavicle check: shoulder bones are near-rigid
              // parts of the torso in any real stance; a clip that
              // swings them far from bind is misapplied (the
              // gyro-shoulder failure), even when the hands stay
              // within reach.
              for (const s of ['Left', 'Right']) {
                const sh = inst.bones[s + 'Shoulder'];
                if (!sh) continue;
                const ang = sh.getWorldQuaternion(new THREE.Quaternion()).angleTo(bindQ[s + 'Shoulder']);
                if (ang > 0.6) { fit = false; why = `${s} shoulder swung ${(ang).toFixed(2)} rad from bind`; break; }
              }
            }
            if (fit) {
              this.hasStance = true;
            } else {
              console.warn(`[WH] select preview: bank '${bank}' stance does not fit ${c.id}'s rig (${why}) — falling back`);
              t3.stance.stop();
              t3.stance.setEffectiveWeight(0);
              if (inst.actions && inst.actions.Idle) inst.actions.Idle.setEffectiveWeight(1);
            }
          }
        }
      } catch (e) {
        console.warn('[WH] select preview: T3 stance unavailable for', c.id, e.message || e);
      }
      return true;
    } catch (e) {
      if (token === this._token) {
        console.warn('[WH] select preview failed for', modelId, e.message || e);
        this._clearModel();
      }
      return false;
    } finally {
      if (token === this._token) this._loading = false;
    }
  }

  _clearModel() {
    if (!this.model) { this.mixer = null; return; }
    if (this.scene) this.scene.remove(this.model);
    // Materials are per-instance clones (assets.createInstance) — dispose
    // them; geometry/textures belong to the cached GLTF and stay shared.
    this.model.traverse((o) => {
      if (o.isMesh && o.material) {
        (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => m.dispose());
      }
    });
    this.model = null;
    this.mixer = null;
    this.hasStance = false;
  }

  clear() { this._token++; this._clearModel(); }

  update(dt) {
    if (!this.renderer || !this.scene || !this.camera) return;
    if (this.mixer) this.mixer.update(dt);
    // Unless a validated teardown-bank stance is playing, the model
    // presents on a slow turntable (the pre-existing preview
    // presentation) — live 3D, never a still image. The GLBs'
    // embedded clips keep playing underneath either way.
    if (this.model && !this.hasStance && !this._loading) {
      this.model.rotation.y += dt * 0.35 * (this.side === 'p1' ? 1 : -1);
    }
    this.renderer.render(this.scene, this.camera);
  }
}

/* ---------------- the select screen controller ---------------- */
/*
 deps: {
   roster:   () => [rosterEntry...]   (already includes custom fighter)
   findChar: (id) => rosterEntry|null
   audio:    audio manager (uiClick)
   onHighlight: (entryOrNull) => {}   (main.js mirrors selectedChar)
 }
*/
/* Fighters with the owner's Tripo 3D models show first (owner 2026-10-21: "show all the fighters
   that have tripo 3D models ... first at the top ... not people ... that don't have models in the
   top rows"). The list is generated from the registry + the GLB files themselves by
   tools/roster/tripo_fighters.py -> data/tripo-fighters.json (no hand-picked order). */
let TRIPO_IDS = null;
const _tripoReady = fetch('data/tripo-fighters.json')
  .then(r => (r.ok ? r.json() : null))
  .then(j => { TRIPO_IDS = new Set((j && j.ids) || []); })
  .catch(() => { TRIPO_IDS = new Set(); });
/* SmutBase primaries (owner intake 2026-10-22; extended display-order law
   2026-10-23: user-hand-picked SmutBase models count JUST AS GOOD as Tripo
   pulls — the hand-chosen model IS the character's primary model). They
   lead the grid right behind the Tripo originals. Same fetch pattern as
   the Tripo list: data-driven, never a hand-picked order in code. */
let SMUTBASE_IDS = null;
const _smutReady = fetch('data/smutbase-fighters.json')
  .then(r => (r.ok ? r.json() : null))
  .then(j => { SMUTBASE_IDS = new Set((j && j.ids) || []); })
  .catch(() => { SMUTBASE_IDS = new Set(); });
const _tiersReady = Promise.all([_tripoReady, _smutReady]);

export function createSelectScreen(deps) {
  const { audio } = deps;
  const $ = (id) => document.getElementById(id);
  const strip = $('char-grid');
  const hint = $('select-hint');
  const confirmBtn = $('confirm-fighter');

  const panes = {
    p1: new PreviewPane($('pane-canvas-p1'), 'p1'),
    p2: new PreviewPane($('pane-canvas-p2'), 'p2'),
  };
  const clock = new THREE.Clock();
  let raf = 0;
  const loop = () => {
    raf = requestAnimationFrame(loop);
    const sel = $('screen-select');
    if (!sel || !sel.classList.contains('active')) return;
    const dt = Math.min(clock.getDelta(), 0.05);
    panes.p1.update(dt);
    panes.p2.update(dt);
  };
  loop();

  const state = {
    mode: null,
    phase: 'pick',        // 'pick' | 'done'
    activeSide: 'p1',     // whose cursor is live
    highlight: { p1: null, p2: null },  // roster entry previewed per side
    locked: { p1: null, p2: null },     // confirmed entries
    teamPicks: [],        // team mode: confirmed ids (all on p1)
    kickCycle: 1,         // K button attire cycling position
    focusIdx: 0,
  };

  /* ---------- card strip ---------- */
  function portraitHTML(c) {
    // Portrait files are the personality pass's drop-in point: the same
    // assets/portraits/<id>.png path the grid has always used. A fighter
    // with no portrait yet gets a monogram plate — never another fighter's
    // face (the old repeated-placeholder bug). T7's panels carry the
    // portrait + the fighter's name; style/stats live on the side plate.
    return `<div class="portrait"><img src="assets/portraits/${c.id}.png" alt="${c.name}" loading="lazy"
      onerror="this.parentElement.classList.add('no-portrait');this.remove();">
      <span class="mono">${(c.name || '?').slice(0, 2)}</span></div>
      <div class="cname">${c.name}</div>`;
  }

  /* Owner law (2026-10-22): NO duplicate fighters on select. Entries that
     share another fighter's model are hidden until they get their own
     models — they stay in the roster data for story/other modes, but never
     as separate select cards. Attire variants live in the attire ladder
     (renderAttires), not as duplicate cards.
     NINE SOULS REDESIGN (2026-10-23): seven souls stay OFF the grid as
     standalone cards (rin, byou, tou, sha, kai, retsu — plus the re-homed
     jin, whose model now ladders inside Phantom's attires per the
     2026-10-22 re-home; 'jin_soul' no longer exists as a roster id).
     ZEN and GYOU STAY as standalone selectable fighters. */
  const SELECT_HIDDEN = new Set([
    'rin', 'byou', 'tou', 'sha', 'kai', 'retsu',
    'ryuji', 'doc-frank-machine-shop',
  ]);
  const selectRoster = () => deps.roster().filter(c => !SELECT_HIDDEN.has(c.id));

  /* T7 grid order: the display-order law tiers, in order —
     TRIPO ORIGINALS, then SMUTBASE ORIGINALS (the 6 hand-picked primaries),
     then MAIN ROSTER. Within a tier, roster order is kept (the roster
     itself is built from the replacement map: one WH card per Tekken slot,
     WH names only — Tekken names never appear on in-universe cards). */
  function tieredRoster() {
    const roster = selectRoster();
    const tripo = TRIPO_IDS || new Set();
    const smut = SMUTBASE_IDS || new Set();
    const tiers = [
      { label: 'TRIPO ORIGINALS', fighters: roster.filter(c => tripo.has(c.id)) },
      { label: 'SMUTBASE ORIGINALS', fighters: roster.filter(c => !tripo.has(c.id) && smut.has(c.id)) },
      { label: 'MAIN ROSTER', fighters: roster.filter(c => !tripo.has(c.id) && !smut.has(c.id)) },
    ];
    return tiers.filter(t => t.fighters.length);
  }

  function build() {
    if (!strip) return;
    // Skin drop-in contract: the look refreshes from ui-skin.js here —
    // T8 art restores via setSkin('t8') with no restructuring.
    applySkin($('screen-select'), getSkin(activeSkinId()));
    strip.innerHTML = '';
    /* T7's signature 2-row portrait grid: column-major flow (each column
       holds 2 cards), horizontal scroll inside its own box. Slim tier
       dividers span both rows so the display-order law stays visible.
       Every card carries data-tier/data-col/data-row for exact 2D
       cursor navigation (d-pad parity with T7). */
    for (const { label, fighters } of tieredRoster()) {
      const div = document.createElement('div');
      div.className = 'grid-tier';
      div.setAttribute('aria-hidden', 'true');
      div.innerHTML = `<span>${label}</span>`;
      strip.appendChild(div);
      let col = 0, row = 0;
      for (const c of fighters) {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.dataset.id = c.id;
        card.dataset.tier = label;
        card.dataset.col = String(col);
        card.dataset.row = String(row);
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `Select ${c.name}`);
        card.innerHTML = portraitHTML(c);
        card.addEventListener('click', () => onCardTap(c, card));
        strip.appendChild(card);
        if (row === 1) { col++; row = 0; } else { row = 1; }
      }
    }
    // Tekken convention: a "?" random slot at the end of the grid.
    const rnd = document.createElement('div');
    rnd.className = 'char-card random-card';
    rnd.dataset.id = '__random';
    rnd.dataset.tier = '__random';
    rnd.setAttribute('role', 'button');
    rnd.setAttribute('tabindex', '0');
    rnd.setAttribute('aria-label', 'Random fighter');
    rnd.innerHTML = `<div class="portrait"><span class="qmark">?</span></div>
      <div class="cname">RANDOM</div>`;
    rnd.addEventListener('click', () => {
      const pool = selectRoster().filter(c => c.id !== state.locked.p1?.id && c.id !== state.locked.p2?.id);
      const pick = pool[Math.floor(Math.random() * pool.length)];
      if (pick) highlight(pick, { fromTap: true, scroll: true });
    });
    strip.appendChild(rnd);
  }

  /* T7 tap rule: tapping a card previews it on your side; tapping the
     ALREADY-highlighted card locks it (same as the CONFIRM button) —
     no dead ends, every tap does something visible. */
  function onCardTap(c, card) {
    card.classList.remove('tap-flash');
    void card.offsetWidth;
    card.classList.add('tap-flash');
    const side = state.activeSide;
    if ((state.highlight[side] && state.highlight[side].id === c.id) ||
        (state.locked[side] && state.locked[side].id === c.id)) {
      if (confirmBtn && !confirmBtn.disabled) confirmBtn.click();
      return;
    }
    highlight(c, { fromTap: true });
  }

  function allCards() { return [...strip.querySelectorAll('.char-card')]; }
  function cardFor(id) { return strip.querySelector(`.char-card[data-id="${id}"]`); }

  function paintCards() {
    allCards().forEach((el) => {
      const id = el.dataset.id;
      el.classList.toggle('cursor-p1', state.highlight.p1?.id === id && state.activeSide === 'p1');
      el.classList.toggle('cursor-p2', state.highlight.p2?.id === id && state.activeSide === 'p2');
      el.classList.toggle('selected',
        (state.highlight.p1?.id === id && state.activeSide === 'p1') ||
        (state.highlight.p2?.id === id && state.activeSide === 'p2'));
      el.classList.toggle('locked-p1', state.locked.p1?.id === id);
      el.classList.toggle('locked-p2', state.locked.p2?.id === id);
      el.classList.toggle('in-team', state.teamPicks.includes(id));
    });
  }

  /* ---------- side plates ---------- */
  function plateEls(side) {
    const root = $(side === 'p1' ? 'pane-p1' : 'pane-p2');
    return {
      root,
      name: root.querySelector('.pane-name'),
      title: root.querySelector('.pane-title'),
      style: root.querySelector('.pane-style'),
      facts: root.querySelector('.pane-facts'),
      stats: root.querySelector('.pane-stats'),
      attires: root.querySelector('.pane-attires'),
      note: root.querySelector('.pane-note'),
      lock: root.querySelector('.lock-badge'),
      tag: root.querySelector('.side-tag'),
    };
  }

  function statRow(label, value, frac, fmt) {
    return `<div class="stat-row"><span class="stat-lab">${label}</span>
      <span class="stat-bar"><i style="width:${Math.round(clamp01(frac) * 100)}%"></i></span>
      <span class="stat-val">${fmt(value)}</span></div>`;
  }

  function renderPlate(side) {
    const els = plateEls(side);
    const locked = state.locked[side];
    const c = locked || state.highlight[side];
    const isActive = state.activeSide === side && !locked;
    els.root.classList.toggle('is-active', isActive);
    els.root.classList.toggle('is-locked', !!locked);
    els.lock.hidden = !locked;
    if (!c) {
      els.name.textContent = side === 'p1' ? 'PLAYER 1' : 'PLAYER 2';
      els.title.textContent = state.mode === 'versus' && side === 'p2' && !state.locked.p1
        ? 'Waiting for P1…' : 'Pick a fighter';
      els.style.textContent = '';
      els.stats.innerHTML = '';
      els.attires.innerHTML = '';
      els.note.hidden = true;
      return;
    }
    els.name.textContent = c.name || '—';
    els.title.textContent = c.title || '';
    const modelId = selectedAttireModel(c);
    els.style.textContent = [c.style, c.archetype, attireLabel(c, modelId)]
      .filter(Boolean).join(' · ');
    // Skin-driven fact block (ui-skin.js `facts`: [LABEL, fighter field]).
    // Values come from the roster entry; unknown origin stays the canon
    // "Parts unknown" — never invented.
    if (els.facts) {
      const skin = getSkin(activeSkinId());
      els.facts.innerHTML = (skin.facts || []).map(([lab, field]) => {
        const v = c[field] || (field === 'origin' ? 'Parts unknown' : '—');
        return `<div class="fact"><span class="fact-lab">${lab}</span>` +
          `<span class="fact-val">${v}</span></div>`;
      }).join('');
    }
    const s = statsFor(c);
    els.stats.innerHTML =
      statRow('POW', s.power, (s.power - 0.5) / 1.5, v => v.toFixed(2)) +
      statRow('SPD', s.speed, s.speed / 3.5, v => v.toFixed(1)) +
      statRow('JMP', s.jump, s.jump / 10, v => v.toFixed(1)) +
      statRow('DEF', s.defense, (s.defense - 0.5) / 1.5, v => v.toFixed(2));
    renderAttires(side, c, !locked && isActive);
  }

  function renderAttires(side, c, interactive) {
    const els = plateEls(side);
    const list = attiresFor(c);
    const sel = selectedAttireModel(c);
    els.attires.innerHTML = '';
    if (list.length < 2) return;
    list.forEach((a) => {
      const chip = document.createElement('button');
      chip.className = 'attire-chip' + (a.model === sel ? ' on' : '');
      chip.type = 'button';
      chip.textContent = a.label;
      chip.disabled = !interactive;
      chip.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!interactive) return;
        audio.uiClick();
        applyAttire(side, c, a.model);
      });
      els.attires.appendChild(chip);
    });
  }

  /* ---------- preview + attire application ---------- */
  async function showOnSide(side, c) {
    const modelId = selectedAttireModel(c);
    const els = plateEls(side);
    const fb = els.root.querySelector('.pane-fallback');
    els.note.hidden = false;
    els.note.textContent = 'LOADING…';
    const ok = await panes[side].show(c, modelId);
    if (state.highlight[side]?.id !== c.id && state.locked[side]?.id !== c.id) return;
    if (panes[side].failed) {
      // No WebGL on this device: show the posed portrait plate
      // instead of the live model, and say so honestly.
      if (fb) { fb.src = `assets/portraits/${c.id}.png`; fb.hidden = false; }
      els.note.hidden = false;
      els.note.textContent = '3D UNAVAILABLE';
      return;
    }
    if (fb) fb.hidden = true;
    els.note.hidden = ok;
    if (!ok) els.note.textContent = 'MODEL PENDING';
  }

  function applyAttire(side, c, modelId) {
    setAttire(c, modelId);
    state.kickCycle = Math.max(1, attiresFor(c).findIndex(a => a.model === modelId));
    renderPlate(side);
    showOnSide(side, c);
    assets.prefetch(modelId);
    if (hint) hint.textContent = `${c.name} — ${attireLabel(c, modelId)}`;
  }

  /* Owner's classic scheme (Tekken 1 manual): PUNCH = attire 1,
     KICK = attire 2. With more than two attires, repeated K taps
     keep cycling 2..n; P always returns to attire 1. */
  function punchAttire() {
    const c = state.highlight[state.activeSide];
    if (!c) return;
    const list = attiresFor(c);
    if (list.length < 2) return;
    audio.uiClick();
    applyAttire(state.activeSide, c, list[0].model); // applyAttire records index 0
  }
  function kickAttire() {
    const c = state.highlight[state.activeSide];
    if (!c) return;
    const list = attiresFor(c);
    if (list.length < 2) return;
    audio.uiClick();
    state.kickCycle = state.kickCycle >= list.length - 1 ? 1 : state.kickCycle + 1;
    applyAttire(state.activeSide, c, list[state.kickCycle].model);
  }

  /* ---------- picking ---------- */
  function highlight(c, opts = {}) {
    if (!c || state.phase === 'done') return;
    const side = state.activeSide;
    if (state.locked[side]) return;
    audio.uiClick();
    state.highlight[side] = c;
    // kickCycle tracks the CURRENT attire index; K advances it
    // (wrapping 2..n), P returns it to 0 (attire 1).
    state.kickCycle = Math.max(0, attiresFor(c).findIndex(a => a.model === selectedAttireModel(c)));
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
    showOnSide(side, c);
    assets.prefetch(c.model || 'pantera');
    if (confirmBtn) confirmBtn.disabled = false;
    const surgeName = c.surge ? c.surge.name : 'SOUL SURGE';
    if (hint) hint.textContent = `${c.name} — ${c.style} · ${surgeName}`;
    if (opts.scroll) {
      const el = cardFor(c.id);
      if (el) el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
    deps.onHighlight(c);
  }

  function selectById(id) {
    const c = deps.findChar(id);
    if (c) highlight(c, { scroll: true });
  }

  /* Called by main.js confirmSelection() BEFORE modes.onConfirm runs,
     with the id being confirmed. Mirrors the mode flow: versus locks
     P1 then hands the cursor to P2; team stacks picks on P1.
     T7 cue: the announcer SHOUTS the fighter's name on lock — ours
     fires the fighter's own select voice line (real owner audio where
     recorded, subtitle fallback otherwise) and the announcer name-shout
     subtitle; the proprietary announcer recording replaces the subtitle
     through the voice-clone pipeline (same placeholder policy as the
     fight announcer). */
  function announceLock(c) {
    if (!c) return;
    voice.play(c.id, 'select-01');
    voice.subtitle('ANNOUNCER', `${c.name}!`);
  }

  function notifyConfirm(confirmedId) {
    const c = deps.findChar(confirmedId);
    if (!c) return;
    announceLock(c);
    if (state.mode === 'versus') {
      if (!state.locked.p1) {
        state.locked.p1 = c;
        state.highlight.p1 = c;
        state.activeSide = 'p2';
        state.highlight.p2 = null;
        deps.onHighlight(null); // P2 must tap a card to pick
      } else {
        state.locked.p2 = c;
        state.highlight.p2 = c;
        state.phase = 'done';
      }
    } else if (state.mode === 'team') {
      state.teamPicks.push(confirmedId);
      state.highlight.p1 = c;
      if (state.teamPicks.length >= 3) {
        state.locked.p1 = c;
        state.phase = 'done';
      }
    } else {
      state.locked.p1 = c;
      state.highlight.p1 = c;
      state.phase = 'done';
    }
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
  }

  function onShow(mode) {
    const fresh = state.phase === 'done' || state.mode !== mode || !state._shown;
    if (fresh) {
      state.mode = mode;
      state.phase = 'pick';
      state.activeSide = 'p1';
      state.highlight = { p1: null, p2: null };
      state.locked = { p1: null, p2: null };
      state.teamPicks = [];
      state.kickCycle = 1;
      panes.p1.clear();
      panes.p2.clear();
      if (confirmBtn) confirmBtn.disabled = true;
      deps.onHighlight(null);
      // T7 cue: the announcer opens the screen — "Choose your fighter!"
      // (subtitle-only placeholder until the proprietary announcer voice
      // lands; owner law: no Tekken audio bytes in the repo).
      voice.announce('choose-your-fighter');
    }
    state._shown = true;
    applySkin($('screen-select'), getSkin(activeSkinId()));
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
  }

  /* T7 timeout behavior (called by main.js when the 99s timer hits 0):
     the active side's current highlight is LOCKED IN — a random fighter
     when nothing is highlighted — then the flow continues (versus hands
     the cursor to P2; the timer restarts for the next side). This is the
     real Tekken rule: the timer never leaves a side unpicked. */
  function timeoutPick() {
    if (state.phase === 'done') return;
    const side = state.activeSide;
    if (!state.highlight[side] && !state.locked[side]) {
      const pool = selectRoster().filter(c => c.id !== state.locked.p1?.id && c.id !== state.locked.p2?.id);
      const pick = pool[Math.floor(Math.random() * pool.length)];
      if (pick) highlight(pick, { scroll: true });
    }
    voice.subtitle('ANNOUNCER', 'TIME UP!');
    if (confirmBtn && !confirmBtn.disabled) confirmBtn.click();
  }

  /* ---------- keyboard (desktop parity; touch is primary) ----------
     T7 d-pad parity on the 2-row grid: arrows walk the grid in 2D
     (up/down toggle rows, left/right move columns within the tier),
     Enter highlights then confirms (via the real CONFIRM button so
     every mode hook still fires), J/K are punch/kick attire switching. */
  function navModel() {
    // Fighter cards only (dividers + the "?" card are not grid cells).
    return allCards()
      .filter(el => el.dataset.id !== '__random')
      .map(el => ({
        el,
        tier: el.dataset.tier,
        row: parseInt(el.dataset.row || '0', 10),
        col: parseInt(el.dataset.col || '0', 10),
      }));
  }
  function focusCard(el) {
    const cards = allCards();
    state.focusIdx = Math.max(0, cards.indexOf(el));
    cards.forEach(x => x.classList.remove('kb-focus'));
    el.classList.add('kb-focus');
    el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
  function moveFocus(dRow, dCol) {
    const cells = navModel();
    if (!cells.length) return;
    const cards = allCards();
    const rnd = cardFor('__random');
    const cur = cards[state.focusIdx];
    // The "?" card: any arrow steps back to the grid's last fighter card.
    if (cur && cur.dataset.id === '__random') {
      const last = cells[cells.length - 1];
      if (last) focusCard(last.el);
      return;
    }
    const here = cells.find(c => c.el === cur) || cells[0];
    const mates = cells.filter(c => c.tier === here.tier);
    const maxCol = Math.max(...mates.map(m => m.col));
    const nCol = Math.min(maxCol, Math.max(0, here.col + dCol));
    const nRow = dRow !== 0 ? 1 - here.row : here.row; // up/down toggles the row
    let target = mates.find(m => m.col === nCol && m.row === nRow)
      || mates.find(m => m.col === nCol)
      || here;
    // Right off the last column of the last tier lands on the "?" card.
    const lastTier = cells[cells.length - 1].tier;
    if (dCol > 0 && nCol === maxCol && here.col === maxCol && here.tier === lastTier && rnd) {
      focusCard(rnd);
      return;
    }
    focusCard(target.el);
  }
  document.addEventListener('keydown', (e) => {
    const sel = $('screen-select');
    if (!sel || !sel.classList.contains('active')) return;
    if (e.key === 'ArrowRight') { moveFocus(0, 1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft') { moveFocus(0, -1); e.preventDefault(); }
    else if (e.key === 'ArrowDown') { moveFocus(1, 0); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { moveFocus(-1, 0); e.preventDefault(); }
    else if (e.key === 'Enter' || e.key === ' ') {
      const cards = allCards();
      const card = cards[state.focusIdx];
      if (!card) return;
      if (card.dataset.id === '__random') { card.click(); e.preventDefault(); return; }
      const cur = state.highlight[state.activeSide];
      if (cur && cur.id === card.dataset.id) {
        if (confirmBtn && !confirmBtn.disabled) confirmBtn.click();
      } else {
        card.click();
      }
      e.preventDefault();
    } else if (e.key === 'j' || e.key === 'J') { punchAttire(); }
    else if (e.key === 'k' || e.key === 'K') { kickAttire(); }
  });

  const pBtn = $('attire-punch');
  const kBtn = $('attire-kick');
  if (pBtn) pBtn.addEventListener('click', punchAttire);
  if (kBtn) kBtn.addEventListener('click', kickAttire);

  // The Tripo/SmutBase lists arrive after the first build: rebuild once
  // so those fighters lead the grid in tier order.
  _tiersReady.then(() => { if (strip && strip.children.length) { build(); paintCards(); } });
  return { build, onShow, selectById, notifyConfirm, highlight, timeoutPick, _state: state, _panes: panes };
}
