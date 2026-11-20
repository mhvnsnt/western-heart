/* Western Heart — Fix Panel (tweak-kit round trip).
 *
 * Permanent suite feature: loads a crew-staged tweak kit
 * (customization/tweak-kits/<kit-id>.json), resolves the fighter's part-group
 * targets (BONES first, then meshes, via the kit's part_map), gives the user
 * per-group rotate/flip/offset controls, and exports ONE patch file
 * (wh-tweak-patch v1) via the single export button.
 *
 * The 8 part groups: head, torso, upper_arms, forearms, hands, thighs, shins, feet.
 * Groups cover both sides together (L/R mirrored) — part-orientation fixes are
 * almost always symmetric.
 *
 * Live preview: bone targets are wrapped in an identity Group inserted between
 * the bone and its parent, and the group's adjust is applied to the WRAPPER.
 * The game's animation keeps writing the bone's own local transform every
 * frame, so the preview survives animation with no per-frame re-application
 * and no accumulation. Mesh targets get the adjust composed onto their base
 * transform. The same numbers go into the exported patch, so preview == import.
 *
 * The rig/model-fix pipeline bakes the patch's per-group rotation_deg / flip /
 * offset / scale into the bind pose (bones) or the part node (meshes).
 *
 * Exposes window.__fixpanel = { kit, targets, values(), setGroup(), patch(),
 * exportPatch() } for tests and the harness console.
 */
import * as THREE from 'three';

export const PART_GROUPS = [
  'head', 'torso', 'upper_arms', 'forearms',
  'hands', 'thighs', 'shins', 'feet',
];

const GROUP_LABELS = {
  head: 'Head', torso: 'Torso', upper_arms: 'Upper arms', forearms: 'Forearms',
  hands: 'Hands', thighs: 'Thighs', shins: 'Shins', feet: 'Feet',
};

/* Default bone-name patterns (Mixamo-style rigs, e.g. nightwolf.glb).
 * A kit can override per fighter via part_map. */
export const DEFAULT_BONE_PATTERNS = {
  head: ['head', 'neck'],
  torso: ['spine', 'chest'],
  upper_arms: ['shoulder', 'upperarm', 'leftarm', 'rightarm'],
  forearms: ['forearm', 'elbow'],
  hands: ['hand', 'wrist', 'finger', 'thumb'],
  thighs: ['upleg', 'thigh', 'hip'],
  shins: ['leg', 'shin', 'calf', 'knee'],
  feet: ['foot', 'feet', 'toe'],
};

function blankAdjust() {
  return { rotation_deg: [0, 0, 0], flip: [false, false, false],
           offset: [0, 0, 0], scale: 1.0, note: '' };
}

export function sanitizeAdjust(raw) {
  const b = blankAdjust();
  if (!raw || typeof raw !== 'object') return b;
  const num3 = (v, dflt) => (Array.isArray(v) && v.length === 3 &&
    v.every((n) => Number.isFinite(n)) ? v.map(Number) : dflt);
  const bool3 = (v, dflt) => (Array.isArray(v) && v.length === 3 &&
    v.every((n) => typeof n === 'boolean') ? v.slice() : dflt);
  return {
    rotation_deg: num3(raw.rotation_deg, b.rotation_deg),
    flip: bool3(raw.flip, b.flip),
    offset: num3(raw.offset, b.offset),
    scale: Number.isFinite(raw.scale) ? Number(raw.scale) : 1.0,
    note: typeof raw.note === 'string' ? raw.note : '',
  };
}

/* Resolve part-group targets: bones first (wrapped), then meshes (direct).
 * partMap: { group: [substring patterns] } matched case-insensitively
 * against bone/node names; bones already claimed by an earlier group win. */
export function resolveTargets(model, partMap) {
  const bones = [];
  const meshes = [];
  model.traverse((o) => {
    if (o.isBone) bones.push(o);
    else if (o.isMesh) meshes.push(o);
  });
  const patterns = {};
  for (const g of PART_GROUPS) {
    const p = (partMap && partMap[g]) || DEFAULT_BONE_PATTERNS[g] || [];
    patterns[g] = p.map((s) => String(s).toLowerCase());
  }
  const claimed = new Set();
  const out = {};
  for (const g of PART_GROUPS) {
    const hit = bones.filter((b) => {
      const n = (b.name || '').toLowerCase();
      return n && !claimed.has(b) && patterns[g].some((p) => n.includes(p));
    });
    hit.forEach((b) => claimed.add(b));
    // Never wrap the root: rotating Hips would move the whole fighter.
    const usable = hit.filter((b) => b.parent && b.parent.isBone);
    out[g] = usable.map((b) => ({ kind: 'bone', name: b.name, object: b }));
  }
  // Fallback: if a group found no bones, try meshes by the same patterns.
  for (const g of PART_GROUPS) {
    if (out[g].length) continue;
    out[g] = meshes
      .filter((m) => {
        const n = (m.name || '').toLowerCase();
        return n && patterns[g].some((p) => n.includes(p));
      })
      .map((m) => ({ kind: 'mesh', name: m.name, object: m }));
  }
  return out;
}

/* Wrap a bone in an identity group so the adjust survives animation.
 * Returns the wrapper; the bone keeps its own local transform untouched. */
export function wrapBone(bone) {
  const parent = bone.parent;
  const wrapper = new THREE.Group();
  wrapper.name = `__fixwrap_${bone.name}`;
  parent.add(wrapper);
  wrapper.add(bone); // keeps bone.position/quaternion/scale as-is
  return wrapper;
}

export function applyAdjust(wrapper, base, adj) {
  const [rx, ry, rz] = adj.rotation_deg.map((d) => (d * Math.PI) / 180);
  wrapper.quaternion.setFromEuler(new THREE.Euler(rx, ry, rz, 'XYZ'));
  wrapper.scale.set(
    base.scale.x * (adj.flip[0] ? -1 : 1) * adj.scale,
    base.scale.y * (adj.flip[1] ? -1 : 1) * adj.scale,
    base.scale.z * (adj.flip[2] ? -1 : 1) * adj.scale,
  );
  wrapper.position.set(
    base.position.x + adj.offset[0],
    base.position.y + adj.offset[1],
    base.position.z + adj.offset[2],
  );
  wrapper.updateMatrix();
}

export function buildPatch({ kit, fighter, attire, values, notes, suiteBuild, resolved }) {
  const changes = [];
  for (const g of PART_GROUPS) {
    const v = values[g];
    if (!v) continue;
    const isDefault = v.rotation_deg.every((n) => n === 0) &&
      v.flip.every((b) => !b) && v.offset.every((n) => n === 0) &&
      v.scale === 1.0;
    if (isDefault) continue; // only export what changed
    changes.push({
      kind: 'part_transform', group: g,
      rotation_deg: v.rotation_deg.slice(),
      flip: v.flip.slice(),
      offset: v.offset.slice(),
      scale: v.scale,
      note: v.note || '',
    });
  }
  return {
    format: 'wh-tweak-patch',
    version: 1,
    kit_id: kit.id,
    fighter,
    attire: attire || kit.attire || 'default',
    exported_at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    exported_by: 'suite',
    suite_build: suiteBuild || '',
    notes: notes || '',
    resolved_targets: resolved || undefined,
    changes,
  };
}

export function downloadJson(filename, obj) {
  const blob = new Blob([JSON.stringify(obj, null, 2) + '\n'],
    { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 4000);
}

/* ---- DOM panel ---- */

function el(tag, attrs, text) {
  const n = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (k === 'style') n.style.cssText = v; else n.setAttribute(k, v);
  }
  if (text != null) n.textContent = text;
  return n;
}

function sliderRow(parent, label, min, max, step, value, fmt, onInput) {
  const row = el('div', { style: 'display:flex;align-items:center;gap:6px;margin:3px 0' });
  const lab = el('span', { style: 'width:64px;flex:none;color:#9cf;font-size:11px' }, label);
  const s = el('input', { type: 'range', min, max, step, value,
    style: 'flex:1;accent-color:#4af' });
  const val = el('span', { style: 'width:64px;text-align:right;color:#cfc;font-size:11px;font-variant-numeric:tabular-nums' });
  const paint = () => { val.textContent = fmt(parseFloat(s.value)); };
  s.addEventListener('input', () => { paint(); onInput(parseFloat(s.value)); });
  paint();
  row.append(lab, s, val);
  parent.appendChild(row);
  return { set(v) { s.value = v; paint(); } };
}

function flipRow(parent, state, onToggle) {
  const row = el('div', { style: 'display:flex;align-items:center;gap:6px;margin:3px 0' });
  row.appendChild(el('span', { style: 'width:64px;flex:none;color:#9cf;font-size:11px' }, 'flip'));
  ['X', 'Y', 'Z'].forEach((axis, i) => {
    const b = el('button', {
      style: 'flex:1;padding:4px 0;background:#222;color:#ccc;border:1px solid #555;border-radius:4px;font-size:11px;cursor:pointer',
    }, 'flip ' + axis);
    const paint = () => {
      b.style.background = state[i] ? '#a33' : '#222';
      b.style.color = state[i] ? '#fff' : '#ccc';
    };
    b.addEventListener('click', () => { state[i] = !state[i]; paint(); onToggle(); });
    paint();
    row.appendChild(b);
  });
  parent.appendChild(row);
}

export async function mountFixPanel({ game, kitId, fetchFn = fetch, suiteBuild = '' }) {
  const kit = await (await fetchFn(`../customization/tweak-kits/${kitId}.json`)).json();
  if (!kit || kit.format !== 'wh-tweak-kit') {
    throw new Error(`tweak kit '${kitId}' missing or bad format`);
  }
  const fighter = game.p1 && game.p1.char ? game.p1.char.id : null;
  const model = game.p1 && game.p1.model;
  if (!model) throw new Error('fix panel: no p1 model to tweak');
  if (kit.fighter && fighter && kit.fighter !== fighter) {
    console.warn(`[FIXPANEL] kit fighter '${kit.fighter}' != p1 '${fighter}' — mounting anyway`);
  }

  const targets = resolveTargets(model, kit.part_map || {});
  // Wrap bones; capture base transforms of wrappers (identity) and meshes.
  const wrapped = new Map(); // target object -> {wrapper, base}
  const meshBase = new Map();
  for (const g of PART_GROUPS) for (const t of targets[g]) {
    if (t.kind === 'bone') {
      const wrapper = wrapBone(t.object);
      wrapped.set(t.object, { wrapper,
        base: { position: wrapper.position.clone(),
                scale: wrapper.scale.clone() } });
    } else if (!meshBase.has(t.object)) {
      meshBase.set(t.object, {
        position: t.object.position.clone(),
        quaternion: t.object.quaternion.clone(),
        scale: t.object.scale.clone(),
      });
    }
  }

  const values = {};
  for (const g of PART_GROUPS) values[g] = sanitizeAdjust((kit.adjustments || {})[g]);

  function applyAll() {
    for (const g of PART_GROUPS) {
      for (const t of targets[g]) {
        if (t.kind === 'bone') {
          const { wrapper, base } = wrapped.get(t.object);
          applyAdjust(wrapper, base, values[g]);
        } else {
          const b = meshBase.get(t.object);
          const m = t.object;
          const [rx, ry, rz] = values[g].rotation_deg.map((d) => (d * Math.PI) / 180);
          m.quaternion.copy(b.quaternion)
            .multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(rx, ry, rz, 'XYZ')));
          m.scale.set(
            b.scale.x * (values[g].flip[0] ? -1 : 1) * values[g].scale,
            b.scale.y * (values[g].flip[1] ? -1 : 1) * values[g].scale,
            b.scale.z * (values[g].flip[2] ? -1 : 1) * values[g].scale);
          m.position.set(b.position.x + values[g].offset[0],
                         b.position.y + values[g].offset[1],
                         b.position.z + values[g].offset[2]);
          m.updateMatrix();
        }
      }
    }
  }

  const resolved = {};
  for (const g of PART_GROUPS) {
    resolved[g] = targets[g].map((t) => ({ kind: t.kind, name: t.name }));
  }

  /* --- panel DOM --- */
  const panel = el('div', { id: 'fixpanel',
    style: 'position:fixed;top:8px;right:8px;width:340px;max-height:calc(100vh - 16px);'
      + 'overflow-y:auto;background:rgba(8,12,20,0.92);color:#eee;border:1px solid #46a;'
      + 'border-radius:8px;padding:10px 12px;font:12px system-ui,sans-serif;z-index:20' });
  const headRow = el('div', { style: 'display:flex;align-items:center;justify-content:space-between;margin-bottom:6px' });
  headRow.appendChild(el('strong', null, `🔧 Fix: ${kit.fighter || fighter}`));
  const close = el('button', { style: 'background:#333;color:#eee;border:1px solid #666;border-radius:4px;padding:2px 8px;cursor:pointer' }, '✕');
  close.addEventListener('click', () => panel.remove());
  headRow.appendChild(close);
  panel.appendChild(headRow);
  panel.appendChild(el('div', { style: 'color:#8aa;font-size:11px;margin-bottom:8px' },
    kit.notes || `kit ${kit.id}`));

  const flagged = new Set(kit.flagged_parts || []);
  for (const g of PART_GROUPS) {
    const n = targets[g].length;
    const title = `${flagged.has(g) ? '🚩 ' : ''}${GROUP_LABELS[g]} ` +
      (n ? `(${n} target${n === 1 ? '' : 's'})` : '(nothing matched!)');
    const sec = el('details', { style: 'margin:6px 0;border-top:1px solid #234;padding-top:6px' });
    if (flagged.has(g) || n === 0) sec.open = true;
    sec.appendChild(el('summary', { style: 'cursor:pointer;color:#fe8' }, title));
    if (n) {
      sec.appendChild(el('div', { style: 'color:#777;font-size:10px;margin:2px 0 4px' },
        targets[g].map((t) => t.name).join(', ')));
    }
    const v = values[g];
    const repaint = () => applyAll();
    const deg = (x) => `${x.toFixed(0)}°`;
    ['X', 'Y', 'Z'].forEach((axis, i) => {
      sliderRow(sec, `rot ${axis}`, -180, 180, 1, v.rotation_deg[i], deg,
        (x) => { v.rotation_deg[i] = x; repaint(); });
    });
    flipRow(sec, v.flip, repaint);
    ['X', 'Y', 'Z'].forEach((axis, i) => {
      sliderRow(sec, `off ${axis}`, -2, 2, 0.01, v.offset[i],
        (x) => `${x.toFixed(2)}`, (x) => { v.offset[i] = x; repaint(); });
    });
    sliderRow(sec, 'scale', 0.5, 2, 0.01, v.scale, (x) => `${x.toFixed(2)}`,
      (x) => { v.scale = x; repaint(); });
    const note = el('input', { type: 'text', placeholder: 'note (optional)',
      value: v.note, maxlength: 120,
      style: 'width:100%;margin-top:4px;padding:4px 6px;background:#111;color:#eee;border:1px solid #444;border-radius:4px;font-size:11px' });
    note.addEventListener('input', () => { v.note = note.value; });
    sec.appendChild(note);
    panel.appendChild(sec);
  }

  const notesBox = el('textarea', { placeholder: 'overall notes for the crew (optional)',
    rows: 2, style: 'width:100%;margin:8px 0;padding:6px;background:#111;color:#eee;border:1px solid #444;border-radius:4px;font-size:11px' });
  panel.appendChild(notesBox);

  const exportBtn = el('button', {
    style: 'width:100%;padding:12px;background:#2a6;color:#fff;border:none;border-radius:6px;'
      + 'font-size:14px;font-weight:700;cursor:pointer;margin-top:4px' },
    '⬇ EXPORT TWEAK PATCH');
  const status = el('div', { style: 'color:#8f8;font-size:11px;margin-top:6px;min-height:16px' });
  exportBtn.addEventListener('click', () => {
    const patch = buildPatch({
      kit, fighter, attire: kit.attire, values,
      notes: notesBox.value, suiteBuild, resolved,
    });
    if (!patch.changes.length) {
      status.textContent = 'nothing changed — tweak a part first';
      return;
    }
    const fname = `${fighter}-${kit.id}-tweak-patch.json`;
    downloadJson(fname, patch);
    status.textContent = `exported ${fname} (${patch.changes.length} change${patch.changes.length === 1 ? '' : 's'}) — send it back in chat`;
    console.log('[FIXPANEL] exported patch', patch);
  });
  panel.appendChild(exportBtn);
  panel.appendChild(status);

  const resetBtn = el('button', {
    style: 'width:100%;padding:6px;background:transparent;color:#c88;border:1px solid #844;'
      + 'border-radius:6px;font-size:11px;cursor:pointer;margin-top:8px' },
    'reset to kit start');
  resetBtn.addEventListener('click', () => location.reload());
  panel.appendChild(resetBtn);

  document.body.appendChild(panel);
  applyAll(); // apply the kit's starting adjustments live
  console.log('[FIXPANEL] mounted kit', kit.id,
    Object.fromEntries(PART_GROUPS.map((g) => [g, targets[g].length])));

  const api = {
    kit, targets,
    values: () => JSON.parse(JSON.stringify(values)),
    setGroup(g, adj) { Object.assign(values[g], sanitizeAdjust(adj)); applyAll(); },
    patch: (notes) => buildPatch({ kit, fighter, attire: kit.attire,
      values, notes: notes || '', suiteBuild, resolved }),
    exportPatch: () => exportBtn.click(),
  };
  window.__fixpanel = api;
  return api;
}
