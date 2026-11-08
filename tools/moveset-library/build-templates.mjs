#!/usr/bin/env node
/* ============================================================
   WESTERN HEART — moveset template library builder
   tools/moveset-library/build-templates.mjs (2026-11-08, lane:
   moveset template library + creation system)

   Regenerates the GENERATED rows of
   game/data/moveset-templates/index.json from MEASURED data only:
   - per-character banks in game/data/moveset-library/banks/*.json
     (counts read from the bank files, never typed in)
   - Tekken 7 frame data in game/data/t7-frame-data/*.json
     (44 files, 6,909 moves measured 2026-11-08)
   - Tekken 8 frame tables in game/data/t8_frame_tables.json
     (41 chars, 6,411 notation-keyed rows measured 2026-11-08)
   - pending-ingest rows for donor games whose teardown files exist
     in the repo but have no ingested bank yet (counts are teardown
     file counts from `git ls-tree -r`, cited per row; per-character
     counts are NOT invented — the row says UNMEASURED where the
     decode has not landed)

   Existing hand-written rows (the 2026-11-05 templates) are kept
   verbatim. Generated rows are idempotent: re-running replaces
   rows whose id starts with a generated prefix.
   Template ids are generic hints (PIPELINE-LAW §2): never a
   franchise display name on the WH roster. `source_character` is
   provenance only — it names where the data came from, it is not
   a roster name and never reaches a player-facing screen.

   Usage: node tools/moveset-library/build-templates.mjs [--check]
   --check exits non-zero if the index on disk differs from what
   this script would write (CI-friendly, no write).
   ============================================================ */

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const INDEX = join(ROOT, 'game/data/moveset-templates/index.json');
const BANKS = join(ROOT, 'game/data/moveset-library/banks');
const T7_DIR = join(ROOT, 'game/data/t7-frame-data');
const T8_FILE = join(ROOT, 'game/data/t8_frame_tables.json');

const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));

function bankTemplates() {
  const out = [];
  for (const bank of ['t3', 'doa', 'vf', 'vf5']) {
    const data = readJson(join(BANKS, `${bank}.json`));
    const perChar = new Map();
    for (const m of data.moves || []) {
      const c = m.source_character || 'POOL';
      if (!perChar.has(c)) perChar.set(c, { moves: 0, prefix: String(m.id).split(':').slice(0, 2).join(':') });
      perChar.get(c).moves += 1;
    }
    for (const [character, { moves, prefix }] of [...perChar.entries()].sort()) {
      out.push({
        id: `${bank}-${slug(character)}`,
        hint: `${bank.toUpperCase()} bank character — ${moves} measured moves in game/data/moveset-library/banks/${bank}.json`,
        source_game: bank === 't3' ? 'tekken3' : bank === 'doa' ? 'doa' : bank === 'vf' ? 'virtua_fighter' : 'virtua_fighter_5',
        source_bank: bank,
        source_character: character,
        library_prefix: prefix,
        moves,
        status: 'template',
        attached_to: [],
        pointers: [`game/data/moveset-library/banks/${bank}.json`],
      });
    }
  }
  return out;
}

function poolTemplates() {
  const pools = [];
  for (const [bank, game, note] of [
    ['wrestling', 'wwf_no_mercy', 'generic No Mercy move pool — per-wrestler grouping not yet decoded, so no per-character template exists yet'],
    ['wmxix', 'wwe_wrestlemania_xix', 'per-clip pool — per-clip identity pending (game/data/moveset-library/wmxix-verified.json: 115 wired to SHOW, 54 provisional hidden, 0 to combat)'],
  ]) {
    const data = readJson(join(BANKS, `${bank}.json`));
    pools.push({
      id: `${bank}-pool`,
      hint: `${bank.toUpperCase()} move pool — ${(data.moves || []).length} measured moves. ${note}`,
      source_game: game,
      source_bank: bank,
      source_character: null,
      moves: (data.moves || []).length,
      status: 'pool',
      attached_to: [],
      pointers: [`game/data/moveset-library/banks/${bank}.json`],
    });
  }
  return pools;
}

function t7Templates() {
  const out = [];
  for (const f of readdirSync(T7_DIR).filter((x) => x.endsWith('.json')).sort()) {
    const data = readJson(join(T7_DIR, f));
    const moves = (data.moves || []).length;
    const fighter = f.replace(/^t7-/, '').replace(/-lp-rp-lk-rk\.json$/, '');
    out.push({
      id: `t7-frame-${slug(fighter)}`,
      hint: `T7 frame data only — ${moves} measured rows in game/data/t7-frame-data/${f}. No animation IDs in this file (anim_ref null); frame data, not a playable bank.`,
      source_game: 'tekken7',
      source_bank: 't7-frame-data',
      source_character: fighter,
      moves,
      status: 'frame-data-only',
      attached_to: [],
      pointers: [`game/data/t7-frame-data/${f}`],
    });
  }
  return out;
}

function t8Templates() {
  const data = readJson(T8_FILE);
  return Object.keys(data.chars).sort().map((fighter) => ({
    id: `t8-frame-${slug(fighter)}`,
    hint: `T8 frame table only — ${Object.keys(data.chars[fighter]).length} measured notation-keyed rows in game/data/t8_frame_tables.json. No animation IDs; frame data, not a playable bank.`,
    source_game: 'tekken8',
    source_bank: 't8-frame-tables',
    source_character: fighter,
    moves: Object.keys(data.chars[fighter]).length,
    status: 'frame-data-only',
    attached_to: [],
    pointers: ['game/data/t8_frame_tables.json'],
  }));
}

/* Donor games with teardown files in the repo but no ingested bank
   yet. `teardown_files` is the `git ls-tree -r` count measured
   2026-11-08; `moves` is null (UNMEASURED) until the ingest lands —
   no per-character row is invented for any of these. */
const PENDING = [
  {
    id: 'urban-reign-pending',
    hint: 'Urban Reign — 72 char PPK slots + 72 textured GLBs, 285 banks / 3,357 motions, 484 named moves per TEARDOWN-PART-C; 4,188 files in teardown/urban-reign. No ingested bank yet (stage/mission PPKs not decoded); 31 movesets already wired into game/ as UR kits.',
    source_game: 'urban_reign', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/urban-reign', 'TEARDOWN-PART-C-URBAN-REIGN.md'],
  },
  {
    id: 'urban-reign-redux-pending',
    hint: 'Urban Reign Redux v0.5 — Mod Manager 0.5 + Editor 0.5 fetched and hash-verified from the author (see ~/workspace/urban-reign-redux/INVENTORY.md); all-in-one Drive link quota-blocked, retry Sun Nov 8 ~7:18 PM CST. Per-fighter counts UNMEASURED until the disc build lands on Windows.',
    source_game: 'urban_reign_redux', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['~/workspace/urban-reign-redux/INVENTORY.md'],
  },
  {
    id: 'soulcalibur2-pending',
    hint: 'Soulcalibur II — 18 named textured fighters + 22 GLB models + 41 stage GLBs (237 files in teardown/soulcalibur-2). No moveset bank ingested yet.',
    source_game: 'soulcalibur2', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/soulcalibur-2'],
  },
  {
    id: 'def-jam-pending',
    hint: 'Def Jam Fight For NY — 271 files in teardown/def-jam-fight-for-ny (EAGL spec + surgical .o/.ssh extracts, not decoded to models/anims yet). Per-character counts UNMEASURED.',
    source_game: 'def_jam_ffny', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/def-jam-fight-for-ny'],
  },
  {
    id: 'street-fighter-3d-pending',
    hint: '3D Street Fighter (EX series) — docs/catalog only in repo (58 files EX Plus Alpha, 2 EX2 Plus, 1 EX3, 4 SFV). No extracted movesets; SFV pull blocked per teardown catalog. Per-character counts UNMEASURED.',
    source_game: 'street_fighter_ex', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/street-fighter-3d-games'],
  },
  {
    id: 'tekken6-pending',
    hint: 'Tekken 6 (PSP) — 3,849 files in teardown/tekken6; 18 fighters x 3 versions movesets (54 files), models encrypted (DATA401). No ingested bank yet.',
    source_game: 'tekken6', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/tekken6'],
  },
  {
    id: 'ttt2-pending',
    hint: 'Tekken Tag Tournament 2 — 56 files in teardown/tekken-tag-tournament-2; roster 59 fighters / 29 stages in docs only, containers not decoded. Per-character counts UNMEASURED.',
    source_game: 'tekken_tag_tournament_2', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/tekken-tag-tournament-2'],
  },
  {
    id: 'pro-wrestling-2019-pending',
    hint: 'Pro-wrestling game (2019 release) — 1,678 files extracted in teardown/wwe2k19 (753.7 MB, .yobj/.bin/.dds), raw, needs WMXIX-style decode path. The CAW + Create-A-Moveset layout is already documented (customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md, moveset name list: 5,581 names). Per-character move counts UNMEASURED.',
    source_game: 'pro-wrestling-2019', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/wwe2k19', 'customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md'],
  },
  {
    id: 'pro-wrestling-2020-2022-pending',
    hint: 'Pro-wrestling games (2020 / 2022 releases) — readme only in repo (1 file each in teardown/wwe2k20, teardown/wwe2k22); the 2022 release is the newest wrestling game Jay owns on Steam (app 1255630) and the creation-suite source of record, but no teardown/archive exists in the repo. Nothing measured yet.',
    source_game: 'pro-wrestling-2020-2022', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['teardown/wwe2k20', 'teardown/wwe2k22', 'docs/tech/STEAM-LIBRARY.md'],
  },
  {
    id: 'devil-within-pending',
    hint: 'Devil Within (Tekken 5) — all 242 files inventoried on branch dw-decode (commit 06eef2ea), 0 bytes decoded; blocked on missing archive bytes (TK5DATA*.BIN). Per-character move counts UNMEASURED until the archive pull lands.',
    source_game: 'devil_within', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['~/workspace/western-heart-audit/TEARDOWN-PART-B-DEVIL-WITHIN.md'],
  },
  {
    id: 'brutal-fist-pending',
    hint: 'Brutal Fist — identification in progress by a separate agent (deliverable ~/workspace/western-heart-audit/BRUTAL-FIST-PULLIN.md, not landed as of 2026-11-08 ~02:30). No roster, no counts yet — this row is a placeholder, not a template.',
    source_game: 'brutal_fist', source_bank: null, source_character: null, moves: null,
    status: 'pending-ingest', attached_to: [],
    pointers: ['~/workspace/western-heart-audit/BRUTAL-FIST-PULLIN.md'],
  },
];

const GENERATED_PREFIXES = ['t3-', 'doa-', 'vf-', 'vf5-', 'wrestling-pool', 'wmxix-pool', 't7-frame-', 't8-frame-',
  'urban-reign-pending', 'urban-reign-redux-pending', 'soulcalibur2-pending', 'def-jam-pending',
  'street-fighter-3d-pending', 'tekken6-pending', 'ttt2-pending', 'pro-wrestling-2019-pending',
  'pro-wrestling-2020-2022-pending', 'devil-within-pending', 'brutal-fist-pending',
  /* Legacy ids (pre-canon-name fix, 2026-11-08): the two pending rows were
     renamed to pro-wrestling-* ids. Keep the old ids listed so a re-run
     drops the stale rows instead of keeping them as hand-written. */
  'wwe2k19-pending', 'wwe2k20-2k22-pending'];
/* Hand-written 2026-11-05 rows that share a generated prefix — never
   treated as generated: t3-ogre-bank (Chatur's bank) and
   doa-speed-striker (pointer row). */
const HANDWRITTEN_KEEP = new Set(['t3-ogre-bank', 'doa-speed-striker']);
const isGenerated = (id) => !HANDWRITTEN_KEEP.has(id) && GENERATED_PREFIXES.some((p) => id === p || id.startsWith(p));

export function buildTemplates() {
  const index = readJson(INDEX);
  const kept = index.templates.filter((t) => !isGenerated(t.id));
  const generated = [...bankTemplates(), ...poolTemplates(), ...t7Templates(), ...t8Templates(), ...PENDING];
  const ids = new Set(generated.map((t) => t.id));
  if (ids.size !== generated.length) throw new Error('duplicate generated template id');
  const out = { ...index, updated: '2026-11-08', templates: [...kept, ...generated] };
  return out;
}

const isMain = process.argv[1] && process.argv[1].endsWith('build-templates.mjs');
if (isMain) {
  const next = buildTemplates();
  const text = JSON.stringify(next, null, 2) + '\n';
  if (process.argv.includes('--check')) {
    const current = readFileSync(INDEX, 'utf8');
    if (current !== text) { console.error(`templates index is stale: ${next.templates.length} templates expected, re-run build-templates.mjs`); process.exitCode = 1; }
    else console.log(`templates index OK: ${next.templates.length} templates`);
  } else {
    writeFileSync(INDEX, text);
    const byStatus = {};
    for (const t of next.templates) byStatus[t.status] = (byStatus[t.status] || 0) + 1;
    console.log(`wrote ${INDEX}: ${next.templates.length} templates`, JSON.stringify(byStatus));
  }
}
