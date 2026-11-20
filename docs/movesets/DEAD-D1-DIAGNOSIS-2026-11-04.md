# Dead d+1 — diagnosis and fix (2026-11-04)

**Finding of the roster pass** (PR #1559, `docs/proof/2026-11-03/roster/roster-verdicts-20261103.json`):
the BASICS probe's `d+1` press returned `false` — dead — on 12 fighters: skull, kinpo,
baek-master-white, megami, menajerii, rave, chordz, bruno, purplerain, dxmmii-patchwork,
negativo, cainelias. Other fighters' d+1 works. This doc traces the press path per fighter,
separates the shared causes from the genuine data gaps, and lands the fix for the shared ones.

**Verdict: not one bug — three resolution gaps (7 fighters, fixed) over one genuine
data-gap class (5 fighters, documented, NOT papered over).**

## The press path (traced in code)

`tryAttack('d+1')` (probe, AI, trials) → `Fighter._tryAttackFresh('d+1')`. The notation
`d+1` matches neither the single-button branch (`/^[1234]$/`) nor the chord branch
(`/^[1234](\+[1234])+$/`), so no buffer resolution runs: the press lives or dies on

```js
move = getRealMove(this._movesetId, 'd+1') || MOVES['d+1']   // MOVES has no 'd+1'
```

`getRealMove` → `resolveMove` → `ms._slots['d+1']`, where `_slots` is built once per
moveset by `_prepare()` in `game/js/movesets.js` from: the file's `slots` table, every
move key itself, legacy P/K aliases, `canonNotation(key)` per key, name-keyed moves'
canonical inputs, and the T3 clip-variant slotting rule. **If no move is slotted on
`d+1`, the press is dead — full stop.** Every result below is a statement about what
`_prepare` did with each fighter's own merged data (all traces run against the real
`movesets.js` in Node, not a re-implementation).

Controls (burger, awapop, scimitar, torch — all 10/10 in the pass): each carries a
literal move keyed `d+1`, sourced from its own base's T8 list (burger ← Bob "Coupe
Chop", awapop ← Nina "Low Jab", scimitar ← Shaheen "Hermit Needle", torch ← Anna
"Low Jab"). That is the entire difference: **their modern source list spells the
crouch jab `d+1`; the 12 dead fighters' merged data carries the same jab — or no
jab — under other spellings the resolver never slotted.**

## Class A — recorded input alternate never slotted (1 fighter: negativo)

Negan's T7 frame data (rbnorway csv) writes the command **`d/b or d+1`** — one move,
two inputs. The merge recorded exactly that on the move: key `d/b+1`,
`input_slots: ["d/b+1", "d+1"]`. The `movesets.js` header documents `input_slots` as
"Tekken input slots the move can occupy", and the moveset editor consumes them — but
`_prepare` never did, so the `d+1` half of the move's own data was unreachable.

**Fix (a):** `_prepare` now slots a move on its recorded `input_slots` alternates
under strict guards: single-step notations only, identical button chord as the
move's own input, exactly one claimant move, target slot still free. The guards
matter — a blanket expansion was measured first and rejected: it would add 2,809
slots repo-wide, including DOA/VF string tables whose `input_slots` list every
button *of* a string (a string's `2` step is not an alternate input) and ambiguous
double claims (ryuji's `1+2`). With the guards, class (a) adds **15 slots repo-wide**,
all same-move alternates (negativo `d+1` and `u+1+2`; menajerii `u/f+4`/`u/b+4` →
her `u+4` "Rising Toe Kick" — her `u/f+4` was the pass's other dead input on her;
megami's TTT2 throw alternates `f+1+3`/`f+2+4`, recorded on her own throw rows).

## Class B — T3 any-of down command slotted on none of its spellings (1 of the 12: skull; same row class in 5 more files)

Skull's own T3 bank (bryan) contains the crouch row **r115**, `t3_command: '1/2/3+LP'`
— Tekken 3's encoding for "any of d/b, d, d/f + LP performs this row" (`t3CommandNotations`
returns `['d/b+1', 'd+1', 'd/f+1']`). In skull's merged file the row is keyed `d/b`
(the `_c37` suffix survives only in its name, "BRYAN d/b_c37 (T3 bryan r115)").
`_prepare`'s T3 clip-variant rule slots the **first** free spelling and only for
keys matching `/^[udfbn](\/[fb])?(_[rc]\d+)+$/` — skull's suffix-less key never
matched, so the row sat on **none** of its three spellings: his `d/b+1` and `d+1`
both dead (his `d/f+1` fires a different, modern-list move).

**Fix (b):** for a move with a decoded T3 row (`t3_row` set) whose command yields
multiple notations **all in the down family** (d, d/b, d/f), slot every still-free
spelling. Down family only, deliberately: the up/side any-of groups (`6/9+LP`,
`4/7+LP`) are jump rows the merge already keys on their playable spelling — slotting
their plain `f+1`/`b+1` spellings would put a jump attack on a standing basic
(measured: the unrestricted version added 277 slots including cainelias `f+1` →
a king jump row; rejected). The restricted class adds skull's `d/b+1`+`d+1` (r115),
the same row for kai/retsu/kingtyrant/t3-eddy/t3-forestlaw, and any-of down kicks
(`1/2/3+LK`/`2/3+RK`) for chordz/docfrank/dxmmii/michiko et al.

## Class C — the crouch jab is present as FC.1; d+1 was never equated (5 fighters: kinpo, chordz, purplerain, bruno, menajerii)

These fighters' merged data has **no `d+1` row at all** — their source lists spell
the crouch jab as the full-crouch row:

| fighter | FC row in own data | provenance |
|---|---|---|
| kinpo | `FC.1` (dmg 3) + `hFC.1` "Crouch Jab" (dmg 5) | t7chicken / Asuka T8 |
| chordz | `FC.1` (dmg 3) | t7chicken (Lars) |
| purplerain | `FC.1` (dmg 3/5) | t7chicken / Lee |
| bruno | `FC 1` (dmg 5, key space-spelled, canon `FC.1`) | t7chicken (Miguel) |
| menajerii | `FC 1` "Crouch Scratch" (dmg 12) | TTT2 Roger Jr. wiki list |

`d+1` and `FC.1` are the same physical input — hold down, press 1 — and the game
already treats them so: the input buffer's FC special case in `_pressV2` resolves a
held-down button press to `FC.<button>` ("in Tekken a button there is the FC move,
not the standing d+2"). Only the direct notation path disagreed. Pantera is the
control that proves the two spellings are distinct *rows* when both exist: he
carries a king-list `d+1` (dmg 5) **and** an `FC.1` (dmg 3) — so the fallback must
never displace a real `d+1`, and it doesn't (it fills only a free slot).

**Fix (c):** in `_prepare`, after all other slotting, if `d+1` is still free and
an `FC.1` (or `hFC.1`) slot exists, slot `d+1` → that key. Scoped to button 1 only:
`d+1`/`FC.1` is the universal Tekken spelling pair for the crouch jab; no such
convention exists for 2/3/4, whose FC rows are distinct named moves (measured and
left alone: kronos/dio/ryusan `d+3`/`d+4` would otherwise change too).

## Class D — genuine data gaps (5 fighters: NO fix landed, nothing fabricated)

For these five, an exhaustive scan of every merged layer (move keys, `input`,
`input_slots`, `t7_command`, `t8_id`, decoded `t3_command` spellings, FC rows)
finds **no row in the fighter's own data that a d+1 press could honestly fire**:

- **baek-master-white** — d+1 exists only as a string head (`d+1>4` "Raise Hammer,
  Trick Kick") with no standalone row; his `d/b+1` "Ducking Jab" is a different
  input; no FC.1; the bryan-bank any-of row r115 that skull has is absent from his
  merge. Same "no entry move in own data" class as the everything-else lane's
  STEP 2 remainder (176 rows).
- **megami** — the TTT2 Jun wiki list merged for her contains no d+1 and no FC.1
  row at all. This is the moveset-side face of the known Jun gap (her standing
  basics are not in Jun's own data — `docs/handoffs/TTT2-BANKS-2026-11-04.md`);
  her dead d+1 closes when that gap closes, not by invention here.
- **rave** — Lei's merged data carries d+1 only back-turned (`BT d+1`) and as
  ground-getup alternates (`FCD or SLD 1 (or d+1)` — state-gated rows, not a
  standing input); his any-of T3 row is the crouch *kick* (`1/2/3+LK`, lei r134).
  No standing crouch-jab row exists in his data to slot.
- **dxmmii-patchwork** — no d+1-capable row in any layer (his jin-bank rows are
  the jump family r33–46; no FC.1, no any-of down LP row).
- **cainelias** — no d+1/FC.1 row in his merged set. Contrast pantera: same king
  bank, but pantera's merge bases include the king T8 list that carries `d+1`;
  cainelias's (Undertaker) merge does not. A data-provenance gap, not a resolver bug.

## Secondary item — Vain Abel (does NOT share this root cause)

His `1+2` fires a throw because his own merged data classes it as one: the move on
`1+2` is "Front Facelock (DOA Bass H (offensive hold))", `move_class: 'throw'`,
`isGrab: true` — a DOA→Tekken mapping artifact in his source data (Bass's hold
button imported onto the 1+2 chord), not a resolver/slotting fault. His `d+1`
resolves correctly ('Low Knuckle', strike, dmg 3). His `1+3` animating with
0 damage is the throw-execution class (his `1+3` is genuinely a throw in data,
"Falcon Arrow", dmg 21 on paper) — the same family as Demonio's `1+3` and the
Pantera-vs-bankless A1 anomaly, i.e. throw *pair/exec* behaviour, not input
resolution. Both are noted here and left to their own lanes; this PR changes
nothing for vainabel (verified: zero slot changes).

## The fix and its blast radius

One file: `game/js/movesets.js`, three additive blocks at the end of `_prepare()`
(order: (a) recorded alternates → (b) T3 any-of down spellings → (c) FC.1 fallback;
each fills **only still-free slots**). Full-registry regression over all 128
moveset files, original vs patched `_prepare` output:

- **0 slots overwritten, 0 removed.** Fighters with a working d+1 (all controls,
  pantera, vainabel, chatur, zen) are byte-identical in resolution; zen and chatur
  receive **zero** additions, per their standing constraints.
- **69 slots added across 35 fighters**, every one traceable to the fighter's own
  data under (a), (b) or (c) above.
- Of the 12 dead: **7 fixed** (skull, kinpo, chordz, purplerain, bruno, menajerii,
  negativo), **5 documented data gaps** (class D).

## Proof

- `test/dead-d1-slotting.test.mjs` — the three rules and their guards on
  synthetic movesets (new, this PR).
- Node trace harness (this lane's scratch): per-fighter `resolveMoveKey(id, 'd+1')`
  before/after for all 12 + controls, and the full-registry slot diff quoted above.
- Browser re-probe (roster harness, identity-gated, patched tree): §REPROBE below.

## Re-probe (browser, roster harness, identity-gated, patched tree)

Four previously-dead fighters re-probed with the pass's own harness
(`tryAttack` per BASICS input, opponent Pantera, shrine):

| fighter | class | d+1 before | d+1 after |
|---|---|---|---|
| skull | B | press **false**, 0 dmg | press **true**, **5.5 dmg, strike** (no throw) |
| negativo | A | press **false**, 0 dmg | press **true**, **2.8 dmg, strike** (no throw) |
| kinpo | C | press **false**, 0 dmg | press **true**, **10.8 dmg, strike** (no throw) |
| menajerii | C (+A) | press **false**, 0 dmg | press **true**, **strike** (no throw); 0 dmg registered at probe spacing — her crouch jab ("Crouch Scratch", 12 on paper) is short-reach; the press/fire defect is closed, the damage-at-spacing is recorded as observed, not hidden. Her other dead input, `u/f+4`, also now presses true (12.5 dmg) via class (a). |

All four fighters' other nine BASICS inputs press true, matching or bettering
the original pass (kinpo `d/f+2` registered 0 dmg this run despite pressing —
spacing variance between runs; its slot is untouched by this patch, per the
registry diff above).

