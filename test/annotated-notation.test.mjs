// Sweep class 2: annotated notations canonicalise to the playable input.
import assert from 'node:assert/strict';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const { canonNotation: c } = await import('../game/js/movesets.js');
const cases = { '3+4 (cyclone1)': '3+4', 'n+1+2 (claw)': 'n+1+2', 'n+1 (nc)': 'n+1', 'n+1+2 (charge)': 'n+1+2*',
  '2+4 (vs2, hold)': '2+4*', '3+4 (vshift, break)': '3+4', 'f,n,d,d/f+3+4_od': 'f,n,d,d/f+3+4', '1+2_od': '1+2',
  'air_charge_b,f+1': 'charge_b,f+1', '360+2': 'f,d,b,u+2', 'fc,f+1+3': 'FC.f+1+3', 'qcb+1,1 (DF)': 'qcb+1,1',
  'JGS* (2 spins), 1': 'JGS.1', 'u+1+2 (neutral)': 'u+1+2', 'f+2': 'f+2', 'b+1+2*': 'b+1+2*' };
let n = 0; for (const [i, o] of Object.entries(cases)) { assert.equal(c(i), o, i); n++; }
console.log(`annotated-notation: ${n}/${n} ok`);
