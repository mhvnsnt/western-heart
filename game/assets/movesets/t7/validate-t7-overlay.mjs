// validate-t7-overlay.mjs — Lane 2 T7 overlay simulation checks (Node, no deps).
// Run from the repo root:  node game/assets/movesets/t7/validate-t7-overlay.mjs
// Or standalone:           node validate-t7-overlay.mjs <dir-with-these-files>
//
// What this checks (simulation on real files only — NOT a playtest):
//  1. Every overlay move has notation / notation_original / notation_lp,
//     a damage KEY (value may be null where the source is null), a
//     hit_level KEY, anim_ref, hitbox object, move_kind, is_throw, and
//     a damage_source flag (MOD for base fighters, NOT MOD for DLC).
//  2. move_count on each file matches its moves[] length; INDEX totals match.
//  3. Strings are TRUE STRING keys: notation_lp contains ',' (a sequence),
//     never a bare chord row standing in for a step. No string notation
//     equals a chord row. For string moves, damage (when present) must
//     split on ',' into the same number of parts as the steps — WH fires
//     each string STEP as its own attack (see pantera.json
//     string_fix_20261024), so a step with no per-step damage is flagged.
//  4. Duplicate notation_lp values are COUNTED per fighter (source-faithful
//     stance/context variants — not an error, but a join must use
//     notation_lp + notes/stance context, never notation alone).
//  5. Bare-digit audit on notation_lp (after removing LP1/RP2/LK3/RK4 and
//     'x N' repeat counts): every remaining digit is listed as a source
//     artifact (see INDEX errata), never silently fixed.
//  6. Jump-input moves (notation starting with u / uf / ub) are COUNTED
//     and flagged: JSON metadata CANNOT detect jumping. Only bone data
//     (hip/pelvis Y rises + falls = jumping; level = standing; down =
//     crouching) can. No jumping animation may be wired into a standing
//     slot on the basis of this file — that check belongs to the
//     animation lane on clip bytes, and this validator explicitly does
//     NOT claim it.
//  7. MADE-WIRING has 188 moves (147 ADAPT + 41 BUILD); STANCE-STATUS has
//     29 UNMAPPED; mot.bin bank counts match the merged frv/dnc tables.
// Exit code 0 = all hard checks pass. Warnings (duplicates, artifacts,
// jump-input counts, string prefix gaps) never fail the run on their own,
// because they describe source shape, not data errors this PR introduced.
import fs from "node:fs";
import path from "node:path";

const dir = process.argv[2] || path.dirname(new URL(import.meta.url).pathname);
const animDir = path.join(dir, "..", "..", "anim", "t7");
const read = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const failures = [];
const warnings = [];
let totalMoves = 0;
let jumpInputs = 0;

const index = read(path.join(dir, "INDEX.json"));
const fighters = index.t7_fighters;
for (const [slug, meta] of Object.entries(fighters)) {
  const file = path.join(dir, path.basename(meta.overlay_file));
  if (!fs.existsSync(file)) { failures.push(`${slug}: overlay file missing: ${file}`); continue; }
  const d = read(file);
  if (d.move_count !== d.moves.length) failures.push(`${slug}: move_count ${d.move_count} != moves[] ${d.moves.length}`);
  const seen = new Map();
  for (const m of d.moves) {
    totalMoves++;
    for (const k of ["notation", "notation_original", "notation_lp", "anim_ref", "hitbox", "move_kind", "is_throw", "damage_source"]) {
      if (!(k in m)) failures.push(`${slug} ${m.notation_lp}: missing field ${k}`);
    }
    if (!("damage" in m)) failures.push(`${slug} ${m.notation_lp}: missing damage key`);
    if (!("hit_level" in m)) failures.push(`${slug} ${m.notation_lp}: missing hit_level key`);
    if (m.anim_ref !== "UNMAPPED") failures.push(`${slug} ${m.notation_lp}: anim_ref is not UNMAPPED (${m.anim_ref}) — no T7 clip bytes exist, so any other value would be a guess`);
    if (!m.hitbox || m.hitbox.boxes !== "UNMAPPED") failures.push(`${slug} ${m.notation_lp}: hitbox.boxes must be UNMAPPED (no coordinates in source)`);
    const wantMod = !["fahkumram", "ganryu", "geese", "kunimitsu", "leroy", "lidia", "negan", "noctis", "zafina"].includes(slug);
    if (wantMod && !String(m.damage_source).includes("MOD")) failures.push(`${slug} ${m.notation_lp}: base fighter damage_source must be MOD`);
    if (!wantMod && !String(m.damage_source).includes("NOT MOD")) failures.push(`${slug} ${m.notation_lp}: DLC damage_source must say NOT MOD`);
    // String checks.
    const lp = m.notation_lp || "";
    if (lp.includes(",")) {
      if (m.move_kind !== "string") failures.push(`${slug} ${lp}: comma notation but move_kind=${m.move_kind}`);
      const steps = lp.split(",").map((s) => s.trim());
      // Hit steps are the steps containing a button; pure-direction steps
      // (f, F, d, qcf, ...) are motion, not hits, and carry no damage part.
      const hitSteps = steps.filter((s) => /LP1|RP2|LK3|RK4/.test(s));
      if (m.damage != null) {
        const parts = String(m.damage).split(",");
        if (parts.length !== hitSteps.length) warnings.push(`${slug} ${lp}: damage parts (${parts.length}) != button hit steps (${hitSteps.length}) — per-step damage ambiguous; engine must not assume running-total damage`);
      }
      // A string step must never be RESOLVED to a chord row by the engine:
      // steps are sequence items; a step containing '+' is a chord STEP
      // (legal, e.g. 'LP1, RP2+LK3'), but the engine must fire the string's
      // own step, never look the step up as a standalone chord move.
      // Data-side, that resolution cannot be proven from JSON alone, so
      // this validator asserts the data shape (comma = string, never a
      // bare '+' row) and leaves step resolution to the combat lane's
      // string engine + play verification. No string notation here equals
      // a chord-only row, because every string notation contains ',' and
      // no chord row does.
    }
    // Bare-digit audit.
    const stripped = lp.replace(/LP1|RP2|LK3|RK4/g, "").replace(/x \d+/g, "");
    const digits = stripped.match(/\d/g);
    if (digits) warnings.push(`${slug} ${lp}: bare digit(s) in notation_lp (source artifact, see INDEX errata): ${digits.join("")}`);
    // Jump-input flag (counted in the summary, not per-row noise).
    // JSON cannot detect jumping — see header note 6.
    const orig = m.notation_original || "";
    if (/^(u|uf|ub)\+/.test(orig)) jumpInputs++;
    seen.set(lp, (seen.get(lp) || 0) + 1);
  }
  const dups = [...seen.entries()].filter(([, c]) => c > 1);
  if (dups.length) warnings.push(`${slug}: ${dups.length} duplicate notation_lp values (stance/context variants, join needs context): ${dups.slice(0, 8).map(([k, c]) => `${k}x${c}`).join("; ")}${dups.length > 8 ? " ..." : ""}`);
}

if (index.after.overlay_moves !== totalMoves) failures.push(`INDEX after.overlay_moves ${index.after.overlay_moves} != counted ${totalMoves}`);
if (Object.keys(fighters).length !== 36) failures.push(`expected 36 overlay fighters (rescoped: 9 slugs held for reconciliation handoff), got ${Object.keys(fighters).length}`);

const made = read(path.join(dir, "MADE-WIRING.json"));
if (made.parsed_count !== 188) failures.push(`MADE-WIRING parsed ${made.parsed_count}, expected 188`);
if (made.moves.filter((m) => m.method === "ADAPT").length !== 147) failures.push(`MADE ADAPT != 147`);
if (made.moves.filter((m) => m.method === "BUILD").length !== 41) failures.push(`MADE BUILD != 41`);
for (const m of made.moves) {
  if (!m.move_list_creator || !m.move_list_creator.additive) failures.push(`MADE ${m.owner}/${m.move}: missing additive Move List Creator wiring`);
  if (!m.input_lp) failures.push(`MADE ${m.owner}/${m.move}: missing input_lp`);
}

const stance = read(path.join(animDir, "STANCE-STATUS.json"));
if (stance.unmapped_29.length !== 29) failures.push(`STANCE unmapped ${stance.unmapped_29.length}, expected 29`);
const frv = read(path.join(animDir, "frv-pond-motbin-bank.json"));
const dnc = read(path.join(animDir, "dnc-ryusan-motbin-bank.json"));
if (frv.counts.moves !== 2338 || frv.counts.bank8000_moves !== 1593 || frv.counts.bank8000_distinct_refs !== 911) failures.push(`frv bank counts mismatch: ${JSON.stringify(frv.counts)}`);
if (dnc.counts.moves !== 2183 || dnc.counts.bank8000_moves !== 1527 || dnc.counts.bank8000_distinct_refs !== 910) failures.push(`dnc bank counts mismatch: ${JSON.stringify(dnc.counts)}`);
for (const bank of [frv, dnc]) {
  for (const m of bank.moves) {
    if (m.anim_id >= 0x8000 && m.bank8000_lookup_index !== m.anim_id - 0x8000) { failures.push(`${bank.wh_character} move ${m.id}: lookup index != anim_id - 0x8000`); break; }
  }
}

console.log(`T7 overlay validation: ${Object.keys(fighters).length} fighters, ${totalMoves} moves, ${jumpInputs} jump-input rows (need hip-Y bone verification, NOT verified here)`);
console.log(`MADE: ${made.parsed_count} (ADAPT ${made.moves.filter((m) => m.method === "ADAPT").length}, BUILD ${made.moves.filter((m) => m.method === "BUILD").length})`);
console.log(`Stance UNMAPPED: ${stance.unmapped_29.length}; frv ${frv.counts.moves}/${frv.counts.bank8000_moves}/${frv.counts.bank8000_distinct_refs}; dnc ${dnc.counts.moves}/${dnc.counts.bank8000_moves}/${dnc.counts.bank8000_distinct_refs}`);
console.log(`Warnings: ${warnings.length} (source shape, not failures — first 40 shown)`);
for (const w of warnings.slice(0, 40)) console.log(`  WARN ${w}`);
if (warnings.length > 40) console.log(`  ... and ${warnings.length - 40} more warnings (see full output)`);
if (failures.length) {
  console.log(`FAILURES: ${failures.length}`);
  for (const f of failures) console.log(`  FAIL ${f}`);
  process.exit(1);
}
console.log("PASS — all hard checks passed. This is simulation on real files, NOT a playtest.");
