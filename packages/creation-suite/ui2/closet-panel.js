// closet-panel.js — phone-first closet panel driving a Viewer instance.
//
// Duck-typed on the viewer: registerClosetSlot / setClosetSlot /
// toggleSlot / focusPart / showFullBody / setLighting /
// saveClosetRecipe / loadClosetRecipe (all added to ui2/viewer.js by
// the closet lane). No import of viewer.js, so the panel loads in any
// page that already has a Viewer. Data comes from the registry v2 JSON
// (packages/creation-suite/closet-registry.json): characters[charId]
// .slots[slot] = { region, t7_spine, items: [{ id, meshes }] }.
// Presets are shortcuts: tapping a preset applies its items, but every
// slot keeps its own toggle afterwards — toggles are the truth.

export const CLOSET_PANEL_CSS = `
.closet-panel{position:fixed;left:0;right:0;bottom:0;max-height:46vh;overflow-y:auto;
  background:rgba(10,12,20,.94);color:#eef;border-top:2px solid #ff8c2e;
  font-family:system-ui,sans-serif;font-size:15px;z-index:50;padding:10px 12px 18px}
.closet-panel button,.closet-panel select,.closet-panel input{min-height:44px;font-size:15px;
  background:#22263a;color:#eef;border:1px solid #444;border-radius:8px;padding:6px 10px}
.closet-panel .cp-row{display:flex;gap:8px;align-items:center;padding:6px 0;border-bottom:1px solid #262a3d}
.closet-panel .cp-slot{flex:1;min-width:0}
.closet-panel .cp-region{font-weight:700;margin:12px 0 2px;color:#ffb066}
.closet-panel .cp-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.closet-panel .cp-head h2{margin:0;font-size:17px;flex:1}
.closet-panel .cp-light.on{background:#ff8c2e;color:#111;border-color:#ff8c2e}
`;

export function renderClosetPanel(container, viewer, registry, charId) {
  const char = registry?.characters?.[charId];
  if (!container || !viewer || !char) return null;
  if (!document.getElementById('closet-panel-css')) {
    const st = document.createElement('style');
    st.id = 'closet-panel-css';
    st.textContent = CLOSET_PANEL_CSS;
    document.head.appendChild(st);
  }
  viewer.setLighting('studio');
  const slots = char.slots || {};
  // Register every slot's mesh universe once, then apply the default item.
  for (const [slotId, slot] of Object.entries(slots)) {
    const universe = [...new Set((slot.items || []).flatMap((it) => it.meshes || []))];
    viewer.registerClosetSlot(slotId, universe);
    const def = (slot.items || []).find((it) => it.id === slot.default_item);
    if (def) viewer.setClosetSlot(slotId, def.meshes);
  }
  const regions = {};
  for (const [slotId, slot] of Object.entries(slots)) {
    (regions[slot.region || 'Body'] ||= []).push([slotId, slot]);
  }
  const el = document.createElement('div');
  el.className = 'closet-panel';
  const lightBtns = ['studio', 'living_room', 'night'].map((p) =>
    `<button class="cp-light${p === 'studio' ? ' on' : ''}" data-light="${p}">${p.replace('_', ' ')}</button>`).join('');
  const presetBtns = Object.entries(char.presets || {}).map(([name]) =>
    `<button data-preset="${name}">${name}</button>`).join('');
  let slotsHtml = '';
  for (const [region, list] of Object.entries(regions)) {
    slotsHtml += `<div class="cp-region">${region}</div>`;
    for (const [slotId, slot] of list) {
      const opts = (slot.items || []).map((it) =>
        `<option value="${it.id}"${it.id === slot.default_item ? ' selected' : ''}>${it.id}</option>`).join('');
      slotsHtml += `<div class="cp-row"><label class="cp-slot">${slotId}</label>
        <input type="checkbox" data-toggle="${slotId}" checked ${slot.always_on ? 'disabled' : ''} aria-label="toggle ${slotId}">
        <select data-item="${slotId}">${opts}</select>
        <button data-focus="${slotId}">Focus</button></div>`;
    }
  }
  el.innerHTML = `<div class="cp-head"><h2>Closet — ${charId}</h2>
    <button data-fullbody>Full body</button></div>
    <div class="cp-head">${lightBtns}</div>
    ${presetBtns ? `<div class="cp-head">Presets: ${presetBtns}</div>` : ''}
    ${slotsHtml}
    <div class="cp-row"><input data-recipe-name placeholder="Recipe name" style="flex:1">
    <button data-recipe-save>Save recipe</button></div>
    <div data-recipes></div>`;
  container.appendChild(el);

  const refreshRecipes = () => {
    const box = el.querySelector('[data-recipes]');
    box.innerHTML = (viewer.recipes || []).map((r) =>
      `<div class="cp-row"><span class="cp-slot">${r.name} v${r.version}</span>
       <button data-recipe-load="${r.name}:${r.version}">Load</button></div>`).join('');
  };
  el.addEventListener('click', (e) => {
    const t = e.target;
    const light = t.dataset.light;
    if (light) {
      viewer.setLighting(light);
      el.querySelectorAll('.cp-light').forEach((b) => b.classList.toggle('on', b.dataset.light === light));
      return;
    }
    if (t.dataset.fullbody !== undefined) { viewer.showFullBody(); return; }
    const focus = t.dataset.focus;
    if (focus) { viewer.focusPart(focus); return; }
    const preset = t.dataset.preset;
    if (preset) {
      const p = (char.presets || {})[preset] || {};
      for (const [slotId, itemId] of Object.entries(p)) {
        const slot = slots[slotId];
        if (!slot) continue;
        const item = (slot.items || []).find((it) => it.id === itemId);
        if (item) {
          viewer.setClosetSlot(slotId, item.meshes);
          const sel = el.querySelector(`[data-item="${slotId}"]`);
          if (sel) sel.value = itemId;
          const tog = el.querySelector(`[data-toggle="${slotId}"]`);
          if (tog) tog.checked = true;
        }
      }
      return;
    }
    if (t.dataset.recipeSave !== undefined) {
      const input = el.querySelector('[data-recipe-name]');
      const name = (input.value || '').trim();
      if (!name) return;
      viewer.saveClosetRecipe(name);
      input.value = '';
      refreshRecipes();
      return;
    }
    const load = t.dataset.recipeLoad;
    if (load) {
      const [name, v] = load.split(':');
      viewer.loadClosetRecipe(name, Number(v));
      refreshRecipes();
    }
  });
  el.addEventListener('change', (e) => {
    const t = e.target;
    if (t.dataset.toggle !== undefined) { viewer.toggleSlot(t.dataset.toggle, t.checked); return; }
    if (t.dataset.item !== undefined) {
      const slot = slots[t.dataset.item];
      const item = (slot.items || []).find((it) => it.id === t.value);
      if (item) viewer.setClosetSlot(t.dataset.item, item.meshes);
    }
  });
  refreshRecipes();
  return el;
}
