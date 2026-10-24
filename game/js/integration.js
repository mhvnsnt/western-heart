/* ============================================================
   WESTERN HEART — integration boot (worker 22, 2026-10-22)
   Wires the newly-vendored open-source systems into the game:

     physics.js      cannon-es          rigid bodies, debris, KO tumble
     hitdetect.js    three-mesh-bvh     BVH precision hit layer (verify)
     springbones.js  WH-original       runtime jiggle (verlet chains)
     hitfx-nebula.js three-nebula       JSON particle hit effects
     fx/particles.js   effekseer 1.80.7  GPU particle runtime (.efkefc)
     fx/hit-effects.js unified hit FX    Effekseer + nebula fallback
     fx/soulurge-fx.js Soul Urge cues    Effekseer ignition/aura/smash
     labels3d.js     troika-three-text  3D nameplates / damage numbers
     camdirector.js  camera-controls    cutscene + photo-mode camera
     lipsync-player.js WH-original      mouth-cue playback (voice lane)

   Design: every system lazy-loads with try/catch. If any vendor file
   fails, the game keeps running — the system is simply absent from
   window.WHIntegration. No system here is on the combat-critical path.

   Loaded from game/index.html as a plain module script AFTER main.js.
   ============================================================ */

const WHIntegration = {
  ready: false,
  systems: {},   // name -> instance
  failed: {},    // name -> error message
};

async function tryInit(name, path, initFn) {
  try {
    const mod = await import(path);
    const inst = await initFn(mod);
    WHIntegration.systems[name] = inst;
    console.info(`[WHIntegration] ${name} ready`);
    return inst;
  } catch (e) {
    WHIntegration.failed[name] = String(e && e.message || e);
    console.warn(`[WHIntegration] ${name} unavailable:`, e);
    return null;
  }
}

function waitForGame() {
  return new Promise((resolve) => {
    if (window.__game && window.__game.arena && window.__game.arena.scene) {
      resolve(window.__game);
      return;
    }
    const t = setInterval(() => {
      if (window.__game && window.__game.arena && window.__game.arena.scene) {
        clearInterval(t);
        resolve(window.__game);
      }
    }, 500);
    setTimeout(() => { clearInterval(t); resolve(window.__game || null); }, 15000);
  });
}

async function boot() {
  const game = await waitForGame();
  if (!game) {
    console.warn('[WHIntegration] no game found; systems idle');
    window.WHIntegration = WHIntegration;
    return;
  }
  const scene = game.arena.scene;
  const camera = game.arena.camera;

  // 1. Physics (cannon-es): arena props + debris + KO tumble.
  await tryInit('physics', './physics.js', async (m) => {
    const p = new m.WHPhysics();
    await p.init(scene);
    // Register knockable arena props (meshes flagged by stages).
    scene.traverse((o) => { if (o.isMesh && o.userData.whProp) p.addProp(o, o.userData.whProp); });
    return p;
  });

  // 2. Hit detection precision layer (three-mesh-bvh, verify mode).
  await tryInit('hitdetect', './hitdetect.js', async (m) => {
    const h = new m.WHHitDetect();
    await h.init();
    return h;
  });

  // 3. Runtime jiggle (spring bones).
  const springs = await tryInit('springbones', './springbones.js', async (m) => {
    return new m.WHSpringBones();
  });

  // 4. Particle hit FX (three-nebula). Replaces _spawnImpact when present.
  await tryInit('hitfx', './hitfx-nebula.js', async (m) => {
    const fx = new m.WHHitFX();
    await fx.init(scene, game.arena.renderer);
    return fx;
  });

  // 4b. Effekseer particle runtime (1.80.7, MIT). Premium hit + Soul Urge
  // FX drawn over the scene from real .efkefc effect files. A failed
  // load leaves everything on the nebula fallback — combat unaffected.
  const efx = await tryInit('efx', './fx/particles.js', async (m) => {
    const fx = new m.WHEffekseerFX();
    await fx.init(game.arena.renderer);
    return fx.ready ? fx : null;
  });

  // 4c. Unified hit effects: Effekseer primary, nebula fallback
  // (dust/surge + Effekseer-unavailable cases).
  const hits = await tryInit('hits', './fx/hit-effects.js', async (m) => {
    const h = new m.WHHitEffects();
    await h.init(efx, WHIntegration.systems.hitfx || null);
    return h;
  });

  // 4d. Soul Urge visual cues (Effekseer ignition/aura/smash).
  const surgefx = await tryInit('surgefx', './fx/soulurge-fx.js', async (m) => {
    const s = new m.WHSoulUrgeFX();
    await s.init(efx);
    return s;
  });

  // 5. 3D labels (troika).
  await tryInit('labels', './labels3d.js', async (m) => {
    const l = new m.WHLabels();
    await l.init(scene);
    return l;
  });

  // 6. Camera director (cutscenes + photo mode). Needs the canvas.
  await tryInit('camdirector', './camdirector.js', async (m) => {
    const d = new m.WHCamDirector();
    const canvas = game.arena.renderer && game.arena.renderer.domElement;
    await d.init(camera, canvas || document.body);
    return d;
  });

  // 7. Lip-sync player (mouth cues from the voice lane).
  await tryInit('lipsync', './lipsync-player.js', async (m) => {
    return new m.WHLipSyncPlayer();
  });

  // 8. Chrono grapple joint-constraint subsystem (Track 4, 2026-10-23):
  //    deterministic joint locks / submission chains / torque nodes for
  //    the ground game. Sleeps while idle (zero cost). The fight state
  //    machine calls grapple.stepCombat(fixedDt, inputs) on the combat
  //    tick; this loop only runs the cosmetic joint solve for the servo
  //    layer via getServoTargets() → PhysicsServo PD controllers.
  await tryInit('grapple', './chrono-grapple.js', async (m) => {
    return new m.ChronoGrapple();
  });

  WHIntegration.ready = true;
  window.WHIntegration = WHIntegration;

  // ---- per-frame updates (own rAF; never touches the combat step) ----
  let last = performance.now();
  const seenFighters = new WeakSet();
  function frame(now) {
    requestAnimationFrame(frame);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const S = WHIntegration.systems;
    try {
      if (S.physics) S.physics.step(dt);
      if (S.grapple) S.grapple.update(dt);
      if (S.hitfx) S.hitfx.update(dt);
      if (S.efx) S.efx.tick(dt);
      if (S.hits) S.hits.update(dt);
      if (S.surgefx) S.surgefx.update(dt);
      // Attach spring chains + nameplates to newly spawned fighters.
      for (const key of ['p1', 'p2']) {
        const f = game[key];
        if (f && f.root && !seenFighters.has(f)) {
          seenFighters.add(f);
          if (S.springbones && springs) {
            const n = S.springbones.autoDiscover(f.root);
            if (n) console.info(`[WHIntegration] ${n} spring chain(s) on ${f.char && f.char.id}`);
          }
          if (S.labels && f.char) {
            S.labels.nameplate(f.root, f.char.name || f.char.id || key.toUpperCase());
          }
        }
      }
      if (S.springbones) S.springbones.update(dt, now / 1000);
      if (S.labels) S.labels.update(dt, camera);
      if (S.camdirector) S.camdirector.update(dt);
      if (S.lipsync) S.lipsync.update();
    } catch (e) {
      console.warn('[WHIntegration] frame error (non-fatal):', e);
    }
  }
  requestAnimationFrame(frame);

  // ---- combat hooks: patch Game.prototype (no game.js edit needed) ----
  // _spawnImpact: nebula FX + physical debris replace/augment the sprite burst.
  // _resolveCombat: after a hit lands, run the BVH verify + damage numbers.
  try {
    const gameMod = await import('./game.js');
    const Gp = gameMod.Game && gameMod.Game.prototype;
    if (Gp) {
      if (Gp._spawnImpact && !Gp._whPatchedImpact) {
        const orig = Gp._spawnImpact;
        Gp._whPatchedImpact = true;
        // Layering (tool-unification law): the game's HitFX (game/js/hitfx.js)
        // owns the hit spark / ring / flash / hitstop presentation.
        // Effekseer (WHHitEffects, game/js/fx/hit-effects.js) ADDS premium
        // GPU particle richness — impact/heavy/ko/block through real
        // .efkefc effects, nebula fallback for dust/surge and for any
        // case where Effekseer is unavailable. Never replaces.
        Gp._spawnImpact = function (x, y, z, color, scale) {
          const r = orig.call(this, x, y, z, color, scale);
          const S = WHIntegration.systems;
          try {
            if (S.hits) S.hits.spawn(x, y, z, color, scale);
            else if (S.hitfx && scale >= 0.9) S.hitfx.spawn(x, y, z, color, scale);
            if (S.physics) {
              S.physics.debris({ x, y, z }, { color, count: 5, power: 4 + scale * 2 });
              S.physics.blast({ x, y, z }, { radius: 1.6, power: 3 * scale });
            }
          } catch (e) { console.warn('[WHIntegration] impact hook', e); }
          return r;
        };
      }
      if (Gp._resolveCombat && !Gp._whPatchedCombat) {
        const origC = Gp._resolveCombat;
        Gp._whPatchedCombat = true;
        Gp._resolveCombat = function (attacker, defender) {
          const hpBefore = defender.hp;
          const r = origC.call(this, attacker, defender);
          try {
            const S = WHIntegration.systems;
            const dealt = Math.max(0, hpBefore - defender.hp);
            if (dealt > 0 || defender.hp <= 0) {
              if (S.hitdetect) {
                S.hitdetect.verify(attacker.root, defender.root, true, null, {
                  move: attacker.attackName, dealt,
                });
              }
              if (S.labels && dealt > 0) {
                const p = defender.root.position;
                S.labels.damageNumber(p.x, p.y + 1.8, p.z, Math.round(dealt));
              }
              if (defender.hp <= 0 && S.physics && defender.root) {
                S.physics.koTumble(defender.root);
              }
              // (KO hit-FX already fired through the _spawnImpact patch above.)
            }
          } catch (e) { console.warn('[WHIntegration] combat hook', e); }
          return r;
        };
      }
      console.info('[WHIntegration] Game.prototype hooks installed');

      // ---- Soul Urge FX hooks (prototype patches — no soulurge.js /
      // fighter.js edits). Ignition burst + aura loop on activate,
      // aura off on expire, cinematic burst on Urge Smash, wind on
      // Urge Dash.
      try {
        const suMod = await import('./soulurge.js');
        const Sp = suMod.SoulUrge && suMod.SoulUrge.prototype;
        if (Sp && !Sp._whFxPatched) {
          Sp._whFxPatched = true;
          const oAct = Sp.activate, oExp = Sp._expire, oSmash = Sp.urgeSmashHit;
          Sp.activate = function (f, id, pips, time) {
            const r = oAct.call(this, f, id, pips, time);
            try {
              const S = WHIntegration.systems;
              if (r && S.surgefx && f) S.surgefx.onActivate(f);
            } catch (e) {}
            return r;
          };
          Sp._expire = function (f, id) {
            try {
              const S = WHIntegration.systems;
              if (S.surgefx && f) S.surgefx.onExpire(f);
            } catch (e) {}
            return oExp.call(this, f, id);
          };
          Sp.urgeSmashHit = function (attacker, hb) {
            try {
              const S = WHIntegration.systems;
              if (S.surgefx && attacker) S.surgefx.onSmash(attacker);
            } catch (e) {}
            return oSmash.call(this, attacker, hb);
          };
          console.info('[WHIntegration] SoulUrge FX hooks installed');
        }
        const fMod = await import('./fighter.js');
        const Fp = fMod.Fighter && fMod.Fighter.prototype;
        if (Fp && Fp.tryUrgeDash && !Fp._whFxDashPatched) {
          Fp._whFxDashPatched = true;
          const oDash = Fp.tryUrgeDash;
          Fp.tryUrgeDash = function () {
            const r = oDash.call(this);
            try {
              const S = WHIntegration.systems;
              if (r && S.surgefx) S.surgefx.onDash(this);
            } catch (e) {}
            return r;
          };
          console.info('[WHIntegration] Fighter urge-dash FX hook installed');
        }
      } catch (e) {
        console.warn('[WHIntegration] soulurge FX hooks:', e);
      }
    }
  } catch (e) {
    console.warn('[WHIntegration] could not patch Game.prototype:', e);
  }
}

window.WHIntegration = WHIntegration;
boot();
