#!/usr/bin/env node
/* ============================================================
   Western Heart — Moveset Library ingest (worker 47, 2026-10-22)

   Builds game/data/moveset-library/banks/*.json + index.json from
   the teardown sources already in the repo. Run from the repo root:

       node tools/moveset-library/ingest.mjs

   HONESTY RULES (owner: no guessing, RULES_NO_GUESSING.md):
   - Every value that is estimated is flagged in provenance.estimated.
   - T3 bank rows have no names in the banks (names live in the ARC
     move-list text, not extracted) -> auto-labels, never invented names.
   - T3 per-row Tekken inputs are NOT decoded here (branch target slots
     don't map to rows without the slot table; the #615 fidelity engine
     owns that decode). input=null on T3 entries; ASSEMBLY assigns slots.
   - attack_word/state_word are preserved raw for later decode.
   ============================================================ */

import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
// WH_REPO_ROOT overrides the repo root (lets the ingest run against any checkout)
const ROOT = process.env.WH_REPO_ROOT || join(HERE, '..', '..');
const OUT = join(ROOT, 'game', 'data', 'moveset-library', 'banks');
mkdirSync(OUT, { recursive: true });

const read = (p) => JSON.parse(readFileSync(join(ROOT, p), 'utf8'));
const exists = (p) => existsSync(join(ROOT, p));

/* ---------- axis vocab (mirrors axes.json) ---------- */
const T3_FIGHTERS = [
  'paul','law','lei','king','yoshimitsu','nina','hwoarang','xiaoyu','eddy',
  'jin','julia','kuma','bryan','heihachi','ogre','gunjack','anna',
  'bosconovitch','gon','forestlaw',
];

/* ---------- bank 1: Tekken 3 ---------- */
function ingestT3() {
  const dir = 'teardown/tekken3/movesets';
  const moves = [];
  let banks = 0;
  for (const fighter of T3_FIGHTERS) {
    const p = `${dir}/moveset_${fighter}.json`;
    if (!exists(p)) { console.warn(`[t3] missing ${p} (skipped)`); continue; }
    banks++;
    const bank = read(p);
    const label = fighter.charAt(0).toUpperCase() + fighter.slice(1);
    for (const row of bank.moves) {
      if (!(row.damage > 0)) continue;
      const startup = row.active_first ?? 0;
      const active = Math.max(1, (row.active_last ?? startup) - startup + 1);
      const total = row.stream_frames ?? (startup + active);
      moves.push({
        id: `t3:${fighter}:row:${row.row}`,
        name: `T3 ${label} — row ${row.row} (${row.damage} dmg)`,
        name_status: 'auto-label — real move names live in the ARC move-list text (not extracted); never an invented canon name',
        source: 'tekken3',
        source_game_label: 'Tekken 3 (PSX SLUS_004.02, divmot bank)',
        source_character: label,
        anim_ref: `t3:${fighter}:row:${row.row}`,
        type: row.attack_class === 1 ? 'throw' : 'strike',
        subtype: null,
        position: 'standing',
        orientation: 'forward',
        input: null,
        input_slots: [],
        frames: { startup, active, recovery: Math.max(0, total - (startup + active)), total },
        damage_raw: row.damage,
        damage: Math.max(1, Math.round(row.damage / 3)),
        hit_level: null,
        limb: null,
        properties: row.attack_class === 1 ? ['throw'] : [],
        wh: { knock: 2.2, soulGain: 8, heavy: row.damage >= 24 },
        provenance: {
          note: 'decoded T3 motion bank row; frames/damage real. input + hit_level NOT decoded (branch target slots need the slot table — fidelity engine lane).',
          estimated: ['damage (WH scale)', 'hit_level', 'input', 'position', 'subtype', 'limb'],
          t3_row: row.row, t3_bank: bank.bank,
          state_word: row.state_word, attack_word: row.attack_word,
          hit_freeze: row.hit_freeze ?? 0,
        },
      });
    }
  }
  return { bank: 't3', game: 'tekken3', banks, moves };
}

/* ---------- bank 2: wrestling (No Mercy mat-kings DB) ---------- */
const MK_CATEGORY_MAP = [
  // [regex, type, position, properties]
  [/weak arm striking|strong striking/i, 'strike', 'standing', []],
  [/weak leg striking/i, 'strike', 'standing', []],
  [/running attack/i, 'strike', 'running', []],
  [/turnbuckle attack|tree of woe/i, 'strike', 'corner', []],
  [/counter punch|counter kick|enziguiri/i, 'counter', 'standing', ['counter-hit']],
  [/front .*grapple|back .*grapple|irish whip grapple|test of strength/i, 'grapple', 'standing', []],
  [/special grapple|front special|back special/i, 'grapple', 'standing', ['finisher-candidate']],
  [/ground .*grapple|ground attack/i, 'grapple', 'grounded', []],
  [/turnbuckle grapple/i, 'grapple', 'corner', []],
  [/recovering attack/i, 'strike', 'grounded', []],
  [/evasion/i, 'transition', 'standing', []],
];

function ingestWrestling() {
  const p = 'moveset-library/movesets/mat-kings-move-database.json';
  const moves = [];
  if (!exists(p)) { console.warn('[wrestling] missing mat-kings DB (skipped)'); return { bank: 'wrestling', game: 'wwf_no_mercy', banks: 0, moves }; }
  const db = read(p);
  const powerToDamage = { F: 2, E: 3, D: 5, C: 8, B: 12, A: 16, S: 22 };
  for (const m of db.moves) {
    let type = 'grapple', position = 'standing', props = [];
    for (const [re, t, pos, pr] of MK_CATEGORY_MAP) {
      if (re.test(m.category || '')) { type = t; position = pos; props = [...pr]; break; }
    }
    const isThrow = /slam|throw|suplex|driver|bomb|piledriver/i.test(m.name || '');
    if (isThrow && type === 'grapple') { type = 'throw'; props.push('throw'); }
    if (/dive|top rope|senton|frog splash|swanton|shooting star|450|moonsault/i.test(m.name || '')) {
      type = 'aerial'; position = 'airborne'; props.push('aerial');
    }
    if (m.ko) props.push('ko');
    if (m.bleed) props.push('bleed');
    moves.push({
      id: `wrestling:${m.move_id.toLowerCase()}`,
      name: m.name || m.source_label || m.move_id,
      name_status: m.name ? 'DB label from No Mercy re-docs' : 'provisional',
      source: 'wwf_no_mercy',
      source_game_label: 'WWF No Mercy (N64) — mat-kings DB',
      source_character: null,
      anim_ref: m.anim_ref || null,
      type, subtype: null, position,
      orientation: 'forward',
      input: m.tekken_input && m.tekken_input !== 'NONE' ? m.tekken_input : null,
      input_slots: m.tekken_input && m.tekken_input !== 'NONE' ? [m.tekken_input] : [],
      frames: { startup: null, active: null, recovery: null, total: m.nframes ?? null },
      damage_raw: null,
      damage: powerToDamage[m.power] ?? 4,
      hit_level: type === 'throw' ? 'throw' : null,
      limb: null,
      properties: props,
      wh: { knock: 2.2, soulGain: 8, heavy: (powerToDamage[m.power] ?? 0) >= 12 },
      provenance: {
        note: 'No Mercy re-docs move DB; Tekken input wired per federation rule (wrestling -> Tekken inputs). Power tier -> WH damage is estimated.',
        estimated: ['damage (WH scale)', 'hit_level', 'subtype', 'limb'],
        mk_move_id: m.move_id, mk_category: m.category, mk_power: m.power,
        mk_slot_eligibility: m.slot_eligibility || [],
      },
    });
  }
  return { bank: 'wrestling', game: 'wwf_no_mercy', banks: 1, moves };
}

/* ---------- bank 3: WMXIX clips ---------- */
function ingestWmxix() {
  const p = 'moveset-library/movesets/WMXIX-MOVES.json';
  const moves = [];
  if (!exists(p)) { console.warn('[wmxix] missing (skipped)'); return { bank: 'wmxix', game: 'wwe_wrestlemania_xix', banks: 0, moves }; }
  const db = read(p);
  const inputMap = (db._meta && db._meta.tekken_input_map) || {};
  for (const m of db.moves || []) {
    moves.push({
      id: `wmxix:${String(m.move_id).toLowerCase()}`,
      name: m.move_name || m.move_id,
      name_status: m.name_status || 'provisional registry label — per-clip move identity not yet decoded',
      source: 'wwe_wrestlemania_xix',
      source_game_label: 'WWE WrestleMania XIX (GC) — YANM clips',
      source_character: null,
      anim_ref: m.anim_ref || null,
      type: 'grapple', subtype: null, position: 'standing',
      orientation: 'forward',
      input: null, input_slots: [],
      frames: { startup: null, active: null, recovery: null, total: null },
      damage_raw: null, damage: 6, hit_level: null, limb: null,
      properties: [],
      wh: { knock: 2.2, soulGain: 8, heavy: false },
      provenance: {
        note: 'WMXIX animation clip registered to the library; per-clip move identity pending teardown hash-set mapping.',
        estimated: ['damage (WH scale)', 'type', 'position', 'input'],
        wmxix_move_id: m.move_id, wmxix_canon_id: m.canon_id || null,
        wmxix_slot_eligibility: m.slot_eligibility || [],
        federation_input_map: inputMap,
      },
    });
  }
  return { bank: 'wmxix', game: 'wwe_wrestlemania_xix', banks: 1, moves };
}

/* ---------- bank 4: DOA federation ---------- */
function ingestDoa() {
  const dir = 'game/assets/movesets';
  const files = ['doa-bass', 'doa-kasumi', 'doa-hayabusa', 'doa-ayane', 'doa-tina', 'doa-jannlee'];
  const moves = [];
  for (const f of files) {
    const p = `${dir}/${f}.json`;
    if (!exists(p)) { console.warn(`[doa] missing ${p} (skipped)`); continue; }
    const d = read(p);
    for (const [key, m] of Object.entries(d.moves || {})) {
      moves.push({
        id: `doa:${f.replace('doa-', '')}:${key.replace(/[^a-z0-9+]+/gi, '-').toLowerCase()}`,
        name: m.name || key,
        name_status: 'DOA community movelist name',
        source: 'doa',
        source_game_label: 'Dead or Alive (federation conversion)',
        source_character: d.tekken_base || f,
        anim_ref: m.anim_ref || null,
        type: m.move_class === 'throw' ? 'throw' : m.move_class === 'signature' ? 'special' : 'strike',
        subtype: null,
        position: /^d\+|^d\/b|^d\/f/.test(key) ? 'crouching' : /b\+/.test(key) ? 'back-turned' : 'standing',
        orientation: 'forward',
        input: m.input || key, input_slots: m.input_slots || [key],
        frames: {
          startup: m.startup != null ? Math.round(m.startup * 60) : null,
          active: m.active != null ? Math.round(m.active * 60) : null,
          recovery: m.recovery != null ? Math.round(m.recovery * 60) : null,
          total: null,
        },
        damage_raw: m.doa_damage ?? null,
        damage: m.damage ?? null,
        hit_level: m.isGrab || m.throw ? 'throw' : null,
        limb: m.limb || null,
        properties: [
          ...(m.throw || m.isGrab ? ['throw'] : []),
          ...(m.unblockable ? ['unblockable'] : []),
          ...(m.heavy ? ['heavy-hit'] : []),
        ],
        wh: { knock: m.knock ?? 2.2, soulGain: m.soulGain ?? 8, heavy: !!m.heavy },
        provenance: {
          note: 'DOA federation conversion (Tekken-notation federation rule); frames converted from seconds@60fps.',
          estimated: ['position', 'hit_level', 'subtype'],
          doa_input: m.doa_input || null, doa_move: m.doa_move || null,
          source_file: `${f}.json`, source_key: key,
        },
      });
    }
    for (const [si, s] of (d.strings || []).entries()) {
      const sInput = typeof s === 'string' ? s : (s.input || s.name);
      const sName = typeof s === 'string' ? `string ${s}` : (s.name || `string ${s.input}`);
      const slug = String(sInput || `string-${si}`).replace(/[^a-z0-9+]+/gi, '-').toLowerCase();
      moves.push({
        id: `doa:${f.replace('doa-', '')}:string:${slug}`,
        name: sName,
        name_status: 'DOA community movelist name',
        source: 'doa', source_game_label: 'Dead or Alive (federation conversion)',
        source_character: d.tekken_base || f,
        anim_ref: (typeof s === 'object' && s.anim_ref) || null,
        type: 'strike', subtype: 'string', position: 'standing', orientation: 'forward',
        input: typeof s === 'string' ? s : (s.input || null),
        input_slots: typeof s === 'string' ? [s] : (s.input_slots || []),
        frames: { startup: null, active: null, recovery: null, total: null },
        damage_raw: null, damage: (typeof s === 'object' && s.damage) ?? null, hit_level: null, limb: null,
        properties: ['string'],
        wh: { knock: 2.2, soulGain: 8, heavy: false },
        provenance: { note: 'DOA string (multi-hit).', estimated: ['damage (WH scale)'], components: (typeof s === 'object' && (s.components || s.hits)) || [] },
      });
    }
  }
  return { bank: 'doa', game: 'doa', banks: files.length, moves };
}

/* ---------- bank 5: VF federation (+ vf5 pending) ---------- */
function ingestVf() {
  const dir = 'game/assets/movesets';
  const files = ['vf-akira', 'vf-sarah', 'vf-kage'];
  const moves = [];
  for (const f of files) {
    const p = `${dir}/${f}.json`;
    if (!exists(p)) { console.warn(`[vf] missing ${p} (skipped)`); continue; }
    const d = read(p);
    for (const [key, m] of Object.entries(d.moves || {})) {
      moves.push({
        id: `vf:${f.replace('vf-', '')}:${key.replace(/[^a-z0-9+]+/gi, '-').toLowerCase()}`,
        name: m.name || key,
        name_status: 'VF federation conversion name',
        source: 'vf',
        source_game_label: 'Virtua Fighter (federation conversion)',
        source_character: d.tekken_base || f,
        anim_ref: m.anim_ref || null,
        type: m.move_class === 'throw' ? 'throw' : m.move_class === 'signature' ? 'special' : 'strike',
        subtype: null,
        position: 'standing', orientation: 'forward',
        input: m.input || key, input_slots: m.input_slots || [key],
        frames: {
          startup: m.startup != null ? Math.round(m.startup * 60) : null,
          active: m.active != null ? Math.round(m.active * 60) : null,
          recovery: m.recovery != null ? Math.round(m.recovery * 60) : null,
          total: null,
        },
        damage_raw: null, damage: m.damage ?? null, hit_level: null, limb: m.limb || null,
        properties: [...(m.throw || m.isGrab ? ['throw'] : []), ...(m.unblockable ? ['unblockable'] : [])],
        wh: { knock: m.knock ?? 2.2, soulGain: m.soulGain ?? 8, heavy: !!m.heavy },
        provenance: { note: 'VF federation conversion (Tekken-notation federation rule).', estimated: ['position', 'hit_level', 'subtype'], source_file: `${f}.json`, source_key: key },
      });
    }
  }
  return { bank: 'vf', game: 'virtua_fighter', banks: files.length, moves };
}

<<<<<<< 547a13642a84bfffef4dd2d695d00ca2d44cce3c
/* ---------- bank 6: VF5 federation (live base kits) ---------- */
function ingestVf5() {
  const dir = 'game/assets/movesets';
  // file -> library fighter slug (matches manifests' base.character)
  const files = { 'vf-elblaze': 'el-blaze', 'vf-jeffry': 'jeffry', 'vf-wolf': 'wolf', 'vf-leifei': 'lei-fei' };
  const moves = [];
  for (const [f, slug] of Object.entries(files)) {
    const p = `${dir}/${f}.json`;
    if (!exists(p)) { console.warn(`[vf5] missing ${p} (skipped)`); continue; }
    const d = read(p);
    for (const [key, m] of Object.entries(d.moves || {})) {
      const idSlug = key.replace(/[^a-z0-9+]+/gi, '-').toLowerCase();
      moves.push({
        id: `vf5:${slug}:${idSlug}`,
        name: m.name || key,
        name_status: 'VF5 community movelist name (federation conversion)',
        source: 'vf5',
        source_game_label: 'Virtua Fighter 5 (federation conversion)',
        source_character: d.display || d.tekken_base || f,
        anim_ref: m.anim_ref || null,
        type: m.move_class === 'throw' ? 'throw' : m.move_class === 'signature' ? 'special' : 'strike',
        subtype: null,
        position: 'standing', orientation: 'forward',
        input: m.input || key, input_slots: m.input_slots || [key],
        frames: {
          startup: m.startup != null ? Math.round(m.startup * 60) : null,
          active: m.active != null ? Math.round(m.active * 60) : null,
          recovery: m.recovery != null ? Math.round(m.recovery * 60) : null,
          total: null,
        },
        damage_raw: null, damage: m.damage ?? null, hit_level: null, limb: m.limb || null,
        properties: [...(m.throw || m.isGrab ? ['throw'] : []), ...(m.unblockable ? ['unblockable'] : [])],
        wh: { knock: m.knock ?? 2.2, soulGain: m.soulGain ?? 8, heavy: !!m.heavy },
        provenance: {
          note: 'VF5 federation conversion (Tekken-notation federation rule). Seeded from community movelists; worker 45 extraction may extend/replace rows.',
          estimated: ['position', 'hit_level', 'subtype'],
          vf_source: d.vf_source || null, source_file: `${f}.json`, source_key: key,
        },
      });
    }
  }
  return { bank: 'vf5', game: 'virtua_fighter_5', banks: Object.keys(files).length, moves };
}

/* ---------- main ---------- */
const banks = [ingestT3(), ingestWrestling(), ingestWmxix(), ingestDoa(), ingestVf(), ingestVf5()];
=======
/* ---------- main ---------- */
const banks = [ingestT3(), ingestWrestling(), ingestWmxix(), ingestDoa(), ingestVf()];
>>>>>>> d95250df

for (const b of banks) {
  writeFileSync(join(OUT, `${b.bank}.json`), JSON.stringify({ bank: b.bank, game: b.game, count: b.moves.length, moves: b.moves }, null, 1));
  console.log(`[ok] ${b.bank}: ${b.moves.length} moves (${b.banks} source banks)`);
}

const index = {
  schema: 'moveset-library/v1',
  built: new Date().toISOString().slice(0, 10),
  builder: 'tools/moveset-library/ingest.mjs (worker 47)',
  honesty: 'estimated fields are flagged per-entry in provenance.estimated; nothing is invented as canon.',
  banks: banks.map((b) => ({
    id: b.bank, game: b.game, file: `banks/${b.bank}.json`,
    moves: b.moves.length, source_banks: b.banks,
  })),
  pending_banks: [
    {
<<<<<<< 547a13642a84bfffef4dd2d695d00ca2d44cce3c
      id: 'vf5-motion',
      game: 'virtua_fighter_5',
      status: 'partial — base kits live from federation conversions (vf-elblaze/jeffry/wolf/leifei.json); worker 45 motion extraction may extend/replace rows',
=======
      id: 'vf5', game: 'virtua_fighter_5',
      status: 'pending — worker 45 extraction in progress; format contract: docs/handoffs/moveset-library-vf5-format.md',
      expected_characters: ['jeffry', 'wolf', 'el-blaze', 'lei-fei'],
>>>>>>> d95250df
    },
    { id: 't7', game: 'tekken_7', status: 'pending — T7 teardown rows land here when extraction completes' },
    { id: 'ttt2', game: 'tekken_tag_2', status: 'pending' },
    { id: 't6', game: 'tekken_6', status: 'pending — decrypt6 lane DATA401' },
    { id: 'soulcalibur', game: 'soulcalibur', status: 'pending — approved systems only' },
    { id: 'urban_reign', game: 'urban_reign', status: 'pending — PPK binary RE' },
    { id: 'bloody_roar', game: 'bloody_roar', status: 'pending — beast transformations' },
    { id: 'sf', game: 'street_fighter', status: 'pending — approved systems only' },
    { id: 'def_jam', game: 'def_jam', status: 'pending' },
  ],
  total_moves: banks.reduce((n, b) => n + b.moves.length, 0),
};
writeFileSync(join(OUT, '..', 'index.json'), JSON.stringify(index, null, 1));
console.log(`[ok] index: ${index.total_moves} total moves`);
