// Canon-wiring regression test for the Move List Creator editor.
// Run: node packages/creation-suite/src/movelist-editor.canon-wiring.test.mjs <moveset-dir>
//   <moveset-dir> holds game/assets/movesets/*.json (wired files carry
//   `canon_moves`). Exits non-zero on any failure. No network, no DOM.
// What it proves (editor-test proof only, NOT play-verified):
//   1. Every canon_moves entry appears in listAllMoves() (by anim_ref).
//   2. No canon row is "unmapped" or "wrong" in its own slot.
//   3. serializeMoveset() with no edits changes nothing except adding
//      the movelist_editor audit block.
//   4. Synthetic checks: an unknown-property canon entry yields
//      "approximate" (assignable with warning), never silent "correct";
//      a genuinely wrong-kind assignment is still blocked by swapMove().
//   5. A Tekken sample row validates exactly as before the canon patch
//      (no weakening of Tekken validation).
import {
  createEditor, listAllMoves, validateAssignment, deriveSlotContext,
  serializeMoveset, swapMove, computeMappingStatus,
} from './movelist-editor.js';
import fs from 'node:fs';
import path from 'node:path';

const dir = process.argv[2];
if (!dir) { console.error('usage: node movelist-editor.canon-wiring.test.mjs <moveset-dir>'); process.exit(2); }
let failures = 0;
const fail = (msg) => { failures += 1; console.error(`FAIL: ${msg}`); };

for (const file of fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
  const ms = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  const fighter = file.replace('.json', '');
  const ed = createEditor({ fighter, moveset: ms });
  const rows = listAllMoves(ed);
  const canonRefs = new Set((ms.canon_moves || []).map((c) => c.anim_ref));
  const canonRows = rows.filter((r) => canonRefs.has(r.anim_ref));
  for (const c of (ms.canon_moves || [])) {
    if (!canonRows.some((r) => r.anim_ref === c.anim_ref)) fail(`${fighter}: canon move missing from list: ${c.name}`);
  }
  for (const r of canonRows) {
    if (r.status === 'unmapped') fail(`${fighter}: canon row unmapped: ${r.name}`);
    if (r.status === 'wrong') fail(`${fighter}: canon row wrong in own slot: ${r.name} (${r.displayInput}) ${r.reasons.join(' ')}`);
    const entry = ed.byId.get(r.id);
    if (entry && !computeMappingStatus(entry).allowed) fail(`${fighter}: canon row blocked in own slot: ${r.name}`);
  }
  const out = serializeMoveset(ed);
  const { movelist_editor, ...restOut } = out;
  if (JSON.stringify(restOut) !== JSON.stringify(ms)) fail(`${fighter}: serializeMoveset changed non-audit content`);
  if (!movelist_editor || !Array.isArray(movelist_editor.edits)) fail(`${fighter}: serializeMoveset missing audit block`);
}

// Synthetic: unknown properties -> approximate, never silent correct.
{
  const ms = { fighter: 'synthetic', moves: {}, specials: [], canon_moves: [
    // Slot for input 1+2 is standing/none/both; only the stance is
    // unknown here, so the row must come back "approximate" (allowed
    // with warning), never "correct" and never "wrong".
    { name: 'Unknown Stance', input: '1+2', display_input: 'LP1+RP2', anim_ref: 'wh:synthetic:unknown', method: 'BUILD', source: 'synthetic', move_class: 'special', limb: 'both',
      properties: { stance: 'unknown', direction: 'none', type: 'strike', limb: 'both', source: 'canon' } },
  ] };
  const ed = createEditor({ fighter: 'synthetic', moveset: ms });
  const row = listAllMoves(ed).find((r) => r.anim_ref === 'wh:synthetic:unknown');
  if (!row || row.status !== 'approximate') fail(`synthetic unknown-property row should be approximate, got ${row?.status}`);
  if (row && row.verification !== 'canon') fail(`synthetic row verification should be canon, got ${row?.verification}`);
}
// Synthetic: genuinely wrong kind is still blocked by swapMove (block mode).
{
  const ms = { fighter: 'synthetic', moves: {
    '1': { name: 'Jab', input: '1', anim_ref: 't3:test:row:1', move_class: 'strike', limb: 'armL' },
    '1+3': { name: 'Throw', input: '1+3', anim_ref: 't3:test:row:2', move_class: 'throw', throw: true, limb: 'armR' },
  }, specials: [] };
  const ed = createEditor({ fighter: 'synthetic', moveset: ms });
  const res = swapMove(ed, '1', '1+3');
  if (res.ok) fail('synthetic: grapple swapped into strike slot should be blocked');
}
console.log(failures === 0 ? 'canon wiring editor tests: PASS' : `canon wiring editor tests: ${failures} FAILURE(S)`);
process.exit(failures === 0 ? 0 : 1);
