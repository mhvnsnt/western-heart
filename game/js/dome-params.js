/* ============================================================
   WESTERN HEART — Dome Parameter Editor
   Editable dome parameters for character customization.
   Owner 2026-10-19: "go in the game and edit it and save the edit
   on the attire... with a live preview just like the tech and
   creation suite straight from the files"

   Parameters are stored in dome-params.json per attire.
   The build script (render-work/build-dome-v5.py) reads the same file.
   ============================================================ */

// Default dome parameters (match build-dome-v5.py DEFAULTS)
export const DOME_PARAM_DEFAULTS = {
  dome_cx: -0.003,
  dome_cy: 0.0,
  fluid_z_top: 0.421,      // DO NOT RAISE (owner 2026-10-19)
  fluid_z_bot: 0.204,
  glass_z_bot: 0.197,      // 1/3 shorter than v4
  glass_joint_z: 0.321,
  liquid_forward_offset: 0.005,  // forward depth toward viewer
  liquid_radius_scale: 1.0,
  fluid_color: [0.30, 0.85, 0.40, 1.0],
  fluid_transmission: 0.6,
  glass_transmission: 1.0,
  glass_ior: 1.5,
  lava_count: 10,
  bubble_count: 24,
  lava_emissive: [0.05, 0.35, 0.10],
};

// Parameter metadata for UI generation
// Each entry: { key, label, type, min, max, step, group }
export const DOME_PARAM_SCHEMA = [
  // Glass
  { key: 'glass_z_bot', label: 'Glass Bottom', type: 'slider', min: 0.15, max: 0.30, step: 0.001, group: 'Glass' },
  { key: 'glass_transmission', label: 'Glass Clarity', type: 'slider', min: 0.0, max: 1.0, step: 0.01, group: 'Glass' },
  { key: 'glass_ior', label: 'Glass IOR', type: 'slider', min: 1.0, max: 2.0, step: 0.01, group: 'Glass' },
  // Liquid
  { key: 'fluid_z_top', label: 'Liquid Top', type: 'slider', min: 0.30, max: 0.421, step: 0.001, group: 'Liquid', locked: true, lockNote: 'DO NOT RAISE (owner 2026-10-19)' },
  { key: 'fluid_z_bot', label: 'Liquid Bottom', type: 'slider', min: 0.15, max: 0.30, step: 0.001, group: 'Liquid' },
  { key: 'liquid_forward_offset', label: 'Forward Depth', type: 'slider', min: 0.0, max: 0.02, step: 0.001, group: 'Liquid' },
  { key: 'liquid_radius_scale', label: 'Liquid Width', type: 'slider', min: 0.8, max: 1.2, step: 0.01, group: 'Liquid' },
  { key: 'fluid_color', label: 'Liquid Color', type: 'color', group: 'Liquid' },
  { key: 'fluid_transmission', label: 'Liquid Clarity', type: 'slider', min: 0.0, max: 1.0, step: 0.01, group: 'Liquid' },
  // Effects
  { key: 'lava_count', label: 'Lava Blobs', type: 'slider', min: 0, max: 20, step: 1, group: 'Effects' },
  { key: 'bubble_count', label: 'Bubbles', type: 'slider', min: 0, max: 50, step: 1, group: 'Effects' },
  { key: 'lava_emissive', label: 'Lava Glow', type: 'color', group: 'Effects' },
];

/**
 * Load dome parameters for an attire.
 * @param {string} attirePath - Path to the attire folder (e.g. 'roster/doc-frank/attires/attire2')
 * @returns {Promise<Object>} Merged parameters (defaults + saved)
 */
export async function loadDomeParams(attirePath) {
  const params = { ...DOME_PARAM_DEFAULTS };
  try {
    const resp = await fetch(`${attirePath}/dome-fix/dome-params.json`);
    if (resp.ok) {
      const saved = await resp.json();
      // Only copy known keys (ignore _comment, _owner_notes)
      for (const key of Object.keys(DOME_PARAM_DEFAULTS)) {
        if (key in saved) params[key] = saved[key];
      }
    }
  } catch (e) {
    console.warn('[WH] Failed to load dome params:', e.message);
  }
  return params;
}

/**
 * Save dome parameters for an attire.
 * In the game, this writes to the attire's dome-params.json.
 * @param {string} attirePath - Path to the attire folder
 * @param {Object} params - Parameters to save
 */
export async function saveDomeParams(attirePath, params) {
  // Filter to known keys
  const toSave = { _comment: 'Doc Frank Wowomomo Dome parameters - editable in character customization' };
  for (const key of Object.keys(DOME_PARAM_DEFAULTS)) {
    toSave[key] = params[key];
  }
  // In a real implementation, this would POST to a server endpoint
  // or use the File System Access API. For now, download as file.
  const blob = new Blob([JSON.stringify(toSave, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'dome-params.json';
  a.click();
  URL.revokeObjectURL(url);
  console.log('[WH] Dome params saved (downloaded). Place in', `${attirePath}/dome-fix/`);
}

/**
 * Create UI controls for dome parameters.
 * @param {HTMLElement} container - DOM element to hold the controls
 * @param {Object} params - Current parameters (mutable)
 * @param {Function} onChange - Called when any param changes (for live preview)
 */
export function createDomeParamUI(container, params, onChange) {
  container.innerHTML = '';
  
  const groups = {};
  for (const schema of DOME_PARAM_SCHEMA) {
    if (!groups[schema.group]) {
      groups[schema.group] = document.createElement('div');
      groups[schema.group].className = 'dome-param-group';
      groups[schema.group].innerHTML = `<h3>${schema.group}</h3>`;
      container.appendChild(groups[schema.group]);
    }
    
    const row = document.createElement('div');
    row.className = 'dome-param-row';
    
    const label = document.createElement('label');
    label.textContent = schema.label;
    if (schema.locked) {
      label.title = schema.lockNote;
      label.style.opacity = '0.5';
    }
    row.appendChild(label);
    
    if (schema.type === 'slider') {
      const input = document.createElement('input');
      input.type = 'range';
      input.min = schema.min;
      input.max = schema.max;
      input.step = schema.step;
      input.value = params[schema.key];
      input.disabled = !!schema.locked;
      
      const val = document.createElement('span');
      val.className = 'dome-param-val';
      val.textContent = params[schema.key];
      
      input.addEventListener('input', () => {
        params[schema.key] = parseFloat(input.value);
        val.textContent = input.value;
        if (onChange) onChange(schema.key, params[schema.key]);
      });
      
      row.appendChild(input);
      row.appendChild(val);
    } else if (schema.type === 'color') {
      const input = document.createElement('input');
      input.type = 'color';
      const c = params[schema.key];
      input.value = rgbToHex(c[0], c[1], c[2]);
      
      input.addEventListener('input', () => {
        const rgb = hexToRgb(input.value);
        params[schema.key] = [rgb.r / 255, rgb.g / 255, rgb.b / 255, c[3] || 1.0];
        if (onChange) onChange(schema.key, params[schema.key]);
      });
      
      row.appendChild(input);
    }
    
    groups[schema.group].appendChild(row);
  }
  
  // Save button
  const saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save to Attire';
  saveBtn.className = 'dome-param-save';
  saveBtn.addEventListener('click', () => {
    const attirePath = container.dataset.attirePath || 'roster/doc-frank/attires/attire2';
    saveDomeParams(attirePath, params);
  });
  container.appendChild(saveBtn);
}

function rgbToHex(r, g, b) {
  const toHex = (v) => Math.round(v * 255).toString(16).padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function hexToRgb(hex) {
  const v = parseInt(hex.slice(1), 16);
  return { r: (v >> 16) & 255, g: (v >> 8) & 255, b: v & 255 };
}
