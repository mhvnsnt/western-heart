// ============================================================
// WESTERN HEART — Character Select (Lane I, Round 2, 2026-10-18)
//
// Tekken 8-style rebuild. Top ~76% = bisected LIVE 3D fighters zone
// (P1 left / P2 right, real GLBs, animated); bottom ~21% = contained
// card strip with INTERNAL scroll (the page never scrolls).
//
// Research basis (docs/select-redesign/SELECT-DESIGN.md):
//   T8  — bisected live-3D zone, "little personal acts" idles,
//         per-character attire slots chosen on the select screen,
//         bottom hints bar, "?" random. 3D real-time: what you see
//         is what you get in the match.
//   TTT2 — two-cursor flow (P1 cursor + P2 cursor), "?" boxes.
//   T6  — "?" random slots at the row ends; punch = outfit 1,
//         kick = outfit 2 (classic rule, T1 PSX manual).
// Owner spec — 75-80/20 split, tap/hover card -> render on your side,
//   name + fighting style + stats, attire switching ON the select,
//   mobile-first tap. Big zone is LIVE 3D ONLY (owner correction).
//
// Honesty notes:
//   * No real Tekken menu/UI files exist in our teardowns — the chrome
//     is rebuilt (see docs/select-redesign/UI-ASSET-INVENTORY.md).
//   * Idle clips: GLB-embedded "Idle" plays where present; otherwise a
//     neutral procedural breathing loop with a per-fighter personality
//     flavor. True per-fighter mocap idles do not exist in our assets.
//   * Fighters with no GLB in the repo show their card art on a 3D card
//     plane (live WebGL, gentle float) labeled MODEL PENDING — never a
//     static DOM <img> in the big zone.
// ============================================================
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.js";
import { clone as skeletonClone } from "three/addons/utils/SkeletonUtils.js";
import { ROSTER } from "./roster.js";

// ---------- per-fighter 3D config ----------
// glb paths are relative to game/ui-wh/. attires follow the owner slot law:
// early slots = WH/original designs, later slots = Tekken-based.
const MODELS = {
  pantera: {
    idle: "prowl",
    attires: [
      { slot: 1, name: "P1 ORIGINAL", glb: "../../docs/tpose-refs/pantera-t7king/pantera-t7king.glb" },
      { slot: 2, name: "LEO MAN", glb: null, pending: true }, // body asset not built yet (only mane/tail pieces)
      { slot: 3, name: "SNOW LEOPARD", glb: "../../roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb" },
      { slot: 4, name: "CLASSIC", glb: "../../roster/pantera/attires/classic/pantera-classic.glb" },
    ],
  },
  zui:        { idle: "weave",   glb: "../assets/models/steve-fox.glb" },
  demonio:    { idle: "menace",  glb: "../assets/models/demonio.glb" },
  phantom:    { idle: "drift",   glb: "../assets/models/phantom.glb" },
  diablo:     { idle: "menace",  glb: "../assets/models/diablo.glb" },
  skull:      { idle: "prowl",   glb: "../assets/models/skull.glb" },
  sam_ur_a1:  { idle: "mech",    glb: "../assets/models/sam-ur-a1.glb" },
  saku_ra:    { idle: "bounce",  glb: "../assets/models/saku-ra.glb" },
  kinpo:      { idle: "bounce",  glb: "../assets/models/kinpo.glb" },
  waterfall:  { idle: "drift",   glb: "../assets/models/waterfall.glb" },
  king_tyrant:{ idle: "showman", glb: "../assets/models/king-tyrant.glb" },
  awa_pop:    { idle: "bounce",  glb: "../assets/models/awa-pop.glb" },
  purple_rain:{ idle: "showman", glb: "../assets/models/purple-rain.glb" },
  nightwolf:  { idle: "prowl",   glb: "../assets/models/nightwolf.glb" },
  cyborg_x: {
    idle: "mech",
    attires: [
      // canon: Tripo main attire = slot 1; cyborg-x.glb (textured, PR #230) = slot 2
      { slot: 1, name: "CAPE JONES", glb: "../assets/models/cape-jones.glb" },
      { slot: 2, name: "CYBORG X", glb: "../assets/models/cyborg-x.glb" },
    ],
  },
  // No GLB in the repo (MODEL-STATUS.md): burger, scimitar, michiko, star,
  // torch, dio, bruno -> card-plane fallback, MODEL PENDING.
};
// Heights measured by the model audit (MODEL-STATUS.md). Never invented.
const HEIGHTS = { pantera: "1.75m", zui: "1.75m", demonio: "1.75m", cyborg_x: "1.49m", diablo: "2.00m" };
// card_pantera.png / card_zui.png are 0 bytes on origin/main -> bust fallbacks.
const CARD_FALLBACK = {
  pantera: "./portraits/pantera_bust.png",
  zui: "./portraits/zui_a1wip_bust.png",
};
const cardURL = (id) => `../../docs/qa/roster-cards/card_${id}.png`;

const esc = (s) => String(s ?? "").replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]));

// Personality idle flavors (procedural; real "Idle" clip wins when present).
const IDLE_FLAVOR = {
  prowl:   { sway: 0.055, speed: 1.0, bob: 0.018, bobSpeed: 1.5 },
  weave:   { sway: 0.13,  speed: 0.85, bob: 0.03,  bobSpeed: 1.1, roll: 0.035 }, // ZUI, drunken soul
  menace:  { sway: 0.03,  speed: 0.6,  bob: 0.012, bobSpeed: 0.9 },
  drift:   { sway: 0.08,  speed: 0.7,  bob: 0.05,  bobSpeed: 1.2 },              // floaters
  bounce:  { sway: 0.05,  speed: 1.6,  bob: 0.055, bobSpeed: 2.3 },             // idols
  mech:    { sway: 0.02,  speed: 2.6,  bob: 0.008, bobSpeed: 3.1, stepped: true },
  showman: { sway: 0.09,  speed: 1.2,  bob: 0.025, bobSpeed: 1.7 },
};

// ---------- three.js zone ----------
function makeZone(canvas) {
  // preserveDrawingBuffer: true lets QA capture tools (and canvas.toDataURL)
  // reliably screenshot the live 3D zone; negligible cost for this scene.
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  // Fight-lighting family (game/js/stages.js): hemi + sun + rim + fill.
  scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x3a2418, 0.9));
  const sun = new THREE.DirectionalLight(0xfff2dd, 1.7); sun.position.set(3, 6, 5); scene.add(sun);
  const rim = new THREE.DirectionalLight(0x7fb2ff, 1.0); rim.position.set(-4, 3, -4); scene.add(rim);
  const fill = new THREE.DirectionalLight(0xffd9c2, 0.55); fill.position.set(-2, 2, 5); scene.add(fill);

  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  const texLoader = new THREE.TextureLoader();
  const cache = new Map(); // glb url -> { obj, skinned, clips }

  const SIDE_X = { p1: -1.55, p2: 1.55 };
  const sides = {};
  for (const side of ["p1", "p2"]) {
    const cam = new THREE.PerspectiveCamera(38, 1, 0.1, 60);
    cam.position.set(SIDE_X[side], 1.5, 4.7);
    cam.lookAt(SIDE_X[side], 1.02, 0);
    const group = new THREE.Group();
    group.position.x = SIDE_X[side];
    scene.add(group);
    // soft ground disc under the fighter
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(1.15, 40),
      new THREE.MeshBasicMaterial({ map: radialTex(), transparent: true, depthWrite: false })
    );
    disc.rotation.x = -Math.PI / 2; disc.position.y = 0.01;
    group.add(disc);
    sides[side] = { cam, group, disc, current: null, mixer: null, flavor: null, phase: Math.random() * 9, key: null };
  }
  function radialTex() {
    const c = document.createElement("canvas"); c.width = c.height = 128;
    const g = c.getContext("2d");
    const grad = g.createRadialGradient(64, 64, 4, 64, 64, 64);
    grad.addColorStop(0, "rgba(0,0,0,0.55)"); grad.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(c); return t;
  }

  function normalize(obj, targetH = 1.72) {
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    if (size.y > 1e-4) obj.scale.setScalar(targetH / size.y);
    const b2 = new THREE.Box3().setFromObject(obj);
    const c = b2.getCenter(new THREE.Vector3());
    obj.position.x -= c.x; obj.position.z -= c.z; obj.position.y -= b2.min.y;
    return obj;
  }

  async function loadTemplate(key, glb) {
    if (cache.has(key)) return cache.get(key);
    const p = new Promise((resolve, reject) => {
      loader.load(glb, (g) => {
        const obj = new THREE.Group();
        obj.add(normalize(g.scene));
        let skinned = false;
        obj.traverse((o) => { if (o.isSkinnedMesh) skinned = true; });
        const clips = (g.animations || []).slice();
        const rec = { obj, skinned, clips };
        cache.set(key, rec); resolve(rec);
      }, undefined, reject);
    });
    cache.set(key, p); // dedupe in-flight
    const rec = await p;
    if (rec && rec.obj) cache.set(key, rec);
    return cache.get(key);
  }

  async function loadCardPlane(key, url) {
    if (cache.has(key)) return cache.get(key);
    const p = new Promise((resolve, reject) => {
      texLoader.load(url, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.85, metalness: 0.05 });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(1.35, 1.0), mat);
        const obj = new THREE.Group(); obj.add(m); m.position.y = 1.05;
        // thin gold frame so it reads as a "card" in 3D, not a photo
        const frame = new THREE.Mesh(
          new THREE.PlaneGeometry(1.43, 1.08),
          new THREE.MeshBasicMaterial({ color: 0xf2b24a })
        );
        frame.position.z = -0.012; obj.add(frame); m.position.z = 0;
        const rec = { obj, skinned: false, clips: [], card: true };
        cache.set(key, rec); resolve(rec);
      }, undefined, reject);
    });
    cache.set(key, p);
    const rec = await p;
    if (rec && rec.obj) cache.set(key, rec);
    return cache.get(key);
  }

  function clearSideVisual(s) {
    if (s.current) { s.group.remove(s.current); s.current = null; }
    if (s.mixer) { s.mixer.stopAllAction(); s.mixer = null; }
    s.flavor = null;
  }
  function clearSide(side) {
    const s = sides[side];
    clearSideVisual(s);
    s.key = null;
  }

  // Show a fighter (or attire) on a side. Live swap, T8-style.
  // The old fighter stays visible until the new GLB is ready (no empty stage).
  async function setSide(side, fighterId, attireIdx = 0, onSwap) {
    const s = sides[side];
    const cfg = MODELS[fighterId];
    const attire = cfg && cfg.attires ? cfg.attires[attireIdx] : null;
    const glb = attire ? attire.glb : cfg && cfg.glb;
    const key = `${fighterId}:a${attireIdx}`;
    if (s.key === key) return;
    s.key = key; // reserve first: supersedes older in-flight loads
    try {
      let rec;
      if (!glb) {
        // MODEL PENDING: card art on a live 3D card plane (never a DOM <img>).
        rec = await loadCardPlane(key, cardURL(fighterId));
      } else {
        rec = await loadTemplate(key, glb);
      }
      if (s.key !== key) return; // superseded while loading
      clearSideVisual(s); // swap only now that the new one is ready
      const inst = rec.skinned ? skeletonClone(rec.obj) : rec.obj.clone(true);
      const inner = new THREE.Group(); inner.add(inst); // keep normalize space clean
      s.group.add(inner);
      // P2 faces left (mirror), like the classic select sides
      inner.rotation.y = side === "p2" ? Math.PI : 0;
      s.current = inner;
      s.flavor = IDLE_FLAVOR[(cfg && cfg.idle) || "prowl"];
      // real embedded Idle clip wins over procedural (T8 "personal acts")
      const idleClip = (rec.clips || []).find((c) => /idle/i.test(c.name));
      if (idleClip && !rec.card) {
        s.mixer = new THREE.AnimationMixer(inst);
        const act = s.mixer.clipAction(idleClip);
        act.play();
      }
      if (rec.card) s.flavor = IDLE_FLAVOR.drift;
      onSwap && onSwap();
    } catch (e) {
      console.warn("[select] 3D load failed", fighterId, attireIdx, e);
      s.key = null;
    }
  }

  const clock = new THREE.Clock();
  let running = true, ready = false;
  function frame() {
    requestAnimationFrame(frame);
    if (!running) return;
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;
    for (const side of ["p1", "p2"]) {
      const s = sides[side];
      if (s.mixer) s.mixer.update(dt);
      if (s.current && s.flavor && !s.mixer) {
        const f = s.flavor, ph = s.phase;
        const sway = f.stepped
          ? Math.round(Math.sin(t * f.speed + ph) * 2) / 2 * f.sway
          : Math.sin(t * f.speed + ph) * f.sway;
        s.current.rotation.y = (side === "p2" ? Math.PI : 0) + sway;
        s.current.position.y = Math.abs(Math.sin(t * f.bobSpeed + ph)) * f.bob;
        if (f.roll) s.current.rotation.z = Math.sin(t * f.speed * 0.7 + ph) * f.roll;
      } else if (s.current && s.mixer) {
        // subtle life on top of the real clip
        s.current.position.y = Math.abs(Math.sin(t * 1.5 + s.phase)) * 0.008;
      }
    }
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== Math.floor(w * renderer.getPixelRatio())) {
      renderer.setSize(w, h, false);
      for (const side of ["p1", "p2"]) sides[side].cam.aspect = (w / 2) / Math.max(h, 1);
      for (const side of ["p1", "p2"]) sides[side].cam.updateProjectionMatrix();
    }
    for (const [i, side] of ["p1", "p2"].entries()) {
      const s = sides[side];
      renderer.setViewport((w / 2) * i, 0, w / 2, h);
      renderer.setScissor((w / 2) * i, 0, w / 2, h);
      renderer.setScissorTest(true);
      renderer.render(scene, s.cam);
    }
    renderer.setScissorTest(false);
    if (!ready) { ready = true; window.__WH_SELECT_READY = true; }
  }
  requestAnimationFrame(frame);
  return { setSide, sides,
    setRunning: (v) => { running = v; if (v) clock.getDelta(); },
    warm: (url) => loadTemplate(url, url).catch(() => {}), // idle prefetch (template cache)
    debug() {
      const out = {};
      for (const side of ["p1", "p2"]) {
        const s = sides[side];
        let bbox = null;
        if (s.current) {
          const b = new THREE.Box3().setFromObject(s.current);
          const sz = b.getSize(new THREE.Vector3()), c = b.getCenter(new THREE.Vector3());
          bbox = { size: sz.toArray().map((n) => +n.toFixed(3)), center: c.toArray().map((n) => +n.toFixed(3)) };
        }
        out[side] = { key: s.key, children: s.group.children.length, hasCurrent: !!s.current, mixer: !!s.mixer, bbox };
      }
      return out;
    },
    dispose: () => { running = false; renderer.dispose(); } };
}

// ---------- select screen ----------
export function initSelect(root, api = {}) {
  if (root.dataset.whselInit) return root._whsel;
  root.dataset.whselInit = "1";
  const byId = (id) => ROSTER.find((r) => r.id === id);

  const S = {
    p1: { id: (api.initial && api.initial.p1) || "pantera", attire: 0, locked: false },
    p2: { id: (api.initial && api.initial.p2) || "saku_ra", attire: 0, locked: false },
    cursor: "p1",
  };
  const normId = (id) => (byId(id) ? id : "pantera");

  const attireOf = (id) => {
    const cfg = MODELS[id];
    return (cfg && cfg.attires) || [{ slot: 1, name: "ATTIRE 1", glb: cfg && cfg.glb }];
  };
  const hasGLB = (id) => {
    const a = attireOf(id);
    return a.some((x) => x.glb);
  };

  // ----- DOM -----
  root.innerHTML = `
    <div class="whsel-head"><h2>CHOOSE YOUR VESSEL<i>魂を選べ</i></h2><span class="sub">TEKKEN 8-STYLE · LIVE 3D</span></div>
    <div class="whsel-zone">
      <canvas class="whsel-gl"></canvas>
      <div class="whsel-bisect"></div>
      <div class="whsel-half l" data-side="p1"></div>
      <div class="whsel-half r" data-side="p2"></div>
      <div class="whsel-side-tag p1">1P<span class="lock"></span></div>
      <div class="whsel-side-tag p2">2P<span class="lock"></span></div>
      <div class="whsel-cursor-toggle">
        <button data-cur="p1" class="on-p1">1P</button><button data-cur="p2">2P</button>
      </div>
      <div class="whsel-stats left"></div>
      <div class="whsel-stats right"></div>
      <div class="whsel-flash"></div>
      <div class="whsel-loading">SUMMONING FIGHTERS…</div>
    </div>
    <div class="whsel-hints">
      <span><b>TAP</b> card: preview</span>
      <button class="confirm">CONFIRM</button>
      <span><b>1·2·3</b> attire</span>
      <span><b>?</b> random</span>
      <span><b>ESC</b> back</span>
    </div>
    <div class="whsel-strip"><div class="cards"></div></div>`;
  const $ = (s) => root.querySelector(s);
  const zone = makeZone($(".whsel-gl"));
  new IntersectionObserver((es) => es.forEach((e) => zone.setRunning(e.isIntersecting)), { threshold: 0.05 }).observe(root);
  document.addEventListener("visibilitychange", () => zone.setRunning(!document.hidden));

  function flash() {
    const f = $(".whsel-flash");
    f.classList.remove("go"); void f.offsetWidth; f.classList.add("go");
  }

  function renderStats(side) {
    const st = S[side], r = byId(st.id), el = $(`.whsel-stats.${side === "p1" ? "left" : "right"}`);
    const attires = attireOf(st.id);
    const chips = attires.map((a, i) =>
      `<button data-attire="${i}" class="${i === st.attire ? "on" : ""}" ${a.pending || !a.glb ? "disabled" : ""}>${a.slot}<span class="an">${esc(a.name)}</span></button>`
    ).join("");
    el.innerHTML = `
      <div class="nm"><span class="k">${esc(r.kanji)}</span>${esc(r.name)}</div>
      <div class="soul">${esc(r.soul)}</div>
      <dl>
        <div><dt>STYLE</dt><dd>${esc(r.body)}</dd></div>
        <div><dt>ORIGIN</dt><dd>${esc(r.origin)}</dd></div>
        <div><dt>HEIGHT</dt><dd>${HEIGHTS[st.id] || "—"}</dd></div>
      </dl>
      ${hasGLB(st.id) ? "" : `<span class="whsel-pending">MODEL PENDING</span>`}
      <div class="whsel-attires"><span class="lbl">ATTIRE</span>${chips}</div>`;
    el.querySelectorAll("[data-attire]").forEach((b) => b.addEventListener("click", (e) => {
      e.stopPropagation();
      st.attire = +b.dataset.attire; st.locked = false;
      refresh(side, true);
    }));
  }

  function renderTags() {
    for (const side of ["p1", "p2"]) {
      $(`.whsel-side-tag.${side} .lock`).textContent = S[side].locked ? "· LOCKED" : "";
      const card = $(`.whsel-card[data-id="${S[side].id}"]`);
      root.querySelectorAll(".whsel-card").forEach((c) => {
        c.classList.toggle("cur-p1", c.dataset.id === S.p1.id);
        c.classList.toggle("cur-p2", c.dataset.id === S.p2.id);
        c.classList.toggle("locked-p1", c.dataset.id === S.p1.id && S.p1.locked);
        c.classList.toggle("locked-p2", c.dataset.id === S.p2.id && S.p2.locked);
      });
    }
    root.querySelectorAll("[data-cur]").forEach((b) => {
      b.className = S.cursor === b.dataset.cur ? (S.cursor === "p1" ? "on-p1" : "on-p2") : "";
    });
  }

  let swapCount = 0;
  function refresh(side, withFlash) {
    renderStats(side); renderTags();
    const st = S[side];
    zone.setSide(side, st.id, st.attire, () => {
      if (++swapCount >= 1) { const l = $(".whsel-loading"); l && l.remove(); }
      if (withFlash) flash();
    });
  }
  function refreshAll(withFlash) { refresh("p1", withFlash); refresh("p2", withFlash); }

  function confirmSide(side) {
    const st = S[side];
    if (!st.locked) {
      st.locked = true; renderTags();
      if (side === "p1") {
        S.cursor = "p2";
        if (S.p2.id === S.p1.id) { // T8-style: nudge P2 off a mirror pick
          const others = ROSTER.filter((r) => r.id !== S.p1.id);
          S.p2.id = others[Math.floor(Math.random() * others.length)].id;
          S.p2.locked = false; refresh("p2", true);
        }
        renderTags();
      } else {
        const a1 = attireOf(S.p1.id)[S.p1.attire], a2 = attireOf(S.p2.id)[S.p2.attire];
        (api.onFight || (() => {}))(S.p1.id, S.p2.id, a1.slot, a2.slot);
      }
    } else if (side === "p2" && S.p1.locked) {
      const a1 = attireOf(S.p1.id)[S.p1.attire], a2 = attireOf(S.p2.id)[S.p2.attire];
      (api.onFight || (() => {}))(S.p1.id, S.p2.id, a1.slot, a2.slot);
    }
  }

  function pick(id, opts = {}) {
    const side = opts.side || S.cursor;
    const st = S[side];
    st.id = normId(id); st.attire = 0; st.locked = false;
    refresh(side, true);
  }
  function randomPick(side) {
    const pool = ROSTER.filter((r) => r.id !== S[side === "p1" ? "p2" : "p1"].id);
    pick(pool[Math.floor(Math.random() * pool.length)].id, { side });
  }

  // ----- card strip (the ONLY scroll; contained in its box) -----
  const cardsEl = $(".whsel-strip .cards");
  cardsEl.innerHTML = ROSTER.map((r) => {
    const img = CARD_FALLBACK[r.id] || cardURL(r.id);
    return `<div class="whsel-card" data-id="${r.id}" role="button" tabindex="0" aria-label="${esc(r.name)}">
      <img class="pic" src="${img}" alt="" loading="lazy" draggable="false">
      <span class="k">${esc(r.kanji)}</span><span class="nm">${esc(r.name)}</span>
      ${hasGLB(r.id) ? "" : `<span class="pend">MODEL PENDING</span>`}
    </div>`;
  }).join("") + `
    <div class="whsel-card random" data-id="?" role="button" tabindex="0" aria-label="Random">
      <div class="pic" style="display:flex;align-items:center;justify-content:center;font-size:44px;color:var(--gold);">?</div>
      <span class="nm">RANDOM</span>
    </div>`;

  let pressTimer = null;
  cardsEl.querySelectorAll(".whsel-card").forEach((c) => {
    const id = c.dataset.id;
    const commit = (side) => { id === "?" ? randomPick(side || S.cursor) : pick(id, { side }); };
    c.addEventListener("click", () => commit());
    c.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); commit(); } });
    // desktop hover = preview on cursor side (T8 hover behavior); tap = commit
    if (matchMedia("(pointer:fine)").matches && id !== "?") {
      c.addEventListener("mouseenter", () => {
        const side = S.cursor;
        if (!S[side].locked) zone.setSide(side, normId(id), 0, null);
      });
      c.addEventListener("mouseleave", () => {
        const side = S.cursor;
        if (!S[side].locked) { const st = S[side]; zone.setSide(side, st.id, st.attire, null); }
      });
    }
    // long-press = assign to the OTHER side (mobile-first P2 pick)
    c.addEventListener("pointerdown", () => {
      pressTimer = setTimeout(() => { commit(S.cursor === "p1" ? "p2" : "p1"); pressTimer = null; }, 550);
    });
    for (const ev of ["pointerup", "pointerleave", "pointercancel"])
      c.addEventListener(ev, () => { if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; } });
  });

  // ----- chrome wiring -----
  root.querySelectorAll("[data-cur]").forEach((b) => b.addEventListener("click", () => {
    S.cursor = b.dataset.cur; renderTags();
  }));
  root.querySelectorAll(".whsel-half").forEach((h) => h.addEventListener("click", () => confirmSide(h.dataset.side)));
  $(".whsel-hints .confirm").addEventListener("click", () => confirmSide(S.cursor));
  // classic Tekken: punch = confirm with attire 1, kick = confirm with attire 2
  document.addEventListener("keydown", (e) => {
    if (!root.isConnected || !root.offsetParent) return;
    if (e.key === "Enter") confirmSide(S.cursor);
    else if (e.key === "Escape") (api.onBack || (() => {}))();
    else if (e.key === "p" || e.key === "P") { S[S.cursor].attire = 0; confirmSide(S.cursor); }
    else if (e.key === "k" || e.key === "K") {
      const n = attireOf(S[S.cursor].id).length;
      S[S.cursor].attire = Math.min(1, n - 1); confirmSide(S.cursor);
    }
  });

  // ----- go -----
  S.p1.id = normId(S.p1.id); S.p2.id = normId(S.p2.id);
  refreshAll(false);

  // Idle prefetch: warm the GLB template cache so card taps swap near-instantly
  // (T8 keeps its select assets resident). Curated list only — the full set is
  // ~300MB, too heavy to hold resident on phones. Skipped on low-memory
  // devices and with ?noprefetch=1 (low-end / software renderers).
  const noPrefetch = new URLSearchParams(location.search).has("noprefetch");
  const idleFn = window.requestIdleCallback || ((fn) => setTimeout(fn, 2000));
  idleFn(() => {
    if (noPrefetch) return;
    if (navigator.deviceMemory && navigator.deviceMemory < 4) return;
    const urls = [
      "../assets/models/steve-fox.glb",   // ZUI (playable gate)
      "../assets/models/demonio.glb",      // DEMONIO (playable gate)
      "../../roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb",
      "../../roster/pantera/attires/classic/pantera-classic.glb",
      "../assets/models/cape-jones.glb",   // CYBORG X slot 1
      "../assets/models/diablo.glb",
      "../assets/models/saku-ra.glb",
    ];
    let i = 0;
    const step = () => {
      if (i < urls.length && !document.hidden) zone.warm(urls[i++]).finally(() => setTimeout(step, 1200));
    };
    step();
  });

  const handle = {
    setFighters(p1, p2) {
      if (p1) { S.p1.id = normId(p1); S.p1.locked = false; }
      if (p2) { S.p2.id = normId(p2); S.p2.locked = false; }
      refreshAll(true);
    },
    destroy() { zone.dispose(); delete root.dataset.whselInit; },
  };
  root._whsel = handle;
  window.__WH_SELECT_DBG = () => zone.debug(); // QA hook: per-side 3D state
  window.__WH_SELECT_FREEZE = (v) => zone.setRunning(!v); // QA hook: freeze rAF for screenshots
  return handle;
}
