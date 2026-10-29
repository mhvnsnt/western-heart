/* ============================================================
   WESTERN HEART — material-resolve (shared, dependency-free)
   ONE material check used in three places:
     1. tools/assets/wh_asset_pipeline.mjs  (every intake: audit before/after)
     2. tools/assets/material_gate.mjs      (CI: every MODEL_URLS model)
     3. game/js/assets.js _ingest           (runtime: every loaded model)
   It works on plain glTF JSON (+ the GLB binary chunk when present), so it
   runs in Node and the browser alike. Verdicts per primitive:
     ok          base colour comes from a texture or COLOR_0 vertex colours
     missing     primitive has no material, or points at a material/texture/
                 image index that does not exist, or an image with no data
     placeholder material name is an exporter stand-in (dummy_material_N,
                 Material.001, unnamed.N, DefaultMaterial, lambert1, ...) AND
                 it has no texture/vertex colour to say otherwise
     untextured  no base-colour texture, no vertex colours and only an exporter-
                 default factor (absent, white, 0.8 grey or black). An explicit
                 authored colour (eye white, metal trim) counts as ok/flat.
   T7 note: UModel `-notex` exports are dummy_material_N + greyscale T_CH_*_D;
   those need the T7 MI resolve (game/js/t7-material.js / creation-suite
   t7material.js) — the audit flags them `t7` so callers can route them.
   ============================================================ */

export const PLACEHOLDER_RE =
  /^(dummy_material(_\d+)?|material(\.\d+)?|material_\d+|unnamed(\.\d+)?|defaultmaterial|default|lambert\d*|blinn\d*|phong\d*|none|placeholder|initialshadinggroup)(\.\d+)?$/i;

export function parseGlb(u8) {
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  if (dv.getUint32(0, true) !== 0x46546c67) throw new Error('not a GLB');
  const jl = dv.getUint32(12, true);
  const json = JSON.parse(new TextDecoder().decode(u8.subarray(20, 20 + jl)));
  let binLen = 0;
  const o = 20 + jl;
  if (o + 8 <= u8.byteLength) binLen = dv.getUint32(o, true);
  return { json, binLength: binLen };
}

function imageOk(json, imgIdx, binLength) {
  const img = (json.images || [])[imgIdx];
  if (!img) return false;
  if (img.uri) return img.uri.length > 0; // external/data URI: existence checked by caller (fileExists)
  const bv = (json.bufferViews || [])[img.bufferView];
  if (!bv || !(bv.byteLength > 0)) return false;
  const buf = (json.buffers || [])[bv.buffer || 0];
  if (buf && buf.uri == null && binLength && (bv.byteOffset || 0) + bv.byteLength > binLength) return false;
  return true;
}

function texImage(json, t) {
  const tex = (json.textures || [])[t];
  if (!tex) return null;
  const e = tex.extensions || {};
  for (const k of ['EXT_texture_webp', 'KHR_texture_basisu', 'EXT_texture_avif']) if (e[k]) return e[k].source;
  return tex.source;
}

/** An explicit non-default, non-black, non-grey-white base colour is an authored flat
 *  colour (eye whites, metal trims) — fine. Absent / white / 0.8 grey / black = exporter default. */
export function authoredFlat(f) {
  if (!Array.isArray(f)) return false;
  const [r, g, b] = f, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
  if (mx < 0.005) return false;                      // pure black: lost texture
  if (mx - mn < 0.03 && (mx > 0.75)) return false;    // white / 0.8 grey default
  return true;
}

/** Audit one glTF. opts.fileExists(uri) -> bool for external image URIs. */
export function auditGltf(json, { binLength = 0, fileExists = null } = {}) {
  const mats = json.materials || [];
  const prims = [];
  const counts = { ok: 0, missing: 0, placeholder: 0, untextured: 0 };
  let t7 = false, flat = 0;
  (json.meshes || []).forEach((m, mi) => (m.primitives || []).forEach((p, pi) => {
    const where = `${m.name || 'mesh' + mi}#${pi}`;
    let verdict = 'ok', why = '';
    const vc = p.attributes && p.attributes.COLOR_0 != null;
    const mat = p.material == null ? null : mats[p.material];
    if (!mat) { verdict = 'missing'; why = p.material == null ? 'no material' : `material ${p.material} absent`; }
    else {
      const name = mat.name || '';
      if (/^dummy_material/i.test(name) || /^MI_CH_|T_CH_/.test(name)) t7 = true;
      const pb = mat.pbrMetallicRoughness || {};
      const bt = pb.baseColorTexture || (mat.extensions && mat.extensions.KHR_materials_pbrSpecularGlossiness &&
        mat.extensions.KHR_materials_pbrSpecularGlossiness.diffuseTexture);
      if (bt) {
        const src = texImage(json, bt.index);
        if (src == null || !imageOk(json, src, binLength)) { verdict = 'missing'; why = `baseColor texture ${bt.index} has no image data`; }
        else {
          const uri = json.images[src].uri;
          if (uri && !uri.startsWith('data:') && fileExists && !fileExists(decodeURIComponent(uri))) {
            verdict = 'missing'; why = `image file ${uri} not found`;
          }
        }
      } else if (vc) verdict = 'ok';
      else if (PLACEHOLDER_RE.test(name.trim()) || !name.trim()) { verdict = 'placeholder'; why = `placeholder material "${name}"`; }
      else if (authoredFlat(pb.baseColorFactor)) { verdict = 'ok'; why = 'authored flat colour'; flat++; }
      else { verdict = 'untextured'; why = `"${name}" has no base-colour texture, vertex colours or authored colour (factor ${JSON.stringify(pb.baseColorFactor || 'default')})`; }
    }
    counts[verdict]++;
    prims.push({ where, material: mat ? mat.name || p.material : null, verdict, why });
  }));
  const bad = counts.missing + counts.placeholder + counts.untextured;
  return { ok: bad === 0 && prims.length > 0, counts, primitives: prims.length, flatAuthored: flat, t7, findings: prims.filter(p => p.verdict !== 'ok') };
}

/** Repairs that are always safe on JSON (no invented content):
 *  - drop texture refs whose image data is absent (so loaders never stall on them)
 *  - nothing else: colour is never made up here. */
export function repairGltfJson(json, opts = {}) {
  const fixed = [];
  for (const [i, mat] of (json.materials || []).entries()) {
    const slots = [['pbrMetallicRoughness', 'baseColorTexture'], ['pbrMetallicRoughness', 'metallicRoughnessTexture'],
      [null, 'normalTexture'], [null, 'occlusionTexture'], [null, 'emissiveTexture']];
    for (const [g, k] of slots) {
      const host = g ? mat[g] : mat;
      if (!host || !host[k]) continue;
      const src = texImage(json, host[k].index);
      if (src == null || !imageOk(json, src, opts.binLength || 0)) { delete host[k]; fixed.push(`material ${i} ${k}: dangling texture dropped`); }
    }
  }
  return fixed;
}

const baseName = n => String(n || '').replace(/\.\d{3}$/, '').trim();

function primVerts(json, p) {
  const a = (json.accessors || [])[p.attributes && p.attributes.POSITION];
  return a ? a.count : -1;
}

/** Same-model donor plan: for every failing material of `target`, find a textured
 *  material in `donor` with the same base name (Blender `.001` suffix ignored)
 *  whose primitives have the same vertex counts — i.e. the identical mesh part
 *  exported once with its textures and once without. Returns
 *  { complete, map: { targetMaterialIndex: donorMaterialIndex } } or null.
 *  Nothing is invented: the donor's own source textures are reused as-is. */
export function donorPlan(target, donor) {
  const audit = auditGltf(target);
  if (audit.ok) return { complete: true, map: {} };
  const tm = target.materials || [], dm = donor.materials || [];
  const vertsBy = (json) => {
    const out = new Map();
    for (const m of json.meshes || []) for (const p of m.primitives || []) {
      if (p.material == null) continue;
      if (!out.has(p.material)) out.set(p.material, []);
      out.get(p.material).push(primVerts(json, p));
    }
    for (const v of out.values()) v.sort((a, b) => a - b);
    return out;
  };
  const tv = vertsBy(target), dv = vertsBy(donor);
  const donorOk = new Map();
  auditGltf(donor); // (cheap) — donor materials must themselves be textured
  dm.forEach((m, i) => {
    const pb = m.pbrMetallicRoughness || {};
    if (pb.baseColorTexture) donorOk.set(baseName(m.name), i);
  });
  const need = new Set();
  for (const m of target.meshes || []) for (const p of m.primitives || []) {
    const mat = tm[p.material];
    const pb = (mat && mat.pbrMetallicRoughness) || {};
    const isVC = p.attributes && p.attributes.COLOR_0 != null;
    if (mat && !pb.baseColorTexture && !isVC && !authoredFlat(pb.baseColorFactor)) need.add(p.material);
    if (mat && !pb.baseColorTexture && !isVC && PLACEHOLDER_RE.test((mat.name || '').trim())) need.add(p.material);
  }
  const map = {};
  for (const ti of need) {
    const di = donorOk.get(baseName(tm[ti].name));
    if (di == null) continue;
    const a = tv.get(ti) || [], b = dv.get(di) || [];
    // same part re-exported: same primitive count, vertex counts within 3% (seam splits differ by a few)
    if (a.length !== b.length || a.some((n, k) => Math.abs(n - b[k]) > Math.max(2, 0.03 * b[k]))) continue;
    map[ti] = di;
  }
  const hits = Object.keys(map).length;
  if (!hits) return null;
  return { complete: hits === need.size, map, needed: need.size };
}
