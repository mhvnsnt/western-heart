// DNA v2: the engine-agnostic character recipe. Superset of Bannon DNA v1
// (docs/DNA_SCHEMA.md in mhvnsnt/Bannon) so Bannon saves migrate losslessly.
export const DNA_VERSION = 2;

// Body sliders. range is the slider range; 0 = model as authored.
// kind: "morph" -> procedural/authored morph target, "bone" -> bone scale.
export const SLIDERS = {
  height:   { kind: 'bone',  range: [-0.25, 0.25], group: 'frame' },
  armLen:   { kind: 'bone',  range: [-0.2, 0.2],   group: 'frame' },
  legLen:   { kind: 'bone',  range: [-0.2, 0.2],   group: 'frame' },
  torsoLen: { kind: 'bone',  range: [-0.2, 0.2],   group: 'frame' },
  shoulders:{ kind: 'bone',  range: [-0.3, 0.4],   group: 'frame' },
  headSize: { kind: 'bone',  range: [-0.2, 0.2],   group: 'frame' },
  weight:   { kind: 'morph', range: [-0.5, 1.5],   group: 'mass' },  // whole-body fat
  muscle:   { kind: 'morph', range: [-0.5, 1.0],   group: 'mass' },
  belly:    { kind: 'morph', range: [-0.5, 2.0],   group: 'mass' },
  chest:    { kind: 'morph', range: [-0.5, 2.0],   group: 'mass' },  // pecs / bust
  glutes:   { kind: 'morph', range: [-0.5, 2.0],   group: 'mass' },
  hips:     { kind: 'morph', range: [-0.5, 1.5],   group: 'mass' },
  thighs:   { kind: 'morph', range: [-0.5, 2.0],   group: 'mass' },
  arms:     { kind: 'morph', range: [-0.5, 1.5],   group: 'mass' },
  neck:     { kind: 'morph', range: [-0.5, 1.5],   group: 'mass' },
};

export const BODY_TYPES = {
  default:  {},
  heavy:    { weight: 1.0, belly: 1.4, thighs: 0.8, arms: 0.6, neck: 0.8, chest: 0.6 },
  muscular: { muscle: 0.9, shoulders: 0.25, arms: 0.5, chest: 0.5, neck: 0.5 },
  female:   { chest: 1.2, hips: 0.9, glutes: 1.0, thighs: 0.6, shoulders: -0.15, neck: -0.3 },
  femaleCurvy: { chest: 1.6, hips: 1.3, glutes: 1.6, thighs: 1.2, weight: 0.3 },
};

export function clampSlider(key, v) {
  const s = SLIDERS[key];
  if (!s) throw new Error(`unknown slider ${key}`);
  return Math.min(s.range[1], Math.max(s.range[0], Number(v) || 0));
}

export function makeDNA({ name = 'CUSTOM', base = 'model', model = null, bodyType = 'default', sliders = {}, attire = {}, physics = {} } = {}) {
  const s = { ...(BODY_TYPES[bodyType] || {}), ...sliders };
  const out = {};
  for (const k of Object.keys(s)) out[k] = clampSlider(k, s[k]);
  return { v: DNA_VERSION, name, base, model, bodyType, sliders: out, attire: { ...attire }, physics: { enabled: true, ...physics } };
}

// Bannon DNA v1 -> v2. v1 morphs/boneScale were multipliers around 1.0.
export function migrate(dna) {
  if (!dna || dna.v === DNA_VERSION) return dna;
  if (dna.v !== 1) throw new Error(`unsupported DNA version ${dna.v}`);
  const sliders = {};
  const all = { ...(dna.morphs || {}), ...(dna.boneScale || {}) };
  const alias = { bust: 'chest', muscularity: 'muscle', neckW: 'neck', waist: 'belly' };
  for (const [k, v] of Object.entries(all)) {
    const key = alias[k] || k;
    if (SLIDERS[key]) sliders[key] = clampSlider(key, v - 1);
  }
  const attire = {};
  if (dna.spec?.mask) attire.face = { id: dna.spec.mask };
  return makeDNA({ name: dna.name, base: dna.base, sliders, attire });
}

export function toJSON(dna) { return JSON.stringify(dna); }
export function fromJSON(s) { return migrate(JSON.parse(s)); }
