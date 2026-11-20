/* Western Heart UI screen definitions (wh-ui-screen v1).
 *
 * The UI WORKSHOP (game/ui-workshop.html) is the visual screen builder:
 * the user drags elements, styles them, and exports a screen-definition JSON
 * through the SAME round-trip patch as everything else (ui_screen_define).
 *
 * Sourcing order (owner): Tekken 8 UI first (customization/ui-screens/t8-source/
 * when extraction lands — the workshop prefers it), other games' UI layered
 * from teardown files, built-in templates (marked as recreations) as fallback.
 * The whole point is REMIX: the user takes pulled UI and edits it into
 * proprietary Western Heart versions in the workshop.
 *
 * Element types v1: label, button, panel, image, card-grid.
 * Reserved for later phases: screen.flow (screen-to-screen flow designer),
 * screen.wiring (selection -> game-action wiring).
 */

export const SCREEN_FORMAT = 'wh-ui-screen';
export const SCREEN_VERSION = 1;

export const ELEMENT_TYPES = ['label', 'button', 'panel', 'image', 'card-grid'];

export function blankStyle() {
  return {
    fontSize: 16, color: '#ffffff', background: 'transparent',
    borderColor: '#f2b01e', borderWidth: 0, radius: 6,
    fontWeight: 400, align: 'left',
  };
}

export function blankElement(type, id) {
  return {
    id: id || ('el_' + Math.random().toString(36).slice(2, 8)),
    type, x: 60, y: 60, w: 200, h: 48,
    text: type === 'label' ? 'Label' : type === 'button' ? 'Button' : '',
    src: '',
    bind: type === 'card-grid' ? 'stages' : '',
    cardW: 200, cardH: 120, gap: 12,
    style: blankStyle(),
  };
}

export function emptyScreen(id, name) {
  return {
    format: SCREEN_FORMAT, version: SCREEN_VERSION,
    id: id || 'untitled', name: name || 'Untitled',
    source: 'workshop',
    canvas: { w: 1280, h: 720 },
    elements: [],
    flow: {},
    wiring: {},
  };
}

/* Validate a screen definition. Returns a list of error strings (empty = valid). */
export function validateScreen(def) {
  const errs = [];
  if (!def || typeof def !== 'object') return ['screen must be an object'];
  if (def.format !== SCREEN_FORMAT) errs.push(`bad format: ${def.format}`);
  if (def.version !== SCREEN_VERSION) errs.push(`unsupported version: ${def.version}`);
  if (!def.id || typeof def.id !== 'string') errs.push('missing id');
  if (!def.canvas || !Number.isFinite(def.canvas.w) || !Number.isFinite(def.canvas.h)) {
    errs.push('bad canvas');
  }
  const seen = new Set();
  for (const [i, e] of (def.elements || []).entries()) {
    const where = `elements[${i}]`;
    if (!e || typeof e !== 'object') { errs.push(`${where} must be an object`); continue; }
    if (!ELEMENT_TYPES.includes(e.type)) { errs.push(`${where}: bad type ${e.type}`); continue; }
    if (!e.id || typeof e.id !== 'string') errs.push(`${where}: missing id`);
    else if (seen.has(e.id)) errs.push(`${where}: duplicate id ${e.id}`);
    else seen.add(e.id);
    for (const k of ['x', 'y', 'w', 'h']) {
      if (!Number.isFinite(e[k])) errs.push(`${where}: bad ${k}`);
    }
    if (e.w <= 0 || e.h <= 0) errs.push(`${where}: w/h must be positive`);
  }
  return errs;
}

function styleFor(e) {
  const s = { ...(e.style || {}) };
  return {
    position: 'absolute',
    left: e.x + 'px', top: e.y + 'px',
    width: e.w + 'px', height: e.h + 'px',
    fontSize: (s.fontSize ?? 16) + 'px',
    color: s.color || '#fff',
    background: s.background || 'transparent',
    border: (s.borderWidth ? `${s.borderWidth}px solid ${s.borderColor || '#f2b01e'}` : 'none'),
    borderRadius: (s.radius ?? 6) + 'px',
    fontWeight: s.fontWeight || 400,
    textAlign: s.align || 'left',
    display: 'flex', alignItems: 'center',
    justifyContent: s.align === 'center' ? 'center' : s.align === 'right' ? 'flex-end' : 'flex-start',
    padding: '6px 10px', boxSizing: 'border-box',
    overflow: 'hidden',
  };
}

function applyStyle(node, css) {
  for (const [k, v] of Object.entries(css)) node.style[k] = v;
}

/* Render a screen definition into a container (position:relative).
 * `data` supplies bound lists: { stages: [{name, universe, swatch:[c1,c2]}], fighters: [...] }.
 * `interactive` enables click-to-select + drag (the workshop); the game uses false.
 * onSelect(id) fires when an element is picked in interactive mode.
 */
export function renderScreen(container, def, data = {}, interactive = false, onSelect = null) {
  container.innerHTML = '';
  container.style.position = 'relative';
  container.style.width = def.canvas.w + 'px';
  container.style.height = def.canvas.h + 'px';
  container.style.overflow = 'hidden';
  container.style.background = '#0d0d14';
  const nodes = {};
  for (const e of def.elements || []) {
    let node;
    if (e.type === 'card-grid') {
      node = document.createElement('div');
      applyStyle(node, styleFor(e));
      node.style.display = 'grid';
      node.style.gridTemplateColumns = `repeat(auto-fill, ${e.cardW || 200}px)`;
      node.style.gap = (e.gap ?? 12) + 'px';
      node.style.alignContent = 'start';
      const items = (data[e.bind] || []);
      for (const it of items) {
        const card = document.createElement('div');
        card.style.cssText = `width:${e.cardW || 200}px;height:${e.cardH || 120}px;border:1px solid #f2b01e;` +
          `border-radius:8px;overflow:hidden;position:relative;background:#16161f;`;
        const sw = document.createElement('div');
        const [c1, c2] = it.swatch || ['#333', '#666'];
        sw.style.cssText = `position:absolute;inset:0;background:linear-gradient(135deg, ${c1}, ${c2});`;
        const nm = document.createElement('div');
        nm.textContent = it.name || '';
        nm.style.cssText = 'position:absolute;left:0;right:0;bottom:0;padding:6px 8px;' +
          'background:rgba(0,0,0,0.65);color:#f2b01e;font-weight:700;font-size:13px;';
        card.append(sw, nm);
        node.appendChild(card);
      }
      if (!items.length) {
        node.textContent = `[${e.bind || 'data'}: no preview data]`;
        node.style.color = '#777';
      }
    } else if (e.type === 'image') {
      node = document.createElement(e.src ? 'img' : 'div');
      if (e.src) node.src = e.src;
      else { node.textContent = '[image]'; node.style.color = '#777'; }
      applyStyle(node, styleFor(e));
      node.style.padding = '0';
    } else {
      // label, button, panel
      node = document.createElement(e.type === 'button' ? 'button' : 'div');
      node.textContent = e.text || '';
      applyStyle(node, styleFor(e));
      if (e.type === 'button') node.style.cursor = 'pointer';
    }
    node.dataset.elid = e.id;
    if (interactive) {
      node.style.cursor = 'move';
      node.addEventListener('pointerdown', (ev) => {
        ev.stopPropagation();
        onSelect && onSelect(e.id, ev);
      });
    }
    container.appendChild(node);
    nodes[e.id] = node;
  }
  return nodes;
}

/* Build a wh-tweak-patch (ui_screen_define) from a screen definition. */
export function buildScreenPatch(def, notes) {
  const errs = validateScreen(def);
  if (errs.length) throw new Error('invalid screen: ' + errs.join('; '));
  return {
    format: 'wh-tweak-patch',
    version: 1,
    kit_id: null,
    fighter: 'ui',
    attire: def.id,
    exported_at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    exported_by: 'suite',
    suite_build: '',
    notes: notes || '',
    changes: [{ kind: 'ui_screen_define', screen: def, note: notes || '' }],
  };
}

export function downloadJson(filename, obj) {
  const blob = new Blob([JSON.stringify(obj, null, 2) + '\n'], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 4000);
}
