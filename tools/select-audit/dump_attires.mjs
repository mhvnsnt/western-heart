// node tools/select-audit/dump_attires.mjs > attires.json — attire ladder per fighter (for analyze.py default-attire check)
globalThis.localStorage = { getItem: () => null, setItem() {} };
const { FULL_ROSTER } = await import('../../game/js/roster-full.js');
const { attiresFor } = await import('../../game/js/attires.js');
const out = {};
for (const f of FULL_ROSTER) out[f.id] = attiresFor(f);
console.log(JSON.stringify(out, null, 1));
