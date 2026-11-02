/* ============================================================
   WESTERN HEART — Tekken-style character select (2026-10-20)
   Built from the teardown record, not a guessed layout:
   - Tekken 3 selector (teardown/tekken3/tools/tekken3recompiled):
     the real RE'd selector composites BACKDROP + LEFT_PLAYER +
     RIGHT_PLAYER + frames + ROSTER + CENTRE packets — a bisected
     P1/P2 zone over a roster field; portraits center-cropped 2:3;
     the selected aperture is LARGER than its neighbours
     (72x108 vs 56x84); the timer starts at 99; a pick is a
     two-step flow (choose fighter, then outfit) and the CPU card
     appears on the CPU's own side.
   - Tekken 1/6 (docs/select-redesign/SELECT-DESIGN.md §1):
     punch button = outfit 1, kick button = outfit 2 at select;
     "?" random slots sit at the ends of the portrait row.
   - Tekken 8 (same doc): live animated 3D models in the big
     zone (never a still), per-character costume slots chosen
     right on the select screen, bottom hints bar.
   Owner spec (2026-10-18 + 2026-10-19): top ~75-80% bisected
   zone, bottom ~20% card strip is the ONLY scrolling element
   and scrolls inside its own box, tap a card -> that fighter's
   animated model appears on YOUR side, name + style on cards,
   name + style + stats on the picked side, attire switching on
   the select screen, touch first.
   Previews reuse the existing model pipeline (assets.js
   loadModels/createInstance) — the same GLBs and Idle clips
   the fight itself uses. Stats shown are the game's real
   numbers: roster `stats` or the Fighter default
   (fighter.js: { speed: 2.8, jump: 7.2, power: 1.1,
   defense: 1.05 }, speed clamped to 3.5).
   ============================================================ */
import { selectVisible } from './core-set.js';
import * as THREE from 'three';
import { assets } from './assets.js';
import { loadGuardStance, createAimStance } from './stance-aim.js';
import { attiresFor, selectableAttires, selectedAttireModel, setAttire, attireLabel, attireEyeGlow } from './attires.js';
import { loadT3Clips, createT3Actions, retargetT3Clips, applyT7Stance } from './t3anims.js';
import { bankIdFor } from './fighter.js';
import { getMovesetInfo } from './movesets.js';
import { warmSelect, warmFight } from './preload.js';
import { NINE_SOULS, newSoulSpiritPick, vesselMatch, soulSpiritLabel } from './soul-spirit.js';
import { fighterPortraitSVG } from './fighter-portraits.js';
import { portraitSrcFor } from './user-portraits.js';

// Select-screen card for a fighter: a portrait the player took in the
// Creation Suite (POSE & PICTURE) is stored on-device keyed by fighter +
// attire and wins over the repo card; the repo card is the fallback.
// The attire is the fighter's currently selected one, so the card shows
// the attire the player actually posed.
function selectPortraitSrc(c) {
  const list = selectableAttires(c);
  const idx = Math.max(0, list.findIndex(a => a.model === selectedAttireModel(c)));
  return portraitSrcFor(c.id, 'attire' + (idx + 1), `assets/portraits/${c.id}.png`);
}



const DEFAULT_STATS = { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 };
const clamp01 = (v) => Math.max(0, Math.min(1, v));

export function statsFor(c) {
  const s = { ...DEFAULT_STATS, ...(c && c.stats ? c.stats : {}) };
  if (s.speed > 3.5) s.speed = 3.5; // same clamp the Fighter applies
  return s;
}

/* ---------------- one side's live 3D preview pane ---------------- */
export class PreviewPane {
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
    // Landscape (owner: bigger fighters): the pane now runs full height
    // behind the roster band (select-t7.css) and the body is framed to
    // ~88% of it, head near the top and legs behind the cards, the way
    // T7's select renders stand. Height rules here (wide pane).
    if (innerWidth > innerHeight) {
      const d2 = THREE.MathUtils.clamp(Math.max((h * 0.57) / tanH, (w * 0.57) / (tanH * aspect)), 2.2, 11);
      this.camera.position.set(0, cy + 0.12 * s, d2);
      this.camera.lookAt(0, cy, 0);
    }
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
        c.colorize ? (c.tintStrength ?? 0.3) : 0, // TINT FIX: own textures, no palette wash (real colors)
        attireEyeGlow(c, modelId)); // per-attire emissive eyes (owner 2026-10-22)
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
          const rc = retargetT3Clips(clips, bank, inst.model, THREE, modelId) || {};
          applyT7Stance(c.id, bank, rc, inst.model, THREE, modelId); // real T7 stance where baked, same as the fight
          const t3 = createT3Actions(inst.mixer, rc, THREE);
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
      // NO-T-POSE backup (Tekken bank first, CMU mocap backup): when the
      // bank stance is missing or failed the fit gates, drive the rig with
      // the bind-independent CMU 14_01 guard (stance-aim.js).
      if (!this.hasStance && inst.bones) {
        try {
          const g = await loadGuardStance();
          if (token !== this._token) return true;
          const aim = createAimStance(THREE, this.model, inst.bones, g);
          if (aim) {
            if (inst.actions && inst.actions.Idle) inst.actions.Idle.setEffectiveWeight(0);
            this.aim = aim; this._aimT = 0; this.hasStance = true; this.stanceSource = 'cmu-14_01';
          }
        } catch (e) { console.warn('[WH] select preview: CMU guard unavailable for', c.id, e.message || e); }
      } else if (this.hasStance) this.stanceSource = 'tekken-bank';
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
    this.aim = null;
    this.stanceSource = null;
  }

  clear() { this._token++; this._clearModel(); }

  update(dt) {
    if (!this.renderer || !this.scene || !this.camera) return;
    if (this.mixer) this.mixer.update(dt);
    if (this.aim) { this._aimT += dt; this.aim.apply(this._aimT); }
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
  window.__whSelectPanes = panes; // proof-script hook (camera framing checks)
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

  const LAST_KEY = 'wh.select.last.v1';
  const state = {
    mode: null,
    phase: 'pick',        // 'pick' | 'done'
    activeSide: 'p1',     // whose cursor is live
    highlight: { p1: null, p2: null },  // roster entry previewed per side
    locked: { p1: null, p2: null },     // confirmed entries
    teamPicks: [],        // team mode: confirmed ids (all on p1)
    kickCycle: 1,         // K button attire cycling position
    focusIdx: 0,
    /* SOUL-SPIRIT TOGGLE (owner directive 2026-10-22 ~23:02 CDT): tertiary
       per-side pick, NOT an attire — { enabled, soulId }. Snapshotted into
       spiritLocked at confirm time so the fight reads the locked pick. */
    spirit: { p1: newSoulSpiritPick(), p2: newSoulSpiritPick() },
    spiritLocked: { p1: null, p2: null },
    // TTT2 TEAM BATTLE (worker 24): the versus submenu lives INSIDE the
    // select screen — 1V1 FIGHT or TEAM BATTLE (2-8 per team), then a
    // character per slot. TTT2 actual: solo/tag choice BEFORE any pick.
    vsMode: null,        // 'solo' | 'team' (versus only; null = not chosen)
    teamSize: 2,         // fighters per team (2 = TTT2 tag rules)
    draft: { p1: [], p2: [] },
    draftSide: 'p1',
    vsTeamsDone: null,   // { p1:[ids], p2:[ids], size } when draft completes
  };

  /* ---------- card strip ---------- */
  function portraitHTML(c) {
    // Portrait files are the personality pass's drop-in point: the same
    // assets/portraits/<id>.png path the old grid used. A fighter with
    // no portrait PNG yet gets the deterministic procedural portrait
    // (game/js/fighter-portraits.js — ported from the owner's own
    // AshLane generator; same id always yields the same face), layered
    // under the img so a real portrait always wins. The monogram plate
    // stays as the last-resort fallback — never another fighter's face
    // (the old repeated-placeholder bug).
    const svgFallback = fighterPortraitSVG(c.id, c.name, c.faction);
    return `<div class="portrait"><span class="svg-fallback" aria-hidden="true">${svgFallback}</span><img src="${selectPortraitSrc(c)}" alt="${c.name}" loading="lazy"
      onerror="this.parentElement.classList.add('no-portrait');this.remove();">
      <span class="mono">${(c.name || '?').slice(0, 2)}</span></div>
      <div class="cname">${c.name}</div><div class="cstyle">${c.style}</div>`;
  }

  /* Owner law (2026-10-22): NO duplicate fighters on select. Entries that
     share another fighter's model are hidden until they get their own
     models — they stay in the roster data for story/other modes, but never
     as separate select cards. Attire variants live in the attire ladder
     (renderAttires), not as duplicate cards.
     NINE SOULS REDESIGN (owner directive 2026-10-22 ~23:02 CDT, refined
     ~23:03 CDT): the seven VESSELED souls (rin, byou, tou, sha, kai,
     jin_soul, retsu) come OFF the grid as standalone cards — they have no
     bodies of their own yet. Only ZEN and GYOU (unvesseled) stay
     selectable as spirit fighters. The seven stay in the roster data for
     story/other modes; per the refinement they return LATER as
     unlockable boss-type characters with vessels/bodies once story modes
     progress — the unlock path is future design, not this change. Their
     presence on a fighter is the soul-spirit toggle (js/soul-spirit.js),
     not a select card. */
  const SELECT_HIDDEN = new Set([
    'rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu', 'zen', 'gyou',
    'ryuji', 'doc-frank-machine-shop',

  ]);
  // Milestone 1 (2026-10-29) showed the core 8 by default; the owner
  // reversed that the same day — all fighters are back on select
  // (game/js/core-set.js). Only SELECT_HIDDEN above still filters.
  const selectRoster = () => deps.roster().filter(c => !SELECT_HIDDEN.has(c.id) && selectVisible(c.id));

  function build() {
    if (!strip) return;
    strip.innerHTML = '';
    const roster = selectRoster();
    // T8 grid (teardown/tekken8/ui/CHARACTER-SELECT.md): ONE compact
    // face-card grid, no tier rows, no names on cards; owner's Tripo
    // fighters still lead (registry order from data/tripo-fighters.json).
    const tripo = TRIPO_IDS || new Set();
    const ordered = [...roster.filter(c => tripo.has(c.id)), ...roster.filter(c => !tripo.has(c.id))];
    const cards = ordered.map((c) => {
      const card = document.createElement('div');
      card.className = 'char-card';
      card.dataset.id = c.id;
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', c.name);
      card.innerHTML = portraitHTML(c);
      card.addEventListener('click', () => highlight(c, { fromTap: true }));
      return card;
    });
    // T8: the "?" random card sits inside the grid flow (centre of the last row).
    const rnd = document.createElement('div');
    rnd.className = 'char-card random-card';
    rnd.dataset.id = '__random';
    rnd.setAttribute('role', 'button');
    rnd.setAttribute('aria-label', 'Random');
    rnd.innerHTML = `<div class="portrait"><span class="qmark">?</span></div>
      <div class="cname">RANDOM</div><div class="cstyle">Fate decides</div>`;
    rnd.addEventListener('click', () => {
      const drafted = [...state.draft.p1, ...state.draft.p2];
      const pool = selectRoster().filter(c => c.id !== state.locked.p1?.id && c.id !== state.locked.p2?.id &&
        !drafted.includes(c.id));
      const pick = pool[Math.floor(Math.random() * pool.length)];
      if (pick) highlight(pick, { fromTap: true, scroll: true });
    });
    cards.splice(Math.max(0, cards.length - 4), 0, rnd);
    cards.forEach(el => strip.appendChild(el));
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
      el.classList.toggle('in-draft-p1', state.draft.p1.includes(id));
      el.classList.toggle('in-draft-p2', state.draft.p2.includes(id));
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
{ const f = els.root.querySelector('.pane-facts'); if (f) f.innerHTML = ''; }
renderSoulSpirit(side, null, false);

      els.note.hidden = true;
      return;
    }
    els.name.textContent = c.name || '—';
    { const aw = els.root.querySelector('.pane-artwash img'); if (aw) aw.src = selectPortraitSrc(c); }
    els.title.textContent = c.title || '';
    const modelId = selectedAttireModel(c);
    els.style.textContent = [c.style, c.archetype, attireLabel(c, modelId)]
      .filter(Boolean).join(' · ');
    // T8 fact block: FIGHTING STYLE / NATIONALITY / HEIGHT / WEIGHT. Values
    // come from roster data only; T8 itself prints "Unknown" for unset ones.
    const facts = els.root.querySelector('.pane-facts');
    if (facts) {
      const fact = (lab, v) => `<div class="fact"><span class="fact-lab">${lab}</span><span class="fact-val">${v || 'Unknown'}</span></div>`;
      facts.innerHTML = fact('Fighting Style', c.style) + fact('Nationality', c.nationality || c.origin)
        + fact('Height', c.height) + fact('Weight', c.weight);
    }
    const s = statsFor(c);
    els.stats.innerHTML =
      statRow('POW', s.power, (s.power - 0.5) / 1.5, v => v.toFixed(2)) +
      statRow('SPD', s.speed, s.speed / 3.5, v => v.toFixed(1)) +
      statRow('JMP', s.jump, s.jump / 10, v => v.toFixed(1)) +
      statRow('DEF', s.defense, (s.defense - 0.5) / 1.5, v => v.toFixed(2));
    renderAttires(side, c, !locked && isActive);
    renderSoulSpirit(side, c, !locked && isActive);
  }

  function renderAttires(side, c, interactive) {
    const els = plateEls(side);
    const list = selectableAttires(c); // pending (not yet playable) slots stay hidden
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

  /* ---------- soul-spirit toggle (tertiary, NOT an attire) ----------
     Owner directive 2026-10-22 ~23:02 CDT: every fighter gets an on/off
     switch for a soul spirit floating behind them + a 9-soul picker.
     Picking the soul that vessels into the highlighted fighter empowers
     them (the buff is applied at fight start; see js/soul-spirit.js). */
  function spiritPanelEl(side) {
    const els = plateEls(side);
    let panel = els.root.querySelector('.soul-spirit-panel');
    if (!panel) {
      panel = document.createElement('div');
      panel.className = 'soul-spirit-panel';
      const plate = els.root.querySelector('.pane-plate');
      const attires = els.root.querySelector('.pane-attires');
      if (plate && attires && attires.nextSibling) plate.insertBefore(panel, attires.nextSibling);
      else if (plate) plate.appendChild(panel);
    }
    return panel;
  }

  function renderSoulSpirit(side, c, interactive) {
    const panel = spiritPanelEl(side);
    const pick = state.spirit[side];
    panel.innerHTML = '';
    if (!c) return;
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'spirit-toggle' + (pick.enabled ? ' on' : '');
    toggle.textContent = soulSpiritLabel(pick);
    toggle.disabled = !interactive;
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!interactive) return;
      audio.uiClick();
      pick.enabled = !pick.enabled;
      if (pick.enabled && !pick.soulId) pick.soulId = 'rin';
      renderPlate('p1'); renderPlate('p2');
      if (hint) hint.textContent = pick.enabled
        ? `${c.name} — soul spirit ${soulByIdName(pick.soulId)} behind them`
        : `${c.name} — soul spirit off`;
    });
    panel.appendChild(toggle);
    if (pick.enabled) {
      const row = document.createElement('div');
      row.className = 'spirit-souls';
      NINE_SOULS.forEach((s) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        const isVessel = vesselMatch(c.id, s.id);
        chip.className = 'spirit-soul' + (pick.soulId === s.id ? ' on' : '') + (isVessel ? ' vessel' : '');
        chip.textContent = `${s.name} ${s.kanji}`;
        chip.title = s.nature + (isVessel ? ' — VESSEL MATCH: empowers ' + c.name : '');
        chip.disabled = !interactive;
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          if (!interactive) return;
          audio.uiClick();
          pick.soulId = s.id;
          renderPlate('p1'); renderPlate('p2');
          if (hint) hint.textContent = isVessel
            ? `${s.name} vessels into ${c.name} — EMPOWERED`
            : `${c.name} — ${s.name} spirit (no vessel bond)`;
        });
        row.appendChild(chip);
      });
      panel.appendChild(row);
      if (vesselMatch(c.id, pick.soulId)) {
        const badge = document.createElement('div');
        badge.className = 'spirit-empowered';
        badge.textContent = '⬢ VESSEL MATCH — EMPOWERED';
        panel.appendChild(badge);
      }
    }
  }

  function soulByIdName(id) {
    const s = NINE_SOULS.find((x) => x.id === id);
    return s ? `${s.name} ${s.kanji}` : '';
  }

  /* ---------- preview + attire application ---------- */
  async function showOnSide(side, c) {
    const modelId = selectedAttireModel(c);
    const els = plateEls(side);
    const fb = els.root.querySelector('.pane-fallback');
    els.note.hidden = true;
    // PRELOAD (2026-10-24): the portrait plate shows instantly while the
    // GLB streams in, then hides only when the 3D model is ready — the
    // preview is never a blank wait. (Fallback handling below already
    // hides it on success and keeps it on failure.)
    if (fb) { fb.src = selectPortraitSrc(c); fb.hidden = false; }
    const ok = await panes[side].show(c, modelId);
    if (state.highlight[side]?.id !== c.id && state.locked[side]?.id !== c.id) return;
    if (panes[side].failed) {
      // No WebGL on this device: show the posed portrait plate
      // instead of the live model, and say so honestly.
if (fb) {
        fb.onerror = () => { fb.onerror = null; fb.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(fighterPortraitSVG(c.id, c.name, c.faction, 256)); };
        fb.src = selectPortraitSrc(c); fb.hidden = false;
      }
      els.note.hidden = false;
      els.note.textContent = '3D UNAVAILABLE';

      return;
    }
    // A model that fails to load shows the fighter's own portrait plate,
    // never a message, a T-pose or another fighter.
    if (fb) { if (!ok) fb.src = selectPortraitSrc(c); fb.hidden = !!ok; }
    els.note.hidden = true;
  }

  function applyAttire(side, c, modelId) {
    setAttire(c, modelId);
    state.kickCycle = Math.max(1, selectableAttires(c).findIndex(a => a.model === modelId));
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
    const list = selectableAttires(c);
    if (list.length < 2) return;
    audio.uiClick();
    applyAttire(state.activeSide, c, list[0].model); // applyAttire records index 0
  }
  function kickAttire() {
    const c = state.highlight[state.activeSide];
    if (!c) return;
    const list = selectableAttires(c);
    if (list.length < 2) return;
    audio.uiClick();
    state.kickCycle = state.kickCycle >= list.length - 1 ? 1 : state.kickCycle + 1;
    applyAttire(state.activeSide, c, list[state.kickCycle].model);
  }

  /* ---------- picking ---------- */
  function highlight(c, opts = {}) {
    if (!c || state.phase === 'done') return;
    if (state.mode === 'versus' && !state.vsMode) {
      // TTT2: no fighter can be previewed before the format is chosen.
      if (hint) hint.textContent = 'VERSUS — choose 1V1 FIGHT or TEAM BATTLE first.';
      return;
    }
    // TTT2 draft: during the slot draft, highlight previews on the
    // side currently drafting (p1 = your team, p2 = rival team).
    const draftMode = state.mode === 'versus' && state.vsMode === 'team' && !state.vsTeamsDone;
    const side = draftMode ? state.draftSide : state.activeSide;
    if (state.locked[side]) return;
    audio.uiClick();
    state.highlight[side] = c;
    // kickCycle tracks the CURRENT attire index; K advances it
    // (wrapping 2..n), P returns it to 0 (attire 1).
    state.kickCycle = Math.max(0, selectableAttires(c).findIndex(a => a.model === selectedAttireModel(c)));
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
    showOnSide(side, c);
    if (c.model) assets.prefetch(c.model);
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
     P1 then hands the cursor to P2; team stacks picks on P1. */
  /* Soul-spirit picks are snapshotted at confirm time: the fight reads
     spiritLocked, so later select-screen resets can't change a locked pick. */
  function lockSpirit(side) {
    state.spiritLocked[side] = { ...state.spirit[side] };
  }

  function notifyConfirm(confirmedId) {
    const c = deps.findChar(confirmedId);
    if (!c) return;
    try {
      const side = state.mode === 'versus' && state.locked.p1 ? 'p2' : 'p1';
      const last = JSON.parse(localStorage.getItem(LAST_KEY) || '{}');
      last[side] = c.id; localStorage.setItem(LAST_KEY, JSON.stringify(last));
    } catch (_) {}
    // TTT2 draft: during a team-battle draft, CONFIRM fills the next
    // team slot (your team first, then the rival team) instead of the
    // classic P1-then-P2 lock flow.
    if (state.mode === 'versus' && state.vsMode === 'team') {
      draftConfirm(c);
      return;
    }    if (state.mode === 'versus') {
      if (!state.locked.p1) {
        state.locked.p1 = c;
        lockSpirit('p1');
        state.highlight.p1 = c;
        state.activeSide = 'p2';
        state.highlight.p2 = null;
        deps.onHighlight(null); // P2 must tap a card to pick
      } else {
        state.locked.p2 = c;
        lockSpirit('p2');
        state.highlight.p2 = c;
        state.phase = 'done';
      }
    } else if (state.mode === 'team') {
      state.teamPicks.push(confirmedId);
      state.highlight.p1 = c;
      if (state.teamPicks.length >= 3) {
        state.locked.p1 = c;
        lockSpirit('p1');
        state.phase = 'done';
      }
    } else {
      state.locked.p1 = c;
      lockSpirit('p1');
      state.highlight.p1 = c;
      state.phase = 'done';
    }
    // PRELOAD (2026-10-24): locked fighters' GLBs warm while the player
    // is on stage select, so FIGHT does not start cold. (Highlight
    // prefetch already warmed P1; this also warms P2 / team picks.)
    try {
      const lockedModels = [state.locked.p1, state.locked.p2].filter(Boolean).map(c => selectedAttireModel(c));
      if (lockedModels.length) warmFight(lockedModels, (id) => assets.prefetch(id));
    } catch (_) {}
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
      state.spirit = { p1: newSoulSpiritPick(), p2: newSoulSpiritPick() };
      state.spiritLocked = { p1: null, p2: null };
      state.kickCycle = 1;
      // TTT2: versus always starts at the format submenu — nothing is
      // pre-picked; the draft state resets for a fresh team battle.
      state.vsMode = null;
      state.teamSize = 2;
      state.draft = { p1: [], p2: [] };
      state.draftSide = 'p1';
      state.vsTeamsDone = null;
      panes.p1.clear();
      panes.p2.clear();
      if (confirmBtn) confirmBtn.disabled = true;
      deps.onHighlight(null);
    }
    // TTT2: the 1V1 / TEAM BATTLE submenu lives INSIDE the select
    // screen for versus (not a separate menu). It hides for other modes.
    if (state.mode === 'versus' && !state.vsMode && state.phase !== 'done') {
      showVsSubmenu();
      if (fresh && hint) hint.textContent = 'VERSUS — choose 1V1 FIGHT or TEAM BATTLE.';
    } else {
      hideVsSubmenu();
    }
    state._shown = true;
    if (fresh) {
      // T7: the P1 cursor starts on the fighter you last confirmed
      // (attire is remembered per fighter by attires.js).
      try {
        const last = JSON.parse(localStorage.getItem(LAST_KEY) || '{}');
        const c = last.p1 && deps.findChar(last.p1);
        if (c && cardFor(c.id)) highlight(c, { scroll: true });
        // No saved pick: T7 parks the P1 cursor on the first slot
        // (Pantera, attire 1 = the owner's own Leo man model).
        else {
          const first = allCards().find(x => x.dataset.id && x.dataset.id !== '__random');
          const fc = first && deps.findChar(first.dataset.id);
          if (fc) highlight(fc, { scroll: true });
        }
      } catch (_) {}
    }
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
    // PRELOAD (2026-10-24): every select card image warms in the
    // background once the screen has painted — tapping any fighter
    // then shows its card from cache instead of a lazy fetch. GLBs
    // are NOT bulk-warmed here (that was the old preloadAll pipe
    // saturation); models warm per highlight + per lock.
    try { warmSelect(selectRoster().map(c => c.id)); } catch (_) {}
  }

  /* ---------- keyboard (desktop parity; touch is primary) ----------
     Arrows walk the strip, Enter highlights then confirms (via the
     real CONFIRM button so every mode hook still fires), J/K are
     punch/kick attire switching. */
  document.addEventListener('keydown', (e) => {
    const sel = $('screen-select');
    if (!sel || !sel.classList.contains('active')) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      const cards = allCards();
      if (!cards.length) return;
      state.focusIdx = (state.focusIdx + (e.key === 'ArrowRight' ? 1 : -1) + cards.length) % cards.length;
      cards.forEach(x => x.classList.remove('kb-focus'));
      const el = cards[state.focusIdx];
      el.classList.add('kb-focus');
      el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      e.preventDefault();
    } else if (e.key === 'Enter' || e.key === ' ') {
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

  /* The fight (main.js startFight) reads each side's locked soul-spirit
     pick here — null when that side picked nothing / toggle off. */
  function soulSpiritLocked(side) {
    const p = state.spiritLocked[side];
    return p ? { ...p } : null;
  }

  // The Tripo list arrives after the first build: rebuild once so those fighters lead the grid.
  _tripoReady.then(() => { if (strip && strip.children.length) { build(); paintCards(); } });
  /* Stage-show hook (main.js): warm the locked fighters' GLBs during
     stage-select dwell. Returns the locked state (empty when nothing
     is locked, so calling it early is a safe no-op). */
  function warmLockedFighters() {
    try {
      const ids = [state.locked.p1, state.locked.p2].filter(Boolean).map(c => selectedAttireModel(c));
      if (ids.length) warmFight(ids, (id) => assets.prefetch(id));
    } catch (_) {}
    return state.locked;
  }

  return { build, onShow, selectById, notifyConfirm, highlight, warmLockedFighters, soulSpiritLocked, _state: state, _panes: panes };

  /* ---------- TTT2 versus submenu (INSIDE the select screen) ----------
     TTT2 actual: "before you select your characters, you will choose
     whether to play as a single character or a two-person tag team."
     1V1 FIGHT -> the classic versus flow. TEAM BATTLE -> team-size
     picker (2 = TTT2 tag rules; 3-8 = TTT2 Team Battle elimination),
     then a character per slot: your team, then the rival team. */
  function vsSubmenu() {
    let el = $('vs-submenu');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'vs-submenu';
    el.className = 'vs-submenu';
    el.innerHTML = `
      <div class="vs-submenu-title">VERSUS — CHOOSE BATTLE FORMAT</div>
      <div class="vs-submenu-row" id="vs-format-row">
        <button type="button" class="vs-format-btn" data-format="solo">
          <b>1V1 FIGHT</b><span>classic versus</span>
        </button>
        <button type="button" class="vs-format-btn" data-format="team">
          <b>TEAM BATTLE</b><span>TTT2 tag &amp; elimination</span>
        </button>
      </div>
      <div class="vs-submenu-row" id="vs-size-row" hidden>
        <div class="vs-size-label">FIGHTERS PER TEAM</div>
        <div class="vs-size-btns" id="vs-size-btns"></div>
        <div class="vs-size-note" id="vs-size-note"></div>
      </div>
      <div class="vs-submenu-row" id="vs-slot-tray" hidden></div>`;
    const grid2 = $('select-grid') || strip; // strip = $('char-grid'); 'grid' was undefined (ReferenceError) so the submenu never got created
    (grid2.parentElement || document.body).appendChild(el);
    el.querySelectorAll('.vs-format-btn').forEach((b) =>
      b.addEventListener('click', () => chooseVsFormat(b.dataset.format)));
    const sizeBtns = el.querySelector('#vs-size-btns');
    for (let n = 2; n <= 8; n++) {
      const sb = document.createElement('button');
      sb.type = 'button';
      sb.className = 'vs-size-btn' + (n === 2 ? ' on' : '');
      sb.dataset.n = String(n);
      sb.innerHTML = `<b>${n}</b><span>${n === 2 ? 'TAG' : n <= 4 ? 'ELIM' : 'WAR'}</span>`;
      sb.addEventListener('click', () => chooseTeamSize(n));
      sizeBtns.appendChild(sb);
    }
    setSizeNote(2);
    return el;
  }
  function setSizeNote(n) {
    const note = $('vs-size-note');
    if (note) note.textContent = n === 2
      ? '2v2 — TTT2 tag rules: tag in/out, red health, rage, tag combos.'
      : `${n}v${n} — TTT2 Team Battle elimination: KO a fighter, the next steps in.`;
  }
  function chooseVsFormat(fmt) {
    audio.uiClick();
    if (fmt === 'solo') {
      state.vsMode = 'solo';
      hideVsSubmenu();
      if (hint) hint.textContent = '1V1 FIGHT — pick your fighter, then the rival.';
    } else {
      state.vsMode = 'team';
      const el = vsSubmenu();
      el.querySelector('#vs-format-row').hidden = true;
      const sizeRow = el.querySelector('#vs-size-row');
      sizeRow.hidden = false;
      el.querySelector('#vs-slot-tray').hidden = true;
      setSizeNote(2);
      if (hint) hint.textContent = 'TEAM BATTLE — how many fighters per team?';
    }
    paintCards();
  }
  function chooseTeamSize(n) {
    audio.uiClick();
    state.teamSize = n;
    state.draft = { p1: [], p2: [] };
    state.draftSide = 'p1';
    state.activeSide = 'p1';
    setSizeNote(n);
    const el = vsSubmenu();
    el.querySelector('#vs-size-row').hidden = true;
    el.querySelector('#vs-format-row').hidden = true;
    const tray = el.querySelector('#vs-slot-tray');
    tray.hidden = false;
    el.querySelectorAll('.vs-size-btn').forEach((b) =>
      b.classList.toggle('on', Number(b.dataset.n) === n));
    renderVsTray();
    deps.onHighlight(null);
    if (confirmBtn) confirmBtn.disabled = true;
    if (hint) hint.textContent = `YOUR TEAM — pick fighter 1 of ${n}.`;
    paintCards();
  }
  function renderVsTray() {
    const tray = $('vs-slot-tray');
    if (!tray) return;
    tray.innerHTML = '';
    for (const side of ['p1', 'p2']) {
      const head = document.createElement('div');
      head.className = 'vs-tray-head';
      head.textContent = side === 'p1' ? 'YOUR TEAM' : 'RIVAL TEAM';
      tray.appendChild(head);
      const row = document.createElement('div');
      row.className = 'vs-tray-row';
      for (let i = 0; i < state.teamSize; i++) {
        const id = state.draft[side][i];
        const slot = document.createElement('div');
        slot.className = 'vs-slot' + (id ? ' filled' : '') +
          (side === state.draftSide && i === state.draft[side].length ? ' next' : '');
        const c = id ? deps.findChar(id) : null;
        slot.innerHTML = `<span class="vs-slot-n">${i + 1}</span><span class="vs-slot-name">${c ? c.name : '—'}</span>`;
        row.appendChild(slot);
      }
      tray.appendChild(row);
    }
  }
  function draftConfirm(c) {
    const side = state.draftSide;
    const arr = state.draft[side];
    if (arr.length >= state.teamSize) return;
    arr.push(c.id);
    audio.uiConfirm();
    renderVsTray();
    paintCards();
    if (arr.length >= state.teamSize) {
      if (side === 'p1') {
        state.draftSide = 'p2';
        state.activeSide = 'p2';
        if (hint) hint.textContent = `RIVAL TEAM — pick fighter 1 of ${state.teamSize}.`;
        deps.onHighlight(null);
        if (confirmBtn) confirmBtn.disabled = true;
      } else {
        state.vsTeamsDone = { p1: [...state.draft.p1], p2: [...state.draft.p2], size: state.teamSize };
        state.phase = 'done';
        hideVsSubmenu();
        if (hint) hint.textContent = 'TEAMS LOCKED — get ready.';
      }
    } else if (hint) {
      hint.textContent = `${side === 'p1' ? 'YOUR TEAM' : 'RIVAL TEAM'} — pick fighter ${arr.length + 1} of ${state.teamSize}.`;
    }
  }
  function hideVsSubmenu() {
    const el = $('vs-submenu');
    if (el) el.hidden = true;
  }
  function showVsSubmenu() {
    const el = vsSubmenu();
    el.hidden = false;
    el.querySelector('#vs-format-row').hidden = false;
    el.querySelector('#vs-size-row').hidden = true;
    el.querySelector('#vs-slot-tray').hidden = true;
  }

  return { build, onShow, selectById, notifyConfirm, highlight, _state: state, _panes: panes };}
