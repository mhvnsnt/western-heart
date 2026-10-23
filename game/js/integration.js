/* ============================================================
   WESTERN HEART — integration boot (worker 22, 2026-10-22)
   Wires the newly-vendored open-source systems into the game:

     physics.js      cannon-es          rigid bodies, debris, KO tumble
     hitdetect.js    three-mesh-bvh     BVH precision hit layer (verify)
     springbones.js  WH-original       runtime jiggle (verlet chains)
     hitfx-nebula.js three-nebula       JSON particle hit effects
     labels3d.js     troika-three-text  3D nameplates / damage numbers
     camdirector.js  camera-controls    cutscene + photo-mode camera
     lipsync-player.js WH-original      mouth-cue playback (voice lane)
     story/cinematic-director.js WH-original + inkjs   keyframe sequences,
      trigger graph (flags/zones/timers/dialogue), ink narrative branches
     story/brawler-camera.js   WH-original   multi-target brawler camera
      (N-target frustum fit on the PR #851 CameraRig math; opt-in)
     story/navmesh.js          WH-original + yuka   NavMesh pathfinding,
      grunt pursue/flank/swarm (Yuka lane: pathfinding only — combat
      state machines belong to the other Yuka track, issue #866)
     story/dialogue-fsm.js     WH-original   combat-reactive banter FSM
      (damage/HP/wave events; LLM/Inworld behind an optional seam)

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

  // 8. Cinematic director (Track 7): keyframe sequences + trigger
  // graph + ink narrative for story mode / Heart and Mind Within.
  await tryInit('cinematic', './story/cinematic-director.js', async (m) => {
    const d = new m.WHCinematicDirector();
    d.onDialogue = (prompt) => {
      window.dispatchEvent(new CustomEvent('wh-dialogue', { detail: prompt }));
    };
    return d;
  });

  // 9. Brawler camera (Track 7): multi-target N-fighter framing built
  // on the PR #851 CameraRig math. Opt-in — the fight camera keeps
  // running unless enable() is called (Heart and Mind Within
  // phase-2 density, cutscene push-ins via setFraming).
  await tryInit('brawlerCam', './story/brawler-camera.js', async (m) => {
    const bc = new m.WHBrawlerCamera().attach(camera);
    bc.setTargets([]);
    bc.setTargetProvider = (fn) => { bc._provider = fn; };
    // Default provider: the two fighters + any heartmind grunt squad.
    bc.setTargetProvider(() => {
      const ts = [];
      for (const key of ['p1', 'p2']) {
        const f = game[key];
        if (f && f.root) ts.push(m.WHBrawlerCamera.targetOf(f.root, key === 'p1' ? 2 : 1.5));
      }
      const hm = window.__heartmind;
      if (hm && hm.squad && hm.squad.grunts) {
        for (const g of hm.squad.grunts) ts.push({ pos: g.pos, weight: 1 });
      }
      return ts;
    });
    // THREE.Raycaster wall clamp against arena collidables (opt-in:
    // heartmind sets the collidable list for tight spaces).
    try {
      const { Raycaster, Vector3 } = await import('three');
      const ray = new Raycaster();
      bc.setObstacleTester((origin, dir, maxDist) => {
        const list = bc._collidables;
        if (!list || !list.length) return null;
        ray.set(new Vector3(origin.x, origin.y, origin.z), new Vector3(dir.x, dir.y, dir.z));
        ray.far = maxDist;
        const hits = ray.intersectObjects(list, false);
        return hits.length ? hits[0].distance : null;
      });
      void Vector3;
    } catch { /* raycast clamp unavailable; camera still frames */ }
    return bc;
  });

  // 10. NavMesh pathfinding (Track 7, Yuka lane: pathfinding only).
  await tryInit('navmesh', './story/navmesh.js', async (m) => {
    const z = new m.WHNavZoneSet();
    const api = {
      zones: z,
      /* Build a walkable zone from the stage's floor rects.
         Heart and Mind Within phase-2 calls this per stage. */
      async buildStageZone(zoneId, rects) {
        const nm = new m.WHNavMesh();
        await nm.init();
        nm.buildFromRects(rects);
        z.addZone(zoneId, nm);
        return nm;
      },
      makeSquad: (zoneId, opts) => {
        const nm = z.zones.get(zoneId);
        return nm ? new m.WHSquad(nm, opts) : null;
      },
    };
    return api;
  });

  // 11. Combat-reactive dialogue FSM (Track 7). Lines come from the
  // game's canon banter data; the FSM only selects. Emits through
  // onLine + a 'wh-dialogue-line' CustomEvent the UI binds to.
  await tryInit('dialogue', './story/dialogue-fsm.js', async (m) => {
    const fsm = new m.WHDialogueFSM();
    fsm.onLine = (rec) => {
      window.dispatchEvent(new CustomEvent('wh-dialogue-line', { detail: rec }));
    };
    try {
      const banter = await import('./versus-banter.js');
      if (banter.VERSUS_BANTER) {
        // Seed from existing canon banter; per-pair wiring happens
        // when a fight's pair key is known (see bindFight below).
        fsm._banterTable = banter.VERSUS_BANTER;
      }
    } catch { /* banter data optional */ }
    fsm.bindFight = (p1Id, p2Id) => {
      fsm.resetFight();
      if (fsm._banterTable) {
        const key = [p1Id, p2Id].sort().join('|');
        fsm.registerBeats(fsm._banterTable, 'fightStart', key);
      }
    };
    return fsm;
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
      if (S.hitfx) S.hitfx.update(dt);
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
      if (S.cinematic) S.cinematic.update(dt, {
        playerPos: game.p1 && game.p1.root ? game.p1.root.position : undefined,
      });
      if (S.brawlerCam && S.brawlerCam.enabled) {
        if (S.brawlerCam._provider) {
          try { S.brawlerCam.setTargets(S.brawlerCam._provider()); } catch { /* keep last */ }
        }
        S.brawlerCam.update(dt);
      }
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
        // owns the hit spark / ring / flash / hitstop presentation. Nebula
        // ADDS GPU particle richness on top — light hits stay with HitFX
        // alone; heavy/KO get the extra nebula burst + ring. Never replaces.
        Gp._spawnImpact = function (x, y, z, color, scale) {
          const r = orig.call(this, x, y, z, color, scale);
          const S = WHIntegration.systems;
          try {
            if (S.hitfx && scale >= 0.9) S.hitfx.spawn(x, y, z, color, scale);
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
    }
  } catch (e) {
    console.warn('[WHIntegration] could not patch Game.prototype:', e);
  }
}

window.WHIntegration = WHIntegration;
boot();
