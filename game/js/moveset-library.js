/* ============================================================
   WESTERN HEART — Moveset Library assembler (worker 47, 2026-10-22)

   Central moveset library -> per-fighter assembled movesets.

   - Loads game/data/moveset-library/index.json + banks/*.json
   - Loads game/data/movesets/<fighter>.json manifests
   - Enforces the MOVESET SOURCE LAW (claimed-map.json): refuses
     claimed Tekken banks unless an approved exception names them
   - Resolves manifest entries (library_id + slot + overrides) into
     v2 moveset-editor-contract moves (docs/movesets/MOVESET-SCHEMA.md),
     the same shape game/js/movesets.js reads from
     game/assets/movesets/{fighter}.json
   - Pending banks (vf5 until worker 45 lands) resolve to honest
     {pending:true} placeholders — the manifest stays valid, the
     fighter is playable from the overlay moves.

   Usage (browser, ES module):
     import { assembleFighter } from './js/moveset-library.js';
     const kit = await assembleFighter('pablo'); // {fighter, moves, strings, pending, report}

   Usage (node):
     node --input-type=module -e "
       import('./game/js/moveset-library.js').then(async m => {
         const kit = await m.assembleFighter('pablo', {root: '.'});
         console.log(kit.report);
       });"
   ============================================================ */

const LIB_ROOT = 'game/data/moveset-library';
const MANIFEST_ROOT = 'game/data/movesets';

let _lib = null;      // {index, banks: {id: bankData}, byId: Map}
let _claimed = null;

async function fetchJson(url, root) {
  if (typeof fetch !== 'undefined' && !root) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`fetch ${url}: ${r.status}`);
    return r.json();
  }
  // node path
  const { readFileSync } = await import('node:fs');
  const { join } = await import('node:path');
  const base = root || process.cwd();
  return JSON.parse(readFileSync(join(base, url), 'utf8'));
}

export async function loadLibrary(opts = {}) {
  if (_lib && !opts.reload) return _lib;
  const root = opts.root || null;
  const index = await fetchJson(`${LIB_ROOT}/index.json`, root);
  const banks = {};
  const byId = new Map();
  for (const b of index.banks) {
    try {
      const data = await fetchJson(`${LIB_ROOT}/${b.file}`, root);
      banks[b.id] = data;
      for (const m of data.moves || []) {
        if (byId.has(m.id)) {
          console.warn(`[moveset-library] duplicate id ${m.id} (bank ${b.id}) — first wins`);
          continue;
        }
        byId.set(m.id, { ...m, _bank: b.id });
      }
    } catch (e) {
      console.warn(`[moveset-library] bank ${b.id} failed to load: ${e.message}`);
      banks[b.id] = { bank: b.id, count: 0, moves: [], _failed: true };
    }
  }
  _lib = { index, banks, byId };
  return _lib;
}

export async function loadClaimedMap(opts = {}) {
  if (_claimed && !opts.reload) return _claimed;
  _claimed = await fetchJson(`${LIB_ROOT}/claimed-map.json`, opts.root || null);
  return _claimed;
}

/* ---- source-law enforcement ---- */
const BANK_GAME = { t3: 'tekken', wrestling: 'wwf_no_mercy', wmxix: 'wwe_wmxix', doa: 'doa', vf: 'vf', vf5: 'vf5', wh: 'wh' };

export function checkSourceLaw(manifest, claimed) {
  const issues = [];
  const exceptions = new Set((claimed.approved_exceptions || []).map((e) => e.fighter.toLowerCase()));
  if (exceptions.has(String(manifest.fighter).toLowerCase())) return { passed: true, issues };
  // Tekken bank ids look like t3:<fighter>:row:<n> — the <fighter> is a T3 roster name.
  // The claimed map keys are display names (King, Eddy Gordo...). Map T3 slugs to display names.
  const T3_TO_DISPLAY = {
    king: 'King', paul: 'Paul Phoenix', law: 'Marshall Law', lei: 'Lei Wulong',
    yoshimitsu: 'Yoshimitsu', nina: 'Nina Williams', hwoarang: 'Hwoarang',
    xiaoyu: 'Ling Xiaoyu', eddy: 'Eddy Gordo', jin: 'Jin Kazama', julia: 'Julia Chang',
    kuma: 'Kuma', bryan: 'Bryan Fury', heihachi: 'Heihachi Mishima', ogre: 'True Ogre',
    gunjack: 'Jack', anna: 'Anna Williams', bosconovitch: 'Bosconovitch',
    gon: 'Gon', forestlaw: 'Forest Law',
  };
  const seen = new Set();
  const checkId = (libId, where) => {
    if (!libId || seen.has(libId)) return;
    seen.add(libId);
    const [ns, char] = libId.split(':');
    if (ns === 't3' && char) {
      const display = T3_TO_DISPLAY[char] || char;
      const claim = claimed.claimed && claimed.claimed[display];
      if (claim) {
        issues.push(`${where}: ${libId} pulls from CLAIMED fighter ${display} (claimed by ${claim.by}) — refused by moveset source law`);
      }
    }
  };
  for (const m of manifest.moves || []) checkId(m.library_id, `move slot ${m.slot}`);
  return { passed: issues.length === 0, issues };
}

/* ---- library entry -> v2 contract move ---- */
function toV2Move(entry, slot, overrides = {}) {
  const f = entry.frames || {};
  const secs = (n) => (n == null ? null : +(n / 60).toFixed(3));
  const props = new Set([...(entry.properties || []), ...((overrides.properties) || [])]);
  const move = {
    name: overrides.name || entry.name,
    input: slot || entry.input,
    input_slots: [slot || entry.input].filter(Boolean),
    move_class: entry.type === 'throw' ? 'throw' : entry.type === 'special' ? 'special' : entry.type === 'aerial' ? 'special' : 'strike',
    anim_ref: entry.anim_ref,
    damage: overrides.damage ?? entry.damage,
    startup: secs(f.startup), active: secs(f.active), recovery: secs(f.recovery),
    limb: entry.limb,
    heavy: !!(entry.wh && entry.wh.heavy),
    knock: (entry.wh && entry.wh.knock) ?? 2.2,
    soulGain: (entry.wh && entry.wh.soulGain) ?? 8,
    throw: props.has('throw'),
    isGrab: props.has('throw'),
    unblockable: props.has('unblockable'),
    note: overrides.note || (entry.provenance && entry.provenance.note) || null,
    library_id: entry.id,
    library_source: entry.source,
    properties: [...props],
  };
  if (overrides.whack) Object.assign(move, overrides.whack);
  return move;
}

<<<<<<< 547a13642a84bfffef4dd2d695d00ca2d44cce3c
/* Fighters such as DEMONIO ship a complete kit in game/assets/movesets/
   (the runtime path movesets.js uses) and have no library manifest in
   game/data/movesets/. Fall back to the assets kit instead of failing. */
const ASSET_KIT_ROOT = 'game/assets/movesets';

export async function loadManifest(fighter, opts = {}) {
  try {
    return await fetchJson(`${MANIFEST_ROOT}/${fighter}.json`, opts.root || null);
  } catch (e) {
    const kit = await fetchJson(`${ASSET_KIT_ROOT}/${fighter}.json`, opts.root || null);
    return { ...kit, _assetKit: true };
  }
=======
export async function loadManifest(fighter, opts = {}) {
  return fetchJson(`${MANIFEST_ROOT}/${fighter}.json`, opts.root || null);
>>>>>>> d95250df
}

/* ---- assemble one fighter ---- */
export async function assembleFighter(fighter, opts = {}) {
  const lib = await loadLibrary(opts);
  const claimed = await loadClaimedMap(opts);
  const manifest = typeof fighter === 'string' ? await loadManifest(fighter, opts) : fighter;
<<<<<<< 547a13642a84bfffef4dd2d695d00ca2d44cce3c
  if (manifest && manifest._assetKit && manifest.moves && !Array.isArray(manifest.moves)) {
    // Already a full schema-v3 kit (game/assets/movesets) — nothing to assemble.
    const { _assetKit, ...kit } = manifest;
    return { ...kit, pending: [], unresolved: [],
      report: { fighter: kit.fighter, display: kit.display, assembled: Object.keys(kit.moves).length, source: `${ASSET_KIT_ROOT}/${kit.fighter}.json` } };
  }
=======
>>>>>>> d95250df

  const law = checkSourceLaw(manifest, claimed);
  const moves = {};
  const pending = [];
  const unresolved = [];

  // base kit (usually pending until its bank lands)
  const base = manifest.base || {};
  if (base.bank) {
    const bankKnown = lib.banks[base.bank] && !lib.banks[base.bank]._failed && (lib.banks[base.bank].moves || []).length > 0;
    if (!bankKnown) {
      pending.push({ bank: base.bank, character: base.character, status: base.status || 'pending', note: base.note || '' });
    } else {
<<<<<<< 547a13642a84bfffef4dd2d695d00ca2d44cce3c
      const prefix = `${base.bank}:${base.character}:`.toLowerCase();
      for (const m of lib.banks[base.bank].moves) {
        if (base.character && !m.id.toLowerCase().startsWith(prefix)) continue;
=======
      for (const m of lib.banks[base.bank].moves) {
        if (base.character && m.source_character && m.source_character.toLowerCase() !== String(base.character).toLowerCase()) continue;
>>>>>>> d95250df
        if (m.input && !moves[m.input]) moves[m.input] = toV2Move(m, m.input);
      }
    }
  }

  // overlay moves from the manifest
  for (const spec of manifest.moves || []) {
    const entry = lib.byId.get(spec.library_id);
    if (!entry) {
      unresolved.push(spec.library_id);
      continue;
    }
    const slot = spec.slot || entry.input;
    if (!slot) {
      unresolved.push(`${spec.library_id} (no slot assigned and entry has no input)`);
      continue;
    }
    moves[slot] = toV2Move(entry, slot, { ...(spec.overrides || {}), note: spec.note });
  }

  const report = {
    fighter: manifest.fighter,
    display: manifest.display,
    library_moves: lib.byId.size,
    assembled: Object.keys(moves).length,
    pending_banks: pending,
    unresolved,
    source_law: law,
    assembly_notes: manifest.assembly_notes || '',
  };

  return {
    fighter: manifest.fighter,
    display: manifest.display,
    schema_version: 3,
    tekken_base: base.character ? `${base.bank}:${base.character}` : 'library-assembled',
    proxy: pending.length > 0,
    proxy_note: pending.length ? `base kit pending: ${pending.map((p) => `${p.bank}:${p.character}`).join(', ')}` : null,
    moves,
    strings: manifest.strings || [],
    specials: manifest.specials || [],
    pending,
    unresolved,
    report,
  };
}

/* ---- node CLI: node game/js/moveset-library.js <fighter> ---- */
const isMain = typeof process !== 'undefined' && process.argv && process.argv[1] && process.argv[1].endsWith('moveset-library.js');
if (isMain) {
  const fighter = process.argv[2] || 'pablo';
  assembleFighter(fighter, { root: process.cwd() })
    .then((kit) => {
      console.log(JSON.stringify(kit.report, null, 1));
      if (kit.report.source_law.passed === false) process.exitCode = 2;
    })
    .catch((e) => { console.error('assemble failed:', e.message); process.exitCode = 1; });
}
