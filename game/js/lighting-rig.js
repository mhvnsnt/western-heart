/* ============================================================
   WESTERN HEART — unified stage + character lighting rig
   (worker 27, 2026-10-22)

   TEARDOWN AUDIT (what the newest games do — adapted, not copied):
   - TEKKEN 7 (UE4): every stage streams TWO lighting units —
     `light` (dynamic lighting info) + `lightstatic` (baked lightmaps /
     Lightmass GI). Source: teardown/tekken7/tekkenmods-docs/.../Stages.
     UE4 lighting modes: static = fully baked, stationary = partially
     baked, movable = fully dynamic. Characters are dynamic meshes lit by
     movable lights + volumetric lightmap/SH probes for indirect.
     Our mapping: hemi/sky/fog = the "baked" ambient stand-in
     (lightstatic); key/rim/fill directionals + accent points =
     the dynamic rig (light). No runtime lightmap baking in a browser —
     the hemisphere + gradient sky carries the baked feel.
   - TEKKEN 8 (UE5): does NOT use Lumen/Nanite (confirmed by Digital
     Foundry + dsogaming Lumen on/off tests) — ships baked-in stage
     lighting + dynamic character lights at a strict 60fps. Same
     split as T7, which validates the approach for us: bake the mood
     into ambient/sky, spend dynamic lights on fighters.
   - STREET FIGHTER V (UE4 + Geomerics Enlighten): real-time GI via
     spherical-harmonic probes — Enlighten's SH probes shade MOVING
     objects (fighters) with indirect light at runtime (80.lv, 2016).
     Our mapping: the per-fighter character rig below (key + soul
     light parented to the fighter) is the SH-probe equivalent —
     indirect-ish light that follows the fighter. SFV also pushes
     characters brighter than the background with a strong rim so they
     "pop" — we do the same via rimBoost + charKey.
   - DEAD OR ALIVE 6 (new engine, not Soft Engine): "physical lighting"
     — precision in how light reflects / creates shadows (Team Ninja,
     OBORO update). Our mapping: keep PBR materials, keep the
     shadow-casting key, don't flatten with ambient.

   BIBLE SERVICE (docs/VISUAL-ART-DIRECTION-BIBLE.md):
   - "Luminous darkness": deep blacks with light BLOOMING out of them —
     the UnrealBloomPass in scene.js is the carrier; per-stage grade
     hooks (exposure/bloom) tune it per land.
   - Grey's law: "Fighters, sigils, UI elements are luminous SOURCES,
     not lit objects." -> soul-glow baseline on every fighter's
     auraLight + subtle soul-tinted emissive on their materials.
   - Thangka color law + Malakor violet family + per-land palettes drive
     every default color below. No pure RGB primaries; max 3 saturated
     hues per composition.
   - Soul light behaviors (§5c): each soul gets color + light behavior,
     honored in fighter.js's aura update via _soulBehavior.

   PERFORMANCE (mobile is the target — user plays on phone):
   - Forward renderer cost scales with total light count in the shader.
     Budget: hemi(1) + dir(3) + accents(<=6) + charKey(2) + soul(2).
     The charKey is ONE PointLight per fighter, no shadows. The soul
     glow reuses the EXISTING auraLight (idle baseline instead of 0) —
     zero new lights for it. Emissive costs nothing extra (already in
     the standard material shader).
   - Motes: 1 draw call, 0 lights, additive points.
   ============================================================ */
import * as THREE from 'three';

/* Soul light table — bible §5c. glow = idle auraLight baseline
   (candela-ish, matches the 0..14 surge scale in fighter.js).
   behavior drives the per-frame modulation in fighter.js. */
export const SOUL_LIGHT = {
  rin:   { color: '#F0F4FF', behavior: 'steady',   glow: 2.0 }, // cold, sourceless
  byou:  { color: '#9DBE3C', behavior: 'flicker',  glow: 1.6 }, // flickering, wrong
  tou:   { color: '#A31621', behavior: 'low',      glow: 2.4, lowY: 0.55 }, // low, predatory
  sha:   { color: '#E0A93E', behavior: 'shimmer',  glow: 2.2 }, // shimmering heat
  kai:   { color: '#0E6B6B', behavior: 'tidal',    glow: 2.0 }, // rolling, tidal
  jin:   { color: '#C8D0DC', behavior: 'steady',   glow: 1.8 }, // hard edge highlight
  retsu: { color: '#E85D1F', behavior: 'pulse',    glow: 2.6 }, // explosive, radial
  zen:   { color: '#050508', behavior: 'steady',   glow: 0.0 }, // absence of light
  gyou:  { color: '#FFFFFF', behavior: 'rainbow',  glow: 2.2 }, // streaking, never still
};

/* Default stage-rig values: everything a stage gets when it doesn't
   declare its own `lighting.rig` block. */
export const DEFAULT_RIG = {
  charKey: ['#ffe9d2', 20, 7],  // color, intensity, distance (r160 physical)
  charKeyPos: [0, 2.7, 2.3],    // front-top of the fighter, follows them
  soulEmissive: 0.12,           // soul-tinted emissive on fighter materials
  rimBoost: 1.0,                // SFV-style rim pop multiplier
  exposure: 1.45, bloom: null,  // null = keep scene default (mobile-aware)
  motes: { color: '#8A6FB8', count: 160, size: 0.055, opacity: 0.5,
           area: [26, 7, 26] }, // Nostalgia Haze default — subtle everywhere
};

/* Resolve which soul-light entry a fighter gets. The nine souls carry
   their soul id as char.id; everyone else falls back to their surge
   color (trim color when no surge block). */
export function resolveSoulLight(fighter) {
  const id = fighter.char && fighter.char.id;
  if (id && SOUL_LIGHT[id]) return { id, ...SOUL_LIGHT[id] };
  const c = fighter.char && fighter.char.surge ? fighter.char.surge.color
    : (fighter.char && fighter.char.colors ? fighter.char.colors.trim : 0xffffff);
  return { id: null, color: '#' + new THREE.Color(c).getHexString(),
           behavior: 'steady', glow: 1.6 };
}

/* ---------------- stage rig ----------------
   Builds the dynamic half of the T7 split (light) on top of the
   baked-ambient half (lightstatic = hemi + sky + fog, already in
   buildBase). Returns { updaters } to merge into the builder's list. */
export function buildStageLightRig(g, def, api) {
  const updaters = [];
  const L = def.lighting;
  const rig = { ...DEFAULT_RIG, ...(L.rig || {}) };
  const _hex = (c) => new THREE.Color(c);

  // Baked-ambient stand-in (T7 lightstatic): hemisphere sky/ground bounce.
  g.add(new THREE.HemisphereLight(_hex(L.hemi[0]), _hex(L.hemi[1]), L.hemi[2]));

  // Key: the one shadow-casting directional (T7 movable key light).
  const sun = new THREE.DirectionalLight(_hex(L.sun[0]), L.sun[1]);
  sun.position.set(...L.sun[2]); sun.castShadow = true;
  const sm = api.isMobile ? 1024 : 2048;
  sun.shadow.mapSize.set(sm, sm);
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 50;
  sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
  sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
  sun.shadow.bias = -0.0006; g.add(sun);

  // Rim: SFV-style separation rim — land-palette tinted, boosted so the
  // fighters read against any background (bible: rim-lit by land-palette).
  const rim = new THREE.DirectionalLight(_hex(L.rim[0]), L.rim[1] * rig.rimBoost);
  rim.position.set(...L.rim[2]); g.add(rim);

  // Fill: soft frontal fill from the camera side.
  const fill = new THREE.DirectionalLight(_hex(L.fill[0]), L.fill[1]);
  fill.position.set(...L.fill[2]); g.add(fill);

  // Atmosphere motes — bible §8.4 "darkness is a material": nebula wisps,
  // soul-motes, pollen-light, dust in lantern beams. 1 draw call, 0 lights.
  const motes = buildMotes(rig.motes, api.isMobile);
  if (motes) { g.add(motes.points); updaters.push(motes.update); }

  return { updaters, rig };
}

/* Floating dust/soul-motes/cinders. Additive points drifting upward. */
function buildMotes(cfg, isMobile) {
  const count = Math.min(cfg.count || 160, isMobile ? 110 : 400);
  if (count <= 0) return null;
  const [ax, ay, az] = cfg.area || [26, 7, 26];
  const pos = new Float32Array(count * 3);
  const seed = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (Math.random() - 0.5) * ax;
    pos[i * 3 + 1] = Math.random() * ay;
    pos[i * 3 + 2] = (Math.random() - 0.5) * az;
    seed[i] = Math.random() * 100;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({
    color: new THREE.Color(cfg.color || '#8A6FB8'),
    size: cfg.size || 0.055, transparent: true,
    opacity: cfg.opacity ?? 0.5, depthWrite: false,
    blending: THREE.AdditiveBlending, sizeAttenuation: true,
  });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  const update = (dt) => {
    const p = geo.attributes.position.array;
    for (let i = 0; i < count; i++) {
      p[i * 3 + 1] += dt * 0.12;                    // slow rise
      p[i * 3] += Math.sin(seed[i] + p[i * 3 + 1]) * dt * 0.05; // sway
      if (p[i * 3 + 1] > ay) p[i * 3 + 1] = 0;      // wrap
    }
    geo.attributes.position.needsUpdate = true;
  };
  return { points, update };
}

/* ---------------- character rig ----------------
   SFV/T7 character-vs-stage separation: each fighter carries their own
   key light (follows them — parented to root, no per-frame cost) plus
   their soul glow (the existing auraLight at an idle baseline instead
   of 0 — zero new lights) plus soul-tinted emissive (Grey's law:
   fighters are luminous sources). Fail-silent: never blocks a match. */
export function attachCharacterRig(fighter, stageDef) {
  try {
    const rig = { ...DEFAULT_RIG, ...((stageDef.lighting && stageDef.lighting.rig) || {}) };
    const soul = resolveSoulLight(fighter);

    // Remember the surge color (auraLight was built with it), then hand
    // the light to the soul color for the idle baseline.
    const surgeHex = fighter.auraLight ? fighter.auraLight.color.getHex() : 0xffffff;
    fighter._surgeColorHex = surgeHex;
    fighter._soulColorHex = new THREE.Color(soul.color).getHex();
    fighter._soulGlowBase = soul.glow;
    fighter._soulBehavior = soul.behavior;
    if (fighter.auraLight) {
      fighter.auraLight.color.set(soul.color);
      if (soul.lowY) fighter.auraLight.position.y = soul.lowY; // TOU: low, predatory
    }

    // Character key — warm front-top light that travels with the fighter.
    const [kc, ki, kd] = rig.charKey;
    const key = new THREE.PointLight(new THREE.Color(kc), ki, kd, 2);
    key.position.set(...rig.charKeyPos);
    fighter.root.add(key);
    fighter._charKey = key;

    // Inner luminosity: whisper of soul color in the materials so the
    // bloom pass catches the fighter (luminous darkness). Skips anything
    // already emissive; mirror matches share materials harmlessly.
    if (soul.id && rig.soulEmissive > 0) {
      const sc = new THREE.Color(soul.color);
      fighter.root.traverse((o) => {
        if (!o.isMesh) return;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of mats) {
          if (!m || !m.isMeshStandardMaterial) continue;
          if ((m.emissiveIntensity || 0) > 0.05) continue;
          m.emissive = m.emissive || new THREE.Color(0x000000);
          m.emissive.copy(sc);
          m.emissiveIntensity = rig.soulEmissive;
        }
      });
    }
    return true;
  } catch (e) {
    console.warn('[WH] attachCharacterRig failed (non-fatal):', e.message);
    return false;
  }
}

/* ---------------- color grade ----------------
   Per-stage grade hooks: tone-mapping exposure + bloom strength.
   Called by Arena.setStage — stage swaps are discrete, so set directly. */
export function applyGrade(arena, def) {
  try {
    const rig = { ...DEFAULT_RIG, ...((def.lighting && def.lighting.rig) || {}) };
    const grade = (def.lighting && def.lighting.grade) || {};
    arena.renderer.toneMappingExposure = grade.exposure ?? rig.exposure ?? 1.45;
    if (arena.bloom) {
      arena.bloom.strength = grade.bloom ?? rig.bloom
        ?? (arena.isMobile ? 0.6 : 0.85);
    }
  } catch (e) {
    console.warn('[WH] applyGrade failed (non-fatal):', e.message);
  }
}

/* Light budget ledger — the most lights any frame should carry.
   stageBase(4: hemi+3dir) + accents(<=6) + charKeys(2) + soul(2) = 14. */
export const LIGHT_BUDGET = {
  stageBase: 4, accentMax: 6, charKey: 2, soul: 2,
  total: 14,
  countStagePointLights(group) {
    let n = 0;
    group.traverse((o) => { if (o.isPointLight) n++; });
    return n;
  },
};
