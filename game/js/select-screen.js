/* ============================================================
   WESTERN HEART — Tekken 8-style character select (2026-10-22
   grid transplant; replaces the 2026-10-20 bisected-zone+strip).
   Layout lineage (decoded from public T8 references — see
   docs/select-redesign/T8-GRID-DECODE.md; no ripped Tekken UI):
   - T8: bisected P1/P2 big-model zone, each side with a large
     faded portrait-art backdrop (red wash P1, blue wash P2),
     big italic name banner, fact block (Fighting Style /
     Nationality / Height / Weight), and a COMPACT CENTERED GRID
     of small square portrait cards — small relative to
     everything else, P1 (pink-red) / P2 (blue) cursors, locked
     cards badged P1/P2, "?" random slot in the grid, bottom
     hints bar (Confirm / Back / Customized Slots).
   - T3 selector (teardown record): the selected aperture is LARGER
     than its neighbours; timer starts at 99; two-step pick
     (fighter, then outfit); "?" random slot.
   - T6/T1: punch = outfit 1, kick = outfit 2 at select.
   Owner spec carried over: tap a card -> that fighter's animated
   model appears on YOUR side; name + style + stats on the plate;
   attire switching ON the select screen (T8 "customized slots");
   touch first; the grid is the ONLY scrolling element and scrolls
   inside its own box — the page never scrolls.
   The LOOK is skin-driven (js/ui-skin.js): every color, font,
   and card-geometry token comes from the active skin, so the T8
   look can be refined or swapped without touching this logic.
   Previews reuse the existing model pipeline (assets.js
   loadModels/createInstance) — the same GLBs and Idle clips
   the fight itself uses. Stats shown are the game's real
   numbers: roster `stats` or the Fighter default
   (fighter.js: { speed: 2.8, jump: 7.2, power: 1.1,
   defense: 1.05 }, speed clamped to 3.5).
   ============================================================ */
import * as THREE from 'three';
import { assets } from './assets.js';
import { attiresFor, selectedAttireModel, setAttire, attireLabel } from './attires.js';
// LOADSPEED: t3anims / fighter / movesets are preview-and-fight-only —
// they stream in on first highlight through lazy.js (warmed during menu
// idle), not at boot. See game/js/lazy.js.
import { lazy } from './lazy.js';
import { mark } from './loadperf.js';
import { getSkin, applySkin, activeSkinId } from './ui-skin.js';
/* Tier membership comes from the roster module (SOUL_IDS/MAIN_IDS) —
   the same source main's select screen used; the grid only restyles
   the presentation, it never redefines the tiers. */
import { SOUL_IDS, MAIN_IDS } from './roster-full.js';

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
    // LOADSPEED: a new tap supersedes the previous preview — abort its
    // download instead of finishing a doomed multi-MB fetch in the
    // background (it used to compete with the new tap for bandwidth).
    if (this._loadAbort) this._loadAbort.abort();
    const loadAbort = new AbortController();
    this._loadAbort = loadAbort;
    mark('preview-start');
    this._loading = true;
    if (!this._ensure()) { this._loading = false; return false; }
    try {
      await assets.loadModels([modelId], null, { signal: loadAbort.signal });
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
      mark('preview-ready');
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
        // LOADSPEED: the T3 bank modules stream on first highlight
        // (warmed during menu idle via lazy.warmIdle).
        const [F, T3A, MS] = await Promise.all([lazy.fighter(), lazy.t3anims(), lazy.movesets()]);
        const { bankIdFor } = F;
        const { loadT3Clips, createT3Actions, retargetT3Clips } = T3A;
        const { getMovesetInfo } = MS;
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
      // LOADSPEED: an aborted superseded load is not a failure — stay quiet.
      if (e && (e.name === 'AbortError' || /abort/i.test(e.message || ''))) return true;
      if (token === this._token) {
        console.warn('[WH] select preview failed for', modelId, e.message || e);
        this._clearModel();
      }
      return false;
    } finally {
      if (token === this._token) { this._loading = false; this._loadAbort = null; }
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

  clear() {
    this._token++;
    if (this._loadAbort) { this._loadAbort.abort(); this._loadAbort = null; }
    this._clearModel();
  }

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

/* Identity canon guard (owner, non-negotiable): the grid is built from
   the roster the game hands us, and these mappings must hold there —
   RAVE = KIKO TANAKA = GHOST is ONE entry ('rave'); MARY POSA goes
   OVER Zafina (no separate Zafina slot); PHANTOM is the select entry
   (Yoshimitsu ladders into Phantom's attires, never a second card).
   This builder asserts the canon rather than re-implementing it: if
   the roster ever violates it, the violation is logged loudly instead
   of silently rendering two cards. */
function assertCanon(roster) {
  const ids = new Set(roster.map(c => c.id));
  const problems = [];
  if (ids.has('kiko-tanaka') || ids.has('ghost')) problems.push('rave/kiko-tanaka/ghost split into separate entries');
  if (ids.has('zafina')) problems.push('separate zafina slot (mary posa goes OVER zafina)');
  if (ids.has('yoshimitsu')) problems.push('separate yoshimitsu slot (ladders into phantom attires)');
  if (problems.length) console.error('[WH] select canon violation:', problems.join(' · '));
}

export function createSelectScreen(deps) {
  const { audio } = deps;
  const $ = (id) => document.getElementById(id);
  const grid = $('char-grid');
  const hint = $('select-hint');
  const confirmBtn = $('confirm-fighter');
  const root = $('screen-select');

  // Skin: every visual token comes from ui-skin.js (drop-in contract
  // documented there). Re-applied on build + onShow so a ?skin=<id>
  // deep link or setSkin() call takes effect without a reload.
  const skin = () => getSkin(activeSkinId());
  if (root) applySkin(root, skin());

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
    // TTT2 TEAM BATTLE (worker 24): the versus submenu lives INSIDE the
    // select screen — 1V1 FIGHT or TEAM BATTLE (2-8 per team), then a
    // character per slot. TTT2 actual: solo/tag choice BEFORE any pick.
    vsMode: null,        // 'solo' | 'team' (versus only; null = not chosen)
    teamSize: 2,         // fighters per team (2 = TTT2 tag rules)
    draft: { p1: [], p2: [] },
    draftSide: 'p1',
    vsTeamsDone: null,   // { p1:[ids], p2:[ids], size } when draft completes
  };

  /* ---------- T8 grid ---------- */
  function portraitHTML(c) {
    // Portrait files are the personality pass's drop-in point:
    // assets/portraits/<id>.png. A fighter with no portrait yet gets
    // a monogram plate — never another fighter's face (the old
    // repeated-placeholder bug).
    return `<div class="portrait"><img src="assets/portraits/${c.id}.png" alt="${c.name}" loading="lazy"
      onerror="this.parentElement.classList.add('no-portrait');this.remove();">
      <span class="mono">${(c.name || '?').slice(0, 2)}</span></div>
      <div class="cname">${c.name}</div>`;
  }

  function build() {
    if (!grid) return;
    if (root) applySkin(root, skin());
    grid.innerHTML = '';
    const roster = deps.roster();
    assertCanon(roster);
    const tripo = TRIPO_IDS || new Set();
    const rest = (list) => list.filter(c => !tripo.has(c.id));
    const tiers = [
      { label: 'TRIPO ORIGINALS', fighters: roster.filter(c => tripo.has(c.id)) },
      { label: 'THE NINE SOULS', fighters: rest(roster.filter(c => SOUL_IDS.includes(c.id))) },
      { label: 'MAIN ROSTER', fighters: rest(roster.filter(c => MAIN_IDS.includes(c.id))) },
      { label: 'BONUS ROSTER', fighters: rest(roster.filter(c => !SOUL_IDS.includes(c.id) && !MAIN_IDS.includes(c.id))) },
    ].filter(t => t.fighters.length);
    tiers.forEach(({ label, fighters }) => {
      const t = document.createElement('div');
      t.className = 'grid-tier';
      t.textContent = label;
      grid.appendChild(t);
      fighters.forEach((c) => {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.dataset.id = c.id;
        card.innerHTML = portraitHTML(c);
        card.addEventListener('click', () => highlight(c, { fromTap: true }));
        grid.appendChild(card);
      });
    });
    // Tekken 6 convention: a "?" random slot in the grid.
    const rnd = document.createElement('div');
    rnd.className = 'char-card random-card';
    rnd.dataset.id = '__random';
    rnd.innerHTML = `<div class="portrait"><span class="qmark">?</span></div>
      <div class="cname">RANDOM</div>`;
    rnd.addEventListener('click', () => {
      const drafted = [...state.draft.p1, ...state.draft.p2];
      const pool = deps.roster().filter(c => c.id !== state.locked.p1?.id && c.id !== state.locked.p2?.id &&
        !drafted.includes(c.id));
      const pick = pool[Math.floor(Math.random() * pool.length)];
      if (pick) highlight(pick, { fromTap: true, scroll: true });
    });
    grid.appendChild(rnd);
  }

  function allCards() { return [...grid.querySelectorAll('.char-card')]; }
  function cardFor(id) { return grid.querySelector(`.char-card[data-id="${id}"]`); }

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
    const rootEl = $(side === 'p1' ? 'pane-p1' : 'pane-p2');
    return {
      root: rootEl,
      artwash: rootEl.querySelector('.pane-artwash img'),
      name: rootEl.querySelector('.pane-name'),
      facts: rootEl.querySelector('.pane-facts'),
      stats: rootEl.querySelector('.pane-stats'),
      attires: rootEl.querySelector('.pane-attires'),
      note: rootEl.querySelector('.pane-note'),
      lock: rootEl.querySelector('.lock-badge'),
      tag: rootEl.querySelector('.side-tag'),
    };
  }

  function statRow(label, value, frac, fmt) {
    return `<div class="stat-row"><span class="stat-lab">${label}</span>
      <span class="stat-bar"><i style="width:${Math.round(clamp01(frac) * 100)}%"></i></span>
      <span class="stat-val">${fmt(value)}</span></div>`;
  }

  /* T8 fact block: label chip in the side color + value below,
     one row per skin.facts entry. Values come from the fighter;
     ORIGIN falls back to canon "Parts unknown" — never invented. */
  function renderFacts(els, c, sk) {
    const rows = [];
    for (const [label, field] of sk.facts) {
      let v = c[field];
      if (field === 'origin' && !v) v = 'Parts unknown';
      if (v === undefined || v === null || v === '') continue;
      rows.push(`<div class="fact"><span class="fact-lab">${label}</span><span class="fact-val">${v}</span></div>`);
    }
    els.facts.innerHTML = rows.join('');
  }

  function renderPlate(side) {
    const els = plateEls(side);
    const locked = state.locked[side];
    const c = locked || state.highlight[side];
    const isActive = state.activeSide === side && !locked;
    els.root.classList.toggle('is-active', isActive);
    els.root.classList.toggle('is-locked', !!locked);
    els.lock.hidden = !locked;
    // Backdrop art wash (T8): the fighter's portrait, huge and faded
    // behind the live model, tinted by side color. Updated only when
    // the fighter changes so the image never reload-flickers.
    const artId = c ? c.id : '';
    if (els.artwash && els.root.dataset.artId !== artId) {
      els.root.dataset.artId = artId;
      if (artId) {
        els.artwash.hidden = false;
        els.artwash.onerror = () => { els.artwash.hidden = true; };
        els.artwash.src = `assets/portraits/${artId}.png`;
      } else {
        els.artwash.hidden = true;
        els.artwash.removeAttribute('src');
      }
    }
    if (!c) {
      els.name.textContent = side === 'p1' ? 'PLAYER 1' : 'PLAYER 2';
      els.facts.innerHTML = '';
      els.stats.innerHTML = '';
      els.attires.innerHTML = '';
      els.note.hidden = true;
      return;
    }
    els.name.textContent = c.name || '—';
    renderFacts(els, c, skin());
    const modelId = selectedAttireModel(c);
    const s = statsFor(c);
    els.stats.innerHTML =
      statRow('POW', s.power, (s.power - 0.5) / 1.5, v => v.toFixed(2)) +
      statRow('SPD', s.speed, s.speed / 3.5, v => v.toFixed(1)) +
      statRow('JMP', s.jump, s.jump / 10, v => v.toFixed(1)) +
      statRow('DEF', s.defense, (s.defense - 0.5) / 1.5, v => v.toFixed(2));
    // Attire label joins the fact block's tail (T8 "customized slots"
    // live on the select screen).
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
    if (opts.fromTap) {
      const el = cardFor(c.id);
      if (el) {
        el.classList.remove('tap-flash');
        void el.offsetWidth; // restart the animation
        el.classList.add('tap-flash');
      }
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
    // TTT2 draft: during a team-battle draft, CONFIRM fills the next
    // team slot (your team first, then the rival team) instead of the
    // classic P1-then-P2 lock flow.
    if (state.mode === 'versus' && state.vsMode === 'team') {
      draftConfirm(c);
      return;
    }
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
    if (root) applySkin(root, skin());
    if (fresh) {
      state.mode = mode;
      state.phase = 'pick';
      state.activeSide = 'p1';
      state.highlight = { p1: null, p2: null };
      state.locked = { p1: null, p2: null };
      state.teamPicks = [];
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
    paintCards();
    renderPlate('p1');
    renderPlate('p2');
  }

  /* ---------- keyboard (desktop parity; touch is primary) ----------
     Arrows walk the grid (up/down jump a full row, computed from the
     rendered columns), Enter highlights then confirms (via the real
     CONFIRM button so every mode hook still fires), J/K are
     punch/kick attire switching. */
  function gridCols() {
    if (!grid) return 1;
    const t = getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length;
    return Math.max(1, t || 1);
  }
  document.addEventListener('keydown', (e) => {
    const sel = $('screen-select');
    if (!sel || !sel.classList.contains('active')) return;
    const cards = allCards();
    if (!cards.length) return;
    const cols = gridCols();
    const step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: cols, ArrowUp: -cols }[e.key];
    if (step !== undefined) {
      state.focusIdx = (state.focusIdx + step + cards.length) % cards.length;
      cards.forEach(x => x.classList.remove('kb-focus'));
      const el = cards[state.focusIdx];
      el.classList.add('kb-focus');
      el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      e.preventDefault();
    } else if (e.key === 'Enter' || e.key === ' ') {
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
  _tripoReady.then(() => { if (grid && grid.children.length) { build(); paintCards(); } });

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
    const grid2 = $('select-grid') || grid;
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

  return { build, onShow, selectById, notifyConfirm, highlight, _state: state, _panes: panes };
}
