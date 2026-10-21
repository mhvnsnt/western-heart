// rigpose.js — Rig & Pose Studio model layer for the Creation Suite.
//
// Pure state for the suite's rig/pose mode: the owner edits bones here,
// this module serializes the edit into the `rig` section of the attire's
// customization.json (schema: customization/CUSTOMIZATION-JSON-SCHEMA.md
// § Rig & Pose). The bake stage (customization/tools/rigpose_bake.py)
// replays that section deterministically — what the owner saves is what
// the game gets, and reload reproduces the same state.
//
// Input skeleton data comes from tools/rig-pose-studio/glb_inspect.py
// reports (joint sets, rest rotations, world positions) — the suite never
// guesses a skeleton; it edits the measured one.
//
// Integration point: ui/profile.js's toCustomizationJson() merges
// `rig: toRigSection(rigPoseState)` when a rig/pose state exists; absence
// of the section is an exact no-op for the rest of the suite.

export const ZERO_OFFSET = Object.freeze({
  pos: [0, 0, 0], rot_deg: [0, 0, 0], scale: [1, 1, 1],
});

const clone = (v) => JSON.parse(JSON.stringify(v));
const isZeroOffset = (o) =>
  o.pos.every((v) => v === 0) && o.rot_deg.every((v) => v === 0) &&
  o.scale.every((v) => v === 1);

export function createRigPoseState(inspect = null, savedRig = null) {
  const bones = new Map();
  const jointNames = new Set();
  for (const skin of inspect?.skins ?? []) {
    for (const row of skin.joint_rows ?? []) jointNames.add(row.name);
  }
  for (const skin of inspect?.skins ?? []) {
    for (const row of skin.joint_rows ?? []) {
      bones.set(row.name, {
        name: row.name,
        isJoint: true,
        restRotDeg: row.rest_rot_deg ?? 0,
        world: row.world ?? null,
        offset: clone(ZERO_OFFSET),
        visible: true,
      });
    }
  }
  const state = {
    bones,
    frame: null,      // {translate:[x,y,z], rot_deg:[x,y,z]} model-frame fix
    added: [],        // [{name, parent, head, tail}]
    removed: [],      // [name]
    strokes: [],      // weight brush strokes, in paint order
    meshVisibility: new Map(), // mesh/node name -> bool (only non-default)
    pose: new Map(),  // bone name -> {rot_deg, pos}
  };
  if (savedRig) applyRigSection(state, savedRig);
  return state;
}

export function applyRigSection(state, rig) {
  if (rig.frame) state.frame = clone(rig.frame);
  for (const [name, spec] of Object.entries(rig.bones ?? {})) {
    const b = state.bones.get(name) ??
      { name, isJoint: true, restRotDeg: 0, world: null, offset: clone(ZERO_OFFSET), visible: true };
    if (spec.offset) b.offset = { ...clone(ZERO_OFFSET), ...clone(spec.offset) };
    if (spec.visible === false) b.visible = false;
    state.bones.set(name, b);
  }
  for (const a of rig.add_bones ?? []) state.added.push(clone(a));
  for (const r of rig.remove_bones ?? []) state.removed.push(r);
  for (const s of rig.weights ?? []) state.strokes.push(clone(s));
  for (const [name, v] of Object.entries(rig.visibility ?? {})) {
    state.meshVisibility.set(name, v);
  }
  for (const [name, p] of Object.entries(rig.pose ?? {})) {
    state.pose.set(name, clone(p));
  }
  return state;
}

// --- owner operations (one function per control in the panel) ---

export function setFrame(state, frame) {
  state.frame = clone(frame);
  return state;
}

export function setBoneOffset(state, name, partial) {
  const b = state.bones.get(name);
  if (!b) throw new Error(`unknown bone: ${name}`);
  Object.assign(b.offset, clone(partial));
  return b;
}

export function setBoneVisible(state, name, visible) {
  const b = state.bones.get(name);
  if (!b) throw new Error(`unknown bone: ${name}`);
  b.visible = !!visible;
  return b;
}

export function addBone(state, spec) {
  if (state.bones.has(spec.name) || state.added.some((a) => a.name === spec.name)) {
    throw new Error(`bone already exists: ${spec.name}`);
  }
  if (!state.bones.has(spec.parent) && !state.added.some((a) => a.name === spec.parent)) {
    throw new Error(`unknown parent bone: ${spec.parent}`);
  }
  state.added.push(clone(spec));
  state.bones.set(spec.name, {
    name: spec.name, isJoint: true, restRotDeg: 0, world: null,
    offset: clone(ZERO_OFFSET), visible: true, added: true,
  });
  return state;
}

export function removeBone(state, name) {
  if (!state.bones.has(name)) throw new Error(`unknown bone: ${name}`);
  if (!state.removed.includes(name)) state.removed.push(name);
  return state;
}

export function addWeightStroke(state, stroke) {
  if (!state.bones.has(stroke.bone)) throw new Error(`unknown bone: ${stroke.bone}`);
  state.strokes.push({
    bone: stroke.bone,
    center: [...stroke.center],
    radius: stroke.radius,
    strength: stroke.strength ?? 1,
    mode: stroke.mode ?? 'add',
  });
  return state;
}

export function setMeshVisibility(state, name, visible) {
  state.meshVisibility.set(name, !!visible);
  return state;
}

export function setPose(state, name, entry) {
  if (!state.bones.has(name)) throw new Error(`unknown bone: ${name}`);
  state.pose.set(name, clone(entry));
  return state;
}

// --- serialization: only non-default edits are saved ---

export function toRigSection(state) {
  const rig = {};
  if (state.frame) rig.frame = clone(state.frame);
  const bones = {};
  for (const b of state.bones.values()) {
    const entry = {};
    if (!isZeroOffset(b.offset)) entry.offset = clone(b.offset);
    if (b.visible === false) entry.visible = false;
    if (Object.keys(entry).length) bones[b.name] = entry;
  }
  if (Object.keys(bones).length) rig.bones = bones;
  if (state.added.length) rig.add_bones = clone(state.added);
  if (state.removed.length) rig.remove_bones = [...state.removed];
  if (state.strokes.length) rig.weights = clone(state.strokes);
  const vis = Object.fromEntries(state.meshVisibility);
  if (Object.keys(vis).length) rig.visibility = vis;
  if (state.pose.size) rig.pose = Object.fromEntries([...state.pose].map(([k, v]) => [k, clone(v)]));
  return Object.keys(rig).length ? rig : null;
}

export function rigPoseSummary(state) {
  return {
    bones: state.bones.size,
    edited: [...state.bones.values()].filter((b) => !isZeroOffset(b.offset)).length,
    added: state.added.length,
    removed: state.removed.length,
    strokes: state.strokes.length,
    hiddenMeshes: [...state.meshVisibility.values()].filter((v) => v === false).length,
    posed: state.pose.size,
  };
}
