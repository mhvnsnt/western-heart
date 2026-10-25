/* CREATION-SUITE EXTRA PARTS (2026-10-23). Converted (glTF) parts from pulled
   wrestling-game CAW data, slotted by t7layout slot names. Loaded ONLY from the
   private asset pack; the public build ships none and this returns []. All part
   names pass tools/canon before reaching the manifest. */
export const SLOTS = ['head', 'hair', 'face', 'upper', 'lower', 'hands', 'feet', 'accessory'];
export async function loadPrivateParts(fetchJson = (u) => fetch(u).then(r => r.json())) {
  if (!globalThis.__WH_PRIVATE_ASSETS) return [];
  const base = globalThis.__WH_PRIVATE_BASE || 'private/';
  try {
    const m = await fetchJson(base + 'creation-parts/manifest.json');
    return (m.parts || []).filter(p => SLOTS.includes(p.slot) && /\.glb$/i.test(p.glb) && p.canon === true);
  } catch { return []; }
}
