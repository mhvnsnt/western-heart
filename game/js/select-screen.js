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
import * as THREE from 'three';
import { assets } from './assets.js';
import { loadGuardStance, createAimStance } from './stance-aim.js';
import { attiresFor, selectedAttireModel, setAttire, attireLabel } from './attires.js';
import { loadT3Clips, createT3Actions, retargetT3Clips } from './t3anims.js';
import { bankIdFor } from './fighter.js';
import { getMovesetInfo } from './movesets.js';
import { assignSelectPoses, poseBankFor, bankAimData, cmuVariant } from './select-poses.js';

/* Select pose map (select-poses.js): id -> unique pose. Built over the
   visible roster by the controller / portrait capture. LOCKED poses are
   the owner's references (t199u steering): Pantera's bank stance and
   Buffalo Bill's plain CMU guard stay exactly as approved. */
export const LOCKED_POSES = { pantera: 'tekken-bank:stance', 'buffalo-bill': 'cmu#0' };
let _poseMap = new Map();
export function setSelectRoster(fighters) {
  const locked = fighters.filter(c => c.id === 'buffalo-bill');
  const rest = fighters.filter(c => c.id !== 'buffalo-bill');
  _poseMap = assignSelectPoses([...locked, ...rest], (c) => (c.id === 'buffalo-bill' ? null : poseBankFor(c, bankIdFor, getMovesetInfo)));
  for (const [id, p] of Object.entries(_overrides)) _poseMap.set(id, p);
  return _poseMap;
}
export function selectPoseMap() { return _poseMap; }
/* Per-fighter pose picks validated against the Pantera card framing by
   tools/portraits/capture_poses.mjs (data/select-poses.json). Applied over
   the deterministic assignment so select, hero render and card portrait
   always show the same pose. */
let _overrides = {};
export function setPoseOverrides(o) { _overrides = o || {}; for (const [id, p] of Object.entries(_overrides)) _poseMap.set(id, p); }
export function setPose(id, p) { _poseMap.set(id, p); }
export const poseOverridesReady = fetch('data/select-poses.json').then(r => (r.ok ? r.json() : null))
  .then(j => { if (j && j.poses) setPoseOverrides(j.poses); }).catch(() => {});

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
        c.colorize ? (c.tintStrength ?? 0.3) : 0); // TINT FIX: own textures, no palette wash (real colors)
      // NO RIG = NO T-POSE (t214u): a model with no skinned mesh can only
      // stand in its bind pose. Show the fighter's posed portrait plate in
      // the hero pane instead until the re-rig lane rigs it.
      let skinned = false;
      inst.model.traverse((o) => { if (o.isSkinnedMesh) skinned = true; });
      if (!skinned) {
        this._clearModel();
        console.warn('[WH] select preview: no rig for', modelId, '- showing portrait plate');
        return false;
      }
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
      // QA/CI hooks: which model, bank and pose clip this pane shows.
      this.modelId = modelId; this.fighterId = c.id; this.inst = inst;
      this.bank = null; this.poseKey = null;
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
      const pose = _poseMap.get(c.id) || null;
      this.pose = pose;
      if (!pose || pose.clip === 'stance') try {
        // The fighter's OWN moveset file decides its bank (its base's motion), same as in the fight.
        const bank = bankIdFor(c.id, getMovesetInfo(c.id) ? c.id : (c.moveset || c.id));
        this.bank = bank || null;
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
      // UNIQUE SELECT POSE (select-poses.js): the fighter's assigned clip
      // from its own source bank, aim-retargeted (bind-independent), or —
      // with no decoded source bank — its own CMU window. Also the NO-T-POSE
      // backup when the bank stance failed the fit gates above.
      if (!this.hasStance && inst.bones) {
        try {
          let data = null, src = null;
          if (pose && pose.bank) {
            data = await bankAimData(THREE, pose.bank, pose.file || 't3_neutral.json');
            src = data ? `tekken-aim:${pose.bank}/${pose.clip}` : null;
          }
          if (!data) {
            const g = await loadGuardStance();
            const cm = (pose && pose.cmu) || { mirror: false, phase: 0 };
            data = g && cmuVariant(g, cm); src = `cmu-14_01${pose && pose.clip !== 'cmu#0' ? ':' + (pose.clip || '') : ''}`;
          }
          if (token !== this._token) return true;
          const aim = data && createAimStance(THREE, this.model, inst.bones, data);
          if (aim) {
            if (inst.actions && inst.actions.Idle) inst.actions.Idle.setEffectiveWeight(0);
            this.aim = aim; this._aimT = (data.phase || 0); this.hasStance = true; this.stanceSource = src;
            this.poseKey = pose ? (pose.bank ? `${pose.bank}/${pose.clip}` : pose.clip) : 'cmu#0';
          }
        } catch (e) { console.warn('[WH] select preview: pose unavailable for', c.id, e.message || e); }
      } else if (this.hasStance) { this.stanceSource = 'tekken-bank'; this.poseKey = `${this.bank}/stance`; }
      // POSED FRAMING (select audit 2026-10-23): bind bounds understate a
      // posed body (bank clips shift the head/hips) and cut heads off.
      // Re-fit the camera to the SKINNED, posed vertices once.
      if (this.hasStance && token === this._token) this._refitPosed();
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

  _refitPosed() {
    try {
      if (this.aim) this.aim.apply(this._aimT || 0);
      if (this.mixer) this.mixer.update(0);
      this.model.updateMatrixWorld(true);
      const bb = new THREE.Box3(), v = new THREE.Vector3();
      this.model.traverse((o) => {
        if (!o.isSkinnedMesh || !o.geometry.attributes.position) return;
        const n = o.geometry.attributes.position.count, step = Math.max(1, Math.floor(n / 3000));
        for (let i = 0; i < n; i += step) { o.getVertexPosition(i, v); bb.expandByPoint(v.applyMatrix4(o.matrixWorld)); }
      });
      if (bb.isEmpty()) return;
      const sz = bb.getSize(new THREE.Vector3());
      if (sz.y < 0.1) return;
      // the model turns: width rules by the larger horizontal extent
      this._fitW = Math.max(sz.x, sz.z) * 1.06; this._fitH = sz.y * 1.08; this._fitCY = bb.min.y + sz.y / 2;
      this._frame();
    } catch (e) { console.warn('[WH] select preview: posed refit failed', e.message || e); }
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
export const SELECT_HIDDEN = new Set([
    'rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu', 'zen', 'gyou',
    'doc-frank-machine-shop', // ryuji restored on main (#947)
  ]);

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
  };

  /* ---------- card strip ---------- */
  function portraitHTML(c) {
    // Portrait files are the personality pass's drop-in point: the same
    // assets/portraits/<id>.png path the old grid used. A fighter with
    // no portrait yet gets a monogram plate — never another fighter's
    // face (the old repeated-placeholder bug).
    return `<div class="portrait"><img src="assets/portraits/${c.id}.png" alt="${c.name}" loading="lazy"
      onerror="this.parentElement.classList.add('no-portrait');this.remove();">
      <span class="mono">${(c.name || '?').slice(0, 2)}</span></div>
      <div class="cname">${c.name}</div><div class="cstyle">${c.style}</div>`;
  }

  /* Owner law (2026-10-22): NO duplicate fighters on select. Entries that
     share another fighter's model are hidden until they get their own
     models — they stay in the roster data for story/other modes, but never
     as separate select cards. Attire variants live in the attire ladder
     (renderAttires), not as duplicate cards. */
  const selectRoster = () => {
    const r = deps.roster().filter(c => !SELECT_HIDDEN.has(c.id));
    setSelectRoster(r);
    return r;
  };

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
      const pool = selectRoster().filter(c => c.id !== state.locked.p1?.id && c.id !== state.locked.p2?.id);
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
      els.note.hidden = true;
      return;
    }
    els.name.textContent = c.name || '—';
    { const aw = els.root.querySelector('.pane-artwash img'); if (aw) aw.src = `assets/portraits/${c.id}.png`; }
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
    els.note.hidden = true;
    const ok = await panes[side].show(c, modelId);
    if (state.highlight[side]?.id !== c.id && state.locked[side]?.id !== c.id) return;
    if (panes[side].failed) {
      // No WebGL on this device: show the posed portrait plate
      // instead of the live model, and say so honestly.
      if (fb) { fb.src = `assets/portraits/${c.id}.png`; fb.hidden = false; }
      els.note.hidden = true; // owner law: never an error message on select
      return;
    }
    // A model that fails to load shows the fighter's own portrait plate,
    // never a message, a T-pose or another fighter.
    if (fb) { if (!ok) fb.src = `assets/portraits/${c.id}.png`; fb.hidden = !!ok; }
    els.note.hidden = true;
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
  function notifyConfirm(confirmedId) {
    const c = deps.findChar(confirmedId);
    if (!c) return;
    try {
      const side = state.mode === 'versus' && state.locked.p1 ? 'p2' : 'p1';
      const last = JSON.parse(localStorage.getItem(LAST_KEY) || '{}');
      last[side] = c.id; localStorage.setItem(LAST_KEY, JSON.stringify(last));
    } catch (_) {}
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

  // The Tripo list arrives after the first build: rebuild once so those fighters lead the grid.
  _tripoReady.then(() => { if (strip && strip.children.length) { build(); paintCards(); } });
  return { build, onShow, selectById, notifyConfirm, highlight, _state: state, _panes: panes };
}
