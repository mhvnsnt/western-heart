import fs from 'fs';
const { canonNotation } = await import('../../../game/js/movesets.js');
const id = process.argv[2]; const m = JSON.parse(fs.readFileSync(`game/assets/movesets/${id}.json`));
const keys = new Set(Object.keys(m.moves)); const own = {}; for (const k of keys) own[canonNotation(k)] = own[canonNotation(k)] || k;
const NOT = /^[A-Za-z0-9_]*\.?[udfbnUDFBN1-4\/+,~:*]+$/;
let named = 0, free = [], shadow = [], bad = [];
for (const [k, v] of Object.entries(m.moves)) { if (NOT.test(k) || !v.input) continue; named++;
  const c = canonNotation(v.input); if (!NOT.test(c)) bad.push(`${k}=${c}`); else if (own[c]) shadow.push(`${k}=${c}->${own[c]}`); else { free.push(`${k}=${c}`); own[c] = k; } }
console.log({ named, free: free.length, shadow: shadow.length, bad: bad.length }); console.log('FREE', free.join(' ')); console.log('SHADOW', shadow.join(' ')); console.log('BAD', bad.join(' '));
